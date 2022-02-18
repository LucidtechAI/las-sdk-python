import logging
import random

import pytest
from las.client import Client

from . import service, util


@pytest.mark.parametrize('preprocess_config', [service.preprocess_config(), None])
@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_create_model(client: Client, preprocess_config, name_and_description):
    response = client.create_model(
        width=300,
        height=300,
        field_config=service.field_config(),
        preprocess_config=preprocess_config,
        **name_and_description,
    )
    logging.info(response)
    assert_model(response)


def test_list_models(client: Client):
    response = client.list_models()
    logging.info(response)
    assert 'models' in response, 'Missing models in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_models_with_pagination(client: Client, max_results, next_token):
    response = client.list_models(max_results=max_results, next_token=next_token)
    logging.info(response)
    assert 'models' in response, 'Missing models in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_get_model(client: Client):
    response = client.get_model(service.create_model_id())
    logging.info(response)
    assert_model(response)


@pytest.mark.parametrize('preprocess_config', [service.preprocess_config(), None])
@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_update_model(client: Client, preprocess_config, name_and_description):
    response = client.update_model(
        service.create_model_id(),
        width=300,
        height=300,
        field_config=service.field_config(),
        preprocess_config=preprocess_config,
        **name_and_description,
    )
    logging.info(response)
    assert_model(response)


def assert_model(response):
    assert 'height' in response, 'Missing height in response'
    assert 'width' in response, 'Missing width in response'
    assert 'name' in response, 'Missing name in response'
    assert 'modelId' in response, 'Missing modelId in response'
    assert 'status' in response, 'Missing status in response'
    assert 'preprocessConfig' in response, 'Missing preprocessConfig in response'
    assert 'fieldConfig' in response, 'Missing fieldConfig in response'
    assert 'description' in response, 'Missing description in response'


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_model(client: Client):
    model_id = service.create_model_id()
    response = client.delete_model(model_id)
    assert 'modelId' in response, 'Missing modelId in response'


