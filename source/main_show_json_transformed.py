#!/usr/bin/python3
"""
this script shows the result of the transformation
of a raw JSON document before being inserted into the DB
"""
import sys
import json
import logging
import artist

from artist import NoMusicalInfoboxException

FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARN)



def process_band(name):
    """function processing a single band during crawling"""
    logging.info('Processing band [%s]', name)
    band = artist.Artist(name)
    try:
        doc = band.get_from_wikipedia(name)
    except LookupError:
        logging.warning('LookupError: the page [%s] does not exist on Wikipedia', name)
    except NoMusicalInfoboxException:
        logging.warning('NoMusicalInfoboxException: the page [%s] does not have a Musical Infobox'
                        , name)
    else:
        print(json.dumps(doc, indent=4))


args = sys.argv

del args[0]

if len(args) > 0:
    for arg in args:
        process_band(arg)
