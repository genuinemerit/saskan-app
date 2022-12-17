#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file contains classes and functions for creating a personal and
family background for a character story.
"""
import sys
# Local packages
sys.path.append('../../web/app')
import main
from main import utils

# CLASS
# =========================

class BackStory:
    '''
    Methods and data for creating and managing a character back story
    in the game world.
    '''

    def __init__(self):
        '''
        Instantiate BackStory object.
        '''
        self.Parents = {}
        self.Siblings = {}
        self.FamilyStatus = {}
        self.Frenemies = {}
        self.Romance = {}

        self.ResetBackStory()

    def ResetBackStory(self):
        '''
        Initialize BackStory object.
        '''
        self.Parents = {'biological':{},
                        'brood':{'parentOne':{'gender':'', 'sex':''},
                                     'parentTwo':{'gender':'', 'sex':''} } }
        self.Siblings = {}
        self.FamilyStatus = {}
        self.Frenemies = {}
        self.Romance = {}

    def SetBasicParentData(self):
        '''
        Establish basic facts about the character's parental units
        '''
        # Are biological parents same as brood parents?
        # If not, are biological parents present?
        self.Parents['biological'] = {'father':{'same':True,'present':True}, 'mother':{'same':True,'present':True}}
        r = utils.random_100()
        if r < 51:
            r = utils.random_100()
            if r < 51:
                self.Parents['biological']['father']['same'] = False
                r = utils.random_100()
                if r < 51:
                    self.Parents['biological']['father']['present'] = False

            r = utils.random_100()
            if r < 51:
                self.Parents['biological']['mother']['same'] = False
                r = utils.random_100()
                if r < 51:
                    self.Parents['biological']['mother']['present'] = False

        # Are brood parents present?
        # Sex & gender of brood parents.
        self.Parents['brood'] = {'parentOne':{'present':True, 'sex':'M', 'gender':'M'},
                                     'parentTwo':{'present':True, 'sex':'F', 'gender':'F'} }

        # Parent #1 (father)
        if self.Parents['biological']['father']['same']:
            self.Parents['brood']['parentOne']['present'] = self.Parents['biological']['father']['present']
            self.Parents['brood']['parentOne']['sex'] = 'M'
            self.Parents['brood']['parentOne']['gender'] = 'M'
        else:
            r = utils.random_100()
            if r < 51:
                self.Parents['brood']['parentOne']['present'] = False
            r = utils.random_100()
            if r < 3:
                self.Parents['brood']['parentOne']['sex'] = 'F'
                self.Parents['brood']['parentOne']['gender'] = 'F'
            r = utils.random_100()
            if r < 3:
                if self.Parents['brood']['parentOne']['gender'] == 'M':
                    self.Parents['brood']['parentOne']['gender'] = 'F'
                else:
                    self.Parents['brood']['parentOne']['gender'] = 'M'

        # Parent #2 (mother)
        if self.Parents['biological']['mother']['same']:
            self.Parents['brood']['parentTwo']['present'] = self.Parents['biological']['mother']['present']
            self.Parents['brood']['parentTwo']['sex'] = 'F'
            self.Parents['brood']['parentTwo']['gender'] = 'F'
        else:
            r = utils.random_100()
            if r < 51:
                self.Parents['brood']['parentTwo']['present'] = False
            r = utils.random_100()
            if r < 3:
                self.Parents['brood']['parentTwo']['sex'] = 'M'
                self.Parents['brood']['parentTwo']['gender'] = 'M'
            r = utils.random_100()
            if r < 3:
                if self.Parents['brood']['parentTwo']['gender'] == 'F':
                    self.Parents['brood']['parentTwo']['gender'] ='M'
                else:
                    self.Parents['brood']['parentTwo']['gender'] = 'F'

        return self.Parents

    def SetParentRelationship(self):
        '''
        For present parents, define the the type of relationship
        '''
        def __setRelationship():
            '''
            Compute a relationship with a present parent
            '''
            relate = ''
            r = utils.random_100()
            if r < 5:
                relate = 'never met or does not remember'
            elif r < 71:
                relate = 'good relationship'
            else:
                relate = 'bad relationship'
            return relate

        def __setTragedy():
            '''
            Compute a story line for a missing parent
            '''
            tragedy = ''
            r = utils.random_100()
            if r < 11:
                tragedy = 'died in a war'
            elif r < 21:
                tragedy = 'died in an accident'
            elif r < 31:
                tragedy = 'was murdered or executed'
            elif r < 41:
                tragedy = 'is said to be in hiding'
            elif r < 51:
                tragedy = 'has amnesia, has forgotten this child'
            elif r < 61:
                tragedy = 'has never known this child'
            elif r < 71:
                tragedy = 'disappeared while on a mission'
            elif r < 81:
                tragedy = 'disappeared for an unknown reason'
            else:
                tragedy = 'at least once left the child with relatives for an extended period'

            return tragedy

        if self.Parents['biological']['father']['same'] == False:
            if self.Parents['biological']['father']['present']:
                self.Parents['biological']['father']['relationship'] = __setRelationship()
            else:
                self.Parents['biological']['father']['tragedy'] = __setTragedy()

        if self.Parents['biological']['mother']['same'] == False:
            if self.Parents['biological']['mother']['present']:
                self.Parents['biological']['mother']['relationship'] = __setRelationship()
            else:
                self.Parents['biological']['mother']['tragedy'] = __setTragedy()

        if self.Parents['brood']['parentOne']['present']:
            self.Parents['brood']['parentOne']['relationship'] = __setRelationship()
        else:
            self.Parents['brood']['parentOne']['tragedy'] = __setTragedy()

        if self.Parents['brood']['parentTwo']['present']:
            self.Parents['brood']['parentTwo']['relationship'] = __setRelationship()
        else:
            self.Parents['brood']['parentTwo']['tragedy'] = __setTragedy()

        return True

    def SetSiblings(self):
        '''
        Describe the character's siblings
        '''
        c = int(utils.random_100() / 10)
        if c < 8 and c > 0:
            self.Siblings['sibCount'] = c
            self.Siblings['sibs'] = []
            for s in range(1,c+1):
                # Relative age
                a = utils.random_100()
                age = ''
                if a < 51:
                    age = 'older'
                elif a < 91:
                    age = 'younger'
                else:
                    age = 'twin'
                # Feelings
                f = utils.random_100()
                feels = ''
                if f < 21:
                    feels = 'dislike'
                elif f < 41:
                    feels = 'friendly'
                elif f < 61:
                    feels = 'neutral'
                elif f < 81:
                    feels = 'very close'
                else:
                    feels = 'hatred'
                # Gender
                g = utils.random_100()
                if g < 51:
                    self.Siblings['sibs'].append([age + ' sister', feels])
                else:
                    self.Siblings['sibs'].append([age + ' brother', feels])
        else:
            self.Siblings['sibCount'] = 0

        return self.Siblings

    def SetFamilyStatus(self):
        '''
        Describe the standing/status of the (brood) family.
        '''
        self.FamilyStatus = {'socialClass':'Unknown', 'clanStatus':None,
                             'wealth':None, 'reputation':None}

        if self.Parents['brood']['parentOne']['present'] \
        or self.Parents['brood']['parentTwo']['present']:
            # Social class and family fortune
            r = utils.random_100()
            if r < 21:
                self.FamilyStatus['socialClass'] = 'low'
                self.FamilyStatus['wealth'] = 'poor'
            elif r < 61:
                self.FamilyStatus['socialClass'] = 'middle'
                m = utils.random_100()
                if m < 51:
                    self.FamilyStatus['wealth'] = 'low'
                else:
                    self.FamilyStatus['wealth'] = 'middle'
            elif r < 81:
                self.FamilyStatus['socialClass'] = 'upper'
                m = utils.random_100()
                if m < 51:
                    self.FamilyStatus['wealth'] = 'middle'
                else:
                    self.FamilyStatus['wealth'] = 'high'
            elif r < 91:
                self.FamilyStatus['socialClass'] = 'elite'
                m = utils.random_100()
                if m < 51:
                    self.FamilyStatus['wealth'] = 'high'
                else:
                    self.FamilyStatus['wealth'] = 'rich'
            else:
                self.FamilyStatus['socialClass'] = 'ruling'
                m = utils.random_100()
                if m < 51:
                    self.FamilyStatus['wealth'] = 'rich'
                else:
                    self.FamilyStatus['wealth'] = 'very-rich'
            # Clan or tribal status
            r = utils.random_100()
            if r < 11:
                self.FamilyStatus['clanStatus'] = 'outcast'
            elif r < 31:
                self.FamilyStatus['clanStatus'] = 'servant-caste'
            elif r < 61:
                self.FamilyStatus['clanStatus'] = 'worker-caste'
            elif r < 81:
                self.FamilyStatus['clanStatus'] = 'cadre-caste'
            elif r < 91:
                self.FamilyStatus['clanStatus'] = 'lower-nobility'
            else:
                self.FamilyStatus['clanStatus'] = 'upper-nobility'
            #Reputation
            r = utils.random_100()
            self.FamilyStatus['tragedy'] = None
            self.FamilyStatus['motive'] = None
            if r < 61:
                self.FamilyStatus['reputation'] = 'good'
            else:
                self.FamilyStatus['reputation'] = 'bad'
                r = utils.random_100()
                if r < 21:
                    self.FamilyStatus['tragedy'] = 'Family was betrayed and lost its fortune.'
                elif r < 41:
                    self.FamilyStatus['tragedy'] = 'Family members were exiled. The child has returned.'
                elif r < 61:
                    self.FamilyStatus['tragedy'] = 'Family members were imprisoned. The child has escaped.'
                elif r < 81:
                    self.FamilyStatus['tragedy'] = 'Family members were murdered. The child escaped.'
                elif r < 91:
                    self.FamilyStatus['tragedy'] = 'Family members vanished. Only the child remained.'
                else:
                    self.FamilyStatus['tragedy'] = 'Family business collapsed.'
                r = utils.random_100()
                if r < 21:
                    self.FamilyStatus['motive'] = 'Clear the family name and restore its honor.'
                elif r < 41:
                    self.FamilyStatus['motive'] = 'Live it down. Forget about the family tragedy.'
                elif r < 61:
                    self.FamilyStatus['motive'] = 'Hunt down those responsible and make them pay.'
                elif r < 81:
                    self.FamilyStatus['motive'] = 'Regain what is rightfully yours.'
                else:
                    self.FamilyStatus['motive'] = 'Rescue, save or help your remaining family if possible.'

            return self.FamilyStatus

    def SetFrenemies(self, CH):
        '''
        Provide an initial back story regarding the character's friends and enemines

        arg 1 = charisma score (max is 18)
        '''

        self.Frenemies = {}
        # Compute Valued Relationship
        r = utils.random_100()
        if r < 11:
            self.Frenemies['bestAlly'] = 'a parent'
        elif r < 21:
            if self.Siblings['sibCount'] > 0:
                self.Frenemies['bestAlly'] = 'a brother or sister'
            else:
                self.Frenemies['bestAlly'] = 'a cousin or family friend'
        elif r < 31:
            self.Frenemies['bestAlly'] = 'a lover'
        elif r < 41:
            self.Frenemies['bestAlly'] = 'a friend'
        elif r < 51:
            self.Frenemies['bestAlly'] = 'yourself'
        elif r < 61:
            self.Frenemies['bestAlly'] = 'an un-shaped sentient creature (a pet)'
        elif r < 71:
            self.Frenemies['bestAlly'] = 'a teacher or mentor'
        elif r < 81:
            self.Frenemies['bestAlly'] = 'a personal hero'
        elif r < 91:
            self.Frenemies['bestAlly'] = 'a public figure or leader'
        else:
            self.Frenemies['bestAlly'] = 'no one'
        # Compute Friends
        self.Frenemies['friendCnt'] = 0
        if CH < 10:
            self.Frenemies['friendCnt'] = 0
        elif CH < 13:
            self.Frenemies['friendCnt'] = 1
        elif CH < 16:
            self.Frenemies['friendCnt'] = 2
        else:
            self.Frenemies['friendCnt'] = 3
        if self.Frenemies['friendCnt'] > 0:
            self.Frenemies['friends'] = []
            for f in range(1,self.Frenemies['friendCnt']+1):
                r = utils.random_100()
                # species
                humani = ''
                if r < 51:
                    humani = 'human-appearing '
                else:
                    humani = 'non-human-appearing '
                # relationship
                relate = ''
                r = utils.random_100()
                if r < 11:
                    relate = 'like family'
                elif r < 21:
                    relate = 'childhood friend'
                elif r < 31:
                    relate = 'family friend'
                elif r < 41:
                    relate = 'like a big brother/sister'
                elif r < 51:
                    relate = 'like a kid brother/sister'
                elif r < 61:
                    relate = 'teacher/mentor'
                elif r < 71:
                    relate = 'like a parent'
                elif r < 81:
                    relate = 'partner or co-worker'
                elif r < 91:
                    relate = 'former lover'
                else:
                    relate = 'former enemy'
                # gender
                r = utils.random_100()
                if r < 51:
                    gender = 'male'
                else:
                    gender = 'female'

                self.Frenemies['friends'].append([humani + ' ' + gender, relate])

        # Compute Enemies
        self.Frenemies['enemyCnt'] = 0
        if CH > 15:
            self.Frenemies['enemyCnt'] = 0
        elif CH > 12:
            self.Frenemies['enemyCnt'] = 1
        elif CH > 9:
            self.Frenemies['enemyCnt'] = 2
        else:
            self.Frenemies['enemyCnt'] = 3
        if self.Frenemies['enemyCnt'] > 0:
            self.Frenemies['enemies'] = []
            for f in range(1,self.Frenemies['enemyCnt']+1):
                r = utils.random_100()
                # species
                humani = ''
                if r < 51:
                    humani = 'human-appearing '
                else:
                    humani = 'non-human-appearing '
                # gender
                r = utils.random_100()
                if r < 51:
                    gender = 'male'
                else:
                    gender = 'female'
                # relationship
                relate = ''
                r = utils.random_100()
                if r < 31:
                    relate = 'enemy agent or warrior'
                elif r < 41:
                    relate = 'ex-friend'
                elif r < 51:
                    relate = 'ex-lover'
                elif r < 61:
                    relate = 'estranged relative'
                elif r < 71:
                    relate = 'childhood rival'
                elif r < 91:
                    relate = 'superior or other high official'
                else:
                    relate = 'ex-coworker or partner'
                # feelings
                feels = ''
                r = utils.random_100()
                if r < 41:
                    feels = 'enemy hates character'
                elif r < 71:
                    feels = 'character hates enemy'
                else:
                    feels = 'mutual hatred'
                # story
                r = utils.random_100()
                if r < 11:
                    story = 'one caused the other to lose face'
                elif r < 21:
                    story = 'one caused the other to lose a friend, relative or lover'
                elif r < 31:
                    story = 'one humiliated the other'
                elif r < 41:
                    story = 'one accused the other of a personal flaw'
                elif r < 51:
                    story = 'one hurt the other physically'
                elif r < 61:
                    story = 'one deserted or betrayed the other'
                elif r < 71:
                    story = 'one turned down a job or romantic offer from the other'
                elif r < 81:
                    story = 'one causes the imprisonment or exile or the other'
                elif r < 91:
                    story = 'one foiled a plan of the other'
                else:
                    story = 'one was a romantic rival of the other'
                # behave
                r = utils.random_100()
                behave = ''
                if r < 21:
                    behave = 'rage and physically attack'
                elif r < 41:
                    behave = 'avoid'
                elif r < 61:
                    behave = 'seek to indirectly injure'
                elif r < 81:
                    behave = 'ignore'
                else:
                    behave = 'verbally assault'

                self.Frenemies['enemies'].append([humani + ' ' + gender, relate, feels, story, behave])

    def SetRomance(self, SO, charGender):
        '''
        Define the character's romantic back story, relationship MO, and
        so forth.

        arg 1 = sexual orientation is a tuple:  kinsey-score, description
        arg 2 = charGender:  one of -- male, female, androgynous
        '''
        oppSex = {'male':'female', 'female':'male', 'androgynous':'androgynous'}
        self.Romance = {}

        # Basic story line
        r = utils.random_100()
        if r < 31:
            # Involved...
            self.Romance['status'] = 'in a relationship'
            # Lover's gender
            if SO[0] < 4:
                self.Romance['loveGender'] = oppSex[charGender]
            elif SO[0] > 7:
                self.Romance['loveGender'] = charGender
            else:
                g = utils.random_100()
                if g < 51:
                    self.Romance['loveGender'] = 'male'
                else:
                    self.Romance['loveGender'] = 'female'
            # In a relationship
            r = utils.random_100()
            relate = ''
            if r < 11:
                self.Romance['relate'] = 'friends/family of lover hate character'
            elif r < 21:
                self.Romance['relate'] = 'friends/family of lover would harm character'
            elif r < 31:
                self.Romance['relate'] = 'friends/family of character hate lover'
            elif r < 41:
                self.Romance['relate'] = 'either character or lover have a rival'
            elif r < 51:
                self.Romance['relate'] = 'currently separated'
                self.Romance['status'] = 'in a relationship but separated'
            elif r < 61:
                self.Romance['relate'] = 'always fighting'
            elif r < 71:
                self.Romance['relate'] = 'everything is great'
            elif r < 81:
                self.Romance['relate'] = 'either character or lover gets insanely jealous'
            elif r < 91:
                self.Romance['relate'] = 'involed in a romantic triangle'
            else:
                self.Romance['relate'] = 'either character or lover is also seeing someone else'
        elif r < 71:
            # Uninvolved currently
            self.Romance['status'] = 'single'
            # Seeking gender
            if SO[0] < 4:
                self.Romance['loveGender'] = oppSex[charGender]
            elif SO[0] > 7:
                self.Romance['loveGender'] = charGender
            else:
                g = utils.random_100()
                if g < 51:
                    self.Romance['loveGender'] = 'male'
                else:
                    self.Romance['loveGender'] = 'female'
            # Relationship standards/needs/relate
            r = utils.random_100()
            if r < 21:
                self.Romance['relate'] = 'anything that moves'
            elif r < 41:
                self.Romance['relate'] = 'looking for the right love-connection soul-mate'
            elif r < 61:
                self.Romance['relate'] = 'no time to waste on romance'
            elif r < 81:
                self.Romance['relate'] = 'not looking for anything serious'
            else:
                self.Romance['relate'] = 'hoping to reconnect with an old flame'

        else:
            # Single due to tragic love affair
            self.Romance['status'] = 'recovering from tragic love affair'
            # that occurred when...
            r = utils.random_100()
            if r < 21:
                self.Romance['relate'] = 'in childhood'
            elif r < 41:
                self.Romance['relate'] = 'in youth'
            elif r < 61:
                self.Romance['relate'] = 'within last 5 years'
            elif r < 81:
                self.Romance['relate'] = 'within last 5 months'
            else:
                self.Romance['relate'] = 'within last 5 weeks'
            # Ex-lover's gender
            if SO[0] < 4:
                self.Romance['loveGender'] = oppSex[charGender]
            elif SO[0] > 7:
                self.Romance['loveGender'] = charGender
            else:
                g = utils.random_100()
                if g < 51:
                    self.Romance['loveGender'] = 'male'
                else:
                    self.Romance['loveGender'] = 'female'
            # What caused the tragedy
            r = utils.random_100()
            if r < 11:
                self.Romance['tragedy'] = 'lover killed in a war'
            elif r < 21:
                self.Romance['tragedy'] = 'lover killed by accident'
            elif r < 31:
                self.Romance['tragedy'] = 'lover mysteriously vanished'
            elif r < 41:
                self.Romance['tragedy'] = 'love-attraction just faded away'
            elif r < 51:
                self.Romance['tragedy'] = 'a personal mission separated lovers'
            elif r < 61:
                self.Romance['tragedy'] = 'lover was kidnapped or imprisoned'
            elif r < 71:
                self.Romance['tragedy'] = 'lover committed suicide'
            elif r < 81:
                self.Romance['tragedy'] = 'social pressure or relatives forced lovers apart'
            elif r < 91:
                self.Romance['tragedy'] = 'lover joined an enemy organization or plan'
            else:
                self.Romance['tragedy'] = 'a rival stole lover from character'
            # Feelings
            r = utils.random_100()
            if r < 11:
                self.Romance['feels'] = 'lover still loves character'
            elif r < 21:
                self.Romance['feels'] = 'character still loves lover'
            elif r < 31:
                self.Romance['feels'] = 'still love each other'
            elif r < 41:
                self.Romance['feels'] = 'character hates ex-lover'
            elif r < 51:
                self.Romance['feels'] = 'ex-lover hates character'
            elif r < 61:
                self.Romance['feels'] = 'hate each other'
            elif r < 71:
                self.Romance['feels'] = 'are now good friends'
            elif r < 81:
                self.Romance['feels'] = 'no more feelings either positive or negative'
            elif r < 91:
                self.Romance['feels'] = 'character likes ex-lover but ex-lover hates character'
            else:
                self.Romance['feels'] = 'ex-lover likes character but character hates ex-lover'

        return self.Romance

def main():
    '''
    For testing...
    '''


if __name__ == '__main__':
    # main()
    pass

