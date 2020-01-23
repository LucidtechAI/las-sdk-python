import configparser

import os
from os.path import expanduser, exists
from typing import Tuple, Optional


class MissingCredentials(Exception):
    pass


class Credentials:
    """Used to fetch and store credentials. One of 4 conditions must be met to successfully create credentials.

    1. credentials_path is provided
    2. access_key_id, secret_access_key and api_key is provided
    3. credentials is located in default path ~/.lucidtech/credentials.cfg
    4. the following environment variables are present:
        - LAS_ACCESS_KEY_ID
        - LAS_SECRET_ACCESS_KEY
        - LAS_API_KEY

    :param credentials_path: Path to credentials file
    :type credentials_path: str
    :param access_key_id: Access Key Id
    :type access_key_id: str
    :param secret_access_key: Secret Access Key
    :type secret_access_key: str
    :param api_key: API key
    :type api_key: str

    """
    def __init__(self, credentials_path=None, access_key_id=None, secret_access_key=None, api_key=None):
        if not all([access_key_id, secret_access_key, api_key]):
            if not credentials_path:
                credentials_path = expanduser('~/.lucidtech/credentials.cfg')

            if exists(credentials_path):
                access_key_id, secret_access_key, api_key = self._read_from_file(credentials_path)
            else:
                access_key_id, secret_access_key, api_key = self._read_from_environ()

        if not all([access_key_id, secret_access_key, api_key]):
            raise MissingCredentials

        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.api_key = api_key

    @staticmethod
    def _read_from_environ() -> Tuple[Optional[str], Optional[str], Optional[str]]:
        access_key_id = os.environ.get('LAS_ACCESS_KEY_ID')
        secret_access_key = os.environ.get('LAS_SECRET_ACCESS_KEY')
        api_key = os.environ.get('LAS_API_KEY')

        return access_key_id, secret_access_key, api_key

    @staticmethod
    def _read_from_file(credentials_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        config = configparser.ConfigParser()
        config.read(credentials_path)
        section = 'default'

        access_key_id = config.get(section, 'access_key_id')
        secret_access_key = config.get(section, 'secret_access_key')
        api_key = config.get(section, 'api_key')

        return access_key_id, secret_access_key, api_key
