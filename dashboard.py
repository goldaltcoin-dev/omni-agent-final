import streamlit as st
import httpx

# 1. THE METADATA CRAWLER
def get_schema_audit():
    headers = {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"
    }
    
    # This queries the Postgres system tables to find ALL your tables and columns
    schema_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/rpc/get_schema_metadata" 
    # NOTE: You may need to create a simple Postgres function for the above, 
    # or use the 'information_schema' via a direct SQL query.
    
    # FALLBACK: Manual scan of your known primary tables
    tables = ["companies", "robot_models", "technical_specs", "funding_rounds"]
    audit_report = []

    for table in tables:
        url = f"{st.secrets['SUPABASE_URL']}/rest/v1/{table}?select=*"
        res = httpx.get(url, headers=headers)
        data = res.json()
        
        # Check for NULLs or missing historical data
        missing_fields = [k for k, v in data[0].items() if v is None] if data else "No Data"
        audit_report.append({
            "Table": table,
            "Total Rows": len(data),
            "Missing/Null Fields": missing_fields
        })
    
    return audit_report

if st.button("🔍 RUN GLOBAL DISCOVERY SCAN"):
    report = get_schema_audit()
    st.write("### 📋 Global Audit Report")
    st.table(report)
    st.info("Copy the table above and give it to me to generate the missing input data.")
