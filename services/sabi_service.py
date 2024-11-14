from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import glob
import re
from functions.sabi_functions import save_new_order, save_return_request, save_issue_report, save_callback_request, save_track_order

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI model and embedding model
llm = OpenAI(api_key=openai_api_key)
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Function to handle Sabi queries
async def handle_sabi_query(query, user_name):
    # Load Sabi-specific documents and process the query
    documents = load_documents_for_app("sabi")
    limited_content = limit_content_size(documents)

    faiss_index = FAISS.from_texts(limited_content, embeddings)
    retriever = faiss_index.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

    # Check for order placement or return request before general QA
    if any(item in query.lower() for item in ["(", ")"]):  # Likely an order
        # Pattern to match items in format: Item name (quantity)
        pattern = r'([^()]+)\s*\((\d+)[^)]*\)'
        matches = re.findall(pattern, query)
        
        if matches:
            # Format order details as structured string
            order_details = ", ".join([f"{item.strip()}: {qty}" for item, qty in matches])
            
            # Extract address if provided
            address_match = re.search(r'(?:address:|deliver to:)\s*(.+?)(?:\.|$)', query.lower())
            address = address_match.group(1).strip() if address_match else "Address pending"
            
            # Save order details
            save_new_order(user_name, order_details, address)
            return "Thank you for your order! We've saved the following details:\n" + \
                   f"Items: {order_details}\n" + \
                   f"Delivery Address: {address}\n" + \
                   "We'll process your order right away!"
    
    # Check for return request with order number and reason
    elif "return" in query.lower() and ("order" in query.lower() or "reason" in query.lower()):
        order_match = re.search(r'order\s*(?:number)?:\s*([A-Z0-9]+)', query, re.IGNORECASE)
        reason_match = re.search(r'reason:\s*(.+?)(?:\.|$)', query, re.IGNORECASE)
        
        if order_match and reason_match:
            order_number = order_match.group(1)
            return_reason = reason_match.group(1).strip()
            save_return_request(user_name, order_number, return_reason)
            return f"Thank you for submitting your return request.\n" + \
                   f"Order Number: {order_number}\n" + \
                   f"Reason: {return_reason}\n" + \
                   "Our team will process it shortly!"
    
    # Handle issue reports
    elif "issue" in query.lower():
        save_issue_report(user_name, query)
        return "Thank you for sharing! We're investigating and will get back to you within 5 minutes."
    
    # Handle callback requests
    elif "callback" in query.lower():
        phone_match = re.search(r'(?:phone|number|call)?\s*[:]\s*(\d+)', query, re.IGNORECASE)
        if phone_match:
            phone_number = phone_match.group(1)
            save_callback_request(user_name, phone_number)
            return f"Thank you! We'll call you shortly at {phone_number} from 02013303232."
    
    # Handle order tracking
    elif "track" in query.lower() and "order" in query.lower():
        order_match = re.search(r'[A-Z]{2}\d{8}', query)
        if order_match:
            order_number = order_match.group(0)
            save_track_order(user_name, order_number)
            return "Thank you! We're checking your order status now."
    
    # If not a direct order or return, use QA chain
    result = qa_chain.invoke(query)
    return result.get('result', 'Sorry, no result found.')

def load_documents_for_app(app_name):
    app_document_paths = {
        "sabi": "documents/Sabi_Market_WhatsApp_Chatbot_Template.txt",
    }
    path = app_document_paths.get(app_name)
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            return [file.read()]
    return []

def limit_content_size(content_list, max_tokens=2000):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=0)  
    limited_content = []
    token_count = 0

    for content in content_list:
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            chunk_tokens = len(chunk.split())
            if token_count + chunk_tokens > max_tokens:
                return limited_content
            limited_content.append(chunk)
            token_count += chunk_tokens
    
    return limited_content
