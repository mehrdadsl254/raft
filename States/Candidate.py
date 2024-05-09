import threading
from Messages.LogRequest import LogRequest
from Messages.LogResponse import LogResponse
from Messages.VoteRequest import VoteRequest
from Messages.VoteResponse import VoteResponse
from Messages.base import Message

class Candidate(threading.Thread):
    def __init__(self, server):
        self.server = server

    def start(self):
        print(self.server._currentTerm)
        # if self.server._timeoutCheckerThread is not None:
        #     self.server._killTimeoutChecker()

        self.server._currentTerm = self.server._currentTerm + 1
        self.server._votedFor = self.server._id
        self.server._votesReceived = {self.server._id}
        self.server._lastTerm = 0
        if len(self.server._log) > 0:
            self.server._lastTerm = self.server._log[-1]['term']

        for n in self.server._neighbors:
            msg = VoteRequest(term=self.server._currentTerm, sender=self.server._id, receiver=n['id'],
                              candidateId=self.server._id, candidateTerm=self.server._currentTerm,
                              candidateLogLength=len(self.server._log), candidateLogTerm=self.server._lastTerm)
            self.server._sendMessage(msg)

        self.server._timeout[0] = self.server._nextTimeout()
        self.server._timoutHandler()



    def _onMessage(self, message):
        if message.type == Message.VOTEREQUEST:
            self._onVoteRequest(message)
        elif message.type == Message.VOTERESPONSE:
            self._onVoteResponse(message)
        elif message.type == Message.LOGREQUEST:
            self._onLogRequest(message)
        elif message.type == Message.LOGRESPONSE:
            self._onLogResponse(message)

    def _onVoteRequest(self, message):
        myLogTerm = self.server._log[-1]['term']
        logOk = (message._candidateLogTerm > myLogTerm) or \
                (message._candidateLogTerm == myLogTerm and
                 message._candidateLogLength >= len(self.server._log))

        termOk = (message._candidateTerm > self.server._currentTerm) or \
                 (message._candidateTerm == self.server._currentTerm and
                  self.server._votedFor in {message._candidateId, None})

        if logOk and termOk:
            self.server._currentTerm = message._candidateTerm
            self.server._currentRole = self.server._FOLLOWER
            self.server._follower.start()
            self.server._votedFor = message._candidateId
            self.server._sendMessage(VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                                                  receiver=message._candidateId, voterId=self.server.id,
                                                  voteGranted=True))
        else:
            self.server._sendMessage(VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                                                  receiver=message._candidateId, voterId=self.server.id,
                                                  voteGranted=False))
