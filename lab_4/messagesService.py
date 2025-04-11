from fastapi import FastAPI
import hazelcast
import threading

app = FastAPI()

hz_client = hazelcast.HazelcastClient(
        cluster_members=["127.0.0.1:5701", "127.0.0.1:5702"])
queue = hz_client.get_queue("messages-queue").blocking()

messages = []

def consume_messages():
    while True:
        msg = queue.take()
        messages.append(msg)
        print(f"Received message: {msg}")

thread = threading.Thread(target=consume_messages, daemon=True)
thread.start()

@app.get("/messages")
def get_messages():
    return {"messages": messages}
