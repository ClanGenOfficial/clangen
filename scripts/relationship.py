from random import choice, randint
from .game_essentials import *
import copy
import ujson

# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['Is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them'],
    "troublesome": ['Made (cat) and (cat) start an argument'],
    "sneaky": ['Is gossiping about (cat) and (cat)'],
    "like": '(cat) confesses to (cat) that they think they like (cat)',
    "trick": 'Has successfully tricked (cat) into believing a crazy tale about the clan leader'
}

EXILED_CATS = {
    "cat_to": ['Bumped into (cat) at the clan border', 'Caught a glimpse of (cat) from the distance'],
    "cat_from": ['Was wandering near the clan territory and met (cat)'],
    "both":['Ran into (cat) by chance']
}

# IN increase or decrease
resource_directory = "scripts/resources/relationship_events/"

NOT_AGE_SPECIFIC = None
try:
    with open(f"{resource_directory}not_age_specific.json", 'r') as read_file:
        NOT_AGE_SPECIFIC = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 1 jsonfile of relationship_events!'

KITTEN_TO_OTHER = None
try:
    with open(f"{resource_directory}kitten_to_other.json", 'r') as read_file:
        KITTEN_TO_OTHER = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 2 jsonfile of relationship_events!'

APPRENTICE_TO_OTHER = None
try:
    with open(f"{resource_directory}apprenice_to_other.json", 'r') as read_file:
        APPRENTICE_TO_OTHER = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 3 jsonfile of relationship_events!'

WARRIOR_TO_OTHER = None
try:
    with open(f"{resource_directory}warrior_to_other.json", 'r') as read_file:
        WARRIOR_TO_OTHER = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 4 jsonfile of relationship_events!'

ELDER_TO_OTHER = None
try:
    with open(f"{resource_directory}elder_to_other.json", 'r') as read_file:
        ELDER_TO_OTHER = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 5 jsonfile of relationship_events!'


LOVE = None
try:
    with open(f"{resource_directory}love.json", 'r') as read_file:
        LOVE = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 6 jsonfile of relationship_events!'


LEADER = None
try:
    with open(f"{resource_directory}leader.json", 'r') as read_file:
        LEADER = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 7 jsonfile of relationship_events!'

DEPUTY = None
try:
    with open(f"{resource_directory}deputy.json", 'r') as read_file:
        DEPUTY = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 8 jsonfile of relationship_events!'

MEDICINE = None
try:
    with open(f"{resource_directory}medicine.json", 'r') as read_file:
        MEDICINE = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 9 jsonfile of relationship_events!'


SPECIAL_CHARACTER = None
try:
    with open(f"{resource_directory}special_character.json", 'r') as read_file:
        SPECIAL_CHARACTER = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 10 jsonfile of relationship_events!'

# How increasing one state influences another directly: (an increase of one state doesn't trigger a chain reaction)
# increase romantic_love -> decreases: dislike | increases: like, comfortable
# increase like -> decreases: dislike | increases: comfortable
# increase dislike -> decreases: romantic_love, like | increases: -
# increase admiration -> decreases: - | increases: -
# increase comfortable -> decreases: jealousy, dislike | increases: trust, like
# increase jealousy -> decreases: - | increases: dislike
# increase trust -> decreases: dislike | increases: -

# !! DECREASING ONE STATE DOES'T INFLUENCE OTHERS !!

# This defines effect the action has, not every action has to have a effect
INCREASE_HIGH = None
try:
    with open(f"{resource_directory}1_INCREASE_HIGH.json", 'r') as read_file:
        INCREASE_HIGH = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 11 jsonfile of relationship_events!'

INCREASE_LOW = None
try:
    with open(f"{resource_directory}1_INCREASE_LOW.json", 'r') as read_file:
        INCREASE_LOW = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 12 jsonfile of relationship_events!'

DECREASE_HIGH  = None
try:
    with open(f"{resource_directory}1_DECREASE_HIGH.json", 'r') as read_file:
        DECREASE_HIGH = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 13 jsonfile of relationship_events!'


DECREASE_LOW = None
try:
    with open(f"{resource_directory}1_DECREASE_LOW.json", 'r') as read_file:
        DECREASE_LOW = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 14 jsonfile of relationship_events!'


# weigths of the stat change
DIRECT_INCREASE_HIGH = 12
DIRECT_DECREASE_HIGH = 9
DIRECT_INCREASE_LOW = 7
DIRECT_DECREASE_LOW = 4
INDIRECT_INCREASE = 6
INDIRECT_DECREASE = 3

