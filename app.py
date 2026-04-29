import streamlit as st
import requests
import pandas as pd
import json

API_URL = "http://127.0.0.1:8000"

# -------- PAGE CONFIG --------
st.set_page_config(page_title="AI HR Agent", layout="wide")

# -------- STYLE --------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1 {
    color: #4CAF50;
    text-align: center;
}
.block {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI HR Agent Dashboard")

# -------- SIDEBAR --------
option = st.sidebar.selectbox(
    "Navigation",
    ["📊 Analyze All Candidates", "📂 Upload Candidate"]
)

# -------- OPTION 1 --------
if option == "📊 Analyze All Candidates":

    st.subheader("📊 Global Analysis")

    if st.button("🚀 Run Analysis"):

        response = requests.get(f"{API_URL}/analyze-all")
        results = response.json()

        # KPI
        avg_risk = sum(r["result"]["risk"] for r in results) / len(results)

        col1, col2 = st.columns(2)
        col1.metric("👥 Total Candidates", len(results))
        col2.metric("⚠️ Average Risk", f"{round(avg_risk,2)} %")

        st.divider()

        # DETAILS
        for r in results:
            res = r["result"]

            with st.expander(f"📄 {r['file']}"):

                col1, col2 = st.columns(2)

                col1.metric("Risk", f"{res['risk']} %")
                col2.metric("Stability", f"{res['stability']} %")

                st.progress(int(res["stability"]))

                df = pd.DataFrame({
                    "Metric": ["Risk", "Stability"],
                    "Value": [res["risk"], res["stability"]]
                })

                st.bar_chart(df.set_index("Metric"))

                st.write("### 🔍 Top Factors")
                for f in res["top_factors"]:
                    st.write(f"- {f}")

                if res["risk"] > 50:
                    st.error("❌ Not Recommended")
                else:
                    st.success("✅ Recommended")

# -------- OPTION 2 --------
elif option == "📂 Upload Candidate":

    st.subheader("📂 Upload Candidate JSON")

    uploaded_file = st.file_uploader("Upload JSON file", type="json")

    if uploaded_file:

        candidate = json.load(uploaded_file)

        response = requests.post(
            f"{API_URL}/analyze-one",
            json=candidate
        )

        result = response.json()["result"]

        col1, col2 = st.columns(2)

        col1.metric("Risk", f"{result['risk']} %")
        col2.metric("Stability", f"{result['stability']} %")

        st.progress(int(result["stability"]))

        df = pd.DataFrame({
            "Metric": ["Risk", "Stability"],
            "Value": [result["risk"], result["stability"]]
        })

        st.bar_chart(df.set_index("Metric"))

        st.write("### 🔍 Top Factors")
        for f in result["top_factors"]:
            st.write(f"- {f}")

        if result["risk"] > 50:
            st.error("❌ Not Recommended")
        else:
            st.success("✅ Recommended")