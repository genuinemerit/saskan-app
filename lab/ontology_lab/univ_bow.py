#!/usr/bin/python3
# pylint: disable=E0401
# pylint: disable=W0611
# -*- coding: utf-8 -*-
"""
Universe Generator tornado web app
:module:    univ_bow
:methods:   msg_paths
            main
:classes:   UnivMeta(RequestHandler)
            UnivBang(RequestHandler)
            UnivList(RequestHandler)
            UnivPlay(RequestHandler)
            UnivAJAX(RequestHandler)
            UnivREST(RequestHandler)
            AppException(HTTPError - pass)
            UnivRobot(RequestHandler)
            UnivErr(RequestHandler)
:command line config variables:
            port, secure
:author:    GM <genuinemerit@protonmail.com>

:services_provided:
    Generate galaxy data and visualizations at specified ports

@DEV: This is an interesting module because it attempts some visualizations,
      but not very successful -- both code quality problems and not very intuitive presentations.
      At this point, I might do better just having it generate data & deal with UX later.

      The positive aspect of this effort was identifying a standard tool for generating
      sound/music files and learning how to play them, as well as experimenting with
      Canvas. Much of the "magic" here is in JavaScript. Good stuff and very interesting,
      with much more to learn, especially about 3D graphics -- a capability that keeps getting
      better and easier, but still requires a lot of attention and practice.  The other
      positive take-away is defining a fairly robust complex data structure (at the galatic
      level).  I will be needing to handle much more of that as I get into each entity.

      There is a lot more I want to do in generating a game world. Don't want to get stuck
      at this level. The characteristics of a planet are more important than the galactic
      settings; and of a geographic region even more so.

      May want to rethink this whole module more in terms of how the character generation
      module is progressing, i.e., define a series of events/services that I want to support,
      build the framework for that, then drill into each piece of it as autonomously as possible.
      Think of it as the drill down into the PLACE entity.

      Then take "lessons learned" from Canvas, sound, animation and data into creating more
      primative services, smaller-scale widgets and so on, that I can use/re-use in multiple
      contexts.

      I probably tried to do too much in one module. I am not opposed to having multiple
      HTML templates for a given .py necessarily, but it may be better in the long run to
      have more "apps" (.py modules), with 1:1 relationship to screens.  Think lambda;
      think micro-services. Keep it simple.

      Also see design notes regarding use of ML and AI algorithms. If I want to get into
      some complexity, I might do better generating a lot of different data sets, with a
      basic algorithm for playing my "game of life" on them, then
      evaluating them to determine what "mix" of initial conditions results in the kind
      of "life" I am interested in.  After reading up on Barabasi's network theory, I may
      also want to explore more use of graphing data, as well as examining metrics
      and patterns regarding network effects of my data and AI's.
"""

## General Purpose imports
import json
import math
import requests
import time
import sys
from collections import namedtuple
from os import path
## Tornado and Jinja2
import jinja2
from tornado import httpserver, web, ioloop
from tornado.options import define, options
from flask_api import status
from tornado_jinja2 import Jinja2Loader
## Home-grown
from func_basic import FuncBasic
from func_queue import FuncQueue
from func_basic import BC
from universe import Universe

## Static methods
#####################

def rest_msgs(p_key=None):
    """ Metadata to drive REST message handling
    """
    msgs = dict()
    msgs["start"] = {'desc':'Run computations for a new universe',
                     'args': ['univ_nm']}
    msg = None
    if p_key is None:
        return msgs
    if p_key not in msgs.keys():
        FB.log_me("Message unknown: '{}'".format(p_key), LOG, BC.ERROR)
    else:
        msg = msgs[p_key]
    return msg

## Classes that inherit from Tornado ##
#######################################


class UnivList(web.RequestHandler):
    """
    Show pick list of saved universes
        -- Get unique keys from /dev/shm/univ.json
        -- Pick one
        -- redirect to get/play/{universe_name}
    GET [univ/list, univ/list/(.*)] -- list saved universes that match pattern
    """

    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for univ/list
        """
        univ_list_html = dict()
        univ_list_html['page_title'] = 'List Saved Universes'
        univ_list_html['load_btn'] = 'List'
        univ_list_html['reset_btn'] = 'Bang'
        univ_list_html['play_btn'] = 'Play'
        urecs = list()
        urecs = FQ.get_records(DATA)
        # FB.log_me("urecs: {}".format(str(urecs)), LOG, BC.INFO)
        univ_list_html['list_items'] = '<table><th><td>Universes</td><th>'
        for uitem in urecs:
            # FB.log_me("uitem: {}".format(str(uitem)), LOG, BC.INFO)
            univ_list_html['list_items'] += '\n<tr><td>' + str(list(uitem.keys())[0]) +  '</td></tr>'
        univ_list_html['list_items'] += '\n</table>'
        # FB.log_me("univ_list_html: {}".format(str(univ_list_html)), LOG, BC.INFO)
        self.render(options.univ_list_html, **univ_list_html)

class UnivBang(web.RequestHandler):
    """
    Serve up a new universe
    GET [univ/bang, univ/bang/]
    """

    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for univ/bang
        """
        univ_bang_html = dict()
        univ_bang_html['page_title'] = 'New Universe'
        univ_bang_html['load_btn'] = 'List'
        univ_bang_html['roll_btn'] = 'Bang'
        univ_bang_html['reset_btn'] = 'Reset'
        univ_bang_html['play_btn'] = 'Play'
        univ_bang_html['sound_btn'] = 'Sound'
        self.render(options.univ_bang_html, **univ_bang_html)

