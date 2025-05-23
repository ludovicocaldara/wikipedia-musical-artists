"""
The artist class gets a band name and returns a dictionary
with a lot of information about the band
The dictionary is then stored in the database"""
import logging
import mw_musical_artist
from mw_musical_artist import NoMusicalInfoboxException
from mw_musical_artist import RedirectException


class Artist:
    """
    The Artist class gets a band name and returns a dictionary
    with a lot of information about the band
    The dictionary is then stored in the database"""

    def __init__(self, band):
        self.band = band

        log_format = ('%(asctime)s - %(levelname)-8s - ' +
                      self.band + ' - %(funcName)-15s - %(message)s')
        logging.basicConfig(format=log_format, level=logging.ERROR)



    ###########################
    # use the connection factory and return the existing connection
    def _get_connection(self):
        if 'mongo_db' not in dir(self):
            from MongoFactory import mongo_db
            self.mongo_db = mongo_db
        return self.mongo_db


    def get_from_wikipedia(self, name):
        """
        This function gets a band name and returns a dictionary.
        There's no modification happening to the database and
        queries only happen if the wikipedia fetch raises exceptions.
        """

        # we try to get the dict from Wikipedia.
        # if any exception happens, we fallback to the database
        # where we should at least have the name and a basic
        # relationship to the (child) band or person
        try:
            ret = mw_musical_artist.MWMusicalArtist(name).get_dict()
            ret['type'] = self._band_or_person(ret)
            ret = self._normalize_dict(ret)
        except LookupError:
            ret = self._normalize_dict(self.get_from_database(name))
            ret['error'] = 'LookupError'
        except NoMusicalInfoboxException:
            ret = self._normalize_dict(self.get_from_database(name))
            ret['error'] = 'NoMusicalInfoboxException'
        except RedirectException:
            ret = self._normalize_dict(self.get_from_database(name))
            ret['error'] = 'RedirectException'
        finally:
            if not ret.get('error'):
                ret['error'] = ''
            else:
                logging.warning('error: %s' , ret['error'], extra={"artist":self.band})

        ret['discovered'] = True
        logging.debug('normalized dict :%s' , ret, extra={"artist":self.band})
        return ret


    # issue#4 given the dict in input, this funcion returns
    # 'person' , 'group_or_band', or nothing at all.
    # It might happens that a band has no Infobox, but alredy
    # exists in the crawling process because it was referenced before hand.
    # In that case, the type must be known already.
    def _band_or_person(self, doc):
        # if the background is there and is valid, that's easy
        if 'background' in doc:
            if doc['background'].lower() == 'person':
                return 'person'
            if doc['background'].lower() == 'group_or_band':
                return 'group_or_band'
        # if the backgroupnd is not valid, we have to figure it out
        # any of the following parameters hints that it's a band or a musician
        band_params = [ 'current_members', 'past_members', 'spinoffs', 'spinoff_of' ]
        person_params = [ 'current_member_of', 'past_member_of', 'occupation', 'instrument' ]
        for param in doc:
            if param in band_params:
                return 'group_or_band'
            if param in person_params:
                return 'person'


    def get_from_database(self, name, coll_name='artist', short=False):
        """
        This function gets a band from the database and returns its dictionary"""
        mongo_db = self._get_connection()
        if short:
            coll = mongo_db['artist_short']
        else:
            coll = mongo_db[coll_name]

        search = {"name":name}
        # workaround bug 35444921: use find instead of find_one
        # or we get ORA-40666 in some circumstances
        res = list(coll.find(search))
        # if it's already there, we rather set the artist with the full details of the result
        if len(res) == 1:
            return res[0]
        # if we have more than one document by querying my unique key, we have a problem
        assert len(res) == 0
        return False


    def _normalize_dict(self, doc, coll_name='artist'):
        # the exercise of filtering the accepted columns was relevant until 23.2.
        # in 23.3 the flex column allows for unknown values
        # that are unnested directly into the document.
        # as we are auto-referencing artists, the flex column changes the ETAG
        # of the table (to check with the devs), so we can't use Flex for this case.
        if coll_name == 'artist':
            accepted_keys = ['id','name','type','link','discovered','genre','label',
                             'current_member_of','past_member_of','past_members',
                             'current_members', 'spinoffs', 'spinoff_of']
            rejected_keys = ['_id','_metadata','members','member_of', 'error']
        else:
            # this is just a bad design hack. I should have splitted
            #  artists, genres, and labels into different classes
            accepted_keys = ['id','name']

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
                elif name in ['spinoffs','spinoff_of','genre','label']:
                    #don't add the array if empty
                    if len(value) != 0:
                        ret[name] = value
                else:
                    ret[name] = value
            else:
                # add the column even if unknown, as the flex column allows for it
                if coll_name == 'artist':
                    if name not in rejected_keys:
                        if not ret.get('extras'):
                            ret['extras'] = dict()
                        ret['extras'][name] = value
        return ret


    ########################
    # this insert a dict into a coll name. no questions
    def _insert_dict(self,doc,coll_name):
        mongo_db = self._get_connection()

        ## temporary, remove after debug, remove after debug
        coll_temp = coll_name.replace('_short','')
        coll = mongo_db[coll_temp]
        #coll = mongo_db[coll_name]

        logging.debug('inserting dict :%s - into collation %s',
                      doc, coll_name, extra={"artist":self.band})
        coll.insert_one(doc)
        logging.debug('inserted dict :%s - into collation %s',
                      doc, coll_name, extra={"artist":self.band})
        # insert_one modifies the dict with the _id included
        ret = self.get_from_database(doc['name'], coll_temp)

        logging.debug('got from database before normalization:%s',
                      ret, extra={"artist":self.band})
        ret = self._normalize_dict(ret, coll_temp)
        logging.debug('got from database after normalization:%s',
                      ret, extra={"artist":self.band})
        #ret['error'] = ''
        logging.debug('returning :%s' , ret, extra={"artist":self.band})
        return ret



    def upsert_artist(self,doc):
        """ This function upserts an artist in the database"""

        # we try to update the sub members only if there were no errors
        # otherwise we only have to update discovered and error
        updated = doc.copy()
        if doc['error'] != '':
            self._upsert_dict(updated,'artist')
            return
        for prop in ["member_of", "members", "spinoff_of", "spinoffs"]:
            if prop in doc:
                logging.debug('%s is there.' , prop, extra={"artist":self.band})
                updated[prop] = list()
                for _, value in enumerate(doc[prop]):
                    # if there is an artist relation, upsert it
                    # issue#4: I prepopulate the type, as when it's referenced
                    # I know already what it is
                    if prop == "members":
                        value['type']='person'
                    if prop == "member_of":
                        value['type']='group_or_band'
                    if prop in ["spinoff_of" , "spinoffs"]:
                        value['type']='group_or_band'
                    ret = self._upsert_dict(value,'artist_short')
                    if not ret.get('error'):
                        ret['error'] = ''
                    if '_id' in ret:
                        ret['id'] = ret['_id']
                        del ret['_id']
                    updated[prop].append(ret)

        for prop in ["genre", "label"]:
            if prop in doc:
                logging.debug('%s is there.' , prop, extra={"artist":self.band})
                updated[prop] = list()
                for _, value in enumerate(doc[prop]):
                    # insert in genres or labels
                    if 'link' in value:
                        del value['link']
                    ret = self._upsert_dict(value, prop )
                    if '_id' in ret:
                        ret['id'] = ret['_id']
                        del ret['_id']
                    updated[prop].append(ret)
        logging.debug('new doc: %s', updated, extra={"artist":self.band})
        self._upsert_dict(updated,'artist')



    # we pass here a relations [e.g. a genre or an artist
    # or a label] which we eventually insert if they are not there
    # it must return the definitive record for update
    def _upsert_dict(self,relation, coll_name):
        mongo_db = self._get_connection()
        coll = mongo_db[coll_name]

        logging.debug('upserting dict :%s - into collation %s' ,
                      relation, coll_name, extra={"artist":self.band})
        # the relation name is unique so we can use it as a key as well
        if relation.get('link') is not None:
            res = list(coll.find({'link': relation.get('link')}))
            if len(res) == 0:
                res = list(coll.find({'name': relation.get('name')}))
        else:
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

            logging.debug('need to update collextion %s document id %s with %s' ,
                          coll_name, res[0]['_id'], copy , extra={"artist":self.band})
            self._update_dict(res[0]['_id'], copy, coll_name)
            copy['id'] = res[0]['_id']
            logging.debug('returning %s' , copy , extra={"artist":self.band})
            return copy

        else:
            # if we have more than one document by querying my unique key, we have a problem
            assert len(res)==0
            assert relation['name'] != ''
            return self._insert_dict(relation, coll_name)


    def _strip_none(self,doc):
        return {key: value for key, value in doc.items() if value is not None}


    def _update_dict(self,doc_id, doc_set, coll_name):
        mongo_db = self._get_connection()
        coll = mongo_db[coll_name]
        logging.debug('updating doc id :%s - with %s - in collection %s' ,
                      doc_id, doc_set, coll_name, extra={"artist":self.band})
        coll.update_one({'_id':doc_id},{'$set':self._strip_none(doc_set)})
        logging.debug('updated doc id :%s - with %s - in collection %s' ,
                      doc_id, doc_set, coll_name, extra={"artist":self.band})
