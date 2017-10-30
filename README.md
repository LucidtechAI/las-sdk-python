# Python SDK for Lucidtech AI Services API

## Installation

```bash
$ pip install lucidtech-las
```

## Usage Match Receipts

```python
from las import Client

api_key = '...'
client = Client(api_key)

transactions = {
    'transaction_1': {'total': '100.00', 'date': '2017-08-21'},
    'transaction_2': {'total': '340.90', 'date': '2016-03-08'},
    'transaction_3': {'total': '90.37', 'date': '2017-02-17'}
}

receipts = {
    'receipt_1': 'https://example.com/receipt1.jpeg',
    'receipt_2': 'https://example.com/receipt2.jpeg',
    'receipt_3': 'https://example.com/receipt3.jpeg',
}

matching_fields = [
    'total',
    'date'
]

response = client.match_receipts(
    transactions=transactions,
    receipts=receipts,
    matching_fields=matching_fields
)

print(response['matchedTransactions'])

# {'transaction_1': 'receipt_2', 'transaction_3': 'receipt_1'}

print(response['notMatchedTransactions'])

# ['transaction_2']
```

## Usage Scan Receipt

```python
from las import Client

api_key = '...'
client = Client(api_key)

fields = client.scan_receipt(receipt_url='https://example.com/img.jpeg')
print(fields)

# [{'label': 'total', 'value': '157.00', 'confidence': '0.968395300'} ...]

with open('img.jpeg', 'rb') as fp:
    fields = client.scan_receipt(receipt_fp=fp)
    print(fields)

# [{'label': 'total', 'value': '157.00', 'confidence': '0.968395300'} ...]
```
