#!python
"""
:module:    se_diagram_wdg.py

:author:    GM (genuinemerit @ pm.me)

Use NetworkX and matplotlib modules to generate graph diagrams.
Use music21 to assign parts, phrases, pitches, notes, durations, etc.
 to nodes, then to generate scores and midi files.

Generate the graph using matplotlib.pyplot and networkx.
This class has no framework GUI elements.
Figures generated then saved to a file in the app /save directory.
It is up to the calling class to display the figure.

Prototype:
    - Data in spreadsheet `places_data.ods`.
    - A kind of affinity dataset spread across multiple tabs.
    - Each tab defines a Topic (T) = the sheet name
    - (T) becomes an attribute of a Node (N) or an Edge (E).
    - Each Sheet (S) = (T) contains 0..n:
        - Node (N) definitions
        - Edge (E) = (Dn) definitions, which are either:
            - Single-directional (D1) or
            - Bi-directional (D2)
Parse out:
    - For both (N) and (Dn):
        -- A label (L), which is like a record type ID
            -- A label is _NOT_ a Unique record ID.
            -- May have ontological attributes = Fields (F1, .., Fn)
            -- (L)'s for (N) are distinct from (L)'s for (E).
    - Every (N) has a unique ID (NID) = Name, a string
        -- The parser de-duplicates. Chooses only first instance.
    - Every (E) has a From Node (FR) and a To Node (TO)
        -- For (E) in (D1), (FR) and (TO) indicate direction
        -- For (E) in (D2), we assume two (E)'s, one in each direction
        -- (E) = all (FR, TO) pairs
        -- (D2) edges are expanded into two (D1) edges.
    - For (L) in (N) or (Dn), (F1, F2, .., Fn) is a unique set (ONT).
        -- Only one (L) per unique (N) or (E) = (FR, TO) pair.
        -- (L) = (F1, F2, .., Fn) is documented but not enforced
    - Nodes, Edges, Labels, Topics, Fields are organized into 3
        consolidated datasets: NODES, EDGES, FIELDS

Things to do with this nutty data...  :-)

- Generate some graph diagrams.
    - Analyze the graphs.

- Generate some musical scores/phrases (see more notes below).

- Generate outline of some geo-spatial data/maps.
    - Possibly use as inputs into blender.

Regarding the musical part of it...
    - Auto-generate a template for parts, phrases, melodies, harmonies,
        dynamics, tempo, panning based on combinations of qualities
        expressed numerically and algorithmically based on multiple
        contexts, like:
    - For (T) associate a key signture =
        set of notes, specific tonic, specified degrees, permitted modulations
    - For (L) associate a 3-line / 12 bar chord progression
        wtih a given pattern like 12-bar blues [I I I I IV IV I I V IV I V].
        Notes in each bar associated w/ diatonic or 7 chords for scale degrees.
    - Geo-spatial context associates a time signature
    - Action-context associates a tempo
    - Randomly or based on other context, associates dynamic patterns /
        velocity for the 12 bars and for a repetition of them, say 3 times
    - For (N), randomly generate and/or pick from standard sets of:
        - number of parts and what instrument to assign to each part
        - mel, har, rhythm (notes and rests) for each bar's main part
        - mel, har, rhythm, panning patterns for additional parts
    - Generate midi file / score based on above
        - Export to MuseScore, Abelton, GarageBand, etc.
        - Tweak to make it sound better.
        - Store in app /sound directory.
"""

import matplotlib.pyplot as plt         # type: ignore
import networkx as nx                   # type: ignore
import pandas as pd                     # type: ignore
import random

