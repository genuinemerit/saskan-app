#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Classes and functions for defining a character's personality

Some notes:
* For information on the Myers-Briggs personality scores,
  see: http://www.personalitypathways.com/type_inventory.html
"""
import random
import sys
# Local packages
sys.path.append('../../web/app')
from main import utils

# FUNCTIONS

# CLASS
# =========================

class Personality(object):
    '''
    Methods and data for creating personality characteristics.
    Global constants
    '''
    _TRAITS = {'I':'introvert',
               'E':'extrovert',
               'S':'sensitive',
               'N':'intuitive',
               'T':'thinking',
               'F':'feeling',
               'J':'judging',
               'P':'perceiving'}
    _TYPES = {'ISTJ':
             {'personality':
                  'Quiet, serious, thorough, dependable',
              'behavior':
                  'Practical, realistic, steady, makes decisions logically',
              'tone':
                  'Orderly, organized, values tradition and loyalty'},
             'ISFJ':
             {'personality':
                  'Quiet, friendly, responsible, conscientious',
              'behavior':
                  'Committed, steady, thorough, painstaking, accurate',
              'tone':
                  'Orderly, harmonious'},
             'INFJ':
             {'personality':
                 'Values meaning, connections in ideas, relationships, things',
             'behavior':
                 'Insightful, wants to know motivations, committed to values',
             'tone':
                 'Organized, decisive'},
             'INTJ':
             {'personality':
                 'Original, great drive for ideas and achievements',
              'behavior':
                  'Sees patterns, long-range perspective, organized, committed',
              'tone':
                  'Skeptical, independent, high standards'},
             'ISTP':
             {'personality':
                 'Tolerant, flexible, observant, finds workable solutions',
              'behavior':
                  'Analytical, digs through data to isolate core of problems',
              'tone':
                  'Factual, logical, values efficiency'},
             'ISFP':
             {'personality':
                 'Quiet, friendly, sensitive, kind',
              'behavior':
                  'Works independently, loyal to people who are close-by',
              'tone':
                  'Conflict-averse, agreeable'},
             'INFP':
             {'personality':
                 'Idealistic, loyal to values and people',
              'behavior':
                  'Curious, sees possibilities,new ideas and potential',
              'tone':
                  'Adaptable, flexible, accepting'},
             'INTP':
             {'personality':
                 'Seeks to develop logical explanations',
              'behavior':
                  'Theoretical, abstract, interested in ideas, adaptable',
               'tone':
                   'Skeptical, critical, analytical'},
             'ESTP':
             {'personality':
                 'Flexible, tolerant, acts pragmatically for quick results',
              'behavior':
                  'Bored by theory, action oriented, spontaneous',
              'tone':
                  'Enjoys material comforts, learns by doing'},
             'ESFP':
             {'personality':
                 'Outgoing, friendly, accepting',
              'behavior':
                  'Collaborative, common sense, realistic, makes work fun',
              'tone':
                  'Flexible, spontaneous, learns by doing with groups'},
             'ENFP':
             {'personality':
                 'Warm, enthusiastic, imaginative',
              'behavior':
                  'Makes connections, confident, needs and gives affirmations',
              'tone':
                  'Spontaenous, flexible, improvisational, verbally fluent'},
             'ENTP':
             {'personality':
                 'Quick, ingenious, stimulating, alert, outspoken',
              'behavior':
                  'Resourceful, likes challenges and strategic analysis',
              'tone':
                  'Bored by routine, unpredictable, many interests'},
             'ESTJ':
             {'personality':
                 'Practical, realistic, matter-of-fact',
              'behavior':
                  'Organizer, gets efficient results, good at routine details',
              'tone':
                  'Logical, systematic, forceful'},
             'ESFJ':
             {'personality':
                 'Warmhearted, conscientious, cooperative',
              'behavior':
                  'Harmonizer, determined, loyal, good at small details',
              'tone':
                  'Provider, contributor, wants to be appreciated'},
             'ENFJ':
             {'personality':
                 'Warm, empathetic, responsive, responsible',
              'behavior':
                  'Empathetic, mindful of others, encourages others',
              'tone':
                  'Sociable, facilitator, inspirational'},
             'ENTJ':
             {'personality':
                 'Frank, decisive, quick to assume leadership',
              'behavior':
                  'Logical, efficient, devises comprehensive solutions',
              'tone':
                  'Well-informed, knowledgable, good presenter of ideas'}
            }

    def __init__(self):
        '''
        Instantiate Personality object.
        '''
        self.person_traits = {}
        self.person_types = {}
        self.myers_briggs = ''
        self.brief_desc = ''
        self.long_desc = {}

    def reset_personality(self):
        '''
        (Re-)Initialize Personality object.
        '''
        self.person_traits = Personality._TRAITS
        self.person_types = Personality._TYPES
        self.myers_briggs = ''
        self.brief_desc = ''
        self.long_desc = {}

    def set_personality(self, intui_in=0, iq_in=0):
        '''
        @param intui_in The character's intuition score (range: 3-24)
        @param iq_in The character's IQ score (range: 40-150)
        Compute a Myers-Briggs personality matrix (MBTI).
        @return a 3-tuple containing: myers_briggs score, brief description,
            elaborated description in a dict object
        '''
        self.reset_personality()
        if not intui_in in range(3, 24):
            intui_in = random.randint(3, 34)
        if not iq_in in range(50, 140):
            iq_in = random.randint(50, 140)

        # Extroverted / Introverted
        if utils.random_100() < 51:
            self.myers_briggs += 'E'
        else:
            self.myers_briggs += 'I'

        # Sensing / Intuitive: bump up based on Intuition ability
        if (utils.random_100() + intui_in) < 51:
            self.myers_briggs += 'S'
        else:
            self.myers_briggs += 'N'

        # Thinking / Feeling: bump down based on IQ ability
        if (utils.random_100() - int(iq_in / 10)) < 51:
            self.myers_briggs += 'T'
        else:
            self.myers_briggs += 'F'

        # Judging / Perceiving
        if utils.random_100() < 51:
            self.myers_briggs += 'J'
        else:
            self.myers_briggs += 'P'

        # Consider using a formatting function for this
        self.brief_desc = self.person_traits[self.myers_briggs[0:1]] \
                       + ', ' + self.person_traits[self.myers_briggs[1:2]] \
                       + ', ' + self.person_traits[self.myers_briggs[2:3]] \
                       + ', ' + self.person_traits[self.myers_briggs[3:]]
        self.long_desc = self.person_types[self.myers_briggs]

        return (self.myers_briggs, self.brief_desc, self.long_desc)

def rpt_personality(p_obj):
    '''
    Nicely-formatted report on the personality
    '''
    rpt = "\n\nPersonality"
    rpt += "\n-------------------------"
    rpt += "\n General Personality: " + p_obj.long_desc['personality']
    rpt += "\n       Personal Tone: " + p_obj.long_desc['tone']
    rpt += "\n Behavioral Tendency: " + p_obj.long_desc['behavior']
    return rpt

def test_me():
    '''
    Simple unit tests for this Class.
    '''
    # Personality
    p_obj = Personality()
    print p_obj.set_personality()
    # print p_obj.__dict__
    print rpt_personality(p_obj)

if __name__ == '__main__':
    test_me()
