#!/usr/bin/python3
"""main script running the crawling process"""
import sys
import json
import logging
import mw_musical_artist


log_format = ('%(asctime)s - %(levelname)-8s - '+ # pylint: disable=C0103
            '%(funcName)-15s - %(message)s')
logging.basicConfig(format=log_format, level=logging.ERROR)

args = sys.argv
del args[0]

def main(arguments):
    """ main function """
    if len(arguments) > 0:
        for arg in args:
            artist = mw_musical_artist.MWMusicalArtist(arg).get_dict()
            print(json.dumps(artist, indent=4))

main(args)
