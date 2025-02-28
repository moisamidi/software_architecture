import hazelcast

import hazelcast
import time

client = hazelcast.HazelcastClient(cluster_name="dev")
distributed_map = client.get_map("distributed-map").blocking()

for i in range(1000):
    distributed_map.put(i, f"value-{i}")



