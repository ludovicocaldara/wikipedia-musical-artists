from json_entity import JsonEntity
class Label(JsonEntity):

    use_extras = False

    @property
    def collection(self):
        return 'label'
