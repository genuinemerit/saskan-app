# coding: utf-8
#!/usr/bin/python3

"""
My first attempt at designing and implementing a game of my own design.
The idea is that turtles emerge from the ocean, lay eggs, return to ocean.
And do with without getting eaten or murdered

Some or all of this probably needs to be turned into one or more Classes...

...which is exactly what I did in turtles_02.py.  Don't even bother with this module.
Just keeping it around to show how my thought processes developed.
"""

# pylint: disable=unused-wildcard-import
# pylint: disable=undefined-variable
# pylint: disable=no-member
import pygame
import random
import time
from collections import OrderedDict
from os import path
from pprint import pprint as pp
from pygame.locals import *
from sys import exit

def static_dir():
    return path.join(path.dirname(path.realpath(__file__)), 'static')

def colors():
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    red = pygame.Color(255, 0, 0)
    green = pygame.Color(0, 255, 0)
    blue = pygame.Color(0, 0, 255)
    return (black, white, red, green, blue)
(BLACK, WHITE, RED, GREEN, BLUE) = colors()

def game_fonts():
    title = pygame.font.Font(None, 32)
    info = pygame.font.Font(None, 16)
    return (title, info)
(TITLE_FONT, TITLE_INFO) = game_fonts()

def turtle_images():
    grn_t = pygame.image.load(path.join(static_dir(), "images/grn_turtle.png"))
    red_t = pygame.image.load(path.join(static_dir(), "images/red_turtle.png"))
    blu_t = pygame.image.load(path.join(static_dir(), "images/blu_turtle.png"))
    return (grn_t, red_t, blu_t)
(GRN_T, RED_T, BLU_T) = turtle_images()

def glow_images():
    grn_g = pygame.image.load(path.join(static_dir(), "images/greenglow.png"))
    red_g = pygame.image.load(path.join(static_dir(), "images/redglow.png"))
    blu_g = pygame.image.load(path.join(static_dir(), "images/blueglow.png"))
    return (grn_g, red_g, blu_g)
(GRN_G, RED_G, BLU_G) = glow_images()

def frame_info(frame_cnt):
    frame_txt = 'Frame: ' + str(frame_cnt)
    frame_obj = info_font.render(frame_txt, True, white, black)
    frame_rect = frame_obj.get_rect()
    frame_rect.topleft = (960,info_y)
    return(frame_obj, frame_rect)

def turtle_info(turtle):
    """ WTF is going on here? """
    if turtle['f'] == 'G':
        info_x = 600
    elif turtle['f'] == 'R':
        info_x = 720
    elif turtle['f'] == 'B':
        info_x = 840
    if turtle['n'] == 1:
        info_y = 30
    elif turtle['n'] == 2:
        info_y = 50
    elif turtle['n'] == 3:
        info_y = 70
    elif turtle['n'] == 4:
        info_y = 90
    elif turtle['n'] == 5:
        info_y = 110
    info_txt = turtle['f'] + str(turtle['n']) + ': ' +\
               str(turtle['r'].top) + ', ' + str(turtle['r'].left)
    info_obj = info_font.render(info_txt, True, white, black)
    info_rect = info_obj.get_rect()
    info_rect.topleft = (info_x, info_y)
    return(info_obj, info_rect)

def turtle_start(turtle, t_primo=None):
    v_turtle = turtle
    if t_primo is None:
        pos_x = random.randint(100, screen_sz['w'] - 100)
        pos_y = random.randint(100, screen_sz['h'] - 100)
    else:
        pos_x = random.randint(t_primo['r'].left - 10, t_primo['r'].right + 10)
        pos_y = random.randint(t_primo['r'].top - 10, t_primo['r'].bottom + 10)
    v_turtle['r'] = turtle['o'].get_rect(center=(pos_x, pos_y))
    return (v_turtle)

def turtle_move(turtle):
    '''
A pygame Rect: (left, top), (width, height)
move(x, y) means move the rectangle by this offset
has attributes top, left, bottom, right,
midtop, midleft, midbottom, midright
center, centerx, centery
size, width, height
w, h
    '''
    v_turtle = turtle
    # set horizontal and vertical movement at a random distance
    move_x = random.randint(1, 5)
    move_y = random.randint(1, 5)
    # randomly change horizontal direction
    rand_d = random.randint(1, 10)
    if rand_d < 3:
        v_turtle['dir_x'] *= -1;
    # randomly change vertical direction
    rand_d = random.randint(1, 10)
    if rand_d < 2:
        v_turtle['dir_y'] *= -1;
    # adjust distance by direction (compute vector)
    move_x *= turtle['dir_x']
    move_y *= turtle['dir_y']
    # bounce off the walls
    if (turtle['r'].right + move_x) > screen_sz['w'] \
    or (turtle['r'].left + move_x) < 0:
        move_x *= -1
        v_turtle['dir_x'] *= -1
    if (turtle['r'].bottom + move_y) > screen_sz['h'] \
    or (turtle['r'].top + move_y) < 0:
        move_y *= -1
        v_turtle['dir_y'] *= -1
    # set new position
    pos_x = turtle['r'].centerx + move_x
    pos_y = turtle['r'].centery + move_y
    v_turtle['r'] = turtle['o'].get_rect(center=(pos_x, pos_y))
    return (v_turtle)

