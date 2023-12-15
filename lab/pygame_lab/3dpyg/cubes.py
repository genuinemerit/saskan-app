#!python
"""
@package: cubes
:classes:
- CubesCanvas
- Cubes
- GameLoop

Experimental pygame game -- creating 3D cubes
Note that pygame does not natively support 3D graphics. This is a hack.
Some website claims to support 3D in Pygame are pure garbage. Others are useful.
For real high-end 3D graphics, use a real 3D graphics library.

Complete garbage ==>: https://gamedevacademy.org/pygame-3d-tutorial-complete-guide/
Actually useful --> https://www.petercollingridge.co.uk/tutorials/3d/pygame

Basic references:
See: https://www.pg.org/docs/ref/draw.html
See: https://www.pg.org/docs/ref/draw.html#pg.draw.rect
See: https://www.pg.org/docs/ref/draw.html#pg.draw.polygon
See: https://www.pg.org/docs/ref/draw.html#pg.draw.circle
See: https://www.pg.org/docs/ref/draw.html#pg.draw.ellipse
See: https://www.pg.org/docs/ref/draw.html#pg.draw.arc
See: https://www.pg.org/docs/ref/draw.html#pg.draw.line
See: https://www.pg.org/docs/ref/draw.html#pg.draw.lines
"""
import math
import pygame as pg
import pygame.draw
import random
import pendulum

from os import path
from pprint import pprint as pp
from pygame.locals import (
    K_ESCAPE,
    K_c, K_f, K_q, K_r, K_w, K_x,
    KEYUP,
    QUIT,
    DOUBLEBUF,
    HWSURFACE
)
from sys import exit
from tornado.options import define, options


class CubesCanvas(object):
    """
    Set configurations for the game context, nominally a "canvas"
    """
    def __init__(self):
        # counters and flags
        self.frame_cnt = 0
        self.freeze_mode = False
        #colors
        self.black = pg.Color(0, 0, 0)
        self.white = pg.Color(255, 255, 255)
        self.red = pg.Color(255, 0, 0)
        self.pink = pg.Color(215, 198, 198)
        self.green = pg.Color(0, 255, 0)
        self.blue = pg.Color(0, 0, 255)
        self.silver = pg.Color(192, 192, 192)
        #fonts
        self.key_font = pg.font.Font(None, 24)
        self.cube_font = pg.font.Font(None, 18)
        # sprites location
        self.img_dir = path.join(path.dirname(path.realpath(__file__)), 'images')
        # Display (window) configurations
        self.display = pg.display.set_mode((1290, 960), DOUBLEBUF|HWSURFACE, 32)
        self.mid_x = 1290 / 2
        self.mid_y = 960 / 2
        area = self.display.get_rect()
        self.screen_width, self.screen_height = (area[2], area[3])
        self.play_width = self.screen_width * 0.85
        self.play_height = self.screen_height * 0.90
        self.mid_x_play = self.play_width / 2
        self.mid_y_play = self.play_height / 2
        pg.display.set_caption("Cubes")
        # key-text object
        title_text = "Draw/Hide: c(ube) | Refresh: r | (Un)Freeze: f |  Quit: q, x, w or ESC"
        self.key_img = self.key_font.render(title_text, True, self.pink, self.black)
        # timer
        self.cooldown = 1000  # milliseconds

    def draw_key_text(self):
        """ Refresh message-key text with generation info"""
        gen_text = "Generation: " + str(self.frame_cnt)
        gen_img = self.key_font.render(gen_text, True, self.pink, self.black)
        self.display.blit(self.key_img, self.key_img.get_rect(topleft=(60, 910)))
        self.display.blit(gen_img, gen_img.get_rect(topleft=(800, 910)))

