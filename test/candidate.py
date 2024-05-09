import server
import time


server3 = server.Server(3, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5001}], 5002, addTimeout=5)
server1 = server.Server(1, [{'id': 2, 'port': 5001}, {'id': 3, 'port': 5002}], 5000, addTimeout=2)
server2 = server.Server(2, [{'id': 1, 'port': 5000}, {'id': 3, 'port': 5002}], 5001, addTimeout=5)

time.sleep(3)


