""" This module is used to create a connection to the MongoDB database """
import os
import pymongo

# import the module to read the environment variables
from dotenv import load_dotenv
load_dotenv()

# load the environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

mongo_uri = (
    "mongodb://"+DB_USER+":"+DB_PASSWORD+"@"+DB_HOST+":"+DB_PORT+"/"+DB_NAME+
    "?authMechanism=PLAIN&authSource=%24external"+
    "&tls=true&tlsInsecure=true&retryWrites=false&loadBalanced=true")

mongo_client = pymongo.MongoClient(mongo_uri)

mongo_db = mongo_client["bands"]
