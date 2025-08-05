import streamlit as st
from utils import call_api
import pandas as pd

# API connection test
api_status = call_api("/")
st.set_page_config(
    initial_sidebar_state="collapsed"  # Au lieu de "expanded"
)

st.title("👤 User Experience")
st.markdown("Discover your personalized learning profile and get content recommendations tailored to your teaching style.")

# Load clusters for examples
clusters_data = call_api("/clusters")
if not clusters_data or not clusters_data.get("success"):
    st.error("Unable to load cluster information")
    st.stop()

clusters = clusters_data["clusters"]

# Sample user IDs per cluster for demo
DEMO_USERS = {
    "0": [
        {"id": 12345, "name": "Marie D. - Primary Teacher (Paris)"},
        {"id": 23456, "name": "Sophie M. - Elementary (Marseille)"},
        {"id": 34567, "name": "Claire R. - Multi-level (Toulouse)"}
    ],
    "1": [
        {"id": 45678, "name": "Jean C. - Middle School (Lyon)"},
        {"id": 56789, "name": "Pierre L. - High School (Lille)"},
        {"id": 67890, "name": "Anne F. - Multi-level (Nantes)"}
    ],
    "2": [
        {"id": 78901, "name": "Thomas B. - Trainer (Bordeaux)"},
        {"id": 89012, "name": "Lucie T. - Expert Teacher (Strasbourg)"},
        {"id": 90123, "name": "Marc V. - Innovation Leader (Rennes)"}
    ],
    "3": [
        {"id": 91234, "name": "Emma S. - Elementary (Nice)"},
        {"id": 92345, "name": "Paul M. - Middle School (Montpellier)"},
        {"id": 93456, "name": "Julie N. - Primary (Dijon)"}
    ],
    "4": [
        {"id": 94567, "name": "Alex T. - High School (Grenoble)"},
        {"id": 95678, "name": "Sarah L. - Vocational (Amiens)"},
        {"id": 96789, "name": "David R. - College (Caen)"}
    ]
}

st.markdown("## 🔍 Find Your Profile")

# User selection interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Choose from examples")

    # Create options for selectbox
    options = ["Select an example user..."]
    user_mapping = {}

    for cluster_id, cluster_info in clusters.items():
        cluster_name = cluster_info["name"]

        # Add cluster header (disabled option)
        cluster_header = f"--- {cluster_name} ---"
        options.append(cluster_header)

        # Add users for this cluster
        if cluster_id in DEMO_USERS:
            for user in DEMO_USERS[cluster_id]:
                user_option = f"  {user['name']}"
                options.append(user_option)
                user_mapping[user_option] = user["id"]

    selected_option = st.selectbox(
        "Example users by cluster:",
        options=options,
        format_func=lambda x: x if not x.startswith("---") else x
    )

with col2:
    st.markdown("### Or enter your ID")
    custom_user_id = st.number_input(
        "Your personal user ID:",
        min_value=1,
        value=None,
        step=1,
        placeholder="Enter your ID...",
        help="Enter your ÊtrePROF user identifier"
    )

# Determine which user ID to use
user_id_to_search = None

if custom_user_id:
    user_id_to_search = custom_user_id
elif selected_option and selected_option in user_mapping:
    user_id_to_search = user_mapping[selected_option]

# Search button
search_btn = st.button("🔍 Discover My Profile", type="primary", disabled=user_id_to_search is None)

