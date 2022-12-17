#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    c_map_prims
:class:     MapMsg, MakeMap
:test:
:author:    genuinemerit <dave@davidstitt.solutions>
"""
# pylint: disable=C0103
# pylint: disable=R0903
# pylint: disable=W0611
from pprint import pprint as pp
import html
import json
from c_func_basic import DotDict          # pylint: disable=E0401
from c_func_basic import FuncBasic        # pylint: disable=E0401
from c_bow_const import BowConst          # pylint: disable=E0401
Ġ = BowConst()
ß = FuncBasic()


####################
# Route Messages
####################
class MapMsg():
    """ If string-based (JSON) messages, deserialize to dict format.
        Construct dict-type of message matching a registered message type.
        Match message to appropriate service.
        Execute the service.
    """
    msg = None
    reg = None
    pub = None
    def __init__(self, p_msg=None, maker=None):
        self.__clear()
        if p_msg is not None and maker is not None:
            self.make(p_msg, maker)

    def __clear(self):
        """ Wipe the message """
        self.msg = {
            "type": Ġ.STR_Ø, "id": Ġ.STR_Ø, "size_xy": Ġ.TUPINT2_Ø, "desc": Ġ.STR_Ø,
            "name": Ġ.STR_Ø, "title": Ġ.STR_Ø, "style": Ġ.STR_Ø,
            "path": Ġ.STR_Ø, "itmtyp": Ġ.STR_Ø,
            "gid": Ġ.STR_Ø, "draw": Ġ.STR_Ø, "fill": Ġ.STR_Ø, "stroke": Ġ.STR_Ø, "zix": Ġ.INT_Ø,
            "tabix":  Ġ.INT_Ø, "thick": Ġ.NUM_Ø, "opaq": Ġ.NUM_Ø, "dash": Ġ.TUPINT2_Ø,
            "move": Ġ.TUPFLT2_Ø, "fontsize": Ġ.INT_Ø, "fontfam": Ġ.STR_Ø,
            "loc_xy": Ġ.TUPINT2_Ø, "words": Ġ.STR_Ø, "uid": Ġ.STR_Ø, "img_id": Ġ.STR_Ø}
        self.reg = {
            'gen': ["type", "id", "desc"],
            'svg': ["name", "size_xy", "title", "style"],
            'ref': ["path", "itmtyp"],
            'grp': ["gid", "fill", "stroke", "thick", "opaq", "dash", "move", "zix"],
            'elm': ["gid", "draw", "loc_xy", "size_xy", "zix", "tabix"],
            'use': ["gid", "uid", "move", "loc_xy", "size_xy", "zix", "tabix"],
            'tgp': ["gid", "fontsize", "fontfam", "zix"],
            'txt': ["gid", "loc_xy", "words", "zix", "tabix"],
            'img': ["gid", "img_id", "loc_xy", "size_xy", "zix", "tabix"],
            'axs': []}
        self.pub = {}

    def make(self, p_msg, maker):
        """ Deserialize string/JSON messages.
            Craft message in dict format with strong typing for registered service.
        :param: p_msg {str or dict}
        :param: maker {object} of class MakeMap
        """
        self.__clear()
        v_msg = None
        if isinstance(p_msg, str):
            v_msg = json.loads(p_msg)
        else:
            v_msg = p_msg

        def __check_fmt(v_msg):
            """ Reject message if malformed """
            self.pub = True
            if not isinstance(v_msg, dict):
                ß.log_me('Unknown message format: <{0}>'.format(str(type(p_msg))), Ġ.ERROR)
                self.pub = False
            elif 'type' not in v_msg.keys():
                ß.log_me('Missing required message key:  <type:>', Ġ.ERROR)
                self.pub = False
            elif v_msg['type'] not in self.reg:
                ß.log_me('Unknown message type: <{0}>'.format(v_msg['type']), Ġ.ERROR)
                self.pub = False
            return self.pub

        def __set_msg(v_msg):
            """ Format publishable message """
            # Log, ignore unrecognized attributes
            for attr in v_msg:
                if attr not in self.msg:
                    ß.log_me('Attribute not recognized: <{0}>'.format(attr), Ġ.WARN)
            # Set standard msg values if provided, else default to strongly-typed param
            for attr in self.msg:
                if attr in v_msg:
                    self.msg[attr] = v_msg[attr]
            # Construct pub message for registered message type
            self.pub = {}
            pub_attrs = list(set(self.reg['gen'] + self.reg[self.msg['type']]))
            for attr in v_msg:
                if attr not in pub_attrs:
                    ß.log_me('Attribute not used: <{0}>'.format(attr), Ġ.INFO)
            for attr in pub_attrs:
                self.pub[attr] = self.msg[attr]

        if __check_fmt(v_msg):
            __set_msg(v_msg)
            # Call the appropriate service
            self.serve(maker)

    def serve(self, maker):
        """ Send the current message to the MakeMap object
        :param: maker {object} of class MakeMap
        """
        if self.msg['type'] == 'svg':
            maker.make_svg(self.pub)
        elif self.msg['type'] == 'ref':
            maker.make_ref(self.pub)
        elif self.msg['type'] == 'grp':
            maker.make_grp(self.pub)
        elif self.msg['type'] == 'elm':
            maker.make_elm(self.pub)
        elif self.msg['type'] == 'use':
            maker.make_use(self.pub)
        elif self.msg['type'] == 'tgp':
            maker.make_tgp(self.pub)
        elif self.msg['type'] == 'txt':
            maker.make_txt(self.pub)
        elif self.msg['type'] == 'img':
            maker.make_img(self.pub)
        elif self.msg['type'] == 'axs':
            maker.make_axs()
        else:
            ß.log_me('No service found for: <{0}>'.format(self.msg['type']), Ġ.WARN)

####################
# Process Messages
####################
class MakeMap():
    """ Drawing primitives to support Map graphics.
        These functions create parts of SVG file(s) that descibe a map.
    """
    msg = None
    code = None
    catalog = None
    file_ls = None
    ntab = None
    xml_id = None
    def __init__(self):
        """ Boot up the map catalog """
        self.__clear()
    def __clear(self):
        """ Wipe the catalog """
        self.msg = DotDict({})   # attributes vary by message type. See MapMsg.
        self.code = ''           # Partially assembled SVG code associated with the msg
        self.catalog = {}        # type : { id: { msg:{name:value}, code:str} }
        self.file_ls = {}        # id: {type:<string>, path:{Path}, code:str}
        self.ntab = {}           # tokenized line returns and tabs based on message level
        self.xml_id = ''         # key to assembled XML file data in self.file_ls

    @classmethod
    def __id_hash(cls):
        """ Generate an ID value """
        hash_id = str(ß.hash_me(str(ß.get_dttm().curr_ts), Ġ.SHA1))
        return hash_id[0:-20]

    @classmethod
    def __set_string(cls, p_value, p_escape=False):
        """ Set to string or None.
            If p_escape is true, then escape the string.
        :returns: the string or None
        """
        v_value = None
        if p_value not in [0, '', None, Ġ.STR_Ø]:
            if p_escape:
                v_value = html.escape(str(p_value))
            else:
                v_value = str(p_value)
        return v_value

    @classmethod
    def __set_number(cls, p_value, p_float=False):
        """ Set to number or None.
            If p_float is true, then set the number to a float.
        :returns: the number or None
        """
        v_value = None
        if p_value in [None, '', Ġ.NUM_Ø, Ġ.INT_Ø]:
            v_value = None
        elif isinstance(p_value, (int, float))\
        or isinstance(int(p_value), int)\
        or isinstance(float(p_value), float):
            if p_float:
                v_value = float(p_value)
            else:
                v_value = int(p_value)
        return v_value

    def __set_num_pair(self, p_value, p_float=False):
        """ Set 2-tuple to numbers or None.
            If p_float is true, then set both numbers to a float.
        :returns: the 2 numbers or None
        """
        v_value = None
        if p_value in [None, 0, '', Ġ.TUPINT2_Ø, Ġ.TUPFLT2_Ø]:
            v_value = None
        elif isinstance(p_value, (tuple)):
            p_val_0, p_val_1 = p_value
            val_0 = self.__set_number(p_val_0, p_float)
            if val_0 is not None:
                val_1 = self.__set_number(p_val_1, p_float)
                v_value = (val_0, val_1)
        return v_value

    def __set_id(self):
        """ Set an element ID value. Generate a value if one is not provided.
            Verify that it is unique within the catalog.
        """
        if 'id' not in self.msg or self.msg.id in [None, 0, "", Ġ.STR_Ø]:
            self.msg['id'] = self.msg.type + "_" + self.__id_hash()
        self.msg.id = str(self.msg.id)
        for k_type in self.catalog:
            if self.msg.id in self.catalog[k_type]:
                ß.log_me('Duplicate ID in catalog: <{0}>'.format(self.msg.id), Ġ.ERROR)
        if self.msg.id in self.file_ls:
            ß.log_me('Duplicate ID in file list: <{0}>'.format(self.msg.id), Ġ.ERROR)

    def __set_name(self):
        """ Set element Name value. If no name provided, set Name to ID. """
        if 'name' not in self.msg or self.msg.name in [None, 0, "", Ġ.STR_Ø]:
            self.msg['name'] = self.msg.id
        self.msg.name = str(self.msg.name).lower()

    def __set_indent(self):
        """ Tokenize indentation based on the message level. """
        tlvl = Ġ.T1 * self.msg.level
        self.ntab = {}
        self.ntab[0] = Ġ.NT0 + tlvl
        self.ntab[1] = Ġ.NT1 + tlvl

    def __set_comment(self):
        """ Create in-line commented note for an element based on desc attribute.
        :returns:  SVG code containing an in-line comment
        """
        # comment = ' / level: {0}'.format(str(self.msg.level))
        comment = ''
        if 'desc' in self.msg and self.msg.desc not in [None, '', Ġ.STR_Ø]:
            comment = '{0}{1}'.format(self.msg.desc, comment)
        # else:
        #    comment = '{0}{1}'.format(self.msg.type, comment)
        if comment != '':
            comment = '{0}<!-- {1} -->'.format(self.ntab[0], comment)
        return comment

    def __set_basic_attrs(self, p_msg):
        """ Set attributes common to all message types """
        self.msg = DotDict(p_msg)
        self.msg.type = p_msg['type'].lower()
        self.__set_id()
        self.__set_name()
        self.msg.desc = self.__set_string(self.msg.desc, True)
        # Baseline identation-level
        def_level = {'svg':0, 'ref':1, 'grp':1, 'tgp':2, 'elm':2, 'use':2, 'img':2, 'txt':3}
        # Baseline hiearchical-order
        def_order = {'svg':0, 'ref':10, 'grp':20, 'tgp':30,
                     'elm':40, 'img':50, 'txt':60, 'use':100}
        self.msg.level = def_level[self.msg.type]
        self.msg.order = def_order[self.msg.type]

    def __set_size_xy(self):
        """ Set height and width values """
        if 'size_xy' not in self.msg or\
        self.msg.size_xy in [None, '', (), Ġ.TUPINT2_Ø]:
            self.msg['size_xy'] = (400, 400)
            ß.log_me('Set to default (400, 400): <size_xy>', Ġ.INFO)
        elif isinstance(self.msg.size_xy, list):
            size_xy = (int(self.msg.size_xy[0]), int(self.msg.size_xy[1]))
            self.msg.size_xy = size_xy
        if self.msg.size_xy[0] in [None, '']:
            self.msg.size_xy[0] = 400
            ß.log_me('Set to default (400, _): <size_xy[0]..x:width>', Ġ.INFO)
        if self.msg.size_xy[1] in [None, '']:
            self.msg.size_xy[1] = 400
            ß.log_me('Set to default (_, 400): <size_xy[1]..y:height>', Ġ.INFO)
        height = int(self.msg.size_xy[0])
        width = int(self.msg.size_xy[1])
        self.msg.size_xy = (height, width)

    def __set_file(self, path_nm=None):
        """ Set name and path of a static file and add it to the file_ls.
            The key to the file_ls is the item's ID on self.msg
        """
        if path_nm is None:
            path_nm = 'static/' + self.msg.name + '.' + self.msg.type
        for _, item in self.file_ls.items():
            if item.path.rqst == path_nm:
                ß.log_me('File name already in use: <{0}>'.format(path_nm), Ġ.ERROR)
        self.file_ls[self.msg.id] = DotDict({"type": str, "path": None})
        self.file_ls[self.msg.id].type = self.msg.type
        self.file_ls[self.msg.id].path = ß.get_path(path_nm)

    def __set_path(self):
        """  Set path attribute value.
             Verify that the path is valid and unique.
             This is for reference files which should already exist.
        """
        if 'path' not in self.msg or self.msg.path in [None, '', Ġ.STR_Ø]:
            ß.log_me('Valid file path is required when defining a <ref> message', Ġ.ERROR)
        path_nm = str(self.msg.path)
        v_path = ß.get_path(path_nm)
        if not v_path.exists:
            ß.log_me('Invalid reference. File not found: <{0}>'.format(path_nm), Ġ.ERROR)
        self.__set_file(path_nm)

    def __set_itmtyp(self):
        """ For external resources, define if it is a script or an image """
        if 'itmtyp' not in self.msg \
        or self.msg.itmtyp in [None, '', Ġ.STR_Ø] \
        or self.msg.itmtyp not in ['script', 'image']:
            ß.log_me('Missing or invalid reference item type: <{0}>'.format(str(self.msg.itmtyp)),
                     Ġ.ERROR)
        self.msg.itmtyp = str(self.msg.itmtyp)

    def __set_gid(self):
        """ Set Group ID (i.e., parent group) value and Element Level.
            Level is always one greater than the parent level.
            Items with no parent are at level 0 (zero).
        """
        if self.msg.gid in [None, 0, '', Ġ.STR_Ø]:
            self.msg.gid = None
        else:
            self.msg.gid = str(self.msg.gid)
            parent_found = False
            for pg in ['tgp', 'grp']:
                if pg in self.catalog:
                    if self.msg.gid in self.catalog[pg]:
                        parent_found = True
                        pg_level = self.catalog[pg][self.msg.gid]['msg'].level
                        pg_order = self.catalog[pg][self.msg.gid]['msg'].order
                        self.msg.level = pg_level + 1
                        self.msg.order = pg_order + 5
            if not parent_found:
                ß.log_me('Parent group not found: <{0}>'.format(self.msg.gid), Ġ.ERROR)

    def __set_uid(self):
        """ Set Use ID. Reference another item which is already defined internally. """
        if self.msg.uid in [None, 0, '', Ġ.STR_Ø]:
            self.msg.uid = None
        else:
            use_found = False
            for k_type in self.catalog:
                if self.msg.uid in self.catalog[k_type]:
                    self.msg.uid = "#" + str(self.msg.uid)
                    use_found = True
                    break
            if not use_found:
                ß.log_me('Referenced item ID not found: <{0}>'.format(self.msg.uid), Ġ.ERROR)

    def __set_img_id(self):
        """ Set Image ID. Reference a file which is already defined externally. """
        if self.msg.img_id in [None, 0, '', Ġ.STR_Ø]:
            self.msg.img_id = None
        else:
            self.msg.img_id = str(self.msg.img_id)
            if self.msg.img_id not in self.file_ls:
                ß.log_me('Referenced Image ID not found: <{0}>'.format(self.msg.img_id), Ġ.ERROR)

    def __set_draw(self):
        """ Assign draw_path value if it does not already exist
            This could be a place to verify and maybe optimize drawing commands.
        """
        if self.msg.draw in ['', None, Ġ.STR_Ø]:
            self.msg.draw = None
        else:
            self.msg.draw = str(self.msg.draw)

    def __render_desc(self):
        """ Add desc tag to code """
        if self.msg.desc is not None:
            self.code += "{0}<desc>{1}</desc>".format(self.ntab[1], self.msg.desc)

    def __render_zix(self):
        """ Add z_index style to code and adjust order """
        if self.msg.zix is not None:
            self.code += ' style="z-index: {0};"'.format(self.msg.zix)
            self.msg.order += int(self.msg.zix) * 2

    def __render_tabix(self):
        """ Add tabindex attribute to code """
        if self.msg.tabix is not None:
            self.code += ' tabindex="{0}"'.format(self.msg.tabix)

    def __catalog_item(self):
        """ Store msg and source code in the catalog """
        if self.msg.type in ['svg', 'xml']:
            if self.msg.type in self.catalog:
                ß.log_me('Only one <{0}> item can be stored'.format(self.msg.type), Ġ.ERROR)
            self.catalog[self.msg.type] = {'msg': self.msg, 'code': self.code}
        else:
            if self.msg.type not in self.catalog:
                self.catalog[self.msg.type] = {}
            self.catalog[self.msg.type][self.msg.id] = {'msg': self.msg, 'code': self.code}

    def __start_xml(self):
        """ Create a cataog entry for XML file.
            Put XML headers at top of file.
            Put SVG headers in after that.
        """
        self.msg = DotDict({"type":'xml'})
        self.__set_id()
        self.__set_name()
        self.__set_file('/dev/shm/' + self.msg.name + '.xml')
        self.code = '<?xml version="1.0"?>'
        self.code += '{0}<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '.format("\n")
        self.code += '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        self.code += self.catalog['svg']['code']
        self.xml_id = self.msg.id

    def __asm_refs(self):
        """ Pull in code from referenced scripts, then referenced images """
        ## Pull in code from externally referenced script items
        ## Then code from externally referenced image items (just show comments)
        for reft in ['script', 'image']:
            self.code += Ġ.NT0
            for _, ref_item in self.catalog['ref'].items():
                if ref_item['msg'].itmtyp == reft:
                    self.code += ref_item['code']

    def __asm_kids(self, pkey: str):
        """ Recursively add code for child-members of a group
            where the children are not use elements.
            Display items in hierarchical order.
        """
        child_code = ''
        # Find keys in the catalog whose gid = pkey and message type in ,,
        for msgt in ['grp', 'tgp', 'elm', 'txt', 'img', 'use']:
            kordkeys = [(kinv['msg'].order, kink)
                        for kink, kinv in self.catalog[msgt].items()
                        if kinv['msg'].gid == pkey]
            # Sort by hierarchical order:
            for kok in sorted(kordkeys):
                _, kkey = kok
                if msgt in ['grp', 'tgp']:
                    child_code += Ġ.NT0
                child_code += self.catalog[msgt][kkey]['code']
                child_code += self.__asm_kids(kkey)
                if self.catalog[msgt][kkey]['msg'].type in ['grp', 'tgp']:
                    self.msg.level = self.catalog[msgt][kkey]['msg'].level
                    self.__set_indent()
                    child_code += "{0}</g>".format(self.ntab[0])
        return child_code

    def __asm_groups(self):
        """ Add code for each uber-parent group.
            Get keys for groups or text-groups that have no parent,
            then order them hierarchically.
        """
        for ptyp in ['grp', 'tgp']:
            if ptyp in self.catalog:
                pordkeys = [(grpv['msg'].order, grpk)
                            for grpk, grpv in self.catalog[ptyp].items()
                            if grpv['msg'].gid is None]
                for pok in sorted(pordkeys):
                    _, pkey = pok
                    self.code += Ġ.NT0
                    self.code += self.catalog[ptyp][pkey]['code']
                    self.code += self.__asm_kids(pkey)
                    self.msg.id = self.catalog[ptyp][pkey]['msg'].id
                    self.msg.level = self.catalog[ptyp][pkey]['msg'].level
                    self.__set_indent()
                    self.code += "{0}</g>".format(self.ntab[0])

    def make_svg(self, p_msg: dict):
        """ Set up a new SVG object. """
        # Set the msg attributes
        p_msg['type'] = 'svg'
        self.__set_basic_attrs(p_msg)
        self.__set_size_xy()
        self.msg.style = self.__set_string(self.msg.style)
        self.msg.title = self.__set_string(self.msg.title, True)
        width = str(self.msg.size_xy[0])
        height = str(self.msg.size_xy[1])
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        self.code += '{0}<svg xmlns="http://www.w3.org/2000/svg"'.format(self.ntab[0])
        self.code += ' xmlns:xlink="http://www.w3.org/1999/xlink"'
        self.code += ' width="{0}" height="{1}"'.format(width, height)
        self.code += ' viewbox="0 0 {0} {1}"'.format(width, height)
        if self.msg.style is not None:
            self.code += ' style="{0}"'.format(self.msg.style)
        self.code += '>'
        if self.msg.title is not None:
            self.code += "{0}<title>{1}</title>".format(self.ntab[1], self.msg.title)
        self.__render_desc()
        self.__catalog_item()

    def make_ref(self, p_msg):
        """ Identify path to an externally-referenced resource. """
        p_msg['type'] = 'ref'
        self.__set_basic_attrs(p_msg)
        self.__set_path()
        self.__set_itmtyp()
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        # Externally referenced images are used in-line. So we just make a comment.
        if self.msg.itmtyp == 'image':
            self.code += "{0}<!-- Reference image: {1} -->".format(self.ntab[0], self.msg.path)
        else:
            self.code += '{0}<script type="text/ecmascript"'.format(self.ntab[0])
            self.code += ' xlink:href="{0}"'.format(self.file_ls[self.msg.id].path.abs)
            self.code += ' xlink:actuate="onLoad" xlink:show="other" xlink:type="simple" />'
        self.__catalog_item()
        return self.msg.id

    def make_grp(self, p_msg):
        """ Generate SVG for blocking out sections of an svg.
        Groups may be identified as parent groups or as child groups which are wrapped by a parent.
        There may be a hierarchy of such relationships. The gid identifies a parent object.
        Text groups are a variation on child groups, with a special set of attributes.
        """
        p_msg['type'] = 'grp'
        self.__set_basic_attrs(p_msg)
        self.__set_gid()  # << Also djusts level and order
        self.msg.fill = self.__set_string(self.msg.fill)
        self.msg.stroke = self.__set_string(self.msg.stroke)
        self.msg.thick = self.__set_number(self.msg.thick, True)
        self.msg.opaq = self.__set_number(self.msg.opaq, True)
        self.msg.dash = self.__set_num_pair(self.msg.dash)
        self.msg.move = self.__set_num_pair(self.msg.move)
        self.msg.zix = self.__set_number(self.msg.zix)
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        self.code += '{0}<g id="{1}"'.format(self.ntab[0], self.msg.id)
        if self.msg.fill is not None:
            self.code += ' fill="{0}"'.format(self.msg.fill)
        if self.msg.stroke is not None:
            self.code += ' stroke="{0}"'.format(self.msg.stroke)
        if self.msg.thick is not None:
            self.code += ' stroke-width="{0}"'.format(self.msg.thick)
        if self.msg.opaq is not None:
            self.code += ' stroke-opaq="{0}"'.format(self.msg.opaq)
        if self.msg.dash is not None:
            self.code += ' stroke-dasharray="{0}"'.format(self.msg.dash)
        if self.msg.move is not None:
            self.code += ' transform="translate({0})"'.format(self.msg.move)
        self.__render_zix()
        self.code += '>'
        self.__render_desc()
        self.__catalog_item()
        return self.msg.id

    def make_elm(self, p_msg):
        """ Generate code for a (Draw) Path element.
            Assume for now that all lines are drawn using path.
        """
        p_msg['type'] = 'elm'
        self.__set_basic_attrs(p_msg)
        self.__set_gid()
        self.__set_draw()
        self.msg.zix = self.__set_number(self.msg.zix)
        self.msg.tabix = self.__set_number(self.msg.tabix)
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        if self.msg.draw is not None:
            self.code += '{0}<path id="{1}" d="{2}"'.format(self.ntab[0],
                                                            self.msg.id, self.msg.draw)
        self.__render_zix()
        self.__render_tabix()
        self.code += ' />'
        self.__catalog_item()
        return self.msg.id

    def make_use(self, p_msg):
        """ Generate SVG code for a Use element.
            For my purposes, use references an internally-defined item.
        """
        p_msg['type'] = 'use'
        self.__set_basic_attrs(p_msg)
        self.__set_gid()
        self.__set_uid()
        self.msg.move = self.__set_num_pair(self.msg.move)
        self.msg.zix = self.__set_number(self.msg.zix)
        self.msg.tabix = self.__set_number(self.msg.tabix)
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        if self.msg.uid is not None:
            self.code += '{0}<use id="{1}" xlink:href="{2}"'.format(self.ntab[0],
                                                                    self.msg.id, self.msg.uid)
        if self.msg.move is not None:
            self.code += ' transform="translate({0},{1})"'.format(self.msg.move[0],
                                                                  self.msg.move[1])
        self.__render_zix()
        self.__render_tabix()
        if self.msg.desc is not None:
            self.code += '>'
            self.__render_desc()
            self.code += '{0}</use>'.format(self.ntab[0])
        else:
            self.code += ' />'
        self.__catalog_item()
        return self.msg.id

    def make_tgp(self, p_msg):
        """ Generate SVG code for a Text Group (child group).
        """
        p_msg['type'] = 'tgp'
        self.__set_basic_attrs(p_msg)
        self.__set_gid()  # << This also sets the level
        self.msg.fontsize = self.__set_number(self.msg.fontsize)
        self.msg.fontfam = self.__set_string(self.msg.fontfam)
        self.msg.zix = self.__set_number(self.msg.zix)
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        self.code += '{0}<g id="{1}"'.format(self.ntab[0], self.msg.id)
        self.code += ' font-family="{0}"'.format(self.msg.fontfam)
        self.code += ' font-size="{0}pt"'.format(self.msg.fontsize)
        self.__render_zix()
        self.code += '>'
        self.__render_desc()
        self.__catalog_item()
        return self.msg.id

    def make_txt(self, p_msg):
        """ Generate SVG code for a Text Element. """
        p_msg['type'] = 'txt'
        self.__set_basic_attrs(p_msg)
        self.__set_gid()  # << This also sets the level
        self.msg.words = self.__set_string(self.msg.words, True)
        self.msg.loc_xy = self.__set_num_pair(self.msg.loc_xy)
        self.msg.zix = self.__set_number(self.msg.zix)
        self.msg.tabix = self.__set_number(self.msg.tabix)
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        self.code += '{0}<text id="{1}"'.format(self.ntab[0], self.msg.id)
        if self.msg.loc_xy is not None:
            self.code += ' x="{0}" y="{1}"'.format(self.msg.loc_xy[0], self.msg.loc_xy[1])
        self.__render_zix()
        self.__render_tabix()
        self.code += '>{0}</text>'.format(self.msg.words)
        self.__catalog_item()
        return self.msg.id

    def make_img(self, p_msg):
        """ Generate SVG code for an Image element reference.
            For my purposes, Img always references an externally-defined item.
        """
        p_msg['type'] = 'img'
        self.__set_basic_attrs(p_msg)
        self.__set_gid()
        self.__set_img_id()
        self.msg.loc_xy = self.__set_num_pair(self.msg.loc_xy)
        self.msg.size_xy = self.__set_num_pair(self.msg.size_xy)
        self.msg.zix = self.__set_number(self.msg.zix)
        self.msg.tabix = self.__set_number(self.msg.tabix)
        # Generate code
        self.__set_indent()
        self.code = self.__set_comment()
        self.code += '{0}<image id="{1}"'.format(self.ntab[0], self.msg.id)
        self.code += ' xlink:href="{0}"'.format(self.file_ls[self.msg.img_id]['path'].abs)
        if self.msg.loc_xy is not None:
            self.code += ' x="{0}" y="{1}"'.format(self.msg.loc_xy[0], self.msg.loc_xy[1])
        if self.msg.size_xy is not None:
            self.code += ' width="{1}" height="{0}"'.format(self.msg.size_xy[0],
                                                            self.msg.size_xy[1])
        self.__render_zix()
        self.__render_tabix()
        if self.msg.desc is not None:
            self.code += '>'
            self.__render_desc()
            self.code += '{0}</image>'.format(self.ntab[0])
        else:
            self.code += ' />'
        self.__catalog_item()
        return self.msg.id

    def make_axs(self):
        """ Generate SVG for axis lines and markers.
            Derive measures based on size of map.
        """
        # pylint: disable=R0914
        ⅎinc = 100        # increment amount for markers
        ⅎoff = 10         # reverse coord offset: for x-axis markers, it is y-start & vice-versa
        ⅎoffΩ = ⅎoff * 2  # end point offset of reverse coordinates
        # start and end coordinates for axis lines:
        minX = minY = 60  # starting offset for axis lines
        maxX, maxY = self.catalog['svg']['msg'].size_xy
        maxX -= (minX * 2) #  Ɣoff * 2 is the end-point offset for axis lines
        maxY -= (minY * 2)
        # Axis lines group
        self.make_grp({'id':'xy_axes', 'desc':"X and Y Axes", 'stroke': "blue",
                       'thick': 1.0, 'opaq': 0.7, 'zix': 2})
        # X and Y axis lines
        for Ɣid, Ɣto in [('x_axis', str(maxX) + ",0"),
                         ('y_axis', "0," + str(maxY))]:
            self.make_elm({'id': Ɣid, 'gid': 'xy_axes', 'zix': 3,
                           'draw': "M {0},{1} l {2}".format(str(minX), str(minY), Ɣto)})
        # X-axis and Y-axis starting markers
        for Ɣid, Ɣfrom, Ɣto in [('x_mark', str(minX) + "," + str(minY - ⅎoff), "0," + str(ⅎoffΩ)),
                                ('y_mark', str(minX - ⅎoff) + "," + str(minY), str(ⅎoffΩ) + ",0")]:
            self.make_elm({'id': Ɣid, 'gid': 'xy_axes', 'zix': 3,
                           'draw': "M {0} l {1}".format(Ɣfrom, Ɣto)})
        # X and Y axis markers
        for ⅎuid, ⅎmax  in [('x_mark', maxX), ('y_mark', maxY)]:
            ⅎmark = ⅎinc
            while ⅎmark < ⅎmax:
                ⅎXY = {'x_mark': ((ⅎmark, 0), 0), 'y_mark': ((0, ⅎmark), 10000)}
                uid = self.make_use({'gid': 'xy_axes', 'uid': ⅎuid, 'move': ⅎXY[ⅎuid][0],
                                     'zix':3})
                self.catalog['use'][uid]['msg'].order += ⅎmark + ⅎXY[ⅎuid][1]
                ⅎmark += ⅎinc
        # Axis lines text group
        self.make_tgp({'id':'xy_labels', 'gid': "xy_axes", 'fontsize':8, 'fontfam':"sans-serif",
                       'zix': 2})
        # Axis lines text elements
        for ⅎaxis, ⅎmax, ⅎmin  in [('x', maxX, minX), ('y', maxY, minY)]:
            ⅎmark = ⅎmin
            ⅎtext = 0
            while ⅎmark < ⅎmax:
                ⅎXY = {'x': ((ⅎmark - 10, minY - ⅎoffΩ), 0),
                       'y': ((minX - (ⅎoffΩ + 20), ⅎmark + 4), 10000)}
                tid = self.make_txt({'gid': 'xy_labels', 'words': str(ⅎtext),
                                     'loc_xy': ⅎXY[ⅎaxis][0], 'zix': 3})
                self.catalog['txt'][tid]['msg'].order += ⅎmark + ⅎXY[ⅎaxis][1]
                ⅎtext += ⅎinc
                ⅎmark += ⅎinc

    def assemble(self):
        """ Assemble entire SVG object.
            Put it all together and save as content for an XML file.
        """
        self.__start_xml()
        self.__asm_refs()
        self.__asm_groups()
        self.code += "\n</svg>\n"
        ## Store the XML-SVG code with its file reference
        self.file_ls[self.xml_id]['code'] = self.code

    def publish(self):
        """ Write assembled XML file to specified target path. """
        xml_path = self.file_ls[self.xml_id]['path'].rqst
        with open(xml_path, 'w') as xmlf:
            xmlf.write(self.file_ls[self.xml_id]['code'])
            xmlf.close()
        self.file_ls[self.xml_id]['path'] = ß.get_path(xml_path)

    def show(self, p_browser: str):
        """ Display the XML/SVG file in specified browser """
        v_browser = str(p_browser.lower())
        if v_browser in ['chrome', 'firefox', 'google-chrome-stable', 'opera']:
            if v_browser == 'chrome':
                v_browser = 'google-chrome-stable'
            cmd = "{0} {1}".format(v_browser, str(self.file_ls[self.xml_id]['path'].abs))
            ß.run_cmd(cmd)

    def remove(self):
        """ Remove assembled XML file from specified target path. """
        cmd = "rm {0}".format(str(self.file_ls[self.xml_id]['path'].abs))
        ß.run_cmd(cmd)


# ======================================
# MAIN / prototype test
# ======================================
if __name__ == "__main__":
    MS = MapMsg()
    MM = MakeMap()
    ## SVG message:
    MS.make({"type":"svg", "desc":"The Gardens at 52 Welles", "name":"gardenmap",
             "size_xy":(2100, 1800), "title":"Garden Map", "style":"margin:10px;"}, MM)
    ## REF message:
    MS.make('{"type":"ref", "id":"saskmap", "path":"static/saskantinon.jpeg", '+\
            '"desc":"Map of Saskantinon", "itmtyp":"image"}', MM)
    MS.make({'type':'ref', "id":"my_cat", 'path':'static/cat.svg', "itmtyp":"image",
             'desc':"Smelly Cat"}, MM)
    MS.make({'type':'ref', 'path':'script/map_functions.js', 'itmtyp':"script",
             'desc':"Interactive Map Functions"}, MM)
    ## GRP messages:
    MS.make({'type':'grp', 'id':'map_border', 'desc':"Map Elements", 'stroke':"blue",
             'thick':0.5, 'opaq':0.5, 'dash':(10, 10), 'zix':0}, MM)
    MS.make({'type':'grp', 'id':'back_ground', 'gid':'map_border', 'desc':"Background Elements",
             'fill':"#e6ffe6", "zix":0}, MM)
    ## ELM and USE messages:
    MS.make('{"type":"elm", "id":"back_ground_path", "gid":"back_ground", ' +\
            '"draw":"M 0,0 l 2100,0 l 0,1800 l -2100,0 Z", "zix":"0"}', MM)
    MS.make({'type':'elm', 'id':'top_border', 'gid':'map_border',
             'draw':"M 0,0 m 40,40 l 2020,0", 'zix': 1}, MM)
    MS.make({'type':'elm', 'id':'left_border', 'gid':'map_border',
             'draw':"M 0,0 m 40,40 l 0,1720", 'zix': 1}, MM)
    MS.make({'type':'use', 'id':'bottom_border', 'gid':'map_border', 'uid':'top_border',
             'move':(0, 1720), 'zix': 1}, MM)
    MS.make({'type':'use', 'id':'right_border', 'gid':'map_border', 'uid': 'left_border',
             'move':(2020, 0), 'zix': 1}, MM)
    ## TGP and TXT messages:
    MS.make({'type':'grp', 'id':'ta_grp', 'desc':"Title and Axis Text", 'fill':'black',
             "zix": 0}, MM)
    MS.make({'type':'tgp', 'id':'title_text', 'gid':'ta_grp', 'fontsize':18, 'fontfam':'serif',
             'zix':1}, MM)
    MS.make({'type':'txt', 'gid':'title_text', 'loc_xy':(1100, 20),
             'words':"Dave & Lex's Garden Landscape", "zix":2}, MM)
    MS.make({'type':'tgp', 'id':'compass', 'gid':'ta_grp', 'fontsize':24,
             'fontfam':'sans-serif', 'zix':1, 'desc':"Directional markers"}, MM)
    MS.make({'type':'txt', 'gid':'compass', 'loc_xy':(30, 30), 'words':"NW", "zix":2}, MM)
    MS.make({'type':'txt', 'gid':'compass', 'loc_xy':(30, 1790), 'words':"SW", "zix":2}, MM)
    MS.make({'type':'txt', 'gid':'compass', 'loc_xy':(2050, 1790), 'words':"SE", "zix":2}, MM)
    MS.make({'type':'txt', 'gid':'compass', 'loc_xy':(2050, 30), 'words':"NE", "zix":2}, MM)
    ## IMG message
    MS.make('{"type":"grp", "id":"pix_grp", "desc":"Embedded images", "fill":"black", ' +\
            '"zix":"1"}', MM)
    MS.make({'type':'img', "id":"sask_pic", "gid":"pix_grp", "img_id":"saskmap",
             'desc':"Saskantinon Map", "loc_xy":(400, 400), "size_xy":(600, 600),
             'zix':2, 'tabix': 1}, MM)
    ## Call to create predefined AXES:
    MS.make({"type":"axs"}, MM)
    ## Assemble, publish, show, remove:
    MM.assemble()
    MM.publish()
    # MM.show('chrome')
    MM.show('firefox')
    # MM.show('opera')
    MM.remove()
