import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ===============================
# Configuração da página
# ===============================
st.set_page_config(page_title="4DX - Gestão de Metas", layout="wide")

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
def init_csv(path, cols):
    if not path.exists():
        pd.DataFrame(columns=cols).to_csv(path, index=False, encoding="utf-8-sig")

init_csv(EQUIPES_PATH, ["equipe"])
init_csv(USUARIOS_PATH, ["nome", "email", "equipe"])
init_csv(METAS_PATH, ["equipe", "responsavel", "meta_crucial", "prazo", "indicador", "meta_final"])
init_csv(MEDIDAS_PATH, ["responsavel", "meta_crucial", "medida_direcao", "frequencia"])
init_csv(SEMANAS_PATH, ["responsavel", "meta_crucial", "semana_ref", "concluido", "planejado"])

# ===============================
# Funções
# ===============================
def carregar(p): 
    return pd.read_csv(p)

def inicio_semana(d=None):
    d = d or datetime.today()
    return (d - timedelta(days=d.weekday())) .date()

def semana_anterior():
    return inicio_semana() - timedelta(days=7)

# ===============================
# Estados globais (CRÍTICO)
# ===============================
for k in [
    "usuario_ok",
    "meta_ok",
    "meta_edit",
    "medida_edit"
]:
    if k not in st.session_state:
        st.session_state[k] = None

# ===============================
# UI
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
        equipe = st.text_input("Equipe")
        if st.form_submit_button("Salvar") and equipe:
            df = carregar(EQUIPES_PATH)
            if equipe not in df["equipe"].values:
                df = pd.concat([df, pd.DataFrame([{"equipe": equipe}])])
                df.to_csv(EQUIPES_PATH, index=False)
                st.success("Equipe cadastrada")
                st.rerun()

    st.divider()
    st.subheader("Cadastro de Usuários")

    if st.session_state.usuario_ok:
        st.success("Usuário cadastrado")
        st.session_state.usuario_ok = False

    df_eq = carregar(EQUIPES_PATH)
    if df_eq.empty:
        st.info("Cadastre uma equipe primeiro.")
    else:
        with st.form("form_user"):
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            equipe = st.selectbox("Equipe", df_eq["equipe"])
            if st.form_submit_button("Salvar") and nome and email:
                df = carregar(USUARIOS_PATH)
                if email not in df["email"].values:
                    df = pd.concat([df, pd.DataFrame([{
                        "nome": nome,
                        "email": email,
                        "equipe": equipe
                    }])])
                    df.to_csv(USUARIOS_PATH, index=False)
                    st.session_state.usuario_ok = True
                    st.rerun()

# ======================================================
# TAB 1 – META CRUCIAL
# ======================================================
with tabs[1]:
    st.subheader("Cadastrar Meta Crucial")

    if st.session_state.meta_ok:
        st.success("Meta salva com sucesso")
        st.session_state.meta_ok = False

    df_eq = carregar(EQUIPES_PATH)
    df_u = carregar(USUARIOS_PATH)
    df_m = carregar(METAS_PATH)

    if df_eq.empty or df_u.empty:
        st.info("Cadastre equipes e usuários primeiro.")
        st.stop()

    equipe = st.selectbox("Equipe", df_eq["equipe"])
    responsavel = st.selectbox(
        "Responsável",
        df_u[df_u["equipe"] == equipe]["nome"]
    )

    existente = df_m[df_m["responsavel"] == responsavel]

    with st.form("form_meta"):
        meta = st.text_area("Meta Crucial", existente.iloc[0]["meta_crucial"] if not existente.empty else "")
        indicador = st.text_input("Indicador", existente.iloc[0]["indicador"] if not existente.empty else "")
        meta_final = st.text_input("Meta Final", existente.iloc[0]["meta_final"] if not existente.empty else "")
        prazo = st.text_input("Prazo", existente.iloc[0]["prazo"] if not existente.empty else "")
        if st.form_submit_button("Salvar"):
            df_m = df_m[df_m["responsavel"] != responsavel]
            df_m = pd.concat([df_m, pd.DataFrame([{
                "equipe": equipe,
                "responsavel": responsavel,
                "meta_crucial": meta,
                "indicador": indicador,
                "meta_final": meta_final,
                "prazo": prazo
            }])])
            df_m.to_csv(METAS_PATH, index=False)
            st.session_state.meta_ok = True
            st.rerun()

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO (CRUD OK)
# ======================================================
with tabs[2]:
    st.subheader("🧭 Medidas de Direção")

    df_m = carregar(METAS_PATH)
    df_med = carregar(MEDIDAS_PATH)

    if df_m.empty:
        st.info("Cadastre uma meta primeiro.")
        st.stop()

    resp = st.selectbox("Responsável", df_m["responsavel"].unique())
    metas_resp = df_m[df_m["responsavel"] == resp]["meta_crucial"]

    if metas_resp.empty:
        st.info("Esse responsável não tem meta.")
        st.stop()

    meta = st.selectbox("Meta", metas_resp)

    medidas = df_med[
        (df_med["responsavel"] == resp) &
        (df_med["meta_crucial"] == meta)
    ]

    for idx, m in medidas.iterrows():
        c1, c2, c3 = st.columns([6, 1, 1])
        c1.write(f"{m['medida_direcao']} ({m['frequencia']})")

        if c2.button("✏️", key=f"edit_med_{idx}"):
            st.session_state.medida_edit = idx

        if c3.button("🗑️", key=f"del_med_{idx}"):
            df_med = df_med.drop(idx)
            df_med.to_csv(MEDIDAS_PATH, index=False)
            st.rerun()

        if st.session_state.medida_edit == idx:
            with st.form(f"form_edit_med_{idx}"):
                txt = st.text_input("Medida", m["medida_direcao"])
                freq = st.selectbox("Frequência", ["Diária", "Semanal", "Mensal", "Projeto"],
                                    index=["Diária", "Semanal", "Mensal", "Projeto"].index(m["frequencia"]))
                if st.form_submit_button("Salvar"):
                    df_med.loc[idx, ["medida_direcao", "frequencia"]] = [txt, freq]
                    df_med.to_csv(MEDIDAS_PATH, index=False)
                    st.session_state.medida_edit = None
                    st.rerun()

    st.divider()
    with st.form("form_nova_med"):
        novas = st.text_area("Nova(s) medida(s) – uma por linha")
        freq = st.selectbox("Frequência", ["Diária", "Semanal", "Mensal", "Projeto"])
        if st.form_submit_button("Adicionar"):
            df_med = pd.concat([df_med, pd.DataFrame([{
                "responsavel": resp,
                "meta_crucial": meta,
                "medida_direcao": t.strip(),
                "frequencia": freq
            } for t in novas.split("\n") if t.strip()])])
            df_med.to_csv(MEDIDAS_PATH, index=False)
            st.rerun()

