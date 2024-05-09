from .base import Message


# follower, term, ack, success
class LogResponse(Message):
    def __init__(self, term, sender : int, receiver : int, ack : int,followerId : int, success : bool):
        super().__init__(Message.LOGRESPONSE, term, sender, receiver)
        self._ack = ack
        self._followerId = followerId
        self._success = success

    def __str__(self):
        return super().__str__() + " " + str(self._ack) + " " + str(self._followerId) + " " + str(self._success)

    @staticmethod
    def ConvertStringToMessage(messageString):
        message = messageString.split(" ")
        return LogResponse(int(message[1]), int(message[2]), int(message[3]), int(message[4]), int(message[5]), bool(message[6]))

