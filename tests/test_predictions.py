import logging

import pytest
from las.client import Client

from . import service


@pytest.mark.parametrize('max_pages', [1, 2, 3, None])
@pytest.mark.parametrize('auto_rotate', [True, False, None])
@pytest.mark.parametrize('image_quality', ['LOW', 'HIGH', None])
def test_create_prediction(client: Client, max_pages, auto_rotate, image_quality):
    document_id = service.create_document_id()
    model_id = service.create_model_id()
    response = client.create_prediction(
        document_id,
        model_id,
        auto_rotate=auto_rotate,
        max_pages=max_pages,
        image_quality=image_quality,
    )
    assert 'predictionId' in response, 'Missing predictionId in response'


def test_list_predictions(client: Client):
    response = client.list_predictions()
    logging.info(response)
    assert 'predictions' in response, 'Missing predictions in response'
