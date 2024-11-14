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

    # Check different intents
    order_keywords = ["order", "buy", "purchase", "want", "need", "get"]
    track_keywords = ["track", "where", "status", "follow"]
    return_keywords = ["return", "exchange", "refund"]
    issue_keywords = ["issue", "problem", "complaint", "wrong"]
    callback_keywords = ["callback", "call back", "call me", "contact me"]

    query_lower = query.lower()
    
    # Track order intent
    if any(keyword in query_lower for keyword in track_keywords):
        order_number_match = re.search(r'[A-Z]{2}\d{8}', query)
        if order_number_match:
            order_number = order_number_match.group()
            save_track_order(user_name, order_number)
            return f"Thank you! We're tracking your order {order_number}. You'll receive updates shortly."
        else:
            return "Please provide your 10-digit order number (e.g., GL09395824) to track your order."

    # Return/exchange intent
    elif any(keyword in query_lower for keyword in return_keywords):
        order_number_match = re.search(r'[A-Z]{2}\d{8}', query)
        
        # Extract reason after the order number
        if order_number_match:
            order_number = order_number_match.group()
            # Get everything after the order number as the reason
            reason_text = query[query.find(order_number) + len(order_number):].strip()
            if reason_text:
                save_return_request(user_name, order_number, reason_text)
                return "Thank you for submitting your return request. We'll process it right away and contact you within 24 hours."
            else:
                return "Please provide a reason for your return along with the order number."
        else:
            return ("To process your return, please provide your order number and reason.\n"
                   "Example: Order Number: GL78340824 Reason: Wrong size delivered")

    # Issue reporting intent
    elif any(keyword in query_lower for keyword in issue_keywords):
        save_issue_report(user_name, query)
        return "Thank you for reporting this issue. Our team will investigate and contact you shortly."

    # Callback intent
    elif any(keyword in query_lower for keyword in callback_keywords) or "phone" in query_lower:
        # Extract phone number with more flexible pattern
        phone_match = re.search(r'(?:\d{11})|(?:\d{3}[-\s]?\d{4}[-\s]?\d{4})', query)
        if phone_match:
            phone_number = ''.join(filter(str.isdigit, phone_match.group()))
            save_callback_request(user_name, phone_number)
            return f"Thank you for requesting a callback! We'll call you shortly on {phone_number} from our customer service number."
        else:
            return "Please provide your phone number (11 digits) for the callback."

    # If phone number is provided without explicit callback request
    elif re.search(r'(?:\d{11})|(?:\d{3}[-\s]?\d{4}[-\s]?\d{4})', query):
        phone_number = ''.join(filter(str.isdigit, re.search(r'(?:\d{11})|(?:\d{3}[-\s]?\d{4}[-\s]?\d{4})', query).group()))
        save_callback_request(user_name, phone_number)
        return f"Thank you! A customer service representative will call you back shortly on {phone_number}."

    # Order intent
    elif any(keyword in query_lower for keyword in order_keywords):
        # Existing order processing code
        if not (("(" in query and ")" in query) or (":" in query)):
            return ("Thank you for choosing to place an order! Please share your order details "
                   "in the following format:\n"
                   "Item name (quantity), Item name (quantity)\n"
                   "Example: Milo (3 cans), 5alive drink (1 pack)")
        
        # Rest of the order processing code remains the same
        items = []
        pattern1 = r'([^()]+)\s*\((\d+)[^)]*\)'
        matches1 = re.findall(pattern1, query)
        items.extend(matches1)
        
        if items:
            order_details = ", ".join([f"{item.strip()}: {qty}" for item, qty in items])
            address_match = re.search(r'(?:address:|deliver to:|at|to)?\s*([^\.]+(?:street|road|avenue|close|drive|lane|boulevard|plaza|estate)[^\.]+)', 
                                    query.lower())
            address = address_match.group(1).strip() if address_match else "Address pending"
            
            save_new_order(user_name, order_details, address)
            return "Thank you for your order! We've saved the following details:\n" + \
                   f"Items: {order_details}\n" + \
                   f"Delivery Address: {address}\n" + \
                   "We'll process your order right away!"

    # If no specific intent is matched, use QA chain
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
