#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file contains classes and functions for creating player and
non-player characters.  It is loosely based on an old Gamma World
structure.  This is for experimental purposes.  Eventually may want
to move this code into the /web application or turn it into some kind
of service.

Some notes:
* For information on the Myers-Briggs personality scores,
  see: http://www.personalitypathways.com/type_inventory.html

On the always-learning-more-about-Python front, note two very cool things
 in this file:

1) Use of pycurl to do CURL type harvesting of data from HTTP streams.
2) Use of BeautifulSoup to manage parsing of HTML data.  It also works on XML.
Both are exeedingly cool.
3) Not quite so exciting, but a learning event: can use range to iterate
   through a decremented series simply by using a -1 (or other negative)
   step value
"""
import logging
import numpy as np
import random
import sys
# Local packages
sys.path.append('./')
import family
import gametime
import lifeform
import names
import orgs
import personality
sys.path.append('../../web/app')
from main import utils

# FUNCTIONS

# CLASS
# =========================

class Character:
    '''
    Methods and data for creating player and non-player characters.
    DEV Notes: Break this out into multiple classes.
    '''

    def __init__(self):
        '''
        Instantiate Character object.
        '''
        # Environment
        self.ClanNames = []
        # DNA mixture, stored as a NumPy indexed array:
        self.DNR = np.zeros(1, dtype=[('h', np.float_),
                                      ('m', np.float_),
                                      ('a', np.float_)])
        self.DNAdesc = ''
        self.DNAmix = ''
        self.DNAappear = ''
        # Sex, Gender and Sexual Orientation
        self.Sex = ''
        self.Gender = ''
        self.SexOrient = []
        # Animal Type
        self.AnimalType = {}
        # Abilities, Hit Points, Karma
        self.Abilities = {'PS':'Physical Strength', 'MS':'Mental Strength',
                          'CH':'Charisma', 'IQ':'Intelligence',
                          'DX':'Dexterity', 'IN':'Intuition',
                          'CN':'Constitution', 'HP':'Hit Points',
                          'K':'Karma'}
        self.Ability = {}
        self.AbilityDesc = {}
        self.HitPoints = 0
        self.Karma = 0
        self.HitPointsDesc = ''
        self.KarmaDesc = ''
        # Character Name
        self.CharClanName = ''
        self.CharacterName = ''
        # Character Age and Dates
        self.StartingAge = 0
        self.BirthDate = {}
        self.ClanInDate = {}
        self.GuildInDate = {}
        # Personality
        self.p_general = ''
        self.p_tone = ''
        self.p_behavior = ''
        self.Guild = {}
        self.Alliance = {}
        self.SecretSociety = {}
        self.SecretOrg = {}

        self.ResetChar()

    def ResetChar(self):
        '''
        (Re-)Initialize Character object.
        '''
        # Environment
        self.ClanNames = []
        # DNA mixture.
        self.DNR['h'] = 0.0
        self.DNR['m'] = 0.0
        self.DNR['a'] = 0.0
        self.DNAdesc = ''
        self.DNAmix = ''
        self.DNAappear = ''
        # Sex, Gender and Orientation
        self.Sex = ''
        self.Gender = ''
        self.SexOrient = [0, 'Asexual']
        # Animal Types
        self.AnimalType = {}
        # Abilities, Hit Points and Karma
        self.Ability = {'MS':0, 'DX':0, 'CH':0, 'CN':0, 'PS':0, 'IQ':0, 'IN':0}
        self.AbilityDesc = {'MS':'', 'DX':'', 'CH':'', 'CN':'', 'PS':'', 'IQ':'', 'IN':''}
        self.HitPoints = 0
        self.Karma = 0
        self.HitPointsDesc = ''
        self.KarmaDesc = ''
        # Character Name
        self.CharClanName = ''
        self.CharacterName = ''
        # Character Age and Dates
        self.StartingAge = 0
        self.BirthDate = {'year':0, 'month':0, 'day':0, 'desc':''}
        self.ClanInDate = {'year':0, 'month':0, 'day':0, 'desc':''}
        self.GuildInDate = {'year':0, 'month':0, 'day':0, 'desc':''}
        # Personality
        self.p_general = ''
        self.p_tone = ''
        self.p_behavior = ''
        # Guild and Alliance
        self.Guild = {}
        self.Alliance = {}
        self.SecretSociety = {}
        self.SecretOrg = {}

    def GetClanNames(self, name_count=10):
        '''
        Initialize Clan names
        '''
        self.ClanNames = names.create_surnames(name_count)
        return self.ClanNames

    def SetDNA(self, mainly_human=False, mainly_shaped=False, mainly_animal=False):
        '''
        Compute relative rates of human, shaped and animal DNA.
        If there is any shaped or animal DNA, there must be some degree of human as well.
        Having mixed DNA implies that the character will have some shaped capabilities.
        The more shaped DNA xe has, the more shaped capabilities will be present.
        The more animal DNA xe has, the more animal characteristics will be present.
        Setting any one of the params to True will weight the calculation in that direction.
        Only the first True argument is used.
        '''
        self.ResetChar()

        # Actual genetic mix / Genotype
        # Break this down into fewer branches.
        # See if there is a way to abstract/simplify this logic.
        if mainly_human:
            self.DNAdesc = 'mainly human'
            self.DNR['h'] = random.uniform(0.95, 1.00)
            self.DNR['m'] = random.uniform(0.00, 0.05)
            if (self.DNR['h'] + self.DNR['m']) > 1.0:
                self.DNR['m'] = 1.0 - self.DNR['h']
            else:
                self.DNR['a'] = 1.0 - (self.DNR['h'] + self.DNR['m'])

        elif mainly_shaped:
            self.DNAdesc = 'mainly shaped'
            self.DNR['m'] = random.uniform(0.70, 0.90)
            self.DNR['h'] = random.uniform(0.00, 0.30)
            if (self.DNR['h'] + self.DNR['m']) > 1.0:
                self.DNR['m'] = 1.0 - self.DNR['h']
            else:
                self.DNR['a'] = 1.0 - (self.DNR['h'] + self.DNR['m'])

        elif mainly_animal:
            self.DNAdesc = 'mainly animal'
            self.DNR['a'] = random.uniform(0.70, 0.90)
            self.DNR['m'] = random.uniform(0.00, 0.20)
            if (self.DNR['a'] + self.DNR['m']) > 1.0:
                self.DNR['m'] = 1.0 - self.DNR['a']
            else:
                self.DNR['h'] = 1.0 - (self.DNR['a'] + self.DNR['m'])
        else:
            # Random selection of human, shaped and animal
            self.DNR['h'] = random.random()
            self.DNR['m'] = random.random()
            if (self.DNR['h'] + self.DNR['m']) > 1.0:
                self.DNR['m'] = 1.0 - self.DNR['h']
            else:
                self.DNR['a'] = 1.0 - (self.DNR['h'] + self.DNR['m'])
            if self.DNR['h'] > 0.80:
                self.DNAdesc = 'human'
            elif self.DNR['m'] > 0.80:
                if self.DNR['a'] > self.DNR['h']:
                    self.DNAdesc += 'shaped animal'
                else:
                    self.DNAdesc += 'shaped human'
            elif self.DNR['a'] > 0.80:
                self.DNAdesc = 'animal'
            elif self.DNR['h'] > 0.45:
                if self.DNR['a'] > self.DNR['m']:
                    self.DNAdesc += 'aninmal human'
                else:
                    self.DNAdesc += 'shaped human'
            elif self.DNR['m'] > 0.45:
                if self.DNR['a'] > self.DNR['h']:
                    self.DNAdesc += 'shaped animal'
                else:
                    self.DNAdesc += 'shaped human'
            elif self.DNR['a'] > 0.45:
                if self.DNR['h'] > self.DNR['m']:
                    self.DNAdesc += 'human animal'
                else:
                    self.DNAdesc += 'shaped animal'
            else:
                if self.DNR['a'] > self.DNR['h']:
                    self.DNAdesc += 'shaped animal'
                else:
                    self.DNAdesc += 'shaped human'
            # Appearance / Phenotype
            if self.DNR['a'] < 0.05:
                if self.DNR['m'] < 0.50:
                    self.DNAappear = 'human-appearing'
                else:
                    self.DNAappear = 'mainly human-appearing'
            else:
                if self.DNR['a'] > 0.50:
                    self.DNAappear = 'mainly animal-appearing'
                elif  self.DNR['a'] > 0.25:
                    self.DNAappear = 'obvious animal traits'
                else:
                    self.DNAappear = 'some obvious animal traits'

        h = self.DNR['h'] * 100
        m = self.DNR['m'] * 100
        a = self.DNR['a'] * 100
        self.DNAmix = "H: {0:.1f}%".format(h[0]) + \
                       " M: {0:.1f}%".format(m[0]) + \
                       " A: {0:.1f}%".format(a[0])

        return (self.DNR, self.DNAdesc, self.DNAmix)

    def SetSex(self, is_male=False, is_female=False, is_inter=False):
        '''
        Either set physical sex or randomly assign it.
        If multiple true arguments provided, the first one is used.
        '''
        if is_male:
            self.Sex = 'male'
        elif is_female:
            self.Sex = 'female'
        elif is_inter:
            self.Sex = 'intersex'
        else:
            r = random.random()
            it = .99                        # intersex threshold
            if self.DNR['m'] > .75:
                it = .95                    # for much-shapeds
            mt = it / 2                     # male threshold
            if r < mt:
                self.Sex = 'male'
            elif r < it:
                self.Sex = 'female'
            else:
                self.Sex = 'intersex'

        return self.Sex

    def SetGender(self, is_male=False, is_female=False, is_andro=False):
        '''
        Either set gender identification or randomly select it.
        If multiple true arguments provided, the first one is used.
        '''
        if is_male:
            self.Gender = 'male'
        elif is_female:
            self.Gender = 'female'
        elif is_andro:
            self.Gender = 'androgynous'
        else:
            r = random.random()
            ot = .95                # opposite Sex Gender ID threshold
            at = .98                # androgyny Gender ID threshold

            # Does this really need so many branches?
            if self.Sex in ['male', 'female']:
                if r < ot:
                    self.Gender = self.Sex
                elif r < at:
                    if self.Sex == 'male':
                        self.Gender = 'female'
                    else:
                        self.Gender = 'male'
                else:
                    self.Gender = 'androgynous'
            else:
                if r < .50:
                    self.Gender = 'male'
                else:
                    self.Gender = 'female'

        return self.Gender

    def SetSexOrient(self, kinsey=-1):
        '''
        Set or compute sexual orientation score from 1 (straight) to 10 (gay),
        or set to zero (asexual).  This is fairly basic. Doesn't try to do
        much more than assign a Kinsey rating.
        '''
        if kinsey > -1:
            kinsey = int(kinsey)
            if kinsey > 10:
                kinsey = 10
            self.SexOrient[0] = kinsey
        else:
            r = utils.random_100()
            if r < 3:
                self.SexOrient[0] = 0
            elif r < 35:
                self.SexOrient[0] = 1
            elif r < 45:
                self.SexOrient[0] = 2
            elif r < 65:
                self.SexOrient[0] = 3
            elif r < 85:
                self.SexOrient[0] = 4
            elif r < 90:
                self.SexOrient[0] = 5
            elif r < 95:
                self.SexOrient[0] = 6
            elif r < 97:
                self.SexOrient[0] = 7
            elif r < 98:
                self.SexOrient[0] = 8
            elif r < 99:
                self.SexOrient[0] = 9
            else:
                self.SexOrient[0] = 10
            orient = ['Asexual', 'Straight', 'Straight', 'Straight',
                      'Straight-bi', 'Bisexual', 'Bisexual', 'Gay-bi',
                      'Gay', 'Gay', 'Gay']
            self.SexOrient[1] = orient[self.SexOrient[0]]

        return self.SexOrient

    def SetAnimalType(self):
        '''
        Starting with DNA rate, then adding random characteristics, identify
        what type of Animals make up the character.  Obviously much more can
        be done here.  This is just a starting point.  Heavily mutated
        characters are basically made up of multiple animals.
        '''
        self.AnimalType = {}
        # Include human if they have any human DNA:
        if self.DNR['h'] > 0.0:
            self.AnimalType['mammal'] = {'primate':['human']}
        # Continue only if animal DNA is > 0
        if self.DNR['a'] > 0.0:
            # Determine how many animal strains are involved based on
            # percentage of shaped DNA
            acnt = 0
            if self.DNR['m'] < 0.35:
                acnt = 1
            elif self.DNR['m'] < 0.65:
                acnt = 2
            elif self.DNR['m'] < 0.95:
                acnt = 3
            else:
                acnt = 4
            # Randomly select animal strains
            for a in range(1,acnt+1):
                # Break this out into sub-functions?
                # Choose class:
                r = utils.random_100()
                className = ''
                if r < 10:
                    className = 'amphibian'
                elif r < 20:
                    className = 'bird'
                elif r < 30:
                    className = 'fish'
                elif r < 50:
                    className = 'insect'
                elif r < 80:
                    className = 'mammal'
                else:
                    className = 'reptile'
                # Choose order:
                # Retrieve the Order list for this Class
                life = lifeform.LifeForm()
                orderDict = life.AnimalClass[className]
                orderNames = orderDict.keys()   # name of Orders in this Class
                ocnt = len(orderNames)          # number of Orders for this Class

                br = int(100 / ocnt)            # evenly assign a random range to each order
                r = utils.random_100()
                orderName = ''
                familyNames = []
                fcnt = 0
                for o in range(1, ocnt + 1):
                    # Select Order that is in the randomized range:
                    if r < (o * br):
                        orderName = orderNames[o-1]
                        # Retreive the Family list for this Order
                        familyNames = orderDict[orderName]
                        fcnt = len(familyNames)         # number of Families for this Order
                        fr = int(100 / fcnt)            # evenly assign a random range to each order
                        break

                # Choose family:
                r = utils.random_100()
                familyName = ''
                for f in range(1, fcnt + 1):
                    # Select Family that is in the randomized range:
                    if r < (f * fr):
                        familyName = familyNames[f-1]
                        break

                if className in self.AnimalType.keys():
                    if orderName in self.AnimalType[className].keys():
                        # Add new Family to an existing Order
                        self.AnimalType[className][orderName].append(familyName)
                    else:
                        # Add new Order to an existing Class
                        self.AnimalType[className][orderName] = [familyName]
                else:
                    # Add a new Class
                    self.AnimalType[className] = {orderName:[familyName]}

        return self.AnimalType

    def SetAbilities(self, inherited_karma=0):
        '''
        Compute randomized starting-point standard ability scores, hit points,
        and karma.  All of these qualities may be modified based on species-specific
        characteristics -- but that is for another day and another layer of complexity!
        For now, there are just some basic adjustments depending on DNA mix.
        Karma is a quality that I am adding in to the game. The idea is to be able
        to pass it along to a new character when a previous one transcends a given
        plane of virtual reality.  Perhaps it will influence Intuition, which I have
        also added...
        '''
        # Compute mental strength as 4d6, subtract the lowest (3:18)
        self.Ability['MS'] = utils.four_d6_sub_low()
        if self.Ability['MS'] < 7:
            self.AbilityDesc['MS'] = 'Low'
        elif self.Ability['MS'] < 10:
            self.AbilityDesc['MS'] = 'Below avg'
        elif self.Ability['MS'] < 15:
            self.AbilityDesc['MS'] = 'Above avg'
        else:
            self.AbilityDesc['MS'] = 'High'

        # Compute dexterity as 4d6, subtract the lowest (3:18)
        self.Ability['DX'] = utils.four_d6_sub_low()
        if self.Ability['DX'] < 7:
            self.AbilityDesc['DX'] = 'Low'
        elif self.Ability['DX'] < 10:
            self.AbilityDesc['DX'] = 'Below avg'
        elif self.Ability['DX'] < 15:
            self.AbilityDesc['DX'] = 'Above avg'
        else:
            self.AbilityDesc['DX'] = 'High'

        # Compute charisma
        #   If Human DNR < 50%, then 4d6, subtract the lowest, with min of 6
        #   Otherwise 4d6 with max of 18  (6:18)
        if self.DNR['h'] < .50:
            self.Ability['CH'] = utils.four_d6_sub_low_min(6)
        else:
            self.Ability['CH'] = utils.four_d6_max_min(18, 6)
        if self.Ability['CH'] < 10:
            self.AbilityDesc['CH'] = 'Low'
        elif self.Ability['CH'] < 13:
            self.AbilityDesc['CH'] = 'Below avg'
        elif self.Ability['CH'] < 16:
            self.AbilityDesc['CH'] = 'Above avg'
        else:
            self.AbilityDesc['CH'] = 'High'

        # Compute constitution
        #   If Human DNR < 50%, then 4d6, subtract the lowest, with min of 8
        #   Otherwise 4d6 with max of 18  (8:18)
        if self.DNR['h'] < .50:
            self.Ability['CN'] = utils.four_d6_sub_low_min(8)
        else:
            self.Ability['CN'] = utils.four_d6_max_min(18, 8)
        if self.Ability['CN'] < 10:
            self.AbilityDesc['CN'] = 'Low'
        elif self.Ability['CN'] < 13:
            self.AbilityDesc['CN'] = 'Below avg'
        elif self.Ability['CN'] < 16:
            self.AbilityDesc['CN'] = 'Above avg'
        else:
            self.AbilityDesc['CN'] = 'High'

        # Compute physical strength as 4d6, subtract the lowest (3:18))
        self.Ability['PS'] = utils.four_d6_sub_low()
        if self.Ability['PS'] < 7:
            self.AbilityDesc['PS'] = 'Low'
        elif self.Ability['PS'] < 10:
            self.AbilityDesc['PS'] = 'Below avg'
        elif self.Ability['PS'] < 15:
            self.AbilityDesc['PS'] = 'Above avg'
        else:
            self.AbilityDesc['PS'] = 'High'

        # Compute intelligence (IQ)
        #   Ranges are aligned to the Wechsler IQ Classifications
        if self.DNR['h'] < .50:
            self.Ability['IQ'] = random.randint(40, 125)
        else:
            self.Ability['IQ'] = random.randint(60, 150)
        if self.Ability['IQ'] < 70:
            self.AbilityDesc['IQ'] = 'Extremely low'
        elif self.Ability['IQ'] < 80:
            self.AbilityDesc['IQ'] = 'Borderline'
        elif self.Ability['IQ'] < 90:
            self.AbilityDesc['IQ'] = 'Low average'
        elif self.Ability['IQ'] < 110:
            self.AbilityDesc['IQ'] = 'Average'
        elif self.Ability['IQ'] < 120:
            self.AbilityDesc['IQ'] = 'High average'
        elif self.Ability['IQ'] < 130:
            self.AbilityDesc['IQ'] = 'Superior'
        else:
            self.AbilityDesc['IQ'] = 'Very superior'

        # Compute intuition
        #   If Human DNR < 50%, then 4d6, subtract the lowest, with min of 3
        #   Otherwise 4d6 with max of 24  (3:24)   3   8   14   19     24
        if self.DNR['h'] < .50:
            self.Ability['IN'] = utils.four_d6_sub_low_min(3)
        else:
            self.Ability['IN'] = utils.four_d6_max_min(24)
        if self.Ability['IN'] < 8:
            self.AbilityDesc['IN'] = 'Low'
        elif self.Ability['IN'] < 14:
            self.AbilityDesc['IN'] = 'Below avg'
        elif self.Ability['IN'] < 18:
            self.AbilityDesc['IN'] = 'Above avg'
        else:
            self.AbilityDesc['IN'] = 'High'

        # Compute Hit Points
        # When a character loses all of its hit points, it leaves the
        #  current virtual plane and travels thru the bardo to its next
        #  level of incarnation.
        # If Human DNR < 50%, then d6 CN number of times.
        # Else d8 CN number of times.  (8:64)       8    22    36    50       64
        if self.DNR['h'] < .50:
            self.HitPoints = utils.d6_n_times(self.Ability['CN'])
        else:
            self.HitPoints = utils.d8_n_times(self.Ability['CN'])
        if self.HitPoints < 22:
            self.HitPointsDesc = 'Low'
        elif self.HitPoints < 36:
            self.HitPointsDesc = 'Below avg'
        elif self.HitPoints < 50:
            self.HitPointsDesc = 'Above avg'
        else:
            self.HitPointsDesc = 'High'

        # Set Karma
        # Karma for a completely new character is baselined at zero (none accumulated)
        # and adjusted slightly based on intuition.  For a character who is the
        # reincarnation of a character, then karma is inherited  (-n:+n)
        self.Karma = inherited_karma
        if self.Ability['IN'] > 20:
            self.Karma += 2
        elif self.Ability['IN'] > 16:
            self.Karma += 1
        elif self.Ability['IN'] < 5:
            self.Karma -= 2
        elif self.Ability['IN'] < 8:
            self.Karma -= 2
        if self.Karma == 0:
            self.KarmaDesc = 'Normal'
        elif self.Karma == 1:
            self.KarmaDesc = 'Lucky'
        elif self.Karma == 2:
            self.KarmaDesc = 'Very lucky'
        elif self.Karma > 2:
            self.KarmaDesc = 'Blessed'
        elif self.Karma == -1:
            self.KarmaDesc = 'Unlucky'
        elif self.Karma == -2:
            self.KarmaDesc = 'Very unlucky'
        elif self.Karma < -2:
            self.KarmaDesc = 'Cursed'

        return (self.Ability, self.HitPoints, self.Karma)

    def SetClanAndTribe(self, c):
        '''
        Select a Clan for the character and within that a tribe.
        '''
        print 'SetClanAndTribe:self.ClanNames: ', self.ClanNames
        print 'SetClanAndTribe:c.ClanNames: ', c.ClanNames


        # print len(self.ClanNames)
        # print len(self.ClanNames)-1
        # r = random.randint(0, len(self.ClanNames)-1)

        # self.CharClanName = self.ClanNames[r]
        return self.CharClanName

    def SetCharName(self, name_count=1, surname=''):
        '''
        Select, or at least suggest, a character name.
        '''
        self.CharacterName = names.behind_the_name(self.Gender, name_count, surname)
        return self.CharacterName

    def SetCharDates(self, age=0):
        '''
        Set the character's age, birthdate and induction dates.  The induction
        dates indicate when the character became an adult member of their
        clan or tribe and when they became a full member of their guild,
        association or other society.

        More to be done here, obviously, but the starting-point is to
        get underway with some information about the character's life-story.
        Generally, a new character becomes active in the game at some age
        between teen years and elderly years.  Exactly what that means
        may vary depending on DNR, but for now we used basic human measures.

        The caller may specify an age as well. It should be an integer.
        '''
        gt = gametime.GameTime()

        def __setWeekDay(day_num):
            '''
            Compute name of a day based on its number. Probably move this to gametime.py
            '''
            day_name = ''
            for d in range(6,0,-1):
                if (day_num % d) == 0:
                    day_name = gt.Calendar['days']['weeks']['weekDayNames'][d]
                    break
            return day_name

        def __formatDate(month_num, day_num):
            '''
            Format a nice date description. Probably move this to gametime.py
            '''
            day_name = __setWeekDay(day_num)
            format_date = day_name['common'] + ', ' + str(day_num) + ' ' + \
                          gt.Calendar['months'][month_num]['common']
            holiday = gt.IsHoliday(month_num, day_num)
            # Add name of holiday if the date is a holiday
            if holiday:
                format_date += ', ' + holiday['common'] + ' ' + holiday['desc']
            return format_date

        if age != 0:
            self.StartingAge = int(age)
        else:
            self.StartingAge = random.randrange(14,42)

        self.BirthDate['year'] = -(self.StartingAge)
        self.BirthDate['month'] = random.randrange(1,12)
        self.BirthDate['day'] = random.randrange(1,30)
        self.BirthDate['desc'] = __formatDate(self.BirthDate['month'], self.BirthDate['day'])

        if (self.StartingAge > 12):
            # For now, we default the Clan induction age to 13
            self.ClanInDate['year'] = -(self.StartingAge - 13)
            self.ClanInDate['month'] = random.randrange(1,12)
            self.ClanInDate['day'] = random.randrange(1,30)
            self.ClanInDate['desc'] = __formatDate(self.ClanInDate['month'], self.ClanInDate['day'])

        if (self.StartingAge > 15):
            # For now, we default the Guild induction age to 16
            self.GuildInDate['year'] = -(self.StartingAge - 16)
            self.GuildInDate['month'] = random.randrange(1,12)
            self.GuildInDate['day'] = random.randrange(1,30)
            self.GuildInDate['desc'] = __formatDate(self.GuildInDate['month'], self.GuildInDate['day'])

        return (self.StartingAge, self.BirthDate, self.ClanInDate, self.GuildInDate)

    def set_personality(self):
        '''
        Compute a Myers-Briggs personality matrix (MBTI) for the character.
        '''
        p_obj = personality.Personality()
        (self.p_general, self.p_tone, self.p_behavior) = \
            p_obj.set_personality(self.Ability['IN'], self.Ability['IQ'])

        return (self.MyersBriggs, self.p_general, self.p_behavior)

    def SetFamily(self, s):
        '''
        Generate family for the character
        '''
        # Family, Romance, Friends, Enemies
        s.SetBasicParentData()
        s.SetParentRelationship()
        s.SetSiblings()
        s.SetFamilyStatus()
        return True

    def SetFrenemiesAndRomance(self, s):
        '''
        Generate friends, enemines and romantic storyline
        '''
        s.SetFrenemies(self.Ability['CH'])
        s.SetRomance(self.SexOrient, self.Gender)
        return True


    def SetGuildAlliance(self, o):
        '''
        Assign the character to a guild. Identify what alliance the
        guild belongs to.
        '''
        self.Guild = o.SetGuild(self.DNAdesc)
        self.Alliance = o.FindAlliance(self.Guild['name'])

        if len(self.Alliance) == 0 \
        or self.Alliance == None \
        or self.Alliance == False:
            print 'ERROR in SetGuildAlliance. Alliance: ', self.Alliance, ' for self.Guild[name]=', self.Guild['name']
            return False

        return True

    def SetSecretSociety(self, o):
        '''
        Assign the secret society most likely to try to recruit the
        character.
        '''
        # Identify which secret societies are associated with the guild-alliance
        societies = o.FindSocieties(self.Alliance['name'])
        # Pick a type of secret society based on guild associations
        r = random.randint(0, len(societies)-1)
        self.SecretSociety = societies[r]
        # Pick a particular secret organization within that society
        self.SecretOrg = o.PickSecretOrg(self.SecretSociety['name'], self.DNR, self.AnimalType, self.StartingAge, self.Gender)
        return True


    # Add: Clan/Tribe/Language
    # Add: Religion
    # Add: Secret Society

def rpt_surnames(c):
    '''
    Report on clan names
    '''

    print c.ClanNames

    rpt = "\n\nENVIRONMENT GENERATED: " + utils.dt_dYmdHZ_Now()
    rpt += "\n====================================================="
    for nm in c.ClanNames:
        rpt += "\n           Clan Name:\t" + str(nm)
    return rpt

def rpt_dna(c):
    '''
    Report on character type
    '''
    rpt = "\n\nCHARACTER GENERATED: " + utils.dt_dYmdHZ_Now()
    rpt += "\n====================================================="
    rpt += "\n\nCharacteristics"
    rpt += "\n-------------------------"
    rpt += "\n             DNA mix:\t" + c.DNAmix
    rpt += "\n            Genotype:\t" + c.DNAdesc
    rpt += "\n           Phenotype:\t" + c.DNAappear
    return rpt

def rpt_sex_gender_orient(c):
    '''
    Report on sex, gender and sexual orientation
    '''
    rpt = "\n      Biological Sex:\t" + c.Sex
    rpt += "\n              Gender:\t" + c.Gender
    rpt += "\n  Sexual Orientation:\t" + c.SexOrient[1]
    return rpt

def rpt_animal_type(c):
    '''
    Report on what type of animal DNA is involved in the character
    '''
    rpt = ''
    for ac in c.AnimalType.keys():
        rpt += "\n               Class:\t" + ac + "\t"
        for ao in c.AnimalType[ac].keys():
            rpt += "  Order: " + ao + "\t"
            for af in c.AnimalType[ac][ao]:
                rpt += "  Family: " + af + "\t"
    return rpt

def rpt_abilities(c):
    '''
    Report on character "abilities", i.e., the standard set of "stats"
    '''
    rpt = "\n\nAbilities"
    rpt += "\n-------------------------"
    # This method of formatting is not exactly right, but seems to work?
    rpt += "\n   Physical Strength:\t" + str(c.Ability['PS']).format('==') + "\t" + c.AbilityDesc['PS']
    rpt += "\n     Mental Strength:\t" + str(c.Ability['MS']).format('==') + "\t" + c.AbilityDesc['MS']
    rpt += "\n        Intelligence:\t" + str(c.Ability['IQ']).format('==') + "\t" + c.AbilityDesc['IQ']
    rpt += "\n           Intuition:\t" + str(c.Ability['IN']).format('==') + "\t" + c.AbilityDesc['IN']
    rpt += "\n           Dexterity:\t" + str(c.Ability['DX']).format('==') + "\t" + c.AbilityDesc['DX']
    rpt += "\n            Charisma:\t" + str(c.Ability['CH']).format('==') + "\t" + c.AbilityDesc['CH']
    rpt += "\n        Constitution:\t" + str(c.Ability['CN']).format('==') + "\t" + c.AbilityDesc['CN']
    rpt += "\n          Hit Points:\t" + str(c.HitPoints).format('==') + "\t" + c.HitPointsDesc
    rpt += "\n               Karma:\t" + str(c.Karma).format('==') + "\t" + c.KarmaDesc
    return rpt

def rpt_clan_and_tribe(c):
    '''
    Report on the character's Clan and Tribe
    '''
    rpt = "\n\nGroup Identity"
    rpt += "\n-------------------------"
    rpt += "\n      Character Clan: " + str(c.CharClanName)
    return rpt

def rpt_identity(c):
    '''
    Report on the basic facets of a character's identity
    '''
    rpt = "\n\nPersonal Identity"
    rpt += "\n-------------------------"
    rpt += "\n      Character Name: " + str(c.CharacterName)
    rpt += "\n                 Age: " + str(c.StartingAge) + " years old"
    rpt += "\n          Birth Date: " + c.BirthDate['desc'] + ' ' + str(c.BirthDate['year'])
    rpt += "\n Clan Induction Date: " + c.ClanInDate['desc'] + ' ' + str(c.ClanInDate['year'])
    rpt += "\nGuild Induction Date: " + c.GuildInDate['desc'] + ' ' + str(c.GuildInDate['year'])
    return rpt

def rpt_personality(c):
    '''
    Report on the character's personality
    '''
    rpt = "\n\nPersonality"
    rpt += "\n-------------------------"
    # rpt += "\n  Myers-Briggs Score: " + c.MyersBriggs + ' (' + c.p_general + ')'
    rpt += "\n General Personality: " + c.p_behavior['personality']
    rpt += "\n       Personal Tone: " + c.p_behavior['tone']
    rpt += "\n Behavioral Tendency: " + c.p_behavior['behavior']
    return rpt

def rpt_biological_parents(s):
    '''
    Report on the character's biological parents.
    '''
    def __biol_parent(m_or_f):
        '''
        Format information for biological parent
        First argument is 'mother' for mother or 'father' for father
        '''
        if not (m_or_f in ('mother', 'father')):
            print 'ERROR: Argument for __biol_parent must be in (\'mother\', \'father\')'
            return False
        fTitle = ''
        story = ''
        pbp = s.Parents['biological'][m_or_f]
        if pbp['present']:
            is_alive = 'may be living'
            is_was = 'is'
        else:
            is_alive = 'is probably dead or missing'
            is_was = 'was'
            story = ', ' + pbp['tragedy']
        if pbp['same']:
            isSame = '; ' + is_was + ' also the brood parent'
            if pbp['present']:
                fTitle = 'Adoptive '
        else:
            isSame = '; ' + is_was + ' not the brood parent'
            if pbp['present']:
                story = ', ' + pbp['relationship']
        rpt = "\n              " + fTitle + m_or_f.title() + ": " + is_alive + story + isSame
        return rpt

    rpt = "\n\nFamily"
    rpt += "\n-------------------------"
    rpt += "\n  Biological Parents"
    rpt += __biol_parent('father')
    rpt += __biol_parent('mother')
    return rpt

def rpt_brood_parents(s):
    '''
    Report on the character's "brood" parents -- their adoptive/nurturing
    parental units, who may or may not be the same as the biological parents.
    '''
    def __brood_parent(one_two):
        '''
        Format information for brood parent
        First argument is 1 or 2
        '''
        if not (one_two in (1, 2)):
            print 'ERROR: argument for __brood_parent must be in (1, 2)'
            return False
        ptags = ['parentOne', 'parentTwo']
        ptag = ptags[one_two-1]
        pbp = s.Parents['brood'][ptag]
        p_title = ''
        if pbp['present']:
            is_alive = ' may be living'
            story = ', ' + pbp['relationship']
        else:
            is_alive = ' is probably dead or missing'
            story = ', ' + pbp['tragedy']
        if pbp['sex'] == 'M' and pbp['gender'] == 'M':
            p_title += 'Father'
        elif pbp['sex'] == 'M' and pbp['gender'] == 'F':
            p_title += 'Father-Mother'
        elif pbp['sex'] == 'F' and pbp['gender'] == 'M':
            p_title += 'Mother-Father'
        elif pbp['sex'] == 'F' and pbp['gender'] == 'F':
            p_title += 'Mother'
        rpt = "\n           Parent #" + str(one_two) + ": " + p_title + \
               ' (sex:' +pbp['sex'] + ', gender:' + pbp['gender'] + \
               ' )' + is_alive + story
        return rpt

    rpt = "\n\n       Brood Parents"
    rpt += __brood_parent(1)
    rpt += __brood_parent(2)
    return rpt

def rpt_siblings(s):
    '''
    Report on the character's brothers and sisters
    '''
    rpt = "\n\n            Siblings: "
    if s.Siblings['sibCount'] == 0:
        rpt += "\tNone"
    else:
        rpt += "\t" +  str(s.Siblings['sibCount'])
        for sib in range(0, s.Siblings['sibCount']):
            rpt += "\n                " + s.Siblings['sibs'][sib][0] + \
                   "\t\trelationship: " + s.Siblings['sibs'][sib][1]
    return rpt

def rpt_family_status(s):
    '''
    Report on the character's family's social status
    '''
    rpt = "\n\n Family Situation:"
    if not('tragedy' in s.FamilyStatus.keys()) or s.FamilyStatus['tragedy'] == None:
        tragedy = 'None'
    else:
        tragedy = s.FamilyStatus['tragedy']
    if not('motive' in s.FamilyStatus.keys()) or s.FamilyStatus['motive'] == None:
        motive = 'None'
    else:
        motive = s.FamilyStatus['motive']
    if not ('wealth' in s.FamilyStatus.keys()) or s.FamilyStatus['wealth'] == None:
        wealth = 'None'
    else:
        wealth = s.FamilyStatus['wealth']
    rpt += "\n       Family Wealth: " + wealth
    rpt += "\n   Family Reputation: " + s.FamilyStatus['reputation']
    rpt += "\n Family Social Class: " + s.FamilyStatus['socialClass']
    rpt += "\n         Clan Status: " + s.FamilyStatus['clanStatus']
    rpt += "\n      Family Tragedy: " + tragedy
    rpt += "\n  Related Motivation: " + motive
    return rpt

def rpt_frenemies_romance(s):
    '''
    Report on the character's friends, enemies and romantic situation
    '''
    rpt = "\n\n Romance, Friends and Enemies"
    rpt += "\n-------------------------"
    rpt += "\n Relationship Status: " + s.Romance['status']
    rpt += "\n          Love Story: " + s.Romance['relate']
    rpt += "\nBeloved is/was/to be: " + s.Romance['loveGender']

    if 'feels' in s.Romance.keys():
        rpt += "\n  Tragic Love Affair: " + s.Romance['tragedy']
        rpt += "\n    Current Feelings: " + s.Romance['feels']

    rpt += "\n\n    Best ally is/was: "  + s.Frenemies['bestAlly']
    rpt += "\n       Other Friends: " + str(s.Frenemies['friendCnt'])
    if s.Frenemies['friendCnt'] > 0:
        for f in range(0, s.Frenemies['friendCnt']):
            rpt += "\n                      a " + s.Frenemies['friends'][f][0] + ' is ' +  s.Frenemies['friends'][f][1]
    rpt += "\n             Enemies: " + str(s.Frenemies['enemyCnt'])
    if s.Frenemies['enemyCnt'] > 0:
        for f in range(0, s.Frenemies['enemyCnt']):
            rpt += "\n                      a " + s.Frenemies['enemies'][f][0] + ' who is ' +  s.Frenemies['enemies'][f][1]
            rpt += "\n                          The " + s.Frenemies['enemies'][f][2] + ' because ' +  s.Frenemies['enemies'][f][3] + '.'
            rpt += "\n                          Strategy: " +  s.Frenemies['enemies'][f][4]
    return rpt

def rpt_guild(c):
    '''
    Report on the character's guild membership
    '''
    rpt = "\n\n Guild"
    rpt += "\n-------------------------"
    rpt += "\n               Guild: " + c.Guild['name'] + ': ' + c.Guild['desc']
    if len(c.Guild['pro']) > 0:
        ptypes = ''
        for typ in c.Guild['pro']:
            ptypes += typ + ', '
        ptypes = ptypes[0:len(ptypes)-2]
    else:
        ptypes = 'none'
    rpt += "\n                         Favors: " + ptypes
    if len(c.Guild['anti']) > 0:
        ptypes = ''
        for typ in c.Guild['anti']:
            ptypes += typ + ', '
        ptypes = ptypes[0:len(ptypes)-2]
    else:
        ptypes = 'none'
    rpt += "\n                         Opposes: " + ptypes
    return rpt

def rpt_alliance(c):
    '''
    Report on the alliance to which the character's guild belongs
    '''
    rpt = "\n\n Alliance"
    rpt += "\n-------------------------"

    if not ('name' in c.Alliance.keys()):
        print 'ERROR No name found for Alliance: ', c.Alliance
        return False

    rpt += "\n            Alliance: " + c.Alliance['name'] + ': ' + c.Alliance['desc'] + ';'
    cls = ''
    for k in c.Alliance['classes']:
        cls += k + ', '
    cls = cls[0:len(cls)-2]
    rpt += "\n                          " + cls
    als = ''
    for a in c.Alliance['aliases']:
        als += a + ', '
    als = als[0:len(als)-2]
    rpt += "\n                   a/k/a: " + als
    return rpt

def rpt_secret_org(c):
    '''
    Report on what secret organization will most likely try to recruit the player.
    DEBUG self.SecretOrg:  {'desc': 'Skillful, good-natured, legendary, support the poor',
    'name': 'Ankat Sunin',
    'aliases': ['Lawless Intelligence', 'Merry Band']}
    '''
    rpt = "\n\n Secret Society"
    rpt += "\n-------------------------"
    rpt += "\n              Society: " + c.SecretSociety['name'] + ': ' + c.SecretSociety['desc'] + ';'
    als = ''
    for nm in c.SecretSociety['aliases']:
        als += nm + ', '
    als = als[0:len(als)-2]
    rpt += "\n                   a/k/a: " + als
    rpt += "\n\nSpecific Organization: " + c.SecretOrg['name'] + ': ' + c.SecretOrg['desc'] + ';'
    als = ''
    if not ('aliases' in c.SecretOrg.keys()):
        print 'ERROR no key "aliases" found in c.SecretOrg: ', c.SecretOrg
        return False

    for nm in c.SecretOrg['aliases']:
        als += nm + ', '
    als = als[0:len(als)-2]
    rpt += "\n                   a/k/a: " + als
    return rpt

def testme():
    # Turn on logging. Save outputs to a local log file.
    logging.basicConfig(filename="char.log",level=logging.DEBUG)

    # Create a character object
    c = Character()
    rpt = ''
    # Generate clan and tribal family names
    # Normally, we will generate the environment first and save it,
    # then produce characters/players in that environment.
    c.GetClanNames(13)
    rpt += rpt_surnames(c)

    print c.ClanNames

    # Character type (DNA mix)
    c.SetDNA()
    rpt += rpt_dna(c)
    # Set Sex, Gender and Orientation
    c.SetSex()
    c.SetGender()
    c.SetSexOrient()
    rpt += rpt_sex_gender_orient(c)
    # Set Animal Type
    c.SetAnimalType()
    rpt += rpt_animal_type(c)
    # Abilities and Hit Points
    c.SetAbilities(0)
    rpt += rpt_abilities(c)

    print c.ClanNames

    # Select Clan and Tribe
    c.SetClanAndTribe(c)
   # rpt += rpt_clan_and_tribe(c)

    # Start the family back story for the character
    s = family.BackStory()
    # Parents and Siblings
    c.SetFamily(s)
    rpt += rpt_biological_parents(s)
    rpt += rpt_brood_parents(s)
    rpt += rpt_siblings(s)
    # Family Social Standing
    rpt += rpt_family_status(s)
    # Friends, Enemies and Romance
    c.SetFrenemiesAndRomance(s)
    rpt += rpt_frenemies_romance(s)

    # Name and Birthdate, Induction dates
    c.SetCharName(2)
    c.SetCharDates()
    rpt += rpt_identity(c)
    # Personality
    c.set_personality()
    rpt += rpt_personality(c)

    # Start the social back story for the character
    o = orgs.Organization()
    # Guild and Alliance
    c.SetGuildAlliance(o)
    rpt += rpt_guild(c)
    rpt += rpt_alliance(c)
    # Secret Society and Organization
    c.SetSecretSociety(o)
    rpt += rpt_secret_org(c)

    print rpt
    logging.info(rpt)

if __name__ == '__main__':
    testme()
