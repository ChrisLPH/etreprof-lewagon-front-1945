import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="EtrePROF - ML Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colors
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }
    .css-1d391kg {
        background-color: #f4f8fe;
    }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = st.secrets["api"]["API_URL"]

def call_api(endpoint, method="GET", data=None):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# Header
st.markdown("# EtrePROF ML Dashboard")
st.markdown("Content classification, user clustering, and personalized recommendations")

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

# Navigation
st.sidebar.title("Navigation")
section = st.sidebar.selectbox(
    "Choose section:",
    ["Content Classification", "User Clusters", "Recommendations", "User Profile"]
)

# Section 1: Content Classification
if section == "Content Classification":
    st.header("Content Classification")
    st.markdown("Analyze markdown content to identify themes and priority challenges.")

    content_input = st.text_area(
        "Paste your markdown content here:",
        height=200,
        placeholder="# Teaching mathematics\n\nStrategies for differentiated learning..."
    )

    analyze_btn = st.button("Analyze Content", type="primary")

    if analyze_btn and content_input.strip():
        with st.spinner("Analyzing..."):
            try:
                url = f"{API_BASE_URL}/classify"
                response = requests.post(url, params={"content": content_input})

                if response.status_code == 200:
                    result = response.json()

                    if result and result.get("success"):
                        data = result["data"]

                        st.success("Analysis completed")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Main Theme", data["theme"])
                        with col2:
                            st.metric("Priority Challenge", data["defi"])

                        st.markdown("### Detailed Results")
                        st.json(data)
                else:
                    st.error(f"API Error: {response.status_code}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    elif analyze_btn:
        st.warning("Please enter content to analyze")

# Section 2: User Clusters
elif section == "User Clusters":
    st.header("User Clusters")
    st.markdown("4 behavioral clusters visualization and real-time recomputing")

    clusters_data = call_api("/clusters")

    if clusters_data and clusters_data.get("success"):
        clusters = clusters_data["clusters"]

        st.markdown("### Clusters Overview")

        cluster_names = []
        cluster_counts = []
        cluster_colors = ['#5f2ec8', '#ffc373', '#45B7D1', '#96CEB4']

        cols = st.columns(4)
        for i, (cluster_id, cluster_info) in enumerate(clusters.items()):
            cluster_names.append(cluster_info["name"])
            cluster_counts.append(cluster_info["profile"]["count"])

            with cols[i]:
                st.markdown(f"#### **{cluster_info['name']}**")
                st.markdown(f"#### {int(cluster_info['profile']['count'])} users")

        # Pie chart
        st.markdown("### Distribution")
        fig_pie = px.pie(
            values=cluster_counts,
            names=cluster_names,
            color_discrete_sequence=cluster_colors
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Detailed profiles
        st.markdown("### Behavioral Profiles")

        selected_cluster = st.selectbox(
            "Select cluster:",
            options=list(clusters.keys()),
            format_func=lambda x: f"Cluster {x}: {clusters[x]['name']}"
        )

        if selected_cluster:
            cluster_profile = clusters[selected_cluster]["profile"]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"#### {clusters[selected_cluster]['name']}")

                key_metrics = {
                    "Tool sheets": cluster_profile.get("nb_fiche_outils", 0),
                    "Practical guides": cluster_profile.get("nb_guide_pratique", 0),
                    "Total interactions": cluster_profile.get("total_interactions_x", 0),
                    "Content diversity": cluster_profile.get("diversite_contenus", 0)
                }

                for metric, value in key_metrics.items():
                    st.metric(metric, f"{value:.2f}" if isinstance(value, float) else value)

            with col2:
                categories = ["Tool sheets", "Guides", "Votes", "Comments", "Emails"]
                values = [
                    cluster_profile.get("nb_fiche_outils", 0),
                    cluster_profile.get("nb_guide_pratique", 0),
                    cluster_profile.get("nb_vote", 0),
                    cluster_profile.get("nb_comments", 0),
                    cluster_profile.get("nb_opened_mail", 0)
                ]

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=clusters[selected_cluster]['name'],
                    line_color=cluster_colors[int(selected_cluster)]
                ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(values) * 1.1] if max(values) > 0 else [0, 1]
                        )),
                    showlegend=False,
                    title=f"Profile - {clusters[selected_cluster]['name']}"
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # Recompute clusters
        st.markdown("### Recompute Clusters")

        if st.button("Recompute clusters", type="secondary"):
            with st.spinner("Recomputing... This may take a few minutes."):
                recompute_result = call_api("/clusters/recompute", method="POST")

                if recompute_result and recompute_result.get("success"):
                    st.success("Clusters recomputed successfully")

                    st.markdown("#### New distribution:")
                    distribution = recompute_result["cluster_distribution"]

                    cols = st.columns(4)
                    for i, (cluster_key, count) in enumerate(distribution.items()):
                        with cols[i]:
                            st.metric(f"Cluster {i}", f"{count:,}")

                    st.rerun()

