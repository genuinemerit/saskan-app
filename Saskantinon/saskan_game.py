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
    PC_GREEN = pg.Color(0, 255, 0)
    PC_PALEPINK = pg.Color(215, 198, 198)
    PC_RED = pg.Color(255, 0, 0)
    PC_SILVER = pg.Color(192, 192, 192)
    PC_WHITE = pg.Color(255, 255, 255)
    # PyGame Fonts
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

    # Frame = WIN*
    # Caption is the title of the window (frame).
    pg.display.set_caption(FI.G[FRAME]["ttl"])
    WIN_W = FI.G[FRAME]["sz"]["w"]
    WIN_H = FI.G[FRAME]["sz"]["h"]
    WIN_MID = (WIN_W / 2, WIN_H / 2)
    WIN = pg.display.set_mode((WIN_W, WIN_H))
    # WIN = pg.display.set_mode((WIN_W, WIN_H), DOUBLEBUF|HWSURFACE, 32)
    # Page Header is within the frame.
    PHDR_LOC = (FI.G[FRAME]["pg_hdr"]["x"],
                FI.G[FRAME]["pg_hdr"]["y"])
    # Menu Bar
    # Sizing of top-menu bar items is done in MenuBar class,
    #  based on text width and height.
    # top, left of the entire menu:
    MBAR_X = FI.G[MENUS]["bar"]["x"]
    MBAR_Y = FI.G[MENUS]["bar"]["y"]
    # w, h, margin of each vertical menu bar menu
    MBAR_W = FI.G[MENUS]["bar"]["w"]
    MBAR_H = FI.G[MENUS]["bar"]["h"]
    MBAR_MARGIN = FI.G[MENUS]["bar"]["margin"]
    MBAR_LOC = (MBAR_X, MBAR_Y)
    # In-Frame "Windows" = PINFO*, PGAME*, IBAR*
    # Key to Game, Info and Help Windows
    PINFO = FI.G["game_windows"]["info"]
    PGAME = FI.G["game_windows"]["game"]
    PHELP = FI.G["uri"]["help"]
    # Info Bar = Status display @ bottom of frame
    IBAR_X = FI.G[FRAME]["ibar"]["x"]
    IBAR_Y = FI.G[FRAME]["ibar"]["y"]
    IBAR_LOC = (IBAR_X, IBAR_Y)
    # Other
    KEYMOD_NONE = 4096
    TIMER = pg.time.Clock()

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
        self.POST = dict()
        self.TEXT = list()
        self.MAP = dict()

    def set_post(self,
                 p_category: str,
                 p_item: str):
        """Capture current status settings for game data.
        These are key values pointing to data in JSON files.

        :args:
        - p_category (str): category key of data to retrieve, e.g. "geo"
        - p_item (str): item key of data to retrieve, e.g. "Saskan Lands"
        """
        self.POST["catg"] = p_category
        self.POST["item"] = p_item

    def get_text(self) -> str:
        """Return data for posted item,
        formatted as a list of strings that can
        be rendered as text on the Console.
        """
        data = FI.S[self.POST["catg"]][self.POST["item"]]
        self.TEXT = list()
        # Item name(s)
        self.TEXT.append(data['name']['common'])
        for k, v in data['name'].items():
            if k != 'common':
                self.TEXT.append(f"  {k}: {v}")
        # Map dimensions
        self.MAP = data['map']
        self.TEXT.append("-" * 16)
        self.TEXT.append("Kilometers")
        self.TEXT.append(f"  North-South: {self.MAP['rect']['n_s_km']}")
        self.TEXT.append(f"  East-West: {self.MAP['rect']['e_w_km']}")
        self.TEXT.append("Degrees")
        self.TEXT.append("  Latitude")
        self.TEXT.append(f"    North: {self.MAP['degrees']['n_lat']}")
        self.TEXT.append(f"    South: {self.MAP['degrees']['s_lat']}")
        self.TEXT.append("  Longitutde")
        self.TEXT.append(f"    West: {self.MAP['degrees']['w_long']}")
        self.TEXT.append(f"    East: {self.MAP['degrees']['e_long']}")
        # Contained by
        self.TEXT.append("-" * 16)
        self.TEXT.append(f"{list(data['contained_by'].keys())[0]}: " +
                         f"{list(data['contained_by'].values())[0]}")
        # Political boundaries
        self.TEXT.append("-" * 16)
        self.TEXT.append("Political Boundaries")
        politics = {k: v for k, v in data['contains'].items() if k in ('federation', 'district')}
        if "federation" in politics:
            self.TEXT.append("  Federations:")
            for fed in politics["federation"]:
                self.TEXT.append(f"    {fed}")
        if "district" in politics:
            self.TEXT.append("  Districts:")
            for dist in politics["district"]:
                self.TEXT.append(f"    {dist}")


