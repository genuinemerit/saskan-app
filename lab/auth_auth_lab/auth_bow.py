#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    auth_bow.py

Prototype/lab module for development of handlers for:

- manage both credentials and sessions
- log all activity

- activity logs cover:
    - client IP
    - client (user) ID if known
    - session ID if known
    - activity data:
        - event type
        - URL
        - timestamp

    * The RabbitMQ system (written in erlang) is installed on the bow-spt server.
    * Use the python3 pika library to manage access to it.
    * Review use of the python3 logging library also.
        * See: https://www.digitalocean.com/community/tutorials/how-to-use-logging-in-python-3
    * There is example code in Dropbox under projects/python/mq
    * Some books on RabbitMQ are in my O'Reilly Safari playlists
    * This is good practice at thinking in terms of queues and topics
    * Eventually will probably want to port this over to AWS Kinesis / Firehose

- credentials data covers:
    - User ID
    - Password
    - client IP(s)
    - User Info
    - Player links
    - Last update timestamp
    - Hash to make entry unique

- session data covers:
    - Session ID
    - Active IP
    - Last activity timestamp
    - Link to recent activity logs (?)

- create a new session
    - guest session: no sessid, no cookie, no data saved
    - registration session: create autorization and authentication credentials
        - roles supported:
            - gamer
            - admin
            - developer
    - login session: verify authorization and authentication

- determine if user will accept cookies or not
    - if YES or NO
        - create credentials cookie for [designated period] max up to 5 days
        - create session cookie per login domain (e.g., for each APP DNS I support)
        - provide a mechanism to delete / overwrite / expire old one(s)
        - write to server
    - if YES
        - write to client

- logout / end sessions
    - based on a user selection or event trigger such as:
        - clicking a logout button
        - after [designated period] of inactivity (e.g. one hour)
        - following broadcast announcement of a maintenance window
    - delete / archive server-side session data
    - reset client session cookies to expire if user accepts cookies

- provide tests for everything
- provide GUI or console feedback

