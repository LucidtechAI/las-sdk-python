import requests
import imghdr

from urllib.parse import urlencode, quote_plus


class Client:
    def __init__(self, api_key, base_endpoint='https://api.lucidtech.ai', stage='v0'):
        self.api_key = api_key
        self.base_endpoint = base_endpoint
        self.stage = stage

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

    def _scan_receipt_with_url(self, receipt_url):
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        params = {'url': receipt_url}
        querystring = urlencode(params, quote_via=quote_plus)
        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts?' + querystring])
        return requests.post(endpoint, data=None, headers=headers).json()

    def _scan_receipt_with_fp(self, receipt_fp):
        supported_formats = {'jpeg', 'png', 'bmp', 'gif'}
        fmt = imghdr.what(receipt_fp)

        if fmt in supported_formats:
            mime_type = 'image/{}'.format(fmt)

            headers = {
                'x-api-key': self.api_key,
                'Content-Type': mime_type
            }

            endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts'])
            return requests.post(endpoint, data=receipt_fp, headers=headers).json()

    def scan_receipt(self, receipt_url=None, receipt_fp=None):
        if receipt_url:
            return self._scan_receipt_with_url(receipt_url)
        elif receipt_fp:
            return self._scan_receipt_with_fp(receipt_fp)
        else:
            raise Exception('receipt_url or receipt_fp must be provided')
