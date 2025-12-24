import streamlit as st
import httpx

def run_global_audit():
    headers = {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"
    }
    
    # Tables to scan for relations and history
    tables = ["companies", "robot_models", "technical_specs"]
    global_report = {}

    for table in tables:
        url = f"{st.secrets['SUPABASE_URL']}/rest/v1/{table}?select=*"
        res = httpx.get(url, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            if not data:
                global_report[table] = "⚠️ Table is EMPTY (No rows found)."
                continue
            
            # Analyze fields
            all_columns = list(data[0].keys())
            null_counts = {col: sum(1 for row in data if row.get(col) is None) for col in all_columns}
            
            global_report[table] = {
                "Row Count": len(data),
                "Columns Found": len(all_columns),
                "Gaps (Null Fields)": {k: v for k, v in null_counts.items() if v > 0}
            }
        else:
            global_report[table] = f"❌ Error: {res.status_code}"

    return global_report

st.title("🛡️ Omni-Agent: Universal Discovery")
if st.button("🔍 START GLOBAL TABLE SCAN"):
    with st.spinner("Analyzing all fields and relations..."):
        report = run_global_audit()
        st.json(report)
        st.info("Copy this JSON and paste it here. I will use it to provide your missing data.")
