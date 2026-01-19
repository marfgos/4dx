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
# Inicialização
# ===============================
if not EQUIPES_PATH.exists():
    pd.DataFrame(columns=["equipe"]).to_csv(EQUIPES_PATH, index=False)

if not USUARIOS_PATH.exists():
    pd.DataFrame(columns=["nome","email","equipe"]).to_csv(USUARIOS_PATH, index=False)

if not METAS_PATH.exists():
    pd.DataFrame(columns=["equipe","responsavel","meta_crucial","prazo","indicador","meta_final"]).to_csv(METAS_PATH, index=False)

if not MEDIDAS_PATH.exists():
    pd.DataFrame(columns=["responsavel","meta_crucial","medida_direcao","frequencia"]).to_csv(MEDIDAS_PATH, index=False)

if not SEMANAS_PATH.exists():
    pd.DataFrame(columns=["responsavel","meta_crucial","semana_ref","concluido","planejado"]).to_csv(SEMANAS_PATH, index=False)

# ===============================
# Funções
# ===============================
def carregar(path): return pd.read_csv(path)

def inicio_semana(d=None):
    d = d or datetime.today()
    return (d - timedelta(days=d.weekday())).date()

def semana_anterior(): return inicio_semana() - timedelta(days=7)

# ===============================
# Estados
# ===============================
for k in ["meta_edit","medida_edit","usuario_ok","meta_ok"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ===============================
# UI
# ===============================
st.title("🎯 4DX – Gestão de Metas")

tabs = st.tabs(["👥 Equipes & Usuários","➕ Meta Crucial","➕ Medida de Direção","📊 Visão Geral"])

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO (EDITÁVEL)
# ======================================================
with tabs[2]:
    st.subheader("🧭 Medidas de Direção")

    df_m = carregar(METAS_PATH)
    df_med = carregar(MEDIDAS_PATH)

    if df_m.empty:
        st.warning("Cadastre uma meta antes.")
        st.stop()

    resp = st.selectbox("Responsável", df_m["responsavel"].unique())
    meta = st.selectbox("Meta", df_m[df_m["responsavel"]==resp]["meta_crucial"])

    medidas = df_med[(df_med["responsavel"]==resp)&(df_med["meta_crucial"]==meta)]

    for idx,m in medidas.iterrows():
        c1,c2,c3 = st.columns([6,1,1])
        c1.write(f"{m['medida_direcao']} ({m['frequencia']})")

        if c2.button("✏️", key=f"edit_med_{idx}"):
            st.session_state.medida_edit = idx

        if c3.button("🗑️", key=f"del_med_{idx}"):
            df_med = df_med.drop(idx)
            df_med.to_csv(MEDIDAS_PATH,index=False)
            st.rerun()

        if st.session_state.medida_edit == idx:
            with st.form(f"edit_form_{idx}"):
                txt = st.text_input("Medida", m["medida_direcao"])
                freq = st.selectbox("Frequência", ["Diária","Semanal","Mensal","Projeto"],
                                    index=["Diária","Semanal","Mensal","Projeto"].index(m["frequencia"]))
                if st.form_submit_button("Salvar"):
                    df_med.loc[idx,["medida_direcao","frequencia"]] = [txt,freq]
                    df_med.to_csv(MEDIDAS_PATH,index=False)
                    st.session_state.medida_edit = None
                    st.rerun()

    st.divider()
    with st.form("nova_med"):
        novas = st.text_area("Nova(s) medida(s) – uma por linha")
        freq = st.selectbox("Frequência",["Diária","Semanal","Mensal","Projeto"])
        if st.form_submit_button("Adicionar"):
            df_med = pd.concat([df_med,pd.DataFrame([{
                "responsavel":resp,
                "meta_crucial":meta,
                "medida_direcao":m.strip(),
                "frequencia":freq
            } for m in novas.split("\n") if m.strip()])])
            df_med.to_csv(MEDIDAS_PATH,index=False)
            st.rerun()

# ======================================================
# TAB 3 – VISÃO GERAL + SEMANAS
# ======================================================
with tabs[3]:
    st.subheader("📊 Visão Geral")

    df_m = carregar(METAS_PATH)
    df_med = carregar(MEDIDAS_PATH)
    df_sem = carregar(SEMANAS_PATH)

    for equipe,g in df_m.groupby("equipe"):
        st.markdown(f"## 🏷️ {equipe}")

        for idx,m in g.iterrows():
            with st.expander(f"🎯 {m['meta_crucial']} — {m['responsavel']}"):

                # -------- MEDIDAS (EDITÁVEIS AQUI TAMBÉM)
                st.markdown("### 🧭 Medidas de Direção")
                medidas = df_med[df_med["meta_crucial"]==m["meta_crucial"]]

                for midx,md in medidas.iterrows():
                    c1,c2,c3 = st.columns([6,1,1])
                    c1.write(f"{md['medida_direcao']} ({md['frequencia']})")

                    if c2.button("✏️", key=f"edit_v_{midx}"):
                        st.session_state.medida_edit = midx

                    if c3.button("🗑️", key=f"del_v_{midx}"):
                        df_med = df_med.drop(midx)
                        df_med.to_csv(MEDIDAS_PATH,index=False)
                        st.rerun()

                # -------- SEMANA (4DX REAL)
                st.markdown("### 📅 Semana")

                sem_pass = semana_anterior()
                sem_atual = inicio_semana()

                reg_pass = df_sem[(df_sem["responsavel"]==m["responsavel"]) &
                                  (df_sem["meta_crucial"]==m["meta_crucial"]) &
                                  (df_sem["semana_ref"]==str(sem_pass))]

                if reg_pass.empty:
                    status = st.radio("Semana passada concluída?",
                                      ["SIM","NAO"], horizontal=True,
                                      key=f"radio_{idx}")
                    if st.button("Confirmar semana passada", key=f"conf_{idx}"):
                        df_sem = pd.concat([df_sem,pd.DataFrame([{
                            "responsavel":m["responsavel"],
                            "meta_crucial":m["meta_crucial"],
                            "semana_ref":str(sem_pass),
                            "concluido":status,
                            "planejado":""
                        }])])
                        df_sem.to_csv(SEMANAS_PATH,index=False)
                        st.rerun()
                else:
                    st.success(f"Semana passada: {reg_pass.iloc[0]['concluido']}")

                planejar = st.text_area("Próxima semana – compromisso")
                if st.button("Salvar compromisso", key=f"prox_{idx}"):
                    df_sem = pd.concat([df_sem,pd.DataFrame([{
                        "responsavel":m["responsavel"],
                        "meta_crucial":m["meta_crucial"],
                        "semana_ref":str(sem_atual),
                        "concluido":"",
                        "planejado":planejar
                    }])])
                    df_sem.to_csv(SEMANAS_PATH,index=False)
                    st.rerun()
