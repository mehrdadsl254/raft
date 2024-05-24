from .base import Message

# cId, cTerm, cLogLength, cLogTerm
class VoteRequest(Message):
    def __init__(self, term, sender : int, receiver : int, candidateId : int, candidateTerm : int, candidateLogLength : int, candidateLogTerm : int):
        super().__init__(Message.VOTEREQUEST, term, sender, receiver)
        self._candidateId = candidateId
        self._candidateTerm = candidateTerm
        self._candidateLogLength = candidateLogLength
        self._candidateLogTerm = candidateLogTerm

    def __str__(self):
        return super().__str__() + "+" + str(self._candidateId) + "+" + str(self._candidateTerm) + "+" + str(self._candidateLogLength) + "+" + str(self._candidateLogTerm)

    def __bytes__(self):
        return str(self).encode()

    @staticmethod
    def ConvertStringToMessage(messageString):
        message = messageString.split("+")
        return VoteRequest(int(message[1]), int(message[2]), int(message[3]), int(message[4]), int(message[5]), int(message[6]), int(message[7]))