import streamlit as st

# Configuration de la page principale
st.set_page_config(
    page_title="ÊtrePROF - AI-Powered Teacher Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }

    .big-button {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem;
        text-decoration: none;
        display: block;
        transition: transform 0.2s;
    }

    .big-button:hover {
        transform: translateY(-2px);
        text-decoration: none;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎯 ÊtrePROF AI Platform</h1>
    <p>Fighting School Inequalities, One Algorithm at a Time!</p>
</div>
""", unsafe_allow_html=True)

# Toggle pour la présentation du projet
with st.expander("📖 About ÊtrePROF Project", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🏫 What is ÊtrePROF?
        ÊtrePROF is a digital professional development platform that supports teachers in their profession.

        **Our mission**: Support teachers and school leaders so they can give all students the best opportunities.

        ### 🚀 From Library to AI Companion
        - **Today**: Content Library - Teachers search when they need
        - **Tomorrow**: Daily AI Companion - AI anticipates teacher needs
        """)

    with col2:
        st.markdown("""
        ### 📊 Key Metrics
        """)



        st.metric("👩‍🏫 Teachers", "200,000+")
        st.metric("📚 Contents", "5,000+")
        st.metric("🎯 ML Clusters", "4")

        st.metric("📊 Interactions", "16M+")
        st.metric("🏷️ Topics", "16")
        st.metric("🎓 Years Active", "7")

st.markdown("---")

# Sélection du persona
st.markdown("### 🎭 Choose Your Experience")

col1, col2 = st.columns(2)

with col1:
    if st.button("👤 User Experience", key="user_btn"):
        st.switch_page("pages/2_User_Experience.py")
    st.markdown("""
    **For Teachers**
    - Get personalized content recommendations
    - Discover your learning profile
    - Find resources matching your needs
    """)

with col2:
    if st.button("👥 Team Dashboard", key="team_btn"):
        st.switch_page("pages/3_Classify_Content.py")
    st.markdown("""
    **For ÊtrePROF Team**
    - Classify new content automatically
    - Analyze user clusters and behaviors
    - Deep dive into user analytics
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>ÊtrePROF</strong> - Your digital professional development platform |
    Powered by <strong>Ecolhuma</strong> 🌟</p>
</div>
""", unsafe_allow_html=True)
