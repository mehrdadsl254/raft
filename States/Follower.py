import threading
from Messages.LogRequest import LogRequest
from Messages.LogResponse import LogResponse
from Messages.VoteRequest import VoteRequest
from Messages.VoteResponse import VoteResponse
from Messages.base import Message

class Follower(threading.Thread):
    def __init__(self, server):
        self.server = server
    def start(self):
        self.server._votesReceived = set()
        self.server._nextTimeout()
        self.server._timeoutHandler()

    def _onMessage(self, message):
        self.server.freezeTimer = False
        if message._type == Message.VOTEREQUEST:
            self._onVoteRequest(message)
        elif message._type == Message.LOGREQUEST:
            self._onLogRequest(message)
        self.server.freezeTimer = False

    def _onVoteRequest(self, message):
        myLogTerm = 0
        if len(self.server._log) > 0:
            myLogTerm = self.server._log[-1]['term']
        logOk = (message._candidateLogTerm > myLogTerm) or\
                (message._candidateLogTerm == myLogTerm and
                 message._candidateLogLength >= len(self.server._log))

        termOk = (message._candidateTerm > self.server._currentTerm) or \
                 (message._candidateTerm == self.server._currentTerm and
                  self.server._votedFor in {message._candidateId, None})

        if logOk and termOk:
            self.server._currentTerm = message._candidateTerm
            self.server._currentState = self.server.FOLLOWER
            self.server._nextTimeout()
            self.server._votedFor = message._candidateId
            self.server._sendMessage(VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                                                  receiver=message._candidateId,voterId=self.server._id,
                                                  granted=True))
        else:
            msg = VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                               receiver=message._candidateId, voterId=self.server._id,
                               granted=False)
            self.server._sendMessage(msg)

    def _onLogRequest(self, message):
        self.server._nextTimeout()
        if message._term > self.server._currentTerm:
            self.server._currentTerm = message._term
            self.server._votedFor = None
            self.server._currentState = self.server.FOLLOWER
            self.server._currentLeader = message._sender

        if message._term == self.server._currentTerm and self.server._currentState == self.server.FOLLOWER:
            self.server._currentLeader = message._leaderId

        logOk = (len(self.server._log) >= message._logLength) and \
                (message._logLength == 0 or message._logTerm == self.server._log[message._logLength - 1]['term'])

        if message._term == self.server._currentTerm and logOk:
            self._appendEnteries(message._logLength, message._leaderCommit, message._entries)
            ack = [0]
            ack[0] = message._logLength + len(message._entries)
            msg = LogResponse(term=self.server._currentTerm, sender=self.server._id,
                              receiver=message._sender, ack=ack[0],followerId=self.server._id, success=True)
            self.server._sendMessage(msg)
        else:
            msg = LogResponse(self.server._currentTerm, self.server._id,
                              message._sender, 0,self.server._id, False)
            self.server._sendMessage(msg)


    def _appendEnteries(self, logLength, leaderCommit, entries):
        if len(entries) > 0 and len(self.server._log) > logLength:
            if self.server._log[logLength]['term'] != entries[0]['term']:
                self.server._log = self.server._log[:logLength]

        if logLength + len(entries) > len(self.server._log):
            for i in range(len(self.server._log) - logLength, len(entries)):
                self.server._log.append(entries[i])

        if leaderCommit > self.server._commitLength:
            for i in range(self.server._commitLength, leaderCommit):
                pass # deliver log[i].msg to the application
            self.server._commitLength = leaderCommit

