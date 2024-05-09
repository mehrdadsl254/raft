import threading
import zmq

messageBoard = []
import time

class SubscribeThread(threading.Thread):
    def run(thread):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://localhost:5555")
        socket.connect("tcp://localhost:5554")
        socket.subscribe("")
        while True:
            message = socket.recv()
            print(message)


class PublishThread(threading.Thread):
    def run(thread):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:5554")
        t0 = time.time()
        time.sleep(1)
        while True:
            if len(messageBoard) == 0:
                continue
            socket.send(messageBoard.pop(0))
            if time.time() - t0 > 20:
                break

def sendMessage(message):
    messageBoard.append(message)





subscribeThread = SubscribeThread()
# subscribeThread.daemon = True
subscribeThread.start()
publishThread = PublishThread()
# publishThread.daemon = True
publishThread.start()

sendMessage(b"Hello from 1")
time.sleep(2)
sendMessage(b"Hello again from 1")





# import time
# messageBoard = []
#
# def senMessage(message):
#     messageBoard.append(message)


#
# def sendMessage():
#     context = zmq.Context() # Socket to talk to server
#     socket = context.socket(zmq.PUB)
#     socket.bind("tcp://*:5554")
#     t0 = time.time()
#     time.sleep(1)
#     while True: # Wait for next request from client
#         if len(messageBoard) == 0:
#             continue
#         socket.send(messageBoard.pop(0))
#         # time.sleep(0.5)
#         if time.time()-t0 > 20:
#             break


# def recieveMessage():
#     context = zmq.Context()
#     socket = context.socket(zmq.SUB)
#     socket.connect("tcp://localhost:5555")
#     socket.connect("tcp://localhost:5554")
#     t0 = time.time()
#     socket.subscribe("")
#     while True: # Wait for next request from client
#         message = socket.recv()
#         # print("Received request: %s" % message) # Do some 'work'
#         print(message)



# t0 = threading.Thread(target=sendMessage)
# t1 = threading.Thread(target=recieveMessage)
# t1.start()
# t0.start()
#
#
# senMessage(b"Hello from 1")
# time.sleep(2)
# senMessage(b"Hello again from 1")
