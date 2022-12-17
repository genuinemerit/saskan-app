#!/bin/python3.6
"""
greetings.property

A simple 'Hello, World' web (HTTP) API built using Tornado.

REQUEST:
    BASE PATH:     <domain>
    VERB(S):       GET
"""
# pylint: disable=E0602
# pylint: disable=W0221
# pylint: disable=W0223
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
# Identify qualiities of the service which can be paramterized at the command line
define("port", default=8080,
       help="Sample API Greeting Service defaults to port 8080", type=int)


class IndexHandler(tornado.web.RequestHandler):
    """
    Class for handling index-level calls, that is, calls to the base service Path.
    Tornado works by extending the RequestHandler class.
    In this example, simply define a base path equal to the server's root "index" path: "/"

    REQUEST:
        PATH:     /
        VERB(S):  GET
        VARIABLES:
            URL:  'greeting' = {string} (optional, default='Hello')

    RESPONSE:
        HEADER: standard
        BODY:   schema = greeting_string_value + <immutable string>
    """

    def get(self):
        """
        get_argument() params are:
            Name of a URL variable: "greeting"
            Default value to use, implying that use of URL variable is optional
        """
        greeting_value = self.get_argument('greeting', 'Hello')
        # The write() method returns output to the caller of the service.
        self.write(greeting_value + ', dear user!')

## MAIN ##
# ========
if __name__ == "__main__":
    """
    In a more full-fledged set-up, we'd probably put these set-up/start-up commands in
    a separate module.
    """
    # This option allows us to test the service from the command line
    tornado.options.parse_command_line()
    # Associate a message pattern to a Class
    # Note that this is literally pattern-matching, using a regular expression:
    APP = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    # Define an instance of a web server app to handle the defined message-to-method mapping
    HTTP_SERVER = tornado.httpserver.HTTPServer(APP)
    # Assign to the specified port
    HTTP_SERVER.listen(options.port)
    # Start it up
    tornado.ioloop.IOLoop.instance().start()
