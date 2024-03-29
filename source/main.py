#!/usr/bin/python3
import Artist
import sys
import time
import json
import logging

from Artist import NoMusicalInfoboxException

FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)



def processBand(name):
    logging.info('Processing band [%s]', name)
    band = Artist.Artist(name)
    doc = band.getFromWikipedia(name)
    band.upsertArtist(doc, 'artist')


args = sys.argv

del args[0]

if len(args) > 0:
  for arg in args:
    processBand(arg)
    

else:

  limit = 100
  iterations=50
  while iterations>0:

    from MongoFactory import mongo_db
    coll = mongo_db['artist_short']

    bands_to_discover = coll.find({'discovered':False, 'error':None }).limit(limit)
    newbands = False
    for new_band in bands_to_discover:
      newbands = True
      processBand(new_band['name']) 
      time.sleep(0.2)

    if not newbands:
      break

    iterations -= 1

