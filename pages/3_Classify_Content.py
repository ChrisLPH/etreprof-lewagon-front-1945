import streamlit as st
from utils import call_api, convert_file_to_markdown
import requests

API_BASE_URL = st.secrets["api"]["API_URL"]

# API connection test
api_status = call_api("/")
if api_status:
    st.success(f"API connected: {api_status.get('status', 'running')}")
else:
    st.error("Cannot connect to API")
    st.stop()

st.header("Content Classification")
st.markdown("Analyze markdown content to identify themes and priority challenges.")


tab_text, tab_file = st.tabs(["📋 Paste Text", "📂 Upload File"])

markdown_content = ""

with tab_text:
    pasted_text = st.text_area(
        "Paste your markdown or text content here:",
        height=250,
        placeholder="# Teaching math\n\nIdeas for differentiation in class..."
    )
    if pasted_text.strip():
        markdown_content = pasted_text.strip()

with tab_file:
    uploaded_file = st.file_uploader("Upload a file (TXT, PDF, DOCX, MD)", type=["txt", "pdf", "docx", "md"])
    if uploaded_file is not None:
        try:
            markdown_content = convert_file_to_markdown(uploaded_file)
            st.success("✅ File processed successfully")
            with st.expander("🔍 Preview extracted content"):
                st.code(markdown_content[:2000])  # Preview max 2000 chars
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
            markdown_content = ""

# Analyse
analyze_btn = st.button("Analyze Content", type="primary")
if analyze_btn and markdown_content:
    with st.spinner("Analyzing..."):
        try:
            url = f"{API_BASE_URL}/classify"
            response = requests.post(url, params={"content": markdown_content})

            if response.status_code == 200:
                result = response.json()

                if result and result.get("success"):
                    data = result["data"]

                    st.success("Analysis completed")

                    topic_principal = data["topic_principal"]
                    st.metric("Main Topic", topic_principal["label"])
                    st.metric("Confidence", f"{topic_principal['confidence']}%")

                    st.markdown("### Detailed Results")
                    st.json(data)
            else:
                st.error(f"API Error: {response.status_code}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

elif analyze_btn:
    st.warning("Please paste text or upload a file first.")







# content_input = st.text_area(
#     "Paste your markdown content here:",
#     height=200,
#     placeholder="# Teaching mathematics\n\nStrategies for differentiated learning..."
# )

# analyze_btn = st.button("Analyze Content", type="primary")

# if analyze_btn and content_input.strip():
#     with st.spinner("Analyzing..."):
#         try:
#             url = f"{API_BASE_URL}/classify"
#             response = requests.post(url, params={"content": content_input})

#             if response.status_code == 200:
#                 result = response.json()

#                 if result and result.get("success"):
#                     data = result["data"]

#                     st.success("Analysis completed")

#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.metric("Main Theme", data["theme"])
#                     with col2:
#                         st.metric("Priority Challenge", data["defi"])

#                     st.markdown("### Detailed Results")
#                     st.json(data)
#             else:
#                 st.error(f"API Error: {response.status_code}")

#         except Exception as e:
#             st.error(f"Error: {str(e)}")

# elif analyze_btn:
#     st.warning("Please enter content to analyze")
