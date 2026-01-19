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
# Estados globais
# ===============================
for k in [
    "usuario_salvo_ok",
    "meta_salva_ok",
    "medida_edit"
]:
    if k not in st.session_state:
        st.session_state[k] = None

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
        nome_equipe = st.text_input("Nome da Equipe", key="nome_equipe")
        salvar_eq = st.form_submit_button("Salvar Equipe")

    if salvar_eq and nome_equipe:
        df = carregar_equipes()
        if nome_equipe not in df["equipe"].values:
            df = pd.concat([df, pd.DataFrame([{"equipe": nome_equipe}])])
            df.to_csv(EQUIPES_PATH, index=False, encoding="utf-8-sig")
            st.success("✅ Equipe cadastrada.")
            st.rerun()

    st.divider()
    st.subheader("Cadastro de Usuários")

    if st.session_state.usuario_salvo_ok:
        st.success("✅ Usuário cadastrado com sucesso.")
        st.session_state.usuario_salvo_ok = False

    df_eq = carregar_equipes()
    if not df_eq.empty:
        with st.form("form_user"):
            nome = st.text_input("Nome", key="user_nome")
            email = st.text_input("Email", key="user_email")
            equipe = st.selectbox("Equipe", df_eq["equipe"], key="user_equipe")
            salvar_user = st.form_submit_button("Salvar Usuário")

        if salvar_user and nome and email:
            df_u = carregar_usuarios()
            if email not in df_u["email"].values:
                df_u = pd.concat([df_u, pd.DataFrame([{
                    "nome": nome,
                    "email": email,
                    "equipe": equipe
                }])])
                df_u.to_csv(USUARIOS_PATH, index=False, encoding="utf-8-sig")
                st.session_state.usuario_salvo_ok = True
                st.rerun()

# ======================================================
# TAB 1 – META CRUCIAL
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Meta Crucial")

    if st.session_state.meta_salva_ok:
        st.success("✅ Meta salva com sucesso.")
        st.session_state.meta_salva_ok = False

    df_eq = carregar_equipes()
    df_u = carregar_usuarios()
    df_metas = carregar_metas()

    equipe = st.selectbox("Equipe", df_eq["equipe"], key="meta_equipe")

    responsavel = st.selectbox(
        "Responsável",
        df_u[df_u["equipe"] == equipe]["nome"],
        key="resp_meta"
    )

    existente = df_metas[df_metas["responsavel"] == responsavel]

    with st.form("form_meta"):
        meta = st.text_area(
            "Meta Crucial",
            value=existente.iloc[0]["meta_crucial"] if not existente.empty else "",
            key="meta_txt"
        )
        indicador = st.text_input(
            "Indicador",
            value=existente.iloc[0]["indicador"] if not existente.empty else "",
            key="meta_ind"
        )
        meta_final = st.text_input(
            "Meta Final",
            value=existente.iloc[0]["meta_final"] if not existente.empty else "",
            key="meta_final"
        )
        prazo = st.text_input(
            "Prazo",
            value=existente.iloc[0]["prazo"] if not existente.empty else "",
            key="meta_prazo"
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

    responsavel = st.selectbox(
        "Responsável",
        df_metas["responsavel"].unique(),
        key="resp_medida"
    )

    meta_sel = st.selectbox(
        "Meta",
        df_metas[df_metas["responsavel"] == responsavel]["meta_crucial"],
        key="meta_medida"
    )

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

        if st.session_state.medida_edit == idx:
            with st.form(f"edit_form_{idx}"):
                txt = st.text_input("Medida", m["medida_direcao"], key=f"txt_{idx}")
                freq = st.selectbox(
                    "Frequência",
                    ["Diária", "Semanal", "Mensal", "Projeto"],
                    index=["Diária", "Semanal", "Mensal", "Projeto"].index(m["frequencia"]),
                    key=f"freq_{idx}"
                )
                salvar = st.form_submit_button("Salvar")

            if salvar:
                df_med.loc[idx, ["medida_direcao", "frequencia"]] = [txt, freq]
                df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")
                st.session_state.medida_edit = None
                st.rerun()

    st.divider()
    with st.form("nova_medida"):
        novas = st.text_area("Adicionar novas medidas (1 por linha)", key="novas_medidas")
        freq = st.selectbox(
            "Frequência",
            ["Diária", "Semanal", "Mensal", "Projeto"],
            key="freq_nova"
        )
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
# TAB 3 – VISÃO GERAL (COM EDIÇÃO)
# ======================================================
with tabs[3]:
    st.subheader("🎯 Metas por Equipe")

    df_metas = carregar_metas()
    df_med = carregar_medidas()

    if "meta_edit_visao" not in st.session_state:
        st.session_state.meta_edit_visao = None

    if df_metas.empty:
        st.info("Nenhuma meta cadastrada.")
        st.stop()

    for equipe, grupo in df_metas.groupby("equipe"):
        st.markdown(f"## 🏷️ Equipe: {equipe}")
        st.divider()

        for idx, meta in grupo.iterrows():
            with st.expander(
                f"🎯 Abrir meta — Responsável: {meta['responsavel']}",
                expanded=False
            ):
                # ===== CABEÇALHO =====
                col_titulo, col_acoes = st.columns([4, 1])

                with col_titulo:
                    st.markdown(f"### {meta['meta_crucial']}")
                    st.caption(f"Responsável: {meta['responsavel']}")

                with col_acoes:
                    if st.button("✏️ Editar", key=f"edit_meta_visao_{idx}"):
                        st.session_state.meta_edit_visao = idx

                    if st.button("🗑️ Excluir", key=f"del_meta_visao_{idx}"):
                        df_metas = df_metas.drop(idx)
                        df_metas.to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

                        df_med = df_med[df_med["meta_crucial"] != meta["meta_crucial"]]
                        df_med.to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

                        st.success("Meta excluída.")
                        st.rerun()

                st.divider()

                # ===== EDIÇÃO =====
                if st.session_state.meta_edit_visao == idx:
                    with st.form(f"form_edit_meta_visao_{idx}"):
                        nova_meta = st.text_area(
                            "Meta Crucial",
                            value=meta["meta_crucial"],
                            key=f"edit_txt_{idx}"
                        )
                        indicador = st.text_input(
                            "Indicador",
                            value=meta["indicador"],
                            key=f"edit_ind_{idx}"
                        )
                        meta_final = st.text_input(
                            "Meta Final",
                            value=meta["meta_final"],
                            key=f"edit_final_{idx}"
                        )
                        prazo = st.text_input(
                            "Prazo",
                            value=meta["prazo"],
                            key=f"edit_prazo_{idx}"
                        )

                        col_salvar, col_cancelar = st.columns(2)
                        salvar = col_salvar.form_submit_button("Salvar")
                        cancelar = col_cancelar.form_submit_button("Cancelar")

                    if salvar:
                        df_metas.loc[idx, [
                            "meta_crucial", "indicador", "meta_final", "prazo"
                        ]] = [nova_meta, indicador, meta_final, prazo]

                        df_metas.to_csv(
                            METAS_PATH, index=False, encoding="utf-8-sig"
                        )

                        df_med.loc[
                            df_med["meta_crucial"] == meta["meta_crucial"],
                            "meta_crucial"
                        ] = nova_meta
                        df_med.to_csv(
                            MEDIDAS_PATH, index=False, encoding="utf-8-sig"
                        )

                        st.session_state.meta_edit_visao = None
                        st.success("Meta atualizada.")
                        st.rerun()

                    if cancelar:
                        st.session_state.meta_edit_visao = None
                        st.rerun()

                # ===== VISUALIZAÇÃO =====
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
