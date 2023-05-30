import Artist
import pymongo
import sys


starting_band = sys.argv[1]


band = Artist.Artist(starting_band)

band.process()


