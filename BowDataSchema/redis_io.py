#!/usr/bin/python3.9
"""
:module:    redis_io.py
:class:     RedisIO

Handle core Redis IO functions.

At this point, redis_io.py is kind of the stand-in for the
Message Translator pattern / "bow_schema.py" design.  What I really
want is two things:
- redis-io should be like a layer on top of saskan_fileio, handling
    similar abstractions (io functions) but for redis instead of files.
- the saskan_fileio module has status-file-checking methods that
  should probably be moved to redis_io.  Storing "flag files" as redis
  records seems like maybe a good idea. Perhaps repurpose the Sandbox
  namespace for Primitives and State Flags?

- "bow_schema" should more specifically be about providing the
    right template to use for specific message types, and verifying
    that a message structure is legit.  It would be calling redis-io
    to do IO against DB 1/Schema DB.

Also, keep in mind that I will need some "bootstrap" capabilities.
In other words, I have to be able to write to a Redis DB directly,
or based on some hard-coded rules, in order to create primitives and
templates in the first place.

Redis Basement should replace "saskan_texts.py".

So I need like a "dev" mode and and "app" mode for upserts.

Nevertheless, would be good idea to go ahead and define a "bow_schema"
class that would be used to validate the structures, at least have a
placeholder for where that kind of logic goes..

Store data in Redis using compressed (zlib) strings --> bytes.
- Data should be validated as a well-formed Avro-style record,
  but using my own validation function. ==> in bow_schema.py
- Redis data is NOT stored in the Avro binary format, just compressed.
  - May eventually want to encrypt as well. Keep in mind it has to
    be decrypted before it can be used. And the encrypted format has to
    be string-friendly. What does that mean? Do we have to do a Base64
    encoding after encypting, before decrypting?

- Redis key = usually the "name" field on the Avro-type record.
    - key format: BoW Store Type + Topic + Message + Plan + Service
    - See design doc: Messages-DataSchemaEvents.md
    - Example: "redis.io_services.ontology_file.get.request"
- Redis value = the Avro-ish record as a bytes string.
- Sandbox (0) namespace --> for testing and prototyping
- Schema (1) namespace  --> store schemas for each message type
- Harvest (2) namespace --> store response payloads for specific messages
- Log (3) namespace     --> store log messages, experiment with Redis streams
- Monitor (4) namespace --> store monitor messages, may also want to use
                            streams here

Main behaviors:

Redis commands: https://redis.io/commands

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

@DEV:
- These are generic functions. May want to consider combining with others?
- Or not.
"""
import datetime
import hashlib
import json
import redis
import secrets
import uuid
import zlib
from copy import copy
from pprint import pprint as pp  # noqa: F401


