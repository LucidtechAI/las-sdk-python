import pytest
import configparser

from functools import partial
from las import Client


@pytest.fixture(scope='module')
def params(cfg):
    config = configparser.ConfigParser()
    config.read(cfg)
    return partial(config.get, 'match_receipts')


@pytest.fixture(scope='module')
def api_key(params):
    return params('api_key')


@pytest.fixture(scope='module')
def url(params):
    return params('url')


@pytest.fixture(scope='module')
def fp(params):
    filename = params('filename')
    return open(filename, 'rb')


def test_scan_receipt_with_url(url, api_key):
    client = Client(api_key)
    detections = client.scan_receipt(receipt_url=url)
    for detection in detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_receipt_with_fp(fp, api_key):
    client = Client(api_key)
    detections = client.scan_receipt(receipt_fp=fp)
    for detection in detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_receipt_with_none(api_key):
    client = Client(api_key)
    try:
        client.scan_receipt()
        assert False
    except Exception as e:
        assert e
