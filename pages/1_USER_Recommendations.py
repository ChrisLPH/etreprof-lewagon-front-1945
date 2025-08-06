import streamlit as st
from utils import call_api

# Configuration de la page
st.set_page_config(
    page_title="ÊtrePROF - User Recommendations",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }
    .profile-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1.5rem;
    }
    .content-divider {
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e1e4e8;
    }
</style>
""", unsafe_allow_html=True)

# Define cluster colors for consistency
cluster_colors = ['#5f2ec8', '#ffc373', '#45B7D1', '#96CEB4', '#FF6B6B']

# Main header
st.markdown("# 👤 Get Your Personalized Recommendations")
st.markdown("Enter your user ID to discover content tailored to your teaching profile.")

# API connection check
api_status = call_api("/")
if not api_status:
    st.error("❌ Cannot connect to API")
    st.stop()

# User input section
col1, col2 = st.columns([2, 1])

with col1:
    user_id = st.number_input(
        "Your ÊtrePROF User ID:",
        min_value=1,
        value=None,
        step=1,
        placeholder="Enter your ID...",
        help="Enter your ÊtrePROF user identifier"
    )

with col2:
    st.markdown("### Try an example")
    example_users = {
        "Select an example...": None,
        "Ben": 93697,
        "Ido": 149692,
        "Oksana": 59714,
        "Kalindi": 24194,
        "Florine": 72085
    }

    selected_example = st.selectbox(
        "Example users:",
        options=list(example_users.keys())
    )

    if selected_example != "Select an example...":
        user_id = example_users[selected_example]

# Get recommendations button
if st.button("🎯 Get My Recommendations", type="primary", disabled=user_id is None):
    if user_id:
        with st.spinner(f"Loading your personalized recommendations..."):
            # Get user profile directly - it now includes recommendations
            profile_result = call_api(f"/user/{user_id}/profile")

            if profile_result and profile_result.get("success"):
                profile_data = profile_result["data"]

                # Extract user information and recommendations
                cluster_info = profile_data["cluster"]
                cluster_id = int(cluster_info['id'])
                recommendations = profile_data["recommendations"]

                # Display header
                st.markdown(f"""
                <div class="profile-header">
                    <h3>✅ Your Personalized Content Recommendations</h3>
                </div>
                """, unsafe_allow_html=True)

                # Display recommended contents
                recommended_contents = recommendations.get("recommendations", [])

                if recommended_contents:
                    # Check if we have actual content
                    real_contents = [c for c in recommended_contents if c.get('id') is not None and c.get('title') != 'Untitled']

                    if real_contents:
                        # Create tabs for different content types
                        all_tab, articles_tab, tools_tab = st.tabs(["All Content", "Articles", "Tool Sheets"])

                        with all_tab:
                            for i, content in enumerate(real_contents, 1):
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.markdown(f"### {i}. {content.get('title', 'No title')}")
                                    st.write(f"**Type:** {content.get('type', 'N/A').replace('_', ' ').title()}")

                                    if content.get('reason'):
                                        st.write(f"💡 **Why this content:** {content['reason']}")

                                    if content.get('url') and content['url'] != '':
                                        st.markdown(f"[📖 Read this content]({content['url']})")

                                with col2:
                                    if content.get('is_priority_challenge'):
                                        st.success(f"✅ Priority Challenge: {content.get('priority_challenge', '')}")

                                st.markdown("<div class='content-divider'></div>", unsafe_allow_html=True)

                        with articles_tab:
                            articles = [c for c in real_contents if c.get('type') == 'article']
                            if articles:
                                for i, content in enumerate(articles, 1):
                                    st.markdown(f"### {i}. {content.get('title', 'No title')}")

                                    if content.get('reason'):
                                        st.write(f"💡 {content['reason']}")

                                    if content.get('url') and content['url'] != '':
                                        st.markdown(f"[📖 Read this article]({content['url']})")

                                    if content.get('is_priority_challenge'):
                                        st.success(f"✅ Priority Challenge: {content.get('priority_challenge', '')}")

                                    st.markdown("<div class='content-divider'></div>", unsafe_allow_html=True)
                            else:
                                st.info("No articles in your recommendations. Check the 'All Content' tab.")

                        with tools_tab:
                            tools = [c for c in real_contents if c.get('type') in ['fiche_outils', 'guide_pratique']]
                            if tools:
                                for i, content in enumerate(tools, 1):
                                    st.markdown(f"### {i}. {content.get('title', 'No title')}")

                                    if content.get('reason'):
                                        st.write(f"💡 {content['reason']}")

                                    if content.get('url') and content['url'] != '':
                                        st.markdown(f"[📥 Download this resource]({content['url']})")

                                    if content.get('is_priority_challenge'):
                                        st.success(f"✅ Priority Challenge: {content.get('priority_challenge', '')}")

                                    st.markdown("<div class='content-divider'></div>", unsafe_allow_html=True)
                            else:
                                st.info("No tool sheets in your recommendations. Check the 'All Content' tab.")
                    else:
                        st.warning("No specific content recommendations available at the moment.")
                else:
                    st.warning("No recommendations available for your profile.")
            else:
                error_message = profile_result.get('error', 'Unable to load your profile') if profile_result else 'Unable to connect to the server'
                st.error(f"❌ {error_message}")

                st.info("""
                **Possible solutions:**
                - Check your user ID and try again
                - Try one of our example users
                - Contact support if the problem persists
                """)

# Navigation
st.divider()
if st.button("🏠 Back to Home"):
    st.switch_page("Welcome.py")

# Footer
st.markdown("""
<div style='text-align: center; color: #666;'>
    ÊtrePROF x Le Wagon - #batch1945
</div>
""", unsafe_allow_html=True)
