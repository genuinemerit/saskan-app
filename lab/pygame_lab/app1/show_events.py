# coding: utf-8
#!/usr/bin/python3

"""
From Beginning Python Games Development with Pygame, 2nd ed.

Type 'q' key or CTRL-q to quit.
If frame is visible, can "X" out.
If app-level menu is visible, can select "Quit" from menu.

Simple black window. Display all event information in console.
Try moving mouse around, clicking, typing various keys and mod-key combos
"""

import pygame
from pygame.locals import *         # pylint: disable=unused-wildcard-import
from os import path
from sys import exit

pygame.init() # pylint: disable=no-member
screen = pygame.display.set_mode((800, 600), DOUBLEBUF|HWSURFACE)           # pylint: disable=undefined-variable

pygame.display.set_caption("Show Pygame Events")

while True:

    for event in pygame.event.get():
        if event.type == QUIT:           # pylint: disable=undefined-variable
            pygame.quit()                # pylint: disable=no-member
            exit()
        elif event.type == KEYUP:        # pylint: disable=undefined-variable
            if event.key in (K_q, K_q & KMOD_CTRL):         # pylint: disable=undefined-variable
                pygame.quit()            # pylint: disable=no-member
                exit()

        print(event)
        pygame.display.update()
