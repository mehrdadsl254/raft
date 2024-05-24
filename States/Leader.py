import threading
from Messages.LogRequest import LogRequest
from Messages.LogResponse import LogResponse
from Messages.VoteRequest import VoteRequest
from Messages.VoteResponse import VoteResponse
from Messages.base import Message

class Leader(threading.Thread):
    def __init__(self, server):
        self.server = server

    def start(self):
        print(f"Leader{self.server._id} started")
        self.server._heartbeatHandler()

    def _replicateLog(self, leaderId, followerId):
        i = self.server._sentLength[followerId]
        entries = self.server._log[i:]
        prevLogTerm = 0
        if i > 0:
            prevLogTerm = self.server._log[i-1]['term']
        message = LogRequest(self.server._currentTerm, self.server._id, followerId,
                             i, leaderId, prevLogTerm, self.server._commitLength, entries)
        self.server._sendMessage(message)


    def _onMessage(self, message):
        self.server.freezeTimer = False
        if message._type == Message.VOTEREQUEST:
            self._onVoteRequest(message)
        elif message._type == Message.LOGRESPONSE:
            self._onLogResponse(message)
        self.server._votedFor = None

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
            self.server._sendMessage(VoteResponse(term=self.server._currentTerm, sender=self.server._id,
                                                  receiver=message._candidateId, voterId=self.server._id,
                                                  granted=False))

    # on
    # receiving(LogResponse, follower, term, ack, success)
    # at
    # nodeId
    # do
    # if term = currentTerm ∧ currentRole = leader then
    # if success = true ∧ ack ≥ ackedLength[follower] then
    # sentLength[follower] := ack
    # ackedLength[follower] := ack
    # CommitLogEntries()
    # else if sentLength[follower] > 0 then
    # sentLength[follower] := sentLength[follower] − 1
    # ReplicateLog(nodeId, follower)
    # end if
    # else if term > currentTerm then
    # currentTerm := term
    # currentRole := follower
    # votedFor := null
    # end if
    # end
    # on
    def _onLogResponse(self, message):
        if message._term == self.server._currentTerm and self.server._currentState == self.server.LEADER:
            if message._success and message._ack >= self.server._ackedLength[message._followerId]:
                self.server._sentLength[message._sender] = message._ack
                self.server._ackedLength[message._sender] = message._ack
                self._commitLogEntries()
            elif self.server._sentLength[message._followerId] > 0:
                self.server._sentLength[message._followerId] = self.server._sentLength[message._followerId] - 1
                self._replicateLog(self.server._id, message._followerId)
        elif message._term > self.server._currentTerm:
            self.server._currentTerm = message._term
            self.server._votedFor = None
            self.server._currentState = self.server.FOLLOWER
            self.server._follower.start()



    def _commitLogEntries(self):

        # ready := {len ∈ {1, ..., log.length} | acks(len) ≥ minAcks}
        # if ready 6= {} ∧ max(ready) > commitLength ∧
        # log[max(ready) − 1].term = currentTerm
        # then
        # for i := commitLength to max(ready) − 1 do
        # deliver
        # log[i].msg
        # to
        # the
        # application
        # end
        # for
        #     commitLength := max(ready)
        # end if
        # end
        # function

        def acks(length):
            return len([n for n in self.server._ackedLength if n >= length])

        minAcks = self.server._majority
        ready = [length for length in range(1, len(self.server._log)+1) if acks(length) >= minAcks]
        if len(ready)>0 and max(ready) > self.server._commitLength and self.server._log[max(ready) - 1]['term'] == self.server._currentTerm:
            for i in range(self.server._commitLength, max(ready)):
                pass#deliver log[i].msg to the application
            self.server._commitLength = max(ready)
            print("Commit length: ", self.server._commitLength)
