import streamlit as st
import pandas as pd
import io

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.files.file import File

# ======================================================
# 🔐 CREDENCIAIS AZURE AD (APP REGISTRATION)
# ======================================================

TENANT_ID = "SEU_TENANT_ID"
CLIENT_ID = "SEU_CLIENT_ID"
CLIENT_SECRET = "SEU_CLIENT_SECRET"

SHAREPOINT_SITE = "https://dellavolpecombr.sharepoint.com/sites/DellaVolpe"

# ======================================================
# 📁 CAMINHOS DOS ARQUIVOS NO SHAREPOINT
# ======================================================

METAS_SP = "/sites/DellaVolpe/Documentos Compartilhados/metas_cruciais.csv"
MEDIDAS_SP = "/sites/DellaVolpe/Documentos Compartilhados/medidas_direcao.csv"

# ======================================================
# 🔌 SHAREPOINT CONTEXT (CORRETO PRA CLOUD)
# ======================================================

def sp_context():
    return ClientContext(SHAREPOINT_SITE).with_credentials(
        ClientCredential(CLIENT_ID, CLIENT_SECRET)
    )

def ler_csv_sp(caminho):
    ctx = sp_context()
    response = File.open_binary(ctx, caminho)
    return pd.read_csv(io.BytesIO(response.content))

def salvar_csv_sp(df, caminho):
    ctx = sp_context()
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")

    ctx.web.get_file_by_server_relative_url(
        caminho
    ).save_binary(
        buffer.getvalue().encode("utf-8-sig")
    )

# ======================================================
# STREAMLIT APP
# ======================================================

st.set_page_config(page_title="4DX - Gestão de Metas", layout="wide")
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
        df_metas = ler_csv_sp(METAS_SP)

        nova = {
            "equipe": equipe,
            "responsavel": responsavel,
            "meta_crucial": meta_crucial,
            "prazo": prazo,
            "indicador": indicador,
            "meta_final": meta_final
        }

        df_metas = pd.concat(
            [df_metas, pd.DataFrame([nova])],
            ignore_index=True
        )

        salvar_csv_sp(df_metas, METAS_SP)
        st.success("✅ Meta cadastrada com sucesso!")

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Medida de Direção")

    df_metas = ler_csv_sp(METAS_SP)

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
            df_medidas = ler_csv_sp(MEDIDAS_SP)

            medidas_lista = [
                m.strip()
                for m in medida.split("\n")
                if m.strip()
            ]

            novas = [{
                "responsavel": responsavel,
                "meta_crucial": meta_sel,
                "medida_direcao": m,
                "frequencia": frequencia
            } for m in medidas_lista]

            df_medidas = pd.concat(
                [df_medidas, pd.DataFrame(novas)],
                ignore_index=True
            )

            salvar_csv_sp(df_medidas, MEDIDAS_SP)
            st.success(f"✅ {len(novas)} medidas cadastradas com sucesso!")

# ======================================================
# TAB 3 – VISÃO GERAL
# ======================================================
with tabs[2]:
    st.subheader("Visão Geral")

    st.markdown("### 🎯 Metas Cruciais")
    st.dataframe(ler_csv_sp(METAS_SP), use_container_width=True)

    st.markdown("### 🧭 Medidas de Direção")
    st.dataframe(ler_csv_sp(MEDIDAS_SP), use_container_width=True)
