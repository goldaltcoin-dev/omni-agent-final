import streamlit as st
import httpx
from datetime import datetime

# Headers for Supabase
headers = {
    "apikey": st.secrets["SUPABASE_KEY"],
    "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

st.title("🛡️ Omni-Agent: Connection Tester")

if st.button("🚀 FORCE SYNC TO DATABASE"):
    # 1. Get the list of IDs
    url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=id,name"
    response = httpx.get(url, headers=headers)
    companies = response.json()
    
    st.write(f"Found {len(companies)} companies. Starting Force-Write...")

    for c in companies:
        # 2. Prepare the payload
        payload = {
            "last_audit": datetime.now().isoformat(),
            "description": "REAL DATA INJECTED DEC 24"
        }
        
        # 3. Try to PATCH the specific ID
        patch_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?id=eq.{c['id']}"
        patch_res = httpx.patch(patch_url, headers=headers, json=payload)
        
        if patch_res.status_code in [200, 204]:
            st.success(f"✅ Row Updated: {c['name']}")
        else:
            st.error(f"❌ Failed {c['name']}: {patch_res.text}")
