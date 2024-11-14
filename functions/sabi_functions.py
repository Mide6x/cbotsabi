import csv
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Data models
class OrderData(BaseModel):
    name: str
    order_details: str
    address: str
    timestamp: str

class ReturnData(BaseModel):
    name: str
    order_number: str
    reason: str
    timestamp: str

def ensure_directory_exists(file_path: str):
    """Ensures the directory exists for the given file path."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_new_order(name: str, order_details: str, address: str):
    """Saves new order details to CSV file."""
    file_path = 'customerrecords/neworder.csv'
    ensure_directory_exists(file_path)
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'name', 'order_details', 'address'])
    
    # Append new order
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, name, order_details, address])

def save_return_request(name: str, order_number: str, reason: str):
    """Saves return request details to CSV file."""
    file_path = 'customerrecords/orderreturns.csv'
    ensure_directory_exists(file_path)
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'name', 'order_number', 'reason'])
    
    # Append new return request
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, name, order_number, reason])

# API endpoints
@router.get("/sabineworders", response_model=List[OrderData])
async def get_new_orders():
    """Returns all new orders as JSON."""
    try:
        file_path = 'customerrecords/neworder.csv'
        if not os.path.exists(file_path):
            return []
        
        orders = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                orders.append(OrderData(**row))
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sabireturns", response_model=List[ReturnData])
async def get_returns():
    """Returns all return requests as JSON."""
    try:
        file_path = 'customerrecords/orderreturns.csv'
        if not os.path.exists(file_path):
            return []
        
        returns = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                returns.append(ReturnData(**row))
        return returns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 