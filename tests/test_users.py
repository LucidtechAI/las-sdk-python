import logging

import pytest

from las.client import BaseClient
from . import util


def test_create_user(client: BaseClient):
    email = 'foo@bar.com'
    response = client.create_user(email)
    logging.info(response)


def test_list_users(client: BaseClient):
    response = client.list_users()
    logging.info(response)
    assert 'users' in response, 'Missing users in response'


def test_get_user(client: BaseClient):
    user_id = util.user_id()
    response = client.get_user(user_id)
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'
    logging.info(response)


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_user(client: BaseClient):
    user_id = util.user_id()
    response = client.delete_user(user_id)
    logging.info(response)
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'
