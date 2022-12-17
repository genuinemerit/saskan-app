#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Classes and functions for generating names of players and places.
This will continue to grow and develop over time. It uses external services.

Character names
===============

Select, or at least suggest, a character name.  This is a very complex area
and will no doubt require modification and tweaking and extension over time.
To begin with, will try to use a few good existing name randomizer services.

DEV Notes:

What I'd like to do is first identify the Clan and Tribe, using a base set of
clan and tribe names.

I'd like to vary the number of names assigned according to the social status of
the family. Characters from higher-class families get more names.  Characters
from lower-class families get shorter and more unusual names.  Same for players
who are less human.

Would like to further randomize the types of names generated in general.
The behindthename service is great, but tends towards Euro-style mixes.
The fantasynamegen services is also great, offering interesting options.
"""
import cStringIO
import pycurl
import random
import sys
# Local packages
sys.path.append('../../web/app')
from main import utils

def connect_to_site(namegen_url, buf):
    '''
    Use CURL to connect and retreive the web content.
    namegen_url is properly formatted URL to retreive name info.
    buf is cStringIO.StringIO object
    '''
    connect_ok = True
    curl = pycurl.Curl()
    curl.setopt(curl.URL, namegen_url)
    curl.setopt(curl.WRITEFUNCTION, buf.write)
    # Time out if the connection phase takes more than n seconds
    curl.setopt(curl.CONNECTTIMEOUT, 6)
    # Time out if the entire transaction takes more than nn seconds
    curl.setopt(curl.TIMEOUT, 12)
    try:
        curl.perform()
    except pycurl.error, error:
        errno, errstr = error
        print 'ERROR: No name generated. Connection timed out to: ' \
              + namegen_url
        print 'CURL error number: ', errno, '; message: ', errstr
        print 'Status: %d' % curl.getinfo(curl.RESPONSE_CODE)
        print 'Status: %f' % curl.getinfo(curl.TOTAL_TIME)
        connect_ok = False
    finally:
        curl.close()

    return (connect_ok, buf)

def behind_the_name(gender='u', name_count=1, surname=''):
    '''
    @param gender is 'male', 'female' or anything else
    @param name_count is the number of "first names". Maximum is 6.
    @param surname can optionally be specified in the call,
        otherwise it is generated randomly

    www.behindthename.com/random/ provides a very nice open GET method.
    They also have a registered API service. See:
        http://www.behindthename.com/api/

    How to call the behindthename service:
    The base URL is:
        http://www.behindthename.com/random/random.php

    Use a specified surname (Quinn), ambiguous, all categories, one middle name:
        ?number=2&gender=u&surname=Quinn&all=yes

    Use a random surname, masculine, all categories, one middle name:
        ?number=2&gender=m&surname=&randomsurname=yes&all=yes

    Use a random surname, feminine, all categories, one middle name:
        ?number=2&gender=f&surname=&randomsurname=yes&all=yes

    Use a random surname, ambiguous, all categories, one middle name:
        ?number=2&gender=u&surname=&randomsurname=yes&all=yes

    Increment the number value to get more names in the name..to a maximum of 6
        ?number=6&gender=u&surname=Quinn&all=yes

    '''
    base_url = 'http://www.behindthename.com/random/random.php'
    character_name = ''
    # Verify valid name count
    name_count = utils.set_min_max(name_count, 1, 6)
    # Set gender for name URL
    name_gender = 'u'
    rgen = utils.random_100()
    if rgen > 75:
        if gender == 'male':
            name_gender = 'm'
        elif gender == 'female':
            name_gender = 'f'
    # Set surname settting
    if surname != '':
        namegen_url = base_url \
                      + '?number=' + str(name_count) \
                      + '&gender=' + name_gender \
                      + '&surname=' + surname \
                      + '&all=yes'
    else:
        namegen_url = base_url \
                      + '?number=' + str(name_count) \
                      + '&gender=' + name_gender \
                      + '&surname=&randomsurname=yes&all=yes'

    buf = cStringIO.StringIO()
    # Call the service
    (connect_ok, buf) = connect_to_site(namegen_url, buf)

    if connect_ok:
        parse_i = buf.getvalue().find('<span class="heavyhuge"')
        parse_txt = buf.getvalue()[parse_i:]
        buf.close()
        parse_i = parse_txt.find('</span>')

        parse_txt = parse_txt[:parse_i]
        parse_lines = parse_txt.strip().split('<a class="plain" href="')
        for p_line in range(1, len(parse_lines)):
            parse_words = parse_lines[p_line].split('/name/')
            parse_words = parse_words[1].split('>')
            parse_words = parse_words[1].split('<')
            character_name += parse_words[0] + ' '

        # Add surname if it was specified
        if surname != '':
            character_name += surname
        # Remove trailing space and convert HTML entities:
        character_name = utils.strip_html_entities(character_name)

    return character_name


def fantasy_name_gen(name_count=1, name_type='random'):
    '''
    This site offer a wide variety of options.  The arguments are visible
    but not as obvious as with behind_the_name

    This call generates a sizable number of invented fantasy names. Based on
    name_count, we pull from the generated list.  Naturally, the caller could
    mix and match to generate names according to various patterns.

    The types to choose from are:
    *  short
    *  medium
    *  long
    *  verylong
    *  heavy (lots of consonants)
    *  open (lots of vowels)
    *  even (alternating consonants and vowels
    *  apostrophe  (yes, names with apostrophes in them)
    *  insulting  (funny in a gross/juvenile kind of way)
    *  idiot (these are actually better than the "insulting" ones,
                  some of them are quite good)
    *  japanese
    * ... see nm_urls.keys() for full list
    *  any other values default to random, meaning one of the above is chosen

    As hinted at in the construction of the URL for japanese names,
    this is a rather sophisticated name generation tool.
    See rinkworks.com/namegen/instr.shtml for detailed info
    or rinkworks.com/namegen/reference.shtml
    for a quick reference.  Can do some very cool stuff with this!
    '''
    # Connection information, rules
    base_url = 'http://rinkworks.com/namegen/fnames.cgi?'
    nm_urls = {'short':'d=1&f=1',
               'medium':'d=1&f=2',
               'long':'d=1&f=3',
               'verylong':'d=1&f=4',
               'heavy':'d=1&f=5',
               'open':'d=1&f=6',
               'even':'d=1&f=7',
               'apostrophe':'d=1&f=8',
               'insulting':'d=1&f=11',
               'idiot':'d=1&f=14',
               'japanese':'d=1&f=(aka|aki|bashi|gawa|kawa|furu|fuku|fuji|'+ \
                          'hana|hara|haru|hashi|hira|hon|hoshi|ichi|iwa|' + \
                          'kami|kawa|ki|kita|kuchi|kuro|marui|matsu|miya|' + \
                          'mori|moto|mura|nabe|naka|nishi|no|da|ta|o|oo|' + \
                          'oka|saka|saki|sawa|shita|shima|i|suzu|taka|take|' + \
                          'to|toku|toyo|ue|wa|wara|wata|yama|yoshi|kei|ko|' + \
                          'zawa|zen|sen|ao|gin|kin|ken|shiro|zaki|yuki|' + \
                          'asa%29%28||||||||||bashi|gawa|kawa|furu|fuku|' + \
                          'fuji|hana|hara|haru|hashi|hira|hon|hoshi|chi|' + \
                          'wa|ka|kami|kawa|ki|kita|kuchi|kuro|marui|matsu|' + \
                          'miya|mori|moto|mura|nabe|naka|nishi|no|da|ta|o|' + \
                          'oo|oka|saka|saki|sawa|shita|shima|suzu|taka|' + \
                          'take|to|toku|toyo|ue|wa|wara|wata|yama|yoshi|' + \
                          'kei|ko|zawa|zen|sen|ao|gin|kin|ken|shiro|' + \
                          'zaki|yuki|sa)'
              }
    # Validate arguments
    name_count = utils.set_min_max(name_count, 1, 8)
    # Assign URL type
    if not name_type in nm_urls.keys():
        name_type = nm_urls.keys()[random.randint(0, len(nm_urls)-1)]
    # Generate a series of goofy names:
    character_name = ''
    cnames = []
    buf = cStringIO.StringIO()
    # Call the service
    (connect_ok, buf) = connect_to_site(base_url + nm_urls[name_type], buf)
    if connect_ok:
        # print 'Connection OK'
        parse_i = buf.getvalue().find("<table class='fnames_results'>")
        parse_txt = buf.getvalue()[parse_i:]
        buf.close()
        parse_i = parse_txt.find('</table>')
        parse_txt = parse_txt[:parse_i]
        find_td_i = 0
        while not find_td_i == -1:
            find_td_i = parse_txt.find('<td>')
            parse_txt = parse_txt[find_td_i:]
            parse_i = parse_txt.find('</td>')
            this_word = parse_txt[4:parse_i]
            this_word = this_word.strip()
            if this_word != '':
                this_word = cnames.append(this_word)
            parse_txt = parse_txt[parse_i:]

        cnlen = len(cnames)

        # If the variable is not used, just use an underscore:
        for _ in range(0, name_count):
            rname_i = random.randint(0, cnlen-1)
            character_name += cnames[rname_i] + ' '

        # Remove trailing space and convert HTML entities:
        character_name = utils.strip_html_entities(character_name)

    return str(character_name)


def create_surnames(name_count=10):
    '''
    @param name_count is the number of family names to generate.
    @return a list of one-word surnames

    Use case: Provide a standard set of clan or tribal names.
    For a particular game world, would save these to a database or file.
    '''
    name_types = ['normal',
                  'short',
                  'medium',
                  'long',
                  'normal',
                  'verylong',
                  'heavy',
                  'open',
                  'normal',
                  'even',
                  'idiot',
                  'japanese',
                  'normal']
    surnames = []
    for _ in range(0, name_count):
        name_words = []
        surname = ''
        # Randomly select a name type
        nm_typ = name_types[random.randint(0, len(name_types)-1)]
        if nm_typ == 'normal':
            # Generate name using behind_the_name service
            surname = behind_the_name('u', 1)
            name_words = str(surname).split(' ')
            surname = name_words[len(name_words)-1]
        else:
            # Generate name using fantasy_name_gen service
            surname = fantasy_name_gen(1, nm_typ)
        surnames.append(str(surname))
    return surnames


def testme():
    '''
    For testing...
    '''
    # print 'Test behind the names:'
    print behind_the_name()
    # print behind_the_name('female',1)
    # print behind_the_name('male',2)
    # print behind_the_name('intersex',3)
    # print behind_the_name('male',1,'Quinn')

    # print 'Test fantasy_name_gen:'
    print fantasy_name_gen(3, 'short')
    # print fantasy_name_gen(2, 'random')
    # print fantasy_name_gen(1, 'idiot')
    # print fantasy_name_gen(-3, 'long')
    # print fantasy_name_gen(6, 'heavy')
    # print fantasy_name_gen(2, 'open')
    # print fantasy_name_gen()
    # print fantasy_name_gen(3, 'even')
    # print fantasy_name_gen(1, 'apostrophe')
    # print fantasy_name_gen(2, 'insulting')
    # print fantasy_name_gen(1, 'verylong')
    print fantasy_name_gen(2, 'japanese')

    print create_surnames()

if __name__ == '__main__':
    testme()
    # pass
