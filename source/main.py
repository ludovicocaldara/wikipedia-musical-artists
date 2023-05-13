import Artists
import json
import sys
import mwparserfromhell
import xmltodict



starting_band = sys.argv[1]


band = Artists.MusicalArtist(starting_band)

discovered = [starting_band]

