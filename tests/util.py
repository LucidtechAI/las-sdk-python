from uuid import uuid4


def asset_id():
    return f'las:asset:{uuid4().hex}'


def batch_id():
    return f'las:batch:{uuid4().hex}'


def consent_id():
    return f'las:consent:{uuid4().hex}'


def document_id():
    return f'las:document:{uuid4().hex}'


def model_id():
    return f'las:model:{uuid4().hex}'


def secret_id():
    return f'las:secret:{uuid4().hex}'


def transition_id():
    return f'las:transition:{uuid4().hex}'


def transition_execution_id():
    return f'las:transition-execution:{uuid4().hex}'


def user_id():
    return f'las:user:{uuid4().hex}'


def workflow_id():
    return f'las:workflow:{uuid4().hex}'


def workflow_execution_id():
    return f'las:workflow-execution:{uuid4().hex}'


def json_schema():
    return {
        "$schema": "https://json-schema.org/draft-04/schema#",
        "title": "response"
    }
