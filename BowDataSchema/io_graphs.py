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
            -- A label (L), which is like a record type ID
            -- A label is _NOT_ a Unique record ID.
            -- Optionally, may have ontological attributes, i.e., associated
               with a set of fields (F1, F2, .., Fn)
            -- Labels for Nodes and Edges are distinct.
        - For (N), there is a unique ID (NID), which is a unique name string
            -- A list of unique Node IDs (NID) handles de-duplication of ID's.
        - For each Edge (E), there is a From Node (FR) and a To Node (TO)
            -- For (E) in (D1), (FR) and (TO) indicate vector direction
            -- For (E) in (D2), a vector is assumed in both directions
            -- (E) is the set of all (FR, TO) pairs, where
               all (D2) edges are expanded into two (D1) vectors.
            -- Unique (E) pairs tie to all (1..n) Labels (L) for that pair.
        - For (L) in (N) or (Dn), (F1, F2, .., Fn) is a unique ontology (ONT).
          Ontologies/Fields
            -- Group sets of attributes (F) for Labels (L)
            -- Are documented but not enforced
        - Nodes, Edges, Labels, Topics, Ontologies are organized into
            a single consolidated Affinity dataset (A)
            -- (A) is a dictionary containing Affinity-"Plus" info
            -- It consolidates the Nodes and Edges from all Topics
            -- It is Affinity"-Plus" since it contains attribute,
               label, and topic info in addition to Node:Edge links.
        """
        pd.options.mode.chained_assignment = None
        self.SHEETS = dict()       # raw dataframes {T: df(S)}
        # unique node ID's {NID: T, L, F: {F1, F2, .., Fn}}
        self.NODES = dict()
        # unique edges {(FR, TO): T, L, F: {F1, F2, .., Fn}}
        self.EDGES = dict()
        self.FIELDS = dict()       # field names {E|N: {L: (F1, F2, .., Fn)}}
        # cleaned, consolidated Affinity-Plus data
        # Is this necessary in addition to NODES and EDGES?
        # Probably not.
        self.AFFINITY = dict()
        # Graphing globals
        self.G = nx.Graph()        # Networkx graph object

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

    def get_raw_dataframes(self,
                           p_file_nm):
        """Init topics (sheet names + descriptions) from manifest tab.
           Load raw data for all sheets to dataframes.

        :args:
        - p_file_nm (str): Name of the workbook.
        :sets:
        - (class attribute): SHEETS
        """
        file_path =\
            path.join(RI.get_config_value('config_path'), p_file_nm)
        manifest_df = self.get_sheet_data(file_path, "manifest")
        if manifest_df is not None:
            for _, topic in manifest_df['Topics'].items():
                self.SHEETS[topic] = self.get_sheet_data(file_path, topic)

    def get_unique_values(self,
                          s_df,
                          cols: list):
        """For the given dataframe, return list of unique values
           in the combination of named columns.

        :args:
        - s_df (DataFrame): Raw sheet being processed
        - col_nm (list): Column names to select on
        :returns:
        - (list): Unique values in column(s) or None
        """
        vals = s_df.dropna(subset=cols)
        vals = vals.drop_duplicates(subset=cols, keep='first')
        if len(cols) == 1:
            vals = vals[cols[0]].tolist()
        else:
            vals = vals[cols].values.tolist()
        vals.sort()
        return vals

    def set_nodes(self,
                  p_topic,
                  s_df):
        """Fill out Nodes indexes. Reject duplicate node names.

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - s_df (datframe): Raw data dataframe for the sheet.
        :sets:
        - (class attribute): NODES
        """
        nids = s_df.dropna(subset=['n_name'])
        nids = nids.drop_duplicates(subset=['n_name'], keep='first')
        nids = nids['n_name'].tolist()
        nids.sort()
        if nids is not None:
            for n_nm in nids:
                if n_nm not in self.NODES.keys():
                    self.NODES[n_nm] = {'T': p_topic}
                else:
                    print(f"{CI.txt.err_record}: DUP {n_nm}: {p_topic}")

    def set_edges(self,
                  p_topic,
                  s_df):
        """Fill out the (E) Edges indexes.

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - s_df (datframe): Raw data dataframe for the sheet.
        :sets:
        - (class attribute): EDGES
        """
        def add_edges(edges, p_topic):
            if edges is not None:
                for vector in edges:
                    if tuple(vector) not in self.EDGES.keys():
                        self.EDGES[tuple(vector)] = {'T': p_topic}

        edges = self.get_unique_values(s_df, ['d1_node_from', 'd1_node_to'])
        if edges is not None:
            add_edges(edges, p_topic)
        edges = self.get_unique_values(s_df, ['d2_node_from', 'd2_node_to'])
        if edges is not None:
            add_edges(edges, p_topic)
        edges = self.get_unique_values(s_df, ['d2_node_to', 'd2_node_from'])
        if edges is not None:
            add_edges(edges, p_topic)

    def set_labels(self,
                   s_df):
        """Fill out labels for Nodes and Edges.

        :args:
        - s_df (datframe): Raw data dataframe for the sheet.
        :sets:
        - (class attribute): NODES, EDGES
        """
        labels = self.get_unique_values(
            s_df, ['n_name', 'n_label'])
        if labels is not None:
            for n_list in labels:
                self.NODES[n_list[0]]['L'] = n_list[1]

        labels = self.get_unique_values(
            s_df, ['d1_node_from', 'd1_node_to', 'd1_label'])
        if labels is not None:
            for v_list in labels:
                self.EDGES[tuple(v_list[:2])]['L'] = v_list[2]

        labels = self.get_unique_values(
            s_df, ['d2_node_from', 'd2_node_to', 'd2_label'])
        if labels is not None:
            for v_list in labels:
                self.EDGES[tuple(v_list[:2])]['L'] = v_list[2]
                self.EDGES[(v_list[1], v_list[0])]['L'] = v_list[2]

    def gather_ontologies(self,
                          n_or_e: str,
                          p_label: str,
                          p_fields: list):
        """Gather ontologies from the label and fields list.

        :args:
        - n_or_e (str): "N" or "E" (Node or Edge)
        - p_label (str): Label being processed.
        - p_fields (list): List of field names for the label.
        :sets:
        - (class attribute): FIELDS
        """
        if n_or_e not in self.FIELDS.keys():
            self.FIELDS[n_or_e] = dict()
        if p_label not in self.FIELDS[n_or_e].keys():
            self.FIELDS[n_or_e][p_label] = p_fields

    def gather_node_fields(self,
                           node_df,
                           p_topic):
        """Gather field names for Nodes view of Sheet data.
           Collect field names and field values.

        :args:
        - node_df (dataframe): View of dataframe for Nodes.
        - p_topic (str): Name of the sheet/topic being processed.
        :sets:
        - (class attribute): NODES
        """
        node_df = node_df.dropna(subset=['n_name'])
        node_df = node_df.drop_duplicates(subset=['n_name'], keep='first')
        if not node_df.empty:
            n_lbls = {n_nm: n_info["L"]
                      for n_nm, n_info in self.NODES.items()
                      if "L" in n_info.keys() and n_info["T"] == p_topic}
            for n_nm, n_lbl in n_lbls.items():
                lbl_df = node_df.loc[node_df['n_label'] == n_lbl]
                if not lbl_df.empty:
                    lbl_df.drop(['n_label', 'n_name'], axis=1, inplace=True)
                    lbl_df = lbl_df.dropna(axis=1, how='all')
                    if not lbl_df.empty:
                        fields = lbl_df.columns.values.tolist()
                        self.gather_ontologies("N", n_lbl, fields)
                        self.NODES[n_nm]["F"] = dict()
                        value_row = node_df.loc[node_df['n_name'] == n_nm]
                        if not value_row.empty:
                            for fld_nm in fields:
                                self.NODES[n_nm]["F"][fld_nm] =\
                                    value_row[fld_nm].values[0]

    def gather_edge_fields(self,
                           p_d,
                           edge_df,
                           p_topic):
        """Gather field names and values for Edges views of Sheet data.
           Collect field names and field values.

        :args:
        - p_d (str): "d1" or "d2" = edge type
        - edge_df (dataframe): View of dataframe for Edges.
        - p_topic (str): Name of the sheet/topic being processed.
        :sets:
        - (class attribute): EDGES
        """
        edge_df = edge_df.dropna(subset=[f'{p_d}_node_from', f'{p_d}_node_to'])
        if not edge_df.empty:
            e_lbls = {e_nm: e_info["L"]
                      for e_nm, e_info in self.EDGES.items()
                      if "L" in e_info.keys() and e_info["T"] == p_topic}
            for e_nm, e_lbl in e_lbls.items():
                lbl_df = edge_df.loc[edge_df[f'{p_d}_label'] == e_lbl]
                if not lbl_df.empty:
                    lbl_df.drop(
                        [f'{p_d}_label', f'{p_d}_node_from', f'{p_d}_node_to'],
                        axis=1, inplace=True)
                    lbl_df = lbl_df.dropna(axis=1, how='all')
                    if not lbl_df.empty:
                        fields = lbl_df.columns.values.tolist()
                        self.gather_ontologies("E", e_lbl, fields)
                        self.EDGES[e_nm]["F"] = dict()
                        value_row = edge_df.loc[
                            (edge_df[f'{p_d}_label'] == e_lbl) &
                            (edge_df[f'{p_d}_node_from'] == e_nm[0]) &
                            (edge_df[f'{p_d}_node_to'] == e_nm[1])]
                        if not value_row.empty:
                            for fld_nm in fields:
                                self.EDGES[e_nm]["F"][fld_nm] =\
                                    value_row[fld_nm].values[0]

    def set_fields(self,
                   p_topic,
                   s_df):
        """Fill out the FIELDS dictionary.
           - For each section (N, D1, D2) of the sheet,
             identify non-name, non-label field/attribute columns.
           - For each label on the sheet, determine which
             field columns are non-null.
           - Accumulate fields across topics as needed for each LABEL.

            :args:
            - p_topic (str): Name of sheet
            - s_df (dataframe): Raw sheet dataframe.
            :sets:
            - (class attribute): FIELDS

        """
        self.gather_node_fields(s_df.iloc[:, s_df.columns.get_loc('N') + 1:
                                          s_df.columns.get_loc('D2')],
                                p_topic)
        self.gather_edge_fields('d1',
                                s_df.iloc[:, s_df.columns.get_loc('D1') + 1:],
                                p_topic)
        self.gather_edge_fields('d2',
                                s_df.iloc[:, s_df.columns.get_loc('D2') + 1:
                                          s_df.columns.get_loc('D1')],
                                p_topic)

    def set_affinity_data(self,
                          p_file_nm: str):
        """Load all data from the affinity data workbook.
           - Read its manifest tab to initialize TOPICS (T)
           - Load the raw data into SHEETS data frames (S).
           - Parse each (S):
             -- Fill out Nodes list
             -- Fill out Edges list
             -- Fill out Labels lists
             -- Fill out Fields dictionary
           - Load the Affinity dictionary

        @DEV:
           - Create an (A) affinity dataframe if needed
           - Create the (G) graph.

        Args:
            p_file_nm (str): Name of spreadsheet in /config.
        """
        self.get_raw_dataframes(p_file_nm)
        for topic, s_df in self.SHEETS.items():
            self.set_nodes(topic, s_df)
            self.set_edges(topic, s_df)
            self.set_labels(s_df)
            self.set_fields(topic, s_df)

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
            f"Data Types\n{CI.txt.val_ul}\n{self.SHEETS.dtypes}\n\n",
            f"Rows, Columns\n{CI.txt.val_ul}\n{self.SHEETS.shape}\n\n",
            f"Sample Data\n{CI.txt.val_ul}\n{str(self.SHEETS.head())}"))

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
