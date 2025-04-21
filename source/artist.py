"""
The artist class gets a band name and returns a dictionary
with a lot of information about the band
The dictionary is then stored in the database"""
from json_entity import JsonEntity
from genre import Genre
from label import Label
from artist_short import ArtistShort

class Artist(JsonEntity):
    """
    The Artist class gets a band name and returns a dictionary
    with a lot of information about the band
    The dictionary is then stored in the database"""

    accepted_keys = ['id','name','background','link','genre','label',
                     'current_member_of','past_member_of','past_members',
                     'current_members', 'spinoffs', 'spinoff_of']
    rejected_keys = ['_metadata','members','member_of']

    def __init__(self, doc):
        super().__init__(doc)
        self.doc = self.doc # pylint: disable=no-member


    @property
    def collection(self):
        return 'artist'

    # issue#4 given the dict in input, this funcion returns
    # 'person' , 'group_or_band', or nothing at all.
    # It might happens that a band has no Infobox, but alredy
    # exists in the crawling process because it was referenced before hand.
    # In that case, the background must be known already.
    def _band_or_person(self):
        # if the background is there and is valid, that's easy
        if 'background' in self.doc:
            if self.doc['background'].lower() == 'person':
                self.doc['background'] = 'person'
                return
            if self.doc['background'].lower() == 'group_or_band':
                self.doc['background'] = 'group_or_band'
                return
            # if the background is not person or group_or_band, we remove it and try to compute it from other fields
            self.doc.pop('background', None)
        # if the backgroupnd is not valid, we have to figure it out
        # any of the following parameters hints that it's a band or a musician
        band_params = [ 'current_members', 'past_members', 'members', 'spinoffs', 'spinoff_of' ]
        person_params = [ 'current_member_of', 'past_member_of', 'member_of', 'occupation', 'instrument' ]
        for param in self.doc:
            if param in band_params:
                self.doc['background'] = 'group_or_band'
                return
            if param in person_params:
                self.doc['background'] = 'person'
                return

    def _merge_members(self):
        # Merge 'current_member_of' and 'past_member_of' into 'member_of'
        if 'current_member_of' in self.doc or 'past_member_of' in self.doc:
            self.doc['member_of'] = (self.doc.get('current_member_of', []) +
                                     self.doc.get('past_member_of', []))
            self.doc.pop('current_member_of', None)
            self.doc.pop('past_member_of', None)
        # Merge 'current_members' and 'past_members' into 'members'
        if 'current_members' in self.doc or 'past_members' in self.doc:
            self.doc['members'] = (self.doc.get('current_members', []) +
                                   self.doc.get('past_members', []))
            self.doc.pop('current_members', None)
            self.doc.pop('past_members', None)


    def _normalize(self):
        """
        _normalize in Artist does a bunch of additional things:
        * It merge the properties:
          * 'current_member_of','past_member_of' into 'member_of'
          * 'current_members','past_members' into 'members'
        * It instantiate Genre and Labels to do sub-normalization
          of the genres and labels
        * It sets the background to 'person' or 'group_or_band'
        """
        super()._normalize()
        self._merge_members()
        self._band_or_person()

        if 'genre' in self.doc:
            # for each genre in self.doc, instantiate a Genre object.
            # the constructor will normalize the genre
            self.doc['genre'] = [ Genre(genre).doc for genre in self.doc['genre'] ]

        if 'label' in self.doc:
            # for each label in self.doc, instantiate a Label object
            # the constructor will normalize the label
            self.doc['label'] = [ Label(label).doc for label in self.doc['label'] ]

        # for these fields, if they have no background yet,
        # if the artist has members, the members are a person, etc.
        # the subroutine will normalize and set the background
        self._normalize_sub_artist('members', 'person')
        self._normalize_sub_artist('member_of', 'group_or_band')
        self._normalize_sub_artist('spinoffs', 'group_or_band')
        self._normalize_sub_artist('spinoff_of', 'group_or_band')


    def _normalize_sub_artist(self, index, background):
        if index in self.doc:
            artists = []
            for artist in self.doc[index]:
                artist_obj = ArtistShort(artist)
                if 'background' not in artist_obj.doc:
                    artist_obj.doc['background'] = background
                artists.append(artist_obj.doc)
            self.doc[index] = artists

    def _get_query(self):
        # we override the definition in artist to use link before name
        if self.doc.get('id') is not None:
            return {'_id': self.doc['id']}
        elif self.doc.get('link') is not None:
            return {'link': self.doc['link']}
        else:
            return {'name': self.doc['name']}

    def upsert(self):
        self._get_connection()
        coll = self.mongo_db[self.collection]

        # as the referenced n:m relationship cannot be inserted directly
        # we have to insert the referenced documents first.
        # We don't care about upserting them, as we just need their existence.
        # the insert function silently exists if the document already exists.
        # any updates will eventually go through the main document upsert.
        if 'label' in self.doc:
            for label in self.doc['label']:
                Label(label).insert()
        if 'genre' in self.doc:
            for genre in self.doc['genre']:
                Genre(genre).insert()
        if 'member_of' in self.doc:
            for artist in self.doc['member_of']:
                if 'link' not in artist:
                    artist['link'] = ''
                ArtistShort(artist).insert()
        if 'members' in self.doc:
            for artist in self.doc['members']:
                if 'link' not in artist:
                    artist['link'] = ''
                ArtistShort(artist).insert()
        if 'spinoffs' in self.doc:
            for artist in self.doc['spinoffs']:
                if 'link' not in artist:
                    artist['link'] = ''
                ArtistShort(artist).insert()
        if 'spinoff_of' in self.doc:
            for artist in self.doc['spinoff_of']:
                if 'link' not in artist:
                    artist['link'] = ''
                ArtistShort(artist).insert()

        # now there's the catch_:
        # even if an artist has been previously inserted through a short insert,
        # it might still have relations to other artists due to other
        # inserts. So we have to merge into the new document (self.doc)
        # the entries from the old one (query_result)
        # especially the relations:
        # 'member_of', 'members', 'spinoffs', 'spinoff_of'
        # so we don't miss any relations.
        # we can't use @nodelete as a safeguard in the
        # duality views, not to miss any relation by mistake, because the relation_id might change.
        query = self._get_query()
        query_result = coll.find_one(query)

        if query_result:
            # here we must remove id and members_id from query_result
            # I don't bother to check if they exist 
            for field in ['member_of', 'members', 'spinoffs', 'spinoff_of']:
                if field in query_result:
                    if field in self.doc:
                        self.doc[field] = self._merge_arrays_by_name(self.doc[field],query_result[field])

            self.doc['id'] = query_result['_id']

        # not sure it's the best place to put this, but if everything is OK, we can set discovered=true
        self.doc['discovered'] = True
        super().upsert()


    def _merge_arrays_by_name(self,array1,array2):
        # merge array2 into array1
        existing_names = {d["name"] for d in array1}
        for dictio in array2:
            # remove id from dictio only if it exists
            if 'id' in dictio:
                del dictio['id']
            if 'id' in dictio:
                del dictio['members_id']
            if dictio["name"] not in existing_names:
                array1.append(dictio)
                existing_names.add(dictio["name"])
        return array1