import streamlit as st
from langchain_groq import ChatGroq
from agent.utils import load_candidates
from agent.tools import analyze_all_candidates
import json
import os

# --- CONFIGURATION DE L'IA (GROQ) ---
# On récupère la clé soit des "Secrets" de Streamlit (pour le web),
# soit d'une variable locale (pour tes tests)
try:
    # Sur le web (Streamlit Cloud)
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    # En local sur ton PC (remplace par ta clé pour tester)
    GROQ_API_KEY = "TA_CLE_GROQ_ICI"

# Initialisation du modèle Groq (Mistral via Groq)
llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name="mixtral-8x7b-32768"
)

def ask_llm(user_input):
    prompt = f"""
You are an AI HR agent.
Available tools:
1. analyze_all_candidates → analyze all candidates

Respond ONLY in JSON format like this:
{{
  "tool": "tool_name",
  "arguments": {{}}
}}

User request:
{user_input}
"""
    # .content est nécessaire avec Groq pour obtenir juste le texte
    response = llm.invoke(prompt)
    return response.content

# --- LE RESTE DE TON CODE (PARSER ET BOUCLE) ---

def parse_llm_output(response):
    try:
        # On nettoie un peu la réponse au cas où l'IA ajoute du texte avant/après le JSON
        start = response.find('{')
        end = response.rfind('}') + 1
        json_str = response[start:end]
        return json.loads(json_str)
    except:
        return None

# Note : On garde cette fonction pour que ton code ne plante pas,
# même si Streamlit remplace l'affichage.
def print_report_console(results):
    for r in results:
        print(f"Report for {r['file']} - Risk: {r['result']['risk']}%")

# Si tu veux encore pouvoir lancer main.py en console :
if __name__ == "__main__":
    print("=== AI HR Agent (Web Ready) ===")
    user_query = input("Ask something: ")
    res = ask_llm(user_query)
    decision = parse_llm_output(res)
    print(decision)