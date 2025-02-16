from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()
logs: Dict[str, str] = {}

class LogMessage(BaseModel):
    id: str
    msg: str

@app.post("/log")
def log_message(log: LogMessage):
    logs[log.id] = log.msg
    print(f"Logged: {log.id} -> {log.msg}")
    return {"status": "Message stored"}

@app.get("/logs")
def get_logs():
    return " | ".join(logs.values())
