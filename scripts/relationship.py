from random import choice, randint
from .game_essentials import *

to_sort = ['Is sharing tongues with (cat)']

# NOT FINISHED

# if the relationship triggers an event
EVENT = {
    "breakup": '(cat) is no longer mates with (cat)'
}

# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['Is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them'],
    "troublesom": ['Made (cat) and (cat) start an argument'],
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
    "childish": ['(cat) chases around a butterfly', 'Is hiding behind a bush ready to pounce on (cat)'],
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
                'Is sharing prey with (cat)'],
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
        "like": ['Is telling a story to (cat)','Is talking with (cat)','Is sharing tongue with (cat)',
                'Tells (cat) a secret','Is giving (cat) a badger ride on their back!',
                'Hopes that their own kits are as cute as (cat) someday', 'Is telling (cat) about a hunting technique',
                'Is sharing tongues with (cat)','Has been spending time with (cat) lately','Just told (cat) a hilarious joke',
                'Plays mossball with (cat)','Pretends to be a warrior with (cat)','Comes up with a plan to sneak out of camp with (cat)'],
        "dislike": ['Is mocking (cat)', 'Ignores (cat)', 'Sticks their tongue out at (cat)'],
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
                'Tells (cat) a secret','Is giving (cat) a badger ride on their back!',
                'Is promising to take (cat) outside of camp if they behave', 'Gave (cat) a trinket they found while out on patrol today',
                'Is telling (cat) about a hunting technique','Is sharing tongues with (cat)','Has been spending time with (cat) lately',
                'Just told (cat) a hilarious joke', 'Plays mossball with (cat)','Pretends to be a warrior with (cat)',
                'Comes up with a plan to sneak out of camp with (cat)'],
        "dislike": ['Is mocking (cat)','Is telling jokes about (cat)','Sticks their tongue out at (cat)',
                    'Is spreading a rumour about (cat)','Tries to scare (cat)'],
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
        "trust": ['Is spreading a rumour about (cat)','Trips over (cat)']
    }
}

# weigths of the stat change
DIRECT_INCREASE = 10
DIRECT_DECREASE = 3
INDIRECT_INCREASE = 6
INDIRECT_DECREASE = 2

