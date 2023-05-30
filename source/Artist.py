import MWMusicalArtist
import sys
import logging
import json

# normalizes the ObjectId returned by mongodb to a str
import pydantic
from bson import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str



class Artist:
  ####################################################
  def __init__(self, band):
    self.band = band

    FORMAT = '%(asctime)s - %(levelname)-8s - '+ self.band +' - %(funcName)-15s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    from MongoFactory import mongo_db
    self.mongo_db = mongo_db

  # input: dict of genres (name)
  # returns: id
  def getOrInsertGenre (self, genre):
    coll = self.mongo_db['genre']
    res = coll.find_one(genre)
    if res:
      genre['id'] = res['_id']
    else:
      res = coll.insert_one(genre)
      genre['id'] = res.inserted_id
    logging.debug('new genre for insertion: %s' , genre, extra={"artist":self.band})
    return genre



  # input: dict of genres (name)
  # returns: the new dict with the id included
  def getOrInsertLabel (self, label):
    coll = self.mongo_db['label']
    res = coll.find_one(label)
    if res:
      label['id'] = res['_id']
    else:
      res = coll.insert_one(label)
      label['id'] = res.inserted_id
    logging.debug('new label for insertion: %s' , label, extra={"artist":self.band})
    return label


  # input: dict of an artist 
  # returns: the new dict with the id included
  def getOrInsertArtist (self, artist):
    #for searching a previous artist, we require only the name, as it's unique
    search = dict({"name":artist["name"]})
    coll = self.mongo_db['band']
    res = coll.find_one(search)
    # if it's already there, we rather set the artist with the full details of the result
    if res:
      artist = res
      logging.debug('found existing artist: %s' , artist['name'], extra={"artist":self.band})
      # we delete the _id as we don't want it as _id but _id
      artist['id'] = artist['_id']
      del(artist['_id'])
      del(artist['_metadata'])
      copy_keys = list(artist.keys())
      for key in copy_keys:
        if  artist[key] is None or not artist[key] or artist[key] == '' or len(artist[key]) == 0:
          del artist[key] 
    else:
      # here we are probably only inserting link and name, so we get only the id from the insertion
      logging.debug('inserting new artist: %s' , artist['name'], extra={"artist":self.band})
      res = coll.insert_one(artist)
      artist['id'] = res.inserted_id
    logging.debug('new artist for insertion: %s' , artist, extra={"artist":self.band})
    return artist


  def insertOrUpdateArtist (self, artist):
    #for searching a previous artist, we require only the name, as it's unique
    search = dict({"name":artist["name"]})
    coll = self.mongo_db['band']
    res = coll.find_one(search)
    # if it's already there, we rather set the artist with the full details of the result
    if res:
      artist = res
      logging.debug('found existing artist: %s' , artist['name'], extra={"artist":self.band})
      # we delete the _id as we don't want it as _id but _id
      artist['id'] = artist['_id']
      del(artist['_id'])
      del(artist['_metadata'])
      copy_keys = list(artist.keys())
      for key in copy_keys:
        if  artist[key] is None or not artist[key] or artist[key] == '' or len(artist[key]) == 0:
          del artist[key] 
    else:
      # here we are probably only inserting link and name, so we get only the id from the insertion
      logging.debug('inserting new artist: %s' , artist['name'], extra={"artist":self.band})
      res = coll.insert_one(artist)
      artist['id'] = res.inserted_id
    logging.debug('new artist for insertion: %s' , artist, extra={"artist":self.band})
    return artist




  def process (self):
    band = MWMusicalArtist.MWMusicalArtist(self.band)
    doc = band.getDict()

    # if the link is not empty, set the name the same as the link
    # then remove the link
    if 'genre' in doc:
      logging.debug('genre is there.' , extra={"artist":self.band})
      for index, genre in enumerate(doc['genre']):
        if 'link' in genre:
          if genre['link'] != '':
            doc['genre'][index]['name'] = doc['genre'][index]['link']
          del doc['genre'][index]['link']
        # if there is a genre, get its id, otherwise insert a new one and get its id
        doc['genre'][index] = self.getOrInsertGenre(doc['genre'][index])

    #do the same for the label
    if 'label' in doc:
      logging.debug('label is there.' , extra={"artist":self.band})
      for index, label in enumerate(doc['label']):
        if 'link' in label:
          if label['link'] != '':
            doc['label'][index]['name'] = doc['label'][index]['link']
          del doc['label'][index]['link']
        # if there is a label, get its id, otherwise insert a new one and get its id
        doc['label'][index] = self.getOrInsertLabel(doc['label'][index])


    for rel in ["current_member_of", "past_member_of", "spinoffs", "spinoff_of", "associated_acts"]:
      if rel in doc:
        logging.debug('%s is there.' , rel, extra={"artist":self.band})
        for index, label in enumerate(doc[rel]):
          # if there is an artist relation, get its id, otherwise insert a new one and get its id
          doc[rel][index] = self.getOrInsertArtist(doc[rel][index])


    print(json.dumps(doc, indent=4))

    self.insertOrUpdateArtist(doc)

