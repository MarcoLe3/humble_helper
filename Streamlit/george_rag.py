import streamlit as st
import boto3
import base64
import os
import json
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Page Setup ---
st.set_page_config(page_title="Humboldt Helper", layout="wide")

# --- Load and Encode Logo ---
def get_base64_image(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir.replace("streamlit", "Streamlit"), "images", "Logo.png")
logo_base64 = get_base64_image(image_path)

# --- Custom CSS ---
st.markdown(f"""
<style>
    .fixed-sidebar {{
        position: fixed;
        left: 0;
        top:  0;
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
    .stApp {{ background-color: #e6e6e6; margin-left: 260px !important; }}
    header[data-testid="stHeader"] {{ background-color: #e6e6e6 !important; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem 0 1rem; border-bottom: 1px solid #ccc; }}
    header[data-testid="stHeader"]::after {{ content: "AI SUMMER CAMP"; color: #b8860b; font-weight: bold; font-size: 14px; position: absolute; right: 2rem; top: 1.5rem; font-family: sans-serif; }}
    .main-title {{ font-size: 22px; font-family: 'Inter', sans-serif; font-weight: bold; color: #000000; margin-bottom: 0.25rem; }}
    .subtitle {{ font-size: 14px; font-family: 'Inter', sans-serif; font-weight: 300; color: #333333; margin-top: 0.25rem; margin-bottom: 0.25rem; }}
    .instruction {{ font-family: 'Inter', sans-serif; font-size: 14px; color: #333333; margin-bottom: 1.5rem; }}
    .stChatMessage div[data-testid="stMarkdownContainer"] p {{ font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 300; color: #000000 !important; }}
    .stChatMessage {{ padding: 10px 0; }}
    .stChatMessage [data-testid="chat-avatar-icon"] {{ display: none !important; }}
    section[data-testid="stForm"] {{ background-color: #cfe3dc !important; padding: 1rem; border-top: 1px solid #aaa; margin-bottom: 1rem; }}
    div[data-testid="column"] > div {{ display: flex; align-items: center; }}
    .search-bar select,
    .search-bar input,
    .search-bar button {{ height: 45px !important; border: none; border-radius: 8px; padding: 0 12px; background-color: #26262f; color: white; font-size: 15px; }}
    .search-bar button {{ width: 45px; padding: 0; font-size: 20px; background-color: #191920; border-radius: 10px; box-shadow: inset 0 0 0 1px #444; transition: background 0.2s ease; cursor: pointer; }}
    .search-bar button:hover {{ background-color: #333; }}
    .lower-search-bar {{ margin-top: 3rem; }}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.markdown(f"""
<div class="fixed-sidebar">
    <div>
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2.5rem;">
            <img src="{logo_base64}" alt="Logo" style="width: 240px;" />
        </div>
        <p>Welcome to Humboldt Helper, your AI guide for research office questions at Cal Poly Humboldt.</p>
        <p><em>Need help? Just ask!</em></p>
    </div>
    <div>
        <hr style="border: 0.5px solid #fff;">
        <strong>Contacts</strong><br><br>
        <p><strong>Website:</strong><br><a href="https://www.humboldt.edu/research" target="_blank" style="color: #FDB515;">humboldt.edu/research</a></p>
        <p><strong>Phone:</strong> (707) 826-3011</p>
        <p><strong>Instagram:</strong><br><a href="https://www.instagram.com/humboldtpolytechnic/" target="_blank" style="color: #FDB515;">@humboldtpolytechnic</a></p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""
<div class="main-title">Humboldt Helper</div>
<div class="subtitle">Let the exploration begin.</div>
<p class="instruction">Please select a category, type your question, and click the send button.</p>
""", unsafe_allow_html=True)

# --- Bedrock Agent Client ---
bedrock_agent = boto3.client(
    'bedrock-agent-runtime',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# --- Knowledge Base IDs ---
KB_OPTIONS = {
    "General Questions from Website": "QTYWCMLKR0",
    "Meeting Agenda & Minutes": "IYGP2BMJEG",
    "PeopleSoft Questions": "A8UGB7Q2ED"
}

# --- Query Function ---
def query_knowledge_base(kb_id: str, query: str, chat_history: str):
    system_prompt = (
        "You are a helpful assistant who gives step-by-step guidelines of a query that users ask. "
        "Give a brief summary before giving the steps of guidelines. "
        "Always respond in clear, concise sentences. "
        "Use the conversation history to understand context. "
        "List any references separately after your response.\n\n"
        "Example Query:\n"
        "How do I complete my monthly ProCard reconciliation?\n\n"
        "Example Response:\n\n"
        "Summary:\n"
        "This guide outlines the step-by-step process for completing your monthly ProCard reconciliation, from receiving the Accounts Payable (AP) notification to submitting your finalized reconciliation report through the Submission Portal.\n\n"
        "Step 1: Receive Email Notification from AP\n"
        "Accounts Payable sends a monthly email to notify cardholders that their ProCard reconciliations are ready for edits.\n\n"
        "Step 2: Access Statement in PeopleSoft\n"
        "Log into PeopleSoft Finance (CFS) via myHumboldt.\n"
        "Click the Accounts Payable tile, go to the ProCard dropdown, and select ProCard Adjustment.\n"
        "Enter your Business Unit, set Origin to 'USB', and search for your reconciliation by name.\n\n"
        "Step 3: Update Descriptions & Chartfields\n"
        "For each transaction, enter a short description and chartfield info.\n"
        "Split charges using the +/- buttons. Save periodically.\n\n"
        "Step 4: Generate & Download ProCard Report\n"
        "Click the Print Report icon. In Process Monitor, open the PDF via View Log/Trace.\n\n"
        "Step 5: Prepare Reconciliation in Adobe\n"
        "Open the PDF and backup files in Adobe. Use Combine Files to merge them in correct order.\n\n"
        "Step 6: Save & Submit\n"
        "Save the final PDF and submit through the portal: https://policy.humboldt.edu/procard-reconciliation-submission\n\n"
        f"{chat_history}"
    )
    try:
        response = bedrock_agent.retrieve_and_generate(
            input={"text": system_prompt},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": f"arn:aws:bedrock:{os.getenv('AWS_DEFAULT_REGION')}::foundation-model/{os.getenv('BEDROCK_MODEL_ID')}",
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": 0.1,
                                "topP": 0.8,
                                "maxTokens": 700
                            }
                        }
                    }
                }
            }
        )
        return {
            "text": response.get("output", {}).get("text", "[No response text]"),
            "citations": response.get("citations", [])
        }
    except Exception as e:
        return {"text": f"❌ Error: {str(e)}", "citations": []}

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I’m Humboldt Helper. Ask me anything about research resources, policies, or PeopleSoft."}]

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and "references" in message:
            if message["references"]:
                st.markdown("---")
                st.markdown("**References**")
                st.markdown("<ul>" + "".join(message["references"]) + "</ul>", unsafe_allow_html=True)

# --- Search UI ---
st.markdown('<div class="lower-search-bar">', unsafe_allow_html=True)
with st.form("search_form", clear_on_submit=True):
    st.markdown('<div class="search-bar">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 5, 0.6])
    with col1:
        category = st.selectbox("Select a topic", list(KB_OPTIONS.keys()), label_visibility="collapsed")
    with col2:
        query = st.text_input("Enter your question", placeholder="Ask about meeting minutes or research...", label_visibility="collapsed")
    with col3:
        submitted = st.form_submit_button("➤")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Submission ---
if submitted and query.strip():
    prompt = f"[{category}] {query.strip()}"
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    chat_history = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_knowledge_base(KB_OPTIONS[category], query.strip(), chat_history)
            answer = response["text"]
            citations = response["citations"]
            references = []
            seen_urls = set()

            if citations:
                for citation in citations:
                    for ref in citation.get("retrievedReferences", []):
                        url = ref.get("metadata", {}).get("url") or ref.get("location", {}).get("webLocation", {}).get("url")
                        if not url or not url.startswith("http") or url in seen_urls:
                            continue
                        seen_urls.add(url)
                        text_excerpt = ref.get("content", {}).get("text", "No preview available").strip().split("\n")[0][:100]
                        references.append(f'<li><a href="{url}" target="_blank">{text_excerpt}...</a></li>')

            st.write(answer)
            if references:
                st.markdown("---")
                st.markdown("**References**")
                st.markdown("<ul>" + "".join(references) + "</ul>", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": answer, "references": references})
    st.rerun()
