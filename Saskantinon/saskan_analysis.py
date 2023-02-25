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

Dataset:
    - Nodes (N):
        - Characters (c)
        - Places (p)
        - Scenes (s)
        - Times (t)
    - Edges (E), all bi-directional (D2), none are self-referential:
        - c-p
        - c-s
        - c-t
        - p-s
        - p-t
        - s-t

Attributes:
    - Each (N) has a unique ID (NID) = Name, a string
    - Each (N) has an edge count (EC) = number of unique Edges (E) it connects
    - Each (N) has a node weight (NW) = total number of Edges (E) it connects
    - Each (E) has an edge weight (EW) = number of times it connects (N) to (N)

Goals:
- Load, scrub and analyze data & graphs to help understand:
    - Most heavily referenced Nodes
    - Most heavily referenced Edges

Method:
- Start by defining data in-line
- Later import it from CSV or JSON or whatever
"""

# import matplotlib.pyplot as plt         # type: ignore
# import networkx as nx                   # type: ignore
import pandas as pd                     # type: ignore
# import pickle

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
        self.EDGES = dict()

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
                      p_set_nm: str):
        """
        Input file is JSON.
        - Nodes (N):
            - Characters (c)
            - Groups (g)
            - Places (p)
            - Scenes (s)
            - (later, add times, using a game calendar)
        - Edges (E), all bi-directional (D2), none are self-referential:
            - c-p
            - c-s
            - g-p
            - g-s
            - p-s

        :args:
        - p_set_nm (str): Name of a schema/ontology file ,w/o extension.
        """
        ds = FI.get_schema(p_set_nm)
        set_nm = list(ds.keys())[0]
        self.SETS[set_nm] = list(ds.values())[0]
        self.NODES[set_nm] = dict()
        for n in ("scenes", "people", "groups", "places"):
            self.NODES[set_nm][n] = list()
        for rec in self.SETS[set_nm]:
            scene = f"{rec['scene_num']:03d}" + " " + rec['scene_nm']
            self.NODES[set_nm]["scenes"].append(scene)
            for node_type in ("people", "groups", "places"):
                for node in rec[node_type]:
                    self.NODES[set_nm][node_type].append(node)
        for n in ("scenes", "people", "groups", "places"):
            self.NODES[set_nm][n] = sorted(list(set(self.NODES[set_nm][n])))
        pp((self.NODES))
