from typing import Dict, Union, Optional


class Field(Dict[str, Union[Optional[str], bool]]):
    def __init__(self, label: str, value: Union[Optional[str], bool], confidence: float = None):
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


class Prediction(Dict[str, str]):
    def __init__(self, document_id: str, consent_id: str, model_id: str, prediction_response: dict):
        prediction = dict(
            document_id=document_id,
            consent_id=consent_id,
            model_id=model_id,
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
    def model_id(self):
        return self['model_id']

    @property
    def fields(self):
        return [Field(**field) for field in self['fields']]
