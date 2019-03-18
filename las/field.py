class Field(dict):
    def __init__(self, label, value, confidence=None):
        field = dict(label=label, value=value)
        field = dict(**field, confidence=confidence) if confidence else field
        super().__init__(**field)

    @property
    def label(self):
        return self['label']

    @property
    def value(self):
        return self['value']

    @property
    def confidence(self):
        return self.get('confidence')
