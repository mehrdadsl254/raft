import server
import time

server3 = server.Server(0, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5001}], 5002, addTimeout=20)

time.sleep(3)

while True:
    entry = input("Enter message: ")
    server3._broadcast(entry)