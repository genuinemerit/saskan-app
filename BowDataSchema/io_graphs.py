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
        roman: tuple = ('', 'I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii')
        sad_happy_0: tuple = (4, ('ii', 'V', 'I'))
        pop_short_0: tuple = (3, ('I', 'V', 'vi', 'IV'))
        pop_short_2: tuple = (3, ('I', 'V', 'vi', 'ii'))
        pop_short_3: tuple = (3, ('I', 'iii', 'vi', 'IV'))
        pop_short_4: tuple = (3, ('I', 'iii', 'vi', 'ii'))
        pop_long_0: tuple = (3, ('I', 'vi', 'IV', 'V'))
        pop_long_1: tuple = (3, ('I', 'IV', 'vi', 'V'))
        pop_long_2: tuple = (3, ('I', 'vi', 'ii', 'V'))
        pop_long_3: tuple = (3, ('I', 'ii', 'vi', 'V'))
        surprise_minor_0: tuple = (2, ('I', 'IV', 'I', 'IV', 'V'),
                                   1, ('vi', 'V', 'IV', 'V'))
        surprise_minor_1: tuple = (2, ('I', 'IV', 'I', 'IV'),
                                   1, ('vi', 'IV', 'vi', 'IV'))
        sad_ballad_0: tuple = (2, ('vi', 'IV', 'vi', 'IV',
                                   'ii', 'V', 'IV', 'V'))
        happy_chorus_0: tuple = (2, ('I', 'IV', 'I', 'IV',
                                     'ii', 'V', 'vi', 'IV'))
        moody_0: tuple = (3, ('I', 'iii', 'IV', 'V'))
        moody_1: tuple = (3, ('I', 'iii', 'VI', 'IV'))
        jazz_pop_0: tuple = (3, ('I', 'ii', 'iii', 'IV', 'V'))
        connect_0: tuple = (2, ('I', 'V', 'vi', 'iii',
                                'IV', 'I', 'IV', 'V'))
        blues_0: tuple = (1, ('I', 'I', 'I', 'I'),
                          1, ('IV', 'IV', 'I', 'I'),
                          1, ('V', 'IV', 'I', 'V'))
        blues_1: tuple = (1, ('I', 'IV', 'I', 'I'),
                          1, ('IV', 'IV', 'I', 'I'),
                          1, ('V', 'IV', 'I', 'V'))
        blues_2: tuple = (1, ('I', 'I', 'I', 'I'),
                          1, ('IV', 'IV', 'I', 'I'),
                          1, ('V', 'IV', 'I', 'I'))

    @dataclass
    class time_signatures():
        """Class for deriving time signatures."""
        cut: str = "2/2"
        march: str = "2/4"
        waltz: str = "3/4"
        common: str = "4/4"
        rolling: str = "6/8"

    def set_modes(self):
        """Populate key/mode data.
        Generate sets of minor keys.
        Create a dictionary of chord progressions.
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
        self.CHORDS = {f.name: f.default
                       for f in fields(self.chord_progressions)}
        self.BEATS = {f.name: f.default
                      for f in fields(self.time_signatures)}

    def set_chords(self):
        """Populate chords data. Generate sets of lead sheets.
        """
        pass

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

    def set_keys_for_topics(self):
        """Assign a key/mode/scale to each Topic.
           Will work out permitted, suggested modulations later.

           @DEV:
            - Derieve score key signature from the scale.

        :sets:
        - (class attribute): self.MUSIC['keys']
        """
        self.MUSIC['keys'] = dict()
        for topic in set([data['T'] for _, data in self.NODES.items()]):
            modes = list(self.KEYS["modes"].keys())
            mode = modes[random.randint(0, len(modes) - 1)]
            knum = random.randint(0, 11)
            key = self.KEYS["modes"][mode][knum][0]
            scale = self.KEYS["modes"][mode][knum][1]
            self.MUSIC['keys'][topic] =\
                {'mode': mode, 'key': key, 'scale': scale}

    def set_chords_for_labels(self):
        """Assign mood/chord progression pattern to each Label.
           Will work out notes, specific chords, durations later,
           specific to each node.

        :sets:
        - (class attribute): self.MUSIC['chords']
        """
        self.MUSIC['chords'] = dict()
        nlabels = set([data['L'] for _, data in self.NODES.items()])
        elabels = set([data['L'] for _, data in self.EDGES.items()])
        for label in nlabels.union(elabels):
            chords = list(self.CHORDS.keys())
            chord_nm = chords[random.randint(0, len(chords) - 1)]
            chord = self.CHORDS[chord_nm]
            self.MUSIC['chords'][label] = {'mood': chord_nm, 'chords': chord}

    def init_scores_for_nodes(self):
        """Initialize data for generating scores for each node
           based on the Topic and Label of each Node.
           Details are handled in subsequent functions.

        :sets:
        - (class attribute): self.MUSIC['scores']
        """
        self.MUSIC['scores'] = dict()
        for nid, ndata in self.NODES.items():
            self.MUSIC['scores'][nid] =\
                {'mode': self.MUSIC['keys'][ndata['T']]['mode'],
                 'key': self.MUSIC['keys'][ndata['T']]['key'],
                 'scale': self.MUSIC['keys'][ndata['T']]['scale'],
                 'chords': self.MUSIC['chords'][ndata['L']]['chords'],
                 'notes': []}

    def set_time_signatures(self):
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

        Assign beats per chords for the label.

        For other labels (that is, eventually, for nodes not in an
        identified sub-graph), just pick a time signature randomly.

        :sets:
        - (class attribute): self.MUSIC[<Node ID>]['time_signatures']
        """
        for nid, ndata in self.NODES.items():
            if ndata['F'] in [{'n_geo_pol_ty': 'province'},
                              {'n_geo_pol_ty': 'region'},
                              {'n_geo_pol_ty': 'town'}]:
                self.MUSIC['scores'][nid]['time_sig'] = self.BEATS['common']
            else:
                beat = list(self.BEATS.keys())[random.randint(
                    0, len(self.BEATS.keys()) - 1)]
                self.MUSIC['scores'][nid]['time_sig'] = self.BEATS[beat]

    def set_number_of_bars(self):
        """Set the number of bars for each node.
           Example of chords:
            (2, ('I', 'IV', 'I', 'IV'), 1, ('vi', 'IV', 'vi', 'IV'))
            (3, ('I', 'ii', 'vi', 'V'))
           Number of bars = sum of (each chord item's length X multiplier)

        :set:
        - (class attribute): self.MUSIC['scores'][<Node ID>]['bars']
        """
        for nid, music in self.MUSIC['scores'].items():
            bars = 0
            for ix, cdata in enumerate(music["chords"]):
                if ix % 2 == 0:
                    mult = cdata
                else:
                    bars += mult * len(cdata)
            self.MUSIC['scores'][nid]['bars'] = bars

    def set_relative_key(self):
        """Set relative key for each node/score.

        If it is a major key, then relative minor is the 6th degree.
        Randomly choose one of the 3 minor keys to use (don't assume
        it has to be the natural minor.)

        If it is a minor key, then relative major is the 3rd degree.
        """
        def get_scale(p_mode, p_key):
            for m in p_mode:
                if m[0] == p_key:
                    return(m[1])

        for nid, music in self.MUSIC['scores'].items():
            if music['mode'] == 'major':
                mode =\
                    random.choice(['harmonic', 'melodic', 'natural']) +\
                    " minor"
                key = music['scale'][5] + "m"
            else:
                mode = "major"
                key = music['scale'][2]
                if key == "F♯":
                    key = "G♭"
            self.MUSIC['scores'][nid]['key_relative'] =\
                (mode, key, get_scale(self.KEYS["modes"][mode], key))

    def set_neighbor_keys(self):
        """Set keys that are a Fifth from key for each node/score.
        For the selected mode, pick the next key and the previous key.
        """
        for nid, music in self.MUSIC['scores'].items():
            mode = self.KEYS['modes'][music['mode']]
            mode_ix = mode.index((music['key'], (music['scale'])))
            n1 = mode_ix + 1 if mode_ix < len(mode) - 1 else 0
            n2 = mode_ix - 1 if mode_ix > 0 else len(mode) - 1
            self.MUSIC['scores'][nid]['key_neighbors'] =\
                (mode[n1], mode[n2])
            # clean up / consolidate the key data
            self.MUSIC['scores'][nid]['key'] =\
                (music['mode'], music['key'], music['scale'])
            del(self.MUSIC['scores'][nid]['scale'])
            del(self.MUSIC['scores'][nid]['mode'])

    def set_melodic_patterns(self):
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
        """
        for nid, music in self.MUSIC['scores'].items():
            count_types = ["asc", "desc", "steady"]
            cnt = dict()
            pattern = []
            for ct in count_types:
                cnt[ct] = 0
            for bar in range(1, music['bars'] + 1):
                if bar == 1:
                    pattern.append("tonic")
                elif bar < int(music['bars'] * .67):
                    pat = random.choice(count_types)
                    pattern.append(pat)
                    cnt[pat] += 1
                elif bar < music['bars']:
                    surprise_cnt = music['bars']
                    for cp, ct in cnt.items():
                        if ct < surprise_cnt:
                            surprise_cnt = ct
                            pat = cp
                    pattern.append(pat)
                    cnt[pat] += 1
                else:
                    pattern.append("tonic")
            self.MUSIC['scores'][nid]['bars'] = (music['bars'], tuple(pattern))

    def set_chords_for_bars(self):
        """
        """
        pass

    def set_notes_for_bars(self):
        """
        """
        pass

    def set_notes_for_nodes(self):
        """Assign notes to each bar according to the time signature.

        Associate each degree of the chord progression with major, minor,
        or diminished chord based on the key and its nearest neighbors
        (modulation candidates). Pick diatonic tritone, inverted-1st,
        inverted-2nd, 7th, harmonic or melodic.

        Assign notes, within the selected chord, to each bar, using
        the guard-rails defined by the patterns, and with durations
        appropriate to the time signature.
        """
        self.set_number_of_bars()
        self.set_relative_key()
        self.set_neighbor_keys()
        self.set_melodic_patterns()
        # @DEV -- pick up here...
        self.set_chords_for_bars()
        self.set_notes_for_bars()

    def set_tempo_for_scores(self):
        """Thinking to tie tempo to Event associated with Node in the
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
        """
        pass

    def set_music_data(self):
        """Generate music data from the graph data.
        Try to set it up to be flexible, based on parsing
        the graph data, not hard-coding associations.

        May want to move this to another class.

        @DEV:
        Also consider algorithms to define dynamics.
        """
        self.set_keys_for_topics()
        self.set_chords_for_labels()
        self.init_scores_for_nodes()
        self.set_time_signatures()
        self.set_notes_for_nodes()
        self.set_tempo_for_scores()

        pp((self.MUSIC['scores']))

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
