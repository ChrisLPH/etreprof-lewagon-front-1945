import streamlit as st
from utils import call_api

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

st.header("📬 Team Recommendations by Cluster")
st.markdown("Content recommendations based on real behavioral cluster analysis.")

# Load real clusters from API
clusters_data = call_api("/clusters")
if not clusters_data or not clusters_data.get("success"):
    st.error("Unable to load cluster information")
    st.stop()

clusters = clusters_data["clusters"]

# Create cluster options with real names
cluster_options = {
    int(k): v["name"]
    for k, v in clusters.items()
}

selected_cluster = st.selectbox(
    "Select cluster:",
    options=list(cluster_options.keys()),
    format_func=lambda x: f"Cluster {x} - {cluster_options[x]}"
)

if st.button("🎯 Show Recommendations", key="show_btn"):
    with st.spinner("Loading recommendations..."):
        response = call_api(f"/recommend/{selected_cluster}")

        if response and response.get("success"):
            rec_data = response["recommendations"]

            st.success(f"✅ Cluster: {rec_data['cluster_name']}")

            # ==================== CLUSTER INFO ====================
            st.markdown("---")
            st.markdown("## 📊 Cluster Overview")

            cluster_desc = rec_data.get("cluster_description", {})

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Cluster Size", cluster_desc.get("taille", "N/A"))

            with col2:
                st.metric("Activity Level", cluster_desc.get("activite_generale", "N/A"))

            # Additional cluster characteristics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Email Engagement:** {cluster_desc.get('engagement_email', 'N/A')}")

            with col2:
                st.write(f"**Content Usage:** {cluster_desc.get('usage_contenu', 'N/A')}")

            with col3:
                st.write(f"**Theme Diversity:** {cluster_desc.get('diversite_thematique', 'N/A')}")


            # ==================== RECOMMENDED CONTENTS ====================
            st.markdown("---")
            st.markdown("## 📚 Recommended Contents")

            recommended_contents = rec_data.get("recommended_contents", [])

            if recommended_contents:
                for i, content in enumerate(recommended_contents, 1):
                    with st.expander(f"{i}. {content.get('title', 'Untitled')} ({content.get('type', 'N/A')})"):

                        # Content details
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.write(f"**Type:** {content.get('type', 'N/A')}")

                            if content.get('reason'):
                                st.write(f"**Reason:** {content['reason']}")


                        with col2:
                            # Content characteristics
                            if content.get('is_priority_challenge'):
                                st.success("✅ Priority Challenge")
                                if content.get('challenge_type'):
                                    st.write(f"**Challenge:** {content['challenge_type']}")

                            if content.get('topic_match'):
                                st.info("🎯 Topic Match")

                            if content.get('id'):
                                st.caption(f"Content ID: {content['id']}")
            else:
                st.warning("No specific content recommendations available for this cluster.")



        else:
            st.error("❌ Failed to load recommendations.")

# ==================== VIEW ALL CLUSTERS ====================
st.markdown("---")
if st.button("📊 View All Clusters Overview"):
    st.markdown("## 🔄 Recommendations Overview for All Clusters")

    all_recommendations = {}

    # Load recommendations for all clusters
    for cluster_id in range(5):
        response = call_api(f"/recommend/{cluster_id}")
        if response and response.get("success"):
            all_recommendations[cluster_id] = response["recommendations"]

    if all_recommendations:
        # Create comparison table
        comparison_data = []

        for cluster_id, rec_data in all_recommendations.items():
            cluster_desc = rec_data.get("cluster_description", {})
            rec_strategy = rec_data.get("recommendation_strategy", {})

            comparison_data.append({
                "Cluster": f"{cluster_id}: {rec_data.get('cluster_name', 'Unknown')}",
                "Size": cluster_desc.get("taille", "N/A"),
                "Activity": cluster_desc.get("activite_generale", "N/A"),
                "Content Usage": cluster_desc.get("usage_contenu", "N/A"),
                "Recommendations": rec_data.get("total_recommendations", 0)
            })

        # Display comparison table
        import pandas as pd
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

        # Detailed view for each cluster
        st.markdown("### Detailed Recommendations by Cluster")

        for cluster_id, rec_data in all_recommendations.items():
            with st.expander(f"Cluster {cluster_id} - {rec_data.get('cluster_name', 'Unknown')}"):

                # Basic info
                cluster_desc = rec_data.get("cluster_description", {})
                st.write(f"**Size:** {cluster_desc.get('taille', 'N/A')}")
                st.write(f"**Activity:** {cluster_desc.get('activite_generale', 'N/A')}")
                st.write(f"**Content Usage:** {cluster_desc.get('usage_contenu', 'N/A')}")


                # Top recommended contents (first 2)
                recommended_contents = rec_data.get("recommended_contents", [])
                if recommended_contents:
                    st.markdown("**Top Recommendations:**")
                    for content in recommended_contents[:2]:
                        if content.get('title') and content.get('title') != 'Untitled':
                            priority_icon = "🎯" if content.get('is_priority_challenge') else "📄"
                            st.markdown(f"• {priority_icon} {content['title']} ({content.get('type', 'N/A')})")

                # System status
                st.caption(f"Status: {rec_data.get('system_status', 'N/A')}")

    else:
        st.error("❌ Failed to load recommendations for comparison.")

# ==================== HELP SECTION ====================
with st.expander("ℹ️ How to Use Team Recommendations", expanded=False):
    st.markdown("""
    ### Understanding the Recommendations

    **Cluster Description:**
    - Shows the behavioral profile of users in each cluster
    - Activity levels, content preferences, and engagement patterns

    **Recommendation Strategy:**
    - Algorithm approach for content selection
    - Popular topics within the cluster
    - Balance between engagement and professional development

    **Recommended Contents:**
    - Real content from the ÊtrePROF platform
    - Topic matches based on cluster preferences
    - Priority challenge content for professional growth

    **Team Actions:**
    - Use recommendations to create targeted campaigns
    - Export data for further analysis
    - Schedule content pushes to specific clusters

    ### Content Types:
    - **🎯 Topic Match:** Content popular within this cluster
    - **✅ Priority Challenge:** Professional development content
    - **📄 General:** Fallback recommendations
    """)

if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()
