import pytest

from las import Receipt
from las.client import LimitExceededException


@pytest.fixture(scope='module')
def url(params):
    return params('receipt_url')


@pytest.fixture(scope='module')
def filename(params):
    return params('receipt_filename')


@pytest.fixture(scope='module')
def receipts_with_url(url):
    return {
        'r1': Receipt(url=url),
        'r2': Receipt(url=url),
        'r3': Receipt(url=url)
    }


@pytest.fixture(scope='module')
def transactions():
    return {
        't1': {'total': '54.50', 'date': '2007-07-03'},
        't2': {'total': '3.59', 'date': '2014-08-06'},
        't3': {'total': 54.50, 'date': '2007-07-30'}
    }


@pytest.fixture(scope='module')
def matching_fields():
    return [
        'total',
        'date'
    ]


def test_match_receipts_with_url1(receipts_with_url, transactions, matching_fields, client):
    response = client.match_receipts(
        transactions=transactions,
        receipts=receipts_with_url,
        matching_fields=matching_fields
    )

    matched = response.matched_transactions
    unmatched = response.unmatched_transactions

    assert matched.get('t3') and matched['t3'] in ['r1', 'r2', 'r3']
    assert 't1' in unmatched and 't2' in unmatched


def test_match_receipts_with_url2(receipts_with_url, transactions, matching_fields, client):
    matching_strategy = {
        'total': {'maximumDeviation': 0.0},
        'date': {'maximumDeviation': 27}
    }

    response = client.match_receipts(
        transactions=transactions,
        receipts=receipts_with_url,
        matching_fields=matching_fields,
        matching_strategy=matching_strategy
    )

    matched = response.matched_transactions
    unmatched = response.unmatched_transactions

    assert matched.get('t1') and matched['t1'] in ['r1', 'r2', 'r3']
    assert matched.get('t3') and matched['t3'] in ['r1', 'r2', 'r3']
    assert 't2' in unmatched


def test_match_receipts_with_url3(receipts_with_url, transactions, matching_fields, client):
    matching_strategy = {
        'date': {
            'minimum': '2007-07-10',
            'maximum': '2007-08-10'
        }
    }

    response = client.match_receipts(
        transactions=transactions,
        receipts=receipts_with_url,
        matching_fields=matching_fields,
        matching_strategy=matching_strategy
    )

    matched = response.matched_transactions
    unmatched = response.unmatched_transactions
    predictions = response.predictions

    assert matched.get('t1') and matched['t1'] in ['r1', 'r2', 'r3']
    assert matched.get('t3') and matched['t3'] in ['r1', 'r2', 'r3']
    assert 't2' in unmatched

    for r_id, receipt_predictions in predictions.items():
        assert r_id in ['r1', 'r2', 'r3']

        for detection in receipt_predictions:
            assert 0 <= detection['confidence'] <= 1
            assert detection['value']
            assert detection['label']


def test_match_receipts_with_filename(filename, transactions, matching_fields, client):
    receipts = {
        'r1': Receipt(filename=filename),
        'r2': Receipt(filename=filename),
        'r3': Receipt(filename=filename)
    }

    response = client.match_receipts(
        transactions=transactions,
        receipts=receipts,
        matching_fields=matching_fields
    )

    matched = response.matched_transactions
    unmatched = response.unmatched_transactions

    assert matched.get('t3') and matched['t3'] in ['r1', 'r2', 'r3']
    assert 't1' in unmatched and 't2' in unmatched


def test_match_receipts_error(filename, transactions, matching_fields, client):
    receipts = {
        'r{}'.format(i): Receipt(filename=filename)
        for i in range(20)
    }

    try:
        client.match_receipts(
            transactions=transactions,
            receipts=receipts,
            matching_fields=matching_fields
        )
        assert False
    except LimitExceededException:
        assert True