class Relationship(object):
    def __init__(self, cat_from, cat_to, mates=False, family=False, romantic_love=0, like=0, dislike=0, admiration=0, comfortable=0, jealousy=0, trust=0) -> None:
        # involved cat
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposit_relationship = None #link to oppositting relationship will be created later

        if mates and romantic_love == 0:
            romantic_love = 50
            comfortable = 40
        
        if family and like == 0:
            like = 30
            comfortable = 10

        # each stat can go from 0 to 100
        # some states don't have a influence right now (WIP)
        self.romantic_love = romantic_love
        self.like = like
        self.dislike = dislike
        self.admiration = admiration
        self.comfortable = comfortable
        self.jealousy = jealousy
        self.trust = trust

        self.current_changes = []

    def link_relationship(self):
        """Add the other relationship object to this easly access and change the other side."""
        self.opposit_relationship = list(filter(lambda r: r.cat_to.ID == self.cat_from.ID , self.cat_to.relationships))[0]

    def start_action(self):
        """This function checks current state of relationship and decides which actions can happen."""
        # check if opposit_relationship is here, otherwise creates it
        if self.opposit_relationship is None:
            self.link_relationship()
        
        action_possibilies = NOT_AGE_SPECIFIC['neutral']

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
        if self.like > 40 or self.comfortable > 30:
            action_possibilies += NOT_AGE_SPECIFIC['friendly']
            relation_keys.append('friendly')
        if self.like > 60 and self.comfortable > 50 and self.trust > 50:
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

        # chance to fall in love with some the character is not close to:
        love_p = randint(0,50)
        if not self.family:
            if self.like > 50 or love_p == 1 or self.romantic_love > 5:
                action_possibilies = action_possibilies + LOVE['love_interest_only']
            if self.romantic_love > 25 and self.opposit_relationship.romantic_love > 15:
                action_possibilies = action_possibilies + LOVE['love_interest']
            if self.mates:
                action_possibilies = action_possibilies + LOVE['mates']

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



        action = choice(action_possibilies)

        # change the stats of the relationships
        self.affect_own_relationship(action)
        self.affect_other_relationship(action)

        # broadcast action
        action_string = action.replace('(cat)', str(self.cat_to.name))
        rel_stat_info = '('
        rel_stat_info += ','.join(self.current_changes) + ')'

        game.relation_events_list.append(str(self.cat_from.name) + " - " + action_string)
        
        if len(self.current_changes) > 1:
            game.relation_events_list.append(rel_stat_info)

    def affect_own_relationship(self, action):
        """Affect the own relationship according to the action."""
        # for easier value change
        number_increase = DIRECT_INCREASE
        number_decrease = DIRECT_DECREASE

        # increases
        if action in INCREASE['from']['romantic_love']:
            self.romantic_love += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' rom. love [' + str(self.cat_from.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['from']['like']:
            self.like += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' like [' + str(self.cat_from.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['from']['dislike']:
            self.dislike += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' d.like [' + str(self.cat_from.name) + ']')
            # indirekt influences
            self.like -= INDIRECT_DECREASE
            self.romantic_love -= INDIRECT_DECREASE
        if action in INCREASE['from']['admiration']:
            self.admiration += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' admir. [' + str(self.cat_from.name) + ']')
        if action in INCREASE['from']['comfortable']:
            self.comfortable += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' comf. [' + str(self.cat_from.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.jealousy -= INDIRECT_DECREASE
            self.like += INDIRECT_INCREASE
            self.trust += INDIRECT_INCREASE
        if action in INCREASE['from']['jealousy']:
            self.jealousy += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' jeal. [' + str(self.cat_from.name) + ']')
        if action in INCREASE['from']['trust']:
            self.trust += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' trust [' + str(self.cat_from.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE


        # decreases
        if action in DECREASE['from']['romantic_love']:
            self.romantic_love -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' rom. love [' + str(self.cat_from.name) + ']')
        if action in DECREASE['from']['like']:
            self.like -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' like [' + str(self.cat_from.name) + ']')
        if action in DECREASE['from']['dislike']:
            self.dislike -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' d.like [' + str(self.cat_from.name) + ']')
        if action in DECREASE['from']['admiration']:
            self.admiration -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' admir. [' + str(self.cat_from.name) + ']')
        if action in DECREASE['from']['comfortable']:
            self.comfortable -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' comf. [' + str(self.cat_from.name) + ']')
        if action in DECREASE['from']['trust']:
            self.trust -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' trust [' + str(self.cat_from.name) + ']')
        if action in DECREASE['from']['jealousy']:
            self.jealousy -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' jeal. [' + str(self.cat_from.name) + ']')


        # cut on boundries
        self.romantic_love = 100 if self.romantic_love > 100 else self.romantic_love
        self.romantic_love = 0 if self.romantic_love < 0 else self.romantic_love
        self.like = 100 if self.like > 100 else self.like
        self.like = 0 if self.like < 0 else self.like
        self.dislike = 100 if self.dislike > 100 else self.dislike
        self.dislike = 0 if self.dislike < 0 else self.dislike
        self.admiration = 100 if self.admiration > 100 else self.admiration
        self.admiration = 0 if self.admiration < 0 else self.admiration
        self.comfortable = 100 if self.comfortable > 100 else self.comfortable
        self.comfortable = 0 if self.comfortable < 0 else self.comfortable
        self.trust = 100 if self.trust > 100 else self.trust
        self.trust = 0 if self.trust < 0 else self.trust
        self.jealousy = 100 if self.jealousy > 100 else self.jealousy
        self.jealousy = 0 if self.jealousy < 0 else self.jealousy

    def affect_other_relationship(self, action):
        """Affect the other relationship according to the action."""
        # for easier value change
        number_increase = DIRECT_INCREASE
        number_decrease = DIRECT_DECREASE

        # increases
        if action in INCREASE['to']['romantic_love']:
            self.opposit_relationship.romantic_love += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' rom. love [' + str(self.cat_to.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['to']['like']:
            self.opposit_relationship.like += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' like [' + str(self.cat_to.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE['to']['dislike']:
            self.opposit_relationship.dislike += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' d.like [' + str(self.cat_to.name) + ']')
            # indirekt influences
            self.like -= INDIRECT_DECREASE
            self.romantic_love -= INDIRECT_DECREASE
        if action in INCREASE['to']['admiration']:
            self.opposit_relationship.admiration += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' admir. [' + str(self.cat_to.name) + ']')
        if action in INCREASE['to']['comfortable']:
            self.opposit_relationship.comfortable += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' comf. [' + str(self.cat_to.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.jealousy -= INDIRECT_DECREASE
            self.like += INDIRECT_INCREASE
            self.trust += INDIRECT_INCREASE
        if action in INCREASE['to']['jealousy']:
            self.opposit_relationship.jealousy -= number_decrease
            self.current_changes.append('+ ' + str(number_increase) + ' jeal. [' + str(self.cat_to.name) + ']')
        if action in INCREASE['to']['trust']:
            self.opposit_relationship.trust += number_increase
            self.current_changes.append('+ ' + str(number_increase) + ' trust [' + str(self.cat_to.name) + ']')
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE


        # decreases
        if action in DECREASE['to']['romantic_love']:
            self.opposit_relationship.romantic_love -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' rom. love [' + str(self.cat_to.name) + ']')
        if action in DECREASE['to']['like']:
            self.opposit_relationship.like -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' like [' + str(self.cat_to.name) + ']')
        if action in DECREASE['to']['dislike']:
            self.opposit_relationship.dislike -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' d.like [' + str(self.cat_to.name) + ']')
        if action in DECREASE['to']['admiration']:
            self.opposit_relationship.admiration -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' admir. [' + str(self.cat_to.name) + ']')
        if action in DECREASE['to']['comfortable']:
            self.opposit_relationship.comfortable -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' comf. [' + str(self.cat_to.name) + ']')
        if action in DECREASE['to']['trust']:
            self.opposit_relationship.trust -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' trust [' + str(self.cat_to.name) + ']')
        if action in DECREASE['to']['jealousy']:
            self.opposit_relationship.jealousy -= number_decrease
            self.current_changes.append('- ' + str(number_decrease) + ' jeal. [' + str(self.cat_to.name) + ']')


        # cut on boundries
        self.opposit_relationship.romantic_love = 100 if self.opposit_relationship.romantic_love > 100 else self.opposit_relationship.romantic_love
        self.opposit_relationship.romantic_love = 0 if self.opposit_relationship.romantic_love < 0 else self.opposit_relationship.romantic_love
        self.opposit_relationship.like = 100 if self.opposit_relationship.like > 100 else self.opposit_relationship.like
        self.opposit_relationship.like = 0 if self.opposit_relationship.like < 0 else self.opposit_relationship.like
        self.opposit_relationship.dislike = 100 if self.opposit_relationship.dislike > 100 else self.opposit_relationship.dislike
        self.opposit_relationship.dislike = 0 if self.opposit_relationship.dislike < 0 else self.opposit_relationship.dislike
        self.opposit_relationship.admiration = 100 if self.opposit_relationship.admiration > 100 else self.opposit_relationship.admiration
        self.opposit_relationship.admiration = 0 if self.opposit_relationship.admiration < 0 else self.opposit_relationship.admiration
        self.opposit_relationship.comfortable = 100 if self.opposit_relationship.comfortable > 100 else self.opposit_relationship.comfortable
        self.opposit_relationship.comfortable = 0 if self.opposit_relationship.comfortable < 0 else self.opposit_relationship.comfortable
        self.opposit_relationship.trust = 100 if self.opposit_relationship.trust > 100 else self.opposit_relationship.trust
        self.opposit_relationship.trust = 0 if self.opposit_relationship.trust < 0 else self.opposit_relationship.trust
        self.opposit_relationship.jealousy = 100 if self.opposit_relationship.jealousy > 100 else self.opposit_relationship.jealousy
        self.opposit_relationship.jealousy = 0 if self.opposit_relationship.jealousy < 0 else self.opposit_relationship.jealousy
