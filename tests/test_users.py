import base64
import pathlib
import random

import pytest
from las.client import Client

from . import service


def test_create_user(client: Client):
    email = 'foo@bar.com'
    response = client.create_user(
        email, 
        app_client_id=service.create_app_client_id(),
        role_ids=[service.create_role_id()],
    )
    assert 'userId' in response, 'Missing userId in response'
    assert 'roleIds' in response, 'Missing roleIds in response'


def test_list_users(client: Client):
    response = client.list_users()
    assert 'users' in response, 'Missing users in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_users_with_pagination(client: Client, max_results, next_token):
    response = client.list_users(max_results=max_results, next_token=next_token)
    assert 'users' in response, 'Missing users in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_get_user(client: Client):
    user_id = service.create_user_id()
    response = client.get_user(user_id)
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'


def test_update_user(client: Client):
    user_id = service.create_user_id()
    name = 'John Doe'
    avatar = base64.b64encode(pathlib.Path('tests/avatar.jpeg').read_bytes()).decode()
    response = client.update_user(user_id, name=name, avatar=avatar, role_ids=[service.create_role_id()])
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'
    assert 'name' in response, 'Missing name in response'
    assert 'avatar' in response, 'Missing avatar in response'


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_user(client: Client):
    user_id = service.create_user_id()
    response = client.delete_user(user_id)
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'
