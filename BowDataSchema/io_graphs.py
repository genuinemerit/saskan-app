#!python
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
        """Class for displaying graphs.

        Prototype works with data in spreadsheet `places_data.ods`.
        It is a kind of affinity dataset, spread across multiple tabs.
        Each tab is defined by "topic" = the sheet name
        - T is informational only, becomes an attribute of the Node or Edge.
        - Keep a list containing:
            -- Topic name (T)
            -- Node Names (ID) associated with the Topic

        The data on a given sheet (S) contains some raw affinity data.
        Each (S) for a (T) may contain 0..n of each:
        - Node (N) definitions
        - Single-directional (D1) edges
        - Bi-directional (D2) edges

        The class methods parse out:
        - For both (N) and (Dn):
            -- A label (L), which is like a record type ID or sub-topic
            -- A label is _NOT_ a Unique record ID.
            -- Optionally, may be additional attribute fields (F0..Fn)
        - For (N), there is a unique ID (ID), which is a unique name string
            -- A list of IDs (NID) handle de-duplication of ID's.
        - For (Dn), there is a From Node (FR) and a To Node (TO)
            -- For (D1), (FR) and (TO) indicate direction of vector
            -- FOr (D2), a vector is assumed in both directions
        - For {(N) | (Dn), (F0)..(Fn)}, a set of unique ontologies (ONT)
          is derived.  Ontologies are
            -- Used to group attributes for Nodes or Edges
            -- Defined by a string, which is a derived name or UID
            -- Unique, but not enforced
        - Nodes and Edges are organized into consolidated Affinity dataset (A)
            -- (A) is a dataframe containing Affinity-"Plus" info
            -- It consolidates the Nodes and Edges
            -- It is Affinity"-Plus" since it contains attributes,
               labels, topic and label info in addition to Node:Edge links.
        - A few control strings are provided by the ConfigIO class:
            -- gg_info: dict = {
                'N': "Nodes",
                'D2': "Bi-directional Edges",
                'D1': "Single-directional Edges"}
            -- gg_static_attrs: set = {'label', 'node_from',
                                       'node_to', 'topic'}
        """
        self.TOPICS = dict()      # Topics & Labels {T: [(str(ID), str(desc))]}
        self.SHEETS = dict()      # raw dataframes {T: df(S)}
        self.NODEIDS = dict()     # unique node UIDS {NID: original_ID+topic}
        self.WORKDATA = dict()    # Work area for cleaning one S
        self.AFFINITY = dict()    # Cleaned, consolidated Affinity-Plus data
        self.ONTOLG = dict()      # Derived ontologies = attribute sets
        # Organized data by graph geometry
        for ggi in CI.gg_info.keys():
            self.WORKDATA[ggi] = None
            self.AFFINITY[ggi] = None
            self.ONTOLG[ggi] = dict()
        # Graphing globals
        self.G = nx.Graph()       # Networkx graph object

    def get_sheet_data(self,
                       p_file_path,
                       p_sheet_nm):
        """Get data from an OpenDocument spreadsheet.

        :args:
        - p_file_path (str): Path to the workbook.
        - p_sheet_nm (str): Name of sheet to load.
        :return:
        - (DataFrame): DataFrame of the sheet.
        """
        sheet_df = None
        ss_type = p_file_path.split('.')[-1].lower()
        if ss_type.lower() in ('xlsx', 'xls'):
            sheet_df = pd.read_excel(p_file_path,
                                     sheet_name=p_sheet_nm)
        elif ss_type.lower() in ('ods'):
            sheet_df = pd.read_excel(p_file_path, engine='odf',
                                     sheet_name=p_sheet_nm)
        else:
            print(f"{CI.txt.err_file}: {p_file_path}")
        return sheet_df

    def get_affinity_data(self,
                          p_file_nm: str):
        """Load all data from the affinity data workbook.
           - Read its manifest tab to initialize TOPICS (T)
           - Load the raw data into SHEETS data frames (S).
           - Parse each (S):
             -- Fill out (NID) and (T) lists

        Args:
            p_file_nm (str): Name of spreadsheet in /config.
        """
        file_path = path.join(RI.get_config_value('config_path'), p_file_nm)

        # Get topics and load the raw sheet data
        manifest_df = self.get_sheet_data(file_path, "manifest")
        if manifest_df is not None:
            for i, t in manifest_df['Topics'].items():
                self.TOPICS[t] =\
                    {"desc": manifest_df["Description"][i], "N": []}
        for t in self.TOPICS.keys():
            self.SHEETS[t] = self.get_sheet_data(file_path, t)

        for t, s in self.SHEETS.items():
            # Fill out (T) list
            node_names = s.dropna(subset=['n_name'])['n_name'].tolist()
            self.TOPICS[t]["N"] += node_names
            # Fill out (NID) list
            # I really should NOT have any duplicate node names
            # The ones I found really were unnecessary dups,
            #  not truly discrete nodes. They should generate
            #  a warning, maybe include on the NODEIDs report,
            #  but flagged as dups and then not included in (A).
            for n in node_names:
                tn = t.lower().replace(' ', '-')
                if n not in self.NODEIDS.values():
                    nid = n
                elif f"{n}_{tn}" not in self.NODEIDS.values():
                    nid = f"{n}_{tn}"
                else:
                    i = RI.get_token()
                    nid = f"{n}_{tn}_{i}"
                self.NODEIDS[(t, n)] = nid
        pp((self.TOPICS))
        pp((self.NODEIDS))

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
                'n': self.SHEET.columns.get_loc('N'),
                'd2': self.SHEET.columns.get_loc('D2'),
                'd1': self.SHEET.columns.get_loc('D1')}
            return colix_dict

        def set_places_data_by_geometry(p_colix: dict):
            """Separate WORKDATA according to gg column slices.
            Drop the geometry (first) column from each slice.
            Reminder:
            - .iloc[] selects rows and columns by index
            - syntax:  .iloc[row_slice, col_slice]
            - `:` means take all in a slice.
            """
            self.WORKDATA['N'] = DataFrame(
                self.SHEET.iloc[:, p_colix['n'] + 1:p_colix['d2'] - 1])
            self.WORKDATA['D2'] = DataFrame(
                self.SHEET.iloc[:, p_colix['d2'] + 1:p_colix['d1'] - 1])
            self.WORKDATA['D1'] = DataFrame(
                self.SHEET.iloc[:, p_colix['d1'] + 1:])

        def scrub_column_names():
            """Remove geometry prefixes from column names.
            Add "group" column to each dataframe.
            """
            for ggk in CI.gg_info.keys():
                gg = ggk.lower() + "_"
                fix_cols =\
                    [fc.replace(gg, "") for fc in self.WORKDATA[ggk].columns]
                self.WORKDATA[ggk].columns = fix_cols
                self.WORKDATA[ggk]['group'] = self.TOPIC

        def remove_rows_with_empty_labels():
            """Delete rows where label is NaN or empty."""
            for df_key in self.WORKDATA.keys():
                self.WORKDATA[df_key] = self.WORKDATA[df_key].dropna(
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
            for ggk, df in self.WORKDATA.items():
                ont_set = (set(df.columns) - CI.gg_static_attrs)
                if ont_set:
                    for lbl in df["label"].unique():
                        if lbl not in self.ONTOLG[ggk].keys():
                            self.ONTOLG[ggk][lbl] = list()
                        self.ONTOLG[ggk][lbl].append(ont_set)

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
            for ggk, SHEET in self.WORKDATA.items():
                if self.AFFINITY[ggk] is None:
                    self.AFFINITY[ggk] = DataFrame(SHEET)
                else:
                    self.AFFINITY[ggk] =\
                        self.AFFINITY[ggk].append(SHEET, ignore_index=True)

        # #####################################################################
        # ## scrub_places_data() main
        # #####################################################################
        colix = get_geometry_col_indexes()
        set_places_data_by_geometry(colix)
        scrub_column_names()
        remove_rows_with_empty_labels()
        derive_ontology_info()
        append_to_places_data()
        pp((self.WORKDATA))
        pp((self.ONTOLG))
        pp((self.AFFINITY))

        """
        for col in self.SHEET.columns:
            if col in CI.ggeometry.keys():
                gg = col
            if col not in self.AFFINITY.keys():
                self.AFFINITY[gg] = {"cols": [],
                                   "desc": CI.ggeometry[gg],
                                   "df": None}
            else:
                self.AFFINITY[gg]["cols"].append(col)
        for gg in CI.ggeometry.keys():
            df = DataFrame(self.SHEET[self.AFFINITY[gg]["cols"]])
            df_null_idx = df.index[df[gg.lower() + "_label"].isna()]
            df.drop(index=df_null_idx, inplace=True)
            df["group"] = self.TOPIC
            fix_cols = list()
            for col in df.columns:
                fix_cols.append(col.replace((gg.lower() + "_"), ""))
            df.columns = fix_cols
            self.AFFINITY[gg]["df"] = df
            ont_set = (set(fix_cols) - CI.gg_static)
            print(ont_set)
            if ont_set:
                if gg not in self.ONTOLG.keys():
                    self.ONTOLG[gg] = dict()
                for label in df["label"].unique():
                    if label not in self.ONTOLG[gg].keys():
                        self.ONTOLG[gg][label] = list()
                    self.ONTOLG[gg][label].append(ont_set)
        print(self.AFFINITY)  # DEBUG only
        print(self.ONTOLG)  # DEBUG only
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

    def get_group_info(self):
        """Return info about the raw group dataframe."""
        pd.set_option('display.max_columns', None)
        return pf((
            f"\n{CI.txt.val_group}\n{CI.txt.val_ul}{self.TOPIC}\n\n",
            f"Data Types\n{CI.txt.val_ul}\n{self.SHEET.dtypes}\n\n",
            f"Rows, Columns\n{CI.txt.val_ul}\n{self.SHEET.shape}\n\n",
            f"Sample Data\n{CI.txt.val_ul}\n{str(self.SHEET.head())}"))

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
