import requests
import json
import pathlib
import logging

from base64 import b64encode
from backoff import on_exception, expo
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from urllib.parse import urlparse
from typing import List, Dict, Optional, Callable

from .credentials import Credentials


logger = logging.getLogger('las')


def dictstrip(d):
    """Given a dict, return the dict with keys mapping to falsey values removed."""
    return {k: v for k, v in d.items() if v}


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
            raise InvalidCredentialsException('Credentials provided is not valid.')

        if response.status_code == 429 and 'Too Many Requests' in response.json().values():
            raise TooManyRequestsException('You have reached the limit of requests per second.')

        if response.status_code == 429 and 'Limit Exceeded' in response.json().values():
            raise LimitExceededException('You have reached the limit of total requests per month.')

        raise e


class ClientException(Exception):
    """A ClientException is raised if the client refuses to
    send request due to incorrect usage or bad request data."""
    pass


class InvalidCredentialsException(ClientException):
    """An InvalidCredentialsException is raised if api key, access key id or secret access key is invalid."""
    pass


class TooManyRequestsException(ClientException):
    """A TooManyRequestsException is raised if you have reached the number of requests per second limit
    associated with your credentials."""
    pass


class LimitExceededException(ClientException):
    """A LimitExceededException is raised if you have reached the limit of total requests per month
    associated with your credentials."""
    pass


