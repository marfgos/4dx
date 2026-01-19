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
        if nome_equipe in df["equipe"].values:
            st.warning("Equipe já existe.")
        else:
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

# ======================================================
# TAB 1 – META CRUCIAL (COM AUTO-PREENCHIMENTO)
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Meta Crucial")

    df_eq = carregar_equipes()
    df_u = carregar_usuarios()
    df_metas = carregar_metas()

    if df_eq.empty or df_u.empty:
        st.warning("Cadastre equipes e usuários antes.")
        st.stop()

    equipe = st.selectbox("Equipe", df_eq["equipe"])
    responsavel = st.selectbox(
        "Responsável",
        df_u[df_u["equipe"] == equipe]["nome"]
    )

    # 🔍 busca meta existente do responsável
    meta_existente = df_metas[df_metas["responsavel"] == responsavel]

    meta_default = meta_existente.iloc[0]["meta_crucial"] if not meta_existente.empty else ""
    indicador_default = meta_existente.iloc[0]["indicador"] if not meta_existente.empty else ""
    meta_final_default = meta_existente.iloc[0]["meta_final"] if not meta_existente.empty else ""
    prazo_default = meta_existente.iloc[0]["prazo"] if not meta_existente.empty else ""

    with st.form("form_meta"):
        meta = st.text_area("Meta Crucial", value=meta_default)
        indicador = st.text_input("Indicador", value=indicador_default)
        meta_final = st.text_input("Meta Final", value=meta_final_default)
        prazo = st.text_input("Prazo", value=prazo_default)
        salvar = st.form_submit_button("Salvar Meta")

    if salvar:
        # remove meta antiga do responsável (se existir)
        df_metas = df_metas[df_metas["responsavel"] != responsavel]

        nova = pd.DataFrame([{
            "equipe": equipe,
            "responsavel": responsavel,
            "meta_crucial": meta,
            "indicador": indicador,
            "meta_final": meta_final,
            "prazo": prazo
        }])

        df_metas = pd.concat([df_metas, nova], ignore_index=True)
        df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

        st.success("Meta salva com sucesso.")
        st.rerun()


# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO (FILTRADA POR RESPONSÁVEL)
# ======================================================
with tabs[2]:
    st.subheader("Cadastrar Medida de Direção")

    df_metas = carregar_metas()
    df_med = carregar_medidas()

    if df_metas.empty:
        st.warning("Cadastre metas antes.")
        st.stop()

    responsavel = st.selectbox(
        "Responsável",
        df_metas["responsavel"].unique()
    )

    metas_resp = df_metas[df_metas["responsavel"] == responsavel]["meta_crucial"]
    meta_sel = st.selectbox("Meta", metas_resp)

    # 🔍 medidas já cadastradas
    medidas_existentes = df_med[
        (df_med["responsavel"] == responsavel) &
        (df_med["meta_crucial"] == meta_sel)
    ]

    st.markdown("### 🧭 Medidas já cadastradas")
    if medidas_existentes.empty:
        st.info("Nenhuma medida cadastrada para esta meta.")
    else:
        for _, m in medidas_existentes.iterrows():
            st.markdown(f"- {m['medida_direcao']} ({m['frequencia']})")

    st.divider()

    with st.form("form_medida"):
        novas_medidas = st.text_area(
            "Adicionar novas medidas (uma por linha)"
        )
        freq = st.selectbox(
            "Frequência",
            ["Diária", "Semanal", "Mensal", "Projeto"]
        )
        salvar = st.form_submit_button("Salvar Medidas")

    if salvar:
        novas = [{
            "responsavel": responsavel,
            "meta_crucial": meta_sel,
            "medida_direcao": m.strip(),
            "frequencia": freq
        } for m in novas_medidas.split("\n") if m.strip()]

        df_med = pd.concat([df_med, pd.DataFrame(novas)], ignore_index=True)
        df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

        st.success("Medidas adicionadas.")
        st.rerun()

# ======================================================
# TAB 3 – VISÃO GERAL (AGRUPADO + TÍTULO EM DESTAQUE)
# ======================================================
with tabs[3]:
    st.subheader("🎯 Metas por Equipe")

    df_metas = carregar_metas()
    df_med = carregar_medidas()

    if "meta_em_edicao" not in st.session_state:
        st.session_state.meta_em_edicao = None

    if df_metas.empty:
        st.info("Nenhuma meta cadastrada.")
    else:
        for equipe, metas_eq in df_metas.groupby("equipe"):
            st.markdown(f"## 🏷️ Equipe: {equipe}")
            st.divider()

            for idx, meta in metas_eq.iterrows():
                with st.expander(
                f"🎯 Abrir meta — Responsável: {meta['responsavel']}"
                ):
                    # ---------- CABEÇALHO DA META ----------
                    col_titulo, col_acoes = st.columns([4, 1])

                    with col_titulo:
                        st.markdown(
                            f"### 🎯 {meta['meta_crucial']}\n"
                            f"<span style='color:gray'>Responsável: {meta['responsavel']}</span>",
                            unsafe_allow_html=True
                        )

                    with col_acoes:
                        if st.button("✏️ Editar", key=f"edit_{idx}"):
                            st.session_state.meta_em_edicao = idx

                        if st.button("🗑️ Excluir", key=f"del_{idx}"):
                            df_metas = df_metas.drop(idx)
                            df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

                            df_med = df_med[df_med["meta_crucial"] != meta["meta_crucial"]]
                            df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

                            st.success("Meta excluída.")
                            st.rerun()

                    st.divider()

                    # ---------- EDIÇÃO ----------
                    if st.session_state.meta_em_edicao == idx:
                        with st.form(f"form_edit_{idx}"):
                            nova_meta = st.text_area("Meta Crucial", meta["meta_crucial"])
                            indicador = st.text_input("Indicador", meta["indicador"])
                            meta_final = st.text_input("Meta Final", meta["meta_final"])
                            prazo = st.text_input("Prazo", meta["prazo"])

                            salvar = st.form_submit_button("Salvar")
                            cancelar = st.form_submit_button("Cancelar")

                        if salvar:
                            df_metas.loc[idx, ["meta_crucial","indicador","meta_final","prazo"]] = [
                                nova_meta, indicador, meta_final, prazo
                            ]
                            df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

                            df_med.loc[
                                df_med["meta_crucial"] == meta["meta_crucial"],
                                "meta_crucial"
                            ] = nova_meta
                            df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

                            st.session_state.meta_em_edicao = None
                            st.success("Meta atualizada.")
                            st.rerun()

                        if cancelar:
                            st.session_state.meta_em_edicao = None
                            st.rerun()

                    # ---------- VISUALIZAÇÃO ----------
                    else:
                        st.markdown(f"**Indicador:** {meta['indicador']}")
                        st.markdown(f"**Meta Final:** {meta['meta_final']}")
                        st.markdown(f"**Prazo:** {meta['prazo']}")

                        st.markdown("### 🧭 Medidas de Direção")
                        medidas = df_med[df_med["meta_crucial"] == meta["meta_crucial"]]

                        if medidas.empty:
                            st.info("Nenhuma medida cadastrada.")
                        else:
                            for _, m in medidas.iterrows():
                                st.markdown(
                                    f"- **{m['medida_direcao']}** "
                                    f"(_{m['frequencia']}_)"
                                )
