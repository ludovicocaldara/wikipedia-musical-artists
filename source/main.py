import Artists
import pymongo
import sys


#FORMAT = '%(asctime)s - %(levelname)-10s - %(artist)-15s - %(message)s'
#logging.basicConfig(format=FORMAT)
#logging.warning('Protocol problem: %s', 'connection reset', extra={"artist":"ciccio"})


starting_band = sys.argv[1]


band = Artists.MusicalArtist(starting_band)


myclient = pymongo.MongoClient("mongodb://bands:Bands##123@localhost:27017/bands?authMechanism=PLAIN&authSource=$external&tls=true&retryWrites=false&loadBalanced=true")


mydb = myclient["bands"]
mycol = mydb["rawbands"]

mydict = { "name": "John", "address": "Highway 37" }

x = mycol.insert_one(mydict)



discovered = [starting_band]


