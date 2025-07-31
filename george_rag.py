import streamlit as st
import boto3

# Initialize Bedrock Agent Runtime client with us-west-2
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

# Set your KB IDs directly here
KB_OPTIONS = {
    "Knowledge Base Helper": "QTYWCMLKR0",  # replace with actual ID
    "Humboldt Meeting PDFs": "IYGP2BMJEG"    # replace with actual ID
}

def query_knowledge_base(kb_id, query):
    try:
        response = bedrock_agent.retrieve_and_generate(
            input={"text": query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",  # ✅ REQUIRED field
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",  # ✅ correct casing
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 3
                        }
                    }
                }
            }
        )
        return response.get("output", {}).get("text", "[No response text]")
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    st.title("🔎 Query Knowledge Base (LLM-Powered)")

    query = st.text_area("Enter your query:")
    selected_kb = st.selectbox("Choose a Knowledge Base to query:", list(KB_OPTIONS.keys()))

    if st.button("Get Answer"):
        if query:
            kb_id = KB_OPTIONS[selected_kb]
            answer = query_knowledge_base(kb_id, query)
            st.subheader(f"🧠 Answer from {selected_kb}")
            st.markdown(answer.replace("\n", "  \n"))  # preserves newlines
        else:
            st.warning("Please enter a query!")

if __name__ == "__main__":
    main()
