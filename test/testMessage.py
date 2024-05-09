from Messages.LogRequest import LogRequest

m1 = LogRequest(1, 2, 3, 4, 5, 6, 7, ['1', '2', '3', '4', '5'])

m1_str = str(m1)

m2 = LogRequest.ConvertStringToMessage(m1_str)
print(m2)