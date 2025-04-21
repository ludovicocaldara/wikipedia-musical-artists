"""
Define an abstract class
"""
import logging
from abc import ABC, abstractmethod
from pymongo.errors import WriteError


class JsonEntity(ABC):
    """ This is an abstract class that defines the interface for
    entities that we want to insert as JSON using Mongo DB.
    """

    # accepted_keys is used for filtering the accepted properties
    # inside the document.
    accepted_keys = ['id','name']
    # if extras is set to true, all keyes not explicitly accepted
    # will be added to the extras dictionary
    use_extras = True
    # explicitly rejected keys don't make it to extras even if
    # use_extras is set to True
    rejected_keys = []

    @property
    @abstractmethod
    def collection(self):
        """ The collection in which the document will be inserted """

    def __init__(self, doc):
        self.doc = doc

        log_format = ('%(asctime)s - %(levelname)-8s - ' +
                       self.doc['name'] + ' - %(funcName)-15s - %(message)s')
        logging.basicConfig(format=log_format, level=logging.ERROR)
        self._normalize()


    def _get_connection(self):
        if 'mongo_db' not in dir(self):
            from MongoFactory import mongo_db
            self.mongo_db = mongo_db


    def _normalize(self):
        '''
        _normalize redefines the document to:
        * include all the accepted keys
        * exclude the rejected keys
        * put in "extras" everything else.
        '''
        copy = dict()
        for name, value in self.doc.items():
            if name in self.rejected_keys or value == '' or value is None:
                pass
            elif name in self.accepted_keys:
                copy[name] = value
            else:
                if self.use_extras:
                    if 'extras' not in copy:
                        copy['extras'] = dict()
                    copy['extras'][name] = value
        self.doc = copy

    def _get_query(self):
        # Check if the document already exists
        # we give priority to id, then link, then name
        if self.doc.get('id') is not None:
            return {'_id': self.doc['id']}
        else:
            return {'name': self.doc['name']}

    def upsert(self):
        '''
        Instead of using pymongo find_and_update,
        we use insert_one and update_one for the upsert.
        Duality Views don't support direct upsert as of 23.6.
        '''
        self._get_connection()
        coll = self.mongo_db[self.collection]

        # if there is no id we try to find a matching record first
        # otherwise we go straight to the update
        self._to_id()

        if 'id' not in self.doc:

            query = self._get_query()
            query_result = coll.find_one(query)

            if query_result:
                query = {'_id': query_result['_id']}

                self._to_underscore_id()
                update = {'$set': self.doc}
                # If the document already exists, update it using its _id
                update_result = coll.update_one(query, update)
                if update_result.modified_count > 0:
                    print(f"Updated document {self.doc['name']}" +
                          " with _id: {self.doc['_id']} in {self.collection} collection")
                self._to_id()
            else:
                # Attempt to insert the document
                insert_result = coll.insert_one(self.doc)
                print(f"Inserted document {self.doc['name']}" +
                      f" with _id: {str(insert_result.inserted_id)} in {str(self.collection)} collection")
                self.doc['id'] = str(insert_result.inserted_id)
        else:
            query = self._get_query()
            self._to_underscore_id()
            update = {'$set': self.doc}
            # If the document already exists, update it using its _id
            update_result = coll.update_one(query, update)
            if update_result.modified_count > 0:
                print(f"Updated document {self.doc['name']}" +
                      f" with _id: {self.doc['_id']} in {self.collection} collection")
            self._to_id()

    def _to_underscore_id(self):
        # if self.doc['id'] is set, convert it to _id
        if self.doc.get('id') is not None:
            self.doc['_id'] = self.doc['id']
            del self.doc['id']

    def _to_id(self):
        # if _id is set, convert it to id
        if self.doc.get('_id') is not None:
            self.doc['id'] = self.doc['_id']
            del self.doc['_id']

    def insert(self):
        """ Insert the document in the collection,
        When we insert Artist's sub-document, we don't care about
        upserting them, as we just need their existence to insert
        the parent doc.
        """
        self._get_connection()
        coll = self.mongo_db[self.collection]
        try:
            insert_result = coll.insert_one(self.doc)
            print(f"Inserted document {self.doc['name']}" +
                   f" with _id: {insert_result.inserted_id} in {self.collection} collection")
        #except DuplicateKeyError:  DVs return WriteError as of 23.6
        except WriteError:
            print(f"Document {self.doc['name']} already exists in {self.collection} collection")
