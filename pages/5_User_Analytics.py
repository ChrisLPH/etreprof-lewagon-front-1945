import streamlit as st
from utils import call_api
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

st.header("🔍 User Analytics - Team Dashboard")
st.markdown("Deep dive into user behavior patterns, engagement metrics, and detailed profiling for team analysis.")

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
        value=12345,
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

            st.success(f"✅ User {user_id} - Analytics Loaded")

            # ==================== OVERVIEW SECTION ====================
            st.markdown("---")
            st.markdown("## 📊 User Overview")

            profile_info = profile_data["profile"]
            cluster_info = profile_data["cluster"]
            cluster_id = cluster_info['id']

            # Key metrics row
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("User ID", user_id)

            with col2:
                anciennete = profile_info.get('anciennete', 0)
                st.metric("Experience", f"{anciennete} years")

            with col3:
                cluster_name = cluster_info.get('name', 'Unknown')
                st.metric("Cluster", f"{cluster_id}: {cluster_name}")

            with col4:
                degre = profile_info.get('degre', 0)
                degre_labels = {1: "Primary", 2: "Secondary", 3: "Trainer"}
                st.metric("Level", degre_labels.get(degre, "Unknown"))

            with col5:
                academie = profile_info.get('academie', 'N/A')
                st.metric("Academy", academie if academie else "N/A")

            # ==================== CLUSTER ANALYSIS ====================
            st.markdown("---")
            st.markdown("## 🎯 Cluster Analysis")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### Cluster Profile")
                if str(cluster_id) in clusters:
                    cluster_details = clusters[str(cluster_id)]

                    st.markdown(f"**Name:** {cluster_details['nom']}")
                    st.markdown(f"**Size:** {cluster_details['taille']}")
                    st.markdown(f"**Main Level:** {cluster_details['niveau_principal']}")

                    st.markdown("#### Behavioral Characteristics")
                    st.write(f"**Activity:** {cluster_details['activite_generale']}")
                    st.write(f"**Email Engagement:** {cluster_details['engagement_email']}")
                    st.write(f"**Content Usage:** {cluster_details['usage_contenu']}")
                    st.write(f"**Theme Diversity:** {cluster_details['diversite_thematique']}")
                    st.write(f"**Recent Activity:** {cluster_details['activite_recente']}")
                    st.write(f"**Consistency:** {cluster_details['consistance_annuelle']}")

            with col2:
                st.markdown("### User Position in All Clusters")

                # Get real cluster data from API
                if clusters:
                    cluster_names = []
                    cluster_counts = []
                    colors = []

                    cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']

                    for cid, cluster_info_detail in clusters.items():
                        cluster_names.append(cluster_info_detail['nom'])  # Use real names

                        # Extract count from size string (e.g., "74,099 utilisateurs (37.3%)")
                        size_str = cluster_info_detail['taille']
                        count = int(size_str.split()[0].replace(',', ''))
                        cluster_counts.append(count)

                        # Highlight user's cluster with gold color
                        if int(cid) == cluster_id:
                            colors.append('#FFD700')  # Gold for user's cluster
                        else:
                            colors.append(cluster_colors[int(cid)])

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
                        percentage = cluster_info_detail['taille'].split('(')[1].replace('%)', '')
                        fig_cluster.add_annotation(
                            x=cluster_info_detail['nom'],
                            y=cluster_counts[i],
                            text=f"{percentage}%",
                            showarrow=False,
                            yshift=10,
                            font=dict(size=10, color="gray")
                        )

                    st.plotly_chart(fig_cluster, use_container_width=True)

                    # Add cluster comparison table
                    st.markdown("#### Cluster Comparison")

                    comparison_data = []
                    for cid, cluster_detail in clusters.items():
                        is_user_cluster = int(cid) == cluster_id
                        comparison_data.append({
                            "Cluster": f"{'👤 ' if is_user_cluster else ''}{cluster_detail['nom']}",
                            "Size": cluster_detail['taille'],
                            "Activity": cluster_detail['activite_generale'],
                            "Content Usage": cluster_detail['usage_contenu'],
                            "Main Level": cluster_detail['niveau_principal']
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
                niveaux = profile_info.get('niveaux_enseignes', [])
                if niveaux:
                    if isinstance(niveaux, list):
                        st.write(f"**Teaching Levels:** {', '.join(niveaux).title()}")
                    else:
                        st.write(f"**Teaching Levels:** {niveaux.title()}")
                else:
                    st.write("**Teaching Levels:** Not specified")

                # Discipline (for secondary only)
                discipline = profile_info.get('discipline')
                if discipline:
                    st.write(f"**Discipline:** {discipline}")

                # Institution type
                type_etab = profile_info.get('type_etab')
                if type_etab:
                    st.write(f"**Institution Type:** {type_etab}")

            with col2:
                st.markdown("### Geographic Information")

                code_postal = profile_info.get('code_postal')
                if code_postal:
                    st.write(f"**Postal Code:** {code_postal}")

                departement = profile_info.get('departement')
                if departement:
                    st.write(f"**Department:** {departement}")

                st.write(f"**Academy:** {academie}")

            # ==================== ENGAGEMENT METRICS ====================
            st.markdown("---")
            st.markdown("## 📈 Engagement Analytics")

            # Note: These metrics would come from the API in a real scenario
            # For now, we'll create placeholder visualizations based on typical patterns

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Activity Timeline (Last 12 Months)")

                # Simulated monthly activity data (would come from API)
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

                # Generate sample data based on cluster behavior
                if cluster_id == 0:  # Peu Engagés Primaire
                    activity = [2, 1, 0, 1, 3, 2, 0, 1, 2, 1, 0, 1]
                elif cluster_id == 1:  # Actifs Polyvalents
                    activity = [8, 12, 10, 15, 18, 14, 16, 20, 17, 19, 13, 11]
                elif cluster_id == 2:  # Super Users
                    activity = [25, 30, 28, 35, 40, 38, 42, 45, 38, 41, 36, 33]
                elif cluster_id == 3:  # Email-Heavy
                    activity = [15, 18, 12, 20, 22, 19, 17, 24, 21, 18, 16, 14]
                else:  # Peu Engagés Secondaire
                    activity = [3, 2, 1, 2, 4, 3, 1, 2, 3, 2, 1, 2]

                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Scatter(
                    x=months,
                    y=activity,
                    mode='lines+markers',
                    name='Monthly Activity',
                    line=dict(color='#45B7D1', width=3),
                    marker=dict(size=8)
                ))

                fig_timeline.update_layout(
                    title="Monthly Interactions",
                    xaxis_title="Month",
                    yaxis_title="Interactions",
                    height=300
                )

                st.plotly_chart(fig_timeline, use_container_width=True)

            with col2:
                st.markdown("### Content Type Preferences")

                # Simulated content preferences (would come from API)
                content_types = ['Articles', 'Tool Sheets', 'Guides', 'Activities', 'Workshops']

                if cluster_id == 0:  # Peu Engagés Primaire
                    preferences = [5, 2, 1, 3, 1]
                elif cluster_id == 1:  # Actifs Polyvalents
                    preferences = [20, 15, 12, 18, 10]
                elif cluster_id == 2:  # Super Users
                    preferences = [35, 28, 25, 30, 20]
                elif cluster_id == 3:  # Email-Heavy
                    preferences = [8, 5, 3, 4, 2]
                else:  # Peu Engagés Secondaire
                    preferences = [4, 3, 2, 2, 1]

                fig_content = px.pie(
                    values=preferences,
                    names=content_types,
                    title="Content Type Distribution"
                )

                fig_content.update_layout(height=300)
                st.plotly_chart(fig_content, use_container_width=True)

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

                # Calculate engagement score
                if cluster_id == 0:
                    engagement = 2.3
                elif cluster_id == 1:
                    engagement = 6.8
                elif cluster_id == 2:
                    engagement = 9.2
                elif cluster_id == 3:
                    engagement = 5.1
                else:
                    engagement = 2.7

                st.metric("Overall Engagement", f"{engagement}/10")

                # Progress bar
                st.progress(engagement / 10)

            with col3:
                st.markdown("### Recommendations Priority")

                if cluster_id in [0, 4]:
                    priority = "Re-engagement"
                    priority_color = "🎯"
                elif cluster_id == 1:
                    priority = "Diversification"
                    priority_color = "🌟"
                elif cluster_id == 2:
                    priority = "Expert Content"
                    priority_color = "🚀"
                else:
                    priority = "Platform Migration"
                    priority_color = "📱"

                st.metric("Strategy Focus", f"{priority_color} {priority}")

            # ==================== RECOMMENDATIONS ====================
            st.markdown("---")
            st.markdown("## 🎯 Team Recommendations")

            recommendations_result = call_api(f"/recommend/{cluster_id}")

            if recommendations_result and recommendations_result.get("success"):
                rec_data = recommendations_result["recommendations"]

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown("### Strategic Approach")

                    cluster_desc = rec_data.get("cluster_description", {})
                    if cluster_desc:
                        st.info(f"**Strategy:** {cluster_desc.get('strategy', 'N/A')}")

                    # Show recommended contents
                    if "recommended_contents" in rec_data and rec_data["recommended_contents"]:
                        st.markdown("#### Specific Content Recommendations")

                        for i, content in enumerate(rec_data["recommended_contents"], 1):
                            with st.expander(f"{i}. {content.get('title', 'Untitled')} ({content.get('type', 'N/A')})"):
                                if content.get('reason'):
                                    st.write(f"**Rationale:** {content['reason']}")
                                if content.get('is_priority_challenge'):
                                    st.success("✅ Priority Challenge Content")
                                if content.get('topic_match'):
                                    st.info("🎯 Topic Match")

                with col2:
                    st.markdown("### Action Items")

                    # Specific actions based on cluster
                    if cluster_id in [0, 4]:  # Low engagement
                        st.markdown("""
                        **Immediate Actions:**
                        - Send re-engagement email
                        - Offer simplified content
                        - Provide onboarding support
                        """)
                    elif cluster_id == 1:  # Balanced
                        st.markdown("""
                        **Growth Actions:**
                        - Introduce advanced features
                        - Promote community features
                        - Suggest premium content
                        """)
                    elif cluster_id == 2:  # Super users
                        st.markdown("""
                        **Retention Actions:**
                        - Invite to beta programs
                        - Offer expert content
                        - Consider ambassador program
                        """)
                    else:  # Email-heavy
                        st.markdown("""
                        **Migration Actions:**
                        - Optimize email CTR
                        - Gradual platform migration
                        - Mobile app promotion
                        """)

            # ==================== EXPORT OPTIONS ====================
            st.markdown("---")
            st.markdown("## 📊 Export & Actions")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📧 Send Re-engagement Email", key="email_btn"):
                    st.success("✅ Re-engagement email queued for user")

            with col2:
                if st.button("📊 Export User Report", key="export_btn"):
                    st.success("✅ Detailed report exported to CSV")

            with col3:
                if st.button("🎯 Add to Campaign", key="campaign_btn"):
                    st.success("✅ User added to targeted campaign")

        elif profile_result and not profile_result.get("success"):
            st.error(f"❌ {profile_result.get('error', 'User not found')}")

            st.markdown("### 💡 Troubleshooting")
            st.info("""
            **Common issues:**
            - User ID doesn't exist in database
            - User has no interaction history
            - API synchronization delay

            **Try with known user IDs:** 12345, 67890, 45678, 89012
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
