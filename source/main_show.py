import MWMusicalArtist
import pymongo
import sys


starting_band = sys.argv[1]


band = MWMusicalArtist.MWMusicalArtist(starting_band)
doc=band.getDict()

print(band.getJson())
