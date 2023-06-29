#!python
"""
:module:    saskan_game.py
:author:    GM (genuinemerit @ pm.me)
Saskan App GUI.  pygame version.

:classes:
    - PG: Frozen constants, using PyGame and config constructs
    - GameMenu: Manage applications menu bars, items, draw and click events
    - HtmlDisplay: Manage display of HTML pages in a browser
    - TextInput: Handle text input events in a single input box
    - TextInputGroup: Handle groups of text input boxes, like a form
    - GameData: Load, scrub, organize, and manage game-related data
    - GameConsole: Manage display of data (text) in game console window
    - GameMap: Manage display of map & related widgets in game map window
    - InfoBar: Manage display of info bar/dock at bottom of main frame
    - SaskanGame: Main game class, includes event loop, event handlers,
        state management, and rendering of all game windows and widgets
    - __main__: Entry point for this module, instantitates all classes


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

@NEXT:

+ Simplify the menu code.
+ Manage status of menu items using metadata. Enable/disable based on state,
  not only on start/default, but following any given menu-item click.

- Extend regions metadata (JSON) and code to support drawing high-level box (map) borders.
- Load schema data for Saskan Lands.
- Display console data.
- Colorize grids based on political boundaries.
- Show key/legend for political boundaries.
- Add region names to map, using different fonts for different types of regions.
- Map degrees and km to default map size and grids.
- Add directional arrows, some measures (text, like degrees N, S, E, W) to the map.

- Get a basic more or less complete (skeletal) game up and running.
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


- See if I can adjust the resolution of the game window based on environment.
  - For example, on the high-res Dell Linux laptop, the game is too small.
  - But on the low-res old Lenovo Linux laptop, the game is too big.
  - ^ lower priority
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
# PyGame Init needs to be here to work properly with PG class.
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
    PC_GRAY_DARK = pg.Color(20, 20, 20)
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
    # In-game "windows" = CONSOLE*, GAMEMAP*, IBAR*, PHELP*
    CONSOLE = FI.G["game_windows"]["info"]
    GAMEMAP = FI.G["game_windows"]["game"]
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

    @DEV - Instead of setting texts to green, only set box borders to green.
    """
    def __init__(self):
        """Initialize the GameMenu object.
        """
        self.mbars = dict()
        self.mitems = dict()
        self.set_menu_bar()
        self.set_menu_items()
        self.draw_menu_bar()
        for mb_ky in self.mitems.keys():
            self.draw_menu_items(mb_ky)
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
                         PG.PC_BLUEPOWDER, PG.PC_GRAY_DARK),
                 "selected": False}
            self.mbars[mb_ky]["tbox"] = self.mbars[mb_ky]["text"].get_rect()
            self.mbars[mb_ky]["box"] =\
                pg.Rect((x, PG.MBAR_Y), (PG.MBAR_W, PG.MBAR_H + (PG.MBAR_MARGIN * 2)))
            x = self.mbars[mb_ky]["box"].right
            self.mbars[mb_ky]["tbox"].left =\
                self.mbars[mb_ky]["box"].left + (self.mbars[mb_ky]["box"].width / 2) - 12
            self.mbars[mb_ky]["tbox"].top =\
                self.mbars[mb_ky]["box"].top + PG.MBAR_MARGIN + 5

    def set_menu_items_state(self,
                            mb_ky: str,
                            mi_ky: str,
                            p_use_default: bool = False):
        """Set the enabled state of identified menu item and/or
           set the enabled status of dependent menu items.
        Dependent menu items are always in the same menu list as the
           selected menu item.
        :attr:
        - mb_ky: str - menu bar key
        - mi_ky: str - menu item key
        - p_use_default: bool - use default enabled value if True
        """
        self.mitems[mb_ky][mi_ky]["enabled"] = False
        txt_color = PG.PC_GRAY
        # Set enabled status of identified item
        if p_use_default:
            if ("default" in list(self.mitems[mb_ky][mi_ky].keys()) and\
                self.mitems[mb_ky][mi_ky]["default"] == "enabled") or\
               "default" not in list(self.mitems[mb_ky][mi_ky].keys()):
                    self.mitems[mb_ky][mi_ky]["enabled"] = True
                    txt_color = PG.PC_BLUEPOWDER
            # Set text color and content of identified item
            self.mitems[mb_ky][mi_ky]["text"] = PG.F_SANS_SM.render(
                self.mitems[mb_ky][mi_ky]["nm"], True, txt_color, PG.PC_GRAY_DARK)
        else:
            # Default selected item to enabled status
            self.mitems[mb_ky][mi_ky]["enabled"] = True
            self.mitems[mb_ky][mi_ky]["text"] = PG.F_SANS_SM.render(
                self.mitems[mb_ky][mi_ky]["nm"], True, PG.PC_BLUEPOWDER,
                PG.PC_GRAY_DARK)
            # Identify dependent menu items and modify their enabled status
            if "disable" in list(self.mitems[mb_ky][mi_ky].keys()):
                for dep_ky in self.mitems[mb_ky][mi_ky]["disable"]:
                    self.mitems[mb_ky][dep_ky]["enabled"] = False
                    self.mitems[mb_ky][dep_ky]["text"] = PG.F_SANS_SM.render(
                        self.mitems[mb_ky][dep_ky]["nm"], True, PG.PC_GRAY,
                        PG.PC_GRAY_DARK)
            if "enable" in list(self.mitems[mb_ky][mi_ky].keys()):
                for dep_ky in self.mitems[mb_ky][mi_ky]["enable"]:
                    self.mitems[mb_ky][dep_ky]["enabled"] = True
                    self.mitems[mb_ky][dep_ky]["text"] = PG.F_SANS_SM.render(
                        self.mitems[mb_ky][dep_ky]["nm"], True,
                        PG.PC_BLUEPOWDER, PG.PC_GRAY_DARK)

    def set_menu_items(self):
        """Add a MenuItems (list of items) to the object.
        Updates mbars with mlist_box, a Rect() object for the menu items.
        Updates mitems with drawing objects for each item under a menu bar.
        - pygame Rect((left, top), (width, height))
        """
        # Init menu items from config
        self.mitems = {ky: val["items"] for ky, val in FI.G[MENUS]["menu"].items()}
        # For each menu bar / list of menu items:
        for mb_ky, mlist in self.mitems.items():
            if "mlist_box" not in list(self.mbars[mb_ky].keys()):
                # Define container box for list of menu items
                # Store it in mbars
                left = self.mbars[mb_ky]["box"].left
                top = self.mbars[mb_ky]["box"].bottom
                self.mbars[mb_ky]["mlist_box"] =\
                    pg.Rect((left, top), (PG.MBAR_W, 0))
            # Set up each menu item:
            mi_x = 0
            for mi_ky, mi_vals in mlist.items():
                # Set status flags
                self.mitems[mb_ky][mi_ky]["selected"] = False
                self.set_menu_items_state(mb_ky, mi_ky, p_use_default=True)
                # Set text box
                text_width = self.mitems[mb_ky][mi_ky]["text"].get_width()
                left = self.mbars[mb_ky]["box"].left + (PG.MBAR_MARGIN * 4)
                top = self.mbars[mb_ky]["box"].bottom +\
                    (PG.MBAR_H * mi_x) + PG.MBAR_MARGIN
                width = text_width + (PG.MBAR_MARGIN * 2)
                self.mitems[mb_ky][mi_ky]["tbox"] =\
                    pg.Rect((left, top), (width, PG.MBAR_H))
                # Adjust container box height
                self.mbars[mb_ky]["mlist_box"].height += PG.MBAR_H
                mi_x += 1

    def click_mbar(self,
                   p_mouse_loc: tuple):
        """
        :attr:
        - p_mouse_loc: tuple
        :return: id of currently selected menu bar, else None
        """
        for mb_ky, mb_vals in self.mbars.items():
            if mb_vals["box"].collidepoint(p_mouse_loc):
                self.mbars[mb_ky]["selected"] = True\
                    if self.mbars[mb_ky]["selected"] is False else False
                for ky in [ky for ky in self.mbars.keys() if ky != mb_ky]:
                    self.mbars[ky]["selected"] = False
                return (mb_ky)
        mb_ky = [k for k, v in self.mbars.items() if v["selected"] is True]
        if len(mb_ky) > 0:
            return mb_ky[0]
        else:
            return None

    def click_mitem(self,
                    p_mouse_loc: tuple,
                    mb_ky: str):
        """ Return id if clicked on a menu item.
        - Only look at items in currently selected list of menu items
        - Ignore clicks on disabled menu items

        :attr:
        - p_mouse_loc: tuple of mouse location
        - mb_ky: id of currently selected menu bar
        :return:
        - (str) id of currrently selected menu item, else None
        """
        # Handle menu item click if a menu bar key was provided
        if mb_ky is None:
            return None
        else:
            # Set all menu items in the list to unselected
            for mi_ky in [k for k, v in self.mitems[mb_ky].items()]:
                self.mitems[mb_ky][mi_ky]["selected"] = False
            # See which, if any, menu item was clicked
            for mi_ky, mi_vals in self.mitems[mb_ky].items():
                if mi_vals['tbox'].collidepoint(p_mouse_loc):
                    # If it is enabled, set it to selected and others
                    # to unselected. Unselect the menu list.
                    if mi_vals["enabled"] is True:
                        self.mitems[mb_ky][mi_ky]["selected"] = True
                        self.mbars[mb_ky]["selected"] = False
                        for other_ky in\
                            [ky for ky in self.mitems[mb_ky].keys()
                            if ky != mi_ky]:
                                self.mitems[mb_ky][other_ky]["selected"] = False
            # Identify the the currently selected menu item
            mi_ky = [k for k, v in self.mitems[mb_ky].items()
                     if v["selected"] is True]
            if len(mi_ky) > 0:
                # Set enabled status of dependent menu items
                self.set_menu_items_state(mb_ky, mi_ky[0])
                return mi_ky[0]
            else:
                return None

    def draw_menu_bar(self):
        """ Draw a Menu Bar item.
        """
        for _, mb_vals in self.mbars.items():
            if mb_vals["selected"]:
                pg.draw.rect(PG.WIN, PG.PC_SILVER, mb_vals["box"], 2)
            else:
                pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, mb_vals["box"], 2)
            PG.WIN.blit(mb_vals["text"], mb_vals["tbox"])

    def draw_menu_items(self,
                        mb_ky):
        """ Draw the list of Menu Items.
        :attr:
        - mb_ky: key to the menu bar data
        """
        if self.mbars[mb_ky]["selected"] is True:
            # Draw container box
            pg.draw.rect(PG.WIN, PG.PC_GRAY_DARK,
                         self.mbars[mb_ky]["mlist_box"], 0)
            for mi_vals in self.mitems[mb_ky].values():
                # Draw each menu item in the selected list-box
                PG.WIN.blit(mi_vals["text"], mi_vals["tbox"])

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
         - Data state trackers = "post", like post-it notes, or
            like data that has been POSTed to a server.
         - etc.
        """
        self.divider = "-" * 16
        self.console = {"box": None,
                        "T": list()}
        # "D" = data outside a specific grid
        # "G" = grids, including a data record for each grid-square
        # "L" = lines
        self.map = {"box": None,
                    "D": dict(),
                    "G": dict(),
                    "L": dict()}
        self.post = {"active": False,
                     "catg": None,
                     "item": None}

        # Default grid and line dimensions.
        self.grid_tloff = {"x": 17, "y": 18}
        self.rows_cnt = 34
        self.cols_cnt = 44
        # Initialize methods...
        self.init_map_dims()
        self.init_grid_data()

    def init_map_dims(self):
        """
        Define static, default map dimensions.
        Add other dimensions as needed for zoom-in.
        Use default units (km, px, deg) here.
        Handle conversions elsewhere.
        px refers to the pygame drawing units.
        deg are + if N of eq, E of 'Greenwich';
                - if S of eq, W of 'Greenwich'.
        N.B.:
        For now, default scaling is hard-coded here.
        Will want to move that to a config file eventually.
        """
        # Default border box for game/map window.
        self.map["box"] = pg.Rect(PG.GAMEMAP["x"], PG.GAMEMAP["y"],
                                  PG.GAMEMAP["w"], PG.GAMEMAP["h"])
        # default PyGame 'pixels' per grid-square.
        self.grid_px_w = self.grid_px_h = 40
        self.line_px_w = self.grid_px_w * self.cols_cnt
        self.line_px_h = self.grid_px_h * self.rows_cnt
        # default kilometers per grid-square.
        self.grid_km_w = self.grid_km_h = 32.7775
        self.line_km_w = self.grid_km_w * self.cols_cnt
        self.line_km_h = self.grid_km_h * self.rows_cnt
        # Default grid line coordinates.
        self.map["L"] = {"rows": [], "cols": []}
        for r in range(self.rows_cnt + 1):
            x = self.grid_tloff["x"] + self.map["box"].x
            y = self.grid_tloff["y"]  + self.map["box"].y +\
                (r * self.grid_px_h)
            self.map["L"]["rows"].append(
                [(x, y), (x + self.line_px_w, y)])
        for c in range(self.cols_cnt + 1):
            x = self.grid_tloff["x"] + self.map["box"].x +\
                (c * self.grid_px_w)
            y = self.grid_tloff["y"] + self.map["box"].y
            self.map["L"]["cols"].append(
                [(x, y), (x, y + self.line_px_h)])

    def init_grid_data(self):
        """ Initialize a data record for each map grid.
        Store game data in the matrix of grids.
        Enhance using Pandas Dataframes, graphs, etc. as needed.
        Hi-level index within the "map" structure is "G", referring to
            "grid".
        Hi-level index within a ["G"] record is "id", referring to shape,
            location, and contents. May or may not be useful.
        Thinking that other sub-sets of data might be useful for
            tracking more dynamic data, such as:
            - what type of mode(s) are currently active in the grid
            - what avatars/objects are currently "in" the grid
            - info tags like resources, elevation, etc.
        This is just a starting point.
        Need to have enough data in each grid-record to be able to
            draw stuff relevant to that grid.

        @TODO:
        - Record the rect for each grid, so that we can draw it autonomously
          from the grid lines.
        """
        self.map["G"] = dict()
        for ci, ln_x in enumerate(self.map["L"]["cols"]):
            for ri, ln_y in enumerate(self.map["L"]["rows"]):
                self.map["G"][f"{str(ci).zfill(2)}_{str(ri).zfill(2)}"] = {
                    "id": f"col: {ci}, row: {ri}",
                    "box": pg.Rect((ln_x[0][0], ln_y[0][1]),
                                   (self.grid_px_w, self.grid_px_h))
                }

    def set_post(self,
                 p_post: dict):
        """Capture status settings, "posted" game data.
        Such as:
        - Key values pointing to data in JSON files, identifying what
          external data sets to retrieve, use.
        - Status information, such as:
            - Game is active
            - Game is paused
            - Game is over
            - Whose turn it is
        :args:
        - p_post (dict): name-value pairs of status settings to store
           in the class's "post" structure.
          Defaults:
            - "catg": name of category to load from JSON
            - "item": name of item to load from JSON
            - "active": boolean indicating whether a game is active
        """
        for k, v in p_post.items():
            self.post[k] = v

    def set_ln_attr_text(self,
                         p_attr: dict):
        """Use this function when the attribute contains a label (l)
          and name (n), and that is all we want to display. For example,
          this works for attributes like "type", ...
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_attr['label']}:")
        self.console["T"].append(f"  {p_attr['name']}")

    def set_lnt_attr_text(self,
                          p_attr: dict):
        """Use this function when the attribute contains a label (l),
          a name (n), and a type (t), and that's all we want to display.
        For example, this works for attributes like "contained_by", ...
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_attr['label']}:")
        self.console["T"].append(f"  {p_attr['name']} " +
                                 f"({p_attr['type']})")

    def set_names_text(self,
                       p_names: dict):
        """Use this function when the attribute is "name".
        There must be one value indexed by "common", plus optionally a set
        of names in different game languages or dialects.
        :attr:
        - p_data (dict): name-value pairs of names to format
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_names['label']}:")
        self.console["T"].append(f"  {p_names['common']}")
        if "other" in p_names.keys():
            for k, v in p_names["other"].items():
                self.console["T"].append(f"    {k}: {v}")

    def set_map_text(self,
                     p_map: dict):
        """Use this function when the attribute is "map".
        :attr:
        - p_data (dict): name-value pairs of map data to format
        """
        self.console["T"].append(self.divider)
        if "distance" in p_map.keys():
            d = p_map["distance"]
            self.console["T"].append(f"{d['label']}:")
            for a in ["height", "width"]:
                self.console["T"].append(f"  {d[a]['label']}:  " +
                                         f"{d[a]['amt']} {d['unit']}")
        if "location" in p_map.keys():
            l = p_map["location"]
            self.console["T"].append(f"{l['label']}:")
            for a in ["top", "bottom", "left", "right"]:
                self.console["T"].append(f"  {l[a]['label']}: " +
                                         f"{l[a]['amt']}{l['unit']}")

    def set_contains_text(self,
                          p_contains: dict):
        """Use this function when the attribute is "contains"."""
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_contains['label']}:")
        if "sub-region" in p_contains.keys():
            self.console["T"].append(f"  {p_contains['sub-region']['label']}:")
            for n in p_contains["sub-region"]["names"]:
                self.console["T"].append(f"    {n}")
        if "movement" in p_contains.keys():
            # roads, waterways, rivers and lakes
            self.console["T"].append(f"  {p_contains['movement']['label']}:")
            attr = {k:v for k, v in p_contains["movement"].items() if k != "label"}
            for _, v in attr.items():
                self.console["T"].append(f"    {v['label']}:")
                for n in v["names"]:
                    self.console["T"].append(f"      {n}")

    def set_console_text(self):
        """For .post item indexed by "catg", format a list of strings
            to render as text for display in Console.
        Store list of strings in console structure, under a key of "T".
        Source of config data to format is determined by value indexed by
            .post["catg"].
        Type of data to format is determined by value indexed by .post["item"]
        """
        self.console["box"] = pg.Rect(PG.CONSOLE["x"], PG.CONSOLE["y"],
                                      PG.CONSOLE["w"], PG.CONSOLE["h"])
        self.console["T"] = list()
        data = FI.S[self.post["catg"]][self.post["item"]]
        if "type" in data.keys():
            self.set_ln_attr_text(data["type"])
        if "contained_by" in data.keys():
            self.set_lnt_attr_text(data["contained_by"])
        if "name" in data.keys():
            self.set_names_text(data["name"])
        if "map" in data.keys():
            self.set_map_text(data["map"])
        if "contains" in data.keys():
            self.set_contains_text(data["contains"])

    def set_map_boundaries(self,
                           p_map: dict):
        """Set the boundaries of the map, based on the map data.
        - Fit the distance data for .post["item"] to default map scaling
        as defined in .init_map_dims(). For example:
        - Center the map within the grid N-S and E-W.
        - Draw boundaries of the map on top of the grid.
        - It may not align exactly to the grid, so this is "D" data.
        - For the grid records, indicate:
            - Is it inside, outside or on the boundary of .map["item"]

            # Default grid and line dimensions.
            self.grid_tloff = {"x": 17, "y": 18}
            self.rows_cnt = 34
            self.cols_cnt = 44
            # default PyGame 'pixels' per grid-square.
            self.grid_px_w = self.grid_px_h = 40
            self.line_px_w = self.grid_px_w * self.cols_cnt
            self.line_px_h = self.grid_px_h * self.rows_cnt
            # default kilometers per grid-square.
            self.grid_km_w = self.grid_km_h = 32.7775
            self.line_km_w = self.grid_km_w * self.cols_cnt
            self.line_km_h = self.grid_km_h * self.rows_cnt
        """
        # use topleft of the gird as the origin of the map, not tloff from tl of frame
        # that will be defined in .map["G"]['00_00')]
        # this is easier to read if I break out the math into separate steps
        grid_00 = {'x': self.map["G"]["00_00"]['box'].left,
                   'y': self.map["G"]["00_00"]['box'].top}
        map_km = {'w': p_map["distance"]["width"]["amt"],
                  'h': p_map["distance"]["height"]["amt"]}
        map_scale = {'w': map_km['w'] / self.line_km_w,
                     'h': map_km['h'] / self.line_km_h}
        map_px = {'w': map_scale['w'] * self.line_px_w,
                  'h': map_scale['h'] * self.line_px_h}
        map_grids = {'w': round(map_px['w'] / self.grid_px_w),
                     'h': round(map_px['h'] / self.grid_px_h)}
        map_offset = {'w': (self.cols_cnt - map_grids['w']) / 2,
                      'h': (self.rows_cnt - map_grids['h']) / 2}
        map_topleft = (grid_00["x"] + round((map_offset['w'] * self.grid_px_w), 2),
                       grid_00["y"] + round((map_offset['h'] * self.grid_px_h), 2))

        if map_km['h'] < self.line_km_h and map_km['w'] < self.line_km_w:
            map_ky =  self.post["item"]
            map_nm = FI.S[self.post["catg"]][map_ky]["name"]
            self.map["D"][map_ky] = {
                "box": pg.Rect(map_topleft, (map_px['w'], map_px['h'])),
                "grids": {
                    "cols": map_grids['w'],
                    "cols_offset": map_offset['w'],
                    "rows": map_grids['h']
                },
                "title": map_nm
            }
            # Next, determine:
            # - what grids are inside, outside or on the boundary of the item
            # - what colors to highight grids inside (fully or partially) the item boundary
            #    -- in other words, colors associated with various levels of mapping?
            # - where and how to display a key or legend for the title and km dimensions
            #   - maybe use fewer grid squares? ..
            #      -- leave room for legend and control widgets?
            #      -- or, use a separate window for that? some of the console perhaps?
            #      -- can I make the console scrollable/collapsable, like a browser?
            # - where and how to display descriptions on the map, options for that?
            # Test colorizing a specific grid -- maybe when it is clicked or scrolled over.
            #   -- First colorize grids inside the map boundary.

    def set_map_data(self):
        """Based on currently selected .post["catg"] and .post["item"],
            assign values to the .map["D"] or ["G"] attributes.
            .map["D"] is for data not confined to a specific grid
            .map["G"][col][row] is a matrix of data for each grid
            For default structure of the grid data record, see .init_grid_data()
        """
        data = FI.S[self.post["catg"]][self.post["item"]]
        if "map" in data.keys():
            self.set_map_boundaries(data["map"])

