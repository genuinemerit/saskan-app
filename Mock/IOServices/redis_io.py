#!/usr/bin/python3.9
"""
:module:    redis_io.py

Mockup for handling core Redis functions.
These would be used mainly by IOServices::redis_response.

Store data in Redis a compressed (zlib) strings --> bytes.
The data should be validated as a well-formed Avro record.
Redis data is NOT stored in the Avro binary format.
The Redis key = the "name" of the Avro record.

Main behaviors:
- Connect to a Redis namespace (SELECT)
- Name a Redis namespace (CLIENT SETNAME)
- Write:
    - A new key (SET k v nx)
    - Update value of existing key (SET k v xx)
    - with an expiration
        - ex secs, px msecs, exat timestamp, pxat timestamp
    - and return previous value (from update, strings only.. SET k v get)
    - and return time to live (SET k v keepttl)
- Read:
    - By key (GET k, MGET k1 k2 k3)
- Hash structures:
    - Does this key exist yet? (EXIST)
    - Add some key:values for this hash
        - (HSET hashitemkey valuekey value)
        - (HMSET hashitemkey valuekey1 value1 valuekey2 value2)
    - Show me all the stuff in this hash item (HGETALL hashitemkey)
- Set structures
- List structures
- String stuff

Prefer "spine-case" for naming templates, schemas, messages, keys, variables.

Type 	Commands

Sets 	SADD, SCARD, SDIFF, SDIFFSTORE, SINTER, SINTERSTORE, SISMEMBER,
        SMEMBERS, SMOVE, SPOP, SRANDMEMBER, SREM, SSCAN, SUNION, SUNIONSTORE

Hashes 	HDEL, HEXISTS, HGET, HGETALL, HINCRBY, HINCRBYFLOAT, HKEYS, HLEN,
        HMGET, HMSET, HSCAN, HSET, HSETNX, HSTRLEN, HVALS
Lists 	BLPOP, BRPOP, BRPOPLPUSH, LINDEX, LINSERT, LLEN, LPOP, LPUSH, LPUSHX,
        LRANGE, LREM, LSET, LTRIM, RPOP, RPOPLPUSH, RPUSH, RPUSHX

Strings 	APPEND, BITCOUNT, BITFIELD, BITOP, BITPOS, DECR, DECRBY, GET,
            GETBIT, GETRANGE, GETSET, INCR, INCRBY, INCRBYFLOAT, MGET, MSET,
            MSETNX, PSETEX, SET, SETBIT, SETEX, SETNX, SETRANGE, STRLEN
"""
from collections import namedtuple
from dataclasses import dataclass
from pprint import pprint as pp  # noqa: F401

import copy
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
        except KeyError as err:
            print(err)
        return True

    def get_hash(self,
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

    def get_schema_hash(self, p_schema: dict) -> str:
        """Return schema hash as string"""
        h_schema = copy.copy(p_schema)
        _ = h_schema.pop("hash", None)
        _ = h_schema.pop("token", None)
        _ = h_schema.pop("update_ts", None)
        _ = h_schema.pop("version", None)
        return self.get_hash(json.dumps(h_schema))

    def add_schema(self: object,
                   p_topic: str,
                   p_ty: str = "topic",
                   p_verb: str = "get",
                   p_act: str = "request",
                   p_doc: str = "",
                   p_fields: list = []) -> tuple:
        """Write new template to Redis SCHEMA database.

        :args:
            p_topic (str) may be hiearchical, with levels separated by colons
            p_ty (str): in sch_ty
            p_verb (str) in sch_verb
            p_act (str) in sch_act
            p_doc (str) URI to a document describing the schema
            fields (list) of dicts where
                keys - strings identifying field names and
                values - strings in field_ty
        :returns:
            named tuple: ("name token")

        Assign type, name, namespace, alias based on verified arguments.
        Assign topic, version, token.
        Assemble the Avro object.
        Write to Redis. The Redis key is the Avro name (sch_nm).
        """

        def init_new_template() -> dict:
            new_templ: dict = self.avro_templ           # type: ignore
            topic: str = self.make_snake_case(p_topic)  # type: ignore
            sch_nm: str = p_ty + "." + topic + "." + p_verb + "." + p_act
            new_templ: dict = self.avro_templ           # type: ignore
            new_templ["aliases"] = ["queue:" + sch_nm]
            new_templ["doc"] = p_doc
            new_templ["name"] = sch_nm
            new_templ["namespace"] = "net.genuinemerit.schema"
            for f in p_fields:
                for k, v in f.items():
                    field = {"name": self.make_snake_case(k),   # type: ignore
                             "type": v}
                new_templ["fields"].append(field)
            return new_templ

        def get_existing_schema(new_templ: dict) -> dict:
            old_templ = dict()
            t_nm: str = new_templ["name"]
            if self.RNS["schema"].exists(t_nm):        # type: ignore
                schema = self.RNS["schema"].get(t_nm)  # type: ignore
                old_templ =\
                    ASD.convert_avro_json_zip_to_py_dict(
                        avro_json_zip=schema)
            return old_templ

        # ============ add_schema() main ============

        r_keys = namedtuple("r_keys", "name token")
        r_keys.name = ""
        r_keys.token = ""
        schema: object = None
        if self.verify_verbs_types(p_ty,                        # type: ignore
                                   p_verb, p_act, p_fields):
            new_templ = init_new_template()
            old_templ = get_existing_schema(new_templ)
            nt_hash = self.get_schema_hash(p_schema=new_templ)  # type: ignore
            ot_hash = self.get_schema_hash(p_schema=old_templ)  # type: ignore
            if nt_hash == ot_hash:
                # No change detected. Return existing record.
                print("No change.")
                r_keys.name = old_templ["name"]
                r_keys.token = old_templ["token"]
            else:
                if len(old_templ) > 0:
                    print("Need to do an update.")
                    # Change detected. Update existing record.
                    template = old_templ
                else:
                    # Write new record.
                    print("Write new record.")
                    template = new_templ
                    template["version"] = "1.0.0"
                template["hash"] = nt_hash
                template["token"] = BowRedis.get_token()
                template["update_ts"] = BowRedis.get_timestamp()
                schema =\
                    ASD.convert_py_dict_to_avro_json_zip(
                        avro_dict=template)
                r_keys.name = template["name"]
                r_keys.token = template["token"]
                # Do an update if needed instead of a write.
                # >> do an increment version function here
                # Consider how to log/archive the old version.
                self.RNS["schema"].set(                  # type: ignore
                    new_templ["name"], schema, nx=True)
            pp(("r_keys: ", (r_keys.name, r_keys.token)))
        return (r_keys.name, r_keys.token)               # type: ignore


if __name__ == "__main__":
    red = BowRedis()
    red.add_schema(p_topic="(#MY:Test_Topic.$Number**%ONE,+",
                   p_ty="topic")
    red.add_schema(p_topic="ontology_file",
                   p_ty="topic",
                   p_fields=[{"something": "string"}])
    red.add_schema(p_topic="ontology_file",
                   p_ty="sqlite",
                   p_verb="put",
                   p_act="response",
                   p_doc="https://github.com/genuinemerit/bow-wiki/wiki")
    # red.add_schema(p_topic="test_topic", p_ty="junk",
    #                         p_verb="junk", p_act="junk")
