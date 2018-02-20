import pytest

from las import Invoice


@pytest.fixture(scope='module')
def url(params):
    return params('invoice_url')


@pytest.fixture(scope='module')
def filename(params):
    return params('invoice_filename')


def scan_invoice(client, invoice):
    response = client.scan_invoice(invoice=invoice)
    for detection in response.detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_invoice_with_url(url, client):
    invoice = Invoice(url=url)
    scan_invoice(client, invoice)


def test_scan_invoice_with_filename(filename, client):
    invoice = Invoice(filename=filename)
    scan_invoice(client, invoice)
