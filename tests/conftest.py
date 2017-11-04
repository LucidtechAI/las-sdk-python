import pytest
import configparser

from las import Client
from functools import partial


def pytest_addoption(parser):
    parser.addoption('--cfg', action='store')


@pytest.fixture(scope='module')
def cfg(request):
    return request.config.getoption('--cfg')


@pytest.fixture(scope='module')
def params(cfg):
    config = configparser.ConfigParser()
    config.read(cfg)
    return partial(config.get, 'match_receipts')


@pytest.fixture(scope='module')
def api_key(params):
    return params('api_key')


@pytest.fixture(scope='module')
def base_endpoint(params):
    return params('base_endpoint')


@pytest.fixture(scope='module')
def stage(params):
    return params('stage')


@pytest.fixture(scope='module')
def client(api_key, base_endpoint, stage):
    return Client(api_key, base_endpoint, stage)
