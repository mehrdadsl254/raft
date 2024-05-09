import sys
import threading
import time
import trace
import random

class ThreadWithKill(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        print(f"bbbThread killed at {self.ident}")
        self.killed = True
        print(f"Thread killed at {self.ident}")


# def func1(a):
#     while True:
#         print(a)
# def func2(b):
#     while True:
#         print(b)
#
# t1 = ThreadWithKill(target=func1, args=("Thread 1",))
# t2 = ThreadWithKill(target=func2, args=("Thread 2",))
#
# t1.start()
# t2.start()
#
# t1.kill()
#
# for i in range(5000):
#     i += 1
#     i *= 2
# t2.kill()

