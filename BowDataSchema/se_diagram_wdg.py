#!/usr/bin/python3.9
"""
:module:    se_diagram_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts

Use NetworkX and matplotlib modules to generate graph diagrams.

This class only generates the graph using matplotlib.pyplot and
networkx. It has no Qt or other GUI elements. The figure is
generated and then saved to a file in the local App /cache directory.

It is up to the calling class to display the figure.


@DEV
    For now, not putting int a box container since I
    had problems getting it to display properly.

    May want to configure it as kind of a sub-class of the Editor,
    sort of like the RecordManager object.
"""

import matplotlib.pyplot as plt         # type: ignore
import networkx as nx                   # type: ignore
from os import path
from pprint import pprint as pp         # noqa: F401

from BowQuiver.saskan_fileio import FileIO      # type: ignore
from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from BowQuiver.saskan_utils import Utils        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

FI = FileIO()
SS = SaskanStyles()
TX = SaskanTexts()
UT = Utils()


class DiagramWidget(object):
    """Container for Networkx Graphing Diagram components.

    Define/enable the Networkx functions widget.
    """
    def __init__(self, wdg_meta: dict):
        """Set up a portal for displaying graphs."""
        self.netx = wdg_meta
        self.APP = path.join(UT.get_home(), 'saskan')
        self.CACHE = path.join(self.APP, TX.db.sask_cache)
        self.img_file_nm = str()
        self.make_network_diagram()

    def make_test_diagram(self):
        """Test with a simple default test graph.

        :return:    Networkx graph
        """
        G = nx.Graph()
        G.add_node('A')
        G.add_nodes_from(['B', 'C'])
        G.add_edge('A', 'B')
        G.add_edges_from([('B', 'C'), ('A', 'C')])
        return G

    def get_image_path(self):
        """Return full path to the current image file.

        For now, only one image file is supported.
        May want to extend this to handle multiple frames.

        :return:    File URL str
        """
        return path.join(self.CACHE, self.img_file_nm)

    def set_content(self,
                    p_w_inches: float,
                    p_h_inches: float,
                    p_graph_title: str = ''):
        """Refresh the graph contents.

        :args:
            p_w_inches:       Width of the graph in inches
            p_h_inches:       Height of the graph in inches
            p_graph_title:    Title of the graph

        :sets:  self.img_file_nm

        :return: tuple (Networkx graph, width, height, title)

        Prototype method. The idea would be to call methods
        or pass in structures that can define a graph.
        """
        self.img_file_nm = 'networkx.png'
        g_width = p_w_inches if p_w_inches > 0.0 else 5.5
        g_height = p_h_inches if p_w_inches > 0.0 else 2.0
        g_title = self.img_file_nm \
            if p_graph_title in ('', None) else p_graph_title
        G = self.make_test_diagram()
        return (G, g_width, g_height, g_title)

    def make_network_diagram(self):
        """Define components of the Networkx widget.
        """
        G, g_w, g_h, g_title = self.set_content(5.5, 2.0, "Test Diagram")
        plt.figure(figsize=(g_w, g_h))      # w, h in inches
        nx.draw_networkx(G, with_labels=True, font_weight='bold')
        plt.title(g_title)
        plt.savefig(self.get_image_path())
