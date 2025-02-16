from fastapi import FastAPI, HTTPException
import requests
import uuid

app = FastAPI()

LOGGING_SERVICE_URL = "http://127.0.0.1:8001"
MESSAGES_SERVICE_URL = "http://127.0.0.1:8002"

@app.post("/send")
def send_message(msg: str):
    message_id = str(uuid.uuid4())
    payload = {"id": message_id, "msg": msg}
    
    try:
        requests.post(f"{LOGGING_SERVICE_URL}/log", json=payload)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Logging service error: {e}")
    
    return {"status": "Message logged", "id": message_id}

@app.get("/fetch")
def fetch_messages():
    try:
        logs_response = requests.get(f"{LOGGING_SERVICE_URL}/logs")
        messages_response = requests.get(f"{MESSAGES_SERVICE_URL}/message")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Service error: {e}")
    
    logs = logs_response.text
    message = messages_response.text
    
    return {"logs": logs, "message": message}