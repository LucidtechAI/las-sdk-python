# Python SDK for Lucidtech AI Services API

![Github Actions build status](https://github.com/LucidtechAI/las-sdk-python/workflows/main/badge.svg)

## Documentation

[Link to docs](https://docs.lucidtech.ai/python/v1/index.html)

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
from las import ApiClient

api_client = ApiClient('<api endpoint>')
prediction = api_client.predict('document.pdf', model_name='invoice')
print(json.dumps(prediction, indent=2))
```

## Contributing

### Prerequisites

```bash
$ pip install tox
```

### Run tests

```bash
$ tox tests/test_config.cfg
```

### Create docs

```bash
$ tox -e docs .docsout
```
