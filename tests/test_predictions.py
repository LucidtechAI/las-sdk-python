import logging

import pytest
from las.client import Client, dictstrip

from . import service


@pytest.mark.parametrize('rotation', [0, 90, 180, 270, None])
@pytest.mark.parametrize('preprocess_config', [
    {'rotation': 0, 'autoRotate': True, 'maxPages': 1, 'imageQuality': 'LOW'},
    {'rotation': 90, 'autoRotate': False, 'maxPages': 2, 'imageQuality': 'HIGH'},
    {'rotation': 180, 'autoRotate': None, 'maxPages': 3, 'imageQuality': None},
    {'rotation': 270, 'autoRotate': True, 'maxPages': None, 'imageQuality': 'HIGH'},
    {'rotation': None, 'autoRotate': False, 'pages': [0, 1, -1], 'imageQuality': 'LOW'},
    None,
])
@pytest.mark.parametrize('postprocess_config', [
    {'strategy': 'BEST_FIRST'},
    {'strategy': 'BEST_N_PAGES', 'parameters': {'n': 3}},
    {'strategy': 'BEST_N_PAGES', 'parameters': {'n': 3, 'collapse': False}},
    None,
])
def test_create_prediction(client: Client, rotation, preprocess_config, postprocess_config):
    document_id = service.create_document_id()
    model_id = service.create_model_id()
    response = client.create_prediction(
        document_id,
        model_id,
        preprocess_config=dictstrip(preprocess_config) if preprocess_config else None,
        postprocess_config=postprocess_config,
    )
    assert 'predictionId' in response, 'Missing predictionId in response'


@pytest.mark.parametrize('sort_by,order', [
    ('createdTime', 'ascending'),
    ('createdTime', 'descending'),
])
def test_list_predictions(client: Client, sort_by, order):
    response = client.list_predictions(sort_by=sort_by, order=order)
    logging.info(response)
    assert 'predictions' in response, 'Missing predictions in response'
