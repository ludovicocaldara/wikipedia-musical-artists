import Artists
import sys


#FORMAT = '%(asctime)s - %(levelname)-10s - %(artist)-15s - %(message)s'
#logging.basicConfig(format=FORMAT)
#logging.warning('Protocol problem: %s', 'connection reset', extra={"artist":"ciccio"})


starting_band = sys.argv[1]


band = Artists.MusicalArtist(starting_band)

discovered = [starting_band]


