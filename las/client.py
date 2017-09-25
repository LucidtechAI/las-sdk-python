import requests


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_endpoint = 'https://api.lucidtech.ai'
        self.stage = 'v0'

    def match_receipts(self, transactions, receipts, matching_fields):
        body = {
            'receipts': receipts,
            'transactions': transactions,
            'matchingFields': matching_fields
        }

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts', 'match'])
        return requests.post(endpoint, json=body, headers=headers).json()
