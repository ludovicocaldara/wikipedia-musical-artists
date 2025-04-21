from json_entity import JsonEntity

class ArtistShort(JsonEntity):

    use_extras = False
    accepted_keys = ['id', 'name', 'link', 'background']

    @property
    def collection(self):
        return 'artist_short'

    def _normalize(self):
        super()._normalize()
        # if link is not there, add it from name
        # this is because we want to be able to query by link
        if 'link' not in self.doc:
            self.doc['link'] = self.doc['name']
