import Artists
import pymongo
import sys


starting_band = sys.argv[1]


band = Artists.MusicalArtist(starting_band)
doc=band.getDict()

print(band.getJson())

discovered = [starting_band]


myclient = pymongo.MongoClient("mongodb://bands:Bands%23%23123@localhost:27017/bands?authMechanism=PLAIN&authSource=$external&ssl=true&retryWrites=false&loadBalanced=true", tlsAllowInvalidCertificates=True)


db = myclient["bands"]
col = db["rawbands"]

x = col.insert_one(doc)

