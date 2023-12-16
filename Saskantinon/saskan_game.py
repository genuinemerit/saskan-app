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
from pprint import pformat as pf    # noqa: F401, format like pp for files
from pprint import pprint as pp     # noqa: F401
from pygame.locals import *         # noqa: F401, F403

from io_file import FileIO          # type: ignore
from io_shell import ShellIO        # type: ignore
from saskan_math import SaskanRect  # type: ignore

FI = FileIO()
SI = ShellIO()
SR = SaskanRect()
# WT = WireTap()

# Global constants for parameterized configs
FRAME = "game_frame"
MENUS = "game_menus"
FONT_TINY_SZ = 12
FONT_SM_SZ = 24
FONT_MED_SZ = 30
LG_FONT_SZ = 36
FONT_SANS = 'DejaVu Sans'
FONT_FXD = 'Courier 10 Pitch'
# PyGame Init needs to be here to work properly with PG class.
pg.init()


@dataclass(frozen=True)
class PG:
    """PyGame and Platform constants."""
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
    CP_BLACK = pg.Color(0, 0, 0)
    CP_BLUE = pg.Color(0, 0, 255)
    CP_BLUEPOWDER = pg.Color(176, 224, 230)
    CP_GRAY = pg.Color(80,80,80)
    CP_GRAY_DARK = pg.Color(20, 20, 20)
    CP_GREEN = pg.Color(0, 255, 0)
    CP_PALEPINK = pg.Color(215, 198, 198)
    CP_RED = pg.Color(255, 0, 0)
    CP_SILVER = pg.Color(192, 192, 192)
    CP_WHITE = pg.Color(255, 255, 255)
    # PyGame Fonts
    F_SANS_TINY = pg.font.SysFont(FONT_SANS, FONT_TINY_SZ)
    F_SANS_SM = pg.font.SysFont(FONT_SANS, FONT_SM_SZ)
    F_SANS_MED = pg.font.SysFont(FONT_SANS, FONT_MED_SZ)
    F_SANS_LG = pg.font.SysFont(FONT_SANS, LG_FONT_SZ)
    F_FIXED_LG = pg.font.SysFont(FONT_FXD, LG_FONT_SZ)
    # PyGame Cursors
    CUR_ARROW = pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW)
    CUR_CROSS = pg.cursors.Cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
    CUR_HAND = pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)
    CUR_IBEAM = pg.cursors.Cursor(pg.SYSTEM_CURSOR_IBEAM)
    CUR_WAIT = pg.cursors.Cursor(pg.SYSTEM_CURSOR_WAIT)
    # Platform info
    
    info = pg.display.Info()
    PLATFORM = (
        FI.F[FRAME]["dsc"] +
        " | " + platform.platform() +
        " | " + platform.architecture()[0] +
        f" | monitor (w, h): {info.current_w}, {info.current_h}" +
        " | Python " + platform.python_version() +
        " | Pygame " + pg.version.ver)

    # Overall frame = WIN object
    # Set sizes and positions based on monitor size
    # For scaling images, see: https://www.pygame.org/docs/ref/transform.html
    # Example: scaled_image = 
    #   pygame.transform.scale(original_image, (new_width, new_height))
    WIN_W = round(info.current_w * 0.9)
    WIN_H = round(info.current_h * 0.9)
    WIN_MID = (WIN_W / 2, WIN_H / 2)
    WIN = pg.display.set_mode((WIN_W, WIN_H))
    pg.display.set_caption(FI.F[FRAME]["ttl"])

    # Menu Bar
    MENU_CNT = len(FI.M[MENUS]["menu"])
    # top, left of the FIRST menu bar member.
    MBAR_X = WIN_W * 0.01
    MBAR_Y = WIN_H * 0.005
    # w, h, margin of __each__ menu bar member.
    MBAR_W = (WIN_W - (MBAR_X * 2)) / MENU_CNT
    MBAR_W = 240 if MBAR_W > 240 else MBAR_W
    MBAR_H = WIN_H * 0.04
    MBAR_MARGIN = 6

    # Game Map
    GAMEMAP_X = int(round(WIN_W * 0.05))
    GAMEMAP_Y = int(round(WIN_H * 0.05))
    GAMEMAP_W = int(round(WIN_W * 0.6))
    GAMEMAP_H = int(round(WIN_H * 0.6))
    GAMEMAP_TTL = FI.W["game_windows"]["gamemap"]["ttl"]

    # Console
    CONSOLE = FI.W["game_windows"]["console"]
    CONSOLE_X = int(round(GAMEMAP_X + GAMEMAP_W + 20))
    CONSOLE_Y = GAMEMAP_Y
    CONSOLE_W = int(round(WIN_W * 0.3))
    CONSOLE_H = GAMEMAP_H
    CONSOLE_TTL = FI.W["game_windows"]["console"]["ttl"]

    # Info Bar
    IBAR_LOC = (GAMEMAP_X, int(round(WIN_H * 0.95)))

    # Help Pages (web pages)
    WHTM = FI.U["uri"]["help"]  # links to web pages / help pages

    # In-window helper settings, may be useful in info/console windows
    HDR_LOC = (60, 40)   # LOC = Top-Left x, y
    PAGE_X = 60
    PAGE_Y = 60
    PAGE_MAX_LNS = 38    # max lines to display per column
    PAGE_V_OFF = 22      # vertical offset for each line of text
    PAGE_COLS = [(PAGE_X, PAGE_Y),
                 (WIN_W * 0.33, PAGE_Y),
                 (WIN_W * 0.67, PAGE_Y)]
    # Other
    KEYMOD_NONE = 4096
    TIMER = pg.time.Clock()

