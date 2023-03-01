import os
import random
from random import choice, randint
import copy
try:
    import ujson
except ImportError:
    import json as ujson
from scripts.event_class import Single_Event

from scripts.utility import get_personality_compatibility
from scripts.game_structure.game_essentials import game

# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them.'],
    "troublesome": ['made (cat) and (cat) start an argument.'],
    "sneaky": ['is gossiping about (cat) and (cat).'],
    "like": '(cat) confesses to (cat) that they think they like (cat).',
    "trick": 'has successfully tricked (cat) into believing a crazy tale about the Clan leader.'
}

EXILED_CATS = {
    "cat_to": ['bumped into (cat) at the Clan border.', 'caught a glimpse of (cat) from the distance.'],
    "cat_from": ['was wandering near the Clan territory and met (cat).'],
    "both": ['ran into (cat) by chance.']
}

OUTSIDE_CATS = {
    "cat_to": ['is thinking about (cat).'],
    "cat_from": ['is thinking about (cat) as they wander far from Clan territory.'],
    "both": ['wonders where (cat) is right now.']
}

# weights of the stat change
DIRECT_INCREASE_HIGH = 13
DIRECT_DECREASE_HIGH = 10
DIRECT_INCREASE_LOW = 8
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
        self.interaction_str = ''
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

        # check if opposite_relationship is here, otherwise creates it
        if self.opposite_relationship is None:
            self.link_relationship()

        # quick fix for exiled cat relationships
        if self.cat_to.exiled and not self.cat_from.exiled:
            action = choice(EXILED_CATS['cat_to'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{self.cat_from.name} {self.interaction_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            return
        elif self.cat_from.exiled and not self.cat_to.exiled:
            action = choice(EXILED_CATS['cat_from'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{self.cat_from.name} {self.interaction_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            return
        elif self.cat_from.exiled and self.cat_to.exiled:
            action = choice(EXILED_CATS['both'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{self.cat_from.name} {self.interaction_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            return

        # quick fix for outside cat relationships
        if self.cat_to.outside and not self.cat_from.outside:
            action = choice(OUTSIDE_CATS['cat_to'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{self.cat_from.name} {self.interaction_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            return
        elif self.cat_from.outside and not self.cat_to.outside:
            action = choice(OUTSIDE_CATS['cat_from'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{self.cat_from.name} {self.interaction_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
            return
        elif self.cat_from.outside and self.cat_to.outside:
            action = choice(OUTSIDE_CATS['both'])
            string_to_replace = '(' + action[action.find("(") + 1:action.find(")")] + ')'
            self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))
            game.cur_events_list.append(Single_Event(
                f"{self.cat_from.name} {self.interaction_str} (neutral effect)", ["relation", "interaction"],
                [self.cat_to.ID, self.cat_from.ID]))
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
        self_relation_effect = self.affect_relationships(action)
        other_relation_effect = self.opposite_relationship.affect_relationships(action, other=True)

        # replace (cat) with actual name
        start_point = action.find("(") + 1
        end_point = action.find(")")
        string_to_replace = f"({action[start_point:end_point]})"
        self.interaction_str = action.replace(string_to_replace, str(self.cat_to.name))

        # replace m_c with cat name
        self.interaction_str = self.interaction_str.replace("m_c", str(self.cat_from.name))

        # add the effect of the current action
        action_string_all = f"{self.cat_from.name} {self.interaction_str} "
        if self_relation_effect == 'neutral effect':
            self_relation_effect = other_relation_effect
        effect_string = f"({self_relation_effect})"

        # connect all information and broadcast
        both = action_string_all + effect_string
        self.log.append(both)
        game.cur_events_list.append(Single_Event(both, ["relation", "interaction"], [self.cat_to.ID, self.cat_from.ID]))

    def get_action_possibilities(self):
        """Base on the current relationship, different actions are """

        if not self.cat_from.is_potential_mate(self.cat_to, for_love_interest=True) or \
                not self.cat_to.is_potential_mate(self.cat_from, for_love_interest=True):
            return self.get_non_romantic_action_possibilities()

        love_chance = 20

        if self.mates and self.romantic_love > 30 and self.opposite_relationship.romantic_love > 25:
            love_chance -= 18
        elif self.romantic_love > 25:
            love_chance -= 8
        elif self.romantic_love > 15:
            love_chance -= 6
        elif self.romantic_love > 10:
            love_chance -= 5
        elif self.platonic_like > 30 or self.romantic_love > 5:
            love_chance -= 3

        if self.cat_from.mate is None and self.cat_to.mate is None:
            love_chance -= 10

        # decide which action (romantic or not) are done
        no_hit = randint(0, love_chance)
        if no_hit or self.dislike > 15:
            return self.get_non_romantic_action_possibilities()
        else:
            return self.get_romantic_action_possibilities()

    def get_non_romantic_action_possibilities(self):
        """Returns a list of action possibilities for increase other relation values, not romantic."""
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
        if self.platonic_like > 40 or self.comfortable > 30 and self.dislike < 25:
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

        return action_possibilities

    def get_romantic_action_possibilities(self):
        """Returns a list of action possibilities for romantic increase."""
        action_possibilities = copy.deepcopy(LOVE['love_interest_only'])

        if self.romantic_love > 25 and self.opposite_relationship.romantic_love > 15:
            action_possibilities = action_possibilities + LOVE['love_interest']

        if self.mates and self.romantic_love > 30 and self.opposite_relationship.romantic_love > 25:
            action_possibilities = action_possibilities + LOVE['mates']

        return action_possibilities

    def affect_relationships(self, action, other=False):
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
            # starter boost for romantic
            if self.romantic_love <= 5:
                number_increase += 8
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
            # starter boost for romantic
            if self.romantic_love <= 5:
                number_increase += 8
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
    #                                new interaction                               #
    # ---------------------------------------------------------------------------- #

    def start_interaction(self) -> None:
        """This function handles the simple interaction of this relationship."""
        # such interactions are only allowed for living clan members
        if self.cat_from.dead or self.cat_from.outside or self.cat_from.exiled:
            return
        if self.cat_to.dead or self.cat_to.outside or self.cat_to.exiled:
            return

        # update relationship
        if self.cat_from.mate == self.cat_to.ID:
            self.mates = True

        # check if opposite_relationship is here, otherwise creates it
        if self.opposite_relationship is None:
            self.link_relationship()

        # get if the interaction is positive or negative for the relationship
        positive = self.positive_interaction()
        rel_type = self.get_interaction_type(positive)

        # look if an increase interaction or an decrease interaction
        in_de_crease = "increase" if positive else "decrease"
        # if the type is jealousy or dislike, then increase and decrease has to be turned around
        if rel_type in ["jealousy", "dislike"]:
            in_de_crease = "decrease" if positive else "increase"

        chance = game.config["relationship"]["chance_for_neutral"]
        if chance == 1:
            in_de_crease = "neutral"
        elif chance > 1 and random.randint(1, chance) == 1:
            in_de_crease = "neutral"

        # choice any type of intensity
        intensity = choice(["low", "medium", "high"])

        # get other possible filters
        season = str(game.clan.current_season).casefold()
        biome = str(game.clan.biome).casefold()

        #in_de_crease = "increase"
        #intensity = "high"
        #rel_type = "romantic"

        all_interactions = NEUTRAL_INTERACTIONS.copy()
        if in_de_crease != "neutral":
            all_interactions = MASTER_DICT[rel_type][in_de_crease].copy()
        possible_interactions = self.get_relevant_interactions(all_interactions, intensity, biome, season)
        if len(possible_interactions) <= 0:
            print("ERROR: No interaction with this conditions. ", rel_type, in_de_crease, intensity)
            possible_interactions = [
                Interaction("fall_back", "Any", "Any", "medium", [
                    "Default string, this should never appear."
                ])
            ]
        self.chosen_interaction = choice(possible_interactions)

        if in_de_crease != "neutral":
            self.interaction_affect_relationships(in_de_crease, intensity, rel_type)
        
        # get any possible interaction string out of this interaction
        interaction_str = choice(self.chosen_interaction.interactions)

        # prepare string for display
        interaction_str = interaction_str.replace("m_c", str(self.cat_from.name))
        interaction_str = interaction_str.replace("r_c", str(self.cat_to.name))

        effect = " (neutral effect)"
        if in_de_crease != "neutral" and positive:
            effect = f" ({intensity} positive effect)"
        if in_de_crease != "neutral" and not positive:
            effect = f" ({intensity} negative effect)"

        interaction_str = interaction_str + effect
        self.log.append(interaction_str)
        game.cur_events_list.append(Single_Event(
            interaction_str, ["relation", "interaction"], [self.cat_to.ID, self.cat_from.ID]
        ))

    def get_amount(self, in_de_crease: str, intensity: str) -> int:
        """Calculates the amount of such an interaction.

            Parameters
            ----------
            in_de_crease : list
                if the relationship value is increasing or decreasing the value
            intensity : str
                the intensity of the affect

            Returns
            -------
            amount : int
                the amount (negative or positive) for the given parameter
        """
        if in_de_crease == "neutral":
            return 0
        # get the normal amount
        amount = game.config["relationship"]["in_decrease_value"][intensity]
        if in_de_crease == "decrease":
            amount = amount * -1

        # take compatibility into account
        compatibility = get_personality_compatibility(self.cat_from, self.cat_to)
        if compatibility is None:
            # neutral compatibility
            amount = amount
        elif compatibility:
            # positive compatibility
            amount += game.config["relationship"]["compatibility_bonus"]
        else:
            # negative compatibility
            amount -= game.config["relationship"]["compatibility_bonus"]
        return amount

    def interaction_affect_relationships(self, in_de_crease: str, intensity: str, rel_type: str) -> None:
        """Affects the relationship according to the chosen types.

            Parameters
            ----------
            in_de_crease : list
                if the relationship value is increasing or decreasing the value
            intensity : str
                the intensity of the affect
            rel_type : str
                relationship value type which needs to be affected

            Returns
            -------
        """
        amount = self.get_amount(in_de_crease, intensity)

        # influence the own relationship
        if rel_type == "romantic":
            self.complex_romantic(amount)
        elif rel_type == "platonic":
            self.complex_platonic(amount)
        elif rel_type == "dislike":
            self.complex_dislike(amount)
        elif rel_type == "admiration":
            self.complex_admiration(amount)
        elif rel_type == "comfortable":
            self.complex_comfortable(amount)
        elif rel_type == "jealousy":
            self.complex_jealousy(amount)
        elif rel_type == "trust":
            self.complex_trust(amount)

        # influence the opposite relationship
        if self.opposite_relationship is None:
            return

        rel_dict = self.chosen_interaction.reaction_random_cat
        if rel_dict:
            self.opposite_relationship.change_according_dictionary(rel_dict)

        rel_dict = self.chosen_interaction.also_influences
        if rel_dict:
            self.change_according_dictionary(rel_dict)

    def change_according_dictionary(self, dictionary : dict) -> None:
        """Change the relationship value types according to the in- or decrease of the given dictionary.

            Parameters
            ----------
            dictionary : dict
                dictionary which defines the changes to the relationship

            Returns
            -------
        """
        for key, value in dictionary.items():
            if value == "neutral":
                continue
            amount = self.get_amount(value, "low")

            if key == "romantic":
                self.romantic_love += amount
            elif key == "platonic":
                self.platonic_like += amount
            elif key == "dislike":
                self.dislike += amount
            elif key == "admiration":
                self.admiration += amount
            elif key == "comfortable":
                self.comfortable += amount
            elif key == "jealousy":
                self.jealousy += amount
            elif key == "trust":
                self.trust += amount

    def positive_interaction(self) -> bool:
        """Returns if the interaction should be a positive interaction or not.

            Parameters
            ----------

            Returns
            -------
            positive : bool
                if the event has a positive or negative impact of the relationship

        """
        # how likely it is to have a positive or negative impact depends on the current values
        list_to_choice = [True, False]
        list_to_choice += [True] * int(self.platonic_like/10)
        list_to_choice += [False] * int(self.dislike/10)

        return choice(list_to_choice)

    def get_interaction_type(self, positive: bool) ->  str:
        """Returns the type of the interaction which should be made.
        
            Parameters
            ----------
            positive : bool
                if the event has a positive or negative impact of the relationship, 
                this define which weight will be used to get the type of the interaction

            Returns
            -------
            rel_type : string
                the relationship type which will happen
        """
        value_weights = {
            "trust": 1,
            "jealousy": 1,
            "comfortable": 1,
            "admiration": 1,
            "dislike": 1,
            "platonic": 1,
            "romantic": 1
        }

        # change the weights according if the interaction should be positive or negative
        if positive:
            value_weights["platonic"] += 1
        else:
            value_weights["dislike"] += 1
            value_weights["jealousy"] += 1

        # increase the chance of a romantic interaction if there already mates
        if self.mates:
            value_weights["romantic"] += 1

        # create the list of choices
        types = []
        for rel_type, weight in value_weights.items():
            types += [rel_type] * weight

        # if a romantic relationship is not possible, remove this type, mut only if there are no mates
        # if there already mates (set up by the user for example), don't remove this type
        mate_from_to = self.cat_from.is_potential_mate(self.cat_to, True)
        mate_to_from = self.cat_to.is_potential_mate(self.cat_from, True)
        if (not mate_from_to or not mate_to_from) and not self.mates:
            while "romantic" in types:
                types.remove("romantic")

        rel_type = choice(types)
        return rel_type

    def get_relevant_interactions(self, interactions : list, intensity : str, biome : str, season : str) -> list:
        """
        Filter interactions based on the status and other constraints.
            
            Parameters
            ----------
            interactions : list
                the interactions which need to be filtered
            intensity : str
                the intensity of the interactions
            biome : str
                biome of the clan
            season : str
                current season of the clan

            Returns
            -------
            filtered : list
                a list of interactions, which fulfill the criteria
        """
        filtered = []
        _season = [season, "Any", "any"]
        _biome = [biome, "Any", "any"]
        # if there are no loaded interactions, return empty list
        if not interactions:
            return filtered
        for inter in interactions:
            in_tags = list(filter(lambda biome: biome in _biome, inter.biome))
            if len(in_tags) > 0:
                continue

            in_tags = list(filter(lambda season: season in _season, inter.season))
            if len(in_tags) > 0:
                continue

            if inter.intensity != intensity:
                continue

            if len(inter.main_status_constraint) >= 1:
                if self.cat_from.status not in inter.main_status_constraint:
                    continue

            if len(inter.random_status_constraint) >= 1:
                if self.cat_to.status not in inter.random_status_constraint:
                    continue

            if len(inter.main_trait_constraint) >= 1:
                if self.cat_from.trait not in inter.main_trait_constraint:
                    continue

            if len(inter.random_trait_constraint) >= 1:
                if self.cat_to.trait not in inter.random_trait_constraint:
                    continue

            if len(inter.main_skill_constraint) >= 1:
                if self.cat_from.skill not in inter.main_skill_constraint:
                    continue

            if len(inter.random_skill_constraint) >= 1:
                if self.cat_to.skill not in inter.random_skill_constraint:
                    continue

            # if there is no constraint, skip other checks
            if len(inter.relationship_constraint) == 0:
                filtered.append(inter)
                continue

            if "siblings" in inter.relationship_constraint and not self.cat_from.is_sibling(self.cat_to):
                continue

            if "mates" in inter.relationship_constraint and not self.mates:
                continue

            if "not_mates" in inter.relationship_constraint and self.mates:
                continue

            if "parent/child" in inter.relationship_constraint and not self.cat_from.is_parent(self.cat_to):
                continue

            if "child/parent" in inter.relationship_constraint and not self.cat_to.is_parent(self.cat_from):
                continue

            value_types = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
            fulfilled = True
            for v_type in value_types:
                tags = list(filter(lambda constr: v_type in constr, inter.relationship_constraint))
                if len(tags) < 1:
                    continue
                threshold = 0
                lower_than = False
                # try to extract the value/threshold from the text
                try:
                    splitted = tags[0].split('_')
                    threshold = int(splitted[1])
                    if len(splitted) > 3:
                        lower_than = True
                except:
                    print(f"ERROR: interaction {inter.id} with the relationship constraint for the value {v_type} follows not the formatting guidelines.")
                    break

                if threshold > 100:
                    print(f"ERROR: interaction {inter.id} has a relationship constraints for the value {v_type}, which is higher than the max value of a relationship.")
                    break

                if threshold <= 0:
                    print(f"ERROR: patrol {inter.id} has a relationship constraints for the value {v_type}, which is lower than the min value of a relationship or 0.")
                    break

                threshold_fulfilled = False
                if v_type == "romantic":
                    if not lower_than and self.romantic_love >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.romantic_love <= threshold:
                        threshold_fulfilled = True
                if v_type == "platonic":
                    if not lower_than and self.platonic_like >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.platonic_like <= threshold:
                        threshold_fulfilled = True
                if v_type == "dislike":
                    if not lower_than and self.dislike >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.dislike <= threshold:
                        threshold_fulfilled = True
                if v_type == "comfortable":
                    if not lower_than and self.comfortable >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.comfortable <= threshold:
                        threshold_fulfilled = True
                if v_type == "jealousy":
                    if not lower_than and self.jealousy >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.jealousy <= threshold:
                        threshold_fulfilled = True
                if v_type == "trust":
                    if not lower_than and self.trust >= threshold:
                        threshold_fulfilled = True
                    elif lower_than and self.trust <= threshold:
                        threshold_fulfilled = True

                if not threshold_fulfilled:
                    fulfilled = False
                    continue

            if fulfilled:
                filtered.append(inter)

        return filtered


    # ---------------------------------------------------------------------------- #
    #                            complex value addition                            #
    # ---------------------------------------------------------------------------- #

    # How increasing one state influences another directly: (an increase of one state doesn't trigger a chain reaction)
    # increase romantic_love -> decreases: dislike | increases: like, comfortable
    # increase like -> decreases: dislike | increases: comfortable
    # increase dislike -> decreases: romantic_love, like | increases: -
    # increase admiration -> decreases: - | increases: -
    # increase comfortable -> decreases: jealousy, dislike | increases: trust, like
    # increase jealousy -> decreases: - | increases: dislike
    # increase trust -> decreases: dislike | increases: -

    # !! DECREASING ONE STATE DOES'T INFLUENCE OTHERS !!

    def complex_romantic(self, value):
        """Add the value to the romantic type and influence other value types as well."""
        self.romantic_love += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.platonic_like += buff
            self.comfortable += buff
            self.dislike -= buff

    def complex_platonic(self, value):
        """Add the value to the platonic type and influence other value types as well."""
        self.platonic_like += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.comfortable += buff
            self.dislike -= buff

    def complex_dislike(self, value):
        """Add the value to the dislike type and influence other value types as well."""
        self.dislike += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.romantic_love -= buff
            self.platonic_like -= buff

    def complex_admiration(self, value):
        """Add the value to the admiration type and influence other value types as well."""
        self.admiration += value

    def complex_comfortable(self, value):
        """Add the value to the comfortable type and influence other value types as well."""
        self.comfortable += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.trust += buff
            self.platonic_like += buff
            self.dislike -= buff
            self.jealousy -= buff

    def complex_jealousy(self, value):
        """Add the value to the jealousy type and influence other value types as well."""
        self.jealousy += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.dislike += buff

    def complex_trust(self, value):
        """Add the value to the trust type and influence other value types as well."""
        self.trust += value
        if value > 0:
            buff = game.config["relationship"]["passive_influence"]
            self.dislike -= buff


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


class Interaction():

    def __init__(self,
                 id,
                 biome=None,
                 season=None,
                 intensity="medium",
                 interactions=None,
                 relationship_constraint=None,
                 main_status_constraint=None,
                 random_status_constraint=None,
                 main_trait_constraint=None,
                 random_trait_constraint=None,
                 main_skill_constraint=None,
                 random_skill_constraint=None,
                 reaction_random_cat=None,
                 also_influences=None):
        self.id = id
        self.intensity = intensity
        self.biome = biome if biome else ["Any"]
        self.season = season if season else ["Any"]

        if interactions:
            self.interactions = interactions
        else:
            self.interactions = [f"This is a default interaction! ID: {id} with cats (m_c), (r_c)"]

        if relationship_constraint:
            self.relationship_constraint = relationship_constraint
        else:
            self.relationship_constraint = []

        if main_status_constraint:
            self.main_status_constraint = main_status_constraint
        else:
            self.main_status_constraint = []

        if random_status_constraint:
            self.random_status_constraint = random_status_constraint
        else:
            self.random_status_constraint = []

        if main_trait_constraint:
            self.main_trait_constraint = main_trait_constraint
        else:
            self.main_trait_constraint = []

        if random_trait_constraint:
            self.random_trait_constraint = random_trait_constraint
        else:
            self.random_trait_constraint = []

        if main_skill_constraint:
            self.main_skill_constraint = main_skill_constraint
        else:
            self.main_skill_constraint = []

        if random_skill_constraint:
            self.random_skill_constraint = random_skill_constraint
        else:
            self.random_skill_constraint = []

        if reaction_random_cat:
            self.reaction_random_cat = reaction_random_cat
        else:
            self.reaction_random_cat = {}
        
        if also_influences:
            self.also_influences = also_influences
        else:
            self.also_influences = {}

# IN increase or decrease
resource_directory = "resources/dicts/relationship_events/"
de_in_crease_path = "DE_IN_CREASE/"
cat_to_other_path = "cat_to_other/"

# ---------------------------------------------------------------------------- #
#                   build master dictionary for interactions                   #
# ---------------------------------------------------------------------------- #

def create_interaction(inter_list) -> list:
    created_list = []
    for inter in inter_list:
        created_list.append(Interaction(
            id=inter["id"],
            biome=inter["biome"] if "biome" in inter else "Any",
            season=inter["season"] if "season" in inter else "Any",
            intensity=inter["intensity"] if "intensity" in inter else "medium",
            interactions=inter["interactions"] if "interactions" in inter else None,
            relationship_constraint = inter["relationship_constraint"] if "relationship_constraint" in inter else [],
            main_status_constraint = inter["main_status_constraint"] if "main_status_constraint" in inter else [],
            random_status_constraint = inter["random_status_constraint"] if "random_status_constraint" in inter else [],
            main_trait_constraint = inter["main_trait_constraint"] if "main_trait_constraint" in inter else [],
            random_trait_constraint = inter["random_trait_constraint"] if "random_trait_constraint" in inter else [],
            main_skill_constraint = inter["main_skill_constraint"] if "main_skill_constraint" in inter else [],
            random_skill_constraint = inter["random_skill_constraint"] if "random_skill_constraint" in inter else [],
            reaction_random_cat= inter["reaction_random_cat"] if "reaction_random_cat" in inter else None,
            also_influences = inter["also_influences"] if "also_influences" in inter else None
        ))
    return created_list

MASTER_DICT = {"romantic": {}, "platonic": {}, "dislike": {}, "admiration": {}, "comfortable": {}, "jealousy": {}, "trust": {}}
rel_types = ["romantic", "platonic", "dislike", "admiration", "comfortable", "jealousy", "trust"]
base_path = os.path.join("resources","dicts", "relationship_events", "normal_interactions")
for rel in rel_types:
    file_name = rel + ".json"
    with open(os.path.join(base_path, file_name), 'r') as read_file:
        loaded_dict = ujson.loads(read_file.read())
        MASTER_DICT[rel]["increase"] = create_interaction(loaded_dict["increase"])
        MASTER_DICT[rel]["decrease"] = create_interaction(loaded_dict["decrease"])

NEUTRAL_INTERACTIONS = []
with open(os.path.join(base_path, "neutral.json"), 'r') as read_file:
    loaded_list = ujson.loads(read_file.read())
    NEUTRAL_INTERACTIONS = create_interaction(loaded_list)

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