class Relationship(object):
    def __init__(self, cat_from, cat_to, mates=False, family=False, romantic_love=0, platonic_like=0, dislike=0, admiration=0, comfortable=0, jealousy=0, trust=0, log = []) -> None:        
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposit_relationship = None #link to oppositting relationship will be created later
        self.current_action_str = ''
        self.triggerd_event = False
        self.log = log

        if self.cat_from.is_parent(self.cat_to) or self.cat_to.is_parent(self.cat_from):
            self.family = True
            if platonic_like == 0:
                platonic_like = 30
                comfortable = 15

        if self.cat_from.is_sibling(self.cat_to):
            self.family = True
            if platonic_like == 0:
                platonic_like = 20
                comfortable = 10

        if self.cat_from.mate != None and self.cat_from.mate == self.cat_to.ID:
            self.mates = True
            if romantic_love == 0:
                romantic_love = 20
                comfortable = 20
                trust = 10

        # each stat can go from 0 to 100
        self.romantic_love = romantic_love
        self.platonic_like = platonic_like
        self.dislike = dislike
        self.admiration = admiration
        self.comfortable = comfortable
        self.jealousy = jealousy
        self.trust = trust

    def link_relationship(self):
        """Add the other relationship object to this easly access and change the other side."""
        opposite_relationship = list(filter(lambda r: r.cat_to.ID == self.cat_from.ID , self.cat_to.relationships))
        if opposite_relationship is not None and len(opposite_relationship) > 0:
            self.opposit_relationship = opposite_relationship[0]
        else:
            # create relationship
            relation = Relationship(self.cat_to,self.cat_from)
            self.cat_to.relationships.append(relation)
            self.opposit_relationship =relation
            
    def start_action(self):
        """This function checks current state of relationship and decides which actions can happen."""
        # update relationship
        if self.cat_from.mate == self.cat_to.ID:
            self.mates = True

        if self.opposit_relationship is None:
            self.link_relationship()

        # quick fix for exiled cat relationships
        if self.cat_to.exiled and not self.cat_from.exiled:
            action = choice(EXILED_CATS['cat_to'])
            string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name)) 
            game.relation_events_list.append(f"{str(self.cat_from.name)} - {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.exiled and not self.cat_to.exiled:
            action = choice(EXILED_CATS['cat_from'])
            string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name)) 
            game.relation_events_list.append(f"{str(self.cat_from.name)} - {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.exiled and self.cat_to.exiled:
            action = choice(EXILED_CATS['both'])
            string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name)) 
            game.relation_events_list.append(f"{str(self.cat_from.name)} - {self.current_action_str} (neutral effect)")
            return

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
        self_relation_effect = self.affect_relationship(action)
        other_relation_effect = self.opposit_relationship.affect_relationship(action, other=True)

        # broadcast action
        string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
        self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))

        actionstring_all = f"{str(self.cat_from.name)} - {self.current_action_str} "
        if self_relation_effect == 'neutral effect':
            self_relation_effect = other_relation_effect
        effect_string =  f"({self_relation_effect})"
        both = actionstring_all+effect_string
        self.log.append(both)
        if len(both) < 100:
            game.relation_events_list.append(both)
        else:
            game.relation_events_list.append(actionstring_all)
            game.relation_events_list.append(effect_string)

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
        if self.dislike > 20 or self.jealousy > 20:
            action_possibilies += NOT_AGE_SPECIFIC['unfriendly']
            relation_keys.append('unfriendly')
            # increase the chance for unfriendly behaviour
            if self.dislike > 30:
                relation_keys.append('unfriendly')
        if self.platonic_like > 40 or self.comfortable > 30:
            action_possibilies += NOT_AGE_SPECIFIC['friendly']
            relation_keys.append('friendly')
        if self.platonic_like > 50 and self.comfortable > 40 and self.trust > 30:
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
        if self.cat_from.age != 'kitten' and self.cat_to.age != 'kitten':
            if self.cat_from.status == 'leader':
                for relation_key in relation_keys:
                    action_possibilies += LEADER['from'][relation_key]
            if self.cat_to.status == 'leader':
                for relation_key in relation_keys:
                    action_possibilies += LEADER['to'][relation_key]

            if self.cat_from.status == 'deputy':
                for relation_key in relation_keys:
                    action_possibilies += DEPUTY['from'][relation_key]
            if self.cat_to.status == 'deputy':
                for relation_key in relation_keys:
                    action_possibilies += DEPUTY['to'][relation_key]

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
        if not self.cat_from.is_potential_mate(self.cat_to, for_love_interest = True):
            return action_possibilies

        # chance to fall in love with some the character is not close to:
        love_p = randint(0,30)
        if self.platonic_like > 30 or love_p == 1 or self.romantic_love > 5:
            # increase the chance of an love event for two unmated cats
            action_possibilies = action_possibilies + LOVE['love_interest_only']
            if self.cat_from.mate == None and self.cat_to.mate == None:
                action_possibilies = action_possibilies + LOVE['love_interest_only']

        if self.opposit_relationship.romantic_love > 20:
            action_possibilies = action_possibilies + LOVE['love_interest_only']

        if self.romantic_love > 25 and self.opposit_relationship.romantic_love > 15:
            action_possibilies = action_possibilies + LOVE['love_interest']

        if self.mates and self.romantic_love > 30 and self.opposit_relationship.romantic_love > 25 :
            action_possibilies = action_possibilies + LOVE['mates']

        return action_possibilies

    def affect_relationship(self, action, other = False):
        """Affect the relationship according to the action."""
        key = 'from'
        if other:
            key = 'to'

        # for easier value change
        number_increase = DIRECT_INCREASE_HIGH
        number_decrease = DIRECT_DECREASE_HIGH
        effect = 'neutral effect'

        # increases
        if action in INCREASE_HIGH[key]['romantic_love']:
            self.romantic_love += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['like']:
            self.platonic_like += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['dislike']:
            self.dislike += number_increase
            effect = 'negative effect'
            # indirekt influences
            self.platonic_like -= INDIRECT_DECREASE
            self.romantic_love -= INDIRECT_DECREASE
            # if dislike reaced a certain point, and is increased, like will get decrease more
            if self.dislike > 24:
                self.platonic_like -= INDIRECT_DECREASE
                self.romantic_love -= INDIRECT_DECREASE
                self.comfortable -= INDIRECT_DECREASE
                self.trust -= INDIRECT_DECREASE
        if action in INCREASE_HIGH[key]['admiration']:
            self.admiration += number_increase
            effect = 'positive effect'
        if action in INCREASE_HIGH[key]['comfortable']:
            self.comfortable += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.jealousy -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.trust += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['jealousy']:
            self.jealousy += number_increase
            effect = 'negative effect'
        if action in INCREASE_HIGH[key]['trust']:
            self.trust += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE

        number_increase = DIRECT_INCREASE_LOW
        if action in INCREASE_LOW[key]['romantic_love']:
            self.romantic_love += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['like']:
            self.platonic_like += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['dislike']:
            self.dislike += number_increase
            if effect == 'neutral effect':
                effect = 'small negative effect'
            # if dislike reaced a certain point, and is increased, like will get decrease more
            if self.dislike > 24:
                self.platonic_like -= INDIRECT_DECREASE
                self.romantic_love -= INDIRECT_DECREASE
                self.comfortable -= INDIRECT_DECREASE
                self.trust -= INDIRECT_DECREASE
        if action in INCREASE_LOW[key]['admiration']:
            self.admiration += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['comfortable']:
            self.comfortable += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['jealousy']:
            self.jealousy += number_increase
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in INCREASE_LOW[key]['trust']:
            self.trust += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'

        # decreases
        if action in DECREASE_HIGH[key]['romantic_love']:
            self.romantic_love -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['like']:
            self.platonic_like -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['dislike']:
            self.dislike -= number_decrease
            effect = 'positive effect'
        if action in DECREASE_HIGH[key]['admiration']:
            self.admiration -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['comfortable']:
            self.comfortable -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['trust']:
            self.trust -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['jealousy']:
            self.jealousy -= number_decrease
            effect = 'positive effect'

        number_decrease = DIRECT_DECREASE_LOW
        if action in DECREASE_LOW[key]['romantic_love']:
            self.romantic_love -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['like']:
            self.platonic_like -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['dislike']:
            self.dislike -= number_decrease
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in DECREASE_LOW[key]['admiration']:
            self.admiration -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['comfortable']:
            self.comfortable -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['jealousy']:
            self.jealousy -= number_decrease
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in DECREASE_LOW[key]['trust']:
            self.trust -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'

        self.cut_boundries()
        return effect

    def cut_boundries(self):
        """Cut the stats of involved relationships."""
        upper_bound = 100
        lower_bound = 0

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

    def special_interactions(self):
        actions_possibilities = []

        # more in dept relationship actions

        return actions_possibilities