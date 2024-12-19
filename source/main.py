#!/usr/bin/python3
"""main script running the crawling process"""
import sys
import logging
from timeit import default_timer as timer
import artist


FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


def process_band(name):
    """function processing a single band during crawling"""
    logging.info('Processing band [%s]', name)
    start = timer()
    band = artist.artist(name)
    end = timer()
    print(end - start) # Time in seconds, e.g. 5.38091952400282
    start = timer()
    doc = band.get_from_wikipedia(name)
    end = timer()
    print(end - start) # Time in seconds, e.g. 5.38091952400282
    start = timer()
    band.upsert_artist(doc, 'artist')
    end = timer()
    print(end - start) # Time in seconds, e.g. 5.38091952400282


args = sys.argv
del args[0]

if len(args) > 0:
    for arg in args:
        process_band(arg)
else:
    limit = 100 # pylint: disable=C0103
    iterations=50 # pylint: disable=C0103
    while iterations>0:
        from MongoFactory import mongo_db
        coll = mongo_db['artist_short']
        bands_to_discover = coll.find({'discovered':False, 'error':None }).limit(limit)
        newbands = False # pylint: disable=C0103
        for new_band in bands_to_discover:
            newbands = True # pylint: disable=C0103
            process_band(new_band['name'])
            # time.sleep(0.2)
        if not newbands:
            break
        iterations -= 1
