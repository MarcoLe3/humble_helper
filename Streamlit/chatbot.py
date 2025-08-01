import streamlit as st
import boto3
import base64
import os
from typing import List, Dict, Any

# --- Page Setup ---
st.set_page_config(page_title="Humboldt Helper", layout="wide")

# --- Google Fonts ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300&family=Poppins:wght@600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- Load and Encode Image ---
def get_base64_image(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Load logo and avatars ---
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_path = script_dir.replace("streamlit", "Streamlit")

image_path = os.path.join(streamlit_path, "images", "Logo.png")
user_icon_path = os.path.join(streamlit_path, "images", "user_icon.png")
bot_icon_path = os.path.join(streamlit_path, "images", "robot_icon.png")

logo_base64 = get_base64_image(image_path)
user_icon = get_base64_image(user_icon_path)
bot_icon = get_base64_image(bot_icon_path)

# --- Custom CSS Styling ---
st.markdown(f"""
<style>
.fixed-sidebar {{
    position: fixed;
    left: 0;
    top: 0;
    width: 260px;
    height: 100%;
    background-color: #004C46;
    color: white;
    padding: 2rem 1rem 1rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 300;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}}

.stApp {{
    background-color: #e6e6e6;
    margin-left: 260px !important;
    padding-top: 3rem;
    padding-bottom: 100px;
}}

header[data-testid="stHeader"] {{
    background-color: #e6e6e6 !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem 0 1rem;
    border-bottom: 1px solid #ccc;
}}

header[data-testid="stHeader"]::after {{
    content: "AI SUMMER CAMP";
    color: #b8860b;
    font-weight: bold;
    font-size: 14px;
    position: absolute;
    right: 2rem;
    top: 1.5rem;
    font-family: sans-serif;
}}

.main-title {{
    font-size: 26px;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    color: #000000;
    margin-bottom: 0.25rem;
}}

.subtitle {{
    font-size: 14px;
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    color: #333333;
    margin-top: 0.25rem;
    margin-bottom: 0.25rem;
}}

.instruction {{
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #333333;
    margin-bottom: 1.5rem;
}}

.message-bubble {{
    display: flex;
    align-items: flex-start;
    margin-bottom: 1.25rem;
}}

.message-bubble img {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    margin-right: 12px;
    margin-top: 4px;
}}

.message-content {{
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 80%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

.message-user {{
    background-color: #444;
    color: white;
}}

.message-assistant {{
    background-color: #f3f3f3;
    color: #000;
}}

.search-bar select,
.search-bar input,
.search-bar button {{
    height: 45px !important;
    border: none;
    border-radius: 8px;
    padding: 0 12px;
    background-color: #26262f;
    color: white;
    font-size: 15px;
}}

.search-bar button {{
    width: 45px;
    padding: 0;
    font-size: 20px;
    background-color: #191920;
    border-radius: 10px;
    box-shadow: inset 0 0 0 1px #444;
    transition: background 0.2s ease;
    cursor: pointer;
}}

.search-bar button:hover {{
    background-color: #333;
}}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.markdown(f"""
<div class="fixed-sidebar">
    <div>
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2.5rem;">
            <img src="data:image/png;base64,{logo_base64}" alt="Cal Poly Humboldt Logo" style="width: 240px;" />
        </div>
        <p>Welcome to Humboldt Helper, your AI guide to find the right files, links, and information across the California State Polytechnic University, Humboldt Office of Research.</p>
        <p><em>Need help? Just Ask!</em></p>
    </div>
    <div>
        <hr style="border: 0.5px solid #fff; margin: 0.5rem 0 0.75rem 0;">
        <div style="line-height: 1.5;">
            <strong>Source</strong><br><br>
            <p><strong>Website:</strong><br>
                <a href="https://www.humboldt.edu/research" target="_blank" style="color: #FDB515;">humboldt.edu/research</a>
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Main Header ---
st.markdown("""
<div class="main-content">
    <div class="main-title">Humboldt Helper</div>
    <p class="instruction">
        Please select a category, type your question, and click the send button.
    </p>
    <div class="subtitle">Let the exploration begin.</div>
</div>
""", unsafe_allow_html=True)

# --- Claude Model Call ---
@st.cache_resource
def get_bedrock_client() -> Any:
    return boto3.client('bedrock-runtime', region_name='us-west-2')

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

# --- Chat Message Display: both left-aligned ---
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    avatar = user_icon if is_user else bot_icon
    css_class = "message-user" if is_user else "message-assistant"
    sender = "You" if is_user else "Humboldt Helper"

    st.markdown(f"""
    <div class="message-bubble">
        <img src="data:image/png;base64,{avatar}">
        <div class="message-content {css_class}">
            <div style="font-size: 13px; font-weight: bold; margin-bottom: 4px;">{sender}</div>
            <div style="font-size: 14px; font-family: Inter, sans-serif;">{msg['content']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Input Form ---
with st.form("search_form", clear_on_submit=True):
    st.markdown('<div class="search-bar">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 5, 0.6])

    with col1:
        category = st.selectbox("Select a topic", ["Research", "Meeting Minutes"], key="category_input", label_visibility="collapsed")

    with col2:
        query = st.text_input("Enter your question or keywords", placeholder="Ask about meeting minutes or research...", key="query_input", label_visibility="collapsed")

    with col3:
        submitted = st.form_submit_button("➤")

    st.markdown('</div>', unsafe_allow_html=True)

# --- On Submit ---
if submitted and query.strip():
    user_prompt = f"[{category}] {query.strip()}"
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.spinner("Thinking..."):
        response = invoke_model(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
