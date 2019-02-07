import pytest
import requests

from las import Receipt
from las.client import FileFormatException
from io import BytesIO


@pytest.fixture(scope='module')
def url(params):
    return params('receipt_url')


@pytest.fixture(scope='module')
def filename(params):
    return params('receipt_filename')


def scan_receipt(client, receipt, **kwargs):
    response = client.scan_receipt(receipt=receipt, **kwargs)
    for detection in response.detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_receipt_with_url(url, client):
    receipt = Receipt(url=url)
    scan_receipt(client, receipt)


def test_scan_receipt_with_filename(filename, client):
    receipt = Receipt(filename=filename)
    scan_receipt(client, receipt)


def test_scan_receipt_with_kwargs(filename, client):
    receipt = Receipt(filename=filename)
    scan_receipt(client, receipt, **{'foo': 1})


def test_scan_receipt_with_junk(client):
    fp = BytesIO(b'junk')
    invoice = Receipt(fp=fp)

    with pytest.raises(FileFormatException):
        scan_receipt(client, invoice)


def test_scan_receipt_with_bad_image(client):
    fp = BytesIO(b'\x00' * 6 + b'JFIF')
    receipt = Receipt(fp=fp)
    with pytest.raises(requests.HTTPError):
        client.scan_receipt(receipt=receipt)
