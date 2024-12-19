""" This module is used to create a connection to the MongoDB database """
import pymongo

#mongo_client = pymongo.MongoClient("mongodb://bands:BandsBands%23%23123@localhost:27017/bands"+
#"?authMechanism=PLAIN&authSource=$external&ssl=true&retryWrites=false&loadBalanced=true",
#  tlsAllowInvalidCertificates=True)
mongo_client = pymongo.MongoClient(
    "mongodb://bands:Welcome##123"+
    "@RDDAINSUH6U1OKC-NEWBANDS.adb.us-ashburn-1.oraclecloudapps.com:27017/bands"+
    "?authMechanism=PLAIN&authSource=$external&ssl=true&retryWrites=false&loadBalanced=true",
    tlsAllowInvalidCertificates=True)

mongo_db = mongo_client["bands"]
