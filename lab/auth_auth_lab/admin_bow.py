#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
BoW Admin Controls tornado web app
:module:    admin_bow
:methods:   msg_paths
            main
:classes:   AdminQueues(RequestHandler)
            AdminServers(RequestHandler)
            AdminLogs(RequestHandler)
            RESTHandler(RequestHandler)
            AdminMeta(RequestHandler)
            AppException(HTTPError)
            RobotHandler(RequestHandler)
            AdminErr(RequestHandler)
:author:    GM <genuinemerit@protonmail.com>

:services_provided:
    - Front-end for administrative controls and monitors at specified ports
    - REST services for administrative controls at specified ports
"""

## General Purpose imports
import json
import math
import requests
import time                              # pylint: disable=W0611
import sys                               # pylint: disable=W0611
from collections import namedtuple
from os import path
## Tornado and Jinja2
import jinja2
from tornado import httpserver, web, ioloop
from tornado.options import define, options
from flask_api import status             # pylint: disable=W0611,E0401
from tornado_jinja2 import Jinja2Loader  # pylint: disable=E0401
## Home-grown
from func_basic import FuncBasic         # pylint: disable=E0401
from func_queue import FuncQueue         # pylint: disable=E0401
from func_basic import BC                # pylint: disable=E0401

## Globals
#####################

## Static methods
#####################
def set_std_menus(admin_html):
    """ Configure menus common to all modes
        :admin_html: {dict}
    """
    admin_html['que_btn'] = 'Show queues'
    admin_html['srv_btn'] = 'Show servers'
    admin_html['log_btn'] = 'Show logs'
    return admin_html

## Classes that inherit from Tornado ##
#######################################

class AdminQueues(web.RequestHandler):
    """
    Manage and monitor data queues
    GET  admin/que
    POST admin/que/show {file_path=file to display}
    """

    def data_received(self, chunk):
        pass

    def format_queues(self, file_name_data, file_data):
        """
        Determine defined queues and queues that actually exist.
        List them and make them clickable for drilling-down.
        @DEV: When creating the JS event listener dynamically, its function call needs to be cast as a function.
          Not sure why this is so, but if we don't do this, the function gets called on page load instead of on click.
          Something to do with closure I think, but not sure I can explain it.
        """
        self.admin_html = dict()

        def format_q_head():
            """ Page title and menu buttons"""
            self.admin_html['page_title'] = 'BoW Queues'
            self.admin_html = set_std_menus(self.admin_html)

        def format_q_file_content(file_name_data, file_data):
            """ File title, file content, format of content display """
            file_html = ''
            if file_name_data is None:
                file_name_data = dict()
                file_name_data['file_path'] = 'File content displays here'
                file_name_data['file_fmt'] = 'json'
            if file_data is not None:
                if file_name_data['file_fmt'] == 'python':
                    file_html = str(file_data)
                elif file_name_data['file_fmt'] == 'text':
                    _, file_jq = FB.run_cmd(["cat {} | jq .".format(file_name_data['file_path'])])
                    file_html = file_jq.decode("utf-8").replace("\n", "<br />")
                    file_html = file_html.replace("{<br />", "<br />{<br />")
                    file_html = file_html.replace("}<br />]<br />", "}<br /><br />]<br />")
                else:
                    file_html = json.dumps(file_data)
            self.admin_html['df_preset'] = file_name_data['file_fmt']
            self.admin_html['file_name'] = file_name_data['file_path']
            self.admin_html['file_content'] = file_html

        def format_q_file_lists():
            """ Locations and names of various type of queue files """
            locations = [('In-Memory', options.memdir),
                         ('Persistent', options.appdir + '/' + options.datdir),
                         ('Archived', options.appdir + '/' + options.arcdir)]
            self.admin_html['que_items'] = str()
            tbl_hdr_html = '<table class="datum"><tr><th class="gray" colspan="2">{}: {}</th></tr>'
            self.admin_html['dynamic_js'] = str()
            for loc in locations:
                self.admin_html['que_items'] += tbl_hdr_html.format(loc[0], loc[1])
                self.admin_html['que_items'] += '<tr><th class="gray">{}</th>'.format('Defined')
                self.admin_html['que_items'] += '<th class="gray padleft">{}</th></tr>'.format('Existing')
                for _, file_list in DATA.items():
                    for _, filenm in file_list.items():
                        file_path = path.join(loc[1], filenm)
                        self.admin_html['que_items'] += '\n<tr><td>{}</td>'.format(filenm)
                        if path.isfile(file_path):
                            # If the file actually exists...
                            file_id = file_path.replace('_', '').replace('.', '').replace('/', '')
                            self.admin_html['que_items'] += '<td class="padleft">'
                            self.admin_html['que_items'] +=\
                                '<span class="clickable" id="{}">{}</span></td></tr>'.format(file_id, filenm)
                            self.admin_html['dynamic_js'] += '\ndocument.getElementById("' + file_id + '")'
                            # The JS function call must be cast explicitly as a function:
                            self.admin_html['dynamic_js'] += '.addEventListener("click", function () '
                            self.admin_html['dynamic_js'] += '{ admin.showData("' + file_path + '"); });'
                self.admin_html['que_items'] += '\n</table>'

        format_q_head()
        format_q_file_content(file_name_data, file_data)
        format_q_file_lists()
        return self.admin_html

    def get(self, *args, **kwargs):
        """
        Handle GET requests for admin/que
        """
        sess_id = args[0] if len(args) > 0 else None
        file_name_data = None
        file_data = None
        if sess_id is not None:
            # @DEV Need to handle case where session ID has been deleted or expired
            file_name_rec = dict()
            file_name_rec = FQ.get_records(path.join(options.memdir, DATA['admin']['ses']), p_key=sess_id, p_latest=True)
            file_name_data = FQ.get_record_data(file_name_rec)
            file_data = FQ.get_records(file_name_data['file_path'], p_latest=True)
        admin_html = self.format_queues(file_name_data, file_data)
        self.render(HTML_NM, **admin_html)

    def post(self, *args, **kwargs):
        """
        Handle POST requests for admin/que
        admin/que {file_path=file to display}
        """
        # Get POST attributes
        req_data = {'file_path': self.get_argument('file_path'),
                    'file_fmt': self.get_argument('file_fmt')}
        # Create a session ID
        sess_id = str(FB.hash_me(str(FB.get_dttm().curr_ts), BC.SHA1))
        # Save session state
        FQ.write_queue(path.join(options.memdir, DATA['admin']['ses']), sess_id, req_data, p_end_rec=False)
        self.redirect("/admin/que/{}".format(sess_id))

class AdminServers(web.RequestHandler):
    """
    Manage and monitor services, processes, jobs
    GET [admin/srv, admin/srv/{.*}]
    POST admin/srv/{.*}
    """

    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for admin/srv
        """
        admin_html = dict()
        admin_html['page_title'] = 'BoW Servers and Processes'
        admin_html = set_std_menus(admin_html)
        admin_html['srv_items'] = str()

        FB.log_me("APPS {}".format(str(APPS)), LOG, options.loglevel)

        for app_nm, app_dat in APPS.items():
            admin_html['srv_items'] += '<table class="datum"><tr><th class="gray">{} {}</th></tr>'.format(app_nm, 'Servers')
            _, result = FB.run_cmd('ps -ef | grep -v grep | grep root | grep {}'.format(app_dat['py']))
            rslt_a = result.decode("utf-8").split('\n')
            for rslt in rslt_a:
                admin_html['srv_items'] += '<tr><td>{}</td></tr>'.format(rslt)
            admin_html['srv_items'] += '<tr><td><a href="{}" target="_blank">{}</a></td></tr>'.format(app_dat['url'],
                                                                                                      app_dat['url'])
            admin_html['srv_items'] += '\n</table>'
        self.render(HTML_NM, **admin_html)

