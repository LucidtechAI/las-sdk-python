# Python SDK for Lucidtech AI Services API

![Github Actions build status](https://github.com/LucidtechAI/las-sdk-python/workflows/main/badge.svg)

## Documentation

[Link to docs](https://docs.cradl.ai/python-docs/index.html)

## Installation

```bash
$ pip install lucidtech-las
```

## Usage

### Quick start

```python
import json
from las import Client

client = Client()
models = client.list_models()['models'] # List all models available
model_id = models[0]['modelId'] # Get ID of first model in list
document = client.create_document('path/to/document.pdf')
prediction = client.create_prediction(document['documentId'], model_id=model_id)
print(json.dumps(prediction, indent=2))
```

## Contributing

### Prerequisites

```bash
$ pip install -r requirements.txt
$ pip install -r requirements.ci.txt
```

### Run tests

```bash
$ make prism-start
$ python -m pytest
```

### Create docs

```bash
$ tox -e docs .docsout
```
