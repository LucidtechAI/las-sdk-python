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
    """Used to fetch and store credentials and to generate/cache an access token.

    :param client_id: The client id
    :type str:
    :param client_secret: The client secret
    :type str:
    :param api_key: The api key
    :type str:
    :param auth_endpoint: The auth endpoint
    :type str:
    :param api_endpoint: The api endpoint
    :type str:"""

    def __init__(self, client_id: str, client_secret: str, api_key: str, auth_endpoint: str, api_endpoint: str):
        if not all([client_id, client_secret, api_key, auth_endpoint, api_endpoint]):
            raise MissingCredentials

        self._token = ('', 0)
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.auth_endpoint = auth_endpoint
        self.api_endpoint = api_endpoint

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


def read_from_environ() -> List[Optional[str]]:
    """Read the following environment variables and return them:
        - LAS_CLIENT_ID
        - LAS_CLIENT_SECRET
        - LAS_API_KEY
        - LAS_AUTH_ENDPOINT
        - LAS_API_ENDPOINT

    :return: List of client_id, client_secret, api_key, auth_endpoint, api_endpoint
    :rtype: List[Optional[str]]"""

    return [os.environ.get(k) for k in (
        'LAS_CLIENT_ID',
        'LAS_CLIENT_SECRET',
        'LAS_API_KEY',
        'LAS_AUTH_ENDPOINT',
        'LAS_API_ENDPOINT'
    )]


def read_from_file(credentials_path: str = expanduser('~/.lucidtech/credentials.cfg'),
                   section: str = 'default') -> List[Optional[str]]:
    """Read a config file and return credentials from it. Defaults to '~/.lucidtech/credentials.cfg'.

    :param credentials_path: Path to read credentials from.
    :type credentials_path: str
    :param section: Section to read credentials from.
    :type section: str

    :return: List of client_id, client_secret, api_key, auth_endpoint, api_endpoint
    :rtype: List[Optional[str]]"""

    if not exists(credentials_path):
        raise MissingCredentials

    config = configparser.ConfigParser()
    config.read(credentials_path)

    client_id = config.get(section, 'client_id')
    client_secret = config.get(section, 'client_secret')
    api_key = config.get(section, 'api_key')
    auth_endpoint = config.get(section, 'auth_endpoint')
    api_endpoint = config.get(section, 'api_endpoint')

    return [client_id, client_secret, api_key, auth_endpoint, api_endpoint]


def guess_credentials() -> Credentials:
    """Tries to fetch Credentials first by looking at the environment variables, next by looking at the default
    credentials path ~/.lucidtech/credentials.cfg. Note that if not all the required environment variables
    are present, _all_ variables will be disregarded, and the credentials in the default path will be used.

    :return: Credentials from file
    :rtype: :py:class:`~las.Credentials`

    :raises: :py:class:`~las.MissingCredentials`"""

    for guesser in [read_from_environ, read_from_file]:
        args = guesser()  # type: ignore
        if all(args):
            return Credentials(*args)
    raise MissingCredentials
