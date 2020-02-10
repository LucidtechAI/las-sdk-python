import configparser
import os
import time
from os.path import exists, expanduser
from typing import List, Optional, Tuple

import requests
from requests.auth import HTTPBasicAuth


class MissingCredentials(Exception):
    pass


class Credentials:
    """Used to fetch and store credentials. Credentials are fetched in the below order. If any point
    yields 5 credentials, those are used, and if not, the constructor continues on to next point.

    1. creds is provided
    2. credentials_path is provided
    3. all of the following environment variables are present:
        - LAS_CLIENT_ID
        - LAS_CLIENT_SECRET
        - LAS_API_KEY
        - LAS_AUTH_ENDPOINT
        - LAS_API_ENDPOINT
    4. credentials is located in default path ~/.lucidtech/credentials.cfg

    Note that all 5 variables must end up being set - if e.g. 4 environment variables are set, but not the fifth,
    all variables will be disregarded, and the credentials in the default path will be used.

    :param credentials_path: Path to credentials file
    :type credentials_path: str
    :param client_id: Client Id
    :type client_id: str
    :param client_secret: Client Secret
    :type client_secret: str
    :param api_key: API key
    :type api_key: str
    :param auth_endpoint: Authorization endpoint
    :type auth_endpoint: str

    """
    def __init__(self, creds: Optional[List[str]] = None, credentials_path: Optional[str] = None):
        self._token = (None, None)
        if creds is not None:
            assert len(creds) == 5, "creds should be a list of 5 strings"
        else:
            if credentials_path is not None:
                creds = list(self._read_from_file(credentials_path))
            else:
                # try to read creds from environment, give up and read from default path if not all are found
                creds_from_environ = self._read_from_environ()
                creds = [None] * 5
                for idx, value in enumerate(creds):
                    if creds_from_environ[idx] is not None:
                        creds[idx] = creds_from_environ[idx]
                if not all(creds):
                    creds = self._read_from_file(None)

        if not all(creds):
            raise MissingCredentials

        client_id, client_secret, api_key, auth_endpoint, api_endpoint = creds

        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.auth_endpoint = auth_endpoint
        self.api_endpoint = api_endpoint

    @staticmethod
    def _read_from_environ() -> List[Optional[str]]:
        return [os.environ.get(k) for k in (
            'LAS_CLIENT_ID',
            'LAS_CLIENT_SECRET',
            'LAS_API_KEY',
            'LAS_AUTH_ENDPOINT',
            'LAS_API_ENDPOINT'
        )]

    @staticmethod
    def _read_from_file(credentials_path: str) -> List[Optional[str]]:
        if not credentials_path:
            credentials_path = expanduser('~/.lucidtech/credentials.cfg')

        if not exists(credentials_path):
            return [None] * 5

        config = configparser.ConfigParser()
        config.read(credentials_path)
        section = 'default'

        client_id = config.get(section, 'client_id')
        client_secret = config.get(section, 'client_secret')
        api_key = config.get(section, 'api_key')
        auth_endpoint = config.get(section, 'auth_endpoint')
        api_endpoint = config.get(section, 'api_endpoint')

        return [client_id, client_secret, api_key, auth_endpoint, api_endpoint]

    @property
    def access_token(self) -> str:
        access_token, expiration = self._token

        if not access_token or time.time() > expiration:
            access_token, expiration = self._get_client_credentials()
            self._token = (access_token, expiration)

        return access_token

    def _get_client_credentials(self) -> Tuple[str, int]:
        url = f'https://{self.auth_endpoint}/token?grant_type=client_credentials'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        auth = HTTPBasicAuth(self.client_id, self.client_secret)

        response = requests.post(url, headers=headers, auth=auth)
        response.raise_for_status()

        response_data = response.json()
        return response_data['access_token'], time.time() + response_data['expires_in']
