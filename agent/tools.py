import pandas as pd
import joblib
import shap

import warnings
warnings.filterwarnings("ignore")


# charger modèle
model = joblib.load("modele/attrition_model.pkl")
model_columns = joblib.load("modele/model_columns.pkl")

explainer = shap.Explainer(model)

def analyze_candidate(candidate):

    df = pd.DataFrame([candidate])

    # align columns
    for col in model_columns:
        if col not in df:
            df[col] = 0

    df = df[model_columns].astype(float)

    # prediction
    prob = model.predict_proba(df)[0][1]
    stability = 1 - prob

    # SHAP
    shap_values = explainer(df)
    values = shap_values.values[0,:,1]

    importance = pd.DataFrame({
        "feature": model_columns,
        "impact": values
    }).sort_values(by="impact", ascending=False)

    top_factors = importance.head(3)["feature"].tolist()

    return {
        "risk": round(prob*100,2),
        "stability": round(stability*100,2),
        "top_factors": top_factors
    }


# NEW FUNCTION
def analyze_all_candidates(candidates):

    results = []

    for c in candidates:
        file_name = c.pop("__file__")

        result = analyze_candidate(c)

        results.append({
            "file": file_name,
            "result": result
        })

    return results