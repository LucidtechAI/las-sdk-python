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


class Prediction(dict):
    def __init__(self, document_id: str, consent_id: str, model_name: str, prediction_response: dict):
        prediction = dict(
            document_id=document_id,
            consent_id=consent_id,
            model_name=model_name,
            fields=prediction_response['predictions']
        )

        super().__init__(**prediction)

    @property
    def document_id(self):
        return self['document_id']

    @property
    def consent_id(self):
        return self['consent_id']

    @property
    def model_name(self):
        return self['model_name']

    @property
    def fields(self):
        return [Field(**field) for field in self['fields']]
