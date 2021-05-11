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


@pytest.mark.parametrize('model_type', [['docker'], ['manual'], 'docker', 'manual', None])
def test_list_models(client: Client, model_type):
    response = client.list_models(model_type=model_type)
    logging.info(response)
    assert 'models' in response, 'Missing models in response'
    if model_type:
        assert 'modelType' in response, 'Missing modelType in response'


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


def assert_model(response):
    assert 'name' in response, 'Missing name in response'
    assert 'modelId' in response, 'Missing modelId in response'
    assert 'modelType' in response, 'Missing modelType in response'
