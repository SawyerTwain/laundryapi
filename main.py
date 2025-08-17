from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import os

app = FastAPI()

machine_status: Dict[str, Dict] = {}

ANDROID_API_KEY = os.getenv("ANDROID_API_KEY")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
ALLOWED_API_KEYS = {k for k in [ANDROID_API_KEY, TELEGRAM_API_KEY] if k}

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key not in ALLOWED_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

@app.get("/", include_in_schema=False)
def root():

    return {"service": "laundryapi", "status": "ok"}

@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}


class StatusUpdate(BaseModel):
    machineId: str
    status: str  
    timestamp: Optional[int] = None

@app.post("/status")
def update_status(data: StatusUpdate, api_key: str = Depends(verify_api_key)):
    if data.status not in ["active", "free", "unknown"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    machine_status[data.machineId] = {
        "status": data.status,
        "timestamp": data.timestamp or int(datetime.utcnow().timestamp())
    }
    return {"message": "Status updated"}

@app.get("/status/{device_id}")
def get_status(device_id: str, api_key: str = Depends(verify_api_key)):
    entry = machine_status.get(device_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"device_id": device_id, "status": entry["status"], "timestamp": entry["timestamp"]}

@app.get("/status")
def get_all_statuses(api_key: str = Depends(verify_api_key)):
    return machine_status