class GameConsole(object):
    """Define and handle the Game Consoled (info) window (rect).

    Display game data like score, etc.; and to contain text inputs.
    It is a rect within the Frame real estate, not a separate Frame object.
    """

    def __init__(self):
        """ Initialize GameConsole.
        """
        self.is_visible = False
        self.box = pg.Rect(PG.CONSOLE["x"], PG.CONSOLE["y"],
                           PG.CONSOLE["w"], PG.CONSOLE["h"])
        self.title = None
        self.text = None
        self.img = None
        WT.log("info", f"\nGameConsole instantiated: {str(self)}",
               __file__, __name__, self, sys._getframe())

    def set_console_text_line(self,
                              p_lnno: int,
                              p_text: str):
        """ Set a line of text to display in the GameConsole rect.
        :args:
        - p_lnno: (int) Line number of text to display.
        - p_text: (str) Text to display in line.
        """
        self.img = PG.F_SANS_SM.render(p_text, True,
                                        PG.PC_BLUEPOWDER,
                                        PG.PC_BLACK)
        self.text = self.img.get_rect()
        y = self.title.y + MED_FONT_SZ
        self.text.topleft = (self.title.x,
                             y + ((SM_FONT_SZ + 2) * (p_lnno + 1)))

    def draw(self):
        """ Draw GameConsole.
        - Black out the GameConsole rect.
        - Draw the console header.
        - Incrementally add lines text (or inputs) to GameConsole
          region based on current posting in GameData object.
        """
        # Draw console container rect.
        pg.draw.rect(PG.WIN, PG.PC_BLUE, GDAT.console["box"], 1)
        # Set and draw console header.
        self.img = PG.F_SANS_LG.render(PG.CONSOLE["ttl"], True,
                                       PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.title = self.img.get_rect()
        self.title.topleft = (PG.CONSOLE["x"] + 5,
                              PG.CONSOLE["y"] + 5)
        PG.WIN.blit(self.img, self.title)
        # Set and draw lines of text, as defined in GameData object.
        for i, ln in enumerate(GDAT.console["T"]):
           self.set_console_text_line(i, ln)
           PG.WIN.blit(self.img, self.text)


class GameMap(object):
    """Define and handle the Game GUI window (rect).

    Display the map, scenes, game widgets, GUI controls.
    It is a rect within the Frame real estate, not a separate Frame object."""

    def __init__(self):
        """Initialize GameMap"""
        self.is_visible = False
        self.box = pg.Rect(PG.GAMEMAP["x"], PG.GAMEMAP["y"],
                           PG.GAMEMAP["w"], PG.GAMEMAP["h"])
        WT.log("info", f"\nGameMap initialized: {str(self)}",
               __file__, __name__, self, sys._getframe())

    def draw(self):
        """Draw the Game map.
        draw(surface, color, coordinates, width)

        Define additional types of structures as needed. e.g., graphs, etc.
        """
        # Draw map container rect and grid lines ("L" data)
        pg.draw.rect(PG.WIN, PG.PC_SILVER, self.box, 5)
        for gline in GDAT.map["L"]["rows"]:
            pg.draw.aalines(PG.WIN, PG.PC_WHITE, False, gline)
        for gline in GDAT.map["L"]["cols"]:
            pg.draw.aalines(PG.WIN, PG.PC_WHITE, False, gline)
        # Draw map boundaries, title, etc. ("D" data)
        for _, v in GDAT.map["D"].items():
            pg.draw.rect(PG.WIN, PG.PC_PALEPINK, v["box"], 5)

    def draw_grid(self, rc):
        """Highlight a particular grid.
        """
        if rc != "":
            pg.draw.rect(PG.WIN, PG.PC_PALEPINK, GDAT.map["G"][rc]["box"], 0)


class InfoBar(object):
    """Info Bar object.
    Deafault text is system info.
    To change text, call GameData.set_console_text() function.
    """
    def __init__(self):
        """ Initialize Info Bar. """
        self.info_status = {
            "on": False,
            "frozen": True,
            "frame_cnt": 0,
            "mouse_loc": (0, 0),
            "grid_loc": ""}
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
        Set and draw the Info Bar text.
        Optionally include status info if the class's info_status["on"]
            attribute is True.
        """
        text = self.system_text + "   | " + self.status_text\
            if self.info_status["on"] is True else self.system_text
        self.itxt = PG.F_SANS_SM.render(text, True, PG.PC_BLUEPOWDER,
                                        PG.PC_BLACK)
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
        """
        N.B.
        All of the major classes are instantiated in the main module
        prior to instantiating the SaskanGame class.

        Initialize in-game keyboard usage. (Modify as needed.)
        Execute the main event loop.
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

    def handle_menu_item_click(self,
                          mb_ky,
                          p_mi_ky):
        """Trigger an event based on menu item selection.

        :args:
        - p_mbar: (str or None) menu item key
        - p_mitem: (str or None )menu item key
        """
        # ==============================================================
        msg = f"\nMenu item clicked: {mb_ky}, {p_mi_ky}, {GMNU.mbars[mb_ky]}, " +\
              f"{GMNU.mitems[mb_ky][p_mi_ky]}"
        WT.log("info", msg, __file__, __name__, self, sys._getframe())
        # ==============================================================
        if p_mi_ky == "exit":
            self.exit_appl()
        elif "help" in p_mi_ky:
            if p_mi_ky == "pg_help":
                WHTM.draw(PG.PHELP["pygame"])
            elif p_mi_ky == "app_help":
                WHTM.draw(PG.PHELP["app"])
            elif p_mi_ky == "game_help":
                WHTM.draw(PG.PHELP["game"])
        elif p_mi_ky == "start":
            GDAT.set_post({"catg": 'geo',
                           "item": 'Saskan Lands',
                           "active": True})
            CONSOLE.is_visible = True
            GAMEMAP.is_visible = True
            GDAT.set_console_text()
            GDAT.set_map_data()
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
        IBAR.info_status["grid_loc"] = ""
        for i, r in enumerate(GDAT.map["L"]["rows"]):
            if IBAR.info_status["mouse_loc"][1] >= r[0][1] and\
               IBAR.info_status["mouse_loc"][1] <= r[0][1] + GDAT.grid_px_h:
                grid_r = i + 1
                break
        for i, c in enumerate(GDAT.map["L"]["cols"]):
            if IBAR.info_status["mouse_loc"][0] >= c[0][0] and\
               IBAR.info_status["mouse_loc"][0] <= c[0][0] + GDAT.grid_px_w:
                grid_c = i + 1
                break
        if grid_r > 0 and grid_c > 0:
            IBAR.info_status["grid_loc"] =\
                f"{str(grid_c - 1).zfill(2)}_{str(grid_r - 1).zfill(2)}"

    def track_state(self):
        """Keep track of the state of the app on each frame.

        Sets:
        - mouse_loc: get current mouse location
        - frame_cnt: increment if tracking status and not in a freeze mode
        - cursor: if no text input box is activated, set to default
        """
        if GDAT.post["active"]:
            IBAR.info_status["on"] = True
        if IBAR.info_status["on"] is True and\
            IBAR.info_status["frozen"] is False:
                IBAR.info_status["frame_cnt"] += 1

        IBAR.info_status["mouse_loc"] = pg.mouse.get_pos()
        if GAMEMAP.is_visible:
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
        # display content based on what is currently
        #  posted in the GameData object
        if CONSOLE.is_visible is True:
            CONSOLE.draw()
        if IBAR.info_status["on"] is True:
            IBAR.set_status_text()
        else:
            IBAR.set_default_text()
        IBAR.draw()
        if GAMEMAP.is_visible is True:
            GAMEMAP.draw()
            GAMEMAP.draw_grid(IBAR.info_status["grid_loc"])

        # for txtin in self.TIG:
        #     txtin.draw()
        # self.PAGE.draw()

        # refresh the menus
        GMNU.draw_menu_bar()
        for mb_ky, mi_ky in GMNU.mitems.items():
            GMNU.draw_menu_items(mb_ky)

        pg.display.update()
        PG.TIMER.tick(30)

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
        # ==============================================================
        WT.log("info", "\nevent loop launched",
               __file__, __name__, self, sys._getframe())
        # ==============================================================
        while True:
            # Get mouse_loc and frame_cnt
            self.track_state()

            for event in pg.event.get():

                # Handle keyboard quit events (ESC or Q)
                self.check_exit_appl(event)

                # Handle mouse click events
                if event.type == pg.MOUSEBUTTONDOWN:

                    # Handle menu-bar click
                    mb_ky = GMNU.click_mbar(IBAR.info_status["mouse_loc"])
                    # Handle menu-item click
                    mi_ky = GMNU.click_mitem(IBAR.info_status["mouse_loc"], mb_ky)
                    if mi_ky is not None:
                       self.handle_menu_item_click(mb_ky, mi_ky)

                    # Handle text input events
                    # Will be mainly on the console window I think
                    # self.do_select_txtin(sIBAR.info_status["mouse_loc"])

                    # Handle game-window click events

            self.refresh_screen()


if __name__ == '__main__':
    """Cache data and resources in memory and launch the app."""

    FI.pickle_saskan(path.join("/home", Path.cwd().parts[2], FI.D['APP']))
    # ====================================================
    WT.log("info", "\ndev/shm cache created",
            __file__, __name__, None, sys._getframe())
    # ====================================================
    GDAT = GameData()
    GMNU = GameMenu()
    WHTM = HtmlDisplay()  # for Help windows
    IBAR = InfoBar()
    CONSOLE = GameConsole()
    GAMEMAP = GameMap()
    SaskanGame()
