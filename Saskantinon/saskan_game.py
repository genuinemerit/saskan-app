"""

:module:    saskan_game.py
:author:    GM (genuinemerit @ pm.me)

Saskan App GUI.  pygame version.

:classes:
    - PG: Frozen constants and static game values
    - GameData: Dynamic game values and data structures
    - GameMenu: Manage menu bars, menu items, draw and click events
    - HtmlDisplay: Manage display of HTML pages in a browser
    - TextInput: Handle text input events in a single input box
    - TextInputGroup: Handle groups of text input boxes, like a form
    - InfoBar: Manage display of info bar/dock at bottom of main frame
    - GameConsole: Manage display of widgets (text, for now) in CDI.CONSOLE
    - GameMap: Manage display of map & related widgets in GAMEMAP
    - SaskanGame: Main class, event loop, state mgmt, event handlers
    - __main__: Entry point for this module, instantitates all classes

    Note:
    For scaling images, see: https://www.pygame.org/docs/ref/transform.html
    Example: scaled_image =\
        pygame.transform.scale(original_image, (new_width, new_height))

@DEV:
- Prototype basic game activities like:
    - map generation
    - avatar placement/movement
    - physics
    - sound and music
- Use pygame for graphics, sound, everything else.
- Go for more features, better performance than earler prototypes,
    but don't worry about interactiviity or complete game yet.
    Focus most on prototyping the windows and widgets.
---> Convert from JSON to DB for most values.
---> Only use JSON for install-level customizations, overrides.
- Use io_time, io_graph, io_music modules for dynamic things.
- Reimplement wiretap and logger modules later on.
    - Print statements and debugger are OK for now.
- Sketch out what I want to do before stating to do much code.
    - Start simple. Experiment, be agile. Use CoPilot and ChatGPT.
    - See pygame_lab/app4 ("turtles") for some ideas.
- Work on loading, displaying more complex maps/settings data.
    - Show key/legend for political boundaries.
    ---> Work on some geographical data.
    - Work on some temporal data.
    - Work on some weather data.
    - Work on some demographic (population, language, religion) data.
    - Show region names, using different fonts for stuff.
    - Show degrees and km data.
    - Add arrows, some measures (text, degrees N, S, E, W) to the map.
    - Elaborate borders, textures at more detail.
    - Zoomi in/out to different levels of detail.
    - Show terrain and other factors into account for movement.
    - Track time, season, date, etc.
- Work on skeletal game events and interactions.
    - Identify a single AI player.
        - See code in ontology lab.
            - Pick a few things to start with.
            - Parameterize the data.
            - Set or get a name.
            - Roll basic attributes, age, home region, DNA, guild affiliation.
            - Pick starting location.
        - Sketch of player actions and events, starting w/movement.
            - Highlight what grid player is in.
            - Display data for grid that player is in.
            - Accept input for what grid to travel to.
            - Compute time to walk, to ride to target grid.
            - Animate movement, show time passing, highlight grids passed thru.
        - Start to develop inventory of image widgets, textures, sounds, etc.
            - Start simple and stupid, then improve.
            - Sound effects for movement.
            - Theme music for different regions.
            - Play a new theme when entering a different region, town, etc.
        - Add simple sets, scenes.
        - Work on player functions like:
            - Energy, market, inventory, food/eating, etc.
    - Add more AI players.
        - Start to design some typical encounters.
        - Start to design some typical scenarios, following the script / beat sheet.

    The security concern with pickling is the possiblity of executing code
    from a remote source which is malicious. The use of it internally is unlikely
    to cause problems. The use of pickle to store data is not a security risk.
    To be safer, create a hash or a signature of the data and store that with the
    pickled data. When you unpickle the data, you can check the hash/signature to
    make sure the data has not been tampered with. This is not a guarantee, but
    it is better than nothing. In my use cases, it may not serve much purpose to
    be pickling data; it can just as easily be stored in a database as JSON.

    Now I'm using JSON data structures on the DB only in a few instances. And
    storing as JSON, not as BLOB/pickled bytes.
"""

# trunk-ignore(bandit/B403)
import pickle           # remove this eventually
# from numpy import append
import pygame as pg
import sys
import webbrowser

from copy import copy
# from dataclasses import dataclass
from pprint import pprint as pp     # noqa: F401, format like pp for files
from pprint import pformat as pf    # noqa: F401, format like pp for files
from pygame.locals import *         # noqa: F401, F403
# from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from io_data import SaskanConstants     # type: ignore
from io_data import DataRec             # type: ignore
from io_data import Display             # type: ignore
from io_data import GameCell            # type: ignore
from io_data import GameCoord           # type: ignore
from io_data import GameImage           # type: ignore
from io_data import GameGrid            # type: ignore
from io_data import GameRect            # type: ignore
from io_data import SaskanRect          # type: ignore

from io_db import DataBase          # type: ignore
from io_file import FileIO          # type: ignore
from io_shell import ShellIO        # type: ignore

# Constants
# ================================================
CON = SaskanConstants()
CAS = CON.Astro()
CCL = CON.Colors()
CDI = Display()
CGM = CON.Geom()
CGO = CON.Geog()

# Data Records
# ================================================
DR = DataRec()

# In-Game Data Structures
# ================================================
GCL = GameCell()
GCO = GameCoord()
GGR = GameGrid()
GIM = GameImage()
GRC = GameRect()
GSR = SaskanRect()

# External Methods
# ================================================
DB = DataBase()
FI = FileIO()
SI = ShellIO()
# WT = WireTap()
# LG = Logger()

pg.init()


class SetGameData(object):
    """Methods for inserting and updating values on SASKAN.db.
    Initially, just use these from the command line. Eventually,
    intergrate them into the GUI when it is useful.  Try to avoid
    going down a rat-hole of GUI features and functionality, like
    a "magical" editor that generates forms based on DB table
    definitions.  Keep it simple, stupid.  If the command line is
    too tiresome, then use a CSV file or JSON file to load data.

    Simple version:
    Basically just a wrapper for calls to the DataBase() class.
    - pull in a list of values, assume they are in correct order.
    - pull in a dict object, pickle it, and store it in a blob.

    Hmmm...
    Problem here is that this is a PyGame module. There is no CLI
    access as long as the game loop is running. So, I need to
    either define a separate module for data management (yes), or
    create a CLI-like interface in the GUI. The former is easier.
    I have done the latter previously and should be able to find
    some code to support that. But it makes for a more complex
    GUI and not one that most users would be familiar with.
    """
    def __init__(self):
        """Initialize the SetGameData object.
        It will be instantiated as SGDT, a global object.
        """
        pass

    @classmethod
    def insert_record(cls,
                      p_sql_nm: str,
                      p_values: list,
                      p_object: dict):
        """Insert a record to SASKAN.db.
        """
        DB.execute_insert(p_sql_nm, (p_values, pickle.dumps(p_object)))

