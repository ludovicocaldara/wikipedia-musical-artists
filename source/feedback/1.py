#!/usr/bin/python3
import sys
sys.path.append('..')

import MWMusicalArtist
from MWMusicalArtist import NoMusicalInfoboxException
from MWMusicalArtist import RedirectException

import json

ret = MWMusicalArtist.MWMusicalArtist('Kyuss').getDict()

print(json.dumps(ret, indent=4))
