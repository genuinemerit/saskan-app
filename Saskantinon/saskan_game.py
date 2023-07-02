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
+ Display console data.

- Extend regions metadata (JSON) and code to support drawing high-level box (map) borders.
- Load schema data for Saskan Lands.
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

from copy import copy
from dataclasses import dataclass
from os import path
from pathlib import Path
from pprint import pprint as pp     # noqa: F401
from pygame.locals import *

from io_file import FileIO          # type: ignore
from io_wiretap import WireTap      # type: ignore
from saskan_math import SaskanRect  # type: ignore

FI = FileIO()
SR = SaskanRect()
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
    # In-game "windows" = CONSWIN*, GRIDWIN*, IBAR*, PHELP*
    CONSWIN = FI.G["game_windows"]["info"]
    GRIDWIN = FI.G["game_windows"]["game"]
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
        self.draw_menu_bar()
        for mb_ky in self.mitems.keys():
            self.draw_menu_items(mb_ky)
        # ==============================================================
        # msg = f"\nGameMenu initialized: {self}"
        # WT.log("info", msg, __file__, __name__, self, sys._getframe())
        # ==============================================================

    def set_menu_bar(self):
        """Set up the menu bar.
        Instantiate MenuBar and add to the object.
        """
        self.mbars =\
            {ky: {"nm": val["nm"]} for ky, val in FI.G[MENUS]["menu"].items()}
        # initialize prev_x to left edge of menu bar per config
        x = PG.MBAR_X
        for mb_ky, attrs in self.mbars.items():
            self.mbars[mb_ky] =\
                {"nm": attrs["nm"],
                 "mb_text": PG.F_SANS_SM.render(attrs["nm"], True,
                            PG.PC_BLUEPOWDER, PG.PC_GRAY_DARK),
                 "selected": False}
            self.mbars[mb_ky]["mt_box"] =\
                self.mbars[mb_ky]["mb_text"].get_rect()
            self.mbars[mb_ky]["mb_box"] =\
                pg.Rect((x, PG.MBAR_Y),
                        (PG.MBAR_W, PG.MBAR_H + (PG.MBAR_MARGIN * 2)))
            x = self.mbars[mb_ky]["mb_box"].right
            self.mbars[mb_ky]["mt_box"].left =\
                self.mbars[mb_ky]["mb_box"].left +\
                    (self.mbars[mb_ky]["mb_box"].width / 2) - 12
            self.mbars[mb_ky]["mt_box"].top =\
                self.mbars[mb_ky]["mb_box"].top + PG.MBAR_MARGIN + 5

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
            self.mitems[mb_ky][mi_ky]["mi_text"] =\
                PG.F_SANS_SM.render(self.mitems[mb_ky][mi_ky]["nm"],
                                    True, txt_color, PG.PC_GRAY_DARK)
        else:
            # Default selected item to enabled status
            self.mitems[mb_ky][mi_ky]["enabled"] = True
            self.mitems[mb_ky][mi_ky]["mi_text"] =\
                PG.F_SANS_SM.render(self.mitems[mb_ky][mi_ky]["nm"],
                                    True, PG.PC_BLUEPOWDER, PG.PC_GRAY_DARK)
            # Identify dependent menu items and modify their enabled status
            if "disable" in list(self.mitems[mb_ky][mi_ky].keys()):
                for dep_ky in self.mitems[mb_ky][mi_ky]["disable"]:
                    self.mitems[mb_ky][dep_ky]["enabled"] = False
                    self.mitems[mb_ky][dep_ky]["mi_text"] =\
                        PG.F_SANS_SM.render(self.mitems[mb_ky][dep_ky]["nm"],
                                            True, PG.PC_GRAY, PG.PC_GRAY_DARK)
            if "enable" in list(self.mitems[mb_ky][mi_ky].keys()):
                for dep_ky in self.mitems[mb_ky][mi_ky]["enable"]:
                    self.mitems[mb_ky][dep_ky]["enabled"] = True
                    self.mitems[mb_ky][dep_ky]["mi_text"] =\
                        PG.F_SANS_SM.render(self.mitems[mb_ky][dep_ky]["nm"],
                                            True, PG.PC_BLUEPOWDER,
                                            PG.PC_GRAY_DARK)

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
                left = self.mbars[mb_ky]["mb_box"].left
                top = self.mbars[mb_ky]["mb_box"].bottom
                self.mbars[mb_ky]["mlist_box"] =\
                    pg.Rect((left, top), (PG.MBAR_W, 0))
            # Set up each menu item:
            mi_x = 0
            for mi_ky, mi_vals in mlist.items():
                # Set status flags
                self.mitems[mb_ky][mi_ky]["selected"] = False
                self.set_menu_items_state(mb_ky, mi_ky, p_use_default=True)
                # Set text box
                text_width = self.mitems[mb_ky][mi_ky]["mi_text"].get_width()
                left = self.mbars[mb_ky]["mb_box"].left + (PG.MBAR_MARGIN * 4)
                top = self.mbars[mb_ky]["mb_box"].bottom +\
                    (PG.MBAR_H * mi_x) + PG.MBAR_MARGIN
                width = text_width + (PG.MBAR_MARGIN * 2)
                self.mitems[mb_ky][mi_ky]["mit_box"] =\
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
            if mb_vals["mb_box"].collidepoint(p_mouse_loc):
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
        if mb_ky is None:
            return None
        else: # if a menu bar key was provided
            # Set all menu items in the list to unselected
            for mi_ky in [k for k, v in self.mitems[mb_ky].items()]:
                self.mitems[mb_ky][mi_ky]["selected"] = False
            # See which, if any, menu item was clicked
            for mi_ky, mi_vals in self.mitems[mb_ky].items():
                if mi_vals['mit_box'].collidepoint(p_mouse_loc):
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
                pg.draw.rect(PG.WIN, PG.PC_SILVER, mb_vals["mb_box"], 2)
            else:
                pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, mb_vals["mb_box"], 2)
            PG.WIN.blit(mb_vals["mb_text"], mb_vals["mt_box"])

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
                PG.WIN.blit(mi_vals["mi_text"], mi_vals["mit_box"])