class GameDataNew(object):
    """Get resources for display in GAMEMAP and CDI.CONSOLE.
    Read mainly from the DB. May be a few config files too.
    Notes:
    - "txt" refers to a string of text.
    - "img" refers to a PyGame image object rendered from the txt.
    - "box" refers to a PyGame rectangle object around the img.
    """
    pass


class GameData(object):
    """Get and set resources displayed in GAMEMAP and CDI.CONSOLE.
    This class is instantiated as GDAT, a global object.
    Notes:
    - "txt" refers to a string of text.
    - "img" refers to aCDI.TIMER PyGame image object rendered from the txt.
    - "box" refers to a PyGame rectangle object around the img.
    @DEV:
    - Layers of data, zoom-in, zoom-out, other views
    - Ee.g.: a region, a town and environs, a village, a scene, star map
    - GUI controls for scroll, zoom, pan, select-move, etc
    - Event trigger conditions / business rules

    - This class is quite large. Let's think about 3 classes:
        - GameData: load data for use in GAMEMAP and CDI.CONSOLE
        - SetConsole: prep data, incl. widget definitions, for CDI.CONSOLE
        - SetGameMap: align data to grid for scaling, zooming
    - And refactor as needed to use io_data and DB structures.
    - Definitely break out into multiple classes.
    """
    def __init__(self):
        """Dynamically loaded data for GAMEMAP and CDI.CONSOLE.
        Values are displayed in CDI.CONSOLE but refer to GAMEMAP.
        For CDI.GRID, static values are read in from PG, then
           data is extended here.
        """
        self.DATASRC = {"actv": False,
                        "catg": None,
                        "item": None}
        self.CONSOLE_REC = {"txt": "",
                            "img": None,
                            "box": None}
        self.CONSOLE_TEXT: list = list()
        self.MAP_BOX = None

    def make_grid_key(self,
                      p_col : int,
                      p_row: int) -> str:
        """Convert integer coordinates to string key
           for use in the .grid["G"] (grid data) matrix.
        :args:
        - p_col: int, column number
        - p_row: int, row number
        :returns:
        - str, key for specific grid-cell record, in "0n_0n" format
        """
        return f"{str(p_col).zfill(2)}_{str(p_row).zfill(2)}"

    # Data load methods
    # The current version of these methods assumes a
    #   specific pattern of name:value pairs in data sources.
    # =================
    def set_datasrc(self,
                    p_datasrc: dict):
        """ Set data in .DATASRC structure from sources outside
           the app, like files or services or database.
           Example: geographical data
        :args:
        - p_datasrc (dict): name-value pairs for .DATASRC structure.
        :sets:
        - self.DATASRC (dict): name-value pairs
        """
        for k, v in p_datasrc.items():
            self.DATASRC[k] = v

    def set_label_name(self,
                       p_attr: dict):
        """Set text for a label (l) and name (n), but no type (t) value.
           Example: "type" attribute
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CDI.CONSOLE[n]["txt"] (list): strings to render as text
        """
        for t in [CDI.DASH16,
                  f"{p_attr['label']}:",
                  f"  {p_attr['name']}"]:
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = t
            self.CONSOLE_TEXT.append(rec)

    def set_label_name_type(self,
                            p_attr: dict):
        """Set text for a label (l), a name (n), and a type (t).
           Example: "contained_by" attribute
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CDI.CONSOLE[n]["txt"] (list): strings to render as text
        """
        for t in [CDI.DASH16,
                  f"{p_attr['label']}:",
                  f"  {p_attr['name']}",
                  f"  {p_attr['type']}"]:
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = t
            self.CONSOLE_TEXT.append(rec)

    def set_proper_names(self,
                         p_attr: dict):
        """Set text for a "name" attribute, which refers to proper
            names. Required value is indexed by "common". Optional
            set of names in various game languages or dialects have
            "other" in key.
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CDI.CONSOLE[n]["txt"] (list): strings to render as text
        """
        for t in [CDI.DASH16,
                  f"{p_attr['label']}:",
                  f"  {p_attr['common']}"]:
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = t
            self.CONSOLE_TEXT.append(rec)
        if "other" in p_attr.keys():
            for k, v in p_attr["other"].items():
                rec = copy(self.CONSOLE_REC)
                rec['txt'] = f"    {k}: {v}"
                self.CONSOLE_TEXT.append(rec)

    def set_map_attr(self,
                     p_attr: dict):
        """Set text for a "map" attribute, referring to game-map data.
           Examples: "distance" or "location" expressed in
              kilometers, degrees, or other in-game measures
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CDI.CONSOLE[n]["txt"] (list): strings to render as text
        """
        ky = "distance" if "distance" in p_attr.keys() else\
            "location" if "location" in p_attr.keys() else None
        if ky is not None:
            sub_k = ["height", "width"] if ky == "distance" else\
                ["top", "bottom", "left", "right"]
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = CDI.DASH16
            self.CONSOLE_TEXT.append(rec)
            rec = copy(self.CONSOLE_REC)
            rec["txt"] =\
                f"{p_attr[ky]['label']}:"
            self.CONSOLE_TEXT.append(rec)
            for s in sub_k:
                rec = copy(self.CONSOLE_REC)
                rec["txt"] =\
                    f"  {p_attr[ky][s]['label']}:  " +\
                    f"{p_attr[ky][s]['amt']} " +\
                    f"{p_attr[ky]['unit']}"
                self.CONSOLE_TEXT.append(rec)

    def set_contains_attr(self,
                          p_attr: dict):
        """Set text for a "contains" attribute, referring to things
            contained by another object.
            Examples: "sub-region", "movement" (i.e, movement paths)
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CDI.CONSOLE[n]["txt"] (list): strings to render as text
        """
        rec = copy(self.CONSOLE_REC)
        rec["txt"] = CDI.DASH16
        self.CONSOLE_TEXT.append(rec)
        rec = copy(self.CONSOLE_REC)
        rec["txt"] = f"{p_attr['label']}:"
        self.CONSOLE_TEXT.append(rec)

        if "sub-region" in p_attr.keys():
            rec = copy(self.CONSOLE_REC)
            rec["txt"] =\
                f"  {p_attr['sub-region']['label']}:"
            self.CONSOLE_TEXT.append(rec)
            for n in p_attr["sub-region"]["names"]:
                rec = copy(self.CONSOLE_REC)
                rec["txt"] = f"    {n}"
                self.CONSOLE_TEXT.append(rec)

        if "movement" in p_attr.keys():
            # roads, waterways, rivers and lakes
            rec = copy(self.CONSOLE_REC)
            rec["txt"] = f"  {p_attr['movement']['label']}:"
            self.CONSOLE_TEXT.append(rec)
            attr = {k:v for k, v in p_attr["movement"].items()
                    if k != "label"}
            for _, v in attr.items():
                rec = copy(self.CONSOLE_REC)
                rec["txt"] = f"    {v['label']}:"
                self.CONSOLE_TEXT.append(rec)
                for n in v["names"]:
                    rec = copy(self.CONSOLE_REC)
                    rec["txt"] = f"      {n}"
                    self.CONSOLE_TEXT.append(rec)

    # Data rendering methods for CDI.CONSOLE
    # ==================================
    def render_text_lines(self):
        """
        Store rendering objects for lines of CDI.CONSOLE text.
        After rendering the img from txt, set the box for the img.
        Then adjust topleft of the box according to line number.
        """
        print('render_text_lines()...')

        x = CDI.CONSOLE_TTL_BOX.x
        y = CDI.CONSOLE_TTL_BOX.y + CDI.FONT_MED_SZ

        pp(("self.CONSOLE_TEXT: ", self.CONSOLE_TEXT))

        for ix, val in enumerate(self.CONSOLE_TEXT):
            txt = val["txt"]
            self.CONSOLE_TEXT[ix]["img"] =\
                CDI.F_SANS_TINY.render(txt, True,
                                       CCL.CP_BLUEPOWDER,
                                       CCL.CP_BLACK)
            self.CONSOLE_TEXT[ix]["box"] =\
                self.CONSOLE_TEXT[ix]["img"].get_rect()
            self.CONSOLE_TEXT[ix]["box"].topleft =\
                (x, y + ((CDI.FONT_TINY_SZ + 2) * (ix + 1)))

            pp(("ix: ", ix, "self.CONSOLE_TEXT[ix]: ", self.CONSOLE_TEXT[ix]))

    def set_console_text(self):
        """Format text lines for display in CDI.CONSOLE.
        - "catg" identifies source of config data to format.
        - "item" identifies type of data to format.

        @TODO:
        - Move the geo data, etc. into a database.
        - May want to revisit, optimize the methods for formatting
          different types of data. Maybe even store img and box
          objects in the DB, rather than rendering them here?
            - Nah. This only gets called once per data source, when
              the user clicks on a menu item. No point in persisting to DB.
        - Use config files only for install-level customizations, overrides.
        """
        self.CONSOLE_TEXT.clear()
        # Contents

        pp((self.DATASRC["catg"], self.DATASRC["item"]))

        if self.DATASRC["catg"] == "geo":
            ci = FI.G[self.DATASRC["catg"]][self.DATASRC["item"]]

            pp((ci))

            if "type" in ci.keys():
                self.set_label_name(ci["type"])
            if "contained_by" in ci.keys():
                self.set_label_name_type(ci["contained_by"])
            if "name" in ci.keys():
                self.set_proper_names(ci["name"])
            if "map" in ci.keys():
                self.set_map_attr(ci["map"])
            if "contains" in ci.keys():
                self.set_contains_attr(ci["contains"])
            self.render_text_lines()

    def compute_map_scale(self,
                          p_attr: dict):
        """Compute scaling, position for the map and grid.
        :attr:
        - p_attr (dict): 'map' data for the "Saskan Lands" region from
            the saskan_geo.json file.
        :sets:
        - CDI.GRID['map']: map km dimensions and scaling factors

        - Get km dimensions for entire map rectangle
        - Reject maps that are too big
        - Divide g km by m km to get # of grid-cells for map box
            - This should be a float.
        - Multiply # of grid-cells in the map box by px per grid-cell
          to get line height and width in px for the map box.
        - Center 'map' in the 'grid'; by grid count, by px

        @DEV
        - Debug, refactor to use io_data structures and eventually
            DB structures for dynamic grid/map mapping.
        - Instead of just snapping the "map" as defined here onto
          the GameGrid structure, think about how to pull in map
          data from the database and align it to the grid.
        - Also consider that the grid settings should also be
          pulled in from a database record.
        - Take some time here to get it working, not just a kludge.
        """
        err = ""
        map = {'ln': dict(),
               'cl': dict()}
        # Evaluate map line lengths in kilometers
        map['ln']['km'] =\
            {'w': round(int(p_attr["distance"]["width"]["amt"])),
             'h': round(int(p_attr["distance"]["height"]["amt"]))}
        if map['ln']['km']['w'] > CDI.G_LNS_KM_W:
            err = f"Map km w {map['w']} > grid km w {CDI.G_LNS_KM_W}"
        if map['ln']['km']['h'] > CDI.G_LNS_KM_H:
            err = f"Map km h {map['h']} > grid km h {CDI.G_LNS_KM_H}"
        if err != "":
            raise ValueError(err)
        # Verified that the map rect is smaller than the grid rect.
        # Compute a ratio of map to grid.
        # Divide map km w, h by grid km w, h
        map['ln']['ratio'] =\
            {'w': round((map['ln']['km']['w'] / CDI.G_LNS_KM_W), 4),
             'h': round((map['ln']['km']['h'] / CDI.G_LNS_KM_H), 4)}
        # Compute map line dimensions in px
        # Multiply grid line px w, h by map ratio w, h
        map['ln']['px'] =\
            {'w': int(round(CDI.G_LNS_PX_W * map['ln']['ratio']['w'])),
            'h': int(round(CDI.G_LNS_PX_H * map['ln']['ratio']['h']))}
        # The map rect needs to be centered in the grid rect.
        #  Compute the offset of the map rect from the grid rect.
        #  Compute topleft of the map in relation to topleft of the grid.
        #  The map top is offset from grid top by half the px difference
        #  between grid height and map height.
        #  The map left is offset from grid left by half the px difference
        #  between grid width and map width.
        # And then adjusted once more for the offset of the grid from the window.
        map['ln']['px']['left'] =\
            int(round((CDI.G_LNS_PX_W - map['ln']['px']['w']) / 2) +
                      CDI.GRID_OFFSET_X)
        map['ln']['px']['top'] =\
            int(round((CDI.G_LNS_PX_H - map['ln']['px']['h']) / 2) +
                      (CDI.GRID_OFFSET_Y * 4))  #  not sure why, but I need this
        CDI.GRID["map"] = map

    def set_map_grid_collisions(self):
        """ Store collisions between CDI.GRIDS and 'map' box.
        """
        cells = {k:v for k, v in CDI.GRID.items() if k != "map"}
        for ck, crec in cells.items():
            CDI.GRID[ck]["is_inside"] = False
            CDI.GRID[ck]["overlaps"] = False
            if SR.rect_contains(
                    CDI.GRID["map"]["box"], crec["box"]):
                CDI.GRID[ck]["is_inside"] = True
            elif SR.rect_overlaps(
                    CDI.GRID["map"]["box"], crec["box"]):
                CDI.GRID[ck]["overlaps"] = True

    # Set "map" dimensions and other content in CDI.GRIDS
    # =================================================
    def set_gamemap_dims(self,
                         p_attr: dict):
        """This method handles placing/creating/drawing map displays
           over the "grid" on the GAMEMAP display.
        :attr:
        - p_attr (dict): game map name-value pairs from geo config data
            For example, 'map' data for the "Saskan Lands" region from
            the saskan_geo.json file.

        - Compute ratio, offsets of map to g_ width & height.
        - Define saskan rect and pygame box for the map
        - Do collision checks between the map box and grid cells
        """
        self.compute_map_scale(p_attr)
        map_px = CDI.GRID["map"]["ln"]["px"]
        CDI.GRID["map"]["s_rect"] =  SR.make_rect(map_px["top"],
                                                      map_px["left"],
                                                      map_px["w"],
                                                      map_px["h"])
        CDI.GRID["map"]["box"] =\
            CDI.GRID["map"]["s_rect"]["pg_rect"]
        self.set_map_grid_collisions()

    def set_map_grid(self):
        """
        Based on currently selected .DATASRC["catg"] and .DATASRC["item"]:
        - assign values to CDI.GRIDS for "map".
        Note:
        - For now, only "geo" data (saskan_geo.json) is handled
        """
        if self.DATASRC["catg"] == "geo":
            data = FI.G[self.DATASRC["catg"]][self.DATASRC["item"]]
            if "map" in data.keys():
                self.set_gamemap_dims(data["map"])


