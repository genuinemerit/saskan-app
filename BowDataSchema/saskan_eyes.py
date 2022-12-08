#!python
"""
:module:    saskan_eyes.py
:author:    GM (genuinemerit @ pm.me)
BoW Saskan App GUI.  pygame version.

Online references:
- https://www.pygame.org/docs/
- https://www.pygame.org/docs/genindex.html

Books:
- Begining Python Games Development -
    - https://learning.oreilly.com/library/view/beginning-python-games/9781484209707/9781484209714_Ch03.xhtml
- Python Game Programming by Example -
    - https://learning.oreilly.com/library/view/python-game-programming/9781785281532/ch05.html
- Program Arcade Games with Python and Pygame -
    - https://learning.oreilly.com/library/view/program-arcade-games/9781484217900/


Video courses:
- The Art of Doing: Video Game Creation with Python and Pygame -
    - https://learning.oreilly.com/videos/the-art-of/9781803231587/
- Game Development with PyGame: Write Your Own Games, Simulations, Demonstrations with Python -
    - https://learning.oreilly.com/videos/game-development-with/9781484256619/


Other libraries that may come in handy eventually:

Algorithms:
- pygame-ai

Physics:
- pymunk

Animation, Sprites:
- pyglet

Primitives, Rendering:
- cocos2d
- panda3d
- wasabi2d

Geometry, Vectors, Matrices:
- pygame.math
- pyrr
- euclid
- vec

Sound:
- pyfxr


Placs to find game assets and resources:
- pyweek
- itch.io

"""

import platform
import pygame as pg
import sys
import typing

from dataclasses import dataclass
from pprint import pprint as pp     # noqa: F401
from pygame.locals import *

from io_file import FileIO          # type: ignore
from io_wiretap import WireTap      # type: ignore

FI = FileIO()
WT = WireTap()
pg.init()


@dataclass(frozen=True)
class PG:
    # Colors
    C_BLACK = pg.Color(0, 0, 0)
    C_BLUE = pg.Color(0, 0, 255)
    C_BLUEPOWDER = pg.Color(176, 224, 230)
    C_GREEN = pg.Color(0, 255, 0)
    C_PALEPINK = pg.Color(215, 198, 198)
    C_RED = pg.Color(255, 0, 0)
    C_WHITE = pg.Color(255, 255, 255)
    # Fonts
    F_SANS_12 = pg.font.SysFont('DejaVu Sans', 12)
    F_SANS_16 = pg.font.SysFont('DejaVu Sans', 16)
    F_SANS_18 = pg.font.SysFont('DejaVu Sans', 18)
    F_FIXED_18 = pg.font.SysFont('Courier 10 Pitch', 18)
    # Cursors
    IBEAM = pg.cursors.Cursor(pg.SYSTEM_CURSOR_IBEAM)
    # Window / Canvas / Display
    APP_NM = 'Saskantinon'
    pg.display.set_caption(APP_NM)
    WIN_W = 1800
    WIN_H = 960
    WIN_MID = (WIN_W / 2, WIN_H / 2)
    WIN = pg.display.set_mode((WIN_W, WIN_H))
    # Menu and Info Bar Widgets
    MBAR_X = 60
    MBAR_Y = 10
    MBAR_W = 100        # Modify based on text content?
    MBAR_H = 26
    MBAR_MARGIN = 6
    MBAR_LOC = (MBAR_X, MBAR_Y)
    IBAR_X = 60
    IBAR_Y = 932
    IBAR_LOC = (IBAR_X, IBAR_Y)
    # Report Page Widgets
    HDR_LOC = (60, 40)      # LOC = Top-Left x, y
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
        - `mbox` is the bounding box for the menu bar item.
        - 'mtxt` is the image (surface) for rendering text.
        - 'tbox` is the bounding box for the text.

        :args:
        - p_name (str): text and UID for menu bar item.
        - p_x_left (int): x location for menu bar box.
        """
        self.is_selected = False
        self.text = p_name
        self.mbox = pg.Rect(p_x_left, PG.MBAR_Y,
                            PG.MBAR_W, PG.MBAR_H)
        self.mtxt = PG.F_SANS_12.render(
            self.text, True, PG.C_BLUEPOWDER, PG.C_BLACK)
        self.tbox = self.mtxt.get_rect()
        self.tbox.topleft =\
            (p_x_left + int((self.mbox.width - self.tbox.width) / 2),
             PG.MBAR_Y + PG.MBAR_MARGIN)

    def draw(self):
        """ Draw a Menu Bar item.
        """
        if self.is_selected:
            pg.draw.rect(PG.WIN, PG.C_BLUEPOWDER, self.mbox, 2)
        else:
            pg.draw.rect(PG.WIN, PG.C_BLUE, self.mbox, 2)
        PG.WIN.blit(self.mtxt, self.tbox)

    def clicked(self, p_mouse_loc) -> bool:
        """ Return True if mouse clicked on the mbox.
        """
        if self.mbox.collidepoint(p_mouse_loc):
            self.is_selected = not(self.is_selected)
            return True
        return False


class MenuItems(object):
    """Define one or more MenuItem's associated with a MenuBar.
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
        self.mbox = pg.Rect(p_mbar.mbox.left,
                            p_mbar.mbox.bottom,
                            p_mbar.mbox.width,
                            p_mbar.mbox.height * self.item_cnt)
        self.mitems = []
        for mx, mi_nm in enumerate(p_mitm_list):
            mtxt = PG.F_SANS_12.render(
                mi_nm, True, PG.C_BLUEPOWDER, PG.C_BLACK)
            tbox = pg.Rect(self.mbox.left + PG.MBAR_MARGIN,
                           ((self.mbox.top + (PG.MBAR_H * mx)) +
                            PG.MBAR_MARGIN),
                           PG.MBAR_W, PG.MBAR_H)
            self.mitems.append({'mtxt': mtxt, 'tbox': tbox, 'text': mi_nm})

    def draw(self):
        """ Draw the list of Menu Items.
        """
        if self.is_visible:
            pg.draw.rect(PG.WIN, PG.C_BLUEPOWDER, self.mbox, 2)
            for mi in self.mitems:
                PG.WIN.blit(mi['mtxt'], mi['tbox'])

    def clicked(self,
                p_mouse_loc):
        """ Return name of clicked menu item or None.
        If clicked on a menu item, set visibility of its container to False.

        @DEV:
        - The tbox coordinates are relative to the mbox.
        - The mouse_loc is relative to the window.
        - Need to convert mouse_loc to mbox coordinates or vice-versa.
        """
        for mi in self.mitems:
            pp(("Examining for click:", mi))
            pp(("mi['tbox']:", mi['tbox']))
            pp(("p_mouse_loc:", p_mouse_loc))
            if mi['tbox'].collidepoint(p_mouse_loc):
                print(f"Menu Item clicked!: {mi['text']}")
                self.is_visible = False
                return mi['text']
        return None


