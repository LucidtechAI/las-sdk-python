import pytest

from las import Receipt


@pytest.fixture(scope='module')
def url(params):
    return params('url')


@pytest.fixture(scope='module')
def filename(params):
    return params('filename')


def upload_receipt(client, receipt):
    receipt_id = client._upload_receipt(receipt)
    assert receipt_id


def test_upload_receipt_with_filename(filename, client):
    receipt = Receipt(filename=filename)
    upload_receipt(client, receipt)


def test_upload_receipt_with_url(url, client):
    receipt = Receipt(url=url)
    upload_receipt(client, receipt)
