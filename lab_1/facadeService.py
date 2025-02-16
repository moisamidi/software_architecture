from fastapi import FastAPI, HTTPException
import grpc
import uuid
import logging
import time
from concurrent import futures
import logging_pb2
import logging_pb2_grpc

app = FastAPI()

logging.basicConfig(level=logging.INFO)

LOGGING_SERVICE_HOST = "127.0.0.1"
LOGGING_SERVICE_PORT = "50051"
MAX_RETRIES = 3  
RETRY_DELAY = 1  

def log_message_with_retry(message_id: str, msg: str):
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}: Connecting to logging-service via GRPC...")
            with grpc.insecure_channel(f"{LOGGING_SERVICE_HOST}:{LOGGING_SERVICE_PORT}") as channel:
                stub = logging_pb2_grpc.LoggingServiceStub(channel)
                request = logging_pb2.LogRequest(id=message_id, msg=msg)
                
                print(f"Sending message: ID={message_id}, Msg={msg}")
                response = stub.LogMessage(request)
                
                print(f"Received response: {response.status}")  
                return response.status
        except grpc.RpcError as e:
            print(f"Retry {attempt + 1}/{MAX_RETRIES} failed: {e}")  
            time.sleep(RETRY_DELAY)
    print("ERROR: Logging service unreachable after retries")
    raise HTTPException(status_code=500, detail="Logging service unreachable after retries")


@app.post("/send")
def send_message(msg: str):
    logging.info(f"Received request to log: {msg}")
    message_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, msg))
    status = log_message_with_retry(message_id, msg)
    logging.info(f"Returning response: status={status}, id={message_id}")
    return {"status": status, "id": message_id}
