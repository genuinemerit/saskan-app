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
    - By key (GET v)
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
from pprint import pprint as pp  # noqa: F401

import datetime
import json
import redis
import secrets
import uuid


class BRStructs(object):
    """BowRedis constants, data structures."""

# CONSTANTS
    def __init__(self):
        self.field_ty = ["array", "hash", "set", "string"]
        self.templ_act = ["list", "publish", "subscribe",
                          "request", "response"]
        self.templ_ty = ["avro", "owl", "redis", "sqlite", "topic"]
        self.templ_verb = ["auth", "decr", "get", "incr",
                           "meta", "put", "remove", "update"]


brs = BRStructs()


class BowRedis(object):
    """Generic Redis handling."""

    def __init__(self):
        """What happened to GitHub Copilot? It is enabled and I am connected,
           but nothing is happening?
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
        self.rns = dict()
        for db_no, db_nm in enumerate(["sandbox", "schema", "result", "log"]):
            self.rns[db_nm] = redis.Redis(host=f'{HOST}', port=PORT, db=db_no)
            self.rns[db_nm].client_setname(db_nm)

    @classmethod
    def big_token(cls) -> str:
        """Generate a cryptographically strong unique ID"""
        return (str(uuid.UUID(bytes=secrets.token_bytes(16)).hex) +
                str(uuid.UUID(bytes=secrets.token_bytes(16)).hex))

    @classmethod
    def today_now(cls) -> str:
        """Return current timestamp w/ microseconds in ISO format as string"""
        return datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc).isoformat()

    @classmethod
    def bump_restricted_chars(cls, p_str: str) -> str:
        """Return string with URI-restricted chars changed to hyphens

        Convert reserved characters...
            : / ? # [ ] @ ! $ & ' * + , ; =
        ...and a few others...
            _ & ( ) ` € " " (space)
        ... to hyphens. Then:
        """
        r_str = p_str
        restrict = [":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'", "%",
                    "*", "+", ",", ";", "=", "(", ")", "`", '"', "€", " ", "_"]
        for r_char in restrict:
            r_str = r_str.replace(r_char, "-")
        return r_str

    @classmethod
    def bump_to_lower(cls, p_str: str) -> str:
        """Return string with uppers bumped to lowers

        And some additional hyphenating aimed at converting camel to spine

        Convert all names of everything (*) to spine-case:
        - convert capital letter in char[0] to `lower`
        - convert series of capital letters to `-lowerseries-`
        - convert non-first capital letters to `-lower`
        """
        r_str = p_str
        r_str = r_str[:1].lower() + r_str[1:]
        count_upper = 0
        for rix, rchar in enumerate(r_str):
            if rchar.isupper():
                count_upper += 1
                if count_upper == 2:
                    r_str = r_str[:rix-1] + "-" + r_str[rix-1:] + "-"
            else:
                count_upper = 0
        r_str = r_str.lower()
        return r_str

    @classmethod
    def bump_hyphens(cls, p_str: str) -> str:
        """Return string stray hyphens removed

        - Remove leading or trailing hyphens
        - Reduce multiple hyphens to single hyphen

        The following are NOT converted to hyphens but
         still removed if trailing or leading:
            . ~ :
        Finally, convert dots to tildes
        """
        other_char = ["-", ".", "~"]
        r_str = p_str
        while "--" in r_str:
            r_str = r_str.replace("--", "-")
        while r_str[-1:] in other_char:
            r_str = r_str[:-1]
        while r_str[:1] in other_char:
            r_str = r_str[1:]
        for ochar in other_char:
            r_str = r_str.replace(ochar + "-", ochar)
            r_str = r_str.replace("-" + ochar, ochar)
        r_str = r_str.replace(".", "~")
        return r_str

    def bump_to_spine_case(self, p_str: str) -> str:
        """Convert string to spine case."""
        r_str = p_str
        r_str = self.bump_restricted_chars(r_str)    # type: ignore
        r_str = self.bump_to_lower(r_str)            # type: ignore
        r_str = self.bump_hyphens(r_str)             # type: ignore
        return r_str

    def add_schema_template(self: object,
                            p_topic: str,
                            p_type: str = "topic",
                            p_verb: str = "get",
                            p_act: str = "request",
                            p_fields: list = []) -> str:
        """Write new template to SCHEMA database.

        :args:
            p_topic (str) may be hiearchical, with levels separated by colons
            p_type (str): in templ_ty
            p_verb (str) in templ_verb
            p_act (str) in templ_act
            fields (list) of dicts where
                keys - strings identifying field names and
                values - strings in field_ty

        :returns:
            serialized response, like
            {"key": key_value, "token": token_value, "ttl"": time_to_live}

        Assign type, name, namespace, alias based on well-structured arguments.
        Assign topic, version, token.
        Assemble the Avro structure. --> Use Avro/snappy modules here.

        topics, resources use nouns. Brokers use verbs, actions.
        Use spinal-case across everything. Use dots for hierarchies.
        """
        def test_verbs_types():
            status_msg = ""
            if p_type not in brs.templ_ty:
                status_msg += f"\nType must be in {str(brs.templ_ty)}"
            if p_verb not in brs.templ_verb:
                status_msg += f"\nVerb must be in {str(brs.templ_verb)}"
            if p_act not in brs.templ_act:
                status_msg += f"\nAct must be in {str(brs.templ_act)}"
            for f in p_fields:
                for k, v in f:
                    if v not in brs.field_ty:
                        status_msg += "\nField type must be in " +\
                                      f"{str(brs.field_ty)}"
            try:
                if status_msg != "":
                    raise Exception(KeyError, status_msg)
            except KeyError as err:
                print(err)

        test_verbs_types()
        topic: str = self.bump_to_spine_case(p_topic)  # type: ignore
        msg_nm: str = "/" + topic + "." + p_verb + "." + p_act
        template: dict = {
            "type": "record",
            "namespace": "net.genuinemerit.schema",
            "name": msg_nm,
            "aliases": ["/queue" + msg_nm],
            "token": self.big_token(),   # type: ignore
            "fields": [{"name": "topics", "type": "array"},
                       {"name": "version", "type": "string"},
                       {"name": "doc", "type": "string"}]
        }
        for f in p_fields:
            for k, v in f:
                field: dict =\
                    {"name": self.bump_to_spine_case(k),  # type: ignore
                     "type": v}
            template["fields"].append(field)
        # This is a schema. We want the hash to be computed for any
        # message that uses it. Do we ALSO want to compute a hash and
        # get a version for the schema itself? (Yes, I think so). So
        # how to distinguish the "meta" from the "data"? Is it more like
        # "hash", "version" and "token" are "meta-meta", that is, just
        # always computed no matter what? I think so. And I think for that
        # reason they should be in the standard part of the record not in
        # the "fields".
        template["fields"].append({"name": "hash", "type": "string"})
        return json.dumps(template)


if __name__ == "__main__":
    red = BowRedis()
    print(red.add_schema_template(p_topic="(#MY:Test_Topic.$Number**%ONE,+",
                                  p_type="topic"))
    print(red.add_schema_template(p_topic="ontology_file", p_type="topic"))
    print(red.add_schema_template(p_topic="test_topic", p_type="junk",
                                  p_verb="junk", p_act="junk"))
