import streamlit as st
import pandas as pd
from pathlib import Path

# ===============================
# Configurações iniciais
# ===============================
st.set_page_config(page_title="4DX - Gestão de Metas", layout="wide")

BASE_PATH = Path("data")
BASE_PATH.mkdir(exist_ok=True)

METAS_PATH = BASE_PATH / "metas_cruciais.csv"
MEDIDAS_PATH = BASE_PATH / "medidas_direcao.csv"

# ===============================
# Inicializa arquivos se não existirem
# ===============================
if not METAS_PATH.exists():
    pd.DataFrame(columns=[
        "equipe",
        "responsavel",
        "meta_crucial",
        "prazo",
        "indicador",
        "meta_final"
    ]).to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

if not MEDIDAS_PATH.exists():
    pd.DataFrame(columns=[
        "responsavel",
        "meta_crucial",
        "medida_direcao",
        "frequencia"
    ]).to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

# ===============================
# Carrega dados
# ===============================
df_metas = pd.read_csv(METAS_PATH)
df_medidas = pd.read_csv(MEDIDAS_PATH)

# ===============================
# Título
# ===============================
st.title("🎯 4DX – Gestão de Metas Cruciais")

tabs = st.tabs(["➕ Cadastrar Meta", "➕ Cadastrar Medida", "📊 Visão Geral"])

# ======================================================
# TAB 1 – CADASTRAR META CRUCIAL
# ======================================================
with tabs[0]:
    st.subheader("Cadastrar Meta Crucial (1 por pessoa)")

    with st.form("form_meta"):
        equipe = st.text_input("Equipe")
        responsavel = st.text_input("Responsável")
        meta_crucial = st.text_area("Meta Crucial")
        prazo = st.text_input("Prazo (ex: 31/03/2026)")
        indicador = st.text_input("Indicador")
        meta_final = st.text_input("Meta Final")

        salvar_meta = st.form_submit_button("Salvar Meta")

    if salvar_meta:
        nova_meta = {
            "equipe": equipe,
            "responsavel": responsavel,
            "meta_crucial": meta_crucial,
            "prazo": prazo,
            "indicador": indicador,
            "meta_final": meta_final
        }

        df_metas = pd.concat([df_metas, pd.DataFrame([nova_meta])], ignore_index=True)
        df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

        st.success("✅ Meta crucial cadastrada com sucesso!")

# ======================================================
# TAB 2 – CADASTRAR MEDIDA DE DIREÇÃO
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Medida de Direção")

    if df_metas.empty:
        st.warning("Cadastre uma meta crucial antes de adicionar medidas.")
    else:
        responsavel_sel = st.selectbox(
            "Responsável",
            df_metas["responsavel"].unique()
        )

        metas_responsavel = df_metas[
            df_metas["responsavel"] == responsavel_sel
        ]["meta_crucial"].unique()

        meta_sel = st.selectbox("Meta Crucial", metas_responsavel)

        with st.form("form_medida"):
            medida = st.text_area("Medida de Direção")
            frequencia = st.selectbox(
                "Frequência",
                ["Diária", "Semanal", "Mensal", "Projeto"]
            )

            salvar_medida = st.form_submit_button("Salvar Medida")

        if salvar_medida:
            nova_medida = {
                "responsavel": responsavel_sel,
                "meta_crucial": meta_sel,
                "medida_direcao": medida,
                "frequencia": frequencia
            }

            df_medidas = pd.concat(
                [df_medidas, pd.DataFrame([nova_medida])],
                ignore_index=True
            )
            df_medidas.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

            st.success("✅ Medida de direção cadastrada com sucesso!")

# ======================================================
# TAB 3 – VISÃO GERAL
# ======================================================
with tabs[2]:
    st.subheader("Visão Geral – 4DX")

    st.markdown("### 🎯 Metas Cruciais")
    st.dataframe(df_metas, use_container_width=True)

    st.markdown("### 🧭 Medidas de Direção")
    st.dataframe(df_medidas, use_container_width=True)

