#!python
"""
:module:    saskan_game.py
:author:    GM (genuinemerit @ pm.me)
Saskan App GUI.  pygame version.

@DEV:
- Prototype basic game activities like:
    - map generation
    - avatar placement/movement
    - physics
    - sound and music
- Use pygame for graphics, sound, everything else.
- Go for more features, better performance than earler prototypes,
    but don't worry too much about interactiviity or complete game
    yet. Focus most on prototyping the WINSas.
- Set up menus. Use what works from Admin GUI, budget GUI, etc.
- Use JSON config files to define sizes, shapes of static things.
- Use io_time, io_graph, io_music modules for dynamic things.
- Use wiretap and logger, but don't get side-tracked.
    - Print statements and debugger are OK for now.
- Sketch out what I want to do before stating to do much code.
    - OK to start simpler. Experiment, be agile.
    - See pygame_lab/app4 ("turtles") for some ideas.

@TODO:
1. Manage status of menu items using metadata. Enable/disable based on state.
- Extend regions metadata (JSON) and code to support drawing high-level box borders.
- Load schema data for Saskan Lands.
- Display console data.
- Colorize grids based on political boundaries.
- Show key/legend for political boundaries.
- Add region names to map, using different fonts for different types of regions.
- Map degrees and km to default map size and grids.
- Add directional arrows, some measures (text, like degrees N, S, E, W) to the map.

@NEXT:
- Get a basic game up and running.
- Manage the status of menu items using metadata. Enable/disable based on state.
- On start:
    - Identify a single AI player.
        - See code in ontology lab.
            - Pick just a few things to start with.
            - Parameterize the data using JSON.
            - Eventually, parameterize all the ontology structures and static data.
            - For now:
                - Just input a name, don't use the generators.
                - Roll the basic attributes, age, home region, DNA, guild affiliation.
                - Pick a starting location.
        - Then do a rough sketch of player actions and events.
            - Highlight what grid player is in.
            - Display data for grid that player is in.
            - Accept input for what grid to travel to.
            - Compute time to walk, to ride to target grid.
            - Animate movement, show time passing, highlight grids passed thru.
    - Add more types of regions, terrain, etc. to map.
        - Start to develop inventory of image widgets, textures, sounds, etc.
        - Sound effects for movement.
        - Theme music for different regions.
        - Play a new theme when entering a different region, town, etc.
    - Add simple sets, scenes, to GameData.
    - Learn! Use what I learn to improve the game.
        - Before adding more players, work on:
            - Elaborating borders, textures at more detail.
            - Zooming in/out to different levels of detail.
            - Taking terrain and other factors into account for movement.
            - Tracking time, season, date, etc.
            - Player functions like:
                - Energy, market, inventory, food/eating, etc.
    - Add more AI players.
        - Start to design some typical encounters.
        - Start to design some typical scenarios, following the script / beat sheet.
"""

import platform
import pygame as pg
import sys
import webbrowser

from dataclasses import dataclass
from os import path
from pathlib import Path
from pprint import pprint as pp     # noqa: F401
from pygame.locals import *

from io_file import FileIO          # type: ignore
from io_wiretap import WireTap      # type: ignore

FI = FileIO()
WT = WireTap()
# Global constants for parameterized configs
FRAME = "game_frame"
MENUS = "game_menus"
TINY_FONT_SZ = 12
SM_FONT_SZ = 24
MED_FONT_SZ = 30
LG_FONT_SZ = 36
# PyGame Init needs to be here to work with PG class.
pg.init()


