import streamlit as st
from utils import call_api
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ÊtrePROF - Team Recommendations",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }
    .recommendation-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Define cluster colors for consistency
cluster_colors = ['#5f2ec8', '#ffc373', '#45B7D1', '#96CEB4', '#FF6B6B']

# Main header
st.markdown("# 📬 Team Recommendations by Cluster")
st.markdown("Content recommendations based on real behavioral cluster analysis.")

# API connection test
api_status = call_api("/")
if not api_status:
    st.error("❌ Cannot connect to API")
    st.stop()

# Load real clusters from API
with st.spinner("Loading cluster data..."):
    clusters_data = call_api("/clusters")
    if not clusters_data or not clusters_data.get("success"):
        st.error("Unable to load cluster information")
        st.stop()

    clusters = clusters_data["clusters"]

# Cluster selection section
st.markdown("## 🎯 Select a Cluster for Recommendations")

# Create cluster options with real names
cluster_options = {
    int(k): v["name"]
    for k, v in clusters.items()
}

col1, col2 = st.columns([3, 1])

with col1:
    selected_cluster = st.selectbox(
        "Choose a user segment to view tailored content recommendations:",
        options=list(cluster_options.keys()),
        format_func=lambda x: f"Cluster {x} - {cluster_options[x]}"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Vertical spacing
    # Use cluster color for button
    show_btn = st.button("🎯 Show Recommendations", key="show_btn", use_container_width=True)

# Process recommendations
if show_btn:
    with st.spinner("Loading recommendations..."):
        response = call_api(f"/recommend/{selected_cluster}")

        if response and response.get("success"):
            # Get recommendations data from new structure
            rec_data = response["recommendations"]

            # Success header with cluster name and color
            st.markdown(f"""
            <div style="background-color: {cluster_colors[selected_cluster]}; color: white; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                <h2>✅ Recommendations for Cluster {selected_cluster}: {cluster_options[selected_cluster]}</h2>
            </div>
            """, unsafe_allow_html=True)

            # ==================== CLUSTER INFO ====================
            st.markdown("## 📊 Cluster Overview")

            # Get cluster description from the clusters data
            cluster_desc = clusters[str(selected_cluster)]["description"]

            # Display metrics in 3 columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Cluster Size", f"{clusters[str(selected_cluster)]['count']:,} users")
                st.write(f"**Email Engagement:** {cluster_desc.get('engagement_email', 'N/A')}")

            with col2:
                st.metric("Activity Level", cluster_desc.get("activite_generale", "N/A"))
                st.write(f"**Content Usage:** {cluster_desc.get('usage_contenu', 'N/A')}")

            with col3:
                st.metric("Main Level", cluster_desc.get("niveau_principal", "Mixed").split('(')[0])
                st.write(f"**Theme Diversity:** {cluster_desc.get('diversite_thematique', 'N/A')}")

            # ==================== RECOMMENDATION STRATEGY ====================
            st.markdown("---")

            # Display recommendation strategy information
            reasoning = rec_data.get("reasoning", {})
            if reasoning:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🧠 Recommendation Strategy")
                    st.info(f"**{reasoning.get('strategy', 'Strategy information not available')}**")

                with col2:
                    st.markdown("### 📊 Content Availability")

                    avail_cols = st.columns(3)
                    with avail_cols[0]:
                        st.metric("Total Contents", reasoning.get("available_contents", 0))
                    with avail_cols[1]:
                        st.metric("Regular Contents", reasoning.get("normal_contents", 0))
                    with avail_cols[2]:
                        st.metric("Priority Contents", reasoning.get("priority_contents", 0))

            # ==================== RECOMMENDED CONTENTS ====================
            st.markdown("## 📚 Recommended Contents")

            recommended_contents = rec_data.get("recommendations", [])

            if recommended_contents:
                # Tabs for different views
                tab1, tab2 = st.tabs(["📄 List View", "🔍 Detailed View"])

                with tab1:
                    # Create a dataframe for the list view
                    content_list = []
                    for i, content in enumerate(recommended_contents, 1):
                        priority = "✅" if content.get('is_priority_challenge') else ""

                        content_list.append({
                            "#": i,
                            "Title": content.get('title', 'Untitled'),
                            "Type": content.get('type', 'N/A'),
                            "Priority": priority,
                            "Reason": content.get('reason', 'N/A')
                        })

                    df = pd.DataFrame(content_list)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                with tab2:
                    # Expandable detailed view
                    for i, content in enumerate(recommended_contents, 1):
                        with st.expander(f"{i}. {content.get('title', 'Untitled')} ({content.get('type', 'N/A')})"):
                            # Content details
                            col1, col2 = st.columns([2, 1])

                            with col1:
                                st.write(f"**Type:** {content.get('type', 'N/A')}")
                                st.write(f"**Source:** {content.get('source', 'N/A')}")

                                if content.get('reason'):
                                    st.write(f"**Reason:** {content['reason']}")

                                if content.get('url'):
                                    st.markdown(f"[View on ÊtrePROF]({content['url']})")

                            with col2:
                                # Content characteristics
                                if content.get('is_priority_challenge'):
                                    st.success(f"✅ Priority Challenge: {content.get('priority_challenge', 'Unknown')}")

                                if content.get('id'):
                                    st.caption(f"Content ID: {content['id']}")
            else:
                st.warning("No specific content recommendations available for this cluster.")
        else:
            st.error("❌ Failed to load recommendations.")

# ==================== VIEW ALL CLUSTERS ====================
st.markdown("---")
st.markdown("## 🔄 Cluster Comparison")

view_all_btn = st.button("📊 View All Clusters Overview", use_container_width=False)
if view_all_btn:
    with st.spinner("Loading data for all clusters..."):
        st.markdown("### Recommendations Overview for All Clusters")

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
                # Get cluster info from the clusters data
                cluster_info = clusters[str(cluster_id)]
                cluster_desc = cluster_info["description"]

                # Get reasoning data
                reasoning = rec_data.get("reasoning", {})

                comparison_data.append({
                    "Cluster": f"{cluster_id}: {cluster_options[cluster_id]}",
                    "Size": f"{cluster_info['count']:,}",
                    "Activity": cluster_desc.get("activite_generale", "N/A"),
                    "Content Usage": cluster_desc.get("usage_contenu", "N/A"),
                    "Recommendations": rec_data.get("total_recommendations", 0),
                    "Available Contents": reasoning.get("available_contents", 0)
                })

            # Display comparison table
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)

            # Detailed view for each cluster
            st.markdown("### Detailed Recommendations by Cluster")

            for cluster_id, rec_data in all_recommendations.items():
                # Use cluster color for expander
                with st.expander(f"Cluster {cluster_id} - {cluster_options[cluster_id]}"):
                    # Add colored header inside expander
                    st.markdown(f"""
                    <div style="background-color: {cluster_colors[cluster_id]}; color: white; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem;">
                        <h4 style="margin: 0;">Cluster {cluster_id}: {cluster_options[cluster_id]}</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Basic info
                    cluster_desc = clusters[str(cluster_id)]["description"]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Size:** {clusters[str(cluster_id)]['count']:,} users")
                        st.write(f"**Activity:** {cluster_desc.get('activite_generale', 'N/A')}")
                        st.write(f"**Content Usage:** {cluster_desc.get('usage_contenu', 'N/A')}")

                        # Strategy info
                        reasoning = rec_data.get("reasoning", {})
                        if reasoning:
                            st.write(f"**Strategy:** {reasoning.get('strategy', 'N/A')}")

                    with col2:
                        # Top recommended contents (first 2)
                        recommended_contents = rec_data.get("recommendations", [])
                        if recommended_contents:
                            st.markdown("**Top Recommendations:**")
                            for content in recommended_contents[:2]:
                                if content.get('title') and content.get('title') != 'Untitled':
                                    priority_icon = "✅" if content.get('is_priority_challenge') else "📄"
                                    st.markdown(f"• {priority_icon} {content['title']} ({content.get('type', 'N/A')})")

                    # System status
                    st.caption(f"Status: {rec_data.get('system_status', 'N/A')}")
        else:
            st.error("❌ Failed to load recommendations for comparison.")

st.divider()
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
    - **✅ Priority Challenge:** Professional development content focused on key educational challenges
    - **📄 General:** Content matched to cluster preferences and behavior patterns
    """)

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🎯 Back to Dashboard"):
        st.switch_page("pages/2_TEAM_Dashboard.py")
with col2:
    api_status = call_api("/")
    if api_status:
        st.success(f"✅ API connected: {api_status.get('status', 'running')}")
    else:
        st.error("❌ Cannot connect to API")
        st.stop()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    ÊtrePROF x Le Wagon - batch #1945
</div>
""", unsafe_allow_html=True)
