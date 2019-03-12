from las import Api
from typing import Iterable


def test_prediction(api: Api, document_paths: Iterable[str], model_names: Iterable[str]):
    for document_path, model_name in zip(document_paths, model_names):
        prediction = api.predict(document_path, model_name=model_name)

        assert prediction.document_id, 'Missing document_id in prediction'
        assert prediction.consent_id, 'Missing consent_id in prediction'
        assert prediction.model_name, 'Missing model_name in prediction'
        assert prediction.fields, 'Missing fields in prediction'

        for field in prediction.fields:
            assert field.label, 'Missing label in field'
            assert type(field.label) == str, 'Label is not str'
            assert field.confidence, 'Missing confidence in field'
            assert 0.0 <= field.confidence <= 1.0, 'Confidence not between 0 and 1'
            assert type(field.value) == str, 'Value is not str'
