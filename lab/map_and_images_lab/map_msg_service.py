#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Map Message Service
:module:    map_msg_service
:classes:   AppException, IndexHandler, ErrHandler
:author:    genuinemerit <dave@davidstitt.solutions>

:services_provided:
    map_msg_service on port 8090

Back-end / middle-ware data service provider.

Works in a very flexible manner, trying to interpret the meaning of requests based on comparing 
 attributes provided vs. metadata (see map_msg_register) rather than assuming hard/fast fixed patterns.

- Supports RESTful read-only GET services supplying metadata info about BoW Map Builder message structures.
It make direct calls to map_msg_register.get_data() in order to retrieve metadata info, both to interpret/
craft messages and to satisfy the GET requests.

- Supports RESTful POST calls for add, update, delete of Map resources. 
For handling of POST requests, it writes messages to "/dev/shm/rqst.que", an in-memory file, which is then 
scanned by the map_msg_handler daemon for processing. Presently, it only returns the key of the message that
was written to the request queue.

Good quick tornado reference:
http://www.tornadoweb.org/en/stable/web.html

HTTPie reference (nice command line testing tool):
https://httpie.org/doc

Example of testing with HTTPie
    http GET http://ananda:8090/svg
    http -f POST http://ananda:8090/svg id=mycoolmap size_xy="(800, 600)" style="margin:10px;"

To Do:
1) Implement in a parallel mode, as needed, using Tornado and NGINX
2) Improve RESTful qualities (better HEAD info, use of PATCH for updates)
3) Add more security features: HTTPS, pass the user IP along, pass the user secret token along.
"""

## General Purpose imports     ##
#################################
import json
from os import path
from collections import OrderedDict as OrdD
from pprint import pprint as pp  # pylint: disable=W0611

## Tornado and Jinja2          ##
#################################
import jinja2
from tornado import httpserver, ioloop, web
from tornado.options import define, options

from bow_func_basic import FuncBasic
from map_msg_register import MapMsgRegister
from flask_api import status  # pylint: disable=E0401
from tornado_jinja2 import Jinja2Loader  # pylint: disable=E0401

MMR = MapMsgRegister()
FC = FuncBasic()
RQST_Q = "/dev/shm/rqst.que"
RSLT_Q = "/dev/shm/rslt.que"
CAT_Q = "/dev/shm/cat.que"

## Classes that inherit from Tornado ##
#######################################

class AppException(web.HTTPError):
    """ For customized app error handling, override Tornado's web.HTTPError """
    pass

class IndexHandler(web.RequestHandler):
    """
    For msgt in [svg, ref, grp, elm, use, tgp, txt, img]:

    GET / or GET /{msgt}
    HEAD / or HEAD /{msgt}
    POST / or POST /{msgt} with = zero to many name:value pairs
    """
    def data_received(self, chunk):
        pass

    def head(self, *args, **kwargs):
        """ Return the requested message structure provided by MMR. """
        msgk = args[0] if args else ''
        # To Do: Consider value of returning more useful header data in any response.
        self.set_header('Meta-Msg-Struct', MMR.get_info(msgk))

    def get(self, *args, **kwargs):
        """ Display the requested message structure provided by MMR. """
        msgk = args[0] if args else ''
        argk = args[1] if len(args) > 1 else None
        response = MMR.get_info(msgk, argk)
        if 'Err' in response:
            self.set_status(status.HTTP_404_NOT_FOUND, reason=response)
        self.write(response)

    def post(self, *args, **kwargs):
        """ Handle processing requests as flexibly as possible.
        1) Look for any argument identified for at least one message key.
        2) Can use either query args or body args. Body args take precedence.
        3) URL arg may be used for message key.
        4) Body > Query > URL arguments is order of precedence.
        5) If explicit msg key, assume it is right. Keep only attrs for that msg.
        6) Else find the message with most matching attributes. Break tie using msg_meta list.
        7) Worst case, it will create a new SVG object.
        """
        msg_meta = json.loads(MMR.get_info())       # Get metadata
        msg_keys = msg_meta['list']                 # Get ranked list of message keys
        del msg_meta['list']
        metarg = dict()

        def get_args():
            """ Harvest likely arguments """
            ticked_arg = list()
            for _, metems in msg_meta.items():
                for argk in metems:
                    if argk not in metarg and argk not in ticked_arg:
                        val_b = self.get_argument(argk, None)
                        val_q = self.get_query_argument(argk, None)
                        if val_b is None and val_q is None:
                            ticked_arg.append(argk)     # Ignore arg if it comes up again in meta
                        else:                           # Prefer body over query args
                            metarg[argk] = val_b if not None else val_q
            if args and 'msg' not in metarg and args[0] in msg_keys:
                metarg['msg'] = args[0]             # Assume URL arg is msg if not ID'd yet

        def detect_msg():
            """ Detect most likely message """
            max_cnt = 0
            arg_cntr = OrdD()
            for msgk in msg_keys:
                arg_cntr[msgk] = 0
                for argk in msg_meta[msgk]:
                    if argk in metarg:
                        arg_cntr[msgk] += 1
                        max_cnt = arg_cntr[msgk] if arg_cntr[msgk] > max_cnt else max_cnt
            for key, kcnt in arg_cntr.items():
                if kcnt == max_cnt:
                    metarg['msg'] = key
                    break

        def fill_msg():
            """ Fill in any missing standard values for the message key """
            for argk, vals in msg_meta[metarg['msg']].items():
                if argk not in metarg and 'meta' not in vals:
                    metarg[argk] = None
                    if 'delete' in vals:
                        metarg[argk] = "False"
                    elif 'text' in vals:
                        metarg[argk] = ''
                    elif 'xy' in vals:
                        metarg[argk] = "(0, 0)"

        def scrub_msg():
            """ Remove attributes that don't belong with the selected message key """
            msg_argks = [margk for margk in msg_meta[metarg['msg']]]
            msgarg = {argk: argv for argk, argv in metarg.items() if argk in msg_argks}
            return msgarg

        get_args()
        if 'msg' not in metarg:
            detect_msg()
        fill_msg()
        msg = json.dumps(scrub_msg())
        # Write the request message to a queue for processing by the map maker.
        # To Do: Reply with acknowledgement and URL to ping to get the actual response.
        # So far it just returns the key on the request queue
        qkey = FC.que_me(msg, RQST_Q)
        response = '{"rqst_q_key": ' + '"{0}"'.format(qkey) + '}'
        self.write(response)

