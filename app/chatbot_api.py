from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from services.sabi_service import handle_sabi_query
from services.trace_service import handle_trace_query
from services.katsu_service import handle_katsu_query
from functions.sabi_functions import router as sabi_router
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Sabi's Chatbot API",
    description="""
    This API provides chatbot functionality for Sabi Market, including:
    * Order processing
    * Order returns
    * Issue reporting
    * Callback requests
    * Order tracking
    
    ## Available Services
    * **Sabi Market**: Main e-commerce platform
    * **Trace**: Logistics tracking
    * **Katsu Bank**: Banking services
    """,
    version="1.0.0",
    contact={
        "name": "Sabi Market Support",
        "url": "https://www.sabi.am/support",
        "email": "support@sabi.am",
    },
)

# Add this after initializing the FastAPI app
app.include_router(
    sabi_router,
    prefix="/sabi",
    tags=["Sabi Market Operations"],
    responses={404: {"description": "Not found"}},
)

# Add after creating the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced request model with better documentation
class QueryRequest(BaseModel):
    query: str = Field(
        ..., 
        description="The user's query or request",
        example="I want to order Milo (5 tins), Rice (2 bags) address: 123 Main Street, Lagos"
    )
    name: str = Field(
        ..., 
        description="Customer's name",
        example="John Doe"
    )
    app: str = Field(
        ..., 
        description="App choice (sabi, trace, or katsu)",
        example="sabi"
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "I want to order Milo (5 tins), Rice (2 bags) address: 123 Main Street, Lagos",
                "name": "John Doe",
                "app": "sabi"
            }
        }

# Enhanced response model
class QueryResponse(BaseModel):
    answer: str = Field(
        ..., 
        description="The chatbot's response",
        example="Thank you for your order! We've saved your details and will process it right away."
    )

@app.post("/chatbot", 
    response_model=QueryResponse,
    tags=["Chatbot"],
    summary="Process a chatbot query",
    description="""
    Process a user query and return an appropriate response.
    
    Supported operations:
    - Place new orders
    - Request returns
    - Report issues
    - Request callbacks
    - Track orders
    
    The response will vary based on the type of query and the selected app.
    """
)
async def get_chatbot_response(query_request: QueryRequest):
    """
    Process a chatbot query with the following steps:
    1. Validate the request
    2. Route to appropriate service (Sabi, Trace, or Katsu)
    3. Process the query
    4. Return the response
    
    If an error occurs, returns a 500 error with details.
    """
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
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/", 
    tags=["Status"],
    summary="Check API Status",
    description="Returns the current status of the API"
)
async def read_root():
    """Check if the API is running."""
    return {
        "status": "online",
        "message": "AI Chatbot API is up and running!",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# Initialize templates
templates = Jinja2Templates(directory="templates")

# UI route
@app.get("/ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})