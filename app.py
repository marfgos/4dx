import streamlit as st
import pandas as pd
from pathlib import Path

# ===============================
# Configuração da página
# ===============================
st.set_page_config(
    page_title="4DX - Gestão de Metas",
    layout="wide"
)

# ===============================
# Paths (Cloud-safe)
# ===============================
BASE_PATH = Path("data")
BASE_PATH.mkdir(exist_ok=True)

METAS_PATH = BASE_PATH / "metas_cruciais.csv"
MEDIDAS_PATH = BASE_PATH / "medidas_direcao.csv"

# ===============================
# Inicialização dos arquivos
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
# Funções de leitura
# ===============================
def carregar_metas():
    return pd.read_csv(METAS_PATH)

def carregar_medidas():
    return pd.read_csv(MEDIDAS_PATH)

# ===============================
# Título
# ===============================
st.title("🎯 4DX – Gestão de Metas Cruciais")

tabs = st.tabs([
    "➕ Meta Crucial",
    "➕ Medida de Direção",
    "📊 Visão Geral"
])

# ======================================================
# TAB 1 – META CRUCIAL
# ======================================================
with tabs[0]:
    st.subheader("Cadastrar Meta Crucial")

    with st.form("form_meta"):
        equipe = st.text_input("Equipe")
        responsavel = st.text_input("Responsável")
        meta_crucial = st.text_area("Meta Crucial")
        prazo = st.text_input("Prazo (ex: 31/03/2026)")
        indicador = st.text_input("Indicador")
        meta_final = st.text_input("Meta Final")

        salvar = st.form_submit_button("Salvar")

    if salvar:
        df = carregar_metas()

        nova = {
            "equipe": equipe,
            "responsavel": responsavel,
            "meta_crucial": meta_crucial,
            "prazo": prazo,
            "indicador": indicador,
            "meta_final": meta_final
        }

        df = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
        df.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

        st.success("✅ Meta cadastrada com sucesso!")

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Medida de Direção")

    df_metas = carregar_metas()

    if df_metas.empty:
        st.warning("Cadastre uma meta antes de adicionar medidas.")
    else:
        responsavel = st.selectbox(
            "Responsável",
            df_metas["responsavel"].unique()
        )

        metas = df_metas[
            df_metas["responsavel"] == responsavel
        ]["meta_crucial"].unique()

        meta_sel = st.selectbox("Meta Crucial", metas)

        with st.form("form_medida"):
            medida = st.text_area(
                "Medida de Direção (uma por linha)",
                height=120
            )

            frequencia = st.selectbox(
                "Frequência",
                ["Diária", "Semanal", "Mensal", "Projeto"]
            )

            salvar_medida = st.form_submit_button("Salvar")

        if salvar_medida:
            df_medidas = carregar_medidas()

            # 🔥 CORREÇÃO: quebra em linhas
            medidas_lista = [
                m.strip()
                for m in medida.split("\n")
                if m.strip()
            ]

            novas_linhas = []

            for m in medidas_lista:
                novas_linhas.append({
                    "responsavel": responsavel,
                    "meta_crucial": meta_sel,
                    "medida_direcao": m,
                    "frequencia": frequencia
                })

            df_medidas = pd.concat(
                [df_medidas, pd.DataFrame(novas_linhas)],
                ignore_index=True
            )

            df_medidas.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

            st.success(f"✅ {len(novas_linhas)} medidas cadastradas com sucesso!")

# ======================================================
# TAB 3 – VISÃO GERAL
# ======================================================
with tabs[2]:
    st.subheader("Visão Geral")

    st.markdown("### 🎯 Metas Cruciais")
    st.dataframe(carregar_metas(), use_container_width=True)

    st.markdown("### 🧭 Medidas de Direção")
    st.dataframe(carregar_medidas(), use_container_width=True)
