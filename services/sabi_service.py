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

    # Check if this is an order intent
    order_keywords = ["order", "buy", "purchase", "want", "need", "get"]
    is_order_intent = any(keyword in query.lower() for keyword in order_keywords)

    if is_order_intent:
        # If it's not in the exact format, prompt for formatted input
        if not (("(" in query and ")" in query) or (":" in query)):
            return ("Thank you for choosing to place an order! Please share your order details "
                   "in the following format:\n"
                   "Item name (quantity), Item name (quantity)\n"
                   "Example: Milo (3 cans), 5alive drink (1 pack)")
        
        # Try different patterns to extract order details
        items = []
        
        # Pattern 1: Item (quantity)
        pattern1 = r'([^()]+)\s*\((\d+)[^)]*\)'
        matches1 = re.findall(pattern1, query)
        items.extend(matches1)
        
        # Pattern 2: Item: quantity
        pattern2 = r'([^:]+):\s*(\d+)'
        matches2 = re.findall(pattern2, query)
        items.extend(matches2)
        
        # Pattern 3: quantity Item/items/pcs/pieces of Item
        pattern3 = r'(\d+)\s*(?:items?|pcs|pieces?|cans?|packs?|bottles?)?\s*(?:of)?\s*([^,\.]+)'
        matches3 = re.findall(pattern3, query)
        items.extend([(item.strip(), qty) for qty, item in matches3 if not any(item.strip() in existing[0] for existing in items)])

        if items:
            # Format order details as structured string
            order_details = ", ".join([f"{item.strip()}: {qty}" for item, qty in items])
            
            # Extract address if provided
            address_match = re.search(r'(?:address:|deliver to:|at|to)?\s*([^\.]+(?:street|road|avenue|close|drive|lane|boulevard|plaza|estate)[^\.]+)', 
                                    query.lower())
            address = address_match.group(1).strip() if address_match else "Address pending"
            
            # Save order details
            save_new_order(user_name, order_details, address)
            return "Thank you for your order! We've saved the following details:\n" + \
                   f"Items: {order_details}\n" + \
                   f"Delivery Address: {address}\n" + \
                   "We'll process your order right away!"
    
    # If not an order or no items found, use QA chain
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
