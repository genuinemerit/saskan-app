#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module defines a Class to assist with rendering views for Views._TXTS.
"""
# import math
import random
# import sys
# sys.path.append('.')
# from main import utils
from pprint import pprint as pp

# FUNCTIONS


# CLASS
# =========================

class Views(object):

    """
    Provide helper functions for managing displays.
    This is used to assist with HTML formatting, especially when similar
    displays are used across multiple screens.  But it also provides a way to
    quickly separate text from the main line of the program without having to
    edit the text strings JSON library.  Items identified in this class may
    later be moved to the even more abstracted JSON library. The idea is to
    be able (hopefully!) to make it easier to localize the game for multiple
    languages.
    """
    _TXTS = {}

    def __init__(self, txts):
        """
        Instantiate new Views object.
            txts:    text dicts "app", "astro"
        """
        Views._TXTS = txts

    @classmethod
    def app_headers(cls):
        """
        Provide standard texts for base.html app header fields

        Returns:
            (page_title, page_subtitle, page_label)
        """
        return (Views._TXTS["bow"], Views._TXTS["bowDesc"], Views._TXTS["bow"])

    @classmethod
    def app_navs(cls):
        """
        Provide standard links for base.html nav fields

        Returns:
            [nav0, nav1, nav2, nav3, nav4, nav5]
        """
        nav = ["<a href='bow'>Home</a>",
               "".join(["<a href='bang'>", Views._TXTS["bang"], "</a>"]),
               "".join(["<a href='kill'>", Views._TXTS["kill"], "</a>"]),
               "", "", ""]
        return nav

    @classmethod
    def start_page(cls):
        """
        Provide sector content for start page

        Returns:
            [sector0, sector1, sector2, sector3, sector4, sector5]
        """
        sector = ["".join(["<hr />", Views._TXTS["start"], "<br />",
                          Views._TXTS["restart"]]),
                  "".join(["<hr />Launch the <a href='bang'>",
                          Views._TXTS["bang"], "</a>!"]),
                  "".join(["<hr /><a href='kill'>", "Stop the universe</a>, ",
                           "I want to get off."]),
                  "", "", ""]
        return sector

    @classmethod
    def show_bang(cls, unvo):
        """
        Provide sector content for Launch the Big Bang page

        Args:
            unvo is a unverse object

        Returns:
            [sector0, sector1, sector2, sector3, sector4, sector5]
        """
        cdat = unvo.rulo.get_cur_step()
        # Display results from previous steps
        prvstep = "<hr />\n<br />" + Views._TXTS["restart"]
        plst = []
        for pord in range (1, cdat["ord_cur"]):
            pdat = unvo.rulo.get_num_step(pord)
            if pord < 6:
                pdat["amt"] = '{:.2f}'.format(pdat["vals"]["pct"]) + " %"
            else:
                pdat["amt"] = str(int(pdat["vals"]["amt"]))
            plst.append(pdat)
        if cdat["stat"] == "done":
            cdat["amt"] = str(int(cdat["vals"]["amt"]))
            plst.append(cdat)
        for dat in plst:
            prvstep += "".join(["\n<br />", dat["lbl"], ": ", dat["amt"]])
        if cdat["stat"] == "done":
            # Display the done message
            curstep = "<br />" + cdat["vals"]["msg"]
            forminp = ""
        else:
            # Display the submit button)
            curstep = "".join(["<br />", Views._TXTS["galaxyPcts"]])
            forminp = "".join(['<form method="post" action="/bang">',
                               '<input type="submit" ',
                               'id="banggo" name="banggo" ',
                               'value="', Views._TXTS["compute"], '">',
                               '</form>'])
        sector = [prvstep, curstep, forminp, "", "", "", ""]
        return sector

    @classmethod
    def show_bang_canvas(cls, unvo):
        """
        Provide canvas and javascript content for Display the Big Bang

        Args:
            unvo is a universe object

        Returns:
            (canvas1, jscript1)
        """
        canvas1 = ""
        jscript1 = ""
        cdat = unvo.rulo.get_cur_step()
        # Javascript to load and run if status of bang scripts is "done"
        if cdat["stat"] == "done":
            # Define the canvas object
            canvas1 = "".join(['<canvas id="pde1" name="pde1" ',
                             'class="w035 h030">',
                             'Browser does not support HTML5 Canvas. ',
                             'Get a newer one.</canvas>'])
            # Create and run javascript. In this example, using Processing.js.
            # There are many options for drawing, including canvas vs. SVG
            # and lots and lots of libraries to choose from.  Since I am
            # relatively familiar with Processing, am going to try sticking
            # to it and d3, as needed. See excellent on-line tutorial for
            # using Processing and Javascript together.  Doing this kind of
            # inline Processing coding is the least efficient, but it shows
            # that it does work and I can manage thru the python program if
            # and when I need to.  The "right way" (more or less) is to set
            # up the Processing program to accept certain inputs, then pass
            # those to it via Javascript.  This is a sample of embedding 
            # Processing code into a Javascript script...
            # Basically, we embed Processing commands inside of Javascript 
            # in this approach. Note how all the PDE code is preceded with
            # a reference to the pjs object in Javascript...
            start_script = '<script type="text/javascript" charset="utf-8">' \
                         + '\n(function() {'
            end_script =  '}());\n</script>'
            pjs_hook = '   var canvas = document.getElementById("pde1");' \
                     + '\n   var pjs = new Processing(canvas);'
            jscript1 = '\n'.join([
                start_script,
                pjs_hook,
                '   var value = 0;',
                '   pjs.setup = function() {',
                '      pjs.size(200,200);',
                '      pjs.noLoop();',
                '   }',
                '   pjs.draw = function() {',
                '      pjs.noStroke();',
                '      pjs.fill(255,75);',
                '      pjs.rect(0,0,200,200);',
                '      pjs.stroke(100,100,200);',
                '      pjs.noFill();',
                '      pjs.bezier(0,100, 33,100+value, 66,100+value, 100,100);',
                '      pjs.bezier(100,100, 133,100+-value, 166,100+-value, 200,100);',
                '   }',
                '   pjs.mouseMoved = function() {',
                '      value = ( pjs.mouseY-100);',
                '      pjs.redraw();',
                '   }',
                '   pjs.setup();',
                end_script])
            # Now let's play around with the Universe...                
            pp(unvo.univ)
            pp(unvo.supergx)
            pp(unvo.reggx)
            # Set number of sectors in Universe:
            # Define the universe as a 3D grid of sectors:
            assign_reg_cnt = 0
            assign_sup_cnt = 0
            while assign_reg_cnt < unvo.reggx["actual_count"] \
              and assign_sup_cnt < unvo.supergx["actual_count"]:
                # Assign characteristics to galactic sectors.
                # Built-in assumption here of a 10x10x10 "Universe" grid
                for sx in range(1, 11):
                    for sy in range(1,11):
                        for sz in range(1, 11):
                            sect_type = "Empty Sector"
                            if assign_reg_cnt < unvo.reggx["actual_count"]:
                                if random.randint(1,100) < 5:
                                    sect_type = "Regular Galactic Clusters"
                                    assign_reg_cnt += 1
                            if assign_sup_cnt < unvo.supergx["actual_count"]:
                                if random.randint(1,100) < 5:
                                    sect_type = "Super Galactic Clusters"
                                    assign_sup_cnt += 1
                            s_idx = "".join(["S_", str(sx).rjust(2, '0'),
                                             str(sy).rjust(2, '0'),
                                             str(sz).rjust(2, '0')])
                            unvo.sectors[s_idx] = sect_type
                            if sect_type != "Empty Sector":       
                                pp((s_idx, sect_type))
            
        return (canvas1, jscript1)

    @classmethod
    def process_bang(cls, cfgo, unvo):
        """
        Provide canvas and javascript content for Display the Big Bang.
        Second sample of embedded Processing code. This one does everything
        inside the Processing script. Here I have tried to translate an 
        entire complex Processing script (actually, collection of scripts)
        into JavaScript.  Kind of interesting, but problematic when I run
        into data types supported in Processing/Java but not in JavaScript,
        and especially methods on those types (for example, vector math).
        
        2) try just pointing the Canvas directly to the PDE sketch:
        <canvas id="pde1" data-processing-sources="..univ01.pde"></canvas>

        3) embed the PDE code within a script of type
        "application/processing": 
        
        <script type="application/processing" target="pde1">
        ... Processing code...
        </script>
        <canvas id="pde1"></canvas>

        4) We an also embed the pde-enabled canvas as a parameter passed to
        a JavaScript function.  This is kind of the "best of all worlds" 
        because now we can mix/match JS and Processing.  Would do like 2) above,
        but then pass the id to a JS function similar to...
        function doSomething(id) {
            var pjs Processing.getInstanceById(id);
            // do some JS stuff. e.g gather input from viewportal
            pjs.draw(myJsInputshere);
        };
    
        Args:
            cfgo is a configuration object
            unvo is a universe object

        Returns:
            (canvas1, jscript1)
        """
        pp(cfgo)        
        
        canvas1 = ""
        jscript1 = ""
            
        # Define the canvas object
        canvas1 = "".join(['<canvas id="pde1" name="pde1" ',
                         'class="w035 h030">',
                         'Browser does not support HTML5 Canvas. ',
                         'Get a newer one.</canvas>'])
        # Define the javascript object
        jscript1 = '\n'.join([
            '<script charset="utf-8" src="static/script/bow/pde/bang.js"></script>',
            '<script charset="utf-8">pjs.setup();</script>'
            '<script charset="utf-8">pjs.draw();</script>'])
        return (canvas1, jscript1)


    @classmethod
    def kill_page(cls):
        """
        Provide sector content for Kill the app page

        Returns:
            [sector0, sector1, sector2, sector3, sector4, sector5]
        """
        sector = ["", "Shutting down the Whole Ball of Wax...", "", "", "", ""]
        return sector