if search_btn and user_id_to_search:
    with st.spinner(f"Loading profile for user {user_id_to_search}..."):
        profile_result = call_api(f"/user/{user_id_to_search}/profile")

        if profile_result and profile_result.get("success"):
            profile_data = profile_result["data"]

            st.success(f"✅ Profile found for user {user_id_to_search}")

            # Display user profile (simplified version)
            st.markdown("---")
            st.markdown("## 📋 Your Teaching Profile")

            col1, col2, col3 = st.columns(3)

            profile_info = profile_data["profile"]
            cluster_info = profile_data["cluster"]

            with col1:
                anciennete = profile_info.get('anciennete', 'N/A')
                st.metric("Teaching Experience", f"{anciennete} years" if anciennete != 'N/A' else "N/A")

            with col2:
                academie = profile_info.get('academie', 'Not specified')
                st.metric("Academy", academie)

            with col3:
                cluster_name = cluster_info.get('name', 'Unknown')
                st.metric("Learning Profile", cluster_name)

            # Teaching levels
            if profile_info.get('niveaux_enseignes'):
                niveaux = profile_info['niveaux_enseignes']
                if isinstance(niveaux, list) and niveaux:
                    st.markdown(f"**Teaching levels:** {', '.join(niveaux).title()}")
                elif isinstance(niveaux, str):
                    st.markdown(f"**Teaching levels:** {niveaux.title()}")

            # Cluster description (user-friendly version)
            st.markdown("### 🎭 Your Learning Profile")
            cluster_id = cluster_info['id']
            if str(cluster_id) in clusters:
                cluster_details = clusters[str(cluster_id)]

                col1, col2 = st.columns(2)

                with col1:
                    st.info(f"**Profile:** {cluster_details['nom']}")
                    st.write(f"**Size:** {cluster_details['taille']}")
                    st.write(f"**Main level:** {cluster_details['niveau_principal']}")

                with col2:
                    st.write(f"**Experience:** {cluster_details['anciennete_moyenne']}")
                    st.write(f"**Activity:** {cluster_details['activite_generale']}")
                    st.write(f"**Content usage:** {cluster_details['usage_contenu']}")

            # Personalized recommendations
            st.markdown("---")
            st.markdown("## 🎯 Your Personalized Recommendations")

            recommendations_result = call_api(f"/recommend/{cluster_id}")

            if recommendations_result and recommendations_result.get("success"):
                rec_data = recommendations_result["recommendations"]

                st.markdown(f"### Based on your profile: {rec_data.get('cluster_name', cluster_name)}")

                col1, col2 = st.columns([2, 1])

                with col1:
                    # Show recommended contents if available
                    if "recommended_contents" in rec_data and rec_data["recommended_contents"]:
                        st.markdown("#### 📚 Recommended Content for You")

                        for i, content in enumerate(rec_data["recommended_contents"][:3], 1):
                            with st.expander(f"{i}. {content.get('title', 'Untitled')}"):
                                st.write(f"**Type:** {content.get('type', 'N/A')}")
                                if content.get('reason'):
                                    st.write(f"**Why this content:** {content['reason']}")
                                if content.get('url'):
                                    st.markdown(f"[📖 Read more]({content['url']})")
                    else:
                        # Fallback to strategy description
                        strategy = rec_data.get("recommendation_strategy", {})
                        if strategy.get("selection_strategy"):
                            st.markdown("#### 💡 Content Strategy for You")
                            st.info(strategy["selection_strategy"])

                with col2:
                    st.markdown("#### 🎯 Recommended Content Types")

                    # Try to get content types from recommendation strategy
                    strategy = rec_data.get("recommendation_strategy", {})
                    if strategy.get("top_topics"):
                        st.markdown("**Popular topics in your profile:**")
                        for topic in strategy["top_topics"][:3]:
                            st.markdown(f"• Topic {topic}")

                    # Show cluster description
                    cluster_desc = rec_data.get("cluster_description", {})
                    if cluster_desc:
                        st.markdown("**Your profile characteristics:**")
                        st.write(f"**Activity:** {cluster_desc.get('activite_generale', 'N/A')}")
                        st.write(f"**Content usage:** {cluster_desc.get('usage_contenu', 'N/A')}")
                        st.write(f"**Theme diversity:** {cluster_desc.get('diversite_thematique', 'N/A')}")

            else:
                st.warning("Unable to load personalized recommendations at the moment.")

            # Call to action
            st.markdown("---")
            st.markdown("### 🚀 Ready to explore more?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🏷️ Classify Your Content", key="classify_btn"):
                    st.switch_page("pages/3_Classify_Content.py")

            with col2:
                if st.button("👥 Explore All Profiles", key="clusters_btn"):
                    st.switch_page("pages/4_User_Clusters.py")

        elif profile_result and not profile_result.get("success"):
            st.error(f"❌ {profile_result.get('error', 'User not found')}")
            st.info("💡 Try with one of the example users above or verify your user ID.")

        else:
            st.error("❌ Unable to load user profile. Please try again.")

