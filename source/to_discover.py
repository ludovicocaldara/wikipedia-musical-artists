#!/usr/bin/python3
"""
this script shows the result of the transformation
of a raw JSON document before being inserted into the DB
"""
import sys
import ssl
import logging
import pymongo
import artist
import mw_musical_artist

FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARN)


def process_band(name):
    """function processing a single band during crawling"""
    logging.info('Processing band [%s]', name)


    try:
        band_dict = mw_musical_artist.MWMusicalArtist(name).get_dict()

    except LookupError:
        logging.warning('LookupError: the page [%s] does not exist on Wikipedia', name)
        # insert into artist_crawling collection the error
        from MongoFactory import mongo_db
        coll = mongo_db['artist_crawling']
        coll.update_one({'name':name}, {'$set': {'error': 'LookupError'}})

    except mw_musical_artist.NoMusicalInfoboxException:
        logging.warning('NoMusicalInfoboxException: the page [%s] does not have a Musical Infobox'
                        , name)
        # insert into artist_crawling collection the error
        from MongoFactory import mongo_db
        coll = mongo_db['artist_crawling']
        coll.update_one({'name':name}, {'$set': {'error': 'NoMusicalInfoboxException'}})

    except mw_musical_artist.RedirectException:
        logging.warning('RedirectException: the page [%s] has been redirected'
                        , name)
        # insert into artist_crawling collection the error
        from MongoFactory import mongo_db
        coll = mongo_db['artist_crawling']
        coll.update_one({'name':name}, {'$set': {'error': 'RedirectException'}})

    else:
        try:
            band = artist.Artist(band_dict)
            band.upsert()
        except pymongo.errors.AutoReconnect:
            logging.error('AutoReconnect: the database is not reachable')
            # insert into artist_crawling collection the error
            from MongoFactory import mongo_db
            coll = mongo_db['artist_crawling']
            coll.update_one({'name':name}, {'$set': {'error': 'SSLEOFError'}})
        except ssl.SSLEOFError:
            logging.error('SSLEOFError: the database is not reachable')

# using args by reference then deleting one messes with the debugger
args = sys.argv.copy()

del args[0]

if len(args) > 0:
    for arg in args:
        process_band(arg)

else:
    limit      = 20 # pylint: disable=C0103
    iterations = 1 # pylint: disable=C0103
    while iterations > 0:
        from MongoFactory import mongo_db
        coll = mongo_db['artist_crawling']

        bands_to_discover = coll.find({'discovered': {'$exists': False},
                                       'error': {'$exists': False}}).limit(limit)

        for new_band in bands_to_discover:
            print(new_band['name'] + ' ' + new_band['link'])
        iterations -= 1
