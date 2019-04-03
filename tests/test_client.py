import pytest
import requests

from las import Client
from las.client import TooManyRequestsException, InvalidCredentialsException, LimitExceededException
from typing import Iterable
from uuid import uuid4
from unittest.mock import patch, Mock


def test_post_documents(client: Client, document_mime_types: Iterable[str]):
    for document_mime_type in document_mime_types:
        consent_id = str(uuid4())
        post_documents_response = client.post_documents(document_mime_type, consent_id)

        assert 'uploadUrl' in post_documents_response, 'Missing uploadUrl in response'
        assert 'documentId' in post_documents_response, 'Missing documentId in response'
        assert 'consentId' in post_documents_response, 'Missing consentId in response'
        assert 'contentType' in post_documents_response, 'Missing contentType in response'


@pytest.fixture(scope='function', params=['image/jpeg', 'application/pdf'])
def document_id(request, client: Client):
    consent_id = str(uuid4())
    post_documents_response = client.post_documents(request.param, consent_id)
    yield post_documents_response['documentId']


def test_post_document_id(client: Client, document_id: str):
    feedback = [
        {'label': 'total_amount', 'value': '54.50'},
        {'label': 'purchase_date', 'value': '2007-07-30'}
    ]

    post_document_id_response = client.post_document_id(document_id, feedback)

    assert 'feedback' in post_document_id_response, 'Missing feedback in response'
    assert 'documentId' in post_document_id_response, 'Missing documentId in response'
    assert 'consentId' in post_document_id_response, 'Missing consentId in response'


@pytest.fixture(scope='function', params=['image/jpeg', 'application/pdf'])
def consent_id(request, client: Client):
    consent_id = str(uuid4())
    client.post_documents(request.param, consent_id)
    yield consent_id


def test_delete_consent_id(client: Client, consent_id: str):
    delete_consent_id_response = client.delete_consent_id(consent_id)

    assert 'consentId' in delete_consent_id_response, 'Missing consentId in response'
    assert 'documentIds' in delete_consent_id_response, 'Missing documentIds in response'


@patch('requests.post')
@patch('requests.delete')
def test_invalid_credentials(delete_mock, post_mock, client: Client):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Forbidden'}),
        raise_for_status=raise_for_status,
        status_code=403
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    with pytest.raises(InvalidCredentialsException):
        client.post_documents('image/jpeg', 'foobar')

    with pytest.raises(InvalidCredentialsException):
        client.post_predictions('foobar', 'invoice')

    with pytest.raises(InvalidCredentialsException):
        client.post_document_id('foobar', [{'foo': 'bar'}])

    with pytest.raises(InvalidCredentialsException):
        client.delete_consent_id('foobar')


@patch('requests.post')
@patch('requests.delete')
def test_too_many_requests(delete_mock, post_mock, client: Client):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Too Many Requests'}),
        raise_for_status=raise_for_status,
        status_code=429
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    with pytest.raises(TooManyRequestsException):
        client.post_documents('image/jpeg', 'foobar')

    with pytest.raises(TooManyRequestsException):
        client.post_predictions('foobar', 'invoice')

    with pytest.raises(TooManyRequestsException):
        client.post_document_id('foobar', [{'foo': 'bar'}])

    with pytest.raises(TooManyRequestsException):
        client.delete_consent_id('foobar')


@patch('requests.post')
@patch('requests.delete')
def test_limit_exceeded(delete_mock, post_mock, client: Client):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Limit Exceeded'}),
        raise_for_status=raise_for_status,
        status_code=429
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    with pytest.raises(LimitExceededException):
        client.post_documents('image/jpeg', 'foobar')

    with pytest.raises(LimitExceededException):
        client.post_predictions('foobar', 'invoice')

    with pytest.raises(LimitExceededException):
        client.post_document_id('foobar', [{'foo': 'bar'}])

    with pytest.raises(LimitExceededException):
        client.delete_consent_id('foobar')
