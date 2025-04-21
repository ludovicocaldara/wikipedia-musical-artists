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
    except mw_musical_artist.NoMusicalInfoboxException:
        logging.warning('NoMusicalInfoboxException: the page [%s] does not have a Musical Infobox'
                        , name)

    else:
        try:
            band = artist.Artist(band_dict)
            band.upsert()
        except pymongo.errors.AutoReconnect:
            logging.error('AutoReconnect: the database is not reachable')
        except ssl.SSLEOFError:
            logging.error('SSLEOFError: the database is not reachable')

# using args by reference then deleting one messes with the debugger
args = sys.argv.copy()

del args[0]

if len(args) > 0:
    for arg in args:
        process_band(arg)
