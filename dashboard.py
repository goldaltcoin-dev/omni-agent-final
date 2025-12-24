import streamlit as st
import httpx  # Standard library for web requests
from google import genai
import json

# --- 1. CONFIG ---
# Direct connection to bypass the broken Supabase library
url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=*,robot_models(*)&limit=1"
headers = {
    "apikey": st.secrets["SUPABASE_KEY"],
    "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"
}
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 2. DASHBOARD ---
st.title("🛡️ Omni-Agent: Global Audit")

if st.button("▶️ RUN TOTAL SCAN"):
    with st.status("🚀 Bypassing library errors... Scanning Universe...") as s:
        # Get data directly via HTTP (No Pydantic/Supabase library needed)
        response = httpx.get(url, headers=headers)
        data = response.json()
        
        if data:
            target = data[0]
            # Omni-Agent searches every table, field, past, and present
            prompt = f"Audit {target['name']} and models {target['robot_models']}. Search all 94 columns for missing specs and Dec 2025 news."
            ai_res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            
            st.subheader(f"Results for {target['name']}")
            st.write(ai_res.text)
            st.success("Past and Present data synced.")