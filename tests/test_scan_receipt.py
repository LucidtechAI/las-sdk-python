import pytest

from las import Receipt


@pytest.fixture(scope='module')
def url(params):
    return params('receipt_url')


@pytest.fixture(scope='module')
def filename(params):
    return params('receipt_filename')


def scan_receipt(client, receipt):
    detections = client.scan_receipt(receipt=receipt)
    for detection in detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_receipt_with_url(url, client):
    receipt = Receipt(url=url)
    scan_receipt(client, receipt)


def test_scan_receipt_with_filename(filename, client):
    receipt = Receipt(filename=filename)
    scan_receipt(client, receipt)
