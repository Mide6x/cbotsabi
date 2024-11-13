# app/main.py

import uvicorn
from fastapi import FastAPI
from .chatbot_api import app as chatbot_app

if __name__ == "__main__":
    uvicorn.run(chatbot_app, host="0.0.0.0", port=8000)