class GameMenu(object):
    """Manage Menu Bar, Menus and Menu Items for Saskan Game app.
    Define a surface for clickable top-level menu bar members,
    drop-down menus associated with them, and items on each menu.
    Clicking on a menu bar member opens or closes a Menu.
    Clicking on Menu Item triggers an event and may also close Menu.

    Define in-memory objects for both Menu bar members, Menus and
    Menu Items with both static and dynamic value attributes.
    A menu bar is a conceptual horizontal row of menu bar members.
       There is no actual menu bar object.
    A menu bar member is a clickable item in the menu bar.
    A menu is a vertical list of menu items.
    A menu item is a clickable item in a menu.
    """
    def __init__(self):
        """Initialize the GameMenu object.
        It will be instantiated as GMNU, a global object.

        Menu members and and menu items are stored in memory
        in class-level attributes (dicts).
        """
        self.mbars: dict = dict()
        self.mitems: dict = dict()
        self.set_menu_bars()
        self.set_menus()
        self.draw_menu_bars()
        for mb_k in self.mitems.keys():
            self.draw_menu_items(mb_k)

    def set_menu_bars(self):
        """Set up the menu bar and the menu bar members,
           storing them in GMNU.
        A menu bar is a conceptual horizontal row of menu bar members.
            There is no actual menu bar object.
        Center text in each menu bar member and kludge the spacing
            based on the text width.
        Load all menu bar members and items info from config into mbars
        Extend the configuration data with text, bounding box and
            selected-status flag for each menu bar member.
        """
        self.mbars =\
            {ky: {"name": val["name"]}
             for ky, val in FI.M[CDI.MENUS]["menu"].items()}
        # x --> left edge of first, leftmost menu bar member
        x = CDI.MBAR_X
        for mb_k, v in self.mbars.items():
            self.mbars[mb_k] =\
                {"name": v["name"],
                 "txt": CDI.F_SANS_SM.render(
                     v["name"], True, CCL.CP_BLUEPOWDER, CP_GRAY_DARK),
                 "selected": False,
                 "tbox": None,
                 "mbox": None}
            # Rect based on text size and location
            self.mbars[mb_k]["tbox"] =\
                self.mbars[mb_k]["txt"].get_rect()
            # Default rect for menu bar member container
            self.mbars[mb_k]["mbox"] =\
                pg.Rect((x, CDI.MBAR_Y), (CDI.MBAR_W,
                                         CDI.MBAR_H +
                                         (CDI.MBAR_MARGIN * 2)))
            x = self.mbars[mb_k]["mbox"].right # shift x for next bar
            # Center text rect in menu bar member rect
            # Kludge to account for visual niceness of text
            self.mbars[mb_k]["tbox"].left =\
                self.mbars[mb_k]["mbox"].left +\
                    (self.mbars[mb_k]["mbox"].width / 2) - 12
            self.mbars[mb_k]["tbox"].top =\
                self.mbars[mb_k]["mbox"].top + CDI.MBAR_MARGIN + 5

    def set_menu_list_box(self,
                          p_mb_k: str):
        """
        Updates mbars with mlist_box, a Rect() object for the menu items
           associated with each menu. That is the bounding box for the
           entire list of menu items under a specific menu bar member.
        Store it in mbars.
        :args:
        - p_mb_k: key to the menu bar member data
        :sets:
        - mbars[mb_k]["mlist_box"]: Rect() object for the menu items
        """
        if "mlist_box" not in list(self.mbars[p_mb_k].keys()):
            left = self.mbars[p_mb_k]["mbox"].left
            top = self.mbars[p_mb_k]["mbox"].bottom
            self.mbars[p_mb_k]["mlist_box"] =\
                pg.Rect((left, top), (CDI.MBAR_W, 0))

    def set_menu_item_box(self,
                          p_mb_k: str,
                          p_mi_k: str,
                          p_mi_x: int):
        """
        Define bounding box for text in menu item.
        - width is text width plus margin on each side
        - height is fixed amount (CDI.MBAR_H)
        - top is bottom of menu bar member box
            plus fixed height X menu item index (order in list)
            plus margin
        - left is left of menu bar member box plus margin
        Adjust container (full list) box height for each item added.
            = fixed height
        :args:
        - p_mb_k: key to the menu bar member data
        - p_mi_k: key of the menu item data
        - p_mi_x: order (index) of the menu item in the list
        """
        text_w = self.mitems[p_mb_k][p_mi_k]["mi_text_enabled"].get_width()
        width = text_w + (CDI.MBAR_MARGIN * 2)
        top = self.mbars[p_mb_k]["mbox"].bottom +\
            (CDI.MBAR_H * p_mi_x) + CDI.MBAR_MARGIN
        left = self.mbars[p_mb_k]["mbox"].left +\
            (CDI.MBAR_MARGIN * 4)
        self.mitems[p_mb_k][p_mi_k]["mitm_box"] =\
            pg.Rect((left, top), (width, CDI.MBAR_H))

        self.mbars[p_mb_k]["mlist_box"].height += CDI.MBAR_H

    def set_menu_item(self,
                      p_mb_k: str,
                      p_mi_k: str,
                      p_mi_x: int,
                      p_mi_v: dict):
        """
        Updates mitems with drawing objects for each item under a menu.
        Not yet managing dependencies between menu items, but keep
            that in mind and use configuration data (eventually) to
            manage them.
        For menu items that set state of in-app options or status rather
            than trigger an event, track them in the ADAT object's "app"
            attribute.  For example, the ibar status_option.
        :args:
        - p_mb_k: key to the menu bar member data
        - p_mi_k: key of the menu item data
        - p_mi_x: order (index) of the menu item in the list
        - p_mi_v: dict of menu item data
        """
        self.mitems[p_mb_k][p_mi_k] = {
            "name": p_mi_v["name"],
            "enabled": True,
            "selected": False,
            "on": False}
        self.mitems[p_mb_k][p_mi_k]['enabled'] =\
            p_mi_v['enabled'] if 'enabled' in p_mi_v.keys() else True
        self.mitems[p_mb_k][p_mi_k]["mi_text_enabled"] =\
            CDI.F_SANS_SM.render(p_mi_v["name"], True,
                                CCL.CP_BLUEPOWDER, CP_GRAY_DARK)
        self.mitems[p_mb_k][p_mi_k]["mi_text_disabled"] =\
            CDI.F_SANS_SM.render(p_mi_v["name"], True,
                                CP_GRAY, CP_GRAY_DARK)
        self.set_menu_item_box(p_mb_k, p_mi_k, p_mi_x)

    def set_menus(self):
        """
        Initialize menu items data from config data.
        Define menu list box and items for each
            vertical menu bar / list of menu items.
        """
        # Init menu items from config
        self.mitems = {ky: val["items"]
                       for ky, val in FI.M[CDI.MENUS]["menu"].items()}
        for mb_k, mlist in self.mitems.items():
            self.set_menu_list_box(mb_k)
            mi_x = 0
            for mi_k, mi_v in mlist.items():
                self.set_menu_item(mb_k, mi_k, mi_x, mi_v)
                mi_x += 1

    def draw_menu_bars(self):
        """ Draw each Menu Bar member.
        Redraw the same thing on every refresh: bounding box for
        the menu bar member (draw) and its text surface (blit).
        First draw everything in unselected mode.
        Then if one is selected, draw in selected mode (green box).
        :renders:
        - menu bar members, the "menu bar"
        """
        for _, mb_vals in self.mbars.items():
            pg.draw.rect(CDI.WIN, CCL.CP_BLUEPOWDER, mb_vals["mbox"], 2)
            CDI.WIN.blit(mb_vals["txt"], mb_vals["tbox"])
        mbox = [mb_vals["mbox"] for _, mb_vals in self.mbars.items()
                if mb_vals["selected"] is True]
        if len(mbox) > 0:
            pg.draw.rect(CDI.WIN, CP_GREEN, mbox[0], 2)

    def draw_menu_items(self,
                        mb_k: str = ''):
        """ Draw the list of Menu Items for the selected menu bar.
        Draw the list bounding box, then blit each menu item using
          the text surface that matches its current status.
        :attr:
        - mb_k: key to the menu bar member data
        :renders:
        - menu items, a "menu"
        """
        if mb_k not in ('', None) and\
                self.mbars[mb_k]["selected"] is True:
            pg.draw.rect(CDI.WIN, CP_GRAY_DARK,
                         self.mbars[mb_k]["mlist_box"], 0)
            for _, mi_v in self.mitems[mb_k].items():
                if mi_v["enabled"]:
                    CDI.WIN.blit(mi_v["mi_text_enabled"], mi_v["mitm_box"])
                else:
                    CDI.WIN.blit(mi_v["mi_text_disabled"], mi_v["mitm_box"])

    def click_mbar(self,
                   p_mouse_loc: tuple) -> str:
        """
        If clicked on a menu bar, toggle its 'selected' attribute.
        Set all others to not selected and return key of clicked bar.
        If no click, return key of previously-selected bar, if any.

        Regardless of whether a menu bar was clicked, search all items
            to determine which is selected, if any.
        Using a list comprehension, so result is a one item
            list if valid menu bar was clicked, else an empty list.
        :attr:
        - p_mouse_loc: tuple (number: x, number: y)
        :return: id of currently selected menu bar, else ''
        """
        mbar_key = ''
        for mb_k, v in self.mbars.items():
            if v["mbox"].collidepoint(p_mouse_loc):
                self.mbars[mb_k]["selected"] = True\
                    if self.mbars[mb_k]["selected"] is False else False
                for ky in [ky for ky in self.mbars.keys() if ky != mb_k]:
                    self.mbars[ky]["selected"] = False
                break
        mb_k = [k for k, v in self.mbars.items() if v["selected"] is True]
        mbar_key = mb_k[0] if len(mb_k) > 0 else ''
        return mbar_key

    def click_mitem(self,
                    p_mouse_loc: tuple,
                    mb_k: str = '') -> tuple:
        """ Return id if clicked on a menu item.
        - Only look at items in specified menu bar member list
        - Set all menu items in the list to unselected.
        - See which, if any, menu item was clicked.
        - If an item is now selected, set other items on the list to not
          selected and also set the bar member to not selected.
          This will have the effect of closing the menu, but still
          passing on info on which item was clicked.
        If a disabled item is clicked, we still close the menu
          but no item is marked as selected.

        :attr:
        - p_mouse_loc: tuple of mouse location
        - mb_k: id of currently selected menu bar, abort if ''
        :return:
        - (str, int) id of bar and ix of selected menu item,
                     else ('', '')
        """
        selected_itm = ('', '')
        if mb_k not in (None, ''):  # if a menu bar was provided
            for mi_k, m_itms in self.mitems[mb_k].items():
                self.mitems[mb_k][mi_k]["selected"] = False
                if m_itms['mitm_box'].collidepoint(p_mouse_loc):
                    if self.mitems[mb_k][mi_k]["enabled"]:
                        selected_itm = (mb_k, mi_k)
                        self.mitems[mb_k][mi_k]["selected"] = True
                    self.mbars[mb_k]["selected"] = False
        return selected_itm

    def set_menus_state(self,
                             mb_k: str,
                             mi_ky: str,
                             p_use_default: bool = False):
        """Set the enabled state of identified menu item and/or
           set the enabled status of dependent menu items.
        Dependent menu items are always in the same menu list as the
           selected menu item.
        :attr:
        - mb_k: str - menu bar key
        - mi_ky: str - menu item key
        - p_use_default: bool - use default enabled value if True
        
        @TODO:
        - Simplify this. May be able to get rid of it.
        """
        self.mitems[mb_k][mi_ky]["enabled"] = False
        txt_color = CP_GRAY
        # Set enabled status of identified item
        if p_use_default:
            if ("default" in list(self.mitems[mb_k][mi_ky].keys()) and\
                self.mitems[mb_k][mi_ky]["default"] == "enabled") or\
               "default" not in list(self.mitems[mb_k][mi_ky].keys()):
                    self.mitems[mb_k][mi_ky]["enabled"] = True
                    txt_color = CCL.CP_BLUEPOWDER
            # Set text color and content of identified item
            self.mitems[mb_k][mi_ky]["mi_text"] =\
                CDI.F_SANS_SM.render(self.mitems[mb_k][mi_ky]["name"],
                                    True, txt_color, CP_GRAY_DARK)
        else:
            # Default selected item to enabled status
            self.mitems[mb_k][mi_ky]["enabled"] = True
            self.mitems[mb_k][mi_ky]["mi_text"] =\
                CDI.F_SANS_SM.render(self.mitems[mb_k][mi_ky]["name"],
                                    True, CCL.CP_BLUEPOWDER, CP_GRAY_DARK)
            # Identify dependent menu items and modify their enabled status
            if "disable" in list(self.mitems[mb_k][mi_ky].keys()):
                for dep_ky in self.mitems[mb_k][mi_ky]["disable"]:
                    self.mitems[mb_k][dep_ky]["enabled"] = False
                    self.mitems[mb_k][dep_ky]["mi_text"] =\
                        CDI.F_SANS_SM.render(self.mitems[mb_k][dep_ky]["name"],
                                            True, CP_GRAY, CP_GRAY_DARK)
            if "enable" in list(self.mitems[mb_k][mi_ky].keys()):
                for dep_ky in self.mitems[mb_k][mi_ky]["enable"]:
                    self.mitems[mb_k][dep_ky]["enabled"] = True
                    self.mitems[mb_k][dep_ky]["mi_text"] =\
                        CDI.F_SANS_SM.render(self.mitems[mb_k][dep_ky]["name"],
                                            True, CCL.CP_BLUEPOWDER,
                                            CP_GRAY_DARK)


