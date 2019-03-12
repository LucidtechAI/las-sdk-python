# Python SDK for Lucidtech AI Services API

## Documentation

[Link to docs](https://docs.lucidtech.ai/python/index.html)

## Installation

```bash
$ pip install lucidtech-las
```

## Usage

### Preconditions

- Documents must be in upright position
- Only one receipt or invoice per document is supported
- Supported file formats are: jpeg, png, gif, bmp, pdf

### Quick start

```python
import json
from las import Api

api = Api('<api key>')
prediction = api.predict('document.pdf', model_name='invoice')
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