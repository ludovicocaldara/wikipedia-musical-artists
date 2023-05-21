import pymongo
import sys



myclient = pymongo.MongoClient("mongodb://bands:Bands##123@localhost:8521/freepdb1?authMechanism=PLAIN&authSource=$external&tls=true&retryWrites=false&loadBalanced=true")



db = myclient["bands"]

col = db["rawbands"]

mydict = { "name": "John", "address": "Highway 37" }

x = col.insert_one(mydict)

