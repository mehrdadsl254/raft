import server
import time


server3 = server.Server(3, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5001}], 5002, addTimeout=5)

time.sleep(3)

