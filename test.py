import time
import threading

def timeoutChecker(timeout, flag):
    while True:
        if time.time() > timeout[0]:
            print("Timeout")
            flag[0] = False
            break


def counter(flag):
    count = 0
    while flag[0]:
        print(count)
        count += 1


_timeout = [0]
_timeout[0] = time.time() + 1
flag = [True]
timeoutchecke = threading.Thread(target=timeoutChecker, args=(_timeout, flag,))
t1 = threading.Thread(target=counter, args=(flag,))
timeoutchecke.start()
t1.start()


