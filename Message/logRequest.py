from .base import Message

#LogRequest, leaderId, term, logLength, logTerm,leaderCommit, entries
class LogRequest(Message):
    def __init__(self, term, sender : int, receiver : int, logLength : int,leaderId : int, logTerm : int, leaderCommit : int, entries : list):
        super().__init__(Message.LOGREQUEST, term, sender, receiver)
        self._logLength = logLength
        self._leaderId = leaderId
        self._logTerm = logTerm
        self._leaderCommit = leaderCommit
        self._entries = entries

    def __str__(self):
        return super().__str__() + " " + str(self._logLength) + " " + str(self._leaderId) + " " + str(self._logTerm) + " " + str(self._leaderCommit) + " " + " ".join(self._entries)

    @staticmethod
    def ConvertStringToMessage(messageString):
        message = messageString.split(" ")
        return LogRequest(int(message[1]), int(message[2]), int(message[3]), int(message[4]), int(message[5]), int(message[6]), int(message[7]), message[8:])

