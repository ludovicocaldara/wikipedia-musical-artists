import Artists
import pymongo
import sys


starting_band = sys.argv[1]


band = Artists.MusicalArtist(starting_band)
doc=band.getDict()

print(band.getJson())

discovered = [starting_band]
