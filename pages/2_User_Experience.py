import streamlit as st
from utils import call_api
import pandas as pd

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

st.title("👤 User Experience")
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
