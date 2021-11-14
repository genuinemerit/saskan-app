#!/usr/bin/python3.9
"""
:module:    redis_io.py

Mockup for handling core Redis functions.
These would be used mainly by IOServices::redis_response.

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


- Make a token (call to secrets)

"""
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


@dataclass
class HashLevel:
    """Define valid hashing levels."""

    SHA512: int = 128
    SHA256: int = 64
    SHA224: int = 56
    SHA1: int = 40


class BRStructs(object):
    """BowRedis constants, data structures."""

# CONSTANTS
    def __init__(self):
        self.field_ty = ["array", "hash", "set", "string"]
        self.sch_act = ["list", "publish", "subscribe",
                        "request", "response"]
        # Keep thinking here... may also be resource, image,
        #   sound, video, binary/executable, etc... ?
        self.sch_ty = ["owl", "redis", "sqlite", "topic"]
        self.sch_verb = ["auth", "decr", "get", "incr",
                         "meta", "put", "remove", "update"]


HASH = HashLevel()
BRS = BRStructs()
ASD = AvroSerDe()


class BowRedis(object):
    """Generic Redis handling."""

    def __init__(self):
        """Initialize Redis connections.

        There is no 'select' command in python-redis.
        Do this instead...
        r1 = redis.Redis(host='127.0.0.1', port=6379, db = 0)
        r2 = redis.Redis(host='127.0.0.1', port=6379, db = 1)
        There is client_setname tho...

        May want to set (?) a password for each namespace,
          which can be done as a .Redis config statement argument.
          Or maybe that is where we "log in" using existing pwd?
        """
        HOST = '127.0.0.1'
        PORT = 6379
        self.RNS = dict()
        for db_no, db_nm in enumerate(["sandbox", "schema", "result", "log"]):
            self.RNS[db_nm] = redis.Redis(host=f'{HOST}', port=PORT, db=db_no)
            self.RNS[db_nm].client_setname(db_nm)

    @classmethod
    def get_hash(cls,
                 p_data_in: str,
                 p_len: int = HASH.SHA256) -> str:
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
        v_hash = hashlib.sha512() if p_len == HASH.SHA512\
            else hashlib.sha224() if p_len == HASH.SHA224\
            else hashlib.sha1() if p_len == HASH.SHA1\
            else hashlib.sha256()
        v_hash.update(p_data_in.encode("utf-8"))
        return v_hash.hexdigest()

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
        r_str = self.bump_restricted_chars(r_str)    # type: ignore
        r_str = self.make_lower(r_str)               # type: ignore
        r_str = self.bump_underbars(r_str)           # type: ignore
        return r_str

    def verify_verbs_types(self, p_ty: str, p_verb: str,
                           p_act: str, p_fields: list) -> bool:
        msg = ""
        if p_ty not in BRS.sch_ty:
            msg += f"\nType must be in {str(BRS.sch_ty)}"
        if p_verb not in BRS.sch_verb:
            msg += f"\nVerb must be in {str(BRS.sch_verb)}"
        if p_act not in BRS.sch_act:
            msg += f"\nAct must be in {str(BRS.sch_act)}"
        for f in p_fields:
            for k, v in f.items():
                if v not in BRS.field_ty:
                    msg += "\nField type must be in " +\
                                    f"{str(BRS.field_ty)}"
        try:
            if msg != "":
                raise Exception(KeyError, msg)
        except KeyError as err:
            print(err)
        return True

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
                   p_fields: list = []) -> object:
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
            serialized response, like
            {"key": key_value, "token": token_value, "ttl"": time_to_live}

        Assign type, name, namespace, alias based on verified arguments.
        Assign topic, version, token.
        Assemble the Avro object.
        Write to Redis. The Redis key is the Avro name (sch_nm).
        """

        self.verify_verbs_types(p_ty, p_verb, p_act, p_fields)  # type: ignore
        topic: str = self.make_snake_case(p_topic)              # type: ignore
        sch_nm: str = p_ty + "." + topic + "." + p_verb + "." + p_act
        new_templ: dict = {
            "aliases": ["queue:" + sch_nm],
            "doc": p_doc,
            "fields": [],
            "hash": "",
            "name": sch_nm,
            "namespace": "net.genuinemerit.schema",
            "token": "",
            "type": "record",
            "update_ts": "",
            "version": ""
        }
        for f in p_fields:
            for k, v in f.items():
                field = {"name": self.make_snake_case(k),    # type: ignore
                         "type": v}
            new_templ["fields"].append(field)
        nt_hash = self.get_schema_hash(p_schema=new_templ)      # type: ignore
        # Redis keys are unique within a namespace.
        schema: object = None
        if self.RNS["schema"].exists(sch_nm):                 # type: ignore
            schema = self.RNS["schema"].get(sch_nm)           # type: ignore
            pp(("Existing schema record", schema))
            old_templ = ASD.convert_avro_to_schema(avro_obj=schema)
            ot_hash = self.get_schema_hash(p_schema=old_templ)  # type: ignore
            if nt_hash != ot_hash:
                # if existing record is different, archive it to log schema
                #   and then update it
                pass
            else:
                pp(("template", old_templ))
        else:
            print("This is a new schema")
            new_templ["hash"] = nt_hash                    # type: ignore
            new_templ["token"] = self.get_token()          # type: ignore
            new_templ["update_ts"] = self.get_timestamp()  # type: ignore
            new_templ["version"] = "1.0.0"
            schema = ASD.convert_schema_to_avro(json_dict=new_templ)
            pp(("template", new_templ))
        pp(("schema", schema))
        return schema


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
