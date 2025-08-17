from fastapi import FastAPI, HTTPException, Depends, Header #1 - main class, 2 - to throw errors with codes, 3 and 4 - to work with the API-keys
from fastapi.responses import RedirectResponse
from pydantic import BaseModel #to validate and describe inputs
from typing import Dict, Optional
from datetime import datetime
import os

app = FastAPI()

machine_status: Dict[str, Dict] = {} #temporary storage in the ram (dictionary)

ALLOWED_API_KEYS = {
    "android": os.getenv("ANDROID_API_KEY", "default_android_key"), #load API keys from environment variables
    "telegram": os.getenv("TELEGRAM_API_KEY", "default_telegram_key"),
}

def verify_api_key(x_api_key: str = Header(...)): #dependency for API key validation
    if x_api_key not in ALLOWED_API_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

class StatusUpdate(BaseModel): #description of the data that the phone sends (scheme for JSON)
    machineId: str
    status: str  # "active", "free", "unknown"
    timestamp: Optional[int] = None 
    
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")

@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}

#POST-update data
@app.post("/status") #If a POST request is received at /status the function will be executed.
def update_status(data: StatusUpdate, api_key: str = Depends(verify_api_key)): #checks that it contains device_id and status.
    if data.status not in ["active", "free", "unknown"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    machine_status[data.machineId] = {
        "status": data.status,
        "timestamp": data.timestamp or int(datetime.utcnow().timestamp()) #save status in the vocabulary
    }
    return {"message": "Status updated"}


#GET-receive data
@app.get("/status/{device_id}")
def get_status(device_id: str, api_key: str = Depends(verify_api_key)):
    entry = machine_status.get(device_id) #trying to find the status based on the id
    if entry is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "device_id": device_id,
        "status": entry["status"],
        "timestamp": entry["timestamp"]
    }

@app.get("/status")
def get_all_statuses(api_key: str = Depends(verify_api_key)):
    return machine_status



