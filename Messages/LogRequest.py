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
        return super().__str__() + "+" + str(self._logLength) + "+" + str(self._leaderId) + "+" + str(self._logTerm) + "+" + str(self._leaderCommit) + "+" + str(self._entries)

    def __bytes__(self):
        return str(self).encode()

    @staticmethod
    def ConvertStringToMessage(messageString):
        # print(messageString)
        message = messageString.split("+")

        def convertStringToListOfDicts(string):
            list = []
            if len(string) == 2:
                return list
            string = string[1:-1]
            string = string.split("},")

            for s in string[:-1]:
                if s != "":
                    s += "}"
                    list.append(eval(s))
            list.append(eval(string[-1]))

            return list

        return LogRequest(int(message[1]), int(message[2]), int(message[3]), int(message[4]), int(message[5]), int(message[6]), int(message[7]), convertStringToListOfDicts(message[8]))