class GameData(object):
    """Get and set static and dynamic resources used inside the app.
    This class is instantiated as GDAT, a global object.
    
    Includes:
    - Status flags
    - Grid defintions

    @DEV:
    - Handle layers of data, zoom-in, zoom-out, other views
    - Example zoomed-in: a region, a town and environs, a village, a scene
    - Where to put GUI controls for scroll, zoom, pan, select-move, etc
    - Also: event trigger conditions (business rules), star maps, etc.
    """
    def __init__(self):
        """Status flags:
        - currently loaded map data
        - currently loaded console
        - currently loaded grid:     
            - "D" = data outside a specific grid
            - "G" = grids matrix, with data record for each grid-square
            - "L" = lines
        - set up default D, G, L
        """
        self.divider = "-" * 16
        self.post = {"active": False,
                     "catg": None,
                     "item": None}
        
        self.console = {"is_visible": False,
                        "con_box": pg.Rect,
                        "T": list(),
                        "t_img": list(),
                        "t_box": list(),
                        "title": {"text": '',
                                  "img": pg.Surface,
                                  "box": pg.Rect}}
        self.grid = {"D": dict(),
                     "L": dict(),
                     "G": dict()}
        self.init_grid_d()
        self.init_grid_l()
        self.init_grid_g()

    # Init methods for GAMEMAP (game map window)
    # ==========================================
    def init_grid_d(self):
        """
        - Define containing dimensions for "D" (general data) matrix.

        - Define sizing of grid and its offset from GAMEMAP.
            - For now, default scaling is hard-coded here.
        - Associate pygame px and km with grid dimensions.
            - Set border box for GAMEMAP.
            - Set grid offset from GAMEMAP.
            - Set number of grid rows, cols.
            - Set px and km per grid-square.
        - For conversions to other units, use SaskanMath class.
        Note: px refers to the pygame drawing units.

        @DEV:
        - Add other dimensions as needed for zoom-in.
        - Move defaults to a config file eventually.
        """
        self.grid["D"] = {
            "is_visible": False,
            "grid_rect": SR.make_rect(PG.GAMEMAP_Y, PG.GAMEMAP_X,
                                      PG.GAMEMAP_W, PG.GAMEMAP_H)}
        self.grid["D"]["grid_box"] = self.grid["D"]["grid_rect"]["box"]
        # TopLeft offset from GAMEMAP to grid:
        self.grid["D"]["offset"] = {"x": 17, "y": 18}
        # Sizing of matrix and of individual grid-squares:
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
        """ 
        - Define "G" (grid-square-specific) data records.
        - Define a rect and box for each grid-square.
        """
        for c in range(0, self.grid["D"]["dim"]["cols"]):
            for r in range(0, self.grid["D"]["dim"]["rows"]):
                g_ky = self.make_grid_key(c, r)
                x = self.grid["L"]["vert_ln"][c][0][0]  # x of vert line
                y = self.grid["L"]["horz_ln"][r][0][1]  # y of horz line
                w = self.grid["D"]["dim"]["px"]["w"]    # width
                h = self.grid["D"]["dim"]["px"]["h"]    # height
                self.grid["G"][g_ky] =\
                    {"g_rect": copy(SR.make_rect(y, x, w, h))}
                self.grid["G"][g_ky]["g_box"] =\
                    self.grid["G"][g_ky]["g_rect"]["box"]

    # Game Data Helper methods
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
        """Capture status settings, "posted" game data, in the sense
           of data "posted" to a bulletin board, or a HTTP POST.
        Example: key values pointing to data in JSON files (later: from DB)
        :args:
        - p_post (dict): name-value pairs for class .post structure.
          Defaults:
            - "active": boolean indicating whether gamewin is active
            - "catg": name of category to load
            - "item": name of item to load
        :sets:
        - self.post (dict): name-value pairs for class .post structure.
        """
        for k, v in p_post.items():
            self.post[k] = v

    # Game Data console methods
    # =============================
    def set_t_lbl_nm(self,
                     p_attr: dict):
        """Set text for a label (l) and name (n), but no type (t).
           Example: an attribute like "type"
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.console["T"] (list): list of strings to render as text
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_attr['label']}:")
        self.console["T"].append(f"  {p_attr['name']}")

    def set_t_lbl_nm_typ(self,
                         p_attr: dict):
        """Set text for a label (l), a name (n), and a type (t).
        
           Example: an attribute like "contained_by"
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.console["T"] (list): list of strings to render as text
        """
        self.console["T"].append(self.divider)
        self.console["T"].append(f"{p_attr['label']}:")
        self.console["T"].append(f"  {p_attr['name']} " +
                                 f"({p_attr['type']})")

    def set_t_proper_names(self,
                           p_names: dict):
        """Set text for a "name" attribute, referring to proper
            names of things.  Must be one value indexed by "common"; 
            and may also optionally have a set of names in different
            game languages or dialects.
        :attr:
        - p_names (dict): name-value pairs to format
        :sets:
        - self.console["T"] (list): list of strings to render as text
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
        """Set text for a "map" attribute, referring to game-map data.
        :attr:
        - p_map (dict): name-value pairs to format
        :sets:
        - self.console["T"] (list): list of strings to render as text
        """
        self.console["T"].append(self.divider)
        if "distance" in p_map.keys():
            distance = p_map["distance"]
            self.console["T"].append(f"{distance['label']}:")
            for a in ["height", "width"]:
                self.console["T"].append(
                    f"  {distance[a]['label']}:  " +
                    f"{distance[a]['amt']} {distance['unit']}")
        if "location" in p_map.keys():
            location = p_map["location"]
            self.console["T"].append(f"{location['label']}:")
            for a in ["top", "bottom", "left", "right"]:
                self.console["T"].append(
                    f"  {location[a]['label']}: " +
                    f"{location[a]['amt']}{location['unit']}")

    def set_t_contains(self,
                       p_contains: dict):
        """Set text for a "contains" attribute, referring to things
            contained by an object.
        :attr:
        - p_contains (dict): name-value pairs to format
        :sets:
        - self.console["T"] (list): list of strings to render as text
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
        y = self.console["title"]["box"].y + FONT_MED_SZ
        for i, c_txt in enumerate(self.console["T"]):
            self.console["t_img"].append(
                PG.F_SANS_SM.render(c_txt, True, PG.CP_BLUEPOWDER,
                                    PG.CP_BLACK))
            self.console["t_box"].append(
                self.console["t_img"][i].get_rect())
            self.console["t_box"][i].topleft =\
                (x, y + ((FONT_SM_SZ + 2) * (i + 1)))

    def set_console_header(self,
                           p_hdr_text: str):
        """Render header string for display in console.
        """
        self.console["title"] = {"text": p_hdr_text}
        self.console["title"]["img"] = PG.F_SANS_LG.render( # type: ignore
            self.console["title"]["text"], True, PG.CP_BLUEPOWDER, PG.CP_BLACK)
        self.console["title"]["box"] = self.console["title"]["img"].get_rect()   # type: ignore
        self.console["title"]["box"].topleft =\
            (PG.CONSOLE_X + 5, PG.CONSOLE_Y + 5)

    def set_console_text(self):
        """Format a list of strings to render as text for display in console.
        Store list of strings in the .console["T"] structure.
        .post["catg"] identifies source of config data to format.
        .post["item"] identifies type of data to format.
        
        @TODO:
        - Move the geo data into a database.
        - Read from database instead of config/schema files in most cases.
        - Only use config files for install-level customizations, overrides.
        """
        self.console["is_visible"] = True
        self.console["con_rect"] =\
            SR.make_rect(PG.CONSOLE_Y, PG.CONSOLE_X,
                         PG.CONSOLE_W, PG.CONSOLE_H)
        self.console["con_box"] = self.console["con_rect"]["box"]
        self.console["T"] = list()
        self.set_console_header(PG.CONSOLE["ttl"])
        
        pp(('self.post["catg"]', self.post["catg"],
            'self.post["item"]', self.post["item"]))
        
        # Contents
        if self.post["catg"] == "geo":
            con_data = FI.G[self.post["catg"]][self.post["item"]]
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
        - Topleft of grid (not GAMEMAP) is origin for map.
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
        # Try breaking each function into a method and asking CoPilot/ChatGPT
        #   to help with the math and the code. Be sure to give an example
        #   of the data structure and the expected or desired output.
        #   Ask for examples of how to execute and test the code.
        # 
        # Break this down functionally. WWHD? (What Would Haskell Do?)
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
                    "item_nm": FI.G[self.post["catg"]][self.post["item"]]["name"],
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
        - Before trying to apply detailed drawings, start with simple
          representations -- circles, squares, lines, etc.
        - Move geo data to database
        """
        self.grid["D"]["is_visible"] = True
        if self.post["catg"] == "geo":
            data = FI.G[self.post["catg"]][self.post["item"]]
            if "map" in data.keys():
                self.set_map_dim(data["map"])


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
             for ky, val in FI.M[MENUS]["menu"].items()}
        # x --> left edge of first, leftmost menu bar member
        x = PG.MBAR_X
        for mb_k, v in self.mbars.items():
            self.mbars[mb_k] =\
                {"name": v["name"],
                 "text": PG.F_SANS_SM.render(
                     v["name"], True, PG.CP_BLUEPOWDER, PG.CP_GRAY_DARK),
                 "selected": False,
                 "tbox": None,
                 "mbox": None}
            # Rect based on text size and location
            self.mbars[mb_k]["tbox"] =\
                self.mbars[mb_k]["text"].get_rect()
            # Default rect for menu bar member container
            self.mbars[mb_k]["mbox"] =\
                pg.Rect((x, PG.MBAR_Y), (PG.MBAR_W,
                                         PG.MBAR_H + 
                                         (PG.MBAR_MARGIN * 2)))
            x = self.mbars[mb_k]["mbox"].right # shift x for next bar
            # Center text rect in menu bar member rect
            # Kludge to account for visual niceness of text
            self.mbars[mb_k]["tbox"].left =\
                self.mbars[mb_k]["mbox"].left +\
                    (self.mbars[mb_k]["mbox"].width / 2) - 12
            self.mbars[mb_k]["tbox"].top =\
                self.mbars[mb_k]["mbox"].top + PG.MBAR_MARGIN + 5

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
                pg.Rect((left, top), (PG.MBAR_W, 0))

    def set_menu_item_box(self,
                          p_mb_k: str,
                          p_mi_k: str,
                          p_mi_x: int):
        """
        Define bounding box for text in menu item.
        - width is text width plus margin on each side
        - height is fixed amount (PG.MBAR_H)
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
        width = text_w + (PG.MBAR_MARGIN * 2)
        top = self.mbars[p_mb_k]["mbox"].bottom +\
            (PG.MBAR_H * p_mi_x) + PG.MBAR_MARGIN
        left = self.mbars[p_mb_k]["mbox"].left +\
            (PG.MBAR_MARGIN * 4)
        self.mitems[p_mb_k][p_mi_k]["mitm_box"] =\
            pg.Rect((left, top), (width, PG.MBAR_H))

        self.mbars[p_mb_k]["mlist_box"].height += PG.MBAR_H

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
            PG.F_SANS_SM.render(p_mi_v["name"], True,
                                PG.CP_BLUEPOWDER, PG.CP_GRAY_DARK)
        self.mitems[p_mb_k][p_mi_k]["mi_text_disabled"] =\
            PG.F_SANS_SM.render(p_mi_v["name"], True,
                                PG.CP_GRAY, PG.CP_GRAY_DARK)
        self.set_menu_item_box(p_mb_k, p_mi_k, p_mi_x)

    def set_menus(self):
        """
        Initialize menu items data from config data.
        Define menu list box and items for each
            vertical menu bar / list of menu items.
        """
        # Init menu items from config
        self.mitems = {ky: val["items"]
                       for ky, val in FI.M[MENUS]["menu"].items()}
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
            pg.draw.rect(PG.WIN, PG.CP_BLUEPOWDER, mb_vals["mbox"], 2)
            PG.WIN.blit(mb_vals["text"], mb_vals["tbox"])
        mbox = [mb_vals["mbox"] for _, mb_vals in self.mbars.items()
                if mb_vals["selected"] is True]
        if len(mbox) > 0:
            pg.draw.rect(PG.WIN, PG.CP_GREEN, mbox[0], 2)

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
            pg.draw.rect(PG.WIN, PG.CP_GRAY_DARK,
                         self.mbars[mb_k]["mlist_box"], 0)
            for _, mi_v in self.mitems[mb_k].items():
                if mi_v["enabled"]:
                    PG.WIN.blit(mi_v["mi_text_enabled"], mi_v["mitm_box"])
                else:
                    PG.WIN.blit(mi_v["mi_text_disabled"], mi_v["mitm_box"])

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
        txt_color = PG.CP_GRAY
        # Set enabled status of identified item
        if p_use_default:
            if ("default" in list(self.mitems[mb_k][mi_ky].keys()) and\
                self.mitems[mb_k][mi_ky]["default"] == "enabled") or\
               "default" not in list(self.mitems[mb_k][mi_ky].keys()):
                    self.mitems[mb_k][mi_ky]["enabled"] = True
                    txt_color = PG.CP_BLUEPOWDER
            # Set text color and content of identified item
            self.mitems[mb_k][mi_ky]["mi_text"] =\
                PG.F_SANS_SM.render(self.mitems[mb_k][mi_ky]["name"],
                                    True, txt_color, PG.CP_GRAY_DARK)
        else:
            # Default selected item to enabled status
            self.mitems[mb_k][mi_ky]["enabled"] = True
            self.mitems[mb_k][mi_ky]["mi_text"] =\
                PG.F_SANS_SM.render(self.mitems[mb_k][mi_ky]["name"],
                                    True, PG.CP_BLUEPOWDER, PG.CP_GRAY_DARK)
            # Identify dependent menu items and modify their enabled status
            if "disable" in list(self.mitems[mb_k][mi_ky].keys()):
                for dep_ky in self.mitems[mb_k][mi_ky]["disable"]:
                    self.mitems[mb_k][dep_ky]["enabled"] = False
                    self.mitems[mb_k][dep_ky]["mi_text"] =\
                        PG.F_SANS_SM.render(self.mitems[mb_k][dep_ky]["name"],
                                            True, PG.CP_GRAY, PG.CP_GRAY_DARK)
            if "enable" in list(self.mitems[mb_k][mi_ky].keys()):
                for dep_ky in self.mitems[mb_k][mi_ky]["enable"]:
                    self.mitems[mb_k][dep_ky]["enabled"] = True
                    self.mitems[mb_k][dep_ky]["mi_text"] =\
                        PG.F_SANS_SM.render(self.mitems[mb_k][dep_ky]["name"],
                                            True, PG.CP_BLUEPOWDER,
                                            PG.CP_GRAY_DARK)


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
        # self.set_ibar_system_text()

    def set_ibar_system_text(self):
        """ Set Info Bar text to system info.
        @TODO:
            Get this info at initialization.
            No point in retrieving it again every few milliseconds.
        """
        self.system_text = (
            FI.F[FRAME]["dsc"] +
            " | " + platform.platform() +
            " | Python " + platform.python_version() +
            " | Pygame " + pg.version.ver)

    def set_ibar_status_text(self):
        """ Set Info Bar text to status text. """
        self.status_text = (
            "Generation: " + str(self.info_status["frame_cnt"]) +
            "    | Mouse: " + str(self.info_status["mouse_loc"]) +
            "    | Grid: " + str(self.info_status["grid_loc"]))

    def draw(self):
        """ Draw Info Bar.
        Set and draw the Info Bar text.
        Draw the info bar text, optionally including status info.
        """
        text = PG.PLATFORM + "   | " + self.status_text\
            if self.info_status["on"] is True else PG.PLATFORM
        self.itxt = PG.F_SANS_SM.render(text, True, PG.CP_BLUEPOWDER,
                                        PG.CP_BLACK)
        self.ibox = self.itxt.get_rect()
        self.ibox.topleft = PG.IBAR_LOC
        PG.WIN.blit(self.itxt, self.ibox)


class HtmlDisplay(object):
    """Set content for display in external web browser.
    This class is instantiated as a global object named WHTM.
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