class AdminLogs(web.RequestHandler):
    """
    Manage and monitor logs
    GET [admin/log, admin/log/{*}]

    POST admin/log/{*}
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for admin/log
        """
        admin_html = dict()
        admin_html['page_title'] = 'BoW Logs'
        admin_html = set_std_menus(admin_html)
        admin_html['log_items'] = str()
        for app, lognms in LOGS.items():
            admin_html['log_items'] += '<table class="datum"><tr><th class="gray">{} {}</th></tr>'.format(app, 'Logs')
            for _, flnm in lognms.items():
                admin_html['log_items'] += '\n<tr><td>{}</td></tr>'.format(path.join(options.memdir, flnm))
            admin_html['log_items'] += '\n</table>'
        self.render(HTML_NM, **admin_html)

    def post(self, *args, **kwargs):
        """
        Handle POST requests for admin/log
        """
        pass

class AdminAJAX(web.RequestHandler):
    """
    Ajax interface to return a JSON data set
    POST [admin/data, admin/data/] {file_nm}
    """
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        """
        Handle POST requests for admin/data {file_path}
        :Args:
        - File name is full path to a file or queue
        """
        file_nm = self.get_argument('file_path')
        file_data = FQ.get_records(file_nm)
        # Hand the full file back to the caller in JSON format
        self.set_header('Content-Type', 'text/json')
        self.write(json.dumps(file_data))

