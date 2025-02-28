import hazelcast
import threading
import time

client = hazelcast.HazelcastClient(cluster_name="dev")

my_map = client.get_map("my-distributed-map").blocking()

my_map.put_if_absent("key", 0)

def increment_with_lock():
    for _ in range(10_000):
        my_map.lock("key")  
        try:
            value = my_map.get("key")
            my_map.put("key", value + 1)
        finally:
            my_map.unlock("key")  

start_time = time.time()

threads = []
for _ in range(3):
    t = threading.Thread(target=increment_with_lock)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

end_time = time.time()

final_value = my_map.get("key")
print(f"final: {final_value}")
print(f"time: {end_time - start_time:.2f} s")

client.shutdown()
