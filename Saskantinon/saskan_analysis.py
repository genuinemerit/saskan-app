#!python
"""
:module:    saskan_analysis.py

:author:    GM (genuinemerit @ pm.me)

Use NetworkX and matplotlib modules to generate diagrams
useful in understanding and studying the saskan world data.

Generate graphs using matplotlib.pyplot and networkx.
This class has no framework GUI elements.
Figures generated then saved to a file in the app /save directory.
It is up to the calling class to display the figure.

Goals:
- Load, scrub and analyze data & graphs to help understand:
    - Most heavily referenced Nodes
    - Most heavily referenced Edges
"""

import matplotlib.pyplot as plt         # type: ignore
import networkx as nx                   # type: ignore
import pandas as pd                     # type: ignore
# import pickle

# from copy import deepcopy
from os import path
from pandas import DataFrame
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_file import FileIO              # type: ignore
from io_shell import ShellIO            # type: ignore

FI = FileIO()
SI = ShellIO()


class Analysis(object):
    """Class for using Networkx Graphing methods.

    Define/enable the Networkx graphing functions.
    """
    def __init__(self):
        """Class for managing graph data, generating graphs
        and other graph-related methods.
        """
        pd.options.mode.chained_assignment = None
        self.SETS = dict()
        self.FRAMES = dict()
        self.NODES = dict()
        self.NODE_TYPES = dict()
        self.EDGES = dict()
        self.EDGE_TYPES = dict()
        self.GRAPHS = dict()

    def get_data(self,
                 p_file_path: str,
                 p_sheet_nm: str = None) -> DataFrame:
        """Get data from a file.
           It can be Excel, ODS, or CSV/TSV

        :args:
        - p_file_path (str): Full path to the file.
        - p_sheet_nm (str): Name of the sheet to load.
        :return:
        - (DataFrame): DataFrame of the data.
        """
        sheet_df = None
        ss_type = p_file_path.split('.')[-1].lower()
        if ss_type.lower() in ('xlsx', 'xls'):
            sheet_df = pd.read_excel(p_file_path,
                                     sheet_name=p_sheet_nm)
        elif ss_type.lower() in ('ods'):
            sheet_df = pd.read_excel(p_file_path, engine='odf',
                                     sheet_name=p_sheet_nm)
        elif ss_type.lower() in ('csv', 'txt'):
            sheet_df = pd.read_csv(p_file_path)
        elif ss_type.lower() in ('tsv'):
            sheet_df = pd.read_csv(p_file_path, sep='\t')
        elif ss_type.lower() in ('txt'):
            sheet_df = pd.read_csv(p_file_path, sep='|', header=True)
        else:
            raise Exception(f"{FI.T['err_file']} {p_file_path}/{p_sheet_nm}")
        return sheet_df

    def set_source(self,
                   p_file_name: str,
                   p_sheet_nm: str = None) -> tuple:
        """
        Input file is Excel, ODS, comma-separated (csv), tab-separated (tsv),
        or tilde-separated (txt). If Excel or ODS, then a sheet name needs
        to be supplied also.

        :args:
        - p_file_path (str): Name of a schema/ontology file.
        - p_sheet_nm (str): Name of the sheet to load. (optional)
        :returns:
        - (tuple): (path to schema files, dataset_nm)
        """
        home = path.expanduser("~")
        src_dir = path.join(home, FI.D["APP"], FI.D["ADIRS"]["ONT"])
        dataset_nm = p_sheet_nm if p_sheet_nm else p_file_name.split('.')[0]
        return(src_dir, dataset_nm)

    def get_ss_data(self,
                    p_file_name: str,
                    p_sheet_nm: str = None):
        """
        Input file is Excel, ODS, comma-separated (csv), tab-separated (tsv),
        or tilde-separated (txt). If Excel or ODS, then a sheet name needs
        to be supplied also.

        :args:
        - p_file_path (str): Name of a schema/ontology file.
        - p_sheet_nm (str): Name of the sheet to load.
        """
        src_dir, dataset_nm = self.set_source(p_file_name, p_sheet_nm)
        self.FRAMES[dataset_nm] =\
            self.get_data(path.join(src_dir, p_file_name), p_sheet_nm)

    def get_json_data(self,
                      p_set: str):
        """
        JSON file resides in one of 3 predefined schema dir's.
        Assumptions about data structure:
        - Collection of records in a list indexed by "scenes".
        - Attributes of each record:
            - scene, people, groups, places, times
            - each attribute contains a list of strings
            - typically expect only one value in the scene list
            - time strings are in a game calendar "SAG" format:
              - Current year at start of game is: 4934
              - First year of era (Time of the Catastrophe) counted as: 1
              - First day of a year counted as: 1
              - Years are 366 days long
              - Every 3rd year, add one leap day (367th day)
              - It is a solar, arithmetic calendar
              - Year begins at Midnight on the Winter Solstice
              - Days are counted Midnight to Midnight
              - No months are reckoned
              - Date format is: "yyyy.ddd"
              - For the purpose of this analysis, hours are ignored
        :args:
        - p_set (str): Name of a schema/ontology file, w/o extension.
                          Example: "scenes"
        """
        ds = FI.get_schema(p_set)
        set_nm = list(ds.keys())[0]
        self.SETS[set_nm] = list(ds.values())[0]
        self.NODE_TYPES[p_set] = list(set(self.SETS[set_nm][0].keys()))

    def get_node_type(self,
                      p_set: str,
                      p_node: str):
        """Return node type for a given node.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        - p_node (str): Node name.
        """
        node_type = None
        for nt, nodes in self.NODES[p_set].items():
            if p_node in nodes:
                node_type = nt
                break
        return node_type

    def set_nodes(self,
                  p_set: str):
        """Pull nodes and node-types from dataset.
        Set NODES data.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        self.NODES[p_set] = dict()
        for nt in self.NODE_TYPES[p_set]:
            self.NODES[p_set][nt] = list()
        for rec in self.SETS[p_set]:
            for nt in self.NODE_TYPES[p_set]:
                for node in rec[nt]:
                    self.NODES[p_set][nt].append(node)
        for nt in self.NODE_TYPES[p_set]:
            self.NODES[p_set][nt] =\
                sorted(list(set(self.NODES[p_set][nt])))

    def set_edge_types(self,
                       p_set: str):
        """Derive edge-types from dataset.
           Skip making edges between people and groups
           Both are a type of character

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        self.EDGE_TYPES[p_set] = set()
        for nt1 in self.NODE_TYPES[p_set]:
            for nt2 in [nt for nt in self.NODE_TYPES[p_set]
                        if nt != nt1]:
                if not(nt1 in ("people", "groups") and
                        nt2 in ("people", "groups")):
                    self.EDGE_TYPES[p_set].add(tuple(sorted([nt1, nt2])))

    def set_edges(self,
                  p_set: str):
        """Derive edges from dataset.
        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        self.EDGES[p_set] = dict()
        for edge in self.EDGE_TYPES[p_set]:
            self.EDGES[p_set][edge] = list()
            nt1, nt2 = edge
            for n in self.NODES[p_set][nt1]:
                for rec in self.SETS[p_set]:
                    if n in rec[nt1]:
                        for m in rec[nt2]:
                            self.EDGES[p_set][edge].append((n, m))

    def set_graph(self,
                  p_set: str):
        """Populate networkx-compatible graph dataset using dataset.
        Note that defining the edges automatically defines the nodes.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        G = nx.MultiDiGraph()
        for e_list in self.EDGES[p_set].values():
            # pp(("e_list", e_list))
            edges = list()
            for (n1, n2) in e_list:
                nt1 = self.get_node_type(p_set, n1)
                nt2 = self.get_node_type(p_set, n2)
                # pp(("nt1:n1", nt1, n1, "nt2:n2", nt2, n2))
                edges.append((f"\n{nt1}\n{n1}",
                              f"\n{nt2}\n{n2}"))
            # pp(("edges", edges))
            G.add_edges_from(edges)
        self.GRAPHS[p_set] = G
        # pp(("G.nodes()", G.nodes()))
        # pp(("G.edges()", G.edges()))

    def set_colors(self,
                   p_set: str):
        """Set color for graph nodes and edges.
        Use a color palette to set the color for each node and edge,
        based on the type of node or edge.

        Set a basic color for each node type.
        Set a blended color for each edge type.
        """
        basic = ("000000", "CC0000", "00CC00", "0000CC",
                 "E0E0E0", "880000", "008800", "000088",
                 "0E0E0E", "888800", "088880", "008888",
                 "808080", "CC8800", "0CC880", "00CC88")
        for nt in self.NODE_TYPES[p_set]:
            nix = self.NODE_TYPES[p_set].index(nt)
            cix = nix if nix < len(basic) else len(basic) - nix
            self.NODE_TYPES[p_set][nix] = (nt, f"#{basic[cix]}")
        # pp(("modified self.NODE_TYPES", self.NODE_TYPES))

    def draw_graph(self,
                   p_set: str):
        """Draw graph based on stored data.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"

        @DEV:
        - Drive edge colors from edge type
        - Pick sets of scenes to draw
        - Explore different layouts (see networkx docs)
        - Use degrees to create a simple report of heaviest nodes
        - Think about weighting the edges too
        - Remove arrows from edges
        """
        G = self.GRAPHS[p_set]
        node_sizes: list = list()
        node_colors: list = list()
        for n in G.nodes():
            node_sizes.append(G.degree(n) * 30)
            ntyp = n.split("\n")[1]
            nc = [c for (nt, c) in self.NODE_TYPES[p_set] if ntyp == nt][0]
            node_colors.append(nc)
        # pp(("node_sizes", node_sizes))
        # pp(("node_colors", node_colors))
        # --> modify to use edge type to drive color <--
        edge_colors = range(2, G.number_of_edges() + 2)
        pos = nx.spring_layout(G, seed=13648)
        # The kamada kawai layout requires scipy to be installed:
        # pos = nx.kamada_kawai_layout(G)
        plt.title(p_set)
        cmap = plt.cm.plasma
        ax = plt.gca()
        ax.set_axis_off()
        nx.draw_networkx_nodes(G, pos,
                               linewidths=1,
                               node_color=node_colors,
                               node_size=node_sizes)
        nx.draw_networkx_edges(G, pos,
                               node_size=node_sizes,
                               edge_color=edge_colors,
                               edge_cmap=cmap,
                               width=2)
        # Node labels
        nx.draw_networkx_labels(G, pos,
                                font_size=9,
                                font_color='indigo',
                                verticalalignment="top")
        plt.show()

    def show_graph(self,
                   p_set: str):
        """Load, scrub and display graph data

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        self.get_json_data(p_set)
        self.set_nodes(p_set)
        self.set_edge_types(p_set)
        self.set_edges(p_set)
        self.set_graph(p_set)
        self.set_colors(p_set)
        self.draw_graph(p_set)
