from json_entity import JsonEntity

class Genre(JsonEntity):

    use_extras = False

    @property
    def collection(self):
        return 'genre'

    def _normalize(self):
        super()._normalize()
        self.doc['name'] = self.doc['name'].title()
