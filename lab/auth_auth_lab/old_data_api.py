#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 9 2016
This is a twisted-only version of a data API.
I'd like to see if I can't use Tornado to do the same thing, but a little easier to read/manage.

@author: dave

===============================
Start up this server: python bow_data.py

Request JSON API's via GET under http://ananda:8080/

* Childless API:
*  /                Return a metalist of available GET APIs
*  /meta            Same as /

* API's with children:
*  /actors          Info about all available actors, including page size
*  /actors/<n>      A page of actor records
*  /actors/<id>     Specific actor record
*  /items           Info about all available items including page size
*  /items/<n>       A page of item records
*  /items/<id>      Specific item record
*  /places          Info about all available places, including page size
*  /places/<n>      A page of place records
*  /places/<id>     Specific place record
"""

import hashlib
import json
from datetime import datetime, timedelta
from os import path
from pprint import pprint as pp
import pytz
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.task import deferLater
from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File

# ================================================
# Generic "private" functions
# ================================================
def _get_time():
    """ Get date-time in UTC """
    local_tz = pytz.timezone("America/New_York")
    local_dttm = local_tz.normalize(local_tz.localize(datetime.now()))
    utc_dttm = local_dttm.astimezone(pytz.utc)
    utc_now = utc_dttm.strftime("%a, %d %b %Y %H:%M:%S %Z")
    utc_dttm_plus1 = utc_dttm + timedelta(days=1)
    utc_plus1day = utc_dttm_plus1.strftime("%a, %d %b %Y %H:%M:%S %Z")
    return(utc_now, utc_plus1day)

def _get_env():
    """
    Generic function to provide environmental values.
    Args:
        A valid timezone like "America/New_York" or None
    Returns:
        {env_values dict}
    """
    hostpath = "/home/dave/Projects/appdev/bow04"
    apppath = "bow/public"
    datapath = "data/json/api/"
    apipath = path.join(hostpath, apppath, datapath)
    (utc_now, utc_plus1day) = _get_time()

    envvals = {"apipath": apipath,
               "json": "application/json",
               "Cj": "application/vnd.collection+json",
               "html": "text/html",
               "utc_now": utc_now,
               "utc_plus1day": utc_plus1day
              }
    return envvals

# ================================================
# Generic Class. Inherits from twisted Resource.
# ================================================
class BowResource(Resource):
    """
    Generic class for Bow API's. Default assumption is that they do have
    child URIs, so isLeaf is not set to True in the generic class.
    Sets headers, manages body, renders response for bow_data API's.
    """
    bow_data = {}
    cj_data = {}
    bow_text = ""
    cj_text = ""
    e_vals = _get_env()
    datafile = ""

    #pylint: disable-msg=R0201
    #pylint: disable-msg=W0613
    def response_failed(self, err, call):
        """ Handle errback if render fails. """
        pp(str(err))
        call.cancel()

    def delayed_render(self, request):
        """
        Callback to finish the request once resource is available.
        This is implemented/overridden in the inherited classes.
        """
        pass

    #pylint: disable-msg=C0103
    #pylint: disable-msg=W0613
    def render_GET(self, request):
        """
        Return JSON for bow_data meta API, using deferred call backs.
        """
        call = deferLater(reactor, 0, lambda: request)
        call.addCallback(self.delayed_render)
        request.notifyFinish().addErrback(self.response_failed, call)
        return NOT_DONE_YET

    def get_data(self, media, filename):
        """
            Read body data from sources.
            Parse body data into dict if it is JSON data.
            Break out "collection" data and text if JSON uses the
              Collection+JSON format.
            All of the data and parsed data is stored in class attributes.
        """
        self.datafile = path.join(self.e_vals["apipath"], filename)
        with open(self.datafile, 'rb') as fobj:
            self.bow_text = fobj.read().replace('\n', '').replace('\t', '')
        if media in ["Cj", "json"]:
            self.bow_data = json.loads(self.bow_text)
            if "collection" in self.bow_data:
                self.cj_data = self.bow_data["collection"]
                self.cj_text = json.dumps(self.cj_data)

    def set_md5_and_etag(self, request):
        """
            Compute md5 hash.
            For APIs that use collection+json, the hash is only for the
            "collections" part of the response.  The "audit" part of the
            response is not part of the standard.
        """
        if "collection" in self.bow_data:
            md5_hash = hashlib.md5(self.cj_text).hexdigest()
        else:
            md5_hash = hashlib.md5(self.bow_text).hexdigest()
        request.setHeader('Content-MD5', md5_hash)
        request.setHeader('Etag', md5_hash)
        return md5_hash

    def reset_audit_data(self, md5_hash):
        """ Determine if data has changed. If so, reset audit info. """
        if ("audit" in self.bow_data and\
        "last_mod_md5" in self.bow_data["audit"] and\
        self.bow_data["audit"]["last_mod_md5"] != md5_hash) or\
        "audit" not in self.bow_data:
            self.bow_data["audit"] = {
                "last_mod_md5": md5_hash,
                "last_mod_dt": self.e_vals["utc_now"]
            }
            self.bow_text = json.dumps(self.bow_data)
            with open(self.datafile, 'wb') as fobj:
                fobj.write(self.bow_text)

    def set_last_mod_date(self, request):
        """ Set Last-Modfified header value """
        if "audit" in self.bow_data and\
        "last_mod_dt" in self.bow_data["audit"]:
            request.setHeader('Last-Modified',
                              self.bow_data["audit"]["last_mod_dt"])
        else:
            request.setHeader('Last-Modified', self.e_vals["utc_now"])

    def set_headers(self, media, request):
        """
        Generic function to set common response header values.

        Args:
            media           Key to mediatype value.
            request         A request object.
        Returns:
            Modified request object.
        """
        e_vals = _get_env()
        if media not in e_vals:
            media = "html"
        request.setHeader('Date', e_vals["utc_now"])
        request.setHeader('Content-Language', 'en-US')
        request.setHeader('Expires', e_vals["utc_plus1day"])
        request.setHeader('Content-Type', e_vals[media] + "; charset=utf-8")
        md5_hash = self. set_md5_and_etag(request)
        self.reset_audit_data(md5_hash)
        self.set_last_mod_date(request)
        request.setHeader('Content-Length', len(self.bow_text))
        return request

    def write_response(self, request):
        """ Send HTTP response. """
        request.write(self.bow_text)
        request.finish()

    def do_render(self, media, filename, request):
        """
        Execution logic for delayed_render, using args from specific API.
        """
        self.get_data(media, filename)
        request = self.set_headers(media, request)
        self.write_response(request)

# ================================================
# API-Specific Classes. Inherit from BowResource.
# ================================================
class BowMeta(BowResource):
    """
        Meta (ToC) data API.
        This is a childless API, so we set isLeaf to True.
        If the URI is extended like meta/1/1/1... it has no effect, only the
        "meta" part is handled.
    """
    isLeaf = True
    #pylint: disable-msg=R0201
    def delayed_render(self, request):
        """ Callback to finish the request once resource is available. """
        self.do_render('Cj', 'meta.json', request)

class BowActors(BowResource):
    """ Actors data API. """
    #pylint: disable-msg=R0201
    def delayed_render(self, request):
        """ Callback to finish the request once resource is available. """
        self.do_render('Cj', 'actors.json', request)

    def getChild(self, name, request):
        """ Handle child-level Actors call """
        if name == '':
            return self
        else:
            pp(("actors child:", name))
            return NoResource()

class BowPlaces(BowResource):
    """ Places data API. """
    #pylint: disable-msg=R0201
    def delayed_render(self, request):
        """ Callback to finish the request once resource is available. """
        self.do_render('Cj', 'places.json', request)

    def getChild(self, name, request):
        """ Handle child-level Places call """
        if name == '':
            return self
        else:
            pp(("places child:", name))
            return NoResource()

class BowItems(BowResource):
    """ Items data API. """
    #pylint: disable-msg=R0201
    def delayed_render(self, request):
        """ Callback to finish the request once resource is available. """
        self.do_render('Cj', 'items.json', request)

    def getChild(self, name, request):
        """ Handle child-level Items call """
        if name == '':
            return self
        else:
            pp(("items child:", name))
            return NoResource()

# ================================================
# Main-line function.
# ================================================
def run_server():
    """ Create the BoW Data factory """
    e_vals = _get_env()
    root = File(e_vals["apipath"])
    root.putChild("", BowMeta())
    root.putChild("meta", BowMeta())
    root.putChild("actors", BowActors())
    root.putChild("places", BowPlaces())
    root.putChild("items", BowItems())
    factory = Site(root)
    endpoint = TCP4ServerEndpoint(reactor, 8080, 50, "ananda")
    endpoint.listen(factory)
    print('Serving Bow Data APIs at http://ananda:8080/')
    reactor.run()                                #pylint: disable-msg=E1101

if __name__ == '__main__':
    """ Launch the BoW JSON data API server.
    """
    run_server()
