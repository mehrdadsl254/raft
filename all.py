import server
import time


server3 = server.Server(0, [{'id': 1, 'port': 5000}, {'id': 2, 'port': 5001}], 5002, addTimeout=20)
server1 = server.Server(1, [{'id': 2, 'port': 5001}, {'id': 0, 'port': 5002}], 5000, addTimeout=10)
server2 = server.Server(2, [{'id': 1, 'port': 5000}, {'id': 0, 'port': 5002}], 5001, addTimeout=1)
time.sleep(3)

server2._broadcast("Hello World")

time.sleep(3)


server2._broadcast("Hello again")




#
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
#
# uri = "mongodb+srv://Mehrdad254:mehrdad254@cluster0.dsk9myw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#
# # Create a new client and connect to the server
# myclient = MongoClient(uri, server_api=ServerApi('1'))
#
# # Send a ping to confirm a successful connection
# try:
#     myclient.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
#
# import pymongo
#
# mydb = myclient["Server1DataBase"]
#
#
#
# # mycol = mydb["RestoreData"]
#
# # mylist = [
# #   { "_id": 1, "term": 2, "logterm": "log"},
# # ]
# #
# # x = mycol.insert_many(mylist)
# #
# #
# # print(x.inserted_ids)
#
# # for x in mycol.find():
# #   print(x["term"])
#
#
#
# # myquery = { '_id': 1 }
# # newvalues = { "$set": { "term": 4 } }
# #
# # mycol.update_one(myquery, newvalues)
# #
# # #print "customers" after the update:
# # for x in mycol.find():
# #   print(x)
#
#
#
#
#
#
# #
#
# mycol = mydb["Logs"]
# # mylist = [
# #   { "_id": 1, "term": 2, "message": "x = x+2"},
# # { "_id": 2, "term": 3, "message": "x = x-2"},
# # { "_id": 3, "term": 4, "message": "x = x*2"},
# # ]
# #
# # x = mycol.insert_many(mylist)
#
#
# # print(x.inserted_ids)
#
# last = 0
# for x in mycol.find():
#   if x['_id'] > last:
#       last = x['_id']
#
# # myquery = {'_id' : 3}
# # mydoc = mycol.find(myquery)
# #
# # for x in mydoc:
# #   print (x["term"],x["message"])
#
#
# myquery = {'_id' : 3}
# mydoc = mycol.find_one(myquery)
# print(mydoc)
# #{'_id': 3, 'term': 4, 'message': 'x = x*2'}