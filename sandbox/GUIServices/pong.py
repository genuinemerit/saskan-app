#!/usr/bin/python3.9
"""
:module:    pong.py
:kv:        pong.kv

:author:    GM (genuinemerit @ pm.me)

Tutorial program for Kivy.

    This program is a simple pong game.
    See: https://kivy.org/doc/stable/tutorials/pong.html

It works in synch with a .kv file. Since the "App" class is
named "PongApp", the .kv file must be named "pong.kv".
The .kv file is located in the same directory as this file.

Widgets:
- PongPaddle --> handles collision physics
- PongBall   --> handles movement physics = ball velocity
- PongGame   --> handles game logic methods:
    - serve
    - update
    - touch

App:
- PongApp --> Manages game loop by calling PongGame update() method
              every frame.
              See kivy-examples for asyncio to learn how to use the
              asyncio event loop.
"""
import kivy                   # type: ignore

from kivy.app import App      # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.properties import (BooleanProperty, NumericProperty)  # type: ignore
from kivy.properties\
    import (ObjectProperty, ReferenceListProperty)  # type: ignore
from kivy.uix.widget import Widget  # type: ignore
from kivy.vector import Vector      # type: ignore

kivy.require('2.0.0')


class PongPaddle(Widget):
    score = NumericProperty(0)
    can_bounce = BooleanProperty(True)

    def bounce_ball(self, ball):
        if self.collide_widget(ball) and self.can_bounce:
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            # Vector is a class from kivy.vector.
            # See: https://kivy.org/doc/stable/api-kivy.vector.html
            # The Vector class is used to represent a 2D vector.
            # The Vector class has a x and y attribute.
            # The Vector class has a magnitude and angle attribute.
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset
            self.can_bounce = False
        elif not self.collide_widget(ball) and not self.can_bounce:
            self.can_bounce = True


class PongBall(Widget):
    """NumericProperty and ReferenceListProperty are
       part of the kivy.properties module. We imported them above.

    Things to get familiar with:
    - https://kivy.org/doc/stable/api-index.html
    - https://kivy.org/doc/stable/api-kivy.properties.html
    """
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    """ObjectProperty gets a bit 'meta-meta'. This is saying that
       we are going to use these as attributes of the class, but
       the assignments will occur in the .kv file rather than in
       the python module."""
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        # bounce ball off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went off a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