class ResultHandler(web.RequestHandler):
    """
    GET /rslt/request_{key} or GET /rslt/{item_id}
    First look on rslt.que. If there, pop it. If not, search cat.que.
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Display the item retrieved from rslt.que. """
        rsltk = args[0]
        rslt_d = dict()
        response = None
        with open (RSLT_Q, 'r') as rsltf:
            rslt_j = rsltf.read()
            rsltf.close()
            if rslt_j not in (None, ''):
                rslt_d = json.loads(rslt_j)
        if rsltk in rslt_d:
            response = json.dumps(rslt_d[rsltk])
            # Remove item from result queue
            del rslt_d[rsltk]
            with open (RSLT_Q, 'w') as rsltf:
                rsltf.write(json.dumps(rslt_d))
                rsltf.close()
        else:
            with open (CAT_Q, 'r') as catf:
                cat_d = json.loads(catf.read())
                catf.close()
            for _, catrec in cat_d.items():
                if catrec['rqst_key'] == rsltk:
                    response = json.dumps(catrec)
                    break
            if response is None:
                response = "No result on queue with key '{0}'".format(rsltk)
                self.set_status(status.HTTP_404_NOT_FOUND, reason=response)
        self.write(response)

class CatalogHandler(web.RequestHandler):
    """
    For msgt in [svg, ref, grp, elm, use, tgp, txt, img]:
        GET /cat /cat/ /cat/list  /cat/list/
            Return list of all keys, with message type.
        GET /cat/list/{msgt}
            Search cat.que for items with this message type. Return list of keys.
        GET /cat/list/info/{msgt}
    Where keyv is a valid key on cat.que:
        GET /cat/info/{keyv}
        GET /cat/{keyv}
            Return detail info for this item.
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Display info retrieved from cat.que. """
        cat_j = ''
        cat_d = dict()
        resp_l = list()
        msg_t = args[0]
        if path.isfile(CAT_Q):
            with open (CAT_Q, 'r') as catf:
                cat_j = catf.read
                if cat_j not in (None, ''):
                    cat_d = json.loads(catf.read())
                catf.close()
            for cat_key, cat_info in cat_d.items():
                if cat_info['msg'] == msg_t:
                    resp_l.append(cat_key)
        else:
            response = "No items found on the catalog yet"
            self.set_status(status.HTTP_404_NOT_FOUND, reason=response)
        self.write(json.dumps(resp_l))

class ErrHandler(web.RequestHandler):
    """
    GET /{err}
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Capture all error displays.  
            To Do: Not sure this is doing anything useful.
        """
        status_code = self.request.path[1:]
        err_out = dict()
        err_out["Status Code"] = status_code
        status_code_str = str(status_code)
        err_out["Status Code"] = status_code_str
        for key, val in self.request.arguments.items():
            err_out[str(key)] = val[0].decode("utf-8")
        self.set_status(status_code, reason=None)
        self.write(json.dumps(err_out))

def main():
    """ Launch the app """
    define("port", default=8090, help="map message services", type=int)
    options.parse_command_line()
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),
                                    autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    settings = dict(template_loader=jinja2_loader,
                    static_path=path.join(path.dirname(__file__), "static"),
                    debug=True)
    #                debug=False).
    app = web.Application(
        handlers=[
            (r"/cat", CatalogHandler),
            (r"/cat/", CatalogHandler),
            (r"/cat/list", CatalogHandler),
            (r"/cat/list/", CatalogHandler),
            (r"/cat/list/(\w+)", CatalogHandler),
            (r"/cat/list/info/(\w+)", CatalogHandler),
            (r"/cat/info/(\w+)", CatalogHandler),
            (r"/cat/(\w+)", CatalogHandler),
            (r"/rslt/(\w+)", ResultHandler),
            (r"/", IndexHandler),
            (r"/(\w+)", IndexHandler),
            (r"/(\w+)/(\w+)", IndexHandler),
            # To Do: Set up Data Get service calls that use two URL args on a GET:
            #  message Type and item ID (or 'all' or 'list'...). So we can request 
            #  the list of values associated with a specific metadata attribute. 
            (r"/(.*)", ErrHandler)],
        **settings
    )
    http_server = httpserver.HTTPServer(app)
    # To Do: Run asynchronous and in parallel using Tornado and NGINX.
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