class AdminREST(web.RequestHandler):
    """
    Handle REST messages
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for admin/msg/{message-value}
        """
        pass

class AdminMeta(web.RequestHandler):
    """
    Get meta-data about admin/ services
    HEAD, GET /admin, /admin/(.*), /meta, /meta/(.*)
    """
    def data_received(self, chunk):
        pass

    def set_hdr_msg(self):
        """ List acceptable URLs in format suitable for display.
        """
        msgs = list()
        msgp = namedtuple('msgp', 'desc protocol path ')
        msgs.append(msgp('Manage queues', ['GET', 'POST'], ['/admin/que/(.*)'])._asdict())
        msgs.append(msgp('Manage servers and jobs', ['GET', 'POST'], ['/admin/srv/(.*)'])._asdict())
        msgs.append(msgp('Manage logs', ['GET', 'POST'], ['/admin/log/(.*)'])._asdict())
        msgs.append(msgp('AJAX data request', ['POST'], ['/admin/data {file_nm}'])._asdict())
        msgs.append(msgp('REST messages', ['GET'], ['/admin/msg/{msg-value}'])._asdict())
        msgs.append(msgp('Get services metadata', ['HEAD', 'GET'], ['/admin/(.*)', '/admin/meta/*'])._asdict())
        msgs.append(msgp('Get robots.txt context', ['GET'], '/robots.txt')._asdict())
        self.set_header('Meta-Messages-List', json.dumps(msgs))
        return json.dumps(msgs)

    def head(self, *args, **kwargs):
        """ Write informational messages as header. """
        self.set_hdr_msg()

    def get(self, *args, **kwargs):
        """ Write informational messages as header and in body. """
        self.write(self.set_hdr_msg())

class AppException(web.HTTPError):
    """ Override Tornado's web.HTTPError. Use flask_api.status codes instead
    """
    pass

