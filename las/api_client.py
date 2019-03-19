import pathlib
import imghdr
import logging

from uuid import uuid4
from typing import List

from ._extrahdr import extra_what
from .client import Client
from .prediction import Prediction, Field


logger = logging.getLogger('las')


class FileFormatException(Client):
    """A FileFormatException is raised if the file format is not supported by the api."""
    pass


class ApiClient(Client):
    """A high level client to invoke api methods from Lucidtech AI Services.

    :param endpoint: Domain endpoint of the api, e.g. https://<prefix>.api.lucidtech.ai/<version>
    :type endpoint: str
    :param credentials: Credentials to use, instance of :py:class:`~las.Credentials`
    :type credentials: Credentials

    """
    def predict(self, document_path: str, model_name: str, consent_id: str = None) -> Prediction:
        """Run inference and create prediction on document.
        This method takes care of creating and uploading a document specified by document_path.
        as well as running inference using model specified by model_name to create prediction on the document.

        >>> from las import ApiClient
        >>> api_client = ApiClient(endpoint='<api endpoint>')
        >>> api_client.predict(document_path='document.jpeg', model_name='invoice')

        :param document_path: Path to document to run inference on
        :type document_path: str
        :param model_name: The name of the model to use for inference
        :type model_name: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Prediction on document
        :rtype: Prediction
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises requests.exception.RequestException: If error was raised by requests
        """

        content_type = self._get_content_type(document_path)
        consent_id = consent_id or str(uuid4())
        document_id = self._upload_document(document_path, content_type, consent_id)
        prediction_response = self.post_predictions(document_id, model_name)
        return Prediction(document_id, consent_id, model_name, prediction_response)

    def send_feedback(self, document_id: str, feedback: List[Field]) -> dict:
        """Send feedback to the model.
        This method takes care of sending feedback related to document specified by document_id.
        Feedback consists of ground truth values for the document specified as a list of Field instances.

        >>> from las import ApiClient
        >>> api_client = ApiClient(endpoint='<api endpoint>')
        >>> feedback = [Field(label='total_amount', value='120.00'), Field(label='purchase_date', value='2019-03-10')]
        >>> api_client.send_feedback('<document id>', feedback)

        :param document_id: The document id of the document that will receive the feedback
        :type document_id: str
        :param feedback: A list of :py:class:`~las.Field` representing the ground truth values for the document
        :type feedback: List[Field]
        :return: Feedback response
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises requests.exception.RequestException: If error was raised by requests
        """

        return self.post_document_id(document_id, feedback)

    def revoke_consent(self, consent_id: str) -> dict:
        """Revoke consent and deleting all documents associated with consent_id.
        Consent id is a parameter that is provided by the user upon making a prediction on a document.
        See :py:func: `~las.ApiClient.predict`.

        >>> from las import ApiClient
        >>> api_client = ApiClient(endpoint='<api endpoint>')
        >>> api_client.revoke_consent('<consent id>')

        :param consent_id: Delete documents associated with this consent_id
        :type consent_id: str
        :return: Revoke consent response
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises requests.exception.RequestException: If error was raised by requests
        """
        return self.delete_consent_id(consent_id)

    def _upload_document(self, document_path: str, content_type: str, consent_id: str) -> str:
        post_documents_response = self.post_documents(content_type, consent_id)
        document_id = post_documents_response['documentId']
        presigned_url = post_documents_response['uploadUrl']
        self.put_document(document_path, content_type, presigned_url)
        return document_id

    @staticmethod
    def _get_content_type(document_path: str) -> str:
        supported_formats = {
            'jpeg': 'image/jpeg',
            'pdf': 'application/pdf'
        }

        fp = pathlib.Path(document_path)
        fmt = imghdr.what(fp) or extra_what(fp)

        if fmt in supported_formats:
            return supported_formats[fmt]
        else:
            raise FileFormatException
