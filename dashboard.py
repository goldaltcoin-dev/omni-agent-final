import streamlit as st
import httpx

def run_deep_audit():
    headers = {"apikey": st.secrets["SUPABASE_KEY"], "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"}
    
    # 1. DISCOVER TABLES
    # We fetch the list of tables we just mapped in the SQL view
    map_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/database_audit_map?select=*"
    schema_map = httpx.get(map_url, headers=headers).json()
    
    unique_tables = list(set([item['table_name'] for item in schema_map]))
    audit_results = []

    for table in unique_tables:
        # 2. SCAN FOR NULLS & DATA GAPS
        data_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/{table}?select=*"
        res = httpx.get(data_url, headers=headers).json()
        
        if not res:
            audit_results.append({"Table": table, "Status": "Empty", "Gaps": "No Data Found"})
            continue

        columns = list(res[0].keys())
        gaps = [col for col in columns if any(row.get(col) is None for row in res)]
        
        audit_results.append({
            "Table": table,
            "Total Rows": len(res),
            "Gaps Found": len(gaps),
            "Specific Null Fields": gaps[:5] # Show first 5 missing fields
        })
    
    return audit_results

st.title("🛡️ Omni-Agent: Universal System Audit")
if st.button("🔍 SCAN ALL TABLES & RELATIONS"):
    report = run_deep_audit()
    st.table(report)
    st.write("### 📋 Instructions for Next Step")
    st.info("Copy the 'Specific Null Fields' and the table names. Give them to me, and I will generate the historical news and technical specs for ALL of them.")
