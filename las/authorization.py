import datetime
import hashlib
import hmac

from urllib.parse import ParseResult
from typing import Tuple, Iterable

from .credentials import Credentials


class Authorization:
    ALGORITHM = 'AWS4-HMAC-SHA256'

    def __init__(self, credentials: Credentials):
        self.region = 'eu-west-1'
        self.service = 'execute-api'
        self.credentials = credentials

    def sign_headers(self, uri: ParseResult, method: str, body: bytes = None) -> dict:
        if not body:
            body = ''.encode('utf-8')

        amz_date, datestamp = self._timestamp()

        canonical_request, headers = self._get_canonical_request(
            uri=uri,
            method=method,
            body=body,
            amz_date=amz_date)

        req_digest = hashlib.sha256(canonical_request).hexdigest()
        cred_scope = self._get_credential_scope(datestamp)
        string_to_sign = self._get_sign_string(amz_date, cred_scope, req_digest)
        signing_key = self._get_signature_key(datestamp)

        signature = hmac.new(signing_key, string_to_sign, hashlib.sha256).hexdigest()

        auth_header = self._build_auth_header(
            amz_date=amz_date,
            access_key=self.credentials.access_key_id,
            api_key=self.credentials.api_key,
            signature=signature,
            credential_scope=cred_scope,
            signed_headers=headers
        )

        return auth_header

    def _get_sign_string(self, amz_date: str, cred_scope: str, req_digest: str) -> bytes:
        sign_parts = [self.ALGORITHM, amz_date, cred_scope, req_digest]
        return '\n'.join(sign_parts).encode('utf-8')

    def _get_credential_scope(self, datestamp: str) -> str:
        scope_parts = [datestamp, self.region, self.service, 'aws4_request']
        return '/'.join(scope_parts)

    def _get_canonical_request(self, uri: ParseResult, method: str, body: bytes, amz_date: str) \
            -> Tuple[bytes, Iterable[str]]:
        canonical_querystring = self._get_canonical_querystring(uri.query)

        header_keys = ('host', 'x-amz-date', 'x-api-key')
        header_values = (uri.netloc, amz_date, self.credentials.api_key)
        headers = dict(zip(header_keys, header_values))

        header_parts = (f'{k}:{v}\n' for k, v in headers.items())
        payload_hash = hashlib.sha256(body).hexdigest()

        request_components = [
            method, uri.path, canonical_querystring,
            ''.join(header_parts), ';'.join(headers),
            payload_hash]

        return '\n'.join(request_components).encode('utf-8'), headers.keys()

    # TODO: Implement AWS sig v4 canonical querystring
    def _get_canonical_querystring(self, querystring: str) -> str:
        if querystring:
            raise NotImplementedError('Creating canonical querystring is not implemented')
        return ''

    def _get_signature_key(self, datestamp: str) -> str:
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        signature = ('AWS4' + self.credentials.secret_access_key).encode('utf-8')
        for part in (datestamp, self.region, self.service, 'aws4_request'):
            signature = sign(signature, part)

        return signature

    @classmethod
    def _build_auth_header(cls, amz_date: str, access_key: str, api_key: str, signature: str,
                           credential_scope: str, signed_headers: Iterable[str]) -> dict:
        auth = {
            'Credential': f'{access_key}/{credential_scope}',
            'SignedHeaders': ';'.join(signed_headers),
            'Signature': signature
        }

        auth_parts = (f'{k}={auth[k]}' for k in auth)
        auth_string = ', '.join(auth_parts)

        headers = {
            'x-amz-date': amz_date,
            'x-api-key': api_key,
            'Authorization': f'{cls.ALGORITHM} {auth_string}'
        }

        headers = {k: v for k, v in headers.items() if v}
        return headers

    @staticmethod
    def _timestamp() -> Tuple[str, str]:
        now = datetime.datetime.utcnow()
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        datestamp = now.strftime('%Y%m%d')
        return amz_date, datestamp
