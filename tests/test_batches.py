import logging
import random

import pytest
from las.client import Client

from . import service, util


@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_create_batch(client: Client, name_and_description):
    response = client.create_batch(**name_and_description)
    assert_batch(response)


def test_list_batches(client: Client):
    response = client.list_batches()
    logging.info(response)
    assert 'batches' in response, 'Missing batches in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_batches_with_pagination(client: Client, max_results, next_token):
    response = client.list_batches(max_results=max_results, next_token=next_token)
    assert 'batches' in response, 'Missing batches in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_batch(client: Client):
    batch_id = service.create_batch_id()
    response = client.delete_batch(batch_id)
    assert_batch(response)


@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_update_batch(client: Client, name_and_description):
    response = client.update_batch(service.create_batch_id(), **name_and_description)
    assert_batch(response)


def assert_batch(response):
    assert 'batchId' in response, 'Missing batchId in response'
    assert 'name' in response, 'Missing name in response'
    assert 'description' in response, 'Missing description in response'

