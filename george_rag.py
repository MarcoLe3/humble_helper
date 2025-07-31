import streamlit as st
import boto3

# Initialize Bedrock Agent Runtime client with us-west-2
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

# Set your KB IDs directly here
KB_OPTIONS = {
    "General Questions from Website": "QTYWCMLKR0",  
    "Meeting Agenda & Minutes": "IYGP2BMJEG",    
    "PeopleSoft Questions": "A8UGB7Q2ED"
}

def query_knowledge_base(kb_id, query):
    systemPrompt = (
        """You are a query creation agent. The user will provide you a question, and your job is to create a step by step instructions to perform the query. Always start with a brief summary of the query, then provide detailed steps to perform the query. Use the following format in the example below: 
        <example>
        The procard reconciliation process is a crucial task for cardholders to ensure that all transactions are accurately recorded and submitted for approval.

        Accessing ProCard Reconciliations in PeopleSoft

        ●	Step 1: Receive email notification from AP:
        ●	Accounts Payable sends monthly email notifications to let cardholders know when reconciliations are available for edits/processing. 
        ●	Step 2: Access Statement in PeopleSoft
        ●	Once available, reconciliations can be accessed in PeopleSoft Finance (CFS) through myHumboldt:
        
        ●	Once in PeopleSoft Finance, select the Accounts Payable Tile. From there, click the ProCard dropdown that will appear on the left side of your screen. Select “ProCard Adjustment” from the drop down.


        ●	From the ProCard Adjustment search screen, you must first select the Business Unit your ProCard falls under by either entering it manually in the Business Unit search bar, or by accessing the full list of Business Units by clicking the magnifying glass at the end of it. 
        ●	The Origin line must then be filled in the same manner. The Origin line should always be set to USB, regardless of your Business Unit. 
        ●	Once your Business Unit & Origin are selected, you can search for your reconciliation by entering your first and/or last name and then clicking the blue “Search” button.

        

        ●	Once you hit search, you should be automatically taken to the following screen, where your current reconciliation should be available for processing. 
        
        ●	Your first transaction of this reconciliation’s cycle will be displayed. To view the next transaction, you can press the arrow keys located in the top right of the Transactions field. You can also select View All to bring up all of your transactions for this cycle at once.
        

        ●	Step 3: Update Descriptions & Chartfields
        ●	For each transaction, there are two main components you must fill out: the Description, and the Chartfield string. For the Description field, a simple explanation of what the purchase was and what it was for will suffice. 
        ○	You can add any information that may be helpful to you and your department here as it will show in OBI in the description field. This can support future budget analysis or research on historical transactions.

        

        ●	The Chartfield string is entered under the Distribution field. This will already be filled with the default chartfield you entered on your ProCard application. If the charge should be allocated to a different Chartfield, you can change each manually, or search for specific Chartfields using the magnifying glass for each field. Questions regarding what specific Chartfields you should use should be fielded by your department’s Budget Analyst.
        ●	RECOMMENDED: While filling out these fields, periodically click the blue “Save” button in the bottom right corner to avoid losing any progress.

        ●	If you want to distribute multiple amounts within a single expense’s total to different chartfields, you can add/remove rows using +/- signs on the right side of the field. The line items must add up to the expense’s original total, or an error will occur. Example:

        ●	Step 4: Generate & Download ProCard Report:
        ●	Once you have finished filling out the Descriptions & Chartfields for all of your transactions, click the small Print Report button (printer icon) located next to Process Monitor near the top of your screen. Then, click Process Monitor to access your Process List.
        

        ●	Your ProCard report should appear at the top of this list, with “SQR Report” listed under the Process Type. It typically takes a moment for the report to generate. Click the top right “Refresh” button to refresh the report’s status.Once the report is generated, the Run Status will be “Success”, and the Distribution Status will be “Posted”. Once the report has been generated, click the “Details” hyperlink.

        ●	From the File List, click the hyperlink for the PDF file in the middle of the list. This will download a PDF copy of your ProCard report that will serve as the cover page of your ProCard Reconciliation Submission.

        ●	Step 5: Prepare Reconciliation Submission Adobe:
        ●	Once you have downloaded the report, open both it and any backup documentation files (invoices, receipts, Hospitality forms, Lost Receipt Memos, approvals, etc.) you have in Adobe Acrobat. Once every file is open, select “Combine Files” under Tools, then “Add Open Files”.
        ●	Once at the Combine screen, you can click and drag each individual document to determine the order they appear in (left-most is first.) Backup documentation should be organized in the same order as their corresponding transactions on your ProCard report.
        ●	After your documents are in order, hold the Ctrl key and click each file until they are all highlighted, as shown below, and then click combine. (You can also hold click and drag your cursor across the documents to select them all.)

        ●	Step 6: Save final Reconciliation and submit through the Submission Portal:
        ●	Save the combined document Binder as a single PDF, and submit the entire file for signature through the ProCard Reconciliation Submission portal, located at this link:https://policy.humboldt.edu/procard-reconciliation-submission.
        ●	On that webpage, you will also find an additional guide titled “ProCard Reconciliation Submission Guide” that will instruct you on how to properly route your submission through the Adobe Submission portal. 


        </example>
        onboarding = hire

        Here is the current conversation history: 
        $conversation_history$

        $output_format_instructions$ """)
    try:
        response = bedrock_agent.retrieve_and_generate(
            input={"text": systemPrompt + query},
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
