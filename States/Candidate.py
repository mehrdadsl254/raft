import threading
import time
from Messages.LogRequest import LogRequest
from Messages.LogResponse import LogResponse
from Messages.VoteRequest import VoteRequest
from Messages.VoteResponse import VoteResponse
from Messages.base import Message

class Candidate(threading.Thread):
    def __init__(self, server):
        self.server = server
        self._electionTime = 5


    def start(self):
        print(f"Candidate{self.server._id} started")
        # print(self.server._currentTerm)
        # if self.server._timeoutCheckerThread is not None:
        #     self.server._killTimeoutChecker()



        self.server._currentTerm = self.server._currentTerm + 1
        self.server._votedFor = self.server._id
        self.server._votesReceived = {self.server._id}
        self.server._lastLogTerm = 0

        if len(self.server._log) > 0:
            self.server._lastLogTerm = self.server._log[-1]['term']

        for n in self.server._neighbors:
            msg = VoteRequest(term=self.server._currentTerm, sender=self.server._id, receiver=n['id'],
                              candidateId=self.server._id, candidateTerm=self.server._currentTerm,
                              candidateLogLength=len(self.server._log), candidateLogTerm=self.server._lastLogTerm)
            self.server._sendMessage(msg)

        self.server._nextElectionTimeout(self._electionTime)
        self.server._timeoutHandler()



    def _onMessage(self, message):
        self.server._freezeTimer = True
        if message._type == Message.VOTEREQUEST:
            self._onVoteRequest(message)
        elif message._type == Message.VOTERESPONSE:
            self._onVoteResponse(message)
        elif message._type == Message.LOGREQUEST:
            self._onLogRequest(message)
        self.server._freezeTimer = False

    def _onVoteRequest(self, message):
        myLogTerm = 0
        if len(self.server._log) > 0:
            myLogTerm = self.server._log[-1]['term']
        logOk = (message._candidateLogTerm > myLogTerm) or \
                (message._candidateLogTerm == myLogTerm and
                 message._candidateLogLength >= len(self.server._log))

        termOk = (message._candidateTerm > self.server._currentTerm) or \
                 (message._candidateTerm == self.server._currentTerm and
                  self.server._votedFor in {message._candidateId, None})

        if logOk and termOk:
            self.server._currentTerm = message._candidateTerm
            self.server._currentState = self.server.FOLLOWER
            self.server._follower.start()
            self.server._votedFor = message._candidateId
            self.server._sendMessage(VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                                                  receiver=message._candidateId, voterId=self.server._id,
                                                  granted=True))


        else:
            msg = VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                                                  receiver=message._candidateId, voterId=self.server._id,
                                                  granted=False)
            self.server._sendMessage(msg)
            print(f"i {self.server._id} vot", self.server._votedFor)
    def _onVoteResponse(self, message):
        if self.server._currentState == self.server.CANDIDATE and\
                message._term == self.server._currentTerm and message._granted:

            self.server._votesReceived.add(message._voterId)

            if len(self.server._votesReceived) >= self.server._majority:
                self.server._cancelTimer()
                self.server._currentState = self.server.LEADER
                self.server._currentLeader = self.server._id
                self.server._leader.start()

                # for follower ∈ nodes \ {nodeId} do
                for n in self.server._neighbors:
                    self.server._sentLength[n['id']] = len(self.server._log)
                    self.server._ackedLength[n['id']] = 0
                    self.server._leader._replicateLog(self.server._id, n['id'])



        elif message._term > self.server._currentTerm:
            self.server._currentTerm = message._term
            self.server._cancelTimer()
            self.server._currentState = self.server.FOLLOWER
            self.server._votedFor = None
            self.server._follower.start()

    def _onLogRequest(self, message):
        if message._term > self.server._currentTerm:
            self.server._currentTerm = message._term
            self.server._votedFor = None
            self.server._currentState = self.server.FOLLOWER
            self.server._currentLeader = message._leaderId

        if message._term == self.server._currentTerm and self.server._currentState == self.server.CANDIDATE:
            self.server._currentState = self.server.FOLLOWER
            self.server._cancelTimer()
            self.server._currentLeader = message._leaderId

        logOk = (len(self.server._log) >= message._logLength) and \
                (message._logLength == 0 or message._logTerm == self.server._log[message._logLength - 1]['term'])
        if message._term == self.server._currentTerm and logOk:
            self._appendEnteries(message._logLength, message._leaderCommit, message._entries)
            ack = [0]
            ack[0] = message._logLength + len(message._entries)
            msg = LogResponse(self.server._currentTerm, self.server._id,
                              message._sender, ack[0],self.server._id, True)

            self.server._sendMessage(msg)
        else:
            msg = LogResponse(self.server._currentTerm, self.server._id,
                              message._sender, 0,self.server._id, False)

            self.server._sendMessage(msg)

        if self.server._currentState == self.server.FOLLOWER:
            self.server._follower.start()

    def _appendEnteries(self, logLength, leaderCommit, entries):
        if len(entries) > 0 and len(self.server._log) > logLength:
            if self.server._log[logLength]['term'] != entries[0]['term']:
                self.server._log = self.server._log[:logLength]

        if logLength + len(entries) > len(self.server._log):
            for i in range(len(self.server._log) - logLength, len(entries)):
                self.server._log.append(entries[i])


        if leaderCommit > self.server._commitLength:
            for i in range(len(self.server._commitLength), leaderCommit):
                pass # deliver log[i].msg to the application
            self.server._commitLength = leaderCommit

