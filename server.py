import time
import threading
import random
import zmq
from Messages.LogRequest import LogRequest
from Messages.LogResponse import LogResponse
from Messages.VoteRequest import VoteRequest
from Messages.VoteResponse import VoteResponse
from Messages.base import Message

class Server(object):

    def __init__(self, Id, neighbors,port=5000):
        self._port = port
        self.FOLLOWER = 0
        self.CANDIDATE = 1
        self.LEADER = 2

        self._currentState = self.FOLLOWER
        self._id = Id
        self._log = []
        self._messageBoard = []
        self._neighbors = neighbors
        self._total_nodes = 0
        self._votedFor = None
        self._commitLength = 0
        self._currentTerm = 0
        self._currentLeader = None
        self._votesReceived = []
        self._sentLength = []
        self._ackedLength = []
        self._lastTerm = 0
        self._addTimeout = 1
        self._timeout = [0]
        self._timeout[0] = time.time() + self._addTimeout



    def _timoutHandler(self):
        timeoutChecker = threading.Thread(target=self.timeoutChecker, args=(self._timeout,))
        timeoutChecker.start()

    def _stateWorker(self):
        while True:
            if self._currentState == self.FOLLOWER:
                self._follower()
            elif self._currentState == self.CANDIDATE:
                self._candidate()
            else:
                self._leader()
    def _follower(self):
        self._timoutHandler()

    def timeoutChecker(self, timeout):
        while True:
            if time.time() > timeout[0]:
                print("Timeout")
                # suspects leader has failed, or on election timeout
                self._currentTerm = self._currentTerm + 1

                # change the state to candidate
                self._currentState = self.CANDIDATE
                self._votedFor = self._id
                self._votesReceived = {self._id}
                self._lastTerm = 0
                break

    def _nextTimeout(self):
        self._currentTime = time.time()
        return self._currentTime + random.randrange(self._addTimeout, 2 * self._addTimeout)

    def messageHandler(self):
        class SubscribeThread(threading.Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.SUB)
                socket.subscribe("")
                for n in self._neighbors:
                    socket.connect("tcp://%s:%d" % ('localhost', n['port']))

                while True:
                    message = socket.recv()
                    self._on_message(message.decode())

        class PublishThread(threading.Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.PUB)
                socket.bind("tcp://*:%d" % self._port)
                time.sleep(1)
                while True:
                    if len(self._messageBoard) == 0:
                        continue
                    message = self._messageBoard.pop(0)
                    socket.send(message)

        self.subscribeThread = SubscribeThread()
        self.publishThread = PublishThread()

        # self.subscribeThread.daemon = True
        self.subscribeThread.start()
        # self.publishThread.daemon = True
        self.publishThread.start()

    def _sendMessage(self, message):
        self._messageBoard.append(message.__bytes__())

    def _on_message(self, message):
        message = Message.ConvertStringToMessage(message)
        if message._receiver == self._id:
            print(f"{self._id} received message: {message}")


server = Server(1, [2, 3, 4])