class UnivPlay(web.RequestHandler):
    """
    Run  visualization module
    GET univ/play/{universe-name}
        -- run {universe-name} if it exists, else redirect to univ/list

    Save current big bang and compute universe-start data
    POST [univ/play, univ/play/]
        -- save new big bang data
        -- run REST msg to compute universe data
        -- redirect to GET univ/play/{universe-name}
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for univ/play

        Add interface to rename the universe.
        """
        univ_play_html = dict()
        univ_play_html['page_title'] = 'Start a Universe'
        univ_play_html['reset_btn'] = 'Bang'
        univ_play_html['play_btn'] = 'Re-Play'
        univ_play_html['sound_btn'] = 'Sound'
        self.render(options.univ_play_html, **univ_play_html)

    def post(self, *args, **kwargs):
        """
        Handle POST requests for univ/bang/play (for now: start state for a new universe)
        @DEV: This seems to hang. Not sure why.
        """
        gxdb_json = self.get_argument('gxdb')
        gxdb = json.loads(gxdb_json)
        univ_nm = "{}~{}".format('BOWU', FB.hash_me(gxdb_json, 40))
        # Write to data queue
        FQ.write_queue(DATA, univ_nm, gxdb)
        # Call REST message handler for "start/univ-nm"
        requests.get(PROTOCOL + HOST_NM + '/univ/msg/start/{}'.format(univ_nm))
        # Redirect to GET /univ/play/univ_nm to animate the results of the computations.
        self.redirect("/univ/play/{}".format(univ_nm))

class UnivAJAX(web.RequestHandler):
    """
    Ajax interface to return a JSON data set
    GET univ/data/{univ_nm}
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for univ/data/<univ_nm>
        :Args:
        - Universe name is a key to a univ.json data record
        """
        univ_nm = args[0]
        univ_data = FB.get_que_recs(DATA, univ_nm, p_latest=True)
        # Hand the "data" portion of the record back to caller in JSON format
        self.set_header('Content-Type', 'text/json')
        self.write(json.dumps(FB.get_que_rec_data(univ_data)))

class UnivREST(web.RequestHandler):
    """
    Handle REST messages
    GET univ/msg/{msg-value}
    """
    def data_received(self, chunk):
        pass


    def parse_rest(self, p_msg):
        """ Evaluate the request
            :p_msg: {list} - first arg is message name, remaining args are parameters
        """
        msg = rest_msgs(p_msg[0])
        msgp_cnt = len(msg['args'])
        if msg:
            if (len(p_msg) - 1) != msgp_cnt:
                FB.log_me("Message param list invalid", LOG, BC.ERROR)
                return False
            else:
                for i in range(1, msgp_cnt + 1):
                    if p_msg[i] is None or p_msg[i] == "":
                        FB.log_me("Message param value invalid", LOG, BC.ERROR)
                        return False
        return msg

    def get(self, *args, **kwargs):
        """
        Handle GET requests for univ/msg/{msg-value}
        """
        msgargs = args[0].split("/")
        msg = self.parse_rest(msgargs)
        if msg is not False:
            _ = Universe(DATA, LOG, HOST_NM, msgargs[0], msgargs[1])

class UnivMeta(web.RequestHandler):
    """
    HEAD /univ, /univ/(.*), /univ/meta, /univ/meta/(.*)
    GET /univ, /univ/(.*), /univ/meta, /univ/meta/(.*)
    """
    def data_received(self, chunk):
        pass

    def set_hdr_msg(self):
        """ List acceptable URLs in format suitable for display.
        """
        msgs = list()
        msgp = namedtuple('msgp', 'desc PROTOCOL path ')
        msgs.append(msgp('List saved universes', ['GET'], '/univ/list')._asdict())
        msgs.append(msgp('Bang out a new universe', ['GET'], '/univ/bang')._asdict())
        msgs.append(msgp('Play universe simulation', ['GET', 'POST'], ['/univ/play', '/univ/play/{univ-name}'])._asdict())
        msgs.append(msgp('AJAX data request', ['GET'], 'univ/data/{univ-nm}')._asdict())
        msgs.append(msgp('REST messages', ['GET'], ['univ/msg/{msg-value}', rest_msgs()])._asdict())
        msgs.append(msgp('Get services metadata', ['HEAD', 'GET'], ['/univ', 'univ/*', '/univ/meta', 'univ/meta/*'])._asdict())
        msgs.append(msgp('Get robots.txt context', ['GET'], '/robots.txt')._asdict())
        self.set_header('Meta-Messages-List', json.dumps(msgs))
        return json.dumps(msgs)

    def head(self, *args, **kwargs):
        """ Write informational messages as header. """
        self.set_hdr_msg()

    def get(self, *args, **kwargs):
        """ Write informational messages as header and in body. """
        self.write(self.set_hdr_msg())

