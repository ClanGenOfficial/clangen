import os
import platform
import subprocess
from random import choice

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat, BACKSTORIES, create_option_preview_cat
from scripts.cat.pelts import Pelt
from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath
from scripts.events_module.short.condition_events import Condition_Events
from scripts.events_module.short.handle_short_events import HandleShortEvents
from scripts.events_module.short.scar_events import Scar_Events
from scripts.game_structure import image_cache, constants
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import get_default_pronouns
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIModifiedScrollingContainer,
    UITextBoxTweaked,
    UICheckbox,
    UIModifiedImage,
    UIScrollingButtonList,
    UIDropDown,
    UICollapsibleContainer,
    UIScrollingDropDown,
)
from scripts.game_structure.windows import EditorSaveCheck, EditorMissingInfo
from scripts.screens.RelationshipScreen import RelationshipScreen
from scripts.screens.Screens import Screens
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.utility import (
    ui_scale,
    process_text,
    ui_scale_dimensions,
    generate_sprite,
    get_text_box_theme,
)


class EventEditScreen(Screens):
    """
    This screen provides an interface to allow devs to edit and create events.
    """

    with open("resources/dicts/events/tags.json", "r", encoding="utf-8") as read_file:
        TAGS = ujson.loads(read_file.read())

    with open("resources/dicts/events/types.json", "r", encoding="utf-8") as read_file:
        TYPES = ujson.loads(read_file.read())

    test_cat_names: dict = {
        "m_c": "MainCat",
        "r_c": "RandomCat",
        "mur_c": "MurderedCat",
        "lead_name": "TestStar",
        "dep_name": "DepCat",
        "med_name": "MedCat",
        "multi_cat": "DeadCat, PerishedCat, and RipCat",
    }
    """Placeholder names for each possible cat abbreviation."""
    # it's possible to have more than 6 new cats, but doubtful that we'll ever refer to more than 2 within event text
    # either way, this adds 6 new cat abbreviations to our test name dict
    for index in range(5):
        test_cat_names[f"n_c:{index}"] = f"NewCat{index}"

    preview_states: tuple = (0, 1, 2)
    """Possible preview states, 0 (no preview), 1 (plural), 2 (singular)."""

    test_pronouns: list = list(get_default_pronouns().values())
    """Pronoun dicts to assign to our test cats."""

    all_camps: dict = {
        "Forest": ["Classic", "Gully", "Grotto", "Lakeside"],
        "Mountainous": ["Cliff", "Cavern", "Crystal River", "Ruins"],
        "Plains": ["Grasslands", "Tunnels", "Wastelands"],
        "Beach": ["Tidepools", "Tidal Cave", "Shipwreck", "Fjord"],
    }
    """Dict with key as biome and value as camp name."""
    # TODO: when possible, change this to pull this from a global attr
    all_seasons: tuple = ("newleaf", "greenleaf", "leaf-fall", "leaf-bare")
    """Tuple of all seasons possible."""

    event_types: dict = TYPES
    """Dict with key as event type and value as allowed subtypes for that type."""

    basic_tag_list: list = TAGS["settings"]
    """List of dicts for all basic event tags. Each dict holds tag name, conflicts, setting, and type required."""

    rel_tag_list: list = TAGS["relationship"]
    """List of dicts for relationship_values. Each dict holds tag name, conflicts, and setting."""
    rel_value_types: list = RelationshipScreen.rel_value_names
    """List of all relationship values."""

    all_ranks: list = Cat.rank_sort_order.copy()
    """List of all possible ranks from highest to lowest."""
    all_ranks.reverse()

    all_ages: list = [age.value for age in Cat.age_moons.keys()]
    """List of all possible ages from oldest to youngest."""
    all_ages.reverse()

    all_skills: dict = {
        k: v
        for (k, v) in zip(
            [path.name for path in SkillPath], [path.value for path in SkillPath]
        )
    }
    """Dict holding all skill info. Key is skill path, value is list of skill levels."""

    adult_traits: list = Personality.trait_ranges["normal_traits"].keys()
    """List of all adult traits."""
    kit_traits: list = Personality.trait_ranges["kit_traits"].keys()
    """List of all kit traits."""

    all_backstories: dict = BACKSTORIES["backstory_categories"]
    """Dict of all backstory categories. Key is the backstory category and value is the backstories within that 
    category."""
    individual_stories: list = []
    """List of all possible backstories"""

    for pool in all_backstories:
        individual_stories.extend(all_backstories[pool])

    new_cat_types: list = TAGS["new_cat"]["types"]
    """All possible cat types."""

    new_cat_bools: list = TAGS["new_cat"]["bool_settings"]
    """New cat tag list. Holds tag name, setting, and conflicts."""

    new_cat_ranks: list = all_ranks.copy()
    """All ranks available to new cats."""
    for rank in TAGS["new_cat"]["disallowed_ranks"]:
        new_cat_ranks.remove(rank)

    new_cat_ages: list = all_ages.copy()
    """List of all age tags available to new cats."""
    new_cat_ages.extend(TAGS["new_cat"]["special_ages"])

    new_cat_genders: list = TAGS["new_cat"]["genders"]
    """List of all gender tags available to new cats"""

    all_injury_pools: dict = constants.INJURY_GROUPS
    """Dict of all injury pools. Key is pool name, value is the injuries within the pool."""
    all_possible_injuries: list = constants.EVENT_ALLOWED_CONDITIONS
    """List of all possible injuries/conditions."""
    fatal_conditions: list = []
    """We need this for death history validity checking. This is a list of all conditions that can kill."""
    for condition in all_possible_injuries:
        if Condition_Events.INJURIES.get(condition):
            for age in Condition_Events.INJURIES[condition]["mortality"]:
                if Condition_Events.INJURIES[condition]["mortality"][age]:
                    fatal_conditions.append(condition)
                    break
                else:
                    break
        elif Condition_Events.ILLNESSES.get(condition):
            for age in Condition_Events.ILLNESSES[condition]["mortality"]:
                if Condition_Events.ILLNESSES[condition]["mortality"][age]:
                    fatal_conditions.append(condition)
                    break
                else:
                    break

    all_scars: list = Pelt.scars1 + Pelt.scars2 + Pelt.scars3
    """List of all possible scars"""

    all_outsider_reps: list = list(constants.OUTSIDER_REPS)
    """List of all possible outsider reputation levels."""
    all_outsider_reps.append("any")

    all_other_clan_reps: list = list(constants.OTHER_CLAN_REPS)
    """List of all possible other clan relationship levels."""
    all_other_clan_reps.append("any")

    section_tabs: dict = {
        "settings": Icon.PAW,
        "main cat": Icon.CAT_HEAD,
        "random cat": Icon.CAT_HEAD,
        "new cats": Icon.CAT_HEAD,
        "personal consequences": Icon.SCRATCHES,
        "outside consequences": Icon.CLAN_UNKNOWN,
        "future effects": Icon.NOTEPAD,
    }
    """Dict for section tab info. Key is the name of the tab, value is the icon assigned."""

    amount_buttons: dict = {
        "amount_up_low_button": Icon.UP_LOW,
        "amount_up_mid_button": Icon.UP_MID,
        "amount_up_high_button": Icon.UP_HIGH,
        "amount_down_low_button": Icon.DOWN_LOW,
        "amount_down_mid_button": Icon.DOWN_MID,
        "amount_down_high_button": Icon.DOWN_HIGH,
    }
    """Dict for amount button names and icons. Key is the name, value is the icon assigned."""

    def __init__(self, name=None):
        super().__init__(name)
        self.chosen_type: str = ""
        """The type currently viewed in the existing events side bar"""
        self.chosen_biome: str = ""
        """The biome currently viewed in the existing events side bar"""
        self.alert_text: str = ""

        self.event_text_container = None
        self.editor_container = None
        self.add_button = None
        self.event_list_container = None
        self.list_frame = None
        self.main_menu_button = None
        self.event_search = None
        self.search_text = None

        self.event_list: list = []
        """List of loaded existing events"""
        self.all_event_ids: list = []
        """List of all event_ids currently in use. Used to check if newly entered event_id is a duplicate."""
        self.open_event: dict = {}
        """dict for the currently open existing event"""
        self.old_event_path: str = ""
        """If currently open event is an existing event, this holds its original file path."""
        self.old_event_index: int = 0
        """If currently open event is an existing event, this holds its original index within its file"""

        self.current_editor_tab: str = ""
        """The currently viewed editor tab."""

        self.type_tab_buttons = {}
        self.biome_tab_buttons = {}
        self.event_buttons = {}

        self.editor_element = {}
        self.lock_buttons = {}

        self.param_locks: dict = {}
        """Param lock information. Key is the name of the lock, value is bool of the lock."""

        self.current_preview_state: int = self.preview_states[0]
        """The currently used preview state. This can be 0 (preview off), 1 (plural), or 2 (singular)"""

        self.event_text_element = {}
        self.event_text_info: str = ""
        """Loaded event text"""

        self.event_id_element = {}
        self.event_id_info: str = ""
        """Loaded event_id"""

        self.location_element = {}
        self.location_info: list = []
        """Loaded location tags"""

        self.season_element = {}
        self.season_info: list = []
        """Loaded season tags"""

        self.type_element = {}
        self.type_info: list = ["death"]
        """Loaded type, kept in a list for ease of use with it's dropdown, but there should only ever be one type"""

        self.sub_element = {}
        self.sub_info: list = []
        """Loaded subtypes"""

        self.tag_element = {}
        self.basic_tag_checkbox = {}
        self.rank_tag_checkbox = {}
        self.tag_info: list = []
        """Loaded tags"""

        self.weight_element = {}
        self.weight_info: int = 20
        """Loaded weight"""

        self.acc_element = {}
        self.acc_button = {}
        self.acc_info: list = []
        """Loaded accessory tags"""
        self.acc_categories = Pelt.acc_categories
        self.open_category: str = ""
        """Currently open acc category (wild, collar, ect.)"""

        self.main_cat_editor = {}
        self.random_cat_editor = {}

        self.death_element = {}
        self.rank_element = {}
        self.age_element = {}

        self.rel_status_element = {}
        self.rel_status_checkbox = {}
        self.rel_value_element = {}

        self.skill_element = {}
        self.level_element = {}
        self.skill_allowed: bool = True
        """True if 'skill' is being assigned, False if 'not_skill' is being assigned"""
        self.open_path: str = ""
        """The skill path that is determining the skills that display"""
        self.chosen_level: str = ""
        """The skill last clicked by the user"""

        self.trait_element = {}
        self.trait_allowed: bool = True
        """True if 'trait' is being assigned, False if 'not_trait' is being assigned"""

        self.backstory_element = {}
        self.open_pool: str = ""
        """The backstory category that is determining the backstories that display"""

        self.main_cat_info: dict = {
            "rank": [],
            "age": [],
            "rel_status": [],
            "dies": False,
            "skill": [],
            "not_skill": [],
            "trait": [],
            "not_trait": [],
            "backstory": [],
        }
        """The main cat's loaded information"""

        self.random_cat_info: dict = {
            "rank": [],
            "age": [],
            "rel_status": [],
            "dies": False,
            "skill": [],
            "not_skill": [],
            "trait": [],
            "not_trait": [],
            "backstory": [],
        }
        """The random cat's loaded information"""

        self.selected_new_cat_info: dict = {}
        """The loaded backstory/parent/adoptive/mate information for the currently open new_cat block"""

        self.current_cat_dict: dict = self.main_cat_info
        """The info dict for the currently loaded cat, this changes depending on the currently open tab"""

        self.new_cat_template: dict = {
            "backstory": [],
            "parent": [],
            "adoptive": [],
            "mate": [],
        }
        """The new cat info *template*, this should not hold the open new_cat's information."""

        self.new_cat_block_dict: dict = {}
        """A dict holding every new_cat block's tag list, key is the new_cat's abbr (i.e. n_c:0) and value is that cat's
         tag list"""
        self.selected_new_cat: str = ""
        """The new cat currently being viewed by the user"""

        self.new_cat_editor = {}
        self.new_cat_element = {}
        self.new_cat_checkbox = {}
        self.cat_story_element = {}
        self.new_status_element = {}
        self.new_age_element = {}
        self.new_gender_element = {}
        self.connections_element = {}

        self.open_connection: str = "parent"
        """The connection tab (parent/adoptive/mate) currently viewed by the user"""

        self.exclusion_element = {}
        self.excluded_cats: list = []
        """The loaded excluded cats"""

        self.open_block: str = "injury"
        """The block list currently viewed by the user"""
        self.injury_element = {}
        self.injury_block_list: list = []
        """The list of currently loaded injury blocks"""
        self.injury_template: dict = {"cats": [], "injuries": [], "scars": []}
        """The template for the injury block info"""
        self.selected_injury_block: str = ""
        """The list index for the injury block currently viewed by the user. This is kept as a string due to it doubling
         as the text for its button."""

        self.history_element = {}
        self.history_block_list: list = []
        """The list of currently loaded history blocks"""
        self.history_template: dict = {
            "cats": [],
            "scar": "",
            "reg_death": "",
            "lead_death": "",
        }
        """The template for the history block info"""
        self.selected_history_block_index: str = ""
        """The list index for the history block currently viewed by the user. This is kept as a string due to it doubling
             as the text for its button."""

        self.relationships_element = {}
        self.relationships_block_list: list = []
        """The list of currently loaded relationships blocks"""
        self.relationships_template: dict = {
            "cats_from": [],
            "cats_to": [],
            "mutual": False,
            "values": [],
            "amount": 0,
        }
        """The template for the relationships block info"""
        self.selected_relationships_block_index: str = ""
        """The list index for the relationships block currently viewed by the user. This is kept as a string due to it doubling
             as the text for its button."""

        self.outsider_element = {}
        self.outsider_info: dict = {"current_rep": [], "changed": 0}
        """The currently loaded outsider info"""

        self.other_clan_element = {}
        self.other_clan_info: dict = {"current_rep": [], "changed": 0}
        """The currently loaded other clan info"""

        self.supply_element = {}
        self.supply_block_list: list = []
        """The list of the currently loaded supply blocks"""
        self.selected_supply_block_index: str = ""
        """The list index for the supply block currently viewed by the user. This is kept as a string due to it doubling
             as the text for its button."""
        self.supply_info: dict = {"type": "", "trigger": [], "adjust": ""}
        """The info for the currently viewed supply block"""

        self.future_element = {}
        self.future_block_list: list = []
        """The list of currently loaded future blocks"""
        self.selected_future_block_index: str = ""
        """The list index for the future block currently viewed by the user. This is kept as a string due to it doubling
             as the text for its button."""
        self.future_template: dict = {
            "event_type": "death",
            "pool": {
                "subtype": [],
                "event_id": [],
                "excluded_event_id": [],
            },
            "moon_delay": [1, 1],
            "involved_cats": {"m_c": None, "r_c": None},
        }
        """The template for the future block info"""
        self.future_cat_info_template: dict = {
            "rank": [],
            "age": [],
            "skill": [],
            "not_skill": [],
            "trait": [],
            "not_trait": [],
        }
        """The template for an uninvolved cat's info."""
        self.available_cats: list = []
        """List of cats who are available to be in the future event."""

    # EVENT JSON PROCESSING
    def unpack_existing_event(self, event: dict):
        """
        Takes the dict of an existing event and assigns its information to necessary attributes. Also finds the old
        file path for that event and saves it for later.
        """
        self.open_event = event.copy()
        biome = "general"
        matching_biomes = []
        for location in event.get("location"):
            for biome in constants.BIOME_TYPES:
                if biome.casefold() in location:
                    matching_biomes.append(biome)
        if len(matching_biomes) <= 1:
            biome = matching_biomes[0] if matching_biomes else "general"

        if not self.chosen_type:
            for name in self.event_types.keys():
                if name in event["event_id"]:
                    self.chosen_type = name
        self.old_event_path = (
            f"resources/lang/en/events/{self.chosen_type}/{biome.casefold()}.json"
        )

        self.type_info = [self.chosen_type]
        self.event_id_info = event["event_id"]
        self.location_info = event["location"] if event.get("location") else []
        if self.location_info == ["any"]:
            self.location_info = []
        self.season_info = event["season"] if event.get("season") else []
        if self.season_info == ["any"]:
            self.season_info = []
        self.sub_info = event["sub_type"] if event.get("sub_type") else []
        self.tag_info = event["tags"] if event.get("tags") else []
        self.weight_info = event["weight"]
        self.event_text_info = event["event_text"]
        self.acc_info = event["new_accessory"] if event.get("new_accessory") else []
        if event.get("m_c"):
            self.main_cat_info = {
                "rank": event["m_c"]["status"] if event["m_c"].get("status") else [],
                "age": event["m_c"]["age"] if event["m_c"].get("age") else [],
                "rel_status": event["m_c"]["relationship_status"]
                if event["m_c"].get("relationship_status")
                else [],
                "dies": event["m_c"]["dies"] if event["m_c"].get("dies") else False,
                "skill": event["m_c"]["skill"] if event["m_c"].get("skill") else [],
                "not_skill": event["m_c"]["not_skill"]
                if event["m_c"].get("not_skill")
                else [],
                "trait": event["m_c"]["trait"] if event["m_c"].get("trait") else [],
                "not_trait": event["m_c"]["not_trait"]
                if event["m_c"].get("not_trait")
                else [],
                "backstory": event["m_c"]["backstory"]
                if event["m_c"].get("backstory")
                else [],
            }
        if event.get("r_c"):
            self.random_cat_info = {
                "rank": event["r_c"]["status"] if event["r_c"].get("status") else [],
                "age": event["r_c"]["age"] if event["r_c"].get("age") else [],
                "rel_status": event["r_c"]["relationship_status"]
                if event["r_c"].get("relationship_status")
                else [],
                "dies": event["r_c"]["dies"] if event["r_c"].get("dies") else False,
                "skill": event["r_c"]["skill"] if event["r_c"].get("skill") else [],
                "not_skill": event["r_c"]["not_skill"]
                if event["r_c"].get("not_skill")
                else [],
                "trait": event["r_c"]["trait"] if event["r_c"].get("trait") else [],
                "not_trait": event["r_c"]["not_trait"]
                if event["r_c"].get("not_trait")
                else [],
                "backstory": event["r_c"]["backstory"]
                if event["r_c"].get("backstory")
                else [],
            }
        if event.get("new_cat"):
            names = [f"n_c:{index}" for index in range(len(event["new_cat"]))]
            self.new_cat_block_dict = {k: v for (k, v) in zip(names, event["new_cat"])}
        else:
            self.new_cat_block_dict = {}
        self.injury_block_list = event["injury"] if event.get("injury") else []
        for block in self.injury_block_list:
            if "injuries" not in block:
                block["injuries"] = []
            if "scars" not in block:
                block["scars"] = []
        self.excluded_cats = (
            event["exclude_involved"] if event.get("exclude_involved") else []
        )
        self.history_block_list = event["history"] if event.get("history") else []
        for block in self.history_block_list:
            if "scar" not in block:
                block["scar"] = ""
            if "reg_death" not in block:
                block["reg_death"] = ""
            if "lead_death" not in block:
                block["lead_death"] = ""
        self.relationships_block_list = (
            event["relationships"] if event.get("relationships") else []
        )
        for block in self.relationships_block_list:
            if "mutual" not in block:
                block["mutual"] = False
        self.outsider_info = (
            event["outsider"] if event.get("outsider") else self.outsider_info
        )
        self.other_clan_info = (
            event["other_clan"] if event.get("other_clan") else self.other_clan_info
        )
        if not "current_rep" in self.other_clan_info:
            self.other_clan_info["current_rep"] = None
        if not "changed" in self.other_clan_info:
            self.other_clan_info["changed"] = 0
        self.supply_block_list = event["supplies"] if event.get("supplies") else []
        self.future_block_list = (
            event["future_event"] if event.get("future_event") else []
        )

    def compile_new_event(self) -> dict:
        """
        Compiles all information for created/edited event into an event dict to return.
        """
        new_event = {"event_id": self.event_id_info}
        if self.location_info:
            new_event["location"] = self.location_info
        else:
            new_event["location"] = ["any"]
        if self.season_info:
            new_event["season"] = self.season_info
        else:
            new_event["season"] = ["any"]
        if self.sub_info:
            new_event["sub_type"] = self.sub_info
        if self.tag_info:
            new_event["tags"] = self.tag_info

        new_event["weight"] = self.weight_info
        new_event["event_text"] = self.event_text_info

        if self.acc_info:
            new_event["new_accessory"] = self.acc_info

        new_event["m_c"] = {}
        if self.main_cat_info["age"]:
            new_event["m_c"]["age"] = self.main_cat_info["age"]
        if self.main_cat_info["rank"]:
            new_event["m_c"]["status"] = self.main_cat_info["rank"]
        if self.main_cat_info["rel_status"]:
            new_event["m_c"]["relationship_status"] = self.main_cat_info["rel_status"]
        if self.main_cat_info["skill"]:
            new_event["m_c"]["skill"] = self.main_cat_info["skill"]
        if self.main_cat_info["not_skill"]:
            new_event["m_c"]["not_skill"] = self.main_cat_info["not_skill"]
        if self.main_cat_info["trait"]:
            new_event["m_c"]["trait"] = self.main_cat_info["trait"]
        if self.main_cat_info["not_trait"]:
            new_event["m_c"]["not_trait"] = self.main_cat_info["not_trait"]
        if self.main_cat_info["backstory"]:
            new_event["m_c"]["backstory"] = self.main_cat_info["backstory"]
        if self.main_cat_info["dies"]:
            new_event["m_c"]["dies"] = self.main_cat_info["dies"]

        new_event["r_c"] = {}
        if self.random_cat_info["age"]:
            new_event["r_c"]["age"] = self.random_cat_info["age"]
        if self.random_cat_info["rank"]:
            new_event["r_c"]["status"] = self.random_cat_info["rank"]
        if self.random_cat_info["rel_status"]:
            new_event["r_c"]["relationship_status"] = self.random_cat_info["rel_status"]
        if self.random_cat_info["skill"]:
            new_event["r_c"]["skill"] = self.random_cat_info["skill"]
        if self.random_cat_info["not_skill"]:
            new_event["r_c"]["not_skill"] = self.random_cat_info["not_skill"]
        if self.random_cat_info["trait"]:
            new_event["r_c"]["trait"] = self.random_cat_info["trait"]
        if self.random_cat_info["not_trait"]:
            new_event["r_c"]["not_trait"] = self.random_cat_info["not_trait"]
        if self.random_cat_info["backstory"]:
            new_event["r_c"]["backstory"] = self.random_cat_info["backstory"]
        if self.random_cat_info["dies"]:
            new_event["r_c"]["dies"] = self.random_cat_info["dies"]
        if not new_event["r_c"]:
            new_event.pop("r_c")

        if self.new_cat_block_dict:
            new_event["new_cat"] = list(self.new_cat_block_dict.values())

        if self.injury_block_list:
            for block in self.injury_block_list:
                if not block["scars"]:
                    block.pop("scars")
            new_event["injury"] = self.injury_block_list

        if self.excluded_cats:
            new_event["exclude_involved"] = self.excluded_cats

        if self.history_block_list:
            for block in self.history_block_list:
                if not block["scar"]:
                    block.pop("scar")
                if not block["reg_death"]:
                    block.pop("reg_death")
                if not block["lead_death"]:
                    block.pop("lead_death")
            new_event["history"] = self.history_block_list

        if self.relationships_block_list:
            new_event["relationships"] = self.relationships_block_list

        if self.outsider_info["current_rep"] or self.outsider_info["changed"]:
            new_event["outsider"] = {}
            if self.outsider_info["current_rep"]:
                new_event["current_rep"] = self.outsider_info["current_rep"]
            if self.outsider_info["changed"]:
                new_event["changed"] = int(self.outsider_info["changed"])

        if self.other_clan_info["current_rep"] or self.other_clan_info["changed"]:
            new_event["other_clan"] = {}
            if self.other_clan_info["current_rep"]:
                new_event["current_rep"] = self.other_clan_info["current_rep"]
            if self.other_clan_info["changed"]:
                new_event["changed"] = int(self.other_clan_info["changed"])

        if self.supply_block_list:
            new_event["supplies"] = self.supply_block_list

        if self.future_block_list:
            new_event["future_event"] = self.future_block_list
            for block in self.future_block_list:
                for cat in block["involved_cats"]:
                    if block["involved_cats"][cat] == "new random cat":
                        block["involved_cats"][cat] = None

        return new_event

    def find_event_path(self) -> str:
        """Finds and returns the best file path based off of current editor info."""

        type = self.type_info[0]
        biomes = []
        biome_path = "general"
        for locale in self.location_info:
            biome = locale.split("_")[0]
            if biome.capitalize() in constants.BIOME_TYPES:
                biomes.append(biome)
        if len(biomes) == 1 and "any" not in biomes:
            biome_path = biomes[0]

        return f"resources/lang/en/events/{type}/{biome_path}.json"

    def get_event_json(self, path: str) -> list:
        """
        Loads the event json information for the given file path and returns it as a list.
        """
        event_list = []

        try:
            with open(path, "r", encoding="utf-8") as read_file:
                events = read_file.read()
                event_list = ujson.loads(events)
        except:
            print(f"Something went wrong with event loading. Is {path} valid?")

        if not event_list and self.editor_element.get("intro_text"):
            self.editor_element["intro_text"].set_text(
                "screens.event_edit.empty_event_list"
            )
            return []

        try:
            if event_list and not isinstance(event_list[0], dict):
                print(
                    f"{path} isn't in the correct event format. Perhaps it isn't an event .json?"
                )
        except KeyError:
            return []

        return event_list

    # USER EVENT HANDLING
    def handle_event(self, event):
        # HANDLE TEXT LINKS
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", "-u", event.link_target])
            elif platform.system() == "Windows":
                os.system(f'start "" {event.link_target}')
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", event.link_target])

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # SEARCHING
            if self.event_search.is_focused:
                self.search_text = self.event_search.get_text()
                self.create_event_display(
                    event_type=self.chosen_type, biome=self.chosen_biome
                )
            # FUTURE EVENT IDS
            if self.current_editor_tab == "future effects":
                self.handle_future_event_ids()

        # HOVER PREVIEWS
        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if (
                self.injury_element.get("scar_list")
                and event.ui_element
                in self.injury_element["scar_list"].buttons.values()
            ):
                for name, button in self.injury_element["scar_list"].buttons.items():
                    if button == event.ui_element:
                        self.injury_element["scar_preview"].set_image(
                            self.get_scar_example(name)
                        )
                        break
            if (
                self.acc_element.get("list")
                and event.ui_element in self.acc_element["list"].buttons.values()
            ):
                for name, button in self.acc_element["list"].buttons.items():
                    if button == event.ui_element:
                        self.acc_element["preview"].set_image(
                            self.get_acc_example(name)
                        )
                        break

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            # MAIN MENU RETURN
            if event.ui_element == self.main_menu_button:
                self.change_screen("start screen")
                return

            # SELECT TYPE
            elif event.ui_element in self.type_tab_buttons.values():
                for tab in self.type_tab_buttons:
                    if event.ui_element == self.type_tab_buttons[tab]:
                        self.chosen_type = tab
                        break
                self.create_event_display(event_type=self.chosen_type)

                self.select_biome_tab_creation()

            # SELECT BIOME
            elif event.ui_element in self.biome_tab_buttons.values():
                if event.ui_element == self.biome_tab_buttons["back"]:
                    self.select_type_tab_creation()
                    self.chosen_biome = None
                    self.chosen_type = None
                    self.create_event_display(event_type=self.chosen_type)

                else:
                    for tab in self.biome_tab_buttons:
                        if event.ui_element == self.biome_tab_buttons[tab]:
                            self.chosen_biome = (
                                tab.capitalize() if tab != "general" else tab
                            )
                            break

                    self.create_event_display(
                        event_type=self.chosen_type, biome=self.chosen_biome
                    )

            # SELECT EVENT
            elif event.ui_element in self.event_buttons.values():
                for index, button in self.event_buttons.items():
                    if button == event.ui_element:
                        self.param_locks.clear()
                        game.event_editing = True
                        self.clear_event_info()
                        opened_event: dict = self.event_list[index]

                        # unpacking into class attr
                        self.unpack_existing_event(opened_event)

                        # collecting old information to compare when saving
                        self.old_event_path = self.find_event_path()
                        old_json = self.get_event_json(self.old_event_path)
                        for ev in old_json:
                            if ev["event_id"] == opened_event["event_id"]:
                                self.old_event_index = old_json.index(ev)

                        if not self.current_editor_tab:
                            self.current_editor_tab = "settings"
                        self.clear_editor_tab()
                        if self.editor_element.get("save"):
                            self.editor_element["save"].set_text("buttons.save")
                        break

            # OPEN EDITOR
            elif event.ui_element == self.add_button:
                self.current_editor_tab = "settings"
                self.open_event = {}
                self.old_event_index = None
                self.clear_event_info()
                self.clear_editor_tab()

            # PARAM LOCKS
            elif event.ui_element in self.lock_buttons.values():
                for name, button in self.lock_buttons.items():
                    if button != event.ui_element:
                        continue
                    if button.text == Icon.UNLOCK:
                        button.set_text(Icon.LOCK)
                        self.param_locks[name] = True
                    elif button.text == Icon.LOCK:
                        button.set_text(Icon.UNLOCK)
                        self.param_locks[name] = False

            elif event.ui_element in self.editor_element.values():
                # SAVE NEW EVENT
                if event.ui_element == self.editor_element["save"]:
                    self.event_text_info = self.event_text_element[
                        "event_text"
                    ].html_text
                    # check validity of event first
                    if (
                        not self.event_text_info
                        or not self.weight_info
                        or not self.type_info
                        or not self.valid_id()
                        or not self.valid_injury()
                        or not self.valid_history()
                        or not self.valid_relationships()
                        or not self.valid_supply()
                        or not self.valid_future()
                    ):
                        EditorMissingInfo(self.alert_text)
                    # if it's all good, SAVE!
                    else:
                        new_event = self.compile_new_event()
                        path = self.find_event_path()
                        event_list = self.get_event_json(path)
                        old_event_file = None
                        if self.open_event:
                            if self.old_event_path != path:
                                old_event_file = self.get_event_json(
                                    self.old_event_path
                                )
                                old_event_file.pop(self.old_event_index)
                                event_list.append(new_event)
                            else:
                                event_list.pop(self.old_event_index)
                                event_list.insert(self.old_event_index, new_event)
                        else:
                            event_list.append(new_event)
                        EditorSaveCheck(
                            path=path,
                            old_path=self.old_event_path,
                            editor_save=self.editor_element["save"],
                            event_list=event_list,
                            old_event_list=old_event_file,
                        )

                # SWITCH EDITOR TAB
                else:
                    for name, button in self.editor_element.items():
                        if (
                            event.ui_element == button
                            and name != self.current_editor_tab
                        ):
                            self.current_editor_tab = name
                            self.clear_editor_tab()
                            break

            # TEXT PREVIEW
            if event.ui_element == self.event_text_element[
                "preview_button"
            ] and self.event_text_element.get("event_text"):
                # finds what the new preview state should be
                index = self.preview_states.index(self.current_preview_state)
                new_index = (index + 1) % 3
                self.current_preview_state = self.preview_states[new_index]

                # switches states
                if new_index == 0:
                    game.event_editing = True
                    self.event_text_element["event_text"].show()
                    self.event_text_element["preview_text"].hide()
                else:
                    game.event_editing = False
                    self.event_text_element["event_text"].hide()
                    text = self.get_processed_text()
                    self.event_text_element["preview_text"].set_text(text)
                    self.event_text_element["preview_text"].show()

            # SETTINGS TAB EVENTS
            elif self.current_editor_tab == "settings":
                self.handle_settings_events(event)

            # MAIN/RANDOM CAT TAB EVENTS
            elif self.current_editor_tab in ["main cat", "random cat"]:
                self.handle_main_and_random_cat_events(event)

            # NEW CAT TAB EVENTS
            elif self.current_editor_tab == "new cats":
                self.handle_new_cat_events(event)

            # PERSONAL CONSEQUENCES TAB EVENTS
            elif self.current_editor_tab == "personal consequences":
                self.handle_personal_events(event)

            # OUTSIDE CONSEQUENCES TAB EVENTS
            elif self.current_editor_tab == "outside consequences":
                self.handle_outside_events(event)

            # FUTURE EFFECTS TAB EVENTS
            elif self.current_editor_tab == "future effects":
                self.handle_future_events(event)

        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if self.event_text_element.get("event_text") == event.ui_element:
                self.event_text_info = self.event_text_element["event_text"].html_text
                if "t_initial" in self.event_text_info:
                    self.event_text_info = ""
                    self.event_text_element["event_text"].set_text(self.event_text_info)
                character_count = len(self.get_processed_text())
                self.event_text_element["counter"].set_text(
                    f"{character_count} characters after processing"
                )

            # CHANGE EVENT ID
            if self.current_editor_tab == "settings":
                if event.ui_element == self.event_id_element.get("entry"):
                    self.event_id_info = self.event_id_element["entry"].text
                    self.valid_id()

            # REL VALUE CONSTRAINTS
            elif self.current_editor_tab in ["random cat", "main cat"]:
                if event.ui_element in self.rel_value_element.values():
                    info = self.current_cat_dict["rel_status"]
                    for value, element in self.rel_value_element.items():
                        value = value.replace("_entry", "")
                        if element != event.ui_element:
                            continue
                        remove_tag = None
                        for tag in info:
                            if value in tag:
                                remove_tag = tag
                                break
                        if remove_tag:
                            info.remove(remove_tag)
                        if element.text:
                            self.current_cat_dict["rel_status"].append(
                                f"{value}_{element.text}"
                            )
                        self.update_rel_status_info()
                        break

            # REL CHANGE AMOUNT
            elif (
                self.current_editor_tab == "personal consequences"
                and self.open_block == "relationships"
            ):
                if event.ui_element == self.relationships_element["amount_entry"]:
                    info = self.get_selected_block_info()
                    if (
                        info["amount"]
                        != self.relationships_element["amount_entry"].text
                    ):
                        info["amount"] = self.relationships_element["amount_entry"].text
                        self.update_block_info()

            elif self.current_editor_tab == "outside consequences":
                # OUTSIDER CHANGE AMOUNT
                if event.ui_element == self.outsider_element["entry"]:
                    info = self.outsider_info["changed"]
                    if info != self.outsider_element["entry"].text:
                        self.outsider_info["changed"] = self.outsider_element[
                            "entry"
                        ].text
                        self.outsider_element["display"].set_text(
                            f"{self.outsider_info}"
                        )

                # OTHER CLAN CHANGE AMOUNT
                if event.ui_element == self.other_clan_element["entry"]:
                    info = self.other_clan_info["changed"]
                    if info != self.other_clan_element["entry"].text:
                        self.other_clan_info["changed"] = self.other_clan_element[
                            "entry"
                        ].text
                        self.other_clan_element["display"].set_text(
                            f"{self.other_clan_info}"
                        )

                # SUPPLY INCREASE
                if event.ui_element == self.supply_element.get("increase_entry"):
                    selected_block = self.get_selected_block_info()
                    info = selected_block["adjust"].replace("increase_", "")
                    if info != self.supply_element["increase_entry"].text:
                        selected_block[
                            "adjust"
                        ] = f"increase_{self.supply_element['increase_entry'].text}"
                        self.update_block_info()
            elif self.current_editor_tab == "future effects":
                if event.ui_element == self.future_element.get(
                    "least_entry"
                ) or event.ui_element == self.future_element.get("most_entry"):
                    if self.future_element["least_entry"].text:
                        least = int(self.future_element["least_entry"].text)
                    else:
                        least = 1
                    if self.future_element["most_entry"].text:
                        most = int(self.future_element["most_entry"].text)
                    else:
                        most = 1

                    self.get_selected_block_info()["moon_delay"] = [least, most]

    def handle_future_event_ids(self):
        if not self.future_element.get("include_entry"):
            return
        if self.future_element["include_entry"].is_focused:
            new_id = self.future_element["include_entry"].get_text()
            block_info = self.get_selected_block_info()["pool"]["event_id"]
            if new_id not in block_info:
                block_info.append(new_id)
            else:
                block_info.remove(new_id)
            text = ""
            for id in block_info:
                text += f"'{id}'<br>"
            self.future_element["include_display"].set_text(text)
            self.future_element["include_entry"].set_text("")
            self.editor_container.on_contained_elements_changed(
                self.future_element["include_display"]
            )
        elif self.future_element["exclude_entry"].is_focused:
            new_id = self.future_element["exclude_entry"].get_text()
            block_info = self.get_selected_block_info()["pool"]["excluded_event_id"]
            if new_id not in block_info:
                block_info.append(new_id)
            else:
                block_info.remove(new_id)
            text = ""
            for id in block_info:
                text += f"'{id}'<br>"
            self.future_element["exclude_display"].set_text(text)
            self.future_element["exclude_entry"].set_text("")
            self.editor_container.on_contained_elements_changed(
                self.future_element["exclude_display"]
            )

    def get_processed_text(self):
        text = self.event_text_element["event_text"].html_text
        test_dict = {}

        if not self.current_preview_state:
            conju = 1
        else:
            conju = self.current_preview_state

        for abbr in self.test_cat_names:
            pronoun = choice(
                [pro for pro in self.test_pronouns if pro["conju"] == conju]
            )
            test_dict[abbr] = (self.test_cat_names[abbr], pronoun)
        text = process_text(text, test_dict)
        return text

    def on_use(self):
        """
        We'll use this to check and update some of our custom ui_elements due to the order update() and handle_event()
        funcs run in.
        """

        if self.current_editor_tab == "settings":
            self.handle_settings_on_use()

        elif self.current_editor_tab in ["main cat", "random cat"]:
            self.handle_main_and_random_cat_on_use()

        elif self.current_editor_tab == "new cats":
            self.handle_new_cat_on_use()

        elif self.current_editor_tab == "personal consequences":
            self.handle_personal_on_use()

        elif self.current_editor_tab == "outside consequences":
            self.handle_outside_on_use()

        elif self.current_editor_tab == "future effects":
            self.handle_future_on_use()

        super().on_use()

    # OVERALL SCREEN CONTROLS
    def exit_screen(self):
        game.event_editing = False

        self.main_menu_button.kill()
        self.list_frame.kill()
        self.event_text_container.kill()

        self.clear_editor_tab()
        self.clear_event_info()
        self.current_editor_tab = None

        if self.event_list_container:
            self.event_list_container.kill()
        if self.event_search:
            self.event_search.kill()
            self.event_search = None
        self.search_text = None

        if self.editor_container:
            self.editor_container.kill()

        if self.editor_element:
            for ele in self.editor_element.values():
                ele.kill()
            self.editor_element.clear()

        if self.event_text_element:
            for ele in self.event_text_element.values():
                ele.kill()
        self.event_text_element.clear()

        self.add_button.kill()
        self.kill_tabs()
        self.kill_event_buttons()

    def screen_switches(self):
        super().screen_switches()
        Screens.show_mute_buttons()

        self.main_menu_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (152, 30))),
            "buttons.main_menu",
            get_button_dict(ButtonStyles.SQUOVAL, (152, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_squoval",
            starting_height=1,
        )

        self.list_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((60, 80), (250, 560))),
            get_box(BoxStyles.ROUNDED_BOX, (250, 560)),
            starting_height=3,
            manager=MANAGER,
        )

        self.select_type_tab_creation()
        self.create_event_display()

        self.event_text_container = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((290, 10), (0, 0))),
            starting_height=1,
            manager=MANAGER,
        )
        self.event_text_element["preview_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((-30, 30), (36, 36))),
            Icon.MAGNIFY,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            container=self.event_text_container,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.preview_text",
        )

        self.event_text_element["box"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 20), (460, 120))),
            get_box(BoxStyles.ROUNDED_BOX, (460, 120)),
            starting_height=1,
            manager=MANAGER,
            container=self.event_text_container,
        )
        self.event_text_element["box"].disable()

        self.event_text_element["character_info"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((10, 5), (-1, -1))),
            "screens.event_edit.event_text_character_count",
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
            container=self.event_text_container,
        )
        self.event_text_element["counter"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((250, 5), (200, -1))),
            "0 characters after processing",
            object_id=get_text_box_theme("#text_box_22_horizright"),
            manager=MANAGER,
            container=self.event_text_container,
        )

        self.editor_element["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((300, 140), (470, 490))),
            get_box(BoxStyles.FRAME, (470, 490)),
            starting_height=2,
            manager=MANAGER,
        )
        self.add_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 580), (36, 36))),
            Icon.NOTEPAD,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.add_event",
        )

        self.create_editor_display()

    def kill_tabs(self):
        """
        Kills the tab buttons.
        """
        for tab in self.type_tab_buttons:
            self.type_tab_buttons[tab].kill()
        for tab in self.biome_tab_buttons:
            self.biome_tab_buttons[tab].kill()

    # EVENT DISPLAY

    def select_type_tab_creation(self):
        # clear all tabs first
        self.kill_tabs()

        self.type_tab_buttons["death"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 136), (36, 36))),
            Icon.STARCLAN,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_deaths",
        )
        self.type_tab_buttons["injury"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.SCRATCHES,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_injuries",
            anchors={"top_target": self.type_tab_buttons["death"]},
        )
        self.type_tab_buttons["misc"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.CLAN_UNKNOWN,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_misc",
            anchors={"top_target": self.type_tab_buttons["injury"]},
        )
        self.type_tab_buttons["new_cat"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.CAT_HEAD,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_new_cat",
            anchors={"top_target": self.type_tab_buttons["misc"]},
        )

    def select_biome_tab_creation(self):
        # clear all tabs first
        self.kill_tabs()

        self.biome_tab_buttons["back"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 90), (36, 36))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
        )
        self.biome_tab_buttons["general"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.PAW,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_general",
            anchors={"top_target": self.biome_tab_buttons["back"]},
        )
        self.biome_tab_buttons["forest"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.LEAFFALL,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_forest",
            anchors={"top_target": self.biome_tab_buttons["general"]},
        )
        self.biome_tab_buttons["mountainous"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.LEAFBARE,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_mountain",
            anchors={"top_target": self.biome_tab_buttons["forest"]},
        )
        self.biome_tab_buttons["plains"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.NEWLEAF,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_plains",
            anchors={"top_target": self.biome_tab_buttons["mountainous"]},
        )
        self.biome_tab_buttons["beach"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.DARKFOREST,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_beach",
            anchors={"top_target": self.biome_tab_buttons["plains"]},
        )

        self.biome_tab_buttons["desert"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.GREENLEAF,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_desert",
            anchors={"top_target": self.biome_tab_buttons["beach"]},
        )

        self.biome_tab_buttons["wetlands"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((27, 10), (36, 36))),
            Icon.HERB,
            get_button_dict(ButtonStyles.ICON_TAB_RIGHT, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_right",
            starting_height=1,
            tool_tip_text="buttons.edit_wetlands",
            anchors={"top_target": self.biome_tab_buttons["desert"]},
        )

    def create_event_display(self, event_type=None, biome=None):
        self.kill_event_buttons()
        event_list = []
        if self.editor_element.get("intro_text"):
            self.editor_element["intro_text"].set_text("screens.event_edit.intro_text")

        path = "resources/lang/en/events"
        type_list = list(self.event_types.keys())
        all_biomes = constants.BIOME_TYPES.copy()
        all_biomes.append("general")

        if not event_type:
            for type_name in type_list:
                for biome_name in all_biomes:
                    event_list.extend(
                        self.get_event_json(
                            f"{path}/{type_name}/{biome_name.casefold()}.json"
                        )
                    )
        elif event_type and not biome:
            for biome_name in all_biomes:
                event_list.extend(
                    self.get_event_json(
                        f"{path}/{event_type}/{biome_name.casefold()}.json"
                    )
                )
        elif event_type and biome:
            event_list.extend(
                self.get_event_json(f"{path}/{event_type}/{biome.casefold()}.json")
            )

        if self.search_text:
            available = event_list.copy()
            event_list = []
            for event in available:
                subtypes = [x for x in event.get("sub_type", [])]
                if self.search_text in event["event_id"]:
                    event_list.append(event)
                elif self.search_text in event["event_text"]:
                    event_list.append(event)
                elif self.search_text in subtypes:
                    event_list.append(event)
            event_list = [
                event
                for event in event_list.copy()
                if set(event["event_id"]).intersection(set(self.search_text))
            ]

        if not self.event_list_container:
            self.event_list_container = UIModifiedScrollingContainer(
                ui_scale(pygame.Rect((68, 90), (236, 511))),
                starting_height=3,
                manager=MANAGER,
                allow_scroll_y=True,
            )

        self.event_list = event_list

        for index, event in enumerate(event_list):
            if not event_type:
                self.all_event_ids.append(event["event_id"])
            test_dict = {}
            for abbr in self.test_cat_names:
                pronoun = choice(
                    [pro for pro in self.test_pronouns if pro["conju"] == 2]
                )
                test_dict[abbr] = (self.test_cat_names[abbr], pronoun)
            preview = process_text(event["event_text"], test_dict)
            game.event_editing = True
            self.event_buttons[index] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, -2 if index > 0 else 0), (234, 36))),
                event["event_id"],
                get_button_dict(ButtonStyles.DROPDOWN, (234, 36)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                starting_height=1,
                anchors={"top_target": self.event_buttons[index - 1]}
                if self.event_buttons.get(index - 1)
                else None,
                container=self.event_list_container,
                tool_tip_text=f"{event['event_id']}<br>{preview}",
            )

        if not self.event_search:
            self.event_search = pygame_gui.elements.UITextEntryLine(
                ui_scale(pygame.Rect((70, 0), (230, 29))),
                manager=MANAGER,
                anchors={"top_target": self.event_list_container},
                placeholder_text="type and hit enter to search",
            )
            self.event_search.change_layer(3)
            self.event_search.set_tooltip("ddd")

    def kill_event_buttons(self):
        for event in self.event_buttons:
            self.event_buttons[event].kill()
        if self.event_list_container:
            self.event_list_container.kill()
            self.event_list_container = None

    # EDITOR DISPLAY
    def clear_editor_tab(self):
        self.editor_container.kill()

        self.create_editor_display()

    def clear_event_info(self):
        """
        Clears all the saved event info, so we can start fresh.
        """
        # resetting all tag lists
        for tag in self.basic_tag_list:
            tag["setting"] = False
        for tag in self.rel_tag_list:
            tag["setting"] = False
        for tag in self.new_cat_bools:
            tag["setting"] = False
        # Settings elements
        self.event_text_info = ""
        self.event_id_element = {}
        self.event_id_info = ""
        self.location_element = {}
        if not self.param_locks.get("location"):
            self.location_info = []
        self.season_element = {}
        if not self.param_locks.get("season"):
            self.season_info = []
        self.type_element = {}
        self.sub_element = {}
        if not self.param_locks.get("subtypes"):
            self.type_info = ["death"]
            self.sub_info = []
        self.tag_element = {}
        self.basic_tag_checkbox = {}
        self.rank_tag_checkbox = {}
        if not self.param_locks.get("tag"):
            self.tag_info = []
        self.weight_element = {}
        if not self.param_locks.get("weight"):
            self.weight_info = 20
        self.acc_element = {}
        if not self.param_locks.get("acc"):
            self.acc_info = []
        self.acc_categories = Pelt.acc_categories
        self.open_category = None
        self.acc_button = {}
        self.main_cat_editor = {}
        self.random_cat_editor = {}
        self.death_element = {}
        self.rank_element = {}
        self.age_element = {}
        self.rel_status_element = {}
        self.rel_status_checkbox = {}
        self.rel_value_element = {}
        self.skill_element = {}
        self.level_element = {}
        self.skill_allowed = True
        self.open_path = None
        self.chosen_level = None
        self.trait_element = {}
        self.trait_allowed = True
        self.backstory_element = {}
        self.open_pool = None
        reference_dict = self.main_cat_info.copy()
        self.main_cat_info = {
            "rank": []
            if not self.param_locks.get("main_rank")
            else reference_dict["rank"],
            "age": []
            if not self.param_locks.get("main_age")
            else reference_dict["age"],
            "rel_status": []
            if not self.param_locks.get("main_rel_status")
            else reference_dict["rel_status"],
            "dies": False
            if not self.param_locks.get("main_dies")
            else reference_dict["dies"],
            "skill": []
            if not self.param_locks.get("main_skill")
            else reference_dict["skill"],
            "not_skill": []
            if not self.param_locks.get("main_not_skill")
            else reference_dict["not_skill"],
            "trait": []
            if not self.param_locks.get("main_trait")
            else reference_dict["trait"],
            "not_trait": []
            if not self.param_locks.get("main_not_trait")
            else reference_dict["not_trait"],
            "backstory": []
            if not self.param_locks.get("main_backstory")
            else reference_dict["backstory"],
        }
        if not self.param_locks.get("main_rel_status"):
            for tag in self.rel_tag_list:
                tag["setting"] = False
        reference_dict = self.random_cat_info.copy()
        self.random_cat_info = {
            "rank": []
            if not self.param_locks.get("random_rank")
            else reference_dict["rank"],
            "age": []
            if not self.param_locks.get("random_age")
            else reference_dict["age"],
            "rel_status": []
            if not self.param_locks.get("random_rel_status")
            else reference_dict["rel_status"],
            "dies": False
            if not self.param_locks.get("random_dies")
            else reference_dict["dies"],
            "skill": []
            if not self.param_locks.get("random_skill")
            else reference_dict["skill"],
            "not_skill": []
            if not self.param_locks.get("random_not_skill")
            else reference_dict["not_skill"],
            "trait": []
            if not self.param_locks.get("random_trait")
            else reference_dict["trait"],
            "not_trait": []
            if not self.param_locks.get("random_not_trait")
            else reference_dict["not_trait"],
            "backstory": []
            if not self.param_locks.get("random_backstory")
            else reference_dict["backstory"],
        }
        self.selected_new_cat_info = {}
        self.new_cat_template = {
            "backstory": [],
            "parent": [],
            "adoptive": [],
            "mate": [],
        }
        self.current_cat_dict = self.main_cat_info
        self.new_cat_editor = {}
        self.new_cat_element = {}
        if not self.param_locks.get("new_cat"):
            self.new_cat_block_dict = {}
        self.selected_new_cat = None
        self.new_cat_checkbox = {}
        self.cat_story_element = {}
        self.new_status_element = {}
        self.new_age_element = {}
        self.new_gender_element = {}
        self.connections_element = {}
        self.open_connection = "parent"
        self.exclusion_element = {}
        if not self.param_locks.get("exclude"):
            self.excluded_cats = []
        self.open_block = "injury"
        self.injury_element = {}
        if not self.param_locks.get("injury"):
            self.injury_block_list = []
            self.selected_injury_block: str = ""
        self.injury_template = {"cats": [], "injuries": [], "scars": []}
        self.history_element = {}
        if not self.param_locks.get("history"):
            self.history_block_list = []
            self.selected_history_block_index: str = ""
        self.history_template = {
            "cats": [],
            "scar": "",
            "reg_death": "",
            "lead_death": "",
        }
        self.relationships_element = {}
        if not self.param_locks.get("relationships"):
            self.relationships_block_list = []
            self.selected_relationships_block_index: str = ""
        self.relationships_template = {
            "cats_from": [],
            "cats_to": [],
            "mutual": False,
            "values": [],
            "amount": 0,
        }
        self.outsider_element = {}
        if not self.param_locks.get("outsider"):
            self.outsider_info = {"current_rep": [], "changed": 0}
        self.other_clan_element = {}
        if not self.param_locks.get("other_clan"):
            self.other_clan_info = {"current_rep": [], "changed": 0}
        self.supply_element = {}
        if not self.param_locks.get("supply"):
            self.supply_block_list = []
            self.selected_supply_block_index: str = ""
        self.supply_info = {"type": "", "trigger": [], "adjust": ""}
        self.current_preview_state = self.preview_states[0]
        self.future_element = {}
        if not self.param_locks.get("future"):
            self.future_block_list = []
            self.selected_future_block_index: str = ""
        self.future_template = {
            "event_type": "death",
            "pool": {
                "subtype": [],
                "event_id": [],
                "excluded_event_id": [],
            },
            "moon_delay": [1, 1],
            "involved_cats": {"m_c": None, "r_c": None},
        }

    def create_editor_display(self):
        self.editor_container = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((314, 150), (470, 470))),
            starting_height=4,
            manager=MANAGER,
            allow_scroll_y=True,
        )
        self.editor_container.scrollable_container.resize_top = False

        if not self.current_editor_tab:
            self.editor_element["intro_text"] = UITextBoxTweaked(
                "screens.event_edit.intro_text",
                ui_scale(pygame.Rect((0, 0), (450, -1))),
                object_id=get_text_box_theme("#text_box_26_horizleft_pad_10_14"),
                line_spacing=1,
                manager=MANAGER,
                container=self.editor_container,
            )
            return
        elif self.editor_element.get("intro_text"):
            self.editor_element["intro_text"].kill()

        # EVENT TEXT
        # this one is special in that it has a separate container
        if not self.event_text_element.get("preview_text"):
            self.event_text_element["preview_text"] = UITextBoxTweaked(
                "",
                ui_scale(pygame.Rect((48, 30), (435, 100))),
                object_id="#text_box_26_horizleft_pad_10_14",
                manager=MANAGER,
                container=self.event_text_container,
                visible=False,
            )
            self.event_text_element["preview_text"].disable()
            self.event_text_element["event_text"] = pygame_gui.elements.UITextEntryBox(
                ui_scale(pygame.Rect((48, 30), (435, 100))),
                object_id="#text_box_26_horizleft_pad_10_14",
                manager=MANAGER,
                container=self.event_text_container,
            )
        else:
            self.event_text_element["event_text"].show()
            self.event_text_element["preview_text"].hide()
        game.event_editing = True

        if self.event_text_info:
            self.event_text_element["event_text"].set_text(self.event_text_info)
            self.event_text_element["counter"].set_text(
                f"{len(self.get_processed_text())} characters after processing"
            )
        else:
            self.event_text_element["event_text"].set_text(
                "screens.event_edit.event_text_initial"
            )

        # SECTION TABS
        if not self.editor_element.get(list(self.section_tabs.keys())[0]):
            prev_element = None
            for name, icon in self.section_tabs.items():
                self.editor_element[name] = UISurfaceImageButton(
                    ui_scale(pygame.Rect((10, -6), (36, 36))),
                    icon,
                    get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
                    manager=MANAGER,
                    object_id="@buttonstyles_icon_tab_bottom",
                    starting_height=1,
                    tool_tip_text=name,
                    anchors=(
                        {
                            "top_target": self.editor_element["frame"],
                            "left_target": self.list_frame,
                        }
                        if not prev_element
                        else {
                            "top_target": self.editor_element["frame"],
                            "left_target": prev_element,
                        }
                    ),
                )
                prev_element = self.editor_element[name]

        if not self.editor_element.get("save"):
            self.editor_element["save"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((340, -8), (80, 36))),
                "buttons.save",
                get_button_dict(ButtonStyles.HORIZONTAL_TAB_MIRRORED, (80, 36)),
                manager=MANAGER,
                object_id="@buttonstyles_horizontal_tab_mirrored",
                starting_height=1,
                tool_tip_text="Add this event to the event json.",
                anchors=(
                    {
                        "top_target": self.editor_element["frame"],
                        "left_target": self.list_frame,
                    }
                ),
            )

        if self.current_editor_tab == "settings":
            self.generate_settings_tab()
        elif self.current_editor_tab == "main cat":
            self.current_cat_dict = self.main_cat_info
            self.generate_main_cat_tab()
        elif self.current_editor_tab == "random cat":
            self.current_cat_dict = self.random_cat_info
            self.generate_random_cat_tab()
        elif self.current_editor_tab == "new cats":
            self.generate_new_cats_tab()
        elif self.current_editor_tab == "personal consequences":
            self.generate_personal_tab()
        elif self.current_editor_tab == "outside consequences":
            self.generate_outside_tab()
        elif self.current_editor_tab == "future effects":
            self.generate_future_tab()

    def create_lock(
        self,
        name,
        top_anchor,
        left_anchor=None,
        container=None,
        x_offset=10,
        y_offset=10,
    ):
        """
        Creates a lock button based on parameters.
        :param top_anchor: The element the divider should anchor it's top coord to
        :param left_anchor: The element the divider should anchor it's left coord to
        :param name: The key the divider should use within the self.editor_element dict
        :param container: As a default, it uses self.editor_container, but you can change that with this param
        """
        if not container:
            container = self.editor_container

        self.lock_buttons[name] = UISurfaceImageButton(
            ui_scale(pygame.Rect((x_offset, y_offset), (36, 36))),
            Icon.UNLOCK,
            get_button_dict(ButtonStyles.ICON, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon",
            container=container,
            anchors=(
                {"top_target": top_anchor}
                if not left_anchor
                else {"top_target": top_anchor, "left_target": left_anchor}
            ),
            starting_height=2,
            tool_tip_text="If locked, these parameters will be preserved when making a new event.",
        )
        if name in self.param_locks.keys():
            # ensure lock reflects current setting
            if self.param_locks[name]:
                self.lock_buttons[name].set_text(Icon.LOCK)
        else:
            self.param_locks[name] = False

    def create_divider(self, top_anchor, name, off_set: int = -12, container=None):
        """
        Creates a divider element based on parameters.
        :param top_anchor: The element the divider should anchor it's top coord to
        :param name: The key the divider should use within the self.editor_element dict
        :param off_set: Use to adjust how close the divider sits to it's top anchor, generally doesn't need to be
        adjusted
        :param container: As a default, it uses self.editor_container, but you can change that with this param
        """
        if not container:
            container = self.editor_container

        self.editor_element[name] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, off_set), (524, 24))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/spacer.png").convert_alpha(),
                ui_scale_dimensions((524, 24)),
            ),
            container=container,
            manager=MANAGER,
            anchors={"top_target": top_anchor},
        )

    # HELPERS
    def get_involved_cats(self, index_limit=None, include_clan=True) -> list:
        """
        Returns a list of cats involved in this event.
        :param index_limit: indicate a maximum index for the new cat list.
        :param include_clan: should "clan" and "some_clan" tags be included
        """
        involved_cats = ["m_c", "r_c"]

        new_cat_list = list(self.new_cat_block_dict.keys())
        if isinstance(index_limit, int):
            for index, item in enumerate(new_cat_list.copy()):
                if index >= index_limit:
                    new_cat_list.remove(item)

        involved_cats.extend(new_cat_list)

        if include_clan:
            involved_cats.extend(
                [
                    "some_clan",
                    "clan",
                    "low_lawful",
                    "high_lawful",
                    "low_social",
                    "high_social",
                    "low_stable",
                    "high_stable",
                    "low_aggress",
                    "high_aggress",
                ]
            )

        return involved_cats

    def add_block(self, event):
        """
        Handles adding a block to a block list.
        :param event: the event.ui_element that triggers this func
        """
        if event not in [
            self.injury_element.get("add"),
            self.history_element.get("add"),
            self.relationships_element.get("add"),
            self.supply_element.get("add"),
            self.future_element.get("add"),
        ]:
            return

        attr = self.get_block_attributes()

        added_block = int(attr["selected"]) + 1 if attr["selected"] else 0
        attr["block_list"].insert(added_block, attr["info_dict"].copy())
        attr["selected"] = str(added_block)
        attr["view"].new_item_list(
            [str(index) for index in range(len(attr["block_list"]))]
        )
        attr["view"].set_selected_list([attr["selected"]] if attr["selected"] else [])

        if self.open_block == "injury":
            self.selected_injury_block = attr["selected"]
            self.update_injury_block_options()
        elif self.open_block == "history":
            self.selected_history_block_index = attr["selected"]
            self.update_history_block_options()
        elif self.open_block == "supply":
            self.selected_supply_block_index = attr["selected"]
            self.update_supply_block_options()
        elif self.open_block == "future":
            self.selected_future_block_index = attr["selected"]
            self.display_future_constraints()
            self.update_future_block_options()
        else:
            self.selected_relationships_block_index = attr["selected"]
            self.update_relationships_block_options()

        self.update_block_info()

    def delete_block(self, event):
        """
        Handles deleting a block from a block list.
        :param event: the event.ui_element that triggers this func
        """

        if event not in [
            self.injury_element.get("delete"),
            self.history_element.get("delete"),
            self.relationships_element.get("delete"),
            self.supply_element.get("delete"),
            self.future_element.get("delete"),
        ]:
            return

        attr = self.get_block_attributes()

        removed_block = int(attr["selected"])
        attr["block_list"].remove(attr["block_list"][removed_block])
        attr["selected"] = str(removed_block - 1) if len(attr["block_list"]) else ""
        attr["view"].new_item_list(
            [str(index) for index in range(len(attr["block_list"]))]
        )
        attr["view"].set_selected_list([attr["selected"]] if attr["selected"] else [])

        if self.open_block == "injury":
            self.selected_injury_block = attr["selected"]
            if not attr["selected"]:
                self.clear_injury_constraints()
            self.update_injury_block_options()
        elif self.open_block == "history":
            self.selected_history_block_index = attr["selected"]
            if not attr["selected"]:
                self.clear_history_constraints()
            self.update_history_block_options()
        elif self.open_block == "supply":
            self.selected_supply_block_index = attr["selected"]
            if not attr["selected"]:
                self.clear_supply_constraints()
            self.update_supply_block_options()
        elif self.open_block == "future":
            self.selected_future_block_index = attr["selected"]
            if not attr["selected"]:
                self.clear_future_constraints()
            self.update_future_block_options()
        else:
            self.selected_relationships_block_index = attr["selected"]
            if not attr["selected"]:
                self.clear_relationships_constraints()
            self.update_relationships_block_options()

        self.update_block_info()
        self.editor_container.on_contained_elements_changed(
            self.editor_element[f"{self.open_block}_start"]
        )

    def get_block_attributes(self) -> dict:
        """
        Returns the attributes for the currently opened block.
        """

        if self.open_block == "injury":
            element = self.injury_element
            view = self.injury_element["block_list"]
            block_list = self.injury_block_list
            info_dict = self.injury_template
            selected = (
                self.selected_injury_block if self.selected_injury_block else None
            )
            display = self.injury_element["display"]
        elif self.open_block == "history":
            element = self.history_element
            view = self.history_element["block_list"]
            block_list = self.history_block_list
            info_dict = self.history_template
            selected = (
                self.selected_history_block_index
                if self.selected_history_block_index
                else None
            )
            display = self.history_element["display"]
        elif self.open_block == "supply":
            element = self.supply_element
            view = self.supply_element["block_list"]
            block_list = self.supply_block_list
            info_dict = self.supply_info
            selected = (
                self.selected_supply_block_index
                if self.selected_supply_block_index
                else None
            )
            display = self.supply_element["display"]
        elif self.open_block == "future":
            element = self.future_element
            view = self.future_element["block_list"]
            block_list = self.future_block_list
            info_dict = self.future_template.copy()
            selected = (
                self.selected_future_block_index
                if self.selected_future_block_index
                else None
            )
            display = None
        else:
            element = self.relationships_element
            view = self.relationships_element["block_list"]
            block_list = self.relationships_block_list
            info_dict = self.relationships_template
            selected = (
                self.selected_relationships_block_index
                if self.selected_relationships_block_index
                else None
            )
            display = self.relationships_element["display"]

        return {
            "element": element,
            "view": view,
            "block_list": block_list,
            "info_dict": info_dict,
            "selected": selected,
            "display": display,
        }

    def get_selected_block_info(self) -> dict:
        """
        Returns the loaded information dict for the currently viewed block.
        """
        if self.open_block == "injury":
            return (
                self.injury_block_list[int(self.selected_injury_block)]
                if self.selected_injury_block
                else self.injury_template
            )
        elif self.open_block == "history":
            return (
                self.history_block_list[int(self.selected_history_block_index)]
                if self.selected_history_block_index
                else self.history_template
            )
        elif self.open_block == "relationships":
            return (
                self.relationships_block_list[
                    int(self.selected_relationships_block_index)
                ]
                if self.selected_relationships_block_index
                else self.relationships_template
            )
        elif self.open_block == "supply":
            return (
                self.supply_block_list[int(self.selected_supply_block_index)]
                if self.selected_supply_block_index
                else self.supply_info
            )
        elif self.open_block == "future":
            return (
                self.future_block_list[int(self.selected_future_block_index)]
                if self.selected_future_block_index
                else self.future_template.copy()
            )

    def new_cat_select(self):
        """
        Handles selecting a new cat block from the button list.
        """
        new_selection = (
            self.new_cat_editor["cat_list"].selected_list[0]
            if self.new_cat_editor["cat_list"].selected_list
            else None
        )
        if self.selected_new_cat != new_selection:
            self.selected_new_cat = new_selection
            self.change_new_cat_info_dict()

            if not self.connections_element.get("display"):
                self.display_new_cat_constraints()

            self.update_new_cat_options()
            self.new_cat_editor["display"].set_text(
                f"selected cat: "
                f"{self.new_cat_block_dict.get(self.selected_new_cat) if self.new_cat_block_dict.get(self.selected_new_cat) else '[]'}"
            )
            self.update_new_cat_button_tooltips()

            # need to reset the cat connections info here or it'll be incorrect
            new_selection = (
                self.connections_element["cat_list"].selected_list.copy()
                if self.connections_element["cat_list"].selected_list
                else []
            )
            self.connections_element["display"].set_text(
                f"chosen cats: {new_selection}"
            )

    def change_new_cat_info_dict(self):
        """
        Handles changes between new cat info dicts. If the newly selected cat has a tag list but not an info dict, then
        this will handle compiling an info dict from the tag list.
        """
        if not self.selected_new_cat_info:
            if self.new_cat_block_dict.get(self.selected_new_cat):
                saved_info = self.new_cat_block_dict[self.selected_new_cat]
                unpacked = {"backstory": [], "parent": [], "adoptive": [], "mate": []}
                for tag in saved_info:
                    if "backstory" in tag:
                        stories = tag.replace("backstory:", "")
                        stories = stories.split(",")
                        unpacked["backstory"] = stories
                    elif "parent" in tag:
                        parents = tag.replace("parent:", "")
                        parents = parents.split(",")
                        unpacked["parent"] = parents
                    elif "adoptive" in tag:
                        adoptive = tag.replace("adoptive:", "")
                        adoptive = adoptive.split(",")
                        unpacked["adoptive"] = adoptive
                    elif "mate" in tag:
                        mates = tag.replace("mate:", "")
                        mates = mates.split(",")
                        unpacked["mate"] = mates
                self.selected_new_cat_info = unpacked
            else:
                self.selected_new_cat_info = {
                    "backstory": [],
                    "parent": [],
                    "adoptive": [],
                    "mate": [],
                }
        self.current_cat_dict = self.selected_new_cat_info

    def valid_id(self) -> bool:
        """
        Checks that the event_id is valid. This also controls the id validation display.
        """
        valid = True
        if (
            self.event_id_info in self.all_event_ids
            and self.event_id_info != self.open_event.get("event_id")
        ):
            text = "screens.event_edit.dupe_id"
            valid = False
        elif not self.event_id_info or self.event_id_info.isspace():
            text = "screens.event_edit.invalid_id"
            valid = False
        else:
            text = "screens.event_edit.valid_id"
        if not valid:
            self.alert_text = (
                f"Event ID is either invalid or a duplicate. Pick a new ID."
            )

        if self.event_id_element.get("check_text"):
            self.event_id_element["check_text"].set_text(text)

        return valid

    def valid_injury(self) -> bool:
        """
        Checks that all injury blocks have all required info.
        """
        valid = True
        for block in self.injury_block_list:
            if not block["cats"]:
                valid = False
            elif not block["injuries"]:
                valid = False

        if not valid:
            self.alert_text = f"An Injury block is missing information! Do all blocks have cats and injuries selected?"

        return valid

    def valid_history(self) -> bool:
        """
        Checks if user has included death/injury histories for all killed or injured cats. Also checks if history blocks
        have all required info.
        """
        valid = True
        dead_cats = []
        injured_cats = []
        if self.main_cat_info["dies"]:
            dead_cats.append("m_c")
        if self.random_cat_info["dies"]:
            dead_cats.append("r_c")
        for cat, block in self.new_cat_block_dict.items():
            if "dead" in block:
                dead_cats.append(cat)

        for block in self.injury_block_list:
            if (
                set(block["injuries"]).intersection(set(Scar_Events.scar_allowed))
                or block["scars"]
            ):
                injured_cats.extend(block["cats"])
                # scar-able injuries are generally also possibly fatal, so plop them in dead
                dead_cats.extend(block["cats"])
            # injuries that don't scar but DO kill
            elif set(block["injuries"]).intersection(set(self.fatal_conditions)):
                dead_cats.extend(block["cats"])

        death_histories = []
        injury_histories = []
        for block in self.history_block_list:
            if "reg_death" in block or "lead_death" in block:
                death_histories.extend(block["cats"])
            if "scar" in block:
                injury_histories.extend(block["cats"])

        missing_deaths = [cat for cat in dead_cats if cat not in death_histories]
        missing_injuries = [cat for cat in injured_cats if cat not in injury_histories]

        if missing_deaths or missing_injuries:
            self.alert_text = (
                f"Death and/or Injury histories are missing for some affected cats. "
                f"<br><br>Missing Death for: {missing_deaths}<br>Missing Injury for: {missing_injuries} "
            )
            valid = False

        if valid:
            for block in self.history_block_list:
                if not block["cats"]:
                    valid = False
                elif (
                    not block["scar"]
                    and not block["reg_death"]
                    and not block["lead_death"]
                ):
                    valid = False

            if not valid:
                self.alert_text = (
                    f"A History block is missing information! Do all blocks have cats selected and at "
                    f"least one text section filled?"
                )

        return valid

    def valid_relationships(self) -> bool:
        """
        Checks if relationship blocks have all required info
        """
        valid = True

        for block in self.relationships_block_list:
            if (
                not block["cats_from"]
                or not block["cats_to"]
                or not block["values"]
                or not block["amount"]
            ):
                valid = False

        if not valid:
            self.alert_text = (
                f"A Relationship block is missing information! Do all blocks have cats, values, "
                f"and an amount chosen?"
            )
        return valid

    def valid_supply(self) -> bool:
        """
        Checks if supply blocks have all required info
        """
        valid = True
        for block in self.supply_block_list:
            if not block["type"]:
                valid = False

        if not valid:
            self.alert_text = (
                f"A Supply block has no type selected. A type must be chosen!"
            )

        return valid

    def valid_future(self):
        """
        Checks if future blocks have all required info
        """
        valid = True
        for block in self.future_block_list:
            pool = block["pool"]
            if not block["event_type"]:
                valid = False
                self.alert_text = (
                    "A Future Event block has no type. A type must be chosen!"
                )
            elif (
                not pool.get("subtype")
                and not pool.get("event_id")
                and not pool.get("excluded_event_id")
            ):
                valid = False
                self.alert_text = "A Future Event block has no subtype, event_id, or excluded_event_id given. Event pool is too broad, you must use at least one of these constraints!"
            elif block["moon_delay"][0] > block["moon_delay"][1]:
                valid = False
                self.alert_text = "A Future Event block has an invalid moon delay. The second moon delay number should be equal to or larger than the first!"

        return valid

    # HANDLE EVENT FUNCS
    def handle_future_events(self, event):
        # ADD BLOCK
        self.add_block(event.ui_element)
        # REMOVE BLOCK
        self.delete_block(event.ui_element)

    def handle_outside_events(self, event):
        # AMOUNT CHANGES
        amount = None
        if event.ui_element == self.outsider_element.get("amount_up_low_button"):
            amount = 5
        elif event.ui_element == self.outsider_element.get("amount_up_mid_button"):
            amount = 10
        elif event.ui_element == self.outsider_element.get("amount_up_high_button"):
            amount = 20
        elif event.ui_element == self.outsider_element.get("amount_down_low_button"):
            amount = -5
        elif event.ui_element == self.outsider_element.get("amount_down_mid_button"):
            amount = -10
        elif event.ui_element == self.outsider_element.get("amount_down_high_button"):
            amount = -20
        if amount:
            self.outsider_element["entry"].set_text(str(amount))
            selected_info = self.outsider_info
            selected_info["changed"] = amount
            self.outsider_element["display"].set_text(f"{self.outsider_info}")
        amount = None
        if event.ui_element == self.other_clan_element.get("amount_up_low_button"):
            amount = 1
        elif event.ui_element == self.other_clan_element.get("amount_up_mid_button"):
            amount = 3
        elif event.ui_element == self.other_clan_element.get("amount_up_high_button"):
            amount = 5
        elif event.ui_element == self.other_clan_element.get("amount_down_low_button"):
            amount = -1
        elif event.ui_element == self.other_clan_element.get("amount_down_mid_button"):
            amount = -3
        elif event.ui_element == self.other_clan_element.get("amount_down_high_button"):
            amount = -5
        if amount:
            self.other_clan_element["entry"].set_text(str(amount))
            selected_info = self.other_clan_info
            selected_info["changed"] = amount
            self.other_clan_element["display"].set_text(f"{self.other_clan_info}")
        # ADD BLOCK
        self.add_block(event.ui_element)
        # REMOVE BLOCK
        self.delete_block(event.ui_element)

    def handle_personal_events(self, event):
        if event.ui_element == self.injury_element.get("injury"):
            self.injury_element["injury"].disable()
            self.history_element["history"].enable()
            self.relationships_element["relationships"].enable()

            self.open_block = "injury"
            self.change_block_editor()
        elif event.ui_element == self.history_element.get("history"):
            self.injury_element["injury"].enable()
            self.history_element["history"].disable()
            self.relationships_element["relationships"].enable()

            self.open_block = "history"
            self.change_block_editor()
        elif event.ui_element == self.relationships_element.get("relationships"):
            self.injury_element["injury"].enable()
            self.history_element["history"].enable()
            self.relationships_element["relationships"].disable()

            self.open_block = "relationships"
            self.change_block_editor()

        # MUTUAL CHANGE
        elif event.ui_element == self.relationships_element.get("mutual"):
            selected_info = self.get_selected_block_info()
            if self.relationships_element["mutual"].checked:
                self.relationships_element["mutual"].uncheck()
                selected_info["mutual"] = False
                self.relationships_element["cat_bridge_info"].set_text(
                    "screens.event_edit.relationships_one_way"
                )
            else:
                self.relationships_element["mutual"].check()
                selected_info["mutual"] = True
                self.relationships_element["cat_bridge_info"].set_text(
                    "screens.event_edit.relationships_mutual"
                )
            self.update_block_info()
        # AMOUNT CHANGES
        amount = None
        if event.ui_element == self.relationships_element.get("amount_up_low_button"):
            amount = 5
        elif event.ui_element == self.relationships_element.get("amount_up_mid_button"):
            amount = 10
        elif event.ui_element == self.relationships_element.get(
            "amount_up_high_button"
        ):
            amount = 20
        elif event.ui_element == self.relationships_element.get(
            "amount_down_low_button"
        ):
            amount = -5
        elif event.ui_element == self.relationships_element.get(
            "amount_down_mid_button"
        ):
            amount = -10
        elif event.ui_element == self.relationships_element.get(
            "amount_down_high_button"
        ):
            amount = -20
        if amount:
            self.relationships_element["amount_entry"].set_text(str(amount))
            selected_info = self.get_selected_block_info()
            selected_info["amount"] = amount
            self.update_block_info()
        # ADD BLOCK
        self.add_block(event.ui_element)
        # REMOVE BLOCK
        self.delete_block(event.ui_element)

    def handle_new_cat_events(self, event):
        # ADD CAT
        if event.ui_element == self.new_cat_editor["add"]:
            new_index = len(self.new_cat_block_dict) if self.new_cat_block_dict else 0
            self.selected_new_cat = f"n_c:{new_index}"
            self.change_new_cat_info_dict()
            self.new_cat_block_dict[self.selected_new_cat] = []
            self.new_cat_editor["cat_list"].new_item_list(
                self.new_cat_block_dict.keys()
            )
            self.new_cat_editor["cat_list"].set_selected_list([self.selected_new_cat])
            self.new_cat_editor["display"].set_text(f"selected cat: []")
            self.update_new_cat_button_tooltips()

            if self.new_cat_element.get("checkbox_container"):
                self.update_new_cat_options()

        # DELETE CAT
        elif (
            event.ui_element == self.new_cat_editor["delete"] and self.selected_new_cat
        ):
            # retain needed info then clear new_cat_list
            deleted = self.selected_new_cat
            self.new_cat_block_dict.pop(deleted)
            self.selected_new_cat_info.clear()
            old_list = self.new_cat_block_dict.copy()
            self.new_cat_block_dict.clear()

            # create new cat list
            for index, cat in enumerate(old_list.values()):
                self.new_cat_block_dict[f"n_c:{index}"] = cat

            self.new_cat_editor["cat_list"].new_item_list(
                self.new_cat_block_dict.keys()
            )

            self.selected_new_cat = (
                list(self.new_cat_block_dict.keys())[-1]
                if self.new_cat_block_dict.keys()
                else None
            )

            if self.selected_new_cat:
                self.new_cat_editor["cat_list"].set_selected_list(
                    [self.selected_new_cat]
                )
                self.new_cat_editor["display"].set_text(
                    f"selected cat: {self.new_cat_block_dict.get(self.selected_new_cat) if self.new_cat_block_dict.get(self.selected_new_cat) else '[]'}"
                )
                self.change_new_cat_info_dict()

            else:
                self.new_cat_editor["display"].set_text("No cat selected")

            self.update_new_cat_options()

        # CHECKBOXES
        elif event.ui_element in self.new_cat_checkbox.values():
            event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
            for info in self.new_cat_bools:
                if event.ui_element == self.new_cat_checkbox.get(info["tag"]):
                    index = self.new_cat_bools.index(info)
                    self.new_cat_bools[index] = {
                        "tag": info["tag"],
                        "setting": False if info["setting"] else True,
                        "conflict": info["conflict"],
                    }

                    # flip the setting of any conflicting tags
                    if info["conflict"]:
                        for tag in info["conflict"]:
                            conflict_info = [
                                block
                                for block in self.new_cat_bools
                                if tag == block["tag"]
                            ][0]
                            conflict_index = self.new_cat_bools.index(conflict_info)
                            if not info[
                                "setting"
                            ]:  # unchecks if conflicted setting is checked
                                self.new_cat_checkbox[tag].uncheck()
                            self.new_cat_bools[conflict_index] = {
                                "tag": conflict_info["tag"],
                                "setting": False,
                                "conflict": conflict_info["conflict"],
                            }
                    self.update_new_cat_tags()
                    break

        # CONNECTIONS
        elif event.ui_element == self.connections_element.get("birth_parent"):
            self.open_connection = "parent"
            self.connections_element["birth_parent"].disable()
            self.connections_element["adopt_parent"].enable()
            self.connections_element["mate"].enable()

            self.connections_element["text"].set_text(
                "screens.event_edit.new_cat_parent_info"
            )
            self.editor_container.on_contained_elements_changed(
                self.connections_element["text"]
            )
            self.connections_element["display"].set_text(
                f"chosen cats: {self.selected_new_cat_info['parent']}"
            )

            self.connections_element["cat_list"].set_selected_list(
                self.selected_new_cat_info["parent"].copy()
            )
            used_cats = (
                self.selected_new_cat_info["adoptive"]
                + self.selected_new_cat_info["mate"]
            )
            for cat, button in self.connections_element["cat_list"].buttons.items():
                if cat in used_cats:
                    button.disable()
                else:
                    button.enable()

        elif event.ui_element == self.connections_element.get("adopt_parent"):
            self.open_connection = "adoptive"
            self.connections_element["birth_parent"].enable()
            self.connections_element["adopt_parent"].disable()
            self.connections_element["mate"].enable()

            self.connections_element["text"].set_text(
                "screens.event_edit.new_cat_adoptive_info"
            )
            self.editor_container.on_contained_elements_changed(
                self.connections_element["text"]
            )
            self.connections_element["display"].set_text(
                f"chosen cats: {self.selected_new_cat_info['adoptive']}"
            )

            self.connections_element["cat_list"].set_selected_list(
                self.selected_new_cat_info["adoptive"].copy()
            )
            used_cats = (
                self.selected_new_cat_info["parent"]
                + self.selected_new_cat_info["mate"]
            )
            for cat, button in self.connections_element["cat_list"].buttons.items():
                if cat in used_cats:
                    button.disable()
                else:
                    button.enable()
        elif event.ui_element == self.connections_element.get("mate"):
            self.open_connection = "mate"
            self.connections_element["birth_parent"].enable()
            self.connections_element["adopt_parent"].enable()
            self.connections_element["mate"].disable()

            self.connections_element["text"].set_text(
                "screens.event_edit.new_cat_mate_info"
            )
            self.editor_container.on_contained_elements_changed(
                self.connections_element["text"]
            )
            self.connections_element["display"].set_text(
                f"chosen cats: {self.selected_new_cat_info['mate']}"
            )

            self.connections_element["cat_list"].set_selected_list(
                self.selected_new_cat_info["mate"].copy()
            )
            used_cats = (
                self.selected_new_cat_info["adoptive"]
                + self.selected_new_cat_info["parent"]
            )
            for cat, button in self.connections_element["cat_list"].buttons.items():
                if cat in used_cats:
                    button.disable()
                else:
                    button.enable()
        else:
            self.handle_main_and_random_cat_events(event)
            self.update_new_cat_tags()

    def handle_main_and_random_cat_events(self, event):
        # DIES
        if event.ui_element == self.death_element.get("checkbox"):
            checked = event.ui_element.checked
            if not checked:
                event.ui_element.check()
            else:
                event.ui_element.uncheck()
            self.current_cat_dict["dies"] = event.ui_element.checked
            self.death_element["display"].set_text(f"dies: {event.ui_element.checked}")

        # REL STATUS CHECKBOXES
        elif event.ui_element in self.rel_status_checkbox.values():
            event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
            for info in self.rel_tag_list:
                if event.ui_element == self.rel_status_checkbox.get(info["tag"]):
                    index = self.rel_tag_list.index(info)
                    self.rel_tag_list[index] = {
                        "tag": info["tag"],
                        "setting": False if info["setting"] else True,
                        "conflict": info["conflict"],
                    }

                    # flip the setting of any conflicting tags
                    if info["conflict"]:
                        for tag in info["conflict"]:
                            conflict_info = [
                                block
                                for block in self.rel_tag_list
                                if tag == block["tag"]
                            ][0]
                            conflict_index = self.rel_tag_list.index(conflict_info)
                            if not info[
                                "setting"
                            ]:  # unchecks if conflicted setting is checked
                                self.rel_status_checkbox[tag].uncheck()
                            self.rel_tag_list[conflict_index] = {
                                "tag": conflict_info["tag"],
                                "setting": False,
                                "conflict": conflict_info["conflict"],
                            }

                    self.update_rel_status_info()
                    break
        # REL VALUE BUTTONS
        elif event.ui_element in self.rel_value_element.values():
            for name, button in self.rel_value_element.items():
                if button != event.ui_element:
                    continue
                amount = 0
                value = name
                if "low" in name:
                    value = name.replace("_low_button", "")
                    amount = 10
                elif "mid" in name:
                    value = name.replace("_mid_button", "")
                    amount = 30
                elif "high" in name:
                    value = name.replace("_high_button", "")
                    amount = 50

                # removing tag if it's already present
                remove_tag = None
                for tag in self.current_cat_dict["rel_status"]:
                    if value in tag:
                        remove_tag = tag
                        break
                if remove_tag:
                    self.current_cat_dict["rel_status"].remove(remove_tag)

                self.current_cat_dict["rel_status"].append(f"{value}_{amount}")
                self.rel_value_element[f"{value}_entry"].set_text(str(amount))
                self.update_rel_status_info()

        # SKILL TOGGLE
        elif event.ui_element == self.skill_element.get("allow"):
            self.skill_element["allow"].disable()
            self.skill_element["exclude"].enable()
            self.skill_allowed = True
        elif event.ui_element == self.skill_element.get("exclude"):
            self.skill_element["exclude"].disable()
            self.skill_element["allow"].enable()
            self.skill_allowed = False
        # SKILL LEVELS
        elif event.ui_element in self.level_element.values():
            for name, button in self.level_element.items():
                if button != event.ui_element:
                    continue
                self.chosen_level = name
                self.update_skill_info()
                break

        # TRAIT TOGGLE
        elif event.ui_element == self.trait_element.get("allow"):
            self.trait_element["allow"].disable()
            self.trait_element["exclude"].enable()
            self.trait_allowed = True
            # reset selected list
            self.trait_element["adult"].set_selected_list(
                list(
                    set(self.current_cat_dict["trait"]).intersection(self.adult_traits)
                )
            )
            self.trait_element["kitten"].set_selected_list(
                list(set(self.current_cat_dict["trait"]).intersection(self.kit_traits))
            )

        elif event.ui_element == self.trait_element.get("exclude"):
            self.trait_element["exclude"].disable()
            self.trait_element["allow"].enable()
            self.trait_allowed = False
            # reset selected list
            self.trait_element["adult"].set_selected_list(
                list(
                    set(self.current_cat_dict["not_trait"]).intersection(
                        self.adult_traits
                    )
                )
            )
            self.trait_element["kitten"].set_selected_list(
                list(
                    set(self.current_cat_dict["not_trait"]).intersection(
                        self.kit_traits
                    )
                )
            )

        # BACKSTORY LIST
        elif event.ui_element in (
            self.backstory_element.get("list").buttons.values()
            if self.backstory_element.get("list")
            else []
        ):
            for name, button in self.backstory_element["list"].buttons.items():
                if button != event.ui_element:
                    continue
                chosen_stories = self.current_cat_dict["backstory"]

                if name in chosen_stories:
                    chosen_stories.remove(name)
                    if not set(chosen_stories).intersection(
                        self.backstory_element["list"].selected_list
                    ):
                        chosen_stories.append(self.open_pool)
                else:
                    chosen_stories.append(name)
                    if self.open_pool in chosen_stories:
                        chosen_stories.remove(self.open_pool)
                self.update_backstory_info()
                break

    def handle_settings_events(self, event):
        # CHANGE LOCATION LIST
        if event.ui_element in self.location_element.values():
            biome_list = constants.BIOME_TYPES
            for biome in biome_list:
                if event.ui_element == self.location_element[biome]:
                    self.update_location_info(biome=biome)
                    break
            for camp in [camp for biome in self.all_camps.values() for camp in biome]:
                if event.ui_element == self.location_element.get(camp):
                    self.update_location_info(camp=camp)
                    break

        # CHANGE BASIC TAGS
        elif event.ui_element in self.basic_tag_checkbox.values():
            event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
            for info in self.basic_tag_list:
                if event.ui_element == self.basic_tag_checkbox.get(info["tag"]):
                    index = self.basic_tag_list.index(info)
                    self.basic_tag_list[index] = {
                        "tag": info["tag"],
                        "setting": False if info["setting"] else True,
                        "required_type": info["required_type"],
                        "conflict": info["conflict"],
                    }

                    # flip the setting of any conflicting tags
                    if info["conflict"]:
                        for tag in info["conflict"]:
                            conflict_info = [
                                block
                                for block in self.basic_tag_list
                                if tag == block["tag"]
                            ][0]
                            conflict_index = self.basic_tag_list.index(conflict_info)
                            if not info[
                                "setting"
                            ]:  # unchecks if conflicted setting is checked
                                self.basic_tag_checkbox[tag].uncheck()
                            self.basic_tag_list[conflict_index] = {
                                "tag": conflict_info["tag"],
                                "setting": False,
                                "required_type": conflict_info["required_type"],
                                "conflict": conflict_info["conflict"],
                            }

                    self.update_tag_info()
                    break

        # CHANGE RANK TAGS
        elif event.ui_element in self.rank_tag_checkbox.values():
            event.ui_element.uncheck() if event.ui_element.checked else event.ui_element.check()
            self.update_tag_info()

        # CHANGE ACC CATEGORY
        # individual accs
        elif (
            self.acc_element.get("list")
            and event.ui_element in self.acc_element["list"].buttons.values()
        ):
            for acc, button in self.acc_element["list"].buttons.items():
                if event.ui_element != button:
                    continue
                if acc in self.acc_info:
                    self.acc_info.remove(acc)
                else:
                    self.acc_info.append(acc)
                break
            self.update_acc_info()
        # greater categories
        elif event.ui_element in self.acc_element.values():
            for group, button in self.acc_element.items():
                if event.ui_element != button:
                    continue
                if group != self.open_category:
                    self.open_category = group
                    self.update_acc_list()
                    if group not in self.acc_info:
                        self.acc_info.append(group)
                        self.replace_accs_with_group(group)
                else:
                    if group in self.acc_info:
                        self.acc_info.remove(group)
                        self.open_category = None
                        self.update_acc_list()
                    else:
                        self.replace_accs_with_group(group)
                break
            self.update_acc_info()

    # INFO DISPLAY UPDATES
    def update_block_info(self):
        """
        Update the block's full text display
        """

        attr = self.get_block_attributes()
        if attr["selected"]:
            text = "<br>".join(
                [
                    f"{key}: {value}"
                    for key, value in attr["block_list"][int(attr["selected"])].items()
                ]
            )
        else:
            text = "No block selected"

        if not attr.get("display"):
            return

        attr["display"].set_text(text)

        if self.editor_element.get(f"{self.open_block}_start"):
            self.editor_container.on_contained_elements_changed(
                self.editor_element[f"{self.open_block}_start"]
            )

    def update_future_block_options(self):
        if not self.future_element.get("sub_dropdown"):
            return

        self.selected_future_block_index = (
            self.future_element["block_list"].selected_list.copy()[0]
            if self.future_element["block_list"].selected_list
            else ""
        )
        if self.selected_future_block_index:
            selected_constraints = self.future_block_list[
                int(self.selected_future_block_index)
            ]
        else:
            selected_constraints = self.future_template.copy()

        # TYPE
        self.future_element["type_dropdown"].set_selected_list(
            [selected_constraints["event_type"]]
        )

        # POOL
        pool = selected_constraints["pool"]
        self.future_element["sub_dropdown"].set_selected_list(pool["subtype"].copy())
        self.future_element["sub_display"].set_text(f"subtype: {pool['subtype']}")

        if pool.get("event_id"):
            text = ""
            for event_id in pool["event_id"]:
                text += f"'{event_id}'<br>"
            self.future_element["include_display"].set_text(text)
        if pool.get("excluded_event_id"):
            text = ""
            for event_id in pool.get("excluded_event_id"):
                text += f"'{event_id}'<br>"
            self.future_element["exclude_display"].set_text(text)

        # DELAY
        self.future_element["least_entry"].set_text(
            str(selected_constraints["moon_delay"][0])
        )
        self.future_element["most_entry"].set_text(
            str(selected_constraints["moon_delay"][1])
        )

        # INVOLVED CATS
        if (
            "murder_reveal" in pool["subtype"]
            or (selected_constraints["event_type"] == "misc" and not pool["subtype"])
            and "mur_c" not in selected_constraints["involved_cats"]
        ):
            selected_constraints["involved_cats"] = {
                "m_c": "r_c",
                "mur_c": "m_c",
                "r_c": None,
            }

        self.available_cats = self.get_involved_cats(include_clan=False)
        if "new random cat" not in self.available_cats:
            self.available_cats.append("new random cat")

        self.create_involved_cats_editor(selected_constraints)

        self.update_block_info()

    def update_supply_block_options(self):
        if not self.supply_element.get("adjust_list"):
            return

        self.selected_supply_block_index = (
            self.supply_element["block_list"].selected_list.copy()[0]
            if self.supply_element["block_list"].selected_list
            else ""
        )

        if self.selected_supply_block_index:
            selected_constraints = self.supply_block_list.copy()[
                int(self.selected_supply_block_index)
            ]
        else:
            selected_constraints = self.supply_info.copy()

        # TYPE
        self.supply_element["type_list"].set_selected_list(
            [selected_constraints["type"]]
        )

        # TRIGGER
        self.supply_element["trigger_list"].set_selected_list(
            selected_constraints["trigger"].copy()
        )

        # ADJUST
        self.supply_element["adjust_list"].set_selected_list(
            [selected_constraints["adjust"]]
        )
        self.create_supply_increase_editor()
        self.update_block_info()

    def update_relationships_block_options(self):
        if not self.relationships_element.get("amount_down_high_button"):
            return

        self.selected_relationships_block_index = (
            self.relationships_element["block_list"].selected_list.copy()[0]
            if self.relationships_element["block_list"].selected_list
            else ""
        )
        if self.selected_relationships_block_index:
            selected_constraints = self.relationships_block_list.copy()[
                int(self.selected_relationships_block_index)
            ]
        else:
            selected_constraints = self.relationships_template.copy()

        # MUTUAL
        if (
            self.relationships_element["mutual"].checked
            and not selected_constraints["mutual"]
        ):
            self.relationships_element["mutual"].uncheck()
            self.relationships_element["cat_bridge_info"].set_text(
                "screens.event_edit.relationships_one_way"
            )
        elif (
            not self.relationships_element["mutual"].checked
            and selected_constraints["mutual"]
        ):
            self.relationships_element["mutual"].check()
            self.relationships_element["cat_bridge_info"].set_text(
                "screens.event_edit.relationships_mutual"
            )

        # CATS
        self.relationships_element["cats_from_list"].set_selected_list(
            selected_constraints["cats_from"].copy()
        )
        self.relationships_element["cats_from_info"].set_text(
            f"cats: {selected_constraints['cats_from']}"
        )
        for name, button in self.relationships_element[
            "cats_from_list"
        ].buttons.items():
            if name in selected_constraints["cats_to"]:
                button.disable()
            else:
                button.enable()

        self.relationships_element["cats_to_list"].set_selected_list(
            selected_constraints["cats_to"].copy()
        )
        self.relationships_element["cats_to_info"].set_text(
            f"cats: {selected_constraints['cats_to']}"
        )
        for name, button in self.relationships_element["cats_to_list"].buttons.items():
            if name in selected_constraints["cats_from"]:
                button.disable()
            else:
                button.enable()

        # VALUES
        self.relationships_element["values_list"].set_selected_list(
            selected_constraints["values"].copy()
        )
        self.relationships_element["values_info"].set_text(
            f"values: {selected_constraints['values']}"
        )

        # AMOUNT
        self.relationships_element["amount_entry"].set_text(
            str(selected_constraints["amount"])
        )

        self.update_block_info()

    def update_history_block_options(self):
        if not self.history_element.get("lead_history_input"):
            return

        self.selected_history_block_index = (
            self.history_element["block_list"].selected_list.copy()[0]
            if self.history_element["block_list"].selected_list
            else ""
        )
        if self.selected_history_block_index:
            selected_constraints = self.history_block_list.copy()[
                int(self.selected_history_block_index)
            ]
        else:
            selected_constraints = self.history_template.copy()

        # CATS
        self.history_element["cats_list"].set_selected_list(
            selected_constraints["cats"].copy()
        )
        self.history_element["cats_info"].set_text(
            f"cats: {selected_constraints['cats']}"
        )

        # SCAR
        self.history_element["scar_history_input"].set_text(
            selected_constraints["scar"]
        )

        # REG_DEATH
        self.history_element["reg_history_input"].set_text(
            selected_constraints["reg_death"]
        )

        # LEAD_DEATH
        self.history_element["lead_history_input"].set_text(
            selected_constraints["lead_death"]
        )

        self.update_block_info()

    def update_injury_block_options(self):
        if not self.injury_element.get("scar_info"):
            return
        self.selected_injury_block = (
            self.injury_element["block_list"].selected_list.copy()[0]
            if self.injury_element["block_list"].selected_list
            else ""
        )
        if self.selected_injury_block:
            selected_constraints = self.injury_block_list.copy()[
                int(self.selected_injury_block)
            ]
        else:
            selected_constraints = self.injury_template.copy()

        # CATS
        self.injury_element["cats_list"].set_selected_list(
            selected_constraints["cats"].copy()
        )
        self.injury_element["cats_info"].set_text(
            f"cats: {selected_constraints['cats']}"
        )

        # INJURIES
        all_injuries = selected_constraints["injuries"]
        pools = []
        injuries = []
        for inj in all_injuries:
            if inj in self.all_injury_pools:
                pools.append(inj)
                continue
            if inj in self.all_possible_injuries:
                injuries.append(inj)

        self.injury_element["injury_pools"].set_selected_list(pools)
        self.injury_element["individual_injuries"].set_selected_list(injuries)
        self.injury_element["injury_info"].set_text(f"injuries: {all_injuries}")

        # SCARS
        self.injury_element["scar_list"].set_selected_list(
            selected_constraints["scars"]
        )
        self.injury_element["scar_info"].set_text(
            f"scars: {selected_constraints['scars']}"
        )

        self.update_block_info()

    def update_new_cat_options(self):
        if not self.selected_new_cat:
            return
        # BOOLS
        for info in self.new_cat_bools:
            if (
                info["tag"] in self.new_cat_block_dict[self.selected_new_cat]
                and not info["setting"]
            ):
                info["setting"] = True
                self.new_cat_checkbox[info["tag"]].check()
            elif (
                info["tag"] not in self.new_cat_block_dict[self.selected_new_cat]
                and info["setting"]
            ):
                info["setting"] = False
                self.new_cat_checkbox[info["tag"]].uncheck()

        # AVAILABLE CATS
        self.connections_element["cat_list"].new_item_list(
            self.get_involved_cats(
                index_limit=int(self.selected_new_cat.strip("n_c:"), False)
            )
        )

        # EVERYTHING ELSE
        cat_type = []
        stories = []
        pool = []
        rank = []
        age = []
        gender = []
        parent = []
        adopt = []
        mate = []

        for tag in self.new_cat_block_dict[self.selected_new_cat]:
            if tag in self.new_cat_types:
                cat_type = [tag]
            elif "backstory" in tag:
                stories = tag.replace("backstory:", "")
                stories = stories.split(",")
                if not isinstance(stories, list):
                    stories = [stories]
                if stories:
                    for pool_name in self.all_backstories:
                        if pool_name in stories:
                            pool = pool_name
                else:
                    pool = []
            elif "status" in tag:
                rank = [tag.replace("status:", "")]
            elif "age" in tag:
                age = [tag.replace("age:", "")]
            elif tag in self.new_cat_genders:
                gender = [tag]
            elif "parent" in tag:
                parent = tag.replace("parent:", "").split(",")
            elif "adoptive" in tag:
                adopt = tag.replace("adoptive:", "").split(",")
            elif "mate" in tag:
                mate = tag.replace("mate:", "").split(",")

        self.cat_story_element["list"].set_selected_list(cat_type)
        self.backstory_element["pools"].set_selected_list(pool)
        self.backstory_element["list"].set_selected_list(stories)
        self.new_status_element["list"].set_selected_list(rank)
        self.new_age_element["list"].set_selected_list(age)
        self.new_gender_element["list"].set_selected_list(gender)
        if self.open_connection == "parent":
            self.connections_element["cat_list"].set_selected_list(parent)
        elif self.open_connection == "adoptive":
            self.connections_element["cat_list"].set_selected_list(adopt)
        elif self.open_connection == "mate":
            self.connections_element["cat_list"].set_selected_list(mate)

    def update_new_cat_tags(self):
        if not self.selected_new_cat:
            return

        selected_cat_info = self.new_cat_block_dict[self.selected_new_cat]

        # BOOL TAGS
        for bool in self.new_cat_bools:
            if bool["setting"] and bool["tag"] not in selected_cat_info:
                selected_cat_info.append(bool["tag"])
            elif not bool["setting"] and bool["tag"] in selected_cat_info:
                selected_cat_info.remove(bool["tag"])

        # CAT TYPES
        selected_type = (
            self.cat_story_element["list"].selected_list[0]
            if self.cat_story_element["list"].selected_list
            else None
        )

        for cat_type in self.new_cat_types:
            if cat_type == selected_type and cat_type not in selected_cat_info:
                selected_cat_info.append(selected_type)
            if cat_type != selected_type and cat_type in selected_cat_info:
                selected_cat_info.remove(cat_type)

        # BACKSTORIES
        possible_stories = list(self.all_backstories.keys()) + self.individual_stories
        chosen_stories = set(possible_stories).intersection(
            self.selected_new_cat_info["backstory"]
        )

        new_story_tag = None
        if chosen_stories:
            new_story_tag = f"backstory:{','.join(chosen_stories)}"

        existing_tag = False
        for tag in selected_cat_info.copy():
            if "backstory" in tag and tag != new_story_tag:
                existing_tag = True
                selected_cat_info.remove(tag)
                break
            elif tag == new_story_tag:
                existing_tag = True
                break
            existing_tag = False

        if new_story_tag and not existing_tag:
            selected_cat_info.append(new_story_tag)

        # RANK
        if self.new_status_element["list"].selected_list:
            rank = self.new_status_element["list"].selected_list[0]
        else:
            rank = None

        new_rank_tag = f"status:{rank}" if rank else None

        existing_tag = False
        for tag in selected_cat_info.copy():
            if "status" in tag and tag != new_rank_tag:
                existing_tag = True
                selected_cat_info.remove(tag)
                break
            elif tag == new_rank_tag:
                existing_tag = True
                break
            existing_tag = False

        if new_rank_tag and not existing_tag:
            selected_cat_info.append(new_rank_tag)

        # AGE
        if self.new_age_element["list"].selected_list:
            age = self.new_age_element["list"].selected_list[0]
        else:
            age = None

        new_age_tag = f"age:{age}" if age else None

        existing_tag = False
        for tag in selected_cat_info.copy():
            if "age" in tag and tag != new_age_tag:
                existing_tag = True
                selected_cat_info.remove(tag)
                break
            elif tag == new_age_tag:
                existing_tag = True
                break
            existing_tag = False

        if new_age_tag and not existing_tag:
            selected_cat_info.append(new_age_tag)

        # GENDER
        if self.new_gender_element["list"].selected_list:
            gender = self.new_gender_element["list"].selected_list[0]
        else:
            gender = None

        if gender and gender not in selected_cat_info:
            for option in self.new_cat_genders:
                if option in selected_cat_info:
                    selected_cat_info.remove(option)
            selected_cat_info.append(gender)

        elif not gender:
            for option in self.new_cat_genders:
                if option in selected_cat_info:
                    selected_cat_info.remove(option)

        # CAT CONNECTIONS
        if self.connections_element["cat_list"].selected_list:
            connections = self.connections_element["cat_list"].selected_list
        else:
            connections = []

        new_tag = None
        if connections:
            new_tag = f"{self.open_connection}:{','.join(connections)}"

        if new_tag and new_tag not in selected_cat_info:
            for tag in selected_cat_info.copy():
                if self.open_connection in tag:
                    selected_cat_info.remove(tag)
                    break
            selected_cat_info.append(new_tag)

        elif not new_tag:
            for tag in selected_cat_info.copy():
                if self.open_connection in tag:
                    selected_cat_info.remove(tag)

        if (
            self.new_cat_editor["display"].html_text
            != f"selected cat: {selected_cat_info}"
        ):
            self.new_cat_editor["display"].set_text(
                f"selected cat: {selected_cat_info}"
            )

        self.editor_container.on_contained_elements_changed(
            self.new_cat_editor["display"]
        )

    def update_backstory_info(self):
        chosen_stories = self.current_cat_dict["backstory"]

        if self.open_pool:
            pool = self.all_backstories[self.open_pool]

            # pool category added only if none of its stories have been selected
            if self.open_pool not in chosen_stories and not set(
                chosen_stories
            ).intersection(set(pool)):
                chosen_stories.append(self.open_pool)

        self.backstory_element["display"].set_text(
            f"chosen backstory: {chosen_stories}"
        )
        self.editor_container.on_contained_elements_changed(
            self.backstory_element["display"]
        )

    def update_trait_info(self, trait_dict, selected_list):
        saved_traits = "trait" if self.trait_allowed else "not_trait"
        if saved_traits not in self.current_cat_dict.keys():
            return

        if self.current_cat_dict.get(saved_traits):
            selected_traits = set(self.current_cat_dict.get(saved_traits)).intersection(
                trait_dict
            )
        else:
            selected_traits = []
        if selected_list != selected_traits:
            removed = [trait for trait in selected_traits if trait not in selected_list]
            added = [trait for trait in selected_list if trait not in selected_traits]
            if removed:
                for trait in removed:
                    self.current_cat_dict[saved_traits].remove(trait)
            if added:
                self.current_cat_dict[saved_traits].extend(added)

        if self.trait_allowed:
            self.trait_element["include_info"].set_text(
                f"chosen allowed traits: {self.current_cat_dict.get('trait')}"
            )
            self.editor_container.on_contained_elements_changed(
                self.trait_element["include_info"]
            )
        else:
            self.trait_element["exclude_info"].set_text(
                f"chosen excluded traits: {self.current_cat_dict.get('not_trait')}"
            )
            self.editor_container.on_contained_elements_changed(
                self.trait_element["exclude_info"]
            )

    def update_skill_info(self):
        skill_tag = f"{self.open_path},{self.chosen_level if self.chosen_level else 0}"

        if self.skill_allowed:
            already_tagged = [
                tag for tag in self.current_cat_dict["skill"] if self.open_path in tag
            ]
            if already_tagged:
                self.current_cat_dict["skill"].remove(already_tagged[0])
            if self.chosen_level:
                self.current_cat_dict["skill"].append(skill_tag)
            self.skill_element["include_info"].set_text(
                f"chosen allowed skills: {self.current_cat_dict['skill']}"
            )
            self.editor_container.on_contained_elements_changed(
                self.skill_element["include_info"]
            )
        else:
            already_tagged = [
                tag
                for tag in self.current_cat_dict["not_skill"]
                if self.open_path in tag
            ]
            if already_tagged:
                self.current_cat_dict["not_skill"].remove(already_tagged[0])
            if self.chosen_level:
                self.current_cat_dict["not_skill"].append(skill_tag)
            self.skill_element["exclude_info"].set_text(
                f"chosen excluded skills: {self.current_cat_dict['not_skill']}"
            )
            self.editor_container.on_contained_elements_changed(
                self.skill_element["exclude_info"]
            )

    def update_rel_status_info(self):
        for info in self.rel_tag_list:
            if (
                info["tag"] not in self.current_cat_dict["rel_status"]
                and info["setting"]
            ):
                self.current_cat_dict["rel_status"].append(info["tag"])
            elif (
                info["tag"] in self.current_cat_dict["rel_status"]
                and not info["setting"]
            ):
                self.current_cat_dict["rel_status"].remove(info["tag"])

        if self.rel_status_element.get("display"):
            self.rel_status_element["display"].set_text(
                f"chosen relationship_status: {self.current_cat_dict['rel_status']}"
            )
            self.editor_container.on_contained_elements_changed(
                self.rel_status_element["display"]
            )

    def replace_accs_with_group(self, group):
        for category_name, accs in self.acc_categories.items():
            if group == category_name:
                for acc in set(self.acc_info).intersection(set(accs)):
                    self.acc_info.remove(acc)
                break

        if group not in self.acc_info:
            self.acc_info.append(group)

    def update_acc_info(self):
        if self.acc_info:
            for (
                category_name,
                accs,
            ) in self.acc_categories.items():
                if category_name in self.acc_info and set(self.acc_info).intersection(
                    set(accs)
                ):
                    self.acc_info.remove(category_name)
                    break
            self.acc_element["display"].set_text(f"chosen accessories: {self.acc_info}")
        else:
            self.acc_element["display"].set_text(f"chosen accessories: []")

        self.editor_container.on_contained_elements_changed(self.acc_element["display"])

    def update_tag_info(self):
        for info in self.basic_tag_list:
            if info["tag"] not in self.tag_info and info["setting"]:
                self.tag_info.append(info["tag"])
            elif info["tag"] in self.tag_info and not info["setting"]:
                self.tag_info.remove(info["tag"])

        for rank, box in self.rank_tag_checkbox.items():
            if "text" in rank:
                continue
            tag = f"clan:{rank}"
            if box.checked and tag not in self.tag_info:
                self.tag_info.append(tag)
            elif not box.checked and tag in self.tag_info:
                self.tag_info.remove(tag)

        if self.tag_element.get("display"):
            self.tag_element["display"].set_text(f"chosen tags: {self.tag_info}")
            self.editor_container.on_contained_elements_changed(
                self.tag_element["display"]
            )

    def update_location_info(self, biome=None, camp=None):
        if biome:
            biome = biome.casefold()
            present = False
            for location in self.location_info:
                if biome in location:
                    present = True
                    break
            if not present:
                self.location_info.append(biome)
                self.update_camp_list(biome.capitalize())

            else:
                for location in self.location_info:
                    if biome in location:
                        self.location_info.remove(location)
                        self.update_camp_list(None)
                        break

        if camp:
            present = True
            parent_biome = None
            camp_index = 0
            old_location_tag = None
            new_string = None

            for camp_biome in self.all_camps.keys():
                if camp in self.all_camps[camp_biome]:
                    parent_biome = camp_biome
                    camp_index = self.all_camps[camp_biome].index(camp) + 1
                    break

            for location in self.location_info:
                if parent_biome.casefold() in location:
                    if f"camp{camp_index}" in location:
                        break
                    else:
                        new_string = f"{location}_camp{camp_index}"
                        selected_camps = [
                            camp for camp in new_string.split("_") if "camp" in camp
                        ]
                        available_camps = len(self.all_camps[parent_biome])
                        if len(selected_camps) == available_camps:
                            new_string = f"{parent_biome.casefold()}"
                        present = False
                        old_location_tag = location
                        break
            if not present:
                self.location_info.remove(old_location_tag)
                self.location_info.append(new_string.casefold())
            else:
                for location in self.location_info:
                    if parent_biome.casefold() in location:
                        old_location_tag = location
                        new_string = location.replace(f"_camp{camp_index}", "")
                        break
                self.location_info.remove(old_location_tag)
                self.location_info.append(new_string)

        self.location_element["display"].set_text(
            (
                f"chosen location: {str(self.location_info)}"
                if self.location_info
                else "chosen location: ['any']"
            )
        )
        self.editor_container.on_contained_elements_changed(
            self.location_element["display"]
        )

    def update_season_info(self):
        if self.season_info:
            self.season_element["display"].set_text(
                f"chosen season: {self.season_info}"
            )
        else:
            self.season_element["display"].set_text("chosen season: ['any']")

    def update_sub_info(self):
        if "accessory" not in self.sub_info:
            for group in self.acc_categories.keys():
                self.acc_element[group].disable()
                if self.acc_element.get("list"):
                    self.acc_element["list"].kill()
                self.acc_info.clear()
                self.update_acc_info()

        if self.sub_info:
            if "accessory" in self.sub_info:
                for group in self.acc_categories.keys():
                    self.acc_element[group].enable()

            self.type_element["display"].set_text(f"chosen subtypes: {self.sub_info}")
        else:
            self.type_element["display"].set_text("chosen subtypes: []")

    # ON USE FUNCS
    def handle_future_on_use(self):
        # FUTURE CONSTRAINT DISPLAY
        if self.selected_future_block_index and not self.future_element.get(
            "m_c_involved_dropdown"
        ):
            self.display_future_constraints()
        elif not self.selected_future_block_index:
            self.clear_future_constraints()
        # SELECT NEW FUTURE BLOCK
        if self.future_element.get(
            "block_list"
        ).selected_list and not self.future_element.get("m_c_involved_dropdown"):
            self.display_future_constraints()
        if self.future_element.get("m_c_involved_dropdown"):
            selected_block = (
                [str(self.selected_future_block_index)]
                if self.selected_future_block_index
                else []
            )
            if self.future_element["block_list"].selected_list != selected_block:
                self.update_future_block_options()

        if not self.future_element.get("m_c_involved_dropdown"):
            return
        block_info = self.get_selected_block_info()

        # TYPE CHANGE
        if (
            self.future_element.get("type_dropdown")
            and self.future_element["type_dropdown"].selected_list[0]
            != block_info["event_type"]
        ):
            # update block info
            block_info["event_type"] = self.future_element[
                "type_dropdown"
            ].selected_list.copy()[0]
            # update available subtypes
            self.future_element["sub_dropdown"].set_selected_list([])
            self.future_element["sub_dropdown"].new_item_list(
                self.event_types[block_info["event_type"]]
            )
            block_info["pool"]["subtype"] = []

        # SUB CHANGE
        elif (
            self.future_element.get("sub_dropdown")
            and self.future_element["sub_dropdown"].selected_list
            != block_info["pool"]["subtype"]
        ):
            # update block info
            block_info["pool"]["subtype"] = self.future_element[
                "sub_dropdown"
            ].selected_list.copy()
            # update display
            self.future_element["sub_display"].set_text(
                f"subtype:{block_info['pool']['subtype']}"
            )

            if "murder_reveal" in block_info["pool"]["subtype"]:
                block_info["involved_cats"] = {
                    "m_c": "r_c",
                    "mur_c": "m_c",
                    "r_c": None,
                }
            else:
                block_info["involved_cats"] = {"m_c": None, "r_c": None}
            self.create_involved_cats_editor()

        # INVOLVED CATS
        else:
            for cat in block_info["involved_cats"]:
                if (
                    self.future_element[f"{cat}_involved_dropdown"].selected_list
                    != block_info["involved_cats"][cat]
                ):
                    block_info["involved_cats"][cat] = self.future_element[
                        f"{cat}_involved_dropdown"
                    ].selected_list.copy()[0]

    def handle_outside_on_use(self):
        # SUPPLY CONSTRAINT DISPLAY
        if self.selected_supply_block_index and not self.supply_element.get(
            "constraint_container"
        ):
            self.display_supply_constraints()
        elif not self.selected_supply_block_index:
            self.clear_supply_constraints()
        # SELECT NEW SUPPLY BLOCK
        if self.supply_element.get(
            "block_list"
        ).selected_list and not self.supply_element.get("adjust_list"):
            self.display_supply_constraints()
        if self.supply_element.get("adjust_list"):
            selected_block = (
                [str(self.selected_supply_block_index)]
                if self.selected_supply_block_index
                else []
            )
            if self.supply_element["block_list"].selected_list != selected_block:
                self.update_supply_block_options()
        # OUTSIDER
        if self.outsider_element.get("list"):
            if (
                self.outsider_element["list"].selected_list
                != self.outsider_info["current_rep"]
            ):
                self.outsider_info["current_rep"] = self.outsider_element[
                    "list"
                ].selected_list.copy()
                self.outsider_element["display"].set_text(f"{self.outsider_info}")
        # OTHER CLAN
        if self.other_clan_element.get("list"):
            if (
                self.other_clan_element["list"].selected_list
                != self.other_clan_info["current_rep"]
            ):
                self.other_clan_info["current_rep"] = self.other_clan_element[
                    "list"
                ].selected_list.copy()
                self.other_clan_element["display"].set_text(f"{self.other_clan_info}")
        # SUPPLY TYPE
        changed = False
        selected_info = self.get_selected_block_info()
        if self.supply_element.get("adjust_list"):
            new_type = [selected_info["type"]] if selected_info["type"] else []
            new_adjust = [selected_info["adjust"]] if selected_info["adjust"] else []

            # TYPE
            if self.supply_element["type_list"].selected_list != new_type:
                selected_info["type"] = (
                    self.supply_element["type_list"].selected_list[0]
                    if self.supply_element["type_list"].selected_list
                    else ""
                )
                changed = True

            # TRIGGER
            elif (
                self.supply_element["trigger_list"].selected_list
                != selected_info["trigger"]
            ):
                selected_info["trigger"] = self.supply_element[
                    "trigger_list"
                ].selected_list.copy()
                changed = True

            # ADJUST
            elif self.supply_element["adjust_list"].selected_list != new_adjust:
                # gotta be a little careful here, since the "increase" tag changes upon user input
                new_tag = (
                    self.supply_element["adjust_list"].selected_list.copy()[0]
                    if self.supply_element["adjust_list"].selected_list
                    else ""
                )
                tag_change = True
                if "increase_" in new_tag and "increase_" in selected_info["adjust"]:
                    tag_change = False

                if tag_change:
                    selected_info["adjust"] = new_tag

                self.create_supply_increase_editor()
                changed = True
        if changed:
            self.update_block_info()

    def handle_personal_on_use(self):
        # EXCLUDE
        if self.exclusion_element.get("cat_list"):
            if self.exclusion_element["cat_list"].selected_list != self.excluded_cats:
                self.excluded_cats = self.exclusion_element[
                    "cat_list"
                ].selected_list.copy()
                self.exclusion_element["display"].set_text(
                    f"exclude_involved: {self.excluded_cats}"
                )

        changed = False

        if self.open_block == "injury":
            # CONSTRAINT DISPLAY
            if self.selected_injury_block and not self.injury_element.get(
                "constraint_container"
            ):
                self.display_injury_constraints()
            elif not self.selected_injury_block:
                self.clear_injury_constraints()

            # SELECT NEW BLOCK
            if self.injury_element.get("scar_list"):
                selected_injury = (
                    [str(self.selected_injury_block)]
                    if self.selected_injury_block
                    else []
                )
                if self.injury_element["block_list"].selected_list != selected_injury:
                    self.update_injury_block_options()

            # CAT LIST
            if self.injury_element.get("cats_list"):
                selected_info = self.get_selected_block_info()
                if (
                    self.injury_element["cats_list"].selected_list
                    != selected_info["cats"]
                ):
                    selected_info["cats"] = self.injury_element[
                        "cats_list"
                    ].selected_list.copy()
                    self.injury_element["cats_info"].set_text(
                        f"cats: {selected_info['cats']}"
                    )
                    self.injury_element[
                        "constraint_container"
                    ].on_contained_elements_changed(self.injury_element["cats_info"])
                    changed = True

            # INJURY LIST
            if self.injury_element.get("individual_injuries"):
                full_selection = (
                    self.injury_element["injury_pools"].selected_list
                    + self.injury_element["individual_injuries"].selected_list
                )
                selected_info = self.get_selected_block_info()
                if full_selection != selected_info["injuries"]:
                    selected_info["injuries"] = full_selection
                    self.injury_element["injury_info"].set_text(
                        f"injuries: {full_selection}"
                    )
                    self.injury_element[
                        "constraint_container"
                    ].on_contained_elements_changed(self.injury_element["injury_info"])
                    changed = True

            # SCAR LIST
            if self.injury_element.get("scar_list"):
                selected_info = self.get_selected_block_info()
                if (
                    self.injury_element["scar_list"].selected_list
                    != selected_info["injuries"]
                ):
                    selected_info["scars"] = self.injury_element[
                        "scar_list"
                    ].selected_list.copy()
                    self.injury_element["scar_info"].set_text(
                        f"scars: {selected_info['scars']}"
                    )
                    self.injury_element[
                        "constraint_container"
                    ].on_contained_elements_changed(self.injury_element["scar_info"])
                    changed = True

        elif self.open_block == "history":
            # CONSTRAINT DISPLAY
            if self.selected_history_block_index and not self.history_element.get(
                "constraint_container"
            ):
                self.display_history_constraints()
            elif not self.selected_history_block_index:
                self.clear_history_constraints()

            # SELECT NEW BLOCK
            if self.history_element.get("lead_history_input"):
                selected_history = (
                    [str(self.selected_history_block_index)]
                    if self.selected_history_block_index
                    else []
                )
                if self.history_element["block_list"].selected_list != selected_history:
                    self.update_history_block_options()

            # CAT LIST
            if self.history_element.get("cats_list"):
                selected_info = self.get_selected_block_info()
                used_cats = []
                for block in self.history_block_list:
                    used_cats.extend(block["cats"])
                if (
                    self.history_element["cats_list"].selected_list
                    != selected_info["cats"]
                ):
                    selected_info["cats"] = self.history_element[
                        "cats_list"
                    ].selected_list.copy()
                    self.history_element["cats_info"].set_text(
                        f"cats: {selected_info['cats']}"
                    )
                    self.history_element[
                        "constraint_container"
                    ].on_contained_elements_changed(self.history_element["cats_info"])
                    changed = True

                for name, button in self.history_element["cats_list"].buttons.items():
                    if name in used_cats and name not in selected_info["cats"]:
                        button.disable()
                    else:
                        button.enable()

            # TEXT ENTRY
            if self.history_element.get("scar_history_input"):
                selected_info = self.get_selected_block_info()
                if (
                    selected_info["scar"]
                    != self.history_element["scar_history_input"].get_text()
                ):
                    selected_info["scar"] = self.history_element[
                        "scar_history_input"
                    ].get_text()
                    changed = True
            if self.history_element.get("reg_history_input"):
                selected_info = self.get_selected_block_info()
                if (
                    selected_info["reg_death"]
                    != self.history_element["reg_history_input"].get_text()
                ):
                    selected_info["reg_death"] = self.history_element[
                        "reg_history_input"
                    ].get_text()
                    changed = True
            if self.history_element.get("lead_history_input"):
                selected_info = self.get_selected_block_info()
                if (
                    selected_info["lead_death"]
                    != self.history_element["lead_history_input"].get_text()
                ):
                    selected_info["lead_death"] = self.history_element[
                        "lead_history_input"
                    ].get_text()
                    changed = True

        elif self.open_block == "relationships":
            # CONSTRAINT DISPLAY
            if (
                self.selected_relationships_block_index
                and not self.relationships_element.get("constraint_container")
            ):
                self.display_relationships_constraints()
            elif not self.selected_relationships_block_index:
                self.clear_relationships_constraints()

            if self.relationships_element.get("amount_down_high_button"):
                selected_relationship = (
                    [str(self.selected_relationships_block_index)]
                    if self.selected_relationships_block_index
                    else []
                )
                selected_info = self.get_selected_block_info()

                # SELECT NEW BLOCK
                if (
                    self.relationships_element["block_list"].selected_list
                    != selected_relationship
                ):
                    self.update_relationships_block_options()

                # CAT LIST
                elif (
                    self.relationships_element["cats_from_list"].selected_list
                    != selected_info["cats_from"]
                ):
                    selected_info["cats_from"] = self.relationships_element[
                        "cats_from_list"
                    ].selected_list.copy()
                    for name, button in self.relationships_element[
                        "cats_to_list"
                    ].buttons.items():
                        if name in selected_info["cats_from"]:
                            button.disable()
                        else:
                            button.enable()
                    self.relationships_element["cats_from_info"].set_text(
                        f"cats: {selected_info['cats_from']}"
                    )
                    self.relationships_element[
                        "constraint_container"
                    ].on_contained_elements_changed(
                        self.relationships_element["cats_from_info"]
                    )
                    changed = True
                elif (
                    self.relationships_element["cats_to_list"].selected_list
                    != selected_info["cats_to"]
                ):
                    selected_info["cats_to"] = self.relationships_element[
                        "cats_to_list"
                    ].selected_list.copy()
                    for name, button in self.relationships_element[
                        "cats_from_list"
                    ].buttons.items():
                        if name in selected_info["cats_to"]:
                            button.disable()
                        else:
                            button.enable()
                    self.relationships_element["cats_to_info"].set_text(
                        f"cats: {selected_info['cats_to']}"
                    )
                    self.relationships_element[
                        "constraint_container"
                    ].on_contained_elements_changed(
                        self.relationships_element["cats_to_info"]
                    )
                    changed = True

                # VALUES
                elif (
                    self.relationships_element["values_list"].selected_list
                    != selected_info["values"]
                ):
                    selected_info["values"] = self.relationships_element[
                        "values_list"
                    ].selected_list.copy()
                    self.relationships_element["values_info"].set_text(
                        f"values: {selected_info['values']}"
                    )
                    changed = True

        if changed:
            self.update_block_info()

    def handle_new_cat_on_use(self):
        # NEW CAT CONSTRAINT DISPLAY
        if self.selected_new_cat and not self.new_cat_element.get("checkbox_container"):
            self.display_new_cat_constraints()

        elif not self.selected_new_cat and self.new_cat_element.get(
            "checkbox_container"
        ):
            self.clear_new_cat_constraints()
        # CHANGE SELECTED CAT
        if self.new_cat_editor.get("cat_list"):
            self.new_cat_select()
        # CAT CONNECTIONS
        if self.connections_element.get("cat_list"):
            new_selection = (
                self.connections_element["cat_list"].selected_list.copy()
                if self.connections_element["cat_list"].selected_list
                else []
            )
            if self.selected_new_cat_info[self.open_connection] != new_selection:
                self.selected_new_cat_info[self.open_connection] = new_selection
                self.connections_element["display"].set_text(
                    f"chosen cats: {new_selection}"
                )
        self.handle_main_and_random_cat_on_use()
        self.update_new_cat_tags()

    def handle_main_and_random_cat_on_use(self):
        # RANKS
        if self.rank_element.get("dropdown") and self.rank_element[
            "dropdown"
        ].selected_list != self.current_cat_dict.get("rank"):
            self.current_cat_dict["rank"] = self.rank_element[
                "dropdown"
            ].selected_list.copy()
            if self.current_cat_dict["rank"]:
                self.rank_element["display"].set_text(
                    f"chosen rank: {self.current_cat_dict['rank']}"
                )
            else:
                self.rank_element["display"].set_text(f"chosen rank: ['any']")
            self.editor_container.on_contained_elements_changed(
                self.rank_element["display"]
            )
        # AGES
        if self.age_element.get("dropdown") and self.age_element[
            "dropdown"
        ].selected_list != self.current_cat_dict.get("age"):
            self.current_cat_dict["age"] = self.age_element[
                "dropdown"
            ].selected_list.copy()

            if self.current_cat_dict["age"]:
                self.age_element["display"].set_text(
                    f"chosen age: {self.current_cat_dict['age']}"
                )
            else:
                self.age_element["display"].set_text(f"chosen age: ['any']")
            self.editor_container.on_contained_elements_changed(
                self.age_element["display"]
            )
        # SKILLS
        if self.skill_element.get("paths"):
            # chosen path has changed
            if (
                self.skill_element["paths"].selected_list
                and self.open_path not in self.skill_element["paths"].selected_list
            ):
                self.open_path = self.skill_element["paths"].selected_list[0]
                self.update_level_list()
            # there is no path selected
            elif not self.skill_element["paths"].selected_list and self.open_path:
                self.chosen_level = None
                self.update_skill_info()
                self.open_path = None
                self.update_level_list()
        # TRAITS
        if self.trait_element.get("adult"):
            combined_selection = self.trait_element["adult"].selected_list.copy()
            combined_selection.extend(self.trait_element["kitten"].selected_list)

            if not combined_selection:
                combined_selection = []

            saved_traits = "trait" if self.trait_allowed else "not_trait"
            if combined_selection != self.current_cat_dict.get(saved_traits):
                self.update_trait_info(
                    self.kit_traits, self.trait_element["kitten"].selected_list
                )
                self.update_trait_info(
                    self.adult_traits, self.trait_element["adult"].selected_list
                )
        # BACKSTORIES
        if self.backstory_element.get("pools"):
            selected_list = self.backstory_element["pools"].selected_list

            if not self.open_pool and not selected_list:
                self.backstory_element["list"].new_item_list([])
                self.update_backstory_info()

            # pool has changed
            elif selected_list and self.open_pool not in selected_list:
                self.open_pool = selected_list[0]
                self.backstory_element["list"].new_item_list(
                    self.all_backstories[self.open_pool]
                )

                for name, button in self.backstory_element["list"].buttons.items():
                    button.set_tooltip(f"cat.backstories.{name}")
                self.update_backstory_info()

            # there is no pool selected
            elif not selected_list and self.open_pool:
                if self.open_pool in self.current_cat_dict["backstory"]:
                    self.current_cat_dict["backstory"].remove(self.open_pool)

                singles_to_remove = set(
                    self.current_cat_dict["backstory"]
                ).intersection(set(self.all_backstories[self.open_pool]))
                if singles_to_remove:
                    for story in singles_to_remove:
                        self.current_cat_dict["backstory"].remove(story)

                self.open_pool = None
                self.backstory_element["list"].new_item_list([])
                self.update_backstory_info()

    def handle_settings_on_use(self):
        # CHANGE TYPE
        if (
            self.type_element.get("type_dropdown")
            and self.type_element["type_dropdown"].selected_list != self.type_info
        ):
            new_type = self.type_element["type_dropdown"].selected_list[0]
            self.type_element["type_dropdown"].parent_button.set_text(new_type)
            self.type_info = [new_type]
            self.sub_info.clear()
            self.update_sub_info()
            self.update_sub_buttons(self.event_types.get(new_type))
            self.update_basic_checkboxes()
        # CHANGE SUBTYPES
        if (
            self.type_element.get("subtype_dropdown")
            and self.type_element["subtype_dropdown"].selected_list != self.sub_info
        ):
            self.sub_info = self.type_element["subtype_dropdown"].selected_list.copy()
            self.update_sub_info()
        # CHANGE SEASONS
        if (
            self.season_element.get("dropdown")
            and self.season_element["dropdown"].selected_list != self.season_info
        ):
            self.season_info = self.season_element["dropdown"].selected_list.copy()
            self.update_season_info()

    # FUTURE EFFECTS EDITOR
    def generate_future_tab(self):
        self.open_block = "future"

        self.future_element["text"] = UITextBoxTweaked(
            "screens.event_edit.future_info",
            ui_scale(pygame.Rect((0, 10), (295, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )

        self.future_element["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 186))),
            get_box(BoxStyles.FRAME, (112, 186)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"left_target": self.future_element["text"]},
        )

        self.future_element["block_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 168)),
            item_list=(
                [str(index) for index in range(len(self.future_block_list))]
                if self.future_block_list
                else []
            ),
            button_dimensions=(96, 30),
            multiple_choice=False,
            disable_selection=True,
            container=self.editor_container,
            manager=MANAGER,
            anchors={"left_target": self.future_element["text"]},
        )

        self.future_element["add"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 4), (36, 36))),
            "+",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.editor_container,
            anchors={
                "top_target": self.future_element["block_list"],
                "left_target": self.future_element["text"],
            },
            tool_tip_text="add a new block",
        )

        self.future_element["delete"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((5, 4), (36, 36))),
            "-",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.editor_container,
            anchors={
                "top_target": self.future_element["block_list"],
                "left_target": self.future_element["add"],
            },
            tool_tip_text="delete selected block",
        )

        self.create_lock(
            name=f"future", top_anchor=self.future_element["text"], x_offset=260
        )
        self.create_divider(self.future_element["delete"], "future_start")

        if self.future_block_list and not self.selected_future_block_index:
            self.selected_future_block_index = "0"
            self.future_element["block_list"].set_selected_list(
                [self.selected_future_block_index]
            )
            self.display_future_constraints()

    def clear_future_constraints(self):
        for name in self.future_element.copy().keys():
            if name in [
                "text",
                "display",
                "frame",
                "block_list",
                "add",
                "delete",
            ]:
                continue
            self.future_element[name].kill()
            self.future_element.pop(name)
        for name in self.editor_element.copy().keys():
            if name in ["future_type", "future_pool", "future_delay"]:
                self.editor_element[name].kill()
                self.editor_element.pop(name)

    def display_future_constraints(self):
        self.clear_future_constraints()
        block_info = self.get_selected_block_info()
        # TYPE
        self.future_element["type_text"] = UITextBoxTweaked(
            "<b>event_type:</b>",
            ui_scale(pygame.Rect((0, 10), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            anchors={"top_target": self.editor_element["future_start"]},
            container=self.editor_container,
        )

        self.future_element["type_dropdown"] = UIDropDown(
            pygame.Rect((17, 17), (150, 30)),
            parent_text="types",
            item_list=list(self.event_types.keys()),
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["future_start"],
                "left_target": self.future_element["type_text"],
            },
            starting_height=3,
            manager=MANAGER,
            child_trigger_close=True,
            parent_reflect_selection=True,
            disable_selection=True,
            starting_selection=[block_info["event_type"]],
        )

        self.create_divider(self.future_element["type_text"], "future_type", off_set=-2)

        # POOL
        self.future_element["pool_text"] = UITextBoxTweaked(
            "screens.event_edit.pool_info",
            ui_scale(pygame.Rect((0, 0), (400, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["future_type"]},
        )
        self.future_element["sub_dropdown"] = UIDropDown(
            pygame.Rect((10, 17), (150, 30)),
            parent_text="subtypes",
            item_list=self.event_types[
                self.future_element["type_dropdown"].selected_list[0]
            ],
            container=self.editor_container,
            anchors={
                "top_target": self.future_element["pool_text"],
            },
            starting_height=3,
            manager=MANAGER,
            child_trigger_close=False,
            multiple_choice=True,
            disable_selection=False,
            starting_selection=block_info["pool"]["subtype"].copy(),
        )
        self.future_element["sub_display"] = UITextBoxTweaked(
            f"subtype:{block_info['pool']['subtype']}",
            ui_scale(pygame.Rect((10, 60), (420, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.future_element["pool_text"]},
        )
        self.future_element["include_text"] = UITextBoxTweaked(
            "event_id:",
            ui_scale(pygame.Rect((10, 0), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.future_element["sub_display"]},
        )
        self.future_element["include_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 3), (260, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.future_element["sub_display"],
                "left_target": self.future_element["include_text"],
            },
        )
        self.future_element["include_display"] = UITextBoxTweaked(
            f"{block_info['pool']['event_id'] if block_info['pool'].get('event_id') else''}",
            ui_scale(pygame.Rect((10, 0), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.future_element["include_text"]},
        )
        self.future_element["exclude_text"] = UITextBoxTweaked(
            "excluded_event_id:",
            ui_scale(pygame.Rect((10, 0), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.future_element["include_display"]},
        )
        self.future_element["exclude_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 3), (200, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.future_element["include_display"],
                "left_target": self.future_element["exclude_text"],
            },
        )
        self.future_element["exclude_display"] = UITextBoxTweaked(
            f"{block_info['pool']['excluded_event_id'] if block_info['pool'].get('excluded_event_id') else ''}",
            ui_scale(pygame.Rect((10, 0), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.future_element["exclude_text"]},
        )

        self.create_divider(self.future_element["exclude_display"], "future_pool")

        # DELAY
        self.future_element["delay_text"] = UITextBoxTweaked(
            "<b>moon_delay:</b>",
            ui_scale(pygame.Rect((0, 10), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["future_pool"]},
        )
        self.future_element["least_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 13), (50, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["future_pool"],
                "left_target": self.future_element["delay_text"],
            },
            initial_text=str(block_info["moon_delay"][0]),
        )
        self.future_element["range_text"] = UITextBoxTweaked(
            "-",
            ui_scale(pygame.Rect((0, 10), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["future_pool"],
                "left_target": self.future_element["least_entry"],
            },
        )
        self.future_element["most_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 13), (50, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["future_pool"],
                "left_target": self.future_element["range_text"],
            },
            initial_text=str(block_info["moon_delay"][1]),
        )

        self.create_divider(
            self.future_element["most_entry"], "future_delay", off_set=-2
        )
        self.create_involved_cats_editor()
        # we redefine this here because somehow subtypes were fucking it up. i've searched for a couple hours and found
        # no discernable reason, but this fixes it.
        self.future_template = {
            "event_type": "death",
            "pool": {
                "subtype": [],
                "event_id": [],
                "excluded_event_id": [],
            },
            "moon_delay": [1, 1],
            "involved_cats": {"m_c": None, "r_c": None},
        }

    def create_involved_cats_editor(self, selected_constraints=None):
        # clear old ones
        for name, ele in self.future_element.copy().items():
            if "_involved_" in name:
                ele.kill()
                self.future_element.pop(name)

        future_cats = self.get_selected_block_info()["involved_cats"]

        if not self.available_cats:
            self.available_cats = self.get_involved_cats(include_clan=False)
        if "new random cat" not in self.available_cats:
            self.available_cats.append("new random cat")

        # make new ones
        prev_element = None
        for cat in future_cats:
            # find what cat has been picked
            selection = future_cats.get(cat)
            if isinstance(selection, dict):
                selection = "new random cat"

            self.future_element[f"{cat}_involved_text"] = UITextBoxTweaked(
                f"The future event's {self.test_cat_names[cat]} should be played by: ",
                ui_scale(pygame.Rect((0, 10), (260, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
                line_spacing=1,
                manager=MANAGER,
                container=self.editor_container,
                anchors={
                    "top_target": (
                        self.editor_element["future_delay"]
                        if not prev_element
                        else prev_element
                    )
                },
            )

            self.future_element[f"{cat}_involved_dropdown"] = UIDropDown(
                pygame.Rect((0, 20), (150, 30)),
                parent_text="available cats",
                item_list=self.available_cats,
                container=self.editor_container,
                anchors={
                    "left_target": self.future_element[f"{cat}_involved_text"],
                    "top_target": (
                        self.editor_element["future_delay"]
                        if not prev_element
                        else prev_element
                    ),
                },
                manager=MANAGER,
                child_trigger_close=True,
                parent_reflect_selection=True,
                starting_selection=[selection] if selection else ["new random cat"],
            )
            prev_element = self.future_element[f"{cat}_involved_text"]

    # OUTSIDE CONSEQUENCES EDITOR
    def generate_outside_tab(self):
        # OUTSIDER
        self.create_outsider_editor()

        # OTHER CLAN
        self.create_other_clan_editor()

        # SUPPLY
        self.create_supply_editor()

    def create_supply_editor(self):
        # INTRO
        self.open_block = "supply"
        self.supply_element["text"] = UITextBoxTweaked(
            "screens.event_edit.supplies_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["other_clan"]},
        )
        # INFO DISPLAY
        self.supply_element["display"] = UITextBoxTweaked(
            "No block selected",
            ui_scale(pygame.Rect((0, 30), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.supply_element["text"]},
        )

        self.create_lock(
            name=f"supply",
            top_anchor=self.supply_element["text"],
            y_offset=-20,
            x_offset=270,
        )
        # BLOCK LIST
        self.supply_element["block_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 136))),
            get_box(BoxStyles.FRAME, (112, 136)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "left_target": self.supply_element["text"],
                "top_target": self.editor_element["other_clan"],
            },
        )
        self.supply_element["block_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 118)),
            item_list=(
                [str(index) for index in range(len(self.supply_block_list))]
                if self.supply_block_list
                else []
            ),
            button_dimensions=(96, 30),
            multiple_choice=False,
            disable_selection=True,
            container=self.editor_container,
            manager=MANAGER,
            anchors={
                "left_target": self.supply_element["text"],
                "top_target": self.editor_element["other_clan"],
            },
        )

        self.supply_element["add"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 4), (36, 36))),
            "+",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.editor_container,
            anchors={
                "top_target": self.supply_element["block_list"],
                "left_target": self.supply_element["text"],
            },
            tool_tip_text="add a new block",
        )
        self.supply_element["delete"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((5, 4), (36, 36))),
            "-",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.editor_container,
            anchors={
                "top_target": self.supply_element["block_list"],
                "left_target": self.supply_element["add"],
            },
            tool_tip_text="delete selected block",
        )
        self.create_divider(self.supply_element["display"], "supply_start")

        if self.supply_block_list:
            self.supply_element["block_list"].set_selected_list(["0"])

    def clear_supply_constraints(self):
        if self.supply_element.get("constraint_container"):
            self.supply_element["constraint_container"].kill()

        for name in self.supply_element.copy().keys():
            if name in [
                "text",
                "display",
                "block_frame",
                "block_list",
                "add",
                "delete",
                "supply",
            ]:
                continue
            self.supply_element.pop(name)

    def display_supply_constraints(self):
        self.clear_supply_constraints()

        # CONSTRAINT CONTAINER
        self.supply_element[
            "constraint_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            container=self.editor_container,
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            resize_right=False,
            anchors={"top_target": self.editor_element["supply_start"]},
        )

        selected_constraints = self.get_selected_block_info()

        # TYPE
        self.supply_element["text"] = UITextBoxTweaked(
            "screens.event_edit.supply_type_info",
            ui_scale(pygame.Rect((0, 0), (270, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.supply_element["constraint_container"],
            anchors={"top_target": self.editor_element["supply_start"]},
        )
        self.supply_element["type_list"] = UIScrollingDropDown(
            pygame.Rect((20, 10), (130, 30)),
            dropdown_dimensions=(130, 200),
            parent_text="types",
            item_list=HandleShortEvents.supply_types,
            multiple_choice=False,
            container=self.supply_element["constraint_container"],
            anchors={
                "left_target": self.supply_element["text"],
                "top_target": self.editor_element["supply_start"],
            },
            manager=MANAGER,
        )
        if selected_constraints.get("type"):
            self.supply_element["type_list"].set_selected_list(
                [selected_constraints["type"]]
            )

        # TRIGGER
        self.supply_element["trigger_text"] = UITextBoxTweaked(
            "screens.event_edit.supply_trigger_info",
            ui_scale(pygame.Rect((0, 10), (270, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.supply_element["constraint_container"],
            anchors={"top_target": self.supply_element["text"]},
        )
        self.supply_element["trigger_list"] = UIDropDown(
            pygame.Rect((10, 20), (130, 30)),
            parent_text="triggers",
            item_list=HandleShortEvents.supply_triggers,
            multiple_choice=True,
            disable_selection=False,
            child_trigger_close=False,
            container=self.supply_element["constraint_container"],
            anchors={
                "left_target": self.supply_element["trigger_text"],
                "top_target": self.supply_element["text"],
            },
            manager=MANAGER,
        )
        if selected_constraints.get("trigger"):
            self.supply_element["trigger_list"].set_selected_list(
                selected_constraints["trigger"]
            )

        # ADJUST
        self.supply_element["adjust_text"] = UITextBoxTweaked(
            "screens.event_edit.supply_adjust_info",
            ui_scale(pygame.Rect((0, 10), (270, 250))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.supply_element["constraint_container"],
            anchors={"top_target": self.supply_element["trigger_text"]},
        )
        self.supply_element["adjust_list"] = UIDropDown(
            pygame.Rect((10, 10), (130, 30)),
            parent_text="adjustments",
            item_list=HandleShortEvents.supply_adjustments,
            multiple_choice=False,
            disable_selection=False,
            container=self.supply_element["constraint_container"],
            anchors={
                "left_target": self.supply_element["adjust_text"],
                "top_target": self.supply_element["trigger_text"],
            },
            manager=MANAGER,
        )
        if selected_constraints.get("adjust"):
            self.supply_element["adjust_list"].set_selected_list(
                [selected_constraints["adjust"]]
            )

        self.create_supply_increase_editor()

    def close_supply_increase_editor(self):
        if not self.supply_element.get("adjust_entry"):
            return

        self.supply_element["adjust_text"].kill()
        self.supply_element["adjust_entry"].kill()
        self.supply_element.pop("adjust_text")
        self.supply_element.pop("adjust_entry")

    def create_supply_increase_editor(self):
        selected_info = self.get_selected_block_info()
        if "increase_#" not in selected_info["adjust"]:
            self.close_supply_increase_editor()
            return

        amount = selected_info["adjust"].replace("increase_", "")
        if amount == "#":
            amount = 0

        self.supply_element["increase_text"] = UITextBoxTweaked(
            "screens.event_edit.supply_increase_info",
            ui_scale(pygame.Rect((280, 12), (100, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.supply_element["adjust_list"]},
        )
        self.supply_element[f"increase_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 15), (40, 29))),
            manager=MANAGER,
            container=self.editor_container,
            initial_text=str(amount),
            anchors={
                "left_target": self.supply_element["increase_text"],
                "top_target": self.supply_element["adjust_list"],
            },
        )

        self.update_block_info()

    def create_other_clan_editor(self):
        self.other_clan_element["text"] = UITextBoxTweaked(
            "screens.event_edit.other_clan_info",
            ui_scale(pygame.Rect((0, 4), (270, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["outsider"]},
        )
        self.other_clan_element["list"] = UIDropDown(
            pygame.Rect((20, 60), (130, 30)),
            parent_text="reputation",
            item_list=self.all_other_clan_reps,
            disable_selection=False,
            multiple_choice=True,
            child_trigger_close=False,
            container=self.editor_container,
            anchors={
                "left_target": self.other_clan_element["text"],
                "top_target": self.editor_element["outsider"],
            },
            manager=MANAGER,
            starting_selection=self.other_clan_info.get("current_rep"),
        )
        self.other_clan_element[f"entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((10, 123), (40, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "left_target": self.other_clan_element["text"],
                "top_target": self.editor_element["outsider"],
            },
            initial_text=str(self.other_clan_info.get("changed")),
        )
        prev_element = None
        for button, icon in self.amount_buttons.items():
            if button == "amount_down_low_button":
                prev_element = None
            self.other_clan_element[button] = UISurfaceImageButton(
                ui_scale(
                    pygame.Rect(
                        (
                            (-2 if prev_element else 20),
                            (
                                -2
                                if icon
                                in [Icon.DOWN_HIGH, Icon.DOWN_MID, Icon.DOWN_LOW]
                                else 110
                            ),
                        ),
                        (30, 30),
                    )
                ),
                icon,
                get_button_dict(ButtonStyles.DROPDOWN, (30, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors=(
                    {
                        "top_target": (
                            self.other_clan_element["amount_up_high_button"]
                        ),
                        "left_target": (
                            prev_element
                            if prev_element
                            else self.other_clan_element["entry"]
                        ),
                    }
                    if icon in [Icon.DOWN_HIGH, Icon.DOWN_MID, Icon.DOWN_LOW]
                    else {
                        "left_target": (
                            prev_element
                            if prev_element
                            else self.other_clan_element["entry"]
                        ),
                        "top_target": self.editor_element["outsider"],
                    }
                ),
            )
            prev_element = self.other_clan_element[button]
        self.other_clan_element["display"] = UITextBoxTweaked(
            f"{self.other_clan_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.other_clan_element["text"],
            },
            allow_split_dashes=False,
        )
        self.create_lock(
            name=f"other_clan",
            top_anchor=self.other_clan_element["text"],
            left_anchor=self.other_clan_element["display"],
        )
        self.create_divider(self.other_clan_element["display"], "other_clan")

    def create_outsider_editor(self):
        self.outsider_element["text"] = UITextBoxTweaked(
            "screens.event_edit.outsider_info",
            ui_scale(pygame.Rect((0, 14), (270, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )
        self.outsider_element["list"] = UIDropDown(
            pygame.Rect((20, 50), (130, 30)),
            parent_text="reputation",
            item_list=self.all_outsider_reps,
            disable_selection=False,
            multiple_choice=True,
            container=self.editor_container,
            child_trigger_close=False,
            anchors={"left_target": self.outsider_element["text"]},
            manager=MANAGER,
            starting_selection=self.outsider_info["current_rep"],
        )
        self.outsider_element[f"entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((10, 113), (40, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"left_target": self.outsider_element["text"]},
            initial_text=str(self.outsider_info["changed"]),
        )
        prev_element = None
        for button, icon in self.amount_buttons.items():
            if button == "amount_down_low_button":
                prev_element = None
            self.outsider_element[button] = UISurfaceImageButton(
                ui_scale(
                    pygame.Rect(
                        (
                            (-2 if prev_element else 20),
                            (
                                -2
                                if icon
                                in [Icon.DOWN_HIGH, Icon.DOWN_MID, Icon.DOWN_LOW]
                                else 100
                            ),
                        ),
                        (30, 30),
                    )
                ),
                icon,
                get_button_dict(ButtonStyles.DROPDOWN, (30, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors=(
                    {
                        "top_target": (self.outsider_element["amount_up_high_button"]),
                        "left_target": (
                            prev_element
                            if prev_element
                            else self.outsider_element["entry"]
                        ),
                    }
                    if icon in [Icon.DOWN_HIGH, Icon.DOWN_MID, Icon.DOWN_LOW]
                    else {
                        "left_target": (
                            prev_element
                            if prev_element
                            else self.outsider_element["entry"]
                        )
                    }
                ),
            )
            prev_element = self.outsider_element[button]
        self.outsider_element["display"] = UITextBoxTweaked(
            f"{self.outsider_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.outsider_element["text"],
            },
            allow_split_dashes=False,
        )
        self.create_lock(
            name=f"outsider",
            top_anchor=self.outsider_element["text"],
            left_anchor=self.outsider_element["display"],
        )
        self.create_divider(self.outsider_element["display"], "outsider")

    # PERSONAL CONSEQUENCES EDITOR
    def generate_personal_tab(self):
        # EXCLUDE INVOLVED
        self.create_exclude_involved_editor()

        self.injury_element["injury"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((40, 10), (120, 30))),
            "injuries",
            get_button_dict(ButtonStyles.MENU_LEFT, (120, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_left",
            container=self.editor_container,
            anchors={"top_target": self.editor_element["exclude"]},
        )
        # injury is picked by default, so this is initially disabled
        self.injury_element["injury"].disable()
        self.history_element["history"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 10), (120, 30))),
            "history",
            get_button_dict(ButtonStyles.MENU_MIDDLE, (120, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_middle",
            container=self.editor_container,
            anchors={
                "left_target": self.injury_element["injury"],
                "top_target": self.editor_element["exclude"],
            },
        )
        self.relationships_element["relationships"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 10), (120, 30))),
            "relationships",
            get_button_dict(ButtonStyles.MENU_RIGHT, (120, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_right",
            container=self.editor_container,
            anchors={
                "left_target": self.history_element["history"],
                "top_target": self.editor_element["exclude"],
            },
        )

        # BLOCKS
        self.open_block = "injury"
        self.change_block_editor()

    def change_block_editor(self):
        if self.injury_element.get("container"):
            self.injury_element["container"].kill()
        if self.history_element.get("container"):
            self.history_element["container"].kill()
        if self.relationships_element.get("container"):
            self.relationships_element["container"].kill()
        if self.lock_buttons:
            for ele in self.lock_buttons.values():
                ele.kill()
            self.lock_buttons.clear()
        if self.open_block == "injury":
            self.create_injury_editor()
            if self.injury_block_list:
                self.display_injury_constraints()
            self.update_injury_block_options()
        elif self.open_block == "history":
            self.create_history_editor()
            if self.history_block_list:
                self.display_history_constraints()
            self.update_history_block_options()
        elif self.open_block == "relationships":
            self.create_relationships_editor()
            if self.relationships_block_list:
                self.display_relationships_constraints()
            self.update_relationships_block_options()

    def create_injury_editor(self):
        # CONTAINER
        self.injury_element["container"] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            container=self.editor_container,
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            resize_right=False,
            anchors={"top_target": self.history_element["history"]},
        )

        # INTRO
        self.injury_element["start_intro"] = UITextBoxTweaked(
            "screens.event_edit.injury_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["container"],
        )

        # INFO DISPLAY
        self.injury_element["display"] = UITextBoxTweaked(
            "No block selected",
            ui_scale(pygame.Rect((0, 30), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["container"],
            anchors={"top_target": self.injury_element["start_intro"]},
        )
        self.create_lock(
            name=f"injury",
            top_anchor=self.injury_element["start_intro"],
            y_offset=-20,
            x_offset=270,
            container=self.injury_element["container"],
        )
        # BLOCK LIST
        self.injury_element["block_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 136))),
            get_box(BoxStyles.FRAME, (112, 136)),
            manager=MANAGER,
            container=self.injury_element["container"],
            anchors={"left_target": self.injury_element["start_intro"]},
        )

        self.injury_element["block_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 118)),
            item_list=(
                [str(index) for index in range(len(self.injury_block_list))]
                if self.injury_block_list
                else []
            ),
            button_dimensions=(96, 30),
            multiple_choice=False,
            disable_selection=True,
            container=self.injury_element["container"],
            manager=MANAGER,
            anchors={"left_target": self.injury_element["start_intro"]},
        )
        if self.injury_block_list:
            self.injury_element["block_list"].set_selected_list(["0"])

        self.injury_element["add"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 4), (36, 36))),
            "+",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.injury_element["container"],
            anchors={
                "top_target": self.injury_element["block_list"],
                "left_target": self.injury_element["start_intro"],
            },
            tool_tip_text="add a new block",
        )

        self.injury_element["delete"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((5, 4), (36, 36))),
            "-",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.injury_element["container"],
            anchors={
                "top_target": self.injury_element["block_list"],
                "left_target": self.injury_element["add"],
            },
            tool_tip_text="delete selected block",
        )

        self.create_divider(
            self.injury_element["display"],
            "injury_start",
            container=self.injury_element["container"],
        )

    def clear_injury_constraints(self):
        if self.injury_element.get("constraint_container"):
            self.injury_element["constraint_container"].kill()

        for name in self.injury_element.copy().keys():
            if name in [
                "injury",
                "container",
                "start_intro",
                "display",
                "block_frame",
                "block_list",
                "add",
                "delete",
                "injury_start",
            ]:
                continue
            self.injury_element.pop(name)

    def display_injury_constraints(self):
        self.clear_injury_constraints()

        # CONSTRAINT CONTAINER
        self.injury_element[
            "constraint_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            container=self.injury_element["container"],
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            resize_right=False,
            anchors={"top_target": self.editor_element["injury_start"]},
        )
        selected_constraints = self.get_selected_block_info()
        # CAT SELECTION
        self.injury_element["cat_intro"] = UITextBoxTweaked(
            "screens.event_edit.injury_cat_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["injury_start"],
            },
        )
        self.injury_element["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 166))),
            get_box(BoxStyles.FRAME, (112, 166)),
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={
                "left_target": self.injury_element["cat_intro"],
                "top_target": self.editor_element["injury_start"],
            },
        )
        self.injury_element["cats_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 148)),
            item_list=self.get_involved_cats(),
            button_dimensions=(96, 30),
            container=self.injury_element["constraint_container"],
            manager=MANAGER,
            anchors={
                "left_target": self.injury_element["cat_intro"],
                "top_target": self.editor_element["injury_start"],
            },
            starting_selection=selected_constraints["cats"],
        )
        self.injury_element["cats_info"] = UITextBoxTweaked(
            f"cats: {selected_constraints['cats']}",
            ui_scale(pygame.Rect((10, 0), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.injury_element["cat_intro"]},
        )
        self.create_divider(
            self.injury_element["cat_frame"],
            "injury_cat",
            container=self.injury_element["constraint_container"],
        )
        # INJURY SELECTION
        # CAT SELECTION
        self.injury_element["injury_intro"] = UITextBoxTweaked(
            "screens.event_edit.injury_pick_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["injury_cat"],
            },
        )
        self.injury_element["injury_pools"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((10, 10), (150, 30))),
            manager=MANAGER,
            parent_text="injury pools",
            item_list=list(self.all_injury_pools.keys()),
            dropdown_dimensions=(150, 300),
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.injury_element["injury_intro"]},
            starting_height=16,
        )
        chosen_pools = []
        for pool, button in self.injury_element[
            "injury_pools"
        ].child_button_dicts.items():
            button.set_tooltip(str(self.all_injury_pools[pool]))
            if pool in selected_constraints["injuries"]:
                chosen_pools.append(pool)
        self.injury_element["injury_pools"].set_selected_list(chosen_pools)

        self.injury_element["individual_injuries"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((100, 10), (220, 30))),
            manager=MANAGER,
            parent_text="individual conditions",
            item_list=self.all_possible_injuries,
            dropdown_dimensions=(220, 300),
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.injury_element["injury_intro"]},
            starting_height=15,
            starting_selection=[
                injury
                for injury in self.all_possible_injuries
                if injury in selected_constraints["injuries"]
            ],
        )
        self.injury_element["injury_info"] = UITextBoxTweaked(
            f"injuries: {selected_constraints['injuries']}",
            ui_scale(pygame.Rect((10, 50), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.injury_element["injury_intro"]},
        )
        self.create_divider(
            self.injury_element["injury_info"],
            "injury_cat",
            container=self.injury_element["constraint_container"],
        )
        self.injury_element["scar_text"] = UITextBoxTweaked(
            "screens.event_edit.scar_pick_info",
            ui_scale(pygame.Rect((0, 14), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.editor_element["injury_cat"]},
        )
        self.injury_element["scar_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((2, 20), (152, 226))),
            get_box(BoxStyles.FRAME, (152, 226)),
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={
                "left_target": self.injury_element["scar_text"],
                "top_target": self.editor_element["injury_cat"],
            },
        )
        self.injury_element["scar_list"] = UIScrollingButtonList(
            pygame.Rect((10, 30), (140, 206)),
            item_list=self.all_scars,
            button_dimensions=(136, 30),
            container=self.injury_element["constraint_container"],
            manager=MANAGER,
            anchors={
                "left_target": self.injury_element["scar_text"],
                "top_target": self.editor_element["injury_cat"],
            },
            starting_height=1,
            starting_selection=[
                scar for scar in self.all_scars if scar in selected_constraints["scars"]
            ],
        )
        self.injury_element["scar_preview"] = UIModifiedImage(
            ui_scale(pygame.Rect((150, 0), (100, 100))),
            image_surface=self.get_scar_example(
                selected_constraints["scars"][0]
                if selected_constraints["scars"]
                else self.all_scars[0]
            ),
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.injury_element["scar_text"]},
        )
        self.injury_element["scar_info"] = UITextBoxTweaked(
            f"scars: {selected_constraints['scars']}",
            ui_scale(pygame.Rect((10, 20), (200, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.injury_element["constraint_container"],
            anchors={"top_target": self.injury_element["scar_preview"]},
        )
        self.create_divider(
            self.injury_element["scar_frame"],
            "injury_scars",
            container=self.injury_element["constraint_container"],
        )

    def get_scar_example(self, scar):
        return pygame.transform.scale(
            generate_sprite(create_option_preview_cat(scar=scar)),
            ui_scale_dimensions((100, 100)),
        )

    def create_history_editor(self):
        # CONTAINER
        self.history_element["container"] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            container=self.editor_container,
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            resize_right=False,
            anchors={"top_target": self.history_element["history"]},
        )

        # INTRO
        self.history_element["start_intro"] = UITextBoxTweaked(
            "screens.event_edit.history_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["container"],
        )

        # INFO DISPLAY
        self.history_element["display"] = UITextBoxTweaked(
            "No block selected",
            ui_scale(pygame.Rect((0, 50), (330, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["container"],
            anchors={"top_target": self.history_element["start_intro"]},
        )
        self.create_lock(
            name=f"history",
            top_anchor=self.history_element["start_intro"],
            y_offset=-5,
            x_offset=270,
            container=self.history_element["container"],
        )
        # BLOCK LIST
        self.history_element["block_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 136))),
            get_box(BoxStyles.FRAME, (112, 136)),
            manager=MANAGER,
            container=self.history_element["container"],
            anchors={"left_target": self.history_element["start_intro"]},
        )

        self.history_element["block_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 118)),
            item_list=(
                [str(index) for index in range(len(self.history_block_list))]
                if self.history_block_list
                else []
            ),
            button_dimensions=(96, 30),
            multiple_choice=False,
            disable_selection=True,
            container=self.history_element["container"],
            manager=MANAGER,
            anchors={"left_target": self.history_element["start_intro"]},
        )
        if self.history_block_list:
            self.history_element["block_list"].set_selected_list(["0"])

        self.history_element["add"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 4), (36, 36))),
            "+",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.history_element["container"],
            anchors={
                "top_target": self.history_element["block_list"],
                "left_target": self.history_element["start_intro"],
            },
            tool_tip_text="add a new block",
        )

        self.history_element["delete"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((5, 4), (36, 36))),
            "-",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.history_element["container"],
            anchors={
                "top_target": self.history_element["block_list"],
                "left_target": self.history_element["add"],
            },
            tool_tip_text="delete selected block",
        )

        self.create_divider(
            self.history_element["display"],
            "history_start",
            container=self.history_element["container"],
        )

    def clear_history_constraints(self):
        if self.history_element.get("constraint_container"):
            self.history_element["constraint_container"].kill()

        for name in self.history_element.copy().keys():
            if name in [
                "history",
                "container",
                "start_intro",
                "display",
                "block_frame",
                "block_list",
                "add",
                "delete",
                "history_start",
            ]:
                continue
            self.history_element.pop(name)

    def display_history_constraints(self):
        self.clear_history_constraints()

        # CONSTRAINT CONTAINER
        self.history_element[
            "constraint_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            container=self.history_element["container"],
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            resize_right=False,
            anchors={"top_target": self.editor_element["history_start"]},
        )
        selected_constraints = self.get_selected_block_info()
        # CAT SELECTION
        self.history_element["cat_intro"] = UITextBoxTweaked(
            "screens.event_edit.history_cat_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["history_start"],
            },
        )
        self.history_element["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 166))),
            get_box(BoxStyles.FRAME, (112, 166)),
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={
                "left_target": self.history_element["cat_intro"],
                "top_target": self.editor_element["history_start"],
            },
        )
        self.history_element["cats_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 148)),
            item_list=self.get_involved_cats(),
            button_dimensions=(96, 30),
            container=self.history_element["constraint_container"],
            manager=MANAGER,
            anchors={
                "left_target": self.history_element["cat_intro"],
                "top_target": self.editor_element["history_start"],
            },
            starting_selection=selected_constraints["cats"],
        )
        self.history_element["cats_info"] = UITextBoxTweaked(
            f"cats: {selected_constraints['cats']}",
            ui_scale(pygame.Rect((10, 0), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.history_element["cat_intro"]},
        )
        self.create_divider(
            self.history_element["cat_frame"],
            "history_cat",
            container=self.history_element["constraint_container"],
        )

        self.history_element["scar_history_text"] = UITextBoxTweaked(
            "screens.event_edit.scar_history_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.editor_element["history_cat"]},
        )
        self.history_element["scar_history_input"] = pygame_gui.elements.UITextEntryBox(
            ui_scale(pygame.Rect((10, 10), (420, 60))),
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.history_element["scar_history_text"]},
            object_id="#visible_entry_box",
            initial_text=selected_constraints["scar"],
        )

        self.create_divider(
            self.history_element["scar_history_input"],
            "history_scar",
            container=self.history_element["constraint_container"],
        )

        self.history_element["reg_history_text"] = UITextBoxTweaked(
            "screens.event_edit.reg_history_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.editor_element["history_scar"]},
        )
        self.history_element["reg_history_input"] = pygame_gui.elements.UITextEntryBox(
            ui_scale(pygame.Rect((10, 10), (420, 60))),
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.history_element["reg_history_text"]},
            object_id="#visible_entry_box",
            initial_text=selected_constraints["reg_death"],
        )

        self.create_divider(
            self.history_element["reg_history_input"],
            "history_reg",
            container=self.history_element["constraint_container"],
        )

        self.history_element["lead_history_text"] = UITextBoxTweaked(
            "screens.event_edit.lead_history_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.editor_element["history_reg"]},
        )
        self.history_element["lead_history_input"] = pygame_gui.elements.UITextEntryBox(
            ui_scale(pygame.Rect((10, 10), (420, 60))),
            manager=MANAGER,
            container=self.history_element["constraint_container"],
            anchors={"top_target": self.history_element["lead_history_text"]},
            object_id="#visible_entry_box",
            initial_text=selected_constraints["lead_death"],
        )

        self.create_divider(
            self.history_element["lead_history_input"],
            "history_lead",
            container=self.history_element["constraint_container"],
        )

    def create_relationships_editor(self):
        self.relationships_element[
            "container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (0, 0))),
            container=self.editor_container,
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            anchors={"top_target": self.history_element["history"]},
        )
        self.relationships_element["start_intro"] = UITextBoxTweaked(
            "screens.event_edit.relationships_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["container"],
        )

        # INFO DISPLAY
        self.relationships_element["display"] = UITextBoxTweaked(
            "No block selected",
            ui_scale(pygame.Rect((0, 50), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["container"],
            anchors={"top_target": self.relationships_element["start_intro"]},
        )

        self.create_lock(
            name=f"relationships",
            top_anchor=self.relationships_element["start_intro"],
            y_offset=-5,
            x_offset=270,
            container=self.relationships_element["container"],
        )

        # BLOCK LIST
        self.relationships_element["block_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 136))),
            get_box(BoxStyles.FRAME, (112, 136)),
            manager=MANAGER,
            container=self.relationships_element["container"],
            anchors={"left_target": self.relationships_element["start_intro"]},
        )

        self.relationships_element["block_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 118)),
            item_list=(
                [str(index) for index in range(len(self.relationships_block_list))]
                if self.relationships_block_list
                else []
            ),
            button_dimensions=(96, 30),
            multiple_choice=False,
            disable_selection=True,
            container=self.relationships_element["container"],
            manager=MANAGER,
            anchors={"left_target": self.relationships_element["start_intro"]},
        )
        if self.relationships_block_list:
            self.relationships_element["block_list"].set_selected_list(["0"])

        self.relationships_element["add"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 4), (36, 36))),
            "+",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.relationships_element["container"],
            anchors={
                "top_target": self.relationships_element["block_list"],
                "left_target": self.relationships_element["start_intro"],
            },
            tool_tip_text="add a new block",
        )

        self.relationships_element["delete"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((5, 4), (36, 36))),
            "-",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.relationships_element["container"],
            anchors={
                "top_target": self.relationships_element["block_list"],
                "left_target": self.relationships_element["add"],
            },
            tool_tip_text="delete selected block",
        )

        self.create_divider(
            self.relationships_element["display"],
            "relationships_start",
            container=self.relationships_element["container"],
        )

    def clear_relationships_constraints(self):
        if self.relationships_element.get("constraint_container"):
            self.relationships_element["constraint_container"].kill()

        for name in self.relationships_element.copy().keys():
            if name in [
                "relationships",
                "container",
                "start_intro",
                "display",
                "block_frame",
                "block_list",
                "add",
                "delete",
                "relationships_start",
            ]:
                continue
            self.relationships_element.pop(name)

    def display_relationships_constraints(self):
        self.clear_relationships_constraints()

        # CONSTRAINT CONTAINER
        self.relationships_element[
            "constraint_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            container=self.relationships_element["container"],
            manager=MANAGER,
            resize_left=False,
            resize_top=False,
            resize_right=False,
            anchors={"top_target": self.editor_element["relationships_start"]},
        )
        selected_constraints = self.get_selected_block_info()

        # CAT SELECTION
        self.relationships_element["cat_intro"] = UITextBoxTweaked(
            "screens.event_edit.relationships_cat_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["relationships_start"],
            },
        )
        self.relationships_element["mutual"] = UICheckbox(
            position=(20, 10),
            container=self.relationships_element["constraint_container"],
            manager=MANAGER,
            anchors={"top_target": self.relationships_element["cat_intro"]},
            check=selected_constraints["mutual"],
        )
        self.relationships_element["mutual_info"] = UITextBoxTweaked(
            "screens.event_edit.relationships_mutual_info",
            ui_scale(pygame.Rect((5, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.relationships_element["cat_intro"],
                "left_target": self.relationships_element["mutual"],
            },
        )
        self.relationships_element["cats_from_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 166))),
            get_box(BoxStyles.FRAME, (112, 166)),
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={"top_target": self.relationships_element["mutual"]},
        )
        self.relationships_element["cats_from_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 148)),
            item_list=self.get_involved_cats(),
            button_dimensions=(96, 30),
            container=self.relationships_element["constraint_container"],
            manager=MANAGER,
            anchors={"top_target": self.relationships_element["mutual"]},
            starting_selection=selected_constraints["cats_from"],
        )
        self.relationships_element["cats_to_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((192, 20), (112, 166))),
            get_box(BoxStyles.FRAME, (112, 166)),
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.relationships_element["mutual"],
                "left_target": self.relationships_element["cats_from_frame"],
            },
        )
        self.relationships_element["cats_to_list"] = UIScrollingButtonList(
            pygame.Rect((200, 28), (100, 148)),
            item_list=self.get_involved_cats(),
            button_dimensions=(96, 30),
            container=self.relationships_element["constraint_container"],
            manager=MANAGER,
            anchors={
                "top_target": self.relationships_element["mutual"],
                "left_target": self.relationships_element["cats_from_frame"],
            },
            starting_selection=self.relationships_template["cats_to"],
        )
        self.relationships_element["cats_from_info"] = UITextBoxTweaked(
            f"cats: {selected_constraints['cats_from']}",
            ui_scale(pygame.Rect((10, 0), (110, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={"top_target": self.relationships_element["cats_from_frame"]},
        )
        self.relationships_element["cats_to_info"] = UITextBoxTweaked(
            f"cats: {selected_constraints['cats_to']}",
            ui_scale(pygame.Rect((200, 0), (110, -1))),
            object_id="#text_box_30_horizright_pad_10_10",
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.relationships_element["cats_from_frame"],
                "left_target": self.relationships_element["cats_from_info"],
            },
        )
        self.relationships_element["cat_bridge_info"] = UITextBoxTweaked(
            (
                "screens.event_edit.relationships_one_way"
                if not self.relationships_element["mutual"].checked
                else "screens.event_edit.relationships_mutual"
            ),
            ui_scale(pygame.Rect((-5, 50), (200, -1))),
            object_id="#text_box_30_horizcenter_pad_10_10",
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.relationships_element["mutual"],
                "left_target": self.relationships_element["cats_from_frame"],
            },
        )

        self.create_divider(
            self.relationships_element["cats_from_info"],
            "relationships_cats",
            container=self.relationships_element["constraint_container"],
        )

        self.relationships_element["values_text"] = UITextBoxTweaked(
            "screens.event_edit.relationships_values_info",
            ui_scale(pygame.Rect((0, 14), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={"top_target": self.editor_element["relationships_cats"]},
        )
        self.relationships_element["values_list"] = UIDropDown(
            ui_scale(pygame.Rect((0, 26), (120, 30))),
            parent_text="values",
            item_list=self.rel_value_types,
            multiple_choice=True,
            disable_selection=False,
            child_trigger_close=False,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["relationships_cats"],
                "left_target": self.relationships_element["values_text"],
            },
            manager=MANAGER,
            starting_selection=selected_constraints["values"],
        )

        self.relationships_element["values_info"] = UITextBoxTweaked(
            f"values: {selected_constraints['values']}",
            ui_scale(pygame.Rect((10, 20), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={"top_target": self.relationships_element["values_text"]},
        )
        self.create_divider(
            self.relationships_element["values_info"],
            "values",
            container=self.relationships_element["constraint_container"],
        )

        self.relationships_element["amount_text"] = UITextBoxTweaked(
            f"screens.event_edit.relationships_amount_info",
            ui_scale(pygame.Rect((0, 10), (240, 130))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["values"],
            },
        )
        self.relationships_element[
            f"amount_entry"
        ] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((10, 23), (40, 29))),
            manager=MANAGER,
            container=self.relationships_element["constraint_container"],
            anchors={
                "top_target": self.editor_element["values"],
                "left_target": self.relationships_element["amount_text"],
            },
            initial_text=str(selected_constraints["amount"]),
        )

        prev_element = None
        for button, icon in self.amount_buttons.items():
            if button == "amount_down_low_button":
                prev_element = None
            self.relationships_element[button] = UISurfaceImageButton(
                ui_scale(
                    pygame.Rect(
                        (
                            (-2 if prev_element else 20),
                            (
                                -2
                                if icon
                                in [Icon.DOWN_HIGH, Icon.DOWN_MID, Icon.DOWN_LOW]
                                else 10
                            ),
                        ),
                        (30, 30),
                    )
                ),
                icon,
                get_button_dict(ButtonStyles.DROPDOWN, (30, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.relationships_element["constraint_container"],
                anchors={
                    "top_target": (
                        self.relationships_element["amount_up_high_button"]
                        if icon in [Icon.DOWN_HIGH, Icon.DOWN_MID, Icon.DOWN_LOW]
                        else self.editor_element["values"]
                    ),
                    "left_target": (
                        prev_element
                        if prev_element
                        else self.relationships_element["amount_entry"]
                    ),
                },
            )
            prev_element = self.relationships_element[button]

    def create_exclude_involved_editor(self):
        self.exclusion_element["intro"] = UITextBoxTweaked(
            "screens.event_edit.exclude_info",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )
        self.exclusion_element["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 166))),
            get_box(BoxStyles.FRAME, (112, 166)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"left_target": self.exclusion_element["intro"]},
        )
        self.exclusion_element["cat_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 148)),
            item_list=self.get_involved_cats(include_clan=False),
            button_dimensions=(96, 30),
            container=self.editor_container,
            manager=MANAGER,
            anchors={"left_target": self.exclusion_element["intro"]},
            starting_selection=self.excluded_cats,
        )
        self.exclusion_element["display"] = UITextBoxTweaked(
            f"exclude_involved: {self.excluded_cats}",
            ui_scale(pygame.Rect((10, 10), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.exclusion_element["intro"]},
        )
        self.create_lock(
            name=f"exclude",
            top_anchor=self.exclusion_element["intro"],
            left_anchor=self.exclusion_element["display"],
            y_offset=50,
        )
        self.create_divider(self.exclusion_element["frame"], "exclude")

    # NEW CATS EDITOR
    def generate_new_cats_tab(self):
        self.new_cat_editor["intro"] = UITextBoxTweaked(
            "screens.event_edit.n_c_info",
            ui_scale(pygame.Rect((0, 10), (295, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )

        self.new_cat_editor["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (112, 186))),
            get_box(BoxStyles.FRAME, (112, 186)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"left_target": self.new_cat_editor["intro"]},
        )

        self.new_cat_editor["cat_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (100, 168)),
            item_list=self.new_cat_block_dict.keys(),
            button_dimensions=(96, 30),
            multiple_choice=False,
            disable_selection=True,
            container=self.editor_container,
            manager=MANAGER,
            anchors={"left_target": self.new_cat_editor["intro"]},
        )
        self.update_new_cat_button_tooltips()

        self.new_cat_editor["add"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 4), (36, 36))),
            "+",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.editor_container,
            anchors={
                "top_target": self.new_cat_editor["cat_list"],
                "left_target": self.new_cat_editor["intro"],
            },
            tool_tip_text="add a new cat",
        )

        self.new_cat_editor["delete"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((5, 4), (36, 36))),
            "-",
            get_button_dict(ButtonStyles.ICON_TAB_BOTTOM, (36, 36)),
            manager=MANAGER,
            object_id="@buttonstyles_icon_tab_bottom",
            container=self.editor_container,
            anchors={
                "top_target": self.new_cat_editor["cat_list"],
                "left_target": self.new_cat_editor["add"],
            },
            tool_tip_text="delete selected cat",
        )

        self.new_cat_editor["display"] = UITextBoxTweaked(
            "No cat selected",
            ui_scale(pygame.Rect((0, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.new_cat_editor["intro"]},
        )
        self.create_lock(
            name=f"new_cat",
            top_anchor=self.new_cat_editor["intro"],
            left_anchor=self.new_cat_editor["display"],
        )
        self.create_divider(self.new_cat_editor["display"], "display")

        if self.new_cat_block_dict and not self.selected_new_cat:
            selected = list(self.new_cat_block_dict.keys())[0]
            self.new_cat_editor["cat_list"].set_selected_list([selected])
            self.new_cat_select()
            self.display_new_cat_constraints()

    def update_new_cat_button_tooltips(self):
        for name, button in self.new_cat_editor["cat_list"].buttons.items():
            button.set_tooltip(f"{self.new_cat_block_dict[name]}")

    def clear_new_cat_constraints(self):
        for ele in self.new_cat_checkbox.values():
            ele.kill()
        self.new_cat_checkbox.clear()
        for ele in self.new_cat_element.values():
            ele.kill()
        self.new_cat_element.clear()

    def display_new_cat_constraints(self):
        self.current_cat_dict = self.selected_new_cat_info

        self.clear_new_cat_constraints()

        # BOOLS
        self.create_bool_editor()

        # BACKSTORY
        self.create_story_editor()

        # STATUS
        self.create_new_cat_status_editor()

        # AGE
        self.create_new_cat_age_editor()

        # GENDER
        self.create_new_cat_gender_editor()

        # PARENT/ADOPTIVE/MATE
        self.create_new_cat_connections_editor()

    def create_new_cat_connections_editor(self):
        self.connections_element["birth_parent"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((50, 20), (120, 30))),
            "birth parents",
            get_button_dict(ButtonStyles.MENU_LEFT, (120, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_left",
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["gender"],
            },
        )
        # parent is picked by default, so this is initially disabled
        self.connections_element["birth_parent"].disable()
        self.connections_element["adopt_parent"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (140, 30))),
            "adoptive parents",
            get_button_dict(ButtonStyles.MENU_MIDDLE, (140, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_middle",
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["gender"],
                "left_target": self.connections_element["birth_parent"],
            },
        )
        self.connections_element["mate"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (80, 30))),
            "mates",
            get_button_dict(ButtonStyles.MENU_RIGHT, (80, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_right",
            container=self.editor_container,
            anchors={
                "left_target": self.connections_element["adopt_parent"],
                "top_target": self.editor_element["gender"],
            },
        )
        self.connections_element["text"] = UITextBoxTweaked(
            "screens.event_edit.new_cat_parent_info",
            ui_scale(pygame.Rect((0, 14), (260, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.connections_element["adopt_parent"]},
        )
        self.connections_element["display"] = UITextBoxTweaked(
            f"chosen cats: {self.selected_new_cat_info['parent']}",
            ui_scale(pygame.Rect((0, 10), (260, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.connections_element["text"]},
        )
        self.connections_element["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((12, 20), (132, 166))),
            get_box(BoxStyles.FRAME, (132, 166)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.connections_element["mate"],
                "left_target": self.connections_element["text"],
            },
        )
        self.connections_element["cat_list"] = UIScrollingButtonList(
            pygame.Rect((20, 28), (120, 148)),
            item_list=self.get_involved_cats(
                index_limit=int(self.selected_new_cat.strip("n_c:")), include_clan=False
            ),
            button_dimensions=(116, 30),
            container=self.editor_container,
            manager=MANAGER,
            anchors={
                "top_target": self.connections_element["mate"],
                "left_target": self.connections_element["text"],
            },
            starting_selection=self.selected_new_cat_info["parent"],
        )

        self.create_divider(self.connections_element["frame"], "connections")

    def create_new_cat_gender_editor(self):
        self.new_gender_element["text"] = UITextBoxTweaked(
            "screens.event_edit.new_cat_gender_info",
            ui_scale(pygame.Rect((0, 14), (290, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["age"]},
        )

        chosen_gender = []
        for tag in self.new_cat_block_dict[self.selected_new_cat]:
            if tag in self.new_cat_genders:
                chosen_gender = [tag]

        self.new_gender_element["list"] = UIDropDown(
            ui_scale(pygame.Rect((0, 26), (130, 30))),
            parent_text="options",
            item_list=self.new_cat_genders,
            disable_selection=False,
            container=self.editor_container,
            child_trigger_close=True,
            parent_reflect_selection=True,
            anchors={
                "top_target": self.editor_element["age"],
                "left_target": self.new_gender_element["text"],
            },
            manager=MANAGER,
            starting_selection=chosen_gender,
        )
        self.new_gender_element["list"].child_button_dicts["can_birth"].set_tooltip(
            "screens.event_edit.can_birth"
        )

        self.create_divider(self.new_gender_element["text"], "gender")

    def create_new_cat_age_editor(self):
        self.new_age_element["text"] = UITextBoxTweaked(
            "screens.event_edit.new_cat_age_info",
            ui_scale(pygame.Rect((0, 14), (290, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["rank"]},
        )

        chosen_age = []
        for tag in self.new_cat_block_dict[self.selected_new_cat]:
            if tag in self.new_cat_ages:
                chosen_age = [tag]
                break

        self.new_age_element["list"] = UIDropDown(
            ui_scale(pygame.Rect((0, 26), (130, 30))),
            parent_text="ages",
            item_list=self.new_cat_ages,
            disable_selection=False,
            container=self.editor_container,
            child_trigger_close=True,
            parent_reflect_selection=True,
            anchors={
                "top_target": self.editor_element["rank"],
                "left_target": self.new_age_element["text"],
            },
            manager=MANAGER,
            starting_selection=chosen_age,
        )
        self.new_age_element["list"].child_button_dicts["mate"].set_tooltip(
            "screens.event_edit.mate"
        )
        self.new_age_element["list"].child_button_dicts["has_kits"].set_tooltip(
            "screens.event_edit.has_kits"
        )
        self.create_divider(self.new_age_element["text"], "age")

    def create_new_cat_status_editor(self):
        self.new_status_element["text"] = UITextBoxTweaked(
            "screens.event_edit.new_cat_rank_info",
            ui_scale(pygame.Rect((0, 14), (260, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["backstory"]},
        )
        chosen_status = []
        for tag in self.new_cat_block_dict[self.selected_new_cat]:
            if tag in self.new_cat_ranks:
                chosen_status = [tag]
        self.new_status_element["list"] = UIDropDown(
            ui_scale(pygame.Rect((0, 26), (180, 30))),
            parent_text="ranks",
            item_list=self.new_cat_ranks,
            disable_selection=False,
            container=self.editor_container,
            child_trigger_close=True,
            parent_reflect_selection=True,
            anchors={
                "top_target": self.editor_element["backstory"],
                "left_target": self.new_status_element["text"],
            },
            manager=MANAGER,
            starting_selection=chosen_status,
        )
        self.create_divider(self.new_status_element["text"], "rank")

    def create_story_editor(self):
        self.cat_story_element["text"] = UITextBoxTweaked(
            "screens.event_edit.cat_type_info",
            ui_scale(pygame.Rect((0, 14), (310, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["bools"]},
        )
        chosen_type = []
        for tag in self.new_cat_block_dict[self.selected_new_cat]:
            if tag in self.new_cat_types:
                chosen_type = [tag]

        self.cat_story_element["list"] = UIDropDown(
            ui_scale(pygame.Rect((10, 26), (100, 30))),
            parent_text="types",
            item_list=self.new_cat_types,
            disable_selection=False,
            container=self.editor_container,
            child_trigger_close=True,
            parent_reflect_selection=True,
            anchors={
                "top_target": self.editor_element["bools"],
                "left_target": self.cat_story_element["text"],
            },
            manager=MANAGER,
            starting_selection=chosen_type,
        )
        self.create_backstory_editor(self.cat_story_element["text"])
        self.create_divider(self.backstory_element["display"], "backstory")

    def create_bool_editor(self):
        self.new_cat_element[
            "checkbox_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((20, 0), (0, 0))),
            container=self.editor_container,
            manager=MANAGER,
            anchors={"top_target": self.editor_element["display"]},
        )
        prev_element = None
        for info in self.new_cat_bools:
            self.new_cat_checkbox[info["tag"]] = UICheckbox(
                position=(0, 15),
                container=self.new_cat_element["checkbox_container"],
                manager=MANAGER,
                check=info["setting"],
                anchors={"top_target": prev_element} if prev_element else None,
            )

            self.new_cat_checkbox[f"{info['tag']}_text"] = UITextBoxTweaked(
                f"screens.event_edit.{info['tag']}",
                ui_scale(pygame.Rect((50, 10), (370, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
                line_spacing=1,
                manager=MANAGER,
                container=self.new_cat_element["checkbox_container"],
                anchors={
                    "top_target": prev_element,
                }
                if prev_element
                else None,
            )

            prev_element = self.new_cat_checkbox[f"{info['tag']}_text"]

        self.create_divider(prev_element, "bools")

    # MAIN/RANDOM CAT EDITOR
    def generate_main_cat_tab(self):
        self.main_cat_editor["intro"] = UITextBoxTweaked(
            "screens.event_edit.mass_death_info"
            if "mass_death" in self.sub_info
            else "screens.event_edit.m_c_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )

        # DEATH
        self.create_dies_editor(self.main_cat_editor)

        # RANK
        self.create_rank_editor()

        # AGE
        self.create_age_editor()

        # REL STATUS
        self.create_rel_status_editor()

        # SKILLS
        self.create_skill_editor()

        # TRAITS
        self.create_trait_editor()

        # BACKSTORIES
        self.create_backstory_editor()

    def generate_random_cat_tab(self):
        self.random_cat_editor["intro"] = UITextBoxTweaked(
            "screens.event_edit.r_c_info",
            ui_scale(pygame.Rect((0, 10), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )

        # DEATH
        self.create_dies_editor(self.random_cat_editor)

        # RANK
        self.create_rank_editor()

        # AGE
        self.create_age_editor()

        # REL STATUS
        self.create_rel_status_editor()

        # SKILLS
        self.create_skill_editor()

        # TRAITS
        self.create_trait_editor()

        # BACKSTORIES
        self.create_backstory_editor()

    def create_backstory_editor(self, prev_element=None):
        prev_element = prev_element if prev_element else self.editor_element["traits"]

        self.backstory_element["text"] = UITextBoxTweaked(
            "screens.event_edit.backstory_info",
            ui_scale(pygame.Rect((0, 14), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": prev_element},
        )

        self.backstory_element["pools"] = UIScrollingButtonList(
            pygame.Rect((25, 20), (200, 198)),
            item_list=[pool for pool in self.all_backstories.keys()],
            button_dimensions=(200, 30),
            multiple_choice=False,
            container=self.editor_container,
            anchors={"top_target": self.backstory_element["text"]},
            manager=MANAGER,
        )
        backstory = set(self.current_cat_dict["backstory"]).intersection(
            self.all_backstories.keys()
        )
        if backstory:
            self.backstory_element["pools"].set_selected_list(list(backstory))

        self.backstory_element["frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((-20, 30), (180, 170))),
            get_box(BoxStyles.ROUNDED_BOX, (180, 170)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.backstory_element["text"],
                "left_target": self.backstory_element["pools"],
            },
        )
        self.backstory_element["frame"].disable()
        self.backstory_element["list"] = UIScrollingButtonList(
            pygame.Rect((-4, 38), (156, 152)),
            item_list=[],
            button_dimensions=(156, 30),
            container=self.editor_container,
            anchors={
                "top_target": self.backstory_element["text"],
                "left_target": self.backstory_element["pools"],
            },
            manager=MANAGER,
        )
        backstory = set(self.current_cat_dict["backstory"]).intersection(
            self.individual_stories
        )
        if backstory:
            self.backstory_element["list"].set_selected_list(list(backstory))

        self.backstory_element["display"] = UITextBoxTweaked(
            f"chosen backstories: {self.current_cat_dict['backstory']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.backstory_element["pools"],
            },
            allow_split_dashes=False,
        )
        if self.current_cat_dict != self.selected_new_cat_info:
            label = "main" if self.current_cat_dict == self.main_cat_info else "random"
            self.create_lock(
                name=f"{label}_backstory",
                top_anchor=self.backstory_element["pools"],
                left_anchor=self.backstory_element["display"],
            )
        self.create_divider(self.backstory_element["display"], "backstory")

    def create_trait_editor(self):
        self.trait_element["text"] = UITextBoxTweaked(
            "screens.event_edit.trait_info",
            ui_scale(pygame.Rect((0, 14), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["skills"]},
        )
        self.trait_element["allow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((130, 10), (80, 30))),
            "allow",
            get_button_dict(ButtonStyles.MENU_LEFT, (80, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_left",
            container=self.editor_container,
            anchors={"top_target": self.trait_element["text"]},
        )
        # allow is picked by default, so this is initially disabled
        self.trait_element["allow"].disable()
        self.trait_element["exclude"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 10), (80, 30))),
            "exclude",
            get_button_dict(ButtonStyles.MENU_RIGHT, (80, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_right",
            container=self.editor_container,
            anchors={
                "left_target": self.trait_element["allow"],
                "top_target": self.trait_element["text"],
            },
        )

        self.trait_element["kitten"] = UIScrollingDropDown(
            pygame.Rect((30, 20), (140, 30)),
            dropdown_dimensions=(140, 198),
            item_list=self.kit_traits,
            parent_text="kitten traits",
            container=self.editor_container,
            anchors={"top_target": self.trait_element["allow"]},
            manager=MANAGER,
        )
        traits = set(self.current_cat_dict["trait"]).intersection(self.kit_traits)
        if traits:
            self.trait_element["kitten"].set_selected_list(list(traits))

        self.trait_element["adult"] = UIScrollingDropDown(
            pygame.Rect((110, 20), (140, 30)),
            dropdown_dimensions=(140, 198),
            item_list=self.adult_traits,
            parent_text="adult traits",
            container=self.editor_container,
            anchors={
                "top_target": self.trait_element["allow"],
            },
            manager=MANAGER,
        )
        traits = set(self.current_cat_dict["trait"]).intersection(self.adult_traits)
        if traits:
            self.trait_element["adult"].set_selected_list(list(traits))

        self.trait_element["include_info"] = UITextBoxTweaked(
            f"chosen allowed traits: {self.current_cat_dict['trait']}",
            ui_scale(pygame.Rect((10, 60), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.trait_element["allow"],
            },
            allow_split_dashes=False,
        )
        label = "main" if self.current_cat_dict == self.main_cat_info else "random"
        self.create_lock(
            name=f"{label}_trait",
            top_anchor=self.trait_element["allow"],
            left_anchor=self.trait_element["include_info"],
            y_offset=60,
        )
        self.trait_element["exclude_info"] = UITextBoxTweaked(
            f"chosen excluded traits: {self.current_cat_dict['not_trait']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.trait_element["include_info"],
            },
            allow_split_dashes=False,
        )
        self.create_lock(
            name=f"{label}_not_trait",
            top_anchor=self.trait_element["include_info"],
            left_anchor=self.trait_element["exclude_info"],
        )
        self.create_divider(self.trait_element["exclude_info"], "traits")

    def create_skill_editor(self, prev_element=None):
        self.skill_element["text"] = UITextBoxTweaked(
            "screens.event_edit.skill_info",
            ui_scale(pygame.Rect((0, 14), (440, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["rel_status"]
                if not prev_element
                else prev_element
            },
        )
        self.skill_element["paths"] = UIScrollingButtonList(
            pygame.Rect((30, 20), (140, 198)),
            item_list=[path for path in self.all_skills.keys()],
            button_dimensions=(140, 30),
            multiple_choice=False,
            container=self.editor_container,
            anchors={"top_target": self.skill_element["text"]},
            manager=MANAGER,
        )
        self.skill_element["allow"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((30, 20), (80, 30))),
            "allow",
            get_button_dict(ButtonStyles.MENU_LEFT, (80, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_left",
            container=self.editor_container,
            anchors={
                "top_target": self.skill_element["text"],
                "left_target": self.skill_element["paths"],
            },
        )
        # allow is picked by default, so this is initially disabled
        self.skill_element["allow"].disable()
        self.skill_element["exclude"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 20), (80, 30))),
            "exclude",
            get_button_dict(ButtonStyles.MENU_RIGHT, (80, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_menu_right",
            container=self.editor_container,
            anchors={
                "left_target": self.skill_element["allow"],
                "top_target": self.skill_element["text"],
            },
        )
        self.skill_element["frame"] = UIModifiedImage(
            ui_scale(pygame.Rect((-20, 20), (254, 130))),
            get_box(BoxStyles.ROUNDED_BOX, (254, 130)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.skill_element["allow"],
                "left_target": self.skill_element["paths"],
            },
        )
        self.skill_element["frame"].disable()
        self.skill_element["include_info"] = UITextBoxTweaked(
            f"chosen allowed skills: {self.current_cat_dict['skill']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.skill_element["paths"],
            },
            allow_split_dashes=False,
        )
        label = "main" if self.current_cat_dict == self.main_cat_info else "random"
        self.create_lock(
            name=f"{label}_skill",
            top_anchor=self.skill_element["paths"],
            left_anchor=self.skill_element["include_info"],
        )
        self.skill_element["exclude_info"] = UITextBoxTweaked(
            f"chosen excluded skills: {self.current_cat_dict['not_skill']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.skill_element["include_info"],
            },
            allow_split_dashes=False,
        )
        self.create_lock(
            name=f"{label}_not_skill",
            top_anchor=self.skill_element["include_info"],
            left_anchor=self.skill_element["exclude_info"],
        )
        self.create_divider(self.skill_element["exclude_info"], "skills")

    def update_level_list(self):
        # kill existing buttons
        if self.level_element:
            for ele in self.level_element.values():
                ele.kill()

        # if no path is selected, don't make new buttons
        if not self.open_path:
            return

        # make new buttons
        level_list = self.all_skills[self.open_path]
        prev_element = None
        for level in range(len(level_list)):
            self.level_element[f"{level + 1}"] = UISurfaceImageButton(
                ui_scale(
                    pygame.Rect((-4, (28 if not prev_element else -2)), (230, 30))
                ),
                level_list[level],
                get_button_dict(ButtonStyles.DROPDOWN, (230, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "top_target": (
                        self.skill_element["allow"]
                        if not prev_element
                        else prev_element
                    ),
                    "left_target": self.skill_element["paths"],
                },
            )
            prev_element = self.level_element[f"{level + 1}"]

    def create_dies_editor(self, editor):
        self.death_element["checkbox"] = UICheckbox(
            position=(7, 7),
            container=self.editor_container,
            manager=MANAGER,
            anchors={"top_target": editor["intro"]},
            check=self.current_cat_dict["dies"],
        )
        # this checks if death is requried and locks out user input
        if "death" in self.type_info and self.current_editor_tab == "main cat":
            self.death_element["checkbox"].check()
            self.death_element["checkbox"].disable()
            self.current_cat_dict["dies"] = True

        # this just checks if the cat's dict says they should die
        if self.current_cat_dict["dies"] and not self.death_element["checkbox"].checked:
            self.death_element["checkbox"].check()

        self.death_element["text"] = UITextBoxTweaked(
            "screens.event_edit.death_info",
            ui_scale(pygame.Rect((40, 6), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": editor["intro"]},
        )

        self.death_element["display"] = UITextBoxTweaked(
            f"dies: {self.current_cat_dict['dies']}",
            ui_scale(pygame.Rect((0, 6), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.death_element["text"],
            },
        )
        label = "main" if self.current_cat_dict == self.main_cat_info else "random"
        self.create_lock(
            name=f"{label}_dies",
            top_anchor=self.death_element["text"],
            left_anchor=self.death_element["display"],
            x_offset=320,
        )
        self.create_divider(self.death_element["display"], "dies")

    def create_rel_status_editor(self):
        self.rel_status_element["container"] = UICollapsibleContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            title_text="<b>relationship_status:</b>",
            top_button_oriented_left=False,
            bottom_button=False,
            scrolling_container_to_reset=self.editor_container,
            manager=MANAGER,
            container=self.editor_container,
            title_object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            anchors={"top_target": self.editor_element["age"]},
        )
        # container for the checkbox list, this will get tossed into the collapsible container ^
        self.rel_status_element[
            "checkboxes"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((48, 0), (0, 0))),
            container=self.rel_status_element["container"],
            manager=MANAGER,
            anchors={"top_target": self.rel_status_element["container"].top_button},
        )

        # only the main cat has access to these tags
        if self.current_editor_tab == "main cat":
            prev_element = None
            # CHECKBOXES
            # clear old elements
            if self.rel_status_checkbox:
                for info in self.rel_tag_list:
                    if (
                        info["tag"] in self.main_cat_info["rel_status"]
                        and not info["setting"]
                    ):
                        info["setting"] = True
                    if self.rel_status_checkbox.get(f"{info['tag']}_text"):
                        self.rel_status_checkbox[f"{info['tag']}_text"].kill()
                    if self.rel_status_checkbox.get(info["tag"]):
                        self.rel_status_checkbox[info["tag"]].kill()
            # make new ones!
            for info in self.rel_tag_list:
                self.rel_status_element[f"{info['tag']}_text"] = UITextBoxTweaked(
                    f"screens.event_edit.{info['tag']}",
                    ui_scale(pygame.Rect((0, 10), (350, -1))),
                    object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
                    line_spacing=1,
                    manager=MANAGER,
                    container=self.rel_status_element["checkboxes"],
                    anchors={
                        "top_target": prev_element,
                    }
                    if prev_element
                    else None,
                )

                self.rel_status_checkbox[info["tag"]] = UICheckbox(
                    position=(350, 10),
                    container=self.rel_status_element["checkboxes"],
                    manager=MANAGER,
                    check=info["setting"],
                    anchors={"top_target": prev_element} if prev_element else None,
                )

                prev_element = self.rel_status_element[f"{info['tag']}_text"]

        # VALUE TAGS
        self.rel_status_element["values"] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((48, 0), (0, 0))),
            container=self.rel_status_element["container"],
            manager=MANAGER,
            anchors={"top_target": self.rel_status_element["checkboxes"]},
        )
        prev_element = None
        for value in self.rel_value_types:
            self.rel_status_element[f"{value}_text"] = UITextBoxTweaked(
                f"{value} toward r_c is > than:",
                ui_scale(pygame.Rect((0, 10), (-1, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
                line_spacing=1,
                manager=MANAGER,
                container=self.rel_status_element["values"],
                anchors={
                    "top_target": prev_element,
                }
                if prev_element
                else None,
            )
            initial_text = "0"
            for tag in self.current_cat_dict["rel_status"]:
                if value in tag:
                    initial_text = tag.replace(f"{value}_", "")

            self.rel_value_element[
                f"{value}_entry"
            ] = pygame_gui.elements.UITextEntryLine(
                ui_scale(pygame.Rect((250, 13), (40, 29))),
                manager=MANAGER,
                container=self.rel_status_element["values"],
                anchors={"top_target": prev_element} if prev_element else None,
                initial_text=initial_text,
            )
            self.rel_value_element[f"{value}_low_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((10, 12), (30, 30))),
                Icon.UP_LOW,
                get_button_dict(ButtonStyles.DROPDOWN, (30, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.rel_status_element["values"],
                anchors=(
                    {
                        "left_target": self.rel_value_element[f"{value}_entry"],
                        "top_target": prev_element,
                    }
                    if prev_element
                    else {
                        "left_target": self.rel_value_element[f"{value}_entry"],
                    }
                ),
            )
            self.rel_value_element[f"{value}_mid_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-2, 12), (30, 30))),
                Icon.UP_MID,
                get_button_dict(ButtonStyles.DROPDOWN, (30, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.rel_status_element["values"],
                anchors=(
                    {
                        "left_target": self.rel_value_element[f"{value}_low_button"],
                        "top_target": prev_element,
                    }
                    if prev_element
                    else {
                        "left_target": self.rel_value_element[f"{value}_low_button"],
                    }
                ),
            )
            self.rel_value_element[f"{value}_high_button"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-2, 12), (30, 30))),
                Icon.UP_HIGH,
                get_button_dict(ButtonStyles.DROPDOWN, (30, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.rel_status_element["values"],
                anchors=(
                    {
                        "left_target": self.rel_value_element[f"{value}_mid_button"],
                        "top_target": prev_element,
                    }
                    if prev_element
                    else {
                        "left_target": self.rel_value_element[f"{value}_mid_button"],
                    }
                ),
            )
            prev_element = self.rel_status_element[f"{value}_text"]
        self.rel_status_element["display"] = UITextBoxTweaked(
            f"chosen relationship_status: {self.current_cat_dict['rel_status']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.rel_status_element["container"]},
        )
        label = "main" if self.current_cat_dict == self.main_cat_info else "random"
        self.create_lock(
            name=f"{label}_rel_status",
            top_anchor=self.rel_status_element["container"],
            left_anchor=self.rel_status_element["display"],
        )
        self.rel_status_element["container"].close()
        self.create_divider(self.rel_status_element["display"], "rel_status")

    def create_age_editor(self):
        self.age_element["text"] = UITextBoxTweaked(
            "screens.event_edit.age_info",
            ui_scale(pygame.Rect((0, 6), (220, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["rank"]},
        )
        self.age_element["dropdown"] = UIScrollingDropDown(
            pygame.Rect((0, 16), (200, 30)),
            manager=MANAGER,
            container=self.editor_container,
            parent_text="ages",
            item_list=self.all_ages,
            dropdown_dimensions=(200, 198),
            anchors={
                "top_target": self.editor_element["rank"],
                "left_target": self.age_element["text"],
            },
            starting_height=1,
            starting_selection=self.current_cat_dict["age"],
        )
        self.age_element["display"] = UITextBoxTweaked(
            f"chosen age: {self.current_cat_dict['age']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.age_element["text"]},
        )
        label = "main" if self.current_cat_dict == self.main_cat_info else "random"
        self.create_lock(
            name=f"{label}_age",
            top_anchor=self.age_element["text"],
            left_anchor=self.age_element["display"],
        )
        self.create_divider(self.age_element["display"], "age")

    def create_rank_editor(self, prev_element=None):
        self.rank_element["text"] = UITextBoxTweaked(
            "screens.event_edit.rank_info",
            ui_scale(pygame.Rect((0, 10), (220, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["dies"]
                if not prev_element
                else prev_element
            },
        )
        self.rank_element["dropdown"] = UIScrollingDropDown(
            pygame.Rect((0, 28), (200, 30)),
            manager=MANAGER,
            container=self.editor_container,
            parent_text="ranks",
            item_list=self.all_ranks,
            dropdown_dimensions=(200, 310),
            starting_height=2,
            anchors={
                "top_target": self.death_element["display"],
                "left_target": self.rank_element["text"],
            },
            starting_selection=self.current_cat_dict["rank"],
        )
        self.rank_element["display"] = UITextBoxTweaked(
            f"chosen rank: {self.current_cat_dict['rank']}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.rank_element["text"]},
        )
        label = "main" if self.current_cat_dict == self.main_cat_info else "random"
        self.create_lock(
            name=f"{label}_rank",
            top_anchor=self.rank_element["text"],
            left_anchor=self.rank_element["display"],
        )
        self.create_divider(self.rank_element["display"], "rank")

    # SETTINGS EDITOR
    def generate_settings_tab(self):
        # EVENT ID
        self.create_event_id_editor()
        # LOCATION
        self.create_location_editor()
        # SEASON
        self.create_season_editor()
        # TYPE AND SUBTYPES
        self.create_type_editor()
        # TAGS
        self.create_tag_editor()
        # WEIGHT
        self.create_weight_editor()
        # ACC
        self.create_acc_editor()

    def create_acc_editor(self):
        self.acc_element["text"] = UITextBoxTweaked(
            "screens.event_edit.acc_info",
            ui_scale(pygame.Rect((0, 15), (450, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.weight_element["text"]},
        )
        prev_element = None
        for group in self.acc_categories.keys():
            self.acc_element[group] = UISurfaceImageButton(
                ui_scale(pygame.Rect((40, 15), (150, 30))),
                group,
                get_button_dict(ButtonStyles.DROPDOWN, (150, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.acc_element["text"]
                    )
                },
            )
            prev_element = self.acc_element[group]
            if "accessory" not in self.sub_info:
                self.acc_element[group].disable()

        self.acc_element["frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((-8, 0), (210, 250))),
            get_box(BoxStyles.FRAME, (210, 250)),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["text"],
                "left_target": prev_element,
            },
        )

        self.acc_element["display"] = UITextBoxTweaked(
            f"chosen accessories: {self.acc_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["frame"],
            },
            allow_split_dashes=False,
        )

        self.create_lock(
            name="acc",
            top_anchor=self.acc_element["frame"],
            left_anchor=self.acc_element["display"],
        )
        self.create_divider(self.acc_element["display"], "acc")

    def update_acc_list(self):
        # kill old buttons
        if self.acc_element.get("list"):
            self.acc_element["list"].kill()

        if not self.open_category:
            # if no category, we kill buttons and return
            return

        category = None
        for category_name, accs in self.acc_categories.items():
            if self.open_category == category_name:
                category = accs
                break

        self.acc_element["list"] = UIScrollingButtonList(
            ui_scale(pygame.Rect((2, 10), (196, 230))),
            item_list=category,
            button_dimensions=(190, 30),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.acc_element["text"],
                "left_target": self.acc_element["WILD"],
            },
            starting_selection=self.acc_info,
        )
        if not self.acc_element.get("preview"):
            self.acc_element["preview"] = UIModifiedImage(
                ui_scale(pygame.Rect((80, 0), (100, 100))),
                image_surface=self.get_acc_example(
                    acc=self.acc_info[0] if self.acc_info else category[0]
                ),
                manager=MANAGER,
                container=self.editor_container,
                anchors={
                    "top_target": self.acc_element[list(self.acc_categories.keys())[-1]]
                },
            )

    @staticmethod
    def get_acc_example(acc):
        """
        Returns the example sprite image for the given acc.
        """
        return pygame.transform.scale(
            generate_sprite(create_option_preview_cat(acc=acc)),
            ui_scale_dimensions((100, 100)),
        )

    def create_weight_editor(self):
        self.weight_element["text"] = UITextBoxTweaked(
            "<b>* weight:</b>",
            ui_scale(pygame.Rect((0, 15), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["tag"]},
        )
        self.weight_element["entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 18), (50, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.editor_element["tag"],
                "left_target": self.weight_element["text"],
            },
            initial_text=f"{self.weight_info}",
        )
        self.create_lock(
            name="weight",
            top_anchor=self.editor_element["tag"],
            left_anchor=self.weight_element["entry"],
            x_offset=268,
        )
        self.create_divider(self.weight_element["entry"], "weight", -10)

    def create_tag_editor(self):
        self.tag_element["collapse_container"] = UICollapsibleContainer(
            ui_scale(pygame.Rect((0, 0), (440, 0))),
            top_button_oriented_left=False,
            title_text="<b>Tags:</b>",
            bottom_button=False,
            resize_right=False,
            scrolling_container_to_reset=self.editor_container,
            manager=MANAGER,
            container=self.editor_container,
            title_object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            anchors={"top_target": self.type_element["display"]},
        )
        self.tag_element[
            "basic_checkbox_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((48, 0), (0, 0))),
            container=self.tag_element["collapse_container"],
            manager=MANAGER,
            anchors={"top_target": self.tag_element["collapse_container"].top_button},
        )

        self.update_basic_checkboxes()

        self.rank_tag_checkbox["text"] = UITextBoxTweaked(
            "screens.event_edit.rank_tags",
            ui_scale(pygame.Rect((0, 10), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.tag_element["collapse_container"],
            anchors={
                "top_target": self.tag_element["basic_checkbox_container"],
                "left_target": self.event_id_element["text"],
            },
        )
        prev_element = None
        rank_list = Cat.rank_sort_order.copy()
        rank_list.append("apps")
        for rank in rank_list:
            if f"clan:{rank}" in self.tag_info:
                setting = True
            else:
                setting = False

            self.rank_tag_checkbox[rank] = UICheckbox(
                position=(400, 10),
                container=self.tag_element["collapse_container"],
                manager=MANAGER,
                check=setting,
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.rank_tag_checkbox["text"]
                    ),
                },
            )

            check_box_rect = pygame.Rect((0, 10), (350, -1))
            check_box_rect.right = -70
            if rank == "apps":
                rank_string = f"two of any apprentice type"
            else:
                rank_string = (
                    f"two {rank}s" if rank not in ("deputy", "leader") else rank
                )
            self.rank_tag_checkbox[f"{rank}_text"] = UITextBoxTweaked(
                rank_string,
                ui_scale(check_box_rect),
                object_id="#text_box_30_horizright_pad_10_10",
                line_spacing=1,
                manager=MANAGER,
                container=self.tag_element["collapse_container"],
                anchors={
                    "top_target": (
                        prev_element if prev_element else self.rank_tag_checkbox["text"]
                    ),
                    "right": "right",
                },
            )

            prev_element = self.rank_tag_checkbox[f"{rank}_text"]

        self.tag_element["display"] = UITextBoxTweaked(
            f"chosen tags: {self.tag_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.tag_element["collapse_container"],
            },
            allow_split_dashes=False,
        )

        self.tag_element["collapse_container"].close()

        self.create_lock(
            name="tag",
            top_anchor=self.tag_element["collapse_container"],
            left_anchor=self.tag_element["display"],
        )
        self.create_divider(self.tag_element["display"], "tag")

    def update_basic_checkboxes(self):
        prev_element = None

        # clear old elements
        if self.basic_tag_checkbox:
            for info in self.basic_tag_list:
                if self.basic_tag_checkbox.get(f"{info['tag']}_text"):
                    self.basic_tag_checkbox[f"{info['tag']}_text"].kill()
                if self.basic_tag_checkbox.get(info["tag"]):
                    self.basic_tag_checkbox[info["tag"]].kill()
            self.basic_tag_checkbox.clear()

        # make new ones!
        for info in self.basic_tag_list:
            if info["tag"] in self.tag_info and not info["setting"]:
                info["setting"] = True
            # first reset the values
            if info.get("required_type") and info["required_type"] != self.type_info[0]:
                # this is to change the setting to false
                index = self.basic_tag_list.index(info)
                self.basic_tag_list[index] = {
                    "tag": info["tag"],
                    "setting": False,
                    "required_type": info["required_type"],
                    "conflict": info["conflict"],
                }
                continue

            self.basic_tag_checkbox[f"{info['tag']}_text"] = UITextBoxTweaked(
                f"screens.event_edit.{info['tag']}",
                ui_scale(pygame.Rect((0, 10), (350, -1))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
                line_spacing=1,
                manager=MANAGER,
                container=self.tag_element["basic_checkbox_container"],
                anchors={
                    "top_target": prev_element,
                }
                if prev_element
                else None,
            )

            self.basic_tag_checkbox[info["tag"]] = UICheckbox(
                position=(350, 10),
                container=self.tag_element["basic_checkbox_container"],
                manager=MANAGER,
                check=info["setting"],
                anchors={"top_target": prev_element} if prev_element else None,
            )

            prev_element = self.basic_tag_checkbox[f"{info['tag']}_text"]

        self.update_tag_info()

    def create_type_editor(self):
        self.type_element["text"] = UITextBoxTweaked(
            "<b>sub/type:</b>",
            ui_scale(pygame.Rect((0, 14), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.season_element["display"]},
        )
        if not self.type_info:
            self.type_info = ["death"]

        self.type_element["type_dropdown"] = UIDropDown(
            pygame.Rect((17, 17), (150, 30)),
            parent_text=self.type_info[0],
            item_list=list(self.event_types.keys()),
            container=self.editor_container,
            anchors={
                "left_target": self.event_id_element["text"],
                "top_target": (self.season_element["display"]),
            },
            starting_height=3,
            manager=MANAGER,
            child_trigger_close=True,
            starting_selection=self.type_info,
        )

        self.update_sub_buttons(self.event_types[self.type_info[0]])

        self.type_element["display"] = UITextBoxTweaked(
            f"chosen subtypes: {self.sub_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.type_element["text"],
            },
            allow_split_dashes=False,
        )
        self.create_lock(
            name="subtypes",
            top_anchor=self.type_element["text"],
            left_anchor=self.type_element["display"],
        )
        self.create_divider(self.type_element["display"], "type")

    def update_sub_buttons(self, type_list):
        if self.type_element.get("subtype_dropdown"):
            self.type_element["subtype_dropdown"].kill()

        self.type_element["subtype_dropdown"] = UIDropDown(
            pygame.Rect((0, 17), (150, 30)),
            parent_text="pick subtypes",
            item_list=type_list,
            manager=MANAGER,
            container=self.editor_container,
            multiple_choice=True,
            disable_selection=False,
            child_trigger_close=False,
            starting_height=3,
            anchors={
                "left_target": self.type_element["type_dropdown"],
                "top_target": self.season_element["display"],
            },
            starting_selection=self.sub_info,
        )

    def create_season_editor(self):
        self.season_element["text"] = UITextBoxTweaked(
            "screens.event_edit.season_info",
            ui_scale(pygame.Rect((0, 10), (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.location_element["display"]},
        )

        self.season_element["dropdown"] = UIDropDown(
            pygame.Rect((10, 20), (150, 30)),
            parent_text="seasons",
            item_list=self.all_seasons,
            container=self.editor_container,
            manager=MANAGER,
            multiple_choice=True,
            disable_selection=False,
            child_trigger_close=False,
            starting_selection=self.season_info,
            starting_height=5,
            anchors={
                "left_target": self.season_element["text"],
                "top_target": self.location_element["display"],
            },
        )

        self.season_element["display"] = UITextBoxTweaked(
            f"chosen season: {self.season_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={
                "top_target": self.season_element["text"],
            },
            allow_split_dashes=False,
        )
        self.create_lock(
            name="season",
            top_anchor=self.season_element["text"],
            left_anchor=self.season_element["display"],
        )
        self.create_divider(self.season_element["display"], "season")

    def create_location_editor(self):
        self.location_element["text"] = UITextBoxTweaked(
            "screens.event_edit.location_info",
            ui_scale(pygame.Rect((0, 10), (450, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.editor_element["event_id"]},
        )
        biome_list = constants.BIOME_TYPES
        prev_element = None
        for biome in biome_list:
            y_pos = 10 if not prev_element else -2
            self.location_element[biome] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, y_pos), (150, 30))),
                biome,
                get_button_dict(ButtonStyles.DROPDOWN, (150, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "left_target": self.event_id_element["text"],
                    "top_target": (
                        self.location_element["text"]
                        if not prev_element
                        else prev_element
                    ),
                },
            )
            prev_element = self.location_element[biome]

        self.location_element["display"] = UITextBoxTweaked(
            f"chosen location: {self.location_info}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"top_target": self.location_element[biome_list[-1]]},
            allow_split_dashes=False,
        )

        self.create_lock(
            name="location",
            top_anchor=self.location_element[biome_list[-1]],
            left_anchor=self.location_element["display"],
        )

        self.create_divider(self.location_element["display"], "location")

    def update_camp_list(self, chosen_biome):
        for biome in self.all_camps:
            for camp in self.all_camps[biome]:
                if self.location_element.get(camp):
                    self.location_element[camp].kill()

        camp_list = self.all_camps.get(chosen_biome)

        if not camp_list:
            return

        prev_element = None
        for camp in camp_list:
            y_pos = 10 if not prev_element else -2
            self.location_element[camp] = UISurfaceImageButton(
                ui_scale(pygame.Rect((20, y_pos), (150, 30))),
                camp,
                get_button_dict(ButtonStyles.DROPDOWN, (150, 30)),
                manager=MANAGER,
                object_id="@buttonstyles_dropdown",
                container=self.editor_container,
                anchors={
                    "left_target": self.location_element[chosen_biome],
                    "top_target": (
                        self.location_element["text"]
                        if not prev_element
                        else prev_element
                    ),
                },
            )
            prev_element = self.location_element[camp]

    def create_event_id_editor(self):
        self.event_id_element["text"] = UITextBoxTweaked(
            f"<b>event_id:</b>",
            ui_scale(pygame.Rect((0, 10), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
        )
        self.event_id_element["entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 13), (230, 29))),
            manager=MANAGER,
            container=self.editor_container,
            anchors={"left_target": self.event_id_element["text"]},
            initial_text=self.event_id_info if self.event_id_info else "",
        )

        self.event_id_element["check_text"] = UITextBoxTweaked(
            "",
            ui_scale(pygame.Rect((0, 10), (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=MANAGER,
            container=self.editor_container,
            anchors={"left_target": self.event_id_element["entry"]},
        )
        self.valid_id()
        self.create_divider(self.event_id_element["text"], "event_id")
