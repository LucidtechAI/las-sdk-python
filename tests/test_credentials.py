import json

import pytest
from las.credentials import read_token_from_cache, write_token_to_cache, Credentials, NULL_TOKEN, read_from_environ


@pytest.fixture(scope='function')
def cache_path(tmp_path):
    return tmp_path / 'token-cache.json'


def test_read_token_from_cache(cache_path, token):
    cache = {'default': token}
    cache_path.write_text(json.dumps(cache))
    cached_token = read_token_from_cache('default', cache_path)
    assert token['access_token'], token['expires_in'] == cached_token


def test_write_token_to_cache(cache_path, token):
    write_token_to_cache('default', (token['access_token'], token['expires_in']), cache_path)
    cache = json.loads(cache_path.read_text())
    assert token == cache['default']


def test_credentials_with_empty_cache(client):
    assert client.credentials._token == NULL_TOKEN
    assert client.credentials.use_cached_profile is None


def test_credentials_with_cache(cache_path, token):
    write_token_to_cache('default', (token['access_token'], token['expires_in']), cache_path)
    credentials = Credentials(*read_from_environ(), use_cached_profile='default', cache_path=cache_path)
    assert credentials._token == (token['access_token'], token['expires_in'])
    assert credentials.use_cached_profile == 'default'
