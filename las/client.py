import requests
import imghdr

from urllib.parse import urlencode, quote_plus
from io import BytesIO


class Client:
    def __init__(self, api_key, base_endpoint='https://api.lucidtech.ai', stage='v0'):
        self.api_key = api_key
        self.base_endpoint = base_endpoint
        self.stage = stage

    def scan_receipt(self, receipt):
        receipt_id = self._upload_receipt(receipt)

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        params = {'receiptId': receipt_id}
        querystring = urlencode(params, quote_via=quote_plus)
        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts?' + querystring])
        return requests.post(endpoint, headers=headers).json()

    def match_receipts(self, transactions, receipts, matching_fields):
        body = {
            'receipts': {k: self._upload_receipt(r) for k, r in receipts.items()},
            'transactions': transactions,
            'matchingFields': matching_fields
        }

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts', 'match'])
        return requests.post(endpoint, json=body, headers=headers).json()

    def _upload_receipt(self, receipt):
        supported_formats = {'jpeg', 'png', 'bmp', 'gif'}
        fmt = imghdr.what(BytesIO(receipt.content))

        if fmt in supported_formats:
            headers = {
                'x-api-key': self.api_key
            }

            endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts/upload'])
            response = requests.get(endpoint, headers=headers).json()
            upload_url = response['uploadUrl']
            receipt_id = response['receiptId']
            response = requests.put(upload_url, data=receipt.content)
            if response.status_code == 200:
                return receipt_id
        else:
            raise Exception('File format {} not supported'.format(fmt))
