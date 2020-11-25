import logging
import random

import pytest

from las.client import BaseClient
from . import util


@pytest.mark.parametrize('description,error_config', [
    (None, None),
    (None, {'email': 'foo@bar.com'}),
    ('foobar', None),
    ('foobar', {'email': 'foo@bar.com'}),
])
def test_create_workflow(client: BaseClient, description, error_config):
    specification = {'definition': {}}
    name = 'foobar'
    response = client.create_workflow(specification, name, description=description, error_config=error_config)
    logging.info(response)
    assert 'name' in response, 'Missing name in response'
    assert 'workflowId' in response, 'Missing workflowId in response'
    if description:
        assert 'description' in response, 'Missing description in response'


def test_list_workflows(client: BaseClient):
    response = client.list_workflows()
    assert 'workflows' in response, 'Missing workflows in response'
    for workflow in response['workflows']:
        assert 'name' in workflow, 'Missing name in response'
        assert 'workflowId' in workflow, 'Missing workflowId in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_workflows_with_pagination(client: BaseClient, max_results, next_token):
    response = client.list_workflows(max_results=max_results, next_token=next_token)
    assert 'workflows' in response, 'Missing workflows in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


@pytest.mark.parametrize('status', [
    ['succeeded'],
    ['failed'],
    'running',
    None,
])
def test_list_workflow_executions(client: BaseClient, status):
    workflow_id = util.workflow_id()
    response = client.list_workflow_executions(workflow_id, status=status)
    logging.info(response)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executions' in response, 'Missing executions in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_workflow_executions_with_pagination(client: BaseClient, max_results, next_token):
    workflow_id = util.workflow_id()
    response = client.list_workflow_executions(workflow_id=workflow_id, max_results=max_results, next_token=next_token)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executions' in response, 'Missing executions in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_execute_workflow(client: BaseClient):
    workflow_id = util.workflow_id()
    response = client.execute_workflow(workflow_id, content={})
    logging.info(response)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executionId' in response, 'Missing executionId in response'


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_workflow(client: BaseClient):
    workflow_id = util.workflow_id()
    response = client.delete_workflow(workflow_id)
    logging.info(response)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'name' in response, 'Missing name in response'