@dataclass(frozen=True)
class PG:
    """PyGame constants."""
    # CLI Colors and accents
    CL_BLUE = '\033[94m'
    CL_BOLD = '\033[1m'
    CL_CYAN = '\033[96m'
    CL_DARKCYAN = '\033[36m'
    CL_END = '\033[0m'
    CL_GREEN = '\033[92m'
    CL_PURPLE = '\033[95m'
    CL_RED = '\033[91m'
    CL_YELLOW = '\033[93m'
    CL_UNDERLINE = '\033[4m'
    # PyGame Colors
    PC_BLACK = pg.Color(0, 0, 0)
    PC_BLUE = pg.Color(0, 0, 255)
    PC_BLUEPOWDER = pg.Color(176, 224, 230)
    PC_GRAY = pg.Color(80,80,80)
    PC_GREEN = pg.Color(0, 255, 0)
    PC_PALEPINK = pg.Color(215, 198, 198)
    PC_RED = pg.Color(255, 0, 0)
    PC_SILVER = pg.Color(192, 192, 192)
    PC_WHITE = pg.Color(255, 255, 255)
    # PyGame Fonts
    F_SANS_TINY = pg.font.SysFont('DejaVu Sans', TINY_FONT_SZ)
    F_SANS_SM = pg.font.SysFont('DejaVu Sans', SM_FONT_SZ)
    F_SANS_MED = pg.font.SysFont('DejaVu Sans', MED_FONT_SZ)
    F_SANS_LG = pg.font.SysFont('DejaVu Sans', LG_FONT_SZ)
    F_FIXED_LG = pg.font.SysFont('Courier 10 Pitch', LG_FONT_SZ)
    # PyGame Cursors
    CUR_ARROW = pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW)
    CUR_CROSS = pg.cursors.Cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
    CUR_HAND = pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)
    CUR_IBEAM = pg.cursors.Cursor(pg.SYSTEM_CURSOR_IBEAM)
    CUR_WAIT = pg.cursors.Cursor(pg.SYSTEM_CURSOR_WAIT)
    # Overall frame = WIN*
    # Caption is the title of the window (frame).
    pg.display.set_caption(FI.G[FRAME]["ttl"])
    WIN_W = FI.G[FRAME]["sz"]["w"]
    WIN_H = FI.G[FRAME]["sz"]["h"]
    WIN_MID = (WIN_W / 2, WIN_H / 2)
    WIN = pg.display.set_mode((WIN_W, WIN_H))
    # Menu Bar
    # Sizing of top-menu bar items is done in MenuBar class,
    #    based on text width and height.
    # This is top, left of the entire menu:
    MBAR_X = FI.G[MENUS]["bar"]["x"]
    MBAR_Y = FI.G[MENUS]["bar"]["y"]
    # This is w, h, margin of each vertical menu bar menu
    MBAR_W = FI.G[MENUS]["bar"]["w"]
    MBAR_H = FI.G[MENUS]["bar"]["h"]
    MBAR_MARGIN = FI.G[MENUS]["bar"]["margin"]
    MBAR_LOC = (MBAR_X, MBAR_Y)
    # In-game "windows" = CONS*, GWIN*, IBAR*, PHELP*
    CONS = FI.G["game_windows"]["info"]
    GWIN = FI.G["game_windows"]["game"]
    PHELP = FI.G["uri"]["help"]
    IBAR_X = FI.G[FRAME]["ibar"]["x"]
    IBAR_Y = FI.G[FRAME]["ibar"]["y"]
    IBAR_LOC = (IBAR_X, IBAR_Y)
    # Other
    KEYMOD_NONE = 4096
    TIMER = pg.time.Clock()


