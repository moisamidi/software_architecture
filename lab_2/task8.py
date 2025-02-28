import hazelcast
import time
import threading

client = hazelcast.HazelcastClient()

# Отримуємо обмежену чергу
queue = client.get_queue("bounded-queue").blocking()

NUM_CONSUMERS = 2  # Кількість читачів
STOP_SIGNAL = "STOP"  # Спеціальний маркер завершення

# 🔹 Продюсер: записує 1..100 у чергу
def producer():
    for i in range(1, 101):
        print(f"Producing: {i}")
        while True:
            if queue.size() < 10:  # Перевіряємо, чи є місце
                queue.put(i)
                break
            print("Queue full, waiting...")
            time.sleep(0.5)  # Очікуємо, поки з'явиться місце
    
    # Надсилаємо по STOP_SIGNAL кожному споживачу
    for _ in range(NUM_CONSUMERS):
        queue.put(STOP_SIGNAL)

# 🔹 Споживачі: вичитують дані з черги одразу
def consumer(name):
    while True:
        item = queue.take()  # Отримуємо елемент
        if item == STOP_SIGNAL:
            print(f"{name} exiting.")
            break
        print(f"{name} consumed: {item}")

# Запускаємо потоки
producer_thread = threading.Thread(target=producer)
consumer_thread_1 = threading.Thread(target=consumer, args=("Consumer 1",))
consumer_thread_2 = threading.Thread(target=consumer, args=("Consumer 2",))

producer_thread.start()
consumer_thread_1.start()
consumer_thread_2.start()

producer_thread.join()
consumer_thread_1.join()
consumer_thread_2.join()

print("Program finished.")
