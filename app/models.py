from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    app: str  # The app from which the user is making the request (e.g., "sabi", "trace", "katsu")
    name: str  # The user's name
    phone_number: Optional[str]  # Optional: The user's phone number
    query: str  # The query the user is asking (e.g., place order, return order, etc.)
    order_details: Optional[str]  # Optional: Order details if applicable (in JSON format)

class QueryResponse(BaseModel):
    answer: str  # The response from the chatbot (e.g., confirmation message, order details)
