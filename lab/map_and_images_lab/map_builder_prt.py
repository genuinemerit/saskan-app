#!/bin/python3.6
"""
Map Maker App
:module:    map_builder_prt
:class:     AppException, IndexHandler, MenuHandler, MapHandler, EditHandler, ErrHandler
:functions: show_debug/5, render_html/0, main/0
:author:    genuinemerit <dave@davidstitt.solutions>

Front-end, user-facing presentation service (web app).

:services_provided:
- map_builder_prt on port 8080

:services_used:
- map_msg_service on port 8090
- map_msg_handler daemon
"""
## General Purpose imports     ##
#################################
import json
import requests
import time
import traceback
import urllib.parse
from collections import OrderedDict as OrdD
from pprint import pprint as pp
from os import path

## Tornado and Jinja2          ##
#################################
import jinja2
from tornado import httpserver, ioloop, web
from tornado.options import define, options
from flask_api import status                # pylint: disable=E0401
from tornado_jinja2 import Jinja2Loader     # pylint: disable=E0401

## Local Classes, Objects , Constants     ##
############################################
from bow_html_forms import BowHtmlForms
BHF = BowHtmlForms()
from bow_map_html import BowMapHtml
BMH = BowMapHtml()

DEBUG = True
MAP_HTML = "map_builder.html"       # my HTML template
SRV = "http://ananda:8090/"         # my Path
MSGT = OrdD()
resp = requests.get("{}{}".format(SRV,"list"))
MSGT = {msgt: msgt.capitalize() for msgt in json.loads(resp.text)}

## Local functions / static methods ##
######################################

def show_debug(p_args=None, p_uri=None, p_cls=None, p_label=None, p_value=None):
    """ Render debug info on HTML output """
    BMH.dbg_msg = ''
    brk = "</br>"
    if DEBUG:
        mod_path = traceback.extract_stack(None, 2)[0][0].split("/")
        BMH.dbg_msg += brk + BHF.tag("Module: ", "strong") + mod_path[len(mod_path) - 1]
        BMH.dbg_msg += brk + BHF.tag("Class: ", "strong") + p_cls if p_cls is not None else ''
        BMH.dbg_msg += brk + BHF.tag("Function: ", "strong") + traceback.extract_stack(None, 2)[0][2]
        BMH.dbg_msg += brk + BHF.tag("Request: ", "strong") + p_uri.split("/")[1]\
          if p_uri is not None else ''
        BMH.dbg_msg += brk + BHF.tag("Path: ", "strong") + p_args[0]\
            if p_args not in [None, ()] else ''
        BMH.dbg_msg += brk + BHF.tag(p_label + ": ", "strong") if p_label is not None else ''
        BMH.dbg_msg += str(p_value) if p_value is not None else ''

def render_html():
    """  Dict of all the things to render """
    html_widg = dict()
    html_widg['err_msg'] = BMH.err_msg
    html_widg['dbg_msg'] = BMH.dbg_msg
    html_widg['menu_btns'] = BMH.menu_btns
    for msgt in MSGT:
        html_widg['{0}_btns'.format(msgt)] = BMH.btns[msgt]
        html_widg['{0}_forms'.format(msgt)] = BMH.forms[msgt]
    html_widg['svg_map'] = BMH.svg_map
    return(html_widg)

## Classes that inherit from Tornado ##
#######################################

class AppException(web.HTTPError):
    """ For customized app error handling, override Tornado's web.HTTPError """
    pass

class IndexHandler(web.RequestHandler):
    """
    GET /
    HEAD /
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Display the app with all menu items turned off."""
        BMH.clear()  # wipe everything
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__)
        self.render(MAP_HTML, **render_html())

    def head(self, *args, **kwargs):
        """ Return app service catalog as a JSON list in the response header.
            May want to look at the OAS standard for how best to label this section.
            Just providing this as an example of how to add more content to a header response.
            The idea would be to make it easy to build automated hooks into the catalog.
        """
        info = ({'PROTOCOL': 'http', 
                 'PATH': '<domain>',
                 'PORT': '8080',
                 '/': [item.strip() for item in IndexHandler.__doc__.strip().split('\n')],
                 '/map': [item.strip() for item in MapHandler.__doc__.strip().split('\n')],
                 '/menu': [item.strip() for item in MenuHandler.__doc__.strip().split('\n')],
                 '/{msgt}/list': [item.strip() for item in ListHandler.__doc__.strip().split('\n')],
                 '/{msgt}/[add|edit|delete]/{key}': 
                 [item.strip() for item in EditHandler.__doc__.strip().split('\n')]})
        self.set_header('catalog', info)

