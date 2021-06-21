import base64
import binascii
import json

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED

import app.settings as settings
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key


private_key = load_pem_private_key(open(settings.auth_private_key_file, "rb").read(), None, crypto_default_backend()).\
    private_bytes(crypto_serialization.Encoding.PEM,
                  crypto_serialization.PrivateFormat.TraditionalOpenSSL,
                  crypto_serialization.NoEncryption()).\
    decode("utf-8")


def create(payload):
    return jwt.encode(payload, private_key, algorithm="RS512")


def decode_base64(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.b64decode(data)


def get_user_id(access_token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    if access_token.credentials:
        if len(access_token.credentials.split(".")) == 3:
            try:
                payload = json.loads(decode_base64(access_token.credentials.split(".")[1]).decode("UTF-8"))
                return payload["sub"]
            except binascii.Error:
                pass
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
