import pathlib
import tempfile
from typing import Iterable

import pytest

from las import Client, Field
from las.client import FileFormatException

pytestmark = pytest.mark.integration


def test_send_feedback(client: Client, document_id: str):
    feedback = [Field(label='total_amount', value='120.00'), Field(label='purchase_date', value='2019-03-10')]
    response = client.send_feedback(document_id, feedback)

    assert 'feedback' in response, 'Missing feedback in response'
    assert 'documentId' in response, 'Missing documentId in response'
    assert 'consentId' in response, 'Missing consentId in response'


def test_invalid_file_format(client: Client, model_ids: Iterable[str]):
    for model_id in model_ids:
        with tempfile.NamedTemporaryFile() as fp:
            with pytest.raises(FileFormatException):
                client.predict(fp.name, model_id=model_id)


def test_predict(monkeypatch, client: Client, document_paths: Iterable[str],
                 model_ids: Iterable[str], content: bytes):
    monkeypatch.setattr(pathlib.Path, 'read_bytes', lambda _: content)

    for document_path, model_id in zip(document_paths, model_ids):
        prediction = client.predict(document_path, model_id=model_id)

        assert prediction.document_id, 'Missing document_id in prediction'
        assert prediction.consent_id, 'Missing consent_id in prediction'
        assert prediction.model_id, 'Missing model_id in prediction'
        assert prediction.fields, 'Missing fields in prediction'

        for field in prediction.fields:
            assert field.label, 'Missing label in field'
            assert type(field.label) == str, 'Label is not str'
            assert field.confidence, 'Missing confidence in field'
            assert 0.0 <= field.confidence <= 1.0, 'Confidence not between 0 and 1'
            assert type(field.value) == str, 'Value is not str'
