import configparser
import pathlib
import string
from functools import partial
from os.path import expanduser
from random import choice, randint
from uuid import uuid4

import pytest

from las import ApiClient, Client


def pytest_addoption(parser):
    parser.addoption('--cfg', action='store')


@pytest.fixture(scope='module')
def cfg(request):
    return expanduser(request.config.getoption('--cfg'))


@pytest.fixture(scope='module')
def config(cfg):
    config = configparser.ConfigParser()
    config.read(cfg)
    return config


@pytest.fixture(scope='module')
def params(config):
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
def client():
    return Client()


@pytest.fixture(scope='module')
def api_client():
    return ApiClient()


@pytest.fixture(scope='module')
def state_machine_arn(params):
    return params('state_machine_arn')


@pytest.fixture(scope='module')
def activity_arn(params):
    return params('activity_arn')


@pytest.fixture(scope='function', params=[('tests/example.jpeg', 'image/jpeg')])
def typed_content(request):
    document_path, mime_type = request.param
    content = pathlib.Path(document_path).read_bytes()
    return content, mime_type


@pytest.fixture
def mime_type():
    return 'image/jpeg'


@pytest.fixture(scope='function')
def document_and_consent_id(monkeypatch, mime_type, client: Client, content):
    monkeypatch.setattr(pathlib.Path, 'read_bytes', lambda _: content)

    consent_id = str(uuid4())
    post_documents_response = client.post_documents(content, mime_type, consent_id)
    yield post_documents_response['documentId'], consent_id


@pytest.fixture(scope='function')
def document_id(document_and_consent_id):
    yield document_and_consent_id[0]


@pytest.fixture(scope='function')
def consent_id(document_and_consent_id):
    yield document_and_consent_id[1]


@pytest.fixture(scope='function')
def content():
    """
    Yields a random bytestring with a length varying from 100 to 1000
    """
    yield ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(randint(100, 1000))).encode()