from copy import copy
from dataclasses import dataclass, fields
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
    """
    def __init__(self):
        """Class for managing graph data, generating graphs
        and other graph-related methods.
        """
        pd.options.mode.chained_assignment = None
        self.SHEETS = dict()
        self.NODES = dict()
        self.EDGES = dict()
        self.FIELDS = dict()  # drop this if not needed
        self.MUSIC = dict()
        self.KEYS = dict()
        self.CHORDS = dict()
        self.set_modes()

    @dataclass
    class major_keys:
        """Class for deriving fifths, modes and key signatures."""
        C: tuple = ('C', 'D', 'E', 'F', 'G', 'A', 'B')
        G: tuple = ('G', 'A', 'B', 'C', 'D', 'E', 'F♯')
        D: tuple = ('D', 'E', 'F♯', 'G', 'A', 'B', 'C♯')
        A: tuple = ('A', 'B', 'C♯', 'D', 'E', 'F♯', 'G♯')
        E: tuple = ('E', 'F♯', 'G♯', 'A', 'B', 'C♯', 'D♯')
        B: tuple = ('B', 'C♯', 'D♯', 'E', 'F♯', 'G♯', 'A♯')
        Gf: tuple = ('G♭', 'A♭', 'B♭', 'C♭', 'D♭', 'E♭', 'F')
        Df: tuple = ('D♭', 'E♭', 'F', 'G♭', 'A♭', 'B♭', 'C')
        Af: tuple = ('A♭', 'B♭', 'C', 'D♭', 'E♭', 'F', 'G')
        Ef: tuple = ('E♭', 'F', 'G', 'A♭', 'B♭', 'C', 'D')
        Bf: tuple = ('B♭', 'C', 'D', 'E♭', 'F', 'G', 'A')
        F: tuple = ('F', 'G', 'A', 'B♭', 'C', 'D', 'E')

    @dataclass
    class chord_progressions:
        """Class for deriving chord progressions."""
        sad_happy_0: tuple = (('ii', 'V', 'I'), ('ii', 'V', 'I'),
                              ('ii', 'V', 'I'), ('ii', 'V', 'I'))
        pop_short_0: tuple = (('I', 'V', 'vi', 'IV'),
                              ('I', 'V', 'vi', 'IV'),
                              ('I', 'V', 'vi', 'IV'))
        pop_short_2: tuple = (('I', 'V', 'vi', 'ii'),
                              ('I', 'V', 'vi', 'ii'),
                              ('I', 'V', 'vi', 'ii'))
        pop_short_3: tuple = (('I', 'iii', 'vi', 'IV'),
                              ('I', 'iii', 'vi', 'IV'),
                              ('I', 'iii', 'vi', 'IV'))
        pop_short_4: tuple = (('I', 'iii', 'vi', 'ii'),
                              ('I', 'iii', 'vi', 'ii'),
                              ('I', 'iii', 'vi', 'ii'))
        pop_long_0: tuple = (('I', 'vi', 'IV', 'V'), ('I', 'vi', 'IV', 'V'),
                             ('I', 'vi', 'IV', 'V'))
        pop_long_1: tuple = (('I', 'IV', 'vi', 'V'), ('I', 'IV', 'vi', 'V'),
                             ('I', 'IV', 'vi', 'V'))
        pop_long_2: tuple = (('I', 'vi', 'ii', 'V'), ('I', 'vi', 'ii', 'V'),
                             ('I', 'vi', 'ii', 'V'))
        pop_long_3: tuple = (('I', 'ii', 'vi', 'V'), ('I', 'ii', 'vi', 'V'),
                             ('I', 'ii', 'vi', 'V'))
        minor_0: tuple = (('I', 'IV', 'I', 'IV', 'V'),
                          ('I', 'IV', 'I', 'IV', 'V'), ('vi', 'V', 'IV', 'V'))
        minor_1: tuple = (('I', 'IV', 'I', 'IV'), ('I', 'IV', 'I', 'IV'),
                          ('vi', 'IV', 'vi', 'IV'))
        sad_0: tuple = (('vi', 'IV', 'vi', 'IV', 'ii', 'V', 'IV', 'V'),
                        ('vi', 'IV', 'vi', 'IV', 'ii', 'V', 'IV', 'V'))
        happy_0: tuple = (('I', 'IV', 'I', 'IV', 'ii', 'V', 'vi', 'IV'),
                          ('I', 'IV', 'I', 'IV', 'ii', 'V', 'vi', 'IV'))
        moody_0: tuple = (('I', 'iii', 'IV', 'V'), ('I', 'iii', 'IV', 'V'),
                          ('I', 'iii', 'IV', 'V'))
        moody_1: tuple = (('I', 'iii', 'vi', 'IV'), ('I', 'iii', 'vi', 'IV'),
                          ('I', 'iii', 'vi', 'IV'))
        jazz_0: tuple = (('I', 'ii', 'iii', 'IV', 'V'),
                         ('I', 'ii', 'iii', 'IV', 'V'),
                         ('I', 'ii', 'iii', 'IV', 'V'))
        connect_0: tuple = (('I', 'V', 'vi', 'iii', 'IV', 'I', 'IV', 'V'),
                            ('I', 'V', 'vi', 'iii', 'IV', 'I', 'IV', 'V'))
        blues_0: tuple = (('I', 'I', 'I', 'I'), ('IV', 'IV', 'I', 'I'),
                          ('V', 'IV', 'I', 'V'))
        blues_1: tuple = (('I', 'IV', 'I', 'I'), ('IV', 'IV', 'I', 'I'),
                          ('V', 'IV', 'I', 'V'))
        blues_2: tuple = (('I', 'I', 'I', 'I'), ('IV', 'IV', 'I', 'I'),
                          ('V', 'IV', 'I', 'I'))

    @dataclass
    class time_signatures():
        """Class for deriving time signatures, beats."""
        march: str = "2/4"
        waltz: str = "3/4"
        common: str = "4/4"

    def set_modes(self):
        """Populate key/mode/scales data.
        Generate sets of minor keys.
        Create a list of chord progressions.
        Create a dict of time signatures (beats).
        """
        self.KEYS['fifths'] =\
            tuple(f.name.replace('f', '♭').replace('s', '♯')
                  for f in fields(self.major_keys))
        self.KEYS['modes'] = dict()
        self.KEYS['modes']['major'] =\
            tuple((f.name.replace('f', '♭').replace('s', '♯'), f.default)
                  for f in fields(self.major_keys))
        nstr = "natural minor"
        hstr = "harmonic minor"
        estr = "melodic minor"
        for m in (nstr, hstr, estr):
            self.KEYS['modes'][m] = list()
        for major in self.KEYS['modes']['major']:
            dg = major[1]
            nat = (dg[5], dg[6], dg[0], dg[1], dg[2], dg[3], dg[4])
            har = list(copy(nat))
            har[6] = har[6][:-1] if har[6][-1:] == '♭' else har[6] + '♯'
            mel = list(copy(har))
            mel[5] = mel[5][:-1] if mel[5][-1:] == '♭' else mel[5] + '♯'
            for m in ((nstr, nat), (hstr, har), (estr, mel)):
                self.KEYS['modes'][m[0]].append((dg[5] + "m", tuple(m[1])))
        for m in (nstr, hstr, estr):
            self.KEYS['modes'][m] = tuple(self.KEYS['modes'][m])
        self.ROMAN: dict = {'degrees': {'major': ('I', 'IV', 'V'),
                                        'minor': ('ii', 'iii', 'vi'),
                                        'diminished': ('VII°')},
                            'order':
                                ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'VII°']}
        self.CHORDS = [f.default for f in fields(self.chord_progressions)]
        self.TIMESIGS = {f.name: f.default
                         for f in fields(self.time_signatures)}
        self.BEATS = {1: 'whole', 2: 'half', 4: 'quarter', 8: 'eighth',
                      16: 'sixteenth', 32: 'thirty-second', 64: 'sixty-fourth'}

    def get_sheet_data(self,
                       p_file_path: str,
                       p_sheet_nm: str):
        """Get data from a spreadsheet.

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
                           p_file_nm: str):
        """Load sheet data, driving from the manifest tab.
           Load raw data for all sheets into pandas dataframes.

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
                          cols: list,
                          s_df: DataFrame):
        """For given dataframe, return list of unique values
           for combination of named columns.

        :args:
        - col_nm (list): Column names to select on
        - s_df (DataFrame): Raw sheet data being processed
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
                  p_topic: str,
                  s_df: DataFrame):
        """Fill out Nodes indexes. Reject duplicate node names.

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - s_df (DataFrame): Raw data for the sheet.
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
                  p_topic: str,
                  s_df: DataFrame):
        """Fill out the (E) Edges indexes.

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - s_df (DataFrame): Raw data for the sheet.
        :sets:
        - (class attribute): EDGES
        """
        def add_edges(edges, p_topic):
            if edges is not None:
                for vector in edges:
                    if tuple(vector) not in self.EDGES.keys():
                        self.EDGES[tuple(vector)] = {'T': p_topic}

        edges = self.get_unique_values(['d1_node_from', 'd1_node_to'], s_df)
        if edges is not None:
            add_edges(edges, p_topic)
        edges = self.get_unique_values(['d2_node_from', 'd2_node_to'], s_df)
        if edges is not None:
            add_edges(edges, p_topic)
        edges = self.get_unique_values(['d2_node_to', 'd2_node_from'], s_df)
        if edges is not None:
            add_edges(edges, p_topic)

    def set_labels(self,
                   s_df: DataFrame):
        """Fill out labels for Nodes and Edges.
        Nodes are indexed by unique name (NID).
        Edges are indexed by (node_from, node_to).

        :args:
        - s_df (DataFrame): Raw data for the sheet.
        :sets:
        - (class attribute): NODES, EDGES
        """
        labels = self.get_unique_values(['n_name', 'n_label'], s_df)
        if labels is not None:
            for n_list in labels:
                self.NODES[n_list[0]]['L'] = n_list[1]
        labels = self.get_unique_values(
            ['d1_node_from', 'd1_node_to', 'd1_label'], s_df)
        if labels is not None:
            for v_list in labels:
                self.EDGES[tuple(v_list[:2])]['L'] = v_list[2]
        labels = self.get_unique_values(
            ['d2_node_from', 'd2_node_to', 'd2_label'], s_df)
        if labels is not None:
            for v_list in labels:
                self.EDGES[tuple(v_list[:2])]['L'] = v_list[2]
                self.EDGES[(v_list[1], v_list[0])]['L'] = v_list[2]

    def gather_fields(self,
                      n_or_e: str,
                      p_label: str,
                      p_fields: list):
        """Gather ontology (field list) from given label.

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
                           p_topic: str,
                           node_df: DataFrame):
        """Gather field names for Nodes view of Sheet data.
           Collect field names and field values.

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - node_df (DataFrame): View of dataframe for Nodes.
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
                        self.gather_fields("N", n_lbl, fields)
                        self.NODES[n_nm]["F"] = dict()
                        value_row = node_df.loc[node_df['n_name'] == n_nm]
                        if not value_row.empty:
                            for fld_nm in fields:
                                self.NODES[n_nm]["F"][fld_nm] =\
                                    value_row[fld_nm].values[0]

    def gather_edge_fields(self,
                           p_topic: str,
                           p_d: str,
                           edge_df: DataFrame):
        """Gather field names and values for Edges views of Sheet data.
           Collect field names and field values.

        :args:
        - p_topic (str): Name of the sheet/topic being processed.
        - p_d (str): "d1" or "d2" = edge type
        - edge_df (DataFrame): View of dataframe for Edges.
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
                        self.gather_fields("E", e_lbl, fields)
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
           - Accumulate Fields (F) for each LABEL.

            :args:
            - p_topic (str): Name of sheet
            - s_df (dataframe): Raw sheet dataframe.
            :sets:
            - (class attribute): FIELDS

        """
        self.gather_node_fields(p_topic,
                                s_df.iloc[:, s_df.columns.get_loc('N') + 1:
                                          s_df.columns.get_loc('D2')])
        self.gather_edge_fields(p_topic, 'd1',
                                s_df.iloc[:, s_df.columns.get_loc('D1') + 1:])
        self.gather_edge_fields(p_topic, 'd2',
                                s_df.iloc[:, s_df.columns.get_loc('D2') + 1:
                                          s_df.columns.get_loc('D1')])

    def set_graph_data(self,
                       p_file_nm: str):
        """Organize data so that networkx can use it.
        Then create a digaram using matplotlib.

        :args:
        - p_file_nm (str): Name of the file being processed.

        :writes:
        - (file): image file of graph diagram

        @DEV:
        - Zillions of options here!
        - The networkx Gallery is good place to start, explore:
          https://networkx.org/documentation/stable/auto_examples/index.html
        - plt.show() works fine for testing, but won't be good for final
          version, where I need to be able to integrate displays into the
          game/editor framework.
        - Looking at it longer-term, it will be worthwhile working on
          a variety of options for both graph diagrams and graph data
          analysis. For example, examining the degrees report shows right
          away what elements of the data landscape are most "connected" and
          which ones are most "disconnected" (and could use more definition).
        - Lots of fun exploring how to use networkx and matplotlib to do the
          diagrams. Won't hurt to go thru the nx gallery and references more
          carefully and perhaps go through some matplotlib tutorials too.
        - See workshops and notebooks on data visualization. bokeh, seaborn,
          graphviz, etc.  I am also intrigued about generating 3D data that
          could be rendered using blender maybe?
        """
        p_img_title = p_file_nm.split(".")[0].replace(" ", "_") + ".png"
        plt.title(p_img_title)
        G = nx.MultiDiGraph()
        G.add_nodes_from(list(self.NODES.keys()))
        G.add_edges_from(list(self.EDGES.keys()))
        pos = nx.spring_layout(G, seed=13648)
        # pos = nx.kamada_kawai_layout(G)
        N = G.number_of_nodes()
        M = G.number_of_edges()
        print(f"Nodes: {N} Edges: {M}")
        print("Degrees:")
        pp((sorted([(dg[1], dg[0]) for dg in nx.degree(G)], reverse=True)))
        # Modify node sizes based on degree and type.
        # Modify node color based on topic, type, etc.
        # Look at the reference. Can set qualities on a subset of items.
        # Can also generate sub-graphs, graphs with only selected nodes.
        node_sizes = [3 + 10 * i for i in range(N)]
        # Likewise, set edge color based on label.
        edge_colors = range(2, M + 2)
        # edge_alphas = [(5 + i) / (M + 4) for i in range(M)]
        cmap = plt.cm.plasma
        nx.draw_networkx_nodes(G, pos,
                               linewidths=1,
                               edgecolors='blue',
                               node_color='white',
                               node_size=node_sizes)
        nx.draw_networkx_edges(G, pos,
                               node_size=node_sizes,
                               edge_color=edge_colors,
                               edge_cmap=cmap,
                               width=2)
        nx.draw_networkx_labels(G, pos,
                                font_size=9,
                                # font_weight='bold',
                                font_color='indigo',
                                verticalalignment="top")
        e_labels = {k: v["L"] for k, v in self.EDGES.items()}
        nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels=e_labels,
                                     font_size=6)
        # for i in range(M):
        #     attrs = {list(self.EDGES.keys())[i]: {"alpha": edge_alphas[i]}}
        # nx.set_edge_attributes(G, attrs)
        ax = plt.gca()
        ax.set_axis_off()

        # plt.show()

        plt.figure(figsize=(30.0, 30.0))      # w, h in inches
        # options = {'font_size': 8,
        #           'node_size': 500,
        #           'node_color': 'blue',
        #           'edgecolors': 'black',
        #           'linewidths': 2}
        # nx.draw_networkx(G, pos=nx.spring_layout(G), **options)
        # nx.draw_networkx(G, with_labels=True, font_weight='normal')
        # ax = plt.gca()
        ax.margins(0.20)
        # plt.axis("off")
        # plt.show()
        save_path = path.join(RI.get_app_path(),
                              RI.get_config_value('save_path'),
                              p_img_title)

        # Hmmm... something goes wrong when I write to file
        # Was displaing nicely using plt.show()

        # Also want to consider saving the graph data so
        # it doesn't have to be recreated each time.

        plt.savefig(save_path)
        print(f"Graph diagram saved to: {save_path}")

    def set_scales_for_topics(self):
        """Assign a key/mode/scale to each Topic.
           Will work out permitted, suggested modulations later.
        :sets:
        - (class attribute): self.MUSIC['key_scales']
        """
        self.MUSIC['scales'] = dict()
        for topic in set([data['T'] for _, data in self.NODES.items()]):
            modes = list(self.KEYS["modes"].keys())
            mode = modes[random.randint(0, len(modes) - 1)]
            knum = random.randint(0, 11)
            key = self.KEYS["modes"][mode][knum][0]
            scale = self.KEYS["modes"][mode][knum][1]
            self.MUSIC['scales'][topic] = {(key, mode): scale}

    def set_chords_for_labels(self):
        """Assign chord progression pattern to each Label.
           Break out the sequences into one set of bars.
           Will work out notes, specific chords, durations later,
           specific to each node.

        :sets:
        - (class attribute): self.MUSIC['chords']
        """
        self.MUSIC['chords'] = dict()
        nlabels = set([data['L'] for _, data in self.NODES.items()])
        elabels = set([data['L'] for _, data in self.EDGES.items()])
        for label in nlabels.union(elabels):
            chord = self.CHORDS[random.randint(0, len(self.CHORDS) - 1)]
            bars = []
            for phrase in chord:
                bars.extend(list(phrase))
            self.MUSIC['chords'][label] = {'phrases': len(chord),
                                           'bars_in_phrase': len(chord[0]),
                                           'bars': bars}

    def set_beat_and_tempo(self, nid: str):
        """A context is defined by set of node values whose labels
        are in the same set, like ["region", "province", "town"].
        Any node on the path of one of those nodes would get that
        node's time signature. If the node in not in such a path,
        then assign a default.

        Select time signature based on such context for each node.

        Pick a time signature: 4/4, 3/4, 6/8, 2/4, .. for nodes whose
        label is in: ["region", "province", "town"] (or ...).
        Would be nice to assign for all nodes in a sub-graph of a
        given "geographical" label too.
        But let's don't go down that rabbit-hole right now. ;-)
        Just assign time signature randomly.

        Assign beats per chords for the label.

        For other labels (that is, eventually, for nodes not in an
        identified sub-graph), just pick a time signature randomly.

        Thinking to tie tempo to Event associated with Node in the
        game timeline.

        Events are part of saskan ontology (or will be) but are not
        defined in the "places_data" file.  Each main sub-class of data
        (see original ER diagram) can be expressed as graph data.
        Game setup can include generating musical framework for all
        graphed data.  For now, just simulate music parts where graphed
        data not defined.

        Tempo: slow, medium, fast, etc., use Italian if you like, but
        really expressed as BPM in the notation, then translated to
        appropriate MIDI instructions either by me or offline apps
        (MuseScore, etc.). Default if no Event detected.

        Simulate this for now.
        Just pick a random integer between 60 and 180.
        :sets:
        - (class attribute): self.MUSIC[<Node ID>]['rhythm']['beat']
        - (class attribute): self.MUSIC[<Node ID>]['rhythm']['tempo']

        For first prototype, all time signature are in 4. (2/4, 3/4, 4/4)
        But let's try to code in a flexible way.
        Possible denominators and their meaning / what gets the beat:
        1 - whole note
        2 - half note
        4 - quarter note
        8 - eighth note
        16 - sixteenth note
        32 - thirty-second note
        64 - sixty-fourth note
        """
        tsig = list(self.TIMESIGS.values())[random.randint(
            0, len(self.TIMESIGS.values()) - 1)]
        beat = tsig.split('/')
        tempo = random.randint(60, 180)
        self.MUSIC['scores'][nid]['rhythm']['time'] = tsig
        self.MUSIC['scores'][nid]['rhythm']['measure'] = int(beat[0])
        self.MUSIC['scores'][nid]['rhythm']['beat'] = int(beat[1])
        self.MUSIC['scores'][nid]['rhythm']['tempo'] = int(tempo)
        self.MUSIC['scores'][nid]['rhythm']['description'] =\
            (f"{beat[0]} beats per measure" +
             f"\n{self.BEATS[int(beat[1])]} note gets the beat" +
             f"\n{tempo} beat/minute = " +
             f"{round((tempo / 60), 2)} beat/second")

    def get_scale(self, p_mode, p_key):
        for m in self.KEYS["modes"][p_mode]:
            if m[0] == p_key:
                return(m[1])

    def set_relative_key(self, nid: str):
        """Set relative key for a score.

        If it is a major key, then relative minor is the 6th degree.
        Randomly choose one of the 3 minor keys to use;
        don't assume it has to be the natural minor.

        If it is a minor key, then relative major is the 3rd degree.

        Not sure yet how to determine best key signature for
        non-major, non-natural-minor keys. I guess it would always
        be the relative major key. Sometimes that is pretty close,
        sometimes it would require more accidentals.
        """
        music = self.MUSIC['scores'][nid]
        mode = list(music['key_scales']['scale'].keys())[0]
        if "major" in mode:
            minors =\
                [ky for ky in self.KEYS['modes'].keys() if "minor" in ky]
            rel_mode = random.choice(minors)
            rel_ky = music['key_scales']['scale'][mode][5] + "m"
            keysig = mode[0]
        else:
            rel_mode = "major"
            rel_ky = music['key_scales']['scale'][mode][2]
            if "F♯" in mode:
                rel_ky = "G♭"
            if "natural minor" in mode:
                keysig = rel_ky
            else:
                keysig = "C"
        self.MUSIC['scores'][nid]['key_scales']['signature'] = keysig
        self.MUSIC['scores'][nid]['key_scales']['relative'] =\
            {(rel_ky, rel_mode): self.get_scale(rel_mode, rel_ky)}

    def set_neighbor_keys(self, nid: str):
        """Set keys that are a Fifth from main key for score.
        For selected mode, pick next key and previous key.
        """
        music = self.MUSIC['scores'][nid]
        scale = list(music['key_scales']['scale'].keys())[0]
        mode = self.KEYS['modes'][scale[1]]
        mix = mode.index((scale[0], (music['key_scales']['scale'][scale])))
        n1 = mix + 1 if mix < len(mode) - 1 else 0
        n2 = mix - 1 if mix > 0 else len(mode) - 1
        n1_ky = mode[n1][0]
        n2_ky = mode[n2][0]
        n1_scale = mode[n1][1]
        n2_scale = mode[n2][1]
        self.MUSIC['scores'][nid]['key_scales']['mod_right'] =\
            {(n1_ky, scale[1]): n1_scale}
        self.MUSIC['scores'][nid]['key_scales']['mod_left'] =\
            {(n2_ky, scale[1]): n2_scale}

    def set_pattern(self, nid: str):
        """
        Mix it up randomly but include patterns like:
        - Ordered patterns (asecnding, descending) for first 8 bars
        - Surprise pattern (bigger steps) for last 4 bars
        - Start/End with tonic or relative minor/relative major tonic

        To start out with, we'll define the patterns like this:
        - asc: go up in thirds or fifths or dominant 7ths
        - desc: go down in thirds or fifths or dominant 7ths
        - steady: go up or down or same in seconds or thirds
        - tonic: use notes in tonic chord of main or relative key
                 in a steady pattern. If the degree is not I,
                 then at least end with a tonic or relative tonic note.
        """
        def least_used_pat(pat_cnt):
            """Return pattern least used so far."""
            max = bar_keysnt
            for p, c in pat_cnt.items():
                if c < max:
                    max = c
                    least_used = p
            return least_used

        music = self.MUSIC['scores'][nid]
        bar_keysnt = len(music['chords']['bars'])
        pat_cnt = {"asc": 0, "desc": 0, "steady": 0, "tonic": 0}
        pat_list = []
        for bar_n in range(0, bar_keysnt):
            if bar_n == 0 or bar_n == (bar_keysnt - 1):
                pat = "tonic"
            elif bar_n < int(bar_keysnt * .67):
                pat = random.choice(list(pat_cnt.keys()))
            else:
                pat = least_used_pat(pat_cnt)
            pat_list.append(pat)
            pat_cnt[pat] += 1
        self.MUSIC['scores'][nid]['chords']['pattern'] = pat_list

    def set_beat_chord(self,
                       m: int,
                       n: int,
                       chords: dict,
                       rhythm: dict,
                       bar_keys: dict,
                       pattern: list,
                       tonic_root: str):
        """Set chord for each beat within a measure.

        Decide which chord to play on the beat:
            from main, relative, or a neighboring scale
        """
        cord = "?"
        rp = random.randint(0, 100)
        if rp < 60 or (pattern == "tonic" and n == 1) or\
            ((m + 1) == len(chords['bars']) and
                n == rhythm['measure']):
            cord = [tonic_root]
        elif rp < 80:
            cord = [bar_keys['relative']]
        elif rp < 90:
            cord = [bar_keys['mod_left']]
        else:
            cord = [bar_keys['mod_right']]
        return cord

    def set_beat_rhythm(self,
                        rhythm: dict,):
        """Set rhythm, in the sense of how many notes to
        play, of what duration, for a given beat.
        Not yet assigning specific pitches or rests.

        This is a Monte Carlo shuffle with filters and retries.

        Result will be like...
        - One beat, or
        - Two beats of equal duration, or
        - Tuple -- 3, 5 or 7 beats of equal duration, or
        - Some combination of beats not of equal duration, but
          which "add up" to one complete beat.

        Document the rhythm pattern with a list of integer / character
        tuples. For a 4/4 time signature, we might see:
          - [(4, 'q')]
          - [(8, 'e'), (8, 'e')]
          - [(8., 'e.'), (16, 's')]
          - [(16, 's'), (16, 's'), (16, 's'), (16, 's')]
        - Indicate musical tuples (like triplets) with a 't'
          and a notation showing the beat note over the tuple count:
          - [(4/3, 't')]
        - For dotted notes put a dot after both the note and the char:
          - [(8., 'e.'), (16, 's')]
          - It's possible to come up with a total less than a full beat,
            but that will be very rare due the backtracking and retries.

        Eventually will reduce the verbosity of the info returned but
        helpful for debugging.
        """
        def assign_tuple(
                rhythm_beat: int,
                beat_notes: list):
            """Assign a musical tuple as a division of the natural beat.
               This can only be done once within the beat."""
            beat_notes.append(
                (f"{rhythm_beat}/{random.choice([3, 5, 7])}", 't'))
            return 1.0, beat_notes

        def assign_beat_note(total_beat: float,
                             beat_keys: list):
            """If at start of looping, bend in favor of longer notes.
            If nearer to end of looping, bend in favor or shorter notes.
            """
            if total_beat > 0.8:
                beat = random.choice(beat_keys[len(beat_keys) - 3:])
            else:
                if random.randint(0, 100) > 32:
                    beat = random.choice(beat_keys[:2])
                else:
                    beat = random.choice(beat_keys)
            return beat

        def assign_dot(duration):
            """Assign dotted notes sparingly."""
            dot = True if random.randint(0, 100) < 23 else False
            if dot:
                duration += (duration * 0.5)
            return (dot, duration)

        # ===== set_beat_rhythm() main =========
        beats = {i: (n, rhythm['beat'] / i) for i, n in
                 {1: 'w', 2: 'h', 4: 'q', 8: 'e',
                  16: 's', 32: 'y', 64: 'z'}.items()
                 if i >= rhythm['beat']}
        try_again = True
        tries = 0
        while try_again is True:
            total_beat = 0.0
            break_me = 0
            beat_notes = list()
            while total_beat < 1.0:
                if total_beat == 0.0 and random.randint(0, 100) < 12:
                    total_beat, beat_notes =\
                        assign_tuple(rhythm['beat'], beat_notes)
                else:
                    beat = assign_beat_note(total_beat, list(beats.keys()))
                    dot, duration = assign_dot(beats[beat][1])
                    if total_beat + duration <= 1.0:
                        total_beat += duration
                        if dot:
                            beat_notes.append(
                                (f"{beat}.", beats[beat][0] + '.'))
                        else:
                            beat_notes.append((str(beat), beats[beat][0]))
                break_me += 1
                if break_me > 100:
                    break
            if total_beat == 1.0 or tries > 9:
                try_again = False
        if total_beat != 1.0:
            print("Warning: set_beat_rhythm() failed to assign a full beat." +
                  f"\nBeats: {beat_notes} = {total_beat}")
        return beat_notes

    def set_pitch_range(self,
                        chord: str):
        """Set range of pitches to use within the beat.
        """

        def assign_octave_range():
            """Assign octave range for a given pitch.
            Choose range of pitches relating to octaves:
            - Closed, stay within tonic4 to tonic5, more or less
            - Open, range within tonic3 to tonic6, more or less.
            """
            min_o = 4
            max_o = 5
            if random.randint(0, 100) < 33:
                min_o -= 1
            if random.randint(0, 100) < 33:
                max_o += 1
            if random.randint(0, 100) < 16:
                min_o -= 1
            if random.randint(0, 100) < 16:
                max_o += 1
            return (min_o, max_o)

        def assign_pitches(min_o: int,
                           max_o: int,
                           chord: str):
            """Identify pitches for chord and octaves being processed.
            - Tonic, 2nd, 3rd, 4th, 5th, 6th, 7th, Octave
            - Which we get from self.KEYS['modes']:
              - If chord is not in 'major' mode, then add an 'm' to chord
                and look randomly in one of the 3 minor modes.
            - Based on range, expand the notes available for the chord,
              notating what octave each note is in.
            We are not yet associating a pitch with a beat, just
            assembling what range of pitches to work with in the beat."""
            chord = "G♭" if chord == "F♯" else chord
            beat_scale = list()
            pitches = list()
            modes: dict = self.KEYS['modes']
            if chord in [scale[0] for scale in modes['major']]:
                beat_scale = [scale[1] for scale in modes['major']
                              if scale[0] == chord]
            else:
                for minor in [m for m in list(modes.keys()) if m != 'major']:
                    if (chord + 'm') in [scale[0] for scale in modes[minor]]:
                        beat_scale = [scale[1] for scale in modes[minor]
                                      if scale[0] == (chord + 'm')]
                        break
            for o in range(min_o, max_o + 1):
                for p in beat_scale:
                    scale = list()
                    for n in p:
                        scale.append(f"{n}{o}")
                    pitches.append(tuple(scale))
            return pitches

        # =============== set_pitch_range() main =========
        min_o, max_o = assign_octave_range()
        pitches = assign_pitches(min_o, max_o, chord)
        return pitches

    def set_notes(self,
                  m: int,
                  chords: dict,
                  rhythm: dict,
                  bar_keys: dict,
                  pattern: list,
                  tonic_root: str):
        """Set notes for each beat within a measure.
        # 3. Choose scale range relating to octaves
        # 3.a. Closed, stay within C4 to C5 (more or less)
        # 3.b. Open, range within C3 to C6 (more or less)
        #
        # 4. Get the pitches for the chord: the 3rd, 5th, 7th
        #    and get the 2nd, 4th and 6th too, for arpeggios.
        #
        # 5. Choose whether to:
        # 5.a. Use a 7th or not
        # 5.b. Use regular or inversion
        # 5.c. If inversion, first, second, or third (if 7th)
        #
        # 6. Run algorithms relating to the patterns
        #    ascending, descending, steady. Assign specific
        #    pitches from the selected set to the rhythm,
        #    using rules for the pattern.
        # 6.a. If ascending, step up thru the chord either
        #    melodically (single notes) or harmonically
        #    (repeating the chord or variations of it).
        #    Do not use pitches lower than previous note.
        # 6.b. If descending, step down thru the chord
        #    Use notes lower than previous notes in the beat.
        # 6.c. If steady, step up and down by 2nds or 3rd only;
        #    or repeat notes at same pitch. tonic = steady
        #
        # 7. Choose whether to have more than one voice.
        #   If so, choose the number of voices and quality
        #   of each:
        # 7.a.  Simple harmonics.
        # 7.b.  Counterpoint.
        # 7.c.  Melodic echo.
        # (Skip this in initial prototypes,
        #  then assume it is LH/bass clef for piano.
        #  Later, add instrumentation, including
        #  percussion.)
        #
        # 8. Later -- also define dynamics.
        #
        # 9. See if I can smooth out any rough edges.

        For writing notes, use a lilypond-like syntax for now.
        Modify this to match what the python music_21 or MMA lib uses.

        - lower-case note-name without a number (e.g. c, d, e, f, g, a, b)
          means a single note of duration =
          the beat note (usually = quarter-note)
        - I will represent sharps and flat using unicode chracters:
            f♯, g♭
        - note-name with a number (e.g. c4, d4, e4, f4, g4, a4, b4)
          means a single note of specified duration.
        - a number with a dot after it means a dotted note of specific duration
        - bars are represented by vertical bars (|)
        - chords/polyphony are represented by angle brackets (< >)
            - duration is coded after the closing bracket (<c e g>4)
            - first note in a chord is relative to first note in previous chord
        - default octave is middle C (C4) for treble, bass C (C3) for bass
        - relative octave changes --> commas (,) and apostrophes (')
        - rests are represented by the letter r (r, r4, r8, r16, r32)

        @DEV / DEBUG
        In some cases, notes is coming back emmpty = {}.
        Not sure why. Suspect something with the measures index/count in
        set_bars()?
        May want to review that later rather than stopping here.
        I am not seeing any cases where this method returns an empty dict.
        """
        notes = {}
        for n in range(1, rhythm['measure'] + 1):
            notes[n] = self.set_beat_chord(m, n, chords, rhythm, bar_keys,
                                           pattern, tonic_root)
            notes[n].append(self.set_beat_rhythm(rhythm))
            notes[n].append(self.set_pitch_range(notes[n][0]))

        # pp(("notes", notes))
        # if notes == {}:
        #     print("notes is empty!!")

        return notes

    def set_bars(self,
                 m: int,
                 chords: dict,
                 key_scales: dict,
                 tonic_root: str,
                 rhythm: dict):
        """Bar = measure = collection of notes in a score, where
        the nunber of beats in a meaure and what kind of note
        gets the beat is defined by the time signature.
        """
        bars = {}
        for b in range(1, chords['bars_in_phrase'] + 1):
            bar_keys = {}
            try:
                d = self.ROMAN['order'].index(chords['bars'][m - 1])
            except IndexError:
                pp(("index out of range",
                    "m: ", m,
                    "len(chords['bars'])", len(chords['bars']),
                    "self.ROMAN['order']", self.ROMAN['order']))
                pp(("chords['bars'][m - 1]", chords['bars'][m - 1]))
            for k in list(key_scales.keys()):
                sk = list(key_scales[k].keys())[0]
                bar_keys[k] = key_scales[k][sk][d]
            pattern = chords['pattern'][m - 1]
            bars[(b, m)] =\
                {"pattern": pattern,
                 "degree": chords['bars'][m - 1],
                 "keys": bar_keys,
                 "chords": self.set_notes(m, chords, rhythm, bar_keys,
                                          pattern, tonic_root)}
            m += 1
        return (bars, m)

    def set_phrases(self,
                    chords: dict,
                    key_scales: dict,
                    tonic_root: str,
                    rhythm: dict):
        """Phrases are collections of measures played in succession.
        """
        phrases = {}
        m = 0
        for p in range(1, chords['phrases'] + 1):
            (bars, m) = self.set_bars(m, chords, key_scales,
                                      tonic_root, rhythm)
            phrases[p] = bars
        return phrases

    def set_chords_and_notes(self, nid: str):
        """Associate each degree of chord progression with notes.
        """
        key_scales = {m: s for m, s in
                      self.MUSIC['scores'][nid]['key_scales'].items()
                      if m != 'signature'}
        tonic_key = list(key_scales["scale"].keys())[0]

        self.MUSIC['scores'][nid]['notes'] = dict()
        for v in range(1, random.randint(1, 2)):
            clef = "treble" if v == 1 else\
                random.choice(["bass", "treble"])
            self.MUSIC['scores'][nid]['notes'][clef] = self.set_phrases(
                chords=self.MUSIC['scores'][nid]['chords'],
                key_scales=key_scales,
                tonic_root=key_scales["scale"][tonic_key][0],
                rhythm=self.MUSIC['scores'][nid]['rhythm'])

    def set_keys_patterns_chords(self, nid: str):
        """Assign notes to each bar according to the time signature.

        Assign notes, within the selected chord, to each bar, using
        the guard-rails defined by the patterns, and with durations
        appropriate to the time signature.

        For now, just create one part with one voice.
        """
        self.set_relative_key(nid)
        self.set_neighbor_keys(nid)
        self.set_pattern(nid)
        self.set_chords_and_notes(nid)

    def set_music_data(self):
        """Generate music data from the graph data.
        Try to set it up to be flexible, based on parsing
        the graph data, not hard-coding associations.

        Probably will want to move this to another class.
        """
        self.set_scales_for_topics()
        self.set_chords_for_labels()
        self.MUSIC['scores'] = dict()
        for nid, ndat in self.NODES.items():
            self.MUSIC['scores'][nid] = dict()
            for m in ('chords', 'key_scales', 'notes', 'rhythm'):
                self.MUSIC['scores'][nid][m] = dict()
            self.MUSIC['scores'][nid]['key_scales']['scale'] =\
                self.MUSIC['scales'][ndat['T']]
            self.MUSIC['scores'][nid]['chords'] =\
                self.MUSIC['chords'][ndat['L']]
            self.set_beat_and_tempo(nid)
            self.set_keys_patterns_chords(nid)

        # pp((self.MUSIC['scores']))

    def set_affinity_data(self,
                          p_file_nm: str):
        """Load all data from the data workbook.
           - Read its manifest tab to initialize TOPICS (T)
           - Load the raw data into SHEETS (S) dataframes.
           - Parse each (S):
             -- Fill out Nodes (N) dict
             -- Fill out Edges (E) dict
             -- Fill out Fields (F) dict
           - Generate graph data and draw a diagram.

        Args:
            p_file_nm (str): Name of spreadsheet in /config.
        """
        self.get_raw_dataframes(p_file_nm)
        for topic, s_df in self.SHEETS.items():
            self.set_nodes(topic, s_df)
            self.set_edges(topic, s_df)
            self.set_labels(s_df)
            self.set_fields(topic, s_df)
        # self.set_graph_data(p_file_nm)

        # Set up framework for music data,
        # assigning keys to topics,
        # progressions to labels, etc.
        self.set_music_data()
        # Then generate a specific score for specific nodes.
        # (Maybe edges too, but let's start with nodes.)
