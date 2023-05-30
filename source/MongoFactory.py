import pymongo

mongo_client = pymongo.MongoClient("mongodb://bands:Bands%23%23123@localhost:27017/bands?authMechanism=PLAIN&authSource=$external&ssl=true&retryWrites=false&loadBalanced=true", tlsAllowInvalidCertificates=True)

mongo_db = mongo_client["bands"]
