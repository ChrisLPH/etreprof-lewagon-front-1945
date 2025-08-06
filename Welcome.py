import streamlit as st

# Configuration de la page principale
st.set_page_config(
    page_title="ÊtrePROF - AI-Powered Teacher Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .big-button {
        background: linear-gradient(45deg, #1f4e79, #2d5aa0);
        color: white;
        padding: 1.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        display: block;
        transition: transform 0.2s;
    }
    .big-button:hover {
        transform: translateY(-2px);
    }
    .feature-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
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


# Choix d'expérience
st.markdown("### 🎭 Choose Your Experience")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 👤 User Experience")
    st.markdown("""
    **For Teachers**
    - Get personalized content recommendations
    - Discover resources matching your needs
    - Find content tailored to your teaching profile
    """)
    if st.button("👤 Access User Experience", key="user_btn", type="primary"):
        st.switch_page("pages/1_USER_Recommendations.py")

with col2:
    st.markdown("#### 🔬 Team Dashboard")
    st.markdown("""
    **For ÊtrePROF Team**
    - Analyze user clusters and behaviors
    - Classify content automatically
    - Generate personalized recommendations
    """)
    if st.button("🔬 Access Team Dashboard", key="team_btn", type="primary"):
        st.switch_page("pages/2_TEAM_Dashboard.py")

# Section "About ÊtrePROF"
with st.expander("**📖 About ÊtrePROF Project**", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🏫 What is ÊtrePROF?
        ÊtrePROF is a digital professional development platform that supports teachers in their profession,
        provided by Ecolhuma, a French non-profit organization.

        **Our mission**: Support teachers and school leaders so they can give all students the best opportunities.

        ### 🚀 From Library to AI Companion
        - **Today**: Content Library - Teachers search when they need
        - **Tomorrow**: Daily AI Companion - AI anticipates teacher needs
        """)

    with col2:
        st.markdown("### 📊 Key Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("👩‍🏫 Teachers", "200,000+")
            st.metric("📚 Contents", "2,000+")
            st.metric("🎓 Years Active", "7")

        with col2:
            st.metric("📊 Interactions", "12M+")
            st.metric("🎯 Clusters", "5")
            st.metric("🏷️ Topics", "16")

    # Section "Priority Challenges"
    st.markdown("### 🎯 Priority Challenges")
    st.markdown("""
    ÊtrePROF focuses on 5 priority challenges which are levers for a fairer and more equal school:
    """)

    challenge_cols = st.columns(5)

    with challenge_cols[0]:
        st.markdown("#### 🌟 Success for All Students")
        st.markdown("Ensuring every student can achieve their potential regardless of background.")

    with challenge_cols[1]:
        st.markdown("#### 🧠 Mental Health")
        st.markdown("Supporting well-being and psychological health in educational settings.")

    with challenge_cols[2]:
        st.markdown("#### 🤝 Inclusive School")
        st.markdown("Creating learning environments that welcome and support all students.")

    with challenge_cols[3]:
        st.markdown("#### 💪 Psychosocial Skills")
        st.markdown("Developing crucial interpersonal and emotional competencies.")

    with challenge_cols[4]:
        st.markdown("#### 🌱 Ecological Transition")
        st.markdown("Preparing students for environmental challenges and sustainable futures.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>ÊtrePROF</strong> - Your digital professional development platform </p>
    <p>Powered by <strong>Ecolhuma</strong> and <strong>Le Wagon - Batch #1945</strong>🌟</p>
</div>
""", unsafe_allow_html=True)
