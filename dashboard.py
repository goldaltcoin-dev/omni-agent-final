import streamlit as st
import httpx
from google import genai
import json
import re

st.set_page_config(layout="wide")
st.title("🛡️ Omni-Agent: Universal Auditor")

def clean_json(raw_text):
    # This removes the ```json and other markdown garbage that causes "Failed to parse"
    return re.sub(r'```json|```', '', raw_text).strip()

def get_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

if st.button("🚀 RUN GLOBAL AUDIT"):
    # 1. Fetch EVERYTHING (Relations included)
    url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=id,name,robot_models(id,name)"
    universe = httpx.get(url, headers=get_headers()).json()
    
    ai = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    for entity in universe:
        st.write(f"### Checking {entity['name']} Universe...")
        
        for model in entity.get('robot_models', []):
            # MISSION: Grounded Dec 2025 Audit
            prompt = f"AUDIT {model['name']} by {entity['name']}. Return ONLY raw JSON with keys: torque_nm, battery_wh, dof, weight_kg, news_dec_2025."
            
            try:
                response = ai.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                raw_data = clean_json(response.text)
                payload = json.loads(raw_data)
                
                # Add the audit timestamp (Dec 24, 2025)
                payload["last_audit"] = "2025-12-24T21:30:00Z"
                
                # 2. PATCH the table
                patch_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/robot_models?id=eq.{model['id']}"
                res = httpx.patch(patch_url, headers=get_headers(), json=payload)
                
                if res.status_code in [200, 204]:
                    st.success(f"✅ RELATIONAL SYNC: {model['name']} (ID: {model['id']}) locked.")
                else:
                    st.error(f"DB Reject: {res.text}")
                    
            except Exception as e:
                st.error(f"Failed to parse {model['name']}: {str(e)}")
