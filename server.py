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

        self._myclient = self.connectToDatabase()

        self._port = port
        self._id = Id
        self._log = []
        self._messageBoard = []
        self._neighbors = neighbors
        # self._total_nodes = 0
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
        self._freezeTimer = False
        self._majority = (len(self._neighbors) + 1) // 2 + 1

        self._reStoreServer()

        self._currentState = self.FOLLOWER
        self._follower = Follower(self)
        self._follower.start()
        self._candidate = Candidate(self)
        self._leader = Leader(self)
        self._messageHandler()
        self._storeHandler()


    def connectToDatabase(self):
        from pymongo.mongo_client import MongoClient
        from pymongo.server_api import ServerApi

        uri = "mongodb+srv://Mehrdad254:mehrdad254@cluster0.dsk9myw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        # Create a new client and connect to the server
        myclient = MongoClient(uri, server_api=ServerApi('1'))

        try:
            myclient.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        return myclient

    def _reStoreServer(self):
        mydb = self._myclient[f"ServerDataBase{self._id}"]
        logCol = mydb["RestoreLogs"]
        propCol = mydb["RestoreProperties"]
        prop = propCol.find_one()
        if prop is None:
            return

        self._currentTerm = prop['currentTerm']
        self._commitLength = prop['commitLength']
        self._lastLogTerm = prop['lastLogTerm']
        self._ackedLength = prop['ackedLength']
        self._sentLength = prop['sentLength']

        for x in logCol.find():
            del x['_id']
            self._log.append(x)
            print(x)

        print(self._log)
        print('term',self._currentTerm)

    def _storeHandler(self):
        class StoringThread(threading.Thread):
            def run(thread):
                while True:
                    time.sleep(5)
                    self._storeServer()

        self.StoringThread = StoringThread()
        self.StoringThread.start()


    def _storeServer(self):
        mydb = self._myclient[f"ServerDataBase{self._id}"]
        logCol = mydb["RestoreLogs"]
        propCol = mydb["RestoreProperties"]
        if propCol.find_one() is not None:
            propCol.delete_one({})
        if logCol.find_one() is not None:
            logCol.delete_many({})
        for log in self._log:
            logc = log.copy()
            logCol.insert_one(logc)
        propCol.insert_one({
            'currentTerm': self._currentTerm,
            'commitLength': self._commitLength,
            'lastLogTerm': self._lastLogTerm,
            'ackedLength': self._ackedLength,
            'sentLength': self._sentLength
        })

    def _cancelTimer(self):
        self._continueTimeoutHandler = False

    def _heartbeatHandler(self):
        threading.Thread(target=self._heartbeat).start()


    def _heartbeat(self):
        while self._currentState == self.LEADER:
            time.sleep(0.1)
            for n in self._neighbors:
                self._leader._replicateLog(leaderId=self._id, followerId=n['id'])




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












