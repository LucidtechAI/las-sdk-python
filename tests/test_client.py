import pytest
import requests
import pathlib

from las import Client
from las.client import TooManyRequestsException, InvalidCredentialsException, LimitExceededException
from typing import Iterable
from uuid import uuid4
from unittest.mock import patch, Mock


def test_post_documents(client: Client, document_paths: Iterable[str], document_mime_types: Iterable[str]):
    for document_path, document_mime_type in zip(document_paths, document_mime_types):
        consent_id = str(uuid4())
        content = pathlib.Path(document_path).read_bytes()
        post_documents_response = client.post_documents(content, document_mime_type, consent_id)

        assert 'documentId' in post_documents_response, 'Missing documentId in response'
        assert 'consentId' in post_documents_response, 'Missing consentId in response'
        assert 'contentType' in post_documents_response, 'Missing contentType in response'


def test_post_document_id(client: Client, document_id: str):
    feedback = [
        {'label': 'total_amount', 'value': '54.50'},
        {'label': 'purchase_date', 'value': '2007-07-30'}
    ]

    post_document_id_response = client.post_document_id(document_id, feedback)

    assert 'feedback' in post_document_id_response, 'Missing feedback in response'
    assert 'documentId' in post_document_id_response, 'Missing documentId in response'
    assert 'consentId' in post_document_id_response, 'Missing consentId in response'


def test_delete_consent_id(client: Client, consent_id: str):
    delete_consent_id_response = client.delete_consent_id(consent_id)

    assert 'consentId' in delete_consent_id_response, 'Missing consentId in response'
    assert 'documentIds' in delete_consent_id_response, 'Missing documentIds in response'


@patch('requests.post')
@patch('requests.delete')
def test_invalid_credentials(delete_mock, post_mock, typed_content, client: Client):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Forbidden'}),
        raise_for_status=raise_for_status,
        status_code=403
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    content, mime_type = typed_content

    with pytest.raises(InvalidCredentialsException):
        client.post_documents(content, mime_type, 'foobar')

    with pytest.raises(InvalidCredentialsException):
        client.post_predictions('foobar', 'invoice')

    with pytest.raises(InvalidCredentialsException):
        client.post_document_id('foobar', [{'foo': 'bar'}])

    with pytest.raises(InvalidCredentialsException):
        client.delete_consent_id('foobar')


@patch('requests.post')
@patch('requests.delete')
def test_too_many_requests(delete_mock, post_mock, typed_content, client: Client):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Too Many Requests'}),
        raise_for_status=raise_for_status,
        status_code=429
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    content, mime_type = typed_content

    with pytest.raises(TooManyRequestsException):
        client.post_documents(content, mime_type, 'foobar')

    with pytest.raises(TooManyRequestsException):
        client.post_predictions('foobar', 'invoice')

    with pytest.raises(TooManyRequestsException):
        client.post_document_id('foobar', [{'foo': 'bar'}])

    with pytest.raises(TooManyRequestsException):
        client.delete_consent_id('foobar')


@patch('requests.post')
@patch('requests.delete')
def test_limit_exceeded(delete_mock, post_mock, typed_content, client: Client):
    raise_for_status = Mock(side_effect=requests.HTTPError())

    too_many_requests_mock = Mock(
        json=Mock(return_value={'message': 'Limit Exceeded'}),
        raise_for_status=raise_for_status,
        status_code=429
    )

    delete_mock.return_value = too_many_requests_mock
    post_mock.return_value = too_many_requests_mock

    content, mime_type = typed_content

    with pytest.raises(LimitExceededException):
        client.post_documents(content, mime_type, 'foobar')

    with pytest.raises(LimitExceededException):
        client.post_predictions('foobar', 'invoice')

    with pytest.raises(LimitExceededException):
        client.post_document_id('foobar', [{'foo': 'bar'}])

    with pytest.raises(LimitExceededException):
        client.delete_consent_id('foobar')
