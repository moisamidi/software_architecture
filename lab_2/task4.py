import hazelcast
import threading

client = hazelcast.HazelcastClient(cluster_name="dev")

my_map = client.get_map("my-distributed-map").blocking()

my_map.put_if_absent("key", 0)

def increment():
    for _ in range(10_000):
        value = my_map.get("key")  
        my_map.put("key", value + 1)

threads = []
for _ in range(3):
    t = threading.Thread(target=increment)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

final_value = my_map.get("key")
print(f"final: {final_value}")

client.shutdown()