class Client:
    """A low level client to invoke api methods from Lucidtech AI Services."""
    def __init__(self, credentials=None):
        """:param endpoint: Domain endpoint of the api, e.g. https://<prefix>.api.lucidtech.ai/<version>
        :type endpoint: str
        :param credentials: Credentials to use, instance of :py:class:`~las.Credentials`
        :type credentials: Credentials"""
        self.credentials = credentials or Credentials()
        self.endpoint = self.credentials.api_endpoint

    def _create_signing_headers(self, path:  str):
        uri = urlparse(f'{self.endpoint}{path}')

        auth_headers = {
            'Authorization': f'Bearer {self.credentials.access_token}',
            'X-Api-Key': self.credentials.api_key
        }
        headers = {**auth_headers, 'Content-Type': 'application/json'}
        return uri, headers

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def _make_request(self, requests_fn: Callable, signing_path: str,
                      body: Optional[dict] = None, params: Optional[dict] = None,
                      encode_body: bool = True) -> dict:
        """Make signed headers, use them to make a HTTP request of arbitrary form and return the result
        as decoded JSON. Optionally pass a payload to JSON-dump and parameters for the request call."""

        kwargs = {'params': params}

        if body is not None:
            data = json.dumps(body)
            if encode_body:  # TODO: read requests-doc to find out whether this is needed
                data = data.encode()
            kwargs['data'] = data

        uri, headers = self._create_signing_headers(signing_path)
        response = requests_fn(
            url=uri.geturl(),
            headers=headers,
            **kwargs
        )

        return _json_decode(response)

    def patch_task_id(self, task_id: str, task_result: dict) -> dict:
        """Add a result to task, calls the PATCH /tasks/{task_id} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Document handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        return self._make_request(requests.patch, f'/tasks/{task_id}', body={'taskResult': task_result})

    def post_tasks(self, activity_arn: str) -> dict:
        """Calls the POST /tasks endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Document handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.post, '/tasks', body={'activityArn': activity_arn})

    def get_data(self, category=None) -> dict:
        """Get data, calls the GET /data endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_processes()

        :return: Processes
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.get, '/data', params={'category': category})

    def get_processes(self, max_results=None, status=None, next_token=None) -> dict:
        """Get processes, calls the GET /processes endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_processes()

        :return: Processes
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        params = {
            'maxResults': max_results,
            'status': status,
            'nextToken': next_token
        }
        return self._make_request(requests.get, '/processes', params=dictstrip(params))

    def post_processes(self, state_machine_arn: str, input_data: dict) -> dict:
        """Creates a new process, calls the POST /processes endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_processes('<state machine arn>', input_data={})

        :param state_machine_arn: State machine arn
        :type state_machine_arn: str
        :param input_data: Input to process
        :type input_data: dict
        :return: Process data
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(
            requests.post, '/processes', body={
                'stateMachineArn': state_machine_arn,
                'inputData': input_data
            }
        )

    def post_documents(self, content: bytes, content_type: str, consent_id: str,
                       batch_id: str = None, feedback: List[Dict[str, str]] = None) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content: The contents to POST
        :type content: bytes
        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :param batch_id: The batch to put the document in
        :type batch_id: str
        :param feedback: A list of feedback items {label: value} representing the ground truth values for the document
        :type feedback: List[Dict[str, str]]
        :return: Document handle id
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = {
            'content': b64encode(content).decode(),
            'contentType': content_type,
            'consentId': consent_id,
            'batchId': batch_id,
            'feedback': feedback
        }
        return self._make_request(requests.post, '/documents', body=dictstrip(body), encode_body=False)

    def get_documents(self, batch_id: Optional[str] = None, consent_id: Optional[str] = None) -> dict:
        """Get document from the REST API, calls the GET /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_documents(batch_id='<batch id>')

        :param batch_id: The batch id that contains the documents of interest
        :type batch_id: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Documents from REST API contained in batch <batch id>
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        return self._make_request(requests.get, '/documents', params={'batchId': batch_id, 'consentId': consent_id})

    def post_predictions(self, document_id: str, model_name: str,
                         max_pages: Optional[int], auto_rotate: Optional[bool]) -> dict:
        """Run inference and create a prediction, calls the POST /predictions endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_predictions(document_id='<document id>', model_name='invoice')

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :param model_name: The name of the model to use for inference
        :type model_name: str
        :param max_pages: Maximum number of pages to run predictions on
        :type model_name: int
        :param auto_rotate: Whether or not to let the API try different rotations on the document when running
        predictions
        :type model_name: bool
        :return: Prediction on document
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = {
            'documentId': document_id,
            'modelName': model_name,
            'maxPages': max_pages,
            'autoRotate': auto_rotate
        }
        return self._make_request(requests.post, '/predictions', body=dictstrip(body))

    def get_document_id(self, document_id: str) -> dict:
        """Get document from the REST API, calls the GET /documents/{documentId} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_document_id(document_id='<document id>')

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :return: Document response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.get, f'/documents/{document_id}')

    def post_document_id(self, document_id: str, feedback: List[Dict[str, str]]) -> dict:
        """Post feedback to the REST API, calls the POST /documents/{documentId} endpoint.
        Posting feedback means posting the ground truth data for the particular document.
        This enables the API to learn from past mistakes.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> feedback = [{'label': 'total_amount', 'value': '156.00'}, {'label': 'invoice_date', 'value': '2018-10-23'}]
        >>> client.post_document_id(document_id='<document id>', feedback=feedback)

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :param feedback: A list of feedback items {label: value} representing the ground truth values for the document
        :type feedback: List[Dict[str, str]]
        :return: Feedback response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        return self._make_request(requests.post, f'/documents/{document_id}', body={'feedback': feedback})

    def delete_consent_id(self, consent_id: str) -> dict:
        """Delete documents with this consent_id, calls the DELETE /consents/{consentId} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.delete_consent_id('<consent id>')

        :param consent_id: Delete documents with this consent_id
        :type consent_id: str
        :return: Delete consent id response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.delete, f'/consents/{consent_id}', body={})

    def put_data(self, data: dict) -> dict:
        """Put custom data to API.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.put_data({'foo': 'bar'})

        :param data: Dict to put
        :type data: dict
        :return: Put data response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.put, '/data', body=data)

    def post_batches(self, description: str) -> dict:
        """Creates a batch handle, calls the POST /batches endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_batches(description='Data from clients obtained during fall 2019')

        :param description: A short description of the batch you intend to create
        :type description: str
        :return: batch handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.post, '/batches', body={'description': description})

    def patch_user_id(self, user_id: str, consent_hash: str) -> dict:
        """Modifies consent hash for a user, calls the PATCH /users/{user_id} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_batches(description='Data from clients obtained during fall 2019')

        :param user_id: The user_id to modify consent hash for
        :type user_id: str
        :param consent_hash: The consent_hash to set
        :type consent_hash: str
        :return: batch handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self._make_request(requests.patch, f'/users/{user_id}', body={'consentHash': consent_hash})

    def get_user_id(self, user_id: str) -> dict:
        """Gets consent hash and user_id for a given user_id, calls the GET /users/{user_id} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_batches(description='Data from clients obtained during fall 2019')

        :param user_id: The user_id to get consent hash for
        :type user_id: str
        :return: batch handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        return self._make_request(requests.get, f'/users/{user_id}')
