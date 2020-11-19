import logging
import random

import pytest

from las.client import BaseClient
from . import util


def test_create_secret(client: BaseClient):
    data = {'username': 'foo', 'password': 'bar'}
    response = client.create_secret(data)
    assert 'secretId' in response, 'Missing secretId in response'


def test_list_secrets(client: BaseClient):
    response = client.list_secrets()
    logging.info(response)
    assert 'secrets' in response, 'Missing secrets in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_secrets_with_pagination(client: BaseClient, max_results, next_token):
    response = client.list_secrets(max_results=max_results, next_token=next_token)
    assert 'secrets' in response, 'Missing secrets in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_update_secret(client: BaseClient):
    secret_id = util.secret_id()
    data = {'username': 'foo', 'password': 'bar'}
    response = client.update_secret(secret_id, data)
    assert 'secretId' in response, 'Missing secretId in response'

