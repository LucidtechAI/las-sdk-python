import json

import requests_mock
import pytest
from las.client import InvalidCredentialsException, LimitExceededException, TooManyRequestsException

from . import service


@pytest.fixture(scope='module')
def client_with_access_token(client):
    _ = client.credentials.access_token
    return client


@pytest.mark.parametrize('error_code,error_content,error_name', [
    (429, json.dumps({'message': 'Limit Exceeded'}).encode(), LimitExceededException),
    (429, json.dumps({'message': 'Too Many Requests'}).encode(), TooManyRequestsException),
    (403, json.dumps({'message': 'Forbidden'}).encode(), InvalidCredentialsException),
])
def test_invalid_credentials(
    error_code,
    error_content,
    error_name,
    content,
    mime_type,
    client_with_access_token,
):

    client = client_with_access_token
    consent_id = service.create_consent_id()
    document_id = service.create_document_id()
    model_id = service.create_model_id()

    with requests_mock.Mocker() as m:
        m.post('/'.join([client.endpoint, 'documents']), status_code=error_code, content=error_content)
        m.post('/'.join([client.endpoint, 'predictions']), status_code=error_code, content=error_content)
        m.patch('/'.join([client.endpoint, 'documents', document_id]), status_code=error_code, content=error_content)
        m.delete('/'.join([client.endpoint, 'documents']), status_code=error_code, content=error_content)

        with pytest.raises(error_name):
            client.create_document(content, mime_type, consent_id=consent_id)

        with pytest.raises(error_name):
            client.create_prediction(document_id, model_id)

        with pytest.raises(error_name):
            client.update_document(document_id, [{'foo': 'bar'}])

        with pytest.raises(error_name):
            client.delete_documents(consent_id=consent_id)
