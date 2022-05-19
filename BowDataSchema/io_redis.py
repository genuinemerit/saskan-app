#!python
"""
:module:    io_redis.py
:class:     RedisIO

Handle core Redis IO functions.

- Data is stored in Redis using compressed (zlib) strings --> bytes.
  - May want to encrypt also, but worry about that later.
- All record content should be validated before being stored.
- Use a simplified bespoke version of Avro syntax:
  - "name" = record key
  - the rest of the record is a dictionary of name/value pairs
  - all records use the same set of audit value pairs

- Basement (0) namespace --> config and state data
- Schema (1) namespace   --> message type schemas
- Harvest (2) namespace  --> response payloads for specific messages
- Log (3) namespace      --> log messages; maybe use Redis streams
- Monitor (4) namespace  --> monitoring messages

Redis commands: https://redis.io/commands

@DEV:
- redis-io is like a layer on top of saskan_fileio, handling
    similar abstractions (io functions) but for redis instead of files.

- saskan_fileio module has status-file-checking methods that
    should probably be moved to io_redis.  Store "flag files" in redis.

- Redis Basement should also replace "saskan_texts.py".

- FLUSHDB -- delete all keys in current namespace
- FLUSHALL -- delete all keys in all namespaces


Main behaviors:

- Administer Redis database.
    - Connect to a Redis namespace (SELECT)
    - Name a Redis namespace (CLIENT SETNAME)
    - Wipe a Redis namespace (FLUSHDB)

- Write/Update:
    - A new key (SET k v nx)
    - Update value of existing key (SET k v xx)
    - with an expiration
        - ex secs, px msecs, exat timestamp, pxat timestamp
    - and return previous value (from update, strings only.. SET k v get)
    - and return time to live (SET k v keepttl)
    - Add some key:values for this hash
        - (HSET hashitemkey valuekey value)
        - (HMSET hashitemkey valuekey1 value1 valuekey2 value2)

- Read:
    - By key (GET k, MGET k1 k2 k3)
    - By keys (KEYS pattern), e.g. `KEYS *` --> show all keys
    - Does this specific key exist yet? (EXIST)
    - Show me all the stuff in this hash item (HGETALL hashitemkey)

- Expire:
    - Set expire for key (EXPIRE k secs) in seconds from now
    - Set expire for key (PEXPIRE k msecs) in milliseconds from now
    - Set expire for key (EXPIREAT k timestamp) at (standard) Unix timestamp
        in seconds
    - Set expire for key (PEXPIREAT k timestamp) at Unix timestamp
        in milliseconds
    - Get the expire time for a key
        - In seconds from now (TTL k) <-- works
        - In milliseconds from now (PTTL k) <-- works
        - As a Unix timestamp (EXPIRETIME k) <-- does not seem to work
"""
import datetime
import hashlib
import json
import redis  # type: ignore
import secrets
import uuid
import zlib

from copy import copy
from pprint import pprint as pp  # noqa: F401

from io_config import ConfigIO

CI = ConfigIO()


