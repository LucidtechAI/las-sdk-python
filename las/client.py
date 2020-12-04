import json
import logging
import pathlib
from base64 import b64encode
from json.decoder import JSONDecodeError
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from urllib.parse import urlparse

import filetype
import requests
from backoff import expo, on_exception  # type: ignore
from requests.exceptions import RequestException

from .credentials import Credentials, guess_credentials
from .prediction import Field, Prediction

logger = logging.getLogger('las')
Queryparam = Union[str, List[str]]


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

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def _make_request(self, requests_fn: Callable, signing_path: str,
                      body: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        """Make signed headers, use them to make a HTTP request of arbitrary form and return the result
        as decoded JSON. Optionally pass a payload to JSON-dump and parameters for the request call."""

        kwargs = {'params': params}
        None if body is None else kwargs.update({'data': json.dumps(body)})
        uri = urlparse(f'{self.endpoint}{signing_path}')
        headers = {
            'Authorization': f'Bearer {self.credentials.access_token}',
            'X-Api-Key': self.credentials.api_key,
            'Content-Type': 'application/json',
        }
        response = requests_fn(
            url=uri.geturl(),
            headers=headers,
            **kwargs,
        )
        return _json_decode(response)

    def create_asset(self, content: bytes) -> dict:
        """Creates an asset handle, calls the POST /assets endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.create_asset(b'<bytes data>')

        :param content: Content to POST
        :type content: bytes
        :return: Asset response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {'content': b64encode(content).decode()}
        return self._make_request(requests.post, '/assets', body=body)

    def list_assets(self, max_results: Optional[int] = None, next_token: Optional[str] = None) -> dict:
        """List assets available, calls the GET /assets endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_assets()

        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Assets response from REST API without the content of each asset
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        params = {
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, '/assets', params=params)

    def get_asset(self, asset_id: str) -> dict:
        """Get asset from the REST API, calls the GET /assets/{assetId} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.get_asset(asset_id='<asset id>')

        :param asset_id: Id of the asset
        :type asset_id: str
        :return: Asset response from REST API with content
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.get, f'/assets/{asset_id}')

    def update_asset(self, asset_id: str, content: bytes) -> dict:
        """Updates an asset, calls the PATCH /assets/assetId endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.update_asset('<asset id>', b'<bytes data>')

        :param asset_id: Id of the asset
        :type asset_id: str
        :param content: Content to PATCH
        :type content: bytes
        :return: Asset response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {'content': b64encode(content).decode()}
        return self._make_request(requests.patch, f'/assets/{asset_id}', body=body)

    def create_batch(self, description: str) -> dict:
        """Creates a batch, calls the POST /batches endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.create_batch(description='<description>')

        :param description: Description of the batch
        :type description: str
        :return: Batch response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.post, '/batches', body={'description': description})

    def create_document(
            self,
            content: bytes,
            content_type: str,
            consent_id: Optional[str] = None,
            batch_id: str = None,
            ground_truth: Sequence[Dict[str, str]] = None,
    ) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.create_document(b'<bytes data>', 'image/jpeg', '<consent id>')

        :param content: Content to POST
        :type content: bytes
        :param content_type: MIME type for the document handle
        :type content_type: str
        :param consent_id: Id of the consent that marks the owner of the document handle
        :type consent_id: str
        :param batch_id: Id of the associated batch
        :type batch_id: str
        :param ground_truth: List of items {label: value} representing the ground truth values for the document
        :type ground_truth: Sequence[Dict[str, str]]
        :return: Document response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'content': b64encode(content).decode(),
            'contentType': content_type,
            'consentId': consent_id,
            'batchId': batch_id,
            'groundTruth': ground_truth,
        }
        return self._make_request(requests.post, '/documents', body=dictstrip(body))

    def list_documents(
        self,
        batch_id: Optional[Queryparam] = None,
        consent_id: Optional[Queryparam] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict:
        """List documents available for inference, calls the GET /documents endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_documents(batch_id='<batch_id>', consent_id='<consent_id>')

        :param batch_id: Ids of batches that contains the documents of interest
        :type batch_id: Queryparam
        :param consent_id: Ids of the consents that marks the owner of the document handle
        :type consent_id: Queryparam
        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Documents response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        params = {
            'batchId': batch_id,
            'consentId': consent_id,
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, '/documents', params=params)

    def delete_documents(self, consent_id: Optional[Queryparam] = None) -> dict:
        """Delete documents with the provided consent_id, calls the DELETE /documents endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.delete_documents('<consent id>')

        :param consent_id: Ids of the consents that marks the owner of the document handle
        :type consent_id: Queryparam
        :return: Documents response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.delete, '/documents', params={'consentId': consent_id})

    def get_document(self, document_id: str) -> dict:
        """Get document from the REST API, calls the GET /documents/{documentId} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.get_document(document_id='<document id>')

        :param document_id: Id of the document
        :type document_id: str
        :return: Document response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.get, f'/documents/{document_id}')

    def update_document(self, document_id: str, ground_truth: Sequence[Dict[str, Union[Optional[str], bool]]]) -> dict:
        """Post ground truth to the REST API, calls the PATCH /documents/{documentId} endpoint.
        Posting ground truth means posting the ground truth data for the particular document.
        This enables the API to learn from past mistakes.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> ground_truth = [{'label': 'total_amount', 'value': '156.00'}, {'label': 'date', 'value': '2018-10-23'}]
        >>> client.update_document(document_id='<document id>', ground_truth=ground_truth)

        :param document_id: Id of the document
        :type document_id: str
        :param ground_truth: List of items {label: value} representing the ground truth values for the document
        :type ground_truth: Sequence[Dict[str, Union[Optional[str], bool]]]
        :return: Document response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.patch, f'/documents/{document_id}', body={'groundTruth': ground_truth})

    def list_models(self, max_results: Optional[int] = None, next_token: Optional[str] = None) -> dict:
        """List models available, calls the GET /models endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_models()

        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Models response from REST API without the content of each model
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        params = {
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, '/models', params=params)

    def create_prediction(
        self,
        document_id: str,
        model_id: str,
        max_pages: Optional[int] = None,
        auto_rotate: Optional[bool] = None,
    ) -> dict:
        """Create a prediction on a document using specified model, calls the POST /predictions endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.create_prediction(document_id='<document id>', model_id='<model id>')

        :param document_id: Id of the document to run inference and create a prediction on
        :type document_id: str
        :param model_id: Id of the model to use for inference
        :type model_id: str
        :param max_pages: Maximum number of pages to run predictions on
        :type max_pages: int
        :param auto_rotate: Whether or not to let the API try different rotations on\
 the document when running predictions
        :type auto_rotate: bool
        :return: Prediction response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'documentId': document_id,
            'modelId': model_id,
            'maxPages': max_pages,
            'autoRotate': auto_rotate,
        }
        return self._make_request(requests.post, '/predictions', body=dictstrip(body))

    def create_secret(self, data: dict, description: Optional[str] = None) -> dict:
        """Creates an secret handle, calls the POST /secrets endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> data = {'username': '<username>', 'password': '<password>'}
        >>> client.create_secret(data, '<description>')

        :param data: Dict containing the data you want to keep secret
        :type data: str
        :param description: Description of the secret
        :type description: str
        :return: Secret response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'data': data,
            'description': description,
        }
        return self._make_request(requests.post, '/secrets', body=dictstrip(body))

    def list_secrets(self, max_results: Optional[int] = None, next_token: Optional[str] = None) -> dict:
        """List secrets available, calls the GET /secrets endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_secrets()

        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Secrets response from REST API without the username of each secret
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        params = {
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, '/secrets', params=params)

    def update_secret(self, secret_id: str, data: dict, description: Optional[str] = None) -> dict:
        """Updates an secret, calls the PATCH /secrets/secretId endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> data = {'username': '<username>', 'password': '<password>'}
        >>> client.update_secret('<secret id>', data, '<description>')

        :param secret_id: Id of the secret
        :type secret_id: str
        :param data: Dict containing the data you want to keep secret
        :type data: str
        :param description: Description of the secret
        :type description: Optional[str]
        :return: Secret response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'data': data,
            'description': description,
        }
        return self._make_request(requests.patch, f'/secrets/{secret_id}', body=dictstrip(body))

    def create_transition(
        self,
        name,
        transition_type: str,
        in_schema: dict,
        out_schema: dict,
        params: Optional[dict] = None,
        description: Optional[str] = None,
    ) -> dict:
        """Creates a transition handle, calls the POST /transitions endpoint.

        >>> import json
        >>> from pathlib import Path
        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> in_schema = {'$schema': 'https://json-schema.org/draft-04/schema#', 'title': 'in', 'properties': {...} }
        >>> out_schema = {'$schema': 'https://json-schema.org/draft-04/schema#', 'title': 'out', 'properties': {...} }
        >>> # A typical docker transitions
        >>> docker_params = {
        >>>     'imageUrl': '<image_url>',
        >>>     'credentials': {'username': '<username>', 'password': '<password>'}
        >>> }
        >>> client.create_transition('<name>', 'docker', in_schema, out_schema, docker_params)
        >>> # A typical manual transitions
        >>> assets = {'jsRemoteComponent': 'las:asset:<hex-uuid>', '<other asset name>': 'las:asset:<hex-uuid>'}
        >>> manual_params = {'assets': assets}
        >>> client.create_transition('<name>', 'manual', in_schema, out_schema, manual_params)

        :param in_schema: Json-schema that defines the input to the transition
        :type in_schema: dict
        :param out_schema: Json-schema that defines the output of the transition
        :type out_schema: dict
        :param name: Name of the transition
        :type name: str
        :param transition_type: Type of transition "docker"|"manual"
        :type transition_type: str
        :param params: Parameters to the corresponding transition type
        :type params: Optional[dict]
        :param description: Description of the transition
        :type description: Optional[str]
        :return: Transition response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'name': name,
            'description': description,
            'inputJsonSchema': in_schema,
            'outputJsonSchema': out_schema,
            'transitionType': transition_type,
            'params': params,
        }
        return self._make_request(requests.post, '/transitions', body=dictstrip(body))

    def list_transitions(
        self,
        transition_type: Optional[Queryparam] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict:
        """List transitions, calls the GET /transitions endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_transitions('<transition_type>')

        :param transition_type: Types of transitions
        :type transition_type: Queryparam
        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Transitions response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        url = '/transitions'
        params = {
            'transitionType': transition_type,
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, url, params=params)

    def update_transition(
        self,
        transition_id: str,
        *,
        name: Optional[str],
        in_schema: Optional[dict],
        out_schema: Optional[dict],
        description: Optional[str] = None,
    ) -> dict:
        """Creates a transition handle, calls the PATCH /transitions/{transitionId} endpoint.

        >>> import json
        >>> from pathlib import Path
        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.update_transition('<transition-id>', name='<name>', description='<description>')

        :param transition_id: Id of the transition
        :type name: str
        :param name: Name of the transition
        :type name: Optional[str]
        :param description: Description of the transition
        :type description: Optional[str]
        :param in_schema: Json-schema that defines the input to the transition
        :type in_schema: Optional[dict]
        :param out_schema: Json-schema that defines the output of the transition
        :type out_schema: Optional[dict]
        :return: Transition response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'name': name,
            'description': description,
            'inputJsonSchema': in_schema,
            'outputJsonSchema': out_schema,
        }
        return self._make_request(requests.patch, f'/transitions/{transition_id}', body=dictstrip(body))

    def execute_transition(self, transition_id: str) -> dict:
        """Start executing a manual transition, calls the POST /transitions/{transitionId}/executions endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.execute_transition('<transition_id>')

        :param transition_id: Id of the transition
        :type transition_id: str
        :return: Transition execution response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        endpoint = f'/transitions/{transition_id}/executions'
        return self._make_request(requests.post, endpoint, body={})

    def list_transition_executions(
        self,
        transition_id: str,
        status: Optional[Queryparam] = None,
        execution_id: Optional[Queryparam] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict:
        """List executions in a transition, calls the GET /transitions/{transitionId}/executions endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_transition_executions('<transition_id>', '<status>')

        :param transition_id: Id of the transition
        :type transition_id: str
        :param status: Statuses of the executions
        :type status: Queryparam
        :param execution_id: Ids of the executions
        :type execution_id: Queryparam
        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Transition executions responses from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        url = f'/transitions/{transition_id}/executions'
        params = {
            'status': status,
            'executionId': execution_id,
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, url, params=params)

    def update_transition_execution(
        self,
        transition_id: str,
        execution_id: str,
        status: str,
        output: Optional[dict] = None,
        error: Optional[dict] = None,
    ) -> dict:
        """Ends the processing of the transition execution,
        calls the PATCH /transitions/{transition_id}/executions/{execution_id} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> output = {...}
        >>> client.update_transition_execution('<transition_id>', '<execution_id>', 'succeeded', output)
        >>> error = {"message": 'The execution could not be processed due to ...'}
        >>> client.update_transition_execution('<transition_id>', '<execution_id>', 'failed', error)

        :param transition_id: Id of the transition that performs the execution
        :type transition_id: str
        :param execution_id: Id of the execution to update
        :type execution_id: str
        :param status: Status of the execution 'succeeded|failed'
        :type status: str
        :param output: Output from the execution, required when status is 'succeded'
        :type output: str
        :param error: Error from the execution, required when status is 'failed', needs to contain 'message'
        :type error: str
        :return: Transition execution response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        url = f'/transitions/{transition_id}/executions/{execution_id}'
        body = {
            'status': status,
            'output': output,
            'error': error,
        }
        return self._make_request(requests.patch, url, body=dictstrip(body))

    def create_user(self, email: str) -> dict:
        """Creates a new user, calls the POST /users endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.create_user('<email>')

        :param email: Email to the new user
        :type email: str
        :return: User response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.post, '/users', body={'email': email})

    def list_users(self, max_results: Optional[int] = None, next_token: Optional[str] = None) -> dict:
        """List users, calls the GET /users endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_users()

        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Users response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        params = {
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, '/users', params=params)

    def get_user(self, user_id: str) -> dict:
        """Get information about a specific user, calls the GET /users/{user_id} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.get_user('<user_id>')

        :param user_id: Id of the user
        :type user_id: str
        :return: User response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.get, f'/users/{user_id}')

    def delete_user(self, user_id: str) -> dict:
        """Delete the user with the provided user_id, calls the DELETE /users/{userId} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.delete_user('<user_id>')

        :param user_id: Id of the user
        :type user_id: str
        :return: User response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.delete, f'/users/{user_id}')

    def create_workflow(
        self,
        specification: dict,
        name: str,
        description: Optional[str] = None,
        error_config: Optional[dict] = None,
    ) -> dict:
        """Creates a new workflow, calls the POST /workflows endpoint.

        >>> from las.client import BaseClient
        >>> from pathlib import Path
        >>> client = BaseClient()
        >>> specification = {'language': 'ASL', 'version': '1.0.0', 'definition': {...}}
        >>> error_config = {'email': '<error-recipient>'}
        >>> client.create_workflow(specification, '<name>', '<description>', error_config)

        :param specification: Specification of the workflow,
            currently supporting ASL: https://states-language.net/spec.html
        :type specification: dict
        :param name: Name of the workflow
        :type name: str
        :param description: Description of the workflow
        :type description: str
        :param error_config: Configuration of error handler
        :type error_config: dict
        :return: Workflow response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'specification': specification,
            'name': name,
            'description': description,
            'errorConfig': error_config,
        }
        return self._make_request(requests.post, '/workflows', body=dictstrip(body))

    def list_workflows(self, max_results: Optional[int] = None, next_token: Optional[str] = None) -> dict:
        """List workflows, calls the GET /workflows endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_workflows()

        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Workflows response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        params = {
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, '/workflows', params=params)

    def update_workflow(self, workflow_id: str, *, name: Optional[str], description: Optional[str] = None) -> dict:
        """Creates a workflow handle, calls the PATCH /workflows/{workflowId} endpoint.

        >>> import json
        >>> from pathlib import Path
        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.update_workflow('<workflow-id>', name='<name>', description='<description>')

        :param workflow_id: Id of the workflow
        :type name: str
        :param name: Name of the workflow
        :type name: Optional[str]
        :param description: Description of the workflow
        :type description: Optional[str]
        :return: Workflow response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        body = {
            'name': name,
            'description': description,
        }
        return self._make_request(requests.patch, f'/workflows/{workflow_id}', body=dictstrip(body))

    def delete_workflow(self, workflow_id: str) -> dict:
        """Delete the workflow with the provided workflow_id, calls the DELETE /workflows/{workflowId} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.delete_workflow('<workflow_id>')

        :param workflow_id: Id of the workflow
        :type workflow_id: str
        :return: Workflow response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.delete, f'/workflows/{workflow_id}')

    def execute_workflow(self, workflow_id: str, content: dict) -> dict:
        """Start a workflow execution, calls the POST /workflows/{workflowId}/executions endpoint.

        >>> from las.client import BaseClient
        >>> from pathlib import Path
        >>> client = BaseClient()
        >>> content = {...}
        >>> client.execute_workflow('<workflow_id>', content)

        :param workflow_id: Id of the workflow
        :type workflow_id: str
        :param content: Input to the first step of the workflow
        :type content: dict
        :return: Workflow execution response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        endpoint = f'/workflows/{workflow_id}/executions'
        return self._make_request(requests.post, endpoint, body={'input': content})

    def list_workflow_executions(
            self,
            workflow_id: str,
            status: Optional[Queryparam] = None,
            sort_by: Optional[str] = None,
            order: Optional[str] = None,
            max_results: Optional[int] = None,
            next_token: Optional[str] = None,
    ) -> dict:
        """List executions in a workflow, calls the GET /workflows/{workflowId}/executions endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.list_workflow_executions('<workflow_id>', '<status>')

        :param workflow_id: Id of the workflow
        :type workflow_id: str
        :param order: Order of the executions, either 'ascending' or 'descending'
        :type order: Optional str
        :param sort_by: the sorting variable of the executions, either 'endTime', or 'startTime'
        :type sort_by: Optional str
        :param status: Statuses of the executions
        :type status: Queryparam
        :param max_results: Maximum number of results to be returned
        :type max_results: int
        :param next_token: A unique token for each page, use the returned token to retrieve the next page.
        :type next_token: str
        :return: Workflow executions responses from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        url = f'/workflows/{workflow_id}/executions'
        params = {
            'status': status,
            'order': order,
            'sortBy': sort_by,
            'maxResults': max_results,
            'nextToken': next_token,
        }
        return self._make_request(requests.get, url, params=params)

    def delete_workflow_execution(self, workflow_id: str, execution_id: str) -> dict:
        """Deletes the execution with the provided execution_id from workflow_id,
        calls the DELETE /workflows/{workflowId}/executions/{executionId} endpoint.

        >>> from las.client import BaseClient
        >>> client = BaseClient()
        >>> client.delete_workflow_execution('<workflow_id>', '<execution_id>')

        :param workflow_id: Id of the workflow
        :type workflow_id: str
        :param execution_id: Id of the execution
        :type execution_id: str
        :return: WorkflowExecution response from REST API
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self._make_request(requests.delete, f'/workflows/{workflow_id}/executions/{execution_id}')


class Client(BaseClient):
    """A high level client to invoke api methods from Lucidtech AI Services."""
    def predict(
        self,
        document_path: str,
        model_id: str,
        consent_id: Optional[str] = None,
    ) -> Prediction:
        """Create a prediction on a document specified by path using specified model.
        This method takes care of creating and uploading a document specified by document_path.
        as well as running inference using model specified by model_id to create prediction on the document.

        >>> from las import Client
        >>> client = Client()
        >>> client.predict(document_path='document.jpeg', model_id='las:model:<hex-uuid>')

        :param document_path: Path to document to run inference on
        :type document_path: str
        :param model_id: Id for the model to use for inference
        :type model_id: str
        :param consent_id: Id to mark the owner of the document handle
        :type consent_id: str
        :return: Prediction on document
        :rtype: Prediction

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        content_type = self._get_content_type(document_path)
        document = pathlib.Path(document_path).read_bytes()
        response = self.create_document(document, content_type, consent_id)
        document_id = response['documentId']
        prediction_response = self.create_prediction(document_id, model_id)
        return Prediction(document_id, consent_id, model_id, prediction_response)

    def send_ground_truth(self, document_id: str, ground_truth: List[Field]) -> dict:
        """Send ground truth to the model.
        This method takes care of sending ground truth related to document specified by document_id.

        >>> from las import Client
        >>> client = Client()
        >>> ground_truth = [Field(label='total_amount', value='120.00'), Field(label='due_date', value='2019-03-10')]
        >>> client.send_ground_truth('<document id>', ground_truth)

        :param document_id: Id of the document that will receive the ground truth
        :type document_id: str
        :param ground_truth: List of :py:class:`~las.Field` representing the ground truth values for the document
        :type ground_truth: List[Field]
        :return: GroundTruth response
        :rtype: dict

        :raises: :py:class:`~las.InvalidCredentialsException`, :py:class:`~las.TooManyRequestsException`,\
 :py:class:`~las.LimitExceededException`, :py:class:`requests.exception.RequestException`
        """
        return self.update_document(document_id, ground_truth)

    @staticmethod
    def _get_content_type(document_path: str) -> str:
        supported_formats = {
            'image/jpeg',
            'application/pdf',
        }

        content = pathlib.Path(document_path).read_bytes()
        guessed_type = filetype.guess(content)

        if guessed_type and guessed_type.mime in supported_formats:
            return guessed_type.mime
        else:
            raise FileFormatException
