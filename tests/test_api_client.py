import pytest
import tempfile

from las import ApiClient, Client, Field
from las.api_client import FileFormatException
from typing import Iterable
from uuid import uuid4


def test_predict(api_client: ApiClient, document_paths: Iterable[str], model_names: Iterable[str]):
    for document_path, model_name in zip(document_paths, model_names):
        prediction = api_client.predict(document_path, model_name=model_name)

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


@pytest.fixture(scope='function', params=['image/jpeg', 'application/pdf'])
def document_id(request, client: Client):
    consent_id = str(uuid4())
    post_documents_response = client.post_documents(request.param, consent_id)
    yield post_documents_response['documentId']


def test_send_feedback(api_client: ApiClient, document_id: str):
    feedback = [Field(label='total_amount', value='120.00'), Field(label='purchase_date', value='2019-03-10')]
    response = api_client.send_feedback(document_id, feedback)

    assert 'feedback' in response, 'Missing feedback in response'
    assert 'documentId' in response, 'Missing documentId in response'
    assert 'consentId' in response, 'Missing consentId in response'


@pytest.fixture(scope='function', params=['image/jpeg', 'application/pdf'])
def consent_id(request, client: Client):
    consent_id = str(uuid4())
    client.post_documents(request.param, consent_id)
    yield consent_id


def test_revoke_consent(api_client: ApiClient, consent_id: str):
    response = api_client.delete_consent_id(consent_id)

    assert 'consentId' in response, 'Missing consentId in response'
    assert 'documentIds' in response, 'Missing documentIds in response'


def test_invalid_file_format(api_client: ApiClient, model_names: Iterable[str]):
    for model_name in model_names:
        with tempfile.NamedTemporaryFile() as fp:
            with pytest.raises(FileFormatException):
                api_client.predict(fp.name, model_name=model_name)