class RedisIO(object):
    """Generic Redis handling."""

    def __init__(self):
        """Initialize Redis connections."""
        self.HOST = '127.0.0.1'
        self.PORT = 6379
        self.RNS = dict()  # associate DB names to Namespaces, connections
        for db_no, db_nm in enumerate(
                ["basement", "schema", "harvest", "log", "monitor"]):
            self.RNS[db_nm] = redis.Redis(
                host=self.HOST, port=self.PORT, db=db_no)
            self.RNS[db_nm].client_setname(db_nm)

    # Helper functions
    # =========================================================================
    @classmethod
    def convert_dict_to_bytes(self,
                              p_msg: dict) -> object:
        """Convert Python dict to compressed JSON bytes."""
        msg_json: str = json.dumps(p_msg)
        return zlib.compress(bytes(msg_json, 'utf-8'))

    @classmethod
    def convert_bytes_to_dict(self,
                              p_msg: bytes) -> dict:
        """Convert compressed JSON bytes to Python dict."""
        msg_dict = zlib.decompress(p_msg)
        return json.loads(msg_dict)

    @classmethod
    def get_hash(cls,
                 p_data_in: str) -> str:
        """Create hash of input string, returning UTF-8 hex-string.
           Use SHA-512 by default.
        """
        v_hash = hashlib.sha512()
        v_hash.update(p_data_in.encode("utf-8"))
        return v_hash.hexdigest()

    @classmethod
    def get_timestamp(cls) -> str:
        """Return current timestamp w/ microseconds in ISO format as string"""
        ts = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc).isoformat()
        return ts

    @classmethod
    def set_version(cls,
                    p_ver: str,
                    p_bump: str) -> str:
        """Return version string with specified counter bumped.

        :Args:
            p_ver: str - Current version string
            p_bump: str - Counter to bump

        If current_version = 1.1.1, then
        - set_version(p_ver, "major") -> 2.0.0
        - set_version(p_ver, "minor") -> 1.2.0
        - set_version(p_ver, "fix") -> 1.1.2
        """
        r_ver = p_ver.split(".")
        if p_bump == "major":
            r_ver[0] = str(int(r_ver[0]) + 1)
            r_ver[1] = "0"
            r_ver[2] = "0"
        elif p_bump == "minor":
            r_ver[1] = str(int(r_ver[1]) + 1)
        elif p_bump == "fix":
            r_ver[2] = str(int(r_ver[2]) + 1)
        m_ver = r_ver[0] + "." + r_ver[1] + "." + r_ver[2]
        return m_ver

    @classmethod
    def get_token(cls) -> str:
        """Generate a cryptographically strong unique ID.

        Move this elsewhere? e.g., editor & service-responses.
        Use it to auto-generate a key for Harvest db records.
        """
        return (str(uuid.UUID(bytes=secrets.token_bytes(16)).hex) +
                str(uuid.UUID(bytes=secrets.token_bytes(16)).hex))

    @classmethod
    def bump_underbars(cls, text) -> str:
        """Remove stray underbars

        - Remove leading or trailing underbars
        - Reduce multiple underbars to single underbars
        """
        r_str = text
        while "__" in r_str:
            r_str = r_str.replace("__", "_")
        while r_str[-1:] == "_":
            r_str = r_str[:-1]
        while r_str[:1] == "_":
            r_str = r_str[1:]
        return r_str

    def clean_redis_key(self, text: str):
        """Convert anything not a letter or colon to underbar.
        And make it lowercase.
        """
        r_str = text
        for char in r_str:
            if not char.isalpha() and \
               not char.isdigit() and \
               not char == ":":
                r_str = r_str.replace(char, "_")
        return self.bump_underbars(r_str).lower()

    # Generic DBA functions
    # =========================================================================
    def list_dbs(self) -> str:
        """Return number and name of the Redis namespaces (DB's).

        List all keys available in each DB. <-- make this a separate function
        """
        result = f"Redis Connections  Host: {self.HOST}  Port: {self.PORT}\n"
        for db_no, db_nm in enumerate(self.RNS.keys()):
            result += f"\nDB #{str(db_no)}: {db_nm}\n"
        return result

    def list_all_keys(self,
                      p_db_nm: str) -> list:
        """List all keys available in specified DB."""
        return self.RNS[p_db_nm].get('KEYS *')

    # Generic DDL functions
    # =========================================================================
    def find_keys(self,
                  p_db: str,
                  p_key_pattern: str):
        """Return keys of records that match search pattern."""
        return self.RNS[p_db].keys(p_key_pattern)

    def count_keys(self,
                   p_db: str,
                   p_key_pattern: str):
        """Return number of keys that match search pattern."""
        keys = self.find_keys(p_db, p_key_pattern)
        return len(keys)

    def get_record(self,
                   p_db: str,
                   p_key_val: str):
        """Return existing record if one exists for a specified key.

        :Args:
        - p_db (str) name of the Redis namespace
        - p_key_val (str) key value of the record to retrieve
        :Returns:
        - rec (dict) - record data

        @DEV:
        - Q: Can this function return more than one record? In other
             words, can I pass in a Redis "wildcard" key?
        """
        rec = None
        if self.RNS[p_db].exists(p_key_val):               # type: ignore
            redis_result = self.RNS[p_db].get(p_key_val)
            rec = self.convert_bytes_to_dict(redis_result)
        return rec

    def get_values(self, record):
        """Return only the values of a record."""
        record.pop("name")
        record.pop("audit")
        return record

    # Generic DML functions
    # =======================================
    # TODO - add a "get_expire_time" function

    def set_audit_values(self,
                         p_db: str,
                         p_data_rec: dict,
                         p_include_hash: bool = True) -> tuple:
        """Set audit values for a record.

        :args:
            p_data_rec: dict - Record to set audit values for
            p_include_hash: bool - Include hash of record in audit values

        :returns: (
            dict - record with audit values set or modified,
            bool - indicates whether to do update (True) or insert (False))
        """
        data_rec = p_data_rec
        r_update = False
        exists = self.get_record(p_db, data_rec["name"])
        if exists is not None and 'audit' in exists:
            audit = exists["audit"]
            audit["version"] = self.set_version(audit["version"], "minor")
            data_rec["audit"] = audit
            r_update = True
        else:
            audit = {"version": "1.0.0"}
        audit["modified"] = self.get_timestamp()
        if p_include_hash:
            audit["hash"] = self.get_hash(str(data_rec))
        data_rec["audit"] = audit
        return (data_rec, r_update)

    def do_expire(self,
                  p_db: str,
                  p_key: str,
                  p_expire: int = 0):
        """Set expiration seconds for a key."""
        if p_expire > 0:
            expire_secs = p_expire * 60 * 60
            self.RNS[p_db].expire(p_key, expire_secs)

    def do_insert(self,
                  p_db: str,
                  p_rec: dict,
                  p_expire: int = 0):
        """Insert a record to Redis.
           Set its expiration time if specified (> 0).
           The p_expire value is in hours. Translate to seconds.
           For now, not allowing anything other than hours.
           'nx' means overwrite existing key if it exists.
        """
        try:
            values = self.convert_dict_to_bytes(p_rec)
            self.RNS[p_db].set(p_rec["name"], values, nx=True)
        except redis.exceptions.ResponseError as e:
            # Write to log instead of raise exception?
            # But.. have to watch out for catch-22 if log is on Redis! :-)
            print(f"\nRedis error: {e}")
            print(f"\nRecord: {p_rec}")
            print(f"\nRecord name: {p_rec['name']}")
            print(f"\nRecord namespace/db: {p_db}")
            raise e
        self.do_expire(p_db, p_rec["name"], p_expire)

    def do_archive(self,
                   p_rec: dict):
        """Copy/archive record to `log` namespace."""
        log_rec = p_rec
        log_rec["name"] = "archive:" + p_rec["name"] + \
            ":" + self.get_timestamp()
        self.do_insert("log", log_rec)

    def do_update(self,
                  p_db: str,
                  p_rec: dict,
                  p_expire: int = 0):
        """Update a record on Redis"""
        old_rec = self.get_record(p_db, p_rec["name"])
        self.do_archive(old_rec)
        try:
            values = self.convert_dict_to_bytes(p_rec)
            self.RNS[p_db].set(p_rec["name"], values, xx=True)
        except redis.exceptions.ResponseError as e:
            # Write to log instead of raise exception
            print(f"\nRedis error: {e}")
            print(f"\nRecord: {p_rec}")
            print(f"\nRecord name: {p_rec['name']}")
            print(f"\nRecord namespace/db: {p_db}")
            raise e
        self.do_expire(p_db, p_rec["name"], p_expire)

    # Bespoke DML-type functions
    # =======================================

    def write_redis_config(self,
                           p_name: str,
                           p_value: str,
                           p_write_msg: bool = False):
        """Write config record to Redis Namespace 0 'Basement'
        - Write full path of locations to Redis Namespace 0 'Basement'
          as config files.
        - Config records carry a single name:value pair

        :args:
        - p_name (str) - Name of config value
        - p_value (str) - Content of config value
        - p_write_msg (bool) - Write message to console
        """
        db = CI.txt.ns_db_basement
        db_rec, do_update = self.set_audit_values(
            db, {"name": "config:" + p_name, p_name: p_value})
        if do_update:
            self.do_update(db, db_rec)
        else:
            self.do_insert(db, db_rec)
        if p_write_msg:
            print(f"{CI.txt.val_ok} " +
                  f"{CI.txt.ns_db_basement}.{db_rec['name']} " +
                  f"({db_rec['audit']['version']})")

    def write_redis_meta(self,
                         p_data: dict):
        """Set text and widget metadata records on Basement DB.
        :args:
        - p_data (dict) - Name of the metadata record, followed by
                           a collection of name:value pairs.
                          Example: {"window" : {"hint": "some text", ...}}
        """
        db = "basement"
        for k, values in p_data.items():
            key = self.clean_redis_key(f"meta:{k}")
            data_rec = {"name": key} | values
            db_rec, update = \
                self.set_audit_values(db, data_rec, p_include_hash=True)
            if update:
                self.do_update(db, db_rec)
            else:
                self.do_insert(db, db_rec)

    def get_app_path(self):
        """Return full path of the application as a string."""
        rec = self.get_record(CI.txt.ns_db_basement,
                              "config:" + CI.app_path_key)
        app_path = str(rec["app_path"])
        return app_path

    def get_config_value(self,
                         p_config_name: str):
        """Return value associated with the config key."""
        rec = self.get_record(CI.txt.ns_db_basement,
                              "config:" + p_config_name)
        value = str(rec[p_config_name])
        return value

    def get_all_configs(self):
        """Return all config records from Basement"""
        db = "basement"
        keys: list = self.find_keys(db, "config:*")
        data: dict = {}
        for k in keys:
            key = k.decode('utf-8').replace("config:", "")
            record = self.get_values(self.get_record(db, k))
            data[key] = record
        return(data)

    def get_all_gui_meta(self):
        """Return all GUI metadata records from Basement"""
        db = "basement"
        keys: list = self.find_keys(db, "meta:*")
        data: dict = {}
        for k in keys:
            key = k.decode('utf-8').replace("meta:", "")
            record = self.get_values(self.get_record(db, k))
            data[key] = record
        return(data)

    # Other possibly bespoke DML-type functions
    # =======================================

    # create_prim()
    # get_prim()
    # set_prim()
        # texts
        # en_*
        # config_*
        # directories
        # app_path
        # app_dir: str = 'saskan'
        # log_dir: str = 'log'
        # files
        # db_status_file: str = 'db_status'
    # create_state_flag()
    # get_state_flag()
    # set_state_flag()
    # create_template()
    # get_template()
    # set_template()
    # set_expiration_rule()
    # query_expiration_rule()
    # query_basement()
    # query_schema()
    # query_harvest()
    # query_monitor()
    # query_log()
    # upsert_basement()
    # upsert_schema()
    # upsert_harvest()
    # upsert_monitor()
    # upsert_log()

    # Need refactoring or more likely obsolete / not needed..
    # =================================================

    def modify_meta(self,
                    p_wdg_catg: str,
                    p_qt_wdg):
        """Update Basement DB with modified widget record.

        - Probably obsolete.
        - Qt prototype saved a copy of or name of instantiated
          widget object with the metadata.
        - If something like this is needed, maybe better to
          have a caching area rather than modifying the Basement.
        """
        db = "basement"
        self.WDG[p_wdg_catg]["w"]["name"] = p_qt_wdg.objectName()
        record = {"basement":
                  {"name": f"widget:{p_wdg_catg}"} | self.WDG[p_wdg_catg]}
        record, _ = \
            self.set_audit_values(record, p_include_hash=True)
        self.do_update(db, record)
        self.WDG[p_wdg_catg]["w"]["object"] = p_qt_wdg

    def set_record_values(self,
                          p_new_rec: dict,
                          p_hash: str,
                          p_rec: dict) -> dict:
        """Return dict for new or updated record."""
        if len(p_rec) == 0:
            rec = copy(p_new_rec)
            rec["version"] = "1.0.0"
        else:
            rec = copy(p_rec)
            # Get updated values
            for k, v in p_new_rec.items():
                if v != p_rec[k]:
                    rec[k] = copy(v)
            rec["version"] = self.set_version(       # type: ignore
                    p_rec["version"])
        # Set audit values
        rec["hash"] = p_hash
        rec["token"] = self.get_token()
        rec["update_ts"] = self.get_timestamp()
        return rec

    @classmethod
    def bump_char_to_underbar(cls, p_str: str) -> str:
        """Return string with URI-restricted chars changed to underbars

        Convert reserved characters...
            : / ? # [ ] @ ! $ & ' * + , ; =
        ...and a few others that can cause hiccups with JSON...
            - & ( ) ` € " " (space) \\
        ... to underbars.
        """
        r_str = p_str
        restrict = [":", "/", "\\", "?", "#", "[", "]",
                    "@", "!", "$", "&", "'", "%",
                    "*", "+", ",", ";", "=", "(", ")",
                    "`", '"', "€", " ", "-", "~"]
        for r_char in restrict:
            r_str = r_str.replace(r_char, "_")
        return r_str

    @classmethod
    def make_lower_spine(cls, p_str: str) -> str:
        """Return string with uppers bumped to lowers
        and some additional hyphenating aimed at converting camel to spine.

        Convert all names of everything (*) to spine-case:
        - convert capital letter in char[0] to `lower`
        - convert series of capital letters to `_lowerseries_`
        - convert non-first capital letters to `_lower`
        """
        r_str = p_str
        r_str = r_str[:1].lower() + r_str[1:]
        count_upper = 0
        for rix, rchar in enumerate(r_str):
            if rchar.isupper():
                count_upper += 1
                if count_upper == 2:
                    r_str = r_str[:rix-1] + "_" + r_str[rix-1:] + "_"
            else:
                count_upper = 0
        r_str = r_str.lower()
        return r_str

    @classmethod
    def bump_stray_underbars(cls, p_str: str) -> str:
        """Remove stray underbars

        - Remove leading or trailing underbars
        - Reduce multiple underbars to single underbars

        Dots are NOT converted to underbars but
         still removed if trailing or leading.
        """
        other_char = ["_", "."]
        r_str = p_str
        while "__" in r_str:
            r_str = r_str.replace("__", "_")
        while r_str[-1:] in other_char:
            r_str = r_str[:-1]
        while r_str[:1] in other_char:
            r_str = r_str[1:]
        for ochar in other_char:
            r_str = r_str.replace(ochar + "_", ochar)
            r_str = r_str.replace("_" + ochar, ochar)
        return r_str

    def convert_to_spine(self, p_str: str) -> str:
        """Convert string p_str to spine case."""
        r_str = p_str
        r_str = self.bump_char_to_underbar(r_str)
        r_str = self.make_lower_spine(r_str)
        r_str = self.bump_stray_underbars(r_str)
        return r_str

    def init_record_values(self,
                           p_db: str,
                           p_ty: str,
                           p_topic: str,
                           p_verb: str,
                           p_act: str,
                           p_doc: str,
                           p_fields: list) -> dict:
        """Assemble new record dict."""
        rec: dict = copy(self.avro_templ)                   # type: ignore
        rec["fields"] = list()
        s_topic: str = self.convert_to_spine(p_topic)        # type: ignore
        sch_nm: str = p_ty + "." + s_topic + "." + p_verb + "." + p_act
        rec["aliases"] = []
        rec["doc"] = p_doc
        rec["name"] = sch_nm
        rec["namespace"] = f"net.genuinemerit.{p_db}"
        for f in p_fields:
            for k, v in f.items():
                rec["fields"].append(
                    {"name": self.convert_to_spine(k),       # type: ignore
                     "type": v})
        return rec

    def upsert_schema(self: object,
                      p_topic: str,
                      p_ty: str = "topic",
                      p_verb: str = "get",
                      p_act: str = "request",
                      p_doc: str = "",
                      p_fields: list = []) -> tuple:
        """Upsert record to Redis SCHEMA namespace.

        :args:
            p_topic (str) may be hierarchical, levels separated by dots
            p_ty (str): in msg_cat
            p_verb (str) in msg_plan
            p_act (str) in msg_svc
            p_doc (str) URI to a document describing schema
            fields (list) of singleton dicts where
                key -> string identifying field names
                value -> string in field_ty
        :returns:
            tuple: ("name/key token")

        Assign type, name, namespace, alias based on verified arguments.
        Compute version, token and hash.
        Assemble and verify the Avro object.
        Write to Redis as compressed (zlib) string. Redis key = Avro name.
        """
        if self.verify_verbs_types(                          # type: ignore
                p_ty, p_verb, p_act, p_fields):
            new_rec = self.init_record_values(               # type: ignore
                "schema", p_ty, p_topic, p_verb, p_act, p_doc, p_fields)
            old_rec = self.get_record(new_rec["name"])  # type: ignore
            nt_hash = self.hash_record(new_rec)              # type: ignore
            ot_hash = self.hash_record(old_rec)              # type: ignore
            up_rec = self.set_record_values(                 # type: ignore
                    new_rec, nt_hash, old_rec)
            if nt_hash == ot_hash:
                print("\nNo change: ")
                up_rec = old_rec
            else:
                # xx = update, nx = write
                upsert = "xx" if len(old_rec) > 0 else "nx"
                self.do_upsert(                      # type: ignore
                    "schema", upsert, up_rec, old_rec)
            # For debugging:
            rec = self.get_record(up_rec["name"])     # type: ignore
            pp(("rec", rec))
        return (up_rec["name"], up_rec["token"])               # type: ignore

    def set_constants(self):
        """Set class constants.

        Handle in Redis Basement and Schema.

        @DEV:
        - Get this info from templates stored in Basement or Schema DBs.
        """
        self.field_ty: set = ("array", "hash", "set", "string")
        self.msg_cat: set = ("owl", "redis", "sqlite", "topic")
        self.msg_plan: set = ("get", "put", "remove", "update", "meta")
        self.msg_svc: set = ("publish", "subscribe", "request", "response")
        self.avro_templ: dict = {
            "aliases": [],
            "channel": "",
            "doc": "",
            "fields": [],
            "hash": "",
            "name": "",
            "namespace": "",
            "token": "",
            "type": "record",
            "update_ts": "",
            "version": ""}

    def verify_verbs_types(self, p_ty: str, p_verb: str,
                           p_act: str, p_fields: list) -> bool:
        """Verify verb and fields types against Schema DB templates.
        @DEV:
        - Get this info from templates."""
        msg = ""
        if p_ty not in self.msg_cat:
            msg += f"\nType must be in {str(self.msg_cat)}"
        if p_verb not in self.msg_plan:
            msg += f"\nVerb must be in {str(self.msg_plan)}"
        if p_act not in self.msg_svc:
            msg += f"\nAct must be in {str(self.msg_svc)}"
        for f in p_fields:
            for k, v in f.items():
                if v not in self.field_ty:
                    msg += "\nField type must be in " +\
                                    f"{str(self.field_ty)}"
        try:
            if msg != "":
                raise Exception(KeyError, msg)
                return False
        except KeyError as err:
            print(err)
        return True
