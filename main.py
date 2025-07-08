from fastapi import FastAPI, HTTPException #1 - main class, 2 - to throw errors with codes 
from pydantic import BaseModel #to validate and describe inputs
from typing import Dict

app = FastAPI()

machine_status: Dict[str, str] = {} #temporary database in the ram (vocabulary)

# description of the data that the phone sends (scheme for JSON)
class StatusUpdate(BaseModel):
    device_id: str
    status: str  # "active", "free", "unknown"

# POST-update data
@app.post("/status") #If a POST request is received at /status the function will be executed.
def update_status(data: StatusUpdate): #checks that it contains device_id and status.
    if data.status not in ["active", "free", "unknown"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    machine_status[data.device_id] = data.status #save status in the vocabulary
    return {"message": "Status updated"}

# GET-receive data
@app.get("/status/{device_id}")
def get_status(device_id: str):
    status = machine_status.get(device_id) #trying to find the status based on the id
    if status is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"device_id": device_id, "status": status}
