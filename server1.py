import server
import time

server1 = server.Server(1, [{'id': 2, 'port': 5001}, {'id': 0, 'port': 5002}], 5000, addTimeout=10)

while True:
    entry = input("Enter message: ")
    server1._broadcast(entry)