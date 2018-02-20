# Python SDK for Lucidtech AI Services API

## Installation

```bash
$ pip install lucidtech-las
```

## Usage

Supported file formats are
- jpeg
- png
- gif
- bmp
- pdf

### Scan Receipt

```python
from las import Client, Receipt

api_key = '...'
client = Client(api_key)

# With URL
receipt = Receipt(url='https://example.com/img.jpeg')

# With file object
with open('img.jpeg', 'rb') as fp:
    receipt = Receipt(fp=fp)
    
# With filename
receipt = Receipt(filename='img.jpeg')

response = client.scan_receipt(receipt)
print(response.detections)

# [{'label': 'total', 'value': '157.00', 'confidence': '0.968395300'} ...]
```

### Scan Invoice

Beta: accurate results only provided for Norwegian invoices atm.

```python
from las import Client, Invoice

api_key = '...'
client = Client(api_key)

# With URL
invoice = Invoice(url='https://example.com/img.jpeg')

# With file object
with open('img.jpeg', 'rb') as fp:
    invoice = Invoice(fp=fp)
    
# With filename
invoice = Invoice(filename='img.jpeg')
    
response = client.scan_invoice(invoice)
print(response.detections)

# [{'label': 'total_amount', 'value': '256.00', 'confidence': '0.98485885'} ...]
```

### Match Receipts


## Current limitations
The number of receipts per request is limited to 15
The number of transactions per request is limited to 100

## Note on formats
The 'date' field expects ISO 8601 yyyy-mm-dd format


```python
from las import Client, Receipt

api_key = '...'
client = Client(api_key)

transactions = {
    'transaction_1': {'total': '100.00', 'date': '2017-08-21'}, 
    'transaction_2': {'total': '340.90', 'date': '2016-03-08'},
    'transaction_3': {'total': '90.37', 'date': '2017-02-17'}
}

receipts = {
    'receipt_1': Receipt(url='https://example.com/receipt1.jpeg'),
    'receipt_2': Receipt(url='https://example.com/receipt2.jpeg'),
    'receipt_3': Receipt(filename='receipt3.jpeg')
}

matching_fields = [
    'total',
    'date'
]

# Optionally specify a matching strategy for respective fields.

matching_strategy = {
    'total': {
        'maximumDeviation': 5.0 # Total amount might differ up to 5.0
    },
    'date': {
        'maximumDeviation': 2 # Date might differ up to 1 days
    }
}

response = client.match_receipts(
    transactions=transactions,
    receipts=receipts,
    matching_fields=matching_fields,
    matching_strategy=matching_strategy
)

print(response.matched_transactions)

# {'transaction_1': 'receipt_2', 'transaction_3': 'receipt_1'}

print(response.unmatched_transactions)

# ['transaction_2']
```


