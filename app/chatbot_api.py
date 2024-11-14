from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from services.sabi_service import handle_sabi_query
from services.trace_service import handle_trace_query
from services.katsu_service import handle_katsu_query
from functions.sabi_functions import router as sabi_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add this after initializing the FastAPI app
app.include_router(sabi_router)

# Define request model
class QueryRequest(BaseModel):
    query: str
    name: str
    app: str  # App choice (Sabi Market, Katsu Bank, Trace)

# Define response model
class QueryResponse(BaseModel):
    answer: str

@app.post("/chatbot", response_model=QueryResponse)
async def get_chatbot_response(query_request: QueryRequest):
    try:
        if query_request.app.lower() == "sabi":
            answer = await handle_sabi_query(query_request.query, query_request.name)
        elif query_request.app.lower() == "trace":
            answer = await handle_trace_query(query_request.query, query_request.name)
        elif query_request.app.lower() == "katsu":
            answer = await handle_katsu_query(query_request.query, query_request.name)
        else:
            return QueryResponse(answer="Invalid app specified.")

        return QueryResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: Root endpoint to confirm API status
@app.get("/")
async def read_root():
    return {"message": "AI Chatbot API is up and running!"}