class UnivRobot(web.RequestHandler):
    """
    GET /robots.txt
    HEAD /robots.txt
    """
    def data_received(self, chunk):
        pass


    def get(self, *args, **kwargs):
        """ Write robots.txt content to body """

        robot_txt = str()
        with open(options.static + '/robots.txt', 'r') as robot_f:
            robot_txt = robot_f.read()
        self.write(robot_txt)

class AppException(web.HTTPError):
    """ For customized app error handling, override Tornado's web.HTTPError
        This means I can use the Flask API definitions of HTTP response codes, which are nicer.
    """
    pass
class UnivErr(web.RequestHandler):
    """
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
    """ Launch the app """
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        path.join(path.dirname(__file__), options.templates)), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    debug_jinja = True if options.loglevel == 'DEBUG' else False
    settings = dict(template_loader=jinja2_loader,
                    static_path=path.join(path.dirname(__file__), options.static),
                    debug=debug_jinja)
    app = web.Application(
        handlers=[
            (r"/univ/bang", UnivBang),
            (r"/univ/bang/", UnivBang),
            (r"/univ/list", UnivList),
            (r"/univ/list/", UnivList),
            (r"/univ/list/(.*)", UnivList),
            (r"/univ/play", UnivPlay),
            (r"/univ/play/", UnivPlay),
            (r"/univ/play/(.*)", UnivPlay),
            (r"/univ/data/(.*)", UnivAJAX),
            (r"/univ/msg", UnivREST),
            (r"/univ/msg/", UnivREST),
            (r"/univ/msg/(.*)", UnivREST),
            (r"/univ/meta", UnivMeta),
            (r"/univ/meta/", UnivMeta),
            (r"/univ/meta/(.*)", UnivMeta),
            (r"/univ", UnivBang),
            (r"/univ/", UnivBang),
            (r"/univ/(.*)", UnivBang),
            (r"/robots.txt", UnivRobot),
            (r"/(.*)", UnivErr)],
        **settings
    )

    FB.log_me("Starting up univ_bow.py at {}{}:{}".format(PROTOCOL, HOST_NM, str(options.port)),
              LOG, options.loglevel)
    # For local prototypes without a real Domain, use secure = 0 (HTTP)
    # For any serious deployment, use secure = 1 (HTTPS)
    if options.secure == 1:
        http_server = httpserver.HTTPServer(app, ssl_options={
            "certfile": "/etc/letsencrypt/live/" + HOST_NM + "/fullchain.pem",
            "keyfile": "/etc/letsencrypt/live/" + HOST_NM + "/privkey.pem",
        })
    else:
        http_server = httpserver.HTTPServer(app)

    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    """
    Start up the app.
    """
    FB = FuncBasic()
    FQ = FuncQueue()
  # Define and collect options
    # See: https://www.tornadoweb.org/en/stable/options.html
    # Note that the location of the config file is passed in as a cmd line option.
    # Command line configs
    define("port", help="Port to run app instance under", type=int)
    define("secure", help="Run under TLS if true", type=int)
    define("conf", help="Relative path to config file", type=str)
    options.parse_command_line(final=False)
    PROTOCOL = 'https://' if options.secure else 'http://'
    # Config file configs
    define("loglevel", help="Debug and log level")
    define("internal_host", help="Internal host IP")
    define("static", help="Location of static resources")
    define("templates", help="Location of HTML templates")
    define("pix", help="Location of graphic resources")
    define("memdir", help="In-memory data storage path")
    define("dat_fil", help="Data queue name")
    define("run_log", help="Log queue name")
    define("apps", help="List of supported app names")
    define("domains", help="List of domain names aligned to app names")
    define("dmn_host", help="Host name")
    define("univ_bang_html", help="HTML template for New Big Bang page")
    define("univ_list_html", help="HTML template for List Universes page")
    define("univ_play_html", help="HTML template for Run Universe page")
    options.parse_config_file(options.conf)

    app_nm = 'univ'
    app_ix = options.apps.split(',').index(app_nm)
    HOST_NM = options.domains.split(',')[app_ix] + options.dmn_host
    DATA = path.join(options.memdir, app_nm + options.dat_fil)
    LOG = path.join(options.memdir, app_nm  + options.run_log)
    main()
