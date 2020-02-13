import json
import logging
import pathlib
from base64 import b64encode
from json.decoder import JSONDecodeError
from typing import Any, Callable, Dict, List, Optional, Sequence
from urllib.parse import urlparse

import filetype
import requests
from backoff import expo, on_exception  # type: ignore
from requests.exceptions import RequestException

from .credentials import Credentials, guess_credentials
from .prediction import Field, Prediction

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
            raise InvalidCredentialsException('Credentials provided are not valid.')

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


class FileFormatException(ClientException):
    """A FileFormatException is raised if the file format is not supported by the api."""
    pass


class BaseClient:
    """A low level client to invoke api methods from Lucidtech AI Services."""
    def __init__(self, credentials: Optional[Credentials] = None):
        """:param credentials: Credentials to use, instance of :py:class:`~las.Credentials`
        :type credentials: Credentials"""
        self.credentials = credentials or guess_credentials()
        self.endpoint = self.credentials.api_endpoint

    def _create_signing_headers(self, path: str):
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

        kwargs: Dict[str, Any] = {'params': params}

        if body is not None:
            data = json.dumps(body)
            # TODO: read requests-doc to find out whether encoding is needed
            kwargs['data'] = data.encode() if encode_body else data

        uri, headers = self._create_signing_headers(signing_path)
        response = requests_fn(
            url=uri.geturl(),
            headers=headers,
            **kwargs
        )

        return _json_decode(response)

    def create_document(self, content: bytes, content_type: str, consent_id: str,
                        batch_id: str = None, feedback: Sequence[Dict[str, str]] = None) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.create_document(b'<bytes data>', 'image/jpeg', '<consent id>')

        :param content: The contents to POST
        :type content: bytes
        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :param batch_id: The batch to put the document in
        :type batch_id: str
        :param feedback: A list of feedback items {label: value} representing the ground truth values for the document
        :type feedback: Sequence[Dict[str, str]]
        :return: Document handle id
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        body = {
            'content': b64encode(content).decode(),
            'contentType': content_type,
            'consentId': consent_id,
            'batchId': batch_id,
            'feedback': feedback
        }
        return self._make_request(requests.post, '/documents', body=dictstrip(body), encode_body=False)

    def list_documents(self, batch_id: Optional[str] = None, consent_id: Optional[str] = None) -> dict:
        """List documents that you have created, calls the GET /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.list_documents()

        :param batch_id: The batch id that contains the documents of interest
        :type batch_id: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Documents from REST API contained in batch <batch id>
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        return self._make_request(requests.get, '/documents', params={'batchId': batch_id, 'consentId': consent_id})

    def create_prediction(self, document_id: str, model_name: str, max_pages: Optional[int] = None,
                          auto_rotate: Optional[bool] = None, extras: Dict[str, Any] = None) -> dict:
        """Create a prediction on a document using specified model, calls the POST /predictions endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.create_prediction(document_id='<document id>', model_name='invoice')

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :param model_name: The name of the model to use for inference
        :type model_name: str
        :param max_pages: Maximum number of pages to run predictions on
        :type max_pages: int
        :param auto_rotate: Whether or not to let the API try different rotations on\
 the document when running predictions
        :type auto_rotate: bool
        :param extras: Extra information to add to json body
        :type extras: Dict[str, Any]

        :return: Prediction on document
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        body = {
            'documentId': document_id,
            'modelName': model_name,
            'maxPages': max_pages,
            'autoRotate': auto_rotate,
            **(extras or {})
        }
        return self._make_request(requests.post, '/predictions', body=dictstrip(body))

    def get_document(self, document_id: str) -> dict:
        """Get document from the REST API, calls the GET /documents/{documentId} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_document(document_id='<document id>')

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :return: Document response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.get, f'/documents/{document_id}')

    def update_document(self, document_id: str, feedback: Sequence[Dict[str, str]]) -> dict:
        """Post feedback to the REST API, calls the POST /documents/{documentId} endpoint.
        Posting feedback means posting the ground truth data for the particular document.
        This enables the API to learn from past mistakes.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> feedback = [{'label': 'total_amount', 'value': '156.00'}, {'label': 'invoice_date', 'value': '2018-10-23'}]
        >>> client.update_document(document_id='<document id>', feedback=feedback)

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :param feedback: A list of feedback items {label: value} representing the ground truth values for the document
        :type feedback: Sequence[Dict[str, str]]
        :return: Feedback response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        return self._make_request(requests.post, f'/documents/{document_id}', body={'feedback': feedback})

    def delete_consent(self, consent_id: str) -> dict:
        """Delete documents with this consent_id, calls the DELETE /consents/{consentId} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.delete_consent('<consent id>')

        :param consent_id: Delete documents with this consent_id
        :type consent_id: str
        :return: Delete consent id response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.delete, f'/consents/{consent_id}', body={})

    def create_batch(self, description: str) -> dict:
        """Creates a batch handle, calls the POST /batches endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.create_batch(description='Data from clients obtained during fall 2019')

        :param description: A short description of the batch you intend to create
        :type description: str
        :return: batch handle id and pre-signed upload url
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,
        :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.post, '/batches', body={'description': description})

    def update_user(self, user_id: str, consent_hash: str) -> dict:
        """Modifies consent hash for user, calls the PATCH /users/{user_id} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.update_user('me', '<consent hash>')

        :param user_id: The user_id to modify consent hash for
        :type user_id: str
        :param consent_hash: The consent_hash to set
        :type consent_hash: str
        :return: batch handle id and pre-signed upload url
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.patch, f'/users/{user_id}', body={'consentHash': consent_hash})

    def get_user(self, user_id: str) -> dict:
        """Get information about user, calls the GET /users/{user_id} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_user('me')

        :param user_id: The user_id to get consent hash for
        :type user_id: str
        :return: batch handle id and pre-signed upload url
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        return self._make_request(requests.get, f'/users/{user_id}')


