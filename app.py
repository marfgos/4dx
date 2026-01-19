
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
    pd.DataFrame(columns=["nome", "email", "equipe"]).to_csv(USUARIOS_PATH, index=False, encoding="utf-8-sig")

if not METAS_PATH.exists():
    pd.DataFrame(columns=["equipe","responsavel","meta_crucial","prazo","indicador","meta_final"]).to_csv(METAS_PATH, index=False, encoding="utf-8-sig")

if not MEDIDAS_PATH.exists():
    pd.DataFrame(columns=["responsavel","meta_crucial","medida_direcao","frequencia"]).to_csv(MEDIDAS_PATH, index=False, encoding="utf-8-sig")

if not SEMANAS_PATH.exists():
    pd.DataFrame(columns=["responsavel","meta_crucial","semana_ref","feito","planejado"]).to_csv(SEMANAS_PATH, index=False, encoding="utf-8-sig")

# ===============================
# Funções
# ===============================
def carregar(path): return pd.read_csv(path)
def inicio_semana(d=None):
    d = d or datetime.today()
    return d - timedelta(days=d.weekday())

def semana_anterior(): return inicio_semana() - timedelta(days=7)

# ===============================
# Estados
# ===============================
for k in ["meta_edit_visao","usuario_ok","meta_ok"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ===============================
# UI
# ===============================
st.title("🎯 4DX – Gestão de Metas")

tabs = st.tabs(["👥 Equipes & Usuários","➕ Meta Crucial","➕ Medida de Direção","📊 Visão Geral"])

# ======================================================
# TAB 0 – EQUIPES & USUÁRIOS
# ======================================================
with tabs[0]:
    st.subheader("Cadastro de Equipes")
    with st.form("eq"):
        eq = st.text_input("Equipe")
        if st.form_submit_button("Salvar"):
            df = carregar(EQUIPES_PATH)
            if eq not in df["equipe"].values:
                df = pd.concat([df,pd.DataFrame([{"equipe":eq}])])
                df.to_csv(EQUIPES_PATH,index=False,encoding="utf-8-sig")
                st.success("Equipe salva")
                st.rerun()

    st.divider()
    st.subheader("Cadastro de Usuários")

    if st.session_state.usuario_ok:
        st.success("Usuário cadastrado com sucesso")
        st.session_state.usuario_ok = False

    df_eq = carregar(EQUIPES_PATH)
    with st.form("user"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        equipe = st.selectbox("Equipe",df_eq["equipe"])
        if st.form_submit_button("Salvar"):
            df = carregar(USUARIOS_PATH)
            if email not in df["email"].values:
                df = pd.concat([df,pd.DataFrame([{"nome":nome,"email":email,"equipe":equipe}])])
                df.to_csv(USUARIOS_PATH,index=False,encoding="utf-8-sig")
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

    equipe = st.selectbox("Equipe",df_eq["equipe"])
    resp = st.selectbox("Responsável",df_u[df_u["equipe"]==equipe]["nome"])

    existente = df_m[df_m["responsavel"]==resp]

    with st.form("meta"):
        meta = st.text_area("Meta",existente.iloc[0]["meta_crucial"] if not existente.empty else "")
        ind = st.text_input("Indicador",existente.iloc[0]["indicador"] if not existente.empty else "")
        final = st.text_input("Meta Final",existente.iloc[0]["meta_final"] if not existente.empty else "")
        prazo = st.text_input("Prazo",existente.iloc[0]["prazo"] if not existente.empty else "")
        if st.form_submit_button("Salvar"):
            df_m = df_m[df_m["responsavel"]!=resp]
            df_m = pd.concat([df_m,pd.DataFrame([{
                "equipe":equipe,"responsavel":resp,"meta_crucial":meta,
                "indicador":ind,"meta_final":final,"prazo":prazo
            }])])
            df_m.to_csv(METAS_PATH,index=False,encoding="utf-8-sig")
            st.session_state.meta_ok = True
            st.rerun()

# ======================================================
# TAB 2 – MEDIDA DE DIREÇÃO
# ======================================================
with tabs[2]:
    st.subheader("Cadastrar Medida de Direção")

    df_m = carregar(METAS_PATH)
    df_med = carregar(MEDIDAS_PATH)

    if df_m.empty:
        st.warning("Cadastre uma meta antes")
        st.stop()

    resp = st.selectbox("Responsável",df_m["responsavel"].unique())
    meta = st.selectbox("Meta",df_m[df_m["responsavel"]==resp]["meta_crucial"])

    st.markdown("### Medidas atuais")
    for i,m in df_med[(df_med["responsavel"]==resp)&(df_med["meta_crucial"]==meta)].iterrows():
        st.write(f"- {m['medida_direcao']} ({m['frequencia']})")

    with st.form("nova_med"):
        txt = st.text_area("Nova(s) medida(s) – uma por linha")
        freq = st.selectbox("Frequência",["Diária","Semanal","Mensal","Projeto"])
        if st.form_submit_button("Salvar"):
            novas = [{"responsavel":resp,"meta_crucial":meta,"medida_direcao":t.strip(),"frequencia":freq}
                     for t in txt.split("\n") if t.strip()]
            df_med = pd.concat([df_med,pd.DataFrame(novas)])
            df_med.to_csv(MEDIDAS_PATH,index=False,encoding="utf-8-sig")
            st.success("Medidas salvas")
            st.rerun()

# ======================================================
# TAB 3 – VISÃO GERAL + SEMANAS
# ======================================================
with tabs[3]:
    st.subheader("Metas por Equipe")

    df_m = carregar(METAS_PATH)
    df_med = carregar(MEDIDAS_PATH)
    df_sem = carregar(SEMANAS_PATH)

    for equipe,g in df_m.groupby("equipe"):
        st.markdown(f"## 🏷️ {equipe}")
        for idx,m in g.iterrows():
            with st.expander(f"🎯 {m['meta_crucial']} — {m['responsavel']}"):
                col1,col2 = st.columns([4,1])
                with col2:
                    if st.button("✏️ Editar",key=f"edit_{idx}"):
                        st.session_state.meta_edit_visao = idx

                if st.session_state.meta_edit_visao == idx:
                    with st.form(f"edit_{idx}"):
                        nova = st.text_area("Meta",m["meta_crucial"])
                        ind = st.text_input("Indicador",m["indicador"])
                        final = st.text_input("Meta Final",m["meta_final"])
                        prazo = st.text_input("Prazo",m["prazo"])
                        if st.form_submit_button("Salvar"):
                            df_m.loc[idx,["meta_crucial","indicador","meta_final","prazo"]] = [nova,ind,final,prazo]
                            df_m.to_csv(METAS_PATH,index=False,encoding="utf-8-sig")
                            st.session_state.meta_edit_visao = None
                            st.success("Meta atualizada")
                            st.rerun()
                else:
                    st.write(f"Indicador: {m['indicador']}")
                    st.write(f"Meta Final: {m['meta_final']}")
                    st.write(f"Prazo: {m['prazo']}")

                st.markdown("### 🧭 Medidas")
                for _,md in df_med[df_med["meta_crucial"]==m["meta_crucial"]].iterrows():
                    st.write(f"- {md['medida_direcao']} ({md['frequencia']})")

                st.markdown("### 📅 Semana")
                sem_pass = semana_anterior()
                sem_atual = inicio_semana()

                feito = st.text_area("Semana passada – o que foi feito?",
                    df_sem[(df_sem["responsavel"]==m["responsavel"]) &
                           (df_sem["meta_crucial"]==m["meta_crucial"]) &
                           (df_sem["semana_ref"]==str(sem_pass.date()))]["feito"].values[0]
                    if not df_sem.empty else ""
                )

                if st.button("Salvar semana passada",key=f"pass_{idx}"):
                    df_sem = df_sem[~((df_sem["responsavel"]==m["responsavel"]) &
                                      (df_sem["meta_crucial"]==m["meta_crucial"]) &
                                      (df_sem["semana_ref"]==str(sem_pass.date())))]
                    df_sem = pd.concat([df_sem,pd.DataFrame([{
                        "responsavel":m["responsavel"],
                        "meta_crucial":m["meta_crucial"],
                        "semana_ref":str(sem_pass.date()),
                        "feito":feito,
                        "planejado":""
                    }])])
                    df_sem.to_csv(SEMANAS_PATH,index=False,encoding="utf-8-sig")
                    st.success("Semana passada salva")
                    st.rerun()

                prox = st.text_area("Próxima semana – planejamento")
                if st.button("Salvar compromisso",key=f"prox_{idx}"):
                    df_sem = pd.concat([df_sem,pd.DataFrame([{
                        "responsavel":m["responsavel"],
                        "meta_crucial":m["meta_crucial"],
                        "semana_ref":str(sem_atual.date()),
                        "feito":"",
                        "planejado":prox
                    }])])
                    df_sem.to_csv(SEMANAS_PATH,index=False,encoding="utf-8-sig")
                    st.success("Compromisso salvo")
                    st.rerun()
