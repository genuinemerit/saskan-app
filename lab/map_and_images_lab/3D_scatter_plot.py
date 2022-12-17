#!/usr/bin/python3  # noqa: E265

"""Play around with the very cool 3D scatter plot visualization.

The mpl_toolkits.mplot3d extends matplotlib to 3D.
It gets installed as part of matplotlib, but may not work with Jupyter.
It is not referenced directly, hence the noqa F401 flake8 exception,
but it provides ability to request a '3d' projection.

This also shows use of the param module, which can be used to define
data in a precise way.  We might use a dataclass and typing these days?
"""
import math

import param
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa F401


class InitData(param.Parameterized):
    """Define data elements for messing around with matplotlib.

    Args:
        (object) param module. Kind of similar to dataclass and Types.
    """

    # Constants
    XDATA = param.List(default=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                       doc="Test data set for x axis", constant=True,
                       readonly=True)
    YDATA = param.List(default=[-8, -6, -4, -2, 0, 2, 4, 6, 8, 10],
                       doc="Test data set for x axis", constant=True,
                       readonly=True)
    ZDATA = param.List(default=[4.6692016091029906718532,
                                3.1415,
                                2.718,
                                2.3,
                                1.0,
                                0.577215,
                                0.207879576,
                                0.12345678910111213141516171819202122232425,
                                0.110001000000000000000001000,
                                0.01101001],
                       doc="Test data set for x axis", constant=True,
                       readonly=True)
    LABELS = param.Dict(default={"xlabel": "Positive integers",
                                 "ylabel": "Pos and Neg Integers",
                                 "zlabel": "Popular Transcendtals and Stuff",
                                 "title": "Scatter in 3 Dimensions"})
    # Containers
    AREADATA = []


class RunData(InitData):
    """Process the test data.

    Args:
        InitData (class): precisely-defined constants and containers
    """

    def viz_data(self):
        """Prepare the data and visualize it in a 3D scatter plot.

        Apply made-up formula to create objects of various sizes.
        """
        self.AREADATA = []
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for zipdata in zip(self.XDATA, self.YDATA, self.ZDATA):
            area =\
                math.pi * float(((zipdata[0] +
                                  abs(zipdata[1])) * zipdata[2]) ** 1.3)
            self.AREADATA.append(area)
        ax.scatter(self.XDATA, self.YDATA, self.ZDATA,
                   s=self.AREADATA, alpha=0.5)
        plt.title(self.LABELS["title"])
        ax.set_xlabel(self.LABELS["xlabel"])
        ax.set_ylabel(self.LABELS["ylabel"])
        ax.set_ylabel(self.LABELS["zlabel"])
        # ax.rcParams["figure.figsize"] = [12.0, 9.0]
        fig = plt.figure(1)
        fig.canvas.set_window_title(self.LABELS["title"])
        plt.show(block=True)


TEST = RunData()
TEST.viz_data()
