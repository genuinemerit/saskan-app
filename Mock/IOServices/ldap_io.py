#!/usr/bin/python3.9
"""
:module:    ldap_io.py

Mockup for handling LDAP functions.

These methods would be called by the IOServices which
handle the LDAP messages. Only the ldap_response.py
module would use these mtehods. (I think...)

See:
- /etc/default/slapd
- /etc/ldap/slapd.d


Using this tutorial as a guide:
https://ldap3.readthedocs.io/en/latest/tutorial_intro.html 

Main behaviors:

- Identify, Connect and Bind to LDAP server.
-  
"""
import ldap3

from pprint import pprint as pp

# pp((dir(ldap3)))

#  systemctl start slapd

server = ldap3.Server('ldap:///:389')
conn = ldap3.Connection(server, auto_bind=True)

pp((server))
pp((conn))