class Cubes(object):
    """
    Manage a collection of Cubes and related objects.
    """
    def __init__(self, canvas):
        """
        Initialize Cubes collection.
        """
        self.canvas = canvas
        # pre-defined objects
        self.o = {'spaces': {},
                  'cubes': {'small': {'color': (204, 204, 204),
                                      'rect': (150, 150, 50, 50)}},
                  'spheres': {}}
        # currently active widgets
        self.w = {'spaces': [], 'cubes': [], 'spheres': []}

    def draw_grid(self):
        """
        Draw 3D Cartesian space
        """
        pass
        # render to buffer
        # self.canvas.display.blit(turt_img, row['turt_rect'])
        # self.canvas.display.blit(text_img, text_img.get_rect(topleft=(text_x, text_y)))

    def set_cube(self,
                 p_cube: str):
        """
        Add or remove a cube from list of cubes to draw.
        :args:
        - p_cube: str - ID of cube to add or remove
        """
        if p_cube not in self.w['cubes']:
            self.w['cubes'].append(p_cube)
        else:
            self.w['cubes'].remove(p_cube)

    def draw_cubes(self):
        """
        Draw cube(s) based on currently active widgets.
        """
        for c in self.w['cubes']:
            cube = self.o['cubes'][c]
            pg.draw.rect(self.canvas.display,
                         cube['color'], pg.Rect(cube['rect']))
            pg.display.flip()

    def draw_sphere(self):
        """
        Draw a sphere. Pass in references to sphere objects.
        """
        pass
        # self.canvas.display.blit(mean_bump_img, mean_bump_img.get_rect(center=(turt_x - 10, turt_y - 10)))

    def set_coords(self, dir_x, dir_y, dir_z):
        """
        Calculate new coordinates for an object
        """
        pass
        # return (str(turt_x), str(turt_y))

    def revise_coords(self, dir_x, dir_y, dir_z, obj_id):
        """
        Set new coordinates for an object.
        """
        pass
        # return(mod_row)

    def anim_cubes(self):
        """
        Move all objects
        """
        pass


class GameLoop(object):
    """
    Cubes set-up and game loop.
    """
    def __init__(self):
        """ Initialize Game. """
        self.clock = pg.time.Clock()
        self.canvas = CubesCanvas()
        self.cubes = Cubes(self.canvas)
        self.main_loop()

    def kill(self):
        """ Tidy up and shut down the app"""
        pg.quit()
        exit()

    def main_loop(self):
        """ Manage main game loop 
        """
        running = True
        while running:
            self.canvas.frame_cnt += 1
            # trap for events
            for event in pg.event.get():
                if event.type == QUIT:
                    running=False
                if event.type == KEYUP:
                    if event.key == K_r:
                        self.canvas.display.fill(self.canvas.black)
                        GameLoop()
                    elif event.key == K_c:
                        self.cubes.set_cube('small')
                    elif event.key in (K_q, K_x, K_w, K_ESCAPE):
                        running=False
                    elif event.key == K_f:
                        self.canvas.freeze_mode = not self.canvas.freeze_mode
            if self.canvas.freeze_mode == False:
                self.canvas.display.fill(self.canvas.black)    # wipe screen
                self.canvas.draw_key_text()
                # self.cubes.draw_grid()
                self.cubes.draw_cubes()
                # self.cubes.draw_cube()
                # self.cubes.draw_sphere()

                pg.display.flip()
                pg.time.delay(self.canvas.cooldown) # easy to slow down, harder to speed up

                # self.clock.tick(30)  # Desired framerate (frames per sec)
                self.clock.tick(60)  # maybe faster ?
                # self.clock.tick(60)  # faster, but not necessarily. This is At Most fps.
                # This provides good metrics if using the .tick() method:
                # logging.info("average FPS: {}".format(str(self.clock.get_fps())))

                # alternatively, use pg.time.wait() or pg.time.delay()
                # to specify milliseconds of delay. tick() uses a lot of CPU;
                # that's why you hear the fan kicking in
                # And logging the average frames per second shows how my game
                #  slows down the longer my turtles are interacting - a design issue
                # pg.time.delay(self.cooldown)   #milliseconds
                # pg.time.wait(self.cooldown)   #milliseconds
                # All of the timers seem to work equally well. .wait() puts slightly
                # less burden on the CPU. The problem is the same with all of them...
                # too much increase in animation frame over frame. Need to "kill off"
                # my turtles faster. :-)
        self.kill()
        

if __name__ == '__main__':
    pg.init()
    GameLoop()