# ======================================================
# TAB 3 – VISÃO GERAL + SEMANAS (ESTÁVEL)
# ======================================================
with tabs[3]:
    st.subheader("📊 Visão Geral")

    df_m = carregar(METAS_PATH)
    df_med = carregar(MEDIDAS_PATH)
    df_sem = carregar(SEMANAS_PATH)

    if df_m.empty:
        st.info("Nenhuma meta cadastrada.")
        st.stop()

    for equipe, grupo in df_m.groupby("equipe"):
        st.markdown(f"## 🏷️ {equipe}")

        for idx, m in grupo.iterrows():
            with st.expander(f"🎯 {m['meta_crucial']} — {m['responsavel']}"):
                st.markdown("### 🧭 Medidas")
                for _, md in df_med[df_med["meta_crucial"] == m["meta_crucial"]].iterrows():
                    st.write(f"- {md['medida_direcao']} ({md['frequencia']})")

        st.markdown("### 📅 Semana")

sem_pass = semana_anterior()
sem_atual = inicio_semana()

# ---------- REGISTROS ----------
reg_pass = df_sem[
    (df_sem["responsavel"] == m["responsavel"]) &
    (df_sem["meta_crucial"] == m["meta_crucial"]) &
    (df_sem["semana_ref"] == str(sem_pass))
]

reg_atual = df_sem[
    (df_sem["responsavel"] == m["responsavel"]) &
    (df_sem["meta_crucial"] == m["meta_crucial"]) &
    (df_sem["semana_ref"] == str(sem_atual))
]

# ---------- SEMANA PASSADA ----------
st.markdown(f"**Semana passada ({sem_pass.strftime('%d/%m/%Y')})**")

if reg_pass.empty:
    st.info("Nenhum compromisso registrado na semana passada.")
else:
    st.markdown(f"🎯 **Meta da semana:** {reg_pass.iloc[0]['planejado']}")
    st.success(f"Status: {reg_pass.iloc[0]['concluido']}")

# ---------- PRÓXIMA SEMANA ----------
st.markdown(f"**Próxima semana ({sem_atual.strftime('%d/%m/%Y')})**")

planejado = st.text_area(
    "Compromisso da próxima semana",
    reg_atual.iloc[0]["planejado"] if not reg_atual.empty else "",
    key=f"planejado_{idx}"
)

if st.button("Salvar compromisso", key=f"save_semana_{idx}"):
    # remove registro existente da semana atual
    df_sem = df_sem[
        ~(
            (df_sem["responsavel"] == m["responsavel"]) &
            (df_sem["meta_crucial"] == m["meta_crucial"]) &
            (df_sem["semana_ref"] == str(sem_atual))
        )
    ]

    df_sem = pd.concat([df_sem, pd.DataFrame([{
        "responsavel": m["responsavel"],
        "meta_crucial": m["meta_crucial"],
        "semana_ref": str(sem_atual),
        "concluido": "",
        "planejado": planejado
    }])])

    df_sem.to_csv(SEMANAS_PATH, index=False, encoding="utf-8-sig")
    st.success("Compromisso da próxima semana salvo.")
    st.rerun()