:author:    GM <genuinemerit@pm.me>
"""
import json
import logging
import math
import pika
import requests
import time
import os
import sys
import pika
from collections import namedtuple
import jinja2
from tornado import httpserver, web, ioloop
from tornado.options import define, options
from flask_api import status
from tornado_jinja2 import Jinja2Loader
# pylint: disable=import-error
from func_basic import FuncBasic
from func_queue import FuncQueue

## Static methods
#####################
def verify_session_id(sessid):
    """
    Check cookie session ID vs. server-stored session ID.
    For now, we just check that it exists locally and matches.
    Will move this to a generic Functions module eventually.

    :Args: - {bytes} returned from call to get_secure_cookie()

    :to-do: We'll want to:

        - Strengthen this to check IPs
        - Clear out old session IDs from local store
        - Expire/refresh client-side cookies
        - Redirect to login/alert bad events, not just fail
    """
    cookie_sessid = sessid.decode("utf-8")
    sessdata_rec = FQ.get_records(SES, cookie_sessid)
    if sessdata_rec is None or len(sessdata_rec) < 1:
        # In this case, how do we know if we EXPECT to have a local session ID?
        raise ValueError("Invalid sessid {}. Delete client cookie".format(cookie_sessid))
    sessdata = FQ.get_record_data(sessdata_rec)
    stored_sessid = sessdata['sessid']
    if cookie_sessid != stored_sessid:
        raise ValueError("Invalid sessid {}. Delete client cookie".format(cookie_sessid))

def set_page_top(args):
    """
    Configure common page items

    :Args:

        - args {list} from the URL call

    :returns: {dict}
    """
    char_html = dict()
    char_html['page_title'] = 'Manage Sessions and Credentials'
    # menu buttons
    char_html['reset_btn'] = "Clear"
    # modes
    char_html['menu_pick'] = ""
    logging.info("args:{}".format(str(args)))
    logging.debug("args:{}".format(str(args)))
    return char_html


class AppException(web.HTTPError):
    """
    Override Tornado's web.HTTPError. Use flask_api.status codes instead
    """
    pass

class AuthReset(web.RequestHandler):
    """
    Reset display on character management page.
    Create a session ID if one does not yet exist.
    This is also the default action for {path}/auth.

    :services:
        - ``GET auth/reset[/*]``
        - ``GET crac[/*]``
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for auth/ or auth/reset

        Create a new secured session ID if one does not yet exist.
        We'll associate this with a real login eventually.
        This is being done here for dev purposes.
        The session ID is stored on the server and also sent to the client
        as a secured (encrypted) cookie.

        Reset menus.
        Hide all displays.
        """
        if not self.get_secure_cookie("bowsessid", max_age_days=31):
            dttm = FB.get_dttm()
            sessid = FB.hash_me(dttm.curr_ts + "Anonymous User" + "Character Gen")
            logging.debug("{}:{}:{}:{}:{}".format(SES, sessid, dttm.curr_utc, 'Anonymous', self.request.remote_ip))
            self.set_secure_cookie("bowsessid", sessid, expires_days=None, secure=True)
        else:
            verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))

        char_html = set_page_top(args)
        char_html['menu_pick'] = "Clear"
        char_html['debug_msg'] = "Session cleared for take-off."
        self.render(HTML_NM, **char_html)

class Robots(web.RequestHandler):
    """
    GET /robots.txt
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Write robots.txt content to body """
        with open(options.static + '/robots.txt', 'r') as robot_f:
            self.write(robot_f.read())

class Unknown(web.RequestHandler):
    """
    Service of last resort...
    GET /{err}
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Capture all error displays. """
        err_out = dict()
        err_out["Status Code"] = status.HTTP_400_BAD_REQUEST
        err_out["URI"] = self.request.uri
        self.set_status(status.HTTP_400_BAD_REQUEST, reason=None)
        self.write(json.dumps(err_out))

## main
#####################

def main():
    """
    Point to templates directory for HTML rendering.
    Point to static directory for js, img, other static resources.
    Set debug level.
    Define URL handlers.
    Define security level.
    For local prototypes w/o a Domain, use secure = 0.
    Otherwise point to SSL certificates.
    Start listening on designated port.
    Launch the auth_bow web app.
    """
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), options.templates)), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    debug_jinja = True if options.log_level == 'DEBUG' else False
    settings = dict(template_loader=jinja2_loader,
                    static_path=os.path.join(os.path.dirname(__file__), options.static),
                    debug=debug_jinja,
                    cookie_secret=options.cookie_secret)
    wapp = web.Application(
        handlers=[
            (r"/auth/reset", AuthReset),
            (r"/auth/reset/", AuthReset),
            (r"/auth/reset/(.*)", AuthReset),
            (r"/auth", AuthReset),
            (r"/auth/", AuthReset),
            (r"/auth/(.*)", AuthReset),
            (r"/robots.txt", Robots),
            (r"/(.*)", Unknown)],
        **settings
    )

    logging.info("Starting up admin_bow.py at {}{}:{}".format(protocol,
                                                    DMN_NM,
                                                    str(options.port)))
    # For local prototypes without a real Domain, only use secure = 0
    if options.secure == 1:
        http_server = httpserver.HTTPServer(APP, ssl_options={
            "certfile": "/etc/letsencrypt/live/" +\
                 DMN_NM + "/fullchain.pem",
            "keyfile": "/etc/letsencrypt/live/" +\
                 DMN_NM + "/privkey.pem",
        })
    else:
        http_server = httpserver.HTTPServer(wapp)

    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    """
    Instantiate helper functions object.
    Define, collect options from command line, from config file.
    Config file location passed in as a cmd line option.
    Identify data and log file locations.

    :methods executed:
        - ``main()``
    """
    FB = FuncBasic()
    FQ = FuncQueue()
    define("app")
    define("port", help="Port for app instance", type=int)
    define("secure", help="Run under TLS if true", type=int)
    define("conf", help="Relative path to config file", type=str)
    options.parse_command_line(final=False)

    protocol = 'https://' if options.secure else 'http://'
    define("log_level", help="Debug and log level")
    define("internal_host", help="Internal host IP")
    define("cookie_secret")
    define("dmn_host", help="Host name")
    define("apps", help="List of supported app names")
    define("app_path", help="Root location of app resources")
    define("app_nm", help="Template for Python app name")
    define("static", help="Location of static resources")
    define("templates", help="Location of HTML templates")
    define("pix", help="Location of graphic resources")
    define("html_nm", help="Template for HTML file name")

    define("mem_path", help="In-memory data storage path")
    define("log_nm", help="Template for Log file name")
    define("auth_fil_nm", help="Credentials files")
    define("dat_fil_nm", help="Data files")
    define("ctl_fil_nm", help="Storage control files")
    define("ses_fil_nm", help="Session state files")
    define("persist_path", help="On-disk active data storage")
    define("archive_path", help="On-disk archive data storage")
    options.parse_config_file(options.conf)

    DATA = dict()
    LOGS = dict()
    APP = options.app
    DMN_NM = APP + "." + options.dmn_host
    HTML_NM = APP + options.html_nm
    AUTH = os.path.join(options.mem_path, APP + options.auth_fil_nm)
    DAT = os.path.join(options.mem_path, APP + options.dat_fil_nm)
    CTL = os.path.join(options.mem_path, APP + options.ctl_fil_nm)
    SES = os.path.join(options.mem_path, APP + options.ses_fil_nm)
    LOG = os.path.join(options.mem_path, APP + options.log_nm)

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    main()
