from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import consul
import socket
import os
import hazelcast

app = FastAPI()
messages: Dict[str, str] = {}

PORT = int(os.getenv("PORT", 8101))  

@app.get("/health")
def health_check():
    return {"status": "ok"}

class LogMessage(BaseModel):
    id: str
    msg: str

@app.post("/log")
def log_message(log: LogMessage):
    messages[log.id] = log.msg
    print(f"Logged: {log.id} -> {log.msg}")
    return {"status": "Message stored"}

c = consul.Consul(host='127.0.0.1', port=8500)
service_id = f"messages-service-{socket.gethostname()}-{PORT}"
c.agent.service.register(
    name="messages-service",
    service_id=service_id,
    address="127.0.0.1",
    port=PORT,
    check=consul.Check.http(f"http://127.0.0.1:{PORT}/health", interval="5s", timeout="2s")
)
hz_client = hazelcast.HazelcastClient(
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702"]
)
queue = hz_client.get_queue("messages-queue").blocking()

@app.get("/messages")
def get_messages():
    if not queue.is_empty():
        message = queue.take()
        print(f"Message taken from queue: {message}")
        return {"msg": message}
    return {"detail": "No messages in queue"}