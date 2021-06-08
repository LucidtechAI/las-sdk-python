import logging

import pytest
from las.client import Client

from . import util


def test_get_organization(client: Client):
    response = client.get_organization('me')
    logging.info(response)
    assert_organization(response)


@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_update_organization(client: Client, name_and_description):
    response = client.update_organization(
        'me',
        **name_and_description,
    )
    logging.info(response)
    assert_organization(response)


def assert_organization(response):
    assert 'organizationId' in response, 'Missing organizationId in response'
    assert 'name' in response, 'Missing name in response'
    assert 'description' in response, 'Missing description in response'
    assert 'organization_id' in response, 'Missing organization_id in response'
    assert 'description' in response, 'Missing description in response'
    assert 'name' in response, 'Missing name in response'
    assert 'number_of_app_clients_allowed' in response, 'Missing number_of_app_clients_allowed in response'
    assert 'number_of_app_clients_created' in response, 'Missing number_of_app_clients_created in response'
    assert 'number_of_assets_allowed' in response, 'Missing number_of_assets_allowed in response'
    assert 'number_of_assets_created' in response, 'Missing number_of_assets_created in response'
    assert 'number_of_batches_allowed' in response, 'Missing number_of_batches_allowed in response'
    assert 'number_of_batches_created' in response, 'Missing number_of_batches_created in response'
    assert 'number_of_models_allowed' in response, 'Missing number_of_models_allowed in response'
    assert 'number_of_models_created' in response, 'Missing number_of_models_created in response'
    assert 'number_of_secrets_allowed' in response, 'Missing number_of_secrets_allowed in response'
    assert 'number_of_secrets_created' in response, 'Missing number_of_secrets_created in response'
    assert 'number_of_transitions_allowed' in response, 'Missing number_of_transitions_allowed in response'
    assert 'number_of_transitions_created' in response, 'Missing number_of_transitions_created in response'
    assert 'number_of_users_allowed' in response, 'Missing number_of_users_allowed in response'
    assert 'number_of_users_created' in response, 'Missing number_of_users_created in response'
    assert 'number_of_workflows_allowed' in response, 'Missing number_of_workflows_allowed in response'
    assert 'number_of_workflows_created' in response, 'Missing number_of_workflows_created in response'
    assert 'monthly_number_of_documents_allowed' in response, 'Missing monthly_number_of_documents_allowed in response'
    assert 'monthly_number_of_documents_created' in response, 'Missing monthly_number_of_documents_created in response'
    assert 'monthly_number_of_predictions_allowed' in response, 'Missing monthly_number_of_predictions_allowed in response'
    assert 'monthly_number_of_predictions_created' in response, 'Missing monthly_number_of_predictions_created in response'
    assert 'monthly_number_of_transition_executions_allowed' in response, 'Missing monthly_number_of_transition_executions_allowed in response'
    assert 'monthly_number_of_transition_executions_created' in response, 'Missing monthly_number_of_transition_executions_created in response'
    assert 'monthly_number_of_workflow_executions_allowed' in response, 'Missing monthly_number_of_workflow_executions_allowed in response'
    assert 'monthly_number_of_workflow_executions_created' in response, 'Missing monthly_number_of_workflow_executions_created in response'
    assert 'monthly_usage_summary' in response, 'Missing monthly_usage_summary in response'

