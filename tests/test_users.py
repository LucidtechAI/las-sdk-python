from las.client import BaseClient
from . import util


def test_create_user(client: BaseClient):
    email = 'foo@bar.com'
    response = client.create_user(email)
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'


def test_list_users(client: BaseClient):
    response = client.list_users()
    assert 'users' in response, 'Missing users in response'


def test_get_user(client: BaseClient,):
    user_id = util.user_id()
    response = client.get_user(user_id)
    assert 'userId' in response, 'Missing userId in response'
    assert 'email' in response, 'Missing email in response'


def test_delete_user(client: BaseClient):
    user_id = util.user_id()
    response = client.delete_user(user_id)
    assert not response, 'Response should be empty'
