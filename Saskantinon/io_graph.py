#!python
"""
:module:    io_graph.py

:author:    GM (genuinemerit @ pm.me)

Use NetworkX to collect data into nodes/edges for analysis
as graphs useful in analyzing, studying the saskan world data.

Generate graphs using matplotlib.pyplot and networkx.
In the saskan_report class.

Currently, graph objects are not saved. Eventually this class
will be called from Admin, wihch in turn will call report class.

Goals:
- Load, scrub and analyze data & graphs to help understand:
    - Most heavily referenced Nodes
    - Most heavily referenced Edges

@DEV:
- Consider whether it makes sense to persist the graph data
- Passing graph data to the saskan_report module for display
  is fine, but might be more "micro-service" to store it and
  not have a direct dependency between classes.
- Figure out why I can import networkx in this class, but not
  in saskan_report.py. Seems really weird.
- Consider whether I really need to use pandas. I think probably
  for some kinds of analysis, it will be useful. Not really
  graph data. Maybe rename this to io_analysis or something.
"""

# import networkx as nx                   # type: ignore
import pandas as pd                     # type: ignore
# import pickle

# from copy import deepcopy
from os import path
from pandas import DataFrame
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_file import FileIO              # type: ignore
from io_shell import ShellIO            # type: ignore
from saskan_report import SaskanReport  # type: ignore

FI = FileIO()
SI = ShellIO()
SR = SaskanReport()


class GraphIO(object):
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

        @DEV:
        - Eventually point to regular file stores and
          use FI.get_schema(), as with JSON file.
        - Consider dropping use of Excel, ODS, CSV files as scheemas;
          just use JSON (or YAML or OWL) for ontologies.
        - May want to keep for real heavy-duty Pandas work, as an
          easy way to save dataframes; but then those can be pickled...

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
        # Consider whether set_graph() belongs in saskan_report.py

        # self.set_graph(p_set,
        #                ["Thinker Stanley P. Quinn",
        #                 "Magister Showan of the Nywing",
        #                 "Ríkila",
        #                 "Inn of the Full Moons"])
        G = SR.set_graph(self.E[p_set],
                         ["Thinker Stanley P. Quinn"])
        # G = SR.set_graph(self.N[p_set], self.E[p_set])
        SR.report_degrees(p_set, G, self.N[p_set])
        SR.draw_graph(p_set, G, self.N[p_set], self.E[p_set])