class InfoBar(object):
    """Info Bar object.
    Deafault text is system info.
    Show status text if it is turned on.
    """
    def __init__(self):
        """ Initialize Info Bar. """
        self.info_status = {
            "frozen": True,
            "frame_cnt": 0,
            "mouse_loc": (0, 0),
            "grid_loc": ""}

    def set_ibar_status_text(self):
        """ Set Info Bar status text. """
        self.status_text = (
            "Frame: " + str(self.info_status["frame_cnt"]) +
            "    | Mouse: " + str(self.info_status["mouse_loc"]) +
            "    | Grid: " + str(self.info_status["grid_loc"]))

    def draw(self):
        """ Draw Info Bar.
        Set and draw the Info Bar text.
        Draw the info bar text, optionally including status info.
        """
        text = CDI.PLATFORM + "   | " + self.status_text
        self.itxt = CDI.F_SANS_SM.render(text, True, CCL.CP_BLUEPOWDER,
                                        CCL.CP_BLACK)
        self.ibox = self.itxt.get_rect()
        self.ibox.topleft = CDI.IBAR_LOC
        CDI.WIN.blit(self.itxt, self.ibox)


class HtmlDisplay(object):
    """Set content for display in external web browser.
    This class is instantiated as a global object named CDI.WHTM.
    Pass in a URI to display in the browser.
    """

    def __init__(self):
        """ Initialize Html Display.
        """
        pass

    def draw(self,
             p_help_uri: str):
        """ Open web browser to display HTML resource.
        It opens subsequent items in the same browser window,
        in new tabs on my setup (Linux Ubuntu, Firefox browser)
        May behave differently on other systems.

        Args: (str) UTI to HTML file to display in browser.
        """
        webbrowser.open(p_help_uri)