class MenuBar(object):
    """ Menu Bar items for the application.
    Define a surface for a clickable top-level menu bar item.
    Clicking on a menu bar item opens or closes a MenuItems.
    """
    def __init__(self,
                 p_name: str,
                 p_x_left: int):
        """Initialize a Menu Bar object.
        = `text` is text content and UID for the menu bar item.
        - `mbox` is the bounding box (rect object) for the menu bar item.
        - 'mtxt` is the image (surface) for rendering text.
        - 'tbox` is the bounding box for the text. Also a rect object,
           but it is derived from the text-image surface object (mtxt).

        :args:
        - p_name (str): text and UID for menu bar item.
        - p_x_left (int): x location for menu bar box.
        """
        self.is_selected = False
        self.text = p_name

        # mbox_w = len(self.text) * 12
        mbox_w = len(self.text) * SM_FONT_SZ

        self.mbox = pg.Rect(p_x_left,
                            PG.MBAR_Y,
                            mbox_w,
                            PG.MBAR_H)
        self.mtxt = PG.F_SANS_SM.render(
            self.text, True, PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.tbox = self.mtxt.get_rect()
        self.tbox.topleft =\
            (p_x_left + int((self.mbox.width - self.tbox.width) / 2),
             PG.MBAR_Y + PG.MBAR_MARGIN)

    def draw(self):
        """ Draw a Menu Bar item.
        """
        if self.is_selected:
            pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, self.mbox, 2)
        else:
            pg.draw.rect(PG.WIN, PG.PC_BLUE, self.mbox, 2)
        PG.WIN.blit(self.mtxt, self.tbox)

    def clicked(self, p_mouse_loc) -> bool:
        """ Return True if mouse clicked on the mbox.
        """
        if self.mbox.collidepoint(p_mouse_loc):
            return True
        return False


