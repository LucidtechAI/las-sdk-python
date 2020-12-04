import pytest
from las.client import BaseClient
from . import util
import logging
import random


@pytest.mark.parametrize('transition_type,params', [
    ('docker', {'imageUrl': 'python3.8'}),
    ('manual', None),
    ('manual', {'assets': {'jsRemoteComponent': util.asset_id()}}),
])
def test_create_transition(client: BaseClient, transition_type, params):
    in_schema = util.json_schema()
    out_schema = util.json_schema()
    response = client.create_transition('name', transition_type, in_schema, out_schema, params=params)
    logging.info(response)
    assert_transition(response)


@pytest.mark.parametrize('transition_type', [['docker'], ['manual'], 'docker', 'manual', None])
def test_list_transitions(client: BaseClient, transition_type):
    response = client.list_transitions(transition_type=transition_type)
    logging.info(response)
    assert 'transitions' in response, 'Missing transitions in response'
    if transition_type:
        assert 'transitionType' in response, 'Missing transitionType in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_transitions_with_pagination(client: BaseClient, max_results, next_token):
    response = client.list_transitions(max_results=max_results, next_token=next_token)
    logging.info(response)
    assert 'transitions' in response, 'Missing transitions in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


@pytest.mark.parametrize('name,description,in_schema,out_schema', [
    ('foo', None, None, None),
    (None, 'foo', None, None),
    (None, None, {'foo': 'bar'}, None),
    (None, None, None, {'foo': 'bar'}),
    ('foo', 'bar', {'foo': 'bar'}, {'foo': 'bar'}),
])
def test_update_transition(client: BaseClient, name, description, in_schema, out_schema):
    in_schema = util.json_schema()
    out_schema = util.json_schema()
    response = client.update_transition(
        util.transition_id(),
        name=name,
        description=description,
        in_schema=in_schema,
        out_schema=out_schema,
    )
    logging.info(response)
    assert_transition(response)


def test_execute_transition(client: BaseClient):
    transition_id = util.transition_id()
    response = client.execute_transition(transition_id)
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'


@pytest.mark.parametrize('status,output,error', [
    ('succeeded', {'foo': 'bar'}, None),
    ('failed', None, {'message': 'foobar'}),
])
def test_update_transition_execution(client: BaseClient, status, output, error):
    transition_id = util.transition_id()
    execution_id = util.transition_execution_id()
    response = client.update_transition_execution(transition_id, execution_id, status, output=output, error=error)
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'


def assert_transition(response):
    assert 'name' in response, 'Missing name in response'
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'transitionType' in response, 'Missing transitionType in response'
