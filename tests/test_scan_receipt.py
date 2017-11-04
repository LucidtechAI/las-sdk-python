import pytest


@pytest.fixture(scope='module')
def url(params):
    return params('url')


@pytest.fixture(scope='module')
def fp(params):
    filename = params('filename')
    return open(filename, 'rb')


def test_scan_receipt_with_url(url, client):
    detections = client.scan_receipt(receipt_url=url)
    for detection in detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_receipt_with_fp(fp, client):
    detections = client.scan_receipt(receipt_fp=fp)
    for detection in detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_receipt_with_none(client):
    try:
        client.scan_receipt()
        assert False
    except Exception as e:
        assert e
