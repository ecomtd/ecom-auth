import binascii

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
from app.settings import auth_qr_aes_key


def to_unicode(s, encoding="utf-8"):
    """
    Converts the string s to unicode if it is of type bytes.

    :param s: the string to convert
    :type s: bytes or str
    :param encoding: the encoding to use (default utf8)
    :type encoding: str
    :return: unicode string
    :rtype: str
    """
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(encoding)
    return s


def to_bytes(s):
    """
    Converts the string s to a unicode encoded byte string
    :param s: string to convert
    :type s: str or bytes
    :return: the converted byte string
    :rtype: bytes
    """
    if isinstance(s, bytes):
        return s
    elif isinstance(s, str):
        return s.encode('utf8')
    return s


def b64encode_and_unicode(s):
    """
    Base64-encode a str (which is first encoded to UTF-8)
    or a byte string and return the result as a str.
    :param s: str or bytes to base32-encode
    :type s: str or bytes
    :return: base64-encoded string converted to unicode
    :rtype: str
    """
    res = to_unicode(base64.b64encode(to_bytes(s)))
    return res


def aes_encrypt_b64(key, data):
    """
    This function encrypts the data using AES-128-CBC. It generates
    and adds an IV.
    This is used for PSKC.

    :param key: Encryption key (binary format)
    :type key: bytes
    :param data: Data to encrypt
    :type data: bytes
    :return: base64 encrypted output, containing IV and encrypted data
    :rtype: str
    """
    # pad data
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    iv = os.urandom(16)
    backend = default_backend()
    mode = modes.CBC(iv)
    cipher = Cipher(algorithms.AES(key), mode=mode, backend=backend)
    encryptor = cipher.encryptor()
    encdata = encryptor.update(padded_data) + encryptor.finalize()
    return b64encode_and_unicode(iv + encdata)


def aes_decrypt_b64(key, enc_data_b64):
    """
    This function decrypts base64 encoded data (containing the IV)
    using AES-128-CBC. Used for PSKC

    :param key: binary key
    :param enc_data_b64: base64 encoded data (IV + encdata)
    :type enc_data_b64: str
    :return: encrypted data
    """
    data_bin = base64.b64decode(enc_data_b64)
    iv = data_bin[:16]
    encdata = data_bin[16:]
    backend = default_backend()
    mode = modes.CBC(iv)
    cipher = Cipher(algorithms.AES(key), mode=mode, backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encdata) + decryptor.finalize()

    # remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    output = unpadder.update(padded_data) + unpadder.finalize()

    return output


def decode_base64(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.b64decode(data)


def encrypt_credentials(credentials):
    return aes_encrypt_b64(decode_base64(auth_qr_aes_key), to_bytes(credentials))


def decrypt_credentials(credentials):
    try:
        return aes_decrypt_b64(decode_base64(auth_qr_aes_key), credentials).decode('utf8')
    except binascii.Error:
        pass
    except ValueError:
        pass