class GameConsole(object):
    """Draw the Game Console window.
    Display game data like score, map descriptions, etc.
    Instantiated as global object CDI.CONSOLE.

    Note:
    - Objects were rendered, boxed in GDAT and PG classes.
    @DEV:
    - Eventually extend to handle text input fields and/or GUI controls.
    - Keep this distinct from GameData() class, which handles data and
      rendering. Methods will grow more complex to handle game play.
    """

    def __init__(self):
        """ Initialize GameConsole.
        """
        pass

    def draw(self):
        """ Draw CDI.CONSOLE rectange and blit its title text img.
        - Blit txt imgs for current data in CONSOLE_TEXT.
        """
        # Draw container rect and header.
        pg.draw.rect(CDI.WIN, CCL.CP_BLACK, CDI.CONSOLE_BOX, 0)
        CDI.WIN.blit(CDI.CONSOLE_TTL_IMG, CDI.CONSOLE_TTL_BOX)
        # Draw lines of text
        for txt in GDAT.CONSOLE_TEXT:
           CDI.WIN.blit(txt["img"], txt["box"])


class GameMap(object):
    """Define and handle the Game GUI "map" window.
    Draw the grid, the map, and (eventually) scenes, game widgets,
    GUI controls and so on mapped to the grid.

    Instantiated as global object GAMEMAP.

    Note:
    - Objects were rendered, boxed in GDAT and PG classes.
    - Collisions between map and grid cells are id'd in GDAT.
    """

    def __init__(self):
        """Initialize GameMap"""
        pass

    def draw_map(self):
        """Draw "grid" and "map" in GAMEMAP using PG, GDAT objects.
        """
        # Draw grid box with thick border
        pg.draw.rect(CDI.WIN, CP_SILVER, CDI.GRID_BOX, 5)
        # Draw grid lines      # vt and hz are: ((x1, y1), (x2, y2))
        for vt in CDI.G_LNS_VT:
            pg.draw.aalines(CDI.WIN, CP_WHITE, False, vt)
        for hz in CDI.G_LNS_HZ:
            pg.draw.aalines(CDI.WIN, CP_WHITE, False, hz)
        # Highlight grid squares inside or overlapping the map box
        for _, grec in GDAT.CDI.GRIDS.items():
            if "is_inside" in grec.keys() and grec["is_inside"]:
                pg.draw.rect(CDI.WIN, CP_WHITE, grec["box"], 0)
            elif "overlaps" in grec.keys() and grec["overlaps"]:
                pg.draw.rect(CDI.WIN, CP_SILVER, grec["box"], 0)
        # Draw map box with thick border
        if GDAT.MAP_BOX is not None:
            pg.draw.rect(CDI.WIN, CP_PALEPINK, GDAT.MAP_BOX, 5) # type: ignore

    def draw_hover_cell(self,
                        p_grid_loc: str):
        """
        Highlight/colorize grid-cell indicating grid that cursor is
        presently hovering over. When this method is called from
        refesh_screen(), it passes in a CDI.GRID key in p_grid_loc.
        :args:
        - p_grid_loc: (str) Column/Row key of grid to highlight,
            in "0n_0n" (col, row) format, using leading zeros.

        @DEV:
        - Provide options for highlighting in different ways.
        - Pygame colors can use an alpha channel for transparency, but..
            - See: https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame
            - Transparency is not supported directly by draw()
            - Achieved using Surface alpha argument with blit()
        """
        if p_grid_loc != "":
            pg.draw.rect(CDI.WIN, CP_PALEPINK,
                GDAT.CDI.GRIDS[p_grid_loc]["box"], 0)


