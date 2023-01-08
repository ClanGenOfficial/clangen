import random
from random import choice, randint
import copy
try:
    import ujson
except ImportError:
    import json as ujson
from scripts.event_class import Single_Event

from scripts.utility import get_personality_compatibility
from scripts.game_structure.game_essentials import *

# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them.'],
    "troublesome": ['made (cat) and (cat) start an argument.'],
    "sneaky": ['is gossiping about (cat) and (cat).'],
    "like": '(cat) confesses to (cat) that they think they like (cat).',
    "trick": 'has successfully tricked (cat) into believing a crazy tale about the Clan leader.'
}

EXILED_CATS = {
    "cat_to": ['bumped into (cat) at the Clan border', 'caught a glimpse of (cat) from the distance.'],
    "cat_from": ['was wandering near the Clan territory and met (cat).'],
    "both": ['ran into (cat) by chance.']
}

OUTSIDE_CATS = {
    "cat_to": ['is thinking about (cat)'],
    "cat_from": ['is thinking about (cat) as they wander far from Clan territory.'],
    "both": ['wonders where (cat) is right now. ']
}

# weights of the stat change
DIRECT_INCREASE_HIGH = 12
DIRECT_DECREASE_HIGH = 9
DIRECT_INCREASE_LOW = 7
DIRECT_DECREASE_LOW = 4
INDIRECT_INCREASE = 6
INDIRECT_DECREASE = 3

# add/decrease weight of personality based compatibility
COMPATIBILITY_WEIGHT = 3


# ---------------------------------------------------------------------------- #
#                           START Relationship class                           #
# ---------------------------------------------------------------------------- #

