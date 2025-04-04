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
    # Initialize session state for delete confirmation
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = False
    
    # Show delete button or confirmation dialog
    if not st.session_state.delete_confirmation:
        if st.button("🗑️ Delete Campaign", type="secondary", use_container_width=True):
            st.session_state.delete_confirmation = True
            st.rerun()
    else:
        st.warning("⚠️ Are you sure you want to delete this campaign?")
        col3, col4 = st.columns(2)
        with col3:
            if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                delete_res = requests.delete(f"{API_BASE}/campaigns/{campaign_id}")
                if delete_res.status_code == 200:
                    st.success("Campaign deleted successfully!")
                    st.session_state.delete_confirmation = False
                    st.rerun()
                else:
                    st.error("Failed to delete campaign")
        with col4:
            if st.button("❌ Cancel", type="secondary", use_container_width=True):
                st.session_state.delete_confirmation = False
                st.rerun()

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

# Display posts in a grid layout
col1, col2 = st.columns(2)
current_col = col1

for i, post in enumerate(posts):
    with current_col:
        with st.container():
            # Create a card-like container with improved styling
            st.markdown(f'''\n                <div style='background-color: var(--background-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid rgba(49, 51, 63, 0.2); box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);'>\n                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>\n                        <h3 style='margin: 0; color: var(--text-color); font-size: 1.2rem; font-weight: 600;'>📝 Post {post['id']}</h3>\n                        <span style='background-color: {('#10B981' if post['status'].lower() == 'completed' else '#3B82F6')}; color: white; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.875rem; font-weight: 500;'>{post['status'].upper()}</span>\n                    </div>\n                    <div style='margin-bottom: 1rem;'>\n                        <strong style='color: var(--text-color); font-size: 0.875rem;'>Title</strong>\n                        <div style='font-size: 1.1rem; margin-top: 0.5rem; color: var(--text-color); font-weight: 500;'>{post.get('title', 'Untitled')}</div>\n                    </div>\n                    <div style='background-color: rgba(49, 51, 63, 0.05); border-radius: 8px; padding: 1rem; color: var(--text-color); font-size: 1rem; line-height: 1.5;'>\n                        {post['content'].replace('\n', '<br>')}\n                    </div>\n                </div>\n            ''', unsafe_allow_html=True)
    
    # Switch columns for next post
    current_col = col2 if current_col == col1 else col1