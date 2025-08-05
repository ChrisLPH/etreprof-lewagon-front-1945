import streamlit as st
from utils import call_api

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

st.set_page_config(
    initial_sidebar_state="expanded"
)

st.header("Team dashboard")

st.markdown("""
            What you can do here ?
            - View user profiles
            - Analyze content performance
            - Explore user behavior
            """)

st.markdown("### Features")
st.markdown("""
- **User Profiles**: View detailed user profiles and their engagement metrics.
- **Content Analysis**: Analyze the performance of your content and identify key themes.
- **User Behavior**: Explore user behavior patterns and engagement trends.
""")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👤 User Experience", key="user_btn"):
        st.switch_page("pages/2_User_Experience.py")
with col2:
    if st.button("📊 Content Analysis", key="content_btn"):
        st.switch_page("pages/3_Classify_Content.py")
with col3:
    if st.button("👥 User Clusters", key="clusters_btn"):
        st.switch_page("pages/4_User_Clusters.py")

with st.expander("User Analytics", expanded=True):
    if st.button("📈 User Analytics", key="analytics_btn"):
        st.switch_page("pages/5_User_Analytics.py")