class Relationship():
    def __init__(self, cat_from, cat_to, mates=False, family=False, romantic_love=0, platonic_like=0, dislike=0,
                 admiration=0, comfortable=0, jealousy=0, trust=0, log=None) -> None:
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposite_relationship = None  # link to opposite relationship will be created later
        self.current_action_str = ''
        self.triggered_event = False
        if log:
            self.log = log
        else:
            self.log = []

        y = random.randrange(0, 31)

        if self.cat_from.is_parent(self.cat_to) or self.cat_to.is_parent(self.cat_from):
            self.family = True
            if platonic_like == 0:
                platonic_like = 30 + y
                comfortable = 10 + y
                admiration = 15 + y
                trust = 10 + y

        if self.cat_from.is_sibling(self.cat_to):
            self.family = True
            if platonic_like == 0:
                platonic_like = 20 + y
                comfortable = 10 + y
                trust = 0 + y

        if self.cat_from.mate is not None and self.cat_from.mate == self.cat_to.ID:
            self.mates = True
            if romantic_love == 0:
                romantic_love = 20 + y
                comfortable = 20 + y
                trust = 10 + y

        # each stat can go from 0 to 100
        self.romantic_love = romantic_love
        self.platonic_like = platonic_like
        self.dislike = dislike
        self.admiration = admiration
        self.comfortable = comfortable
        self.jealousy = jealousy
        self.trust = trust

    def link_relationship(self):
        """Add the other relationship object to this easily access and change the other side."""
        if self.cat_from.ID in self.cat_to.relationships:
            self.opposite_relationship = self.cat_to.relationships[self.cat_from.ID]
        else:
            # create relationship
            relation = Relationship(self.cat_to, self.cat_from)
            self.cat_to.relationships[self.cat_from.ID] = relation
            self.opposite_relationship = relation

    def start_action(self):
        """This function checks current state of relationship and decides which actions can happen."""
        # update relationship
        if self.cat_from.mate == self.cat_to.ID:
            self.mates = True

        if self.opposite_relationship is None:
            self.link_relationship()

        # quick fix for exiled cat relationships
        if self.cat_to.exiled and not self.cat_from.exiled:
            action = choice(EXILED_CATS['cat_to'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)", "relation",
                [self.cat_to.ID, self.cat_from.ID]))
            # game.relation_events_list.append(f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.exiled and not self.cat_to.exiled:
            action = choice(EXILED_CATS['cat_from'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)", "relation",
                [self.cat_to.ID, self.cat_from.ID]))
            # game.relation_events_list.append(f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.exiled and self.cat_to.exiled:
            action = choice(EXILED_CATS['both'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)", "relation",
                [self.cat_to.ID, self.cat_from.ID]))
            # game.relation_events_list.append(f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)")
            return

        # quick fix for outside cat relationships
        if self.cat_to.outside and not self.cat_from.outside:
            action = choice(OUTSIDE_CATS['cat_to'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            # game.relation_events_list.append(
            #     f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.outside and not self.cat_to.outside:
            action = choice(OUTSIDE_CATS['cat_from'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            # game.relation_events_list.append(
            #    f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.outside and self.cat_to.outside:
            action = choice(OUTSIDE_CATS['both'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            # game.relation_events_list.append(
            #    f"{str(self.cat_from.name)} {self.current_action_str} (neutral effect)")
            return

        # get action possibilities
        action_possibilities = self.get_action_possibilities()

        # check if the action is relevant (action of characters include age in the replacement string)
        action_relevant = False
        action = None
        while not action_relevant:
            action = choice(action_possibilities)
            relevant_ages = action[action.find("(") + 1:action.find(")")]
            relevant_ages = relevant_ages.split(',')
            relevant_ages = [age.strip() for age in relevant_ages]

            if len(relevant_ages) == 1 and relevant_ages[0] == 'cat':
                action_relevant = True
            if self.cat_to.age in relevant_ages:
                action_relevant = True

        # change the stats of the relationships
        self_relation_effect = self.affect_relationship(action)
        other_relation_effect = self.opposite_relationship.affect_relationship(action, other=True)

        # replace (cat) with actual name
        start_point = action.find("(") + 1
        end_point = action.find(")")
        string_to_replace = f"({action[start_point:end_point]})"
        self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))

        # add the effect of the current action
        action_string_all = f"{str(self.cat_from.name)} {self.current_action_str} "
        if self_relation_effect == 'neutral effect':
            self_relation_effect = other_relation_effect
        effect_string = f"({self_relation_effect})"

        # connect all information and broadcast
        both = action_string_all + effect_string
        self.log.append(both)
        game.cur_events_list.append(Single_Event(both, ["relation", "interaction"], [self.cat_to.ID, self.cat_from.ID]))
        # game.relation_events_list.append(both)

    def get_action_possibilities(self):
        """Creates a list of possibles actions of this relationship"""
        # check if opposite_relationship is here, otherwise creates it       
        action_possibilities = copy.deepcopy(GENERAL['neutral'])

        key = self.cat_to.status
        if key == "senior warrior":
            key = "warrior"

        # NORMAL INTERACTIONS
        # check how the relationship is
        relation_keys = ['neutral']
        if self.dislike > 20 or self.jealousy > 20:
            action_possibilities += GENERAL['unfriendly']
            relation_keys.append('unfriendly')
            # increase the chance for unfriendly behavior
            if self.dislike > 30:
                relation_keys.append('unfriendly')
        if self.platonic_like > 40 or self.comfortable > 30:
            action_possibilities += GENERAL['friendly']
            relation_keys.append('friendly')
        if self.platonic_like > 50 and self.comfortable > 40 and self.trust > 30:
            action_possibilities += GENERAL['close']
            relation_keys.append('close')

        # add the interactions to the possible ones
        if self.cat_from.status == "kitten":
            for relation_key in relation_keys:
                action_possibilities += KITTEN_TO_OTHER[key][relation_key]
        if self.cat_from.status == "apprentice":
            for relation_key in relation_keys:
                action_possibilities += APPRENTICE_TO_OTHER[key][relation_key]
        if self.cat_from.status == "medicine cat apprentice":
            for relation_key in relation_keys:
                action_possibilities += MEDICINE_APP_TO_OTHER[key][relation_key]
        if self.cat_from.status == "warrior" or self.cat_from.status == "senior warrior":
            for relation_key in relation_keys:
                action_possibilities += WARRIOR_TO_OTHER[key][relation_key]
        if self.cat_from.status == "medicine cat":
            for relation_key in relation_keys:
                action_possibilities += MEDICINE_TO_OTHER[key][relation_key]
        if self.cat_from.status == "deputy":
            for relation_key in relation_keys:
                action_possibilities += DEPUTY_TO_OTHER[key][relation_key]
        if self.cat_from.status == "leader":
            for relation_key in relation_keys:
                action_possibilities += LEADER_TO_OTHER[key][relation_key]
        if self.cat_from.status == "elder":
            for relation_key in relation_keys:
                action_possibilities += ELDER_TO_OTHER[key][relation_key]

        # CHARACTERISTIC INTERACTION
        character_keys = SPECIAL_CHARACTER.keys()
        if self.cat_from.trait in character_keys:
            action_possibilities += SPECIAL_CHARACTER[self.cat_from.trait]

        # LOVE
        if not self.cat_from.is_potential_mate(self.cat_to, for_love_interest=True) or \
                not self.cat_to.is_potential_mate(self.cat_from, for_love_interest=True):
            return action_possibilities

        # chance to fall in love with some the character is not close to:
        love_p = randint(0, 20)
        if self.platonic_like > 30 or love_p == 1 or self.romantic_love > 5:
            # increase the chance of an love event for two un-mated cats
            action_possibilities = action_possibilities + LOVE['love_interest_only']
            if self.cat_from.mate is None and self.cat_to.mate is None:
                action_possibilities = action_possibilities + LOVE['love_interest_only']

        if self.opposite_relationship.romantic_love > 20:
            action_possibilities = action_possibilities + LOVE['love_interest_only']

        if self.romantic_love > 25 and self.opposite_relationship.romantic_love > 15:
            action_possibilities = action_possibilities + LOVE['love_interest']

        if self.mates and self.romantic_love > 30 and self.opposite_relationship.romantic_love > 25:
            action_possibilities = action_possibilities + LOVE['mates']

        return action_possibilities

    def affect_relationship(self, action, other=False):
        """Affect the relationship according to the action."""
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
        key = 'from'
        if other:
            key = 'to'

        # for easier value change
        number_increase = self.get_high_increase_value()
        number_decrease = self.get_high_decrease_value()
        effect = 'neutral effect'

        # increases
        if action in INCREASE_HIGH[key]['romantic_love']:
            self.romantic_love += number_increase
            effect = 'positive effect'
            # indirect influences
            self.dislike -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['like']:
            self.platonic_like += number_increase
            effect = 'positive effect'
            # indirect influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['dislike']:
            self.dislike += number_increase
            effect = 'negative effect'
            # indirect influences
            self.platonic_like -= INDIRECT_DECREASE
            self.romantic_love -= INDIRECT_DECREASE
            # if dislike reached a certain point, and is increased, like will get decrease more
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
            # indirect influences
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
            # indirect influences
            self.dislike -= INDIRECT_DECREASE

        number_increase = self.get_low_increase_value()
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
            # if dislike reached a certain point, and is increased, like will get decrease more
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

        number_decrease = self.get_low_decrease_value()
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

        return effect

    def get_high_increase_value(self):
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            return DIRECT_INCREASE_HIGH
        if compatibility:
            return DIRECT_INCREASE_HIGH + COMPATIBILITY_WEIGHT
        else:
            return DIRECT_INCREASE_HIGH - COMPATIBILITY_WEIGHT

    def get_high_decrease_value(self):
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            return DIRECT_DECREASE_HIGH
        if compatibility:
            return DIRECT_DECREASE_HIGH + COMPATIBILITY_WEIGHT
        else:
            return DIRECT_DECREASE_HIGH - COMPATIBILITY_WEIGHT

    def get_low_increase_value(self):
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            return DIRECT_INCREASE_LOW
        if compatibility:
            return DIRECT_INCREASE_LOW + COMPATIBILITY_WEIGHT
        else:
            return DIRECT_INCREASE_LOW - COMPATIBILITY_WEIGHT

    def get_low_decrease_value(self):
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            return DIRECT_DECREASE_LOW
        if compatibility:
            return DIRECT_DECREASE_LOW + COMPATIBILITY_WEIGHT
        else:
            return DIRECT_DECREASE_LOW - COMPATIBILITY_WEIGHT

    # ---------------------------------------------------------------------------- #
    #                                   property                                   #
    # ---------------------------------------------------------------------------- #

    @property
    def romantic_love(self):
        return self._romantic_love

    @romantic_love.setter
    def romantic_love(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._romantic_love = value

    @property
    def platonic_like(self):
        return self._platonic_like

    @platonic_like.setter
    def platonic_like(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._platonic_like = value

    @property
    def dislike(self):
        return self._dislike

    @dislike.setter
    def dislike(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._dislike = value

    @property
    def admiration(self):
        return self._admiration

    @admiration.setter
    def admiration(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._admiration = value

    @property
    def comfortable(self):
        return self._comfortable

    @comfortable.setter
    def comfortable(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._comfortable = value

    @property
    def jealousy(self):
        return self._jealousy

    @jealousy.setter
    def jealousy(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._jealousy = value

    @property
    def trust(self):
        return self._trust

    @trust.setter
    def trust(self, value):
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self._trust = value


# IN increase or decrease
resource_directory = "resources/dicts/relationship_events/"
de_in_crease_path = "DE_IN_CREASE/"
cat_to_other_path = "cat_to_other/"

# ---------------------------------------------------------------------------- #
#                           load event possibilities                           #
# ---------------------------------------------------------------------------- #


GENERAL = None
with open(f"{resource_directory}{cat_to_other_path}not_age_specific.json", 'r') as read_file:
    GENERAL = ujson.loads(read_file.read())

KITTEN_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}kitten_to_other.json", 'r') as read_file:
    KITTEN_TO_OTHER = ujson.loads(read_file.read())

APPRENTICE_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}apprentice_to_other.json", 'r') as read_file:
    APPRENTICE_TO_OTHER = ujson.loads(read_file.read())

MEDICINE_APP_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}medicine_app_to_other.json", 'r') as read_file:
    MEDICINE_APP_TO_OTHER = ujson.loads(read_file.read())

WARRIOR_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}warrior_to_other.json", 'r') as read_file:
    WARRIOR_TO_OTHER = ujson.loads(read_file.read())

ELDER_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}elder_to_other.json", 'r') as read_file:
    ELDER_TO_OTHER = ujson.loads(read_file.read())

LEADER_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}leader_to_other.json", 'r') as read_file:
    LEADER_TO_OTHER = ujson.loads(read_file.read())

DEPUTY_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}deputy_to_other.json", 'r') as read_file:
    DEPUTY_TO_OTHER = ujson.loads(read_file.read())

MEDICINE_TO_OTHER = None
with open(f"{resource_directory}{cat_to_other_path}medicine_to_other.json", 'r') as read_file:
    MEDICINE_TO_OTHER = ujson.loads(read_file.read())

LOVE = None
with open(f"{resource_directory}love.json", 'r') as read_file:
    LOVE = ujson.loads(read_file.read())

SPECIAL_CHARACTER = None
with open(f"{resource_directory}special_character.json", 'r') as read_file:
    SPECIAL_CHARACTER = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                             load de- and increase                            #
# ---------------------------------------------------------------------------- #


INCREASE_HIGH = None
try:
    with open(f"{resource_directory}{de_in_crease_path}INCREASE_HIGH.json", 'r') as read_file:
        INCREASE_HIGH = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 1_INCREASE_HIGH.json file of relationship_events!'

INCREASE_LOW = None
try:
    with open(f"{resource_directory}{de_in_crease_path}INCREASE_LOW.json", 'r') as read_file:
        INCREASE_LOW = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 1_INCREASE_LOW.json file of relationship_events!'

DECREASE_HIGH = None
try:
    with open(f"{resource_directory}{de_in_crease_path}DECREASE_HIGH.json", 'r') as read_file:
        DECREASE_HIGH = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 1_DECREASE_HIGH.json file of relationship_events!'

DECREASE_LOW = None
try:
    with open(f"{resource_directory}{de_in_crease_path}DECREASE_LOW.json", 'r') as read_file:
        DECREASE_LOW = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the 1_DECREASE_LOW.json file of relationship_events!'
