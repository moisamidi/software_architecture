from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import consul
import socket
import os
import hazelcast

app = FastAPI()
logs: Dict[str, str] = {}

PORT = int(os.getenv("PORT", 8001)) 

@app.get("/health")
def health_check():
    return {"status": "ok"}

class LogMessage(BaseModel):
    id: str
    msg: str

hz_client = hazelcast.HazelcastClient(
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702"]
)
logs = hz_client.get_map("logs-map").blocking()

@app.post("/log")
def log_message(log: LogMessage):
    logs.put(log.id, log.msg)
    print(f"Logged: {log.id} -> {log.msg}")
    return {"status": "Message stored"}

@app.get("/logs")
def get_logs():
    all_logs = logs.entry_set()
    return " | ".join([msg for _, msg in all_logs])

c = consul.Consul(host='127.0.0.1', port=8500)
service_id = f"logging-service-{socket.gethostname()}-{PORT}"
c.agent.service.register(
    name="logging-service",
    service_id=service_id,
    address="127.0.0.1",
    port=PORT,
    check=consul.Check.http(f"http://127.0.0.1:{PORT}/health", interval="5s", timeout="2s")
)
