#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Matplotlib basics.

This lesson works from materials provided in J.R. Johansson's lecture series,
available online at:
https://github.com/jrjohansson/scientific-python-lectures/blob/master/Lecture-4-Matplotlib.ipynb

Also see ../Data_Science/books_course_notes/Notes_on_matplotib.md
for more explanation, links.
"""
from pprint import pprint as pp
import numpy as np
import matplotlib.pyplot as plt


def init_vectors():
    """Init arrays used in basic vector and matrix examples.

    Return a collection of 5 vectors.
    """
    return (np.array([1, 2, 3, 4]),
            np.array([1., 2., 3., 4.]),
            np.array(['a', 'b', 'c', 'd']),
            np.array(["a", "b", "c", "d"]),
            np.array(['ab', 'cd', 'ef', 'gh']))


def show_vectors():
    """Look at some numpy basics: vectors, arrays.

    Unlike python lists, Numpy arrays are statically typed and homogenous.
    They are also more memory-efficient.
    Shape of a vector: number of items in it.
    """
    print(show_vectors.__doc__)
    (vector1, vector2, vector3, vector4, vector5) = init_vectors()
    pp({"vector1 -- array of integers":
        {"type": type(vector1),
         "shape": vector1.shape,
         "shape_": np.shape(vector1),
         "content": vector1},
        "vector2 -- array of floats":
        {"type": type(vector2),
         "size": np.size(vector2),
         "content": vector2},
        "vector3 -- array of one-byte strings":
        {"type": type(vector3),
         "content": vector3},
        "vector4 -- another array of one-byte strings":
        {"type": type(vector4),
         "content": vector4},
        "vector5 -- array of two-byte strings":
        {"type": type(vector5),
         "content": vector5}})


def show_matrices():
    """Numpy basics: matrices, grids.

    Shape of a matrix: number of arrays, number of items in each.
    Matrix and dot multiplications can be applied (see other labs),
    and can be done using C or Fortran if desired.
    See other labs or references for full list of dtypes.
    Most common ones are: int, float, complex, bool, object
    """
    print(show_matrices.__doc__)
    (vector1, vector2, vector3, _, _) = init_vectors()
    matrix1 = np.array([[1, 2, 3], [4, 5, 6]])
    matrix2 = np.array([vector1, vector2])
    matrix3 = np.array([vector1, vector3])
    matrix4 = np.array([vector1, vector2, vector3])
    pp({"matrix1 -- two integer arrays":
        {"type": type(matrix1),
         "shape": np.shape(matrix1),
         "size": np.size(matrix1),
         "content": matrix1},
        "matrix2 -- integer Union float = float":
        {"type": type(matrix2),
         "content": matrix2},
        "matrix3 -- integer Union string = string, 21 bytes":
        {"type": type(matrix3),
         "content": matrix3},
        "matrix4 -- integer Union float = string, 32 bytes":
        {"type": type(matrix4),
         "content": matrix4}})


def init_arrays():
    """Methods for initializing Numpy arrays."""

    def init_zeros():
        """Set all values to float zero."""
        print(init_zeros.__doc__)
        pp({"zeros":
            {"np.zeros(np.int(8))":
             np.zeros(np.int(8)),
             "np.array([np.zeros(8), np.zeros(8)])":
             np.array([np.zeros(8), np.zeros(8)])}})

    def init_a_range():
        """Use arange() to initialize.

        N.B.:  It is a_range, not arrange.
        arange (start-value, stop-value, step-value)
        """
        print(init_a_range.__doc__)
        pp({"a range":
            {"arange(0, 10, 1))": np.arange(0, 10, 1),
             "arange(0, 10, 2))": np.arange(0, 10, 2),
             "arange(0, 10, 0.5))": np.arange(0, 10, 0.5)}})

    def init_linspace():
        """Use linspace() to initialize.

        linspace (start-val, stop-val, num-of-samples, endpoint=[True|False],
              retstep=[False|True], dtype=None)
        Return evenly spaced samples over a specified interval,
        in linear space.
        See: https://en.wikipedia.org/wiki/Linear_space_(geometry)
        """
        print(init_linspace.__doc__)
        pp({"linspace":
            {"linspace(2.0, 3.0, num=10)":
             np.linspace(2.0, 3.0, num=10),
             "linspace(2.0, 3.0, num=10, endpoint=False)":
             np.linspace(2.0, 3.0, num=10, endpoint=False),
             "linspace(2.0, 3.0, num=10, retstep=True)":
             np.linspace(2.0, 3.0, num=10, retstep=True),
             "linspace(2.0, 3.0, num=5, retstep=True)":
             np.linspace(2.0, 3.0, num=5, retstep=True),
             "linspace(2.0, 3.0, num=10, dtype=int)":
             np.linspace(2.0, 3.0, num=10, dtype=int)}})

    def init_logspace():
        """Use logspace() to initialize.

        logspace (start, stop, num, endpoint, base=10.0, dtype=None)
        Returns numbers spaced evenly on a log scale, using provided base,
        with default as base 10.
        """
        print(init_logspace.__doc__)
        pp({"logspace":
            {"np.logspace(0, 10, 10)":
             np.logspace(0, 10, 10),
             "np.logspace(0, 10, 10, base=10.0)":
             np.logspace(0, 10, 10, base=10.0),
             "np.logspace(0, 10, 10, base=2)":
             np.logspace(0, 10, 10, base=2)}})

    def init_mgrid():
        """Remember that mgrid is similar to meshgrid in MATLIB.

        It returns a "dense" multi-dimensional grid.
        Evidently this type of thing is useful in "broadcast functions" but my
        math is not strong enough yet to grasp the implications of this.
        mgrid[a series of comma-separated matrix defintions in the form x:y:z,
          where x is starting value, y is ending value, and z is optionally
          the step value.]
        Interesting discussion on meshgrids can be found here:
        https://stackoverflow.com/questions/36013063/what-is-the-purpose-of-meshgrid-in-python-numpy
        """
        print(init_mgrid.__doc__)
        pp({"mgrid":
            {"np.mgrid[0:5, 0:5]": np.mgrid[0:5, 0:5],
             "np.mgrid[0:5:0.5, 0:5:0.5]": np.mgrid[0:10:2, 0:10:2]}})

    print(init_arrays.__doc__)
    init_zeros()
    init_a_range()
    init_linspace()
    init_logspace()
    init_mgrid()


def plot_arrays():
    """Graphs display content of Numpy arrays.

    linspace with endpoint True vs. False shown graphically.
    N.B.: Correct Cartesian space, not "video" space, so
    "y" positive is UP, and "y" negative is DOWN

    1-d array, 8 values set to zero.

    2 1-d arrays, 8 values set by linspace

    A subplot means drawing multiple diagrams in a figure.
    See:
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplot.html

    Basic function structure:
    `subplot(nrows, ncols, index, **kwargs)`
    `nrows`: how many rows of plots.
    `ncols`: how many columns of plots.
    `index` refers to position within a grid.
    In this example, we have two plots across two rows in one column.
    The `index` indicates the plot shown should be in row 1 or 2.
    It is probably more common to use "axes", returned from subplot().

    Linear space diagrams...
    1) Use matrix addition to modify all values of grid_y
    2) Same, with modified y value.

    Logspace diagrams... same approach
    """
    print(plot_arrays.__doc__)
    cols = 8
    grid_y = np.zeros(cols)
    grid_x1 = np.linspace(0, 10, cols, endpoint=True)
    grid_x2 = np.linspace(0, 10, cols, endpoint=False)
    pp({"linspace_grid": {"grid_x1": grid_x1, "grid_x2": grid_x2}})
    plt.subplot(2, 1, 1)
    plt.plot(grid_x1, grid_y, 'o')          # maps to x=val, y=0.0
    plt.plot(grid_x2, grid_y + 0.5, 'o')    # maps to x=val, y=0.5
    plt.ylim([-0.5, 1])                     # define y axis labels
    plt.title("linear space")

    plt.subplot(2, 1, 2)
    cols = 10
    grid2_y = np.zeros(cols)
    grid2_x1 = np.logspace(0.1, 1, cols, endpoint=True)
    grid2_x2 = np.logspace(0.1, 1, cols, endpoint=False)
    pp({"logspace_grid": {"grid2_x1": grid2_x1, "grid2_x2": grid2_x2}})
    plt.plot(grid2_x1, grid2_y, 'o')          # maps to x=val, y=0.0
    plt.plot(grid2_x2, grid2_y + 0.5, 'o')    # maps to x=val, y=0.5
    plt.ylim([-0.5, 1])                       # define y axis labels
    plt.title("log space")

    plt.show()


if __name__ == '__main__':
    show_vectors()
    show_matrices()
    init_arrays()
    plot_arrays()
