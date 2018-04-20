import requests
import imghdr
import logging

from backoff import on_exception, expo
from urllib.parse import urlencode, quote_plus
from io import BytesIO
from ._extrahdr import what
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from concurrent.futures import ThreadPoolExecutor
from functools import partial


logger = logging.getLogger('las')
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)


def _fatal_code(e):
    return 400 <= e.response.status_code < 500


def _json_decode(response):
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


class ClientException(Exception):
    """a ClientException is raised if the client refuses to
    send request due to incorrect usage or bad request data."""
    pass


class LimitExceededException(ClientException):
    """a LimitExceededException is raised if the number of
    transactions or receipts exceeds the limit"""
    pass


class FileFormatException(ClientException):
    """a FileFormatException is raised if the file format
    is not supported by the api."""
    pass


class InvalidAPIKeyException(ClientException):
    """an InvalidAPIKeyException is raised if api key is invalid."""
    pass


class _Response:
    def __init__(self, requests_response):
        self.requests_response = requests_response
        self.status_code = requests_response.status_code


class ScanResponse(_Response):
    """a ScanResponse object contains the result of a successful call
    to the scan api. Do not create this object on your own, the
    :py:class:`~las.client.Client` object will do that for you.

    :param requests.Response requests_response: A requests response object.
    :param detections: A list of detections done on the document.
    :type detections: list(dict)

    """
    def __init__(self, requests_response):
        super().__init__(requests_response)
        self.detections = _json_decode(requests_response)


class MatchResponse(_Response):
    """a MatchResponse object contains the result of a successful call
    to the matching api. Do not create this object on your own, the
    :py:class:`~las.client.Client` object will do that for you.

    :param requests.Response requests_response: A requests response object.
    :param matched_transactions: A dictionary of matched transaction ids to receipt ids.
    :type matched_transactions: dict(str, str)
    :param unmatched_transactions: A list of unmatched transaction ids.
    :type unmatched_transactions: list(str)

    """
    def __init__(self, requests_response):
        super().__init__(requests_response)
        decoded = _json_decode(requests_response)
        self.matched_transactions = decoded['matchedTransactions']
        self.unmatched_transactions = decoded['unmatchedTransactions']


class Client:
    """a Client object stores configuration state and allows you to invoke
    api methods from Lucidtech AI Services.

    :param str api_key: Your api key
    :param str base_endpoint: Domain endpoint of the api
    :param str stage: Version of the api

    """
    def __init__(self, api_key, base_endpoint='https://api.lucidtech.ai', stage='v0'):
        self.api_key = api_key
        self.base_endpoint = base_endpoint
        self.stage = stage

    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def scan_receipt(self, receipt):
        """Scan receipt.

        >>> from las import Client, Receipt
        >>> client = Client(api_key='<api key>')
        >>> receipt = Receipt(url='https://example.com/receipt.jpeg')
        >>> response = client.scan_receipt(receipt)

        :param Receipt receipt: The receipt to scan
        :return: The results of the scan
        :rtype: ScanResponse
        :raises FileFormatException: If the receipt file format is not supported by the api
        :raises InvalidAPIKeyException: If the api key is invalid

        """
        document_id = self._upload_document(receipt, 'EU')

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        params = {'documentId': document_id}
        querystring = urlencode(params, quote_via=quote_plus)
        endpoint = '/'.join([self.base_endpoint, self.stage, 'receipts?' + querystring])
        response = requests.post(endpoint, headers=headers)
        return ScanResponse(response)

    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def scan_invoice(self, invoice):
        """Scan invoice.

        >>> from las import Client, Invoice
        >>> client = Client(api_key='<api key>')
        >>> invoice = Invoice(url='https://example.com/invoice.jpeg')
        >>> response = client.scan_invoice(invoice)

        :param Invoice invoice: The invoice to scan
        :return: The results of the scan
        :rtype: ScanResponse
        :raises FileFormatException: If the receipt file format is not supported by the api
        :raises InvalidAPIKeyException: If the api key is invalid

        """
        document_id = self._upload_document(invoice, 'EU')

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        params = {'documentId': document_id}
        querystring = urlencode(params, quote_via=quote_plus)
        endpoint = '/'.join([self.base_endpoint, self.stage, 'invoices?' + querystring])
        response = requests.post(endpoint, headers=headers)
        return ScanResponse(response)

    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def match_receipts(self, transactions, receipts, matching_fields, matching_strategy=None, num_upload_threads=10):
        """Matches transactions and receipts

        >>> from las import Client, Receipt
        >>> client = Client(api_key='<api key>')
        >>> transactions = {'t1': {'total': '100.34', 'date': '2018-03-04'}}
        >>> receipts = {'r1': Receipt(url='https://example.com/receipt.jpeg')}
        >>> matching_fields = ['total', 'date']
        >>> matching_strategy = {'total': 'maximumDeviation': '2.00'}
        >>> response = client.match_receipts(transactions, receipts, matching_fields, matching_strategy)

        :param transactions: A dictionary of transaction ids to transaction data
        :type transactions: dict(str, dict)
        :param receipts: A dictionary of receipt ids to :py:class:`~las.receipt.Receipt` objects
        :type receipts: dict(str, Receipt)
        :param matching_fields: A list of all the fields to check for matching
        :type matching_fields: list(str)
        :param matching_strategy: A dictionary of fields to matching strategies for that field
        :type matching_strategy: dict(str, dict) or None
        :param num_upload_threads: A number specifying maximum allowed threads for uploading receipts
        :type num_upload_threads: int
        :return: The results of the matching
        :rtype: MatchResponse
        :raises FileFormatException: If the receipt file format is not supported by the api
        :raises InvalidAPIKeyException: If the api key is invalid
        :raises LimitExceededException: If number of transactions exceeds 100 or number of receipts exceeds 15
        :raises ClientException: If transactions or receipts is empty or None
        """
        if not transactions:
            raise ClientException('"transactions" cannot be empty or None')

        if not receipts:
            raise ClientException('"receipts" cannot be empty or None')

        if len(transactions) > 100:
            raise LimitExceededException('Exceeded maximum of 100 transactions per request')

        if len(receipts) > 15:
            raise LimitExceededException('Exceeded maximum of 15 receipts per request')

        matching_strategy = matching_strategy or {}
        max_workers = min(len(receipts), num_upload_threads)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            receipt_handles = {}
            upload_document = partial(self._upload_document, region='EU')
            for k, r in zip(receipts.keys(), executor.map(upload_document, receipts.values())):
                receipt_handles[k] = r

        body = {
            'receipts': receipt_handles,
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

    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def _upload_document(self, document, region):
        supported_formats = {
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'bmp': 'image/bmp',
            'gif': 'image/gif',
            'tiff': 'image/tiff',
            'pdf': 'application/pdf'
        }

        fp = BytesIO(document.content)
        fmt = imghdr.what(fp) or what(fp)

        if fmt in supported_formats:
            headers = {'x-api-key': self.api_key}
            endpoint = '/'.join([self.base_endpoint, self.stage, 'documents'])
            payload = {'documentType': supported_formats[fmt], 'region': region}
            response = requests.put(endpoint, headers=headers, json=payload)
            decoded = _json_decode(response)

            upload_url = decoded['uploadUrl']
            document_id = decoded['documentId']
            headers = {'Content-Type': supported_formats[fmt]}
            response = requests.put(upload_url, headers=headers, data=document.content)
            response.raise_for_status()

            return document_id
        elif fmt:
            raise FileFormatException('File format {} not supported'.format(fmt))
        else:
            raise FileFormatException('File format not recognized')
