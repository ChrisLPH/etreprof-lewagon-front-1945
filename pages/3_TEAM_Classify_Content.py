import streamlit as st
from utils import call_api, convert_file_to_markdown
import requests

# Page configuration
st.set_page_config(
    page_title="ÊtrePROF - Content Classification",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fe;
    }
    .result-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = st.secrets["api"]["API_URL"]

# Title with icon
st.markdown("# 📋 Content Classification")
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

# Analysis section with improved layout
col1, col2 = st.columns([2, 1])

with col1:
    analyze_btn = st.button("🔍 Analyze Content", type="primary", disabled=not markdown_content)

with col2:
    # Add a small help text
    if not markdown_content:
        st.info("Please enter content to analyze.")

# Process analysis
if analyze_btn and markdown_content:
    with st.spinner("Analyzing content..."):
        try:
            url = f"{API_BASE_URL}/classify"
            response = requests.post(url, params={"content": markdown_content})

            if response.status_code == 200:
                result = response.json()

                if result and result.get("success"):
                    data = result["data"]

                    st.success("✅ Analysis completed successfully")

                    topic_principal = data["topic_principal"]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Main Topic", topic_principal["label"])

                    with col2:
                        confidence = topic_principal['confidence']
                        # Color-coded confidence
                        if confidence >= 70:
                            st.metric("Confidence", f"{confidence}%", delta="High")
                        elif confidence >= 50:
                            st.metric("Confidence", f"{confidence}%", delta="Medium")
                        else:
                            st.metric("Confidence", f"{confidence}%", delta="Low")

                    with st.expander("ℹ️ Detailed Results"):
                        st.json(data)

                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"API Error: {response.status_code}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

elif analyze_btn:
    st.warning("Please paste text or upload a file first.")

# Help section
with st.expander("ℹ️ About Content Classification"):
    st.markdown("""
    This tool uses BERTopic, a neural topic modeling technique, to analyze and classify educational content.

    ### How to use:
    1. Paste text or upload a file
    2. Click "Analyze Content"
    3. View the identified topic and confidence score

    For best results, provide content with clear educational themes and at least 100-200 words.
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