class MenuItems(object):
    """Define one or more MenuItem associated with a MenuBar.
    Clicking on a menu bar item triggers a function and sets
    visibility of the MenuItems to False.
    """
    def __init__(self,
                 p_mitm_list: list,
                 p_mbar: MenuBar):
        """ Initialize Menu Items.
        The container (mbox) surface holds all the items.
        Each MenuItem is clickable, per its bounding box (tbox).

        :args:
        - p_mitm_list (list): list of menu item names.
        - p_mbar (MenuBar): the parent MenuBar object

        Rect = (left, top, width, height)
        """
        self.name = p_mbar.text
        self.is_visible = False
        self.item_cnt = len(p_mitm_list)
        # Protoype of box to draw around  menu items.
        self.mbox = pg.Rect(p_mbar.mbox.left,
                            p_mbar.mbox.bottom,
                            0,
                            p_mbar.mbox.height * self.item_cnt)
        self.mitems = []
        for mx, mi in enumerate(p_mitm_list):
            mi_id = mi[0]
            mi_nm = mi[1]
            mtxt = PG.F_SANS_SM.render(
                mi_nm, True, PG.PC_BLUEPOWDER, PG.PC_BLACK)
            mitm_w = mtxt.get_width() + (PG.MBAR_MARGIN * 2)
            # Box for each item in the menu item list.
            tbox = pg.Rect(self.mbox.left + PG.MBAR_MARGIN,
                           ((self.mbox.top + (PG.MBAR_H * mx)) +
                            PG.MBAR_MARGIN),
                           mitm_w, PG.MBAR_H)
            # Set mbox width equal to largest tbox width
            if tbox.width > self.mbox.width:
                self.mbox.width = tbox.width
            self.mitems.append(
                {'id': mi_id, 'mtxt': mtxt, 'tbox': tbox, 'text': mi_nm})

    def draw(self):
        """ Draw the list of Menu Items.
        """
        if self.is_visible:
            pg.draw.rect(PG.WIN, PG.PC_BLUEPOWDER, self.mbox, 2)
            for mi in self.mitems:
                PG.WIN.blit(mi['mtxt'], mi['tbox'])

    def clicked(self,
                p_mouse_loc):
        """ Return id and name of clicked menu item or None.
        """
        for mi in self.mitems:
            if mi['tbox'].collidepoint(p_mouse_loc):
                return (mi['id'], mi['text'])
        return None


class MenuGroup(object):
    """Define a group object for menu bars and menu items.
    Reference menus by name and associate menu bar with its items.
    """
    def __init__(self):
        self.mbars: dict = dict()
        self.mitems: dict = dict()
        self.current_bar = None
        self.current_item = None

    def add_bar(self,
                p_mbar: MenuBar):
        """Add a MenuBar to the collection."""
        self.mbars[p_mbar.text] = p_mbar

    def add_item(self,
                 p_mitems: MenuItems):
        """Add a MenuItems to the collection."""
        self.mitems[p_mitems.name] = p_mitems


