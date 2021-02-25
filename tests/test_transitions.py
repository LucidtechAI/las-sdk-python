import logging
import random
from datetime import datetime

import pytest
from las.client import Client

from . import service, util


@pytest.mark.parametrize('transition_type,parameters', [
    ('docker', {'imageUrl': 'python3.8'}),
    ('manual', None),
    ('manual', {'assets': {'jsRemoteComponent': service.create_asset_id()}}),
])
@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_create_transition(client: Client, transition_type, parameters, name_and_description):
    schema = util.create_json_schema()
    response = client.create_transition(
        transition_type,
        in_schema=schema,
        out_schema=schema,
        parameters=parameters,
        **name_and_description,
    )
    logging.info(response)
    assert_transition(response)


def test_get_transition(client: Client):
    response = client.get_transition(service.create_transition_id())
    logging.info(response)
    assert_transition(response)


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_transition(client: Client):
    response = client.delete_transition(service.create_transition_id())
    logging.info(response)
    assert_transition(response)


@pytest.mark.parametrize('transition_type', [['docker'], ['manual'], 'docker', 'manual', None])
def test_list_transitions(client: Client, transition_type):
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
def test_list_transitions_with_pagination(client: Client, max_results, next_token):
    response = client.list_transitions(max_results=max_results, next_token=next_token)
    logging.info(response)
    assert 'transitions' in response, 'Missing transitions in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_get_transition_execution(client: Client):
    response = client.get_transition_execution(
        service.create_transition_id(),
        service.create_transition_execution_id(),
    )
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'


@pytest.mark.parametrize('in_schema,out_schema', [
    (None, None),
    ({'foo': 'bar'}, None),
    (None, {'foo': 'bar'}),
    ({'foo': 'bar'}, {'foo': 'bar'}),
])
@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations(True))
def test_update_transition(client: Client, name_and_description, in_schema, out_schema):
    response = client.update_transition(
        service.create_transition_id(),
        in_schema=in_schema,
        out_schema=out_schema,
        **name_and_description,
    )
    logging.info(response)
    assert_transition(response)


def test_execute_transition(client: Client):
    response = client.execute_transition(service.create_transition_id())
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'


@pytest.mark.parametrize('status,output,error', [
    ('succeeded', {'foo': 'bar'}, None),
    ('failed', None, {'message': 'foobar'}),
])
@pytest.mark.parametrize('start_time', [f'{datetime.utcnow()}', datetime.utcnow(), None])
def test_update_transition_execution(client: Client, status, output, error, start_time):
    transition_id = service.create_transition_id()
    execution_id = service.create_transition_execution_id()
    response = client.update_transition_execution(
        transition_id,
        execution_id,
        status,
        output=output,
        error=error,
        start_time=start_time,
    )
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'


def test_send_heartbeat(client: Client):
    transition_id = service.create_transition_id()
    execution_id = service.create_transition_execution_id()
    response = client.send_heartbeat(transition_id, execution_id)
    logging.info(response)
    assert response == {'Your requested executed successfully': '204'}


def assert_transition(response):
    assert 'name' in response, 'Missing name in response'
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'transitionType' in response, 'Missing transitionType in response'
