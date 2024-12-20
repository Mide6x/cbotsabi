# Sabi Chatbot System

A multi-service chatbot system that handles customer interactions for Sabi Market, Trace, and Katsu Bank services.

## Table of Contents

- [System Overview](#system-overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [System Architecture](#system-architecture)
- [Document Handling Capacity](#document-handling-capacity)
- [Directory Structure](#directory-structure)

## System Overview

The Sabi Chatbot System is a FastAPI-based application that provides intelligent chatbot functionality for three distinct services:

- Sabi Market: E-commerce and order management
- Trace: Product tracking and logistics
- Katsu Bank: Banking services

The system uses OpenAI's language models for natural language processing and maintains separate training documents for each service.

## Features

- Multi-service support (Sabi Market, Trace, Katsu Bank)
- Real-time chat interface
- Document upload system for training data
- Customer record management
- Order tracking
- Return processing
- Callback request handling
- Automated response improvement system

## Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment tool (venv recommended)
- Modern web browser
- Git

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/cbotsabi.git
cd cbotsabi

```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

3. Install dependencies:

```bash
pip install -r requirements.txt

```

4. Create .env file:

```bash
OPENAI_API_KEY=your_api_key_here

```

5. Create required directories:

```bash
mkdir -p documents/sabiMarket documents/trace documents/katsu

```

6. Start the application:

```bash
python app/main.py

```

## API Documentation

### Main Endpoints

1. Chat Interface

```python
POST /chatbot
```

Request body:

```json
{
  "query": "string",
  "name": "string",
  "app": "string",
  "address": "string"
}
```

2. Document Upload

```python
POST /upload-document
```

Form data:

- app: string (sabi/trace/katsu)
- document: file (.txt)

3. Customer Records

```python
GET /sabi/sabineworders
GET /sabi/sabireturns
GET /sabi/sabitracking
GET /sabi/sabicallbacks
```

### Web Interfaces

- Chat UI: `/ui`
- Document Upload: `/upload`
- Customer Records: `/records`

## System Architecture

### Components

1. Frontend Layer

- HTML/CSS/JavaScript interface
- Real-time chat functionality
- Document upload interface
- Customer records dashboard

2. API Layer

- FastAPI application
- Request handling and routing
- Response processing
- File management

3. Service Layer

- Sabi Market service
- Trace service
- Katsu Bank service
- Document processing

4. Data Layer

- Document storage
- Customer records
- Training data
- Feedback system

### Data Flow

1. User Input Flow:

```
User Input → Frontend → API → Service Layer → OpenAI Processing → Response
```

2. Document Training Flow:

```
Upload → Document Processing → Vector Storage → Training Data Update
```

3. Customer Records Flow:

```
Database → API Endpoints → Frontend Dashboard
```

## Document Handling Capacity

### System Parameters

1. **Chunk Size and Overlap**

- Current chunk size: 1000 characters
- Chunk overlap: 200 characters
- Documents are split into 1000-character segments with 200-character overlaps

2. **FAISS Vector Store Limitations**

- FAISS is efficient for handling millions of vectors
- Current implementation uses similarity search with k=3 nearest neighbors

3. **OpenAI API Context Window**

- System uses default OpenAI model (GPT-3.5-turbo)
- Maximum context window: ~4000 tokens
- Effective working space: ~2000 tokens (as set in limit_content_size)

### Maximum Recommended Capacity

1. **Document Size Limits**

- Individual document size: Up to 1MB of text
- Total number of documents: 50-100 per service folder
- Total combined size: ~50MB of text content

2. **Optimal Limits to Prevent Hallucination**

Per Service Folder:

- Maximum number of documents: 30-40
- Maximum size per document: 500KB
- Total combined size: 15-20MB

These limits are implemented across all services:

- Sabi Market: `documents/sabiMarket/`
- Trace: `documents/trace/`
- Katsu Bank: `documents/katsu/`

Exceeding these limits may result in:

- Increased response latency
- Lower relevance accuracy
- Higher likelihood of hallucinations
- Inconsistent answers across similar queries

## Directory Structure

```

cbotsabi/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── chatbot_api.py
│ ├── models.py
│ └── utils.py
├── services/
│ ├── sabi_service.py
│ ├── trace_service.py
│ └── katsu_service.py
├── templates/
│ ├── index.html
│ ├── document_upload.html
│ └── customer_records.html
├── documents/
│ ├── sabiMarket/
│ ├── trace/
│ └── katsu/
├── scripts/
│ └── improve_responses.py
├── requirements.txt
└── .env

```

```

```
