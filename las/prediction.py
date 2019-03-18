from .field import Field


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
