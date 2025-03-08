# pylint: disable=line-too-long
"""

TODO: Docs


"""

# pylint: enable=line-too-long

import os
import random
import statistics
from random import choice, randint

import i18n
import pygame
import ujson

from scripts.cat.cats import Cat, cat_class
from scripts.cat.history import History
from scripts.cat.names import names
from scripts.cat.sprites import sprites
from scripts.clan_resources.freshkill import FreshkillPile, Nutrition
from scripts.clan_resources.herb.herb_supply import HerbSupply
from scripts.events_module.generate_events import OngoingEvent
from scripts.game_structure.game_essentials import game
from scripts.housekeeping.datadir import get_save_dir
from scripts.housekeeping.version import get_version_info, SAVE_VERSION_NUMBER
from scripts.utility import (
    get_current_season,
    quit,
    clan_symbol_sprite, get_living_clan_cat_count,
)  # pylint: disable=redefined-builtin


class Clan:
    """

    TODO: Docs

    """

    BIOME_TYPES = ["Forest", "Plains", "Mountainous", "Beach"]

    CAT_TYPES = [
        "newborn",
        "kitten",
        "apprentice",
        "warrior",
        "medicine",
        "deputy",
        "leader",
        "elder",
        "mediator",
        "general",
    ]

    leader_lives = 0
    clan_cats = []
    starclan_cats = []
    darkforest_cats = []
    unknown_cats = []
    seasons = [
        "Newleaf",
        "Newleaf",
        "Newleaf",
        "Greenleaf",
        "Greenleaf",
        "Greenleaf",
        "Leaf-fall",
        "Leaf-fall",
        "Leaf-fall",
        "Leaf-bare",
        "Leaf-bare",
        "Leaf-bare",
    ]

    temperament_dict = {
        "low_social": ["cunning", "proud", "bloodthirsty"],
        "mid_social": ["amiable", "stoic", "wary"],
        "high_social": ["gracious", "mellow", "logical"],
    }

    with open("resources/placements.json", "r", encoding="utf-8") as read_file:
        layouts = ujson.loads(read_file.read())

    age = 0
    current_season = "Newleaf"
    all_clans = []

    def __init__(
        self,
        name="",
        leader=None,
        deputy=None,
        medicine_cat=None,
        biome="Forest",
        camp_bg=None,
        symbol=None,
        game_mode="classic",
        starting_members=[],
        starting_season="Newleaf",
        self_run_init_functions=True,
    ):
        self.history = History()
        if name == "":
            return

        self.name = name
        self.leader = leader
        self.leader_lives = 9
        self.leader_predecessors = 0
        self.deputy = deputy
        self.deputy_predecessors = 0
        self.medicine_cat = medicine_cat
        self.med_cat_list = []
        self.med_cat_predecessors = 0

        self.med_cat_number = len(
            self.med_cat_list
        )  # Must do this after the medicine cat is added to the list.
        self.age = 0
        self.current_season = "Newleaf"
        self.starting_season = starting_season
        self.instructor = None
        # This is the first cat in starclan, to "guide" the other dead cats there.
        self.biome = biome
        self.camp_bg = camp_bg
        self.chosen_symbol = symbol
        self.game_mode = game_mode
        self.pregnancy_data = {}
        self.inheritance = {}
        self.custom_pronouns = {}

        # Init Settings
        self.clan_settings = {}
        self.setting_lists = {}
        with open("resources/clansettings.json", "r", encoding="utf-8") as read_file:
            _settings = ujson.loads(read_file.read())

        for setting, values in _settings["__other"].items():
            self.clan_settings[setting] = values[0]
            self.setting_lists[setting] = values

        all_settings = []
        all_settings.append(_settings["general"])
        all_settings.append(_settings["role"])
        all_settings.append(_settings["relation"])
        all_settings.append(_settings["freshkill_tactics"])
        all_settings.append(_settings["clan_focus"])

        for setting in all_settings:  # Add all the settings to the settings dictionary
            for setting_name, inf in setting.items():
                self.clan_settings[setting_name] = inf[2]
                self.setting_lists[setting_name] = [inf[2], not inf[2]]

        # Reputation is for loners/kittypets/outsiders in general that wish to join the clan.
        # it's a range from 1-100, with 30-70 being neutral, 71-100 being "welcoming",
        # and 1-29 being "hostile". if you're hostile to outsiders, they will VERY RARELY show up.
        self._reputation = 80

        self.starting_members = starting_members
        if game_mode in ["expanded", "cruel season"]:
            self.freshkill_pile = FreshkillPile()
        else:
            self.freshkill_pile = None
        self.herb_supply = HerbSupply()
        self.primary_disaster = None
        self.secondary_disaster = None
        self.war = {
            "at_war": False,
            "enemy": None,
            "duration": 0,
        }
        self.last_focus_change = None
        self.clans_in_focus = []

        self.faded_ids = (
            []
        )  # Stores ID's of faded cats, to ensure these IDs aren't reused.
        if self_run_init_functions:
            self.post_initialization_functions()

    # The clan couldn't save itself in time due to issues arising, for example, from this function: "if deputy is not None: self.deputy.status_change('deputy') -> game.clan.remove_med_cat(self)"
    def post_initialization_functions(self):
        if self.deputy is not None:
            self.deputy.status_change("deputy")
            self.clan_cats.append(self.deputy.ID)

        if self.leader:
            self.leader.status_change("leader")
            self.clan_cats.append(self.leader.ID)

        if self.medicine_cat is not None:
            self.clan_cats.append(self.medicine_cat.ID)
            self.med_cat_list.append(self.medicine_cat.ID)
            if self.medicine_cat.status != "medicine cat":
                Cat.all_cats[self.medicine_cat.ID].status_change("medicine cat")

    def create_clan(self):
        """
        This function is only called once a new clan is
        created in the 'clan created' screen, not every time
        the program starts
        """
        self.instructor = Cat(
            status=choice(
                [
                    "apprentice",
                    "mediator apprentice",
                    "medicine cat apprentice",
                    "warrior",
                    "medicine cat",
                    "leader",
                    "mediator",
                    "deputy",
                    "elder",
                ]
            ),
        )
        self.instructor.dead = True
        self.instructor.dead_for = randint(20, 200)
        self.add_cat(self.instructor)
        self.add_to_starclan(self.instructor)
        self.all_clans = []

        key_copy = tuple(Cat.all_cats.keys())
        for i in key_copy:  # Going through all currently existing cats
            # cat_class is a Cat-object
            not_found = True
            for x in self.starting_members:
                if Cat.all_cats[i] == x:
                    self.add_cat(Cat.all_cats[i])
                    not_found = False
            if (
                Cat.all_cats[i] != self.leader
                and Cat.all_cats[i] != self.medicine_cat
                and Cat.all_cats[i] != self.deputy
                and Cat.all_cats[i] != self.instructor
                and not_found
            ):
                Cat.all_cats[i].example = True
                self.remove_cat(Cat.all_cats[i].ID)

        # give thoughts,actions and relationships to cats
        for cat_id in Cat.all_cats:
            Cat.all_cats.get(cat_id).init_all_relationships()
            Cat.all_cats.get(cat_id).backstory = "clan_founder"
            if Cat.all_cats.get(cat_id).status == "apprentice":
                Cat.all_cats.get(cat_id).status_change("apprentice")
            Cat.all_cats.get(cat_id).thoughts()

        game.save_cats()
        number_other_clans = randint(3, 5)
        for _ in range(number_other_clans):
            other_clan_names = [str(i.name) for i in self.all_clans] + [game.clan.name]
            other_clan_name = choice(
                names.names_dict["normal_prefixes"] + names.names_dict["clan_prefixes"]
            )
            while other_clan_name in other_clan_names:
                other_clan_name = choice(
                    names.names_dict["normal_prefixes"]
                    + names.names_dict["clan_prefixes"]
                )
            other_clan = OtherClan(name=other_clan_name)
            self.all_clans.append(other_clan)
        self.save_clan()
        game.save_clanlist(self.name)
        game.switches["clan_list"] = game.read_clans()
        # if map_available:
        #    save_map(game.map_info, game.clan.name)

        # CHECK IF CAMP BG IS SET -fail-safe in case it gets set to None-
        if game.switches["camp_bg"] is None:
            random_camp_options = ["camp1", "camp2"]
            random_camp = choice(random_camp_options)
            game.switches["camp_bg"] = random_camp

        # if no game mode chosen, set to Classic
        if game.switches["game_mode"] is None:
            game.switches["game_mode"] = "classic"
            self.game_mode = "classic"
        # if game.switches['game_mode'] == 'cruel_season':
        #    game.settings['disasters'] = True

        # set the starting season
        season_index = self.seasons.index(self.starting_season)
        self.current_season = self.seasons[season_index]

    def add_cat(self, cat):  # cat is a 'Cat' object
        """Adds cat into the list of clan cats"""
        if cat.ID in Cat.all_cats and cat.ID not in self.clan_cats:
            self.clan_cats.append(cat.ID)

    def add_to_starclan(self, cat):  # Same as add_cat
        """
        Places the dead cat into StarClan.
        It should not be removed from the list of cats in the clan
        """
        if (
            cat.ID in Cat.all_cats
            and cat.dead
            and cat.ID not in self.starclan_cats
            and cat.df is False
        ):
            # The dead-value must be set to True before the cat can go to starclan
            self.starclan_cats.append(cat.ID)
            if cat.ID in self.darkforest_cats:
                self.darkforest_cats.remove(cat.ID)
            if cat.ID in self.unknown_cats:
                self.unknown_cats.remove(cat.ID)
            if cat.ID in self.med_cat_list:
                self.med_cat_list.remove(cat.ID)
                self.med_cat_predecessors += 1

    def add_to_darkforest(self, cat):  # Same as add_cat
        """
        Places the dead cat into the dark forest.
        It should not be removed from the list of cats in the clan
        """
        if cat.ID in Cat.all_cats and cat.dead and cat.df:
            self.darkforest_cats.append(cat.ID)
            if cat.ID in self.starclan_cats:
                self.starclan_cats.remove(cat.ID)
            if cat.ID in self.unknown_cats:
                self.unknown_cats.remove(cat.ID)
            if cat.ID in self.med_cat_list:
                self.med_cat_list.remove(cat.ID)
                self.med_cat_predecessors += 1
            # update_sprite(Cat.all_cats[str(cat)])
            # The dead-value must be set to True before the cat can go to starclan

    def add_to_unknown(self, cat):
        """
        Places dead cat into the unknown residence.
        It should not be removed from the list of cats in the clan
        :param cat: cat object
        """
        if cat.ID in Cat.all_cats and cat.dead and cat.outside:
            self.unknown_cats.append(cat.ID)
            if cat.ID in self.starclan_cats:
                self.starclan_cats.remove(cat.ID)
            if cat.ID in self.darkforest_cats:
                self.darkforest_cats.remove(cat.ID)
            if cat.ID in self.med_cat_list:
                self.med_cat_list.remove(cat.ID)
                self.med_cat_predecessors += 1

    def add_to_clan(self, cat):
        """
        TODO: DOCS
        """
        if (
            cat.ID in Cat.all_cats
            and not cat.outside
            and not cat.dead
            and cat.ID in Cat.outside_cats
        ):
            # The outside-value must be set to True before the cat can go to cotc
            Cat.outside_cats.pop(cat.ID)
            cat.clan = str(game.clan.name)

    def add_to_outside(self, cat):  # same as add_cat
        """
        Places the gone cat into cotc.
        It should not be removed from the list of cats in the clan
        """
        if cat.ID in Cat.all_cats and cat.outside and cat.ID not in Cat.outside_cats:
            # The outside-value must be set to True before the cat can go to cotc
            Cat.outside_cats.update({cat.ID: cat})

    def remove_cat(self, ID):  # ID is cat.ID
        """
        This function is for completely removing the cat from the game,
        it's not meant for a cat that's simply dead
        """

        if Cat.all_cats[ID] in Cat.all_cats_list:
            Cat.all_cats_list.remove(Cat.all_cats[ID])

        if ID in Cat.all_cats:
            Cat.all_cats.pop(ID)

        if ID in self.clan_cats:
            self.clan_cats.remove(ID)
        if ID in self.starclan_cats:
            self.starclan_cats.remove(ID)
        if ID in self.unknown_cats:
            self.unknown_cats.remove(ID)
        if ID in self.darkforest_cats:
            self.darkforest_cats.remove(ID)

    def __repr__(self):
        if self.name is not None:
            _ = (
                f"{self.name}: led by {self.leader.name}"
                f"with {self.medicine_cat.name} as med. cat"
            )
            return _

        else:
            return "No Clan"

    def new_leader(self, leader):
        """
        TODO: DOCS
        """
        if leader:
            self.history.add_lead_ceremony(leader)
            self.leader = leader
            Cat.all_cats[leader.ID].status_change("leader")
            self.leader_predecessors += 1
            self.leader_lives = 9
        game.switches["new_leader"] = None

    def new_deputy(self, deputy):
        """
        TODO: DOCS
        """
        if deputy:
            self.deputy = deputy
            Cat.all_cats[deputy.ID].status_change("deputy")
            self.deputy_predecessors += 1

    def new_medicine_cat(self, medicine_cat):
        """
        TODO: DOCS
        """
        if medicine_cat:
            if medicine_cat.status != "medicine cat":
                Cat.all_cats[medicine_cat.ID].status_change("medicine cat")
            if medicine_cat.ID not in self.med_cat_list:
                self.med_cat_list.append(medicine_cat.ID)
            medicine_cat = self.med_cat_list[0]
            self.medicine_cat = Cat.all_cats[medicine_cat]
            self.med_cat_number = len(self.med_cat_list)

    def remove_med_cat(self, medicine_cat):
        """
        Removes a med cat. Use when retiring, or switching to warrior
        """
        if medicine_cat:
            if medicine_cat.ID in game.clan.med_cat_list:
                game.clan.med_cat_list.remove(medicine_cat.ID)
                game.clan.med_cat_number = len(game.clan.med_cat_list)
            if self.medicine_cat:
                if medicine_cat.ID == self.medicine_cat.ID:
                    if game.clan.med_cat_list:
                        game.clan.medicine_cat = Cat.fetch_cat(
                            game.clan.med_cat_list[0]
                        )
                        game.clan.med_cat_number = len(game.clan.med_cat_list)
                    else:
                        game.clan.medicine_cat = None

    @staticmethod
    def switch_clans(clan):
        """
        TODO: DOCS
        """
        game.save_clanlist(clan)
        quit(savesettings=False, clearevents=True)

    def save_clan(self):
        """
        TODO: DOCS
        """

        clan_data = {
            "clanname": self.name,
            "clanage": self.age,
            "biome": self.biome,
            "camp_bg": self.camp_bg,
            "clan_symbol": self.chosen_symbol,
            "gamemode": self.game_mode,
            "last_focus_change": self.last_focus_change,
            "clans_in_focus": self.clans_in_focus,
            "instructor": self.instructor.ID,
            "reputation": self.reputation,
            "mediated": game.mediated,
            "starting_season": self.starting_season,
            "temperament": self.temperament,
            "version_name": SAVE_VERSION_NUMBER,
            "version_commit": get_version_info().version_number,
            "source_build": get_version_info().is_source_build,
            "custom_pronouns": self.custom_pronouns,
        }

        # LEADER DATA
        if self.leader:
            clan_data["leader"] = self.leader.ID
            clan_data["leader_lives"] = self.leader_lives
        else:
            clan_data["leader"] = None

        clan_data["leader_predecessors"] = self.leader_predecessors

        # DEPUTY DATA
        if self.deputy:
            clan_data["deputy"] = self.deputy.ID
        else:
            clan_data["deputy"] = None

        clan_data["deputy_predecessors"] = self.deputy_predecessors

        # MED CAT DATA
        if self.medicine_cat:
            clan_data["med_cat"] = self.medicine_cat.ID
        else:
            clan_data["med_cat"] = None
        clan_data["med_cat_number"] = self.med_cat_number
        clan_data["med_cat_predecessors"] = self.med_cat_predecessors

        # LIST OF CLAN CATS
        clan_data["clan_cats"] = ",".join([str(i) for i in self.clan_cats])

        clan_data["faded_cats"] = ",".join([str(i) for i in self.faded_ids])

        # Patrolled cats
        clan_data["patrolled_cats"] = [str(i) for i in game.patrolled]

        # OTHER CLANS
        clan_data["other_clans"] = [vars(i) for i in self.all_clans]

        clan_data["war"] = self.war

        self.save_herb_supply(game.clan)
        self.save_disaster(game.clan)
        self.save_pregnancy(game.clan)

        self.save_clan_settings()
        if game.clan.game_mode in ["expanded", "cruel season"]:
            self.save_freshkill_pile(game.clan)

        game.safe_save(f"{get_save_dir()}/{self.name}clan.json", clan_data)

        if os.path.exists(get_save_dir() + f"/{self.name}clan.txt") & (
            self.name != "current"
        ):
            os.remove(get_save_dir() + f"/{self.name}clan.txt")

    def switch_setting(self, setting_name):
        """Call this function to change a setting given in the parameter by one to the right on it's list"""
        self.settings_changed = True

        # Give the index that the list is currently at
        list_index = self.setting_lists[setting_name].index(
            self.clan_settings[setting_name]
        )

        if (
            list_index == len(self.setting_lists[setting_name]) - 1
        ):  # The option is at the list's end, go back to 0
            self.clan_settings[setting_name] = self.setting_lists[setting_name][0]
        else:
            # Else move on to the next item on the list
            self.clan_settings[setting_name] = self.setting_lists[setting_name][
                list_index + 1
            ]

    def save_clan_settings(self):
        game.safe_save(
            get_save_dir() + f"/{self.name}/clan_settings.json", self.clan_settings
        )

    def load_clan(self):
        """
        TODO: DOCS
        """

        version_info = None
        if os.path.exists(
            get_save_dir() + "/" + game.switches["clan_list"][0] + "clan.json"
        ):
            version_info = self.load_clan_json()
        elif os.path.exists(
            get_save_dir() + "/" + game.switches["clan_list"][0] + "clan.txt"
        ):
            self.load_clan_txt()
        else:
            game.switches["error_message"] = "There was an error loading the clan.json"

        game.clan.load_clan_settings()

        return version_info

    def load_clan_txt(self):
        """
        TODO: DOCS
        """

        if game.switches["clan_list"] == "":
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return
        if game.switches["clan_list"][0].strip() == "":
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return
        game.switches["error_message"] = "There was an error loading the clan.txt"
        with open(
            get_save_dir() + "/" + game.switches["clan_list"][0] + "clan.txt",
            "r",
            encoding="utf-8",
        ) as read_file:  # pylint: disable=redefined-outer-name
            clan_data = read_file.read()
        clan_data = clan_data.replace("\t", ",")
        sections = clan_data.split("\n")
        if len(sections) == 7:
            general = sections[0].split(",")
            leader_info = sections[1].split(",")
            deputy_info = sections[2].split(",")
            med_cat_info = sections[3].split(",")
            instructor_info = sections[4]
            members = sections[5].split(",")
            other_clans = sections[6].split(",")
        elif len(sections) == 6:
            general = sections[0].split(",")
            leader_info = sections[1].split(",")
            deputy_info = sections[2].split(",")
            med_cat_info = sections[3].split(",")
            instructor_info = sections[4]
            members = sections[5].split(",")
            other_clans = []
        else:
            general = sections[0].split(",")
            leader_info = sections[1].split(",")
            deputy_info = 0, 0
            med_cat_info = sections[2].split(",")
            instructor_info = sections[3]
            members = sections[4].split(",")
            other_clans = []
        if len(general) == 9:
            if general[3] == "None":
                general[3] = "camp1"
            elif general[4] == "None":
                general[4] = 0
            elif general[7] == "None":
                general[7] = "classic"
            elif general[8] == "None":
                general[8] = 50
            game.clan = Clan(
                name=general[0],
                leader=Cat.all_cats[leader_info[0]],
                deputy=Cat.all_cats.get(deputy_info[0], None),
                medicine_cat=Cat.all_cats.get(med_cat_info[0], None),
                biome=general[2],
                camp_bg=general[3],
                game_mode=general[7],
                self_run_init_functions=False,
            )
            game.clan.post_initialization_functions()
            game.clan.reputation = general[8]
        elif len(general) == 8:
            if general[3] == "None":
                general[3] = "camp1"
            elif general[4] == "None":
                general[4] = 0
            elif general[7] == "None":
                general[7] = "classic"
            game.clan = Clan(
                name=general[0],
                leader=Cat.all_cats[leader_info[0]],
                deputy=Cat.all_cats.get(deputy_info[0], None),
                medicine_cat=Cat.all_cats.get(med_cat_info[0], None),
                biome=general[2],
                camp_bg=general[3],
                game_mode=general[7],
                self_run_init_functions=False,
            )
            game.clan.post_initialization_functions()
        elif len(general) == 7:
            if general[4] == "None":
                general[4] = 0
            elif general[3] == "None":
                general[3] = "camp1"
            game.clan = Clan(
                name=general[0],
                leader=Cat.all_cats[leader_info[0]],
                deputy=Cat.all_cats.get(deputy_info[0], None),
                medicine_cat=Cat.all_cats.get(med_cat_info[0], None),
                biome=general[2],
                camp_bg=general[3],
                self_run_init_functions=False,
            )
            game.clan.post_initialization_functions()
        elif len(general) == 3:
            game.clan = Clan(
                name=general[0],
                leader=Cat.all_cats[leader_info[0]],
                deputy=Cat.all_cats.get(deputy_info[0], None),
                medicine_cat=Cat.all_cats.get(med_cat_info[0], None),
                biome=general[2],
                self_run_init_functions=False,
            )
            game.clan.post_initialization_functions()
        else:
            game.clan = Clan(
                general[0],
                Cat.all_cats[leader_info[0]],
                Cat.all_cats.get(deputy_info[0], None),
                Cat.all_cats.get(med_cat_info[0], None),
                self_run_init_functions=False,
            )
            game.clan.post_initialization_functions()
        game.clan.age = int(general[1])
        if not game.config["lock_season"]:
            game.clan.current_season = game.clan.seasons[game.clan.age % 12]
        else:
            game.clan.current_season = game.clan.starting_season
        game.clan.leader_lives, game.clan.leader_predecessors = int(
            leader_info[1]
        ), int(leader_info[2])

        if len(deputy_info) > 1:
            game.clan.deputy_predecessors = int(deputy_info[1])
        if len(med_cat_info) > 1:
            game.clan.med_cat_predecessors = int(med_cat_info[1])
        if len(med_cat_info) > 2:
            game.clan.med_cat_number = int(med_cat_info[2])
        if len(sections) > 4:
            if instructor_info in Cat.all_cats:
                game.clan.instructor = Cat.all_cats[instructor_info]
                game.clan.add_cat(game.clan.instructor)
        else:
            game.clan.instructor = Cat(status=choice(["warrior", "warrior", "elder"]))
            # update_sprite(game.clan.instructor)
            game.clan.instructor.dead = True
            game.clan.add_cat(game.clan.instructor)
        if other_clans != [""]:
            for other_clan in other_clans:
                other_clan_info = other_clan.split(";")
                self.all_clans.append(
                    OtherClan(
                        other_clan_info[0], int(other_clan_info[1]), other_clan_info[2]
                    )
                )

        else:
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())

        for cat in members:
            if cat in Cat.all_cats:
                game.clan.add_cat(Cat.all_cats[cat])
                game.clan.add_to_starclan(Cat.all_cats[cat])
            else:
                print("WARNING: Cat not found:", cat)
        self.load_pregnancy(game.clan)

        # assigning a symbol, since this save would be too old to have a chosen symbol
        game.clan.chosen_symbol = clan_symbol_sprite(game.clan, return_string=True)

        game.switches["error_message"] = ""

    def load_clan_json(self):
        """
        TODO: DOCS
        """
        other_clans = []
        if game.switches["clan_list"] == "":
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return
        if game.switches["clan_list"][0].strip() == "":
            number_other_clans = randint(3, 5)
            for _ in range(number_other_clans):
                self.all_clans.append(OtherClan())
            return

        game.switches["error_message"] = "There was an error loading the clan.json"
        with open(
            get_save_dir() + "/" + game.switches["clan_list"][0] + "clan.json",
            "r",
            encoding="utf-8",
        ) as read_file:  # pylint: disable=redefined-outer-name
            clan_data = ujson.loads(read_file.read())

        if clan_data["leader"]:
            leader = Cat.all_cats[clan_data["leader"]]
            leader_lives = clan_data["leader_lives"]
        else:
            leader = None
            leader_lives = 0

        if clan_data["deputy"]:
            deputy = Cat.all_cats[clan_data["deputy"]]
        else:
            deputy = None

        if clan_data["med_cat"]:
            med_cat = Cat.all_cats[clan_data["med_cat"]]
        else:
            med_cat = None

        game.clan = Clan(
            name=clan_data["clanname"],
            leader=leader,
            deputy=deputy,
            medicine_cat=med_cat,
            biome=clan_data["biome"],
            camp_bg=clan_data["camp_bg"],
            game_mode=clan_data["gamemode"],
            self_run_init_functions=False,
        )
        game.clan.post_initialization_functions()

        game.clan.reputation = int(clan_data["reputation"])

        game.clan.age = clan_data["clanage"]
        game.clan.starting_season = (
            clan_data["starting_season"]
            if "starting_season" in clan_data
            else "Newleaf"
        )
        get_current_season()

        game.clan.leader_lives = leader_lives
        game.clan.leader_predecessors = clan_data["leader_predecessors"]

        game.clan.deputy_predecessors = clan_data["deputy_predecessors"]
        game.clan.med_cat_predecessors = clan_data["med_cat_predecessors"]
        game.clan.med_cat_number = clan_data["med_cat_number"]
        # Allows for the custom pronouns to show up in the add pronoun list after the game has closed and reopened.
        if "custom_pronouns" in clan_data.keys():
            if clan_data["custom_pronouns"]:
                if isinstance(clan_data["custom_pronouns"], list):
                    # english-only pronouns from an old version
                    game.clan.custom_pronouns["en"] = clan_data["custom_pronouns"]
                else:
                    game.clan.custom_pronouns = clan_data["custom_pronouns"]

        # Instructor Info
        if clan_data["instructor"] in Cat.all_cats:
            game.clan.instructor = Cat.all_cats[clan_data["instructor"]]
            game.clan.add_cat(game.clan.instructor)
        else:
            game.clan.instructor = Cat(status=choice(["warrior", "warrior", "elder"]))
            # update_sprite(game.clan.instructor)
            game.clan.instructor.dead = True
            game.clan.add_cat(game.clan.instructor)

        # check for symbol
        if "clan_symbol" in clan_data:
            game.clan.chosen_symbol = clan_data["clan_symbol"]
        else:
            game.clan.chosen_symbol = clan_symbol_sprite(game.clan, return_string=True)

        if "other_clans" in clan_data:
            for other_clan in clan_data["other_clans"]:
                game.clan.all_clans.append(
                    OtherClan(
                        other_clan["name"],
                        int(other_clan["relations"]),
                        other_clan["temperament"],
                        other_clan["chosen_symbol"],
                    )
                )
        else:
            if "other_clan_chosen_symbol" not in clan_data:
                for name, relation, temper in zip(
                    clan_data["other_clans_names"].split(","),
                    clan_data["other_clans_relations"].split(","),
                    clan_data["other_clan_temperament"].split(","),
                ):
                    game.clan.all_clans.append(OtherClan(name, int(relation), temper))
            else:
                for name, relation, temper, symbol in zip(
                    clan_data["other_clans_names"].split(","),
                    clan_data["other_clans_relations"].split(","),
                    clan_data["other_clan_temperament"].split(","),
                    clan_data["other_clan_chosen_symbol"].split(","),
                ):
                    game.clan.all_clans.append(
                        OtherClan(name, int(relation), temper, symbol)
                    )

        for cat in clan_data["clan_cats"].split(","):
            if cat in Cat.all_cats:
                game.clan.add_cat(Cat.all_cats[cat])
                game.clan.add_to_starclan(Cat.all_cats[cat])
                game.clan.add_to_darkforest(Cat.all_cats[cat])
                game.clan.add_to_unknown(Cat.all_cats[cat])
            else:
                print("WARNING: Cat not found:", cat)
        if "war" in clan_data:
            game.clan.war = clan_data["war"]

        if "faded_cats" in clan_data:
            if clan_data["faded_cats"].strip():  # Check for empty string
                for cat in clan_data["faded_cats"].split(","):
                    game.clan.faded_ids.append(cat)

        game.clan.last_focus_change = clan_data.get("last_focus_change")
        game.clan.clans_in_focus = clan_data.get("clans_in_focus", [])

        # Patrolled cats
        if "patrolled_cats" in clan_data:
            game.patrolled = clan_data["patrolled_cats"]

        # Mediated flag
        if "mediated" in clan_data:
            if not isinstance(clan_data["mediated"], list):
                game.mediated = []
            else:
                game.mediated = clan_data["mediated"]

        self.load_pregnancy(game.clan)
        self.load_herb_supply(game.clan)
        self.load_disaster(game.clan)
        if game.clan.game_mode != "classic":
            self.load_freshkill_pile(game.clan)
        game.switches["error_message"] = ""

        # Return Version Info.
        return {
            "version_name": clan_data.get("version_name"),
            "version_commit": clan_data.get("version_commit"),
            "source_build": clan_data.get("source_build"),
        }

    def load_clan_settings(self):
        if os.path.exists(
            get_save_dir() + f'/{game.switches["clan_list"][0]}/clan_settings.json'
        ):
            with open(
                get_save_dir() + f'/{game.switches["clan_list"][0]}/clan_settings.json',
                "r",
                encoding="utf-8",
            ) as write_file:
                _load_settings = ujson.loads(write_file.read())

        for key, value in _load_settings.items():
            if key in self.clan_settings:
                self.clan_settings[key] = value

    def load_pregnancy(self, clan):
        """
        Load the information about what cat is pregnant and in what 'state' they are in the pregnancy.
        """
        if not game.clan.name:
            return
        file_path = get_save_dir() + f"/{game.clan.name}/pregnancy.json"
        if os.path.exists(file_path):
            with open(
                file_path, "r", encoding="utf-8"
            ) as read_file:  # pylint: disable=redefined-outer-name
                clan.pregnancy_data = ujson.load(read_file)
        else:
            clan.pregnancy_data = {}

    def save_pregnancy(self, clan):
        """
        Save the information about what cat is pregnant and in what 'state' they are in the pregnancy.
        """
        if not game.clan.name:
            return

        game.safe_save(
            f"{get_save_dir()}/{game.clan.name}/pregnancy.json", clan.pregnancy_data
        )

    def load_disaster(self, clan):
        """
        TODO: DOCS
        """
        if not game.clan.name:
            return

        file_path = get_save_dir() + f"/{game.clan.name}/disasters/primary.json"
        try:
            if os.path.exists(file_path):
                with open(
                    file_path, "r", encoding="utf-8"
                ) as read_file:  # pylint: disable=redefined-outer-name
                    disaster = ujson.load(read_file)
                    if disaster:
                        clan.primary_disaster = OngoingEvent(
                            event=disaster["event"],
                            tags=disaster["tags"],
                            duration=disaster["duration"],
                            current_duration=(
                                disaster["current_duration"]
                                if "current_duration"
                                else disaster["duration"]
                            ),  # pylint: disable=using-constant-test
                            trigger_events=disaster["trigger_events"],
                            progress_events=disaster["progress_events"],
                            conclusion_events=disaster["conclusion_events"],
                            secondary_disasters=disaster["secondary_disasters"],
                            collateral_damage=disaster["collateral_damage"],
                        )
                    else:
                        clan.primary_disaster = {}
            else:
                os.makedirs(get_save_dir() + f"/{game.clan.name}/disasters")
                clan.primary_disaster = None
                with open(file_path, "w", encoding="utf-8") as rel_file:
                    json_string = ujson.dumps(clan.primary_disaster, indent=4)
                    rel_file.write(json_string)
        except:
            clan.primary_disaster = None

        file_path = get_save_dir() + f"/{game.clan.name}/disasters/secondary.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as read_file:
                    disaster = ujson.load(read_file)
                    if disaster:
                        clan.secondary_disaster = OngoingEvent(
                            event=disaster["event"],
                            tags=disaster["tags"],
                            duration=disaster["duration"],
                            current_duration=(
                                disaster["current_duration"]
                                if "current_duration"
                                else disaster["duration"]
                            ),  # pylint: disable=using-constant-test
                            progress_events=disaster["progress_events"],
                            conclusion_events=disaster["conclusion_events"],
                            collateral_damage=disaster["collateral_damage"],
                        )
                    else:
                        clan.secondary_disaster = {}
            else:
                os.makedirs(get_save_dir() + f"/{game.clan.name}/disasters")
                clan.secondary_disaster = None
                with open(file_path, "w", encoding="utf-8") as rel_file:
                    json_string = ujson.dumps(clan.secondary_disaster, indent=4)
                    rel_file.write(json_string)

        except:
            clan.secondary_disaster = None

    def save_disaster(self, clan=game.clan):
        """
        TODO: DOCS
        """
        if not clan.name:
            return
        file_path = get_save_dir() + f"/{clan.name}/disasters/primary.json"
        if not os.path.isdir(f"{get_save_dir()}/{clan.name}/disasters"):
            os.mkdir(f"{get_save_dir()}/{clan.name}/disasters")
        if clan.primary_disaster:
            disaster = {
                "event": clan.primary_disaster.event,
                "tags": clan.primary_disaster.tags,
                "duration": clan.primary_disaster.duration,
                "current_duration": clan.primary_disaster.current_duration,
                "trigger_events": clan.primary_disaster.trigger_events,
                "progress_events": clan.primary_disaster.progress_events,
                "conclusion_events": clan.primary_disaster.conclusion_events,
                "secondary_disasters": clan.primary_disaster.secondary_disasters,
                "collateral_damage": clan.primary_disaster.collateral_damage,
            }
        else:
            disaster = {}

        game.safe_save(f"{get_save_dir()}/{clan.name}/disasters/primary.json", disaster)

        if clan.secondary_disaster:
            disaster = {
                "event": clan.secondary_disaster.event,
                "tags": clan.secondary_disaster.tags,
                "duration": clan.secondary_disaster.duration,
                "current_duration": clan.secondary_disaster.current_duration,
                "trigger_events": clan.secondary_disaster.trigger_events,
                "progress_events": clan.secondary_disaster.progress_events,
                "conclusion_events": clan.secondary_disaster.conclusion_events,
                "secondary_disasters": clan.secondary_disaster.secondary_disasters,
                "collateral_damage": clan.secondary_disaster.collateral_damage,
            }
        else:
            disaster = {}

        game.safe_save(
            f"{get_save_dir()}/{clan.name}/disasters/secondary.json", disaster
        )

    def load_herb_supply(self, clan):
        """
        Loads the Clan's saved herb supply info
        """
        if not game.clan.name:
            return

        save_dir = get_save_dir()

        current_file_path = save_dir + f"/{game.clan.name}/herb_supply.json"
        old_file_path = save_dir + f"/{game.clan.name}/herbs.json"

        try:
            # load the old file path and convert the save data into current format
            if os.path.exists(old_file_path):
                with open(
                    old_file_path, "r", encoding="utf-8"
                ) as save_file:
                    herbs = ujson.load(save_file)
                    clan.herb_supply = HerbSupply()
                    clan.herb_supply.convert_old_save(herbs)

            # load the current file path, if it exists in save
            elif os.path.exists(current_file_path):
                with open(
                    current_file_path, "r", encoding="utf-8"
                ) as save_file:
                    herbs = ujson.load(save_file)
                    clan.herb_supply = HerbSupply(herb_supply=herbs["storage"])
                    clan.herb_supply.collected = herbs["collected"]

            # else just start us with an empty herb supply
            else:
                clan.herb_supply = HerbSupply()
            clan.herb_supply.required_herb_count = get_living_clan_cat_count(Cat) * 2
        except:
            clan.herb_supply = HerbSupply()

    def save_herb_supply(self, clan):
        """
        saves the Clan's current herb supply
        """
        if not clan.herb_supply:
            return

        game.safe_save(
            f"{get_save_dir()}/{game.clan.name}/herb_supply.json",
            clan.herb_supply.combined_supply_dict
        )

        # delete old herb save file if it exists
        if os.path.exists(get_save_dir() + f"/{game.clan.name}/herbs.json"):
            os.remove(get_save_dir() + f"/{game.clan.name}/herbs.json")


    def load_freshkill_pile(self, clan):
        """
        TODO: DOCS
        """
        if not game.clan.name or clan.game_mode == "classic":
            return

        file_path = get_save_dir() + f"/{game.clan.name}/freshkill_pile.json"
        try:
            if os.path.exists(file_path):
                with open(
                    file_path, "r", encoding="utf-8"
                ) as read_file:  # pylint: disable=redefined-outer-name
                    pile = ujson.load(read_file)
                    clan.freshkill_pile = FreshkillPile(pile)

                file_path = get_save_dir() + f"/{game.clan.name}/nutrition_info.json"
                if os.path.exists(file_path) and clan.freshkill_pile:
                    with open(file_path, "r", encoding="utf-8") as read_file:
                        nutritions = ujson.load(read_file)
                        for k, nutr in nutritions.items():
                            nutrition = Nutrition()
                            nutrition.max_score = nutr["max_score"]
                            nutrition.current_score = nutr["current_score"]
                            clan.freshkill_pile.nutrition_info[k] = nutrition
                        if len(nutritions) <= 0:
                            for cat in Cat.all_cats_list:
                                clan.freshkill_pile.add_cat_to_nutrition(cat)
            else:
                clan.freshkill_pile = FreshkillPile()
        except:
            clan.freshkill_pile = FreshkillPile()

    def save_freshkill_pile(self, clan):
        """
        TODO: DOCS
        """
        if clan.game_mode == "classic" or not clan.freshkill_pile:
            return

        game.safe_save(
            f"{get_save_dir()}/{game.clan.name}/freshkill_pile.json",
            clan.freshkill_pile.pile,
        )

        data = {}
        for k, nutr in clan.freshkill_pile.nutrition_info.items():
            data[k] = {
                "max_score": nutr.max_score,
                "current_score": nutr.current_score,
                "percentage": nutr.percentage,
            }

        game.safe_save(f"{get_save_dir()}/{game.clan.name}/nutrition_info.json", data)

    ## Properties

    @property
    def reputation(self):
        return self._reputation

    @reputation.setter
    def reputation(self, a: int):
        self._reputation = int(a)
        if self._reputation > 100:
            self._reputation = 100
        elif self._reputation < 0:
            self._reputation = 0

    @property
    def temperament(self):
        """Temperament is determined whenever it's accessed. This makes sure it's always accurate to the
        current cats in the Clan. However, determining Clan temperament is slow!
        Clan temperament should be used as sparsely as possible, since
        it's pretty resource-intensive to determine it."""

        all_cats = [
            i
            for i in Cat.all_cats_list
            if i.status not in ["leader", "deputy"] and not i.dead and not i.outside
        ]
        leader = (
            Cat.fetch_cat(self.leader)
            if isinstance(Cat.fetch_cat(self.leader), Cat)
            else None
        )
        deputy = (
            Cat.fetch_cat(self.deputy)
            if isinstance(Cat.fetch_cat(self.deputy), Cat)
            else None
        )

        weight = 0.3

        if (leader or deputy) and all_cats:
            clan_sociability = round(
                weight
                * statistics.mean(
                    [i.personality.sociability for i in [leader, deputy] if i]
                )
                + (1 - weight)
                * statistics.median([i.personality.sociability for i in all_cats])
            )
            clan_aggression = round(
                weight
                * statistics.mean(
                    [i.personality.aggression for i in [leader, deputy] if i]
                )
                + (1 - weight)
                * statistics.median([i.personality.aggression for i in all_cats])
            )
        elif leader or deputy:
            clan_sociability = round(
                statistics.mean(
                    [i.personality.sociability for i in [leader, deputy] if i]
                )
            )
            clan_aggression = round(
                statistics.mean(
                    [i.personality.aggression for i in [leader, deputy] if i]
                )
            )
        elif all_cats:
            clan_sociability = round(
                statistics.median([i.personality.sociability for i in all_cats])
            )
            clan_aggression = round(
                statistics.median([i.personality.aggression for i in all_cats])
            )
        else:
            print("returned default temper: stoic")
            return "stoic"

        # _temperament = ['low_aggression', 'med_aggression', 'high_aggression', ]
        if 11 <= clan_sociability:
            _temperament = self.temperament_dict["high_social"]
        elif 7 <= clan_sociability:
            _temperament = self.temperament_dict["mid_social"]
        else:
            _temperament = self.temperament_dict["low_social"]

        if 11 <= clan_aggression:
            _temperament = _temperament[2]
        elif 7 <= clan_aggression:
            _temperament = _temperament[1]
        else:
            _temperament = _temperament[0]

        return _temperament

    @temperament.setter
    def temperament(self, val):
        return


