#!/usr/bin/python3.9
"""
:module:    paint.py

Tutorial program for Kivy.

    This program is a simple paint program.
    See: https://kivy.org/doc/stable/tutorials/firstwidget.html

Also note that Kivy supports the use of the "KV" language,
a declartive way to define widgets outside of the python source code.

    See: https://kivy.org/doc/stable/guide/lang.html

Many examples are provided when Kivy is installed.

    See: /usr/local/share/kivy-examples/
    And: /usr/local/share/kivy-examples/guide/ for this particular example.

Also consider doing the series of videos referred to as the "crash course":
    https://kivy.org/doc/stable/tutorials/crashcourse.html

Easy-peasy, launch the app at command line, like:
    python3.9 paint.py
        to use default window size
or
    python3.9 paint.py --size=640x480
        to specify a window size in px = width x height

Don't need another server or anything. It's an app, not a web service.
"""
from random import random
from kivy.app import App                    # type: ignore
from kivy.uix.widget import Widget          # type: ignore
from kivy.uix.button import Button          # type: ignore
from kivy.graphics import Color, Ellipse, Line    # type: ignore


class MyPaintWidget(Widget):
    """
    Always instantiate a sub-class of a standard widget so
    that app-level modifications won't change the underlying
    Kivy "primitive" widget.

    This will make even more sense once we start using .kv files.
    """

    def on_touch_down(self, touch):
        # color = (random(), random(), random()) # random RGB color
        color = (random(), 1., 1.)               # random HSV color space
        with self.canvas:
            # Color(1, 1, 0)            # specified rgb color (yellow)
            # Color(*color)             # kwarg-y, pythonic ref to RGB tuple
            Color(*color, mode='hsv')   # ref to an HSV color space
            # For an explanation of HSV mode, see:
            #   https://psychology.fandom.com/wiki/HSV_color_space
            # We are saying "pick any color, but make it bright and saturated"
            d = 30.             # diameter
            # Draw circles at touch locations
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            # Get origin of touch for drawing a line.
            # Instantiate a line object to draw a line.
            # For explanation of "touch.ud" see:
            #   https://stackoverflow.com/questions/51841557/kivy-what-does-touch-ud-means
            # and
            #   https://kivy.org/doc/stable/api-kivy.input.motionevent.html#kivy.input.motionevent.MotionEvent
            # It is from the Kivy API, a type of dict used to capture info
            #   about motion events.
            touch.ud['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        # Draw a line between the last touch location and current one
        #   using random color.
        touch.ud['line'].points += [touch.x, touch.y]


class MyPaintApp(App):
    """
    The main app class. It is standard Kivy to name it like Something*App*.
    It inherits the Kivy App class.

    When we start to use .kv files, having an "*App" class is mandatory.

    Generally speaking buttons would not be added on top of other widgets.
    Don't want user to be able to draw over top of the button.
    """

    def build(self):
        """Notice use of "parent" here as the foundation.
        Add both "painter" and "clearbtn" objects to it as widgets.
        They will be sibling objects. The "parent" is like
          the "root" window object in TKinter?  OK...

        It's a dummy widget, a container for other widgets. Later
        we will get more structured with widget tree hierarchy.
        Kivy offers various approaches to widget layout.
        It's like Tk on meth. :-)

        Notice that we have not provided a position for the
        button, so it deafults to bottom left. We can change that.

        Also keep in mind that Kivy uses Cartesian coordinates.
        y-zero is at the bottom of the screen. x-zero is at the left.
        """
        parent = Widget()
        self.painter = MyPaintWidget()
        clearbtn = Button(text='Clear')
        # Here is where we connect the button to a method.
        clearbtn.bind(on_release=self.clear_canvas)
        parent.add_widget(self.painter)
        parent.add_widget(clearbtn)
        return parent

    def clear_canvas(self, obj):
        """Here's the method called when clear button is pressed.

        It would generally be referred to a callback function.

        Notice how canvas is referenced a sub-entity of app's
        "painter" widget, which is the "MyPaintWidget" object.
        """
        self.painter.canvas.clear()


if __name__ == '__main__':
    MyPaintApp().run()
