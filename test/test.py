import time
import server

server1 = server.Server(1, [{'id': 2, 'port': 5556}, {'id': 3, 'port': 5001}, {'id': 4, 'port': 5557}], 5000)
server2 = server.Server(2, [{'id': 1, 'port': 5000}, {'id': 3, 'port': 5001}, {'id': 4, 'port': 5557}], 5556)

server1.messageHandler()
server2.messageHandler()

time.sleep(1)
time.sleep(3)


server1.sendMessage(b"Hello from 1")
server2.sendMessage(b"Hello from 2")

server1.sendMessage(b"Hello again from 1")
server2.sendMessage(b"Hello again from 2")




