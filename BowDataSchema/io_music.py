#!python
"""
:module:    io_music.py

:author:    GM (genuinemerit @ pm.me)

Use music21 to assign parts, phrases, pitches, notes, durations, etc.
 to nodes, then to generate scores and midi files.

This class assumes that graph data describing Nodes and Edges
related to some topic (see io_graphs.py) has already been parsed
and saved as pickled files. It uses the *_nodes.pickle file
to drive the generation of music.
"""

import music21 as m21
import pickle
import random

from copy import copy
from dataclasses import dataclass   # fields
from os import path
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp

from sympy import false         # noqa: F401

from io_config import ConfigIO          # type: ignore
from io_file import FileIO              # type: ignore
from io_redis import RedisIO            # type: ignore

CI = ConfigIO()
FI = FileIO()
RI = RedisIO()


class MusicIO(object):
    """Class for Music Generation methods.
    """
    def __init__(self,
                 p_file_nm: str):
        """Class for managing music data, generating scores
        and other music-related methods.

        How to:
        - Load and create a fresh SCORE pickle from the NODES pickle:
            self.set_music_data()
        - Create a fresh MIDI-type file/object from the SCORE pickle
          and show it in MuseScore3:
            self.set_midi_data()

        :args: p_save_nm: str
            - Generic name of files where nodes data object saved
            - Example: "places_data"
        """
        self.file_nm = path.join(RI.get_app_path(),
                                 RI.get_config_value('save_path'),
                                 p_file_nm)
        with open(self.file_nm + "_nodes.pickle", 'rb') as f:
            self.NODES = pickle.load(f)
        self.PALETTE = dict()
        self.SCORE = dict()

    @dataclass
    class CANON:
        """Class for defining canonical components of musical language.
        Class also used for deriving chordal/harmonic progressions.
        A THEME is like a motif of chord progressions.
        A PROG(gression) is a collection of phrases that repeat a THEME.

        These materials should remain immutable.

        The class uses music21 convention of "#" for sharp (#) and "-"
        for flat (-). Double-flat (--) is --. Double-sharp (##) is ##.
        A m21 method displays notes using proper unicode characters for
        accidentals and so forth, so don't worry about that in here.

        Regarding tuplets...
        triplet = m21.duration.Tuplet(3, 2)
          means, put 3 notes into a tuple with duration of 2 eighths
        Example of quintuplet lasting as long as 2 eighths:
        quintuplet = m21.duration.Tuplet(5, 2)

        See these references for more information on music21 library:
        web.mit.edu/music21/doc/
        web.mit.edu/music21/doc/genindex.html
        web.mit.edu/music21/doc/py-modindex.html

        The "genindex" link is the best detailed technical reference.
        Class for deriving melodic progressions.

        So far I have little meta-language for defining motives.
        No doubt better ones out there. But want to explore a bit.
        Specific pitches are assigned later,
        using both stochastic and deterministic methods.

        My little meta-language...

        Motives MO1...MOn are associated with time signatures.
        A time signature may have 1..n motives:

        For any score, 6 motives are required:
        '1' = primary motif
        '2' = secondary motif
        * = surprise motif, use about 2/3 thru score
        x = concluding motif, use on last bar of score
        '3' = tertiary motif
        '$' = turnaround motif, use on penultimate bar of the score
        ..but a motif can be empty.

        A motif is often broken into two half-motives if 4/4 or 6/8 time,
         or two part-motives (1/3 , 2/3) if 3/4 time.
        | = mid-point of the motif, if there is one.
        Each partial-motive has one to n motif-notes.

        Every motif-note has a relative duration:

        B = a beat equal to the that of the timesig denominator
            Example, in 4/4 or 3/4, a quarter note duration
        Q = 1/4 B. In 4/4, a sixteenth note.
        S = 1/2 B. In 4/4, an eighth note.
        D = 2 B. In 4/4, a half note.
        T = Triplet B. In 4/4, a triplet-eighth.
        _ - Tie note to next note.  <-- NOT implemented yet.

        Rests are defined by following a motify-note with 'r'.

        And a relative direction:

        ^ = ascend as compared to previous note
        v = descend as compared to previous note
        ~ = either ascend or descend or stay the same, but
            do so consistently when the motif is repeated

        Rests have an 'r' instead of a direction.


        A score is made up of n bars playing the motives,
        as they are defined, or with variations.

        Variations are rules applied to a motif.
        The simplest rule is "as is", i.e., no change.
        So far, planning to implement only a few others, like:
        - Swap the order of the partial-motives in a bar.
        - Invert the direction rules in a partial-motive.
        - Invert the order of the motif-notes in a partial-motive.
        - Combination of those.
        - Randomly modify the dynamics of the motives.

        NOT USING FOR NOW..
        Optional modifiers for dynamics and articulation,
        if any, follow the note's duration and direction.
        P = piannissimo
        p = piano
        m = mezzo-forte
        f = forte
        F = fortissimo
        > = accent the note
        + = fermata

        Eventually want to add timbre (MIDI instrumentation) too.

        Whitespace removed from analysis. Only here used to ease display.
        """
        NOTES = dict()
        for nty in ('full', 'rest', 'dotted', 'tuplet'):
            NOTES[nty] = dict()
        NOTES['full'] = {'breve': 8.0, 'whole': 4.0, 'half': 2.0,
                         'quarter': 1.0, 'eighth': 0.5, '16th': 0.25,
                         '32nd': 0.125, '64th': 0.0625}
        for n, d in NOTES['full'].items():
            dur = copy(d)
            NOTES['full'][n] = m21.duration.Duration(dur)
            NOTES['rest'][n] = m21.note.Rest(quarterLength=dur)
            NOTES['dotted'][n] = m21.duration.Duration(dur + (dur / 2))
        # May want to add triplets for eighths also.
        NOTES['tuplet'] = {
            # duration of one half note:
            'tripletQtrs': m21.duration.Tuplet(3, 4),
            'quintupletQtrs': m21.duration.Tuplet(5, 4),
            # duration of one quarter note:
            'triplet8ths': m21.duration.Tuplet(3, 2),
            'quintuplet8ths': m21.duration.Tuplet(5, 2),
            # duration of one eighth note:
            'triplet16ths': m21.duration.Tuplet(3, 1),
            'quintuplet16ths': m21.duration.Tuplet(5, 1)}

        SCALE = dict()
        for k in ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#',
                  'F', 'B-', 'E-', 'A-', 'D-', 'G-', 'C-', 'F-']:
            SCALE[k] = {
                'major': m21.scale.MajorScale(k),
                'minor': m21.scale.MinorScale(k),
                'harmonicMinor': m21.scale.HarmonicMinorScale(k),
                'melodicMinor': m21.scale.MelodicMinorScale(k)}

        KEYSIG = dict()
        for k in SCALE.keys():
            KEYSIG[k] = dict()
            for mode, m_obj in SCALE[k].items():
                a_cnt = 0
                for p in m_obj.pitches:
                    a_cnt = a_cnt + 1 if '#' in p.name\
                        else a_cnt - 1 if '-' in p.name else a_cnt
                KEYSIG[k][mode] = m21.key.KeySignature(a_cnt)

        TIMESIG = dict()
        for sig in ('2/2', '3/4', '4/4', '6/8'):
            TIMESIG[sig] = m21.meter.TimeSignature(sig)

        THEME = dict()
        THEME[0] = ['ii', 'V', 'I']
        THEME[1] = ['I', 'V', 'vi', 'IV']
        THEME[2] = ['I', 'V', 'vi', 'ii']
        THEME[3] = ['I', 'iii', 'vi', 'IV']
        THEME[4] = ['I', 'iii', 'vi', 'ii']
        THEME[5] = ['I', 'vi', 'IV', 'V']
        THEME[6] = ['I', 'IV', 'vi', 'V']
        THEME[7] = ['I', 'vi', 'ii', 'V']
        THEME[8] = ['I', 'ii', 'vi', 'V']
        THEME[9] = ['I', 'IV', 'I', 'IV', 'V']
        THEME[10] = ['I', 'IV', 'I', 'IV']
        THEME[11] = ['vi', 'IV', 'vi', 'IV']
        THEME[12] = ['ii', 'V', 'IV', 'V']
        THEME[13] = ['ii', 'V', 'vi', 'IV']
        THEME[14] = ['I', 'iii', 'IV', 'V']
        THEME[15] = ['I', 'ii', 'iii', 'IV', 'V']
        THEME[16] = ['I', 'V', 'vi', 'iii']
        THEME[17] = ['IV', 'I', 'IV', 'V']
        THEME[18] = ['I', 'I', 'I', 'I']
        THEME[19] = ['IV', 'IV', 'I', 'I']
        THEME[20] = ['V', 'IV', 'I', 'V']
        THEME[21] = ['I', 'IV', 'I', 'I']
        THEME[22] = ['V', 'IV', 'I', 'I']

        DEGREES = {
            'I': 1,
            'ii': 2,
            'iii': 3,
            'IV': 4,
            'V': 5,
            'vi': 6,
            'vii': 7}

        PROG = dict()
        PROG[0] = {"phrases": 4, "chords": THEME[0] * 4}
        PROG[1] = {"phrases": 3,  "chords": THEME[1] * 3}
        PROG[2] = {"phrases": 3,  "chords": THEME[2] * 3}
        PROG[3] = {"phrases": 3,  "chords": THEME[3] * 3}
        PROG[4] = {"phrases": 3,  "chords": THEME[4] * 3}
        PROG[5] = {"phrases": 3,  "chords": THEME[5] * 3}
        PROG[6] = {"phrases": 3,  "chords": THEME[6] * 3}
        PROG[7] = {"phrases": 3,  "chords": THEME[7] * 3}
        PROG[8] = {"phrases": 3,  "chords": THEME[8] * 3}
        PROG[9] = {"phrases": 3,  "chords": THEME[9] * 3}
        PROG[10] = {"phrases": 3,  "chords": THEME[10] * 2 + THEME[11]}
        PROG[11] = {"phrases": 4,  "chords": THEME[11] + THEME[12] +
                    THEME[11] + THEME[12]}
        PROG[12] = {"phrases": 4,  "chords": THEME[10] + THEME[13] +
                    THEME[10] + THEME[13]}
        PROG[13] = {"phrases": 3,  "chords": THEME[14] * 3}
        PROG[14] = {"phrases": 3,  "chords": THEME[15] * 3}
        PROG[15] = {"phrases": 4,  "chords": THEME[16] + THEME[17] +
                    THEME[16] + THEME[17]}
        PROG[16] = {"phrases": 3,  "chords": THEME[18] + THEME[19] +
                    THEME[20]}
        PROG[17] = {"phrases": 3,  "chords": THEME[21] + THEME[19] +
                    THEME[20]}
        PROG[18] = {"phrases": 3,  "chords": THEME[18] + THEME[19] +
                    THEME[22]}

        MOTIF = dict()

        # 4 total beats per motif - check
        MOTIF['4/4'] = {
            "MO1": {'1st': "S~S~B^        | S~S~Bv",
                    '2nd': "T~B~          | T~B~",
                    '3rd': "",
                    'Change': "S~S~S~S~      | SrS~B~",
                    'Turn': 'Q~QvQ~QvQ~QvQ~Qv  | SvS^S^S^',
                    'End': 'B~B~          | D~'}}

        # 3 total beats per motif - check
        MOTIF['3/4'] = {
            "MO2": {'1st': "D~        | S^S^",
                    '2nd': "D~        | SvSv",
                    '3rd': "",
                    'Change': "T~        | D~",
                    'Turn': "",
                    'End': 'S~S~      | D~'},
            "MO3": {'1st': "S~Q~Q~    | D^",
                    '2nd': "S~Q~Q~    | Dv",
                    '3rd': "",
                    'Change': "T~        | D~",
                    'Turn': "",
                    'End': 'S~        | B~B~'}}

        # 2 total beats per motif - check
        MOTIF['2/2'] = {
            "MO4": {'1st': "B~B~",
                    '2nd': "D~",
                    '3rd': "",
                    'Change': "S~S~S~Sr",
                    'Turn': "",
                    'End': 'Dv'}}

        # 6 total beats per motif - check
        MOTIF['6/8'] = {
            "MO4": {'1st': "B~B^B^       | B~BvBv",
                    '2nd': "B~BvBv       | B~B~B~",
                    '3rd': "B~B~B~       | DvB~",
                    'Change': "B^B^B^       | DvB~",
                    'Turn': "",
                    'End': 'SvSvSvSvSvSv | D~B~'}}

    def set_bar_pitches(self,
                        nnm: str,
                        p_barx: int,
                        p_degree: dict,
                        p_pattern: dict,
                        p_scale: dict,
                        p_chords: dict):
        """Assign pitches for one measure.

        Rules:
        - If only one rhythm-note, use either a full 7 chord or a triad.
        - If first note in a multi-note bar start with p_chords[0] note.

        @DEV
        - Refine this further to handle surprise, minor-third, & fifth
        - If the corresponding rhythm-note is a rest, then indicate no pitch.
        - Maybe work more on patterns for "steady" (arpeggios) that take
          into account previous notes.
        - Before doing that stuff ^, try to generate a music21 or
          lilypond or diret-to-midi file, play it, see how it sounds.
          Work in on "compiling" the patterns into a usable format
          before tweaking the composition algorithm more.
        """
        pitches = list()
        rhythm_notes = self.SCORE[nnm]["notes"][1]["rhythm"][p_barx]
        chrd_x = 0
        scal_x = 0
        chords = None
        scales = None
        pitch = None

        for dur_x, _ in enumerate(rhythm_notes):
            if p_pattern["rule"] == "tonic" and len(rhythm_notes) == 1:
                if random.randint(0, 100) < 30:
                    pitches = p_chords["main"]      # 7 chord
                else:
                    pitches = p_chords["main"][:2]  # triad
            else:
                if dur_x == 0:                      # first note in bar
                    chrd_x = 0
                    tone = ""
                    chord_pick = random.randint(0, 100)
                    if chord_pick < 60 or p_pattern["rule"] == "tonic":
                        tone = "main"
                    elif chord_pick < 80:
                        tone = "rel"
                    elif chord_pick < 90:
                        tone = "IV"
                    elif chord_pick < 95:
                        tone = "V"
                    else:
                        tone = "parl"
                    chords = p_chords[tone]
                    scales = p_scale[tone]
                    pitch = chords[chrd_x]
                    scal_x = scales.index(pitch)
                else:                               # subsequent notes
                    if p_pattern["direction"] == "asc":
                        chrd_x += 1\
                            if (chrd_x + 1) < (len(chords) - 1) else 0
                        pitch = chords[chrd_x]
                    elif p_pattern["direction"] == "desc":
                        if chrd_x > 0:
                            chrd_x = chrd_x - 1
                        else:
                            chrd_x = (len(chords) - 1)
                        pitch = chords[chrd_x]
                    else:
                        pick_interval = random.randint(0, 100)
                        if pick_interval > 75:
                            scal_x += 1\
                                if (scal_x + 1) < (len(scales) - 1) else 0
                        elif pick_interval > 50:
                            if scal_x > 0:
                                scal_x = scal_x - 1
                            else:
                                scal_x = (len(scales) - 1)
                        pitch = scales[scal_x]
                # pp(("chrd_x: ", chrd_x,
                #     "scal_x: ", scal_x, "pitch: ", pitch))
                pitches.append(pitch)
            # pp(("pitches", pitches))
        self.SCORE[nnm]["notes"][1]["pitch"][p_barx] = pitches

    def get_sevens(self,
                   p_note: str,
                   p_scale: list):
        """Return a list containing triad plus dominant 7th
        for notes in designated key. Dominant means flat the 7th.

        Turned off the range for now.
        """
        notex = p_scale.index(p_note)
        # chord_range = 4
        chord_range = ""
        chord = [p_note + str(chord_range)]
        for n in range(3):
            if notex < (len(p_scale) - 2):
                notex = notex + 2
            else:
                notex = 0
                # chord_range += 1
            note = p_scale[notex]
            if n == 2:
                if note[-1:] == "#":
                    note = note[:1]
                else:
                    note += "-"
            chord.append(note + str(chord_range))
        return chord

    def pick_a_pitch(self,
                     nnm: str,
                     bars: dict):
        """Assign a pitch for every interval in a measure.
        - Choose triad or other harmonic vs. melodic line.
        - Apply interval change to tonic if using harmonics.
        - Start of each phrase should echo the first bar.
        - End of each phrase should be punctuated in some fashion.
        - Eventually, maybe adjust for register changes, but for
          now just see how music21 handles it.

        :args:
        - nnm (str) : Name of node being processed.
        - bars (dict) : Dictionary of bars.

        return: (dict) : Enhanced bars data.
        """
        scale = self.SCORE[nnm]["scale"]
        bar_cnt = 0
        for roman in self.SCORE[nnm]['chords']:
            bars[bar_cnt] = dict()
            degree = self.CANON.DEGREES[roman]
            bar_values = list(bars.values())
            mx = bar_values.index(bar_cnt)\
                if bar_cnt in bars.values() else None
            m_nm = list(bars.keys())[mx]\
                if mx is not None else None
            pp(("mx: ", mx, "  roman: ", roman, "  degree: ", degree, "  m_nm: ", m_nm))

            # Handle bars for which a specific motif is defined.
            if m_nm is not None and m_nm in self.SCORE[nnm]['motif'].keys():
                print(f"\n\nProcessing bar: {m_nm} / {mx}")
                this_bar = list()
                for dirs in self.SCORE[nnm]['motif'][m_nm]['dirs']:
                    pitches = list()
                    for dir in dirs:
                        degree += dir
                        # Increase/decrease probability of using a
                        # chord based on what type of bar it is.
                        if random.randint(0, 100) < 70:
                            pitch = m21.chord.Chord([
                                scale.pitchFromDegree(degree),
                                scale.pitchFromDegree(degree + 2),
                                scale.pitchFromDegree(degree + 4)])
                        else:
                            pitch = scale.pitchFromDegree(degree)
                        pitches.append(pitch)
                    this_bar.append(pitches)
                bars[bar_cnt]['pitches'] = this_bar
                bars[bar_cnt]['notes'] =\
                    self.SCORE[nnm]['motif'][m_nm]['notes']
                del bars[m_nm]

            # TODO: Handle bars for which a specific motif is not defined.

            # First, those identified as Phrase Start or Phrase End. Apply
            #  specific variations to those bars which either echo the first
            #  bar or contain punctuation that marks a phrase end.
            # (Not sure what these "rules" are yet. :-)  )

            # And finally, the remaining bars, using a random choice of
            # variations, like:
            # - Choose notes similar to preceding bar but...
            # - Swap the order of the partial-motives in a bar.
            # - Invert the direction rules in a partial-motive.
            # - Invert the order of the motif-notes in a partial-motive.
            # - Combination of those.
            # - Randomly modify the dynamics of the motives.

            bar_cnt += 1
        return bars

    def identify_bars(self, nnm):
        """Assign name and index to bars that align directly or
        indirectly to a motif.

        :args:
        - nnm (str) : Name of node being processed.

        return: (dict) : initialized set of bar names and indexes.
        """
        bars = {
            '1st': 0,
            '2nd': int(round(self.SCORE[nnm]['bar_cnt'] * .25)),
            'Change': int(round(self.SCORE[nnm]['bar_cnt'] * .67)),
            'End': self.SCORE[nnm]['bar_cnt'] - 1
        }
        # Compute size of phrases
        p_sz = int(round(
            self.SCORE[nnm]['bar_cnt'] / self.SCORE[nnm]['phr_cnt']))
        # Determine where is the 3rd motif, if one is defined.
        if self.SCORE[nnm]['motif']['3rd'] != '':
            bars['3rd'] = int(round(self.SCORE[nnm]['bar_cnt'] * .75))
        # Determine where is the turnaround, if one is defined.
        if self.SCORE[nnm]['motif']['Turn'] != '':
            bars['Turn'] = bars['End'] - 1
        # Identify first and last bar of each phrase.
        for p in range(0, self.SCORE[nnm]['phr_cnt']):
            bars[f'End phrase {p + 1}'] = ((p + 1) * p_sz) - 1
            if ((p + 1) * p_sz) < len(bars):
                bars[f'Start phrase {p + 2}'] = ((p + 1) * p_sz)
        return bars

    def set_pitches(self,
                    nnm: str):
        """For each measure, set the pitch for each motif-note.

        :args:
        - nnm (str) : Name of node being processed.

        :sets:
        - (class attribute): self.SCORE
        """
        bars = self.identify_bars(nnm)
        bars = self.pick_a_pitch(nnm, bars)
        self.SCORE[nnm]['bars'] = bars

        print("\n\n")
        pp(("nnm, score: ", nnm, self.SCORE[nnm]))

    def translate_direction(self,
                            p_meta: str,):
        """Translate motif direction metadata into an integer representing
           number of interval steps up (postive) or down (negative).

        :args:
        - p_meta (char) : one-byte meta-character being analyzed

        :returns: (int) : indicating number of interval steps up or down
        """
        intervals = random.choice([-1, 0, 1]) if p_meta == '~' else\
            random.choice([-3, -2, 11]) if p_meta == 'v' else\
            random.choice([3, 2, 1]) if p_meta == '^' else 0
        return intervals

    def translate_duration(self,
                           p_meta: str,
                           p_next: str,
                           p_denom: int):
        """Translate motif duration metadata into music21 durations, rests.

        :args:
        - p_meta (char) : one-byte meta-character being analyzed
        - p_next_meta (char) : one-byte meta-character following p_meta
        - p_denom (int) : time signature denominator
                        elif (denom == 2 and meta == 'W'):
                            n.append(no['full']['breve'])\
        """
        cnot = self.CANON.NOTES
        rules = (([(8, 'Q')], '32nd'),
                 ([(4, 'Q'), (8, 'S')], '16th'),
                 ([(4, 'S'), (8, 'B'), (2, 'Q')], 'eighth'),
                 ([(4, 'B'), (8, 'D'), (2, 'S')], 'quarter'),
                 ([(4, 'D'), (8, 'W'), (2, 'B')], 'half'),
                 ([(4, 'W'), (2, 'D')], 'whole'),
                 ([(2, 'W')], 'breve'))

        def translate_triplet(p_denom):
            note = cnot['tuplet']['triplet8ths'] if p_denom == 4 else \
                cnot['tuplet']['triplet16ths'] if p_denom == 8 else \
                cnot['tuplet']['tripletQtrs'] if p_denom == 2 else \
                cnot['full']['quarter'] if p_denom == 4 else\
                cnot['full']['eighth'] if p_denom == 8 else\
                cnot['full']['half'] if p_denom == 2 else\
                cnot['full']['quarter']
            return note

        def translate_note(p_meta, p_denom, p_rest_or_full):
            for r in rules:
                for dm in r[0]:
                    if p_denom == dm[0] and p_meta == dm[1]:
                        return cnot[p_rest_or_full][r[1]]
            return None

        if p_meta == 'T':
            note = translate_triplet(p_denom)
        elif p_next == 'r':
            note = translate_note(p_meta, p_denom, 'rest')
        else:
            note = translate_note(p_meta, p_denom, 'full')

        return note

    def translate_motif(self,
                        p_mots: list,
                        p_denom: int):
        """Translate metadata from one motif into music21 objects.

        :args:
        - p_mot (list) : list of one or two motif metadata strings
        - p_denom (int) : time signature denominator

        :returns: (dict) : {'notes': [list-1 of durations and rests][list-2],
                            'dirs': [list-1 of directional integers][list-2]}
        """
        if p_mots == [""]:
            return ""
        notes = list()
        dirs = list()
        for mot in p_mots:
            no = list()
            dr = list()
            for mx, meta in enumerate(mot):
                if meta in ('Q', 'S', 'B', 'D', 'W', 'T'):
                    no.append(
                        self.translate_duration(meta, mot[mx + 1], p_denom))
                elif meta in ('^', 'v', '~'):
                    dr.append(self.translate_direction(meta))
            notes.append(no)
            dirs.append(dr)
        return {'notes': notes, 'dirs': dirs}

    def set_motif(self, nnm: str):
        """Select motif for the score + timesig combo.
        Convert motif to note- and rest-durations matching time signature.
        Set integers representing number of interval steps up (postive) or
        down (negative).

        :sets:
        - (class attribute): self.SCORE
        """
        ts = self.SCORE[nnm]['beat']['time_sig'].ratioString
        denom = self.SCORE[nnm]['beat']['time_sig'].denominator
        mot_raw = self.CANON.MOTIF[ts][random.choice(
            list(self.CANON.MOTIF[ts].keys()))]
        motif = dict()
        for mot_nm, mot_str in mot_raw.items():
            mots = mot_str.split('|') if '|' in mot_str else [mot_str]
            motif[mot_nm] = self.translate_motif(mots, denom)
        self.SCORE[nnm]['motif'] = motif

    def set_meter(self, nnm: str):
        """Select random time signature and tempo.
        Example:  time_sig = 3/4 so
            pulses per measure = 3, pulse note = quater note = '4'
        For BPM (= tempo), pick random integer between 60 and 160.

        :sets:
        - (class attribute): self.SCORE
        """
        ts = random.choice(list(self.CANON.TIMESIG.keys()))
        self.SCORE[nnm]['beat'] = {
            'bar_dur': self.CANON.TIMESIG[ts].barDuration,
            'beat_dur': self.CANON.TIMESIG[ts].beatDuration,
            'beat_cnt': self.CANON.TIMESIG[ts].beatCount,
            'metron': m21.tempo.MetronomeMark(random.randint(60, 160)),
            'time_sig': self.CANON.TIMESIG[ts]}

    def set_node_scores(self):
        """Assign a score to each unique Node.
        Recall that a "Node" = an entity on the graph.

        :sets:
        - (class attribute): self.SCORE
        """
        # dbug_max = len(self.NODES.keys())
        dbug_max = 3
        dbug = 0
        for nnm, nd in self.NODES.items():
            dbug += 1
            label = self.PALETTE['labels'][nd['L']]
            topic = self.PALETTE['topics'][nd['T']]
            self.SCORE[nnm] = {
                "bar_cnt": label["bar_cnt"], "phr_cnt": label["phr_cnt"],
                "chords": label["chords"],
                "keysig": topic["keysig"], "scale": topic["scale"]}
            self.set_meter(nnm)
            self.set_motif(nnm)
            self.set_pitches(nnm)
            if dbug >= dbug_max:
                break

    def set_label_progressions(self):
        """Assign a chord progression pattern to unique Node Label.
        Recall that a "Label" defines Node record-types.

        :sets:
        - (class attribute): self.PALETTE
        """
        self.PALETTE['labels'] = dict()
        labels = set([data['L'] for _, data in self.NODES.items()])
        for label in labels:
            p_x = random.choice(list(self.CANON.PROG.keys()))
            self.PALETTE['labels'][label] =\
                {"chords": self.CANON.PROG[p_x]['chords'],
                 "phr_cnt": self.CANON.PROG[p_x]['phrases'],
                 "bar_cnt": len(self.CANON.PROG[p_x]['chords'])}

    def set_topic_modes(self):
        """Assign a key and scale for each unique Node Topic.
        Recall that a "Topic" = a spreadsheet name = a geo-spatial category.
        Keep in mind that not all the CANON scales have minor modes.

        :sets:
        - (class attribute): self.PALETTE
        """
        self.PALETTE['topics'] = dict()
        topics = set([data['T'] for _, data in self.NODES.items()])
        # 67% chance to use major, else minor
        for topic in topics:
            k = random.choice(list(self.CANON.SCALE.keys()))
            if random.randint(100, 100) < 67:
                m = "major"
            else:
                got_it = False
                while not got_it:
                    m = random.choice(
                        ["minor", "harmonicMinor", "melodicMinor"])
                    if m in self.CANON.SCALE[k]:
                        got_it = True
                    else:
                        k = random.choice(list(self.CANON.SCALE.keys()))
            self.PALETTE['topics'][topic] =\
                {"keysig": self.CANON.KEYSIG[k][m],
                 "scale": self.CANON.SCALE[k][m]}

    def set_music_data(self):
        """Generate music data from the graph data.

        :sets:
        - (class attribute): self.PALETTE
        - (class attribute): self.SCORE
        print("\n\nRetrieved graph data ===")
        pp(("NODES", self.NODES))

        print("\n\nFixed canonical musical materials ===")
        pp(("CANON.SCALE", self.CANON.SCALE))
        pp(("CANON.TIMESIG", self.CANON.TIMESIG))
        pp(("CANON.KEYSIG", self.CANON.KEYSIG))
        pp(("CANON.NOTES", self.CANON.NOTES))
        pp(("CANON.THEME", self.CANON.THEME))
        pp(("CANON.PROG", self.CANON.PROG))
        pp(("CANON.MOTIF", self.CANON.MOTIF))

        print("\n\nGeneric thematic assignments ==============")
        pp(("PALETTE", self.PALETTE))

        print("\n\nMelodic and harmonic assignments ==============")
        pp(("SCORE", self.SCORE))
        """
        self.set_topic_modes()
        self.set_label_progressions()
        self.set_node_scores()
        """

        # self.file_nm
        with open(self.file_nm + "_scores.pickle", 'wb') as obj_file:
            pickle.dump(self.SCORE, obj_file)
        print(f"Music SCORE object pickled to: {self.file_nm}" +
              "_scores.pickle")
        """

    def parse_score(self,
                    nnm: str,
                    p_key_sig: str,
                    p_beat: dict,
                    p_notes: dict):
        """Parse a score into music21 note objects.
        :args:
        - nnm (str): name of the Node
        - p_beat (dict): the beat data for one node
        - p_notes (dict): the voice #1 notes data for one Node

        :returns:
        - music21.stream.Score object (a midi file, basically)

        Will need to consider rhythm also in order to generate music
        per the desired algorithmic structure. Remember that measures
        with a single beat are treated as chords, so there will be 3
        pitches but only a single note. Obviously, rhythm also gives
        us duration. The notes data tells us the clef. The beat data
        has time signature and BPM. The modes['key_sig'] has key signature.

        Duration in music21 is based in quarter notes having a value 1.0.
        So, a dotted quarter is 1.5. A half note is 2.0. A whole note is 4.0.
        An eighth note is 0.5. A sixteenth note is 0.25. A thirty-second note
        is 0.125. A sixty-fourth note is 0.0625. These are the same values
        stored in the self.CANON.NOTES dataclass object.

        I'm finding way too many rests in the score, so I am going to
        ignore them for now (since I ignored them when assigning pitches
        anyway).

        Not quite getting how music21 handles dotted notes, so am going
        to remove them for now, which will create some weirdness. :-)

        OK. Making some headway. I am thinking that I should probably just
        use music21-oriented objects in the CANON to start with, and
        reference them directly when generating the score. This can inlcude
        clefs, key signatures, time signatures, and BPM.

        Once the notes are parsed, a music21 object/stream is created.
        - Send to MuseScore: <object>.show()
        - Play it: <object>.show('midi') <-- my default player is timidity
        """
        print(f"\n\n========  {nnm}  ============")
        pp((("key signature", p_key_sig), ("beat", p_beat)))
        score = m21.stream.Stream()
        score.clef = m21.clef.TrebleClef()
        score.timeSignature = m21.meter.TimeSignature(p_beat["time_sig"])
        for m, pitches in p_notes['pitch'].items():
            measure = m21.stream.Stream()
            range = 4
            used = set()
            rhythms = p_notes['rhythm'][m]
            pp((("\nmeasure: ", m), ("pitches", pitches),
                ("rhythms", rhythms)))
            if len(rhythms) == 1:
                # handle chords here
                pass
            else:
                for px, pit in enumerate(pitches):
                    rhy = rhythms[px].replace('r', '').replace('.', '')
                    dur = self.CANON.NOTES[rhy][1]
                    if pit[:1] in used:
                        range = random.choice([3, 4, 5])\
                            if range == 4 else 4
                    else:
                        used.add(pit[:1])
                    pit += str(range)
                    pit = pit.replace("-", "-").replace("#", "#")
                    # print(f"{pit} ({dur}) = " +
                    #      f"{m21.pitch.Pitch(pit).unicodeName}")
                    pp((("pit", pit), ("rhy", rhy), ("dur", dur)))
                    measure.append(m21.note.Note(pit, type=dur))
            # measure.show("midi")
            score.append(measure)
        score.show("midi")
        return score

    def set_midi_data(self):
        """Generate music file from music object that can be
           loaded into MuscScore3 or other midi-style program.


        After learning how to do some stuff, may want to reduce the
        m21 modules imported to just the ones that are needed.

        Also keep in mind that music21 supports microtonal music, and
        can also define durations of any length, regardless of whether
        such a note exists in canonical notation.

        Furthermore, it has a large set of music21 objects, which means
        I can choose instruments/timbres, use the system to define
        rhythms/beats, manipulate metronome/tempo and more.

        This is such a large, complete library, it is really silly for
        me to invent another layer of my own on top of it -- other than
        for the pure joy and pedantic thrill of it of course! :-)

        Should be able to simplify this once the set_music_data methods
        are more closely aligned to music21 objects.
        """
        with open(self.file_nm + "_scores.pickle", 'rb') as f:
            self.SCORE = pickle.load(f)
        m21.environment.set('midiPath', '/usr/bin/timidity')
        print("\n\nMelodic and harmonic assignments ==============")
        dbug_max = 2
        dbug = 0
        book = m21.stream.Stream()
        for n_name, n_data in self.SCORE.items():
            dbug += 1
            score = self.parse_score(n_name, n_data["modes"]["key_sig"],
                                     n_data["beat"], n_data["notes"][1])
            book.append(score)
            if dbug >= dbug_max:
                break
        book.show()
