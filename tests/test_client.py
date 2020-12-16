import json
import uuid
from base64 import b64encode, b64decode
from pathlib import Path

import requests_mock
import pytest
from las.client import InvalidCredentialsException, LimitExceededException, TooManyRequestsException, parse_content

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


@pytest.mark.parametrize('content', [
    __file__,
    Path(__file__),
    open(__file__, 'rb'),
    open(__file__, 'r'),
    open(__file__),
    Path(__file__).open(),
    Path(__file__).open('rb'),
    Path(__file__).open('r'),
    Path(__file__).read_bytes(),
    Path(__file__).read_text().encode(),
    b64encode(Path(__file__).read_bytes()),
])
def test_parse_content(content):
    expected_result = b64encode(Path(__file__).read_bytes()).decode()
    result = parse_content(content)
    assert result == expected_result


@pytest.mark.parametrize(('content', 'error'), [
    (uuid.uuid4().hex, FileNotFoundError),
    (Path(uuid.uuid4().hex), FileNotFoundError),
    (Path(__file__).read_bytes().decode(), OSError),
    (Path(__file__).read_text()[0:30], FileNotFoundError),
    (b64encode(Path(__file__).read_bytes()).decode()[0:30], FileNotFoundError),
    (1, TypeError),
    (0.1, TypeError),
    (bytearray(b'abc'), TypeError),
])
def test_parse_erroneous_content(content, error):
    with pytest.raises(error):
        parse_content(content)
