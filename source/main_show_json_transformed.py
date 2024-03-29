#!/usr/bin/python3
import Artist
import sys
import time
import json
import logging

from Artist import NoMusicalInfoboxException

FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARN)



def processBand(name):
    logging.info('Processing band [%s]', name)
    band = Artist.Artist(name)
    try:
      doc = band.getFromWikipedia(name)
    except LookupError:
      logging.warning('LookupError: the page [%s] does not exist on Wikipedia', name)
    except NoMusicalInfoboxException:
      logging.warning('NoMusicalInfoboxException: the page [%s] does not have a Musical Infobox', name)
    else:  
      print(json.dumps(doc, indent=4))


args = sys.argv

del args[0]

if len(args) > 0:
  for arg in args:
    processBand(arg)
    

