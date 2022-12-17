#!/bin/python3.6
"""
A simple web (HTTP) API built using Tornado demonstrating both a GET and a POST.

Things to remember are:
* Each method (service path) in Tornado is a class that inherits from RequestHandler
* All messages (message patterns) are defined as regular expressions in the MAIN program

New in this example:
* More concise way of pulling in and referencing tornado modules
* Customized error handling

REQUEST:
    BASE PATH:     <domain>
    VERB(S):  GET, POST

"""
# pylint: disable=E0401
# pylint: disable=E0602
# pylint: disable=W0221
# pylint: disable=W0223

from http.client import responses  # Provides default HTTP status code messages
# import json
# import traceback
import textwrap     # Provides text wrapping functions
from tornado import httpserver, ioloop, web
from tornado.options import define, options

from flask_api import status    # Provides good constants describing HTTP status codes


# Identify qualiities of the service which can be parameterized at the command line
# We could also just hard-code the port value in the MAIN program
define("port", default=8080,
       help="Sample API String Reversal defaults to port 8080", type=int)

class AppException(web.HTTPError):
    """ For customized application error handling, override web.HTTPError """
    pass

class ReverseHandler(web.RequestHandler):
    """
    REQUEST:
        PATH: /reverse/{string}
        VERB: GET
        VARIABLES:
            url: {string} (required)
    REPONSE:
        HEAD: standard
        BODY: schema = <string>
    """
    def get(self, in_var):
        """
        Unnnamed URL parameter is pulled in a simple parameter to the function.
        Return parameter as reversed string value.
        """
        # The third value in a python array/string slicing instruction is the "step" value.
        # When it is negative, then it reverses the order of the sliced values returned.
        # So when applied with no start & no end index, and a value of negative one, it has the
        # effect of returning the entire string (or array), reversed.
        self.write(in_var[::-1])

class WrapHandler(web.RequestHandler):
    """
    REQUEST:
        PATH: /wrap
        VERB: POST
        VARIABLES:
            BODY:
                'text'  = {string}   (required)
                'width' = {integer}  (optional, default=40)
    REPONSE:
        HEAD: standard
        BODY: schema = word-wrapped <string>
    """
    def post(self):
        """
        Return input with line-wrap inserted at specified width value, defaulted to 40.
        """
        # Nothing fancy. POST uses the same get_argument function that would be used if it was a
        # url variable with a GET. If there is no argument indexed by 'text', what happens?
        text_value = self.get_argument('text')
        width_value = self.get_argument('width', 40)
        if not str(width_value).isdigit():
            # Alternatively, just set it to the default value and return a "warning"
            # in the REPONSE HEAD?
            print(responses[status.HTTP_400_BAD_REQUEST])
            msg = "{0}, ".format(responses[status.HTTP_400_BAD_REQUEST]) +\
            "Width parameter value must be a positive integer"
            raise AppException(reason=msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.write(textwrap.fill(text_value, int(width_value)))

## MAIN ##
# ========
if __name__ == "__main__":
    """
    In a full-fledged set-up, maybe put set-up/start-up commands in a separate module.
    """
    # This option allows us to parameterize the service from the command line
    options.parse_command_line()
    # Associate a message pattern to a Class.
    # Note that this is literally pattern-matching, using a regular expression:
    APP = web.Application(
        handlers=[
            (r"/reverse/(\w+)", ReverseHandler),
            (r"/wrap", WrapHandler)
        ]
    )
    # Define an instance of a web server app to handle the defined message-to-method mapping
    HTTP_SERVER = httpserver.HTTPServer(APP)
    # Assign to the specified port
    HTTP_SERVER.listen(options.port)
    # Start it up
    ioloop.IOLoop.instance().start()
