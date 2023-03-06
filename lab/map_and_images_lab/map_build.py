#!/bin/python3.6
"""
Map Maker App

@DEV:
- Heh! A few years later...
- Use PyGame, not Tornado, as foundation.
- Use PyGame, not SVG (for the most part).
- Use SVG if useful in some cases, but likely
   can do much the same with Pyame drawing prims.
- Focus more attention on integrating artwork.
    - Do drawings, paintings to import.
    - Play around with Blender more.
    - Overlay, reiterpret and recombine for game play.
- See what can be accmoplished using ChatGPT and
    various AI art generation techniques.
- Where it makes sense to use services, sure, but
    don't get too obsessed with that. Try to focus
    on getting working prototypes.
- Wrap this under a PyGame "Saksan Game" engine.
- Create sprites for the various map elements, including
  characters and non-player characters.
    - Do little sketches (pencil, pen) of the characters
- Maybe focus first on tying sprint movement to road
  locations and then expand from there.
- For example, provide simple functions to determine
  travel time between towns.
"""
# pylint: disable=E0401
# pylint: disable=E0602
# pylint: disable=R0903
# pylint: disable=R1710
# pylint: disable=W0221
# pylint: disable=W0223
# pylint: disable=W0611
# pylint: disable=W0702

## General Purpose imports     ##
#################################
from pprint import pprint as pp
from http.client import responses
from os import path

## Tornado and Jinja2          ##
#################################
import jinja2
from tornado import httpserver, ioloop, web
from tornado.options import define, options
from flask_api import status
from tornado_jinja2 import Jinja2Loader

## Local Classes, Objects      ##
#################################
from c_map_prims import MapMsg, MakeMap
from c_map_html import MapHtml
HM = MapHtml()
MS = MapMsg()
MM = MakeMap()

## Local methods that interface with local objects ##
#####################################################

