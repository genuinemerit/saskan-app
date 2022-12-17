#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    map_svg_maker
:class:     disable
:author:    genuinemerit <dave@davidstitt.solutions>

Back-end data management module for creating, modifying, deleting, assembling part of SVG Map. 
Currently is called directly, only by map_msg_handler. 

Writes to in-memory "queues" ("/dev/shm") and to files located at /home/bow/log:
- catalog = cat.que, holds the complete catalog of active items that are part of the Map inventory.
- SVG = svg.que, holds the most-recently assembled version of the SVG file(s).
- /home/bow/log/delete.que = items that were delted from the catalog
- /home/bow/log/bow.log = action log

To Do:
- Clean-up/archive/persist - store copies of the catalog and SVG queues to /home/bow/log
- Enable delete logic - Remove from cat.que.

#pylint: disable=R0902
#pylint: disable=R0904
"""
from pprint import pprint as pp
from os import path
import html
import json
import requests
from bow_const import BowConst
from bow_func_basic import FuncBasic
BC = BowConst()
FC = FuncBasic()

#######################
# Process Map Messages
#######################

class MapMaker():
    """
        In support of interactive SVG map graphics for awesome purposes.
        * Drawing primitives for SVG structure.
        * Assembly of primitives into a coherent SVG presentation.
        * References to external resources.

        These functions create parts of SVG file(s) that describe a map.
        Return results to caller, who will store the results on a results queue.

        Try to both simplify and separate out tweaking individual components and assembly.

        This class also stores the information in a class object and responds to queries.
        To Do:
        * It might make sense to just pickle the entire (data) object?
        * Or (perhaps better) store it as JSON files.
    """
    msg = None
    delete_msg = None
    msgtyp = None
    msgid = None
    msgsrv = None
    meta = None
    cat_msg = None
    cat_d = None
    cat_q = None
    svg_q = None
    delete_log = None
    indent = None
    hier = None

    file_ls = None
    ntab = None
    xml_id = None
    svg_id = None

    def __init__(self):
        """ Boot up the map catalog """
        self.msgsrv = 'http://ananda:8090/'   # URL for map message web services
        self.msg = dict()               # Attributes of message-in currently being processed
        self.delete_msg = bool()        # Delete-action flag
        self.msgtyp = ''                # Type of message currently being processed.
        self.msgid = ''                 # ID of message currently being processed.
        self.meta = dict()              # Metadata for the message being processed.
        self.cat_msg = dict()           # Attribues of stored-message
        self.cat_d = dict()           # In-memory of identifiers and locators
        self.cat_q = "/dev/shm/cat.que"
        self.svg_q = "/dev/shm/svg.que"
        self.delete_log = "/home/bow/log/delete.que"
        self.indent = dict()
        self.hier = dict()
        self.indent = {'svg': 0, 'ref': 1, 'grp': 1, 'tgp': 2,
                       'elm': 2, 'use': 2, 'img': 2, 'txt': 3}
        self.hier = {'svg': 0, 'ref': 10, 'grp': 20, 'tgp': 30,
                     'elm': 40, 'img': 50, 'txt': 60, 'use': 100}

        # Not sure I need these... or might move to another class:
        self.file_ls = dict()           # id: {type:<string>, path:{Path}, code:str}
        self.ntab = dict()              # tokenized line returns and tabs based on message level
        self.xml_id = ''                # key to assembly of XML file data in self.file_ls
        self.svg_id = ''                # key to assembly of SVG data in self.cat_d['svg']

    @classmethod
    def __id_hash(cls):
        """ Generate an ID value """
        hash_id = str(FC.hash_me(str(FC.get_dttm().curr_ts), BC.SHA1))
        return hash_id[0:-20]

    @classmethod
    def __set_number(cls, p_value, p_float=False):
        """ Set to number or None.
            If p_float is true, then set the number to a float.
        :returns: the number or None
        """
        v_value = None
        if p_value in [None, '']:
            v_value = None
        elif isinstance(p_value, (int, float))\
        or isinstance(float(p_value), float):
                # or isinstance(int(p_value), int)\
            if p_float:
                v_value = float(p_value)
            else:
                v_value = int(p_value)
        return v_value

    def set_indent(self):
        """ Tokenize indentation based on the message level.
            Assume msgtyp has been set. """
        self.msg['indent'] = str(self.indent[self.msgtyp])
        self.msg['tabs'] = list()
        self.msg['tabs'].append('\n' + '\t' * self.indent[self.msgtyp])
        self.msg['tabs'].append('\n\t' + '\t' * self.indent[self.msgtyp])

    def load_catalog(self):
        """ Pull catalog into memory from storage.
            Call message service to get metadata for message type being processed.
            Assumes that self.msgtyp has already been set.
        """
        self.cat_d = dict()           # Full catalog
        self.cat_msg = dict()    # Metadata for type of msg being processed
        if path.isfile(self.cat_q):
            with open(self.cat_q, 'r') as cat_f:
                cat_j = cat_f.read()
                self.cat_d = json.loads(cat_j)
                cat_f.close()
        resp = requests.get('{0}{1}'.format(self.msgsrv, self.msgtyp))
        self.meta = json.loads(resp.text)

    def set_msgid(self):
        """ Set a message ID value. Generate a value if one is not provided.
            Verify that it is unique within the catalog.
        """
        if self.msg['id'] in [None, 0, '']:
            self.msg['id'] = self.msgtyp + "_" + self.__id_hash()
        self.msgid = html.escape(self.msg['id'].lower().replace(' ', '_'))
        self.msg['id'] = self.msgid
        if self.msgid in self.cat_d:
            self.cat_msg = self.cat_d[self.msgid]
            FC.log_me('Updating {0}'.format(self.msgid), BC.INFORM)
        else:
            self.cat_msg = self.msg
            FC.log_me('Inserting {0}'.format(self.msgid), BC.INFORM)

    def set_name(self):
        """ Set element Name value. If no name provided, set Name to ID.
            Assume set_msgid has been called.
        """
        if self.msg['name'] in [None, 0, '']:
            if self.cat_msg['name'] in [None, 0, '']:
                self.msg['name'] = self.msgid
            else:
                self.msg['name'] = self.cat_msg['name']
        else:
            self.msg['name'] = html.escape(self.msg['name'].lower().replace(' ', '_'))

    def set_xy(self, msg_attr):
        """ Set (x,y) values """
        xy_val = self.msg[msg_attr]
        if xy_val in [None, '']:
            if self.cat_msg[msg_attr]:
                if self.cat_msg[msg_attr]['val'] not in [None, '']:
                    xy_val = self.cat_msg[msg_attr]['val']
                elif 'required' in self.meta[msg_attr]:
                    xy_val = '(400, 400)'
        self.msg[msg_attr] = dict()
        self.msg[msg_attr]['data'] = ['0', '0']
        self.msg[msg_attr]['val'] = '(0, 0)'
        if xy_val not in [None, '']:
            if xy_val[0] != '(':
                xy_val = '(' + xy_val
            if xy_val[-1] != ')':
                xy_val = xy_val + ')'
            self.msg[msg_attr]['val'] = xy_val
            xy_data = xy_val[1:-1].replace(' ', '').split(',')
            self.msg[msg_attr]['data'] = xy_data

    def set_comment(self):
        """ Create in-line commented note for an element based on desc attribute.
        """
        self.msg['comment'] = '' if self.msg['desc'] in [None, ''] else \
          '{0}<!-- {1} -->'.format(self.msg['tabs'][0], html.unescape(self.msg['desc']))

    def handle_delete(self):
        """ Remove item from inventory. Assume set_msgid has been called. """
        self.delete_msg = False
        if self.msg['delete'].capitalize() == "True":
            self.delete_msg = True
            if self.msgid in self.cat_d:
                # Not quite sure what is going on here...
                # We want to log the fact that a delete happened
                # We want to remove the item from the catalog
                # And we want to return a confirmation (cat_msg) of the delete 
                FC.que_me(self.cat_d[self.msgid])
                del self.cat_d[self.msgid]
                FC.log_me('Deleting {0}'.format(self.msgid), BC.INFORM)

    def set_path(self, msg_attr):
        """  Set path attribute value.
        Example:  Path(exists=True, rqst='static/cat.svg', abs='/home/dave/Projects/python/bowmap/gm_map/static/cat.svg', isDir=False, isFile=True, isLink=False, isMount=False, parent='/home/dave/Projects/python/bowmap/gm_map/static', item='cat.svg'))
        """
        rqst_path = self.msg[msg_attr]
        self.msg[msg_attr] = dict()
        self.msg[msg_attr]['rqst'] = rqst_path
        if rqst_path in (None, ''):
            if self.cat_msg[msg_attr] not in (None, ''):
                self.msg[msg_attr] = self.cat_msg[msg_attr]
        
        path_attr = FC.get_path(rqst_path)
        if not path_attr.exists:
            FC.log_me('Reference file not found: "{0}"'.format(self.msg[msg_attr]), BC.WARN)
        else:            
            self.msg[msg_attr]['exists'] = str(path_attr.exists)
            self.msg[msg_attr]['rqst'] = path_attr.rqst
            self.msg[msg_attr]['abs'] = path_attr.abs
            self.msg[msg_attr]['isDir'] = str(path_attr.isDir)
            self.msg[msg_attr]['isFile'] = str(path_attr.isFile)
            self.msg[msg_attr]['isLink'] = str(path_attr.isLink)
            self.msg[msg_attr]['isMount'] = str(path_attr.isMount)
            self.msg[msg_attr]['parentDir'] = path_attr.parent
            self.msg[msg_attr]['fileNm'] = path_attr.item

    def set_option(self, msg_attr):
        """ Set selected value of an attribute that is of type 'select' """
        if self.msg[msg_attr] in [None, '']:
            if msg_attr in self.cat_msg and self.cat_msg[msg_attr] not in [None, '']:
                self.msg[msg_attr] = self.cat_msg[msg_attr]
        options = [val[4:] for val in self.meta[msg_attr] if val[:4] == 'opt_']
        if self.msg['itmtyp'] not in options:
            FC.log_me('Bad selection option: "{0}"'.format(self.msg['itmtyp']), BC.WARN)

    def set_gid(self):
        """ Set Parent ID value.
            Adjust indent Level to be one greater than the parent level.
            Adjust hier level to be 5 greater than the parrent hier.
            Items with no parent are at level 0 (zero).
        """
        if self.msg['gid'] in [None, '']:
            if 'gid' in self.cat_msg and self.cat_msg['gid'] not in [None, '']:
                self.msg['gid'] = self.cat_msg['gid']
        else:
            self.msg['gid'] = html.escape(self.msg['gid'].lower().replace(' ', '_'))
        if self.msg['gid'] not in self.cat_d:
            FC.log_me('Parent group not found: "{0}"'.format(self.msg['gid']), BC.WARN)
        else:
            self.msg['indent'] = str(int(self.cat_d[self.msg['gid']]['indent']) + 1)
            self.msg['hier'] = str(int(self.cat_d[self.msg['gid']]['indent']) + 5)

    def set_uid(self):
        """ Set Use ID. Reference another item which is already defined internally. """
        if self.msg['uid'] in [None, '']:
            if 'uid' in self.cat_msg and self.cat_msg['uid'] not in [None, '']:
                self.msg['uid'] = self.cat_msg['uid']
        else:
            self.msg['uid'] = html.escape(self.msg['uid'].lower().replace(' ', '_'))
        if self.msg['uid'] not in self.cat_d:
            FC.log_me('Referenced item ID not found: "{0}"'.format(self.msg['uid']), BC.WARN)

    def set_img_id(self):
        """ Set Image ID. Reference a file which is already defined externally. """
        if self.msg['img_id'] in [None, '']:
            if 'img_id' in self.cat_msg and self.cat_msg['img_id'] not in [None, '']:
                self.msg['img_id'] = self.cat_msg['img_id']
        else:
            self.msg['img_id'] = html.escape(self.msg['img_id'].lower().replace(' ', '_'))
        if self.msg['img_id'] not in self.cat_d:
            FC.log_me('Referenced Image ID not found: "{0}"'.format(self.msg['img_id']), BC.WARN)
        else:
            img_id = self.msg['img_id']
            self.msg['img_id'] = dict()
            self.msg['img_id']['path'] = self.cat_d[img_id]['path']
            self.msg['img_id']['ref'] = img_id

    def set_common_values(self, p_msg):
        """ Verify/set values on attributes common to all message types """
        self.msg = p_msg
        self.msg['code'] = ''
        if not self.delete_msg:
            self.msgtyp = self.msg['msg']
            self.set_indent()
            self.load_catalog()
            self.set_msgid()
            self.set_name()
            self.msg['hier'] = str(self.hier[self.msgtyp])
            for msg_attr in self.msg:
                if msg_attr in self.meta:
                    if 'xy' in self.meta[msg_attr]:
                        self.set_xy(msg_attr)
                    elif 'path' in self.meta[msg_attr]:
                        self.set_path(msg_attr)
                    elif 'select' in self.meta[msg_attr]:
                        self.set_option(msg_attr)
                    elif msg_attr == 'gid':
                        self.set_gid()
                    elif msg_attr == 'uid':
                        self.set_uid()
                    elif msg_attr == 'img_id':
                        self.set_img_id()
                    elif 'text' in self.meta[msg_attr] or\
                      'number' in self.meta[msg_attr]:
                        self.msg[msg_attr] = html.escape(self.msg[msg_attr])
            self.set_comment()

    def render_tags(self, tags):
        """ Add simple tagged value to code, where msg key = tag name.
            For example, good for 'desc' and 'title' tags.
        """
        for tag in tags:
            if self.msg[tag] not in [None, '']:
                self.msg['code'] += "{0}<{1}>{2}</{3}>".format(
                    self.msg['tabs'][1], tag, self.msg[tag], tag)

    def render_attr(self, js_nm, msg_attr):
        """ Add non-tagged name=value pair to the code, where the value is quoted.
            For example, stroke="blue"
        """
        if self.msg[msg_attr] not in ['', None]:
            self.msg['code'] += ' {0}="{1}"'.format(js_nm, self.msg[msg_attr])

    def render_zix(self):
        """ Add z_index style to code and adjust order """
        if self.msg['zix'] not in [None, '']:
            self.msg['code'] += ' style="z-index: {0};"'.format(self.msg['zix'])
            self.msg['indent'] += str(int(self.msg['zix']) * 2)

    def save_catalog(self):
        """ Populate the local and queued catalog message structures """
        for key in self.msg:
            if self.msg[key] not in [None, '']:
                if key not in self.cat_msg or self.msg[key] != self.cat_msg[key]:
                    self.cat_msg[key] = self.msg[key]
        self.cat_d[self.msgid] = self.cat_msg
        # Write message results to catalog
        # To Do: Consider how delete is managed
        with open(self.cat_q, 'w') as catq:
            catq.write(json.dumps(self.cat_d))
            catq.close()

    def handle_svg(self, p_msg):
        """ Handle an SVG message:  Add, Update or Delete an SVG-wrapper item.
            Return the modified item as a python dict().
        """
        self.set_common_values(p_msg)
        self.msg['close'] = '{0}</svg>'.format(self.msg['tabs'][0])
        self.msg['code'] += '{0}<svg xmlns="http://www.w3.org/2000/svg"'.format(self.msg['tabs'][0])
        self.msg['code'] += ' xmlns:xlink="http://www.w3.org/1999/xlink"'
        self.msg['code'] += ' width="{0}" height="{1}"'.format(
            str(self.msg['size_xy']['data'][0]), str(self.msg['size_xy']['data'][1]))
        self.msg['code'] += ' viewbox="0 0 {0} {1}"'.format(
            str(self.msg['size_xy']['data'][0]), str(self.msg['size_xy']['data'][1]))
        if self.msg['style'] not in [None, '']:
            self.msg['code'] += ' style="{0}"'.format(self.msg['style'])
        self.msg['code'] += '>'
        self.render_tags(['title', 'desc'])
        self.save_catalog()
        return self.cat_msg

    def handle_ref(self, p_msg):
        """ Identify path to an externally-referenced resource. """
        self.set_common_values(p_msg)
        # Externally referenced images are used in-line. So we just make a comment for those.
        self.msg['close'] = ''
        path_ref = self.msg['path']['abs'] if 'abs' in self.msg['path'] else self.msg['path']['rqst']
        if self.msg['itmtyp'] == 'image':
            self.msg['code'] += "{0}<!-- Reference image: {1} -->".format(self.msg['tabs'][0], path_ref)
        else:
            self.msg['code'] += '{0}<script type="text/ecmascript"'.format(self.msg['tabs'][0])
            self.msg['code'] += ' xlink:href="{0}"'.format(path_ref)
            self.msg['code'] += ' xlink:actuate="onLoad" xlink:show="other" xlink:type="simple">'
            self.msg['code'] += '</script>'
        self.render_tags(['desc'])
        self.save_catalog()
        return self.cat_msg

    def handle_grp(self, p_msg):
        """ Generate SVG for blocking out sections of an svg.
        Groups may be identified as parent groups or as child groups which are wrapped by a parent.
        There may be a hierarchy of such relationships. The gid identifies a parent object.
        """
        self.set_common_values(p_msg)
        self.msg['close'] ='{0}</g>'.format(self.msg['tabs'][0])
        self.msg['code'] += '{0}<g '.format(self.msg['tabs'][0])
        self.render_attr('id', 'id')
        self.render_attr('fill', 'fill')
        self.render_attr('stroke', 'stroke')
        self.render_attr('stroke-width', 'thick')
        self.render_attr('stroke-opacity', 'opaq')
        if self.msg['dash'] not in ['', None]:
            self.msg['code'] += ' {0}="{1}"'.format('stroke-dasharray', self.msg['dash']['val'])
        if self.msg['move'] is not None:
            self.msg['code'] += ' transform="translate({0})"'.format(self.msg['move'])
        self.render_zix()
        self.msg['code'] += '>'
        self.render_tags(['desc'])
        self.save_catalog()
        return self.cat_msg

    def handle_elm(self, p_msg):
        """ Generate code for a (Draw) Path element.
            Assume for now that all lines are drawn using path.
        """
        self.set_common_values(p_msg)
        self.msg['close'] = ''
        if self.msg['draw'] is not None:
            self.msg['code'] += '{0}<path id="{1}" d="{2}"'.format(
                self.msg['tabs'][0], self.msgid, self.msg['draw'])
        self.render_attr('tabindex', 'tabix')
        self.render_zix()
        self.msg['code'] += ' />'
        self.render_tags(['desc'])
        self.save_catalog()
        return self.cat_msg

    def handle_use(self, p_msg):
        """ Generate SVG code for a Use element.
            For my purposes, use references an internally-defined item.\
            Transform is a complex algorithm with multiple attributes such as:
                translate, rotate, skewX, matrix, and scale
            Translate moves the object horizotonally (+/-) and vertically (+/-)
            Scale resizes it horizontally (factor, required) and vertically (same as horizontal if
                not stated explicitly). I am only supporting a single value, for proportional scaling.
            Not yet supporting rotate, skew or matrix
        """
        self.set_common_values(p_msg)
        self.msg['close'] = ''
        self.msg['code'] += '{0}<use id="{1}" xlink:href="{2}"'.format(
            self.msg['tabs'][0], self.msgid, self.msg['uid'])
        if self.msg['loc_xy'] is not None:
            self.msg['code'] += ' x="{0}", y="{1}"'.format(self.msg['loc_xy']['data'][0],
                                                           self.msg['loc_xy']['data'][1])
        if self.msg['size_xy'] is not None:
            self.msg['code'] += ' width="{0}", height="{1}"'.format(self.msg['size_xy']['data'][0],
                                                                    self.msg['size_xy']['data'][1])
        if self.msg['move_xy'] is not None or self.msg['scale'] is not None:
            self.msg['code'] += ' transform="'
            if self.msg['move_xy'] is not None:
                self.msg['code'] += ' translate({0},{1})'.format(self.msg['move_xy']['data'][0], 
                                                                 self.msg['move_xy']['data'][1])
            if self.msg['scale'] is not None:
                self.msg['code'] += ' scale({0})'.format(self.msg['scale'])
            self.msg['code'] += '"' 
        self.render_attr('tabindex', 'tabix')
        self.render_zix()
        self.msg['code'] += '>'
        self.render_tags(['desc'])
        self.msg['code'] += '{0}</use>'.format(self.msg['tabs'][0])
        self.save_catalog()
        return self.cat_msg

    def handle_tgp(self, p_msg):
        """ Generate SVG code for a Text Group (child group).
        """
        self.set_common_values(p_msg)
        self.msg['close'] ='{0}</g>'.format(self.msg['tabs'][0])
        self.msg['code'] += '{0}<g '.format(self.msg['tabs'][0])
        self.render_attr('id', 'id')
        self.render_attr('font-family', 'fontfam')
        self.msg['code'] += ' font-size="{0}pt"'.format(self.msg['fontsize'])
        self.render_zix()
        self.msg['code'] += '>'
        self.render_tags(['desc'])
        self.save_catalog()
        return self.cat_msg

    def handle_txt(self, p_msg):
        """ Generate SVG code for a Text Element. """
        self.set_common_values(p_msg)
        self.msg['close'] = ''
        self.msg['code'] += '{0}<text'.format(self.msg['tabs'][0])
        self.render_attr('id', 'id')
        if self.msg['loc_xy'] is not None:
            self.msg['code'] += ' x="{0}" y="{1}"'.format(
                self.msg['loc_xy']['data'][0], self.msg['loc_xy']['data'][1])
        self.render_attr('tabindex', 'tabix')
        self.render_zix()
        self.msg['code'] += '>{0}</text>'.format(self.msg['words'])
        self.render_tags(['desc'])
        self.save_catalog()
        return self.cat_msg

    def handle_img(self, p_msg):
        """ Generate SVG code for an Image element reference.
            For my purposes, Img always references an externally-defined item.
        """
        self.set_common_values(p_msg)
        self.msg['close'] = ''
        self.msg['code'] += '{0}<image'.format(self.msg['tabs'][0])
        self.render_attr('id', 'id')
        if 'path' in self.msg['img_id']:
            if 'abs' in self.msg['img_id']['path'] and self.msg['img_id']['path']['abs'] not in (None, ''):
                self.msg['code'] += ' xlink:href="{0}"'.format(self.msg['img_id']['path']['abs'])
            else:
                self.msg['code'] += ' xlink:href="{0}"'.format(self.msg['img_id']['path']['rqst'])
        if self.msg['loc_xy'] is not None:
            self.msg['code'] += ' x="{0}" y="{1}"'.format(
                self.msg['loc_xy']['data'][0], self.msg['loc_xy']['data'][1])
        if self.msg['size_xy'] is not None:
            self.msg['code'] += ' width="{1}" height="{0}"'.format(
                self.msg['size_xy']['data'][0], self.msg['size_xy']['data'][1])
        self.render_attr('tabindex', 'tabix')
        self.render_zix()
        self.msg['code'] += '>'
        self.render_tags(['desc'])
        self.msg['code'] += '{0}</image>'.format(self.msg['tabs'][0])
        self.save_catalog()
        return self.cat_msg


    #############################
    # Consider putting the rest of the code into a separate Class or module.
    # The distinction between an "XML file" and the "SVG file" is negligible; don't confuse things.
    #############################
    def __start_xml(self):
        """ Create a catalog entry for XML file.
            Put XML headers at top of file.
            Put SVG headers in after that.
        """
        self.svg_id = self.msg.id
        if 'svg' not in self.cat_d:
            FC.log_me('Must create a SVG header first', BC.ERROR)
        self.msg = dict()
        self.msg['type'] = 'xml'
        self.set_msgid()
        self.set_name()
        self.msg['xml'] = '/dev/shm/' + self.msg['name'] + '.xml'
        self.msg['code'] = '<?xml version="1.0"?>'
        self.msg['code'] += '{0}<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '.format(
            "\n")
        self.msg['code'] += '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'

        self.msg['code'] += self.cat_d['svg'][self.svg_id]['code']
        self.xml_id = self.msg.id

    def __asm_refs(self):
        """ Pull in code from referenced scripts, then referenced images """
        # Pull in code from externally referenced script items
        # Then code from externally referenced image items (just show comments)
        if 'ref' in self.cat_d:
            for reft in ['script', 'image']:
                self.msg['code'] += BC.NT0
                for _, ref_item in self.cat_d['ref'].items():
                    if ref_item['msg'].itmtyp == reft:
                        self.msg['code'] += ref_item['code']

    def __asm_kids(self, pkey):
        """ Recursively add code for child-members of a group
            where the children are not use elements.
            Display items in hierarchical order.
        """
        child_code = ''
        kordkeys = []
        for msgtyp in ['grp', 'tgp', 'elm', 'txt', 'img', 'use']:
            # kordkeys = [(cat_val['msg'].order, cat_key)
            #            for cat_key, cat_val in self.cat_d[msgtyp].items()
            #            if msgtyp in self.cat_d and cat_val['msg'].gid == pkey]
            if msgtyp in self.cat_d:
                for cat_key, cat_val in self.cat_d[msgtyp].items():
                    if cat_val['msg'].gid == pkey:
                        kordkeys.append((cat_val['msg'].order, cat_key))

            # Sort by hierarchical order:
            for _, kkey in sorted(kordkeys):
                if msgtyp in ['grp', 'tgp']:
                    child_code += BC.NT0
                if msgtyp in self.cat_d:
                    child_code += self.cat_d[msgtyp][kkey]['code']
                    child_code += self.__asm_kids(kkey)
                    if self.cat_d[msgtyp][kkey]['msg'].type in ['grp', 'tgp']:
                        self.msg.level = self.cat_d[msgtyp][kkey]['msg'].level
                        self.set_indent()
                        child_code += "{0}</g>".format(self.ntab[0])
        return child_code

    def __asm_groups(self):
        """ Add code for each uber-parent group.
            Get keys for groups or text-groups that have no parent,
            then order them hierarchically.
        """
        pordkeys = []
        for ptyp in ['grp', 'tgp']:
            if ptyp in self.cat_d:
                for grpk, grpv in self.cat_d[ptyp].items():
                    if grpv['msg'].gid in ['None', None]:
                        pordkeys.append((grpv['msg'].order, grpk))
                for pok in sorted(pordkeys):
                    _, pkey = pok
                    self.msg['code'] += BC.NT0
                    self.msg['code'] += self.cat_d[ptyp][pkey]['code']
                    self.msg['code'] += self.__asm_kids(pkey)
                    self.msg.id = self.cat_d[ptyp][pkey]['msg'].id
                    self.msg.level = self.cat_d[ptyp][pkey]['msg'].level
                    self.set_indent()
                    self.msg['code'] += "{0}</g>".format(self.ntab[0])

    def assemble(self):
        """ Assemble entire SVG object.
            Put it all together and save as content for an XML file.
        """
        self.__start_xml()
        self.__asm_refs()
        self.__asm_groups()
        self.msg['code'] += "\n</svg>\n"
        # Store the XML-SVG code with its file reference
        self.file_ls[self.xml_id]['code'] = self.msg['code']

    ##################################
    # Handle this kind of thing via RESTful services.
    # Probably just add to map_msg_service
    ###################################
    def get_code(self):
        """ Return code currently assembled as-is. """
        if self.xml_id in self.file_ls and 'code' in self.file_ls[self.xml_id]:
            return self.file_ls[self.xml_id]['code']
        return ''

    def get_catalog(self):
        """ Return the current catalog data """
        return self.cat_d

    def get_file_list(self):
        """ Return the current file list data """
        return self.file_ls

    def publish(self):
        """ Write assembled XML file to specified target path. """
        xml_path = self.file_ls[self.xml_id]['path'].rqst
        with open(xml_path, 'w') as xmlf:
            xmlf.write(self.file_ls[self.xml_id]['code'])
            xmlf.close()
        self.file_ls[self.xml_id]['path'] = FC.get_path(xml_path)

    def show(self, p_browser: str):
        """ Display the XML/SVG file in specified browser """
        v_browser = str(p_browser.lower())
        if v_browser in ['chrome', 'firefox', 'google-chrome-stable', 'opera']:
            if v_browser == 'chrome':
                v_browser = 'google-chrome-stable'
            cmd = "{0} {1}".format(v_browser, str(
                self.file_ls[self.xml_id]['path'].abs))
            FC.run_cmd(cmd)

    def remove(self):
        """ Remove assembled XML file from specified target path. """
        cmd = "rm {0}".format(str(self.file_ls[self.xml_id]['path'].abs))
        FC.run_cmd(cmd)
