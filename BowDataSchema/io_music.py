#!python
"""
:module:    io_music.py

:author:    GM (genuinemerit @ pm.me)

Use music21 to assign parts, phrases, pitches, notes, durations, etc.
 to nodes, then to generate scores and midi files.

- Generate some musical scores/phrases (see more notes below).
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
        for key, sc in MAJOR.items():
            MINOR["natural"][key] =\
                [sc[5], sc[6], sc[0], sc[1], sc[2], sc[3], sc[4]]
            MINOR["harmonic"][key] = copy(MINOR["natural"][key])
            MINOR["harmonic"][key][6] = MINOR["harmonic"][key][6][:-1]\
                if MINOR["harmonic"][key][6][-1:] == '♭'\
                else MINOR["harmonic"][key][6] + '♯'
            MINOR["melodic"][key] = copy(MINOR["natural"][key])
            MINOR["melodic"][key][5] = MINOR["melodic"][key][5][:-1]\
                if MINOR["melodic"][key][5][-1:] == '♭'\
                else MINOR["melodic"][key][5] + '♯'

        DEGREES = dict()
        DEGREES['major'] = ['I', 'IV', 'V']
        DEGREES['minor'] = ['ii', 'iii', 'vi']
        DEGREES['diminished'] = ['VII°']
        DEGREES['arabic'] = ['1', '2', '3', '4', '5', '6', '7']
        DEGREES['roman'] = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'VII°']

        NOTES = dict()
        NOTES[1] = 'whole'
        NOTES[2] = 'half'
        NOTES[4] = 'quarter'
        NOTES[8] = 'eighth'
        NOTES[16] = 'sixteenth'
        NOTES[32] = 'thirty-second'
        NOTES[64] = 'sixty-fourth'

        TIMESIGS = dict()
        TIMESIGS["2/4"] = "March"
        TIMESIGS["3/4"] = "Waltz"
        TIMESIGS["4/4"] = "Common"

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


    def get_scale(self, p_mode, p_key):
        for m in self.CANON["modes"][p_mode]:
            if m[0] == p_key:
                return(m[1])

    def set_relative_key(self, node_nm: str):
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
        music = self.MUSIC['scores'][node_nm]
        mode = list(music['key_scales']['scale'].keys())[0]
        if "major" in mode:
            minors =\
                [ky for ky in self.CANON['modes'].keys() if "minor" in ky]
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
        self.MUSIC['scores'][node_nm]['key_scales']['signature'] = keysig
        self.MUSIC['scores'][node_nm]['key_scales']['relative'] =\
            {(rel_ky, rel_mode): self.get_scale(rel_mode, rel_ky)}

    def set_neighbor_keys(self, node_nm: str):
        """Set keys that are a Fifth from main key for score.
        For selected mode, pick next key and previous key.
        """
        music = self.MUSIC['scores'][node_nm]
        scale = list(music['key_scales']['scale'].keys())[0]
        mode = self.CANON['modes'][scale[1]]
        mix = mode.index((scale[0], (music['key_scales']['scale'][scale])))
        n1 = mix + 1 if mix < len(mode) - 1 else 0
        n2 = mix - 1 if mix > 0 else len(mode) - 1
        n1_ky = mode[n1][0]
        n2_ky = mode[n2][0]
        n1_scale = mode[n1][1]
        n2_scale = mode[n2][1]
        self.MUSIC['scores'][node_nm]['key_scales']['mod_right'] =\
            {(n1_ky, scale[1]): n1_scale}
        self.MUSIC['scores'][node_nm]['key_scales']['mod_left'] =\
            {(n2_ky, scale[1]): n2_scale}

    def set_pattern(self, node_nm: str):
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

        music = self.MUSIC['scores'][node_nm]
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
        self.MUSIC['scores'][node_nm]['chords']['pattern'] = pat_list

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
        cord = list()
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
        try_again: bool = True
        tries: int = 0
        while try_again is True:
            total_beat: float = 0.0
            break_me: int = 0
            beat_notes: list = list()
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
            - Which we get from self.CANON['modes']:
              - If chord is not in 'major' mode, then add an 'm' to chord
                and look randomly in one of the 3 minor modes.
            - Based on range, expand the notes available for the chord,
              notating what octave each note is in.
            - We are not yet associating a pitch with a beat, just
              assembling what range of pitches to work with in the beat.

            :returns: (list) of 1..n pitch tuples, w/ pitches assigned to
                octaves by number, like E3, F♯3 and so on. This identifies
                the range of pitches avaialbe to choose from for the beat.
            """
            chord = "G♭" if chord == "F♯" else chord
            beat_scale = list()
            pitches = list()
            modes: dict = self.CANON['modes']
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

    def set_beat_pitches(self,
                         m: int,
                         n: int,
                         notes: list,
                         pattern: str,
                         prev_pitch: str):
        """Set specific pitches for each beat.
        Assign specific pitches from the selected set,
        using rules for pattern asc, desc, steady, tonic.
        Choose single pitches, chords, or both.
        If a chord, choose seven, regular triad, or inverted.
        If inverted, 1st, 2nd or 3rd (if it is a 7 chord)
        For ascending, step up melodically (single notes)
        or harmonically (repeating the chord or variations
        of it) and only use pitches > previous pitch.
        If descending, step down, using lower notes, chords.
        If steady, step up and down by 2nds or 3rd only, or
        repeat notes at same pitch. If tonic, do a steady
        pattern featuring the degree 1 pitch in octave 4.

        Only require octave 4 if m is 0 (first measure)
        b = beat index, which is actually the notes within a beat.
        m (measure) can have several beats (n) in it.
         for example, if time sig is 3/4, then there will be 3 n's.
        Within each 'n' (beat), there is a rhythm, which may
         consist of one or several notes (or rests). For each
         'stroke' of a rythm, there is a pitch.

        Might help to review here from the top, making sure that
        terminology is clear and clearly explained. Some debugging
        that does not use the entire set of places data might
        help too.
        """
        print(f"\npattern: {pattern}")
        print(f"prev_pitch: {prev_pitch}")
        beat_cnt: int = len(notes[1])
        print(f"beat_cnt: {beat_cnt}")
        PALETTE: dict = dict()
        score: list = list()
        for r in notes[2]:
            for degree, note in enumerate(r):
                PALETTE[note] = degree + 1
        pp(("pitch PALETTE", PALETTE))
        for b in range(0, beat_cnt):
            print(f"\nm, n, b: {m}, {n}, {b}")
            if pattern == "tonic" and b == 0:
                score.append([(p, d) for p, d in PALETTE.items()
                             if d == 1 and p[-1:] == "4"][0])
                prev_pitch = score[b]
            else:
                note_or_chord = "note"\
                    if random.randint(0, 100) < 80 else "chord"
                print(f"Next a : {note_or_chord}")
                score.append(("?", 0))
        pp(("score", score))
        return score

    def set_notes(self,
                  m: int,
                  chords: dict,
                  rhythm: dict,
                  bar_keys: dict,
                  pattern: list,
                  tonic_root: str):
        """Set notes _for each beat_ within a measure.

        Possible denominators and their meaning / what gets the beat:
        1 - whole note
        2 - half note
        4 - quarter note
        8 - eighth note
        16 - sixteenth note
        32 - thirty-second note
        64 - sixty-fourth note

        #
        # 7. Choose whether to have more than one voice.
        #   If so, choose the number of voices and quality
        #   of each:
        # 7.a.  (More) simple harmonics.
        # 7.b.  Counterpoint: parallel, round, fugue or other.
        # 7.c.  Where to use 3rds and 6ths.
        # 7.d.  Where/when to use 5th and octaves.
        # 7.e.  Whether to use 4ths, 2nds or 7th at all.
        # 7.f.  What species of counterpoint notes to use:
        #       1:1, 1:2, ... 1:4, or a combination of these.
        # 7.g.  Follow skips by skips in the opposite direction.
        # 7.h.  Identify the high point of the counterpoint.
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
        In some cases, notes is coming back empty = {} in the final MUSIC
        dict. Not sure why. Suspect something with the measures index/count
        in set_bars()?
        Review/fix that later rather than stopping here.
        Not seeing any cases where this method returns an empty dict.
        m = measure, indexed starting at zero
        n = beat within a measure, indexed starting at one (why?)
            used to index a variable called "notes", a list where each
            item indexed by n is a list containing:
            1 - the name of a scale.
            2 - a list of tuples designating rhythms within the beat
            3 - a list of tuples designating range of pitches to choose from
        """
        notes = {}
        prev_pitch: str = ""
        for n in range(1, rhythm['measure'] + 1):
            notes[n] = self.set_beat_chord(m, n, chords, rhythm, bar_keys,
                                           pattern, tonic_root)
            notes[n].append(self.set_beat_rhythm(rhythm))
            notes[n].append(self.set_pitch_range(notes[n][0]))
            print(f"m, n: {m}, {n}")
            pp(("notes[n]   ", notes[n]))
            if n > 1:
                pp(("notes[n-1]   ", notes[n-1]))
            prev_pitch = "" if m == 0 and n == 1 else notes[n - 1][3][-1:]
            notes[n].append(
                self.set_beat_pitches(
                    m, n, notes[n], str(pattern), prev_pitch))

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

    def set_chords_and_notes(self, node_nm: str):
        """Associate each degree of chord progression with notes.
        """
        key_scales = {m: s for m, s in
                      self.MUSIC['scores'][node_nm]['key_scales'].items()
                      if m != 'signature'}
        tonic_key = list(key_scales["scale"].keys())[0]

        self.MUSIC['scores'][node_nm]['notes'] = dict()
        for v in range(1, random.randint(1, 2)):
            clef = "treble" if v == 1 else\
                random.choice(["bass", "treble"])
            self.MUSIC['scores'][node_nm]['notes'][clef] = self.set_phrases(
                chords=self.MUSIC['scores'][node_nm]['chords'],
                key_scales=key_scales,
                tonic_root=key_scales["scale"][tonic_key][0],
                rhythm=self.MUSIC['scores'][node_nm]['rhythm'])

    def set_keys_patterns_chords(self, node_nm: str):
        """Assign notes to each bar according to the time signature.

        Assign notes, within the selected chord, to each bar, using
        the guard-rails defined by the patterns, and with durations
        appropriate to the time signature.

        For now, just create one part with one voice.
        """
        self.set_relative_key(node_nm)
        self.set_neighbor_keys(node_nm)
        self.set_pattern(node_nm)
        self.set_chords_and_notes(node_nm)

    def set_beat_and_tempo(self, p_node_nm: str):
        """Select random time signature. For now: 2/4, 3/4, 4/4
        Example:  time_sig = 3/4 so
            pulses per measure = 3, pulse note = quater note = '4'
        For BPM (= tempo), pick random integer between 60 and 180.

        :sets:
        - (class attribute): self.MUSIC['scores'][<Node ID>]['rhythm'][...]
        """
        tsig = list(self.TIMESIGS.values())[random.randint(
            0, len(self.TIMESIGS.values()) - 1)]
        pulse_per_m = tsig.split('/')[0]
        pulse_note = tsig.split('/')[1]
        bpm = random.randint(60, 180)
        self.MUSIC['scores'][p_node_nm]['rhythm']['time_sig'] = tsig
        self.MUSIC['scores'][p_node_nm]['rhythm']['measure'] = int(pulse_per_m)
        self.MUSIC['scores'][p_node_nm]['rhythm']['beat'] = int(pulse_note)
        self.MUSIC['scores'][p_node_nm]['rhythm']['bpm'] = int(bpm)
        self.MUSIC['scores'][p_node_nm]['rhythm']['description'] =\
            (f"{pulse_per_m} beats per measure" +
             f"\n{self.BEATS[int(pulse_note)]} note gets the beat" +
             f"\n{bpm} beat/minute = " +
             f"{round((bpm / 60), 2)} beat/second")

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
        # elabels = set([data['L'] for _, data in self.EDGES.items()])
        # for label in nlabels.union(elabels):
        for label in nlabels:
            chord = self.CHORDS[random.randint(0, len(self.CHORDS) - 1)]
            bars = []
            for phrase in chord:
                bars.extend(list(phrase))
            self.MUSIC['chords'][label] = {'phrases': len(chord),
                                           'bars_in_phrase': len(chord[0]),
                                           'bars': bars}

    def set_topic_modes(self):
        """Assign a mode, key and scale for each Node Topic.

        :sets:
        - (class attribute): self.MUSIC['key_scales']
        """
        topics = set([data['T'] for _, data in self.NODES.items()])
        for topic in topics:
            self.PALETTE[topic] = dict()
            mode = random.choice(["major", "natural", "harmonic", "melodic"])
            if mode == "major":
                key = random.choice(list(self.CANON.MAJOR.keys()))
                scale = self.CANON.MAJOR[key]
            else:
                key = random.choice(list(self.CANON.MINOR[mode].keys()))
                scale = self.CANON.MINOR[mode][key]
            self.PALETTE[topic]['mode'] = [key, mode, scale]

    def set_music_data(self):
        """Generate music data from the graph data.
        Try to set it up to be flexible, based on parsing
        the graph data, not hard-coding associations.
        """
        print("\n\nRetrieved graph data ===")
        pp((self.NODES))

        print("\n\nCanonical, fixed Musical materials ===")
        pp((self.CANON.MAJOR))
        pp((self.CANON.MINOR))
        pp((self.CANON.DEGREES))
        pp((self.CANON.NOTES))
        pp((self.CHORD.THEME))
        pp((self.CHORD.PROG))

        self.set_topic_modes()
        print("\n\nGeneric/Thematic assignments ==============")
        pp((self.PALETTE))
        """
        self.set_chords_for_labels()
        DEBUG_CNT = 3
        print("\n\nMUSIC")
        pp((self.MUSIC))
        self.MUSIC['scores'] = dict()
        cnt = 0
        for node_nm, ndat in self.NODES.items():
            cnt += 1
            self.MUSIC['scores'][node_nm] = dict()
            for m in ('chords', 'key_scales', 'notes', 'rhythm'):
                self.MUSIC['scores'][node_nm][m] = dict()
            self.MUSIC['scores'][node_nm]['key_scales']['scale'] =\
                self.MUSIC['scales'][ndat['T']]
            self.MUSIC['scores'][node_nm]['chords'] =\
                self.MUSIC['chords'][ndat['L']]
            self.set_beat_and_tempo(node_nm)
            # self.set_keys_patterns_chords(node_nm)
            if cnt >= DEBUG_CNT:
                break

        print("\n\nMUSIC['scores']")
        pp((self.MUSIC['scores']))
        """