class OtherClan:
    """
    TODO: DOCS
    """

    interaction_dict = {
        "ally": ["offend", "praise"],
        "neutral": ["provoke", "befriend"],
        "hostile": ["antagonize", "appease", "declare"],
    }

    temperament_list = [
        "cunning",
        "wary",
        "logical",
        "proud",
        "stoic",
        "mellow",
        "bloodthirsty",
        "amiable",
        "gracious",
    ]

    def __init__(self, name="", relations=0, temperament="", chosen_symbol=""):
        clan_names = names.names_dict["normal_prefixes"]
        clan_names.extend(names.names_dict["clan_prefixes"])
        self.name = name or choice(clan_names)
        self.relations = relations or randint(8, 12)
        self.temperament = temperament or choice(self.temperament_list)
        if self.temperament not in self.temperament_list:
            self.temperament = choice(self.temperament_list)

        self.chosen_symbol = (
            None  # have to establish None first so that clan_symbol_sprite works
        )
        self.chosen_symbol = (
            chosen_symbol
            if chosen_symbol
            else clan_symbol_sprite(self, return_string=True)
        )

    def __repr__(self):
        return f"{self.name}Clan"


class StarClan:
    """
    TODO: DOCS
    """

    forgotten_stages = {
        0: [0, 100],
        10: [101, 200],
        30: [201, 300],
        60: [301, 400],
        90: [401, 500],
        100: [501, 502],
    }  # Tells how faded the cat will be in StarClan by months spent
    dead_cats = {}

    def __init__(self):
        """
        TODO: DOCS
        """
        self.instructor = None

    def fade(self, cat):
        """
        TODO: DOCS
        """
        white = pygame.Surface((sprites.size, sprites.size))
        fade_level = 0
        if cat.dead:
            for f in self.forgotten_stages:  # pylint: disable=consider-using-dict-items
                if cat.dead_for in range(
                    self.forgotten_stages[f][0], self.forgotten_stages[f][1]
                ):
                    fade_level = f
        white.fill((255, 255, 255, fade_level))
        return white


clan_class = Clan()
clan_class.remove_cat(cat_class.ID)

