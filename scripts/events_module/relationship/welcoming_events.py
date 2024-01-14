import os
import ujson
from copy import deepcopy
from random import choice

from scripts.utility import change_relationship_values, event_text_adjust
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event
from scripts.cat.cats import Cat

class Welcoming_Events():
    """All events which are related to welcome a new cat in the clan."""
    
    @staticmethod    
    def welcome_cat(clan_cat: Cat, new_cat: Cat) -> None:
        """Checks and triggers the welcome event from the Clan cat to the new cat.

            Parameters
            ----------
            clan_cat : Cat
                the Clan cat which welcome the new cat
            new_cat : Cat
                new cat which will be welcomed

            Returns
            -------
        """
        if new_cat.ID == clan_cat.ID:
            return

        # setup the status as "key" to use it
        status = clan_cat.status
        if status == "medicine cat" or status == "medicine cat apprentice":
            status = "medicine"

        if status == "mediator apprentice":
            status = "mediator"

        # collect all events
        possible_events = deepcopy(GENERAL_WELCOMING)
        if status not in WELCOMING_MASTER_DICT:
            print(f"ERROR: there is no welcoming json for the status {status}")
        else:
            possible_events.extend(WELCOMING_MASTER_DICT[status])
        filtered_events = Welcoming_Events.filter_welcome_interactions(possible_events, new_cat)

        # choose which interaction will be displayed
        random_interaction = choice(filtered_events)
        interaction_str = choice(random_interaction.interactions)

        # prepare string for display
        interaction_str = event_text_adjust(Cat, interaction_str, clan_cat, new_cat)

        # influence the relationship
        new_to_clan_cat = game.config["new_cat"]["rel_buff"]["new_to_clan_cat"]
        clan_cat_to_new = game.config["new_cat"]["rel_buff"]["clan_cat_to_new"]
        change_relationship_values(
            cats_to=        [clan_cat.ID], 
            cats_from=      [new_cat],
            romantic_love=  new_to_clan_cat["romantic"],
            platonic_like=  new_to_clan_cat["platonic"],
            dislike=        new_to_clan_cat["dislike"],
            admiration=     new_to_clan_cat["admiration"],
            comfortable=    new_to_clan_cat["comfortable"],
            jealousy=       new_to_clan_cat["jealousy"],
            trust=          new_to_clan_cat["trust"]
        )
        change_relationship_values(
            cats_to=        [new_cat.ID], 
            cats_from=      [clan_cat],
            romantic_love=  clan_cat_to_new["romantic"],
            platonic_like=  clan_cat_to_new["platonic"],
            dislike=        clan_cat_to_new["dislike"],
            admiration=     clan_cat_to_new["admiration"],
            comfortable=    clan_cat_to_new["comfortable"],
            jealousy=       clan_cat_to_new["jealousy"],
            trust=          clan_cat_to_new["trust"]
        )

        # add it to the event list
        game.cur_events_list.append(Single_Event(
            interaction_str, ["relation", "interaction"], [new_cat.ID, clan_cat.ID]))

        # add to relationship logs
        if new_cat.ID in clan_cat.relationships:
            if clan_cat.age == 1:
                clan_cat.relationships[new_cat.ID].log.append(interaction_str + f" - {clan_cat.name} was {clan_cat.moons} moons old")
            else:
                clan_cat.relationships[new_cat.ID].log.append(interaction_str + f" - {clan_cat.name} was {clan_cat.moons} moons old")

            new_cat.relationships[clan_cat.ID].link_relationship()

        if clan_cat.ID in new_cat.relationships:
            if new_cat.age == 1:
                new_cat.relationships[clan_cat.ID].log.append(interaction_str + f" - {new_cat.name} was {new_cat.moons} moon old")
            else:
                new_cat.relationships[clan_cat.ID].log.append(interaction_str + f" - {new_cat.name} was {new_cat.moons} moons old")

    @staticmethod
    def filter_welcome_interactions(welcome_interactions : list, new_cat: Cat) -> list:
        """Filter welcome events based on states.
    
            Parameters
            ----------
            welcome_interactions : list
                a list of welcome interaction
            new_cat : Cat
                new cat which will be welcomed

            Returns
            -------
            filtered list of welcome interactions
        """
        filtered = []
        for interaction in welcome_interactions:
            if interaction.background and new_cat.backstory not in interaction.background:
                continue

            if interaction.new_cat_moons:
                threshold_moon = interaction.new_cat_moons.split('_')
                threshold_moon = int(threshold_moon[len(threshold_moon) - 1])

                if "over" in interaction.new_cat_moons and new_cat.moons < threshold_moon:
                    continue
                if "under" in interaction.new_cat_moons and new_cat.moons > threshold_moon:
                    continue
                if "over" not in interaction.new_cat_moons and "under" not in interaction.new_cat_moons:
                    print(f"ERROR: The new cat welcoming event {interaction.id} has a not valid moon restriction for the new cat.")
                    continue

            filtered.append(interaction)
        return filtered


class Welcome_Interaction():

    def __init__(self,
                 id,
                 interactions=None,
                 background=None,
                 new_cat_moons=None
                 ):
        self.id = id
        self.background = background
        self.new_cat_moons = new_cat_moons
        
        if interactions:
            self.interactions = interactions
        else:
            self.interactions = ["m_c is welcoming r_c."]

# ---------------------------------------------------------------------------- #
#                   build master dictionary for interactions                   #
# ---------------------------------------------------------------------------- #

def create_welcome_interaction(inter_list) -> list:
    created_list = []

    for inter in inter_list:
        created_list.append(Welcome_Interaction(
            id=inter["id"],
            interactions=inter["interactions"] if "interactions" in inter else None,
            background=inter["background"] if "background" in inter else None,
            new_cat_moons=inter["new_cat_moons"] if "new_cat_moons" in inter else None
            )
        )

    return created_list


base_path = os.path.join(
    "resources",
    "dicts",
    "relationship_events",
    "welcoming_events"
)

WELCOMING_MASTER_DICT = {}
for file in os.listdir(base_path):
    if "general.json" == file:
        continue
    status = file.split(".")[0]
    with open(os.path.join(base_path, file), 'r') as read_file:
        welcome_list = ujson.load(read_file)
        WELCOMING_MASTER_DICT[status] = create_welcome_interaction(welcome_list)

GENERAL_WELCOMING = []
with open(os.path.join(base_path, "general.json"), 'r') as read_file:
    loaded_list = ujson.loads(read_file.read())
    GENERAL_WELCOMING = create_welcome_interaction(loaded_list)