class PageHeader(object):
    """Set text for header.
    HDR is a widget drawn at top of the page,
    just above the menu bar.

    @DEV - Consider whether this is really useful or not.
    """

    def __init__(self,
                 p_hdr_text: str):
        """ Initialize PageHeader. """
        self.img = PG.F_SANS_LG.render(p_hdr_text, True,
                                       PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.box = self.img.get_rect()
        self.box.topleft = PG.PHDR_LOC

    def draw(self):
        """ Draw PageHeader. """
        PG.WIN.blit(self.img, self.box)


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


class PageInfo(object):
    """Define and handle the Game Info window (rect).

    Display game data like score, etc.; and to contain text inputs.
    It is a rect within the Frame real estate, not a separate Frame object.
    """

    def __init__(self):
        """ Initialize PageInfo.
        """
        WT.log("info", f"PageInfo instantiated: {str(self)}",
               __file__, __name__, self, sys._getframe())
        self.BOX = pg.Rect(PG.PINFO["x"], PG.PINFO["y"],
                           PG.PINFO["w"], PG.PINFO["h"])
        self.TTL = None
        self.TXT = None
        self.IMG = None

    def set_header(self):
        """ Set PageInfo (Game Console) header.
        Set the title  text to display in the PageInfo rect.
        """
        self.IMG = PG.F_SANS_LG.render(PG.PINFO["ttl"], True,
                                       PG.PC_BLUEPOWDER, PG.PC_BLACK)
        self.TTL = self.IMG.get_rect()
        self.TTL.topleft = (PG.PINFO["x"] + 5,
                            PG.PINFO["y"] + 5)

    def set_text_line(self,
                      p_lnno: int,
                      p_text: str):
        """ Set a line of text to display in the PageInfo rect.
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

    def draw(self,
             p_gd: GameData):
        """ Draw PageInfo.
        - Black out the PageInfo rect.
        - Draw the console header.
        - Incrementally add lines text (or inputs) to PageInfo
          region based on current posting in GameData object.
        """
        pg.draw.rect(PG.WIN, PG.PC_BLUE, self.BOX, 1)
        self.set_header()
        PG.WIN.blit(self.IMG, self.TTL)
        for i, ln in enumerate(p_gd.TEXT):
           self.set_text_line(i, ln)
           PG.WIN.blit(self.IMG, self.TXT)


class PageGame(object):
    """Define and handle the Game GUI window (rect).

    Display the map, scenes, game widgets, GUI controls.
    It is a rect within the Frame real estate, not a separate Frame object."""

    def __init__(self,
                 p_info_text: str):
        """Initialize PageGame"""
        self.box = pg.Rect(PG.PGAME["x"], PG.PGAME["y"],
                           PG.PGAME["w"], PG.PGAME["h"])
        WT.log("info", f"PageGame initialized: {str(self)}",
               __file__, __name__, self, sys._getframe())

    def draw(self):
        """Draw the Game page.
        draw(surface, color, coordinates, width)

        See turtles app for ideas on managing the game data and drawing
        widgets based on that. Used a pandas dataframe to hold the data,
        which is nice because rows are conveniently indexed and can be
        mapped to rectangular screen coordinates.

        Just assume 2D for now. If we want to add 3D, we can do that later.
        """
        pg.draw.rect(PG.WIN, PG.PC_SILVER, self.box, 5)


class InfoBar(object):
    """Info Bar item.
    It is located across bottom of window.
    Deafault text is system info.
    To change the text, call set_text function.
    """

    def __init__(self):
        """ Initialize Info Bar. """
        self.set_default_text()

    def set_default_text(self):
        """ Set Info Bar text to system info. """
        self.text = (
            FI.G[FRAME]["dsc"] +
            " | " + platform.platform() +
            " | Python " + platform.python_version() +
            " | Pygame " + pg.version.ver)

    def set_status_text(self,
                        p_status: dict):
        """ Set Info Bar text to status text. """
        self.text = (
            "Generation: " + str(p_status["frame_cnt"]) +
            "    |    Mouse: " + str(p_status["mouse_loc"]))

    def draw(self,
             p_frame_cnt_mode: bool = False,
             p_frame_cnt: int = 0,
             p_mouse_loc: tuple = (0, 0)):
        """ Draw Info Bar.
        Optionally draw frame count and mouse location.

        :args:
        - p_frame_cnt_mode: (bool) True to display frame counter
        - p_frame_cnt: (int) Frame counter value
        - p_mouse_loc: (tuple) Mouse location (x, y)
        """
        self.itxt = PG.F_SANS_SM.render(
            self.text, True, PG.PC_BLUEPOWDER, PG.PC_BLACK)
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
        Refresh shared data space.
        Initialize counters, modes, trackers, widgets.
        Execute the main event loop.
        """
        FI.pickle_saskan(path.join("/home", Path.cwd().parts[2], FI.D['APP']))
        WT.log("info", "dev/shm cache created",
               __file__, __name__, self, sys._getframe())

        # Keyboard assignments
        # Modify as needed for game mode...
        self.QUIT_KY: list = [pg.K_q, pg.K_ESCAPE]
        self.ANIM_KY: list = [pg.K_F3, pg.K_F4, pg.K_F5]
        self.DATA_KY: list = [pg.K_a, pg.K_l]
        self.RPT_TYPE_KY: list = [pg.K_KP1, pg.K_KP2, pg.K_KP3]
        self.RPT_MODE_KY: list = [pg.K_UP, pg.K_RIGHT, pg.K_LEFT]

        # Menu bar and menu items
        self.MEG = MenuGroup()
        prev_x = PG.MBAR_X
        for _, mn in FI.G[MENUS]["menu"].items():
            mn_nm = mn["nm"]
            self.MEG.add_bar(MenuBar(mn_nm, prev_x))
            prev_x = self.MEG.mbars[mn_nm].mbox.right
            mil = [(mi_id, mi['nm']) for mi_id, mi in mn["items"].items()]
            self.MEG.add_item(MenuItems(mil, self.MEG.mbars[mn_nm]))
        self.MEG.current_bar = None
        self.MEG.current_item = None

        # Game, Console, Page Header rects and external (browser) Help windows
        self.PINFO = None
        self.PGAME = None
        self.PHDR = PageHeader(FI.G[FRAME]["pg_hdr"]["default_text"])
        self.WHTML = HtmlDisplay()

        # Status trackers and information bar
        self.STATUS = {
            "on": False,
            "frozen": False,
            "frame_cnt": 0,
            "mouse_loc": (0, 0)}
        self.IBAR = InfoBar()

        # Static data and resources
        self.GD = GameData()

        # Test mouse logging message
        # msg = "Mouse location: " + str(self.mouse_loc)
        # WT.log("info", msg, __file__, __name__, self, sys._getframe())

        # Test log report
        # I have display to console turned on in wiretap.
        # That seems a little easier to read than dumping the logs.
        # WT.dump_log()

        # Make it go!
        # Makes more sense to me to trigger the main loop here,
        #  rather than in __main__ module.
        self.main_loop()

    # Mouse Click Event Handlers
    # ==============================================================
    def do_select_mbar(self,
                       p_mouse_loc):
        """Trap for a mouse click on a menu bar item.
        This function is called whenever there is a mouseclick.
        The click may or may not be in the top menu bar.

        :args:
        - p_mouse_loc: (tuple) mouse location
        """
        for m_nm, mbar in self.MEG.mbars.items():
            if mbar.clicked(p_mouse_loc):
                if mbar.is_selected:
                    # Hide bar and item list if currently selected.
                    mbar.is_selected = False
                    self.MEG.mitems[m_nm].is_visible = False
                    self.MEG.current_bar = None
                    self.MEG.current_item = None
                else:
                    mbar.is_selected = True
                    self.MEG.mitems[m_nm].is_visible = True
                    self.MEG.current_bar = m_nm
                    # Hide and unselect any other items and menus.
                    for m_other_nm, other_mbar in self.MEG.mbars.items():
                        if not m_other_nm == m_nm:
                            other_mbar.is_selected = False
                            self.MEG.mitems[m_other_nm].is_visible = False
            else:
                if self.MEG.current_bar == m_nm:
                    mbar.is_selected = True
                else:
                    mbar.is_selected = False

    def do_select_mitem(self,
                        p_mouse_loc):
        """Trap for a mouse click on a menu item.
        This function is called whenever there is a mouseclick.
        A menu item may or may not have been clicked.

        :args:
        - p_mouse_loc: (tuple) mouse location
        """
        item_id = None
        self.MEG.current_item = None
        for bar_nm, ilist in self.MEG.mitems.items():
            if ilist.is_visible:
                item_id = ilist.clicked(p_mouse_loc)
                if item_id is not None:
                    # Then a vert menu bar item was clicked.
                    # item_id = (key_nm, display_nm)
                    self.MEG.current_item = item_id[0]
                    # hide the selected item list and unselect its bar
                    self.MEG.mitems[bar_nm].is_visible = False
                    self.MEG.mbars[bar_nm].is_selected = False
        return item_id

    # Keyboard and Menu Item Event Handlers
    # ==============================================================
    def exit_app(self):
        """Exit the app.
        """
        pg.quit()
        sys.exit()

    def handle_menu_event(self,
                          p_menu_item):
        """Trigger an event based on menu item selection.
        N.B. -- Draw calls in the pygame frame are handled in the screen refresh loop.
        """
        menu_nm = self.MEG.current_item
        m_item_id = p_menu_item[0]
        m_item_text = p_menu_item[1]

        msg = f"Menu item clicked: {menu_nm}, {m_item_id}, {m_item_text}"
        WT.log("info", msg, __file__, __name__, self, sys._getframe())

        if m_item_id == "exit":
            self.exit_app()
        elif "help" in m_item_id:
            if m_item_id == "pg_help":
                self.WHTML.draw(PG.PHELP["pygame"])
            elif m_item_id == "app_help":
                self.WHTML.draw(PG.PHELP["app"])
            elif m_item_id == "game_help":
                self.WHTML.draw(PG.PHELP["game"])
        elif m_item_id == "start":
            # Console/Game Info window
            self.PINFO = PageInfo()
            self.GD.set_post('geo', 'Saskan Lands')
            # Game/Map window
            self.PGAME = PageGame(PG.PGAME["ttl"])
        elif m_item_id == "status":
            self.STATUS["on"] = not self.STATUS["on"]
        elif m_item_id == "pause_resume":
            self.STATUS["frozen"] = not self.STATUS["frozen"]

    def check_exit_app(self, event: pg.event.Event):
        """Handle exit if one of the exit modes is triggered.
        This is triggered by the Q key, ESC key or `X`ing the window.

        :args:
        - event: (pg.event.Event) event to handle
        """
        if (event.type == pg.QUIT or
                (event.type == pg.KEYUP and event.key in self.QUIT_KY)):
            self.exit_app()

    # Loop Events
    # ==============================================================
    def track_state(self):
        """Keep track of the state of the app on each frame.

        Sets:
        - mouse_loc: get current mouse location
        - frame_cnt: increment if tracking status and not in a freeze mode
        - cursor: if no text input box is activated, set to default

        @DEV:
        More...
        - Mouse-click was inside the Game window
        - Mouse-click was inside the Console window
        """
        self.STATUS["mouse_loc"] = pg.mouse.get_pos()

        if self.STATUS["on"] is True and self.STATUS["frozen"] is False:
            self.STATUS["frame_cnt"] += 1

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
        # black out the screen
        PG.WIN.fill(PG.PC_BLACK)

        # self.PHDR.draw()

        # refresh the Game/Console window
        # text to display is based on what is currently
        #  set to be posted in the GameData object
        if self.PINFO is not None:
            self.GD.get_text()
            self.PINFO.draw(self.GD)

        # refresh the Game/Map window
        if self.PGAME is not None:
            self.PGAME.draw()

        # Info/Status bar
        if self.STATUS["on"] is True:
            self.IBAR.set_status_text(self.STATUS)
        else:
            self.IBAR.set_default_text()
        self.IBAR.draw()

        # for txtin in self.TIG:
        #     txtin.draw()
        # self.PAGE.draw()

        # refresh the menus
        for m_nm, mbar in self.MEG.mbars.items():
            mbar.draw()
            self.MEG.mitems[m_nm].draw()

        pg.display.update()
        PG.TIMER.tick(30)

    # Main Loop
    # ==============================================================
    def main_loop(self):
        """Manage the event loop.
        - Handle window events (quit --> ESC or Q)
        """
        WT.log("info", "event loop launched",
               __file__, __name__, self, sys._getframe())
        while True:
            # Get mouse_loc and frame_cnt
            self.track_state()

            for event in pg.event.get():

                # Handle keyboard quit events (ESC or Q)
                self.check_exit_app(event)

                # Handle game & animation keyboard events

                if event.type == pg.MOUSEBUTTONDOWN:

                    # Handle menu events
                    self.do_select_mbar(self.STATUS["mouse_loc"])
                    menu_item = self.do_select_mitem(self.STATUS["mouse_loc"])
                    if self.MEG.current_item is not None:
                        self.handle_menu_event(menu_item)

                    # Handle text input events
                    # self.do_select_txtin(self.STATUS["mouse_loc"])

                    # Handle game-click events

            self.refresh_screen()

# Run program
if __name__ == '__main__':
    """Run program."""
    SaskanGame()
