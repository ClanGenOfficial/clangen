from random import choice, randint
from tkinter.messagebox import NO
from .game_essentials import *
import copy

# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['Is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them'],
    "troublesome": ['Made (cat) and (cat) start an argument'],
    "sneaky": ['Is gossiping about (cat) and (cat)'],
    "like": '(cat) confesses to (cat) that they think they like (cat)',
    "trick": 'Has successfully tricked (cat) into believing a crazy tale about the clan leader'
}

SPECIAL_CHARACTER = {
    "strange": ['Is following (cat) around', 'Tells (cat) that they\'re pelt looks like a different colour today'],
    "bloodthirsty": ['Talks to (cat) how best to kill prey, very enthusiastic'],
    "ambitious": ['Has been listening to (elder/deputy/senior warrior/leader) closely'],
    "righteous": ['Makes sure (cat) is following the warrior code'],
    "fierce": [ 'Is not backing down in an argument with (cat)', 
                'Is telling (cat) in great detail how they would protect them from any danger'],
    "nervous": ['Is stuttering while speaking to (cat)'],
    "strict":['Scorns (apprentice) for not catching enough prey'],
    "charismatic": ['Charms (cat)', 'Smiles at (cat) whenever they meet', 'Knows what to say to make (cat) feel better', 
                    'Compliments (cat) for their good disposition'],
    "calm": ['Relaxing with (cat)','Is soothing (cat)\'s irrational thoughts', 'Is helping (cat) calm down'],
    "loving": [ 'Is making sure (cat) knows that they are loved','Is telling (cat) how much they cherish them', 
                'Is purring loudly to comfort (cat)'],
    "playful": ['Is playing tag with (cat)'],
    "cold": ['Hissed at (cat)', 'Tells (cat) to leave them alone', 'Glaring at (cat) from across the camp'],
    "vengeful": ['Thinking about how (cat) wronged them', 'Is watching (cat) scornfully', 'Is glaring daggers at (cat)'],
    "shameless": ['Is asking (cat) to tell them about how good they look'],
    "troublesome": ['Pulled a prank on (cat)', 'Blamed (cat) for their own mistake', 'Won\'t stop bothering (cat)',
                    'Feels bad that they caused a problem for (cat)'],
    "empathetic": [ 'Listening to (elder)\'s woes', 'Is listening to (cat)\'s troubles',
                    'Noticed (apprentice) was struggling, and offered to help them'],
    "adventurous": ['Wants to explore Twoleg place with (cat)', 'Wants to sneak along the border with (cat)', 
                    'Tells (cat) that there\'s so much to see in the world!'],
    "thoughful": [  'Gave (cat) their favorite piece of prey', 'Is being quite considerate with (cat)', 
                    'Took the time to help (apprentice) work through a technique they are struggling with'],
    "compassionate": [  'Curled around (cat) to share warmth', 'Lets (cat) have the last piece of fresh kill', 
                        'Goes out of their way to cheer up (cat)', 'Listening to (cat)\'s problems',
                        'Gives (cat) an item they may like', 'Helps (elder) get around camp'],
    "childish": ['Chases around a butterfly', 'Is hiding behind a bush ready to pounce on (cat)'],
    "confident": ['Is building up (cat)\'s confidence', 'Stands tall when (cat) walks by'],
    "careful": ['Tells (cat) to get their ailment treated as soon as possible', 'Chiding (cat) for being so reckless',
                'Apologized to (cat) for possibly hurting their feelings'],
    "altruistic": ['Let (cat) lean on their shoulder after a recent injury', 'Is poised to help train (apprentice)'],
    "bold": ['Winks at (cat)', 'Challenged (cat) to spar with them'],
    "patient": ['Watching the shooting stars with (cat)', 
                'Calmly explains hunting techniques to (cat) again for the fourth time today'],
    "sneaky": [ 'Is gossiping about (cat)', 'Is teaching (cat) how to walk without making a sound', 
                'Is showing (cat) how to sneak up on their enemies'],
    "wise": ['Is giving (cat) advice'],
    "cowardly": ['Is hiding from (cat)'],
    "impulsive": [  'Crashes into (cat) while eager for patrol', 'Rejects (cat)\'s advice without letting them finish', 
                    'Interrupts (cat) during a conversation'],
    "tidy": [   'Is annoyed by the mess (cat) made', 'Grooms the grime off (cat)\'s pelt', 
                'Is cross with (cat) for getting dirt all over the fresh-kill pile'],
    "dreamy": ['Talks about dreams with (cat)', 'Gets distracted from conversation with (cat)']
}

