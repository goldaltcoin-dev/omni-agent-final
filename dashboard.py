import streamlit as st
import httpx
from google import genai
import json

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Omni-Agent: Global Sync")
st.title("🛡️ Omni-Agent: Universal Relational Audit")

# Direct connection headers (Past, Present, and Future Sync)
def get_auth_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# --- 2. THE AUDIT ENGINE ---
def run_universal_scan():
    # Fetch all records across tables using relational joins
    base_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=*,robot_models(*)&order=last_audit.asc.nullslast"
    res = httpx.get(base_url, headers=get_auth_headers())
    
    if res.status_code != 200:
        st.error(f"Database Connection Failed: {res.text}")
        return []

    universe = res.json()
    ai = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    sync_logs = []

    for entity in universe:
        with st.status(f"Auditing {entity['name']} Universe...", expanded=False) as status:
            # MISSION: Audit every field (94 columns) + Past/Present Sync
            prompt = f"""
            PERFORM TOTAL RELATIONAL AUDIT for {entity['name']}.
            Tables: companies, robot_models (Linked via ID).
            
            1. 94-COLUMN SCAN: For models {[m['name'] for m in entity.get('robot_models', [])]}, find specific values for Torque(Nm), Battery(Wh), DoF, and Weight(kg).
            2. PAST: Verify founding history (2023-2024) and original prototypes.
            3. PRESENT: Identify Dec 2025 milestones, news, and funding.
            
            OUTPUT: Valid JSON only. Do not ask questions. Fill every field.
            """
            
            # Grounding with Google Search for "Present" 2025 news
            response = ai.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config={'tools': [{'google_search': {}}]}
            )
            
            try:
                # 3. Save Audit back to Database
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                audit_payload = json.loads(clean_json)
                audit_payload["last_audit"] = "2025-12-24T12:00:00Z" # Dec 2025 Timestamp
                
                update_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?id=eq.{entity['id']}"
                httpx.patch(update_url, headers=get_auth_headers(), json=audit_payload)
                
                status.update(label=f"✅ {entity['name']} Locked.", state="complete")
                sync_logs.append(f"Successfully audited {entity['name']} and linked models.")
            except Exception as e:
                status.update(label=f"❌ {entity['name']} Error.", state="error")
                sync_logs.append(f"Failed {entity['name']}: {str(e)}")
    
    return sync_logs

# --- 3. INTERFACE ---
st.info("Initiating 100% Audit of all tables, fields, and connections.")

if st.button("🚀 INITIATE UNIVERSAL RELATIONAL SYNC"):
    results = run_universal_scan()
    st.balloons()
    for log in results:
        st.write(log)
