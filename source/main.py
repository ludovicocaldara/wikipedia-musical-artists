import Artist
import sys
import time




args = sys.argv

del args[0]

for arg in args:
  band = Artist.Artist(arg)
  band.process()


limit = 1


from MongoFactory import mongo_db
coll = mongo_db['band_short']

bands_to_discover = coll.find({'discovered':False}).limit(limit)

for band in bands_to_discover:
  print(band)
  time.sleep(0.5)

