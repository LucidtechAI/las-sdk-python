import pytest


@pytest.fixture(scope='module')
def url(params):
    return params('url')


def test_match_receipts(url, client):
    receipts = {
        'r1': url,
        'r2': url,
        'r3': url
    }

    transactions = {
        't1': {'total': '100.00', 'date': '2014-08-06'},
        't2': {'total': '3.59', 'date': '2014-08-06'},
        't3': {'total': 100, 'date': '2014-06-08'}
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