elif search_btn:
    st.warning("⚠️ Please select an example user or enter your personal ID.")

# Help section
with st.expander("❓ How does this work?", expanded=False):
    st.markdown("""
    ### About Your Learning Profile

    Your profile is determined by analyzing your interaction patterns on the ÊtrePROF platform:

    - **Activity level:** How often you engage with content
    - **Content preferences:** Types of resources you typically use
    - **Learning style:** Whether you prefer structured guides, quick tips, or in-depth materials

    Based on these patterns, we assign you to one of 5 behavioral profiles and provide personalized content recommendations.

    ### The 5 Learning Profiles:
    """)

    for cluster_id, cluster_info in clusters.items():
        st.markdown(f"**{cluster_info['name']}** ({cluster_info['taille']}) - {cluster_info['niveau_principal']}")

################################################################################################
# import streamlit as st
# from utils import call_api
# import pandas as pd

# # API connection test
# api_status = call_api("/")
# if api_status:
#     st.success(f"API connected: {api_status.get('status', 'running')}")
# else:
#     st.error("Cannot connect to API")
#     st.stop()

# st.title("👤 User Experience")
# st.header("Recommendations by Cluster")
# st.markdown("Personalized content strategies based on behavioral cluster profiles")

# clusters_data = call_api("/clusters")
# if clusters_data and clusters_data.get("success"):
#     cluster_options = {
#         int(k): v["name"]
#         for k, v in clusters_data["clusters"].items()
#     }

# selected_cluster_id = st.selectbox(
#     "Choose cluster:",
#     options=list(cluster_options.keys()),
#     format_func=lambda x: f"Cluster {x}: {cluster_options[x]}"
# )

# if st.button("Get recommendations", type="primary"):
#     with st.spinner("Generating recommendations..."):
#         recommendations = call_api(f"/recommend/{selected_cluster_id}")

#         if recommendations and recommendations.get("success"):
#             rec_data = recommendations["recommendations"]

#             st.markdown(f"### {rec_data['cluster_name']}")

#             col1, col2 = st.columns([2, 1])

#             with col1:
#                 st.markdown("#### Recommended Strategy")
#                 st.info(rec_data["strategy"])

#                 st.markdown("#### Cluster Description")
#                 st.write(rec_data["description"])

#                 st.markdown("#### Next Steps")
#                 st.write(rec_data.get("next_steps", "To be defined"))

#             with col2:
#                 st.markdown("#### Recommended Content Types")
#                 for content_type in rec_data["recommended_content_types"]:
#                     st.markdown(f"• {content_type}")

#                 st.markdown("#### Engagement Approach")
#                 st.write(rec_data["engagement_approach"])

#             if recommendations.get("status"):
#                 st.warning(f"{recommendations['status']}")

# # All recommendations overview
# if st.button("View all recommendations"):
#     st.markdown("### Strategies for all clusters")

#     all_recommendations = {}

#     for cluster_id in range(5):
#         rec_result = call_api(f"/recommend/{cluster_id}")
#         if rec_result and rec_result.get("success"):
#             all_recommendations[cluster_id] = rec_result["recommendations"]

#     if all_recommendations:
#         comparison_data = []
#         for cluster_id, rec in all_recommendations.items():
#             comparison_data.append({
#                 "Cluster": f"{cluster_id}: {rec['cluster_name']}",
#                 "Strategy": rec["strategy"],
#                 "Approach": rec["engagement_approach"],
#                 "Content Types": ", ".join(rec["recommended_content_types"][:2]) + "..."
#             })

#         df_comparison = pd.DataFrame(comparison_data)
#         st.dataframe(df_comparison, use_container_width=True)
