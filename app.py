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
            st.warning("Equipe já existe.")
        else:
            df_eq = pd.concat([df_eq, pd.DataFrame([{"equipe": nome_equipe}])])
            df_eq.to_csv(EQUIPES_PATH, index=False, encoding="utf-8-sig")
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
            salvar = st.form_submit_button("Salvar Usuário")

        if salvar:
            df_u = carregar_usuarios()
            if email in df_u["email"].values:
                st.warning("Email já cadastrado.")
            else:
                df_u = pd.concat([df_u, pd.DataFrame([{
                    "nome": nome,
                    "email": email,
                    "equipe": equipe
                }])])
                df_u.to_csv(USUARIOS_PATH, index=False, encoding="utf-8-sig")
                st.success("Usuário cadastrado.")
                st.rerun()

    st.divider()
    st.subheader("✏️ Renomear Equipe")

    if not df_eq.empty:
        equipe_atual = st.selectbox("Equipe", df_eq["equipe"])
        novo_nome = st.text_input("Novo nome")

        if st.button("Salvar novo nome"):
            if novo_nome and novo_nome not in df_eq["equipe"].values:
                df_eq.loc[df_eq["equipe"] == equipe_atual, "equipe"] = novo_nome
                df_eq.to_csv(EQUIPES_PATH, index=False, encoding="utf-8-sig")

                df_u = carregar_usuarios()
                df_u.loc[df_u["equipe"] == equipe_atual, "equipe"] = novo_nome
                df_u.to_csv(USUARIOS_PATH, index=False, encoding="utf-8-sig")

                df_m = carregar_metas()
                df_m.loc[df_m["equipe"] == equipe_atual, "equipe"] = novo_nome
                df_m.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

                st.success("Equipe renomeada.")
                st.rerun()

# ======================================================
# TAB 1 – META CRUCIAL
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Meta Crucial")

    df_eq = carregar_equipes()
    df_u = carregar_usuarios()

    if df_eq.empty or df_u.empty:
        st.warning("Cadastre equipes e usuários antes.")
        st.stop()

    with st.form("form_meta"):
        equipe = st.selectbox("Equipe", df_eq["equipe"])
        responsavel = st.selectbox(
            "Responsável",
            df_u[df_u["equipe"] == equipe]["nome"]
        )
        meta = st.text_area("Meta Crucial")
        indicador = st.text_input("Indicador")
        meta_final = st.text_input("Meta Final")
        prazo = st.text_input("Prazo")
        salvar = st.form_submit_button("Salvar Meta")

    if salvar:
        df_m = carregar_metas()
        df_m = pd.concat([df_m, pd.DataFrame([{
            "equipe": equipe,
            "responsavel": responsavel,
            "meta_crucial": meta,
            "indicador": indicador,
            "meta_final": meta_final,
            "prazo": prazo
        }])])
        df_m.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")
        st.success("Meta cadastrada.")

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO
# ======================================================
with tabs[2]:
    st.subheader("Cadastrar Medida de Direção")

    df_metas = carregar_metas()

    if not df_metas.empty:
        responsavel = st.selectbox("Responsável", df_metas["responsavel"].unique())
        metas = df_metas[df_metas["responsavel"] == responsavel]["meta_crucial"]
        meta_sel = st.selectbox("Meta", metas)

        with st.form("form_medida"):
            medida = st.text_area("Medida (1 por linha)")
            freq = st.selectbox("Frequência", ["Diária", "Semanal", "Mensal", "Projeto"])
            salvar = st.form_submit_button("Salvar")

        if salvar:
            df_med = carregar_medidas()
            novas = [{
                "responsavel": responsavel,
                "meta_crucial": meta_sel,
                "medida_direcao": m.strip(),
                "frequencia": freq
            } for m in medida.split("\n") if m.strip()]

            df_med = pd.concat([df_med, pd.DataFrame(novas)])
            df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")
            st.success("Medidas cadastradas.")

# ======================================================
# TAB 3 – VISÃO GERAL (EDITAR / EXCLUIR METAS)
# ======================================================
with tabs[3]:
    st.subheader("🎯 Metas")

    df_metas = carregar_metas()
    df_med = carregar_medidas()

    for idx, meta in df_metas.iterrows():
        key = f"meta_{idx}"
        with st.expander(f"{meta['meta_crucial']} — ({meta['responsavel']})"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Editar", key=f"edit_{key}"):
                    st.session_state[f"edit_{key}"] = True

            with col2:
                if st.button("🗑️ Excluir", key=f"del_{key}"):
                    df_metas = df_metas.drop(idx)
                    df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

                    df_med = df_med[df_med["meta_crucial"] != meta["meta_crucial"]]
                    df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

                    st.success("Meta excluída.")
                    st.rerun()

            if st.session_state.get(f"edit_{key}", False):
                with st.form(f"form_edit_{key}"):
                    nova_meta = st.text_area("Meta", meta["meta_crucial"])
                    indicador = st.text_input("Indicador", meta["indicador"])
                    meta_final = st.text_input("Meta Final", meta["meta_final"])
                    prazo = st.text_input("Prazo", meta["prazo"])
                    salvar = st.form_submit_button("Salvar alterações")

                if salvar:
                    df_metas.loc[idx, ["meta_crucial","indicador","meta_final","prazo"]] = \
                        [nova_meta, indicador, meta_final, prazo]
                    df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

                    df_med.loc[
                        df_med["meta_crucial"] == meta["meta_crucial"],
                        "meta_crucial"
                    ] = nova_meta
                    df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

                    st.session_state[f"edit_{key}"] = False
                    st.success("Meta atualizada.")
                    st.rerun()

            else:
                st.markdown(f"**Indicador:** {meta['indicador']}")
                st.markdown(f"**Meta Final:** {meta['meta_final']}")
                st.markdown(f"**Prazo:** {meta['prazo']}")

                st.markdown("#### 🧭 Medidas de Direção")
                medidas = df_med[df_med["meta_crucial"] == meta["meta_crucial"]]

                if medidas.empty:
                    st.info("Nenhuma medida cadastrada.")
                else:
                    for _, m in medidas.iterrows():
                        st.markdown(f"- {m['medida_direcao']} ({m['frequencia']})")
