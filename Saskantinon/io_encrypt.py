#!python
"""
:module:    io_encrypt.py
:class:     EncryptUtils

Functions:

    - Generate an encryption key
    - Use encryption key to encrypt anything and return it in encrypted format
    - Use encryption key to decrypt using known encryption key
        - Return it in plain text format,
        - And store it in a defined location, using a pre-defined format
    - Retrieve the stored encryption key
    - Encrypt an ID and a password, storing the encrypted values in a
      pre-defined format
    - Retrieve encrypted ID and password
"""
import json
import secrets
from collections import namedtuple
from cryptography.fernet import Fernet  # type: ignore
from os import getcwd, path
from tornado.options import define, options

import arrow


class EncryptUtils(object):
    """Generic utilities cloned from Utils class"""

    @classmethod
    def get_dttm(cls):
        """Get date and time values.

        Returns:
            namedtuple
            - .curr_utc {string} UTC date time (YYYY-MM-DD HH:mm:ss.SSSSS ZZ)
            - .next_utc {string} UTC date time plus 1 day
            - .curr_ts  {string} UTC time stamp (YYYYMMDDHHmmssSSSSS)
        """
        long_format = 'YYYY-MM-DD HH:mm:ss.SSSSS ZZ'
        dttm = namedtuple("dttm", "curr_utc next_utc curr_ts")
        utc_dttm = arrow.utcnow()
        dttm.curr_utc = str(utc_dttm.format(long_format))
        dttm.next_utc = str(utc_dttm.shift(days=+1).format(long_format))
        dttm.curr_ts = dttm.curr_utc.strip()
        for rm in [' ', ':', '+', '.', '-']:
            dttm.curr_ts = dttm.curr_ts.replace(rm, '')
        dttm.curr_ts = dttm.curr_ts[0:-4]
        return dttm


class Encrypt(object):
    """
    @class:  BowEncrypt

    Support encryption, storing/retrieving encrypted texts.
    """
    def __init__(self):
        """
        Initialize BowEncrypt object
        """
        self.cwd = getcwd()
        self.set_configs()
        self.UT = EncryptUtils()

    def set_configs(self):
        """
        Define config items. load their values from config file
        """
        for config_item in ['tag_creds', 'encrypt_tag']:
            define(config_item)
        script_path = path.abspath(path.realpath(__file__))
        script_dir = path.split(script_path)[0]
        config_path = path.abspath(path.join(script_dir,
                                             'model/BowEncrypt.conf'))
        options.parse_config_file(config_path)

    @classmethod
    def encrypt_me(cls, p_str_plaintext, p_key):
        """
        Return encrypted byte stream from the input string.

        :Args:
            {string} to be encrypted
            {bytes}  encryption key as byte-stream

        :Return:  {bytes} encrypted version of input
        """
        cipher_suite = Fernet(p_key)
        encoded_bytes = cipher_suite.encrypt(bytes(p_str_plaintext, 'utf-8'))
        return encoded_bytes

    @classmethod
    def decrypt_me(cls, p_bytes_encrypted, p_key):
        """
        Return decrypted version of the input bytes.

        :Args: {bytes} result of calling encrypt_me()
               {bytes} encryption key as byte-stream

        :Return: {string} decrypted value
        """
        cipher_suite = Fernet(p_key)
        decoded_str = cipher_suite.decrypt(p_bytes_encrypted)
        decoded_str = decoded_str.decode("utf-8")
        return decoded_str

    def create_encrypt_key(self, p_key_tag=None):
        """
        Create a key for use with Fernet encryption.
        Store in a persisted as defined in config file,
          first removing any older records using the same tag.
        Return the encrypted byte-stream and the formatted record.

        @DEV: Just return the value to the caller w/o storing it.
               Let caller manage that if desired.

        :Args:  {string} (Optional) verify/identify encryption-key value.
                         If None, then use options.encrypt_tag

        :Return: {tuple} ( {string} encryption tag,
                           {bytes} encryption key )
        """
        encrypt_tag = p_key_tag\
            if p_key_tag is not None else options.encrypt_tag
        encrypt_key = Fernet.generate_key()

        return (encrypt_tag, encrypt_key)

    def create_secret_key(self, key_length=None, context_key=None):
        """
        Return a cryptographically strong random value that is URL safe,
        A value shorter than 32 bytes is not good.

        Return in JSON format that includes a timestamp and a context key

        :Args:
            - {integer} desired length of the key or None
            - {string} desired context key or None

        :Return: {tuple} ({bytes} encryption key, {string} JSON record)
        """
        key_length = 32 if key_length is None else key_length
        key_length = 32 if key_length < 32 else key_length
        secret_key = secrets.token_urlsafe(key_length)
        ts = self.UT.get_dttm()
        context_key = ts.curr_lcl if context_key is None else context_key
        secret_record = dict()
        secret_record[context_key] =\
            {"date": str(ts.curr_lcl), "key": str(secret_key)}
        return (secret_key, json.dumps(secret_record))