# IN increase or decrease
NOT_AGE_SPECIFIC = {
    "unfriendly": ['Has successfully tricked (cat) into believing a crazy tale about the clan leader',
                   'Doesn\'t think that (cat) has been completely honest lately',
                   'Is mocking (cat)', 'Ignores (cat)','Is telling jokes about (cat)',
                   'Is spreading a rumour about (cat)'],
    "neutral": ['Whines about (cat)', 'Is telling a story to (cat)', 'Is talking with (cat)',
                'Is sharing prey with (cat)', 'Had a huge argument with (cat)', 'Had a fight with (cat)'],
    "friendly": ['Is sharing tongue with (cat)'],
    "close": ['Tells (cat) a secret']
}

KITTEN_TO_OTHER = {
    "kitten": {
        "unfriendly": ['Tries to scare (cat)'],
        "neutral": ['Has a mock battle with (cat)', 
                    'Is jealous that (cat) is getting more attention than them',
                    'Plays mossball with (cat)', 'Sticks their tongue out at (cat)',
                    'Is pretending to be (cat)'],
        "friendly": ['Chomps on (cat)\'s ear',
                     'Pretends to be a warrior with (cat)',
                     'Is pretending to ward off foxes with (cat)',
                     'Is pretending to fight off badgers with (cat)',
                     'Is racing (cat) back and forth across the camp clearing'],
        "close": [  'Comes up with a plan to sneak out of camp with (cat)']
    },
    "apprentice": {
        "unfriendly": [],
        "neutral": ['Sticks their tongue out at (cat)',
                    'Is hiding under a bush from (cat), but they can\'t stop giggling',
                    'Is pretending to be (cat)'],
        "friendly": [],
        "close": []
    },
    "warrior": {
        "unfriendly": [],
        "neutral": ['Is biting (cat)\'s tail',
                    'Sticks their tongue out at (cat)',
                    'Is demanding (cat)\'s attention', 
                    'Is hiding under a bush from (cat), but they can\'t stop giggling',
                    'Is pretending to be (cat)'],
        "friendly": [],
        "close": []
    },
    "elder": {
        "unfriendly": [],
        "neutral": ['Sticks their tongue out at (cat)', 
                    'Is hiding under a bush from (cat), but they can\'t stop giggling'],
        "friendly": [],
        "close": []
    }
}