class Client(BaseClient):
    """A high level client to invoke api methods from Lucidtech AI Services."""
    DEFAULT_CONSENT_ID = 'default'
    DEFAULT_BATCH_ID = 'default'

    def predict(self, document_path: str, model_name: str, consent_id: str = DEFAULT_CONSENT_ID,
                extras: Dict[str, Any] = None) -> Prediction:
        """Create a prediction on a document specified by path using specified model.
        This method takes care of creating and uploading a document specified by document_path.
        as well as running inference using model specified by model_name to create prediction on the document.

        >>> from las import Client
        >>> client = Client()
        >>> client.predict(document_path='document.jpeg', model_name='invoice')

        :param document_path: Path to document to run inference on
        :type document_path: str
        :param model_name: The name of the model to use for inference
        :type model_name: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :param extras: Extra information to add to json body
        :type extras: Dict[str, Any]

        :return: Prediction on document
        :rtype: Prediction
        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        content_type = self._get_content_type(document_path)
        document = pathlib.Path(document_path).read_bytes()
        response = self.create_document(document, content_type, consent_id)
        document_id = response['documentId']
        prediction_response = self.create_prediction(document_id, model_name)
        return Prediction(document_id, consent_id, model_name, prediction_response)

    def send_feedback(self, document_id: str, feedback: List[Field]) -> dict:
        """Send feedback to the model.
        This method takes care of sending feedback related to document specified by document_id.
        Feedback consists of ground truth values for the document specified as a list of\
 :py:class:`~las.Field` instances.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> feedback = [Field(label='total_amount', value='120.00'), Field(label='purchase_date', value='2019-03-10')]
        >>> client.send_feedback('<document id>', feedback)

        :param document_id: The document id of the document that will receive the feedback
        :type document_id: str
        :param feedback: A list of :py:class:`~las.Field` representing the ground truth values for the document
        :type feedback: List[Field]

        :return: Feedback response
        :rtype: dict
        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """

        return self.update_document(document_id, feedback)

    def revoke_consent(self, consent_id: str) -> dict:
        """Revoke consent and deleting all documents associated with consent_id.
        Consent id is a parameter that is provided by the user upon making a prediction on a document.
        See :py:meth:`~las.ApiClient.predict`.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.revoke_consent('<consent id>')

        :param consent_id: Delete documents associated with this consent_id
        :type consent_id: str

        :return: Revoke consent response
        :rtype: dict
        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self.delete_consent(consent_id)

    @staticmethod
    def _get_content_type(document_path: str) -> str:
        supported_formats = {
            'image/jpeg',
            'application/pdf'
        }

        content = pathlib.Path(document_path).read_bytes()
        guessed_type = filetype.guess(content)

        if guessed_type and guessed_type.mime in supported_formats:
            return guessed_type.mime
        else:
            raise FileFormatException
