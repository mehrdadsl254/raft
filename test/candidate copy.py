from server import Server
import time

server1 = Server(1, [{'id': 2, 'port': 5001}, {'id': 3, 'port': 5002}], 5000, addTimeout=2)
server2 = Server(2, [{'id': 1, 'port': 5000}, {'id': 3, 'port': 5002}], 5001, addTimeout=5)


time.sleep(3)

