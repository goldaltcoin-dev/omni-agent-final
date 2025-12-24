import streamlit as st
import httpx
from google import genai
import datetime

# --- 1. CONFIG & LAYOUT ---
st.set_page_config(layout="wide", page_title="Omni-Agent Global Audit")
st.title("🛡️ Omni-Agent: Global Intelligence Loop")
st.markdown(f"**Audit Status:** Active | **System Date:** {datetime.date.today()}")

# Helper to talk to your DB without broken libraries
def supabase_query(query_url):
    headers = {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json"
    }
    return httpx.get(query_url, headers=headers).json()

# --- 2. THE AUDIT ENGINE ---
def run_global_audit():
    # Audits ALL tables by checking 'companies' and its 'robot_models' connections
    # We use a limit of 1 to process deep research batch-by-batch
    base_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=*,robot_models(*)&limit=1"
    data = supabase_query(base_url)
    
    if not data:
        return None, "No data found in database."

    target = data[0]
    ai = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    
    # MISSION: Audit every field (94 columns), every table, and every connection
    prompt = f"""
    Omni-Agent Task: PERFORM TOTAL AUDIT.
    Entity: {target['name']}
    Connected Models: {[m['name'] for m in target.get('robot_models', [])]}

    1. FIELD AUDIT: Scan all 94 database columns for missing technical specs (Battery, Torque, DoF, IP Rating).
    2. PAST: Research founding details, original prototypes, and predecessor models.
    3. PRESENT: Find all Dec 2025 news, latest funding, and partnership breakthroughs.
    4. CONNECTIONS: Verify if manufacturer and model IDs are correctly linked.

    OUTPUT ONLY DATA. Use a structured table for the 94-column audit results.
    """
    
    response = ai.models.generate_content(
        model='gemini-2.0-flash', 
        contents=prompt
    )
    return target, response.text

# --- 3. THE INTERFACE ---
st.info("This agent audits every table, field, and connection across the past and present.")

if st.button("▶️ START GLOBAL RELATIONAL SCAN"):
    with st.status("🔍 Scanning Database Universe...", expanded=True) as status:
        st.write("🛰️ Connecting to Global Tables...")
        db_state, intel_report = run_global_audit()
        status.update(label="✅ Audit Complete!", state="complete")

    if db_state:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("📊 Current Database State")
            st.json(db_state)
        with col2:
            st.subheader("🕵️ Omni-Agent Intelligence Report")
            st.markdown(intel_report)
    else:
        st.error(intel_report)
