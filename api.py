from fastapi import FastAPI
from agent.tools import analyze_all_candidates

app = FastAPI()

@app.get("/")
def home():
    return {"message": "HR AI Agent API is running 🚀"}


# 🔹 Analyse tous les candidats (depuis fichiers)
@app.get("/analyze-all")
def analyze_all():
    from agent.utils import load_candidates

    candidates = load_candidates()
    results = analyze_all_candidates(candidates)

    return results


# 🔹 Analyse un candidat envoyé
@app.post("/analyze-one")
def analyze_one(candidate: dict):

    candidate["__file__"] = "uploaded_candidate.json"

    results = analyze_all_candidates([candidate])

    return results[0]