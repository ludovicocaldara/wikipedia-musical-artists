#!/usr/bin/python3
import MWMusicalArtist
import sys
import time
import json
import logging

from Artist import NoMusicalInfoboxException

FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.ERROR)



args = sys.argv

del args[0]

if len(args) > 0:
  for arg in args:
    artist = MWMusicalArtist.MWMusicalArtist(arg).getDict()
    print(json.dumps(artist, indent=4))

