import MWMusicalArtist
import sys
import logging
from MWMusicalArtist import NoMusicalInfoboxException
from MWMusicalArtist import RedirectException


class Artist:

  def __init__(self, band):
    self.band = band

    FORMAT = '%(asctime)s - %(levelname)-8s - '+ self.band +' - %(funcName)-15s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)



  ###########################
  # use the connection factory and return the existing connection
  def _get_connection(self):
    if 'mongo_db' not in dir(self):
      from MongoFactory import mongo_db
      self.mongo_db = mongo_db
    return self.mongo_db


  def getFromWikipedia(self, name):
    try:
      ret = self._normalize_dict(MWMusicalArtist.MWMusicalArtist(name).getDict())
    except LookupError:
      ret = self._normalize_dict(self.getFromDatabase(name))
      ret['error'] = 'LookupError'
    except NoMusicalInfoboxException:
      ret = self._normalize_dict(self.getFromDatabase(name))
      ret['error'] = 'NoMusicalInfoboxException'
    except RedirectException:
      ret = self._normalize_dict(self.getFromDatabase(name))
      ret['error'] = 'RedirectException'
    finally:
      if not ret.get('error'):
        ret['error'] = ''
      ret['discovered'] = True
      logging.debug('normalized dict :%s' , ret, extra={"artist":self.band})
      return ret


  def getFromDatabase(self, name, short=False):
    mongo_db = self._get_connection()
    if short:
      coll = mongo_db['artist_short']
    else:
      coll = mongo_db['artist']

    search = {"name":name}
    # workaround bug 35444921: use find instead of find_one or we get ORA-40666 in some circumstances
    res = list(coll.find(search))
    # if it's already there, we rather set the artist with the full details of the result
    if len(res) == 1:
      return res[0]
    # if we have more than one document by querying my unique key, we have a problem
    assert (len(res) == 0)
    return false


  def _normalize_dict(self, doc):
    # in the very first simple try we consider only members. No labels, genres, spinoffs and no associated acts.
    #accepted_keys = ['name','type','link','discovered','genre','label','current_member_of','past_member_of','past_members','current_members','spinoff_of','spinoffs','associated_acts']
    accepted_keys = ['name','type','link','discovered','current_member_of','past_member_of','past_members','current_members']
    ret = dict()
    for name, value in doc.items():
      if name in accepted_keys:
        # we want to merge current and past members
        if name in ['current_member_of','past_member_of']:
          if not ret.get('member_of'):
            ret['member_of'] = list()
          ret['member_of'].extend(value)
        elif name in ['current_members','past_members']:
          if not ret.get('members'):
            ret['members'] = list()
          ret['members'].extend(value)
        else:
          ret[name] = value
    return ret


  ########################
  # this insert a dict into a coll name. no questions
  def _insert_dict(self,doc,coll_name):
    mongo_db = self._get_connection()

    ## temporary, remove after debug, remove after debug
    coll_temp = coll_name.replace('_short','')
    coll = mongo_db[coll_temp]
    #coll = mongo_db[coll_name]

    logging.debug('inserting dict :%s - into collation %s' , doc, coll_name, extra={"artist":self.band})
    res = coll.insert_one(doc)
    logging.debug('inserted dict :%s - into collation %s' , doc, coll_name, extra={"artist":self.band})
    # insert_one modifies the dict with the _id included
    ret = self._normalize_dict(self.getFromDatabase(doc['name']))
    ret['error'] = ''
    return ret



  def upsertArtist(self,doc,coll_name):
    mongo_db = self._get_connection()
    coll = mongo_db[coll_name]

    updated = doc.copy()
    for prop in ["member_of", "members"]:
      if prop in doc:
        logging.debug('%s is there.' , prop, extra={"artist":self.band})
        updated[prop] = list()
        for name, value in enumerate(doc[prop]):
          # if there is an artist relation, upsert it
          ret = self._upsert_dict(value,'artist_short')
          if '_id' in ret:
            ret['id'] = ret['_id']
            del ret['_id']
          updated[prop].append(ret)
    logging.debug('new doc: %s', updated, extra={"artist":self.band})
    self._upsert_dict(updated,'artist')



  # we pass here a relations [e.g. a genre or an artist or a label] which we eventually insert if they are not there
  # it must return the definitive record for update
  def _upsert_dict(self,relation, coll_name):
    mongo_db = self._get_connection()
    coll = mongo_db[coll_name]
    
    logging.debug('upserting dict :%s - into collation %s' , relation, coll_name, extra={"artist":self.band})
    # the relation name is unique so we can use it as a key as well
    res = list(coll.find({'name': relation.get('name')}))
    if len(res) == 1:
      logging.debug('we already have the relation :%s ' , res[0] , extra={"artist":self.band})
      # we have already a relation, we rather use the relation detail from the DB
      copy = res[0].copy()
      del copy['_id']
      del copy['_metadata']
      logging.debug('copy before merge is :%s ' , copy , extra={"artist":self.band})
      copy.update(relation)
      if '_id' in copy:
        del copy['_id']
      logging.debug('copy after merge is :%s ' , copy , extra={"artist":self.band})

      logging.debug('need to update collextion %s document id %s with %s' , coll_name, res[0]['_id'], copy , extra={"artist":self.band})
      self._update_dict(res[0]['_id'], copy, coll_name)
      copy['id'] = res[0]['_id']
      logging.debug('returning %s' , copy , extra={"artist":self.band})
      return copy

    else:
      # if we have more than one document by querying my unique key, we have a problem
      assert(len(res)==0)
      return self._insert_dict(relation, coll_name)
    

  def _strip_none(self,doc):
    return {key: value for key, value in doc.items() if value is not None}


  def _update_dict(self,doc_id, doc_set, coll_name):
    mongo_db = self._get_connection()
    coll = mongo_db[coll_name]
    logging.debug('updating doc id :%s - with %s - in collection %s' , doc_id, doc_set, coll_name, extra={"artist":self.band})
    coll.update_one({'_id':doc_id},{'$set':self._strip_none(doc_set)})
    logging.debug('updated doc id :%s - with %s - in collection %s' , doc_id, doc_set, coll_name, extra={"artist":self.band})
