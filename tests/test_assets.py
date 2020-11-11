import logging
import random
from pathlib import Path

import pytest

from las.client import BaseClient
from . import util


def test_create_asset(client: BaseClient):
    content = Path('tests/remote_component.js').read_bytes()
    response = client.create_asset(content)
    assert 'assetId' in response, 'Missing assetId in response'


def test_list_assets(client: BaseClient):
    response = client.list_assets()
    logging.info(response)
    assert 'assets' in response, 'Missing assets in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_assets_with_pagination(client: BaseClient, max_results, next_token):
    response = client.list_assets(max_results=max_results, next_token=next_token)
    assert 'assets' in response, 'Missing assets in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_get_asset(client: BaseClient):
    asset_id = util.asset_id()
    response = client.get_asset(asset_id)
    assert 'assetId' in response, 'Missing assetId in response'
    assert 'content' in response, 'Missing content in response'

