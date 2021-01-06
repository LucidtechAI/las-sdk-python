from pathlib import Path
from uuid import uuid4


def create_asset_id():
    return f'las:asset:{uuid4().hex}'


def create_batch_id():
    return f'las:batch:{uuid4().hex}'


def create_consent_id():
    return f'las:consent:{uuid4().hex}'


def create_document_id():
    return f'las:document:{uuid4().hex}'


def create_model_id():
    return f'las:model:{uuid4().hex}'


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


def document_path():
    return Path(__file__)
