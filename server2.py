import server
import time

server2 = server.Server(2, [{'id': 1, 'port': 5000}, {'id': 0, 'port': 5002}], 5001, addTimeout=3)


while True:
    entry = input("Enter message: ")
    server2._broadcast(entry)
