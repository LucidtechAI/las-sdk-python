import pytest
import configparser

from las import Client, Api
from functools import partial
from os.path import expanduser


def pytest_addoption(parser):
    parser.addoption('--cfg', action='store')


@pytest.fixture(scope='module')
def cfg(request):
    return expanduser(request.config.getoption('--cfg'))


@pytest.fixture(scope='module')
def params(cfg):
    config = configparser.ConfigParser()
    config.read(cfg)
    return partial(config.get, 'default')


def split_and_strip(s, delimiter=','):
    return [i.strip() for i in s.split(delimiter)]


@pytest.fixture(scope='module')
def model_names(params):
    return split_and_strip(params('model_names'))


@pytest.fixture(scope='module')
def document_paths(params):
    return split_and_strip(params('document_paths'))


@pytest.fixture(scope='module')
def document_mime_types(params):
    return split_and_strip(params('document_mime_types'))


@pytest.fixture(scope='module')
def endpoint(params):
    return params('endpoint')


@pytest.fixture(scope='module')
def client(endpoint):
    return Client(endpoint)


@pytest.fixture(scope='module')
def api(endpoint):
    return Api(endpoint)
