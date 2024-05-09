import server
import time
import Messages.LogRequest as LogRequest
# from .. Messages.LogResponse import LogResponse
# from .. Messages.VoteRequest import VoteRequest
# from .. Messages.VoteResponse import VoteResponse
# from .. Messages.base import Message

server1 = server.Server(1, [{'id': 2, 'port': 5001}, {'id': 3, 'port': 5002}], 5000)
server2 = server.Server(2, [{'id': 1, 'port': 5000}, {'id': 3, 'port': 5002}], 5001)
server3 = server.Server(3, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5001}], 5002)

server1.messageHandler()
server2.messageHandler()
server3.messageHandler()

time.sleep(3)

msg12 = LogRequest.LogRequest(1, 1, 2, 4, 5, 6, 7, ['12'])
msg23 = LogRequest.LogRequest(1, 2, 3, 4, 5, 6, 7, ['23'])
msg31 = LogRequest.LogRequest(1, 3, 1, 4, 5, 6, 7, ['31'])

server1._sendMessage(msg12)
server2._sendMessage(msg23)
server3._sendMessage(msg31)


