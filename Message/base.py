from .logRequest import LogRequest
from .logResponse import LogResponse
from .voteRequest import VoteRequest
from .voteResponse import VoteResponse

class Message:

    VOTEREQUEST = 0
    VOTERESPONSE = 1
    LOGREQUEST = 2
    LOGRESPONSE = 3
    def __init__(self, type, term, sender : int, receiver : int):

        self._type = type
        self._term = term
        self._sender = sender
        self._receiver = receiver


    def __str__(self):
        return str(self._type) + " " + str(self._term) + " " + str(self._sender) + " " + str(self._receiver)


    @staticmethod
    def ConvertStringToMessage(messageString):
        message = messageString.split(" ")
        if int(message[0]) == Message.VOTEREQUEST:
            return VoteRequest.ConvertStringToMessage(messageString)
        elif int(message[0]) == Message.VOTERESPONSE:
            return VoteResponse.ConvertStringToMessage(messageString)
        elif int(message[0]) == Message.LOGREQUEST:
            return LogRequest.ConvertStringToMessage(messageString)
        else:
            return LogResponse.ConvertStringToMessage(messageString)







