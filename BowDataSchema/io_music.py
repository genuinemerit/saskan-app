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

        How to:
        - Load and create a fresh SCORES pickle from the NODES pickle:
            self.set_music_data()
        - Create a fresh MIDI-type file/object from the SCORES pickle
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
        self.SCORES = dict()

    @dataclass
    class CANON:
        """Class for defining canonical components of musical language.

        The class uses music21 convention of "#" for sharp (#) and "-"
        for flat (-). Double-flat (--) is --. Double-sharp (##) is ##.
        A m21 method displays notes using proper unicode characters for
        accidentals and so forth.

        Regarding tuplets...
        triplet = m21.duration.Tuplet(3, 2)
          means, put 3 notes into a tuple with duration of 2 eighths
        Example of quintuplet lasting as long as 2 eighths:
        quintuplet = m21.duration.Tuplet(5, 2)

        See these references for more information:
        web.mit.edu/music21/doc/
        web.mit.edu/music21/doc/genindex.html
        web.mit.edu/music21/doc/py-modindex.html

        The "genindex" link is the best detailed technical reference.
        """
        NOTES = dict()
        for nty in ('full', 'rest', 'dotted', 'tuplet'):
            NOTES[nty] = dict()
        NOTES['full'] = {'whole': 4.0, 'half': 2.0, 'quarter': 1.0,
                         'eighth': 0.5, '16th': 0.25, '32nd': 0.125,
                         '64th': 0.0625}
        for n, d in NOTES['full'].items():
            dur = copy(d)
            NOTES['full'][n] = m21.duration.Duration(dur)
            NOTES['rest'][n] = m21.note.Rest(quarterLength=dur)
            NOTES['dotted'][n] = m21.duration.Duration(dur + (dur / 2))
        NOTES['tuplet'] = {
            'triplet': m21.duration.Tuplet(3, 2),
            'quintuplet': m21.duration.Tuplet(5, 2)}

        SCALES = dict()
        for k in ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#',
                  'F', 'B-', 'E-', 'A-', 'D-', 'G-', 'C-', 'F-']:
            SCALES[k] = dict() if k not in SCALES.keys() else SCALES[k]
            SCALES[k]['major'] = m21.scale.MajorScale(k)
            SCALES[k]['parallel']: m21.scale.MinorScale(k)
            rk = m21.key.Key(k).relative.tonic.name
            SCALES[rk] = dict() if rk not in SCALES.keys() else SCALES[rk]
            SCALES[rk]['natural'] = m21.scale.MinorScale(rk)
            SCALES[rk]['harmonic'] = m21.scale.HarmonicMinorScale(rk)
            SCALES[rk]['melodic'] = m21.scale.MelodicMinorScale(rk)

        KEYSIGS = dict()
        for k in SCALES.keys():
            KEYSIGS[k] = dict()
            for mode, m_obj in SCALES[k].items():
                a_cnt = 0
                for p in m_obj.pitches:
                    a_cnt = a_cnt + 1 if '#' in p.name\
                        else a_cnt - 1 if '-' in p.name else a_cnt
                KEYSIGS[k][mode] = m21.key.KeySignature(a_cnt)

        TIMESIGS = dict()
        for sig in ('cut', '3/4', '6/8', 'common'):
            TIMESIGS[sig] = m21.meter.TimeSignature(sig)

    @dataclass
    class CHORD:
        """Class for deriving chord progressions.

        What else can I do in the way of motives, chord progressions,
        as well as maybe articulations, dynamics, timbre and maybe even
        counterpoint? I know I can't get too carried away, need to ierate
        on simpler prototypes. Still...
        - Something not enirely stochastic. Define some kind of pattern
          for repetition, for reaching a climax, for calm resolution or
          turnaround.
        - I like the chord progression themes and progressions OK.
          Let's keep that but maybe add additional deterministic stuff
          on motives, cadences, ...?
        """
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
        rhythm_notes = self.SCORES[nnm]["notes"][1]["rhythm"][p_barx]
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
        self.SCORES[nnm]["notes"][1]["pitch"][p_barx] = pitches

    def set_pitches(self, nnm: str):
        """For each measure, set the pitch for each rhythm-note."""
        def get_sevens(p_note: str,
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

        # set_pitches() MAIN
        # ===================================================
        self.SCORES[nnm]["notes"][1]['pitch'] = dict()
        print("\n\n")
        for barx, pat in enumerate(
                self.SCORES[nnm]["compose"]["pattern"]):
            self.SCORES[nnm]["notes"][1]['pitch'][barx] = list()
            deg = {"roman": self.SCORES[nnm]["compose"]["progress"][barx]}
            deg["x"] = self.CANON.DEGREES['roman'].index(deg["roman"])
            mods = self.SCORES[nnm]["modes"]["mods"]
            sca = {"main": self.SCORES[nnm]["modes"]["key_scale"],
                   "IV": mods['IV_key']['scale'],
                   "V": mods['V_key']['scale'],
                   "parl": mods['parallel']['scale'],
                   "rel": mods['relative']['scale']}
            chord = {"main": get_sevens(
                        sca["main"][deg["x"]],
                        self.SCORES[nnm]["modes"]["key_scale"]),
                     "IV": get_sevens(sca["IV"][deg["x"]],
                                      mods['IV_key']['scale']),
                     "V": get_sevens(sca["V"][deg["x"]],
                                     mods['V_key']['scale']),
                     "parl": get_sevens(sca["parl"][deg["x"]],
                                        mods['parallel']['scale']),
                     "rel": get_sevens(sca["rel"][deg["x"]],
                                       mods['relative']['scale'])}
            # print("\n====")
            # pp((("barx", barx),
            #     ("pat", pat),
            #     ("deg", deg),
            #     ("scale", sca),
            #     ("chord", chord)))
            self.set_bar_pitches(nnm, barx, deg, pat, sca, chord)

    def set_rhythm(self, nnm: str):
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
        def set_beat_note(nnm: str,
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
                self.SCORES[nnm]["notes"][1]['rhythm'][m].append((note))
            return beats

        # set_rhythm() MAIN
        # on first prototype, just doing one voice
        # =============================================================
        self.SCORES[nnm]["notes"][1]['rhythm'] = dict()
        for m, _ in enumerate(self.SCORES[nnm]["compose"]["pattern"]):
            beats = 0
            b_per_bar = self.SCORES[nnm]['beat']['per_bar']
            n_cnt = len(list(self.CANON.NOTES.keys()))
            n_earlier = int(round(n_cnt * 0.5))
            tries = 0
            do_overs = 0
            while do_overs < 10:
                self.SCORES[nnm]["notes"][1]['rhythm'][m] = list()
                while beats < b_per_bar:
                    beats = set_beat_note(
                        nnm, beats, b_per_bar, n_earlier)
                    tries += 1
                    if tries > 100:
                        print(f"tries exceeded 100 for {nnm}")
                        break
                do_overs += 1
                if beats == self.SCORES[nnm]['beat']['per_bar']:
                    break
                if do_overs >= 10:
                    # maybe save each try and if we have to quit,
                    # then pick the one with beats closest to 1.0.
                    print(f"do-overs exceeded 10 for {nnm}")

    def set_voices(self, nnm: str):
        """Determine how many voices to use and what clef they are in.
        Assume all voices are in the same key.
        """
        self.SCORES[nnm]["notes"] = dict()
        voice_cnt = random.randint(1, self.CANON.MAX_VOICES)
        for v in range(voice_cnt):
            clef = "𝄞" if (v == 0) or (random.randint(1, 101) < 80) else "𝄢"
            self.SCORES[nnm]["notes"][v + 1] = {"clef": clef}

    def set_melodic_pattern(self, nnm: str):
        """Set melodic pattern (asc, desc, steady) for each bar.
        Random mix but including rough rules like:
        - More ordered patterns (asc, desc) for first 2/3rds of bars
        - More surprise pattern (bigger intervals) for last 1/3 of bars
        - Include taste of the tonic or relative tonic in first and last bars
        - Include taste of a fifth or a minor third at end of phrases
           that are not the last bar in the score

        @DEV:
        - Pick it up here.
        - This is maybe where I can both do something more interesting.
        - Maybe condense some code too.
        - Consider how I might assgin a motif (or more than one) to
          each phrase, then play them out over its bars. Starting/ending
          on tonic or relative tonic may or may not be necessary since I
          already have an indication of chords / notes to use in the chord
          progression.
        - Consider playing around with dynamics, accents and timbres too.
        - ascending, descending, or steady are too simple. Ditch them.
        - Consider using:
            - Relatively simpler patterns in the first and last bars.
            - Turnaround kind of patterns in the penultimate bar.
            - Building up to higher notes, most complexity at about
              2/3rd point of the score. Like maybe pick a max pitch to
              aim for or something like that.
            - Define complexity as a function of number of notes,
              including harmonics vs. sparse melody, space of
              intervals, type of intervals.
            - Some simple accents and dynamics.
        - I think it will probably work better to have these kinds of
          patterns defined as rules, more or less, in the CANON. Then
          here we are picking which ones to use, how to tweak them. I'd
          rather not just build up another pile of metadata; would prefer
          to get right to assigning notes (with pitch and duration) to bars.
        """
        dir_tracker = {"asc": 0, "desc": 0, "steady": 0}
        b_cnt = self.SCORES[nnm]["compose"]["bars"]
        bpp = self.SCORES[nnm]["compose"]["bars_per_phrase"]
        pattern = list()
        for m in range(b_cnt):
            direction = random.choice(list(dir_tracker.keys()))
            prog = self.SCORES[nnm]["compose"]["progress"][m]
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
        self.SCORES[nnm]["compose"]["pattern"] = pattern

    def set_modulated_keys(self, nnm: str):
        """Set keys, scales to use for modulations:
        - Parallel key - shares same tonic as main key
        - Relative key - shares same notes as main key
        - V key - a fifth "up", "to the "right" on Circle of 5ths
        - IV key - a fourth "down", "to the "left" on Circle of 5ths

        Not sure this is really helpful? Modulation is a complex idea.
        Might module for a measure, or just for one out-of-key note.
        I am unlikely to come up with a deterministic way to do this
        any time soon. Creating a ton of metadata seems like overkill.
        I expect there are simpler music21 ways to do this, as well as
        to change registers.

        I already have the parallel and relative keys accessible.
        Grabbing the IVth or Vth should be easier now too. Don't
        really need to store them again at the socre level.

        Choose minor mode randomly if main key is major.
        Set the key signature to match the major key.
        """
        def get_key(nnm):
            """And set key signature to match the major key."""
            if mod == "parallel":
                m_key = self.SCORES[nnm]['modes']['key_scale'][0]
            elif mod == "relative":
                if self.SCORES[nnm]['modes']['key_mode'] == "major":
                    m_key = self.SCORES[nnm]['modes']['key_scale'][5]
                    self.SCORES[nnm]['modes']["key_sig"] =\
                        self.SCORES[nnm]['modes']['key']
                else:
                    m_key = self.SCORES[nnm]['modes']['key_scale'][2]
                    self.SCORES[nnm]['modes']["key_sig"] = m_key
            elif mod == "V_key":
                m_key = self.SCORES[nnm]['modes']['key_scale'][4]
            elif mod == "IV_key":
                m_key = self.SCORES[nnm]['modes']['key_scale'][3]
            return m_key

        def adjust_key(p_key, p_mode):
            m_key = p_key
            if p_mode == "minor":
                if p_key in ("A-", "C-", "D-", "G-"):
                    m_key = p_key[:1]
                m_key += "m"
            elif p_mode == "major":
                if m_key == "F#":
                    m_key = "G-"
                if m_key in ("C-", "C#", "D#", "G#"):
                    m_key = p_key[:1]
            return m_key

        # set_modulated_keys() MAIN
        # =============================================================
        self.SCORES[nnm]['modes']["mods"] = dict()
        for mod in ("parallel", "relative", "V_key", "IV_key"):
            m_key = get_key(nnm)
            if mod in ("parallel", "relative"):
                if self.SCORES[nnm]['modes']['key_mode'] == "major":
                    m_key = adjust_key(m_key, "minor")
                    m_mode = random.choice(list(self.CANON.MINOR.keys()))
                    m_scale = self.CANON.MINOR[m_mode][m_key]
                else:
                    m_mode = "major"
                    m_key = adjust_key(m_key, "major")
                    m_scale = self.CANON.MAJOR[m_key]
            else:
                m_mode = self.SCORES[nnm]['modes']['key_mode']
                m_key = adjust_key(m_key, "major")
                if m_mode == "major":
                    m_key = adjust_key(m_key, "major")
                    m_scale = self.CANON.MAJOR[m_key]
                else:
                    m_key = adjust_key(m_key, "minor")
                    m_scale = self.CANON.MINOR[m_mode][m_key]
            self.SCORES[nnm]['modes']["mods"][mod] = {
                "key": m_key, "mode": m_mode, "scale": m_scale}

    def set_time_and_tempo(self, nnm: str):
        """Select random time signature. Set related items.
        Example:  time_sig = 3/4 so
            pulses per measure = 3, pulse note = quater note = '4'
        For BPM (= tempo), pick random integer between 60 and 180.

        :sets:
        - (class attribute): self.SCORES
        """
        ts = random.choice(list(self.CANON.TIMESIGS.keys()))
        self.SCORES[nnm]['beat'] = {
            'time_sig': self.CANON.TIMESIGS[ts],
            'cnt': self.CANON.TIMESIGS[ts].beatCount,
            'bar_dur': self.CANON.TIMESIGS[ts].barDuration,
            'div': self.CANON.TIMESIGS[ts].beatDivisionCount,
            'dur': self.CANON.TIMESIGS[ts].beatDuration,
            'metro': m21.tempo.MetronomeMark(random.randint(60, 180))}

    def set_node_scores(self):
        """Assign a score to each unique Node.
        Recall that a "Node" = an entity on the graph.

        :sets:
        - (class attribute): self.SCORES
        """
        dbug_max = len(self.NODES.keys())
        # dbug_max = 3
        dbug = 0
        for nnm, nd in self.NODES.items():
            dbug += 1
            label = self.PALETTE['labels'][nd['L']]
            topic = self.PALETTE['topics'][nd['T']]
            self.SCORES[nnm] = {
                "bar_cnt": label["bar_cnt"], "phr_cnt": label["phr_cnt"],
                "chords": label["chords"],
                "keysig": topic["keysig"], "scale": topic["scale"]}
            self.set_time_and_tempo(nnm)
            """
            # self.set_modulated_keys(nnm) <-- not needed?
            self.set_melodic_pattern(nnm)
            self.set_voices(nnm)
            self.set_rhythm(nnm)
            self.set_pitches(nnm)
            """
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
            p_x = random.choice(list(self.CHORD.PROG.keys()))
            self.PALETTE['labels'][label] =\
                {"chords": self.CHORD.PROG[p_x]['chords'],
                 "phr_cnt": self.CHORD.PROG[p_x]['phrases'],
                 "bar_cnt": len(self.CHORD.PROG[p_x]['chords'])}

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
            k = random.choice(list(self.CANON.SCALES.keys()))
            if random.randint(100, 100) < 67:
                m = "major"
            else:
                got_it = False
                while not got_it:
                    m = random.choice(["natural", "harmonic", "melodic"])
                    if m in self.CANON.SCALES[k]:
                        got_it = True
                    else:
                        k = random.choice(list(self.CANON.SCALES.keys()))
            self.PALETTE['topics'][topic] =\
                {"keysig": self.CANON.KEYSIGS[k][m],
                 "scale": self.CANON.SCALES[k][m]}

    def set_music_data(self):
        """Generate music data from the graph data.

        :sets:
        - (class attribute): self.PALETTE
        - (class attribute): self.SCORES
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

        print("\n\nGeneric thematic assignments ==============")
        pp(("PALETTE", self.PALETTE))
        """
        self.set_topic_modes()
        self.set_label_progressions()
        self.set_node_scores()

        print("\n\nMelodic and harmonic assignments ==============")
        pp(("SCORES", self.SCORES))
        """

        # self.file_nm
        with open(self.file_nm + "_scores.pickle", 'wb') as obj_file:
            pickle.dump(self.SCORES, obj_file)
        print(f"Music SCORES object pickled to: {self.file_nm}" +
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
            self.SCORES = pickle.load(f)
        m21.environment.set('midiPath', '/usr/bin/timidity')
        print("\n\nMelodic and harmonic assignments ==============")
        dbug_max = 2
        dbug = 0
        book = m21.stream.Stream()
        for n_name, n_data in self.SCORES.items():
            dbug += 1
            score = self.parse_score(n_name, n_data["modes"]["key_sig"],
                                     n_data["beat"], n_data["notes"][1])
            book.append(score)
            if dbug >= dbug_max:
                break
        book.show()
