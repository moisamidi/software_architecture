from fastapi import FastAPI, HTTPException
import requests
import uuid
import random
from pydantic import BaseModel
import hazelcast

app = FastAPI()

hz_client = hazelcast.HazelcastClient(
        cluster_members=["127.0.0.1:5701", "127.0.0.1:5702"])
queue = hz_client.get_queue("messages-queue").blocking()

MESSAGES_SERVICE_INSTANCES = [
    "http://127.0.0.1:8101",
    "http://127.0.0.1:8102"
]


LOGGING_SERVICE_INSTANCES = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003"
]

class Message(BaseModel):
    msg: str

@app.post("/send")
def send_message(message: Message):
    message_id = str(uuid.uuid4())
    payload = {"id": message_id, "msg": message.msg}

    queue.offer(message.msg)

    random.shuffle(LOGGING_SERVICE_INSTANCES)
    for instance in LOGGING_SERVICE_INSTANCES:
        try:
            response = requests.post(f"{instance}/log", json=payload, timeout=2)
            if response.status_code == 200:
                return {"status": "Message added to queue and logged", "id": message_id}
        except requests.exceptions.RequestException:
            continue
    
    raise HTTPException(status_code=500, detail="All logging services are unavailable")

@app.get("/fetch")
def fetch_messages():
    random.shuffle(MESSAGES_SERVICE_INSTANCES)
    for instance in MESSAGES_SERVICE_INSTANCES:
        try:
            response = requests.get(f"{instance}/messages", timeout=2)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            continue
    raise HTTPException(status_code=500, detail="All message services are unavailable")
