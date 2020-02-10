import pathlib
from typing import Iterable
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
import requests

from las import Client
from las.client import InvalidCredentialsException, LimitExceededException, TooManyRequestsException

pytestmark = pytest.mark.integration


def test_post_documents(monkeypatch, client: Client, document_paths: Iterable[str], document_mime_types: Iterable[str],
                        content):
    monkeypatch.setattr(pathlib.Path, 'read_bytes', lambda _: content)

    for document_path, document_mime_type in zip(document_paths, document_mime_types):
        consent_id = str(uuid4())
        content = pathlib.Path(document_path).read_bytes()
        post_documents_response = client.post_documents(content, document_mime_type, consent_id)

        assert 'documentId' in post_documents_response, 'Missing documentId in response'
        assert 'consentId' in post_documents_response, 'Missing consentId in response'
        assert 'contentType' in post_documents_response, 'Missing contentType in response'


def test_post_processes(client: Client, state_machine_arn: str):
    post_processes_response = client.post_processes(state_machine_arn, {})
    assert 'executionArn' in post_processes_response, 'Missing executionArn in response'


def test_post_tasks(client: Client, state_machine_arn: str, activity_arn: str):
    client.post_processes(state_machine_arn, {})
    post_tasks_response = client.post_tasks(activity_arn)
    assert 'taskId' in post_tasks_response, 'Missing taskId in response'
    assert 'taskToken' in post_tasks_response, 'Missing taskToken in response'
    assert 'taskData' in post_tasks_response, 'Missing taskData in response'


def test_patch_task_id(client: Client, state_machine_arn: str, activity_arn: str):
    client.post_processes(state_machine_arn, {'foo': 'bar'})
    post_tasks_response = client.post_tasks(activity_arn)
    task_id = post_tasks_response['taskId']
    task_result = {'message': 'Hello world!'}
    patch_task_id_response = client.patch_task_id(task_id, task_result)
    assert 'taskId' in patch_task_id_response, 'Missing taskId in response'
    assert 'taskResult' in patch_task_id_response, 'Missing taskResult in response'
    assert 'taskData' in patch_task_id_response, 'Missing taskData in response'


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
