import streamlit as st
import pandas as pd
import json
import io
import os

# 🔹 IMPORTATION DE TES OUTILS LOCAUX
from agent.tools import analyze_all_candidates
from agent.utils import load_candidates

# -------- CONFIGURATION DE LA PAGE --------
st.set_page_config(page_title="AI HR Agent", layout="wide", page_icon="🤖")

# -------- CONFIGURATION DE L'IA (GROQ) --------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "TA_CLE_GROQ_ICI"

# -------- DESIGN PERSONNALISÉ (CSS CORRIGÉ) --------
st.markdown("""
<style>
    /* Fond général */
    .main { background-color: #0e1117; color: #f5f5f5; }

    /* Titre Principal */
    .main-title { color: #4CAF50; font-size: 3rem; font-weight: 700; margin-bottom: 10px; }

    /* STYLE DES RECTANGLES (METRICS) */
    div[data-testid="stMetric"] {
        background-color: #1c1f26;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #475569; /* ENTOURAGE GRIS */
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* TEXTE BLANC (LABEL ET VALEUR) */
    [data-testid="stMetricLabel"] > div, 
    [data-testid="stMetricValue"] > div {
        color: #ffffff !important;
    }

    /* COULEUR DES FLÈCHES (DELTA) */
    /* On ne force pas le blanc ici pour laisser le Rouge/Vert de Streamlit s'afficher */
    [data-testid="stMetricDelta"] > div {
        font-weight: bold !important;
    }

    /* Boutons personnalisés */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">🤖 AI HR Agent Dashboard</h1>', unsafe_allow_html=True)
st.write("Analyse prédictive de la stabilité des candidats.")


# -------- FONCTION DE GÉNÉRATION DE RAPPORT --------
def generate_report_text(result, file_name):
    report = f"""
    ===========================================
    RAPPORT D'ANALYSE RH - AGENT IA
    ===========================================
    Candidat : {file_name}
    Date : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

    SCORE DE RISQUE : {result['risk']}%
    SCORE DE STABILITÉ : {result['stability']}%

    FACTEURS CLÉS :
    {chr(10).join(['- ' + f for f in result['top_factors']])}

    DÉCISION :
    {'⚠️ ATTENTION : Risque élevé' if result['risk'] > 50 else '✅ PROFIL STABLE : Recommandé'}
    -------------------------------------------
    """
    return report


# -------- NAVIGATION --------
option = st.sidebar.selectbox("Menu", ["📊 Analyse Globale", "📂 Analyser un Candidat"])

# -------- OPTION 1 : ANALYSE GLOBALE --------
if option == "📊 Analyse Globale":
    st.subheader("📊 Monitoring de la base candidats")
    if st.button("🔄 Lancer l'analyse de la base"):
        candidates = load_candidates()
        if not candidates:
            st.info("Dossier 'candidats' vide.")
        else:
            results = analyze_all_candidates(candidates)
            avg_risk = sum(r["result"]["risk"] for r in results) / len(results)

            c1, c2 = st.columns(2)
            # Ici on utilise delta pour afficher la flèche
            c1.metric("Candidats", len(results))
            c2.metric("Risque Moyen", f"{round(avg_risk, 1)}%", delta=f"{round(avg_risk, 1)}%", delta_color="inverse")

            st.divider()
            for r in results:
                with st.expander(f"Dossier : {r['file']}"):
                    res = r["result"]
                    st.write(f"**Risque :** {res['risk']}% | **Stabilité :** {res['stability']}%")
                    st.download_button(label=f"Exporter Rapport {r['file']}", data=generate_report_text(res, r['file']),
                                       file_name=f"Analyse_{r['file']}.txt", key=r['file'])

# -------- OPTION 2 : UPLOAD CANDIDAT --------
elif option == "📂 Analyser un Candidat":
    st.subheader("📂 Analyser un nouveau profil")
    uploaded_file = st.file_uploader("Charger JSON", type="json")

    if uploaded_file:
        candidate_data = json.load(uploaded_file)
        if st.button("🚀 Analyser"):
            candidate_data["__file__"] = uploaded_file.name
            full_res = analyze_all_candidates([candidate_data])
            res = full_res[0]["result"]

            st.divider()
            col1, col2 = st.columns(2)

            # --- LES FLÈCHES DE COULEUR ---
            # delta_color="inverse" : Si le chiffre monte, c'est Rouge (car le risque est mauvais)
            col1.metric("Risque d'Attrition", f"{res['risk']}%", delta=f"{res['risk']}%", delta_color="inverse")

            # delta_color="normal" : Si le chiffre monte, c'est Vert (car la stabilité est bonne)
            col2.metric("Score de Stabilité", f"{res['stability']}%", delta=f"{res['stability']}%",
                        delta_color="normal")

            st.progress(int(res['stability']))

            st.write("### 🧠 Facteurs d'influence")
            factor_df = pd.DataFrame({"Facteurs": res["top_factors"], "Impact": [85, 70, 55]})
            st.bar_chart(factor_df.set_index("Facteurs"))

            if res['risk'] > 50:
                st.error("❌ Profil à risque élevé.")
            else:
                st.success("✅ Profil stable recommandé.")

            st.download_button(
                label="📥 Télécharger le Rapport Complet",
                data=generate_report_text(res, uploaded_file.name),
                file_name=f"Rapport_{uploaded_file.name}.txt"
            )