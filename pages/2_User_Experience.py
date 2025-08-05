import streamlit as st
from utils import call_api

# Configuration de la page
st.set_page_config(
    page_title="ÊtrePROF - User Experience",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

st.title("👤 Get Your Personalized Recommendations")
st.markdown("Enter your user ID to discover content tailored to your teaching profile.")

# User input
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
        "Marie (Primary Teacher)": 12345,
        "Jean (Middle School)": 45678,
        "Thomas (Trainer)": 78901,
        "Emma (Elementary)": 91234,
        "Alex (High School)": 94567
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
        with st.spinner(f"Loading recommendations for user {user_id}..."):

            # Get user profile to find cluster
            profile_result = call_api(f"/user/{user_id}/profile")

            if profile_result and profile_result.get("success"):
                profile_data = profile_result["data"]
                cluster_id = profile_data["cluster"]["id"]
                cluster_name = profile_data["cluster"]["name"]

                # Small delay to ensure data is properly loaded
                import time
                time.sleep(0.5)

        # Second spinner for recommendations
        with st.spinner("Loading your personalized recommendations..."):
            # Get recommendations for user's cluster
            recommendations_result = call_api(f"/recommend/{cluster_id}")

            if recommendations_result and recommendations_result.get("success"):
                rec_data = recommendations_result["recommendations"]

                st.success(f"✅ Recommendations for User {user_id}")

                st.markdown(f"## 📚 Content Recommended for You")
                st.info(f"Based on your profile: **{cluster_name}**")

                # Show recommended contents
                recommended_contents = rec_data.get("recommended_contents", [])

                if recommended_contents:
                    # Filter out placeholder content
                    real_contents = [c for c in recommended_contents if c.get('id') is not None and c.get('title') != 'Untitled']

                    if real_contents:
                        for i, content in enumerate(real_contents, 1):
                            with st.container():
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.markdown(f"### {i}. {content.get('title', 'No title')}")
                                    st.write(f"**Type:** {content.get('type', 'N/A').title()}")

                                    if content.get('reason'):
                                        st.write(f"💡 {content['reason']}")

                                    if content.get('url') and content['url'] != '':
                                        st.markdown(f"[📖 Read this content]({content['url']})")

                                with col2:
                                    if content.get('is_priority_challenge'):
                                        st.success("✅ Professional Development")
                                    if content.get('topic_match'):
                                        st.info("🎯 Popular Choice")

                            st.markdown("---")
                    else:
                        st.warning("No specific content recommendations available at the moment.")
                else:
                    st.warning("No recommendations available for your profile.")

            else:
                st.error("Unable to load recommendations. Please try again.")



# Navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("app.py")
