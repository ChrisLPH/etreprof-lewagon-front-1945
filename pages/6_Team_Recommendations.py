import streamlit as st
from utils import call_api
import requests

API_BASE_URL = st.secrets["api"]["API_URL"]

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()


st.set_page_config(page_title="Team Recommendations", page_icon="📬", layout="wide")

st.header("📬 Behavioral Recommendations by Cluster")
st.markdown("Use these strategies to select content types for your newsletters and platform actions.")

cluster_labels = {
    0: "Balanced Users",
    1: "Email Specialists",
    2: "Super Users",
    3: "Inactive Users"
}

selected_cluster = st.selectbox(
    "Select cluster:",
    options=list(cluster_labels.keys()),
    format_func=lambda x: f"Cluster {x} - {cluster_labels[x]}"
)

if st.button("🎯 Show Recommendations", key="show_btn"):
    with st.spinner("Loading recommendations..."):
        response = call_api(f"/recommend/{selected_cluster}")

        if response and response.get("success"):
            rec = response["recommendations"]

            st.success(f"✅ Cluster: {rec['cluster_name']}")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### 🧠 Recommended Strategy")
                st.info(rec.get("strategy", "—"))

                st.markdown("### 🧭 Description")
                st.write(rec.get("description", "—"))

                st.markdown("### 🔜 Next Steps")
                st.write(rec.get("next_steps", "—"))

            with col2:
                st.markdown("### 📌 Recommended Content Types")
                for content_type in rec.get("recommended_content_types", []):
                    st.markdown(f"- ✅ **{content_type}**")

                st.markdown("### 🎯 Engagement Approach")
                st.code(rec.get("engagement_approach", "—"))

            st.markdown("---")
            st.markdown(f"📎 **Status**: {response.get('status', '—')}")
        else:
            st.error("❌ Failed to load recommendations.")

# Optional: view all clusters
if st.button("📊 View All Clusters"):
    st.markdown("## 🔄 Overview of all recommendation strategies")

    for cid in range(5):
        response = call_api(f"/recommend/{cid}")
        if response and response.get("success"):
            rec = response["recommendations"]
            with st.expander(f"Cluster {cid} - {rec['cluster_name']}"):
                st.markdown(f"**Strategy:** {rec['strategy']}")
                st.markdown(f"**Description:** {rec['description']}")
                st.markdown(f"**Recommended types:** {', '.join(rec['recommended_content_types'])}")
                st.markdown(f"**Engagement:** `{rec['engagement_approach']}`")
                st.markdown(f"**Status:** _{response.get('status')}_")
        else:
            st.warning(f"Cluster {cid} failed to load.")
