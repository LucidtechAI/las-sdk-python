import pathlib
import imghdr
import logging

from uuid import uuid4

from ._extrahdr import extra_what
from .client import Client, ClientException


logger = logging.getLogger('las')


class FileFormatException(ClientException):
    """a FileFormatException is raised if the file format is not supported by the api."""
    pass


class Field(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def label(self):
        return self['label']

    @property
    def confidence(self):
        return self['confidence']

    @property
    def value(self):
        return self['value']


class Prediction(dict):
    def __init__(self, document_id: str, consent_id: str, model_name: str, prediction_response: dict):
        prediction = dict(
            document_id=document_id,
            consent_id=consent_id,
            model_name=model_name,
            fields=prediction_response['predictions']
        )

        super().__init__(**prediction)

    @property
    def document_id(self):
        return self['document_id']

    @property
    def consent_id(self):
        return self['consent_id']

    @property
    def model_name(self):
        return self['model_name']

    @property
    def fields(self):
        return [Field(**field) for field in self['fields']]


class Api(Client):
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

    def predict(self, document_path: str, model_name: str, consent_id: str = None) -> Prediction:
        content_type = self._get_content_type(document_path)
        consent_id = consent_id or str(uuid4())
        document_id = self._upload_document(document_path, content_type, consent_id)
        prediction_response = self.post_predictions(document_id, model_name)
        return Prediction(document_id, consent_id, model_name, prediction_response)
