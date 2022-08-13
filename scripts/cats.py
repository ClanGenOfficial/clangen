from .pelts import *
from .names import *
from .sprites import *
from .game_essentials import *
from random import choice, randint
import math
import os.path
import json


class Cat(object):
    used_screen = screen
    traits = ['strange', 'bloodthirsty', 'ambitious', 'loyal', 'righteous', 'fierce', 'nervous', 'strict',
              'charismatic', 'calm', 'daring', 'loving', 'playful', 'lonesome', 'cold',
              'insecure', 'vengeful', 'shameless', 'faithful', 'troublesome', 'empathetic', 'adventurous', 'thoughtful',
              'compassionate', 'childish', 'confident', 'careful',
              'altruistic', 'bold', 'patient', 'responsible', 'sneaky', 'wise']
    kit_traits = ['bouncy', 'bullying', 'daydreamer', 'nervous', 'charming', 'attention-seeker', 'impulsive',
                  'inquisitive', 'bossy', 'troublesome', 'quiet', 'daring', 'sweet',
                  'insecure', 'noisy', 'polite']
    ages = ['kitten', 'adolescent', 'young adult', 'adult', 'senior adult', 'elder', 'dead']
    age_moons = {'kitten': [0, 5], 'adolescent': [6, 11], 'young adult': [12, 47], 'adult': [48, 95],
                 'senior adult': [96, 119], 'elder': [120, 199]}
    gender_tags = {'female': 'F', 'male': 'M'}
    skills = ['good hunter', 'great hunter', 'fantastic hunter', 'smart', 'very smart', 'extremely smart',
              'good fighter', 'great fighter', 'excellent fighter', 'good speaker',
              'great speaker', 'excellent speaker', 'strong connection to starclan', 'good teacher', 'great teacher',
              'fantastic teacher']

    all_cats = {}  # ID: object

    def __init__(self, prefix=None, gender=None, status="kitten", parent1=None, parent2=None, pelt=None,
                 eye_colour=None, suffix=None, ID=None, moons=None, example=False):
        self.gender = gender
        self.status = status
        self.age = None
        self.parent1 = parent1
        self.parent2 = parent2
        self.pelt = pelt
        self.eye_colour = eye_colour
        self.mentor = None
        self.former_mentor = []
        self.apprentice = []
        self.former_apprentices = []
        self.mate = None
        self.placement = None
        self.example = example
        self.dead = False
        self.died_by = None  # once the cat dies, tell the cause
        self.dead_for = 0  # moons
        self.thought = ''
        if ID is None:
            self.ID = str(randint(10000, 99999))
        else:
            self.ID = ID
        # personality trait and skill
        if self.status != 'kitten':
            self.trait = choice(self.traits)
            if self.status != 'apprentice' and self.status != 'medicine cat apprentice':
                self.skill = choice(self.skills)
            else:
                self.skill = '???'
        else:
            self.trait = self.trait = choice(self.kit_traits)
            self.skill = '???'
        if self.gender is None:
            self.gender = choice(["female", "male"])
        self.g_tag = self.gender_tags[self.gender]
        if status is None:
            self.age = choice(self.ages)
        else:
            if status in ['kitten', 'elder']:
                self.age = status
            elif status == 'apprentice' or status == 'medicine cat apprentice':
                self.age = 'adolescent'
            else:
                self.age = choice(['young adult', 'adult', 'adult', 'senior adult'])
        if moons is None:
            self.moons = randint(self.age_moons[self.age][0], self.age_moons[self.age][1])
        else:
            self.moons = moons

        # eye colour
        if self.eye_colour is None:
            a = randint(0, 200)
            if a == 1:
                self.eye_colour = choice(["BLUEYELLOW", "BLUEGREEN"])
            else:
                if self.parent1 is None:
                    self.eye_colour = choice(eye_colours)
                elif self.parent2 is None:
                    par1 = self.all_cats[self.parent1]
                    self.eye_colour = choice([par1.eye_colour, choice(eye_colours)])
                else:
                    par1 = self.all_cats[self.parent1]
                    par2 = self.all_cats[self.parent2]
                    self.eye_colour = choice([par1.eye_colour, par2.eye_colour, choice(eye_colours)])

        # pelt
        if self.pelt is None:
            if self.parent1 is None:
                # If pelt has not been picked manually, this function chooses one based on possible inheritances
                self.pelt = choose_pelt(self.gender)

            elif self.parent2 is None and self.parent1 in self.all_cats.keys():
                # 1 in 3 chance to inherit a single parent's pelt
                par1 = self.all_cats[self.parent1]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, None]), choice([par1.pelt.white, None]),
                                        choice([par1.pelt.name, None]),
                                        choice([par1.pelt.length, None]))

            elif self.parent1 in self.all_cats.keys() and self.parent2 in self.all_cats.keys():
                # 2 in 3 chance to inherit either parent's pelt
                par1 = self.all_cats[self.parent1]
                par2 = self.all_cats[self.parent2]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, par2.pelt.colour, None]),
                                        choice([par1.pelt.white, par2.pelt.white, None]),
                                        choice([par1.pelt.name, par2.pelt.name, None]),
                                        choice([par1.pelt.length, par2.pelt.length, None]))

        # NAME
        if self.pelt is not None:
            self.name = Name(status, prefix, suffix, self.pelt.colour, self.eye_colour, self.pelt.name)
        else:
            self.name = Name(status, prefix, suffix, eyes=self.eye_colour)

        # SPRITE
        self.age_sprites = {'kitten': randint(0, 2), 'adolescent': randint(3, 5), 'elder': randint(3, 5)}
        self.reverse = choice([True, False])
        self.skin = choice(skin_sprites)

        # scars & more
        scar_choice = randint(0, 15)
        if self.age in ['kitten', 'adolescent']:
            scar_choice = randint(0, 50)
        elif self.age in ['young adult', 'adult']:
            scar_choice = randint(0, 20)
        if scar_choice == 1:
            self.specialty = choice([choice(scars1), choice(scars2)])
        else:
            self.specialty = None

        scar_choice2 = randint(0, 30)
        if self.age in ['kitten', 'adolescent']:
            scar_choice2 = randint(0, 100)
        elif self.age in ['young adult', 'adult']:
            scar_choice2 = randint(0, 40)
        if scar_choice2 == 1:
            self.specialty2 = choice([choice(scars1), choice(scars2)])
        else:
            self.specialty2 = None

        # random event
        if self.pelt is not None:
            if self.pelt.length != 'long':
                self.age_sprites['adult'] = randint(6, 8)
            else:
                self.age_sprites['adult'] = randint(0, 2)
            self.age_sprites['young adult'] = self.age_sprites['adult']
            self.age_sprites['senior adult'] = self.age_sprites['adult']
            self.age_sprites['dead'] = None  # The sprite that the cat has in starclan

            # WHITE PATCHES
            if self.pelt.white and self.pelt.white_patches is not None:
                pelt_choice = randint(0, 10)
                if pelt_choice == 1 and self.pelt.name in ['Calico', 'TwoColour', 'Tabby',
                                                           'Speckled'] and self.pelt.colour != 'WHITE':
                    self.white_patches = choice(['COLOURPOINT', 'COLOURPOINTCREAMY', 'RAGDOLL'])
                elif pelt_choice == 1 and self.pelt.name in ['Calico', 'TwoColour', 'Tabby', 'Speckled']:
                    self.white_patches = choice(['COLOURPOINT', 'RAGDOLL'])
                elif self.pelt.name in ['Tabby', 'Speckled', 'TwoColour'] and self.pelt.colour == 'WHITE':
                    self.white_patches = choice(
                        ['ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
                         'LIGHTSONG', 'VITILIGO'])
                else:
                    self.white_patches = choice(self.pelt.white_patches)
            else:
                self.white_patches = choice(['EXTRA', None, None])

            # pattern for tortie/calico cats
            if self.pelt.name == 'Calico':
                self.pattern = choice(calico_pattern)
            elif self.pelt.name == 'Tortie':
                self.pattern = choice(tortie_pattern)
            else:
                self.pattern = None
        else:
            self.white_patches = None
            self.pattern = None

        # Sprite sizes
        self.sprite = None
        self.big_sprite = None
        self.large_sprite = None

        # experience and current patrol status
        self.experience = 0
        self.in_camp = 1

        experience_levels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high',
                             'master', 'max']
        self.experience_level = experience_levels[math.floor(self.experience / 10)]

        # SAVE CAT INTO ALL_CATS DICTIONARY IN CATS-CLASS
        self.all_cats[self.ID] = self

    def __repr__(self):
        return self.ID

    def thoughts(self):
        # actions or thoughts for all cats. These switch either every moon or every time the game is re-opened

        for c in self.all_cats.keys():
            other_cat = random.choice(list(self.all_cats.keys()))
            while other_cat == c:
                other_cat = random.choice(list(self.all_cats.keys()))
            other_cat = self.all_cats.get(other_cat)
            other_name = str(other_cat.name)
            cat = self.all_cats.get(c)
            thought = 'Is not thinking about much right now'  # placeholder thought - should never appear in game
            if cat.dead:
                # individual thoughts
                starclan_thoughts = ['Is feeling quite lazy', 'Is spending a considerable amount of time grooming',
                                     'Is looking forward to today', 'Is feeling down...',
                                     'Is feeling happy!', 'Is curious about other clans', 'Is feeling sassy today',
                                     "Is thinking about a message to send",
                                     "Wishes they were still alive", "Is admiring StarClan territory",
                                     "Is thinking about their life", "Is missing a loved one",
                                     "Is hoping to meet with a medicine cat soon", "Is admiring the stars in their fur",
                                     "Is watching over a clan ceremony",
                                     "Is hoping to give a life to a new leader", "Is hoping they will be remembered",
                                     "Is watching over the clan", "Is worried about the clan",
                                     "Is relaxing in the sun", "Is wondering about twolegs",
                                     "Is thinking about their ancient ancestors",
                                     "Is worried about the cats in the Dark Forest",
                                     "Is thinking of advice to give to a medicine cat", "Is exploring StarClan",
                                     "Is sad seeing how the clan has changed", "Wishes they could speak to old friends",
                                     "Is sneezing on stardust",
                                     "Is comforting another StarClan cat", "Is exploring StarClan\'s hunting grounds",
                                     "Is hunting mice in StarClan",
                                     "Is chattering at the birds in StarClan", "Is chasing rabbits in StarClan",
                                     "Can feel some cat forgetting them..."]
                if other_cat.dead:
                    starclan_thoughts.extend([  # thoughts with other cats that are dead
                        'Is sharing tongues with ' + other_name,
                        'Has been spending time with ' + other_name + ' lately', 'Is acting huffy at ' + other_name,
                        'Is sharing a freshkill with ' + other_name, 'Is curious about ' + other_name,
                        'Is talking with ' + other_name, 'Doesn\'t want to talk to ' + other_name,
                        'Is having a serious fight with ' + other_name,
                        'Wants to spend more time with ' + other_name + '!',
                        'Is thinking about future prophecies with ' + other_name,
                        'Is watching over the clan with ' + other_name,
                        'Is listening to long-forgotten stories about the clan'])
                elif not other_cat.dead:
                    starclan_thoughts.extend([  # thoughts with other cats that are alive
                        'Is watching over ' + other_name, 'Is curious about what ' + other_name + ' is doing',
                        'Wants to send a message to ' + other_name,
                        'Is currently walking in the dreams of ' + other_name, 'Is proud of ' + other_name,
                        'Is disappointed in ' + other_name, 'Wants to warn ' + other_name,
                        'Has been following the growth of ' + other_name, 'Has seen the future demise of ' + other_name,
                        'Is looking to visit ' + other_name + ' in a dream soon',
                        'Accidentally found themselves in ' + other_name + '\'s dreams the other night',
                        'Wants to warn ' + other_name + ' about something that will happen soon',
                        'Knows what ' + other_name + '\'s secret is and wants to tell some cat'])
                if cat.status in ['kitten', 'apprentice', 'medicine cat apprentice']:  # dead young cat thoughts
                    starclan_thoughts.extend(
                        ['Wishes they had more time to grow up', 'Wonders what their full name would have been',
                         'Is bothering older StarClan cats',
                         'Is learning about the other cats in StarClan'])
                elif cat.status == 'elder':  # dead elder thoughts
                    starclan_thoughts.extend(
                        ['Is grateful that they lived such a long life', 'Is happy that their joints no longer ache',
                         'Is telling stories to the younger cats of StarClan',
                         'Watches over the younger cats of StarClan',
                         'Is observing how different the clan is from when they were alive'])
                elif cat.status == 'leader':  # dead leader thoughts
                    starclan_thoughts.extend(['Hoped that they were a good leader', 'Wishes that they had ten lives',
                                              'Is proud of their clan from StarClan',
                                              'Is pleased to see the new direction the clan is heading in',
                                              'Still frets over their beloved former clanmates from afar',
                                              'Rejoices with every new kit born to the clan they still hold so dear'])
                thought = choice(starclan_thoughts)  # sets current thought to a random applicable thought
            elif not cat.dead:
                # general individual thoughts
                thoughts = ['Is feeling quite lazy', 'Is spending a considerable amount of time grooming',
                            'Is looking forward to today', 'Is feeling down...',
                            'Is feeling excited', 'Is feeling nervous', 'Is feeling content', "Is relaxing in camp",
                            'Is daydreaming', 'Is napping', 'Thinks they are going crazy',
                            'Is feeling gloomy', "Is looking around camp", 'Is feeling happy!',
                            'Is curious about the other clans', 'Is feeling sassy today',
                            'Wants to spend time alone today', "Is eating some freshkill",
                            'Is heading to the dirtplace', 'Is rethinking their life choices',
                            'Is in the medicine den', 'Is having a good day', 'Is having a hard day',
                            'Is talking to themselves',
                            'Regrets not eating the bird on the freshkill pile earlier', 'Is basking in the sun',
                            'Feels a sense of dread', 'Is feeling unappreciated',
                            'Is staring off into space', 'Is worried others are judging them',
                            'Almost choked on their prey', 'Is chattering at the birds in the trees above',
                            'Was recently caught humming to themselves',
                            'Had a nightmare involving the rushing river nearby',
                            'Wishes they were still in their nest sleeping',
                            'Is craving the taste of mouse', 'Is craving the taste of rabbit',
                            'Is craving the taste of vole', 'Is craving the taste of frog',
                            'Is craving the taste of shrew', 'Is wondering if they would be a good swimmer',
                            'Is thinking about how awful kittypet food must taste',
                            'Is feeling underappreciated...', 'Is staring off into space',
                            'Is picking the burrs from their pelt', 'Has a sore paw from a bee sting',
                            'Is sharpening their claws', 'Woke up on the wrong side of the nest']
                if other_cat.dead:  # thoughts with other cats who are dead
                    if cat.status in ['kitten', 'apprentice',
                                      'medicine cat apprentice']:  # young cat thoughts about dead cat
                        thoughts.extend(
                            ['Is listening to stories about ' + other_name, 'Is learning more about ' + other_name,
                             'Is sad they couldn\'t spend time with ' + other_name,
                             'Is wondering if ' + other_name + ' would have been their friend'])
                    elif cat.status in ['warrior', 'medicine cat', 'deputy',
                                        'leader']:  # older cat thoughts about dead cat
                        thoughts.extend(
                            ['Is listening to stories about ' + other_name, 'Is learning more about ' + other_name,
                             'Is sad they couldn\'t spend more time with ' + other_name,
                             'Wishes they could visit ' + other_name + ' in StarClan', 'Is remembering ' + other_name])
                    if cat.status == 'elder':  # elder thoughts about dead cat
                        thoughts.extend(['Is telling stories about ' + other_name,
                                         'Is sad they couldn\'t spend more time with ' + other_name,
                                         'Wishes they could visit ' + other_name + ' in StarClan',
                                         'Is remembering ' + other_name,
                                         'Wishes that ' + other_name + ' were still alive',
                                         'Found a trinket that used to belong to ' + other_name,
                                         'Is forgetting who ' + other_name + ' was',
                                         'Is thinking fondly of ' + other_name,
                                         'Sometimes feels like ' + other_name + " is still right there next to them"])
                    if cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice' or cat.skill == 'strong connection to starclan':  # medicine cat/strong connection
                        # thoughts about dead cat
                        thoughts.extend(
                            ['Was given a prophecy by ' + other_name, 'Was sent an omen by ' + other_name,
                             'Is dreaming about ' + other_name + ' who gives them a message',
                             'Is visited by ' + other_name, 'Senses ' + other_name + ' is nearby',
                             'Saw ' + other_name + ' in a dream, warning them about... something',
                             'Is asking for guidance from ' + other_name,
                             'Is wondering desperately why ' + other_name + ' wasn\'t there when they needed them',
                             'Is sure that they saw ' + other_name + ' appear in the forest today... why?',
                             'Blames themselves for ' + other_name + '\'s death...'])
                elif not other_cat.dead:  # thoughts with other cat who is alive
                    if cat.status in ['warrior', 'elder', 'deputy',
                                      'leader'] and other_cat.status == 'apprentice':  # older cat thoughts about younger cat
                        thoughts.extend(['Is giving ' + other_name + ' advice',
                                         'Is telling ' + other_name + ' about a hunting technique',
                                         'Is scolding ' + other_name,
                                         'Is giving ' + other_name + ' a task',
                                         other_name + ' reminds them of when they were their age',
                                         'Is telling ' + other_name + ' about their own days as an apprentice',
                                         'Is frustrated that ' + other_name + ' won\'t take their duties more seriously',
                                         'Has successfully tricked ' + other_name + ' into believing a crazy tale about the clan leader',
                                         'Can\'t believe ' + other_name + ' caught that rabbit on patrol yesterday',
                                         'Doesn\'t think that ' + other_name + ' has been completely honest lately',
                                         'Is fuming from an argument with ' + other_name])
                    if cat.status == 'kitten':  # kit thoughts
                        if other_cat.status == 'kitten':  # kit thoughts with other kit
                            thoughts.extend(
                                ['Pretends to be a warrior with ' + other_name, 'Plays mossball with ' + other_name,
                                 'Has a mock battle with ' + other_name,
                                 'Comes up with a plan to sneak out of camp with ' + other_name,
                                 'Whines about ' + other_name, 'Chomps on ' + other_name + '\'s ear',
                                 'Is pretending to ward off foxes with ' + other_name,
                                 'Is pretending to fight off badgers with ' + other_name,
                                 'Is racing ' + other_name + ' back and forth across the camp clearing',
                                 'Is talking excitedly with ' + other_name + ' about how cool their clan leader is',
                                 'Is talking excitedly with ' + other_name + ' about how cool their clan deputy is',
                                 'Is jealous that ' + other_name + ' is getting more attention than them',
                                 'Won\'t stop crying that they\'re hungry... but they just ate!'])
                        elif other_cat.status != 'kitten':  # kit thoughts about older cat
                            thoughts.extend(
                                ['Is biting ' + other_name + '\'s tail', 'Sticks their tongue out at ' + other_name,
                                 'Whines to ' + other_name,
                                 'Is demanding ' + other_name + '\'s attention'
                                                                'Really looks up to ' + other_name,
                                 'Is hiding under a bush from ' + other_name + ', but they can\'t stop giggling',
                                 'Is pretending to be ' + other_name])
                    elif cat.status in ['apprentice', 'medicine cat apprentice', 'warrior', 'medicine cat', 'deputy',
                                        'leader']:
                        if other_cat.status == 'kitten':  # older cat thoughts about kit
                            thoughts.extend(['Trips over ' + other_name, 'Is giving advice to ' + other_name,
                                             'Is giving ' + other_name + ' a badger ride on their back!',
                                             'Hopes that their own kits are as cute as ' + other_name + ' someday',
                                             'Had to nip ' + other_name + ' on the rump because they were being naughty',
                                             'Is promising to take ' + other_name + ' outside of camp if they behave',
                                             'Is watching ' + other_name + ' perform an almost-decent hunting crouch',
                                             'Can\'t take their eyes off of' + other_name + ' for more than a few seconds',
                                             'Gave ' + other_name + ' a trinket they found while out on patrol today'])
                        else:
                            thoughts.extend(
                                ['Is fighting with ' + other_name, 'Is talking with ' + other_name,
                                 'Is sharing prey with ' + other_name, 'Heard a rumor about ' + other_name,
                                 'Just told ' + other_name + ' a hilarious joke'])
                    if cat.age == other_cat.age and cat.parent1 != other_cat.parent1 and cat.parent2 != other_cat.parent2 and cat.ID not in [
                        other_cat.parent1,
                        other_cat.parent2] and other_cat.ID \
                            not in [
                        cat.parent1,
                        cat.parent2] and cat.mate is None and other_cat.mate is None and cat.age == other_cat.age:
                        thoughts.extend(
                            ['Is developing a crush on ' + other_name, 'Is spending a lot of time with ' + other_name,
                             'Feels guilty about hurting ' + other_name + '\'s feelings',
                             'Can\'t seem to stop talking about ' + other_name,
                             'Would spend the entire day with ' + other_name + ' if they could',
                             'Was caught enjoying a moonlit stroll with ' + other_name + ' last night...',
                             'Keeps shyly glancing over at ' + other_name + ' as the clan talks about kits',
                             'Gave a pretty flower they found to ' + other_name,
                             'Is admiring ' + other_name + ' from afar...'
                                                           'Is thinking of the best ways to impress ' + other_name,
                             'Doesn\'t want ' + other_name + ' to overwork themselves',
                             'Is rolling around a little too playfully with ' + other_name + '...',
                             'Is wondering what it would be like to grow old with ' + other_name,
                             'Thinks that ' + other_name + ' is really funny',
                             'Thinks that ' + other_name + ' is really charming'])
                if cat.status == 'kitten':
                    thoughts.extend(['Plays mossball by themselves', 'Is annoying older cats',
                                     'Wonders what their full name will be', 'Pretends to be a warrior',
                                     'Is becoming interested in herbs', 'Tries to sneak out of camp',
                                     'Is rolling around on the ground', 'Is chasing their tail',
                                     'Is playing with a stick', 'Is nervous for their apprentice ceremony',
                                     'Is excited for their apprentice ceremony',
                                     'Wonders who their mentor will be', "Practices the hunting crouch",
                                     'Pretends to fight an enemy warrior', 'Wants to take a nap',
                                     'Is scared after having a nightmare',
                                     'Thinks they saw a StarClan cat in their dreams', 'Wants to snuggle',
                                     'Wishes other cats would stop babying them', 'Is hiding from other cats',
                                     'Is bouncing around in excitement', 'Whines about being hungry',
                                     'Is asking the older cats about how kittens are made',
                                     'Is pestering older cats to play with them', 'Is whining for milk',
                                     'Is whimpering in their sleep', 'Is trying to growl menacingly',
                                     'Is adamantly refusing to take their nap',
                                     'Was nipped on the rump by an elder for being naughty',
                                     'Is batting pebbles across the camp clearing',
                                     'Is regretting eating the bug that they caught',
                                     'Recently took a tumble off of a log',
                                     'Is busy mastering a battle move they are performing incorrectly',
                                     'Refuses to eat the herbs the medicine cat has given them for their tummy',
                                     'Is scrambling the Medicine Cat\'s herbs!',
                                     'Is crying after rough-housing too hard with the older cats',
                                     'Is hatching a plan to sneak out of camp and play',
                                     'Is running like a whirlwind around the camp',
                                     'Is pretending to be the clan leader',
                                     'Is pretending to be deputy', 'Is pretending to be the medicine cat',
                                     'Doesn\'t want to grow up yet...', 'Wants to be a warrior already!',
                                     'Got in trouble for bringing thorns into the nest'
                                     'Is asking older cats how kits are born'])
                elif cat.status == 'apprentice':
                    thoughts.extend(
                        ['Is thinking about the time they caught a huge rabbit', 'Wonders what their full name will be',
                         'Is irritating their mentor',
                         'Is arguing with their mentor', 'Is listening to their mentor',
                         'Plans to visit the elders soon', "Practices the hunting crouch",
                         'Pretends to fight an enemy warrior', 'Practices some battle moves',
                         'Is becoming interested in herbs', 'Volunteers for the dawn patrol',
                         'Volunteers to gather herbs', 'Hopes they will do battle training soon',
                         'Is pulling a prank on the warriors', 'Can\'t wait to be a warrior',
                         'Is wondering if they are good enough to become a warrior', 'Is gathering moss',
                         'Doesn\'t want to become a warrior yet', 'Is gossiping',
                         'Is acting angsty', 'Was put on kit-sitting duty', 'Is showing off to the kits',
                         'Is dreading their apprentice duties',
                         'Is helping the elders with their ticks',
                         'Fell into the nearby creek yesterday and is still feeling damp',
                         'Is helping to repair the elder\'s den', 'Is helping to reinforce the camp wall with brambles',
                         'Was asked to gather fresh moss for the elders\' bedding', 'Is making their mentor laugh',
                         'Is really bonding with their mentor',
                         'Is having a hard time keeping up with their training',
                         'Has been lending the Medicine Cat a paw lately',
                         'Is daydreaming about having a mate and kits someday', 'Had quite the adventure today',
                         'Was tasked with lining nests with fresh moss today',
                         'Wants to be a warrior already!', 'Is dreaming of someday making their clan proud',
                         'Is awkwardly deflecting kits\' questions about where kits come from'])
                elif cat.status == 'medicine cat apprentice':
                    thoughts.extend(
                        ['Is struggling to remember all of the names of herbs', 'Is counting the poppy seeds',
                         'Is helping organize the herb stores',
                         'Wonders what their full name will be', 'Plans to help the elders with their ticks',
                         'Is looking forward to the half-moon meeting',
                         'Is wondering if they are good enough to become a medicine cat',
                         'Helps apply a poultice to a small wound', 'Is making new nests',
                         'Is proud of their ability to care for their clanmates', 'Is tending growing herbs',
                         'Made a mess of the herbs and is panicking',
                         'Is carefully picking up spilled poppy seeds', 'Is out gathering more cobwebs',
                         'Is reciting the names of herbs aloud',
                         'Wishes the other apprentices could understand how they feel',
                         'Was startled awake in the wee hours by a vivid dream',
                         'Has been hearing the voices of StarClan cats...',
                         'Has the foul taste of bitter herbs in their mouth',
                         'Is enjoying learning all of the herbs a medicine cat needs!',
                         'Is happy that they chose life as a Medicine Cat',
                         'Is lining nests with fresh moss and feathers'])
                elif cat.status == 'medicine cat':
                    thoughts.extend(['Is looking for herbs', 'Is organizing the herb stores', 'Is drying some herbs',
                                     'Is counting the poppy seeds', 'Is gathering cobwebs',
                                     'Is interpreting an omen', 'Is interpreting a prophecy',
                                     'Hopes for a message from StarClan soon', 'Is checking up on the warriors',
                                     'Is feeling stressed taking care of the clan',
                                     'Is thinking about taking on a new apprentice',
                                     'Is wondering if they could borrow some catmint from the other clans',
                                     'Is looking forward to the half-moon meeting',
                                     'Is wrapping a wound with cobwebs', 'Is clearing out old herbs',
                                     'Is proud of their ability to care for their clanmates',
                                     'Chased kits out of their den', 'Is wishing they could have a mate and kits',
                                     'Is tending growing herbs',
                                     'Wishes they had an extra set of paws',
                                     'Is carefully picking up spilled poppy seeds', 'Is out gathering more cobwebs',
                                     'Is reciting the names of herbs aloud',
                                     'Wishes their clanmates could understand their struggles',
                                     'Was startled awake in the wee hours by a vivid dream'
                                     'Is running low on catmint', 'Is running low on marigold',
                                     'Is running low on burdock root', 'Is running low on poppy seeds',
                                     'Is running low on cobwebs', 'Is running low on feverfew',
                                     'Is running low on borage leaves' 'Is running low on tansy' 'Is running low on mouse bile',
                                     'Is teaching kits about what plants to stay away from',
                                     'Plans to go out gathering herbs today',
                                     'Has been hearing the voices of StarClan cats...',
                                     'Is lining nests with fresh moss and feathers'])
                    if cat.trait == 'bloodthirsty':
                        thoughts.extend(['Is gathering deathberries', 'Has been disappearing a lot lately',
                                         'Insists only on treating cats who need it'])
                    elif cat.trait == 'strange':
                        thoughts.extend(
                            ['Insists everyone eat camomile leaves everyday at moonhigh', 'Hisses at the kits randomly',
                             'Sleeps in the middle of the clearing'])
                elif cat.status == 'warrior':
                    thoughts.extend(['Caught scent of a fox earlier', 'Caught scent of an enemy warrior earlier',
                                     'Is helping gathering herbs', 'Is thinking about love',
                                     'Is decorating their nest', 'Is reinforcing the camp with brambles',
                                     'Wants to be chosen as the new deputy', 'Caught a huge rabbit',
                                     'Is dreaming about being leader', 'Tries to set a good example for younger cats',
                                     'Wants to go on a patrol', 'Wants to go on a hunting patrol',
                                     'Is hoping to lead the next patrol', 'Is guarding the camp entrance',
                                     'Is thinking about kits', 'Is watching over the kits', 'Is gossiping',
                                     'Plans to visit the medicine cat', 'Is sharpening their claws', 'Is feeling sore',
                                     'Is being pestered by flies', 'Feels overworked',
                                     'Overslept and missed their patrol', 'Is exhausted from yesterday\'s patrol',
                                     'Wants to have kits', 'Is sparring with some campmates',
                                     'Fell into the nearby creek yesterday and is still feeling damp',
                                     'Is helping to reinforce the nursery wall with brambles',
                                     'Is hoping to be assigned to the dawn patrol tomorrow',
                                     'Is hoping to be assigned to the hunting patrol today',
                                     'Is hoping to be asked to help patrol the borders today',
                                     'Is itching to run in a wide open space',
                                     'Has offered to help the deputy organize today\'s patrols',
                                     'Is guarding the camp entrance dutifully',
                                     'Is helping to escort the medicine cat to gather herbs'])
                    if cat.trait == 'bloodthirsty':
                        thoughts.extend(['Is thinking about murder', 'Is acting suspicious',
                                         'Has been washing their paws a lot lately', 'Has disappeared often recently'])
                    elif cat.trait == 'strange':
                        thoughts.extend(['Is telling every cat about their weird dreams', 'Is chasing a butterfly',
                                         'Stares at random cats'])
                elif cat.status == 'deputy':
                    thoughts.extend(['Is assigning cats to a border patrol', 'Is assigning cats to a hunting patrol',
                                     'Is wondering what it would be like to be a leader',
                                     'Is spending time alone', 'Tries to set a good example for younger cats',
                                     'Is thinking about kits', 'Is stressed about organizing patrols',
                                     "Wonders who will give them nine lives", 'Feels overworked',
                                     'Is hoping for a break', 'Is assessing the apprentices',
                                     'Wishes they had an extra set of paws', 'Is assigning cats to the dawn patrol',
                                     'Is assigning cats to the hunting patrol',
                                     'Is assigning cats to patrol the borders', 'Can\'t believe they overslept today',
                                     'Is unsure of what the rest of the clan thinks of them as deputy',
                                     'Is doing their best to honor their clan and their leader',
                                     'Must speak with the leader soon about something they found while out on patrol'])
                    if cat.trait == 'bloodthirsty':
                        thoughts.extend(['Is thinking about murder', 'Is acting suspicious',
                                         'Has been washing their paws a lot lately', 'Has disappeared often recently',
                                         'Thinks about killing the leader and staging it as an accident',
                                         'Encourages the leader to start a war'])
                    elif cat.trait == 'strange':
                        thoughts.extend(['Accidentally assigns the same cat to three patrols',
                                         'Insists a hunting patrol only bring back mice',
                                         'Goes missing and comes back smelling like garlic'])
                elif cat.status == 'leader':
                    thoughts.extend(
                        ['Is hoping for a sign from StarClan', 'Is hoping that they are leading their clan well',
                         'Thinks about who should mentor new apprentices',
                         'Is worried about clan relations', 'Is spending time alone',
                         'Tries to set a good example for the deputy',
                         'Is thinking about forming an alliance', 'Is assessing some apprentices',
                         'Is thinking about battle strategies', 'Almost lost a life recently',
                         'Is counting how many lives they have left', 'Is thinking about what to say at the gathering',
                         'Is questioning their ability to lead',
                         'Is dreading the clan meeting they must call later today',
                         'Is finding the responsibility of leadership to be quite the heavy burden',
                         'Is feeling blessed by StarClan this moon',
                         'Is making a solemn vow to protect their clanmates',
                         'Has been letting their deputy call the shots recently, and is proud of their initiative',
                         'Called an important clan meeting recently',
                         'Is pondering the next mentors for the kits of the clan',
                         'Has recently picked up the scent of mischievous kits in their den...',
                         'Is pondering recent dreams they have had... perhaps from StarClan?',
                         'Recently called a clan meeting, but forgot what to say',
                         'Think they have been hearing the voices of StarClan cats...'])
                    if cat.trait == 'bloodthirsty':
                        thoughts.extend(['Encourages warriors to start fights on border patrols',
                                         'Is debating if they should declare a war with another clan',
                                         'Is wondering if they could hold apprentice ceremonies at 4 moons old instead',
                                         'Has been growling to themselves'])
                    elif cat.trait == 'strange':
                        thoughts.extend(
                            ['No thoughts, head empty', 'Insists they they received ten lives instead of nine',
                             'Has a crazed look in their eyes'])
                elif cat.age == 'elder':
                    thoughts.extend(
                        ['Is complaining about their nest being too rough', 'Is complaining about their aching joints',
                         'Is telling stories about when they were young',
                         'Is giving advice to younger cats', 'Is complaining about thorns in their nest',
                         'Is bossing around the younger cats',
                         'Is telling scary stories to the younger cats', 'Is snoring in their sleep',
                         'Thinking about how too many cats die young',
                         'Is complaining about being cold', 'Is grateful they have lived so long',
                         'Is sharing their wisdom', 'Is being pestered by fleas',
                         'Is requesting an apprentice\'s help with their ticks',
                         'Is predicting rainy weather based on their aching bones',
                         'Hopes their legacy will continue on after their death',
                         'Is sharing wisdom with younger cats that is... less than helpful',
                         'Is recounting daring expeditions for the younger cats to hear', 'Is in quite the mood today',
                         'Is feeling rather chipper today',
                         'Is snoring loudly in their sleep', 'Is telling a rather tall tale to any cat who will listen',
                         'Is asking apprentices to help check them for ticks', 'Is assisting with camp cleanup',
                         'Feels too stiff to leave their nest today...',
                         'Has been sleeping a lot more as of late', 'Has been enjoying their old age',
                         'Got lost outside of camp for a bit today',
                         'Doesn\'t like how times have changed since they were young', 'Is feeling rather cross today',
                         'Thinks that times have changed for the better since they were young',
                         'Is recalling something no other cat remembers anymore',
                         'Is enjoying the warm sun in the camp clearing', 'Is grumbling about the weather',
                         'Is giving the clan leader attitude'])
                thought = choice(thoughts)
            cat.thought = thought

            # on_patrol = ['Is having a good time out on patrol', 'Wants to return to camp to see ' + other_name,  #              'Is currently out on patrol',
            # 'Is getting rained on during their patrol',  #              'Is out hunting'] //will add later  # interact_with_loner = ['Wants to know where ' + other_name + '  #
            # came from.'] // will add

    def status_change(self, new_status):
        # revealing of traits and skills
        if self.status == 'kitten':
            self.trait = choice(self.traits)
        if (self.status == 'apprentice' and new_status != 'medicine cat apprentice') or (
                self.status == 'medicine cat apprentice' and new_status != 'apprentice'):
            self.skill = choice(self.skills)

        self.status = new_status
        self.name.status = new_status
        if 'apprentice' in new_status:
            self.update_mentor()
        # update class dictionary
        self.all_cats[self.ID] = self

    def is_valid_mentor(self, potential_mentor):
        # Dead cats can't be mentors
        if potential_mentor.dead:
            return False
        # Match jobs
        if self.status == 'medicine cat apprentice' and potential_mentor.status != 'medicine cat':
            return False
        if self.status == 'apprentice' and potential_mentor.status not in ['leader', 'deputy', 'warrior']:
            return False
        # If not an app, don't need a mentor
        if 'apprentice' not in self.status:
            return False
        # Dead cats don't need mentors
        if self.dead:
            return False
        return True

    def update_mentor(self, new_mentor=None):
        if new_mentor is None:
            # If not reassigning and current mentor works, leave it
            if self.mentor and self.is_valid_mentor(self.mentor):
                return
        old_mentor = self.mentor
        # Should only have mentor if alive and some kind of apprentice
        if 'apprentice' in self.status and not self.dead:
            # Need to pick a random mentor if not specified
            if new_mentor is None:
                potential_mentors = []
                priority_mentors = []
                for cat in self.all_cats.values():
                    if self.is_valid_mentor(cat):
                        potential_mentors.append(cat)
                        if len(cat.apprentice) == 0:
                            priority_mentors.append(cat)
                # First try for a cat who currently has no apprentices
                if len(priority_mentors) > 0:
                    new_mentor = choice(priority_mentors)
                elif len(potential_mentors) > 0:
                    new_mentor = choice(potential_mentors)
            # Mentor changing to chosen/specified cat
            self.mentor = new_mentor
            if new_mentor is not None:
                if self not in new_mentor.apprentice:
                    new_mentor.apprentice.append(self)
                if self in new_mentor.former_apprentices:
                    new_mentor.former_apprentices.remove(self)
        else:
            self.mentor = None
        # Move from old mentor's apps to former apps
        if old_mentor is not None and old_mentor != self.mentor:
            if self in old_mentor.apprentice:
                old_mentor.apprentice.remove(self)
            if self not in old_mentor.former_apprentices:
                old_mentor.former_apprentices.append(self)
            if old_mentor not in self.former_mentor:
                self.former_mentor.append(old_mentor)

    def update_sprite(self):
        # First make pelt, if it wasn't possible before

        if self.pelt is None:
            if self.parent1 is None:
                # If pelt has not been picked manually, this function chooses one based on possible inheritances
                self.pelt = choose_pelt(self.gender)

            elif self.parent2 is None and self.parent1 in self.all_cats.keys():
                # 1 in 3 chance to inherit a single parent's pelt
                par1 = self.all_cats[self.parent1]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, None]), choice([par1.pelt.white, None]),
                                        choice([par1.pelt.name, None]),
                                        choice([par1.pelt.length, None]))

            elif self.parent1 in self.all_cats.keys() and self.parent2 in self.all_cats.keys():
                # 2 in 3 chance to inherit either parent's pelt
                par1 = self.all_cats[self.parent1]
                par2 = self.all_cats[self.parent2]
                self.pelt = choose_pelt(self.gender, choice([par1.pelt.colour, par2.pelt.colour, None]),
                                        choice([par1.pelt.white, par2.pelt.white, None]),
                                        choice([par1.pelt.name, par2.pelt.name, None]),
                                        choice([par1.pelt.length, par2.pelt.length, None]))
            else:
                self.pelt = choose_pelt(self.gender)

        # THE SPRITE UPDATE
        # draw colour & style
        new_sprite = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)

        if self.pelt.name not in ['Tortie', 'Calico']:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                                  'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(sprites.sprites[self.pelt.sprites[1] + 'extra' + self.pelt.colour + str(
                    self.age_sprites[self.age])], (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites[self.pelt.sprites[1] + self.pelt.colour + str(self.age_sprites[self.age])], (0, 0))
        else:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                                  'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(
                    sprites.sprites[self.pelt.sprites[1] + 'extra' + self.pattern + str(self.age_sprites[self.age])],
                    (0, 0))
            else:
                new_sprite.blit(sprites.sprites[self.pelt.sprites[1] + self.pattern + str(self.age_sprites[self.age])],
                                (0, 0))

        # draw white patches
        if self.white_patches is not None:
            if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                                  'medicine cat apprentice'] or self.age == 'elder':
                new_sprite.blit(sprites.sprites['whiteextra' + self.white_patches + str(self.age_sprites[self.age])],
                                (0, 0))
            else:
                new_sprite.blit(sprites.sprites['white' + self.white_patches + str(self.age_sprites[self.age])], (0, 0))

        # draw eyes & scars1
        if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                              'medicine cat apprentice'] or self.age == 'elder':
            if self.specialty in scars1:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars1:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
            new_sprite.blit(sprites.sprites['eyesextra' + self.eye_colour + str(self.age_sprites[self.age])], (0, 0))
        else:
            if self.specialty in scars1:
                new_sprite.blit(sprites.sprites['scars' + self.specialty + str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars1:
                new_sprite.blit(sprites.sprites['scars' + self.specialty2 + str(self.age_sprites[self.age])], (0, 0))
            new_sprite.blit(sprites.sprites['eyes' + self.eye_colour + str(self.age_sprites[self.age])], (0, 0))

        # draw line art
        if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                              'medicine cat apprentice'] or self.age == 'elder':
            new_sprite.blit(sprites.sprites['lines' + str(self.age_sprites[self.age] + 9)], (0, 0))
        else:
            new_sprite.blit(sprites.sprites['lines' + str(self.age_sprites[self.age])], (0, 0))

        # draw skin and scars2 and scars3
        blendmode = pygame.BLEND_RGBA_MIN
        if self.pelt.length == 'long' and self.status not in ['kitten', 'apprentice',
                                                              'medicine cat apprentice'] or self.age == 'elder':
            new_sprite.blit(sprites.sprites['skinextra' + self.skin + str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars2:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0), special_flags=blendmode)
            if self.specialty2 in scars2:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0), special_flags=blendmode)
            if self.specialty in scars3:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty + str(self.age_sprites[self.age])],
                                (0, 0))
            if self.specialty2 in scars3:
                new_sprite.blit(sprites.sprites['scarsextra' + self.specialty2 + str(self.age_sprites[self.age])],
                                (0, 0))
        else:
            new_sprite.blit(sprites.sprites['skin' + self.skin + str(self.age_sprites[self.age])], (0, 0))
            if self.specialty in scars2:
                new_sprite.blit(sprites.sprites['scars' + self.specialty + str(self.age_sprites[self.age])], (0, 0),
                                special_flags=blendmode)
            if self.specialty2 in scars2:
                new_sprite.blit(sprites.sprites['scars' + self.specialty2 + str(self.age_sprites[self.age])], (0, 0),
                                special_flags=blendmode)
            if self.specialty in scars3:
                new_sprite.blit(sprites.sprites['scars' + self.specialty + str(self.age_sprites[self.age])], (0, 0))
            if self.specialty2 in scars3:
                new_sprite.blit(sprites.sprites['scars' + self.specialty2 + str(self.age_sprites[self.age])], (0, 0))

        # reverse, if assigned so
        if self.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

        # apply
        self.sprite = new_sprite
        self.big_sprite = pygame.transform.scale(new_sprite, (sprites.new_size, sprites.new_size))
        self.large_sprite = pygame.transform.scale(self.big_sprite, (sprites.size * 3, sprites.size * 3))

        # update class dictionary
        self.all_cats[self.ID] = self

    def draw(self, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - sprites.size / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - sprites.size
        self.used_screen.blit(self.sprite, new_pos)

    def draw_big(self, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - sprites.new_size / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - sprites.new_size
        self.used_screen.blit(self.big_sprite, new_pos)

    def draw_large(self, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - sprites.size * 3 / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - sprites.size * 3
        self.used_screen.blit(self.large_sprite, new_pos)

    def save_cats(self):
        cats = {}
        for cat in self.all_cats.values():
            cats[cat.ID]["name_prefix"] = cat.name.prefix
            cats[cat.ID]["name_suffix"] = cat.name.suffix
            cats[cat.ID]["gander"] = cat.gender
            cats[cat.ID]["status"] = cat.status
            cats[cat.ID]["age"] = cat.age  # does this really need to be converted to a string if we store as json?
            cat[cat.ID]["trait"] = cat.trait
            cat[cat.ID]["parent_1"] = cat.parent1
            cat[cat.ID]["parent_2"] = cat.parent2
            cat[cat.ID]["mentor"] = cat.mentor.ID
            cat[cat.ID]["pelt_name"] = cat.pelt.name
            cat[cat.ID]["pelt_color"] = cat.pelt.color
            cat[cat.ID]["pelt_white"] = cat.pelt.white  # does this need to be converted to string
            cat[cat.ID]["pelt_length"] = cat.pelt.length
            cat[cat.ID]["sprite_kitten"] = cat.age_sprites['kitten']  # does this need to be converted to string
            cat[cat.ID]["sprite_adolescent"] = cat.age_sprites['adolescent']  # does this need to be converted to string
            cat[cat.ID]["sprite_adult"] = cat.age_sprites['adult']  # does this need to be converted to string
            cat[cat.ID]["sprite_elder"] = cat.age_sprites['elder']  # need to be a string?
            cat[cat.ID]["sprite_young_adult"] = cat.age_sprites['young adult']
            cat[cat.ID]["senior_adult"] = cat.age_sprites["seinor adult"]
            cat[cat.ID]["eye_color"] = cat.eye_colour
            cat[cat.ID]["reverse"] = cat.reverse  # need to be a string?
            cat[cat.ID]["white_patches"] = cat.white_patches  # need to be string?
            cat[cat.ID]["pattern"] = cat.pattern
            cat[cat.ID]["skin"] = cat.skin
            cat[cat.ID]["skill"] = cat.skill
            cat[cat.ID]["specialty"] = cat.specialty  # need to be a string?
            cat[cat.ID]["moons"] = cat.moons  # need to be a string?
            cat[cat.ID]["mate"] = cat.mate  # need to be a string?
            cat[cat.ID]["dead"] = cat.dead  # need to be a string?
            cat[cat.ID]["sprite_dead"] = cat.age_sprites['dead']  # needs to be a string?
            cat[cat.ID]["scar_2"] = cat.specialty2
            cat[cat.ID]["experience"] = cat.experience
            cat[cat.ID]["dead_for"] = cat.dead_for  # need to be a string?
            cat[cat.ID]["apprentices"] = cat.apprentice  # we can store this as a list in the dict/json is that oK?
            cat[cat.ID][
                "former_apprentices"] = cat.former_apprentices  # we can store this as a list in the dict/json is that oK?

        if game.switches['naming_text'] != '':
            clanname = game.switches['naming_text']
        elif game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        else:
            clanname = game.switches['clan_list'][0]
        with open('saves/' + clanname + 'cats.json', 'w') as write_file:
            data = json.dumps(cats)
            write_file.write(data)

    def load_cats(self):
        cat_data = {}
        if game.switches['clan_list'][0].strip() == '':
            cat_data = {}
        else:
            if os.path.exists('saves/' + game.switches['clan_list'][0] + 'cats.json'):
                with open('saves/' + game.switches['clan_list'][0] + 'cats.json', 'r') as read_file:
                    file = read_file.read()
                    cat_data = json.loads(file)

        if cat_data:
            for cat_id, cat in cat_data.items():
                the_pelt = choose_pelt(cat.get("gender"), cat.get("pelt_color"), cat.get("pelt_white"),
                                       cat.get("pelt_length"), True)
                the_cat = Cat(cat.get("name_prefix"), cat.get("gender"), cat.get("status"), cat.get("parent_1"),
                              cat.get("parent_2"), the_pelt, cat.get("eye_color"), cat.get("name_suffix"),
                              cat_id, cat.get("moons"), False)
                the_cat.age = cat.get("age")
                the_cat.mentor = cat.get("mentor")
                age_sprite_list = [('kitten', "sprite_kitten"), ("adolescent", "sprite_adolescent"),
                                   ("adult", "sprite_adult"), ("elder", "sprite_elder"),
                                   ("young adult", "sprite_young_adult"),
                                   ("senior adult", "sprite_senior_adult")]
                for age_sprite in age_sprite_list:
                    the_cat.age_sprites[age_sprite[0]] = cat.get(age_sprite[1])
                the_cat.reverse = cat.get("reverse")
                the_cat.white_patches = cat.get("white_patches")
                the_cat.pattern = cat.get("pattern")
                the_cat.trait = cat.get('trait')
                the_cat.skin = cat.get('skin')
                the_cat.specialty = cat.get("specialty")
                the_cat.specialty2 = cat.get("specialty_2")
                the_cat.experience = cat.get("experience")
                if the_cat.experience:
                    experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high',
                                        'very high', 'master', 'max']
                    the_cat.experience_level = experiencelevels[math.floor(int(the_cat.experience) / 10)]
                else:
                    the_cat.experience = 0
                the_cat.moons = cat.get('moons')
                the_cat.mate = cat.get("mate")
                the_cat.dead = cat.get('dead')
                if the_cat.dead:
                    the_cat.age_sprites['dead'] = cat.get("sprite_dead")
                    the_cat.dead_for = cat.get("dead_for")
                    the_cat.skill = cat.get("skill")

                the_cat.apprentice = cat.get("apprentices")
                the_cat.former_apprentices = cat.get("former_apprentices")
                # CAT: ID(0) - prefix:suffix(1) - gender(2) - status(3) - age(4) - trait(5) - parent1(6) - parent2(7)
                #  - mentor(8)
                # PELT: pelt(9) - colour(10) - white(11) - length(12)
                # SPRITE: kitten(13) - apprentice(14) - warrior(15) - elder(16) - eye colour(17) - reverse(18)
                # - white patches(19) - pattern(20) - skin(21) - skill(22) - NONE(23) - spec(24) - moons(25) - mate(26)
                # dead(27) - SPRITE:dead(28)

            game.switches['error_message'] = 'There was an error loading this clan\'s mentors/apprentices'

            for n in self.all_cats.values():
                # Load the mentors and apprentices after all cats have been loaded
                n.mentor = cat_class.all_cats.get(n.mentor)
                apps = []
                former_apps = []
                for app_id in n.apprentice:
                    app = cat_class.all_cats.get(app_id)
                    # Make sure if cat isn't an apprentice, they're a former apprentice
                    if 'apprentice' in app.status:
                        apps.append(app)
                    else:
                        former_apps.append(app)
                for f_app_id in n.former_apprentices:
                    f_app = cat_class.all_cats.get(f_app_id)
                    former_apps.append(f_app)
                n.apprentice = apps
                n.former_apprentices = former_apps
                n.update_sprite()

            game.switches['error_message'] = ''

    def load(self, cat_dict):
        """ A function that takes a dictionary containing other dictionaries with attributes and values of all(?)
         cats from a save file and redistributes the values onto new cat object attributes.
         The dict is in form:
         cat_dict = { ID : [(prefix, suffix), {attribute: value}] }"""
        for cat in cat_dict.keys():  # cat is the ID of the cats
            # create the cat object
            name = cat_dict[cat][0]
            new_cat = Cat(prefix=name[0], suffix=name[1], ID=cat)

            # put attribute dict into easier accessible variable
            attr_dict = cat_dict[cat][1]

            # go through attributes
            for attr in attr_dict.keys():
                value = attr_dict[attr]  # value of attribute
                # turn value into other forms than string if necessary
                if value == 'None':
                    value = None
                elif value == 'False':
                    value = False
                elif value == 'True':
                    value = True

                # Assign values to cat object
                if attr == 'status':
                    new_cat.status = value  # STATUS
                if attr == 'parent1':
                    new_cat.parent1 = value  # PARENT1
                if attr == 'parent2':
                    new_cat.parent2 = value  # PARENT2
                if attr == 'sex':
                    new_cat.gender = value  # SEX / GENDER
                if attr == 'moons':
                    new_cat.moons = int(value)  # MOONS
                if attr == 'age':
                    new_cat.age = int(value)  # AGE
                if attr == 'dead':
                    new_cat.dead = value  # DEAD ( OR NOT )
                if attr == 'dead_for':
                    new_cat.dead_for = int(value)  # DEAD FOR ( MOONS )
                if attr == 'pelt':
                    new_cat.pelt = value  # PELT
                if attr == 'eye_colour':
                    new_cat.eye_colour = value  # EYES
                if attr == 'mate':
                    new_cat.mate = value  # MATE
                if attr == 'trait':
                    new_cat.trait = value  # TRAIT
                if attr == 'skill':
                    new_cat.skill = value  # SKILL
                if attr == 'mentor':
                    new_cat.mentor = value

    def describe_color(self):
        color_name = ''
        if self.pelt.name == 'SingleColour' or self.pelt.name == 'TwoColour':
            color_name = str(self.pelt.colour).lower()
        elif self.pelt.name == "Tabby":
            color_name = str(self.pelt.colour).lower() + ' tabby'
        elif self.pelt.name == "Speckled":
            color_name = str(self.pelt.colour).lower() + ' speckled'
        elif self.pelt.name == "Tortie" or self.pelt.name == "Calico":
            color_name = 'tortie'  # check for calico or for white later

        # not enough to comment on
        if self.white_patches is None or self.white_patches in ['EXTRA']:
            color_name = color_name  # what is this even lol
        # enough to comment but not make calico
        elif self.white_patches in ['LITTLE', 'LITTLECREAMY', 'LIGHTTUXEDO', 'BUZZARDFANG']:
            color_name = color_name + ' and white'
        # and white
        elif self.white_patches in ['ANY', 'TUXEDO', 'ANY2', 'ANYCREAMY', 'TUXEDOCREAMY', 'ANY2CREAMY', 'BROKEN']:
            if color_name == 'tortie':
                color_name = 'calico'
            else:
                color_name = color_name + ' and white'
        # white and
        elif self.white_patches in ['VAN', 'VANCREAMY', 'ONEEAR', 'LIGHTSONG']:
            color_name = 'white and ' + color_name
        # colorpoint
        elif self.white_patches in ['COLOURPOINT', 'RAGDOLL', 'COLOURPOINTCREAMY']:
            color_name = color_name + ' point'
            if color_name == 'darkginger point':
                color_name = 'flame point'
        # vitiligo
        elif self.white_patches in ['VITILIGO']:
            color_name = color_name + ' with vitiligo'
        else:
            color_name = color_name + ' color error'

        if color_name == 'tortie':
            color_name = 'tortoiseshell'

        if color_name == 'white and white':
            color = name = 'white'

        return color_name

    def describe_cat(self):
        if self.gender == 'male':
            sex = 'tom'
        else:
            sex = 'she-cat'
        description = self.describe_color()
        description += ' ' + str(self.pelt.length).lower() + '-furred ' + sex
        return description


# CAT CLASS ITEMS
cat_class = Cat(example=True)
game.cat_class = cat_class

# The randomized cat sprite in Main Menu screen
example_cat = Cat(status=choice(["kitten", "apprentice", "warrior", "elder"]), example=True)
example_cat.update_sprite()


# Twelve example cats
def example_cats():
    e = random.sample(range(12), 2)
    for a in range(12):
        if a in e:
            game.choose_cats[a] = Cat(status='warrior')
        else:
            game.choose_cats[a] = Cat(status=choice(['kitten', 'apprentice', 'warrior', 'warrior', 'elder']))
        game.choose_cats[a].update_sprite()
