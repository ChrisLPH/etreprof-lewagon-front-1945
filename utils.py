# utils.py
import requests
import streamlit as st
import pdfplumber
import mammoth

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


def convert_file_to_markdown(uploaded_file) -> str:
    suffix = uploaded_file.name.split('.')[-1].lower()

    if suffix in ['txt', 'md']:
        return uploaded_file.read().decode("utf-8")

    elif suffix == 'pdf':
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n\n".join([page.extract_text() for page in pdf.pages])

    elif suffix == 'docx':
        result = mammoth.convert_to_markdown(uploaded_file)
        return result.value

    else:
        raise ValueError("Unsupported file format")
