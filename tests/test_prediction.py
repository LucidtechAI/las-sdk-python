import pytest


@pytest.fixture(scope='module')
def invoice_path(params):
    return params('invoice_path')


def test_invoice_prediction(api, invoice_path):
    invoice_prediction = api.predict(invoice_path, model_name='invoice')

    assert invoice_prediction.document_id, 'Missing document_id in prediction'
    assert invoice_prediction.consent_id, 'Missing consent_id in prediction'
    assert invoice_prediction.model_name, 'Missing model_name in prediction'
    assert invoice_prediction.fields, 'Missing fields in prediction'

    for field in invoice_prediction.fields:
        assert field.label, 'Missing label in field'
        assert type(field.label) == str, 'Label is not str'
        assert field.confidence, 'Missing confidence in field'
        assert 0.0 <= field.confidence <= 1.0, 'Confidence not between 0 and 1'
        assert type(field.value) == str, 'Value is not str'


@pytest.fixture(scope='module')
def receipt_path(params):
    return params('receipt_path')


def test_receipt_prediction(api, receipt_path):
    receipt_prediction = api.predict(receipt_path, model_name='receipt')

    assert receipt_prediction.document_id, 'Missing document_id in prediction'
    assert receipt_prediction.consent_id, 'Missing consent_id in prediction'
    assert receipt_prediction.model_name, 'Missing model_name in prediction'
    assert receipt_prediction.fields, 'Missing fields in prediction'

    for field in receipt_prediction.fields:
        assert field.label, 'Missing label in field'
        assert type(field.label) == str, 'Label is not str'
        assert field.confidence, 'Missing confidence in field'
        assert 0.0 <= field.confidence <= 1.0, 'Confidence not between 0 and 1'
        assert type(field.value) == str, 'Value is not str'
