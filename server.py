import time
import threading
import random

class Server(object):

    def __init__(self, Id, neighbors):
        self._id = Id
        self._log = []
        self._messageBoard = []
        self._neighbors = neighbors
        self._total_nodes = 0
        self._votedFor = None
        self._commitLength = 0
        self._currentTerm = 0
        self._currentLeader = None
        self._votesReceived = []
        self._sentLength = []
        self._ackedLength = []
        self._currentState =
        self._lastTerm =
        # self._state.set_server(self)
        self._timeout = [0]
        self._timeout[0] = time.time() + 1
        timeoutchecker = threading.Thread(target=self.timeoutChecker, args=(self._timeout, self.flag,))
        timeoutchecker.start()




    def timeoutChecker(self, timeout):
        while True:
            if time.time() > timeout[0]:
                print("Timeout")
                # suspects leader has failed, or on election timeout
                self._currentTerm = self._currentTerm + 1

                # change the state to candidate
                # self._currentState = candidate
                self.votedFor = self._id
                self._votesReceived = {self._id}
                self._lastTerm = 0


    def _nextTimeout(self):
        self._currentTime = time.time()
        return self._currentTime + random.randrange(self._timeout,2 * self._timeout)


server = Server(1, [2, 3, 4])

# print from 1 to 10












