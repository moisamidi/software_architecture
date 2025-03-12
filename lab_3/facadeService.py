from fastapi import FastAPI, HTTPException
import requests
import uuid
import random

app = FastAPI()

LOGGING_SERVICE_INSTANCES = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003"
]

@app.post("/send")
def send_message(msg: str):
    message_id = str(uuid.uuid4())
    payload = {"id": message_id, "msg": msg}
    random.shuffle(LOGGING_SERVICE_INSTANCES) 
    
    for instance in LOGGING_SERVICE_INSTANCES:
        try:
            response = requests.post(f"{instance}/log", json=payload, timeout=2)
            if response.status_code == 200:
                return {"status": "Message logged", "id": message_id}
        except requests.exceptions.RequestException:
            continue
    
    raise HTTPException(status_code=500, detail="All logging services are unavailable")

@app.get("/fetch")
def fetch_messages():
    random.shuffle(LOGGING_SERVICE_INSTANCES)
    
    for instance in LOGGING_SERVICE_INSTANCES:
        try:
            response = requests.get(f"{instance}/logs", timeout=2)
            if response.status_code == 200:
                return {"logs": response.json()}
        except requests.exceptions.RequestException:
            continue
    
    raise HTTPException(status_code=500, detail="All logging services are unavailable")
