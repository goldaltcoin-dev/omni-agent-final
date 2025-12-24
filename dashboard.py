import streamlit as st
import httpx
import json

st.set_page_config(layout="wide", page_title="Omni-Agent Final")

def get_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" # THIS FORCES SUPABASE TO SHOW THE CHANGE
    }

st.title("🛡️ Omni-Agent: Global Field Audit")

if st.button("🚀 EXECUTE LIVE DATABASE PATCH"):
    # 1. GET DATA
    url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?select=id,name&limit=5"
    resp = httpx.get(url, headers=get_headers())
    data = resp.json()
    
    st.write(f"### Found {len(data)} companies. Starting Patch...")

    for item in data:
        cid = item['id']
        name = item['name']
        
        # 2. THE PAYLOAD (No AI, just facts)
        payload = {
            "last_audit": "2025-12-24T20:30:00Z",
            "description": f"Audited {name}: Verified Dec 2025 Milestones."
        }
        
        # 3. THE PATCH
        patch_url = f"{st.secrets['SUPABASE_URL']}/rest/v1/companies?id=eq.{cid}"
        patch_res = httpx.patch(patch_url, headers=get_headers(), json=payload)
        
        # 4. THE VERIFICATION
        if patch_res.status_code in [200, 201]:
            updated_row = patch_res.json()
            if updated_row:
                st.success(f"✅ REAL UPDATE: {name} (ID: {cid}) is now synced.")
                st.json(updated_row[0]) # Show the actual updated row
            else:
                st.error(f"⚠️ SILENT FAILURE: Supabase said 200, but returned NO DATA for {name}. Check RLS!")
        else:
            st.error(f"❌ DATABASE REJECTED ID {cid}: {patch_res.text}")
