#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Map Message-Info Server
:module:    map_msg_register
:class:     MapMsgRegister
:author:    genuinemerit <dave@davidstitt.solutions>

Back-end / middle-ware queue-aware information manager.

Not a daemon.
Does not call or provide any services. 
It get called directly, via its get_data() function, from the map_msg_service,
 and could be considered as "bound" to that module.

Standalone module that receives direct calls only from map_msg_service.
Manages the services metadata registry as an in-memory queue.
Returns messages to map_msg_service matching registered message types.

To DO:
1) Eventually, explore using Kafka or ZeroMQ or RabbitMQ to queue up requests, move
   towards a more completely message-based architecture.
2) In the meantime, keep moving towards treating all component interactions as messages.
"""
## General Purpose imports     ##
#################################
import json
from collections import OrderedDict as OrdD
from os import path
from pprint import pprint as pp  # pylint: disable=W0611

from bow_func_basic import FuncBasic

FC = FuncBasic()


class MapMsgRegister():
    """
        This class defines structure of messages supported for the Map Builder app.
        The message metadata is managed on an in-memory /dev/shm file) named "registry.que".
    """
    registry_path = None
    func_name = None
    reg_d = None
    reg_j = None

    def __init__(self):
        """ Initialize the class """
        self.registry_path = "/dev/shm/registry.que"
        self.__register()


    def __set_xy(self, msgk, p_attr):
        """ Set xy attribute """
        if p_attr == 'loc':
            self.reg_d[msgk]['loc_xy'] = ('Horz, Vert (px, px)', 'required', 'integer',
                                          'xy', 'size_6')
        elif p_attr == 'size':
            self.reg_d[msgk]['size_xy'] = ('Width, Height (px, px)', 'required', 'integer',
                                           'xy', 'size_6')
        else:
            self.reg_d[msgk][p_attr + '_xy'] = ('X, Y (px, px)', 'required', 'integer',
                                                'xy', 'size_6')

    def __set_idx(self, msgk, p_attr):
        """ Set index attribute """
        if p_attr.lower() == 'z':
            self.reg_d[msgk]['zix'] = ('Z-Index', 'text', 'integer', 'size_6')
        elif p_attr.lower() == 'tab':
            self.reg_d[msgk]['tabix'] = ('Tab-Index', 'text', 'integer', 'size_6')
        else:
            self.reg_d[msgk][p_attr + 'ix'] = (p_attr.capitalize() + '-Index',
                                               'text', 'integer', 'size_6')

    def __set_svg_msg(self, msgk):
        """ Define form and data attributes for SVG Header """
        self.reg_d[msgk]['order'] = (
            'rank_01', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['title'] = ('Title', 'text')
        self.reg_d[msgk]['style'] = ('Inline style', 'text')
        self.__set_xy(msgk, 'size')

    def __set_ref_msg(self, msgk):
        """ Define form and data attributes for Reference Items """
        self.reg_d[msgk]['order'] = ('rank_02', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['path'] = ('Path', 'text', 'required', 'path')
        self.reg_d[msgk]['itmtyp'] = ('msg', 'select', 'required', 'opt_image', 'opt_script')

    def __set_grp_msg(self, msgk):
        """ Define form and data attributes for Group Items """
        self.reg_d[msgk]['order'] = ('rank_03', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['gid'] = ('Parent ID', 'text', 'size_32')
        self.reg_d[msgk]['fill'] = ('Fill Color', 'text')
        self.reg_d[msgk]['stroke'] = ('Stroke Color', 'text')
        self.reg_d[msgk]['thick'] = ('Thickness', 'text', 'number')
        self.reg_d[msgk]['opaq'] = ('Opaqueness Factor', 'text', 'number')
        self.reg_d[msgk]['dash'] = ('Dash Array (len, space)', 'xy', 'integer', 'size_2')
        self.reg_d[msgk]['move'] = ('Move Instructions', 'text')
        self.__set_idx(msgk, 'z')

    def __set_elm_msg(self, msgk):
        """ Define form and data attributes for Basic Element Items """
        self.reg_d[msgk]['order'] = ('rank_04', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['draw'] = ('Draw Instructions', 'text')
        self.__set_xy(msgk, 'loc')
        self.__set_xy(msgk, 'size')
        self.__set_idx(msgk, 'z')
        self.__set_idx(msgk, 'tab')

    def __set_use_msg(self, msgk):
        """ Define form and data attributes for Use-Element Items """
        self.reg_d[msgk]['order'] = ('rank_05', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['uid'] = ('Use ID', 'text', 'required')
        self.reg_d[msgk]['scale'] = ('Scale', 'number')
        self.__set_xy(msgk, 'move')
        self.__set_xy(msgk, 'loc')
        self.__set_xy(msgk, 'size')
        self.__set_idx(msgk, 'z')
        self.__set_idx(msgk, 'tab')

    def __set_tgp_msg(self, msgk):
        """ Define form and data attributes for Text Group Items """
        self.reg_d[msgk]['order'] = ('rank_06', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['fontsize'] = ('Font Size', 'text', 'integer', 'size_2', 'required')
        self.reg_d[msgk]['fontfam'] = ('Font Family', 'text', 'required')
        self.__set_idx(msgk, 'z')

    def __set_txt_msg(self, msgk):
        """ Define form and data attributes for Text Items """
        self.reg_d[msgk]['order'] = ('rank_07', 'hide', 'text', 'readonly', 'meta')
        self.__set_xy(msgk, 'loc')
        self.reg_d[msgk]['words'] = ('Words', 'text', 'required')
        self.__set_idx(msgk, 'z')
        self.__set_idx(msgk, 'tab')

    def __set_img_msg(self, msgk):
        """ Define form and data attributes for Image Items """
        self.reg_d[msgk]['order'] = ('rank_08', 'hide', 'text', 'readonly', 'meta')
        self.reg_d[msgk]['img_id'] = ('Image ID', 'text', 'required')
        self.__set_xy(msgk, 'loc')
        self.__set_xy(msgk, 'size')
        self.__set_idx(msgk, 'z')
        self.__set_idx(msgk, 'tab')

    def __set_common_attrs(self):
        """ Define attributes included in all messages """
        for msgk in self.func_name:
            self.reg_d[msgk]['msg'] = (msgk, 'hide', 'text', 'readonly')
            self.reg_d[msgk]['delete'] = ('delete', 'text', 'hide', 'readonly', 'default_False')
            self.reg_d[msgk]['num'] = ('#', 'text', 'hide', 'readonly', 'meta')
            self.reg_d[msgk]['id'] = ('ID', 'text', 'size_32')
            if msgk == 'svg':
                self.reg_d[msgk]['gid'] = ('Parent ID', 'text', 'size_32')
            else:
                self.reg_d[msgk]['gid'] = ('Parent ID', 'text', 'required', 'size_32')
            self.reg_d[msgk]['name'] = ('Name', 'text', 'size_32')
            self.reg_d[msgk]['desc'] = ('Desc', 'text', 'size_64')

    def __register(self):
        """ Register accepted message formats.
            Save in JSON format to disk and to an in-memory file.
            Read it back into program memory.
        """
        self.reg_d = OrdD()
        # Set up the message structures
        self.func_name = OrdD()
        self.func_name['svg'] = self.__set_svg_msg
        self.func_name['ref'] = self.__set_ref_msg
        self.func_name['grp'] = self.__set_grp_msg
        self.func_name['elm'] = self.__set_elm_msg
        self.func_name['use'] = self.__set_use_msg
        self.func_name['tgp'] = self.__set_tgp_msg
        self.func_name['txt'] = self.__set_txt_msg
        self.func_name['img'] = self.__set_img_msg
        for msgk in self.func_name:
            self.reg_d[msgk] = OrdD()
        self.__set_common_attrs()
        for msgk, do_msg_set_up in self.func_name.items():
            do_msg_set_up(msgk)
        # Rank the message keys
        msg_reduce = {key: item['order'][0] for key, item in self.reg_d.items()}
        msg_reduce = sorted(msg_reduce.items(), key=lambda x: x[1])
        msg_keys = OrdD()
        msg_keys = [val[0] for val in msg_reduce]
        self.reg_d['list'] = msg_keys
        with open(self.registry_path, 'w') as regf:
            regf.write(json.dumps(self.reg_d))
            regf.close()
        with open(self.registry_path, 'r') as regf:
            self.reg_j = regf.read()
            self.reg_d = json.loads(self.reg_j)

    ##################################
    # Public Function
    ##################################
    def get_info(self, msgk=None, attrk=None):
        """ Return message-structure metadata info for requested message key.
            Called only as info-level support for REST services in:  map_msg_service)
        """
        rebuild_registry = True
        if path.isfile(self.registry_path):
            with open(self.registry_path, 'r') as regf:
                self.reg_j = regf.read()
                self.reg_d = json.loads(self.reg_j)
                if self.reg_j and self.reg_j not in (None, '') and self.reg_d:
                    rebuild_registry = False
        if rebuild_registry:
            self.__register()
        if msgk in (None, ''):
            info_j = self.reg_j
        elif msgk.lower() not in self.reg_d:
            info_d = dict()
            info_d['Err'] = "Invalid message key '{0}'".format(msgk)
            info_j = json.dumps(info_d)
        else:
            msgk = msgk.lower()
            attrk = attrk.lower() if attrk not in (None, '') else None
            if attrk in (None, '') or attrk not in self.reg_d[msgk]:
                info_j = json.dumps(self.reg_d[msgk])
            else:
                info_j = json.dumps(self.reg_d[msgk][attrk])            
        return info_j