class GameMenu(object):
    """Define an in-memory object for menu bars & menu items with both static
    and dynamic value attributes.
    Reference menus by both key and name. Associate menu bar with its items.
    Pull in static values from JSON and assign initial values to dynamic fields.
    """
    def __init__(self):
        """Initialize the GameMenu object.
        """
        self.mbars = dict()
        self.mitems = dict()
        self.set_menu_bar()
        self.set_menu_items()
        self.draw_mbar()
        for mb_ky, m_items in self.mitems.items():
            for mi_ky in list(m_items.keys()):
                self.draw_mitems(mb_ky, mi_ky)
        # ==============================================================
        msg = f"\nGameMenu initialized: {self}"
        WT.log("info", msg, __file__, __name__, self, sys._getframe())
        # ==============================================================

    def set_menu_bar(self):
        """Set up the menu bar.
        Instantiate MenuBar and add to the object.

        @DEV - check logic for setting width of menu bar per text size.
        - Can't figure out why first menu bar box is so wide. It doesn't seem to match
          the actual configuration of the Rect() object.
        - Going to try fixed widths for menus.
        """
        self.mbars = {ky: {"nm": val["nm"]} for ky, val in FI.G[MENUS]["menu"].items()}

        # initialize prev_x to left edge of menu bar per config
        x = PG.MBAR_X
        for mb_ky, attrs in self.mbars.items():

            self.mbars[mb_ky] =\
                {"nm": attrs["nm"],
                 "text": PG.F_SANS_SM.render(attrs["nm"], True,
                         PG.PC_BLUEPOWDER, PG.PC_BLACK),
                 "selected": False}
            self.mbars[mb_ky]["tbox"] = self.mbars[mb_ky]["text"].get_rect()
            self.mbars[mb_ky]["box"] =\
                pg.Rect((x, PG.MBAR_Y), (PG.MBAR_W, PG.MBAR_H + (PG.MBAR_MARGIN * 2)))
            x = self.mbars[mb_ky]["box"].right
            self.mbars[mb_ky]["tbox"].left =\
                self.mbars[mb_ky]["box"].left + (self.mbars[mb_ky]["box"].width / 2) - 12
            self.mbars[mb_ky]["tbox"].top =\
                self.mbars[mb_ky]["box"].top + PG.MBAR_MARGIN + 5

    def set_menu_items(self):
        """Add a MenuItems (list of items) to the object."""
        self.mitems = {ky: val["items"] for ky, val in FI.G[MENUS]["menu"].items()}

        mx = 0
        for mb_ky, list_attr in self.mitems.items():

            if "mlist_box" not in list(self.mbars[mb_ky].keys()):
                self.mbars[mb_ky]["mlist_box"] =\
                pg.Rect(self.mbars[mb_ky]["box"].left,
                        self.mbars[mb_ky]["box"].bottom,
                        PG.MBAR_W,
                        self.mbars[mb_ky]["box"].height * len(list(self.mitems.keys())))
                self.mbars[mb_ky]["mlist_visible"] = False
            for mi_ky, item_attr in list_attr.items():
                self.mitems[mb_ky][mi_ky]["selected"] = False
                self.mitems[mb_ky][mi_ky]["enabled"] = True\
                if "default" not in list(item_attr.keys())\
                    or item_attr["default"] == "enabled" \
                else False
            txt_color = PG.PC_GREEN if self.mitems[mb_ky][mi_ky]["enabled"] is True\
                  else PG.PC_GRAY
            self.mitems[mb_ky][mi_ky]["text"] = PG.F_SANS_SM.render(
                item_attr["nm"], True, txt_color, PG.PC_BLACK)
            self.mitems[mb_ky][mi_ky]["tbox"] =\
                pg.Rect(self.mbars[mb_ky]["box"].left + PG.MBAR_MARGIN,
                        ((self.mbars[mb_ky]["box"].top + (PG.MBAR_H * mx)) + PG.MBAR_MARGIN),
                         self.mitems[mb_ky][mi_ky]["text"].get_width() + (PG.MBAR_MARGIN * 2),
                         PG.MBAR_H)
            mx += 1

    def draw_mbar(self):
        """ Draw a Menu Bar item.
        """
        for mb_ky, attr in self.mbars.items():
            if attr["selected"]:
                pg.draw.rect(PG.WIN, PG.PC_GREEN, attr["box"], 4)
            else:
                pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, attr["box"], 4)
            PG.WIN.blit(attr["text"], attr["tbox"])

    def draw_mitems(self,
                    p_mb_ky,
                    p_mi_ky):
        """ Draw the list of Menu Items.

        :attr:
        - p_mb_ky: key to the menu bar data
        - p_mi_ky: key to the menu item data
        """
        if self.mbars[p_mb_ky]["mlist_visible"] is True:
            pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER,
                         self.mbars[p_mb_ky]["mlist_box"], 2)
            for attr in self.mitems[p_mb_ky].values():
                # Draw each menu item in the identified box
                PG.WIN.blit(attr["txt"], attr["tbox"])

    def click_mbar(self,
                   p_mouse_loc: tuple) -> str:
        """
        :attr:
        - p_mouse_loc: tuple
        :return: id if clicked mbar item, else None
        """
        for mb_ky, attr in self.mbars.items():
            if attr["box"].collidepoint(p_mouse_loc):
                if attr["selected"] is True:
                    # Hide bar and item list if currently selected.
                    self.mitems[mb_ky]["selected"] = False
                    self.mitems[mb_ky]["mlist_visible"] = False
                else:
                    self.mitems[mb_ky]["selected"] = True
                    self.mitems[mb_ky]["mlist_visible"] = True
                    # Hide and unselect other items and menus.
                    for other_ky in list(self.mbars.keys()):
                        if not other_ky == mb_ky:
                            self.mitems[other_ky]["mlist_visible"] = False
                            self.mitems[other_ky]["selected"] = False
                return (mb_ky)
            else:
                if attr["selected"] is True:
                     self.mitems[mb_ky]["selected"] = True
                else:
                     self.mitems[mb_ky]["selected"] = False
        return None

    def click_mitem(self,
                    p_mouse_loc: tuple) -> str:
        """ Return id if clicked on a menu item.

        :attr:
        - p_mouse_loc: tuple of mouse location
        :return:
        - (str) id of clicked menu item
        """
        for mb_ky, val in self.mitems.items():
            for mi_ky, attr in val.items():

                pp((self.mitems[mb_ky][mi_ky],
                    self.mitems[mb_ky][mi_ky]["selected"]))

                self.mitems[mb_ky][mi_ky]["selected"] = False
                if attr['tbox'].collidepoint(p_mouse_loc):
                    self.mitems[mb_ky][mi_ky]["selected"] = True
                    return (mi_ky)
        return None

