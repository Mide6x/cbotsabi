import os
import requests
from bs4 import BeautifulSoup
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define paths and URLs
website_url = "https://www.sabi.am/"
documents_folder = "documents"

# Function to scrape a website starting from a given URL
def scrape_website(base_url):
    pages_content = {}
    visited_urls = set()

    def scrape_page(url):
        if url in visited_urls:
            return
        visited_urls.add(url)

        response = requests.get(url)
        if response.status_code != 200:
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        pages_content[url] = page_text

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                href = base_url + href
            if base_url in href and href not in visited_urls:
                scrape_page(href)

    scrape_page(base_url)
    return pages_content

# Function to load Q&A documents from a folder
def load_documents_from_folder(folder_path):
    documents = []
    for file_path in glob.glob(os.path.join(folder_path, '*.txt')):
        with open(file_path, 'r', encoding='utf-8') as file:
            documents.append(file.read())
    return documents

# Scrape website and load documents
website_content = scrape_website(website_url)
document_texts = load_documents_from_folder(documents_folder)

# Print the scraped content
for url, content in website_content.items():
    print(f"URL: {url}")
    print(f"Content: {content[:500]}...")  # Print the first 500 characters for brevity

# Print document content from the folder
for doc in document_texts:
    print(f"Document content: {doc[:500]}...")  # Print the first 500 characters for brevity
