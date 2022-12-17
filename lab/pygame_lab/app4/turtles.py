# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
@package: turtles

Experimental pygame game -- swarming turtles having interactions
"""
# pylint: disable=unused-wildcard-import
# pylint: disable=undefined-variable
# pylint: disable=no-member
import logging
import math
import pandas as pd
import pygame
import random
import time
# Package sub-imports
from os import chdir, getcwd, listdir, path, remove
from pprint import pprint as pp
from pygame.locals import *
from sys import exit
from tornado.options import define, options
# Local imports
from log.logger import logger

class config_canvas(object):
    """
    Set standard constant configurations for the game context, nominally a "canvas"
    """
    def __init__(self):
        # options
        define_items = list()
        define_items = ['bale_size', 'bale_names', 'cooldown',
                        "mark_trail", "length_trail", "max_move"]
        for item in define_items:
            define(item)
        script_path = path.abspath(path.realpath(__file__))
        script_dir = path.split(script_path)[0]
        config_file = path.abspath(path.join(script_dir, 'turtles.conf'))
        options.parse_config_file(config_file)
        self.bale_size = int(options.bale_size)              # number of turtles in a clutch
        self.bale_names = options.bale_names.split(',')      # prefixes to image resources
        self.cooldown = int(options.cooldown)                # milliseconds
        self.mark_trail = int(options.mark_trail)            # mark the trail every n frames
        self.max_move = int(options.max_move)                # max number pixels turtle can move in a frame
        self.length_trail = int(options.length_trail)        # how many trail markers
        # counters and flags
        self.frame_cnt = 0
        self.freeze_mode = False
        #colors
        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.pink = pygame.Color(215, 198, 198)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)
        self.silver = pygame.Color(192, 192, 192)
        #fonts
        self.key_font = pygame.font.Font(None, 24)
        self.turt_font = pygame.font.Font(None, 18)
        # sprites location
        self.img_dir = path.join(path.dirname(path.realpath(__file__)), 'static/images')
        # Display (window) configurations
        self.display = pygame.display.set_mode((1290, 960), DOUBLEBUF|HWSURFACE, 32)
        self.mid_x = 1290 / 2
        self.mid_y = 960 / 2
        area = self.display.get_rect()
        self.screen_width, self.screen_height = (area[2], area[3])
        self.play_width = self.screen_width * 0.85
        self.play_height = self.screen_height * 0.90
        self.mid_x_play = self.play_width / 2
        self.mid_y_play = self.play_height / 2
        pygame.display.set_caption("Turtle Swarm")
        # key-text object
        title_text = "Refresh: r | (Un)Freeze: f |  Quit: q, x, w or ESC"
        self.key_img = self.key_font.render(title_text, True, self.pink, self.black)

    def draw_key_text(self):
        """ Refresh message-key text with generation info"""
        gen_text = "Generation: " + str(self.frame_cnt)
        gen_img = self.key_font.render(gen_text, True, self.pink, self.black)
        self.display.blit(self.key_img, self.key_img.get_rect(topleft=(60, 910)))
        self.display.blit(gen_img, gen_img.get_rect(topleft=(800, 910)))

class Turtles(object):
    """
    Manage a collection of Turtle objects.
    """
    def __init__(self, canvas):
        """
        Initialize Turtles collection.
        A 'bale' is a family of turtles.
        A 'mark' are the breadcrumbs from where a turtle has been
        'Bumps' occur due to interactions with other turtles (eventually, other creatures)
        They may be good (up) or bad (down)
        A 'glow' is the result of having good bumps
        """
        self.canvas = canvas
        self.life_phase = {
            'juvenile':3,
            'young':5,
            'active':10,
            'middle':20,
            'senior':40,
            'old':60,
            'ancient':999999
        }
        # Using pandas dataframe may speed things up.
        turt_cols = ["bale_home", "bale_name",
                     "turt_loc", "turt_id", "turt_img_path", "turt_rect",
                     "born_frame", "age", "life_force", "phase", "is_ill",
                     "glows", "mean_bumps", "nice_bumps",
                     "dir_x", "dir_y", "trail"]
        turts_list = list()
        for bale_name in self.canvas.bale_names:
            bale_x = random.randint(-300, 300) + self.canvas.mid_x_play
            bale_y = random.randint(-300, 300) + self.canvas.mid_y_play
            for bale_id in range(1, self.canvas.bale_size + 1):
                    bale_home = str(bale_x) + ":" + str(bale_y)
                    turt_x = random.randint(-80, 80) + bale_x
                    turt_y = random.randint(-80, 80) + bale_y
                    turt_loc = str(turt_x) + ":" + str(turt_y)
                    turt_id = bale_name[:1] + str(bale_id)
                    turt_img_path = path.join(self.canvas.img_dir, bale_name + "_turtle.png")
                    turt_rect = pygame.image.load(turt_img_path).get_rect(center=(turt_x, turt_y))
                    dir_x = -1 if random.randint(-10, 10) < 0 else 1
                    dir_y = -1 if random.randint(-10, 10) < 0 else 1
                    turts_list.append((
                        bale_home, bale_name,
                        turt_loc, turt_id, turt_img_path, turt_rect,
                        0, "y:0, m:0", 500.0, "juvenile", "N",
                        0, 0, 0,
                        dir_x, dir_y, ""
                    ))
        self.turts_df = pd.DataFrame.from_records(turts_list, columns=turt_cols)
        # LOG.write_log(LOG.INFO, "Turtles initialized:  {}".format(self.turts_df))

    def draw_turtles(self):
        """
        Draw all Turtles
        """
        text_y = 10
        for _, row in self.turts_df.iterrows():
            # load turtle image
            turt_img = pygame.image.load(row['turt_img_path'])
            # get turtle info
            turt_events = ''
            if row['mean_bumps'] > 0:
                turt_events += 'M'
            if row['nice_bumps'] > 0:
                turt_events += 'N'
            if row['glows'] > 0:
                turt_events += 'G'
            turt_text = str(row['turt_id']) +\
                        '/' + str(row['phase']) +\
                        '/' + str(row['age']) +\
                        '/{:.0f}'.format(row['life_force']) +\
                        '/{}'.format(turt_events)
            # format turtle info
            text_img = self.canvas.turt_font.render(turt_text, True, self.canvas.silver, self.canvas.black)
            text_x = self.canvas.play_width + 10  # left side of info text
            text_y = text_y + 12                  # top side of infotext
            # render to buffer
            self.canvas.display.blit(turt_img, row['turt_rect'])
            self.canvas.display.blit(text_img, text_img.get_rect(topleft=(text_x, text_y)))

    def draw_trails(self):
        """
        Draw trails showing where turtles have been
        """
        trail_imgs = {
            'red': pygame.image.load(path.join(self.canvas.img_dir, "red_mark.png")),
            'blu': pygame.image.load(path.join(self.canvas.img_dir, "blu_mark.png")),
            'grn': pygame.image.load(path.join(self.canvas.img_dir, "grn_mark.png"))
        }
        for _, df_row in self.turts_df.iterrows():
            trail_img = trail_imgs[df_row['bale_name']]
            trail = df_row['trail'].split(',')
            if len(trail) > 1 or (len(trail) == 1 and trail[0] != ''):
                for trail_loc in trail:
                    trail_xy = trail_loc.split(':')
                    trail_x, trail_y = (float(trail_xy[0]), float(trail_xy[1]))
                    self.canvas.display.blit(trail_img, trail_img.get_rect(center=(trail_x, trail_y)))

    def draw_bumps_and_glows(self):
        """
        Draw bumps showing where collions between turtles took place
        """
        glow_imgs = {
            'red': pygame.image.load(path.join(self.canvas.img_dir, "red_glow.png")),
            'blu': pygame.image.load(path.join(self.canvas.img_dir, "blu_glow.png")),
            'grn': pygame.image.load(path.join(self.canvas.img_dir, "grn_glow.png"))
        }
        mean_bump_img = pygame.image.load(path.join(self.canvas.img_dir, "bump_mean.png"))
        nice_bump_img = pygame.image.load(path.join(self.canvas.img_dir, "bump_nice.png"))
        for ix, df_row in self.turts_df.iterrows():
            turt_loc = df_row['turt_loc'].split(':')
            turt_x, turt_y = (float(turt_loc[0]), float(turt_loc[1]))
            if df_row['mean_bumps'] > 0:
                # Need to figure out more about where the bump happened
                self.canvas.display.blit(mean_bump_img, mean_bump_img.get_rect(center=(turt_x - 10, turt_y - 10)))
                self.turts_df.at[ix, 'mean_bumps'] = 0
            if df_row['nice_bumps'] > 0:
                self.canvas.display.blit(nice_bump_img, nice_bump_img.get_rect(center=(turt_x + 10, turt_y - 10)))
                self.turts_df.at[ix, 'nice_bumps'] = 0
            if df_row['glows'] > 0:
                glow_img = glow_imgs[df_row['bale_name']]
                self.canvas.display.blit(glow_img, glow_img.get_rect(center=(turt_x - 20, turt_y - 20)))
                self.turts_df.at[ix, 'glows'] = 0

    def move_one_turtle(self, df_row):
        """
        Move one turtle

        :Return: {dict} one modified data row in the Turtles dataframe
        """
        def set_direction(df_row):
            """
            Decide whether to change direction
            """
            dir_x = int(df_row['dir_x'])
            dir_y = int(df_row['dir_y'])
            dir_x = dir_x * -1 if random.randint(-10, 10) < 0 else dir_x
            dir_y = dir_y * -1 if random.randint(-10, 10) < 0 else dir_y

            return (dir_x, dir_y)

        def set_coords(dir_x, dir_y, df_row):
            """
            Calculate new coordinates for a turtle
            """
            turt_loc = df_row['turt_loc'].split(':')
            turt_x = float(turt_loc[0])
            turt_y = float(turt_loc[1])
            max_move = self.canvas.max_move
            turt_x = turt_x + (random.randint(1, max_move) * dir_x)
            turt_y = turt_y + (random.randint(1, max_move) * dir_y)
            if turt_x < 12:
                turt_x = 20
            elif turt_x > (self.canvas.play_width - 12):
                turt_x = self.canvas.play_width - 20
            if turt_y < 12:
                turt_y = 20
            elif turt_y > (self.canvas.play_height - 12):
                turt_y = self.canvas.play_height - 20
            return (str(turt_x), str(turt_y))

        def revise_location(dir_x, dir_y, turt_x, turt_y, df_row):
            """
            Set new coordinates for a turtle
            return {dict} modified, refreshed Turtles data row
            """
            mod_row = dict(df_row)
            mod_row['dir_x'] = dir_x
            mod_row['dir_y'] = dir_y
            mod_row['turt_loc'] = turt_x + ":" + turt_y
            turt_img_path = path.join(self.canvas.img_dir, df_row['bale_name'] + "_turtle.png")
            mod_row['turt_rect'] = pygame.image.load(turt_img_path).get_rect(center=(float(turt_x), float(turt_y)))
            return(mod_row)

        def revise_age(mod_row):
            """
            Compute and set turtle age in years and months
            Revise life_phase too

            return {tuple} (years of age, refreshed Turtles data row)
            """
            frames_alive = self.canvas.frame_cnt - int(mod_row['born_frame'])
            years = math.floor(frames_alive / 365)
            rem = (frames_alive / 365) - years
            months = math.floor(12 * rem)
            mod_row['age'] = "{}:{}".format(str(years), str(months))
            for phase, ph_years in self.life_phase.items():
                if years <= ph_years:
                    mod_row['phase'] = phase
                    break

            return (years, mod_row)

        def set_age_and_illness(years, mod_row):
            """
            Provide changes to age and illness status

            return {tuple} (life_force_adjustment factor, illness factor)
            """
            lf_factor = 0.0
            ill_factor = 0.0
            if years <= self.life_phase['juvenile']:
                lf_factor = 0.15
                ill = random.randint(-20,10)
            elif years <= self.life_phase['young']:
                lf_factor = 0.1
                ill = random.randint(-10,20)
            elif years <= self.life_phase['active']:
                lf_factor = 0.05
                ill = random.randint(-15,15)
            elif years <= self.life_phase['middle']:
                lf_factor = 0.02
                ill = random.randint(-20,10)
            elif years <= self.life_phase['senior']:
                lf_factor = 0.01
                ill = random.randint(-30,10)
            elif years <= self.life_phase['old']:
                lf_factor = 0.0
                ill = random.randint(-40,10)
            else:
                lf_factor = -0.1
                ill = random.randint(-50,10)
            if ill < 0:
                ill_factor = ill / 100

            return (lf_factor, ill_factor)

        def set_life_force_age_ill(lf_factor, ill_factor, mod_row):
            """
            Modify age, illness status, life force and image based on adjustment factors

            return {dict} modified data row
            """
            life_force = mod_row['life_force']
            life_force = life_force + (life_force / 365 * lf_factor)
            if ill_factor < 0.0:
                mod_row['is_ill'] = 'Y'
                life_force = life_force + (life_force / 365 * ill_factor)
                mod_row['turt_img_path'] = path.join(self.canvas.img_dir, mod_row['bale_name'] + "_turtle_ill.png")
            else:
                mod_row['is_ill'] = 'N'
                mod_row['turt_img_path'] = path.join(self.canvas.img_dir, mod_row['bale_name'] + "_turtle.png")
            mod_row['life_force'] = round(life_force, 5)
            return mod_row

        def revise_data_row(mod_row, df_row):
            """
            Modify data frame row based on adjustments made
            """
            for key in mod_row.keys():
                if key not in ('turt_loc', 'dir_x', 'dir_y',
                               'age', 'phase', 'life_force', 'is_ill',
                               'turt_img_path', 'turt_rect'):
                    mod_row[key] = df_row[key]
            return mod_row

        # move_one() main
        dir_x, dir_y = set_direction(df_row)
        turt_x, turt_y = set_coords(dir_x, dir_y, df_row)
        mod_row = revise_location(dir_x, dir_y, turt_x, turt_y, df_row)
        years, mod_row = revise_age(mod_row)
        lf_factor, ill_factor = set_age_and_illness(years, mod_row)
        mod_row = set_life_force_age_ill(lf_factor, ill_factor, mod_row)
        mod_row = revise_data_row(mod_row, df_row)
        return mod_row

    def mark_trail(self, df_row):
        """
        For every mark_trail frames, record where the turtle has been
        """
        mod_row = dict(df_row)
        trail = df_row['trail'].split(',')
        if len(trail) == 0:
            trail = list()
        if len(trail) > self.canvas.length_trail:
            trail.pop(0)
        # append the current location to trails list
        trail.append(df_row['turt_loc'])
        if len(trail) == 1:
            mod_row['trail'] = trail[0]
        else:
            mod_row['trail'] = ','.join(trail)
        # remove leading comma or comma-space from string-representation of list
        if mod_row['trail'][:2] == ', ':
            mod_row['trail'] = mod_row['trail'][2:]
        elif  mod_row['trail'][:1] == ',':
            mod_row['trail'] = mod_row['trail'][1:]

        for key in mod_row.keys():
            if key not in ('trail'):
                mod_row[key] = df_row[key]
        return mod_row

    def mark_bumps_and_glows(self, df_row_L, df_row_R):
        """
        Compute bumps and store the bump info for current turtle-row
        Compute glows and store the glow info for current turtle-row
        """
        def set_life_force_bumps_glows(mod_row):
            """
            Adjust life force based on bumps and glows
            """
            life_force = int(mod_row['life_force'])
            life_force = life_force - (mod_row['mean_bumps'] * 100)\
                                    + (mod_row['nice_bumps'] * 100)\
                                    + (mod_row['glows'] * 50)
            mod_row['life_force'] = life_force
            return mod_row

        mod_row = dict(df_row_L)
        if df_row_L['turt_id'] != df_row_R['turt_id']:
            rect_L = df_row_L['turt_rect']
            rect_R = df_row_R['turt_rect']
            if df_row_L['bale_name'] == df_row_R['bale_name']:
                if rect_L.colliderect(rect_R) or rect_R.colliderect(rect_L):
                    if random.randint(-5, 10) > 0:
                        mod_row['glows'] += 1
            else:
                if rect_L.colliderect(rect_R) or rect_R.colliderect(rect_L):
                    if random.randint(-10, 10) < 0:
                        mod_row['mean_bumps'] += 1
                    else:
                        mod_row['nice_bumps'] += 1

        mod_row = set_life_force_bumps_glows(mod_row)

        for key in mod_row.keys():
            if key not in ('mean_bumps', 'nice_bumps', 'glows', 'life_force'):
                mod_row[key] = df_row_L[key]
        return mod_row

    def move_turtles(self):
        """
        Move all turtles
        Compute marks, bumps, glows, life-force
        """
        def update_df(mod_row):
            """
            Apply changes to the dataframe
            """
            for key, val in mod_row.items():
                self.turts_df.at[ix, key] = val

        for ix, row in self.turts_df.iterrows():
            update_df(self.move_one_turtle(row))

        if (self.canvas.frame_cnt % self.canvas.mark_trail) == 0:
            for ix, row in self.turts_df.iterrows():
                update_df(self.mark_trail(row))

        for ix, row_left in self.turts_df.iterrows():
            for _, row_right in self.turts_df.iterrows():
                update_df(self.mark_bumps_and_glows(row_left, row_right))

class GameLoop(object):
    """
    Turtle Swarm set-up and game loop.
    """
    def __init__(self):
        """ Initialize Game. """
        self.clock = pygame.time.Clock()
        self.canvas = config_canvas()
        self.turtles = Turtles(self.canvas)
        # LOG.write_log(LOG.INFO, "Game initialized")
        self.main_loop()

    def kill(self):
        """ Tidy up and shut down the app"""
        pygame.quit()
        LOG.close_logs()
        exit()

    def main_loop(self):
        """ Manage main game loop """
        while True:
            self.canvas.frame_cnt += 1
            # trap for events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.kill()
                if event.type == KEYUP:
                    if event.key == K_r:
                        self.canvas.display.fill(self.canvas.black)
                        GameLoop()
                    elif event.key in (K_q, K_x, K_w, K_ESCAPE):
                        self.kill()
                    elif event.key == K_f:
                        self.canvas.freeze_mode = not self.canvas.freeze_mode
            if self.canvas.freeze_mode == False:
                # wipe screen
                self.canvas.display.fill(self.canvas.black)
                self.canvas.draw_key_text()
                self.turtles.draw_trails()
                self.turtles.draw_bumps_and_glows()
                self.turtles.draw_turtles()
                self.turtles.move_turtles()

                pygame.display.flip()
                pygame.time.delay(self.canvas.cooldown) # easy to slow down, harder to speed up

                # self.clock.tick(30)  # Desired framerate (frames per sec)
                self.clock.tick(60)  # maybe faster ?
                # self.clock.tick(60)  # faster, but not necessarily. This is At Most fps.
                # This provides good metrics if using the .tick() method:
                # logging.info("average FPS: {}".format(str(self.clock.get_fps())))

                # alternatively, use pygame.time.wait() or pygame.time.delay()
                # to specify milliseconds of delay. tick() uses a lot of CPU;
                # that's why you hear the fan kicking in
                # And logging the average frames per second shows how my game
                #  slows down the longer my turtles are interacting - a design issue
                # pygame.time.delay(self.cooldown)   #milliseconds
                # pygame.time.wait(self.cooldown)   #milliseconds
                # All of the timers seem to work equally well. .wait() puts slightly
                # less burden on the CPU. The problem is the same with all of them...
                # too much increase in animation frame over frame. Need to "kill off"
                # my turtles faster. :-)

if __name__ == '__main__':
    LOG = logger()
    LOG.set_logs()
    pygame.init()
    GameLoop()
