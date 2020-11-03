import pathlib
from typing import Iterable
from unittest.mock import Mock, patch

import requests

import pytest
from las.client import BaseClient, InvalidCredentialsException, LimitExceededException, TooManyRequestsException
from . import util

pytestmark = pytest.mark.integration


@patch('requests.post')
@patch('requests.delete')
def test_invalid_credentials(delete_mock, post_mock, typed_content, client: BaseClient):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    invalid_credentials_mock = Mock(
        json=Mock(return_value={'message': 'Forbidden'}),
        raise_for_status=raise_for_status,
        status_code=403
    )

    delete_mock.return_value = invalid_credentials_mock
    post_mock.return_value = invalid_credentials_mock

    content, mime_type = typed_content
    consent_id = util.consent_id()
    document_id = util.document_id()
    model_id = util.model_id()

    with pytest.raises(InvalidCredentialsException):
        client.create_document(content, mime_type, consent_id)

    with pytest.raises(InvalidCredentialsException):
        client.create_prediction(document_id, model_id)

    with pytest.raises(InvalidCredentialsException):
        client.update_document(document_id, [{'foo': 'bar'}])

    with pytest.raises(InvalidCredentialsException):
        client.delete_documents(consent_id)


@patch('requests.post')
@patch('requests.delete')
def test_too_many_requests(delete_mock, post_mock, typed_content, client: BaseClient):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Too Many Requests'}),
        raise_for_status=raise_for_status,
        status_code=429
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    content, mime_type = typed_content
    consent_id = util.consent_id()
    document_id = util.document_id()
    model_id = util.model_id()

    with pytest.raises(TooManyRequestsException):
        client.create_document(document_id, mime_type, consent_id)

    with pytest.raises(TooManyRequestsException):
        client.create_prediction(document_id, model_id)

    with pytest.raises(TooManyRequestsException):
        client.update_document(document_id, [{'foo': 'bar'}])

    with pytest.raises(TooManyRequestsException):
        client.delete_documents(consent_id)


@patch('requests.post')
@patch('requests.delete')
def test_limit_exceeded(delete_mock, post_mock, typed_content, client: BaseClient):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Limit Exceeded'}),
        raise_for_status=raise_for_status,
        status_code=429
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    content, mime_type = typed_content
    consent_id = util.consent_id()
    document_id = util.document_id()
    model_id = util.model_id()

    with pytest.raises(LimitExceededException):
        client.create_document(content, mime_type, consent_id)

    with pytest.raises(LimitExceededException):
        client.create_prediction(document_id, model_id)

    with pytest.raises(LimitExceededException):
        client.update_document(document_id, [{'foo': 'bar'}])

    with pytest.raises(LimitExceededException):
        client.delete_documents(consent_id)
