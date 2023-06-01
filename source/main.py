import Artist
import sys
import time
import json


args = sys.argv

del args[0]

for arg in args:
  band = Artist.Artist(arg)
  doc = band.getFromWikipedia(arg)

  print(json.dumps(doc,indent=2))
  band.upsertArtist(doc, 'artist')



limit = 10


from MongoFactory import mongo_db
coll = mongo_db['artist_short']

bands_to_discover = coll.find({'discovered':False}).limit(limit)

for new_band in bands_to_discover:
  print(new_band['name'])

  band = Artist.Artist(new_band['name'])
  doc = band.getFromWikipedia(new_band['name'])

  band.upsertArtist(doc, 'artist')
  time.sleep(0.5)