# Section 3: Recommendations
elif section == "Recommendations":
    st.header("Recommendations by Cluster")
    st.markdown("Personalized content strategies based on behavioral cluster profiles")

    cluster_options = {
        0: "Balanced Users",
        1: "Email Specialists",
        2: "Super Users",
        3: "Inactive Users"
    }

    selected_cluster_id = st.selectbox(
        "Choose cluster:",
        options=list(cluster_options.keys()),
        format_func=lambda x: f"Cluster {x}: {cluster_options[x]}"
    )

    if st.button("Get recommendations", type="primary"):
        with st.spinner("Generating recommendations..."):
            recommendations = call_api(f"/recommend/{selected_cluster_id}")

            if recommendations and recommendations.get("success"):
                rec_data = recommendations["recommendations"]

                st.markdown(f"### {rec_data['cluster_name']}")

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown("#### Recommended Strategy")
                    st.info(rec_data["strategy"])

                    st.markdown("#### Cluster Description")
                    st.write(rec_data["description"])

                    st.markdown("#### Next Steps")
                    st.write(rec_data.get("next_steps", "To be defined"))

                with col2:
                    st.markdown("#### Recommended Content Types")
                    for content_type in rec_data["recommended_content_types"]:
                        st.markdown(f"• {content_type}")

                    st.markdown("#### Engagement Approach")
                    st.write(rec_data["engagement_approach"])

                if recommendations.get("status"):
                    st.warning(f"{recommendations['status']}")

    # All recommendations overview
    if st.button("View all recommendations"):
        st.markdown("### Strategies for all clusters")

        all_recommendations = {}

        for cluster_id in range(4):
            rec_result = call_api(f"/recommend/{cluster_id}")
            if rec_result and rec_result.get("success"):
                all_recommendations[cluster_id] = rec_result["recommendations"]

        if all_recommendations:
            comparison_data = []
            for cluster_id, rec in all_recommendations.items():
                comparison_data.append({
                    "Cluster": f"{cluster_id}: {rec['cluster_name']}",
                    "Strategy": rec["strategy"],
                    "Approach": rec["engagement_approach"],
                    "Content Types": ", ".join(rec["recommended_content_types"][:2]) + "..."
                })

            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)

# Section 4: User Profile
elif section == "User Profile":
    st.header("User Profile Lookup")
    st.markdown("Search for a specific user to view their cluster assignment and personalized recommendations")

    col1, col2 = st.columns([2, 1])

    with col1:
        user_id = st.number_input(
            "User ID:",
            min_value=1,
            value=12345,
            step=1,
            help="Enter the numeric user identifier"
        )

    with col2:
        search_btn = st.button("Search profile", type="primary")

    if search_btn:
        with st.spinner(f"Searching user profile {user_id}..."):
            profile_result = call_api(f"/user/{user_id}/profile")

            if profile_result and profile_result.get("success"):
                profile_data = profile_result["data"]

                st.success(f"User {user_id} found")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("User ID", profile_data["user_id"])

                with col2:
                    cluster_info = profile_data["cluster"]
                    st.metric("Cluster", f"{cluster_info['id']}: {cluster_info['name']}")

                with col3:
                    profile = profile_data["profile"]
                    engagement_score = (
                        profile.get("anciennete", 0) * 2 +
                        profile.get("degre", 0) * 10
                    ) / 10
                    st.metric("Engagement Score", f"{engagement_score:.1f}/10")

                st.markdown("### Detailed Profile")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Pedagogical Information")
                    profile_info = profile_data["profile"]

                    st.write(f"**Seniority:** {profile_info.get('anciennete', 'N/A')} years")
                    st.write(f"**Degree:** {profile_info.get('degre', 'N/A')}")
                    st.write(f"**Academy:** {profile_info.get('academie', 'N/A')}")

                    if profile_info.get('niveaux_enseignes'):
                        niveaux = profile_info['niveaux_enseignes']
                        if isinstance(niveaux, list):
                            st.write(f"**Teaching levels:** {', '.join(niveaux)}")
                        else:
                            st.write(f"**Teaching levels:** {niveaux}")

                with col2:
                    st.markdown("#### Personalized Recommendations")
                    recommendations = profile_data["recommendations"]

                    st.info(f"**Strategy:** {recommendations['strategy']}")

                    st.markdown("**Recommended content types:**")
                    for content_type in recommendations["recommended_content_types"]:
                        st.markdown(f"• {content_type}")

                # Cluster position visualization
                st.markdown("### Position in clusters")

                cluster_id = cluster_info['id']
                cluster_colors = ['#5f2ec8', '#ffc373', '#45B7D1', '#96CEB4']

                fig = go.Figure()

                clusters_sizes = [15234, 8756, 2341, 28408]
                cluster_names = ["Balanced Users", "Email Specialists", "Super Users", "Inactive Users"]

                fig.add_trace(go.Bar(
                    x=cluster_names,
                    y=clusters_sizes,
                    marker_color=[cluster_colors[i] if i != cluster_id else '#FFD700' for i in range(4)],
                    text=[f"Your cluster" if i == cluster_id else "" for i in range(4)],
                    textposition="auto"
                ))

                fig.update_layout(
                    title=f"User {user_id} position in clusters",
                    xaxis_title="Clusters",
                    yaxis_title="Number of users",
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

            elif profile_result and not profile_result.get("success"):
                st.error(f"{profile_result.get('error', 'User not found')}")
            else:
                st.error("Error searching profile")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    ÊtrePROF x Le Wagon - #batch1945
</div>
""", unsafe_allow_html=True)
