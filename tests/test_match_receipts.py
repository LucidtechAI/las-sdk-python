import pytest

from las import Receipt


@pytest.fixture(scope='module')
def url(params):
    return params('url')


@pytest.fixture(scope='module')
def filename(params):
    return params('filename')


def test_match_receipts_with_url(url, client):
    receipts = {
        'r1': Receipt(url=url),
        'r2': Receipt(url=url),
        'r3': Receipt(url=url)
    }

    transactions = {
        't1': {'total': '54.50', 'date': '2007-07-03'},
        't2': {'total': '3.59', 'date': '2014-08-06'},
        't3': {'total': 54.50, 'date': '2007-07-30'}
    }

    matching_fields = [
        'total',
        'date'
    ]

    response = client.match_receipts(
        transactions=transactions,
        receipts=receipts,
        matching_fields=matching_fields
    )

    matched = response['matchedTransactions']
    not_matched = response['notMatchedTransactions']

    assert matched.get('t3') and matched['t3'] in ['r1', 'r2', 'r3']
    assert 't1' in not_matched and 't2' in not_matched


def test_match_receipts_with_filename(filename, client):
    receipts = {
        'r1': Receipt(filename=filename),
        'r2': Receipt(filename=filename),
        'r3': Receipt(filename=filename)
    }

    transactions = {
        't1': {'total': '54.50', 'date': '2007-07-03'},
        't2': {'total': '3.59', 'date': '2014-08-06'},
        't3': {'total': 54.50, 'date': '2007-07-30'}
    }

    matching_fields = [
        'total',
        'date'
    ]

    response = client.match_receipts(
        transactions=transactions,
        receipts=receipts,
        matching_fields=matching_fields
    )

    matched = response['matchedTransactions']
    not_matched = response['notMatchedTransactions']

    assert matched.get('t3') and matched['t3'] in ['r1', 'r2', 'r3']
    assert 't1' in not_matched and 't2' in not_matched
