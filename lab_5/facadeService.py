from fastapi import FastAPI, HTTPException
import requests
import uuid
import random
from pydantic import BaseModel
import hazelcast
import consul
import socket
import os

app = FastAPI()

PORT = int(os.getenv("PORT", 8200))

@app.get("/health")
def health_check():
    return {"status": "ok"}

c = consul.Consul(host='127.0.0.1', port=8500)
service_id = f"facade-service-{socket.gethostname()}-{PORT}"
c.agent.service.register(
    name="facade-service",
    service_id=service_id,
    address="127.0.0.1",
    port=PORT,
    check=consul.Check.http(f"http://127.0.0.1:{PORT}/health", interval="5s", timeout="2s")
)

hz_client = hazelcast.HazelcastClient(
        cluster_members=["127.0.0.1:5701", "127.0.0.1:5702"])
queue = hz_client.get_queue("messages-queue").blocking()

def discover_service_instances(service_name):
    services = []
    consul_services = c.catalog.service(service_name)[1]
    for svc in consul_services:
        services.append(f"http://{svc['ServiceAddress']}:{svc['ServicePort']}")
    return services

class Message(BaseModel):
    msg: str

@app.post("/send")
def send_message(message: Message):
    message_id = str(uuid.uuid4())
    payload = {"id": message_id, "msg": message.msg}

    queue.offer(message.msg)

    logging_services = discover_service_instances("logging-service")
    random.shuffle(logging_services)
    for instance in logging_services:
        try:
            response = requests.post(f"{instance}/log", json=payload, timeout=5)
            if response.status_code == 200:
                return {"status": "Message added to queue and logged", "id": message_id}
        except requests.exceptions.RequestException:
            continue
    
    raise HTTPException(status_code=500, detail="All logging services are unavailable")

@app.get("/fetch")
def fetch_messages():
    message_services = discover_service_instances("messages-service")
    random.shuffle(message_services)
    for instance in message_services:
        try:
            response = requests.get(f"{instance}/messages", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            continue
    raise HTTPException(status_code=500, detail="All message services are unavailable")