class MenuHandler(web.RequestHandler):
    """
    POST /menu/map /menu/wipe /menu/{msgt}
    """
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        """ Show/hide forms based on use of "menu" buttons. 
            Trigger a redirect to GET path for selected message type.
        """
        p_msg = '/' if args == () or args[0] == 'wipe' else '/' + args[0]
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__,
                   p_label="p_msg", p_value=p_msg)
        self.redirect(p_msg)

class MapHandler(web.RequestHandler):
    """
    GET /map
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Handle redirects from menu handler. Display the rendered SVG file. 
        """
        # To Do: Retrieve the code from most recent map-assembly response.
        BMH.clear()
        # BMH.svg_map = MM.get_code()
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__)
        self.render(MAP_HTML, **render_html())

class ListHandler(web.RequestHandler):
    """
    For msgt in [ref, grp, elm, use, tgp, txt, img]:
        GET /{msgt}/list
        POST /{msgt}/list
    """
    def data_received(self, chunk):
        pass

    def add_new(self, msg_t, args):
        """ Nothing found on catalog, so present a form to add a new item.
        """   
        disp_msg = 'No items created yet on catalog for {0}'.format(msg_t.upper())
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__,
                p_label=msg_t, p_value=disp_msg)
        BMH.make_edit_form(msg_t, "add")

    def list(self, msg_t, args):
        """ Handle request to list all items in the catalog for selected message type.
            List will be keys of items in the catalog queue of the requested message type.
            Calls BMH to make a form that lists key values to select from.
        """
        resp = requests.get("{0}{1}{2}".format(SRV, "cat/list/", msg_t))
        if resp.status_code != 200:
            self.add_new(msg_t, args)
        else:
            show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__)
            keys = list()
            keys = json.loads(resp.text)
            if keys:
                disp_msg = str(len(keys)) + " keys found for message type " + msg_t
                BMH.make_select_list_form(msg_t, disp_msg, keys)
            else:
                self.add_new(msg_t, "add")
        self.render(MAP_HTML, **render_html())

    def get(self, *args, **kwargs):
        """ Handle requests for list of items associated with a message type.
            Display select list of available keys, with a Submit and Add button.
        """
        BMH.err_msg = ''
        msg_t = self.request.uri.split("/")[1]
        self.list(msg_t, args)

    def post(self, *args, **kwargs):
        """ To Do: Capture list requests in body arguments, not just in URL arguments.
        """
        BMH.err_msg = ''
        msg_t = self.request.uri.split("/")[1]
        self.list(msg_t, args)

class SelectHandler(web.RequestHandler):
    """
    For msgt in [svg, ref, grp, elm, use, tgp, txt, img]:
        POST /{msgt}/select, ...
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Should not be getting anything here. Menu redirects should go to ListHandler.
            Remove this once we're sure it is not being used.
        """
        BMH.err_msg = ''
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__)
        rpath = '/' + str(status.HTTP_400_BAD_REQUEST) + '?' +\
          'ERR=' + urllib.parse.quote_plus('Bad Request "{0}"'.format(args[0]))
        self.redirect(rpath)

    def post(self, *args, **kwargs):
        """ Retrieve the selected item from catalog and create an edit form for it
        """
        # =========== post =================
        BMH.err_msg = ''
        url_args = self.request.uri.split("/")
        msg_t = url_args[1]
        form_action = url_args[2]                               # select, ...
        select_value = self.get_argument(msg_t + "_keys")
        rslt = requests.get("{0}{1}{2}".format(SRV, "cat/info/", select_value))
        attr_vals = json.loads(rslt.text)
        pp(("attr_vals: ", attr_vals))
        # Send msg to message handler.
        resp = requests.post("{0}".format(SRV), data=attr_vals)
        BMH.make_edit_form(msg_t, "submit", json.loads(resp.text))
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__,
                   p_label="Action", p_value=form_action)
        self.render(MAP_HTML, **render_html())

