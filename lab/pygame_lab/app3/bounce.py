# coding: utf-8
#!/usr/bin/python3

"""
An intro to pygame. From www.pygame.org/docs/tut/intro/intro.html
There are many, many nice examples and tutorials for pygame online.
And I have two books with Pygame examples.

This is another simple intro to basic concepts.
For next level, check out something like www.pygame.org/docs/tut/chimp/ChimpLineByLine.html
"""

# pylint: disable=unused-wildcard-import
# pylint: disable=undefined-variable
# pylint: disable=no-member
import pygame
import time
# This provides constants like MOUSEMOTION, QUIT and so forth:
from pygame.locals import *
from sys import exit
from os import path
from pprint import pprint as pp

static_dir = path.join(path.dirname(path.realpath(__file__)), 'static')
# Sound worked fine with an .ogg file but not an .mp3
# Was able to convert .mp3 to .ogg using Audacity
sound_file = path.join(static_dir, 'sounds/Bounce.ogg')
# Resolution on the ball gif is odd. Not sure what's up with that.
ball_file = path.join(static_dir, 'images/ball.gif')
show_splash = True

# TOP-left corner is 0, 0.
# y moves TOP to BOTTOM 0..n.
speed = [1, 1]
mousex, mousey = 0, 0
# Colors can be expressed as triplets or using pygame.Color() RGB object
# RGB color for black
# black = 0, 0, 0
black = pygame.Color(0, 0, 0)
blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)
size = width, height = 800, 600

pygame.init()

# The pygame.time module provides methods for monitoring time
# The Clock object is useful for tracking time, frames per second and so on
gameClock = pygame.time.Clock()
gameClock.tick(30)

# set_mode() creates a display "surface"
screen = pygame.display.set_mode(size, DOUBLEBUF|HWSURFACE, 32)
# Set the window title
pygame.display.set_caption('Bouncing Ball')

# Load images to a "foreground surface". convert() to same depth as surface
# When I do NOT convert() the ball, this image renders more correctly.
# ball = pygame.image.load(ball_file).convert()
ball = pygame.image.load(ball_file)

# Create a sound object from a file or stream
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=8192)
soundObj = pygame.mixer.Sound(file=sound_file)

# Create a font object.  Also see pygame.freetype.Font <-- look into this
# Specifying a font of None means to use the default pygame font.
# font_path = pygame.font.match_font('cabin')
# font_path = pygame.font.match_font('uroob')
# font_path = pygame.font.match_font('bitstreamcharter')
font_path = pygame.font.match_font('carlito')
fontObj = pygame.font.Font(font_path, 24)
msg = 'Type Q or Ctl-Q to quit. Type C to clear or restore this message'
msgObj = fontObj.render(msg, True, white)
msgRect = msgObj.get_rect()
msgRect.topleft = (10,20)

# get_rect() for a loaded surface object defaults to a location of 0, 0
# Use center argument to set starting point for ball rect
ballrect = ball.get_rect(center=(320,240))

# Game Loop
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			exit()
		elif event.type == KEYUP:
			if event.key in (K_q, K_q & KMOD_CTRL):
				pygame.quit()
				exit()
			elif event.key == K_c:
				show_splash = False if show_splash else True
		elif event.type == pygame.MOUSEMOTION:
			# Respond to mouse movement
			# Compare to app0. This another way of overlyaing/reacting to mouse movement
			mousex, mousey = event.pos
			ballrect = ball.get_rect(center=(mousex,mousey))
			screen.fill(black)
			screen.blit(ball, ballrect)

	if show_splash:
		# Blit the message to a buffer
		screen.blit(msgObj, msgRect)
		# diplay.update() actually refreshes only a specified rectangle within the display
		# passing no arguments, update() is the same thing as flip()
		# Pass the mouse over this section and you'll see the ball in the background.
		pygame.display.update(msgRect)
	else:
		# move() translates the rectangle according to given offset.
		# We defaulted it to [1, 1] (right, down) and will keep the absolute value (1 pixel)
		# but change direction when the ball hits the sides of background surface.
		ballrect = ballrect.move(speed)
		# Even with minimum movement of 1, the ball moves very fast
		# Slow it down with a 5 millisecond delay
		time.sleep(.005)
		if ballrect.left < 0 or ballrect.right > width:
			soundObj.play()
			speed[0] = -speed[0]
		if ballrect.top < 0 or ballrect.bottom > height:
			soundObj.play()
			speed[1] = -speed[1]
		# To make erasing easy, we just fill the whole screen with black each iteration
		screen.fill(black)
		screen.blit(ball, ballrect)
		# display.flip() refreshes the entire display
		pygame.display.flip()
