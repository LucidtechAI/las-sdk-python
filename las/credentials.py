import configparser
import requests
import time
import os
from requests.auth import HTTPBasicAuth
from os.path import expanduser, exists
from typing import Tuple, Optional


class MissingCredentials(Exception):
    pass


class Credentials:
    """Used to fetch and store credentials. One of 4 conditions must be met to successfully create credentials.

    1. credentials_path is provided
    2. client_id, client_secret, api_key and auth_endpoint is provided
    3. credentials is located in default path ~/.lucidtech/credentials.cfg
    4. the following environment variables are present:
        - LAS_CLIENT_ID
        - LAS_CLIENT_SECRET
        - LAS_API_KEY

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
    def __init__(self, credentials_path=None, client_id=None, client_secret=None, api_key=None,
                 auth_endpoint=None, api_endpoint=None):
        self._token = (None, None)
        if not all([client_id, client_secret, api_key, auth_endpoint, api_endpoint]):
            assert not any([client_id, client_secret, api_key, auth_endpoint, api_endpoint])
            if not credentials_path:
                credentials_path = expanduser('~/.lucidtech/credentials.cfg')

            if exists(credentials_path):
                creds = self._read_from_file(credentials_path)
            else:
                creds = self._read_from_environ()
            client_id, client_secret, api_key, auth_endpoint, api_endpoint = creds

        if not all([client_id, client_secret, api_key]):
            raise MissingCredentials

        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.auth_endpoint = auth_endpoint
        self.api_endpoint = api_endpoint

    @staticmethod
    def _read_from_environ() -> Tuple[Optional[str], Optional[str], Optional[str]]:
        creds = [os.environ.get(k) for k in
                 ['LAS_CLIENT_ID', 'LAS_CLIENT_SECRET', 'LAS_API_KEY',
                  'LAS_AUTH_ENDPOINT', 'LAS_API_ENDPOINT']]
        return tuple(creds)

    @staticmethod
    def _read_from_file(credentials_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        config = configparser.ConfigParser()
        config.read(credentials_path)
        section = 'default'

        client_id = config.get(section, 'client_id')
        client_secret = config.get(section, 'client_secret')
        api_key = config.get(section, 'api_key')
        auth_endpoint = config.get(section, 'auth_endpoint')
        api_endpoint = config.get(section, 'api_endpoint')

        return client_id, client_secret, api_key, auth_endpoint, api_endpoint

    @property
    def access_token(self) -> str:
        access_token, expiration = self._token

        if not access_token or time.time() > expiration:
            access_token, expiration = self._get_client_credentials()
            self._token = (access_token, expiration)

        return access_token

    def _get_client_credentials(self) -> Tuple[str, int]:
        url = f'https://{self.auth_endpoint}/oauth2/token?grant_type=client_credentials'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        auth = HTTPBasicAuth(self.client_id, self.client_secret)

        response = requests.post(url, headers=headers, auth=auth)
        response.raise_for_status()

        response_data = response.json()
        return response_data['access_token'], time.time() + response_data['expires_in']
