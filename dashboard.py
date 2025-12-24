import streamlit as st
import httpx
from google import genai
import time

st.set_page_config(layout="wide", page_title="Omni-Agent: Global Audit")

# --- 1. CONFIG ---
def get_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# --- 2. GLOBAL SCAN LOGIC ---
def run_global_audit_loop():
    # 1. Fetch all companies that need an audit (ordered by oldest update)
    base_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=*,robot_models(*)&order=last_audit.asc"
    res = httpx.get(base_url, headers=get_headers())
    all_companies = res.json()
    
    ai = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    results = []

    for company in all_companies:
        with st.spinner(f"Auditing {company['name']}..."):
            # 2. Deep Intelligence Audit (94-Cols + Past + Dec 2025)
            prompt = f"""
            Audit {company['name']} and models {[m['name'] for m in company.get('robot_models', [])]}.
            - Technical Audit: Fill all 94 columns (Torque, Battery, DOF, Height, Weight).
            - Past: Find founding history and prototype evolution.
            - Present: Find Dec 2025 news (funding, deployments, milestones).
            - Link: Verify relational IDs are correct.
            Output as valid JSON only. Use one specific number for stats.
            """
            response = ai.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            
            try:
                # 3. Save to Database (Past, Present, and Future synced)
                import json
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                audit_payload = json.loads(clean_json)
                audit_payload["last_audit"] = "now()" # Update the audit timestamp
                
                update_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?id=eq.{company['id']}"
                httpx.patch(update_url, headers=get_headers(), json=audit_payload)
                results.append(f"✅ {company['name']} Synced.")
            except Exception as e:
                results.append(f"❌ {company['name']} Failed: {str(e)}")
    
    return results

# --- 3. THE DASHBOARD ---
st.title("🛡️ Omni-Agent: Universal Relational Scan")
st.info("Currently Auditing: Every table and connection in the database universe.")

if st.button("🚀 INITIATE GLOBAL SYNC"):
    sync_results = run_global_audit_loop()
    st.balloons()
    for r in sync_results:
        st.write(r)
