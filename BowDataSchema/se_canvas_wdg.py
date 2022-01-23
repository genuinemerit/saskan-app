#!/usr/bin/python3.9
"""
:module:    se_canvas_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts

Using QPainter is as clear as mud. Online docs are
not helpful and commentary quickly devolves into a
welter of Qt-speak that assumes a few years of
experience in Qt-landia. Snore.

Possibilities:

Define the OpenGL Canvas functions using QOpenGLWidget,
and/or use other drawing tools.
Methods on QOpenGLWidget include:
- initializeGL()
- paintGL()
- resizeGL()
May also want to check out QOpenGLWindow if having issues,
    but QOpenGLWidget is more stable.
The pyside2 docs on this are more obscure than usual and all
    of the examples are in C++.
Presumably they expect I'm already familiar with OpenGL and
    how to manage framebuffers and so on. Probably want to review
    some of the books on that before proeeding with this.

OpenGL is intended as a 3D drawing space. To do 2D drawing in
    an OpenGL containter, see: QPainter

- Let's assume I don't need 3D drawing yet.
- Try out QPainter. It has lots of drawing methods.
- See: https://doc.qt.io/qt-5/paintsystem-drawing.html
- From a quick look, seems similar to other painting/filling libs.
- But I am tripping over the bizarre QPainter methods. It's not
  a widget, it's a painter. But it's not clear how to use it.

Would PyGame be an option here? Could it be integrated with Qt?
How about Processing? Tkinter Canvas? Native python PIL/pillow?

Some of the web pages on Tkinter are so badly written and poorly
presented in such fractured English it's like they are trying to
keep you from using it. LOL!

Maybe getting familiar with QtGui.QImage and QPixmap will help.

Also consider checking out:
- pygame
- pyglet --> supports OpenGL/3d
- PyCairo --> no 3D support but maybe that's OK
- SFML --> seems to be a mystery
- OpenCV --> I did a little work with this at one point
            it's all about "computer vision" and image processing
            IIRC, if you want camera capture, you need to use OpenCV
- Kivy --> I got very frustrated with it as a general GUI solution,
        but maybe using it only for graphics is a good idea?  See:
        kivy.graphics.
- Of all these, I had the best experience with pygame. There is a
    StackOverflow example of pygame/Qt intergration here:
    https://stackoverflow.com/questions/38280057/how-to-integrate-pygame-and-pyqt4
    - Might be a good place to start experimenting with it
    - This same example shows up all over the place.
- Another interesting-looking one is:
    https://github.com/hongvin/DinoRun-PyQt-PyGame

Along QPainter and pygame, maybe check out how/when to use PIL/pillow.
See: https://github.com/python-pillow/Pillow
and https://pillow.readthedocs.io/en/stable/handbook/index.html
But it is mainly an image processing library.

Hey! Let's also recall work done with matplotlib and bokeh. Thinking in
terms of data analysis, so those might be better starting points
than something more like a painter or an animator.

Part of what has intrigued me is the idea of creating graph diagrams.
On the theory side, this is probably a good time to read the book
on the mathematics.
On the data structure basics, here is nice review/summary:
https://www.section.io/engineering-education/graph-data-structure-python/
He uses simple, familiar Python data structures -- similar to
an earlier BoW prototype.

Check out the NetworkX library for more extensive graph analysis.
Another library is igraph. The former seems better. And it looks like
it has plot visualization capabilities for graph structures.

Some food-for-thought on plotting graphs in python:
https://www.geeksforgeeks.org/generate-graph-using-dictionary-python/

And, of course, when the number-crunching gets heavy, turn to pandas!

Finally, there is a Python version of Processing these days, but don't
know that Processing can be integrated into a regular python app?
You can run the Processing editor in Python Mode no problem. But in a
regular python context, not sure that will work.

So... let's play around with...
- NetworkX
- Matplotlib
- Bokeh
- Seaborn
- mayavi
x  cartopy <== difficult install. needs cython and GEOS >= 3.7.2.
    This is complex, requires first installing a Postgres DB, etc.
    Skip it for now. But maybe come back to it later.
"""

from os import path
from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtGui import QPainter
# from PySide2.QtWidgets import QGraphicsLayout
# from PySide2.QtWidgets import QLabel
# from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QGraphicsWidget

from BowQuiver.saskan_fileio import FileIO      # type: ignore
from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from BowQuiver.saskan_utils import Utils        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

FI = FileIO()
SS = SaskanStyles()
TX = SaskanTexts()
UT = Utils()


class CanvasWidget(QGraphicsWidget):
    """Build container for the Canvas (Painter) components.

    Define/enable the Canvas functions widget.
    """
    def __init__(self):
        """super() call is required."""
        super().__init__()
        self.APP = path.join(UT.get_home(), 'saskan')
        self.RES = path.join(self.APP, 'res')
        self.make_canvas_widget()

    def set_content(self):
        """Refresh the canvas contents.

        Place-holder method.
        """
        pass

    def test_paint_event(self):
        """Test the canvas widget.

        This is a test method.
        """
        self.canvas = QPainter()
        # self.canvas.begin(self)
        self.canvas.setPen(Qt.red)
        self.canvas.setFont(QFont("Arial", 20))
        self.canvas.drawLine(0, 0, 100, 100)
        self.canvas.drawText(20, 20, "Hello Saskantinon!")
        # self.canvas.end()

    def make_canvas_widget(self):
        """Define components of the Help widget.
        """
        # Controls container
        self.setGeometry(640, 750, 600, 200)
        # cnv_layout = QGraphicsLayout()
        # self.setLayout(cnv_layout)
        # Title
        # Ideally, this would be set based on modes metadata "Title"
        # title = QLabel("Canvas")
        # title.setStyleSheet(SS.get_style('title'))
        # cnv_layout.addWidget(title)
        # Display area
        self.test_paint_event()