class EditHandler(web.RequestHandler):
    """
    For msgt in [svg, ref, grp, elm, use, tgp, txt, img]:
        POST /{msgt}/add, /{msgt}/select, ...
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Should not be getting anything here. Menu redirects should go to ListHandler.
            Remove this once we're sure it is not being used.
        """
        BMH.err_msg = ''
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__)
        rpath = '/' + str(status.HTTP_400_BAD_REQUEST) + '?' +\
          'ERR=' + urllib.parse.quote_plus('Bad Request "{0}"'.format(args[0]))
        self.redirect(rpath)

    def post(self, *args, **kwargs):
        """ Process form for editing various types of SVG components, or handle map rendering.
            For msgt in [map, svg, ref, grp, elm, use, tgp, txt, img]:
                POST /{msgt}/add /{msgt}/edit /{msgt}/delete
            To Do: Include a catalog key in the URL for editing a specific item of the message type.
        """
        # =========== post =================
        BMH.err_msg = ''
        url_args = self.request.uri.split("/")
        msg_t = url_args[1]
        form_action = url_args[2]                               # add, ...
        resp = requests.get("{0}{1}".format(SRV, msg_t))        # valid, expected arguments
        attr_d = json.loads(resp.text)
        attr_vals = dict()
        # Pull in data from form.
        for attr_nm, attr_meta in attr_d.items():
            if 'xy' in attr_meta:
                attr_vals[attr_nm] = "({0}, {1})".format(str(self.get_argument(attr_nm + "_x")),
                                                         str(self.get_argument(attr_nm + "_y")))
            else:
                attr_vals[attr_nm] = self.get_argument(attr_nm)
        attr_vals['delete'] = 'True' if form_action == 'delete' else 'False'
        # Send msg to message handler.
        resp = requests.post("{0}".format(SRV), data=attr_vals)
        time.sleep(0.5)
        resp = requests.post("{0}{1}{2}".format(SRV, "rslt/", json.loads(resp.text)["rqst_q_key"]))
        pp(("resp.text", resp.text))
        BMH.make_edit_form(msg_t, "submit", json.loads(resp.text))
        show_debug(p_args=args, p_uri=self.request.uri, p_cls=__class__.__name__,
                   p_label="msg/action", p_value="{0}/{1}".format(msg_t, form_action))
        self.render(MAP_HTML, **render_html())

class ErrHandler(web.RequestHandler):
    """
    GET /{err}
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Capture all error displays.  """
        BMH.clear()  # wipe everything
        status_code = self.request.path[1:]
        rowln = BHF.tdata("Status Code:")
        if status_code.isnumeric():
            rowln += BHF.tdata(str(status_code))
        else:
            rowln += BHF.tdata(str(status.HTTP_400_BAD_REQUEST))
        html = BHF.trow(rowln)
        for key, val in self.request.arguments.items():
            rowln = BHF.tdata(key)
            rowln += BHF.tdata(val[0].decode("utf-8"))
            html += "\n" + BHF.trow(rowln)
        BMH.err_msg = BHF.table(html)
        # raise web.HTTPError(int(status_code))
        self.render(MAP_HTML, **render_html())

def main():
    """ Launch the app """
    define("port", default=8080, help="map constructor", type=int)
    options.parse_command_line()
    # Create a instance of Jinja2Loader so I can use Jinja-style templates.
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    # Replace Tornado default template Loader with Jinja's.
    settings = dict(template_loader=jinja2_loader,
                    static_path=path.join(path.dirname(__file__), "static"),
                    debug=True)
    #                debug=False)
    # Associate message patterns to services.
    url_handlers = [
        (r"/", IndexHandler),
        (r"/menu/wipe", MenuHandler),
        (r"/menu/(\w+)", MenuHandler),
        (r"/map", MapHandler),
        (r"/wipe", web.RedirectHandler, dict(url=r"/menu/wipe")),
        (r"/wipe/", web.RedirectHandler, dict(url=r"/menu/wipe"))
    ]
    for msgt in MSGT:
        url_handlers.append((r"/{0}".format(msgt), ListHandler))
        url_handlers.append((r"/{0}/".format(msgt), ListHandler))
        # url_handlers.append((r"/{0}/submit/(\w+)".format(msgt), EditHandler))
        url_handlers.append((r"/{0}/add".format(msgt), EditHandler))
        url_handlers.append((r"/{0}/select".format(msgt), SelectHandler))
        # url_handlers.append((r"/{0}/add/(\w+)".format(msgt), EditHandler))
        # url_handlers.append((r"/{0}/edit/(\w+)".format(msgt), EditHandler))
        # url_handlers.append((r"/{0}/delete/(\w+)".format(msgt), EditHandler))
    url_handlers.append((r"/(.*)", ErrHandler))
    app = web.Application(
        handlers=url_handlers,
        **settings
    )
    http_server = httpserver.HTTPServer(app)
    # Run a single instance. Next we'll work on running it behind a load balancer.
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