class HtmlDisplay(object):
    """Set content for display in external web browser.
    """

    def __init__(self):
        """ Initialize Html Display.

        @DEV
        - Look into ways of configuring browser window.
        """
        pass

    def draw(self,
             p_help_uri: str):
        """ Open web browser to display HTML resource.
        It opens subsequent items in the same browser window,
        in new tabs on my setup (Linux Ubuntu, Firefox browser)

        Args: (str) UTI to HTML file to display in browser.
        """
        webbrowser.open(p_help_uri)
        # webbrowser.open_new_tab(p_help_uri)


class TextInput(pg.sprite.Sprite):
    """Define and handle a text input widget.
    Use this to get directions, responses from player
    until I have graphic or voice methods available.
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
        self.t_box = pg.Rect(p_x, p_y, p_w, p_h)
        self.t_value = ""
        self.t_font = PG.F_FIXED_LG
        self.t_color = PG.PC_GREEN
        self.text = self.t_font.render(self.t_value, True, self.t_color)
        self.is_selected = False

    def draw(self):
        """ Place text in the widget, centered in the box.
        This has the effect of expanding the text as it is typed
        in both directions. Draw the surface (box). Then blit the text.
        """
        self.pos = self.text.get_rect(center=(self.t_box.x + self.t_box.w / 2,
                                              self.t_box.y + self.t_box.h / 2))
        if self.is_selected:
            pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, self.t_box, 2)
        else:
            pg.draw.rect(PG.WIN, PG.PC_BLUE, self.t_box, 2)
        PG.WIN.blit(self.text, self.pos)

    def clicked(self, p_mouse_loc) -> bool:
        """ Return True if mouse is clicked in the widget.
        """
        if self.t_box.collidepoint(p_mouse_loc):
            self.is_selected = not(self.is_selected)
            return True
        return False

    def update_text(self, p_text: str):
        """ Update text value.
        If text is too wide for the widget, truncate it.
        - `self.value` is the current value of the text string.
        - `self.text` is the rendered text surface.
        It actually gets updated in the `draw` method.

        :args:
        - p_text: (str) Newest version of text to render.
        """
        temp_txt = self.t_font.render(p_text, True, self.t_color)
        if temp_txt.get_rect().width > (self.t_box.w - 10):
            p_text = p_text[:-1]
            temp_txt = self.t_font.render(p_text, True, self.t_color)
        self.t_value = p_text
        self.text = temp_txt


class TextInputGroup(pg.sprite.Group):
    """Define a group object.
    A pygame group is basically a list of objects.
    Customized from the multiple sprites tracker to track text input widgets.
    The `current` attribute holds the currently-selected txtin widget.
    Conversely, the textinput object itself has an `is_selected` attribute
    that is True if it is the currently-selected txtin widget.
    If no textinput object is selected, then `current` is None and no
    txtin object has is_selected == True.

    This is helpful for handling multiple text input widgets, as if in a form.
    """
    def __init__(self):
        super().__init__()
        self.current = None     # ID currently-selected text input widget.


class GameData(object):
    """Retrieve static game data from JSON and image file(s).
    Organize it into data structures for use by the game
    console and the game map.

    @DEV:
    - Reorganize as needed into text, Pandas Dataframe, graph,
      any other data formats that will be useful.
    - Consider how to handle layers of data, e.g. on a map, or
      in a scene, so that zoom-in, zoom-out, and other views
      can be handled without having to re-read the data.
    - Think how to map dimensions of a given region to the
      dimensions of the Game (map) window. Probably best to
      start with a fixed size for a grid-square, compute number
      of grids in the GUI region, and align data to that -- as
      opposed to defining grid sizes based on dimensions in the
      data, which could cause different grid sizes for different
      sets of mapped data.
      - So start out by defining a fixed grid size, then assign
        a key to that grid, showing km per grid. Assign degrees
        so that the display shows lat/long outside the range of the
        data. Then center the mapped data on the display grid.
      - Map the Saskan Lands major political boundaries, then work
        on layering in different things .. more detailed regions,
        towns, roads, geographical features, neighboring regions,
        etc.
      - Once I have a feelig for that, then work on mapping data
        for a more zoomed-in region, like a town and its environs.
        Then for a scene, like a building, or a room.
    - Consider where to provide screen real estate for GUI controls...
      scroll, zoom, pan, select-move and so on.
        - Those things may not be part of this class, but they will
          interact with it at any rate.
    """
    def __init__(self):
        """Initialize Game Data structures
         - Geographical map(s)
         - Event drivers
         - Star map(s)
         - State trackers
         - etc.
        """
        self.CON = {"box": None,
                    "T": list()}
        self.MAP = {"box": None,
                    "D": dict(),
                    "G": dict(),
                    "L": dict()}
        self.POST = {"active": False,
                     "catg": None,
                     "item": None}
        self.init_map_dims()
        self.init_grid_data()

    def init_map_dims(self):
        """
        Define static default map dimensions.
        Add other dimensions as needed for zoom-in.
        Handle conversions elsewhere.
        Default units (km, px, deg) are defined here.
        px refers to drawing units in pygame.
        deg are + if N of eq, E of Greenwich;
                - if S of eq, W of Greenwich.
        """
        # Default border box for the game window.
        self.MAP["box"] = pg.Rect(PG.GWIN["x"], PG.GWIN["y"],
                                  PG.GWIN["w"], PG.GWIN["h"])
        # Default grid and line dimensions.
        self.grid_tloff = {"x": 17, "y": 18}
        self.rows_cnt = 34
        self.cols_cnt = 44
        self.grid_px_w = self.grid_px_h = 40
        self.grid_km_w = self.grid_km_h = 32.7775
        self.line_px_w = self.grid_px_w * self.cols_cnt
        self.line_px_h = self.grid_px_h * self.rows_cnt
        self.line_km_w = self.grid_km_w * self.cols_cnt
        self.line_km_h = self.grid_km_h * self.rows_cnt
        # Default grid line coordinates.
        self.MAP["L"] = {"rows": [], "cols": []}
        for r in range(self.rows_cnt + 1):
            x = self.grid_tloff["x"] + self.MAP["box"].x
            y = self.grid_tloff["y"]  + self.MAP["box"].y + (r * self.grid_px_h)
            self.MAP["L"]["rows"].append(
                [(x, y), (x + self.line_px_w, y)])
        for c in range(self.cols_cnt + 1):
            x = self.grid_tloff["x"] + self.MAP["box"].x + (c * self.grid_px_w)
            y = self.grid_tloff["y"] + self.MAP["box"].y
            self.MAP["L"]["cols"].append(
                [(x, y), (x, y + self.line_px_h)])

    def init_grid_data(self):
        """ Define a record for each grid to store game data.
        Use Pandas Dataframes, graphs, etc. as needed.
        """
        grid_record = {"id": {"text": None, "rect": None, "img": None},
                       "tl_px": {"x":(), "y":()},
                       "tl_dg": {"lat": (), "lon": ()},
                       "km": {"w": 0.0, "h": 0.0},
                       "text": "",
                       "lines": list(),
                       "points": list(),
                       "sounds": list(),
                       "images": list()}
        grid_col = {c: grid_record for c in range(self.cols_cnt)}
        self.MAP["G"] = {r: grid_col for r in range(self.rows_cnt)}

    def set_post(self,
                 p_post: dict):
        """Capture status settings for game data.
        Such as:
        - Key values pointing to data in JSON files, identifying what
          external data sets to retrieve, use.
        - Status information, such as:
            - Game is active
            - Game is paused
            - Game is over
            - Whose turn it is
        :args:
        - p_post (dict): name-value pairs of status settings, such as:
            - "catg": name of category to load from JSON
            - "item": name of item to load from JSON
            - "active": boolean indicating whether game is active
        """
        for k, v in p_post.items():
            self.POST[k] = v

    def set_console_text(self) -> str:
        """For posted category item, format list of strings to render as Console text.
        """
        self.CON["box"] = pg.Rect(PG.CONS["x"], PG.CONS["y"],
                                  PG.CONS["w"], PG.CONS["h"])
        self.CON["T"] = list()
        if self.POST["catg"] == "geo":
            self.set_geo_text(FI.S[self.POST["catg"]][self.POST["item"]])

    def set_geo_text(self,
                     con_data: dict):
        """Format geo data for display as Console text.
        This content should be further abstracted, internationalised.
        """
        # Item name(s)
        self.CON["T"].append(con_data['name']['common'])
        for k, v in con_data['name'].items():
            if k != 'common':
                self.CON["T"].append(f"  {k}: {v}")
        # Item attributes
        for t in [
            "-" * 16,
            "Kilometers",
            f"  North-South: {con_data['map']['rect']['n_s_km']}",
            f"  East-West: {con_data['map']['rect']['e_w_km']}",
            "Degrees",
            "  Latitude",
            f"    North: {con_data['map']['degrees']['n_lat']}",
            f"    South: {con_data['map']['degrees']['s_lat']}",
            "  Longitude",
            f"    West: {con_data['map']['degrees']['w_long']}",
            f"    East: {con_data['map']['degrees']['e_long']}",
            "-" * 16,
            f"{list(con_data['contained_by'].keys())[0]}: " +
                f"{list(con_data['contained_by'].values())[0]}",
            "-" * 16,
            "Political Boundaries"]:
                self.CON["T"].append(t)
        # Lists of Item attributes
        politics = {k: v for k, v in con_data['contains'].items()\
                    if k in ('federation', 'district')}
        if "federation" in politics:
            self.CON["T"].append("  Federations:")
            for fed in politics["federation"]:
                self.CON["T"].append(f"    {fed}")
        if "district" in politics:
            self.CON["T"].append("  Districts:")
            for dist in politics["district"]:
                self.CON["T"].append(f"    {dist}")


class GameConsole(object):
    """Define and handle the Game Info window (rect).

    Display game data like score, etc.; and to contain text inputs.
    It is a rect within the Frame real estate, not a separate Frame object.
    """

    def __init__(self):
        """ Initialize GameConsole.
        """
        self.is_visible = False
        self.BOX = pg.Rect(PG.CONS["x"], PG.CONS["y"],
                           PG.CONS["w"], PG.CONS["h"])
        self.TTL = None
        self.TXT = None
        self.IMG = None
        WT.log("info", f"\nGameConsole instantiated: {str(self)}",
               __file__, __name__, self, sys._getframe())

    def set_header(self):
        """ Set Game Console header.
        """
        self.IMG = PG.F_SANS_LG.render(PG.CONS["ttl"], True,
                                       PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.TTL = self.IMG.get_rect()
        self.TTL.topleft = (PG.CONS["x"] + 5,
                            PG.CONS["y"] + 5)

    def set_console_text_line(self,
                      p_lnno: int,
                      p_text: str):
        """ Set a line of text to display in the GameConsole rect.
        :args:
        - p_lnno: (int) Line number of text to display.
        - p_text: (str) Line of text to display.
        """
        self.IMG = PG.F_SANS_MED.render(p_text, True,
                                        PG.PC_BLUEPOWDER,
                                        PG.PC_BLACK)
        self.TXT = self.IMG.get_rect()
        y = self.TTL.y + LG_FONT_SZ
        self.TXT.topleft = (self.TTL.x,
                            y + ((MED_FONT_SZ + 2) * (p_lnno + 1)))

    def draw(self):
        """ Draw GameConsole.
        - Black out the GameConsole rect.
        - Draw the console header.
        - Incrementally add lines text (or inputs) to GameConsole
          region based on current posting in GameData object.
        """
        pg.draw.rect(PG.WIN, PG.PC_BLUE, GDAT.CON["box"], 1)
        self.set_header()
        PG.WIN.blit(self.IMG, self.TTL)
        for i, ln in enumerate(GDAT.CON["T"]):
           self.set_console_text_line(i, ln)
           PG.WIN.blit(self.IMG, self.TXT)


class GameWindow(object):
    """Define and handle the Game GUI window (rect).

    Display the map, scenes, game widgets, GUI controls.
    It is a rect within the Frame real estate, not a separate Frame object."""

    def __init__(self):
        """Initialize GameWindow"""
        self.is_visible = False
        self.BOX = pg.Rect(PG.GWIN["x"], PG.GWIN["y"],
                           PG.GWIN["w"], PG.GWIN["h"])
        WT.log("info", f"\nGameWindow initialized: {str(self)}",
               __file__, __name__, self, sys._getframe())

    def draw(self):
        """Draw the Game map.
        draw(surface, color, coordinates, width)

        Define additional types of structures as needed. e.g., graphs, etc.
        """
        pg.draw.rect(PG.WIN, PG.PC_SILVER, self.BOX, 5)
        # horizontal lines
        for gline in GDAT.MAP["L"]["rows"]:
            pg.draw.aalines(PG.WIN, PG.PC_WHITE, False, gline)
        # vertical lines
        for gline in GDAT.MAP["L"]["cols"]:
            pg.draw.aalines(PG.WIN, PG.PC_WHITE, False, gline)


class InfoBar(object):
    """Info Bar object.
    Deafault text is system info.
    To change the text, call set_console_text function.
    """
    def __init__(self):
        """ Initialize Info Bar. """
        self.info_status = {
            "on": False,
            "frozen": True,
            "frame_cnt": 0,
            "mouse_loc": (0, 0),
            "grid_loc": (0, 0)}
        self.set_default_text()

    def set_default_text(self):
        """ Set Info Bar text to system info. """
        self.system_text = (
            FI.G[FRAME]["dsc"] +
            " | " + platform.platform() +
            " | Python " + platform.python_version() +
            " | Pygame " + pg.version.ver)

    def set_status_text(self):
        """ Set Info Bar text to status text. """
        self.status_text = (
            "Generation: " + str(self.info_status["frame_cnt"]) +
            "    | Mouse: " + str(self.info_status["mouse_loc"]) +
            "    | Grid: " + str(self.info_status["grid_loc"]))

    def draw(self):
        """ Draw Info Bar.
        Optionally draw status info.
        """
        if self.info_status["on"]:
            self.itxt = PG.F_SANS_SM.render(
                self.system_text + "   | " + self.status_text,
                True, PG.PC_BLUEPOWDER, PG.PC_BLACK)
        else:
            self.itxt = PG.F_SANS_SM.render(
                self.system_text, True, PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.ibox = self.itxt.get_rect()
        self.ibox.topleft = PG.IBAR_LOC
        PG.WIN.blit(self.itxt, self.ibox)


# ====================================================
#  SASKAN GAME
# ====================================================
class SaskanGame(object):
    """PyGame GUI for controlling Saskantinon game functions.
    Initiated and executed by __main__.
    """
    def __init__(self, *args, **kwargs):
        """ Initialize in-game keyboard usage. (Modify as needed.)
        Execute the main event loop.
        All of the major classes are instantiated in the main module
         prior to instantiating the SaskanGame class.
        """
        self.QUIT_KY: list = [pg.K_q, pg.K_ESCAPE]
        self.ANIM_KY: list = [pg.K_F3, pg.K_F4, pg.K_F5]
        self.DATA_KY: list = [pg.K_a, pg.K_l]
        self.RPT_TYPE_KY: list = [pg.K_KP1, pg.K_KP2, pg.K_KP3]
        self.RPT_MODE_KY: list = [pg.K_UP, pg.K_RIGHT, pg.K_LEFT]

        self.main_loop()


    # Keyboard and Menu Item Event Handlers
    # ==============================================================
    def exit_appl(self):
        """Exit the app.
        """
        pg.quit()
        sys.exit()

    def check_exit_appl(self,
                       event: pg.event.Event):
        """Handle exit if one of the exit modes is triggered.
        This is triggered by the Q key, ESC key or `X`ing the window.

        :args:
        - event: (pg.event.Event) event to handle
        """
        if (event.type == pg.QUIT or
                (event.type == pg.KEYUP and event.key in self.QUIT_KY)):
            self.exit_appl()

    def handle_menu_event(self,
                          p_mb_ky,
                          p_mi_ky):
        """Trigger an event based on menu item selection.

        :args:
        - p_mbar: (str or None) menu item key
        - p_mitem: (str or None )menu item key
        """
        # ==============================================================
        msg = f"\nMenu item clicked: {p_mb_ky}, {p_mi_ky}, {GMNU.mbars[p_mb_ky]}, " +\
              f"{GMNU.mitems[p_mb_ky][p_mi_ky]}"
        WT.log("info", msg, __file__, __name__, self, sys._getframe())
        # ==============================================================
        if p_mi_ky == "exit":
            self.exit_appl()
        elif "help" in p_mi_ky:
            if p_mi_ky == "pg_help":
                WHTML.draw(PG.PHELP["pygame"])
            elif p_mi_ky == "app_help":
                WHTML.draw(PG.PHELP["app"])
            elif p_mi_ky == "game_help":
                WHTML.draw(PG.PHELP["game"])
        elif p_mi_ky == "start":
            GDAT.set_post({"catg": 'geo',
                           "item": 'Saskan Lands',
                           "active": True})
            CONS.is_visible = True
            GWIN.is_visible = True
        elif p_mi_ky == "status":
            IBAR.info_status["on"] = not IBAR.info_status["on"]
        elif p_mi_ky == "pause_resume":
            IBAR.info_status["frozen"] = not IBAR.info_status["frozen"]


    # Loop Events
    # ==============================================================
    def track_grid(self):
        """Keep tracks of what grid the mouse is in."""
        grid_r = 0
        grid_c = 0
        IBAR.info_status["grid_loc"] = ("", "")
        for i, r in enumerate(GDAT.MAP["L"]["rows"]):
            if IBAR.info_status["mouse_loc"][1] >= r[0][1] and\
               IBAR.info_status["mouse_loc"][1] <= r[0][1] + GDAT.grid_px_h:
                grid_r = i + 1
                break
        for i, c in enumerate(GDAT.MAP["L"]["cols"]):
            if IBAR.info_status["mouse_loc"][0] >= c[0][0] and\
               IBAR.info_status["mouse_loc"][0] <= c[0][0] + GDAT.grid_px_w:
                IBAR.info_status["grid_loc"] = i + 1
                grid_c = i + 1
                break
        if grid_r > 0 and grid_c > 0:
            IBAR.info_status["grid_loc"] = (grid_r, grid_c)
        else:
            IBAR.info_status["grid_loc"] = ""

    def track_state(self):
        """Keep track of the state of the app on each frame.

        Sets:
        - mouse_loc: get current mouse location
        - frame_cnt: increment if tracking status and not in a freeze mode
        - cursor: if no text input box is activated, set to default
        """
        if GDAT.POST["active"]:
            IBAR.info_status["on"] = True
        if IBAR.info_status["on"] is True and\
            IBAR.info_status["frozen"] is False:
                IBAR.info_status["frame_cnt"] += 1

        IBAR.info_status["mouse_loc"] = pg.mouse.get_pos()
        self.track_grid()

        # For managing text input boxes:
        # if self.TIG.current is None:
        #     pg.mouse.set_cursor(pg.cursors.Cursor())

    def refresh_screen(self):
        """Refresh the screen with the current state of the app.
        30 milliseconds between each frame is the normal framerate.
        To go into slow motion, add a wait here, but don't change the framerate.

        N.B. Frozen refers only to the game animation and time-based
        event developments. It has no effect on rendering of the
        game, console or info windows except that we stop incrementing
        the frame count, which is handled in track_state().
        """
        # black out the entire screen
        PG.WIN.fill(PG.PC_BLACK)

        # refresh the Game/Console window
        # text to display is based on what is currently
        #  set to be posted in the GameData object
        if CONS.is_visible is True:
            GDAT.set_console_text()
            CONS.draw()

        # refresh the Game/Map window
        if GWIN.is_visible is True:
            GWIN.draw()

        # Info/Status bar
        if IBAR.info_status["on"] is True:
            IBAR.set_status_text()
        else:
            IBAR.set_default_text()
        IBAR.draw()

        # for txtin in self.TIG:
        #     txtin.draw()
        # self.PAGE.draw()

        # refresh the menus
        GMNU.draw_mbar()
        for mb_ky, mi_ky in GMNU.mitems.items():
            GMNU.draw_mitems(mb_ky, list(mi_ky.keys())[0])

        pg.display.update()
        PG.TIMER.tick(30)

    # Main Loop
    # ==============================================================
    def main_loop(self):
        """Manage the event loop.
        - Handle window events (quit --> ESC or Q)
        """
        WT.log("info", "\nevent loop launched",
               __file__, __name__, self, sys._getframe())
        while True:
            # Get mouse_loc and frame_cnt
            self.track_state()

            for event in pg.event.get():

                # Handle keyboard quit events (ESC or Q)
                self.check_exit_appl(event)

                # Handle mouse click events
                if event.type == pg.MOUSEBUTTONDOWN:

                    # Handle menu-click events
                    mb_ky = GMNU.click_mbar(IBAR.info_status["mouse_loc"])
                    mi_ky = GMNU.click_mitem(IBAR.info_status["mouse_loc"])

                    if mi_ky is not None:
                        self.handle_menu_event(mb_ky, mi_ky)

                    # Handle text input events
                    # self.do_select_txtin(sIBAR.info_status["mouse_loc"])

                    # Handle game-click events

            self.refresh_screen()

# Run program
if __name__ == '__main__':
    """Run program."""

    FI.pickle_saskan(path.join("/home", Path.cwd().parts[2], FI.D['APP']))
    # ====================================================
    WT.log("info", "\ndev/shm cache created",
            __file__, __name__, None, sys._getframe())
    # ====================================================
    GDAT = GameData()    # Init static game data and resources
    GMNU = GameMenu()
    WHTML = HtmlDisplay()  # for Help windows
    IBAR = InfoBar()
    CONS = GameConsole()
    GWIN = GameWindow()
    SaskanGame()
