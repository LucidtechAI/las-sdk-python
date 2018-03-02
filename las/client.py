import requests
import imghdr
import logging

from backoff import on_exception, expo
from urllib.parse import urlencode, quote_plus
from io import BytesIO
from .extrahdr import what
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError


logger = logging.getLogger('las')
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)


def fatal_code(e):
    return 400 <= e.response.status_code < 500


def json_decode(response):
    try:
        response.raise_for_status()
        return response.json()
    except JSONDecodeError as e:
        logger.error('Error in response. Returned {}'.format(response.text))
        raise e
    except Exception as e:
        logger.error('Error in response. Returned {}'.format(response.text))

        if response.status_code == 403 and 'Forbidden' in response.json().values():
            raise InvalidAPIKeyException('API key provided is not valid')

        raise e


class LimitExceededException(Exception):
    pass


class FileFormatException(Exception):
    pass


class InvalidAPIKeyException(Exception):
    pass


class Response:
    def __init__(self, status_code):
        self.status_code = status_code


class ScanResponse(Response):
    def __init__(self, response):
        super().__init__(response.status_code)
        self.detections = json_decode(response)


class MatchResponse(Response):
    def __init__(self, response):
        super().__init__(response.status_code)
        decoded = json_decode(response)
        self.matched_transactions = decoded['matchedTransactions']
        self.unmatched_transactions = decoded['unmatchedTransactions']


class Client:
    def __init__(self, api_key, base_endpoint='https://api.lucidtech.ai', stage='v0'):
        self.api_key = api_key
        self.base_endpoint = base_endpoint
        self.stage = stage

    @on_exception(expo, RequestException, max_tries=3, giveup=fatal_code)
    def scan_receipt(self, receipt):
        receipt_id = self._upload_receipt(receipt)

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        params = {'receiptId': receipt_id}
        querystring = urlencode(params, quote_via=quote_plus)
        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts?' + querystring])
        response = requests.post(endpoint, headers=headers)
        return ScanResponse(response)

    @on_exception(expo, RequestException, max_tries=3, giveup=fatal_code)
    def scan_invoice(self, invoice):
        receipt_id = self._upload_receipt(invoice)

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        params = {'receiptId': receipt_id}
        querystring = urlencode(params, quote_via=quote_plus)
        endpoint = '/'.join([self.base_endpoint, self.stage, 'invoices?' + querystring])
        response = requests.post(endpoint, headers=headers)
        return ScanResponse(response)

    @on_exception(expo, RequestException, max_tries=3, giveup=fatal_code)
    def match_receipts(self, transactions, receipts, matching_fields, matching_strategy=None):
        if len(transactions) > 100:
            raise LimitExceededException('Exceeded maximum of 100 transactions per request')

        if len(receipts) > 15:
            raise LimitExceededException('Exceeded maximum of 15 receipts per request')

        matching_strategy = matching_strategy or {}

        body = {
            'receipts': {k: self._upload_receipt(r) for k, r in receipts.items()},
            'transactions': transactions,
            'matchingFields': matching_fields,
            'matchingStrategy': matching_strategy
        }

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts', 'match'])
        response = requests.post(endpoint, json=body, headers=headers)
        return MatchResponse(response)

    @on_exception(expo, RequestException, max_tries=3, giveup=fatal_code)
    def _upload_receipt(self, receipt):
        supported_formats = {'jpeg', 'png', 'bmp', 'gif', 'pdf'}
        fp = BytesIO(receipt.content)
        fmt = imghdr.what(fp) or what(fp)

        if fmt in supported_formats:
            headers = {
                'x-api-key': self.api_key
            }

            endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts/upload'])

            response = requests.get(endpoint, headers=headers)
            decoded = json_decode(response)

            upload_url = decoded['uploadUrl']
            receipt_id = decoded['receiptId']
            response = requests.put(upload_url, data=receipt.content)
            response.raise_for_status()
            return receipt_id
        elif fmt:
            raise FileFormatException('File format {} not supported'.format(fmt))
        else:
            raise FileFormatException('File format not recognized')
