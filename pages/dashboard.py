import streamlit as st
import requests

API_BASE = "https://techlocal-copy.onrender.com"

st.set_page_config(page_title="Campaign Dashboard", layout="wide")
st.title("📊 Campaign Dashboard")

# --- Select Campaign ---
st.header("Select Campaign")
res = requests.get(f"{API_BASE}/campaigns")
campaigns = res.json()
if not campaigns:
    st.info("No campaigns found. Please create a campaign first.")
    st.stop()

campaign_dict = {f"{c['id']} - {c['title']}": c['id'] for c in campaigns}
selected_label = st.selectbox("Campaign", list(campaign_dict.keys()))
campaign_id = campaign_dict[selected_label]

# Add delete button with confirmation
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🗑️ Delete Campaign", type="secondary", use_container_width=True):
        if st.button("⚠️ Confirm Delete", type="primary", use_container_width=True):
            delete_res = requests.delete(f"{API_BASE}/campaigns/{campaign_id}")
            if delete_res.status_code == 200:
                st.success("✅ Campaign deleted successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to delete campaign")

# --- View Themes ---
st.header("Campaign Themes")
themes = requests.get(f"{API_BASE}/themes/campaigns/{campaign_id}").json()
for t in themes:
    st.subheader(f"📘 Theme {t['id']} - {t['title']}")
    st.markdown(t['story'])
    if t['is_selected']:
        st.markdown("🟢 **Selected Theme**")

# --- View Posts ---
st.header("Content Posts")
posts = requests.get(f"{API_BASE}/content/campaigns/{campaign_id}/posts").json()
for post in posts:
    st.markdown(f"### 📝 Post {post['id']}")
    st.text_area("Content", value=post['content'], height=150, key=f"content_{post['id']}", disabled=True)
    st.markdown(f"**Status:** `{post['status']}`")
    st.divider()