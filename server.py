import time
import threading
import random
import zmq
from Messages.LogRequest import LogRequest
from Messages.LogResponse import LogResponse
from Messages.VoteRequest import VoteRequest
from Messages.VoteResponse import VoteResponse
from Messages.base import Message
from ThreadingWithKill import ThreadWithKill
class Server(object):

    def __init__(self, Id, neighbors, port=5000, addTimeout=1):

        self.FOLLOWER = 0
        self.CANDIDATE = 1
        self.LEADER = 2

        self._port = port
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
        self._addTimeout = addTimeout
        self._timeout = [0]
        self._timeout[0] = time.time()
        self._timeoutCheckerThread = None
        self._messageHandler()
        self._currentState = self.FOLLOWER
        self._mainWorkerThread = self._stateWorker()
        self._newWorkerThread = None


    def _timoutHandler(self):
        self._timeoutCheckerThread = ThreadWithKill(target=self.timeoutChecker, args=(self._timeout,))
        self._timeoutCheckerThread.start()

    def _killTimeoutChecker(self):
        self._timeoutCheckerThread.kill()
        # self._timeoutCheckerThread.join()
        self._timeoutCheckerThread = None


    def _stateWorker(self):
        if self._currentState == self.FOLLOWER:
            newWorkerThread = ThreadWithKill(target=self._follower)
            newWorkerThread.start()
            return newWorkerThread
        elif self._currentState == self.CANDIDATE:
            newWorkerThread = ThreadWithKill(target=self._candidate)
            newWorkerThread.start()
            return newWorkerThread
        elif self._currentState == self.LEADER:
            newWorkerThread = ThreadWithKill(target=self._leader)
            newWorkerThread.start()
            return newWorkerThread

    def _follower(self):
        self._timeout[0] = self._nextTimeout()
        self._timoutHandler()

    def _leader(self):
        pass

    def _candidate(self):
        if self._timeoutCheckerThread is not None:
            self._killTimeoutChecker()
        if self._mainWorkerThread is not None:
            self._mainWorkerThread.kill()
            # self._mainWorkerThread.join()
        self._mainWorkerThread = self._newWorkerThread
        self._newWorkerThread = None


        self._currentTerm = self._currentTerm + 1
        self._votedFor = self._id
        self._votesReceived = {self._id}
        self._lastTerm = 0
        if len(self._log) > 0:
            self._lastTerm = self._log[-1].term

        for n in self._neighbors:
            msg = VoteRequest(term = self._currentTerm, sender = self._id, receiver = n['id'],
                              candidateId = self._id, candidateTerm = self._currentTerm,
                              candidateLogLength = len(self._log), candidateLogTerm = self._lastTerm)
            self._sendMessage(msg)

        self._timeout[0] = self._nextTimeout()
        self._timoutHandler()

    def timeoutChecker(self, timeout):
        is_timeout = False
        while not is_timeout:
            if time.time() > timeout[0]:
                is_timeout = True
                print(f"Timeout at {self._id}")
                # suspects leader has failed, or on election timeout
                self._currentState = self.CANDIDATE
                self._newWorkerThread = self._stateWorker()

    def _nextTimeout(self):
        self._currentTime = time.time()
        return self._currentTime + random.randrange(self._addTimeout, 2 * self._addTimeout)

    def _messageHandler(self):
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
            print(f"Message received at {self._id} from {message._sender}")















