import configparser

from os.path import expanduser
from typing import Tuple


class MissingCredentials(Exception):
    pass


class Credentials:
    """Used to fetch and store credentials. One of 3 conditions must be met to successfully create credentials.

    1. credentials_path is provided
    2. access_key_id, secret_access_key and api_key is provided
    3. credentials is located in default path ~/.lucidtech/credentials.cfg

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
        if any([not access_key_id, not secret_access_key, not api_key]):
            if not credentials_path:
                credentials_path = expanduser('~/.lucidtech/credentials.cfg')

            access_key_id, secret_access_key, api_key = self._read_credentials(credentials_path)

        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.api_key = api_key

        if any([not access_key_id, not secret_access_key, not api_key]):
            raise MissingCredentials

    @staticmethod
    def _read_credentials(credentials_path: str) -> Tuple[str, str, str]:
        config = configparser.ConfigParser()
        config.read(credentials_path)
        section = 'default'

        access_key_id = config.get(section, 'access_key_id')
        secret_access_key = config.get(section, 'secret_access_key')
        api_key = config.get(section, 'api_key')

        return access_key_id, secret_access_key, api_key
