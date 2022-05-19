#!/usr/bin/python3.9
"""
:module:    se_diagram_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts

Use NetworkX and matplotlib modules to generate graph diagrams.

This class only generates the graph using matplotlib.pyplot and
networkx. It has no framework GUI elements. The figure is
generated and then saved to a file in the app /save directory.

It is up to the calling class to display the figure.
"""

import matplotlib.pyplot as plt         # type: ignore
import networkx as nx                   # type: ignore
from os import path
from pprint import pprint as pp         # noqa: F401

from io_config import ConfigIO          # type: ignore
from io_file import FileIO              # type: ignore
from io_redis import RedisIO            # type: ignore

CI = ConfigIO()
FI = FileIO()
RI = RedisIO()


class GraphIO(object):
    """Class for Networkx Graphing methods.

    Define/enable the Networkx graphing functions.

    The Graph Class is for undirected networks.
    """
    def __init__(self,
                 p_img_title: str,
                 p_nodelist: dict = None,
                 p_edgelist_path: str = None,
                 p_edgelist: list = None,
                 p_w_edgelist_path: str = None,
                 p_w_edgelist: list = None,
                 p_graph_data: dict = None,
                 p_redis_data: tuple = None):
        """Class for displaying graphs.

        :args:
        - p_img_file_nm:    Name of the image file to save
        - p_node_list (dict) - Labeled nodes to add to graph.
                                {'label': ['list of node names'], ...}
        - p_edgelist_path (str) - File containing a pair of connected nodes
                                  on each line.
        - p_edgelist (list) - List of tuples of connected nodes.
        - p_w_edgelist_path (str) - File containing a pair of connected nodes
                                    then a weighting number on each line.
        - p_edgelist (list) - List of tuples of connected nodes and
                              a weighting number.
        - p_graph_data (dict) - Data to be visualized as a graph
                                TBD -- placeholder for more complex inputs
        - p_redis_data (tuple) - Key to data to be visualized.
                                 Must in the form of:
                                 (db_name, data_record_key)
                                TBD -- placeholder for more complex inputs
                                GUI metadata can be mapped as a DAG?
        """
        self.G = nx.Graph()
        if p_nodelist is not None:
            for label, nodes in p_nodelist.items():
                self.G.add_nodes_from(nodes, label=label)
        elif p_edgelist_path is not None:
            self.G = nx.read_edgelist(p_w_edgelist_path)
        elif p_edgelist is not None:
            for pair in p_edgelist:
                self.G.add_node(pair[0])
                self.G.add_node(pair[1])
                self.G.add_edge(pair[0], pair[1])
        elif p_w_edgelist_path is not None:
            self.G = nx.read_weighted_edgelist(p_w_edgelist_path)
        elif p_w_edgelist is not None:
            for pair in p_w_edgelist:
                self.G.add_node(pair[0])
                self.G.add_node(pair[1])
                self.G.add_edge(pair[0], pair[1])
                self.G.edges[pair[0], pair[1]]['weight'] = pair[2]
        elif p_graph_data is not None:
            pass
        elif p_redis_data is not None:
            db_data = RI.get_redis_data(p_redis_data[0], p_redis_data[1])
            pp(("db_data", db_data))

        self.make_network_diagram(p_img_title)

    def make_network_diagram(self,
                             p_img_title: str):
        """Generate a drawing from the Graph object.
        """
        plt.figure(figsize=(10.0, 10.0))      # w, h in inches

        pp(("G", self.G))

        nx.draw_networkx(self.G, with_labels=True, font_weight='bold')
        plt.title(p_img_title)
        save_path = path.join(RI.get_app_path(),
                              RI.get_config_value('save_path'),
                              p_img_title.replace(" ", "_") + '.png')
        plt.savefig(save_path)
        print(f"Graph diagram saved to: {save_path}")

    # ================ obsolete =======================================

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
