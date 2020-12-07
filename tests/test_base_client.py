import requests

import pytest

from unittest.mock import Mock, patch

from las.client import InvalidCredentialsException, LimitExceededException, TooManyRequestsException
from . import util


def create_invalid_credentials_mock():
    return Mock(
        json=Mock(return_value={'message': 'Forbidden'}),
        raise_for_status=Mock(side_effect=requests.HTTPError()),
        status_code=403,
    )


def create_too_many_requests_mock():
    return Mock(
        json=Mock(return_value={'message': 'Too Many Requests'}),
        raise_for_status=Mock(side_effect=requests.HTTPError()),
        status_code=429,
    )


def create_limit_exceeded_mock():
    return Mock(
        json=Mock(return_value={'message': 'Limit Exceeded'}),
        raise_for_status=Mock(side_effect=requests.HTTPError()),
        status_code=429,
    )


@pytest.fixture(scope='module')
def client_with_access_token(client):
    _ = client.credentials.access_token
    return client


@patch('requests.post')
@patch('requests.patch')
@patch('requests.delete')
@pytest.mark.parametrize('error_mock,error_name', [
    (create_invalid_credentials_mock(), InvalidCredentialsException),
    (create_too_many_requests_mock(), TooManyRequestsException),
    (create_limit_exceeded_mock(), LimitExceededException),
])
def test_invalid_credentials(
    post_mock,
    patch_mock,
    delete_mock,
    error_mock,
    error_name,
    typed_content,
    client_with_access_token,
):

    client = client_with_access_token
    delete_mock.return_value = error_mock
    post_mock.return_value = error_mock
    patch_mock.return_value = error_mock

    content, mime_type = typed_content
    consent_id = util.consent_id()
    document_id = util.document_id()
    model_id = util.model_id()

    with pytest.raises(error_name):
        client.create_document(content, mime_type, consent_id=consent_id)

    with pytest.raises(error_name):
        client.create_prediction(document_id, model_id)

    with pytest.raises(error_name):
        client.update_document(document_id, [{'foo': 'bar'}])

    with pytest.raises(error_name):
        client.delete_documents(consent_id=consent_id)
