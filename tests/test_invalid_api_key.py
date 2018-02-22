import pytest

from las import Receipt
from las.client import InvalidAPIKeyException


@pytest.fixture(scope='module')
def url(params):
    return params('receipt_url')


def test_invalid_api_key(url, client):
    receipt = Receipt(url=url)
    client.api_key = 'foo'

    try:
        client.scan_receipt(receipt)
        assert False
    except InvalidAPIKeyException:
        assert True
    except Exception:
        assert False
