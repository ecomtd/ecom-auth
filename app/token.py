import jwt
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
