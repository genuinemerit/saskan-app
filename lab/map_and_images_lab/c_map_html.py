#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    c_map_html
:class:     MapHtml
:test:      TestMapHtml
:author:    genuinemerit <dave@davidstitt.solutions>
"""
# pylint: disable=C0103
# pylint: disable=E0401
# pylint: disable=R0902
# pylint: disable=R0913
# pylint: disable=W0611
from pprint import pprint as pp
from c_form_html import FormHtml
HT = FormHtml()

class MapHtml():
    """
Render HTML for Map Maker application.
    """
    def __init__(self):
        self.menu_btns = None
        self.mn_show = None
        self.svg_form = None
        self.ref_btns = None
        self.ref_forms = None
        self.grp_btns = None
        self.grp_forms = None
        self.elm_btns = None
        self.elm_forms = None
        self.svg_code = None
        self.clear()

    def clear(self):
        """ Wipe content of all templated Map Maker HTML objects """
        self.menu_btns = ''
        self.mn_show = {'res':('Wipe All', 'Wipe All', 'True'),
                        'map':('Show Map', 'Hide Map', 'True'),
                        'svg':('Edit SVG', 'Hide SVG', 'True'),
                        'ref':('Edit Ref File', 'Hide Ref File(s)', 'True'),
                        'grp':('Edit Group', 'Hide Group(s)', 'True'),
                        'elm':('Edit Element', 'Hide Element(s)', 'True')}
        self.svg_form = ''
        self.ref_btns = ''
        self.ref_forms = ''
        self.grp_btns = ''
        self.grp_forms = ''
        self.elm_btns = ''
        self.elm_forms = ''
        self.svg_code = ''

    def make_menu_buttons(self):
        """ Generate HTML code for 'menu bar' buttons. """
        html = ''
        for menu_key, (menu_nm1, menu_nm2, menu_mode) in self.mn_show.items():
            disp_nm = menu_nm1 if menu_mode == 'True' else menu_nm2
            btn = HT.button(disp_nm, "submit", "/menu/{0}".format(menu_key))
            inp = HT.input("hidden", "show_{0}".format(menu_key), menu_mode)
            form = HT.form(btn + inp, "post")
            html += HT.tdata(form)
        html = HT.table(HT.trow(html))
        self.menu_btns = html
        return html

    def set_show_mode(self, p_keys, p_mode):
        """ Set the mode of identified menus to provided value
            p_keys {list} of menu keys
            p_mode {string} in ['True', 'False']
        """
        if not isinstance(p_keys, list):
            p_keys = [p_keys]
        for menu_key in p_keys:
            menu_nm1, menu_nm2, _ = self.mn_show[menu_key]
            self.mn_show[menu_key] = (menu_nm1, menu_nm2, p_mode)

    def make_add_list_buttons(self, p_path):
        """ Generate buttons to request list or add-new. """
        btnvals = {
            'ref': {'html':"<h2>Locate Image or Script Files</h2>",
                    'txt': "Referenced File(s)"},
            'grp': {'html':"<h2>Define Group(s)</h2>",
                    'txt': "Group(s)"},
            'elm': {'html':"<h2>Define Element(s)</h2>",
                    'txt': "Element(s)"},
        }
        html = btnvals[p_path]['html']
        btn = HT.button("List {0}".format(btnvals[p_path]['txt']),
                        "submit", "/{0}/list".format(p_path))
        btn += ("&nbsp;" * 3)
        btn += HT.button("Add a {0}".format(btnvals[p_path]['txt'][:-3]),
                         "submit", "/{0}/add".format(p_path))
        btn = HT.table(HT.trow(HT.tdata(btn, "2")))
        html += btn
        form = HT.form(html, "post")
        if p_path == 'ref':
            self.ref_btns = form
        elif p_path == 'grp':
            self.grp_btns = form
        elif p_path == 'elm':
            self.elm_btns = form
        return form

    def set_list_btns(self, s_path):
        """ Handle list/add buttons for this group of forms.
            May expand this section later to select location, for example.
        """
        self.set_show_mode(s_path, 'False')
        self.make_add_list_buttons(s_path)

    def make_svg_form(self, vals):
        """ Generate HTML code for the SVG form.
            Set its values using those passed in on params.
    @param vals {dict} - Indexed by same keys as attrs
        """
        attrs = {'id': 'ID', 'desc': 'Description', 'name': 'Name', 'title': 'Title',
                 'style': 'Inline styling', 'width': 'Width (px)', 'height': 'Height (px)'}
        self.svg_form = ''
        html = ''
        for attr, label in attrs.items():
            svg_nm = "svg_{0}".format(attr)
            formlines = HT.tdata(label)
            formlines += HT.tdata(HT.input("text", svg_nm, vals[svg_nm]))
            formlines = HT.trow(HT.tdata(formlines))
            html += formlines
        edit_verb = 'Create' if vals['svg_id'] == '' else 'Update'
        btn = HT.button(edit_verb, "submit", "/svg/edit")
        if edit_verb == 'Update':
            btn += ("&nbsp;" * 3) + HT.button("Delete", "submit", "/svg/delete")
        html += HT.trow(HT.tdata(btn, p_colspan="2"))
        html = HT.form(HT.table(html), "post")
        self.svg_form = '<h2>Create SVG</h2>\n<p>Define the SVG header...</p>\n' + html
        return self.svg_form

    @classmethod
    def __set_counter_line(cls, cnt, path):
        """ Format input row that identifies count of the item """
        formline = HT.tdata('Item #')
        formline += HT.tdata(HT.input("text", "{}_num".format(path), str(cnt), None, True))
        return HT.trow(formline)

    @classmethod
    def __set_text_inputs(cls, cnt, path, attrs, vals):
        """ Format input rows that are standard text inputs
            attrs {dict} : {attr_nm: attr_lbl, ...}  Example: {'id': 'ID'}
            vals {dict} : created by get_data() method
        """
        html = ''
        for attr, label in attrs.items():
            formline = HT.tdata(label)
            formline += HT.tdata(HT.input("text", '{0}_{1}'.format(path, attr),
                                          vals[cnt]["{0}_".format(path) + attr]))
            formline = HT.trow(formline)
            html += formline
        return html

    @classmethod
    def __set_upd_delete_btns(cls, cnt, path, vals):
        """ Format button HTML for 'update' and 'delete' """
        btn = HT.button("Update", "submit", "/{0}/edit".format(path))
        if vals[cnt]['{0}_id'.format(path)] != '':
            btn += ('&nbsp;' * 3) + HT.button("Delete", "submit", "/{0}/delete".format(path))
        return HT.trow(HT.tdata(btn, "2"))

    def make_ref_forms(self, vals):
        """ Generate HTML code for the reference item form(s). """
        self.ref_forms = ''
        for cnt in range(1, len(vals) + 1):
            html = self.__set_counter_line(cnt, 'ref')
            attrs = {'id': 'ID', 'path': 'Path'}
            html += self.__set_text_inputs(cnt, 'ref', attrs, vals)
            formline = HT.tdata("Type")
            opts = {"Image": ("image", False), "Script": ("script", False), }
            if vals[cnt]['ref_itmtyp'] == 'script':
                opts["Script"] = ("script", True)
            formline += HT.tdata(HT.select("ref_itmtyp", opts))
            html += HT.trow(formline)
            html += self.__set_upd_delete_btns(cnt, 'ref', vals)
            self.ref_forms += HT.form(HT.table(html), "post")
        return self.ref_forms

    def make_grp_forms(self, vals):
        """ Generate HTML code for the group item form(s). """
        self.grp_forms = ''
        for cnt in range(1, len(vals) + 1):
            html = self.__set_counter_line(cnt, 'grp')
            attrs = {'id':"ID", 'desc':"Desc", 'gid':"Parent ID", 'fill':"Fill Color",
                     'stroke':"Stroke Color", 'thick':"Thickness", 'opaq':"Opaqueness Factor",
                     'dash':"Dash Array", 'move':"Move Instructions", 'zix':"Z-Index"}
            html += self.__set_text_inputs(cnt, 'grp', attrs, vals)
            html += self.__set_upd_delete_btns(cnt, 'grp', vals)
            self.grp_forms += HT.form(HT.table(html), "post")
        return self.grp_forms

    def make_elm_forms(self, vals):
        """ Generate HTML code for the element item form(s). """

        pp(("vals: ", vals))

        self.elm_forms = ''
        for cnt in range(1, len(vals) + 1):
            html = self.__set_counter_line(cnt, 'elm')
            attrs = {'id':"ID", 'desc':"Desc", 'gid':"Parent ID", 'draw':"Draw Instruction",
                     'zix':"Z-Index", 'tabix':"Tab-Index"}
            html += self.__set_text_inputs(cnt, 'elm', attrs, vals)
            # Element x,y attributes
            xy_items = {'loc_x':('Horz start (x)', 'elm_loc_x', 'elm_loc_xy', 0),
                        'loc_y':('Vert start (y)', 'elm_loc_y', 'elm_loc_xy', 1),
                        'size_x':('Horz end (x)', 'elm_size_x', 'elm_size_xy', 0),
                        'size_y':('Vert end (y)', 'elm_size_y', 'elm_size_xy', 1)}
            for _, (xy_lbl, xy_nm, xy_val, xy_ix) in xy_items.items():
                formline = HT.tdata(xy_lbl)

                pp(("vals[cnt][xy_val]: ", vals[cnt][xy_val]))

                formline += HT.tdata(HT.input("text", xy_nm, vals[cnt][xy_val][xy_ix]))
                formline = HT.trow(formline)
                html += formline
            # Buttons
            html += self.__set_upd_delete_btns(cnt, 'elm', vals)
            self.elm_forms += HT.form(HT.table(html), "post")
        return self.elm_forms
