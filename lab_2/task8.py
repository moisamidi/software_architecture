import hazelcast
import time
import threading

client = hazelcast.HazelcastClient()

queue = client.get_queue("bounded-queue").blocking()

NUM_CONSUMERS = 2  
STOP_SIGNAL = "STOP"  

def producer():
    for i in range(1, 101):
        print(f"Producing: {i}")
        while True:
            if queue.size() < 10:  
                queue.put(i)
                break
            print("Queue full, waiting...")
            time.sleep(0.5) 
    
    for _ in range(NUM_CONSUMERS):
        queue.put(STOP_SIGNAL)

def consumer(name):
    while True:
        item = queue.take() 
        if item == STOP_SIGNAL:
            print(f"{name} exiting.")
            break
        print(f"{name} consumed: {item}")

producer_thread = threading.Thread(target=producer)
consumer_thread_1 = threading.Thread(target=consumer, args=("Consumer 1",))
consumer_thread_2 = threading.Thread(target=consumer, args=("Consumer 2",))

producer_thread.start()
consumer_thread_1.start()
consumer_thread_2.start()

producer_thread.join()
consumer_thread_1.join()
consumer_thread_2.join()

print("Program finished")
