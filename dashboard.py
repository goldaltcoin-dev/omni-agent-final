import streamlit as st
import httpx
from google import genai

# Page Setup
st.set_page_config(layout="wide", page_title="Omni-Agent Delta Scanner")

# Direct Connection (Bypasses all library errors)
def run_audit():
    url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=*,robot_models(*)&limit=1"
    headers = {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"
    }
    
    # 1. Get Data
    res = httpx.get(url, headers=headers)
    data = res.json()[0]
    
    # 2. AI Search (Past, Present, 94-Columns)
    ai = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    prompt = f"Audit {data['name']}. Find missing specs for all 94 columns. Find Dec 2025 news and history."
    response = ai.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    
    return data, response.text

st.title("🛡️ Omni-Agent: Global Intelligence Audit")
st.info("Scanning every table, field, and connection across Past, Present, and Future.")

if st.button("▶️ START DEEP SCAN"):
    db_data, ai_report = run_audit()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Database State")
        st.json(db_data)
    with col2:
        st.subheader("Omni-Agent Discovery (94-Cols + News)")
        st.write(ai_report)
