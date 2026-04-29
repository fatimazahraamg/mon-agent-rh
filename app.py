import streamlit as st
import pandas as pd
import json
import os
from langchain_groq import ChatGroq

# 🔹 IMPORTATION DE TES OUTILS LOCAUX
# On importe directement les fonctions de tes fichiers agent/tools.py et agent/utils.py
from agent.tools import analyze_all_candidates
from agent.utils import load_candidates

# -------- CONFIGURATION DE L'IA (GROQ) --------
try:
    # Récupération de la clé API depuis les Secrets de Streamlit
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    # Pour tes tests en local uniquement
    GROQ_API_KEY = "TA_CLE_GROQ_ICI"

# -------- CONFIGURATION DE LA PAGE --------
st.set_page_config(page_title="IA Agent RH - Dashboard", layout="wide")

# Style personnalisé pour faire "App Professionnelle"
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #4CAF50;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI HR Agent Dashboard")
st.write("Analyse prédictive de la stabilité et du risque d'attrition des candidats.")

# -------- BARRE LATÉRALE (NAVIGATION) --------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/912/912214.png", width=100)
st.sidebar.title("Menu")
option = st.sidebar.selectbox(
    "Choisissez une action :",
    ["📊 Analyser les dossiers (JSON)", "📂 Upload un nouveau candidat"]
)

# -------- OPTION 1 : ANALYSE DES FICHIERS EXISTANTS --------
if option == "📊 Analyser les dossiers (JSON)":
    st.subheader("📊 Analyse globale des candidats en base")

    if st.button("🚀 Lancer l'analyse groupée"):
        with st.spinner("L'IA analyse les profils..."):
            # On charge les candidats depuis le dossier /candidats
            candidates = load_candidates()

            if not candidates:
                st.warning("Aucun fichier JSON trouvé dans le dossier 'candidats'.")
            else:
                # APPEL DIRECT à ta fonction (sans passer par une API externe)
                results = analyze_all_candidates(candidates)

                # Calcul des indicateurs clés (KPI)
                avg_risk = sum(r["result"]["risk"] for r in results) / len(results)

                col1, col2 = st.columns(2)
                col1.metric("👥 Total Candidats", len(results))
                col2.metric("⚠️ Risque Moyen", f"{round(avg_risk, 2)} %")

                st.divider()

                # Affichage détaillé par candidat
                for r in results:
                    res = r["result"]
                    with st.expander(f"📄 Dossier : {r['file']}"):
                        c1, c2 = st.columns(2)
                        c1.metric("Risque d'attrition", f"{res['risk']} %")
                        c2.metric("Score de stabilité", f"{res['stability']} %")

                        st.write("### 🔍 Facteurs clés d'influence")
                        for factor in res["top_factors"]:
                            st.write(f"- {factor}")

                        if res["risk"] > 50:
                            st.error("❌ Recommandation : Risque élevé (Attention)")
                        else:
                            st.success("✅ Recommandation : Profil stable")

# -------- OPTION 2 : UPLOAD D'UN NOUVEAU FICHIER --------
elif option == "📂 Upload un nouveau candidat":
    st.subheader("📂 Analyser un nouveau profil (JSON)")

    uploaded_file = st.file_uploader("Glissez un fichier JSON ici", type="json")

    if uploaded_file:
        # Lecture du fichier uploadé
        candidate_data = json.load(uploaded_file)

        if st.button("🔍 Analyser ce candidat"):
            with st.spinner("Analyse en cours..."):
                # On prépare la donnée comme attendu par ta fonction
                candidate_data["__file__"] = uploaded_file.name

                # APPEL DIRECT à ta fonction
                full_result = analyze_all_candidates([candidate_data])
                result = full_result[0]["result"]

                # Affichage du résultat
                st.balloons()

                col1, col2 = st.columns(2)
                col1.metric("Risque", f"{result['risk']} %")
                col2.metric("Stabilité", f"{result['stability']} %")

                st.progress(int(result["stability"]))

                st.write("### 🔍 Pourquoi ce score ?")
                for f in result["top_factors"]:
                    st.write(f"- {f}")

                if result["risk"] > 50:
                    st.error("❌ Avis : Ne pas retenir (Instabilité probable)")
                else:
                    st.success("✅ Avis : Profil à fort potentiel")