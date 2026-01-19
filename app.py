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
# Paths
# ===============================
BASE_PATH = Path("data")
BASE_PATH.mkdir(exist_ok=True)

EQUIPES_PATH = BASE_PATH / "equipes.csv"
USUARIOS_PATH = BASE_PATH / "usuarios.csv"
METAS_PATH = BASE_PATH / "metas_cruciais.csv"
MEDIDAS_PATH = BASE_PATH / "medidas_direcao.csv"

# ===============================
# Inicialização dos arquivos
# ===============================
if not EQUIPES_PATH.exists():
    pd.DataFrame(columns=["equipe"]).to_csv(EQUIPES_PATH, index=False, encoding="utf-8-sig")

if not USUARIOS_PATH.exists():
    pd.DataFrame(columns=["nome", "email", "equipe"]).to_csv(
        USUARIOS_PATH, index=False, encoding="utf-8-sig"
    )

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
# Funções
# ===============================
def carregar_equipes():
    return pd.read_csv(EQUIPES_PATH)

def carregar_usuarios():
    return pd.read_csv(USUARIOS_PATH)

def carregar_metas():
    return pd.read_csv(METAS_PATH)

def carregar_medidas():
    return pd.read_csv(MEDIDAS_PATH)

# ===============================
# Título
# ===============================
st.title("🎯 4DX – Gestão de Metas")

tabs = st.tabs([
    "👥 Equipes & Usuários",
    "➕ Meta Crucial",
    "➕ Medida de Direção",
    "📊 Visão Geral"
])

# ======================================================
# TAB 0 – EQUIPES & USUÁRIOS
# ======================================================
with tabs[0]:
    st.subheader("Cadastro de Equipes")

    with st.form("form_equipe"):
        nome_equipe = st.text_input("Nome da Equipe")
        salvar_eq = st.form_submit_button("Salvar Equipe")

    if salvar_eq and nome_equipe:
        df_eq = carregar_equipes()

        if nome_equipe in df_eq["equipe"].values:
            st.warning("⚠️ Essa equipe já existe.")
        else:
            df_eq = pd.concat(
                [df_eq, pd.DataFrame([{"equipe": nome_equipe}])],
                ignore_index=True
            )
            df_eq.to_csv(EQUIPES_PATH, index=False, encoding="utf-8-sig")
            st.success("✅ Equipe cadastrada com sucesso!")

    st.divider()

    st.subheader("Cadastro de Usuários")

    df_eq = carregar_equipes()

    if df_eq.empty:
        st.warning("Cadastre uma equipe antes de adicionar usuários.")
    else:
        with st.form("form_usuario"):
            nome_usuario = st.text_input("Nome do Usuário")
            email_usuario = st.text_input("Email")
            equipe_usuario = st.selectbox("Equipe", df_eq["equipe"])
            salvar_user = st.form_submit_button("Salvar Usuário")

        if salvar_user and nome_usuario and email_usuario:
            df_user = carregar_usuarios()

            if email_usuario in df_user["email"].values:
                st.warning("⚠️ Já existe um usuário cadastrado com esse email.")
            else:
                df_user = pd.concat(
                    [df_user, pd.DataFrame([{
                        "nome": nome_usuario,
                        "email": email_usuario,
                        "equipe": equipe_usuario
                    }])],
                    ignore_index=True
                )
                df_user.to_csv(USUARIOS_PATH, index=False, encoding="utf-8-sig")
                st.success("✅ Usuário cadastrado com sucesso!")

# ======================================================
# TAB 1 – META CRUCIAL
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Meta Crucial")

    df_eq = carregar_equipes()
    df_users = carregar_usuarios()

    if df_eq.empty or df_users.empty:
        st.warning("Cadastre equipes e usuários antes de criar metas.")
        st.stop()

    with st.form("form_meta"):
        equipe = st.selectbox("Equipe", df_eq["equipe"])

        df_resp = df_users[df_users["equipe"] == equipe]

        opcoes_resp = df_resp.apply(
            lambda x: f"{x['nome']} ({x['email']})",
            axis=1
        )

        responsavel_sel = st.selectbox("Responsável", opcoes_resp)
        responsavel = responsavel_sel.split(" (")[0]

        meta_crucial = st.text_area("Meta Crucial")
        prazo = st.text_input("Prazo (ex: 31/03/2026)")
        indicador = st.text_input("Indicador")
        meta_final = st.text_input("Meta Final")

        salvar_meta = st.form_submit_button("Salvar Meta")

    if salvar_meta:
        df = carregar_metas()

        df = pd.concat(
            [df, pd.DataFrame([{
                "equipe": equipe,
                "responsavel": responsavel,
                "meta_crucial": meta_crucial,
                "prazo": prazo,
                "indicador": indicador,
                "meta_final": meta_final
            }])],
            ignore_index=True
        )

        df.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")
        st.success("✅ Meta cadastrada com sucesso!")

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO
# ======================================================
with tabs[2]:
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
            medida = st.text_area("Medida de Direção (uma por linha)", height=120)
            frequencia = st.selectbox(
                "Frequência",
                ["Diária", "Semanal", "Mensal", "Projeto"]
            )
            salvar_medida = st.form_submit_button("Salvar Medidas")

        if salvar_medida:
            df_medidas = carregar_medidas()

            medidas_lista = [m.strip() for m in medida.split("\n") if m.strip()]

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

            df_medidas.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")
            st.success(f"✅ {len(novas)} medidas cadastradas!")

# ======================================================
# TAB 3 – VISÃO GERAL
# ======================================================
with tabs[3]:
    st.subheader("Visão Geral")

    st.markdown("### 👥 Equipes")
    st.dataframe(carregar_equipes(), use_container_width=True)

    st.markdown("### 👤 Usuários")
    st.dataframe(carregar_usuarios(), use_container_width=True)

    st.markdown("### 🎯 Metas Cruciais")
    st.dataframe(carregar_metas(), use_container_width=True)

    st.markdown("### 🧭 Medidas de Direção")
    st.dataframe(carregar_medidas(), use_container_width=True)
