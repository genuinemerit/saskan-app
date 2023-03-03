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
        self.PALETTE = ("#000000", "#CC0000", "#00CC00", "#0000CC",
                        "#E0E0E0", "#880000", "#008800", "#000088",
                        "#0E0E0E", "#888800", "#088880", "#008888",
                        "#808080", "#CC8800", "#0CC880", "#00CC88")
        self.DS = dict()
        self.G = dict()
        self.N = dict()
        self.E = dict()
        self.NODES = dict()
        self.NODE_TYPES = dict()
        self.EDGES = dict()
        self.EDGE_TYPES = dict()

    # Helper functions
    def get_ntype(self,
                  p_set: str,
                  p_node_nm: str):
        """Return node type for a given node name.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        - p_node_nm (str): Node name.
        """
        node_type = None
        for nt, nodes in self.N[p_set]["name"].items():
            if p_node_nm in nodes:
                node_type = nt
                break
        return node_type

    # Data load and scrub functions
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
        self.DS[dataset_nm] =\
            self.get_data(path.join(src_dir, p_file_name), p_sheet_nm)

    def get_json_data(self,
                      p_set: str):
        """
        JSON file resides in one of 3 predefined schema dir's.
        Save JSON data as a dict in DS.
        Derive node types and save in N["type]
        Sort node-types ascending, no dups

        :args:
        - p_set (str): Name of a schema/ontology, e.g.: "scenes"
        """
        ds = FI.get_schema(p_set)
        self.DS[p_set] = list(ds.values())[0]
        self.N[p_set] = {"types": list(),
                         "name": dict(), "size": dict(), "color": dict()}
        self.E[p_set] = {"types": list(),
                         "name": dict(), "color": dict()}
        self.N[p_set]["types"] = sorted(list(set(self.DS[p_set][0].keys())))

    def set_node_names(self,
                       p_set: str):
        """Pull nodes from dataset; set N["name"] data.
        Node names are stored as a list indexed by node type.
        List is sorted and duplicates removed.
        Assign a color to each node type.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        for nt in self.N[p_set]["types"]:
            self.N[p_set]["name"][nt] = list()
        for rec in self.DS[p_set]:
            for nt in self.N[p_set]["types"]:
                for node in rec[nt]:
                    self.N[p_set]["name"][nt].append(node)
        for nix, ntyp in enumerate(self.N[p_set]["types"]):
            self.N[p_set]["name"][ntyp] =\
                sorted(list(set(self.N[p_set]["name"][ntyp])))
            cix = nix if nix < len(self.PALETTE) else len(self.PALETTE) - nix
            color = f"{self.PALETTE[cix]}"
            for node in self.N[p_set]["name"][ntyp]:
                self.N[p_set]["color"][node] = color
        # pp((self.N))

    def set_edge_types(self,
                       p_set: str,
                       p_no_edge: list = [("", "")]):
        """Derive edge-types from dataset.
        Skip making edges between node-types w/o logical relationship.
        Sort node-names in edge-type tuple ascending.
        Sort list of edge-types ascending, no dups.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        - p_no_edge (list): List of tuples of node-names to skip,
                that is, not to make edges between. (optional)
        """
        for n1 in self.N[p_set]["types"]:
            for n2 in [n for n in self.N[p_set]["types"] if n != n1]:
                skip_it = False
                for (en1, en2) in p_no_edge:
                    if (n1 == en1 and n2 == en2) or\
                         (n1 == en2 and n2 == en1):
                        skip_it = True
                        break
                if not skip_it:
                    self.E[p_set]["types"].append(tuple(sorted([n1, n2])))
        self.E[p_set]["types"] = sorted(list(set(self.E[p_set]["types"])))

    def set_edges(self,
                  p_set: str):
        """Derive edge names from dataset.
        Store edges as a list indexed by edge-type.
        Sort each list of edges ascending, no dups.
        Assign colors to each edge type (node-tuple).

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        for eix, etyp in enumerate(self.E[p_set]["types"]):
            self.E[p_set]["name"][etyp] = list()
            n1, n2 = etyp
            for n in self.N[p_set]["name"][n1]:
                for rec in self.DS[p_set]:
                    if n in rec[n1]:
                        for m in rec[n2]:
                            self.E[p_set]["name"][etyp].append((n, m))
            self.E[p_set]["name"][etyp] =\
                sorted(list(set(self.E[p_set]["name"][etyp])))
            # colors
            cix = eix if eix < len(self.PALETTE) else len(self.PALETTE) - eix
            color = f"{self.PALETTE[cix]}"
            for edge in self.E[p_set]["name"][etyp]:
                self.E[p_set]["color"][etyp] = color
        # pp((self.E))

    def set_graph(self,
                  p_set: str,
                  p_include: list = None,):
        """Populate networkx-compatible graph dataset using dataset.
        - Defining the edges automatically also defines the nodes.
        - Limiting the graph to a subset of nodes here affects what
          is reported and displayed by report_graph() and plot_graph().
        - If no subset is defined, all nodes are included.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        - p_include (list): List of node names to include in graph (optional)
        """
        G = nx.MultiDiGraph()
        for e_list in self.E[p_set]["name"].values():
            edges = list()
            for (n1, n2) in e_list:
                if p_include is None:
                    edges.append(tuple((n1, n2)))
                elif n1 in p_include or n2 in p_include:
                    edges.append(tuple((n1, n2)))
            G.add_edges_from(edges)
        self.G[p_set] = G
        # pp((G.nodes(), G.edges()))

    def report_graph(self,
                     p_set: str):
        """Show report of graphed data

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"

        @DEV:
        - Integrate analysis into the admin app
        - Provide interactive options and reports like:
            - List all nodes, be able to pick a subset
            - List node-type and edge-type, be able to pick subset
            - List scenes on a timeline,
                optionally list selected nodes in each scene
        - Do NOT try to create an editor for the JSON file,
            just use a fucking editor. :-)
        """
        print("NODE DEGREES\n=====================")
        G = self.G[p_set]
        rpt_data = sorted([(G.degree(n), n, self.get_ntype(p_set, n))
                           for n in G.nodes()], reverse=True)
        pp((rpt_data))

    def draw_graph(self,
                   p_set: str):
        """Draw graph based on G data.

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"

        @DEV:
        - Explore different layouts (see networkx docs)
            - See io_graphs for example:
            pos = nx.kamada_kawai_layout(G)
        """
        G = self.G[p_set]
        node_sizes = [G.degree(n) * 23 for n in G.nodes()]
        node_labels = {n: f"\n{self.get_ntype(p_set, n)}\n{n}"
                       for n in G.nodes()}
        node_colors = [self.N[p_set]["color"][n] for n in G.nodes()]
        edge_colors = [self.E[p_set]["color"][
                        (self.get_ntype(p_set, e[0]),
                         self.get_ntype(p_set, e[1]))].replace("0", "5")
                       for e in G.edges()]
        # Folks online tend to recommend graphviz for drawing graphs, but
        # I could not get graphviz to work with my environment, networkx.

        # See: https://networkx.org/documentation/stable/reference/drawing.html

        # Most of these layouts need or require additional parameters,
        #  but I am not clear yet on how to set them usefully.

        # Ones I prefer so far are marked with a "# *" comment.
        pos = nx.spiral_layout(G)                   # *
        # pos = nx.spring_layout(G, seed=13648)     # *
        # pos = nx.circular_layout(G)               # *
        # pos = nx.shell_layout(G)                  # *
        # pos = nx.kamada_kawai_layout(G)           # requires scipy
        # pos = nx.random_layout(G)
        # pos = nx.spectral_layout(G)
        plt.title(p_set)
        cmap = plt.cm.plasma
        ax = plt.gca()
        ax.set_axis_off()
        nx.draw_networkx_nodes(G, pos,
                               linewidths=1,
                               node_color=node_colors,
                               node_size=node_sizes)
        nx.draw_networkx_edges(G, pos,
                               arrows=False,
                               edge_color=edge_colors,
                               edge_cmap=cmap,
                               width=1)
        # Node labels
        nx.draw_networkx_labels(G, pos,
                                font_size=9,
                                font_color='indigo',
                                labels=node_labels,
                                verticalalignment="top")
        plt.show()

    def analyze_data(self,
                     p_set: str):
        """Load, scrub and display graph data

        :args:
        - p_set (str): Name of a schema/ontology, e.g. "scenes"
        """
        # basic gathering and loading
        self.get_json_data(p_set)
        self.set_node_names(p_set)
        self.set_edge_types(p_set, [("people", "groups")])
        self.set_edges(p_set)
        # selection, display and reporting
        # self.set_graph(p_set,
        #                ["Thinker Stanley P. Quinn",
        #                 "Magister Showan of the Nywing",
        #                 "Ríkila",
        #                 "Inn of the Full Moons"])
        self.set_graph(p_set)
        self.report_graph(p_set)
        self.draw_graph(p_set)
