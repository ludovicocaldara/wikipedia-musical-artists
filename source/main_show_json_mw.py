#!/usr/bin/python3
"""main script running the crawling process"""
import sys
import json
import logging
import mw_musical_artist

FORMAT = '%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.ERROR)


args = sys.argv

del args[0]

if len(args) > 0:
    for arg in args:
        artist = mw_musical_artist.mw_musical_artist(arg).get_dict()
        print(json.dumps(artist, indent=4))
