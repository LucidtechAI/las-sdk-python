import pytest

from las import Client
from typing import Iterable
from uuid import uuid4


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


def test_delete_consent_id(client: Client, consent_id):
    delete_consent_id_response = client.delete_consent_id(consent_id)

    assert 'consentId' in delete_consent_id_response, 'Missing consentId in response'
    assert 'documentIds' in delete_consent_id_response, 'Missing documentIds in response'
