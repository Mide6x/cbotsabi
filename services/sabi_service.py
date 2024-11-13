from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import glob

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