class RobotHandler(web.RequestHandler):
    """
    GET /robots.txt
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """ Write robots.txt content to body """
        with open(options.static + '/robots.txt', 'r') as robot_f:
            self.write(robot_f.read())

class AdminErr(web.RequestHandler):
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
            (r"/admin/que", AdminQueues),
            (r"/admin/que/", AdminQueues),
            (r"/admin/que/(.*)", AdminQueues),
            (r"/admin/srv", AdminServers),
            (r"/admin/srv/", AdminServers),
            (r"/admin/srv/(.*)", AdminServers),
            (r"/admin/log", AdminLogs),
            (r"/admin/log/", AdminLogs),
            (r"/admin/log/(.*)", AdminLogs),
            (r"/admin/data", AdminAJAX),
            (r"/admin/data/", AdminAJAX),
            (r"/admin/data/(.*)", AdminAJAX),
            (r"/admin/msg", AdminREST),
            (r"/admin/msg/", AdminREST),
            (r"/admin/msg/(.*)", AdminREST),
            (r"/admin/meta", AdminMeta),
            (r"/admin/meta/", AdminMeta),
            (r"/admin/meta/(.*)", AdminMeta),
            (r"/admin", AdminQueues),
            (r"/admin/", AdminQueues),
            (r"/admin/(.*)", AdminQueues),
            (r"/robots.txt", RobotHandler),
            (r"/(.*)", AdminErr)],
        **settings
    )

    FB.log_me("Starting up admin_bow.py at {}{}:{}".format(protocol, HOST_NM, str(options.port)),
              LOG, options.loglevel)
    # For local prototypes without a real Domain, only use secure = 0
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
    # Define and collect options.
    # See: https://www.tornadoweb.org/en/stable/options.html
    # Note that the location of the config file is passed in as a cmd line option.
    # Command line configs
    define("port", help="Port to run app instance under", type=int)
    define("secure", help="Run under TLS if true", type=int)
    define("conf", help="Relative path to config file", type=str)
    options.parse_command_line(final=False)
    protocol = 'https://' if options.secure else 'http://'
    # Config file configs
    # Anything I want to pull in from the file has to be defined.
    define("loglevel", help="Debug and log level")
    define("internal_host", help="Internal host IP")
    define("static", help="Location of static resources")
    define("templates", help="Location of HTML templates")
    define("pix", help="Location of graphic resources")
    define("appdir", help="Root location of app resources")
    define("arcdir", help="On-disk archive data storage location")
    define("datdir", help="On-disk data storage location")
    define("memdir", help="In-memory data storage path")
    define("apps", help="List of supported app names")
    define("domains", help="List of domain names aligned to app names")
    define("htmls", help="List of HTML templates aligned to app names")
    define("paths", help="List of default paths aligned to apps")
    define("dmn_host", help="Host name")
    define("pyapp_nm", help="Python app file name")
    define("html_nm", help="HTML template file name")
    define("dat_fil", help="Data queue name")
    define("ctl_fil", help="Name of storage control files")
    define("ses_fil", help="Name of session state storage files")
    define("run_log", help="Log queue name")
    define("job_log", help="Log queue name")
    define("pid_log", help="Log queue name")
    options.parse_config_file(options.conf)

    this_app_nm = 'admin'
    app_nms = options.apps.split(',')
    app_ix = app_nms.index(this_app_nm)
    domain_nms = options.domains.split(',')
    domain_nm = domain_nms[app_ix]
    HTML_NM = options.htmls.split(',')[app_ix] + options.html_nm
    HOST_NM = domain_nm + options.dmn_host
    APPS = dict()
    DATA = dict()
    LOGS = dict()
    for app_nm in app_nms:
        APPS[app_nm] = dict()
        APPS[app_nm]['py'] = app_nm + options.pyapp_nm
        APPS[app_nm]['url'] = 'https://' + domain_nms[app_nms.index(app_nm)] + options.dmn_host +\
                              '/' + options.paths.split(',')[app_nms.index(app_nm)]
        DATA[app_nm] = dict()
        DATA[app_nm]['dat'] = app_nm + options.dat_fil
        DATA[app_nm]['ctl'] = app_nm + options.ctl_fil
        DATA[app_nm]['ses'] = app_nm + options.ses_fil
        LOGS[app_nm] = dict()
        LOGS[app_nm]['run'] = app_nm + options.run_log
        LOGS[app_nm]['job'] = app_nm + options.job_log
        LOGS[app_nm]['pid'] = app_nm + options.pid_log

    LOG = path.join(options.memdir, LOGS[this_app_nm]['run'])
    FB.log_me("DATA: {}".format(str(DATA)), LOG, options.loglevel)
    FB.log_me("LOGS: {}".format(str(LOGS)), LOG, options.loglevel)
    FB.log_me("APPS: {}".format(str(APPS)), LOG, options.loglevel)

    main()
