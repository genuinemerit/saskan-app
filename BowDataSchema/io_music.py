#!python
"""
:module:    io_music.py

:author:    GM (genuinemerit @ pm.me)

Use music21 to assign parts, phrases, pitches, notes, durations, etc.
 to nodes, then to generate scores and midi files.

This class assumes that graph data has already been parsed
and saved as pickled files. It uses the *_nodes.pickle file
to drive the generation of music.
"""

import pickle
import random

from collections import OrderedDict
from copy import copy
from dataclasses import dataclass   # fields
from os import path
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

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

        It assumes a nodes data file has been pickled to the
        save directory which ends with "_nodes.pickle".

        :args: p_save_nm: str
            - Generic name of related files where nodes data object saved
            - Example: "places_data"
        """
        save_nm = path.join(RI.get_app_path(),
                            RI.get_config_value('save_path'),
                            p_file_nm)
        with open(save_nm + "_nodes.pickle", 'rb') as f:
            self.NODES = pickle.load(f)
        self.PALETTE = dict()
        self.SCORES = dict()
        self.set_music_data()

    @dataclass
    class CANON:
        """Class for defining canonical components of musical language."""
        MAJOR = OrderedDict()
        MAJOR['C'] = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        MAJOR['G'] = ['G', 'A', 'B', 'C', 'D', 'E', 'F♯']
        MAJOR['D'] = ['D', 'E', 'F♯', 'G', 'A', 'B', 'C♯']
        MAJOR['A'] = ['A', 'B', 'C♯', 'D', 'E', 'F♯', 'G♯']
        MAJOR['E'] = ['E', 'F♯', 'G♯', 'A', 'B', 'C♯', 'D♯']
        MAJOR['B'] = ['B', 'C♯', 'D♯', 'E', 'F♯', 'G♯', 'A♯']
        MAJOR['G♭'] = ['G♭', 'A♭', 'B♭', 'C♭', 'D♭', 'E♭', 'F']
        MAJOR['D♭'] = ['D♭', 'E♭', 'F', 'G♭', 'A♭', 'B♭', 'C']
        MAJOR['A♭'] = ['A♭', 'B♭', 'C', 'D♭', 'E♭', 'F', 'G']
        MAJOR['E♭'] = ['E♭', 'F', 'G', 'A♭', 'B♭', 'C', 'D']
        MAJOR['B♭'] = ['B♭', 'C', 'D', 'E♭', 'F', 'G', 'A']
        MAJOR['F'] = ['F', 'G', 'A', 'B♭', 'C', 'D', 'E']

        MINOR = dict()
        minor_names = ("natural", "harmonic", "melodic")
        for m in minor_names:
            MINOR[m] = OrderedDict()
        for major_k, sc in MAJOR.items():
            minor_k = MAJOR[major_k][5] + 'm'
            MINOR["natural"][minor_k] =\
                [sc[5], sc[6], sc[0], sc[1], sc[2], sc[3], sc[4]]
            MINOR["harmonic"][minor_k] = copy(MINOR["natural"][minor_k])
            MINOR["harmonic"][minor_k][6] =\
                MINOR["harmonic"][minor_k][6][:-1]\
                if MINOR["harmonic"][minor_k][6][-1:] == '♭'\
                else MINOR["harmonic"][minor_k][6] + '♯'
            if '♯♯' in MINOR["harmonic"][minor_k][6]:
                MINOR["harmonic"][minor_k][6] =\
                    MINOR["harmonic"][minor_k][6][:1] + '𝄪'
            MINOR["melodic"][minor_k] = copy(MINOR["natural"][minor_k])
            MINOR["melodic"][minor_k][5] =\
                MINOR["melodic"][minor_k][5][:-1]\
                if MINOR["melodic"][minor_k][5][-1:] == '♭'\
                else MINOR["melodic"][minor_k][5] + '♯'
            if '♯♯' in MINOR["melodic"][minor_k][5]:
                MINOR["melodic"][minor_k][5] =\
                    MINOR["melodic"][minor_k][5][:1] + '𝄪'

        DEGREES = dict()
        DEGREES['major'] = ['I', 'IV', 'V']
        DEGREES['minor'] = ['ii', 'iii', 'vi']
        DEGREES['diminished'] = ['VII°']
        DEGREES['arabic'] = ['1', '2', '3', '4', '5', '6', '7']
        DEGREES['roman'] = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'VII°']

        NOTES = OrderedDict()
        NOTES['1'] = (4, 'whole', 'w', '𝅝')
        NOTES['2'] = (2, 'half', 'h', '𝅗𝅥')
        NOTES['4'] = (1, 'quarter', 'q', '𝅘𝅥')
        NOTES['8'] = (0.5, 'eighth', 'e', '𝅘𝅥𝅮')
        NOTES['16'] = (0.25, 'sixteenth', 's', '𝅘𝅥𝅯')
        NOTES['2.'] = (3, 'dotted_half', 'h.', '𝄼.')
        NOTES['4.'] = (1.5, 'dotted_quarter', 'q.', '𝄽.')
        NOTES['T'] = (1, 'triplet', 't', '')
        NOTES['8.'] = (0.75, 'dotted_eighth', 'e.', '𝄾.')
        NOTES['8r'] = (0.5, 'eighth_rest', 'er', '𝄾')
        NOTES['4r'] = (1, 'quarter_rest', 'qr', '𝄽')
        NOTES['2r'] = (2, 'half_rest', 'hr', '𝄼')
        NOTES['1r'] = (4, 'whole_rest', 'wr', '𝄻')
        NOTES['16r'] = (0.25, 'sixteenth_rest', 'sr', '𝄿')
        NOTES['16t'] = (0.5, 'double_sixteenth', 'ss', '♬')
        NOTES['16.'] = (0.375, 'dotted_sixteenth', 's.', '𝅘𝅥𝅯.')
        NOTES['32'] = (0.125, 'thirty_second', 'ts', '𝅘𝅥𝅰')
        NOTES['32r'] = (0.125, 'thirty_second_rest', 'tsr', '𝅀')
        NOTES['32.'] = (0.1875, 'dotted_thirty_second', 'ts.', '𝅘𝅥𝅰.')
        NOTES['64'] = (0.0625, 'sixty_fourth', 'sf', '𝅘𝅥𝅱')
        NOTES['64r'] = (0.0625, 'sixty_fourth_rest', 'sfr', '𝅁')
        NOTES['64.'] = (0.9375, 'dotted_sixty_fourth', 'sf.', '𝅘𝅥𝅱.')

        TIMESIGS = dict()
        TIMESIGS["2/4"] = "March"
        TIMESIGS["3/4"] = "Waltz"
        TIMESIGS["4/4"] = "Common"

        MAX_VOICES = 3

    @dataclass
    class CHORD:
        """Class for deriving chord progressions."""

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

    def set_bar_pitches(self,
                        p_n_name: str,
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
        - Before doing that stuff ^, maybe try to generate a music21 or
          lilypond or diret-to-midi file, play it, see how it sounds.
          Get a little work in on "compiling" the patterns into a usable
          format.
        """
        pitches = list()
        rhythm_notes = self.SCORES[p_n_name]["notes"][1]["rhythm"][p_barx]
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
                pp(("chrd_x: ", chrd_x, "scal_x: ", scal_x, "pitch: ", pitch))
                pitches.append(pitch)

            pp(("pitches", pitches))

        self.SCORES[p_n_name]["notes"][1]["pitch"][p_barx] = pitches

    def set_pitches(self, p_n_name: str):
        """For each measure, set the pitch for each rhythm-note."""
        def get_sevens(p_note: str,
                       p_scale: list):
            """Return a list containing triad plus dominant 7th
            for notes in designated key. Dominant means flat the 7th.

            Assume we always start in range of C4-C5 for now.
            Later we'll adjust that based on clef and voice.
            May not want to assign a range here at all... we could
            end up wanting to use inverted chords, assign different
            ranges for different voices, etc.

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
                    if note[-1:] == "♯":
                        note = note[:1]
                    else:
                        note += "♭"
                chord.append(note + str(chord_range))
            return chord

        # set_pitches() MAIN
        # ===================================================
        self.SCORES[p_n_name]["notes"][1]['pitch'] = dict()
        print("\n\n")
        for barx, pat in enumerate(
                self.SCORES[p_n_name]["compose"]["pattern"]):
            self.SCORES[p_n_name]["notes"][1]['pitch'][barx] = list()
            deg = {"roman": self.SCORES[p_n_name]["compose"]["progress"][barx]}
            deg["x"] = self.CANON.DEGREES['roman'].index(deg["roman"])
            mods = self.SCORES[p_n_name]["modes"]["mods"]
            sca = {"main": self.SCORES[p_n_name]["modes"]["key_scale"],
                   "IV": mods['IV_key']['scale'],
                   "V": mods['V_key']['scale'],
                   "parl": mods['parallel']['scale'],
                   "rel": mods['relative']['scale']}
            chord = {"main": get_sevens(
                        sca["main"][deg["x"]],
                        self.SCORES[p_n_name]["modes"]["key_scale"]),
                     "IV": get_sevens(sca["IV"][deg["x"]],
                                      mods['IV_key']['scale']),
                     "V": get_sevens(sca["V"][deg["x"]],
                                     mods['V_key']['scale']),
                     "parl": get_sevens(sca["parl"][deg["x"]],
                                        mods['parallel']['scale']),
                     "rel": get_sevens(sca["rel"][deg["x"]],
                                       mods['relative']['scale'])}
            print("\n====")
            pp((("barx", barx),
                ("pat", pat),
                ("deg", deg),
                ("scale", sca),
                ("chord", chord)))
            self.set_bar_pitches(p_n_name, barx, deg, pat, sca, chord)

    def set_rhythm(self, p_n_name: str):
        """For each bar within each voice, establish a rhythmic progression.
        It will be described using musical notation, but without pitches.
        Assume that '4' = quarter note gets the beat in all cases.
        Examples, time signature 2/4:
        - One-and-Two-and (single pulse): (2) = one half
        - One-and, Two-and (double pulse): (4, 4) = two quarters
        - One-and-Two, and (shuffle-in): (4., 8) = dotted quater note, eighth
        - One, and-Two-and (shuffle-out): (8, 4.) = eighth, dotted quater note
        - One, and, Two, and (4-tuple): (8, 8, 8, 8) = 4 eighths
        ...and so on, including 16th, 32nd and 64th notes

        The largest note in a bar is the beat note / beats per bar,
        or the next whole-integer "up" from a fractional result.
        Example for 2/4: 4 / 2 = 2 (half note)
        Example for 3/4: 4 / 3 = 1.33 --> 2 (half note)
        Example for 4/4: 4 / 4 = 1 (whole note)

        Try to establish this without hard-coding the time signature.

        Use of 16ths, 32nd and 64ths is discouraged using filtering rules,
        but they are still needed in order to solve all situations.

        Use iterative backtracking (do-overs) to ensure rhythms are
        compatible with time signature.

        @DEV:
        - When adding more voices, may want to have more rules
        - That is, derive the additional voices' rhythms from the
          previously-established rhythms.
        """
        def set_beat_note(p_n_name: str,
                          p_beats: int,
                          p_beats_per_bar: int,
                          p_earlier_beat: int):
            """Assign random note and duration. Increment total beat duration.
            Voice index is hard-coded for now.
            """
            beats = p_beats
            if p_beats < p_beats_per_bar * 0.85:
                note = random.choice(
                    list(self.CANON.NOTES.keys())[:p_earlier_beat])
            else:
                note = random.choice(list(self.CANON.NOTES.keys()))
            duration = self.CANON.NOTES[note][0]
            if (p_beats + duration) <= b_per_bar:
                beats += duration
                self.SCORES[p_n_name]["notes"][1]['rhythm'][m].append((note))
            return beats

        # set_rhythm() MAIN
        # on first prototype, just doing one voice
        # =============================================================
        self.SCORES[p_n_name]["notes"][1]['rhythm'] = dict()
        for m, _ in enumerate(self.SCORES[p_n_name]["compose"]["pattern"]):
            beats = 0
            b_per_bar = self.SCORES[p_n_name]['beat']['per_bar']
            n_cnt = len(list(self.CANON.NOTES.keys()))
            n_earlier = int(round(n_cnt * 0.5))
            tries = 0
            do_overs = 0
            while do_overs < 10:
                self.SCORES[p_n_name]["notes"][1]['rhythm'][m] = list()
                while beats < b_per_bar:
                    beats = set_beat_note(
                        p_n_name, beats, b_per_bar, n_earlier)
                    tries += 1
                    if tries > 100:
                        print(f"tries exceeded 100 for {p_n_name}")
                        break
                do_overs += 1
                if beats == self.SCORES[p_n_name]['beat']['per_bar']:
                    break
                if do_overs >= 10:
                    # maybe save each try and if we have to quit,
                    # then pick the one with beats closest to 1.0.
                    print(f"do-overs exceeded 10 for {p_n_name}")

    def set_voices(self, p_n_name: str):
        """Determine how many voices to use and what clef they are in.
        Assume all voices are in the same key.
        """
        self.SCORES[p_n_name]["notes"] = dict()
        voice_cnt = random.randint(1, self.CANON.MAX_VOICES)
        for v in range(voice_cnt):
            clef = "𝄞" if (v == 0) or (random.randint(1, 101) < 80) else "𝄢"
            self.SCORES[p_n_name]["notes"][v + 1] = {"clef": clef}

    def set_melodic_pattern(self, p_n_name: str):
        """Set melodic pattern (asc, desc, steady) for each bar.
        Random mix but including rough rules like:
        - More ordered patterns (asc, desc) for first 2/3rds of bars
        - More surprise pattern (bigger intervals) for last 1/3 of bars
        - Include taste of the tonic or relative tonic in first and last bars
        - Include taste of a fifth or a minor third at end of phrases
           that are not the last bar in the score

        Just assign pattern name to each bar, not notes or pitches.
        """
        dir_tracker = {"asc": 0, "desc": 0, "steady": 0}
        b_cnt = self.SCORES[p_n_name]["compose"]["bars"]
        bpp = self.SCORES[p_n_name]["compose"]["bars_per_phrase"]
        pattern = list()
        for m in range(b_cnt):
            direction = random.choice(list(dir_tracker.keys()))
            prog = self.SCORES[p_n_name]["compose"]["progress"][m]
            orderly_odds = 85
            rule = "none"
            if (m == 0) or (m + 1 == b_cnt) or (prog == "I"):
                rule = "tonic"
                orderly_odds = 80
            elif ((m + 1) % bpp == 0):
                rule = "fifth" if random.randint(1, 101) > 50\
                    else "minor_third"
                orderly_odds = 90
            elif m > (b_cnt * .67):
                min_dir = min(dir_tracker.values())
                direction =\
                    [d for d, c in dir_tracker.items() if c == min_dir][0]
                orderly_odds = 25
            interval = "surprise" if random.randint(1, 101) > orderly_odds\
                else "orderly"
            if rule == "none":
                rule = "tonic" if random.randint(1, 101) > 90 else\
                    "fifth" if random.randint(1, 101) > 90 else\
                    "minor_third" if random.randint(1, 101) > 90 else "none"
            dir_tracker[direction] += 1
            pattern.append({"direction": direction,
                            "interval": interval,
                            "rule": rule})
        self.SCORES[p_n_name]["compose"]["pattern"] = pattern

    def set_modulated_keys(self, p_n_name: str):
        """Set keys, scales to use for modulations:
        - Parallel key - shares same tonic as main key
        - Relative key - shares same notes as main key
        - V key - a fifth "up", "to the "right" on Circle of 5ths
        - IV key - a fourth "down", "to the "left" on Circle of 5ths

        Choose minor mode randomly if main key is major.
        Set the key signature to match the major key.
        """
        def get_key(p_n_name):
            """And set key signature to match the major key."""
            if mod == "parallel":
                m_key = self.SCORES[p_n_name]['modes']['key_scale'][0]
            elif mod == "relative":
                if self.SCORES[p_n_name]['modes']['key_mode'] == "major":
                    m_key = self.SCORES[p_n_name]['modes']['key_scale'][5]
                    self.SCORES[p_n_name]['modes']["key_sig"] =\
                        self.SCORES[p_n_name]['modes']['key']
                else:
                    m_key = self.SCORES[p_n_name]['modes']['key_scale'][2]
                    self.SCORES[p_n_name]['modes']["key_sig"] = m_key
            elif mod == "V_key":
                m_key = self.SCORES[p_n_name]['modes']['key_scale'][4]
            elif mod == "IV_key":
                m_key = self.SCORES[p_n_name]['modes']['key_scale'][3]
            return m_key

        def adjust_key(p_key, p_mode):
            m_key = p_key
            if p_mode == "minor":
                if p_key in ("A♭", "C♭", "D♭", "G♭"):
                    m_key = p_key[:1]
                m_key += "m"
            elif p_mode == "major":
                if m_key == "F♯":
                    m_key = "G♭"
                if m_key in ("C♭", "C♯", "D♯", "G♯"):
                    m_key = p_key[:1]
            return m_key

        # set_modulated_keys() MAIN
        # =============================================================
        self.SCORES[p_n_name]['modes']["mods"] = dict()
        for mod in ("parallel", "relative", "V_key", "IV_key"):
            m_key = get_key(p_n_name)
            if mod in ("parallel", "relative"):
                if self.SCORES[p_n_name]['modes']['key_mode'] == "major":
                    m_key = adjust_key(m_key, "minor")
                    m_mode = random.choice(list(self.CANON.MINOR.keys()))
                    m_scale = self.CANON.MINOR[m_mode][m_key]
                else:
                    m_mode = "major"
                    m_key = adjust_key(m_key, "major")
                    m_scale = self.CANON.MAJOR[m_key]
            else:
                m_mode = self.SCORES[p_n_name]['modes']['key_mode']
                m_key = adjust_key(m_key, "major")
                if m_mode == "major":
                    m_key = adjust_key(m_key, "major")
                    m_scale = self.CANON.MAJOR[m_key]
                else:
                    m_key = adjust_key(m_key, "minor")
                    m_scale = self.CANON.MINOR[m_mode][m_key]
            self.SCORES[p_n_name]['modes']["mods"][mod] = {
                "key": m_key, "mode": m_mode, "scale": m_scale}

    def set_time_and_tempo(self, p_n_name: str):
        """Select random time signature. Set related items.
        Example:  time_sig = 3/4 so
            pulses per measure = 3, pulse note = quater note = '4'
        For BPM (= tempo), pick random integer between 60 and 180.

        :sets:
        - (class attribute): self.SCORES
        """
        time_sig = random.choice(list(self.CANON.TIMESIGS.keys()))
        beat_note = int(time_sig.split('/')[1])
        beats_per_min = random.randint(60, 180)
        self.SCORES[p_n_name]['beat'] = {
            'note': beat_note,
            'note_name': self.CANON.NOTES[str(beat_note)],
            'per_bar': int(time_sig.split('/')[0]),
            'per_min': beats_per_min,
            'per_sec': round(beats_per_min / 60, 2),
            'time_sig': time_sig,
            'time_sig_name': self.CANON.TIMESIGS[time_sig]}

    def set_node_scores(self):
        """Assign a score to each unique Node.
        Recall that a "Node" = an entity on the graph.

        :sets:
        - (class attribute): self.SCORES
        """
        DBUGCNT_max = 3
        DBUGCNT = 0
        for n_name, n_data in self.NODES.items():
            DBUGCNT += 1
            self.SCORES[n_name] =\
                {"compose":
                    {"bars": self.PALETTE['labels'][n_data['L']]["bars"],
                     "bars_per_phrase":
                        self.PALETTE['labels'][n_data['L']]["bars_per_phrase"],
                     "phrases": self.PALETTE['labels'][n_data['L']]["phrases"],
                     "progress":
                        self.PALETTE['labels'][n_data['L']]["progress"]},
                 'modes':
                    {"key": self.PALETTE['topics'][n_data['T']]["key"],
                     "key_mode": self.PALETTE['topics'][n_data['T']]["mode"],
                     "key_scale":
                         self.PALETTE['topics'][n_data['T']]["scale"]}}
            self.set_time_and_tempo(n_name)
            self.set_modulated_keys(n_name)
            self.set_melodic_pattern(n_name)
            self.set_voices(n_name)
            self.set_rhythm(n_name)
            self.set_pitches(n_name)
            if DBUGCNT >= DBUGCNT_max:
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
            prog_ix = random.choice(list(self.CHORD.PROG.keys()))
            self.PALETTE['labels'][label] =\
                {"progress": self.CHORD.PROG[prog_ix]['chords'],
                 "phrases": self.CHORD.PROG[prog_ix]['phrases'],
                 "bars": len(self.CHORD.PROG[prog_ix]['chords']),
                 "bars_per_phrase":
                     int(len(self.CHORD.PROG[prog_ix]['chords']) /
                         self.CHORD.PROG[prog_ix]['phrases'])}

    def set_topic_modes(self):
        """Assign a mode, key and scale for each unique Node Topic.
        Recall that a "Topic" = a spreadsheet name = a geo-spatial category.

        :sets:
        - (class attribute): self.PALETTE
        """
        self.PALETTE['topics'] = dict()
        topics = set([data['T'] for _, data in self.NODES.items()])
        for topic in topics:
            mode = random.choice(["major", "natural", "harmonic", "melodic"])
            if mode == "major":
                key = random.choice(list(self.CANON.MAJOR.keys()))
                scale = self.CANON.MAJOR[key]
            else:
                key = random.choice(list(self.CANON.MINOR[mode].keys()))
                scale = self.CANON.MINOR[mode][key]
            self.PALETTE['topics'][topic] =\
                {"key": key, "mode": mode, "scale": scale}

    def set_music_data(self):
        """Generate music data from the graph data.

        :sets:
        - (class attribute): self.PALETTE
        - (class attribute): self.SCORES
        """
        print("\n\nRetrieved graph data ===")
        pp(("NODES", self.NODES))

        print("\n\nFixed canonical musical materials ===")
        pp(("CANON.MAJOR", self.CANON.MAJOR))
        pp(("CANON.MINOR", self.CANON.MINOR))
        pp(("CANON.DEGREES", self.CANON.DEGREES))
        pp(("CANON.TIMESIGS", self.CANON.TIMESIGS))
        pp(("CANON.NOTES", self.CANON.NOTES))
        pp(("CHORD.THEME", self.CHORD.THEME))
        pp(("CHORD.PROG", self.CHORD.PROG))

        self.set_topic_modes()
        self.set_label_progressions()
        print("\n\nGeneric thematic assignments ==============")
        pp(("PALETTE", self.PALETTE))

        self.set_node_scores()
        print("\n\nMelodic and harmonic assignments ==============")
        pp(("SCORES", self.SCORES))
