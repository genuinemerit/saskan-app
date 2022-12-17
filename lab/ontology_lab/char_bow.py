#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    char_bow

BoW Character Management tornado web app.
Front-end for chracter and context management at specified ports.
REST services for character management at specified ports

:author:    GM <genuinemerit@protonmail.com>
"""
import json
import math
import requests
import time
import os
import sys
from collections import namedtuple
import jinja2
from tornado import httpserver, web, ioloop
from tornado.options import define, options
from flask_api import status
from tornado_jinja2 import Jinja2Loader
# pylint: disable=import-error
from func_basic import FuncBasic
from func_queue import FuncQueue
from func_basic import BC

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
        raise ValueError(FB.log_me('Invalid sessid {}. Delete client cookie / Login again.'.format(cookie_sessid), LOG, BC.ERROR))
    sessdata = FQ.get_record_data(sessdata_rec)
    stored_sessid = sessdata['sessid']
    if cookie_sessid != stored_sessid:
        raise ValueError(FB.log_me('Invalid sessid {}. Delete client cookie / Login again.'.format(cookie_sessid), LOG, BC.ERROR))

def set_page_top():
    """
    Configure common page items
    :returns: {dict}
    """
    char_html = dict()
    char_html['page_title'] = 'Manage Characters'
    # menu buttons
    char_html['reset_btn'] = "Clear"
    char_html['load_btn'] = "Open"
    char_html['place_btn'] = "Place"
    char_html['genes_btn'] = "Genes"
    char_html['sex_btn'] = "Sex"
    char_html['karms_btn'] = "Karms"
    char_html['horde_btn'] = "Horde"
    char_html['fam_btn'] = "Fam"
    char_html['name_btn'] = "Name"
    char_html['time_btn'] = "Time"
    char_html['trait_btn'] = "Trait"
    char_html['fren_btn'] = "Freny"
    char_html['org_btn'] = "Orgs"
    char_html['bleev_btn'] = "Bleevs"
    char_html['fact_btn'] = "Facts"
    char_html['stuff_btn'] = "Stuff"

    char_html['save_btn'] = "Save"
    # modes
    char_html['menu_pick'] = ""
    # hide-show classes
    char_html['pick_action_class'] = 'hidden snow'
    char_html['pick_format_class'] = 'hidden snow'
    topics = ['place', 'genes', 'sex', 'karms', 'horde', 'fam', 'name', 'time',
              'trait', 'fren', 'org', 'bleev', 'fact', 'stuff']
    for topic in topics:
        char_html['{}_class'.format(topic)] = 'hidden snow'
    return char_html

def handle_buttons(args, topic_nm):
    """
    Generic logic for handling button-presses and states.

    :Args:

        - args {list} from the URL call
        - topic_nm {string} identifying button/edit collection
    """
    topic_note = {
        'place': "Places everyone!",
        'genes': "Gene genie, your face is mess!",
        'sex': "The lyricism of the masses",
        'karms': "What goes around comes around",
        'horde': "All for one, one for all",
        'fam': "There's no place like home",
        'name': "A rose by any other name...",
        'time': "Time waits for no one",
        'trait': "Persistence is a virtue",
        'fren': "Every friendship is different",
        'org': "Collective action creates shared responsibility",
        'bleev': "Whatever you believe is true",
        'fact': "Facts are stubborn things",
        'stuff': "The stuff that dreams are made of"
    }
    subtopic_note = {
        'place': 'Marking up the ',
        'genes': 'Sequencing the ',
        'sex': 'Performing the ',
        'karms': 'Accumulating the ',
        'horde': 'Taking census of the ',
        'fam': 'Rounding up the ',
        'name': 'Naming the ',
        'time': 'Watching the ',
        'trait': 'Calculating the ',
        'fren': 'Checking out the ',
        'org': 'Organizing the ',
        'bleev': 'Immanetizing the ',
        'fact': 'Examining the ',
        'stuff': 'Collecting the '
    }
    subtopics = {
        'place': ['closure', 'land', 'region', 'muni'],
        'genes': ['human', 'animal', 'crafted', 'mix'],
        'sex': ['biosex', 'gender', 'orient'],
        'karms': ['points', 'merit', 'demerit', 'inherit'],
        'horde': ['confed', 'tribe', 'clan'],
        'fam': ['class', 'rents', 'sibs'],
        'name': ['famnm', 'persnm', 'honor', 'alias'],
        'time': ['era', 'season', 'calendar', 'clock', 'festival', 'birth'],
        'trait': ['power', 'spirit', 'charm', 'wit', 'craft', 'instinct', 'persist', 'psych', 'life'],
        'fren': ['ally', 'friends', 'enemies', 'romance'],
        'org': ['guild', 'militia', 'society'],
        'bleev': ['religion', 'science', 'philosophy', 'mythology'],
        'fact': ['gloss', 'hint', 'image', 'sound', 'smell', 'taste', 'touch',
                 'state', 'memory', 'event', 'actor', 'player'],
        'stuff': ['props', 'maker', 'market', 'price', 'money']
    }

    html = set_page_top()
    html['debug_msg'] = topic_note[topic_nm]
    html['menu_pick'] = topic_nm.capitalize()
    argvals = [topic_nm]
    if len(args) > 0:
        argvals = args[0].split("/")
        if argvals[0] in subtopics[topic_nm]:
            html['submenu_pick'] = argvals[0].capitalize()
            if len(argvals) > 1:
                html['resource_pick'] = argvals[1]
    html['{}_class'.format(topic_nm)] = 'snow'

    FB.log_me("argvals[0] = {}  argvals[0][-1:] = {}".format(argvals[0], argvals[0][-1:]),
              LOG, options.loglevel)

    html['{}_msg'.format(topic_nm)] = subtopic_note[topic_nm] + FB.pluralize(argvals[0])
    html['pick_format_class'] = 'snow'
    html['pick_action_class'] = 'snow'
    return html


class AppException(web.HTTPError):
    """
    Override Tornado's web.HTTPError. Use flask_api.status codes instead
    """
    pass

class CracReset(web.RequestHandler):
    """
    Reset display on character management page.
    Create a session ID if one does not yet exist.
    This is also the default action for {path}/crac.

    :services:
        - ``GET crac/reset[/*]``
        - ``GET crac[/*]``
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/ or crac/reset

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
            FQ.write_queue(SES, sessid, {'session_start': dttm.curr_utc,
                                         'sessid': sessid,
                                         'user': 'Anonymous',
                                         'IP': self.request.remote_ip})
            self.set_secure_cookie("bowsessid", sessid, expires_days=None, secure=True)
        else:
            verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))

        char_html = set_page_top()
        char_html['menu_pick'] = "Clear"
        char_html['debug_msg'] = "Session cleared for take-off."
        self.render(HTML_NM, **char_html)

class CracPlace(web.RequestHandler):
    """
    Handle editing of:

        - place (generic)
        - closure (like a continent)
        - land (like a country)
        - region (hierarchy of sub-regions)
        - muni (any kind of municipality)

    :services:
        - ``GET crac/place[/*]``
        - ``GET crac/place/closure[/*]``
        - ``GET crac/place/land[/*]``
        - ``GET crac/place/region[/*]``
        - ``GET crac/place/muni[/*]``

    From old region.py:
                self.regions[row['COMMON_NM']] = \
                    {'desc':row['REGION_DESC'],
                     'lang1':row['FIRST_LANG'],
                     'lang2':row['SECOND_LANG'],
                     'name1':row['LOCAL_NM_1'],
                     'name2':row['LOCAL_NM_2'],
                     'con':row['CONTAINER'],
                     'geo':row['GEO_DESC']}

    Thinking of data in terms of graphs and maybe ontologies...
    Notes derived from DataDesign.pdf and region.py...
        A PLACE may have the following relationships:
            - TO
                - 0..1 PLACE
                - 0..1 NAME
                - 0..1 GEOGRAPHY
            - FROM
                - 0..1 PLACE
                - 0..1 PROP
                - 0..1 MARKET
                - 0..1 LANG
                - 0..1 ACTOR
                - 0..1 GROUP (of ACTOR)
                - 0..1 ORG
        All "type" attributes can be defined as a NAME
        A NAME may have the following relationships:
            - TO
                - 0..1 NAME
                - 0..1 GLOSS
                - 0..1 LANG
            - FROM
                - 0..1 NAME
                - 0..1 {many objects, including PLACE}
        All "description" attributes can be defined as a GLOSS
        A GLOSS may have the following relationships:
            - TO
                - 0..1 GLOSS
                - 0..1 IMAGE
                - 0..1 SOUND
            - FROM
                - 0..1 GLOSS
                - 0..1 LANG
                - 0..1 NAME
                - 0..1 IMAGE
                - 0..1 SOUND

    :to-do:
        - add the Muni button
        - expand into the Universe and the Multiverse: galaxies, star systems, planets
        - exapnd into the Microverse: neighborhoods, buildings, rooms, nests, etc.
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/place[/{sub-category}][/{resource_id}]

        :to-do: - Lookup resources in DAT. Create lists. Identify types. Handle ownership.
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'place')
        self.render(HTML_NM, **html)

class CracGenes(web.RequestHandler):
    """
    If a resource ID is not specified, list items available for loading.
    Then pick which one to load into the editor.

    If a resource ID is specified, retrieve it from DAT, make sure it is cached.

    :services:
        - ``GET crac/genes[/*]``
        - ``GET crac/human[/*]``
        - ``GET crac/animal[/*]``
        - ``GET crac/crafted[/*]``
        - ``GET crac/mix[/*]``

    :to-do:

        - as with places, review notes on this topic from data model and older code
        - will want to align this with "tree of life" selections, options available in-game

        In terms of the data model, the Genes revolve around the Actor entity.
        But the model doesn't really capture qualities and attributes of Actors other than
        Name and association to places and other actors.
        Probably the Gloss entity is closest thing there so far that would be like reference data.

        See /data/data_animal.json for an early attempt to define a taxonomy of animal species, etc.
        May want to consider putting certain types of constraints around levels of mixing,
        to what extent I want a "Doctor Doolittle talks to the animals" world vs. an "Island of
        Doctor Moreau" animal-human mix kind of world.  In other words, not just what types to
        pick from, but what rules govern the genetic "mix" in the game world.

        The /data/mongo/sem_actors.js file has good attribute-level definitions for Actors,
        including some related to genetic mix.

        The /data/mongo/sem_gloss.js file is also interesting. Using this structure may provide a
        good starting point for anything that is not quite fully attributed yet. ("Stuff"?)
        Kind of related to that, see /data/mysql/create_ref_tables.sql for a nice, simple definition
        of more traditional reference data structures as 2 relational tables.

        The postgres dba file /db/psql/dba_c02_types.psql has many enum values and regexes that
        might be useful in any context. This also helps to think how internationalization might be
        handled. Likewise, db/psql/dba_c03_records.psql identifies compound attributes that might
        be used in multiple places.

        For all of the entities in the "semantic" category on the E-R model, the postgresql files
        are probably the latest/greatest. See for example: /data/psql/bow_sem_create.psql

        Many of the actors will be a mix of traits from the human, animal and crafted categories.
        Probably want to build up an inventory of "mixologies" too.

        - Consider whether to add plant types of life-forms, and possibly exo-biological ones as well.

    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/genes[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'genes')
        self.render(HTML_NM, **html)

class CracSex(web.RequestHandler):
    """
    If a resource ID is not specified, list items available for loading.
    Then pick which one to load into the editor.

    If a resource ID is specified, retrieve it from DAT, make sure it is cached.

    This category deals with biological sex, gender appearance and sexual orientation.

    :services:
        - ``GET crac/sex[/*]``
        - ``GET crac/sex/biosex[/*]``
        - ``GET crac/sex/gender[/*]``
        - ``GET crac/sex/orient[/*]``

    :to-do:

    See the actor script, glossary entity and reference items noted above in the Genes method.
    At some level, there may be intersecting constraints between these choices and genetic mix.

    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/sex[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'sex')
        self.render(HTML_NM, **html)

class CracKarms(web.RequestHandler):
    """
    If a resource ID is not specified, list items available for loading.
    Then pick which one to load into the editor.

    If a resource ID is specified, retrieve it from DAT, make sure it is cached.

    This category deals with biological sex, gender appearance and sexual orientation.

    :services:
        - ``GET crac/karms[/*]``
        - ``GET crac/karms/merit[/*]``
        - ``GET crac/karms/demerit[/*]``
        - ``GET crac/karms/inherit[/*]``

    :to-do:

    - At its simplest level, this is just the regular "roll-up" of actor characteristics.
    - But also want to use it in a more complex sense...
    - see chars.py for basic abilities, Life Force, etc.

    The use of "karms" as a game concept flows from its use in some chat rooms.
    The idea is that an actor may accumulate either merits or demerits during game play.
    This is distinct from other types of "wins". It affects how others perceive the
    actor, to some extent, affects the scoring of a rebirth (in some way, not sure how yet),
    and in the meta-game I envision (with many levels of "heavens" and "hells" and some
    "buddha realms"), it affects their role/direction/capabilities in those realms.

    Part of the game play is to figure out how to "burn karms" in order to achieve
    a good rebirth (or extinction). It is inter-related with the idea that a Player's
    actions with an Actor carry over, to some degree, even after the Actor "dies".

    I had this as randomly-determined attribute of a new character. (See Actor script)
    What I need to do here is associate karms with various types of events, outcomes,
    and perhaps evaluations/reactions by other players. In some sense, I'd like to
    use this as a way to (subtly) reinforce the idea that everything is inter-connected,
    along with some concept of reward/punishment.

    Events will be a separate aspect of the game, not handled directly in this Class.
    What I want to do here is both have a way to initialize an Actor and to define/refine
    the karms.
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/karms[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'karms')
        self.render(HTML_NM, **html)

class CracHorde(web.RequestHandler):
    """
    :services:
        - ``GET crac/horde[/*]``
        - ``GET crac/horde/confed[/*]``
        - ``GET crac/horde/tribe[/*]``
        - ``GET crac/horde/clan[/*]``

    :to-do:
        - Define hierarchies and networks of social groupings
        - Align their characteristics to genetic mixes
        - In the E-R model, this aligns mainly to the Group entities
        - Constraints may apply based on Genes
        - But is inter-related with Place and Lang
        - May want to extend this to embrace concepts like Nationality, Citizenship/Subject-status, etc.
        - But need to have a fairly clear demarcation between Horde, which is tied to Fam, vs. Org,
           which is tied more to Place and Events
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/horde[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'horde')
        self.render(HTML_NM, **html)

class CracFam(web.RequestHandler):
    """
    :services:
        - ``GET crac/fam[/*]``
        - ``GET crac/fam/class[/*]``
        - ``GET crac/fam/rents[/*]``
        - ``GET crac/fam/sibs[/*]``
    :to-do:
        - see family.py for some guidance
        - When creating a new charcter, this helps to identify parents, social status, siblings
        - As the network of Actors get bigger, would be cool to use "real" Actors where possible
        - OR similarly, plug a new Actor into a currently NPR role in an "existing" Fam
        - The family is tied into Horde structures also, but is at a much more detailed level
        - As with much of the stuff in this Class, there is no presumption that anything is
           tied to a Player. That is a separate thing.
        - As we get into this more, it may also be useful to have like a "standard bio" (or more
            than one) for various types of Actors.
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/fam[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'fam')
        self.render(HTML_NM, **html)

class CracName(web.RequestHandler):
    """
    :services:
        - ``GET crac/name[/*]``
        - ``GET crac/name/famnm[/*]``
        - ``GET crac/name/persnm[/*]``
        - ``GET crac/name/honor[/*]``
        - ``GET crac/name/alias[/*]``

    :to-do:
        - see names.py
        - Need to be interdependencies with Genes, Place, Horde and Fam
        - In a more complex setting, would also be tied to Lang
        - May be able to simulate Lang by using specific auto-gen options tied to place, horde, etc.
        - As noted in names.py, also tweak based on social status
        - Will likely be adjusted once Org, Traits, Bleevs are defined
        - May want to move this to the end so that other attributes can be gathered first
        - May or may not want to have a sense of gendered names
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/name[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'name')
        self.render(HTML_NM, **html)

class CracTime(web.RequestHandler):
    """
    :services:
        - ``GET crac/time[/*]``
        - ``GET crac/time/era[/*]``
        - ``GET crac/time/season[/*]``
        - ``GET crac/time/calendar[/*]``
        - ``GET crac/time/clock[/*]``
        - ``GET crac/time/festival[/*]``
        - ``GET crac/time/birth[/*]``

    :to-do:
        - see stacks/gametime_010.py for a basic fantasy calendar
        - These would be tied mainly to Places, but perhaps also to Hordes and Orgs
        - My thought on "birth" is to not only generate a birth-date, with all auspicious notes,
           for a given Actor. But also to keep a register of all "births".
        - For NPR/sibling/parent/frenemy births, record a minimum of info then sketch in details later.
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/time[/{sub-category}][/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'time')
        self.render(HTML_NM, **html)

class CracTrait(web.RequestHandler):
    """
    GET  crac/traits

    :services:
        - ``GET crac/traits[/*]``
        - ``GET crac/traits/power[/*]``
        - ``GET crac/traits/spirit[/*]``
        - ``GET crac/traits/charm[/*]``
        - ``GET crac/traits/wit[/*]``
        - ``GET crac/traits/craft[/*]``
        - ``GET crac/traits/instinct[/*]``
        - ``GET crac/traits/persist[/*]``
        - ``GET crac/traits/psych[/*]``
        - ``GET crac/traits/life[/*]``

    :to-do:
        - "Roll up" basic character traits for role-playing
        - Modify if the actor inherits some karms
        - Modify according to genes
        - If special mutations are available, roll for those
        - Consider either using this area, or a new one, to develop character flaws, inner problems and so on
        - Consider extending this to include a Meyers-Briggs personality score
        - The "personality.py" script has logic dealing with generating personality / psychological qualities
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/traits
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'trait')
        self.render(HTML_NM, **html)

class CracFrens(web.RequestHandler):
    """
    :services:
        - ``GET crac/frens[/*]``
        - ``GET crac/frens/ally[/*]``
        - ``GET crac/frens/friends[/*]``
        - ``GET crac/frens/enemies[/*]``
        - ``GET crac/frens/romance[/*]``

    :to-do:
        - "Roll up" a frenemies network for the actor
        - It covers both friendships and romances
        - This helps to construct situations, problems, interactions
        - It can hook into existing actors, trigger new ones, or denote a space for an actor but not create one
        - The "family.py" script has logic dealing with generating frenemies

    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/frens
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'fren')
        self.render(HTML_NM, **html)

class CracOrgs(web.RequestHandler):
    """
    :services:
        - ``GET crac/orgs[/*]``
        - ``GET crac/orgs/guild[/*]``
        - ``GET crac/orgs/militia[/*]``
        - ``GET crac/orgs/society[/*]``

    :to-do:
        - Define hierarchies and networks of formal organizations - business/guild, military, societies
        - In the E-R model, this aligns mainly to the Org entities
        - Constraints may apply based on Genes, Place, Lang, Nationality, etc.
        - Need to have a fairly clear demarcation between Org, which is tied more to Place and Events,
            vs. Fam/Horde, which is tied to clan, tribe, family
        - Some cross-over with "bleevs" also. Religious, spiritual, philosophical orgs are covered here;
           whereas the "bleevs" entities are more abstract characteristics that may be associated to
           actors or orgs
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/orgs
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'org')
        self.render(HTML_NM, **html)

class CracBleevs(web.RequestHandler):
    """
    :services:
        - ``GET crac/bleev[/*]``
        - ``GET crac/bleev/religion[/*]``
        - ``GET crac/bleev/science[/*]``
        - ``GET crac/bleev/philosophy[/*]``
        - ``GET crac/bleev/mythology[/*]``

    :to-do:
        - Modify E-R model to include belief systems (BS :-) )
        - Can be constrained by or apply to orgs, fams, hordes, actors, maybe places
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/bleev
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'bleev')
        self.render(HTML_NM, **html)

class CracFacts(web.RequestHandler):
    """
    :services:
        - ``GET crac/fact[/*]``
        - ``GET crac/fact/gloss[/*]``
        - ``GET crac/fact/hint[/*]``
        - ``GET crac/fact/image[/*]``
        - ``GET crac/fact/sound[/*]``
        - ``GET crac/fact/smell[/*]``
        - ``GET crac/fact/taste[/*]``
        - ``GET crac/fact/touch[/*]``
        - ``GET crac/fact/state[/*]``
        - ``GET crac/fact/memory[/*]``
        - ``GET crac/fact/event[/*]``
        - ``GET crac/fact/actor[/*]``
        - ``GET crac/fact/player[/*]``

    :to-do:
        - The "facts" consist of actions on entities that describe, depict or relate
          to specific things within the game world. May eventually want to expand this
          to handle internationalization.
        - Most all of the "facts" will be associated with one or more other game elements,
          but can also just stand alone as inventory items
        - I will want to break out events/actions relating to persons/players in more detail.
          For now, just treating all players as "NPC" AIs.
        - I envision the "event" event are API hooks into my own lambda/functions inventory and
          as a way to hook into plug-ins and extensions.
        - "memory" is playback of an actor's actions. Hoping to weave this into the game play
          and not just have it as a "replay the game" feature. May support the "karms" stuff.
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/fact
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'fact')
        self.render(HTML_NM, **html)


class CracStuff(web.RequestHandler):
    """
    GET  crac/stuff
    :services:
        - ``GET crac/stuff[/*]``
        - ``GET crac/stuff/props[/*]``
        - ``GET crac/stuff/maker[/*]``
        - ``GET crac/stuff/market[/*]``
        - ``GET crac/stuff/price[/*]``
        - ``GET crac/stuff/money[/*]``

    :to-do:
        - The "stuff" has to do with inanimate objects and whatnot used within the game world.
        - A "maker" describes a role that creates the prop. This would be tied to guilds, etc.
        - Market, price, currency will tied to places and probably orgs. It implies handling
          some kind of exchange rate, probably thru the conceit of a "universal" currency.
        - a/k/a "resources" but I am trying to use livelier and fresher language, terminology.
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/stuff
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        html = handle_buttons(args, 'stuff')
        self.render(HTML_NM, **html)


class CracOpen(web.RequestHandler):
    """
    If a resource ID is not specified, list items available for loading.
    Then pick which one to load into the editor.

    If a resource ID is specified, retrieve it from DAT, make sure it is cached.

    :services:
        - ``GET crac/load[/*]``
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/load[/{resource_id}]
        """
        verify_session_id(self.get_secure_cookie("bowsessid", max_age_days=31))
        # chardata = FQ.get_records(DAT)
        char_html = set_page_top()
        char_html['menu_pick'] = "Open"
        char_html['debug_msg'] = "Opening the pod bay doors."
        char_html['gendata_class'] = 'snow'
        char_html['gendata'] = ''
        # if len(args) > 0:
        #     resource_id = args[0].split("/")
        char_html['pick_format_class'] = 'snow'
        self.render(HTML_NM, **char_html)

class CracSave(web.RequestHandler):
    """
    If a resource ID is specified, append to existing DAT item.
    If no resource ID specified, create a new DAT item and assign resource ID to it.
    The item being saved is the one currently active in the editor.
    Moving this to the end of the line for now, since I need to edit
    something before I can save it. We'll also probably want to turn this into
    or augment it with an auto-save capability.

    :services:
        - ``GET crac/save[/*]``
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/save
        """
        char_html = set_page_top()
        self.render(HTML_NM, **char_html)

class CracMap(web.RequestHandler):
    """
    GET  crac/map
    """
    def data_received(self, chunk):
        pass
    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/map
        """
        char_html = set_page_top()
        self.render(HTML_NM, **char_html)

class CracData(web.RequestHandler):
    """
    Ajax interface to return a JSON data set
    POST [crac/data, crac/data/] {file_nm}
    """
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        """
        Handle POST requests for crac/data {file_path}
        :Args:
        - File name is full path to a file or queue
        """
        file_nm = self.get_argument('file_path')
        file_data = FB.get_que_recs(file_nm)
        # Hand the full file back to the caller in JSON format
        self.set_header('Content-Type', 'text/json')
        self.write(json.dumps(file_data))

class CracMsgs(web.RequestHandler):
    """
    Handle REST messages
    """
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        """
        Handle GET requests for crac/msg/{message-value}
        """
        pass

class CracMeta(web.RequestHandler):
    """
    Get meta-data about crac/ services
    HEAD, GET /admin, /crac/(.*), /meta, /meta/(.*)
    """
    def data_received(self, chunk):
        pass

    def set_hdr_msg(self):
        """ List acceptable URLs in format suitable for display.
        """
        msgs = list()
        msgp = namedtuple('msgp', 'desc protocol path ')

        msgs.append(msgp('Start or Refresh a session', ['GET'], ['/crac/reset[/(.*)]'])._asdict())
        msgs.append(msgp('Load saved work', ['GET'], ['/crac/load[/(.*)]'])._asdict())

        msgs.append(msgp('Manage places', ['GET'], ['/crac/place[/(.*)]'])._asdict())
        msgs.append(msgp('Manage genotypes and phenotypes', ['GET'], ['/crac/genes[/(.*)]'])._asdict())
        msgs.append(msgp('Manage gender performance and sexuality', ['GET'], ['/crac/sex[/(.*)]'])._asdict())
        msgs.append(msgp('Manage basic attributes and points', ['GET'], ['/crac/karms[/(.*)]'])._asdict())
        msgs.append(msgp('Manage culture, language, clan affiliations', ['GET'], ['/crac/horde[/(.*)]'])._asdict())
        msgs.append(msgp('Manage broods and biological family', ['GET'], ['/crac/fam[/(.*)]'])._asdict())
        msgs.append(msgp('Manage names', ['GET'], ['/crac/name[/(.*)]'])._asdict())
        msgs.append(msgp('Manage dates, time and holidays', ['GET'], ['/crac/time[/(.*)]'])._asdict())
        msgs.append(msgp('Manage personality traits and appearance', ['GET'], ['/crac/traits[/(.*)]'])._asdict())
        msgs.append(msgp('Manage friends, enemies and social network', ['GET'], ['/crac/frens[/(.*)]'])._asdict())
        msgs.append(msgp('Manage jobs, organizations, memberships', ['GET'], ['/crac/orgs[/(.*)]'])._asdict())
        msgs.append(msgp('Manage belief, religion, philosophy', ['GET'], ['/crac/bleev[/(.*)]'])._asdict())
        msgs.append(msgp('Manage knowledge, education level, literacy', ['GET'], ['/crac/fact[/(.*)]'])._asdict())
        msgs.append(msgp('Manage inventory, money, graphics, sounds', ['GET'], ['/crac/stuff[/(.*)]'])._asdict())

        msgs.append(msgp('Save current work', ['GET'], ['/crac/save[/(.*)]'])._asdict())

        msgs.append(msgp('AJAX data request', ['POST'], ['/crac/data {file_nm}'])._asdict())
        msgs.append(msgp('REST messages', ['GET'], ['/crac/msg/{msg-value}'])._asdict())
        msgs.append(msgp('Get services metadata', ['HEAD', 'GET'], ['/crac/(.*)', '/crac/meta/*'])._asdict())
        msgs.append(msgp('Get robots.txt context', ['GET'], '/robots.txt')._asdict())

        self.set_header('Meta-Messages-List', json.dumps(msgs))
        return json.dumps(msgs)

    def head(self, *args, **kwargs):
        """ Write informational messages as header. """
        self.set_hdr_msg()

    def get(self, *args, **kwargs):
        """ Write informational messages as header and in body. """
        self.write(self.set_hdr_msg())

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
    Launch the char_bow app.
    """
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), options.templates)), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    debug_jinja = True if options.loglevel == 'DEBUG' else False
    settings = dict(template_loader=jinja2_loader,
                    static_path=os.path.join(os.path.dirname(__file__), options.static),
                    debug=debug_jinja,
                    cookie_secret=options.char_cookie_secret)
    app = web.Application(
        handlers=[
            (r"/crac/reset", CracReset),
            (r"/crac/reset/", CracReset),
            (r"/crac/reset/(.*)", CracReset),
            (r"/crac/place", CracPlace),
            (r"/crac/place/", CracPlace),
            (r"/crac/place/(.*)", CracPlace),
            (r"/crac/genes", CracGenes),
            (r"/crac/genes/", CracGenes),
            (r"/crac/genes/(.*)", CracGenes),
            (r"/crac/sex", CracSex),
            (r"/crac/sex/", CracSex),
            (r"/crac/sex/(.*)", CracSex),
            (r"/crac/karms", CracKarms),
            (r"/crac/karms/", CracKarms),
            (r"/crac/karms/(.*)", CracKarms),
            (r"/crac/horde", CracHorde),
            (r"/crac/horde/", CracHorde),
            (r"/crac/horde/(.*)", CracHorde),
            (r"/crac/fam", CracFam),
            (r"/crac/fam/", CracFam),
            (r"/crac/fam/(.*)", CracFam),
            (r"/crac/name", CracName),
            (r"/crac/name/", CracName),
            (r"/crac/name/(.*)", CracName),
            (r"/crac/time", CracTime),
            (r"/crac/time/", CracTime),
            (r"/crac/time/(.*)", CracTime),
            (r"/crac/trait", CracTrait),
            (r"/crac/trait/", CracTrait),
            (r"/crac/trait/(.*)", CracTrait),
            (r"/crac/frens", CracFrens),
            (r"/crac/frens/", CracFrens),
            (r"/crac/frens/(.*)", CracFrens),
            (r"/crac/orgs", CracOrgs),
            (r"/crac/orgs/", CracOrgs),
            (r"/crac/orgs/(.*)", CracOrgs),
            (r"/crac/bleev", CracBleevs),
            (r"/crac/bleev/", CracBleevs),
            (r"/crac/bleev/(.*)", CracBleevs),
            (r"/crac/fact", CracFacts),
            (r"/crac/fact/", CracFacts),
            (r"/crac/fact/(.*)", CracFacts),
            (r"/crac/stuff", CracStuff),
            (r"/crac/stuff/", CracStuff),
            (r"/crac/stuff/(.*)", CracStuff),

            (r"/crac/load", CracOpen),
            (r"/crac/load/", CracOpen),
            (r"/crac/load/(.*)", CracOpen),
            (r"/crac/save", CracSave),
            (r"/crac/save/", CracSave),
            (r"/crac/save/(.*)", CracSave),
            (r"/crac/map", CracMap),
            (r"/crac/map/", CracMap),
            (r"/crac/map/(.*)", CracMap),
            (r"/crac/data", CracData),
            (r"/crac/data/", CracData),
            (r"/crac/data/(.*)", CracData),
            (r"/crac/msg", CracMsgs),
            (r"/crac/msg/", CracMsgs),
            (r"/crac/msg/(.*)", CracMsgs),
            (r"/crac/meta", CracMeta),
            (r"/crac/meta/", CracMeta),
            (r"/crac/meta/(.*)", CracMeta),
            (r"/crac", CracReset),
            (r"/crac/", CracReset),
            (r"/crac/(.*)", CracReset),
            (r"/robots.txt", Robots),
            (r"/(.*)", Unknown)],
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
    Instantiate helper functions object.
    Define, collect options from command line, from config file.
    Config file location passed in as a cmd line option.
    Identify data and log file locations.

    :methods executed:
        - ``main()``
    """
    FB = FuncBasic()
    FQ = FuncQueue()

    define("port", help="Port to run app instance under", type=int)
    define("secure", help="Run under TLS if true", type=int)
    define("conf", help="Relative path to config file", type=str)
    options.parse_command_line(final=False)
    protocol = 'https://' if options.secure else 'http://'
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
    define("dmn_host", help="Host name")
    define("pyapp_nm", help="Python application name")
    define("html_nm", help="HTML template file name")
    define("dat_fil", help="Data queue name")
    define("ctl_fil", help="Name of storage control files")
    define("ses_fil", help="Name of session state storage files")
    define("run_log", help="Log queue name")
    define("job_log", help="Log queue name")
    define("pid_log", help="Log queue name")
    define("char_bow_html", help="HTML template for Char page")
    define("char_cookie_secret", help="To encrypt cookie communications")
    options.parse_config_file(options.conf)

    DATA = dict()
    LOGS = dict()
    this_app_nm = 'char'
    app_ix = options.apps.split(',').index(this_app_nm)
    domain_nm = options.domains.split(',')[app_ix]
    HTML_NM = options.htmls.split(',')[app_ix] + options.html_nm
    HOST_NM = domain_nm + options.dmn_host
    DAT = os.path.join(options.memdir, this_app_nm + options.dat_fil)
    DATA['ctl'] = this_app_nm + options.ctl_fil
    SES = os.path.join(options.memdir, this_app_nm + options.ses_fil)
    LOG = os.path.join(options.memdir, this_app_nm + options.run_log)
    main()
