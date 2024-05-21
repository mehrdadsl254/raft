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
from States.Follower import Follower
from States.Candidate import Candidate
from States.Leader import Leader

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
        self._votesReceived = set()
        self._sentLength = [0 for _ in range(len(neighbors)+1)]
        self._ackedLength = [0 for _ in range(len(neighbors)+1)]
        self._lastLogTerm = 0
        self._addTimeout = addTimeout
        self._timeout = [0]
        self._timeout[0] = time.time()
        self._timeoutCheckerThread = None
        self._continueTimeoutHandler = False
        self._messageHandler()
        self._freezeTimer = False
        self._majority = (len(self._neighbors) + 1) // 2 + 1
        self._currentState = self.FOLLOWER
        self._follower = Follower(self)
        self._follower.start()
        self._candidate = Candidate(self)
        self._leader = Leader(self)



    def _cancelTimer(self):
        self._continueTimeoutHandler = False

    def _heartbeatHandler(self):
        threading.Thread(target=self._heartbeat).start()


    def _heartbeat(self):
        while self._currentState == self.LEADER:
            time.sleep(0.1)
            for n in self._neighbors:
                self._leader._replicateLog(leaderId=self._id, followerId=n['id'])




        # self._mainWorkerThread = self._stateWorker()
        # self._newWorkerThread = None



    # def _stateWorker(self):
    #     if self._currentState == self.FOLLOWER:
    #         newWorkerThread = ThreadWithKill(target=self._follower)
    #         newWorkerThread.start()
    #         return newWorkerThread
    #     elif self._currentState == self.CANDIDATE:
    #         newWorkerThread = ThreadWithKill(target=self._candidate)
    #         newWorkerThread.start()
    #         return newWorkerThread
    #     elif self._currentState == self.LEADER:
    #         newWorkerThread = ThreadWithKill(target=self._leader)
    #         newWorkerThread.start()
    #         return newWorkerThread

    # def _follower(self):
    #     self._timeout[0] = self._nextTimeout()
    #     self._timoutHandler()

    # def _candidate(self):
        # if self._timeoutCheckerThread is not None:
        #     self._killTimeoutChecker()
        # if self._mainWorkerThread is not None:
        #     self._mainWorkerThread.kill()
        # self._mainWorkerThread = self._newWorkerThread
        # self._newWorkerThread = None
        #
        # self._currentTerm = self._currentTerm + 1
        # self._votedFor = self._id
        # self._votesReceived = {self._id}
        # self._lastTerm = 0
        # if len(self._log) > 0:
        #     self._lastTerm = self._log[-1].term
        #
        # for n in self._neighbors:
        #     msg = VoteRequest(term=self._currentTerm, sender=self._id, receiver=n['id'],
        #                       candidateId=self._id, candidateTerm=self._currentTerm,
        #                       candidateLogLength=len(self._log), candidateLogTerm=self._lastTerm)
        #     self._sendMessage(msg)
        #
        # self._timeout[0] = self._nextTimeout()
        # self._timoutHandler()

    # def _leader(self):
    #     pass

    def _nextTimeout(self):
        self._currentTime = time.time()
        self._timeout[0] = self._currentTime + self._addTimeout * random.random() + self._addTimeout
    def _nextElectionTimeout(self, electionTime=2):
        self._currentTime = time.time()
        self._timeout[0] = self._currentTime + electionTime

    def _timeoutHandler(self):
        self._continueTimeoutHandler = True
        self._timeoutCheckerThread = ThreadWithKill(target=self.timeoutChecker, args=(self._timeout,))
        self._timeoutCheckerThread.start()

    def timeoutChecker(self, timeout):
        while self._continueTimeoutHandler:
            if not self._freezeTimer:
                if time.time() > timeout[0]:
                    self._cancelTimer()
                    # suspects leader has failed, or on election timeout
                    self._currentState = self.CANDIDATE
                    self._candidate.start()

    def _killTimeoutChecker(self):
        print("Killing timeout checker of node %d" % self._id)
        self._timeoutCheckerThread.kill()
        self._timeoutCheckerThread = None

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
                    self._onMessage(message.decode())

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

    def _onMessage(self, message):
        message = Message.ConvertStringToMessage(message)
        if message._receiver == self._id:
            if self._currentState == self.FOLLOWER:
                self._follower._onMessage(message)
            elif self._currentState == self.CANDIDATE:
                self._candidate._onMessage(message)
            elif self._currentState == self.LEADER:
                self._leader._onMessage(message)


    def _broadcast(self, record):
        if self._currentState == self.LEADER:
            self._log.append({'term': self._currentTerm, 'msg': record})
            self._ackedLength[self._id] = len(self._log)
            # for each follower ∈ nodes \ {nodeId} do
            for n in self._neighbors:
                self._leader._replicateLog(leaderId=self._id, followerId=n['id'])
        else:
            pass