APPRENTICE_TO_OTHER = {
    "kitten": {
        "unfriendly": [],
        "neutral": ['Trips over (cat)'],
        "friendly": [],
        "close": []
    },
    "apprentice": {
        "unfriendly": [],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously',
                    'Has a mock battle with (cat)'],
        "friendly": [],
        "close": []
    },
    "warrior": {
        "unfriendly": [],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously'],
        "friendly": [],
        "close": []
    },
    "elder": {
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

WARRIOR_TO_OTHER = {
    "kitten": {
        "unfriendly":['Is scolding (cat)'],
        "neutral": ['Trips over (cat)', 'Had to nip (cat) on the rump because they were being naughty',
                    'Is watching (cat) perform an almost-decent hunting crouch', 
                    'Is watching over (cat)'],
        "friendly": ['Is giving (cat) a badger ride on their back!', 'Hopes that their own kits are as cute as (cat) someday',
                     'Is promising to take (cat) outside of camp if they behave', 'Gave (cat) a trinket they found while out on patrol today'],
        "close":[],
    },
    "apprentice": {
        "unfriendly": ['Is scolding (cat)'],
        "neutral": ['Is giving advice to (cat)', 'Is watching (cat) perform an almost-decent hunting crouch',
                    'Is telling (cat) about a hunting technique', 'Is giving (cat) a task'],
        "friendly": [],
        "close": []
    },
    "warrior": {
        "unfriendly": [],
        "neutral": ['Is telling (cat) about a hunting technique',
                    'Is giving (cat) a task','Is frustrated that (cat) won\'t take their duties more seriously'],
        "friendly": ['Has been spending time with (cat) lately',
                     'Is telling (cat) about their own days as an apprentice'],
        "close": ['Just told (cat) a hilarious joke']
    },
    "elder": {
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

ELDER_TO_OTHER = {
    "kitten": {
        "unfriendly": ['Is scolding (cat)'],
        "neutral": [],
        "friendly": [],
        "close": []
    },
    "apprentice": {
        "unfriendly": ['Is scolding (cat)'],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously'],
        "friendly": [],
        "close": []
    },
    "warrior": {
        "unfriendly": ['Is scolding (cat)'],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously'],
        "friendly": [],
        "close": []
    },
    "elder": {
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

LOVE = {
    "love_interest_only": ['Is developing a crush on (cat)', 'Is admiring (cat) from afar...', 'Is spending a lot of time with (cat)',
                            'Gave a pretty flower they found to (cat)'],
    "love_interest": [  'Can\'t seem to stop talking about (cat)', 'Would spend the entire day with (cat) if they could', 
                        'Keeps shyly glancing over at (cat) as the clan talks about kits', 
                        'Is thinking of the best ways to impress (cat)', 'Doesn\'t want (cat) to overwork themselves', 
                        'Is rolling around a little too playfully with (cat)...', 
                        'Is wondering what it would be like to grow old with (cat)', 'Thinks that (cat) is really funny',
                        'Thinks that (cat) is really charming'],
    "mates": ['Was caught enjoying a moonlit stroll with (cat) last night...']
}

LEADER = {
    "from":{
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    },
    "to":{
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

DEPUTY = {
    "from":{
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    },
    "to":{
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

MEDICINE = {
    "from":{
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    },
    "to":{
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}


# How increasing one state influences another directly: (an increase of one state doesn't trigger a chain reaction)
# increase romantic_love -> decreases: dislike | increases: like, comfortable
# increase like -> decreases: dislike | increases: comfortable
# increase dislike -> decreases: romantic_love, like | increases: -
# increase admiration -> decreases: - | increases: -
# increase comfortable -> decreases: jealousy, dislike | increases: trust, like
# increase jealousy -> decreases: - | increases: dislike
# increase trust -> decreases: dislike | increases: comfortable

# !! DECREASING ONE STATE DOES'T INFLUENCE OTHERS !!

# This defines effect the action has, not every action has to have a effect
INCREASE = {
    "from": {
        "romantic_love": ['Is developing a crush on (cat)', 'Is admiring (cat) from afar...', 
                          'Is spending a lot of time with (cat)', 'Gave a pretty flower they found to (cat)',
                          'Can\'t seem to stop talking about (cat)', 'Would spend the entire day with (cat) if they could',
                          'Keeps shyly glancing over at (cat) as the clan talks about kits', 
                          'Is rolling around a little too playfully with (cat)...',
                          'Was caught enjoying a moonlit stroll with (cat) last night...'],
        "like": ['Is telling a story to (cat)','Is talking with (cat)','Pretends to be a warrior with (cat)',
                'Is giving (cat) a badger ride on their back!', 'Hopes that their own kits are as cute as (cat) someday',
                'Is sharing tongues with (cat)','Has been spending time with (cat) lately','Just told (cat) a hilarious joke',
                'Plays mossball with (cat)'],
        "dislike": ['Is mocking (cat)', 'Ignores (cat)', 'Sticks their tongue out at (cat)','Had an huge argument with (cat)',
                    'Had a fight with (cat)'],
        "admiration": ['Is watching (cat) perform an almost-decent hunting crouch'],
        "comfortable": ['Is telling a story to (cat)','Is sharing prey with (cat)','Tells (cat) a secret',
                        'Is sharing tongues with (cat)','Comes up with a plan to sneak out of camp with (cat)'],
        "jealousy": ['Is jealous that (cat) is getting more attention than them'],
        "trust":['Is talking with (cat)','Tells (cat) a secret','Comes up with a plan to sneak out of camp with (cat)']
    },
    "to": {
        "romantic_love": ['Is spending a lot of time with (cat)', 'Gave a pretty flower they found to (cat)',
                          'Is rolling around a little too playfully with (cat)...', 
                          'Was caught enjoying a moonlit stroll with (cat) last night...'],
        "like": ['Is telling a story to (cat)','Is talking with (cat)','Is sharing tongue with (cat)',
                'Is giving (cat) a badger ride on their back!', 'Is promising to take (cat) outside of camp if they behave',
                'Gave (cat) a trinket they found while out on patrol today', 'Is telling (cat) about a hunting technique',
                'Is sharing tongues with (cat)','Has been spending time with (cat) lately',
                'Just told (cat) a hilarious joke', 'Plays mossball with (cat)','Pretends to be a warrior with (cat)',
                'Comes up with a plan to sneak out of camp with (cat)'],
        "dislike": ['Is mocking (cat)','Is telling jokes about (cat)','Sticks their tongue out at (cat)',
                    'Is spreading a rumour about (cat)','Tries to scare (cat)','Had an huge argument with (cat)',
                    'Had a fight with (cat)'],
        "admiration": ['Is promising to take (cat) outside of camp if they behave', 'Is telling (cat) about a hunting technique'],
        "comfortable": ['Is telling a story to (cat)','Is sharing prey with (cat)','Tells (cat) a secret', 
                        'Is sharing tongues with (cat)','Is telling (cat) about their own days as an apprentice',
                        'Comes up with a plan to sneak out of camp with (cat)'],
        "jealousy": [],
        "trust":['Is talking with (cat)','Tells (cat) a secret','Tries to scare (cat)',
                'Comes up with a plan to sneak out of camp with (cat)']
    }
}

DECREASE  = {
    "from": {
        "romantic_love": [],
        "like": ['Is telling jokes about (cat)', 'Whines about (cat)'],
        "dislike": [],
        "admiration": ['Is frustrated that (cat) won\'t take their duties more seriously'],
        "comfortable": [],
        "jealousy": [],
        "trust": []
    },
    "to": {
        "romantic_love": [],
        "like": ['Is telling jokes about (cat)'],
        "dislike": [],
        "admiration": ['Is scolding (cat)'],
        "comfortable": [],
        "jealousy": [],
        "trust": ['Is spreading a rumour about (cat)','Trips over (cat)', 'Doesn\'t think that (cat) has been completely honest lately',
                'Has successfully tricked (cat) into believing a crazy tale about the clan leader']
    }
}

# weigths of the stat change
DIRECT_INCREASE = 8
DIRECT_DECREASE = 5
INDIRECT_INCREASE = 6
INDIRECT_DECREASE = 3

class Relationship(object):
    def __init__(self, cat_from, cat_to, mates=False, family=False, romantic_love=0, platonic_like=0, dislike=0, admiration=0, comfortable=0, jealousy=0, trust=0) -> None:        
        # involved cat
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposit_relationship = None #link to oppositting relationship will be created later
        self.effect = 'neutral effect'

        # check if cats are related
        parents_to = [self.cat_to.parent1, self.cat_to.parent2]
        parents_from = [self.cat_from.parent1, self.cat_from.parent2]
        parents_to = set([c for c in parents_to if c is not None])
        parents_from = set([c for c in parents_from if c is not None])
        # if there is any same element in any of the lists, they are related
        if parents_to & parents_from:
            family = True
            self.family = True

        if mates and romantic_love == 0:
            romantic_love = 50
            comfortable = 40
        
        if family and platonic_like == 0:
            platonic_like = 20
            comfortable = 10

        # each stat can go from 0 to 100
        self.romantic_love = romantic_love
        self.platonic_like = platonic_like
        self.dislike = dislike
        self.admiration = admiration
        self.comfortable = comfortable
        self.jealousy = jealousy
        self.trust = trust

        self.current_changes_to = []
        self.current_changes_from = []

    def link_relationship(self):
        """Add the other relationship object to this easly access and change the other side."""
        opposite_relationship = list(filter(lambda r: r.cat_to.ID == self.cat_from.ID , self.cat_to.relationships))
        if opposite_relationship is not None or len(opposite_relationship) > 0:
            self.opposit_relationship = opposite_relationship[0]

    def start_action(self):
        """This function checks current state of relationship and decides which actions can happen."""
        # update relationship
        if self.cat_from.mate == self.cat_to:
            self.mates = True

        if self.opposit_relationship is None:
            self.link_relationship()

        self.current_changes_to = []
        self.current_changes_from = []

        # get action possibilities
        action_possibilies = self.get_action_possibilities()

        # check if the action is relevant (action of characters include age in the replacement string)
        action_relevant = False
        action = None
        while not action_relevant:
            action = choice(action_possibilies)
            relevant_ages = action[action.find("(")+1:action.find(")")]
            relevant_ages = relevant_ages.split(',')
            relevant_ages = [age.strip() for age in relevant_ages]

            if len(relevant_ages) == 1 and relevant_ages[0] == 'cat':
                action_relevant = True
            if self.cat_to.age in relevant_ages:
                action_relevant = True
                    
        # change the stats of the relationships
        self.affect_own_relationship(action)
        self.affect_other_relationship(action)

        # broadcast action
        string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
        action_string = action.replace(string_to_replace, str(self.cat_to.name)) 
        self.action_results(action_string)
        rel_stat_info_from = '('
        rel_stat_info_from += ','.join(self.current_changes_from) + '[' + str(self.cat_from.name) + '])'
        rel_stat_info_to = '('
        rel_stat_info_to += ','.join(self.current_changes_to) + '[' + str(self.cat_to.name) + '])'

        game.relation_events_list.append(f"{str(self.cat_from.name)} - {action_string} ({self.effect})")

        self.effect = 'neutral effect'
        #if len(self.current_changes_from) > 0:
        #    game.relation_events_list.append(rel_stat_info_from)
        #if len(self.current_changes_to) > 0:
        #    game.relation_events_list.append(rel_stat_info_to)

    def action_results(self, action_string):
        """Things that can happen, this events will show on the """

        # new mates
        cat_to_no_mate = self.cat_to.mate == None or self.cat_to.mate == ''
        cat_from_no_mate = self.cat_from.mate == None or self.cat_from.mate == ''
        both_no_mates = cat_to_no_mate and cat_from_no_mate
        if self.romantic_love > 25 and self.opposit_relationship.romantic_love > 25 and both_no_mates:
            self.cat_to.mate = self.cat_from.ID
            self.cat_from.mate = self.cat_to.ID
            self.mates = True
            game.cur_events_list.append(f'{str(self.cat_from.name)} and {str(self.cat_to.name)} have become mates')
        
        # breakup and new mate
        #if game.settings['affair']:
        #    if self.romantic_love > 30 and self.opposit_relationship.romantic_love > 30:
        #        print("AFFAIR")
        
        # breakup
        if self.mates and 'negative' in self.effect:
            chance_number = 30
            if 'fight' in action_string:
                chance_number = 20
            chance = randint(0,chance_number)
            if chance == 1 or self.dislike > 20:
                self.cat_to.mate = None
                self.cat_from.mate = None
                self.romantic_love = 10
                self.mates = False
                game.cur_events_list.append(f'{str(self.cat_from.name)} and {str(self.cat_to.name)} broke up')

    def get_action_possibilities(self):
        """Creates a list of possibles actions of this relationship"""
        # check if opposit_relationship is here, otherwise creates it       
        action_possibilies = copy.deepcopy(NOT_AGE_SPECIFIC['neutral'])

        key = self.cat_to.status
        if key == "senior warrior" or key == "deputy" or\
                key == "leader" or key == "medicine cat":
            key = "warrior"
        
        if key == "medicine cat apprentice":
            key = "apprentice"

        # NORMAL INTERACTIONS
        # check how the relationship is
        relation_keys = ['neutral']
        if self.dislike > 20:
            action_possibilies += NOT_AGE_SPECIFIC['unfriendly']
            relation_keys.append('unfriendly')
            if self.dislike > 30:
                relation_keys.append('unfriendly')
        if self.platonic_like > 40 or self.comfortable > 30:
            action_possibilies += NOT_AGE_SPECIFIC['friendly']
            relation_keys.append('friendly')
        if self.platonic_like > 60 and self.comfortable > 50 and self.trust > 50:
            action_possibilies += NOT_AGE_SPECIFIC['close']
            relation_keys.append('close')

        # add the interactions to the posssible ones
        if self.cat_from.status == "kitten":
            for relation_key in relation_keys:
                action_possibilies += KITTEN_TO_OTHER[key][relation_key]
        if self.cat_from.status == "apprentice":
            for relation_key in relation_keys:
                action_possibilies += APPRENTICE_TO_OTHER[key][relation_key]
        if (self.cat_from.status == "warrior" or self.cat_from.status == "senior warrior"):
            for relation_key in relation_keys:
                action_possibilies += WARRIOR_TO_OTHER[key][relation_key]
        if self.cat_from.status == "elder":
            for relation_key in relation_keys:
                action_possibilies += ELDER_TO_OTHER[key][relation_key]

        # STATUS INTERACTIONS
        if self.cat_from.status == 'leader':
            for relation_key in relation_keys:
                action_possibilies += LEADER['from'][relation_key]
        if self.cat_to.status == 'leader':
            for relation_key in relation_keys:
                action_possibilies += LEADER['to'][relation_key]
        
        if self.cat_from.status == 'deputy':
            for relation_key in relation_keys:
                action_possibilies += LEADER['from'][relation_key]
        if self.cat_to.status == 'deputy':
            for relation_key in relation_keys:
                action_possibilies += LEADER['to'][relation_key]
        
        if self.cat_from.status == 'medicine cat':
            for relation_key in relation_keys:
                action_possibilies += MEDICINE['from'][relation_key]
        if self.cat_to.status == 'medicine cat':
            for relation_key in relation_keys:
                action_possibilies += MEDICINE['to'][relation_key]

        # CHARACTERISTIC INTERACTION
        character_keys = SPECIAL_CHARACTER.keys()
        if self.cat_from.trait in character_keys:
            action_possibilies += SPECIAL_CHARACTER[self.cat_from.trait]

        # LOVE
        # check mate status and settings
        cat_from_has_mate = self.cat_from.mate != None or self.cat_from.mate != ''
        if cat_from_has_mate and not self.mates and not game.settings['affair']:
            return action_possibilies

        # chance to fall in love with some the character is not close to:
        # check ages of cats
        age_group1 = ['adolescent', 'young adult', 'adult']
        age_group2 = ['adult', 'senior adult', 'elder']
        both_are_kits = self.cat_from.age == 'kitten' and self.cat_to.age == 'kitten'
        none_of_them_are_kits = self.cat_from.age != 'kitten' and self.cat_to.age != 'kitten'
        both_in_same_age_group = (self.cat_from.age in age_group1 and self.cat_to.age in age_group1) or\
            (self.cat_from.age in age_group2 and self.cat_to.age in age_group2)

        love_p = randint(0,30)
        if not self.family and (both_are_kits or none_of_them_are_kits) and both_in_same_age_group:
            if self.platonic_like > 40 or love_p == 1 or self.romantic_love > 5:
                action_possibilies = action_possibilies + LOVE['love_interest_only']

            if self.opposit_relationship.romantic_love > 20:
                action_possibilies = action_possibilies + LOVE['love_interest_only']

            if self.romantic_love > 25 and self.opposit_relationship.romantic_love > 15:
                action_possibilies = action_possibilies + LOVE['love_interest']

            if self.mates and self.romantic_love > 30 and self.opposit_relationship.romantic_love > 25 :
                action_possibilies = action_possibilies + LOVE['mates']

        return action_possibilies

    def affect_own_relationship(self, action):
        """Affect the own relationship according to the action."""
        # for easier value change
        number_increase = DIRECT_INCREASE
        number_decrease = DIRECT_DECREASE

        # increases
        if action in INCREASE['from']['romantic_love']:
            self.romantic_love += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' rom. love ')
            self.effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['from']['like']:
            self.platonic_like += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' like ')
            self.effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['from']['dislike']:
            self.dislike += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' dislike ')
            self.effect = 'negative effect'
            # indirekt influences
            self.platonic_like -= INDIRECT_DECREASE
            self.romantic_love -= INDIRECT_DECREASE
            # if dislike reaced a certain point, and is increased, like will get decrease more
            if self.dislike > 30:
                self.platonic_like -= INDIRECT_DECREASE
                self.romantic_love -= INDIRECT_DECREASE
        if action in INCREASE['from']['admiration']:
            self.admiration += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' admir. ')
            self.effect = 'positive effect'
        if action in INCREASE['from']['comfortable']:
            self.comfortable += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' comfortable ')
            self.effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.jealousy -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.trust += INDIRECT_INCREASE
        if action in INCREASE['from']['jealousy']:
            self.jealousy += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' jeal. ')
            self.effect = 'positive effect'
        if action in INCREASE['from']['trust']:
            self.trust += number_increase
            self.current_changes_from.append('+ ' + str(number_increase) + ' trust ')
            self.effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE


        # decreases
        if action in DECREASE['from']['romantic_love']:
            self.romantic_love -= number_decrease
            self.current_changes_from.append('- ' + str(number_decrease) + ' rom. love ')
            self.effect = 'negative effect'
        if action in DECREASE['from']['like']:
            self.platonic_like -= number_decrease
            self.current_changes_from.append(('- ' + str(number_decrease) + ' like '))
            self.effect = 'negative effect'
        if action in DECREASE['from']['dislike']:
            self.dislike -= number_decrease
            self.current_changes_from.append('- ' + str(number_decrease) + ' dislike ')
            self.effect = 'positive effect'
        if action in DECREASE['from']['admiration']:
            self.admiration -= number_decrease
            self.current_changes_from.append('- ' + str(number_decrease) + ' admir. ')
            self.effect = 'negative effect'
        if action in DECREASE['from']['comfortable']:
            self.comfortable -= number_decrease
            self.current_changes_from.append('- ' + str(number_decrease) + ' comfortable ')
            self.effect = 'negative effect'
        if action in DECREASE['from']['trust']:
            self.trust -= number_decrease
            self.current_changes_from.append('- ' + str(number_decrease) + ' trust ')
            self.effect = 'negative effect'
        if action in DECREASE['from']['jealousy']:
            self.jealousy -= number_decrease
            self.current_changes_from.append('- ' + str(number_decrease) + ' jeal. ')
            self.effect = 'negative effect'

        self.cut_boundries()

    def affect_other_relationship(self, action):
        """Affect the other relationship according to the action."""
        # for easier value change
        number_increase = DIRECT_INCREASE
        number_decrease = DIRECT_DECREASE

        # increases
        if action in INCREASE['to']['romantic_love']:
            self.opposit_relationship.romantic_love += number_increase
            self.current_changes_to.append('+ ' + str(number_increase) + ' rom. love ')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['to']['like']:
            self.opposit_relationship.platonic_like += number_increase
            self.current_changes_to.append('+ ' + str(number_increase) + ' like ')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['to']['dislike']:
            self.opposit_relationship.dislike += number_increase
            self.current_changes_to.append('+ ' + str(number_increase) + ' dislike ')
            # indirekt influences
            self.opposit_relationship.platonic_like -= INDIRECT_DECREASE
            self.opposit_relationship.romantic_love -= INDIRECT_DECREASE
            # if dislike reaced a certain point, and is increased, like will get decrease more
            if self.dislike > 30:
                self.opposit_relationship.platonic_like -= INDIRECT_DECREASE
                self.opposit_relationship.romantic_love -= INDIRECT_DECREASE
        if action in INCREASE['to']['admiration']:
            self.opposit_relationship.admiration += number_increase
            self.current_changes_to.append('+ ' + str(number_increase) + ' admir. ')
        if action in INCREASE['to']['comfortable']:
            self.opposit_relationship.comfortable += number_increase
            self.current_changes_to.append('+ ' + str(number_increase) + ' comfortable ')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.jealousy -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.trust += INDIRECT_INCREASE
        if action in INCREASE['to']['jealousy']:
            self.opposit_relationship.jealousy -= number_decrease
            self.current_changes_to.append('+ ' + str(number_increase) + ' jeal. ')
        if action in INCREASE['to']['trust']:
            self.opposit_relationship.trust += number_increase
            self.current_changes_to.append('+ ' + str(number_increase) + ' trust ')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE


        # decreases
        if action in DECREASE['to']['romantic_love']:
            self.opposit_relationship.romantic_love -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' rom. love ')
        if action in DECREASE['to']['like']:
            self.opposit_relationship.platonic_like -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' like ')
        if action in DECREASE['to']['dislike']:
            self.opposit_relationship.dislike -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' dislike ')
        if action in DECREASE['to']['admiration']:
            self.opposit_relationship.admiration -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' admir. ')
        if action in DECREASE['to']['comfortable']:
            self.opposit_relationship.comfortable -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' comfortable ')
        if action in DECREASE['to']['trust']:
            self.opposit_relationship.trust -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' trust ')
        if action in DECREASE['to']['jealousy']:
            self.opposit_relationship.jealousy -= number_decrease
            self.current_changes_to.append('- ' + str(number_decrease) + ' jeal. ')

        self.cut_boundries()

    def cut_boundries(self):
        upper_bound = 100
        lower_bound = 0

        """Cut the stats of involved relationships."""
        # current_relationship
        self.romantic_love = upper_bound if self.romantic_love > upper_bound else self.romantic_love
        self.romantic_love = lower_bound if self.romantic_love < lower_bound else self.romantic_love
        self.platonic_like = upper_bound if self.platonic_like > upper_bound else self.platonic_like
        self.platonic_like = lower_bound if self.platonic_like < lower_bound else self.platonic_like
        self.dislike = upper_bound if self.dislike > upper_bound else self.dislike
        self.dislike = lower_bound if self.dislike < lower_bound else self.dislike
        self.admiration = upper_bound if self.admiration > upper_bound else self.admiration
        self.admiration = lower_bound if self.admiration < lower_bound else self.admiration
        self.comfortable = upper_bound if self.comfortable > upper_bound else self.comfortable
        self.comfortable = lower_bound if self.comfortable < lower_bound else self.comfortable
        self.trust = upper_bound if self.trust > upper_bound else self.trust
        self.trust = lower_bound if self.trust < lower_bound else self.trust
        self.jealousy = upper_bound if self.jealousy > upper_bound else self.jealousy
        self.jealousy = lower_bound if self.jealousy < lower_bound else self.jealousy
        
        # opposit relationship
        if self.opposit_relationship == None:
            self.link_relationship()
        if len(self.opposit_relationship) > 0 and self.opposit_relationship is not None:
            self.opposit_relationship.romantic_love = upper_bound if self.opposit_relationship.romantic_love > upper_bound else self.opposit_relationship.romantic_love
            self.opposit_relationship.romantic_love = lower_bound if self.opposit_relationship.romantic_love < lower_bound else self.opposit_relationship.romantic_love
            self.opposit_relationship.platonic_like = upper_bound if self.opposit_relationship.platonic_like > upper_bound else self.opposit_relationship.platonic_like
            self.opposit_relationship.platonic_like = lower_bound if self.opposit_relationship.platonic_like < lower_bound else self.opposit_relationship.platonic_like
            self.opposit_relationship.dislike = upper_bound if self.opposit_relationship.dislike > upper_bound else self.opposit_relationship.dislike
            self.opposit_relationship.dislike = lower_bound if self.opposit_relationship.dislike < lower_bound else self.opposit_relationship.dislike
            self.opposit_relationship.admiration = upper_bound if self.opposit_relationship.admiration > upper_bound else self.opposit_relationship.admiration
            self.opposit_relationship.admiration = lower_bound if self.opposit_relationship.admiration < lower_bound else self.opposit_relationship.admiration
            self.opposit_relationship.comfortable = upper_bound if self.opposit_relationship.comfortable > upper_bound else self.opposit_relationship.comfortable
            self.opposit_relationship.comfortable = lower_bound if self.opposit_relationship.comfortable < lower_bound else self.opposit_relationship.comfortable
            self.opposit_relationship.trust = upper_bound if self.opposit_relationship.trust > upper_bound else self.opposit_relationship.trust
            self.opposit_relationship.trust = lower_bound if self.opposit_relationship.trust < lower_bound else self.opposit_relationship.trust
            self.opposit_relationship.jealousy = upper_bound if self.opposit_relationship.jealousy > upper_bound else self.opposit_relationship.jealousy
            self.opposit_relationship.jealousy = lower_bound if self.opposit_relationship.jealousy < lower_bound else self.opposit_relationship.jealousy