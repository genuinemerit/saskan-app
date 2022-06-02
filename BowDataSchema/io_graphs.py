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
import pandas as pd                     # type: ignore

from os import path
from pandas import DataFrame
from pprint import pformat as pf        # noqa: F401
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
    def __init__(self):
        """Class for displaying graphs."""
        self.G = nx.Graph()       # Networkx graph object
        self.CONFIG_PATH = RI.get_config_value('config_path')
        self.FILE_PATH = None
        self.GRP_NM = None        # Logical group of nodes/edge = sheet name
        self.GRP_DF = None        # Raw data load dataframe = sheet data
        self.GRP_DATA = dict()    # Work area for cleaning one sheet's data
        self.PLC_DATA = dict()    # Cleaned, consolidated Places affinity+ data
        self.PLC_ONT = dict()     # Derived ontologies = node or edge attr sets
        # Organized data by graph geometry
        for ggk in CI.gg_info.keys():
            self.GRP_DATA[ggk] = None
            self.PLC_DATA[ggk] = None
            self.PLC_ONT[ggk] = dict()

    def get_sheet_data(self,
                       p_file_nm: str,
                       p_sheet_nm: str):
        """Load data from a spreadsheet into a dataframe.
        Derive file type from extension.
        Once it is loaded we'll refer to this as the group data.

        @DEV:
            If we could gather all the sheet names and go from there
            in order to parse the entire workbook, that would be swell.
            Supposedly that is doable with excel, but with ods, this
            just gives me the column names on the first sheet:
            print(f"Sheet name(s): {self.GRP_DF.keys()}")

        Args:
            p_file_nm (str): Name of ods spreadsheet in /config.
            p_sheet_nm (str): Name of sheet to load.
        """
        def get_excel_data():
            """Get data from Excel spreadsheet.
            If no sheet name is specified, it may load all sheets?
            """
            if self.GRP_NM is None:
                self.GRP_DF = pd.read_excel(self.FILE_PATH)
            else:
                self.GRP_DF = pd.read_excel(self.FILE_PATH,
                                           sheet_name=p_sheet_nm)

        def get_ods_data():
            """Get data from OpenDocument spreadsheet.
            If no sheet name is specified, it loads the first sheet.
            """
            if self.GRP_NM is None:
                self.GRP_DF =\
                    pd.read_excel(self.FILE_PATH, engine='odf')
            else:
                self.GRP_DF = pd.read_excel(self.FILE_PATH, engine='odf',
                                           sheet_name=p_sheet_nm)

        self.FILE_PATH = path.join(self.CONFIG_PATH, p_file_nm)
        self.GRP_NM = p_sheet_nm.strip()
        ss_type = self.FILE_PATH.split('.')[-1]
        if ss_type in ['xlsx', 'xls']:
            get_excel_data()
        elif ss_type in ['ods']:
            get_ods_data()
        else:
            print(f"{CI.txt.err_file}: {self.FILE_PATH}")

    def get_group_info(self):
        """Return info about the raw group dataframe."""
        pd.set_option('display.max_columns', None)
        return pf((
            f"\n{CI.txt.val_group}\n{CI.txt.val_ul}{self.GRP_NM}\n\n",
            f"Data Types\n{CI.txt.val_ul}\n{self.GRP_DF.dtypes}\n\n",
            f"Rows, Columns\n{CI.txt.val_ul}\n{self.GRP_DF.shape}\n\n",
            f"Sample Data\n{CI.txt.val_ul}\n{str(self.GRP_DF.head())}"))

    def scrub_places_data(self):
        """Organize Places data into cleaned frames.

        - Break out sheet data into 3 dataframes: N, D2, D1.
        - Add a column for the group (sheet) name to each dataframe.
        - Rename columns to remove prefixes.
        - Remove rows with no value in `label` column.
        - Derive and store ontology info from non-static column names.

        - Process properly for multiple sheets.
        - Minimize redundant metadata.
        """
        def get_geometry_col_indexes():
            """Determine what columns belong to which geometries."""
            colix_dict = {
                'n': self.GRP_DF.columns.get_loc('N'),
                'd2': self.GRP_DF.columns.get_loc('D2'),
                'd1': self.GRP_DF.columns.get_loc('D1')}
            return colix_dict

        def set_places_data_by_geometry(p_colix: dict):
            """Separate GRP_DATA according to gg column slices.
            Drop the geometry (first) column from each slice.
            Reminder:
            - .iloc[] selects rows and columns by index
            - syntax:  .iloc[row_slice, col_slice]
            - `:` means take all in a slice.
            """
            self.GRP_DATA['N'] = DataFrame(
                self.GRP_DF.iloc[:, p_colix['n'] + 1:p_colix['d2'] - 1])
            self.GRP_DATA['D2'] = DataFrame(
                self.GRP_DF.iloc[:, p_colix['d2'] + 1:p_colix['d1'] - 1])
            self.GRP_DATA['D1'] = DataFrame(
                self.GRP_DF.iloc[:, p_colix['d1'] + 1:])

        def scrub_column_names():
            """Remove geometry prefixes from column names.
            Add "group" column to each dataframe.
            """
            for ggk in CI.gg_info.keys():
                gg = ggk.lower() + "_"
                fix_cols =\
                    [fc.replace(gg, "") for fc in self.GRP_DATA[ggk].columns]
                self.GRP_DATA[ggk].columns = fix_cols
                self.GRP_DATA[ggk]['group'] = self.GRP_NM

        def remove_rows_with_empty_labels():
            """Delete rows where label is NaN or empty."""
            for df_key in self.GRP_DATA.keys():
                self.GRP_DATA[df_key] = self.GRP_DATA[df_key].dropna(
                    subset=['label'])

        def derive_ontology_info():
            """Derive ontology info from column names.
            @DEV:
            - Later, refactoring?... consider cases where the same label
              may indicate a different ontology.
            - Probably would want to add attributes to existing ontology
              rather than define a new / alternative one.
            - The "ontology" should be loose. These are attributes 
              suggested for use with this node or edge. Neither mandatory
              (can be null) nor restrictive (can be other attributes).

            The way I have it set, the ontology is defined only by the
            first incidence of a given label within a geometry.

            Reminder:
            - A `set` is an iterable collection of unique values.
            - Denoted in python by `{}`.
            """
            for ggk, df in self.GRP_DATA.items():
                ont_set = (set(df.columns) - CI.gg_static_attrs)
                if ont_set:
                    for lbl in df["label"].unique():
                        if lbl not in self.PLC_ONT[ggk].keys():
                            self.PLC_ONT[ggk][lbl] = list()
                        self.PLC_ONT[ggk][lbl].append(ont_set)

        def append_to_places_data():
            """Append scrubbed Group data to Places dataframe.

            *** PICK UP HERE ***
            @DEV:
            - Needs work to account for additional attributes that
              may be added to the geometry from each sheet.
            - Make sure it gets added to the consolidated dataframe.
            - Make sure the rows for the group get all their values
              carried over.
            - Make sure values for all rows are getting loaded at 
              the group level. e.g. is `geo_ty` really empty for 
              all items in the `The Heliopticon` group?
            """
            for ggk, grp_df in self.GRP_DATA.items():
                if self.PLC_DATA[ggk] is None:
                    self.PLC_DATA[ggk] = DataFrame(grp_df)
                else:
                    self.PLC_DATA[ggk] =\
                        self.PLC_DATA[ggk].append(grp_df, ignore_index=True)

        colix = get_geometry_col_indexes()
        set_places_data_by_geometry(colix)
        scrub_column_names()
        remove_rows_with_empty_labels()
        derive_ontology_info()
        append_to_places_data()
        pp((self.GRP_DATA))
        pp((self.PLC_ONT))
        pp((self.PLC_DATA))

        """
        for col in self.GRP_DF.columns:
            if col in CI.ggeometry.keys():
                gg = col
            if col not in self.PLC_DATA.keys(): 
                self.PLC_DATA[gg] = {"cols": [],
                                   "desc": CI.ggeometry[gg],
                                   "df": None}
            else:
                self.PLC_DATA[gg]["cols"].append(col)
        for gg in CI.ggeometry.keys():
            df = DataFrame(self.GRP_DF[self.PLC_DATA[gg]["cols"]])
            df_null_idx = df.index[df[gg.lower() + "_label"].isna()]
            df.drop(index=df_null_idx, inplace=True)
            df["group"] = self.GRP_NM
            fix_cols = list()
            for col in df.columns:
                fix_cols.append(col.replace((gg.lower() + "_"), ""))
            df.columns = fix_cols
            self.PLC_DATA[gg]["df"] = df
            ont_set = (set(fix_cols) - CI.gg_static)
            print(ont_set)
            if ont_set:
                if gg not in self.PLC_ONT.keys():
                    self.PLC_ONT[gg] = dict()
                for label in df["label"].unique():
                    if label not in self.PLC_ONT[gg].keys():
                        self.PLC_ONT[gg][label] = list()
                    self.PLC_ONT[gg][label].append(ont_set)
        print(self.PLC_DATA)  # DEBUG only
        print(self.PLC_ONT)  # DEBUG only
        """

    def make_network_diagram(self,
                             p_img_title: str):
        """Generate a drawing from the Graph object.

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
