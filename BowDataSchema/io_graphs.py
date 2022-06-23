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
        self.NODES = dict()        # unique node ID's
                                   #   {NID: T, L, F1, F2, .., Fn})]
        self.EDGES = dict()        # unique D1 edges
                                   #   {(FR, TO): T, L, F1, F2, .., Fn}
        self.FIELDS = dict()       # attributes / fields [(F1, F2, .., Fn)]
        self.AFFINITY = dict()     # cleaned, consolidated Affinity-Plus data
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
        - (Class): SHEETS
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
        pp(("vals", vals))
        return vals

    def set_nodes(self,
                  p_topic,
                  s_df):
        """Fill out Nodes indexes. Reject duplicate node names..

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - s_df (datframe): Raw data dataframe for the sheet.
        :sets:
        - (Class): NODES
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
        - (Class): EDGES
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
        """Fill out lists of unique labels for Nodes and Edges.

        :args:
        - s_df (datframe): Raw data dataframe for the sheet.
        :sets:
        - (Class): LABELS

        @DEV:
        - Allow for multiple labels per node, per edge.
        - ["L"] --> list()
        """
        labels = self.get_unique_values(
            s_df, ['n_name', 'n_label'])
        if labels is not None:
            for n_list in labels:
                self.NODES[n_list[0]]['L'] = n_list[1]

        labels = self.get_unique_values(
            s_df, ['d1_node_from', 'd1_node_to', 'd1_label'])
        pp(("labels", labels))
        if labels is not None:
            for v_list in labels:
                self.EDGES[tuple(v_list[:2])]['L'] = v_list[2]

        # Need to update the reverse entry also?
        labels = self.get_unique_values(
            s_df, ['d2_node_from', 'd2_node_to', 'd2_label'])
        pp(("labels", labels))
        if labels is not None:
            for v_list in labels:
                self.EDGES[tuple(v_list[:2])]['L'] = v_list[2]

    def append_fields(self,
                      p_N_or_E: str,
                      p_lbl: str,
                      p_lbl_df):
        """Select field names used with the given label.
           Add them to fields list if not yet there.

        @DEV:
            Add the fields to the NODES and EDGES lists
            instead of to the FIELDS list.
            Similar to how LABELS were handled.

        :args:
        - p_N_or_E (str): "N" or "E" (Node or Edge)
        - p_lbl (str): Label being processed.
        - p_lbl_df (dataframe): View of dataframe for Nodes or Edges
             containing only candidate fields/attributes for the label.
        """
        if "N" not in self.FIELDS:
            self.FIELDS["N"] = dict()
        if "E" not in self.FIELDS:
            self.FIELDS["E"] = dict()
        if not p_lbl_df.empty:
            p_lbl_df = p_lbl_df.dropna(axis=1, how='all')
            fields = p_lbl_df.columns.values.tolist()
            if p_lbl in self.FIELDS[p_N_or_E]:
                for fld in fields:
                    if fld not in self.FIELDS[p_N_or_E][p_lbl]:
                        self.FIELDS[p_N_or_E][p_lbl].append(fld)
            else:
                self.FIELDS[p_N_or_E][p_lbl] = fields

    def gather_node_attrs(self,
                          node_df,
                          p_labels):
        """Gather fields / attributes for Nodes view of sheet.

        :args:
        - node_df (dataframe): View of dataframe for Nodes.
        """
        node_df = node_df.dropna(subset=['n_name'])
        node_df = node_df.drop_duplicates(subset=['n_name'], keep='first')
        for lbl in p_labels["N"]:
            lbl_df = node_df.loc[node_df['n_label'] == lbl]
            lbl_df.drop(['n_label', 'n_name'], axis=1, inplace=True)
            self.append_fields("N", lbl, lbl_df)

    def gather_edge_attrs(self,
                          p_d,
                          edge_df,
                          p_labels):
        """Gather fields/attributes for Edges views of sheet.

        :args:
        - p_d (str): "d1" or "d2" = edge type
        - edge_df (dataframe): View of dataframe for Edges.
        """
        for lbl in p_labels["E"]:
            lbl_df = edge_df.loc[edge_df[f'{p_d}_label'] == lbl]
            lbl_df.drop(
                [f'{p_d}_label', f'{p_d}_node_from', f'{p_d}_node_to'],
                axis=1, inplace=True)
            self.append_fields("E", lbl, lbl_df)

    def set_fields(self,
                   s_df,
                   p_labels):
        """Fill out the FIELDS dictionary.
           - For each section (N, D1, D2) of the sheet,
             identify non-name, non-label field/attribute columns.
           - For each label on the sheet, determine which
             field columns are non-null.
           - Accumulate fields across topics as needed for each LABEL.

            :args:
            - s_df (dataframe): Raw sheet dataframe.
            :sets:
            - (Class): FIELDS
        """
        self.gather_node_attrs(s_df.iloc[:, s_df.columns.get_loc('N') + 1:
                                         s_df.columns.get_loc('D2')],
                               p_labels)
        self.gather_edge_attrs('d1',
                               s_df.iloc[:, s_df.columns.get_loc('D1') + 1:],
                               p_labels)
        self.gather_edge_attrs('d2',
                               s_df.iloc[:, s_df.columns.get_loc('D2') + 1:
                                         s_df.columns.get_loc('D1')],
                               p_labels)

    def set_affinity_matrix(self):
        """Fill out the AFFINITY matrix."""
        self.AFFINITY = {node: {"topic": topic} for node, topic in self.NODES}

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
           - Create the (A) affinity dataframe.
           - Create the (G) graph.

        Args:
            p_file_nm (str): Name of spreadsheet in /config.
        """
        self.get_raw_dataframes(p_file_nm)
        labels: dict = {"N": dict(), "E": dict()}
        for topic, s_df in self.SHEETS.items():
            self.set_nodes(topic, s_df)
            self.set_edges(topic, s_df)
            self.set_labels(s_df)
            self.set_fields(s_df, labels)
        self.set_affinity_matrix()

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
                'n': self.SHEETS.columns.get_loc('N'),
                'd2': self.SHEETS.columns.get_loc('D2'),
                'd1': self.SHEETS.columns.get_loc('D1')}
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
                self.SHEETS.iloc[:, p_colix['n'] + 1:p_colix['d2'] - 1])
            self.WORKDATA['D2'] = DataFrame(
                self.SHEETS.iloc[:, p_colix['d2'] + 1:p_colix['d1'] - 1])
            self.WORKDATA['D1'] = DataFrame(
                self.SHEETS.iloc[:, p_colix['d1'] + 1:])

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
                        if lbl not in self.FIELDS[ggk].keys():
                            self.FIELDS[ggk][lbl] = list()
                        self.FIELDS[ggk][lbl].append(ont_set)

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
        pp((self.FIELDS))
        pp((self.AFFINITY))

        """
        for col in self.SHEETS.columns:
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
                if gg not in self.FIELDS.keys():
                    self.FIELDS[gg] = dict()
                for label in df["label"].unique():
                    if label not in self.FIELDS[gg].keys():
                        self.FIELDS[gg][label] = list()
                    self.FIELDS[gg][label].append(ont_set)
        print(self.AFFINITY)  # DEBUG only
        print(self.FIELDS)  # DEBUG only
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
