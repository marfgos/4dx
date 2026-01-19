import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

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
SEMANAS_PATH = BASE_PATH / "semanas.csv"

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

if not SEMANAS_PATH.exists():
    pd.DataFrame(columns=[
        "responsavel",
        "meta_crucial",
        "semana_ref",
        "feito",
        "planejado"
    ]).to_csv(SEMANAS_PATH, index=False, encoding="utf-8-sig")

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

def carregar_semanas():
    return pd.read_csv(SEMANAS_PATH)

def inicio_semana(data=None):
    if not data:
        data = datetime.today()
    return (data - timedelta(days=data.weekday()))


def semana_anterior():
    return inicio_semana() - timedelta(days=7)

# ===============================
# Estados globais
# ===============================
for k in [
    "usuario_salvo_ok",
    "meta_salva_ok",
    "medida_edit",
    "meta_edit_visao"
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
        nome_equipe = st.text_input("Nome da Equipe")
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
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            equipe = st.selectbox("Equipe", df_eq["equipe"])
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
# TAB 3 – VISÃO GERAL (COM SEMANAS)
# ======================================================
with tabs[3]:
    st.subheader("🎯 Metas por Equipe")

    df_metas = carregar_metas()
    df_med = carregar_medidas()
    df_sem = carregar_semanas()

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
                st.markdown(f"### {meta['meta_crucial']}")
                st.markdown(f"**Indicador:** {meta['indicador']}")
                st.markdown(f"**Meta Final:** {meta['meta_final']}")
                st.markdown(f"**Prazo:** {meta['prazo']}")

                st.markdown("### 🧭 Medidas de Direção")
                medidas = df_med[df_med["meta_crucial"] == meta["meta_crucial"]]
                if medidas.empty:
                    st.info("Nenhuma medida cadastrada.")
                else:
                    for _, m in medidas.iterrows():
                        st.markdown(f"- {m['medida_direcao']} ({m['frequencia']})")

                # ===============================
                # 📅 CONTROLE SEMANAL
                # ===============================
                semana_passada = semana_anterior()
                semana_atual = inicio_semana()

                reg_passado = df_sem[
                    (df_sem["responsavel"] == meta["responsavel"]) &
                    (df_sem["meta_crucial"] == meta["meta_crucial"]) &
                    (df_sem["semana_ref"] == str(semana_passada.date()))
                ]

                reg_atual = df_sem[
                    (df_sem["responsavel"] == meta["responsavel"]) &
                    (df_sem["meta_crucial"] == meta["meta_crucial"]) &
                    (df_sem["semana_ref"] == str(semana_atual.date()))
                ]

                st.divider()
                st.markdown("## 📅 Semana")

                st.markdown(f"**Semana passada ({semana_passada.strftime('%d/%m/%Y')})**")
                if reg_passado.empty:
                    st.info("Nenhum registro.")
                else:
                    st.success(reg_passado.iloc[0]["feito"])

                st.markdown(f"**Próxima semana ({semana_atual.strftime('%d/%m/%Y')})**")
                planejado = st.text_area(
                    "O que será feito?",
                    value=reg_atual.iloc[0]["planejado"] if not reg_atual.empty else "",
                    key=f"semana_{idx}"
                )

                if st.button("Salvar compromisso", key=f"save_sem_{idx}"):
                    df_sem = df_sem[
                        ~(
                            (df_sem["responsavel"] == meta["responsavel"]) &
                            (df_sem["meta_crucial"] == meta["meta_crucial"]) &
                            (df_sem["semana_ref"] == str(semana_atual.date()))
                        )
                    ]

                    df_sem = pd.concat([df_sem, pd.DataFrame([{
                        "responsavel": meta["responsavel"],
                        "meta_crucial": meta["meta_crucial"],
                        "semana_ref": str(semana_atual.date()),
                        "feito": planejado,
                        "planejado": planejado
                    }])])

                    df_sem.to_csv(SEMANAS_PATH, index=False, encoding="utf-8-sig")
                    st.success("Compromisso semanal salvo.")
                    st.rerun()
