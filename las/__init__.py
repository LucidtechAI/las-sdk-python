import logging

from .client import Client
from .api import Api


logger = logging.getLogger('las')
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)