class MenuGroup(object):
    """Define a group object for menu bars and menu items.
    Used a dict so as to easily reference them by name, and
    easily associate the bar with its items.
    """
    def __init__(self):
        self.mbars: dict = dict()
        self.mitms: dict = dict()
        self.current_bar = None
        self.current_item = None

    def add_bar(self,
                p_mbar: MenuBar):
        """Add a MenuBar to the collection."""
        self.mbars[p_mbar.text] = p_mbar

    def add_item(self,
                 p_mitms: MenuItems):
        """Add a MenuItems to the collection."""
        self.mitms[p_mitms.name] = p_mitms


class PageHeader(object):
    """Set text for header.
    HDR is a widget drawn at top of the window.
    """

    def __init__(self,
                 p_hdr_txt: str = ""):
        """ Initialize PageHeader. """
        self.img = PG.F_SANS_18.render(p_hdr_txt, True,
                                       PG.C_BLUEPOWDER, PG.C_BLACK)
        self.box = self.img.get_rect()
        self.box.topleft = PG.HDR_LOC

    def draw(self):
        """ Draw PageHeader. """
        PG.WIN.blit(self.img, self.box)


class InfoBar(object):
    """Info Bar item.
    It is located across bottom of window.
    """

    def __init__(self,
                 p_text: str = ""):
        """ Initialize Info Bar. """
        if p_text == "":
            self.text = (
                "Python: " + platform.python_version() +
                " | Pygame: " + pg.version.ver +
                " | OS: " + platform.platform())
        else:
            self.text = p_text
        self.itxt = PG.F_SANS_12.render(
            self.text, True, PG.C_BLUEPOWDER, PG.C_BLACK)
        self.ibox = self.itxt.get_rect()
        self.ibox.topleft = PG.IBAR_LOC

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
        PG.WIN.blit(self.itxt, self.ibox)
        if p_frame_cnt_mode is True:
            genimg = PG.F_SANS_12.render(
                "Generation: " + str(p_frame_cnt) +
                "    |    Mouse: " + str(p_mouse_loc),
                True, PG.C_BLUEPOWDER, PG.C_BLACK)
            PG.WIN.blit(genimg,
                        genimg.get_rect(topleft=(PG.WIN_W * 0.67,
                                                 PG.IBAR_Y)))


class TextInput(pg.sprite.Sprite):
    """Define and handle a text input widget.
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
        self.t_font = PG.F_FIXED_18
        self.t_color = PG.C_GREEN
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
            pg.draw.rect(PG.WIN, PG.C_BLUEPOWDER, self.t_box, 2)
        else:
            pg.draw.rect(PG.WIN, PG.C_BLUE, self.t_box, 2)
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
    """
    def __init__(self):
        super().__init__()
        self.current = None     # ID currently-selected text input widget.


class SaskanEyes(object):
    """PyGame GUI for controlling Saskantinon functions.
    Initiated and executed by __main__.
    """
    def __init__(self, *args, **kwargs):
        """Initialize counters, modes, trackers, widgets.
        Execute the main event loop.
        """
        # Refresh all data in shared memory
        # FI.pickle_saskan()
        WT.log_module(__file__, __name__, self)
        # Mouse tracking
        self.mouse_loc = (0, 0)
        # Test log message
        WT.log_msg("info", "Mouse location: " + str(self.mouse_loc))
        # Test log report
        WT.dump_log()


# Run program
if __name__ == '__main__':
    """Run program."""
    SaskanEyes()
