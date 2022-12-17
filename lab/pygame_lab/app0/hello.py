# coding: utf-8
#!/usr/bin/python3

"""
Very simple Hello, World using pygame
From Beginning Python Games Development with Pygame, 2nd ed.

Can type just the 'q' key or CTRL-q to quit.
If frame is visible, can "X" out.
If app-level menu is visible, can select "Quit" from menu.

Will need to key-quit when testing full screen version.
"""

import pygame
from pygame.locals import *         # pylint: disable=unused-wildcard-import
from os import path
from sys import exit

pygame.init() # pylint: disable=no-member

## The second parameter is the display MODE... zero is the default.

# screen = pygame.display.set_mode((640, 480), 0, 32)

## Careful. Be sure key-based quit functions are working first before trying this mode.
## If using an extended display, this will probably reset it to dual-display mode.
# screen = pygame.display.set_mode((640, 480), FULLSCREEN, 32)            # pylint: disable=undefined-variable

## Unlikely to work without more configuration:
# screen = pygame.display.set_mode((640, 480), OPENGL, 32)                # pylint: disable=undefined-variable

## Works fine. If background is slightly smaller than window size, you'll see
## what happens when the cursor "draws outside the lines"
# screen = pygame.display.set_mode((640, 480), RESIZABLE, 32)             # pylint: disable=undefined-variable

## Careful. Be sure key-based or menu-based quit functions are working first before trying this mode.
## NOFRAME and RESIZABLE appear to be incompatible.
# screen = pygame.display.set_mode((640, 480), NOFRAME, 32)               # pylint: disable=undefined-variable

## This seems to work fine and provides a very sharp resolution.
## Combine multiple display modes using or-wise operator
# screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE, 32)   # pylint: disable=undefined-variable
# screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE|RESIZABLE|NOFRAME, 32)   # pylint: disable=undefined-variable
# screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE|RESIZABLE, 32)   # pylint: disable=undefined-variable
# screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE|NOFRAME, 32)   # pylint: disable=undefined-variable

## The 3rd parameter is the bit-depth, which determines number of colors available.
## If not defined, pygame defaults to desktop depth
# 32 = 16.7 M colors + spare bits
# 24 = 16.7 M colors
# 16 = 65,536 colors
# 15 = 32,768 colors + a spare bit
# 8 = 256 colors
# screen = pygame.display.set_mode((640, 480), 0, 8)      # With this setting, my cursor doesn't show up
# screen = pygame.display.set_mode((640, 480), 0, 16)     # Works fine
# screen = pygame.display.set_mode((640, 480), 0)           # Default, works fine
screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE)           # pylint: disable=undefined-variable

pygame.display.set_caption("Hello, Turtle World")

static_dir = path.join(path.dirname(path.realpath(__file__)), 'static')
bg_file = path.join(static_dir, 'images/tek_cfg_001.jpg')
curs_file = path.join(static_dir, 'images/blu_turtle.png')

# Always use "convert()". It adjusts the image to the depth of the display, speeding up drawing
background = pygame.image.load(bg_file).convert()
# Use "convert_alpha()" if the image has transparency.
mouse_cursor = pygame.image.load(curs_file).convert_alpha()

while True:

    # pylint says QUIT, quit() etc are undefined, but they're not. Works fine.
    for event in pygame.event.get():
        if event.type == QUIT:           # pylint: disable=undefined-variable
            pygame.quit()                # pylint: disable=no-member
            exit()
        # Catch the q-key
        # Catch the ctrl-q key - combine keys with mods using and-wise operator
        elif event.type == KEYUP:        # pylint: disable=undefined-variable
            if event.key in (K_q, K_q & KMOD_CTRL):         # pylint: disable=undefined-variable
                pygame.quit()            # pylint: disable=no-member
                exit()

        # blit background pic into buffer
        # coordinate 0,0 is upper-left corner of display
        screen.blit(background, (0, 0))

        # We are basically drawing over the cursor
        # Adjust the cursor-pic location so it feels like cursor is in middle of it
        # blit the "cursor" image into buffer
        x, y = pygame.mouse.get_pos()
        x -= mouse_cursor.get_width() / 2
        y -= mouse_cursor.get_height() / 2
        screen.blit(mouse_cursor, (x, y))

        # Update moves images from block buffer to display
        pygame.display.update()
