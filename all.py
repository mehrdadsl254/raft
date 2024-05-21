import server
import time


server3 = server.Server(0, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5001}], 5002, addTimeout=8)
server1 = server.Server(1, [{'id': 2, 'port': 5001}, {'id': 0, 'port': 5002}], 5000, addTimeout=3)
server2 = server.Server(2, [{'id': 1, 'port': 5000}, {'id': 0, 'port': 5002}], 5001, addTimeout=1)
time.sleep(3)

server2._broadcast("Hello World")

time.sleep(3)


server2._broadcast("Hello ")