def make_map(msg):
    """ Send message to the map maker, then assemble code if result is sucessful.
        This updates the map data catalog and (re-)generates the SVG code.

        The backend is broken into two parts in order to simulate the possibilities for
        backend message queueing and so forth.  Could make it a single object.

        Trap for failures and translate that into a HTTP status code.
        We could also make presentation of such failures a little bit nicer.

        Start thinking about asychronous calls and responses...
    """
    try:
        # pp(("msg: ", msg))
        MS.make(msg, MM)
        MM.assemble()
    except:
        # Use status code constants from the reponses Class because they are very explicit.
        err = "{0}, ".format(responses[status.HTTP_500_INTERNAL_SERVER_ERROR]) +\
            "Problem making or assembling the Map. See logs for more info."
        raise AppException(
            reason=err, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#        raise tornado.web.HTTPError(status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_svg_data():
    """ Load current catalog of SVG data
        Returns data in SVG form & "Update" or "Create" signal by calling make_svg_form()
    """
    attrs = ['id', 'desc', 'name', 'title', 'style', 'width', 'height']
    vals = {}
    for attr in attrs:
        vals["svg_{0}".format(attr)] = ""
    catalog = MM.get_catalog()
    if 'svg' in catalog:
        for attr in ['id', 'desc', 'name', 'title', 'style']:
            item_nm = "svg_{0}".format(attr)
            vals[item_nm] = catalog['svg']['msg'][attr]
            if vals[item_nm] in ['None', None]:
                vals[item_nm] = ''
        vals['svg_width'] = str(catalog['svg']['msg']['size_xy'][0])
        vals['svg_height'] = str(catalog['svg']['msg']['size_xy'][1])
    return HM.make_svg_form(vals)

def get_data(p_dom, p_add=False):
    """ Load current catalog of data for designated domain
        Return data in HTML forms by calling the appropriate HM.make_*_forms() method
    """
    vals = {}
    keys = {'ref': ['id', 'path', 'itmtyp'],
            'grp': ['id', 'desc', 'gid', 'fill', 'stroke', 'thick', 'opaq', 'dash', 'move', 'zix'],
            'elm': ['id', 'desc', 'gid', 'draw', 'loc_xy', 'size_xy', 'zix', 'tabix']}
    catalog = MM.get_catalog()
    num = 0
    if p_dom in catalog:
        for key, item in catalog[p_dom].items():
            num += 1
            vals[num] = {}
            vals[num]["{0}_num".format(p_dom)] = str(num)
            vals[num]["{0}_id".format(p_dom)] = key
            for attr in keys[p_dom]:
                if attr != 'id':
                    item_nm = '{0}_{1}'.format(p_dom, attr)
                    if item['msg'][attr] in ['None', None]:
                        vals[num][item_nm] = ''
                    else:
                        vals[num][item_nm] = item['msg'][attr]
    if p_add:
        # Add empty data for a new item
        num += 1
        vals[num] = {}
        vals[num]['{0}_num'.format(p_dom)] = str(num)
        for attr in keys[p_dom]:
            if attr[-2:] == 'xy':
                vals[num]['{0}_{1}'.format(p_dom, attr)] = (0, 0)
            else:
                vals[num]['{0}_{1}'.format(p_dom, attr)] = ''

    # pp(("get_data vals: ", vals))
    make_form = {'ref': HM.make_ref_forms,
                 'grp': HM.make_grp_forms,
                 'elm': HM.make_elm_forms}
    return make_form[p_dom](vals)

    # if p_dom == 'ref':
    #    return HM.make_ref_forms(vals)
    #if p_dom == 'grp':
    #    return HM.make_grp_forms(vals)
    ##    return HM.make_elm_forms(vals)

## Local methods that support the map_build app ##
############################################

def get_info():
    """ Get the service catalog for this app """
    return (
        {'PROTOCOL': 'http',
         'PATH': '<domain>',
         'PORT': '8080',
         '/': [item.strip() for item in IndexHandler.__doc__.strip().split('\n')],
         '/map': [item.strip() for item in MapHandler.__doc__.strip().split('\n')],
         '/menu': [item.strip() for item in MenuHandler.__doc__.strip().split('\n')],
         '/svg': [item.strip() for item in SVGHandler.__doc__.strip().split('\n')],
         '/ref': [item.strip() for item in RefHandler.__doc__.strip().split('\n')],
         '/grp': [item.strip() for item in GrpHandler.__doc__.strip().split('\n')]
        })

def render_html():
    """ Generic dict of things to render """
    HM.make_menu_buttons()
    return({"menu_btns": HM.menu_btns,
            "svg_form": HM.svg_form,
            "ref_btns": HM.ref_btns,
            "ref_forms": HM.ref_forms,
            "grp_btns": HM.grp_btns,
            "grp_forms": HM.grp_forms,
            "elm_btns": HM.elm_btns,
            "elm_forms": HM.elm_forms,
            "svg_code": HM.svg_code})

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

    def get(self):
        """ Return text describing this service."""
        # msg = "Services for building an SVG map:"
        self.write(get_info())

    def head(self):
        """ Return app service catalog as a JSON list in the response header.
            May want to look at the OAS standard for how best to label this section.
            Just providing this as an example of how to add more content to a header response.
            The idea would be to make it easy to build automated hooks into the catalog.
        """
        self.set_header('catalog', get_info())

class MenuHandler(web.RequestHandler):
    """
    POST /menu/map
    POST /menu/svg
    POST /menu/ref
    """
    def post(self, sub_path):
        """ Show/hide forms based on use of "menu" buttons. """
        if sub_path == 'res':
            HM.clear()  # wipe everything
            self.render('create.html', **render_html())
        else:
            goto = {'map': '/map', 'svg': '/svg',
                    'ref': '/ref/list', 'grp': '/grp/list', 'elm': '/elm/list'}
            # Get "showing" value from hidden input
            # Flip the "showing mode" quality of the clicked menu item
            # Unless it is the "res" (Wipe) menu item, which always has "mode" 'True'
            show_mode_arg = 'show_{0}'.format(sub_path)
            show_mode_val = self.get_argument(show_mode_arg)
            # Adjust "showing" modes depending on what was clicked + current mode
            if sub_path != 'res':
                HM.set_show_mode(sub_path, 'True' if show_mode_val == 'False' else 'False')
            if sub_path == 'map':
                HM.set_show_mode(['svg', 'ref', 'grp'], 'True')
            else:
                HM.set_show_mode('map', 'True')
            HM.svg_code = ''    # Wipe the map display
            if show_mode_val == 'True':
                self.redirect(goto[sub_path])  # Trigger GET redirect URL
            else:
                # Wipe the appropriate display(s)
                if sub_path == 'svg':
                    HM.svg_form = ''
                elif sub_path == 'ref':
                    HM.ref_btns = ''
                    HM.ref_forms = ''
                elif sub_path == 'grp':
                    HM.grp_btns = ''
                    HM.grp_forms = ''
                self.render('create.html', **render_html())

class MapHandler(web.RequestHandler):
    """
    GET /map
    """
    def get(self):
        """ Handle redirects from menu handler. Display the rendered SVG file. """
        HM.clear()
        HM.set_show_mode(['map'], 'False')
        HM.svg_code = MM.get_code()
        self.render('create.html', **render_html())

class SVGHandler(web.RequestHandler):
    """
    GET /svg
    POST /svg/edit
    POST /svg/delete
    """

    def get(self):
        """ Refresh SVG data from catalog, if it exists, else present an empty form.
        """
        HM.set_show_mode(['svg'], 'False')
        get_svg_data()
        self.render('create.html', **render_html())

    def post(self, sub_path):
        """ Process form for creating/updating SVG header.
            Call back-end engine objects to assemble map data and SVG object.
            Refresh the form with results.
            @DEV - Front-end edits
            @DEV - More graceful HTTP error displays
            @DEV - Don't allow an ID to be updated
        """
        if sub_path == 'delete':
            # Wipe back-end content and HTML content
            MS.clear()
            MM.clear()
            HM.clear()
        else:
            # Create message for back-end:
            msg = {}
            msg['type'] = 'svg'
            msg['id'] = self.get_argument('svg_id')
            msg['desc'] = self.get_argument('svg_desc')
            msg['name'] = self.get_argument('svg_name')
            msg['title'] = self.get_argument('svg_title')
            msg['size_xy'] = (self.get_argument('svg_width'), self.get_argument('svg_height'))
            msg['style'] = self.get_argument('svg_style')
            make_map(msg)  # Send message to update map data catalog and generate SVG code
            get_svg_data()

        self.render('create.html', **render_html())

class RefHandler(web.RequestHandler):
    """
    GET /ref/list
    POST /ref/list
    POST /ref/add
    POST /ref/edit
    POST /ref/delete
    """
    def get(self, _):
        """ Handle menu-driven redirects. Display list/add buttons. """
        HM.set_show_mode('ref', 'False')
        HM.make_add_list_buttons('ref')
        self.render('create.html', **render_html())

    def post(self, sub_path):
        """ Handle adds/updates/deletes for reference items.
            Refresh display of REF items.
        """
        HM.set_show_mode('ref', 'False')
        HM.make_add_list_buttons('ref')
        if sub_path in ['edit', 'delete']:
            msg = {}
            msg['type'] = 'ref'
            msg['id'] = self.get_argument('ref_id')
            msg['path'] = self.get_argument('ref_path')
            msg['itmtyp'] = self.get_argument('ref_itmtyp')
            msg['delete'] = True if sub_path == 'delete' else False
            make_map(msg)  # Update catalog and generate SVG code
        get_data('ref', True if sub_path == 'add' else False)
        self.render('create.html', **render_html())

class GrpHandler(web.RequestHandler):
    """
    GET /grp/list
    POST /grp/list
    POST /grp/add
    POST /grp/edit
    POST /grp/delete
    """
    def get(self, _):
        """ Handle menu-driven redirects.  Display list/add buttons. """
        HM.set_list_btns('grp')
        self.render('create.html', **render_html())

    def post(self, sub_path):
        """ Handle adds/updates/deletes for group items.
            Refresh display of GRP items.
        """
        HM.set_list_btns('grp')
        if sub_path in ['edit', 'delete']:
            msg = {}
            msg['type'] = 'grp'
            msg['id'] = self.get_argument('grp_id')
            msg['desc'] = self.get_argument('grp_desc')
            msg['gid'] = self.get_argument('grp_gid')
            msg['fill'] = self.get_argument('grp_fill')
            msg['stroke'] = self.get_argument('grp_stroke')
            msg['thick'] = self.get_argument('grp_thick')
            msg['opaq'] = self.get_argument('grp_opaq')
            msg['dash'] = self.get_argument('grp_dash')
            msg['move'] = self.get_argument('grp_move')
            msg['zix'] = self.get_argument('grp_zix')
            msg['delete'] = True if sub_path == 'delete' else False
            make_map(msg)  # Update catalog and generate SVG code
        get_data('grp', True if sub_path == 'add' else False)
        self.render('create.html', **render_html())

class ElmHandler(web.RequestHandler):
    """
    GET /elm/list
    POST /elm/list
    POST /elm/add
    POST /elm/edit
    POST /elm/delete
    """
    def get(self, _):
        """ Handle menu-driven redirects. Display list/add buttons.  """
        HM.set_list_btns('elm')
        self.render('create.html', **render_html())

    def post(self, sub_path):
        """ Handle adds/updates/deletes for element items.
            Refresh display of ELM items.
        """
        HM.set_list_btns('elm')
        if sub_path in ['edit', 'delete']:
            msg = {}
            msg['type'] = 'elm'
            msg['id'] = self.get_argument('elm_id')
            msg['desc'] = self.get_argument('elm_desc')
            msg['gid'] = self.get_argument('elm_gid')
            msg['draw'] = self.get_argument('elm_draw')
            msg['loc_xy'] = (self.get_argument('elm_loc_x'),
                             self.get_argument('elm_loc_y'))
            msg['size_xy'] = (self.get_argument('elm_size_x'),
                              self.get_argument('elm_size_y'))
            msg['zix'] = self.get_argument('elm_zix')
            msg['tabix'] = self.get_argument('elm_tabix')
            msg['delete'] = True if sub_path == 'delete' else False
            make_map(msg)  # Update catalog and generate SVG code
        get_data('elm', True if sub_path == 'add' else False)
        self.render('create.html', **render_html())

class ErrHandler(web.RequestHandler):
    """
    GET /{err}
    """
    def get(self, _):
        """ Capture all error displays.  """
        print("Generic error handler trapped it..")
        pp((Tornado.web.HTTPError))
        raise tornado.web.HTTPError(status.HTTP_500_INTERNAL_SERVER_ERROR)

def main():
    """ Launch the app """
    define("port", default=8080, help="map constructor", type=int)
    options.parse_command_line()
    # Create a instance of Jinja2Loader
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),
                                    autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    # Give it to Tornado to replace the default template  Loader.
    settings = dict(template_loader=jinja2_loader,
                    static_path=path.join(path.dirname(__file__), "static"),
                    debug=True)
    #                debug=False)
    # Associate message patterns to services.
    app = web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/menu/(\w+)", MenuHandler),
            (r"/map", MapHandler),
            (r"/svg", SVGHandler),
            (r"/svg/(\w+)", SVGHandler),
            (r"/ref/(\w+)", RefHandler),
            (r"/grp/(\w+)", GrpHandler),
            (r"/elm/(\w+)", ElmHandler)],
        #    (r"/(.*)", ErrHandler)],
        **settings
    )
    http_server = httpserver.HTTPServer(app)
    # Run a single instance. Next we'll work on running it behind a load balancer.
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    """
    Web (HTTP) API built using Tornado demonstrating GET, HEAD, POST and PATCH.

    Things to remember from this lesson:
    * A single 'Handler' class may handle more than one service.
    * Do this if calls are closely related.
        For example, a GET and a HEAD for the same path.
    * Use Jinja2 rather than the default Tornado templating system.

    New in this example:
    * Handling closely-related calls in the same handler.
    * Connecting (synchronously) to a back-end service.
        The backend "engine" in this case building a map object using SVG syntax.
        It creates an SVG object which is returned to the caller.
    * POST is used to create a new SVG object.
    * PATCH is used to update it.
    * HEAD is used to get information about the service catalog.
    * Moved "main" logic into a function.
    * How to integrate with Jinja2.

    Notes:
    * Some very useful testing tools include:
        * command line tools: curl, httpie, siege
        * browser tools: postman
    * Look at tornado docs on options for putting up multiple instances of the app on one port
        but in all available cores:  http://www.tornadoweb.org/en/stable/guide/running.html
      While that is interesting and works fine, it will be better to run multiple instances
        of the app using different ports, behind a load balancer (NGINX).
        That will be addressed in the next exercise after this one..

    REQUEST:
        BASE PATH:     <domain>
        @DEV -- will probably want to qualify this further like <domain>/map
        VERB(S):  GET, HEAD, POST, PATCH

    """
    main()
