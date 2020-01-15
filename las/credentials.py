import configparser
import requests
import time

from os.path import expanduser
from typing import Tuple
from requests.auth import HTTPBasicAuth


class MissingCredentials(Exception):
    pass


class Credentials:
    """Used to fetch and store credentials. One of 3 conditions must be met to successfully create credentials.

    1. credentials_path is provided
    2. client_id, client_secret, api_key and auth_endpoint is provided
    3. credentials is located in default path ~/.lucidtech/credentials.cfg

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
    def __init__(self, credentials_path=None, client_id=None, client_secret=None,
                 api_key=None, auth_endpoint=None, api_endpoint=None):
        self._token = (None, None)

        if any([not client_id, not client_secret, not api_key, not auth_endpoint, not api_endpoint]):
            if not credentials_path:
                credentials_path = expanduser('~/.lucidtech/credentials.cfg')

            client_id, client_secret, api_key, auth_endpoint, api_endpoint \
                = self._read_credentials(credentials_path)

        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.auth_endpoint = auth_endpoint
        self.api_endpoint = api_endpoint

        if any([not self.client_id, not self.client_secret, not self.api_key,
                not self.auth_endpoint, not self.api_endpoint]):
            raise MissingCredentials

    @staticmethod
    def _read_credentials(credentials_path: str) -> Tuple[str, str, str, str, str]:
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

