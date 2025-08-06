import streamlit as st
from utils import call_api
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="ÊtrePROF - User Clusters",
    page_icon="👥",
    layout="wide",
)

# Custom CSS to improve appearance
st.markdown("""
<style>
    .cluster-header {
        text-align: center;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .cluster-count {
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .characteristic {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 3px;
        background-color: rgba(240, 240, 240, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Main title with icon
st.markdown("# 👥 User Clusters")
st.markdown("Analysis of 5 behavioral user clusters on ÊtrePROF platform")

# API connection verification
api_status = call_api("/")
if not api_status:
    st.error("❌ Unable to connect to the API")
    st.stop()

# Retrieving cluster data
with st.spinner("Loading cluster data..."):
    clusters_data = call_api("/clusters")

if clusters_data and clusters_data.get("success"):
    clusters = clusters_data["clusters"]

    # Clusters overview
    st.markdown("## 📊 Clusters Overview")

    cluster_names = []
    cluster_counts = []
    cluster_colors = ['#5f2ec8', '#ffc373', '#45B7D1', '#96CEB4', '#FF6B6B']

    # Cluster cards
    cols = st.columns(5)
    for i, (cluster_id, cluster_info) in enumerate(clusters.items()):
        cluster_names.append(cluster_info["name"])
        cluster_counts.append(cluster_info["count"])

        with cols[i]:
            # Dynamic style based on cluster color
            st.markdown(f"""
            <div class="cluster-header" style="background-color: {cluster_colors[int(cluster_id)]}; color: white;">
                {cluster_info["name"]}
            </div>
            <div class="cluster-count">
                {int(cluster_info["count"]):,}
            </div>
            """, unsafe_allow_html=True)

    # Distribution chart
    st.markdown("### 🍰 User Distribution")

    fig_pie = px.pie(
        values=cluster_counts,
        names=cluster_names,
        color_discrete_sequence=cluster_colors,
        hole=0.4,  # Donut chart for a more modern look
        labels={'label': 'Cluster', 'value': 'Number of users'}
    )

    # Legend to the side as requested
    fig_pie.update_layout(
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1),
        margin=dict(t=30, b=10, l=10, r=120)
    )

    # Clean presentation without text in pie slices
    fig_pie.update_traces(
        textposition='none'
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    # Separator
    st.markdown("---")

    # Detailed profiles
    st.markdown("## 🔍 Detailed Cluster Analysis")

    # Cluster selection with colored badges
    cluster_options = {k: f"{v['name']} ({v['percentage']}%)" for k, v in clusters.items()}

    selected_cluster = st.selectbox(
        "Select a cluster to analyze in detail:",
        options=list(cluster_options.keys()),
        format_func=lambda x: cluster_options[x]
    )

    if selected_cluster:
        profile = clusters[selected_cluster]["profile"]
        description = clusters[selected_cluster]["description"]

        # Section header with cluster color
        st.markdown(f"""
        <h3 style="background-color: {cluster_colors[int(selected_cluster)]}; color: white; padding: 0.8rem; border-radius: 5px;">
            Cluster {selected_cluster}: {clusters[selected_cluster]['name']}
        </h3>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])

        with col1:
            # Main metrics
            st.subheader("📈 Key Indicators")

            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

            with metrics_col1:
                st.metric("Size", f"{profile['size']:,} users")
                st.metric("Percentage", f"{profile['percentage']:.1f}%")

            with metrics_col2:
                st.metric("Average Experience", description["anciennete_moyenne"])
                st.metric("Main Level", description["niveau_principal"].split('(')[0])

            with metrics_col3:
                st.metric("Thematic Diversity", description["diversite_thematique"])
                st.metric("General Activity", description["activite_generale"])

            # Behavioral characteristics
            st.subheader("🧠 Behavioral Characteristics")

            char_col1, char_col2 = st.columns(2)

            with char_col1:
                st.markdown(f"""
                <div class="characteristic">
                    <strong>General Activity:</strong> {description['activite_generale']}
                </div>
                <div class="characteristic">
                    <strong>Email Engagement:</strong> {description['engagement_email']}
                </div>
                """, unsafe_allow_html=True)

            with char_col2:
                st.markdown(f"""
                <div class="characteristic">
                    <strong>Content Usage:</strong> {description['usage_contenu']}
                </div>
                <div class="characteristic">
                    <strong>Thematic Diversity:</strong> {description['diversite_thematique']}
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # Teaching levels distribution chart
            st.subheader("🏫 Teaching Levels")

            niveaux = description["repartition_niveaux"]
            level_names = list(niveaux.keys())
            level_values = [float(v.replace('%', '')) for v in niveaux.values()]

            fig_levels = px.pie(
                values=level_values,
                names=level_names,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={'label': 'Level', 'value': 'Percentage'}
            )

            fig_levels.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=11
            )

            fig_levels.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=300
            )

            st.plotly_chart(fig_levels, use_container_width=True)

        # Radar chart for profile comparison
        st.subheader("📊 Behavioral Profile")

        categories = ["General Activity", "Email Engagement", "Content Usage",
                     "Thematic Diversity", "Experience"]

        values = [
            profile.get("activity_level", 0) / 2 * 10,  # Scale to 0-10
            profile.get("email_engagement", 0) / 2 * 10,
            profile.get("content_usage", 0) / 2 * 10,
            profile.get("topic_count", 0) / 8 * 10,  # Assuming max is around 8
            min(profile.get("anciennete", 0) / 20 * 10, 10)  # Cap at 10
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
                    range=[0, 10],
                    tickvals=[0, 2, 4, 6, 8, 10],
                    ticktext=["0", "2", "4", "6", "8", "10"]
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(t=30, b=30, l=80, r=80)
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    # Recomputing clusters (disabled for demo)
    st.markdown("---")
    st.markdown("### 🔄 Recompute Clusters")

    with st.expander("Advanced: Cluster Recomputation", expanded=False):
        # Votre message d'avertissement
        st.info("⚠️ This feature is dangerous and takes a very long time.")
        st.markdown("""
        #### What happens during recomputation?

        This process will:
        1. Load all user data
        2. Process behavioral features
        3. Run K-means clustering algorithm
        4. Reassign all users to clusters
        5. Update cluster statistics

        This operation should only be performed when necessary, such as after significant changes to the user base.
        """)
        # Bouton et logique de recalcul
        if st.button("Recompute clusters", type="primary"):
            with st.spinner("Recomputing clusters... This may take a few minutes."):
                recompute_result = call_api("/clusters/recompute", method="POST")

                if recompute_result and recompute_result.get("success"):
                    st.success("✅ Clusters recomputed successfully!")
                    st.balloons()

                    # Afficher les résultats du recalcul
                    if "cluster_distribution" in recompute_result:
                        distribution = recompute_result["cluster_distribution"]
                        st.write("### New cluster distribution:")

                        cols = st.columns(len(distribution))
                        for i, (cluster_key, count) in enumerate(distribution.items()):
                            with cols[i]:
                                st.metric(f"Cluster {cluster_key.split('_')[1]}", f"{count:,}")

                        st.info("Please refresh the page to see updated cluster data.")
                else:
                    st.error("❌ Failed to recompute clusters. Please try again.")




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
