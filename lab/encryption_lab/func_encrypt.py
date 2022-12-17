#!/python
"""
:module:  func_encrypt
:class: FuncEncrypt

Functions:
    
    - Generate an encryption key 
    - Use encryption key to encrypt anything and return it in encrypted format
    - Use encryption key to decrypt using a known encryption key and return it in plain text format, 
        - and storing the encryption key in a defined location, using a pre-defined format
    - Retrieve the stored encryption key
    - Encrypt an ID and a password, storing the encrypted values in a pre-defined format
    - Retrieve encrypted ID and password
"""
import os
from cryptography.fernet import Fernet
import json
from pprint import pprint as pp
import sys
from tornado.options import define, options
from func_basic import FuncBasic
FB=FuncBasic()

class FuncEncrypt(object):
    """
    Provide functions to support encryption, as well as storing/retrieving encrypted texts.
    """
    def __init__(self):
        """
        Initialize FuncEncrypt object
        """
        self.cwd = os.getcwd()
        self.set_configs()
        self.set_files()
    
    def set_configs(self):
        """
        Name (define) the configuration items and load their values from configuration file
        """
        for config_item in ['file_credentials', 'file_encrypt_key', 
                            'tag_creds', 'tag_key' ]:
            define(config_item)
        # Get configuration values from configuration file
        conf_file = os.path.join(self.cwd, 'func_encrypt.conf')
        options.parse_config_file(conf_file)

    def set_files(self):
        """
        Set absolute paths to files
        """
        key_file_info = FB.get_path(options.file_encrypt_key)
        self.keys_file = key_file_info.abs

        cred_file_info = FB.get_path(options.file_credentials)
        self.creds_file = cred_file_info.abs
    
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
        
        :Args: {bytes} that were the result of calling the encrypt_me() function
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
        Store it in a formatted record a off-line storage location defined in config file, 
          first removing any older records using the same tag.
        Return the encrypted byte-stream and the formatted record.
        
        :Args:  {string} (Optional) tag to verify/identify the encryption-key value.
                         If None, then use options.tag_key
        
        :Return: {tuple} ( {bytes} encryption key,  {string} JSON_formatted record )
        """
        tag_key = p_key_tag if p_key_tag is not None else options.tag_key
        encrypt_key = Fernet.generate_key()
        ts = FB.get_dttm()
        encrypt_record = {tag_key: {"date": str(ts.curr_ts), 
                                    "key": str(encrypt_key.decode('utf-8'))}}
        encrypt_record = json.dumps(encrypt_record)
        ekey_data = list()
        # Remove any records with this tag:
        ekf_info = FB.get_path(options.file_encrypt_key)
        if ekf_info.exists:
            try:
                with open(options.file_encrypt_key, 'r+') as ekf:
                    ekey_data = ekf.readlines()
                    for ekey_rec in ekey_data:
                        ekey_rec_dict = json.loads(ekey_rec)
                        for ekey, _ in ekey_rec_dict.items():
                            if ekey == tag_key:
                                del ekey_data[ekey_data.index(ekey_rec)]
                    ekf.close()
            except IOError as e:
                msg = "Could not read or modify {}\n{}".format(options.file_encrypt_key, str(e))
                print(msg)
                sys.exit()
            os.remove(options.file_encrypt_key)

        # Rebuild the file after clean up
        ekey_data.append(encrypt_record)
        try:
            with open(options.file_encrypt_key, 'a+') as ekf:
                for e_rec in ekey_data:
                    ekf.write(e_rec + '\n')
                ekf.close()
        except IOError as e:
            msg = "Could not write to {}\n{}".format(options.file_encrypt_key, str(e))
            print(msg)
            sys.exit()

        return (encrypt_key, encrypt_record)
        
    def retrieve_encrypt_key(self, p_key_tag=None):
        """
        Read encryption key from off-line storage
        Each record of the file is a JSON-encoded structure that loads into a dict()
        The file is read into a list structure
        
        :Args: 
            {string}  Optional. A tag created by store_encrypt_key() 
                      Use tag to identify/verify what key to use.
                      If None, then use options.tag_key
                      
        :Return:  {tuple}  (key value as byte-stream; encryption record as JSON)
        """
        tag_key = p_key_tag if p_key_tag is not None else options.tag_key
        encrypt_key_records = list()
        try:
            with open(options.file_encrypt_key, 'r') as ekf:
                encrypt_key_records = ekf.readlines()
                ekf.close()
        except IOError as e:
            msg = 'Could not open {}\n{}'.format(options.file_encrypt_key, str(e))
            print(msg)
            sys.exit()
        
        encrypt_record = None
        for ekrec in encrypt_key_records:
            ekrec = json.loads(ekrec)
            for key, data in ekrec.items():
                if key == tag_key:
                    encrypt_record = ekrec
                    break
            if encrypt_record is not None:
                break

        for key, data in encrypt_record.items():
            return (data['key'].encode(), json.dumps(encrypt_record))
        
        if encrypt_record is None:
            msg = 'No encrypt record found for key: {}'.format(tag_key)
            print(msg)
            sys.exit()
                
    def store_credentials(self, user_id, user_password, p_creds_tag=None, p_key_tag=None):
        """
        Store encryption key off-line
        Remove any records with same Creds Tag and Encrypt Tag before writing new record
        
        :Args: 
            {string} Clear text user ID, will be encrypted using defined encryption key.
            {string} Clear text password, will be encrypted using defined encryption key.
            {string} Optional. A tag to identify/verify what key to use. Example:  "netezza_cbrdm"
                     If None, then use options.tag_creds
            {string} Optional.Encryption key store tag. Will retrieve encryption key value from store using this.
                     If None, then use options.tag_key
        """
        creds_tag = p_creds_tag if p_creds_tag is not None else options.tag_creds
        key_tag = p_key_tag if p_key_tag is not None else options.tag_key
        encrypt_key, _ = self.retrieve_encrypt_key(key_tag)

        encrypt_uid = self.encrypt_me(user_id, encrypt_key)
        encrypt_pwd = self.encrypt_me(user_password, encrypt_key)

        ecred_data = list()
        # Remove any records with these tags:
        ecrf_info = FB.get_path(options.file_credentials)
        if ecrf_info.exists:
            try:
                with open(options.file_encrypt_key, 'r+') as ecrf:
                    ecred_data = ecrf.readlines()
                    for ecred_rec in ecred_data:
                        ecred_rec_dict = json.loads(ecred_rec)
                        for c_key, c_data in ecred_rec_dict.items():
                            if c_key == creds_tag and c_data['encrypt_tag'] == key_tag:
                                del ecred_data[ecred_data.index(ecred_rec)]
                    ecrf.close()
            except IOError as e:
                msg = "Could not read or modify {}\n{}".format(options.file_credentials, str(e))
                print(msg)
                sys.exit()
            os.remove(options.file_credentials)

        ts = FB.get_dttm()        
        encrypt_record = {creds_tag: {"date": str(ts.curr_ts),
                                    "encrypt_tag": key_tag,
                                    "uid": encrypt_uid.decode(),
                                    "pwd": encrypt_pwd.decode()}}
        ecred_data.append(json.dumps(encrypt_record))

        try:
            with open(options.file_credentials, 'a+') as credf:
                for cred_rec in ecred_data:
                    credf.write(cred_rec + '\n')
                credf.close()
        except IOError as e:
            msg = "Could not write to {}\n{}".format(options.file_credentials, str(e))
            print(msg)
            sys.exit()

    def retrieve_credentials(self, p_tag_creds=None):
        """
        Retreive and decrypt user ID and password from off-line storage
        
        :Args:    {string} Optional. Credential tag. If None, use configuration options.tag_creds
        :Return:  {tuple}  (encrypted userid, encrypted password, encrypt-key tag, credentials record as JSON)
        """
        tag_creds = p_tag_creds if p_tag_creds is not None else options.tag_creds
        cred_records = list()
        try:
            with open(options.file_credentials, 'r') as credf:
                cred_records = credf.readlines()
                credf.close()
        except IOError as e:
            msg = "Could not read from {}\n{}".format(options.file_credentials, str(e))
            print(msg)
            sys.exit()
        
        return_record = None
        this_timestamp = None
        prev_timestamp = None
        for crec in cred_records:
            return_record = json.loads(crec)
            for key, data in return_record.items():
                this_timestamp = data['date']
                if key == tag_creds and\
                (prev_timestamp is None or this_timestamp >= prev_timestamp):
                    return_record = json.loads(crec)
            prev_timestamp = this_timestamp

        for key, data in return_record.items():
            return (data['uid'].encode(), data['pwd'].encode(), data['encrypt_tag'], json.dumps(return_record))

        if return_record is None:
            msg = 'No credentials record found'
            print(msg)
            sys.exit()
            