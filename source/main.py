#!/usr/bin/python3
"""main script running the crawling process

If an argument is passed, it uses it as Wikipedia page name
and just gets that data.

If no arguments are passed, it starts crawling from from the database
using artists that haven't been discovered yet.

Example: python main.py "Kyuss"
"""
import sys
import logging
#import cProfile
from timeit import default_timer as timer
import artist


FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


def process_band(name):
    """function processing a single band during crawling"""
    logging.info('Processing band [%s]', name)
    band = artist.Artist(name)
    start = timer()
    doc = band.get_from_wikipedia(name)
    end = timer()
    print(f'Get from WikiPedia: {((end - start)*1000):.2f}')
    start = timer()
    band.upsert_artist(doc)
    end = timer()
    print(f'Upsert to database: {((end - start)*1000):.2f}')

def main(args):
    """ main function """
    del args[0]

    if len(args) > 0:
        for arg in args:
            process_band(arg)
    else:
        limit = 10 # pylint: disable=C0103
        iterations=1 # pylint: disable=C0103
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

main(sys.argv)