class RedisIOUtils(object):
    """Helper functions"""

    @classmethod
    def get_token(cls) -> str:
        """Generate a cryptographically strong unique ID"""
        return (str(uuid.UUID(bytes=secrets.token_bytes(16)).hex) +
                str(uuid.UUID(bytes=secrets.token_bytes(16)).hex))

    @classmethod
    def get_timestamp(cls) -> str:
        """Return current timestamp w/ microseconds in ISO format as string"""
        return datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc).isoformat()

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

    @classmethod
    def bump_version(cls,
                     p_ver: str,
                     p_bump: str) -> str:
        """Return version string with specified counter bumped.

        :Args:
            p_ver: str - Current version string
            p_bump: str - Counter to bump

        If current_version = 1.1.1, then
        - bump_version(p_ver, "major") -> 2.0.0
        - bump_version(p_ver, "minor") -> 1.2.0
        - bump_version(p_ver, "fix") -> 1.1.2
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
        return ".".join(r_ver)

    def convert_to_spine(self, p_str: str) -> str:
        """Convert string p_str to spine case."""
        r_str = p_str
        r_str = self.bump_char_to_underbar(r_str)
        r_str = self.make_lower_spine(r_str)
        r_str = self.bump_stray_underbars(r_str)
        return r_str

    def compute_hash(self,
                     p_data_in: str) -> str:
        """Create hash of input string, returning UTF-8 hex-string.
           Use SHA-512 by default.

        Args:
            p_data_in (string): data to be hashed

        Returns:
            string: UTF-8-encoded hash of input argument
        """
        v_hash = hashlib.sha512()
        v_hash.update(p_data_in.encode("utf-8"))
        return v_hash.hexdigest()

    def convert_dict_to_bytes(self, msg_d: dict) -> object:
        """Convert Python dict to compressed JSON bytes."""
        msg_j: str = json.dumps(msg_d)
        return zlib.compress(bytes(msg_j, 'utf-8'))

    def convert_bytes_to_dict(self, msg_jzby: bytes) -> dict:
        """Convert compressed JSON bytes to Python dict."""
        msg_j = zlib.decompress(msg_jzby)
        return json.loads(msg_j)


class RedisIO(object):
    """Generic Redis handling."""

    # Summary, admin, state and log queries (DBA type functions)
    # =========================================================================
    def __init__(self):
        """Initialize Redis connections."""
        self.UT = RedisIOUtils()
        self.HOST = '127.0.0.1'
        self.PORT = 6379
        self.RNS = dict()  # associate DB names to Namespaces, connections
        for db_no, db_nm in enumerate(
                ["basement", "schema", "harvest", "log", "monitor"]):
            self.RNS[db_nm] = redis.Redis(
                host=self.HOST, port=self.PORT, db=db_no)
            self.RNS[db_nm].client_setname(db_nm)

    def list_dbs(self) -> str:
        """Return number and name of the Redis namespaces (DB's).

        List keys available in each DB. <-- make this a separate function
        """
        result = f"Redis Connections  Host: {self.HOST}  Port: {self.PORT}\n"
        for db_no, db_nm in enumerate(self.RNS.keys()):
            if db_no > 0:
                result += f"\nDB #{str(db_no)}: {db_nm}\n"
                result += f"Keys: {str(self.RNS[db_nm].get('KEYS *'))}\n"
        return result

    # Primitive, state, template set-up functions (DDL type functions)
    # =========================================================================

    # Basic, fundamental, helper functions
    # =======================================

    # Add function to count number of records with requested key, but not
    #  return anything.

    def find_records(self,
                     p_db: str,
                     p_key_pattern: str):
        """Return keys of records that match search pattern.

        This is a Redis KEYS function.

        :args:
            p_db: str - name of DB to search
            p_key_pattern: str - search criteria
        :returns:
            dict: records if found, else None
        """
        result = None
        # print(f"Looking for keys like {p_key_pattern} on db {p_db}")
        result = self.RNS[p_db].keys(p_key_pattern)
        return result

    def get_record(self,
                   p_db: str,
                   p_key_val: str):
        """Return existing record if one exists for a specified key.

        This is a Redis GET function.

        :args:
            p_db: str - name of DB to search
            p_key_val: str - key to search for
        :returns:
            dict: records if found, else None
        """
        rec = None
        if self.RNS[p_db].exists(p_key_val):               # type: ignore
            redis_result = self.RNS[p_db].get(p_key_val)
            rec = self.UT.convert_bytes_to_dict(redis_result)
        return rec

    def hash_record(self, p_rec: dict) -> str:
        """Return hash of JSON record, excluding audit fields.

        @DEV:
        - Get audit fields from template.
        """
        h_schema = copy(p_rec)
        _ = h_schema.pop("hash", None)
        _ = h_schema.pop("token", None)
        _ = h_schema.pop("update_ts", None)
        _ = h_schema.pop("version", None)
        j_schema = json.dumps(h_schema)
        hash_v = self.UT.compute_hash(j_schema)
        return hash_v

    def encrypt_record(self):
        pass

    def decrypt_record(self):
        pass

    def init_record_values(self,
                           p_ns: str,
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
        rec["namespace"] = f"net.genuinemerit.{p_ns}"
        for f in p_fields:
            for k, v in f.items():
                rec["fields"].append(
                    {"name": self.convert_to_spine(k),       # type: ignore
                     "type": v})
        return rec

    # Generic DML-type functions
    # =======================================

    def set_record_values(self,
                          p_new_rec: dict,
                          p_hash: str,
                          p_old_rec: dict) -> dict:
        """Return dict for new or updated record."""
        if len(p_old_rec) == 0:
            rec = copy(p_new_rec)
            rec["version"] = "1.0.0"
        else:
            rec = copy(p_old_rec)
            # Get updated values
            for k, v in p_new_rec.items():
                if v != p_old_rec[k]:
                    rec[k] = copy(v)
            rec["version"] = self.bump_version(       # type: ignore
                    p_old_rec["version"])
        # Set audit values
        rec["hash"] = p_hash
        rec["token"] = self.UT.get_token()
        rec["update_ts"] = self.UT.get_timestamp()
        return rec

    def do_archive(self,
                   p_old_rec: dict) -> None:
        """Archive previous record to `log` namespace."""
        arc_key = p_old_rec["name"] +\
            ".archive." + self.get_timestamp()   # type: ignore
        arc_schema = self.UT.convert_dict_to_bytes(
            msg_d=p_old_rec)
        self.RNS["log"].set(                     # type: ignore
            arc_key, arc_schema, nx=True)

    def do_upsert(self,
                  p_ns: str,
                  p_upsert: str,
                  p_rec: dict,
                  p_old_rec: dict):
        """Either update (xx) or write (nx) a record to Redis"""
        if p_upsert == "xx":
            self.do_archive(p_old_rec)      # type: ignore
            self.RNS[p_ns].set(p_rec["name"],       # type: ignore
                               self.UT.convert_dict_to_bytes(
                                   msg_d=p_rec), xx=True)
        elif p_upsert == "nx":
            try:
                self.RNS[p_ns].set(
                    p_rec["name"],
                    self.UT.convert_dict_to_bytes(
                        msg_d=p_rec), nx=True)
            except redis.exceptions.ResponseError as e:
                print(f"\nRedis error: {e}")
                print(f"\nRecord: {p_rec}")
                print(f"\nRecord name: {p_rec['name']}")
                print(f"\nRecord namespace: {p_ns}")
                raise e

    # Bespoke DML-type functions
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

    # Probably need lots of refactoring for these functions....
    # =================================================
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
