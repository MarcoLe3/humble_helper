import streamlit as st
import boto3
from typing import List, Dict, Any

# --- Page Setup ---
st.set_page_config(
    page_title="Humboldt Helper",
    layout="wide"
)

# --- Custom CSS Styling (with fixed sidebar) ---
st.markdown("""
    <style>
    /* Fixed Sidebar */
    .fixed-sidebar {
        position: fixed;
        left: 0;
        top: 0;
        width: 260px;
        height: 100%;
        background-color: #004C46;
        color: white;
        padding: 2rem 1rem 1rem 1rem;
        font-family: sans-serif;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
    }

    /* Push content right to accommodate sidebar */
    .stApp {
        margin-left: 260px !important;
        background-color: #e6e6e6;
    }

    /* Header bar */
    header[data-testid="stHeader"] {
        background-color: #e6e6e6 !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem 0 1rem;
        border-bottom: 1px solid #ccc;
    }

    header[data-testid="stHeader"]::after {
        content: "AI SUMMER CAMP";
        color: #b8860b;
        font-weight: bold;
        font-size: 14px;
        position: absolute;
        right: 2rem;
        top: 1.5rem;
        font-family: sans-serif;
    }

    .main-title {
        font-size: 40px;
        font-family: serif;
        color: #000000;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        font-size: 18px;
        margin-top: 0.5rem;
        color: #333333;
        font-family: sans-serif;
    }

    .stChatMessage div[data-testid="stMarkdownContainer"] p {
        font-family: serif;
        color: #000000 !important;
    }

    .stChatMessage {
        padding: 10px 0;
    }

    div[data-baseweb="input"] {
        background-color: #dddddd !important;
        border-radius: 20px !important;
    }

    div[data-baseweb="input"] textarea {
        background-color: #dddddd !important;
        color: #000000 !important;
        border-radius: 20px !important;
        min-height: 80px !important;
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Fixed Sidebar Content ---
st.markdown("""
<div class="fixed-sidebar">
    <div>
        <h3 style="font-family: serif;">Cal Poly <br> <span style='color: #FDB515;'>Humboldt.</span></h3>
        <p style="font-size: 13px;">Welcome to Humboldt Helper, your AI guide for research files, links, and opportunities across the California State Polytechnic University, Humboldt Office of Research.</p>
        <p style="font-size: 12px;"><em>Need help? Just ask!</em></p>
    </div>
    <div style="font-size: 14px;">
        <strong>Quick Contacts</strong><br>
        <ul style="padding-left: 1rem;">
            <li>Website: Humboldt Research</li>
            <li>Phone:</li>
            <li>Email:</li>
            <li>Instagram</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Title and Subtitle ---
st.markdown("""
<div class="main-title">Humboldt Helper</div>
<div class="subtitle">Let the exploration begin.</div>
""", unsafe_allow_html=True)

# --- Bedrock Client Setup ---
@st.cache_resource
def get_bedrock_client() -> Any:
    return boto3.client('bedrock-runtime', region_name='us-west-2')

# --- Claude Model Invocation ---
def invoke_model(messages: List[Dict[str, str]]) -> str:
    client = get_bedrock_client()
    bedrock_messages = [{
        "role": msg["role"],
        "content": [{"text": msg["content"]}]
    } for msg in messages]

    try:
        response = client.converse(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=bedrock_messages,
            inferenceConfig={"maxTokens": 1000},
        )
        return response['output']['message']['content'][0]['text']
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi! I’m Humboldt Helper. I can help you locate research documents, funding opportunities, and resources regarding research. How can I assist you?"
    }]

# --- Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- User Input ---
if prompt := st.chat_input("Ask about grants, documents, or research..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = invoke_model(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
