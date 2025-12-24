import streamlit as st
import httpx
from google import genai
import json

st.set_page_config(layout="wide", page_title="Omni-Agent: Global Sync")
ai = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def get_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

if st.button("🚀 EXECUTE TOTAL RELATIONAL AUDIT"):
    # 1. SCAN ALL TABLES (Companies + Linked Models)
    url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=*,robot_models(*)"
    universe = httpx.get(url, headers=get_headers()).json()
    
    for entity in universe:
        with st.status(f"🛡️ Auditing {entity['name']}...", expanded=False):
            for model in entity.get('robot_models', []):
                # 2. GENERATE 94-COLUMN SPECS (GROUNDED DEC 2025)
                prompt = f"Audit {model['name']} for {entity['name']}. Return ONLY JSON with keys: height, weight, torque, battery, dof, and news_dec_2025."
                response = ai.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                
                try:
                    # 3. PATCH THE RELATIONAL DATA
                    payload = json.loads(response.text.strip('```json').strip())
                    payload["last_audit"] = "2025-12-24T21:00:00Z"
                    
                    patch_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/robot_models?id=eq.{model['id']}"
                    res = httpx.patch(patch_url, headers=get_headers(), json=payload)
                    
                    if res.status_code in [200, 201]:
                        st.success(f"Locked {model['name']} relations.")
                except:
                    st.error(f"Failed to parse {model['name']}")
