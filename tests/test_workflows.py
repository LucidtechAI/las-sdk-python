import logging
import random

import pytest

from las.client import Client
from . import service


@pytest.mark.parametrize('description,error_config', [
    (None, None),
    (None, {'email': 'foo@bar.com'}),
    ('foobar', None),
    ('foobar', {'email': 'foo@bar.com'}),
])
def test_create_workflow(client: Client, description, error_config):
    specification = {'definition': {}}
    name = 'foobar'
    response = client.create_workflow(specification, name=name, description=description, error_config=error_config)
    logging.info(response)
    assert_workflow(response)
    if description:
        assert 'description' in response, 'Missing description in response'


def test_list_workflows(client: Client):
    response = client.list_workflows()
    assert 'workflows' in response, 'Missing workflows in response'
    for workflow in response['workflows']:
        assert_workflow(workflow)


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_workflows_with_pagination(client: Client, max_results, next_token):
    response = client.list_workflows(max_results=max_results, next_token=next_token)
    assert 'workflows' in response, 'Missing workflows in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


@pytest.mark.parametrize('name,description', [
    ('foo', None),
    (None, 'foo'),
    ('foo', 'bar'),
])
def test_update_workflow(client: Client, name, description):
    response = client.update_workflow(
        service.create_workflow_id(),
        name=name,
        description=description,
    )
    logging.info(response)
    assert_workflow(response)


@pytest.mark.parametrize('status', [
    ['succeeded'],
    ['failed'],
    'running',
    None,
])
def test_list_workflow_executions(client: Client, status):
    workflow_id = service.create_workflow_id()
    response = client.list_workflow_executions(workflow_id, status=status)
    logging.info(response)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executions' in response, 'Missing executions in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_workflow_executions_with_pagination(client: Client, max_results, next_token):
    workflow_id = service.create_workflow_id()
    response = client.list_workflow_executions(workflow_id=workflow_id, max_results=max_results, next_token=next_token)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executions' in response, 'Missing executions in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_execute_workflow(client: Client):
    workflow_id = service.create_workflow_id()
    response = client.execute_workflow(workflow_id, content={})
    logging.info(response)
    assert_workflow_execution(response)


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_workflow_execution(client: Client):
    workflow_id = service.create_workflow_id()
    execution_id = service.create_workflow_execution_id()
    response = client.stop_workflow_execution(workflow_id, execution_id)
    logging.info(response)
    assert_workflow_execution(response)


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_workflow(client: Client):
    workflow_id = service.create_workflow_id()
    response = client.delete_workflow(workflow_id)
    logging.info(response)
    assert_workflow(response)


def assert_workflow(response):
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'name' in response, 'Missing name in response'


def assert_workflow_execution(response):
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'startTime' in response, 'Missing startTime in response'
    assert 'endTime' in response, 'Missing endTime in response'
    assert 'transitionExecutions' in response, 'Missing transitionExecutions in response'
