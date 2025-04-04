import streamlit as st
import requests
import pandas as pd
from io import BytesIO

API_BASE = "https://techlocal-copy.onrender.com"

st.set_page_config(page_title="Campaign Dashboard", layout="wide")
st.title("📊 Thông tin campaign và bài viết")

# --- Select Campaign ---
st.header("Chọn Campaign để xem chi tiết")
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
st.header("Ý tưởng cho Pages")
themes = requests.get(f"{API_BASE}/themes/campaigns/{campaign_id}").json()
selected_themes = [t for t in themes if t['is_selected']]
if selected_themes:
    for t in selected_themes:
        st.subheader(f"📘 Theme {t['id']} - {t['title']}")
        st.markdown(t['story'])
        st.markdown("🟢 **Selected Theme**")
else:
    st.info("No theme has been selected for this campaign yet.")

# --- View Posts ---
st.header("Nội dung các bài viết")
posts = requests.get(f"{API_BASE}/content/campaigns/{campaign_id}/posts").json()

# Add Excel export functionality
if posts:
    # Create DataFrame for export
    df = pd.DataFrame([
        {
            'Post ID': post['id'],
            'Title': post.get('title', 'Untitled'),
            'Content': post['content'],
            'Status': post['status']
        } for post in posts
    ])
    
    # Create Excel file in memory
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    # Add download button
    st.download_button(
        label="📥 Download Posts as Excel",
        data=excel_buffer,
        file_name=f"campaign_{campaign_id}_posts.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.divider()

# Display posts
for post in posts:
    with st.container():
        st.markdown(f"### 📝 Post {post['id']}")
        st.markdown(f"**Title:** {post.get('title', 'Untitled')}")
        st.text_area("Content", value=post['content'], height=150, key=f"content_{post['id']}", disabled=True)
        st.markdown(f"**Status:** `{post['status']}`")
        st.divider()