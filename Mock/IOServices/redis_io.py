#!/usr/bin/python3.9
"""
:module:    redis_io.py

Mockup for handling core Redis functions.
To be used mainly by IOServices::redis_response.

Store data in Redis a compressed (zlib) strings --> bytes.
- Data should be validated as a well-formed Avro record.
- Redis data is NOT stored in the Avro binary format.
- Redis key = usually the "name" field on the Avro record.

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
    - By keys (KEYS pattern)
    - Does this specific key exist yet? (EXIST)
    - Show me all the stuff in this hash item (HGETALL hashitemkey)

Redis commands: https://redis.io/commands

"""
from copy import copy
from dataclasses import dataclass
from pprint import pprint as pp  # noqa: F401

import datetime
import hashlib
import json
import redis
import secrets
import uuid

from avro_serde import AvroSerDe  # type: ignore

ASD = AvroSerDe()


class BowRedis(object):
    """Generic Redis handling."""

    def __init__(self):
        """Initialize Redis connections."""
        self.set_constants()
        self.RNS = dict()
        for db_no, db_nm in enumerate(["sandbox", "schema", "result", "log"]):
            self.RNS[db_nm] = redis.Redis(
                host=self.HOST, port=self.PORT, db=db_no)
            self.RNS[db_nm].client_setname(db_nm)

    def set_constants(self):
        """Set class constants."""
        self.HOST = '127.0.0.1'
        self.PORT = 6379
        self.field_ty: list = ["array", "hash", "set", "string"]
        self.sch_act: list = ["list", "publish", "subscribe",
                              "request", "response"]
        self.sch_ty: list = ["owl", "redis", "sqlite", "topic"]
        self.sch_verb: list = ["auth", "decr", "get", "incr",
                               "meta", "put", "remove", "update"]
        self.avro_templ: dict = {
            "aliases": [], "doc": "", "fields": [], "hash": "",
            "name": "", "namespace": "", "token": "",
            "type": "record", "update_ts": "", "version": ""}

    @dataclass
    class HashLevel:
        """Define valid hashing levels."""

        SHA512: int = 128
        SHA256: int = 64
        SHA224: int = 56
        SHA1: int = 40

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
    def bump_restricted_chars(cls, p_str: str) -> str:
        """Return string with URI-restricted chars changed to underbars

        Convert reserved characters...
            : / ? # [ ] @ ! $ & ' * + , ; =
        ...and a few others that can cause hiccups with JSON or Avro...
            - & ( ) ` € " " (space) \\
        ... to underbars. Then:
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
    def make_lower(cls, p_str: str) -> str:
        """Return string with uppers bumped to lowers

        And some additional hyphenating aimed at converting camel to spine

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
    def bump_underbars(cls, p_str: str) -> str:
        """Return string stray underbars removed

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
                     major: bool = False,
                     minor: bool = True,
                     fix: bool = False) -> str:
        """Return version string with counter bumped."""
        r_ver = p_ver.split(".")
        r_ver[0] = str(int(r_ver[0]) + 1) if major else r_ver[0]
        r_ver[1] = str(int(r_ver[1]) + 1) if minor else r_ver[1]
        r_ver[2] = str(int(r_ver[2]) + 1) if fix else r_ver[2]
        return ".".join(r_ver)

    def make_snake_case(self, p_str: str) -> str:
        """Convert string to spine case."""
        r_str = p_str
        r_str = BowRedis.bump_restricted_chars(r_str)
        r_str = BowRedis.make_lower(r_str)
        r_str = BowRedis.bump_underbars(r_str)
        return r_str

    def verify_verbs_types(self, p_ty: str, p_verb: str,
                           p_act: str, p_fields: list) -> bool:
        msg = ""
        if p_ty not in self.sch_ty:
            msg += f"\nType must be in {str(self.sch_ty)}"
        if p_verb not in self.sch_verb:
            msg += f"\nVerb must be in {str(self.sch_verb)}"
        if p_act not in self.sch_act:
            msg += f"\nAct must be in {str(self.sch_act)}"
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

    def compute_hash(self,
                     p_data_in: str,
                     p_len: int = HashLevel.SHA256) -> str:
        """Create hash of input string, returning UTF-8 hex-string.

        - 128-byte hash uses SHA512
        - 64-byte hash uses SHA256
        - 56-byte hash uses SHA224
        - 40-byte hash uses SHA1

        Args:
            p_data_in (string): data to be hashed
            p_len (int): optional hash length, default is SHA256

        Returns:
            string: UTF-8-encoded hash of input argument
        """
        v_hash = hashlib.sha512() if p_len == self.HashLevel.SHA512\
            else hashlib.sha224() if p_len == self.HashLevel.SHA224\
            else hashlib.sha1() if p_len == self.HashLevel.SHA1\
            else hashlib.sha256()
        v_hash.update(p_data_in.encode("utf-8"))
        return v_hash.hexdigest()

    def get_record_hash(self, p_rec: dict) -> str:
        """Return hash of JSON record."""
        h_schema = copy(p_rec)
        _ = h_schema.pop("hash", None)
        _ = h_schema.pop("token", None)
        _ = h_schema.pop("update_ts", None)
        _ = h_schema.pop("version", None)
        j_schema = json.dumps(h_schema)
        hash_v = self.compute_hash(j_schema, self.HashLevel.SHA256)
        return hash_v

    def init_new_record(self,
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
        s_topic: str = self.make_snake_case(p_topic)        # type: ignore
        sch_nm: str = p_ty + "." + s_topic + "." + p_verb + "." + p_act
        rec["aliases"] = ["queue/" + sch_nm]
        rec["doc"] = p_doc
        rec["name"] = sch_nm
        rec["namespace"] = f"net.genuinemerit.{p_ns}"
        for f in p_fields:
            for k, v in f.items():
                rec["fields"].append(
                    {"name": self.make_snake_case(k),       # type: ignore
                     "type": v})
        return rec

    def get_existing_record(self,
                            p_nm: str) -> dict:
        """Return existing record if one exists for specified key."""
        rec = dict()
        if self.RNS["schema"].exists(p_nm):               # type: ignore
            rec = ASD.convert_avro_jzby_to_py_dict(
                avro_jzby=self.RNS["schema"].get(p_nm))   # type: ignore
        return rec

    def set_upserted_record(self,
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
        rec["token"] = BowRedis.get_token()
        rec["update_ts"] = BowRedis.get_timestamp()
        return rec

    def archive_old_record(self,
                           p_old_rec: dict) -> None:
        """Archive previous record to `log` namespace."""
        arc_key = p_old_rec["name"] +\
            ".archive." + self.get_timestamp()   # type: ignore
        arc_schema = ASD.convert_py_dict_to_avro_jzby(
            avro_d=p_old_rec)
        self.RNS["log"].set(                     # type: ignore
            arc_key, arc_schema, nx=True)

    def upsert_redis_record(self,
                            p_ns: str,
                            p_upsert: str,
                            p_rec: dict,
                            p_old_rec: dict):
        """Either update (xx) or write (nx) a record to Redis"""
        if p_upsert == "xx":
            print("\nArchive and update record:")
            self.archive_old_record(p_old_rec)      # type: ignore
            self.RNS[p_ns].set(p_rec["name"],       # type: ignore
                               ASD.convert_py_dict_to_avro_jzby(
                                   avro_d=p_rec), xx=True)
        elif p_upsert == "nx":
            print("\nWrite new record:")
            self.RNS[p_ns].set(p_rec["name"],       # type: ignore
                               ASD.convert_py_dict_to_avro_jzby(
                                   avro_d=p_rec), nx=True)

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
            p_ty (str): in sch_ty
            p_verb (str) in sch_verb
            p_act (str) in sch_act
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
        # ============ upsert_schema() main ============
        if self.verify_verbs_types(                             # type: ignore
                p_ty, p_verb, p_act, p_fields):
            new_rec = self.init_new_record(                     # type: ignore
                "schema", p_ty, p_topic, p_verb, p_act, p_doc, p_fields)
            old_rec = self.get_existing_record(new_rec["name"])  # type: ignore
            nt_hash = self.get_record_hash(new_rec)              # type: ignore
            ot_hash = self.get_record_hash(old_rec)              # type: ignore
            up_rec = self.set_upserted_record(                   # type: ignore
                    new_rec, nt_hash, old_rec)
            if nt_hash == ot_hash:
                print("\nNo change: ")
                up_rec = old_rec
            else:
                # xx = update, nx = write
                upsert = "xx" if len(old_rec) > 0 else "nx"
                self.upsert_redis_record(                      # type: ignore
                    "schema", upsert, up_rec, old_rec)
            # For debugging:
            rec = self.get_existing_record(up_rec["name"])     # type: ignore
            pp(("rec", rec))
        return (up_rec["name"], up_rec["token"])               # type: ignore


if __name__ == "__main__":
    red = BowRedis()
    red.upsert_schema(p_topic="(#MY:Test_Topic.$Number**%THREE,+",
                      p_ty="redis",
                      p_fields=[{"lang": "string"}])
    red.upsert_schema(p_topic="ontology_file",
                      p_ty="owl",
                      p_fields=[{"something_new": "string"},
                                {"something_old": "string"},
                                {"something_borrowed": "string"}])
    red.upsert_schema(p_topic="ontology_file",
                      p_ty="sqlite",
                      p_verb="auth",
                      p_act="subscribe",
                      p_doc="https://github.com/genuinemerit/bow-wiki/wiki")
    # red.upsert_schema(p_topic="test_topic", p_ty="junk",
    #                         p_verb="junk", p_act="junk")
