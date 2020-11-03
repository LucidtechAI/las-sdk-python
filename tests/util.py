from uuid import uuid4


def batch_id():
    return f'las:batch:{uuid4().hex}'


def consent_id():
    return f'las:consent:{uuid4().hex}'


def model_id():
    return f'las:model:{uuid4().hex}'


def document_id():
    return f'las:document:{uuid4().hex}'
