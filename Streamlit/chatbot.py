import streamlit as st
import boto3
import base64
import os
from typing import List, Dict, Any

# --- Page Setup ---
st.set_page_config(
    page_title="Humboldt Helper",
    layout="wide"
)

# --- Google Fonts ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- Function to Base64 Encode Image ---
def get_base64_image(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# --- Load logo from local images path ---
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_path = script_dir.replace("streamlit", "Streamlit")
image_path = os.path.join(streamlit_path, "images", "Logo.png")

logo_base64 = get_base64_image(image_path)

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
        font-size: 22px;
        font-family: 'Inter', sans-serif;
        font-weight: bold;
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

    .stChatMessage div[data-testid="stMarkdownContainer"] p {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 300;
        color: #000000 !important;
    }}

    .stChatMessage {{
        padding: 10px 0;
    }}

    .stChatMessage [data-testid="chat-avatar-icon"] {{
        display: none !important;
    }}

    section[data-testid="stForm"] {{
        background-color: #cfe3dc !important;
        padding: 1rem;
        border-top: 1px solid #aaa;
        margin-bottom: 1rem;
    }}

    div[data-testid="column"] > div {{
        display: flex;
        align-items: center;
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

    .lower-search-bar {{
        margin-top: 3rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
st.markdown(f"""
<div class="fixed-sidebar">
    <div>
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2.5rem;">
            <img src="{logo_base64}" alt="Cal Poly Humboldt Logo" style="width: 240px;" />
        </div>
        <p>
            Welcome to Humboldt Helper, your AI guide to find the right files, links, and information across the California State Polytechnic University, Humboldt Office of Research.
        </p>
        <p><em>Need help? Just Ask!</em></p>
    </div>
    <div>
        <hr style="border: 0.5px solid #fff; margin: 0.5rem 0 0.75rem 0;">
        <div style="line-height: 1.5;">
            <strong>Contacts</strong><br><br>
            <p style="margin-bottom: 0.5rem;">
                <strong>Website:</strong><br>
                <a href="https://www.humboldt.edu/research" target="_blank" style="color: #FDB515;">humboldt.edu/research</a>
            </p>
            <p style="margin-bottom: 0.5rem;">
                <strong>Phone:</strong> (707) 826-3011
            </p>
            <p style="margin-bottom: 0;">
                <strong>Instagram:</strong><br>
                <a href="https://www.instagram.com/humboldtpolytechnic/" target="_blank" style="color: #FDB515;">@humboldtpolytechnic</a>
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Title, Subtitle, and Instructions ---
st.markdown("""
<div class="main-title">Humboldt Helper</div>
<div class="subtitle">Let the exploration begin.</div>
<p class="instruction">
Please select a category, type your question, and click the send button.
</p>
""", unsafe_allow_html=True)

# --- Bedrock Client Setup ---
@st.cache_resource
def get_bedrock_client() -> Any:
    return boto3.client('bedrock-runtime', region_name='us-west-2')

# --- Claude Model Call ---
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

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- Search Form ---
st.markdown('<div class="lower-search-bar">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Submission ---
if submitted and query.strip():
    user_prompt = f"[{category}] {query.strip()}"
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = invoke_model(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
