import string
from os import urandom
from random import choice, randint

import pytest
from las import Client
from requests_mock import Mocker


@pytest.fixture(scope='session', autouse=True)
def mock_access_token_endpoint():
    response = {
        'access_token': ''.join(choice(string.ascii_uppercase) for _ in range(randint(50, 50))),
        'expires_in': 123456789,
    }

    with Mocker(real_http=True) as m:
        m.post('/token', json=response)
        yield


@pytest.fixture(scope='module')
def client():
    client = Client()
    return client


@pytest.fixture
def mime_type():
    return 'image/jpeg'


@pytest.fixture(scope='function')
def content():
    """
    Yields a random JPEG bytestring with a length 2E4
    """
    yield b'\xFF\xD8\xFF\xEE' + urandom(int(2E4))
