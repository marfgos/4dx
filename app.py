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
        salvar = st.form_submit_button("Salvar Equipe")

    if salvar and nome_equipe:
        df = carregar_equipes()
        if nome_equipe not in df["equipe"].values:
            df = pd.concat([df, pd.DataFrame([{"equipe": nome_equipe}])])
            df.to_csv(EQUIPES_PATH, index=False, encoding="utf-8-sig")
            st.success("Equipe cadastrada.")
            st.rerun()

    st.divider()
    st.subheader("Cadastro de Usuários")

    df_eq = carregar_equipes()
    if not df_eq.empty:
        with st.form("form_user"):
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            equipe = st.selectbox("Equipe", df_eq["equipe"])
            salvar_user = st.form_submit_button("Salvar Usuário")

        if salvar_user:
            df_u = carregar_usuarios()
            if email not in df_u["email"].values:
                df_u = pd.concat([df_u, pd.DataFrame([{
                    "nome": nome,
                    "email": email,
                    "equipe": equipe
                }])])
                df_u.to_csv(USUARIOS_PATH, index=False, encoding="utf-8-sig")
                st.success("Usuário cadastrado.")
                st.rerun()

# ======================================================
# TAB 1 – META CRUCIAL (AUTO + SUCESSO)
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Meta Crucial")

    df_eq = carregar_equipes()
    df_u = carregar_usuarios()
    df_metas = carregar_metas()

    if "meta_salva_ok" not in st.session_state:
        st.session_state.meta_salva_ok = False

    if st.session_state.meta_salva_ok:
        st.success("✅ Meta salva com sucesso.")
        st.session_state.meta_salva_ok = False

    equipe = st.selectbox("Equipe", df_eq["equipe"])
    responsavel = st.selectbox(
        "Responsável",
        df_u[df_u["equipe"] == equipe]["nome"]
    )

    existente = df_metas[df_metas["responsavel"] == responsavel]

    with st.form("form_meta"):
        meta = st.text_area(
            "Meta Crucial",
            value=existente.iloc[0]["meta_crucial"] if not existente.empty else ""
        )
        indicador = st.text_input(
            "Indicador",
            value=existente.iloc[0]["indicador"] if not existente.empty else ""
        )
        meta_final = st.text_input(
            "Meta Final",
            value=existente.iloc[0]["meta_final"] if not existente.empty else ""
        )
        prazo = st.text_input(
            "Prazo",
            value=existente.iloc[0]["prazo"] if not existente.empty else ""
        )
        salvar = st.form_submit_button("Salvar Meta")

    if salvar:
        df_metas = df_metas[df_metas["responsavel"] != responsavel]
        df_metas = pd.concat([df_metas, pd.DataFrame([{
            "equipe": equipe,
            "responsavel": responsavel,
            "meta_crucial": meta,
            "indicador": indicador,
            "meta_final": meta_final,
            "prazo": prazo
        }])])
        df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")
        st.session_state.meta_salva_ok = True
        st.rerun()

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO
# ======================================================
with tabs[2]:
    st.subheader("Cadastrar Medida de Direção")

    df_metas = carregar_metas()
    df_med = carregar_medidas()

    responsavel = st.selectbox("Responsável", df_metas["responsavel"].unique())
    meta_sel = st.selectbox(
        "Meta",
        df_metas[df_metas["responsavel"] == responsavel]["meta_crucial"]
    )

    st.markdown("### 🧭 Medidas já cadastradas")
    medidas = df_med[
        (df_med["responsavel"] == responsavel) &
        (df_med["meta_crucial"] == meta_sel)
    ]

    for idx, m in medidas.iterrows():
        col1, col2, col3 = st.columns([6, 1, 1])
        col1.write(f"{m['medida_direcao']} ({m['frequencia']})")

        if col2.button("✏️", key=f"edit_med_{idx}"):
            st.session_state.medida_edit = idx

        if col3.button("🗑️", key=f"del_med_{idx}"):
            df_med = df_med.drop(idx)
            df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")
            st.rerun()

        if st.session_state.get("medida_edit") == idx:
            with st.form(f"form_edit_med_{idx}"):
                txt = st.text_input("Medida", m["medida_direcao"])
                freq = st.selectbox(
                    "Frequência",
                    ["Diária", "Semanal", "Mensal", "Projeto"],
                    index=["Diária", "Semanal", "Mensal", "Projeto"].index(m["frequencia"])
                )
                salvar = st.form_submit_button("Salvar")

            if salvar:
                df_med.loc[idx, ["medida_direcao", "frequencia"]] = [txt, freq]
                df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")
                st.session_state.medida_edit = None
                st.rerun()

    st.divider()
    with st.form("form_medida"):
        novas = st.text_area("Adicionar novas medidas (1 por linha)")
        freq = st.selectbox("Frequência", ["Diária", "Semanal", "Mensal", "Projeto"])
        salvar = st.form_submit_button("Salvar Medidas")

    if salvar:
        df_med = pd.concat([df_med, pd.DataFrame([{
            "responsavel": responsavel,
            "meta_crucial": meta_sel,
            "medida_direcao": m.strip(),
            "frequencia": freq
        } for m in novas.split("\n") if m.strip()])])
        df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")
        st.rerun()

# ======================================================
# TAB 3 – VISÃO GERAL
# ======================================================
with tabs[3]:
    st.subheader("🎯 Metas por Equipe")

    df_metas = carregar_metas()
    df_med = carregar_medidas()

    if "meta_edit" not in st.session_state:
        st.session_state.meta_edit = None

    for equipe, grupo in df_metas.groupby("equipe"):
        st.markdown(f"## 🏷️ Equipe: {equipe}")
        st.divider()

        for idx, meta in grupo.iterrows():
            with st.expander(f"🎯 Abrir meta — Responsável: {meta['responsavel']}"):
                st.markdown(f"### {meta['meta_crucial']}")
                st.markdown(f"**Indicador:** {meta['indicador']}")
                st.markdown(f"**Meta Final:** {meta['meta_final']}")
                st.markdown(f"**Prazo:** {meta['prazo']}")

                st.markdown("### 🧭 Medidas de Direção")
                medidas = df_med[df_med["meta_crucial"] == meta["meta_crucial"]]

                for _, m in medidas.iterrows():
                    st.markdown(f"- {m['medida_direcao']} ({m['frequencia']})")
