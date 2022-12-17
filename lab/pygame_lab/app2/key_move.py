# coding: utf-8
#!/usr/bin/python3

"""
From Beginning Python Games Development with Pygame, 2nd ed.
Example of trapping for key strokes

Use up, down, left, right arrow keys to move the "background" picture
Also note use of screen.fill() to keep a truly clean (black) background
"""
# pylint: disable=unused-wildcard-import
# pylint: disable=undefined-variable
# pylint: disable=no-member
import pygame
from pygame.locals import *
from os import path
from sys import exit

static_dir = path.join(path.dirname(path.realpath(__file__)), 'static')
bg_file = path.join(static_dir, 'images/tek_cfg_001.jpg')

pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF|HWSURFACE, 32)
pygame.display.set_caption("Demonstrate key strokes")
background = pygame.image.load(bg_file).convert()
x, y = 0, 0
move_x, move_y = 0, 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYUP:
            if event.key in (K_q, K_q & KMOD_CTRL):
                pygame.quit()
                exit()

        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                move_x = -1
            elif event.key == K_RIGHT:
                move_x = +1
            elif event.key == K_UP:
                move_y = -1
            elif event.key == K_DOWN:
                move_y = +1
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                move_x = 0
            elif event.key == K_RIGHT:
                move_x = 0
            elif event.key == K_UP:
                move_y = 0
            elif event.key == K_DOWN:
                move_y = 0

        x += move_x
        y += move_y

        screen.fill((0, 0, 0))   # 0,0,0 = color = black
        screen.blit(background, (x, y))

        pygame.display.update()