class TextInput(pg.sprite.Sprite):
    """Define and handle a text input widget.
    Use this to get directions, responses from player
    until I have graphic or voice methods available.
    Expand on this to create GUI control buttons, etc.
    """
    def __init__(self,
                 p_x: int,
                 p_y: int,
                 p_w: int = 100,
                 p_h: int = 50):
        """
        Define text input widget.

        :args:
        - p_x: (int) x-coordinate of top left corner
        - p_y: (int) y-coordinate of top left corner
        - p_w: (int) width of text input widget
        - p_h: (int) height of text input widget
        """
        super().__init__()
        self.t_rect = SR.make_rect(p_y, p_x, p_w, p_h)
        self.t_box = self.t_rect["box"]
        self.t_value = ""
        self.t_font = CDI.F_FIXED_LG
        self.t_color = CP_GREEN
        self.text = self.t_font.render(self.t_value, True, self.t_color)
        self.is_selected = False

    def update_text(self, p_text: str):
        """ Update text value.
        If text is too wide for the widget, truncate it.
        - `self.value` is the current value of the text string.
        - `self.text` is the rendered text surface.
        It will gets refreshed in the `draw` method.

        :args:
        - p_text: (str) Text to render.
        """
        temp_txt = self.t_font.render(p_text, True, self.t_color)
        # shouldn't this be a while loop?...
        if temp_txt.get_rect().width > (self.t_box.w - 10):
            p_text = p_text[:-1]
            temp_txt = self.t_font.render(p_text, True, self.t_color)
        self.t_value = p_text
        self.text = temp_txt

    def clicked(self, p_mouse_loc) -> bool:
        """ Return True if mouse is clicked in the widget.
        """
        if self.t_box.collidepoint(p_mouse_loc):
            self.is_selected = not(self.is_selected)
            return True
        return False

    def draw(self):
        """ Place text in the widget, centered in the box.
        This has the effect of expanding the text as it is typed
        in both directions. Draw the surface (box). Then blit the text.
        """
        self.pos = self.text.get_rect(center=(self.t_box.x + self.t_box.w / 2,
                                              self.t_box.y + self.t_box.h / 2))
        if self.is_selected:
            pg.draw.rect(CDI.WIN, CCL.CP_BLUEPOWDER, self.t_box, 2)
        else:
            pg.draw.rect(CDI.WIN, CP_BLUE, self.t_box, 2)
        CDI.WIN.blit(self.text, self.pos)


