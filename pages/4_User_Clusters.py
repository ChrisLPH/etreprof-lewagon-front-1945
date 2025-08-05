import streamlit as st
from utils import call_api
import plotly.express as px
import plotly.graph_objects as go

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

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
