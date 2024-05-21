from .base import Message

# voterId, term, granted
class VoteResponse(Message):
    def __init__(self, term, sender : int, receiver : int,voterId : int, granted : bool):
        super().__init__(Message.VOTERESPONSE, term, sender, receiver)
        self._voterId = voterId
        self._granted = granted

    def __str__(self):
        return super().__str__() + "+" + str(self._voterId) + "+" + str(self._granted)

    def __bytes__(self):
        return str(self).encode()

    @staticmethod
    def ConvertStringToMessage(messageString):
        message = messageString.split("+")
        return VoteResponse(int(message[1]), int(message[2]), int(message[3]), int(message[4]), bool(message[5]))

