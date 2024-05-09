import time
from test import server

server3 = server.Server(3, [{'id': 2, 'port': 5556}, {'id': 4, 'port': 5557}, {'id': 1, 'port': 5000}], 5001)
server4 = server.Server(4, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5556}, {'id': 3, 'port': 5001}], 5557)


server3.messageHandler()
server4.messageHandler()

time.sleep(1)

time.sleep(3)

server3.sendMessage(b"Hello again from 3")
server4.sendMessage(b"Hello again from 4")
server3.sendMessage(b"Hello from 3")
server4.sendMessage(b"Hello from 4")



