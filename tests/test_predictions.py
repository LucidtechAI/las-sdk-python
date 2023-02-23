import logging

import pytest
from las.client import Client

from . import service


@pytest.mark.parametrize(('rotation', 'auto_rotate', 'max_pages', 'image_quality'), [
    (0, True, 1, 'LOW'),
    (90, False, 2, 'HIGH'),
    (180, None, 3, 'None'),
    (270, True, None, 'HIGH'),
    (None, False, 1, 'LOW', ),
])
@pytest.mark.parametrize('postprocess_config', [
    {'strategy': 'BEST_FIRST'},
    {'strategy': 'BEST_N_PAGES', 'parameters': {'n': 3}},
    {'strategy': 'BEST_N_PAGES', 'parameters': {'n': 3, 'collapse': False}},
    None,
])
def test_create_prediction(client: Client, rotation, max_pages, auto_rotate, image_quality, postprocess_config):
    document_id = service.create_document_id()
    model_id = service.create_model_id()
    response = client.create_prediction(
        document_id,
        model_id,
        auto_rotate=auto_rotate,
        image_quality=image_quality,
        max_pages=max_pages,
        postprocess_config=postprocess_config,
        rotation=rotation,
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