class TextInputGroup(pg.sprite.Group):
    """Define a group object.
    A pygame group is a list of objects.
    This class is helpful for handling multiple input widgets, as in a form.

    Customized from the multiple sprites tracker to track text input widgets.
    The `current` attribute holds the currently-selected textinput widget.
    Conversely, the textinput object itself has an `is_selected` attribute
    that is True if it is the currently-selected one.
    If no textinput object is selected, then `current` is None and no
    textinput object has is_selected == True.

    @DEV:
    - Do I actually use this? How? Where? Example?
    """
    def __init__(self):
        super().__init__()
        self.current = None     # ID currently-selected text input widget.

# ====================================================
#  SASKAN GAME
# ====================================================
class SaskanGame(object):
    """PyGame GUI for controlling Saskantinon game functions.
    Initiated and executed by __main__.
    """
    def __init__(self, *args, **kwargs):
        """
        All major classes are instantiated in the main module
        prior to instantiating the SaskanGame class.
        Execute the main event loop.
        """
        self.MOUSEDOWN = False
        self.MOUSECLICKED = False

        self.main_loop()

    # Core Events
    # ==============================================================
    def exit_appl(self):
        """Exit the app cleanly.
        """
        pg.quit()
        sys.exit()

    def check_exit_appl(self,
                       event: pg.event.Event):
        """Handle exit if one of the exit modes is triggered.
        This is triggered by the Q key, ESC key or `X`ing the window.

        :args:
        - event: (pg.event.Event) event to handle
        
        @TODO:
        - Add data cleanup events if/when needed.
        """
        if (event.type == pg.QUIT or
                (event.type == pg.KEYUP and
                    event.key in CDI.KY_QUIT)):
            self.exit_appl()

    def handle_menu_item_click(self,
                               menu_k: tuple):
        """Trigger an event based on menu item selection.

        :args:
        - menu_k: (tuple) menu bar and menu item keys
        """
        # mb_k = menu_k[0]
        mi_k = menu_k[1]
        # mi_nm = GMNU.mitems[mb_k][mi_k]["name"]
        if mi_k == "exit":
            self.exit_appl()
        elif "help" in mi_k:
            if mi_k == "pg_help":
                CDI.WHTM.draw(CDI.WHTM["pygame"])
            elif mi_k == "app_help":
                CDI.WHTM.draw(CDI.WHTM["app"])
            elif mi_k == "game_help":
                CDI.WHTM.draw(CDI.WHTM["game"])
        elif mi_k == "start":
            GDAT.set_datasrc({"catg": 'geo',
                              "item": 'Saskan Lands',
                              "active": True})
            GDAT.set_console_text()
            GDAT.set_map_grid()
        # elif mi_k == "status":
        #     IBAR.info_status["on"] = not IBAR.info_status["on"]
        elif mi_k == "pause_resume":
            IBAR.info_status["frozen"] = not IBAR.info_status["frozen"]

    # Loop Events
    # ==============================================================
    def track_grid(self):
        """Keep track of what grid mouse is over using CDI.G_LNS_VT, CDI.G_LNS_HZ
           to ID grid loc. May be a little faster than parsing thru each
           element of .grid["G"] matrix.
        Note:
        Since "L" defines lines, it has a count one greater than # of
          grids in each row or column.
        """
        mouse_loc = IBAR.info_status["mouse_loc"]
        IBAR.info_status["grid_loc"] = ""
        grid_col = -1
        # vt ande hz are: (x1, y1), (x2, y2)
        for i in range(0, CDI.GRID_COLS):
            vt = CDI.G_LNS_VT[i]
            if mouse_loc[0] >= vt[0][0] and\
               mouse_loc[0] <= vt[0][0] + CDI.GRID_CELL_PX_W:
                    grid_col = i
                    break
        grid_row = -1
        for i in range(0, CDI.GRID_ROWS):
            hz = CDI.G_LNS_HZ[i]
            if mouse_loc[1] >= hz[0][1] and\
               mouse_loc[1] <= hz[0][1] + CDI.GRID_CELL_PX_H:
                    grid_row = i
                    break
        if grid_row > -1 and grid_col > -1:
            IBAR.info_status["grid_loc"] =\
                GDAT.make_grid_key(grid_col, grid_row)

    def track_state(self):
        """Keep track of the state of the app on each frame.

        Sets:
        - mouse_loc: get current mouse location
        - frame_cnt: increment if tracking status and not in a freeze mode
        - cursor: if no text input box is activated, set to default
        """
        IBAR.info_status["mouse_loc"] = pg.mouse.get_pos()
        if IBAR.info_status["frozen"] is False:
            IBAR.info_status["frame_cnt"] += 1
        self.track_grid()

        # For managing text input boxes:
        # if self.TIG.current is None:
        #     pg.mouse.set_cursor(pg.cursors.Cursor())

    def refresh_screen(self):
        """Refresh the screen with the current state of the app.
        30 milliseconds between each frame is the normal framerate.
        To go into slow motion, add a wait here, but don't change the framerate.

        Frozen refers only to the game animation and time-based
        event developments. It has no effect on rendering of the
        game, console or info windows except that we stop incrementing
        the frame count, which is handled in track_state().
        """
        # black out the entire screen
        CDI.WIN.fill(CCL.CP_BLACK)

        # Display info content based on what is currently
        #  posted in the GameData object
        CDI.CONSOLE.draw()

        # Check, Draw info bar
        IBAR.set_ibar_status_text()
        IBAR.draw()
        
        # Draw the game map
        GAMEMAP.draw_map()
        GAMEMAP.draw_hover_cell(IBAR.info_status["grid_loc"])

        # for txtin in self.TIG:
        #     txtin.draw()
        # self.PAGE.draw()

        # refresh the menus
        GMNU.draw_menu_bars()
        for mb_k in GMNU.mitems.keys():
            GMNU.draw_menu_items(mb_k)

        pg.display.update()
        CDI.TIMER.tick(30)

    # Main Loop
    # ==============================================================
    def main_loop(self):
        """Manage the event loop.
        - Track the state of the app
        - Check for exit events
        - Handle menu click events
        - Handle text input events
        - Handle other click events
        - Refresh the screen
        """
        while True:
            self.track_state()

            for event in pg.event.get():

                self.check_exit_appl(event)

                # Avoid flicker due to mouse button down/up events
                if event.type == pg.MOUSEBUTTONDOWN:  # pyright: ignore[reportUnboundVariable] # noqa: E501
                    self.MOUSEDOWN = True
                    self.MOUSECLICKED = False

                if event.type == pg.MOUSEBUTTONUP:   # pyright: ignore[reportUnboundVariable] # noqa: E501
                    if self.MOUSEDOWN:
                        self.MOUSEDOWN = False
                        self.MOUSECLICKED = True

                if self.MOUSECLICKED:
                    self.MOUSECLICKED = False
                    # Handle menu-bar click
                    mb_k = GMNU.click_mbar(
                        IBAR.info_status["mouse_loc"])
                    # Handle menu-item click
                    menu_k = GMNU.click_mitem(
                        IBAR.info_status["mouse_loc"], mb_k)
                    if menu_k[1] != '':
                       self.handle_menu_item_click(menu_k)

                    # Handle text input events
                    # Will be mainly on the console window I think
                    # self.do_select_txtin(sIBAR.info_status["mouse_loc"])

                    # Handle game-window click events

            self.refresh_screen()


if __name__ == '__main__':
    """Cache data and resources in memory and launch the app."""

    GDAT = GameData()
    GMNU = GameMenu()
    IBAR = InfoBar()
    CDI.WHTM = HtmlDisplay()  # for Help windows
    CDI.CONSOLE = GameConsole()
    GAMEMAP = GameMap()
    SaskanGame()