class HtmlDisplay(object):
    """Set content for display in external web browser.
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
        self.t_rect = SR.make_rect(p_y, p_x, p_w, p_h)
        self.t_box = self.t_rect["box"]
        self.t_value = ""
        self.t_font = PG.F_FIXED_LG
        self.t_color = PG.PC_GREEN
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
            pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, self.t_box, 2)
        else:
            pg.draw.rect(PG.WIN, PG.PC_BLUE, self.t_box, 2)
        PG.WIN.blit(self.text, self.pos)


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


class GameData(object):
    """Retrieve static game data from JSON and image file(s).
    Organize it into data structures for use by game console and grid.
    `console`, `con`, `conswin` refer to the text-based console "window".
    `grid_window` `gridwin` refer to the game map "window".
    `grid` refers to matrix inside the grid window.
    `controls` (not defined yet) refers to GUI controls inside gridwin.
    `map` refers to data that has been mapped to the grid and
      is ready for display within / on top of the matrix.

    @DEV:
    - Consider how to handle layers of data, e.g. on a map, or
      in a scene, so that zoom-in, zoom-out, and other views
      can be handled without having to re-read the data.
    - Work on mapping data for a zoomed-in region, like a town and environs.
        Then for a scene, like a building, or a room.
    - Consider where to provide screen real estate for GUI controls like
      scroll, zoom, pan, select-move and so on.
        - Those things may not be part of this class, but will interact.
    """
    def __init__(self):
        """Initialize Game Data structures
         - Geographical map(s)
         - Data state trackers = "post", like post-it notes, or
            like data that has been POSTed to a server.
        @DEV:
         - Event drivers
         - Star map(s)
         - etc.
        """
        self.divider = "-" * 16
        # Currently loaded map data
        self.post = {"active": False,
                     "catg": None,
                     "item": None}
        # Currently loaded console
        self.console = {"is_visible": False,
                        "con_box": None,
                        "T": list(),
                        "t_img": list(),
                        "t_box": list()
                        }
        # Currently loaded grid
        # "D" = data outside a specific grid
        # "G" = grids matrix, with data record for each grid-square
        # "L" = lines
        self.grid = {"D": dict(),    # data outside a specific grid
                     "L": dict(),    # lines
                     "G": dict()}    # grid matrix, grid-square data recs}
        # Default grid and line dimensions.
        self.init_grid_d()
        self.init_grid_l()
        self.init_grid_g()

    # helper set and make methods
    # ==============================
    def make_grid_key(self,
                      p_col : int,
                      p_row: int) -> str:
        """Convert integer coordinates to string key
           for use in the .grid["G"] (grid data) matrix.
        :args:
        - p_col: int, column number
        - p_row: int, row number
        :returns:
        - str, key for specific grid-square record, in "0n_0n" format
        """
        return f"{str(p_col).zfill(2)}_{str(p_row).zfill(2)}"

    def set_post(self,
                 p_post: dict):
        """Capture status settings, "posted" game data.
        Such as Key values pointing to data in JSON files
        :args:
        - p_post (dict): name-value pairs for class .post structure.
          Defaults:
            - "catg": name of category to load from JSON
            - "item": name of item to load from JSON
            - "active": boolean indicating whether gamewin is active
        """
        for k, v in p_post.items():
            self.post[k] = v

    # gridwin initialization methods
    # ==============================
    def init_grid_d(self):
        """
        Define containing dimensions for the "D" matrix.
        Define sizing of grid and its offset from gridwin.
        Associate pygame px and km with grid dimensions.
        - Set border box for gridwin.
        - Set grid offset from gridwin.
        - Set number of grid rows, cols.
        - Set px and km per grid-square.
        For conversions to other units, use SaskanMath class.
        - px refers to the pygame drawing units.
        @DEV:
        - May add other dimensions as needed for zoom-in.
        - For now, default scaling is hard-coded here.
          Let's move that to a config file eventually.
        """
        self.grid["D"] = {
            "is_visible": False,
            "grid_rect": SR.make_rect(PG.GRIDWIN["y"], PG.GRIDWIN["x"],
                                      PG.GRIDWIN["w"], PG.GRIDWIN["h"])}
        self.grid["D"]["grid_box"] = self.grid["D"]["grid_rect"]["box"]
        # TopLeft offset from gridwin to grid:
        self.grid["D"]["offset"] = {"x": 17, "y": 18}
        # Sizing of the matrix and of individual grid-squares:
        self.grid["D"]["dim"] = {
            "rows": 34,
            "cols": 44,
            "px": {"w": 40, "h": 40},
            "km": {"w": 32.7775, "h": 32.7775}}

    def init_grid_l(self):
        """
        Define dimensions for the "L" (lines) matrix.
        """
        grid_d = self.grid["D"]
        d_dim = grid_d["dim"]
        self.grid["L"]["dim"] = {
            "vert_lns": d_dim["cols"] + 1,
            "horz_lns": d_dim["rows"] + 1,
            "px": {"w": d_dim["px"]["w"] * d_dim["cols"],
                   "h": d_dim["px"]["h"] * d_dim["rows"]},
            "km": {"w": d_dim["km"]["w"] * d_dim["cols"],
                   "h": d_dim["km"]["h"] * d_dim["rows"]}}

        # Set horiztonal line segment x,y coordinates.
        self.grid["L"]["horz_ln"] = list()
        left_x = grid_d["offset"]["x"] + grid_d["grid_box"].x
        right_x = left_x + (d_dim["px"]["w"] * d_dim["cols"])
        for hz in range(self.grid["L"]["dim"]["horz_lns"]):
            y = grid_d["offset"]["y"]  + grid_d["grid_box"].y +\
                (hz * d_dim["px"]["h"])
            self.grid["L"]["horz_ln"].append([(left_x, y), (right_x, y)])

        # Set vertical line segment x,y coordinates.
        self.grid["L"]["vert_ln"] = list()
        top_y = grid_d["offset"]["y"]  + grid_d["grid_box"].y
        bottom_y = top_y + (d_dim["px"]["h"] * d_dim["rows"])
        for vt in range(self.grid["L"]["dim"]["vert_lns"]):
            x = grid_d["offset"]["x"]  + grid_d["grid_box"].x +\
                (vt * d_dim["px"]["w"])
            self.grid["L"]["vert_ln"].append([(x, top_y), (x, bottom_y)])

    def init_grid_g(self):
        """ Define in "G" matrix a data record for each grid-square.
        - Define a rect and box for each grid-square.
        """
        for c in range(0, self.grid["D"]["dim"]["cols"]):
            for r in range(0, self.grid["D"]["dim"]["rows"]):
                g_ky = self.make_grid_key(c, r)
                x = self.grid["L"]["vert_ln"][c][0][0]  # x of vert line
                y = self.grid["L"]["horz_ln"][r][0][1]  # y of horz line
                w = self.grid["D"]["dim"]["px"]["w"]    # width of a grid-square
                h = self.grid["D"]["dim"]["px"]["h"]    # height of a grid-square
                self.grid["G"][g_ky] = {"g_rect": copy(SR.make_rect(y, x, w, h))}
                self.grid["G"][g_ky]["g_box"] = self.grid["G"][g_ky]["g_rect"]["box"]

    # console methods
    # =============================
    def set_t_lbl_nm(self,
                     p_attr: dict):
        """Attribute contains a label (l) and name (n),
           and that is all we want to display.
           For example, attributes like "type", ...
        :attr:
        - p_attr (dict): name-value pairs to format
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_attr['label']}:")
        self.console["T"].append(f"  {p_attr['name']}")

    def set_t_lbl_nm_typ(self,
                         p_attr: dict):
        """Attribute contains a label (l), a name (n), and a type (t),
        and that's all we want to display.
        For example, attributes like "contained_by", ...
        :attr:
        - p_attr (dict): name-value pairs to format
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_attr['label']}:")
        self.console["T"].append(f"  {p_attr['name']} " +
                                 f"({p_attr['type']})")

    def set_t_proper_names(self,
                           p_names: dict):
        """Attribute is "name", referring to proper names of things.
        Must be one value indexed by "common"; optionally a set
        of names in different game languages or dialects.
        :attr:
        - p_names (dict): name-value pairs to format
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_names['label']}:")
        self.console["T"].append(f"  {p_names['common']}")
        self.set_console_header(p_names['common'])
        if "other" in p_names.keys():
            for k, v in p_names["other"].items():
                self.console["T"].append(f"    {k}: {v}")

    def set_t_map(self,
                  p_map: dict):
        """Attribute is "map", referring to game-map data.
        :attr:
        - p_map (dict): name-value pairs to format
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

    def set_t_contains(self,
                       p_contains: dict):
        """Attribute is "contains", referring to things contained by an object.
        :attr:
        - p_contains (dict): name-value pairs to format
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_contains['label']}:")
        if "sub-region" in p_contains.keys():
            self.console["T"].append(
                f"  {p_contains['sub-region']['label']}:")
            for n in p_contains["sub-region"]["names"]:
                self.console["T"].append(f"    {n}")
        if "movement" in p_contains.keys():
            # roads, waterways, rivers and lakes
            self.console["T"].append(
                f"  {p_contains['movement']['label']}:")
            attr = {k:v for k, v in p_contains["movement"].items()
                    if k != "label"}
            for _, v in attr.items():
                self.console["T"].append(f"    {v['label']}:")
                for n in v["names"]:
                    self.console["T"].append(f"      {n}")

    def render_text_lines(self):
        """ Render lines of text to display in the GameConsole rect.
        Store rendered text objects in .console["T"] structure.
        """
        x = self.console["title"]["box"].x
        y = self.console["title"]["box"].y + MED_FONT_SZ
        for i, c_txt in enumerate(self.console["T"]):
            self.console["t_img"].append(
                PG.F_SANS_SM.render(c_txt, True, PG.PC_BLUEPOWDER,
                                    PG.PC_BLACK))
            self.console["t_box"].append(
                self.console["t_img"][i].get_rect())
            self.console["t_box"][i].topleft =\
                (x, y + ((SM_FONT_SZ + 2) * (i + 1)))

    def set_console_header(self,
                           p_hdr_text: str):
        """Render header string for display in console."""
        self.console["title"] = {"text": p_hdr_text}
        self.console["title"]["img"] = PG.F_SANS_LG.render(
            self.console["title"]["text"], True, PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.console["title"]["box"] =\
            self.console["title"]["img"].get_rect()
        self.console["title"]["box"].topleft =\
            (PG.CONSWIN["x"] + 5, PG.CONSWIN["y"] + 5)

    def set_console_text(self):
        """Format a list of strings to render as text for display in console.
        Store list of strings in the .console["T"] structure.
        .post["catg"] identifies source of config data to format.
        .post["item"] identifies type of data to format.
        """
        self.console["is_visible"] = True
        self.console["con_rect"] = SR.make_rect(PG.CONSWIN["y"], PG.CONSWIN["x"],
                                   PG.CONSWIN["w"], PG.CONSWIN["h"])
        self.console["con_box"] = self.console["con_rect"]["box"]
        self.console["T"] = list()
        self.set_console_header(PG.CONSWIN["ttl"])
        # Contents
        con_data = FI.S[self.post["catg"]][self.post["item"]]
        if "type" in con_data.keys():
            self.set_t_lbl_nm(con_data["type"])
        if "contained_by" in con_data.keys():
            self.set_t_lbl_nm_typ(con_data["contained_by"])
        if "name" in con_data.keys():
            self.set_t_proper_names(con_data["name"])
        if "map" in con_data.keys():
            self.set_t_map(con_data["map"])
        if "contains" in con_data.keys():
            self.set_t_contains(con_data["contains"])
        self.render_text_lines()

    # set map dimensions and content
    # ================================
    def set_map_dim(self,
                    p_map: dict):
        """Set dimensions of current map within the grid.
        - Scale .post["item"] type data to grid default dims.
        For example:
        - Center the selected map within the grid N-S and E-W.
        - Draw boundaries of the map on top of the grid and store
          as .grid["D"] data.
        - Indicate if each grid-square is inside, outside or crossing
          the map boundaries. Store as .grid["G"] data.
        N.B.
        - Topleft of grid (not gridwin) is origin for map.
        - Easier to read math broken into separate steps, rather than
          one big function.
        :attr:
        - p_map (dict): game map name-value pairs from geo config data
            For example, data for the "Saskan Lands" region.
        @DEV:
        - What to do if the map data defines an area larger than the grid?

        # Next, determine:
        # - what grids are inside, outside or on the boundary of the item
        #   -- need something like a collider algorithm for that
        #   -- start simple, with rectangles
        #   -- then, add more complex shapes
        #   -- then, add more complex shapes with holes
        #   -- then, add more complex shapes with holes and islands
        #   -- then, add more complex shapes with holes and islands and tunnels
        #   -- and so on... probably want to use a library before too long
        #      but want to get a feel for the math first

        # For each grid, do a collision check with the dimensions of the item boundary.

        # - where to store that info (most likely in the grid records)
        # - what colors to highight grids inside (fully or partially) the item boundary
        #    -- in other words, colors associated with various levels of mapping?

        # - where and how to display a key or legend for the title and km dimensions
        #   - maybe use fewer grid squares? ..
        #      -- leave room for legend and control widgets?
        #      -- or, use a separate window for that? some of the console perhaps?
        #      -- can I make the console scrollable/collapsable, like a browser?

        # - where and how to display descriptions on the map, options for that?
        #   -- First colorize grids inside the map boundary.
        """
        grid_l = self.grid["L"]["dim"]
        grid_d = self.grid["D"]["dim"]
        grid_origin = {'x': self.grid["G"]["00_00"]['g_box'].left,
                       'y': self.grid["G"]["00_00"]['g_box'].top}

        map_km = {'w': p_map["distance"]["width"]["amt"],
                  'h': p_map["distance"]["height"]["amt"]}
        # Ratio of map width, height to grid-line width, height
        map_scale = {'w': map_km['w'] / grid_l["km"]["w"],
                     'h': map_km['h'] / grid_l["km"]["h"]}
        map_px = {'w': map_scale['w'] * grid_l["px"]["w"],
                  'h': map_scale['h'] * grid_l["px"]["h"]}
        # Compute number of grid squares that fit in the map
        map_grids = {'w': round(map_px['w'] / grid_d["px"]["w"]),
                     'h': round(map_px['h'] / grid_d["px"]["h"])}
        # Compute offset to center the map in the grid; by grid count, by pixels
        map_offset = {'w': (grid_d["cols"] - map_grids['w']) / 2,
                      'h': (grid_d["rows"] - map_grids['h']) / 2}
        map_left = (grid_origin["x"] +
                    round((map_offset['w'] *
                           grid_d["px"]["w"]), 2))
        map_top = (grid_origin["y"] +
                   round((map_offset['h'] *
                          grid_d["px"]["h"]), 2))
        # Define rect and box for the map
        if map_km['h'] < grid_l["km"]["h"] and\
           map_km['w'] < grid_l["km"]["w"]:
                self.grid["D"]["map"] = {
                    "item_ky": self.post["item"],
                    "item_nm": FI.S[self.post["catg"]][self.post["item"]]["name"],
                    "m_rect": SR.make_rect(map_top, map_left, map_px['w'], map_px['h'])}
                self.grid["D"]["map"]["m_box"] = self.grid["D"]["map"]["m_rect"]["box"]
        # Do a collision check between the map box and each grid box
        for gk, grec in GDAT.grid["G"].items():
            self.grid["G"][gk]["is_inside"] = False
            self.grid["G"][gk]["overlaps"] = False
            if SR.rect_contains(self.grid["D"]["map"]["m_box"], grec["g_box"]):
                self.grid["G"][gk]["is_inside"] = True
            elif SR.rect_overlaps(self.grid["D"]["map"]["m_box"], grec["g_box"]):
                self.grid["G"][gk]["overlaps"] = True

    def set_map_data(self):
        """Based on currently selected .post["catg"] and .post["item"],
            assign values to the .grid["D"] or ["G"] attributes.
            .grid["D"] is for data not confined to a specific grid
            .grid["G"][col_row] is a matrix of data for each grid
            For default structure of the grid data record, see .init_grid_data()
        @TODO:
        - For now just set the map dimensions and scaling it to the grid.
        - Next, start defining map content into the grid ("G").
        """
        self.grid["D"]["is_visible"] = True
        data = FI.S[self.post["catg"]][self.post["item"]]
        if "map" in data.keys():
            self.set_map_dim(data["map"])

class GameConsole(object):
    """Draw the Game Consoled (info) window (rect).
    Display game data like score, map descriptions, etc.
    It is a rect within the Frame, not a separate Frame object.
    N.B.:
    - GameData class does data load and rendering stored in "T" matrix.
    @DEV:
    - May extend the console to handle text input fields.
    """

    def __init__(self):
        """ Initialize GameConsole.
        """
        pass

    def draw(self):
        """ Draw GameConsole.
        - Draw the GameConsole rect.
        - Draw the console header.
        - Draw text lines for GameConsole based on current GameData.
        """
        # Draw container rect and header.
        pg.draw.rect(PG.WIN, PG.PC_BLACK, GDAT.console["con_box"], 0)
        PG.WIN.blit(GDAT.console["title"]["img"],
                    GDAT.console["title"]["box"])
        # Draw lines of text, as rendered in GameData object.
        for i, _ in enumerate(GDAT.console["T"]):
           PG.WIN.blit(GDAT.console["t_img"][i],
                       GDAT.console["t_box"][i])


class GameMap(object):
    """Define and handle the Game GUI window (rect).
    Draw the grid, the map, and (eventually) scenes, game widgets,
    GUI controls and so on mapped to the grid.

    This class use sdata stored in the GameData object.
    """

    def __init__(self):
        """Initialize GameMap"""
        pass

    def draw(self):
        """Draw the Game map.
        draw(surface, color, coordinates, width)
        """
        # Draw grid box with thick border
        pg.draw.rect(PG.WIN, PG.PC_SILVER, GDAT.grid["D"]["grid_box"], 5)
        # Draw grid lines
        for vt in GDAT.grid["L"]["vert_ln"]:
            pg.draw.aalines(PG.WIN, PG.PC_WHITE, False, vt)
        for hz in GDAT.grid["L"]["horz_ln"]:
            pg.draw.aalines(PG.WIN, PG.PC_WHITE, False, hz)
        # Highlight grid squares inside or overlapping the map box
        for gk, grec in GDAT.grid["G"].items():
            if grec["is_inside"]:
                pg.draw.rect(PG.WIN, PG.PC_WHITE, grec["g_box"], 0)
            elif grec["overlaps"]:
                pg.draw.rect(PG.WIN, PG.PC_SILVER, grec["g_box"], 0)
        # Draw map box with thick border
        pg.draw.rect(PG.WIN, PG.PC_PALEPINK, GDAT.grid["D"]["map"]["m_box"], 5)

    def draw_grid(self, grid_loc: str):
        """For now, just highlight/ colorized a grid-square.
        The INFOBAR object stores a "grid_loc" value indicating
        what grid the cursor is presently hovering over. When this
        method is called from refesh_screen(), it passes that key
        in the grid_loc argument.
        :args:
        - grid_loc: (str) Column/Row key of grid to highlight,
            in "0n_0n" (col, row) format, using leading zeros.

        @DEV:
        - Provide options for highlighting in different ways.
        - Pygame colors can use an alpha channel for transparency, but..
            - See: https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame
            - Transparency is not supported directly by draw()
            - Achieved using Surface alpha argument with blit()
        """
        if grid_loc != "":
            pg.draw.rect(PG.WIN, PG.PC_PALEPINK,
                GDAT.grid["G"][grid_loc]["g_box"], 0)


class InfoBar(object):
    """Info Bar object.
    Deafault text is system info.
    Show status text if it is turned on.
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
        Just rendering the text here since the status info can change
            every frame.
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
            GDAT.set_console_text()
            GDAT.set_map_data()
        elif p_mi_ky == "status":
            IBAR.info_status["on"] = not IBAR.info_status["on"]
        elif p_mi_ky == "pause_resume":
            IBAR.info_status["frozen"] = not IBAR.info_status["frozen"]

    # Loop Events
    # ==============================================================
    def track_grid(self):
        """Keep track of what grid mouse is over.
        Use "L" (lines) data to ID grid loc. Maybe a little
            faster than parsing thru each element of .grid["G"] matrix.

        N.B.:
        Since "L" defines lines, it has a count one greater than # of
          grids in each row or column.
        """
        mouse_loc = IBAR.info_status["mouse_loc"]
        IBAR.info_status["grid_loc"] = ""
        grid_col = -1
        for i in range(0, GDAT.grid["D"]["dim"]["cols"]):
            vt = GDAT.grid["L"]["vert_ln"][i]
            if mouse_loc[0] >= vt[0][0] and\
               mouse_loc[0] <= vt[0][0] + GDAT.grid["D"]["dim"]["px"]["w"]:
                    grid_col = i
                    break
        grid_row = -1
        for i in range(0, GDAT.grid["D"]["dim"]["rows"]):
            hz = GDAT.grid["L"]["horz_ln"][i]
            if mouse_loc[1] >= hz[0][1] and\
               mouse_loc[1] <= hz[0][1] + GDAT.grid["D"]["dim"]["px"]["h"]:
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
        if GDAT.post["active"]:
            IBAR.info_status["on"] = True
        if IBAR.info_status["on"] is True and\
            IBAR.info_status["frozen"] is False:
                IBAR.info_status["frame_cnt"] += 1
        IBAR.info_status["mouse_loc"] = pg.mouse.get_pos()
        if GDAT.grid["D"]["is_visible"] is True:
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
        if GDAT.console["is_visible"] is True:
            CONSWIN.draw()
        if IBAR.info_status["on"] is True:
            IBAR.set_status_text()
        else:
            IBAR.set_default_text()
        IBAR.draw()
        if GDAT.grid["D"]["is_visible"] is True:
            GRIDWIN.draw()
            GRIDWIN.draw_grid(IBAR.info_status["grid_loc"])

        # for txtin in self.TIG:
        #     txtin.draw()
        # self.PAGE.draw()

        # refresh the menus
        GMNU.draw_menu_bar()
        for mb_ky in GMNU.mitems.keys():
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
    CONSWIN = GameConsole()
    GRIDWIN = GameMap()
    SaskanGame()
