#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file contains classes and functions for creating settings and objects
and configurations and whatnot for my totally awesome RPG world. It is
basically a quick substitute for a database and/or config files.  This
class deals with organizations, especially guilds, religions, clans,
tribes and secret societies.
"""
import random

# CLASS
# =========================

class Organization:
    '''
    Methods and data for managing Organizations in the game world.
    '''

    def __init__(self):
        '''
        Instantiate Organization object.
        In my default world, government and nation-state structures are
        fairly weak and local.  There are very few if any "imperial",
        much less "global" structures.
        However, there will be a need to manage organizations on almost
        any scale, including planetary, inter-planetary, galactic and
        heavenly/hellish.   All in good time...
        '''
        self.Guild = {
                       0: {'name':'Agents of the Sun',
                           'desc':'Special operations for human militia, Watchers officer corps',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},

                       1: {'name':'Day Watchers',
                           'desc':'Law enforcement, human militia, justice, criminal investigations',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},

                       2: {'name':'Heliocastric Specialists',
                           'desc':'Intelligence and technology organization for Heliocrastic/human command and control',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},

                       3: {'name':'Heliocastronic Offices',
                           'desc':'Elite, ruling ranks of Heliocratic organization, church and state leadership',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},

                       4: {'name':'Helioptic Innkeepers',
                           'desc':'Food, beverage and lodging, networking for humans only',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},

                       5: {'name':'Night Watchers',
                           'desc':'Criminal and political investigations, spy work, intelligence gathering, interrogations',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},

                       6: {'name':'Volunteers',
                           'desc':'Enforcement of virture and punishment of vice, morals policing, human supremacy militia',
                           'pro':['human'], 'neut':[], 'anti':['shaped', 'animal']},


                       7: {'name':'Heliocastric Scribes',
                           'desc':'Bureaucratic cadre for Heliocrastic organizations, correspondence, credit',
                           'pro':['human'], 'neut':['shaped'], 'anti':['animal']},

                       8: {'name':'Helioptic Brooders',
                           'desc':'Helioptic child care, communal kitchens, housekeeping, match-making for humans ony',
                           'pro':['human'], 'neut':['shaped'], 'anti':['animal']},

                       9: {'name':'Herders',
                           'desc':'Meat, dairy, and animal products for human and carnivore clients',
                           'pro':['human'], 'neut':['shaped'], 'anti':['animal']},

                       10: {'name':'Hunters',
                           'desc':'Fresh meat for carnivores, mercenaries, killers',
                           'pro':['human'], 'neut':['shaped'], 'anti':['animal']},

                       11: {'name':'Serfs and Farmers',
                           'desc':'Grains, vegetables, and other farm products, farm labor, animal-slave labor',
                           'pro':['human'], 'neut':['shaped'], 'anti':['animal']},


                       12: {'name':'Riders',
                           'desc':'Protection, transport, investigative services, import/export, mercenaries',
                           'pro':['human'], 'neut':['shaped', 'animal'], 'anti':[]},


                       13: {'name':'Actors',
                           'desc':'Entertainments, performances, jesters, stealth and disguises, language instruction',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       14: {'name':'Bakers',
                           'desc':'Supply baked goods, especially breads and grain-foods, to inns, institutions and individuals',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       15: {'name':'Bards',
                           'desc':'Musical and poetic entertainment and story-telling, teaching',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       16: {'name':'Carpenters and Candlemakers',
                           'desc':'Construction, building in stone and wood, furniture, crafts of all kinds',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       17: {'name':'Herbalists',
                           'desc':'Pharmceuticals and herbs of all types, medicinal, recreational and weaponized, medical advice',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       18: {'name':'Jewellers',
                           'desc':'Rare gems, decorative items, banking and credit, business intelligence services',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       19: {'name':'Shoppers',
                           'desc':'Investigative services, trade, access to some lower-cost rare artifacts',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       20: {'name':'Tailors',
                           'desc':'Woven and leather clothing mainly for human-appearing clients',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       21: {'name':'Toolmakers',
                           'desc':'All types of non-weapon, relatively low-technology tools and devices',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},

                       22: {'name':'Vintners',
                           'desc':'Supply alcoholic and other potions to inns, institutions and individuals',
                           'pro':['human', 'shaped'], 'neut':['animal'], 'anti':[]},


                       23: {'name':'Armorers',
                           'desc':'Low-tech weapons to all clients',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       24: {'name':'Brewers',
                           'desc':'Mildly alcoholic and other popular drinks, including water-provisioning and -divining',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       25: {'name':'Cobblers',
                           'desc':'Creation and repair of foot and hoof and similar apparel',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       26: {'name':'Elders',
                           'desc':'Story-telling, knowledge transfer, village leaders, clan leaders, intelligence gathering',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       27: {'name':'Finders',
                           'desc':'Intelligence gathering, locating rare artifacts, exchange in rare goods',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       28: {'name':'Free Innkeepers',
                           'desc':'Food, beverage and lodging, access to entertainments and meeting-places, networking',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       29: {'name':'Harpers',
                           'desc':'Musical instruments and accompaniments, musical theory, dream interpretation, hypnosis',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       30: {'name':'Healers',
                           'desc':'Medicine and psychological counseling',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       31: {'name':'Miners',
                           'desc':'Raw materials for construction and crafts of all types',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},

                       32: {'name':'Sailors',
                           'desc':'Sea-faring, import/export, astronomical and geographical knowledge',
                           'pro':['human', 'shaped', 'animal'], 'neut':[], 'anti':[]},


                       33: {'name':'Free Brooders',
                           'desc':'Non-Helioptic child care, communal kitchens, housekeeping and match-making',
                           'pro':['human', 'animal'], 'neut':['shaped'], 'anti':[]},

                       34: {'name':'Birthers',
                           'desc':'Childbirth, abortions, contraceptives, sex magick, healing, womens health',
                           'pro':['human', 'animal'], 'neut':['shaped'], 'anti':[]},


                       35: {'name':'Scanners',
                           'desc':'Psychiatric and psychological counseling, investigative services, spells and curses',
                           'pro':['shaped'], 'neut':['human', 'animal'], 'anti':[]},

                       36: {'name':'Windriders',
                           'desc':'Protection, investigative, justice and transport services',
                           'pro':['shaped'], 'neut':['human', 'animal'], 'anti':[]},


                       37: {'name':'Astrologers',
                           'desc':'Prognostication, astronomical knowledge, specialized knowledge regarding flight',
                           'pro':['shaped', 'animal'], 'neut':['human'], 'anti':[]},

                       38: {'name':'Free Scribes',
                           'desc':'Reading, correspondence, translations, intelligence gathering',
                           'pro':['shaped', 'animal'], 'neut':['human'], 'anti':[]},

                       39: {'name':'Mages',
                           'desc':'Spiritual advice, proganostication, magical spells and charms, animal medicine',
                           'pro':['shaped', 'animal'], 'neut':['animal'], 'anti':[]},


                       40: {'name':'Free Farmers',
                           'desc':'Grains, vegetables and so forth produced without serf/slave labor',
                           'pro':['animal'], 'neut':['human', 'shaped'], 'anti':[]},

                       41: {'name':'Free Hunters',
                           'desc':'Fresh meat for carnivores, mercenaries, killers',
                           'pro':['animal'], 'neut':['shaped'], 'anti':['human']}
                     }

        self.Alliance = {
                          0:{'name':'Helioptic Union',
                             'aliases':['Sun Guilds',
                                        'Watchers',
                                        'Flicks',
                                        'Lions Club'],
                             'members':['Night Watchers',
                                        'Day Watchers',
                                        'Volunteers',
                                        'Helioptic Brooders',
                                        'Helioptic Innkeepers',
                                        'Agents of the Sun',
                                        'Heliocastric Specialists',
                                        'Heliocratic Scribes',
                                        'Heliocastronic Offices'],
                             'classes':['governance', 'police/militia', 'popular trades', 'nobility'],
                             'desc':'Ruling bodies, human-supremacist, theocratic, sponsors festivals',
                             'religions':['Heliopticonism']
                             },

                          1:{'name':'The Five Guilds',
                             'aliases':['2+3',
                                        'The Five',
                                        'Fivers',
                                        'The Hand of Man',
                                        'The Pyramid',
                                        'Lead Craft Guilds'],
                             'members':['Windriders',
                                        'Tailors',
                                        'Toolmakers',
                                        'Herbalists',
                                        'Jewellers'],
                             'classes':['elite crafts', 'police/militia', 'nobility'],
                             'desc':'Wealthy, independent, human-centric, sponsors festivals',
                             'religions':None
                             },

                          2:{'name':'The Old Guild Alliance',
                             'aliases':['The Ancients',
                                        'Wanderers'],
                             'members':['Sailors',
                                        'Elders',
                                        'Finders'],
                             'classes':['governance', 'intelligentsia', 'elite merchants', 'lower nobility'],
                             'desc':'Traditionalist and esoteric, associated with old ways and secrets, shadowy connections',
                             'religions':['Josism',
                                          'Dulunism',
                                          'Receptumism',
                                          'Hodorea']
                            },

                          3:{'name':'The Candlemakers Craft Hall',
                             'aliases':['Makers',
                                        'The Three Lights',
                                        'The Triplets',
                                        'The Triangle'],
                             'members':['Carpenters and Candlemakers',
                                        'Armorers',
                                        'Cobblers'],
                             'classes':['popular crafts', 'workers', 'middle-class'],
                             'desc':'Less-elite craft guilds, suppliers to all, business-like, avoid trouble, sponsor festivals',
                             'religions':None
                            },

                          4:{'name':'Free Hosteleries Cooperative',
                             'aliases':['Foodies',
                                        'Riderfolk',
                                        'Festivales'],
                             'members':['Riders',
                                        'Bards',
                                        'Actors',
                                        'Harpers',
                                        'Free Innkeepers',
                                        'Vintners',
                                        'Brewers',
                                        'Bakers'],
                             'classes':['popular trades', 'police/militia', 'middle-class'],
                             'desc':'Entertainment, associated with traditional festivals, independent, shadowy connections',
                             'religions':['Heliopticonism',
                                          'Josism']
                            },

                          5:{'name':'Provisioners Corporation',
                             'aliases':['Toilers',
                                        'Workers'],
                             'members':['Serfs and Farmers',
                                        'Hunters',
                                        'Herders',
                                        'Miners',
                                        'Shoppers'],
                             'classes':['industrial trades', 'merchants', 'workers', 'toilers', 'servants'],
                             'desc':'Supply-chain, industrial goods, human-centric, shadowy connections',
                             'religions':['Josism',
                                          'Dulunism']
                            },

                          6:{'name':'The New Guild Alliance',
                             'aliases':['The Life League',
                                        'Wooters'],
                             'members':['Birthers',
                                        'Free Brooders',
                                        'Healers',
                                        'Scanners',
                                        'Free Scribes'],
                             'classes':['popular trades', 'poor workers', 'intelligentsia'],
                             'desc':'Eclectic and esoteric, woman-centric, quietly rebellious and contrarian',
                             'religions':['Josism',
                                          'Dulunism',
                                          'Receptumism']
                            },

                          7:{'name':'The Night Hall',
                             'aliases':['The Dark Riders',
                                        'Stargazers',
                                        'The Nameless',
                                        'Moonies',
                                        'Esoteric Guilds',
                                        'The Fair Wind'],
                             'members':['Astrologers',
                                        'Mages',
                                        'Free Farmers',
                                        'Free Hunters'],
                             'classes':['popular trades', 'poor workers', 'toilers', 'intelligentsia'],
                             'desc':'Esoteric, occult, deep learning and secrets, contentious, opposed to human order',
                             'religions':['Dulunism']
                            }
                        }
        self.Societies = { 0: {'name':'Santagraal',
                               'aliases':['Old Timers Club',
                                          'The Order of Blood',
                                          'Restorationists'],
                               'desc':'Recovery and restoration of old ways. Peaceful end to DNA-mixing and evolution shaping.',
                               'alliances': ['Free Hosteleries Cooperative',
                                             'The New Guild Alliance'],
                               'orgs': { 0: {'name':'The Receivership',
                                             'aliases':['The Book Club'],
                                             'desc':'Historical knowledge gathering and transfer, literacy'},
                                         1: {'name':'The Companions',
                                             'aliases':['The Kennel', 'The Farm'],
                                             'desc':'Re-training animals to be happy as subservients and pets'},
                                         2: {'name':'The Vaccinators',
                                             'aliases':['The Way Back'],
                                             'desc':'Medical and spritual treatments for reversal of shaped evolution'},
                                       }
                              },

                           1: {'name':'Vannasuul',
                               'aliases':['The Far Wind',
                                          'The Dark Elves',
                                          'The Federation'],
                               'desc':'Mutant ascendancy. Alliance with extra-terrestial forces. Planetary exodus.',
                               'alliances': ['The New Guild Alliance',
                                             'The Night Hall'],
                               'orgs': { 0: {'name':'Lamoru',
                                             'aliases':['Sky Spell'],
                                             'desc':'First outer order, reading-the-stars, basic math, astronomy and navigation'},
                                         1: {'name':'Bin Fybkis',
                                             'aliases':['Dragon Riders'],
                                             'desc':'Second outer order, advanced astronomy and math, basic geology and chemistry'},
                                         2: {'name':'Laffe Lusok',
                                             'aliases':['Caravan to the South'],
                                             'desc':'Third outer order, basic physics, history of mankind'},
                                         3: {'name':'Hossaron',
                                             'aliases':['Weather Watch'],
                                             'desc':'Fourth outer order, weather prediction, astro-physics'},
                                         4: {'name':'Arko Hetobi',
                                             'aliases':['The Midnight Monster'],
                                             'desc':'First inner order, initiation to inner circle, quantum mechanics and nuclear physics'},
                                         5: {'name':'Tlinkit Mankata',
                                             'aliases':['The Magickal Medicine'],
                                             'desc':'Second inner order, bio-chemistry, molecular biology, genomics, intro evolution shaping'},
                                         6: {'name':'Oribbisiffi',
                                             'aliases':['The Northern Mirror'],
                                             'desc':'Third inner order, electronics, advanced relativity, tachyon theory, suspension methods'},
                                         7: {'name':'Lunanniruka',
                                             'aliases':['The Moons Throne'],
                                             'desc':'Fourth inner order, space elevator, space station, moon base, space travel'}
                                       }
                              },

                           2: {'name':'Yaarareea',
                               'aliases':['Adamantites',
                                          'Invisible College'],
                               'desc':'Promotion of wisdom and enlightenment. End to suffering and violence. Healing, transendence.',
                               'alliances': ['The Five Guilds',
                                             'The Old Guild Alliance',
                                             'The New Guild Alliance'],
                               'orgs': { 0: {'name':'Sithaa Viriyaa',
                                             'aliases':['The Good Old School', 'The Doctrine of Analysis', 'Boneshakers'],
                                             'desc':'Entry-level. Simple breathing, fundamentals of meditation and accumulating merit'},
                                         1: {'name':'Mahi Sassaka',
                                             'aliases':['The Blue Robes'],
                                             'desc':'Focus on separating monk-practitioners from daily routines. Training monks.'},
                                         2: {'name':'Kassya People',
                                             'aliases':['The White Robes'],
                                             'desc':'Focus on healing, calming meditations. Monks engaged in pro-peace actions'},
                                         3: {'name':'Himavanti',
                                             'aliases':['The Jetavana', 'The Hidden Monks'],
                                             'desc':'Retreat from the world.  Meditating remotely. Creation of remote monastaries.'},
                                         4: {'name':'Madyammi',
                                             'aliases':['The Empty Vessel', 'The Big Wheel'],
                                             'desc':'Promote meditation on the nature of emptiness, impermanence and interconnectedness.'},
                                         5: {'name':'Yogini',
                                             'aliases':['The Third Wheel', 'School of Pure Being', 'Pure Mind School'],
                                             'desc':'Promote meditations on and interpretations of ultimate realities, visiting heavens and dieties.'},
                                         6: {'name':'Patna Maidan',
                                             'aliases':['The Seven Sisters', 'The Regular-Folks Forum'],
                                             'desc':'Focus on ultimate truths being revealed by extraordinary practitioners from the lowest classes.'},
                                         7: {'name':'Vejjarama',
                                             'aliases':['The Path of the Cause'],
                                             'desc':'Focus on exercising the all-wise nature of all-beings through skillful means. Guru-centric.'}
                                       }
                               },

                           3: {'name':'Bitama',
                               'aliases':['Hashishim',
                                          'Assassins League',
                                          'The Outfit'],
                               'desc':'Money, ideological obsessions, sometimes justice.',
                               'alliances': ['Helioptic Union',
                                             'The Candlemakers Craft Hall',
                                             'Provisioners Corporation',
                                             'The Night Hall',
                                             'Free Hosteleries Cooperative'],
                               'orgs': { 0: {'name':'Intani Sakel',
                                             'aliases':['The Killers Hands', 'The Keepers Friends'],
                                             'desc':'Almost respectable, diverse, highly organized, business-like' },
                                         1: {'name':'Hamhim op Toa',
                                             'aliases':['Uncles Workshop', 'The Dispatchers'],
                                             'desc':'Small-time, debt-settlers, friend-of-the-village-chief' },
                                         2: {'name':'Exterminators',
                                             'aliases':['The Western Army'],
                                             'desc':'Merecenaries, heavily-armed, massacres' },
                                         3: {'name':'Kilikon Mina',
                                             'aliases':['The Holy Looters', 'Silent But Deadly'],
                                             'desc':'Extremely dangerous, inside jobs, evil cult, assassinations' },
                                         4: {'name':'Ferel Simari',
                                             'aliases':['Windy Dogs', 'Wild Wolves'],
                                             'desc':'Barbarians, anti-human, beserkers' },
                                         5: {'name':'Yka Ronen',
                                             'aliases':['High Binders', 'Quiet Stranglers'],
                                             'desc':'Garrotting, vendettas, assassins for assassins, pub owners' },
                                         6: {'name':'Alcedamites',
                                             'aliases':['The Whackers'],
                                             'desc':'Cheap killers, drug-addled, non-professional' },
                                         7: {'name':'Feralites',
                                             'aliases':['Metal Heads', 'The Iron Hand'],
                                             'desc':'Mysterious, possibly-legend, machines, drones, liquid metal ninjas' }
                                       }
                              },

                           4: {'name':'Basimi',
                               'aliases':['Thieves Guilds',
                                          'Snake Lodge'],
                               'desc':'Money, materialism and sometimes redistribution.',
                               'alliances': ['The Five Guilds',
                                             'The Old Guild Alliance',
                                             'Free Hosteleries Cooperative'],
                               'orgs':{0: {'name':'Ankat Sunin',
                                           'aliases':['Lawless Intelligence', 'Merry Band'],
                                           'desc':'Skillful, good-natured, legendary, support the poor'},
                                       1: {'name':'Ker en Totak',
                                           'aliases':['Magick and Honor', 'The Honor Society', 'Army of the Poor'],
                                           'desc':'Rebels, support the poor, anti-slavery, torment the rich'},
                                       2: {'name':'Koret Sakel',
                                           'aliases':['The Black Hand', 'Cutty Bastards'],
                                           'desc':'Extortion, protection rackets, violent'},
                                       3: {'name':'Nerb Iro',
                                           'aliases':['The Blue Home', 'The Picayunes', 'The Small Hands'],
                                           'desc':'Pick-pockets, con-artists, petty thieves'},
                                       4: {'name':'Buccaneers',
                                           'aliases':['The Highway Women'],
                                           'desc':'Highway bandits, pirates, support for women'},
                                       5: {'name':'Hetobne Kult',
                                           'aliases':['Midnight Riders', 'The Family', 'Black Meadows', 'Choc'],
                                           'desc':'Nomads, travellers, clever cons, leaderless'},
                                       6: {'name':'Lusok Tufa',
                                           'aliases':['Caravanners', 'Picaroons', 'The Players Club'],
                                           'desc':'Rigged games of chance, elaborate long cons'},
                                       7: {'name':'Corsairs',
                                           'aliases':['Men of Mayhem', 'Fight Club'],
                                           'desc':'Bash and grab, high-tech weapons, pro-shaped'},
                                       8: {'name':'Society of Autolycus',
                                           'aliases':['Thuggi', 'Murder, Inc.', 'The Gorillas'],
                                           'desc':'Stick-ups, highway robbery, brawlers, audacious, pro-animal'},
                                       9: {'name':'Telu en Botu',
                                           'aliases':['Boots and Bones', 'The Insiders', 'The Doctors'],
                                           'desc':'High-level organized crime, blackmail, corruption, black market'},
                                       10: {'name':'Whitefriars Club',
                                           'aliases':['Masters of Disguise', 'Dark Actors'],
                                           'desc':'Classy, polite, cat-burglars, infiltrators, elaborate robberies and cons'} }
                              },

                           5: {'name':'Raokasannum',
                               'aliases':['Gate of the Animals',
                                          'Animal Liberation Fronts',
                                          'Animal Liberation Armies',
                                          'Animal Farms',
                                          'Animal Justice Leagues'],
                               'desc':'Animal ascendancy. Suppression of human privilege. Revenge. Justice. Humor',
                               'alliances': ['The Night Hall'],
                               'orgs': { 0:{'name':'Lissambia United',
                                            'aliases':['The Frog Kings', 'Tetrapod Front'],
                                            'desc':'Advocates for frogs, newts, salamanders and so on. Loud, seldom violent.'},
                                         1:{'name':'Birds of a Feather',
                                            'aliases':['The Yardbirds'],
                                            'desc':'Advocates for yardbirds, groundbirds, hummingbird and woodpeckers. Diverse, contentious.'},
                                         2:{'name':'Flying Tigers',
                                            'aliases':['Death From Above'],
                                            'desc':'Militant birds of prey and owls. Usually lone actors. Very extreme, very dangerous.'},
                                         3:{'name':'Tide of Justice Alliance',
                                            'aliases':['The Swim Team'],
                                            'desc':'Lesser fish and swimming, wading, shore and sea birds mainly working out their own problems.'},
                                         4:{'name':'Water Worlders',
                                            'aliases':['Shark Supremacists', 'Octo-corp'],
                                            'desc':'Large marine animals coalition dominated by sharks and octopuses. Seek a drowned world.'},
                                         5:{'name':'Arani-Coleopteric Union',
                                            'aliases':['Association for the Advancement of Spiders and Bugs', 'Icky-corp'],
                                            'desc':'Loose coalition of spiders and beetles advocating against discrimination and stereotyping'},
                                         6:{'name':'Buzz for Freedom',
                                            'aliases':['Flying Bugs Union'],
                                            'desc':'Amorphous mass-social/artistic movement of butterflies, flies, bugs, and cicadas.'},
                                         7:{'name':'Sting for Freedom',
                                            'aliases':['Bees and Bugs Revolutionary Army'],
                                            'desc':'Extremely militant cells of bees, wasps, grasshoppers, cockroaches, mantis, locusts, etc.'},
                                         8:{'name':'We Are The Ones',
                                            'aliases':['Mammals United', 'Furballs'],
                                            'desc':'Umbrella group for the protection of all evolved mammals.  Mammal-supremacists.'},
                                         9:{'name':'Cats',
                                            'aliases':['Hairball Brigades', 'Lions and Tigers'],
                                            'desc':'Feline-supremacists uniting all cats. Anti-vegetarian. Sectarian. Occasionally very militant, but will always negotiate.'},
                                         10:{'name':'Foxes and Friends',
                                            'aliases':['We Are Not Cats', 'Anti-Cat Coalition'],
                                            'desc':'Anti-feline, anti-squirrel, anti-rabbit movement spearheaded by red foxes. Mainly foxes, some coyotes, dogs and wolverines. Cunning. Murderous against squirrel and rabbit uprisings.'},
                                         11:{'name':'Anti-Slavery Movement',
                                            'aliases':['Rebel Horse Army', 'Free Hooves Movement', 'Vegetarian Animal League'],
                                            'desc':'Hooved mammals opposed to all animal enslavement and animal-consumption, whether animals are evolved or not. Militant vegetarians.'},
                                         12:{'name':'Marine Pro-Life Coalition',
                                            'aliases':['Whales R Us'],
                                            'desc':'Legendary group of large marine mammal intelligentsia. Make rare profound proclamations about sentient enlightenment then vanish again.'},
                                         13:{'name':'Rabbit Liberation Front',
                                            'aliases':['The RLF'],
                                            'desc':'Extremely militant vegetarian-communist ideologues. Mostly engage in highway robberies and frequent uprisings.'},
                                         14:{'name':'Rabbit Liberation Front (Revolutionary)',
                                            'aliases':['The RLF(R)'],
                                            'desc':'Extremely militant vegetarian-communist ideologues. Mostly engage in robberies against the RLF, plus regular uprisings.'},
                                         15:{'name':'Real Revolutionary Rabbit Liberation Front',
                                            'aliases':['The RRRLF'],
                                            'desc':'Extremely militant vegetarian-communist ideologues. Mostly engage in theoretical disputes with RLF and RLF(R), but also occasional uprisings.'},
                                         16:{'name':'United Rabbit-Kanga Workers Alliance',
                                            'aliases':['The URKWA'],
                                            'desc':'Militant vegetarian-anarchist coalition of rabbits and mainly oppossums, with a few kanagoos. Riot during other events.'},
                                         18:{'name':'The Black Kangaroos',
                                            'aliases':['The BKs'],
                                            'desc':'Evolved kangaroos and wallabies advocating for world-wide peaceful transformations. Mostly provide free vegetarian food dispensaries.'},
                                         19:{'name':'The Legion of Martyrs',
                                            'aliases':['The Harebrains'],
                                            'desc':'A quasi-religious rabbit movement devoted to memorializing the mountains of RLF, RLF(R) and RRRLF dead.'},
                                         20:{'name':'Ape Legal Aid',
                                            'aliases':['Militant Monkeys for Peace', 'Gorilla Lawyers Guild'],
                                            'desc':'Non-human primate assistance organization working for full legal equality with human primates.'},
                                         21:{'name':'Revolutionary Squirrel Party',
                                            'aliases':['The RSP'],
                                            'desc':'A squirrel-led movement uniting rodents of all kinds against oppression, particularly by dogs and canines. Mass demonstrations.'},
                                         22:{'name':'Revolutionary Squirrels and Rats Party',
                                            'aliases':['The RSRP'],
                                            'desc':'A rat-led offshoot of the RSP. Much more militant, engaging in riots as well as demonstrations.'},
                                         23:{'name':'Revolutionary Squirrel Air Force',
                                            'aliases':['The RSAF'],
                                            'desc':'The armed wing of the RSRP, led by flying-squirrels. Engage in aerial attacks during RSRP riots.'},
                                         24:{'name':'Lizards and Snakes Campaign for Human Rights',
                                            'aliases':['The LSCHR', 'The Comedians'],
                                            'desc':'Advocates for equal treatment of evolved snakes and lizards, usually through stand-up comedy routines that cleverly mock humans.'},
                                         25:{'name':'The College of Turtles',
                                            'aliases':['Turtles Union'],
                                            'desc':'Make pronouncements similar to the large marine mammals, but via long speeches and meetings lasting for many hours or days'},
                                         26:{'name':'The United Congress of Non-Human Animals',
                                            'aliases':['The UC', 'Congress', 'Animal Congress'],
                                            'desc':'An umbrella political movement that attempts to unite animal demands. Largely ineffective. May be a human front.'},
                                       }
                               },

                           6: {'name':'Ungaerama',
                               'aliases':['The Artificial Hand',
                                          'Shapers Union'],
                               'desc':'Shaped evolution, machine and AI ascendancy. Suppression of biological privilege.',
                               'alliances': ['The Old Guild Alliance'],
                               'orgs': {0: {'name':'Orchestra of Jaenisch',
                                            'aliases':['Evolution 101'],
                                            'desc':'Open, outer level, introduction to genetics'},
                                        1: {'name':'Breeding for Fun and Profit',
                                            'aliases':['Evolution 102'],
                                            'desc':'Open, outer level, experimentation with and history of selective breeding'},
                                        2: {'name':'The Breakers',
                                            'aliases':['Evolution 201'],
                                            'desc':'First semi-secret level, introduction to genomic editing'},
                                        3: {'name':'The Code Breakers',
                                            'aliases':['Evolution 202'],
                                            'desc':'Second semi-secret level, introduction to computer programming'},
                                        4: {'name':'Augmentation and Fermentation',
                                            'aliases':['Evolution 203'],
                                            'desc':'Third semi-secret level, introduction to mind-altering drugs, initiation'},
                                        5: {'name':'Ergo, Algo',
                                            'aliases':['Evolution 301'],
                                            'desc':'First secret level, advanced computer programming'},
                                        6: {'name':'A New Kind',
                                            'aliases':['Evolution 302'],
                                            'desc':'Second secret level, computer implants and genetic modifications'},
                                        7: {'name':'A New Life',
                                            'aliases':['Evolution 303'],
                                            'desc':'Third secret level, advanced artificial intelligence and robotics'},
                                       }
                               },

                           7: {'name':'Yanterama',
                               'aliases':['The Pure Hand',
                                          'The Human League',
                                          'The Old School'],
                               'desc':'Human supremacy. Elimination of sentient animals and shaped evolution. Restoration.',
                               'alliances': ['Helioptic Union',
                                             'Provisioners Corporation'],
                               'orgs': { 0: {'name':'The Rod and Fork Club',
                                             'aliases':['Bar-B-Q Lovers'],
                                             'desc':'Popularize the benefits of eating any type of animals. Militant meat-eaters.'},
                                         1: {'name':'Old Glory',
                                             'aliases':['Restorationists', 'Revivalists'],
                                             'desc':'Nostalgia for human-only civiization, myth-making, story-telling, arts'},
                                         2: {'name':'Grim Tales',
                                             'aliases':['Horrorites'],
                                             'desc':'Promote tales of animal and mutant atrocities against humans'},
                                         3: {'name':'Grim Reapers',
                                             'aliases':['The Red Hand'],
                                             'desc':'Secret. Promote sabotage, terrorism against evolved animal and shaped-human communities'},
                                       }
                              },

                           8: {'name':'Likihakaual',
                               'aliases':['Heart Warriors',
                                          'The Order of Healers'],
                               'desc':'Healing arts. Genetic manipulation. Shaped evolution for good. Social engineering. Affairs of state.',
                               'alliances': ['The Five Guilds',
                                             'The New Guild Alliance'],
                               'orgs': {0: {'name':'Order of Assissi',
                                            'desc':'Open, outer level, human-friendly'},
                                        1: {'name':'Order of Aquarius',
                                            'desc':'Open, outer level, shaped-friendly'},
                                        2: {'name':'Order of the Healing Touch',
                                            'desc':'Open, outer level, animal-friendly'},
                                        3: {'name':'Order of the Golden Flame',
                                            'desc':'Semi-secret, middle level, helioptic-centric'},
                                        4: {'name':'Order of the Silver Star',
                                            'desc':'Semi-secret, middle level, dulunic-centric'},
                                        5: {'name':'Order of the Two-in-One',
                                            'desc':'Semi-secret, middle level, shaped-centric'},
                                        6: {'name':'Order of the Monkey',
                                            'desc':'Semi-secret, middle level, animal-centric'},
                                        7: {'name':'Order of the New Age',
                                            'desc':'Secret, inner level, social-policy-centric'},
                                        8: {'name':'Order of the Invisible College',
                                            'desc':'Secret, inner level, science-centric'},
                                        9: {'name':'Order of the Eternals',
                                            'desc':'Secret, inner level, enlightenment-centric'} }
                              }
                         }

    def SetGuild(self, char_type):
        '''
        Randomly select a guild and position within it, adjusting choice
        according to the character's DNA type
        '''
        # Determine whether char appears mainly human or animal or clearly shaped
        ctype = char_type.split()
        if 'shaped' in ctype:
            ctype = 'shaped'
        elif 'human' in ctype:
            ctype = 'human'
        else:
            ctype = 'animal'

        # Randomly select a guild.  Once karma comes into play, that
        # could also affect guild-selection
        not_found = True
        while not_found:
            r = random.randint(0, len(self.Guild.keys())-1)
            # A definite OK to join:
            if ctype in self.Guild[r]['pro'] \
            or ctype in self.Guild[r]['neut']:
                not_found = False
                break
            # A definite Not-OK to join:
            elif ctype in self.Guild[r]['anti']:
                continue

        return self.Guild[r]

    def FindAlliance(self, guild_name):
        '''
        For given Guild, provided as argument 1, return info about what
        alliance it belongs to.
        '''
        alli = {}
        for a in range (0, len(self.Alliance.keys())):
            mems = self.Alliance[a]['members']
            for m in range (0, len(mems)):
                if guild_name == mems[m]:
                    alli = self.Alliance[a]
                    return alli
        return False

    def FindSocieties(self, alliance_name):
        '''
        For given Alliance, provided as argument 1, return info about what
        secret societies it has shadowy relationships to.

        This needs work. Probably want to break out sub-sets of data
        so they are easier to search, parse, etc.
        '''
        societies = []
        for s in range (0, len(self.Societies.keys())):
            allis = self.Societies[s]['alliances']
            for a in range (0, len(allis)):
                if alliance_name == allis[a]:
                    societies.append(self.Societies[s])
        return societies

    def PickSecretOrg(self, society_name, char_DNR, char_animal_type, char_age, char_gender):
        '''
        Based on a pre-selected secret society name, plus the character's
        age and species, select which organization or level within the
        secret society that the character may be associated with or
        recruited by.

        char_DNR = a list containing a 3-tuple of floats: h, a, m percentages
        char_animal_type = dict showing ordered items from the lifeform catalog
        char_age = integer (years)
        char_gender = male, female or androgynous
        '''
        # print society_name, char_DNR, char_animal_type, char_age, char_gender
        # print '\n'
        # Add logic to refine choices based on character qualities

        org = {}
        for s in range (0, len(self.Societies.keys())):
            if self.Societies[s]['name'] == society_name:
                not_found = True
                while not_found:
                    r = random.randint(0, len(self.Societies[s]['orgs'])-1)
                    org = self.Societies[s]['orgs'][r]
                    not_found = False

        return org

def main():
    '''
    For testing...
    '''

if __name__ == '__main__':
    # main()
    pass