class PageHeader(object):
    """Create an object to hold text for header.
    This class instantiates a widget drawn at top of a window.
    For example, on a console or report window.
    It is not a global object.

    Should probably be instantiated as a global object: PHDR.
    Its location is fixed and set in the PG dataclass.
    """

    def __init__(self,
                 p_hdr_txt: str = ""):
        """ Initialize PageHeader.
        :args:
        - p_hdr_txt: (str) Text to display in header.
        """
        self.set_text(p_hdr_txt)

    def set_text(self,
                 p_hdr_txt: str = ""):
        """ Set text for PageHeader.
        :args:
        - p_hdr_txt: (str) Text to display in header.
        """
        self.img = PG.F_SANS_LG.render(p_hdr_txt, True,
                                       PG.CP_BLUEPOWDER, PG.CP_BLACK)
        self.box = self.img.get_rect()
        self.box.topleft = PG.HDR_LOC

    def draw(self):
        """ Draw PageHeader. """
        PG.WIN.blit(self.img, self.box)


class GameConsole(object):
    """Draw the Game Consoled (info) window (rect).
    Display game data like score, map descriptions, etc.
    Instantiated as global object CONSOLE.

    N.B.:
    - GameData class does data load and rendering stored in "T" matrix.
    @DEV:
    - Eventually extend the console to handle text input fields.
    """

    def __init__(self):
        """ Initialize GameConsole.
        """
        pass

    def set_text(self,
                 p_data):
        """ Set text for GameConsole (does not draw or render)
        If modeled after HomeFinance report (main) screen...
        - Convert line feed characters to list of strings.
        - Convert single string to list of one string.
        - Convert tab characters to spaces.

        :args:
        - p_data: (str, str/ LF, or list of str) Data text.

        :sets:
        (list) self.lines, (list of str) for header and data.
        
        @TODO:
        - This is likely to be more like a game control console,
          with buttons and maybe text input fields.
        - Text display should be very contextual, closely tied to
          activities on the map or in the console.
        """
        pass

    def draw(self):
        """ Draw GameConsole.
        - Draw the GameConsole rect.
        - Draw the console header.
        - Draw text lines for GameConsole based on current GameData.
        """
        # Draw container rect and header.
        pg.draw.rect(PG.WIN, PG.CP_BLACK, GDAT.console["con_box"], 0)
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

    This class use data stored in the GameData object.
    """

    def __init__(self):
        """Initialize GameMap"""
        pass

    def draw(self):
        """Draw the Game map.
        draw(surface, color, coordinates, width)
        """
        # Draw grid box with thick border
        pg.draw.rect(PG.WIN, PG.CP_SILVER, GDAT.grid["D"]["grid_box"], 5)
        # Draw grid lines
        for vt in GDAT.grid["L"]["vert_ln"]:
            pg.draw.aalines(PG.WIN, PG.CP_WHITE, False, vt)
        for hz in GDAT.grid["L"]["horz_ln"]:
            pg.draw.aalines(PG.WIN, PG.CP_WHITE, False, hz)
        # Highlight grid squares inside or overlapping the map box
        for _, grec in GDAT.grid["G"].items():
            if grec["is_inside"]:
                pg.draw.rect(PG.WIN, PG.CP_WHITE, grec["g_box"], 0)
            elif grec["overlaps"]:
                pg.draw.rect(PG.WIN, PG.CP_SILVER, grec["g_box"], 0)
        # Draw map box with thick border
        pg.draw.rect(PG.WIN, PG.CP_PALEPINK, GDAT.grid["D"]["map"]["m_box"], 5)

    def draw_grid(self, grid_loc: str):
        """For now, just highlight/colorize a grid-square.
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
            pg.draw.rect(PG.WIN, PG.CP_PALEPINK,
                GDAT.grid["G"][grid_loc]["g_box"], 0)


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
        self.t_color = PG.CP_GREEN
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
            pg.draw.rect(PG.WIN, PG.CP_BLUEPOWDER, self.t_box, 2)
        else:
            pg.draw.rect(PG.WIN, PG.CP_BLUE, self.t_box, 2)
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

        # Text input examples:
        self.TIG = TextInputGroup()
        self.self.TIG.add(TextInput(PG.WIN_W * 0.2, PG.WIN_H * 0.02, 50, 24))
        self.self.TIG.add(TextInput(PG.WIN_W * 0.25, PG.WIN_H * 0.02, 50, 24))

        Initialize in-game keyboard usage. (Modify as needed.)
        Execute the main event loop.
        
        @TODO:
        - See if kbd assigns can be done in PG dataclass.
        """
        self.QUIT_KY: list = [pg.K_q, pg.K_ESCAPE]
        self.ANIM_KY: list = [pg.K_F3, pg.K_F4, pg.K_F5]
        self.DATA_KY: list = [pg.K_a, pg.K_l]
        self.RPT_TYPE_KY: list = [pg.K_KP1, pg.K_KP2, pg.K_KP3]
        self.RPT_MODE_KY: list = [pg.K_UP, pg.K_RIGHT, pg.K_LEFT]
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
                    event.key in self.QUIT_KY)):
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
                WHTM.draw(PG.WHTM["pygame"])
            elif mi_k == "app_help":
                WHTM.draw(PG.WHTM["app"])
            elif mi_k == "game_help":
                WHTM.draw(PG.WHTM["game"])
        elif mi_k == "start":
            GDAT.set_post({"catg": 'geo',
                           "item": 'Saskan Lands',
                           "active": True})
            GDAT.set_console_text()
            GDAT.set_map_data()
        elif mi_k == "status":
            IBAR.info_status["on"] = not IBAR.info_status["on"]
        elif mi_k == "pause_resume":
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

        Frozen refers only to the game animation and time-based
        event developments. It has no effect on rendering of the
        game, console or info windows except that we stop incrementing
        the frame count, which is handled in track_state().
        """
        # black out the entire screen
        PG.WIN.fill(PG.CP_BLACK)

        # Display info content based on what is currently
        #  posted in the GameData object
        if GDAT.console["is_visible"] is True:
            CONSOLE.draw()

        # Check, Draw info bar
        if IBAR.info_status["on"] is True:
            IBAR.set_ibar_status_text()
        # else:
        #    IBAR.set_ibar_system_text()
        IBAR.draw()
        
        # Draw the game map
        if GDAT.grid["D"]["is_visible"] is True:
            GAMEMAP.draw()
            GAMEMAP.draw_grid(IBAR.info_status["grid_loc"])

        # for txtin in self.TIG:
        #     txtin.draw()
        # self.PAGE.draw()

        # refresh the menus
        GMNU.draw_menu_bars()
        for mb_k in GMNU.mitems.keys():
            GMNU.draw_menu_items(mb_k)

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
    WHTM = HtmlDisplay()  # for Help windows
    CONSOLE = GameConsole()
    GAMEMAP = GameMap()
    SaskanGame()
