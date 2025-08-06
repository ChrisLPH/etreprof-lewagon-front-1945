import streamlit as st
from utils import call_api

# Page configuration
st.set_page_config(
    page_title="ÊtrePROF - Team Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }
    .dashboard-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        height: 100%;
    }
    .nav-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard header
st.markdown("""
<div class="dashboard-header">
    <h1>🎯 Team Dashboard</h1>
    <p>Management tools for ÊtrePROF platform administrators</p>
</div>
""", unsafe_allow_html=True)

# Dashboard overview
st.markdown("## 📌 Platform Overview")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Users", "198,895")

with col2:
    st.metric("📚 Content Items", "2,134")

with col3:
    st.metric("🏫 Active Academies", "31/31")

with col4:
    st.metric("📊 Clusters", "5")

# What you can do section
st.markdown("## 🛠️ Team Tools")

# Description
st.markdown("""
Explore the powerful suite of tools available to your team. These tools are designed to help you:
- Understand user behavior patterns
- Optimize content for better engagement
- Deliver personalized experiences
- Make data-driven decisions
""")

st.divider()

# Navigation section
st.markdown("### 📱 Quick Navigation")

# Feature buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown("#### 📋 Content Classification")
        st.markdown("Automatically classify content and identify themes.")
        if st.button("Analyze Content", key="content_btn", type="primary"):
            st.switch_page("pages/3_TEAM_Classify_Content.py")

with col2:
    with st.container():
        st.markdown("#### 👥 Users Clusters")
        st.markdown("Analyze behavioral segments and understand user patterns.")
        if st.button("Explore Clusters", key="clusters_btn", type="primary"):
            st.switch_page("pages/4_TEAM_User_Clusters.py")

with col3:
    with st.container():
        st.markdown("#### 📊 User Analytics")
        st.markdown("Deep dive into user behavior and engagement metrics.")
        if st.button("View Analytics", key="analytics_btn", type="primary"):
            st.switch_page("pages/5_TEAM_User_Analytics.py")

with col4:
    with st.container():
        st.markdown("#### 📬 Recommendations")
        st.markdown("Generate personalized content recommendations for users.")
        if st.button("View Recommendations", key="recommendations_btn", type="primary"):
            st.switch_page("pages/6_TEAM_Recommendations.py")

st.divider()

# User Experience
st.markdown("### 👤 User Experience Preview")
st.markdown("See the platform from your users' perspective.")

with st.container():
    st.markdown("#### Try the User Experience")
    st.markdown("Preview how teachers interact with the platform and view personalized recommendations.")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        As a teacher on ÊtrePROF, users can:
        - Discover content tailored to their teaching profile
        - Find resources matching their specific needs
        - Get recommendations based on their behavior cluster
        """)
    with col2:
        if st.button("👤 Try User View", key="user_btn", use_container_width=True):
            st.switch_page("pages/1_USER_Recommendations.py")
    st.markdown('</div>', unsafe_allow_html=True)

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"✅ API connected: {api_status.get('status', 'running')}")
else:
    st.error("❌ Cannot connect to API")
    st.stop()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    ÊtrePROF x Le Wagon - #batch1945
</div>
""", unsafe_allow_html=True)
