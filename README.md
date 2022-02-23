# Python SDK for Lucidtech AI Services API

![Github Actions build status](https://github.com/LucidtechAI/las-sdk-python/workflows/main/badge.svg)

## Documentation

[Link to docs](https://docs.lucidtech.ai/reference/python)

## Installation

```bash
$ pip install lucidtech-las
```

## Usage

### Preconditions

- Documents must be in upright position
- Only one receipt or invoice per document is supported
- Supported file formats are: jpeg, pdf

### Quick start

```python
import json
from las import Client

client = Client()
document = client.create_document('path/to/document.pdf', 'application/pdf')
prediction = client.create_prediction(document['documentId'], model_id='las:model:<hex-uuid>')
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
