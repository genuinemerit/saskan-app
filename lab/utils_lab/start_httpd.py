#!/usr/bin/python2.7
''' Start up a simple HTTP server. It points to the directory where
    this file resides.  A single-line version is:
    python -m SimpleHTTPServer 8000
'''
import SimpleHTTPServer
import SocketServer

PORT = 8000

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

HTTPD = SocketServer.TCPServer(("", PORT), Handler)

print "Serving HTTP at port", PORT
HTTPD.serve_forever()
