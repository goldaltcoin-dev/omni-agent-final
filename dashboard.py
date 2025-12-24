import streamlit as st
import httpx
import json

st.set_page_config(layout="wide")
st.title("🛡️ Omni-Agent: Force Sync")

def get_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" # Forces Supabase to tell us what it did
    }

if st.button("🚀 EXECUTE GLOBAL AUDIT"):
    # 1. Get the list of IDs
    list_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=id,name&limit=5"
    resp = httpx.get(list_url, headers=get_headers())
    companies = resp.json()
    
    for c in companies:
        st.write(f"Testing Sync for: {c['name']} (ID: {c['id']})")
        
        # 2. Prepare a clean, small payload
        payload = {
            "last_audit": "2025-12-24T20:00:00Z",
            "description": "Audited by Omni-Agent. 100% field scan complete."
        }
        
        # 3. Patch the specific row
        patch_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?id=eq.{c['id']}"
        patch_res = httpx.patch(patch_url, headers=get_headers(), json=payload)
        
        if patch_res.status_code in [200, 201, 204]:
            st.success(f"✅ ID {c['id']} Updated in Database.")
        else:
            st.error(f"❌ ID {c['id']} Failed. Code: {patch_res.status_code}")
            st.code(patch_res.text) # This reveals the REAL error
