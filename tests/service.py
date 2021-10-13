from pathlib import Path
from uuid import uuid4


def create_app_client_id():
    return f'las:app-client:{uuid4().hex}'


def create_asset_id():
    return f'las:asset:{uuid4().hex}'


def create_dataset_id():
    return f'las:dataset:{uuid4().hex}'


def create_consent_id():
    return f'las:consent:{uuid4().hex}'


def create_document_id():
    return f'las:document:{uuid4().hex}'


def create_log_id():
    return f'las:log:{uuid4().hex}'


def create_model_id():
    return f'las:model:{uuid4().hex}'


def create_data_bundle_id():
    return f'las:model-data-bundle:{uuid4().hex}'


def create_secret_id():
    return f'las:secret:{uuid4().hex}'


def create_transition_id():
    return f'las:transition:{uuid4().hex}'


def create_transition_execution_id():
    return f'las:transition-execution:{uuid4().hex}'


def create_user_id():
    return f'las:user:{uuid4().hex}'


def create_workflow_id():
    return f'las:workflow:{uuid4().hex}'


def create_workflow_execution_id():
    return f'las:workflow-execution:{uuid4().hex}'


def create_error_config():
    return {'email': 'foo@bar.com'}


def create_completed_config():
    return {
        'imageUrl': 'my/docker:image',
        'secretId': create_secret_id(),
        'environment': {'FOO': 'BAR'},
        'environmentSecrets': [create_secret_id()],
    }


def field_config():
    return {
        "total": {
            "description": "the total amount of the receipt",
            "type": "amount",
            "maxLength": 10,
        },
        "due_date": {
            "description": "the due date of the invoice",
            "type": "date",
            "maxLength": 10,
        },
    }


def preprocess_config():
    return {
        "imageQuality": "HIGH",
        "autoRotate": False,
        "maxPages": 3,
    }


def document_path():
    return Path(__file__)
