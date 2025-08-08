import streamlit as st
from utils import call_api
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="ÊtrePROF - User Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }

    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .characteristic {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 3px;
        background-color: rgba(240, 240, 240, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Define cluster colors for consistency - SAME AS IN OTHER PAGES
cluster_colors = ['#5f2ec8', '#ffc373', '#45B7D1', '#96CEB4', '#FF6B6B']

# Header
st.markdown("# 🔍 User Analytics - Team Dashboard")
st.markdown("Deep dive into user behavior patterns, engagement metrics, and detailed profiling for team analysis.")

# API connection test
api_status = call_api("/")
if not api_status:
    st.error("❌ Cannot connect to API")
    st.stop()

# Load clusters for context
clusters_data = call_api("/clusters")
clusters = {}
if clusters_data and clusters_data.get("success"):
    clusters = clusters_data["clusters"]

# User ID input
col1, col2 = st.columns([3, 1])

with col1:
    user_id = st.number_input(
        "User ID to analyze:",
        min_value=1,
        value=93697,
        step=1,
        help="Enter the user ID for detailed behavioral analysis"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Vertical alignment
    analyze_btn = st.button("🔍 Analyze User", type="primary")

if analyze_btn:
    with st.spinner(f"Loading comprehensive analytics for user {user_id}..."):
        profile_result = call_api(f"/user/{user_id}/profile")

        if profile_result and profile_result.get("success"):
            profile_data = profile_result["data"]

            # Extract user information
            user_profile = profile_data["profile"]
            cluster_info = profile_data["cluster"]
            cluster_id = int(cluster_info['id'])  # Ensure cluster_id is integer
            recommendations = profile_data["recommendations"]

            # Success header with user ID and cluster color
            st.markdown(f"""
            <div class="profile-header" style="border-left: 8px solid {cluster_colors[cluster_id]};">
                <h2>✅ User {user_id} - {cluster_info['name']}</h2>
            </div>
            """, unsafe_allow_html=True)

            # ==================== OVERVIEW SECTION ====================
            st.markdown("### 📊 User Overview")

            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("User ID", user_id)

            with col2:
                anciennete = user_profile.get('anciennete')
                if anciennete:
                    st.metric("Experience", f"{anciennete} years")
                else:
                    st.metric("Experience", "Not specified")

            with col3:
                cluster_name = cluster_info.get('name', 'Unknown')
                st.metric("Cluster", f"{cluster_id}: {cluster_name}")

            with col4:
                degre = user_profile.get('degre')
                degre_labels = {1: "Primary", 2: "Secondary", 3: "Trainer"}
                if degre:
                    st.metric("Level", degre_labels.get(degre, "Unknown"))
                else:
                    st.metric("Level", "Not specified")

            # ==================== CLUSTER ANALYSIS ====================
            st.markdown("---")
            st.markdown("## 🎯 Cluster Analysis")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### Cluster Profile")

                cluster_desc = cluster_info["description"]

                # Use consistent cluster color
                st.markdown(f"""
                <div style="background-color: {cluster_colors[cluster_id]}; color: white; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem;">
                    <h4 style="margin: 0;">Cluster {cluster_id}: {cluster_name}</h4>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**Size:** {clusters[str(cluster_id)]['count']:,} users")
                st.markdown(f"**Main Level:** {cluster_desc['niveau_principal']}")
                st.markdown(f"**Average Experience:** {cluster_desc['anciennete_moyenne']}")

                st.markdown("#### Behavioral Characteristics")
                st.markdown(f"""
                <div class="characteristic">
                    <strong>Activity Level:</strong> {cluster_desc['activite_generale']}
                </div>
                <div class="characteristic">
                    <strong>Email Engagement:</strong> {cluster_desc['engagement_email']}
                </div>
                <div class="characteristic">
                    <strong>Content Usage:</strong> {cluster_desc['usage_contenu']}
                </div>
                <div class="characteristic">
                    <strong>Theme Diversity:</strong> {cluster_desc['diversite_thematique']}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("### User Position in All Clusters")

                # Get real cluster data from API
                if clusters:
                    cluster_names = []
                    cluster_counts = []
                    colors = []

                    for cid, cluster_info_detail in clusters.items():
                        cid_int = int(cid)  # Convert to integer for color indexing
                        cluster_names.append(cluster_info_detail['name'])

                        # Extract count
                        count = cluster_info_detail['count']
                        cluster_counts.append(count)

                        # Highlight user's cluster with gold color, use consistent colors for others
                        if cid_int == cluster_id:
                            colors.append('#FFD700')  # Gold for user's cluster
                        else:
                            colors.append(cluster_colors[cid_int])

                    # Create bar chart
                    fig_cluster = go.Figure(data=[
                        go.Bar(
                            x=cluster_names,
                            y=cluster_counts,
                            marker_color=colors,
                            text=[f"👤 This User" if int(cid) == cluster_id else "" for cid in clusters.keys()],
                            textposition="auto",
                            textfont=dict(size=12, color="white")
                        )
                    ])

                    fig_cluster.update_layout(
                        title=f"User {user_id} Position Across All Clusters",
                        xaxis_title="User Clusters",
                        yaxis_title="Number of Users",
                        showlegend=False,
                        height=400,
                        xaxis={'categoryorder': 'total descending'}  # Sort by size
                    )

                    # Add annotations for percentages
                    for i, (cid, cluster_info_detail) in enumerate(clusters.items()):
                        percentage = cluster_info_detail['percentage']
                        fig_cluster.add_annotation(
                            x=cluster_info_detail['name'],
                            y=cluster_counts[i],
                            text=f"{percentage:.1f}%",
                            showarrow=False,
                            yshift=10,
                            font=dict(size=10, color="gray")
                        )

                    st.plotly_chart(fig_cluster, use_container_width=True)

                    # Add cluster comparison table
                    st.markdown("#### Cluster Comparison")

                    comparison_data = []
                    for cid, cluster_detail in clusters.items():
                        cid_int = int(cid)
                        is_user_cluster = cid_int == cluster_id
                        comparison_data.append({
                            "Cluster": f"{'👤 ' if is_user_cluster else ''}{cluster_detail['name']}",
                            "Size": f"{cluster_detail['count']:,} ({cluster_detail['percentage']:.1f}%)",
                            "Activity": cluster_detail['description']['activite_generale'],
                            "Content Usage": cluster_detail['description']['usage_contenu'],
                            "Main Level": cluster_detail['description']['niveau_principal'].split('(')[0]
                        })

                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

                else:
                    st.error("Unable to load cluster data for visualization")

            # ==================== DETAILED PROFILE ====================
            st.markdown("---")
            st.markdown("## 👨‍🏫 Detailed Professional Profile")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Teaching Information")

                # Teaching levels
                niveaux = user_profile.get('niveaux_enseignes', [])
                if niveaux and len(niveaux) > 0:
                    if isinstance(niveaux, list):
                        st.write(f"**Teaching Levels:** {', '.join(niveaux).title()}")
                    else:
                        st.write(f"**Teaching Levels:** {niveaux.title()}")
                else:
                    st.write("**Teaching Levels:** Not specified")

                # Degree level
                if degre:
                    st.write(f"**Degree Level:** {degre_labels.get(degre, 'Unknown')}")
                else:
                    st.write("**Degree Level:** Not specified")

            with col2:
                st.markdown("### Geographic Information")

                academie = user_profile.get('academie')
                st.write(f"**Academy:** {academie}")

            # ==================== RECOMMENDED CONTENT ====================
            st.markdown("---")
            st.markdown("## 📚 Personalized Recommendations")

            # Display recommendations from the API
            if recommendations and "recommendations" in recommendations:
                recommended_contents = recommendations["recommendations"]
                if recommended_contents:
                    # Show strategy info if available
                    reasoning = recommendations.get("reasoning", {})
                    if reasoning:
                        st.info(f"**Strategy:** {reasoning.get('strategy', 'N/A')}")

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
                    st.warning("No recommendations available for this user.")
            else:
                st.warning("No recommendations data available.")

            # ==================== BEHAVIORAL INSIGHTS ====================
            st.markdown("---")
            st.markdown("## 🧠 Behavioral Insights")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### Risk Assessment")

                # Calculate churn risk based on cluster
                if cluster_id in [0, 4]:  # Low engagement clusters
                    risk_level = "High"
                    risk_color = "🔴"
                    risk_score = 75
                elif cluster_id == 3:  # Email-heavy
                    risk_level = "Medium"
                    risk_color = "🟡"
                    risk_score = 45
                else:  # Active clusters
                    risk_level = "Low"
                    risk_color = "🟢"
                    risk_score = 15

                st.metric("Churn Risk", f"{risk_color} {risk_level}", f"{risk_score}%")

                if risk_level == "High":
                    st.warning("⚠️ User shows low engagement patterns. Consider targeted re-engagement strategies.")
                elif risk_level == "Medium":
                    st.info("📧 User prefers email engagement. Consider newsletter optimization.")
                else:
                    st.success("✅ User shows healthy engagement patterns.")

            with col2:
                st.markdown("### Engagement Score")

                # Calculate engagement score based on cluster
                engagement_scores = {
                    0: 2.3,
                    1: 6.8,
                    2: 9.2,
                    3: 5.1,
                    4: 2.7
                }
                engagement = engagement_scores.get(cluster_id, 5.0)

                st.metric("Overall Engagement", f"{engagement}/10")

                # Progress bar
                st.progress(engagement / 10)

            with col3:
                st.markdown("### Recommendations Priority")

                strategy_map = {
                    0: ("Re-engagement", "🎯"),
                    1: ("Diversification", "🌟"),
                    2: ("Expert Content", "🚀"),
                    3: ("Platform Migration", "📱"),
                    4: ("Re-engagement", "🎯")
                }

                priority, priority_color = strategy_map.get(cluster_id, ("General Content", "📚"))

                st.metric("Strategy Focus", f"{priority_color} {priority}")



        elif profile_result and not profile_result.get("success"):
            st.error(f"❌ {profile_result.get('error', 'User not found')}")

            st.markdown("### 💡 Troubleshooting")
            st.info("""
            **Common issues:**
            - User ID doesn't exist in database
            - User has no interaction history
            - API synchronization delay

            **Try with known user IDs:** 6000, 12345, 45678, 89012
            """)

        else:
            st.error("❌ Unable to load user analytics. Please try again.")

# Help section for team
with st.expander("🔧 Team Analytics Guide", expanded=False):
    st.markdown("""
    ### How to Use This Dashboard

    **Purpose:** Deep behavioral analysis for team decision-making, not end-user consumption.

    **Key Metrics:**
    - **Churn Risk:** Likelihood of user becoming inactive
    - **Engagement Score:** Overall platform activity level
    - **Cluster Analysis:** Behavioral segmentation insights

    **Action Items:**
    - Use recommendations for targeted campaigns
    - Export reports for stakeholder presentations
    - Monitor high-risk users for intervention

    **Privacy Note:** This detailed view is for internal team use only.
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