def turtles_reset(turtles):
    # Sort them by key
    v_turtles = OrderedDict(sorted(turtles.items(), key=lambda t: t[0]))
    # Give them starting qualities
    for t in v_turtles:
        v_turtles[t]['dir_x'] = 1
        v_turtles[t]['dir_y'] = 1
        if v_turtles[t]['n'] == 1:
            v_turtles[t] = turtle_start(v_turtles[t])
        else:
            primo = v_turtles[t]['f'] + '1'
            v_turtles[t] = turtle_start(v_turtles[t], v_turtles[primo])
        (info_obj, info_rect) = turtle_info(v_turtles[t])
    return(v_turtles)

def fam_glows(t_id, turtles):
    # Check for collisions between members of the same turtle family.
    # At the average of their centers, blit a glow image.
    glowobj = {}
    g_cnt = 0
    t_turtle = turtles[t_id]
    t_rect = t_turtle['r']
    for tt in turtles:
        if turtles[tt]['f'] == t_turtle['f'] \
        and turtles[tt]['n'] != t_turtle['n']:
            if t_turtle['r'].colliderect(turtles[tt]['r']):
                g_cnt += 1
                pos_x = (t_turtle['r'].centerx + turtles[tt]['r'].centerx) / 2
                pos_y = (t_turtle['r'].centery + turtles[tt]['r'].centery) / 2
                glowobj[t_turtle['f'] + str(g_cnt)] = \
                    (glowimg[t_turtle['f']], glowimg[t_turtle['f']].get_rect(center=(pos_x, pos_y)))
    return(glowobj)

pygame.init()
imgdir = '../static/images/'
(title_font, info_font) = fonts()
(grn_t, red_t, blu_t) = turtle_images()
glowimg = {}
glowobj = {}
(glowimg['G'], glowimg['R'], glowimg['B']) = glow_images()

screen_sz = {'w': 1280, 'h' : 960}
screen_mid = (screen_sz['w'] / 2, screen_sz['h'] / 2)
screen = pygame.display.set_mode((screen_sz['w'], screen_sz['h']))
pygame.display.set_caption('Saskantinon')
frame_cnt = 0

title_txt = "Welcome to Saskantinon.  'r' to refresh. 'q' or 'x' to quit."
title_obj = title_font.render(title_txt, True, white, black)
title_rect = title_obj.get_rect()
title_rect.topleft = (10,20)

gameClock = pygame.time.Clock()
gameClock.tick(30)          # This is the desired framerate.
time.sleep(1)

turtles = {}
sibs = 1
# set number of turtles to create of each color
while sibs < 6:
    turtles['G' + str(sibs)] = {'o': grn_t, 'f': 'G', 'n': sibs,
                                'r': grn_t.get_rect(center=screen_mid)}
    turtles['R' + str(sibs)] = {'o': red_t, 'f': 'R', 'n': sibs,
                                'r': red_t.get_rect(center=screen_mid)}
    turtles['B' + str(sibs)] = {'o': blu_t, 'f': 'B', 'n': sibs,
                                'r': blu_t.get_rect(center=screen_mid)}
    sibs += 1
turtles = turtles_reset(turtles)

# Game Loop
while True:
    # trap for events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYUP:
            if event.key == K_r:
                screen.fill(black)
                turtles_reset()
            elif event.key == K_q or event.key == K_x:
                pygame.quit()
                sys.exit()
    # wipe screen and blit title
    screen.fill(black)
    screen.blit(title_obj, title_rect)
    for t in turtles:
        # blit turtle images
        screen.blit(turtles[t]['o'], turtles[t]['r'])
        # check for collisions and blit the family glows
        glows = fam_glows(t, turtles)
        for g in glows:
            screen.blit(glows[g][0], glows[g][1])
        # blit turtle display info
        # (info_obj, info_rect) = turtle_info(turtles[t])
        # screen.blit(info_obj, info_rect)
        # move turtles
        turtles[t] = turtle_move(turtles[t])
    # blit frame display info
    frame_cnt += 1
    # (frame_obj, frame_rect) = frame_info(frame_cnt)
    # screen.blit(frame_obj, frame_rect)
    # update display and wait
    pygame.display.update()
    pygame.time.delay(100)
    gameClock.tick(30)          # This is the desired framerate.
