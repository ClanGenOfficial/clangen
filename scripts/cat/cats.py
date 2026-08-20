"""
Contains the Cat and Personality classes
"""

from __future__ import annotations

import bisect
import itertools
import os.path
import sys
from random import choice, randint, sample, random
from typing import Dict, List, Any, Union, Callable, Optional, TYPE_CHECKING, Literal

import i18n
import ujson  # type: ignore

import scripts.game_structure.localization as pronouns
from scripts.cat import pronouns
from scripts.cat.enums import (
    CatAge,
    CatRank,
    CatSocial,
    CatGroup,
    CatCompatibility,
    CatThought,
)
from scripts.cat.factories.typed_dicts import (
    MentorshipDict,
    CatTogglesDict,
    InheritanceDict,
    AfterlifeAffinityDict,
    GenderDict,
)
from scripts.cat.history import History
from scripts.cat.microservices.grief import grief
from scripts.cat.names import Name
from scripts.cat.pelts import Pelt
from scripts.cat.personality import Personality
from scripts.cat.skills import CatSkills, SkillPath, scale_progress
from scripts.cat.status import Status
from scripts.cat_relations.cat_handle_funcs import init_all_relationships
from scripts.config import get_config
from scripts.cat_relations.inheritance import Inheritance
from scripts.cat_relations.inheritance2 import inheritance_db
from scripts.cat_relations.relationship import Relationship, create_one_relationship
from scripts.cat_relations.enums import RelType, RelTier, rel_type_tiers
from scripts.clan_package.settings import get_clan_setting

from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure import image_cache, constants, game
from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.localization import load_lang_resource
from scripts.game_structure.screen_settings import screen
from scripts.housekeeping.datadir import get_save_dir
from scripts.cat import microservices
from scripts.cat.sprites.display_sprites import update_sprite, update_mask
from scripts.events_module.text_adjust import (
    event_text_adjust,
    leader_ceremony_text_adjust,
)
from scripts.events_module.event_filters import get_personality_compatibility
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank

import scripts.game_structure.screen_settings

if TYPE_CHECKING:
    import pygame

import scripts.game_structure.screen_settings


class Cat:
    """The cat class."""

    used_screen = screen
    current_pronoun_lang = None

    age_moons = {
        CatAge.NEWBORN: constants.CONFIG["cat_ages"]["newborn"],
        CatAge.KITTEN: constants.CONFIG["cat_ages"]["kitten"],
        CatAge.ADOLESCENT: constants.CONFIG["cat_ages"]["adolescent"],
        CatAge.YOUNG_ADULT: constants.CONFIG["cat_ages"]["young adult"],
        CatAge.ADULT: constants.CONFIG["cat_ages"]["adult"],
        CatAge.SENIOR_ADULT: constants.CONFIG["cat_ages"]["senior adult"],
        CatAge.SENIOR: constants.CONFIG["cat_ages"]["senior"],
    }

    # This in is in reverse order: top of the list at the bottom
    rank_sort_order = [
        CatRank.NEWBORN,
        CatRank.KITTEN,
        CatRank.ELDER,
        CatRank.APPRENTICE,
        CatRank.WARRIOR,
        CatRank.MEDIATOR_APPRENTICE,
        CatRank.MEDIATOR,
        CatRank.MEDICINE_APPRENTICE,
        CatRank.MEDICINE_CAT,
        CatRank.DEPUTY,
        CatRank.LEADER,
    ]

    gender_tags = {"female": "F", "male": "M"}

    # EX levels and ranges.
    # Ranges are inclusive to both bounds
    experience_levels_range = {
        "untrained": (0, 0),
        "learning": (1, 50),
        "prepared": (51, 110),
        "capable": (110, 170),
        "proficient": (171, 240),
        "adept": (241, 320),
        "masterful": (321, 321),
    }

    all_cats: Dict[str, Cat] = {}  # ID: object
    id_iter = itertools.count()

    all_cats_list: List[Cat] = []
    ordered_cat_list: List[Cat] = []

    # DEBUG SETTINGS
    disable_random = False

    def __init__(
        self,
        ID: str,
        gender_dict: GenderDict,
        pelt: Pelt,
        moons: int,
        status: Status,
        backstory: str,
        skills: CatSkills,
        personality: Personality,
        mentorship: MentorshipDict,
        inheritance: InheritanceDict,
        affinity: AfterlifeAffinityDict,
        toggles: CatTogglesDict,
        experience: int,
        birth_cooldown: int,
        specsuffix_hidden=False,  # to delete once Name is decoupled from Cat
        *,
        example=False,
        faded=False,
        **kwargs,
    ):
        """
        Initialize the cat.

        :param ID: Cat's ID value
        :param gender_dict: Cat's sex & gender (and pronouns if loading from save)
        :param pelt: Pelt object
        :param moons: Cat's age in moons
        :param status: Status object
        :param backstory: Cat's backstory
        :param skills: CatSkills object
        :param personality: Personality object
        :param mentorship: MentorshipDict containing mentor data and apprentice data, including former for both
        :param inheritance: Inheritance object
        :param affinity: AffinityDict containing starclan & dark forest affinity values
        :param toggles: Dict of cat-related behavior toggles
        :param experience: Cat's experience value
        :param birth_cooldown: How many moons that must pass before this cat can give birth again
        :param specsuffix_hidden: Whether to show or hide the "special suffix" for a cat's name
        :param example: Marks a cat as being part of the MakeClanScreen
        :param faded: Set to True if a cat is faded
        :param kwargs: Any other non-specified values. Can include biome for some reason.
        """

        self._history = None

        # This must be at the top. It's a smaller list of things to init, which is only for faded cats
        if faded:
            self.init_faded(ID, moons, status, inheritance)
            return

        self.generate_events = GenerateEvents()

        # Private attributes
        self._mentor = None  # plz
        self._experience = None
        self._moons = None
        self._pronouns: Dict[str, List[Dict[str, Union[str, int]]]] = {}

        # Public attributes
        self.ID = ID

        self.gender: Literal["male", "female"] = gender_dict["sex"]
        self.genderalign = gender_dict["genderalign"]
        if gender_dict.get("pronouns"):  # pronouns are lazy-loaded for new cats
            self.pronouns = gender_dict.get("pronouns")

        self.pelt: Pelt = pelt
        self.moons: int = moons
        self.status: Status = status
        self.backstory = backstory
        self.skills = skills
        self.personality = personality

        # mentorship
        self.mentor = mentorship["mentor"]
        self.former_mentor = mentorship["former_mentor"]
        self.patrol_with_mentor = mentorship["patrol_with_mentor"]
        self.apprentice = mentorship["apprentice"]
        self.former_apprentices = mentorship["former_apprentices"]

        # inheritance
        self.parent1 = inheritance["parent1"]
        self.parent2 = inheritance["parent2"]
        self.adoptive_parents = inheritance["adoptive_parents"]
        self.faded_offspring = inheritance["faded_offspring"]
        """Stores of a list of faded offspring, for relation tracking purposes"""
        self.mate = inheritance["mate"]
        self.previous_mates = inheritance["previous_mates"]
        self.inheritance = None

        # afterlife affinity
        self.dark_forest_affinity = affinity["dark_forest"]
        self.starclan_affinity = affinity["starclan"]

        # toggles
        self.no_kits = toggles["no_kits"]
        self.no_mates = toggles["no_mates"]
        self.no_retire = toggles["no_retire"]
        self.prevent_fading = toggles["prevent_fading"]  # Prevents a cat from fading
        self.favourite = toggles["favourite"]

        # misc
        self.experience = experience
        self.birth_cooldown = birth_cooldown
        self.specsuffix_hidden = specsuffix_hidden  # kill this ASAP

        # other misc
        self.name: Optional[Name] = None
        self.relationships = {}
        self.placement = None
        self.example = example
        self.thought = ""
        self.next_thought_type: CatThought = CatThought.WHILE_ALIVE
        self.assign_thought()

        # conditions setup
        self.illnesses = {}
        self.injuries = {}
        self.healed_condition = None
        self.leader_death_heal = None
        self.also_got = False
        self.permanent_condition = {}

        self.faded = faded  # This is only used to flag cats that are faded, but won't be added to the faded list until
        # the next save.

        # Private Sprite
        self._sprite: Optional["pygame.Surface"] = None
        self._sprite_mask: Optional["pygame.Mask"] = None
        self._sprite_working: bool = self.not_working()
        """used to store whether we should be displaying sick sprite or not"""

        # SAVE CAT INTO ALL_CATS DICTIONARY IN CATS-CLASS
        self.all_cats[self.ID] = self

        if self.ID is not None:
            Cat.insert_cat(self)

    @property
    def age(self):
        return CatAge.get_from_moons(self.moons)

    def init_faded(
        self, ID: str, moons: int, status: Status, inheritance: InheritanceDict
    ):
        """
        Perform faded-specific initialization
        :param ID: Cat ID
        :param moons: age in moons
        :param status: last known status
        :param inheritance: family data
        :return: bool
        """
        self.ID = ID
        self.parent1 = inheritance["parent1"]
        self.parent2 = inheritance["parent2"]
        self.adoptive_parents = inheritance["adoptive_parents"]
        self.faded_offspring = inheritance["faded_offspring"]
        self.mate = inheritance["mate"]
        self.status = status
        self._pronouns = {}  # Needs to be set as a dict
        self.moons = moons
        self.inheritance = None  # This should never be used, but just for safety
        # name is assigned by FadedCatFactory

        self.faded = True
        self.set_faded()
        return True

    def __repr__(self):
        return "CAT OBJECT:" + self.ID

    def __eq__(self, other):
        return False if not isinstance(other, Cat) else self.ID == other.ID

    def __hash__(self):
        return hash(self.ID)

    @property
    def dead(self) -> bool:
        return bool(self.status.group.is_afterlife())

    @dead.setter
    def dead(self, die: bool):
        if die:
            if self.status.group.is_afterlife():
                print(
                    f"WARNING: Tried to kill {self.name} ID: {self.ID} but this cat is already dead!"
                )
                return

            game.updated_afterlife_cats.add(self)

            cat_default_afterlife_id = self.status.get_default_afterlife_id()
            if cat_default_afterlife_id == CatGroup.UNKNOWN_RESIDENCE_ID:
                pass

            # kits are auto-accepted
            elif self.age in (CatAge.KITTEN, CatAge.NEWBORN):
                self.history.add_afterlife_acceptance(
                    game.clan.instructor.status.group,
                    is_kit=True,
                )
            else:
                cat_skills = self.skills.get_skill_dict()
                if cat_default_afterlife_id == CatGroup.STARCLAN_ID:
                    affinity = self.starclan_affinity
                    skill_match = SkillPath.STAR
                    skill_conflict = SkillPath.DARK

                    afterlife_group = CatGroup.STARCLAN
                    rejected_ID = CatGroup.DARK_FOREST_ID
                else:
                    affinity = self.dark_forest_affinity
                    skill_match = SkillPath.DARK
                    skill_conflict = SkillPath.STAR

                    afterlife_group = CatGroup.DARK_FOREST
                    rejected_ID = CatGroup.STARCLAN_ID

                # scales with skill tier
                affinity += get_config("affinity.skill_favor.match") * cat_skills.get(
                    skill_match, 0
                )
                affinity += get_config(
                    "affinity.skill_favor.conflict"
                ) * cat_skills.get(skill_conflict, 0)

                # afterlife does not like this cat
                if affinity < 0:
                    # might send them to the opposite afterlife instead
                    if random() < abs(affinity / 100):
                        self.history.add_afterlife_acceptance(
                            afterlife_group, rejected=True
                        )
                        self.status.send_to_afterlife(rejected_ID)
                        return
                    # fine, they can go to afterlife, but some cats don't like it
                    self.history.add_afterlife_acceptance(
                        afterlife_group, contentious=True
                    )
                # afterlife thinks this cat is ok
                else:
                    self.history.add_afterlife_acceptance(afterlife_group)
            self.status.send_to_afterlife()

    @property
    def dead_for(self) -> int:
        return sum(
            entry.get("moons_as")
            for entry in self.status.group_history
            if entry.get("group")
            in (
                CatGroup.STARCLAN_ID,
                CatGroup.UNKNOWN_RESIDENCE_ID,
                CatGroup.DARK_FOREST_ID,
            )
        )

    @dead_for.setter
    def dead_for(self, moons: int):
        self.status.change_current_moons_as(moons)

    @property
    def mentor(self):
        """Return managed attribute '_mentor', which is the ID of the cat's mentor."""
        return self._mentor

    @mentor.setter
    def mentor(self, mentor_id: Any):
        """Makes sure `Cat.mentor` can only be None (no mentor) or a string (mentor ID)."""
        if mentor_id is None or isinstance(mentor_id, str):
            self._mentor = mentor_id
        else:
            print(
                f"Mentor ID {mentor_id} of type {type(mentor_id)} isn't valid :("
                "\nCat.mentor has to be either None (no mentor) or the mentor's ID as a string."
            )

    @property
    def pronouns(self) -> List[Dict[str, Union[str, int]]]:
        """
        Loads the correct pronouns for the loaded language.
        :return: List of dicts for the cat's pronouns
        """
        if self.faded:
            value = pronouns.get_default_pronouns()["0"]
            return [value]

        locale = i18n.config.get("locale")
        value = self._pronouns.get(locale)
        if value is None:
            self._pronouns[locale] = pronouns.get_new_pronouns(self.genderalign)
            value = self._pronouns[locale]
        return value

    @pronouns.setter
    def pronouns(
        self,
        val: Union[
            Dict[str, List[Dict[str, Union[str, int]]]],
            List[Dict[str, Union[str, int]]],
        ],
    ):
        """
        Sets the pronouns for the cat. Contains protection for "old-style" pronouns
        :param val:
        :return:
        """
        if isinstance(val, dict):
            self._pronouns = val
            return
        elif isinstance(val, list):
            # possibly old-style pronouns
            self._pronouns[i18n.config.get("locale")] = val
            return

    @property
    def history(self) -> History:
        """load history if it is None"""
        if self._history is None:
            self.load_history()
        return self._history

    @history.setter
    def history(self, val: History):
        self._history = val

    @property
    def genderalign_string(self):
        """
        Returns the localized genderalign string, if one exists, or the original text if not
        :return: string for display
        """
        # translate it if it's default
        if self.genderalign in (
            "female",
            "male",
            "trans female",
            "trans male",
            "nonbinary",
        ):
            return i18n.t(f"general.{self.genderalign}")
        # otherwise, it's custom - just return it directly
        return self.genderalign

    @property
    def gender_string(self):
        return i18n.t(f"general.{self.gender}")

    def is_alive(self):
        """Check if this cat is alive

        :return: True if alive, False if dead
        """
        return not self.dead

    def die(self, body: bool = True, grief_allowed: bool = True):
        """Kills cat.
        :param body: defaults to True, use this to mark if the body was recovered so
        that grief messages will align with body status
        :param grief_allowed: defaults to True, set to False if death should not trigger grief
        """
        if (
            self.status.is_leader
            and "pregnant" in self.injuries
            and game.clan.leader_lives > 0
        ):
            self.illnesses.clear()

            self.injuries = {
                key: value
                for (key, value) in self.injuries.items()
                if key == "pregnant"
            }
        else:
            self.injuries.clear()
            self.illnesses.clear()

        # Deal with leader death
        if self.status.is_leader:
            if game.clan.leader_lives > 0:
                self.assign_thought(CatThought.ON_DEATH)
                return

            if game.clan.leader_lives <= 0:
                self.dead = True
                game.just_died.append(self.ID)
                game.clan.leader_lives = 0

        else:
            self.dead = True
            game.just_died.append(self.ID)

        self.assign_thought(CatThought.ON_DEATH)

        for app in self.apprentice.copy():
            fetched_cat = Cat.fetch_cat(app)
            if fetched_cat:
                fetched_cat.update_mentor()
        self.update_mentor()

        # handle grief
        # since we just yeeted them to their afterlife, we gotta check their previous group affiliation, not current
        if (
            grief_allowed
            and game.clan
            and self.status.get_last_living_group() == CatGroup.PLAYER_CLAN_ID
            and not self.status.is_exiled(CatGroup.PLAYER_CLAN_ID)
        ):
            grief(self, body)
            game.dead_cats_to_grieve.append(self)

        # mark the sprite as outdated
        self.pelt.rebuild_sprite = True

    def exile(self):
        """This is used to send a cat into exile."""

        self.status.exile_from_group()
        self.assign_thought(CatThought.ON_EXILE)

        for app in self.apprentice:
            fetched_cat = Cat.fetch_cat(app)
            if fetched_cat:
                fetched_cat.update_mentor()
        self.update_mentor()

    def leave_clan(self, new_social_status: CatSocial):
        """Removes cat from the Clan willingly. Makes status changes and removes apprentices."""
        if not new_social_status:
            new_social_status = choice(
                (CatSocial.KITTYPET, CatSocial.LONER, CatSocial.ROGUE)
            )
        self.status.leave_group(new_social_status=new_social_status)
        self.assign_thought()

        for app in self.apprentice.copy():
            app_ob = Cat.fetch_cat(app)
            if app_ob:
                app_ob.update_mentor()

        self.update_mentor()

        for x in self.apprentice:
            Cat.fetch_cat(x).update_mentor()

    def become_lost(self):
        """Makes a Clan cat a lost cat. Makes status changes and removes apprentices."""

        self.status.become_lost(
            new_social_status=choice([CatSocial.KITTYPET, CatSocial.LONER])
        )

        for app in self.apprentice.copy():
            app_ob = Cat.fetch_cat(app)
            if app_ob:
                app_ob.update_mentor()

        self.update_mentor()

        self.assign_thought(CatThought.ON_LOST)

        for x in self.apprentice:
            Cat.fetch_cat(x).update_mentor()

    def rank_change(self, new_rank: CatRank, resort=False, new_thought=True):
        """Changes the status of a cat. Additional functions are needed if you want to make a cat a leader or deputy.
        :param new_rank: CatRank that the cat is becoming
        :param resort: If sorting type is 'rank', and resort is True, it will resort the cat list. This should
                only be true for non-timeskip status changes.
        :param new_thought: If true, cat will receive a special rank change thought. Default is True
        """

        old_rank = self.status.rank

        # this is a private function, but it's meant to be used here.
        self.status._change_rank(new_rank)  # pylint: disable=protected-access

        self.name.status = new_rank

        self.update_mentor()
        for app in self.apprentice.copy():
            fetched_cat = Cat.fetch_cat(app)
            if isinstance(fetched_cat, Cat):
                fetched_cat.update_mentor()

        # If they have any apprentices, make sure they are still valid:
        if old_rank == CatRank.MEDICINE_CAT and game.clan:
            game.clan.remove_med_cat(self)

        # updates mentors
        if self.status.rank in [
            CatRank.APPRENTICE,
            CatRank.MEDICINE_APPRENTICE,
            CatRank.MEDIATOR_APPRENTICE,
            CatRank.MEDIATOR,
        ]:
            pass

        elif self.status.rank in [CatRank.WARRIOR, CatRank.ELDER]:
            if not game.clan:
                pass
            elif old_rank == CatRank.LEADER and (
                game.clan.leader and game.clan.leader.ID == self.ID
            ):
                game.clan.leader = None
                game.clan.leader_predecessors += 1
            elif game.clan.deputy and game.clan.deputy.ID == self.ID:
                game.clan.deputy = None
                game.clan.deputy_predecessors += 1

        elif self.status.rank == CatRank.MEDICINE_CAT:
            if game.clan is not None:
                game.clan.new_medicine_cat(self)

        # update thought
        if new_thought and new_rank not in (
            CatRank.NEWBORN,
            CatRank.KITTEN,
        ):  # newborn and kitten aren't really "ranks" to be promoted to
            self.assign_thought(CatThought.ON_RANK_CHANGE)
        # however we don't want kittens to somehow have a newborn thought, so we'll have them reset to a normal kitten thought
        # just in case
        if new_thought and new_rank == CatRank.KITTEN:
            self.assign_thought()

        # update class dictionary
        self.all_cats[self.ID] = self

        # If we have it sorted by rank, we also need to re-sort
        if switch_get_value(Switch.sort_type) == "rank" and resort:
            Cat.sort_cats()

    def rank_change_traits_skill(self, mentor):
        """Updates trait and skill upon ceremony"""

        if self.status.rank in (
            CatRank.WARRIOR,
            CatRank.MEDICINE_CAT,
            CatRank.MEDIATOR,
        ):
            # Give a couple doses of mentor influence:
            if mentor:
                max_influence = randint(0, 2)
                i = 0
                while max_influence > i:
                    i += 1
                    affect_personality = self.personality.mentor_influence(
                        Cat.fetch_cat(mentor).personality
                    )
                    affect_skills = self.skills.mentor_influence(Cat.fetch_cat(mentor))
                    if affect_personality:
                        self.history.add_facet_mentor_influence(
                            mentor.ID,
                            affect_personality[0],
                            affect_personality[1],
                        )
                    if affect_skills:
                        self.history.add_skill_mentor_influence(
                            affect_skills[0], affect_skills[1], affect_skills[2]
                        )

            self.history.add_mentor_skill_influence_strings()
            self.history.add_mentor_facet_influence_strings()
        return

    def change_name(self, new_prefix=None, new_suffix=None):
        self.name = Name(
            prefix=new_prefix,
            suffix=new_suffix,
            biome=game.clan.biome,
            specsuffix_hidden=self.specsuffix_hidden,
            cat=self,
        )

    def change_affinity(self, starclan_change: int = 0, dark_forest_change: int = 0):
        """
        Changes the starclan and dark forest affinity of the cat; applying additional modifiers based on the closeness of the cat's personality facets to the facets of the respective afterlife
        :param starclan_change: The amount to change starclan affinity by
        :param dark_forest_change: The amount to change dark forest affinity by
        """
        modifier = get_config("affinity.base_compatibility_multiplier")

        if starclan_change:
            compatibility = game.starclan.get_compatibility(self)

            if compatibility == CatCompatibility.POSITIVE:
                starclan_change += round(starclan_change * modifier)
            elif compatibility == CatCompatibility.NEGATIVE:
                starclan_change -= round(starclan_change * modifier)

        if dark_forest_change:
            compatibility = game.dark_forest.get_compatibility(self)

            if compatibility == CatCompatibility.POSITIVE:
                dark_forest_change += round(dark_forest_change * modifier)
            elif compatibility == CatCompatibility.NEGATIVE:
                dark_forest_change -= round(dark_forest_change * modifier)

        self.starclan_affinity += starclan_change
        self.dark_forest_affinity += dark_forest_change

    def manage_outside_trait(self):
        """To be run every moon on outside cats
        to keep trait and skills making sense."""
        if not self.status.is_outsider and not self.status.is_other_clancat:
            return

        self.personality.set_kit(self.age.is_baby())  # Update kit trait stuff

    def describe_cat(self, short=False):
        """Generates a string describing the cat's appearance and gender.

        :param short: Whether to truncate the output, default False
        :type short: bool
        """
        output = Pelt.describe_appearance(self, short)
        # Add "a" or "an"
        if i18n.config.get("locale") == "en":
            output = f"an {output}" if output[0].lower() in "aeiou" else f"a {output}"
        # else:
        #     output = i18n.t("utility.indefinite", text=output, m_c=self)
        event_text_adjust(Cat, output, main_cat=self)
        return output

    def convert_history(self, died_by, scar_events):
        """
        Handle old history save conversions
        """
        deaths = []
        if died_by:
            deaths.extend(
                {"involved": None, "text": death, "moon": "?"} for death in died_by
            )
        scars = []
        if scar_events:
            scars.extend(
                {"involved": None, "text": scar, "moon": "?"} for scar in scar_events
            )
        self.history = History(died_by=deaths, scar_events=scars, cat=self)

    def load_history(self):
        """Load this cat's history"""
        if self._history:
            return

        try:
            if switch_get_value(Switch.clan_save_id) != "":
                clanname = switch_get_value(Switch.clan_save_id)
            else:
                clanname = switch_get_value(Switch.clan_list)[0]
        except IndexError:
            print("History failed to load, no Clan in switches?")
            self._history = History(
                beginning={},
                mentor_influence={},
                app_ceremony={},
                lead_ceremony=None,
                possible_history={},
                died_by=[],
                scar_events=[],
                murder={},
                cat=self,
            )
            return

        history_directory = f"{get_save_dir()}/{clanname}/history/"
        cat_history_directory = history_directory + self.ID + "_history.json"

        if not os.path.exists(cat_history_directory):
            self._history = History(
                beginning={},
                mentor_influence={},
                app_ceremony={},
                lead_ceremony=None,
                possible_history={},
                died_by=[],
                scar_events=[],
                murder={},
                cat=self,
            )
            return
        try:
            with open(cat_history_directory, "r", encoding="utf-8") as read_file:
                history_data = ujson.loads(read_file.read())

                self._history = History(
                    beginning=(
                        history_data["beginning"] if "beginning" in history_data else {}
                    ),
                    mentor_influence=(
                        history_data["mentor_influence"]
                        if "mentor_influence" in history_data
                        else {}
                    ),
                    app_ceremony=(
                        history_data["app_ceremony"]
                        if "app_ceremony" in history_data
                        else {}
                    ),
                    lead_ceremony=(
                        history_data["lead_ceremony"]
                        if "lead_ceremony" in history_data
                        else None
                    ),
                    possible_history=(
                        history_data["possible_history"]
                        if "possible_history" in history_data
                        else {}
                    ),
                    died_by=(
                        history_data["died_by"] if "died_by" in history_data else []
                    ),
                    scar_events=(
                        history_data["scar_events"]
                        if "scar_events" in history_data
                        else []
                    ),
                    murder=history_data["murder"] if "murder" in history_data else {},
                    afterlife_acceptance=(
                        history_data["afterlife_acceptance"]
                        if "afterlife_acceptance" in history_data
                        else None
                    ),
                    cat=self,
                )
        except Exception:
            self._history = None
            print(
                f"WARNING: There was an error reading the history file of cat #{self} or their history file was "
                f"empty. Default history info was given. Close game without saving if you have save information "
                f"you'd like to preserve!"
            )

    def save_history(self, history_dir):
        """Save this cat's history.

        :param history_dir: Directory to save cat's history to
        :type history_dir: str
        """
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        history_dict = self.history.make_dict()
        try:
            safe_save(f"{history_dir}/{self.ID}_history.json", history_dict)
        except:
            self.history = History(
                beginning={},
                mentor_influence={},
                app_ceremony={},
                lead_ceremony=None,
                possible_history={},
                died_by=[],
                scar_events=[],
                murder={},
                cat=self,
            )

            print(f"WARNING: saving history of cat #{self.ID} didn't work")

    def generate_lead_ceremony(self):
        """Create a leader ceremony and add it to the history"""

        load_leader_ceremonies()

        # determine which dict we're pulling from
        if game.clan.instructor.status.group == CatGroup.DARK_FOREST:
            starclan = False
            ceremony_dict: Dict = LEAD_CEREMONY_DF
        else:
            starclan = True
            ceremony_dict: Dict = LEAD_CEREMONY_SC

        # ---------------------------------------------------------------------------- #
        #                                    INTRO                                     #
        # ---------------------------------------------------------------------------- #
        all_intros = ceremony_dict["intros"]

        # filter the intros
        possible_intros = []
        for intro in all_intros:
            tags = all_intros[intro]["tags"]

            if game.clan.age != 0 and "new_clan" in tags:
                continue
            elif game.clan.age == 0 and "new_clan" not in tags:
                continue

            if (
                all_intros[intro]["lead_trait"]
                and self.personality.trait not in all_intros[intro]["lead_trait"]
            ):
                continue
            possible_intros.append(all_intros[intro])

        if chosen_intro := choice(possible_intros):
            intro = choice(chosen_intro["text"])
        else:
            intro = "this should not appear"

        # ---------------------------------------------------------------------------- #
        #                                 LIFE GIVING                                  #
        # ---------------------------------------------------------------------------- #
        life_givers = []
        dead_relations = []
        life_giving_leader = None
        num_of_lives_to_give = game.clan.leader_lives

        # grab life givers that the cat actually knew in life and sort by amount of relationship!
        relationships = self.relationships.values()

        for rel in relationships:
            kitty = self.fetch_cat(rel.cat_to)
            if kitty and kitty.dead and kitty.status.rank != CatRank.NEWBORN:
                # check where they reside
                if starclan:
                    if kitty.status.group != CatGroup.STARCLAN:
                        continue
                else:
                    if kitty.status.group != CatGroup.DARK_FOREST:
                        continue
                # guides aren't allowed here
                if kitty == game.clan.instructor:
                    continue
                else:
                    dead_relations.append(rel)

        # sort relations by the strength of their relationship
        dead_relations.sort(
            key=lambda rel: rel.romance
            + rel.like
            + rel.respect
            + rel.comfort
            + rel.trust,
            reverse=True,
        )

        # if we have relations, then make sure we only take the top 8
        if dead_relations:
            for i, rel in enumerate(dead_relations):
                if i >= num_of_lives_to_give - 1:
                    break
                if rel.cat_to.status.is_leader:
                    life_giving_leader = rel.cat_to
                    continue
                life_givers.append(rel.cat_to.ID)

        cats_in_afterlife = [
            self.fetch_cat(i)
            for i in game.clan.clan_cats
            if self.fetch_cat(i)
            and i not in life_givers
            and self.fetch_cat(i).status.group
            == (CatGroup.STARCLAN if starclan else CatGroup.DARK_FOREST)
        ]

        # check amount of life givers, if we need more, then grab from the other dead cats
        if len(life_givers) < num_of_lives_to_give - 1:
            extra_amount_needed = (num_of_lives_to_give - 1) - len(life_givers)

            possible_dead_cats = [
                i
                for i in cats_in_afterlife
                if i.status.rank not in (CatRank.LEADER, CatRank.NEWBORN)
            ]
            # this part just checks how many cats are available, if there aren't enough to fill all the slots,
            # then we just take however many are available

            if len(possible_dead_cats) - 1 < extra_amount_needed:
                extra_givers = possible_dead_cats
            else:
                extra_givers = sample(possible_dead_cats, k=extra_amount_needed)

            life_givers.extend(extra_givers)

        # making sure we have a leader at the end
        ancient_leader = False
        leaders = [x for x in cats_in_afterlife if x.status.is_leader]
        if not life_giving_leader and leaders:
            # choosing if the life giving leader will be the oldest leader or previous leader
            coin_flip = randint(1, 2)
            if coin_flip == 1:
                # pick the oldest leader
                leaders.sort(key=lambda x: -1 * int(x.dead_for))
                ancient_leader = True
                life_giving_leader = leaders[0]
            else:
                # pick previous leader
                leaders.sort(key=lambda x: int(Cat.fetch_cat(x).dead_for))
                life_giving_leader = leaders[0]

        if life_giving_leader:
            life_givers.append(life_giving_leader)

        # check amount again, if more are needed then we'll add the ghost-y cats at the end
        if len(life_givers) < num_of_lives_to_give:
            unknown_blessing = True
        else:
            unknown_blessing = False

        extra_lives = num_of_lives_to_give - len(life_givers)
        possible_lives = ceremony_dict["lives"]
        ceremony_entries = [{"involved": None, "text": intro}]
        used_lives = []
        used_virtues = []
        for giver in life_givers:
            giver_cat = self.fetch_cat(giver)
            if not giver_cat:
                continue
            life_list = []
            for life in possible_lives:
                tags = possible_lives[life]["tags"]
                rank = giver_cat.status.rank

                if "unknown_blessing" in tags:
                    continue

                if "guide" in tags and giver_cat != game.clan.instructor:
                    continue
                if game.clan.age != 0 and "new_clan" in tags:
                    continue
                elif game.clan.age == 0 and "new_clan" not in tags:
                    continue
                if "old_leader" in tags and not ancient_leader:
                    continue
                if "leader_parent" in tags and giver_cat.ID not in self.get_parents():
                    continue
                elif "leader_child" in tags and giver_cat.ID not in self.get_children():
                    continue
                elif (
                    "leader_sibling" in tags and giver_cat.ID not in self.get_siblings()
                ):
                    continue
                elif "leader_mate" in tags and giver_cat.ID not in self.mate:
                    continue
                elif (
                    "leader_former_mate" in tags
                    and giver_cat.ID not in self.previous_mates
                ):
                    continue
                if "leader_mentor" in tags and giver_cat.ID not in self.former_mentor:
                    continue
                if (
                    "leader_apprentice" in tags
                    and giver_cat.ID not in self.former_apprentices
                ):
                    continue
                if (
                    possible_lives[life]["rank"]
                    and rank not in possible_lives[life]["rank"]
                ):
                    continue
                if (
                    possible_lives[life]["lead_trait"]
                    and self.personality.trait not in possible_lives[life]["lead_trait"]
                ):
                    continue
                if possible_lives[life]["star_trait"] and (
                    giver_cat.personality.trait
                    not in possible_lives[life]["star_trait"]
                ):
                    continue
                life_list.extend(list(possible_lives[life]["life_giving"]))

            i = 0
            chosen_life = {}
            while i < 10:
                attempted = []
                if life_list:
                    chosen_life = choice(life_list)
                    if chosen_life not in used_lives and chosen_life not in attempted:
                        break
                    attempted.append(chosen_life)
                    i += 1
                else:
                    print(
                        f"WARNING: life list had no items for giver #{giver_cat.ID}. Using default life. "
                        f"If you are a beta tester, please report and ping scribble along with "
                        f"all the info you can about the giver cat mentioned in this warning."
                    )
                    chosen_life = ceremony_dict["default_life"]
                    break

            used_lives.append(chosen_life)
            if "virtue" in chosen_life:
                poss_virtues = [
                    i for i in chosen_life["virtue"] if i not in used_virtues
                ] or ["faith", "friendship", "love", "strength"]
                virtue = choice(poss_virtues)
                used_virtues.append(virtue)
            else:
                virtue = None

            ceremony_entries.append(
                {
                    "involved": giver_cat.ID,
                    "text": chosen_life["text"],
                    "virtue": virtue,
                }
            )
        if unknown_blessing:
            possible_blessing = []
            for life in possible_lives:
                tags = possible_lives[life]["tags"]

                if "unknown_blessing" not in tags:
                    continue

                if (
                    possible_lives[life]["lead_trait"]
                    and self.personality.trait not in possible_lives[life]["lead_trait"]
                ):
                    continue
                possible_blessing.append(possible_lives[life])
            chosen_blessing = choice(possible_blessing)
            chosen_text = choice(chosen_blessing["life_giving"])
            ceremony_entries.append(
                {
                    "involved": None,
                    "text": chosen_text["text"],
                    "virtue": chosen_text["virtue"],
                    "extra_lives": extra_lives,
                }
            )

        # ---------------------------------------------------------------------------- #
        #                                    OUTRO                                     #
        # ---------------------------------------------------------------------------- #

        # get the outro
        all_outros = ceremony_dict["outros"]

        possible_outros = []
        for outro in all_outros:
            tags = all_outros[outro]["tags"]

            if game.clan.age != 0 and "new_clan" in tags:
                continue
            elif game.clan.age == 0 and "new_clan" not in tags:
                continue

            if (
                all_outros[outro]["lead_trait"]
                and self.personality.trait not in all_outros[outro]["lead_trait"]
            ):
                continue
            possible_outros.append(all_outros[outro])

        chosen_outro = choice(possible_outros)

        outro_entry = {"involved": None, "text": "this should not appear"}
        if chosen_outro:
            outro_entry["text"] = choice(chosen_outro["text"])
            if "r_c" in outro_entry["text"] and life_givers:
                outro_giver_cat = self.fetch_cat(life_givers[-1])
                if outro_giver_cat:
                    outro_entry["involved"] = outro_giver_cat.ID

        ceremony_entries.append(outro_entry)

        self.history.lead_ceremony = ceremony_entries

    def render_lead_ceremony(self):
        """Render data with current name and pronouns."""

        data = self.history.lead_ceremony
        if not data:
            return ""
        if isinstance(data, str):
            # legacy ceremony is a string
            return data

        paragraphs = [
            leader_ceremony_text_adjust(
                Cat,
                entry["text"],
                leader=self,
                life_giver=entry.get("involved"),
                virtue=entry.get("virtue"),
                extra_lives=entry.get("extra_lives"),
            )
            for entry in data
        ]

        return "<br><br>".join(paragraphs)

    # ---------------------------------------------------------------------------- #
    #                              moon skip functions                             #
    # ---------------------------------------------------------------------------- #

    def one_moon(self, other_clan_cats: list = None):
        """Handles a moon skip for an alive cat."""
        old_age = self.age
        self.moons += 1
        if self.moons == 1 and self.status.rank == CatRank.NEWBORN:
            self.status._change_rank(CatRank.KITTEN)

        if old_age != self.age:
            # Things to do if the age changes
            self.personality.facet_wobble(facet_max=2)
            self.pelt.rebuild_sprite = True

        # reset next thought type
        self.assign_thought()

        if not self.status.alive_in_player_clan:
            # this is handled in events.py
            self.personality.set_kit(self.age.is_baby())
            return

        # Set personality to correct type
        self.personality.set_kit(self.age.is_baby())
        # Upon age-change

        if self.status.rank.is_any_apprentice_rank():
            self.update_mentor()

    def assign_thought(self, thought_type: CatThought = None):
        """
        Assigns next thought type to be displayed on cat's profile.
        :param thought_type: Indicate what type of thought should be generated
        """
        # reset current thought
        self.thought = None
        # default thought type
        if not thought_type:
            if game.clan and self is game.clan.instructor:
                thought_type = CatThought.IS_GUIDE
            elif self.dead:
                thought_type = CatThought.WHILE_DEAD
            else:
                thought_type = CatThought.WHILE_ALIVE

        self.next_thought_type = thought_type

    def moon_skip_illness(self, illness):
        """handles the moon skip for illness"""
        if not self.is_ill():
            return True

        if self.illnesses[illness]["event_triggered"]:
            self.illnesses[illness]["event_triggered"] = False
            return True

        mortality = self.illnesses[illness]["mortality"]

        # leader should have a higher chance of death
        if self.status.is_leader and mortality != 0:
            mortality = int(mortality * 0.7)
            if mortality == 0:
                mortality = 1

        if mortality and not int(random() * mortality):
            if self.status.is_leader:
                self.leader_death_heal = True
                game.clan.leader_lives -= 1

            self.die()
            return False

        moons_with = game.clan.age - self.illnesses[illness]["moon_start"]

        # focus buff
        recovery_buff = constants.CONFIG["focus"]["rest_and_recover"][
            "moons_earlier_healed"
        ]

        if self.illnesses[illness]["duration"] - moons_with <= 0:
            self.healed_condition = True
            return False

        # CLAN FOCUS! - if the focus 'rest_and_recover' is selected
        elif (
            get_clan_setting("rest_and_recover")
            and self.illnesses[illness]["duration"] - recovery_buff - moons_with <= 0
        ):
            self.healed_condition = True
            return False

    def moon_skip_injury(self, injury):
        """handles the moon skip for injury"""
        if not self.is_injured():
            return True

        if self.injuries[injury]["event_triggered"] is True:
            self.injuries[injury]["event_triggered"] = False
            return True

        mortality = self.injuries[injury]["mortality"]

        # leader should have a higher chance of death
        if self.status.is_leader and mortality != 0:
            mortality = int(mortality * 0.7)
            if mortality == 0:
                mortality = 1

        if mortality and not int(random() * mortality):
            if self.status.is_leader:
                game.clan.leader_lives -= 1
            self.die()
            return False

        moons_with = game.clan.age - self.injuries[injury]["moon_start"]

        # focus buff
        recovery_buff = constants.CONFIG["focus"]["rest_and_recover"][
            "moons_earlier_healed"
        ]

        # if the cat has an infected wound, the wound shouldn't heal till the illness is cured
        if (
            not self.injuries[injury]["complication"]
            and self.injuries[injury]["duration"] - moons_with <= 0
        ):
            self.healed_condition = True
            return False

        # CLAN FOCUS! - if the focus 'rest_and_recover' is selected
        elif (
            not self.injuries[injury]["complication"]
            and get_clan_setting("rest_and_recover")
            and self.injuries[injury]["duration"] - recovery_buff - moons_with <= 0
        ):
            self.healed_condition = True
            return False

    def moon_skip_permanent_condition(self, condition):
        """handles the moon skip for permanent conditions"""
        if not self.is_disabled():
            return "skip"

        if self.permanent_condition[condition]["event_triggered"]:
            self.permanent_condition[condition]["event_triggered"] = False
            return "skip"

        mortality = self.permanent_condition[condition]["mortality"]
        moons_until = self.permanent_condition[condition]["moons_until"]
        born_with = self.permanent_condition[condition]["born_with"]

        # handling the countdown till a congenital condition is revealed
        if moons_until is not None and moons_until >= 0 and born_with is True:
            self.permanent_condition[condition]["moons_until"] = int(moons_until - 1)
            self.permanent_condition[condition]["moons_with"] = 0
            if self.permanent_condition[condition]["moons_until"] != -1:
                return "skip"
        if (
            self.permanent_condition[condition]["moons_until"] == -1
            and self.permanent_condition[condition]["born_with"] is True
        ):
            self.permanent_condition[condition]["moons_until"] = -2
            return "reveal"

        # leader should have a higher chance of death
        if self.status.is_leader and mortality != 0:
            mortality = int(mortality * 0.7)
            if mortality == 0:
                mortality = 1

        if mortality and not int(random() * mortality):
            if self.status.is_leader:
                game.clan.leader_lives -= 1
            self.die()
            return "continue"

    # ---------------------------------------------------------------------------- #
    #                                   relative                                   #
    # ---------------------------------------------------------------------------- #
    def get_parents(self):
        """Returns list containing parent IDs of this cat.

        The order matters! The first cat will be considered the one who gave birth
        to this cat for queen calculations.
        """
        bio_parents = [parent for parent in (self.parent1, self.parent2) if parent]
        return bio_parents + self.adoptive_parents

    def get_siblings(self):
        """Returns list of the siblings(id)."""
        return inheritance_db.get_siblings(self.ID)

    def get_children(self):
        """Returns list of the children (ids)."""
        return inheritance_db.get_children(self.ID)

    def is_grandparent(self, other_cat: Cat):
        """Check if the cat is the grandparent of the other cat."""
        return inheritance_db.is_grandparent(self.ID, other_cat.ID)

    def is_parent(self, other_cat: Cat):
        """Check if the cat is the parent of the other cat."""
        return inheritance_db.is_parent(self.ID, other_cat.ID)

    def is_sibling(self, other_cat: Cat):
        """Check if the cats are siblings."""
        return inheritance_db.is_sibling(self.ID, other_cat.ID)

    def is_littermate(self, other_cat: Cat):
        """Check if the cats are littermates."""
        if not self.is_sibling(other_cat):
            return False
        return inheritance_db.is_littermate(self.ID, other_cat.ID)

    def is_uncle_aunt(self, other_cat: Cat):
        """Check if the cats are related as uncle/aunt and niece/nephew."""
        return inheritance_db.is_uncle_aunt(self.ID, other_cat.ID)

    def is_cousin(self, other_cat: Cat):
        """Check if this cat and other_cat are cousins."""
        return inheritance_db.is_cousin(self.ID, other_cat.ID)

    def is_related(self, other_cat, exclude_cousins):
        """Checks if the given cat is related to the current cat, according to the inheritance."""
        return inheritance_db.is_related(self.ID, other_cat.ID, exclude_cousins)

    def get_relatives(self, exclude_cousins=True) -> list:
        """Returns a list of ids of all nearly related ancestors."""
        return inheritance_db.get_relatives(self.ID, exclude_cousins)

    # ---------------------------------------------------------------------------- #
    #                                  conditions                                  #
    # ---------------------------------------------------------------------------- #

    def not_working(self):
        """returns True if the cat cannot work, False if the cat can work"""
        for illness in self.illnesses:
            if self.illnesses[illness]["severity"] != "minor":
                return True
        return any(
            self.injuries[injury]["severity"] != "minor" for injury in self.injuries
        )

    def not_work_because_hunger(self):
        """returns True if the only condition, why the cat cannot work is because of starvation"""
        non_minor_injuries = [
            injury
            for injury in self.injuries
            if self.injuries[injury]["severity"] != "minor"
        ]
        if len(non_minor_injuries) > 0:
            return False
        non_minor_illnesses = [
            illness
            for illness in self.illnesses
            if self.illnesses[illness]["severity"] != "minor"
        ]
        return "starving" in non_minor_illnesses and len(non_minor_illnesses) == 1

    def retire_cat(self):
        """This is only for cats that retire due to health condition"""

        # There are some special tasks we need to do for apprentice
        # Note that although you can un-retire cats, they will be a full warrior/med_cat/mediator
        if self.moons > 6 and self.status.rank.is_any_apprentice_rank():
            _ment = Cat.fetch_cat(self.mentor) if self.mentor else None
            self.rank_change(
                CatRank.WARRIOR
            )  # Temp switch them to warrior, so the following step will work
            self.rank_change_traits_skill(_ment)

        self.rank_change(CatRank.ELDER)
        return

    def is_ill(self):
        """Returns true if the cat is ill."""
        return len(self.illnesses) > 0

    def is_injured(self):
        """Returns true if the cat is injured."""
        return len(self.injuries) > 0

    def is_disabled(self):
        """Returns true if the cat have permanent condition"""
        return len(self.permanent_condition) > 0

    def available_to_work(self):
        return self.status.alive_in_player_clan and not self.not_working()

    def save_condition(self):
        # save conditions for each cat
        save_id = None
        if switch_get_value(Switch.clan_save_id) != "":
            save_id = switch_get_value(Switch.clan_save_id)
        elif len(switch_get_value(Switch.clan_list)) > 0:
            save_id = switch_get_value(Switch.clan_list)[0]
        elif game.clan is not None:
            save_id = game.clan.save_id

        condition_directory = get_save_dir() + "/" + save_id + "/conditions"
        condition_file_path = condition_directory + "/" + self.ID + "_conditions.json"

        if (not self.is_ill() and not self.is_injured() and not self.is_disabled()) or (
            (self.dead or self.status.is_outsider) and not self.is_disabled()
        ):
            if os.path.exists(condition_file_path):
                os.remove(condition_file_path)
            return

        conditions = {}

        if self.is_ill():
            conditions["illnesses"] = self.illnesses

        if self.is_injured():
            conditions["injuries"] = self.injuries

        if self.is_disabled():
            conditions["permanent conditions"] = self.permanent_condition

        safe_save(condition_file_path, conditions)

    def load_conditions(self):
        if switch_get_value(Switch.clan_save_id) != "":
            clanname = switch_get_value(Switch.clan_save_id)
        else:
            clanname = switch_get_value(Switch.clan_list)[0]

        condition_directory = get_save_dir() + "/" + clanname + "/conditions/"
        condition_cat_directory = condition_directory + self.ID + "_conditions.json"
        if not os.path.exists(condition_cat_directory):
            return

        try:
            with open(condition_cat_directory, "r", encoding="utf-8") as read_file:
                rel_data = ujson.loads(read_file.read())
                self.illnesses = rel_data.get("illnesses", {})
                self.injuries = rel_data.get("injuries", {})
                self.permanent_condition = rel_data.get("permanent conditions", {})

            if "paralyzed" in self.permanent_condition and not self.pelt.paralyzed:
                self.pelt.paralyzed = True

        except Exception as e:
            print(
                f"WARNING: There was an error reading the condition file of cat #{self}.\n",
                e,
            )

    # ---------------------------------------------------------------------------- #
    #                                    mentor                                    #
    # ---------------------------------------------------------------------------- #

    def is_valid_mentor(self, potential_mentor: Cat):
        # If not an app, don't need a mentor
        if not self.status.rank.is_any_apprentice_rank():
            return False

        # App and mentor must be members of the same clan
        if self.status.group_ID != potential_mentor.status.group_ID:
            return False

        # Match jobs
        if (
            self.status.rank == CatRank.MEDICINE_APPRENTICE
            and potential_mentor.status.rank != CatRank.MEDICINE_CAT
        ):
            return False
        if (
            self.status.rank == CatRank.APPRENTICE
            and potential_mentor.status.rank
            not in [CatRank.LEADER, CatRank.DEPUTY, CatRank.WARRIOR]
        ):
            return False
        if (
            self.status.rank == CatRank.MEDIATOR_APPRENTICE
            and potential_mentor.status.rank != CatRank.MEDIATOR
        ):
            return False

        return True

    def __remove_mentor(self):
        """Should only be called by update_mentor, also sets fields on mentor."""
        if not self.mentor:
            return
        mentor_cat = Cat.fetch_cat(self.mentor)
        if not mentor_cat:
            return
        if self.ID in mentor_cat.apprentice:
            mentor_cat.apprentice.remove(self.ID)
        if self.moons > 6:
            if self.ID not in mentor_cat.former_apprentices:
                mentor_cat.former_apprentices.append(self.ID)
            if mentor_cat.ID not in self.former_mentor:
                self.former_mentor.append(mentor_cat.ID)
        self.mentor = None

    def __add_mentor(self, new_mentor_id: str):
        """Should only be called by update_mentor, also sets fields on mentor."""
        # reset patrol number
        self.patrol_with_mentor = 0
        self.mentor = new_mentor_id
        mentor_cat = Cat.fetch_cat(self.mentor)
        if not mentor_cat:
            return
        if self.ID not in mentor_cat.apprentice:
            mentor_cat.apprentice.append(self.ID)

    def update_mentor(self, new_mentor: Any = None):
        """Takes mentor's ID as argument, mentor could just be set via this function."""
        # No !!
        if isinstance(new_mentor, Cat):
            print("Everything is terrible!! (new_mentor {new_mentor} is a Cat D:)")
            return

        # Check if cat can have a mentor
        if (
            self.dead
            or self.status.is_outsider
            or not self.status.rank.is_any_apprentice_rank()
        ):
            self.__remove_mentor()
            return

        # If eligible, cat should get a mentor.
        if new_mentor:
            self.__remove_mentor()
            self.__add_mentor(new_mentor)

        # Check if current mentor is valid
        if self.mentor:
            mentor_cat = Cat.fetch_cat(
                self.mentor
            )  # This will return None if there is no current mentor
            if mentor_cat and not self.is_valid_mentor(mentor_cat):
                self.__remove_mentor()

        # Need to pick a random mentor if not specified
        if not self.mentor:
            potential_mentors = []
            priority_mentors = []
            for cat in self.all_cats.values():
                if self.is_valid_mentor(cat):
                    potential_mentors.append(cat)
                    if not cat.apprentice and not cat.not_working():
                        priority_mentors.append(cat)
            # First try for a cat who currently has no apprentices and is working
            if priority_mentors:  # length of list > 0
                new_mentor = choice(priority_mentors)
            elif potential_mentors:  # length of list > 0
                new_mentor = choice(potential_mentors)
            if new_mentor:
                self.__add_mentor(new_mentor.ID)

    # ---------------------------------------------------------------------------- #
    #                                 relationships                                #
    # ---------------------------------------------------------------------------- #
    def is_potential_mate(
        self,
        other_cat: Cat,
        for_love_interest: bool = False,
        age_restriction: bool = True,
        first_cousin_mates: bool = False,
        ignore_no_mates: bool = False,
    ):
        """
        Checks if this cat is potential mate for the other cat.
        There are no restrictions if the current cat already has a mate or not (this allows poly-mates).
        """

        try:
            first_cousin_mates = get_clan_setting("first cousin mates")
        except:
            if "unittest" not in sys.modules:
                raise

        # just to be sure, check if it is not the same cat
        if self.ID == other_cat.ID:
            return False

        # No Mates Check
        if not ignore_no_mates and (self.no_mates or other_cat.no_mates):
            return False

        # Inheritance check
        if self.is_related(other_cat, first_cousin_mates):
            return False

        # check dead cats
        if self.dead != other_cat.dead:
            return False

        # check that outside status is the same
        if self.status.is_outsider != other_cat.status.is_outsider:
            return False

        # check for age
        if age_restriction:
            if (self.moons < 14 or other_cat.moons < 14) and not for_love_interest:
                return False

            # the +1 is necessary because both might not already be aged up
            # if only one is aged up at this point, later they are more moons apart than the setting defined
            # constants.CONFIG boolean "override_same_age_group" disables the same-age group check.
            if (
                constants.CONFIG["mates"].get("override_same_age_group", False)
                or self.age != other_cat.age
            ) and (
                abs(self.moons - other_cat.moons)
                > constants.CONFIG["mates"]["age_range"] + 1
            ):
                return False

        if (
            not self.age.can_have_mate() or not other_cat.age.can_have_mate()
        ) and self.age != other_cat.age:
            return False

        # check for mentor

        # Current mentor
        if other_cat.ID in self.apprentice or self.ID in other_cat.apprentice:
            return False

        # Former mentor
        is_former_mentor = (
            other_cat.ID in self.former_apprentices
            or self.ID in other_cat.former_apprentices
        )
        return bool(
            not is_former_mentor or get_clan_setting("romantic with former mentor")
        )

    def unset_mate(
        self, other_cat: Cat, user_initiated_breakup: bool = False, fight: bool = False
    ):
        """Unset the mate from both self and other_cat"""
        if not other_cat:
            return

        # Both cats must have mates for this to work
        if len(self.mate) < 1 or len(other_cat.mate) < 1:
            return

        # AND they must be mates with each other.
        if self.ID not in other_cat.mate or other_cat.ID not in self.mate:
            print(
                f"Unsetting mates: These {self.name} and {other_cat.name} are not mates!"
            )
            return

        # If only deal with relationships if this is a breakup.
        if user_initiated_breakup:
            self_relationship = None
            if not self.dead:
                if other_cat.ID not in self.relationships:
                    create_one_relationship(self, other_cat)
                self_relationship = self.relationships[other_cat.ID]
                self_relationship.romance -= randint(20, 60)
                self_relationship.comfort -= randint(10, 30)
                self_relationship.trust -= randint(5, 15)
                if fight:
                    self_relationship.romance -= randint(10, 30)
                    self_relationship.like -= randint(15, 45)

            if not other_cat.dead:
                if self.ID not in other_cat.relationships:
                    create_one_relationship(other_cat, self)
                other_relationship = other_cat.relationships[self.ID]
                other_relationship.romance -= 40
                other_relationship.comfort -= 20
                other_relationship.trust -= 10
                if fight:
                    self_relationship.romance -= 20
                    other_relationship.like -= 30

        self.mate.remove(other_cat.ID)
        other_cat.mate.remove(self.ID)

        # Handle previous mates:
        if other_cat.ID not in self.previous_mates:
            self.previous_mates.append(other_cat.ID)
        if self.ID not in other_cat.previous_mates:
            other_cat.previous_mates.append(self.ID)

        inheritance_db.load_inheritances(Cat)

    def set_mate(self, other_cat: Cat, recalculate_inheritance: bool = True):
        """
        Sets up a mate relationship between self and other_cat.
        :param other_cat: The other cat
        :param recalculate_inheritance: Set to False if this func should SKIP recalculating inheritance. Take care when using this.
        """
        if other_cat.ID not in self.mate:
            self.mate.append(other_cat.ID)
        if self.ID not in other_cat.mate:
            other_cat.mate.append(self.ID)

        # If the current mate was in the previous mate list, remove them.
        if other_cat.ID in self.previous_mates:
            self.previous_mates.remove(other_cat.ID)
        if self.ID in other_cat.previous_mates:
            other_cat.previous_mates.remove(self.ID)

        if recalculate_inheritance:
            inheritance_db.load_inheritances(Cat)

        # Set starting relationship values
        if not self.dead:
            if other_cat.ID not in self.relationships:
                create_one_relationship(self, other_cat)
                self.relationships[other_cat.ID].mates = True
            self_relationship = self.relationships[other_cat.ID]
            self_relationship.romance += 20
            self_relationship.comfort += 20
            self_relationship.trust += 10
            self_relationship.mates = True

        if not other_cat.dead:
            if self.ID not in other_cat.relationships:
                create_one_relationship(other_cat, self)
                other_cat.relationships[self.ID].mates = True
            other_relationship = other_cat.relationships[self.ID]
            other_relationship.romance += 20
            other_relationship.comfort += 20
            other_relationship.trust += 10
            other_relationship.mates = True

    def unset_adoptive_parent(self, other_cat: Cat):
        """Unset the adoptive parent from self"""
        self.adoptive_parents.remove(other_cat.ID)
        inheritance_db.load_inheritances(Cat)
        if not self.dead:
            if other_cat.ID not in self.relationships:
                create_one_relationship(self, other_cat)
            self_relationship = self.relationships[other_cat.ID]
            self_relationship.like -= randint(10, 30)
            self_relationship.comfort -= randint(10, 30)
            self_relationship.trust -= randint(5, 15)

        if not other_cat.dead:
            if self.ID not in other_cat.relationships:
                create_one_relationship(other_cat, self)
            other_relationship = other_cat.relationships[self.ID]
            other_relationship.like -= 20
            other_relationship.comfort -= 20
            other_relationship.trust -= 10

    def set_adoptive_parent(self, other_cat: Cat):
        """Sets up a parent-child relationship between self and other_cat."""
        self.adoptive_parents.append(other_cat.ID)
        inheritance_db.load_inheritances(Cat)

        # Set starting relationship values
        if not self.dead:
            if other_cat.ID not in self.relationships:
                create_one_relationship(self, other_cat)
            self_relationship = self.relationships[other_cat.ID]
            self_relationship.like += 20
            self_relationship.comfort += 20
            self_relationship.trust += 10

        if not other_cat.dead:
            if self.ID not in other_cat.relationships:
                create_one_relationship(other_cat, self)
            other_relationship = other_cat.relationships[self.ID]
            other_relationship.like += 20
            other_relationship.comfort += 20
            other_relationship.trust += 10

    def create_inheritance_new_cat(self):
        """Creates the inheritance class for a new cat."""
        # set the born status to true, just for safety
        self.inheritance = Inheritance(self, True)

    def save_relationship_of_cat(self, relationship_dir):
        # save relationships for each cat

        rel = []
        for r in self.relationships.values():
            rel.append(r.to_dict())

        safe_save(f"{relationship_dir}/{self.ID}_relations.json", rel)

    @staticmethod
    def mediate_relationship(mediator, cat1, cat2, allow_romantic, sabotage=False):
        # Gather some important info

        # Gathering the relationships.
        if cat1.ID in cat2.relationships:
            rel1 = cat1.relationships[cat2.ID]
        else:
            rel1 = create_one_relationship(cat1, cat2)

        if cat2.ID in cat1.relationships:
            rel2 = cat2.relationships[cat1.ID]
        else:
            rel2 = create_one_relationship(cat2, cat1)

        # Output string.
        output = ""

        # Determine the chance of failure.
        if mediator.experience_level == "untrained":
            chance = 15
        elif mediator.experience_level == "learning":
            # Negative bonus for very low.
            chance = 20
        elif mediator.experience_level == "prepared":
            chance = 35
        elif mediator.experience_level == "proficient":
            chance = 55
        elif mediator.experience_level == "adept":
            chance = 70
        elif mediator.experience_level == "masterful":
            chance = 100
        else:
            chance = 40

        compat = get_personality_compatibility(cat1, cat2)
        if compat == CatCompatibility.POSITIVE:
            chance += 10
        elif compat == CatCompatibility.NEGATIVE:
            chance -= 5

        # Cat's compatibility with mediator also has an effect on success chance.
        for cat in (cat1, cat2):
            if (
                get_personality_compatibility(cat, mediator)
                == CatCompatibility.POSITIVE
            ):
                chance += 5
            elif (
                get_personality_compatibility(cat, mediator)
                == CatCompatibility.NEGATIVE
            ):
                chance -= 5

        # Determine chance to fail, turning sabotage into mediate and mediate into sabotage
        if not int(random() * chance):
            apply_bonus = False
            if sabotage:
                output += i18n.t("screens.mediation.sabotage_failed")
                sabotage = False
            else:
                output += i18n.t("screens.mediation.mediate_failed")
                sabotage = True
        else:
            apply_bonus = True
            # EX gain on success
            if mediator.status.rank == CatRank.MEDIATOR:
                exp_gain = randint(10, 24)

                gm_modifier = 1
                if game.clan and game.clan.game_mode == "expanded":
                    gm_modifier = 3

                if mediator.experience_level == "proficient":
                    lvl_modifier = 1.25
                elif mediator.experience_level == "adept":
                    lvl_modifier = 1.75
                elif mediator.experience_level == "masterful":
                    lvl_modifier = 2
                else:
                    lvl_modifier = 1
                mediator.add_experience(exp_gain / lvl_modifier / gm_modifier)

        if mediator.status.rank == CatRank.MEDIATOR_APPRENTICE:
            mediator.add_experience(max(randint(1, 6), 1))

        # determine the traits to effect
        # Are they mates?
        mates = rel1.cat_from.ID in rel1.cat_to.mate

        rel_values = [v for v in [*RelType] if v != RelType.ROMANCE]
        if allow_romantic and (mates or cat1.is_potential_mate(cat2)):
            rel_values.append(RelType.ROMANCE)

        # Determine the number of traits to effect, and choose the traits
        chosen_rel = sample(rel_values, k=randint(2, len(rel_values)))

        if compat is True:
            personality_bonus = 2
        elif compat is False:
            personality_bonus = -2
        else:
            personality_bonus = 0

        # Effects on traits
        for rel_type in chosen_rel:
            # The EX bonus in not applied upon a fail.
            if apply_bonus:
                if mediator.experience_level == "very low":
                    # Negative bonus for very low.
                    bonus = randint(-2, -1)
                elif mediator.experience_level == "low":
                    bonus = randint(-2, 0)
                elif mediator.experience_level == "high":
                    bonus = randint(1, 3)
                elif mediator.experience_level == "masterful":
                    bonus = randint(3, 4)
                elif mediator.experience_level == "max":
                    bonus = randint(4, 5)
                else:
                    bonus = 0  # Average gets no bonus.
            else:
                bonus = 0

            ran = (5, 10) if rel_type == RelType.ROMANCE and mates else (4, 6)

            amount = ((randint(ran[0], ran[1]) + bonus) + personality_bonus) * (
                -1 if sabotage else 1
            )

            setattr(rel1, rel_type, getattr(rel1, rel_type) + amount)
            setattr(rel2, rel_type, getattr(rel2, rel_type) + amount)

            output += i18n.t(
                f"screens.mediation.output_{'decrease' if sabotage else 'increase'}",
                trait=i18n.t(f"screens.mediation.{rel_type}"),
            )

        return output

    def set_faded(self):
        """This function is for cats that are faded. It will set the sprite and the faded tag"""
        self.faded = True

        # Silhouette sprite
        if self.age == CatAge.NEWBORN:
            file_name = "faded_newborn"
        elif self.age == CatAge.KITTEN:
            file_name = "faded_kitten"
        elif self.age in [
            CatAge.ADULT,
            CatAge.YOUNG_ADULT,
            CatAge.SENIOR_ADULT,
        ]:
            file_name = "faded_adult"
        elif self.age == CatAge.ADOLESCENT:
            file_name = "faded_adol"
        else:
            file_name = "faded_senior"

        if self.status.group == CatGroup.DARK_FOREST:
            file_name += "_df"
        elif self.status.group == CatGroup.UNKNOWN_RESIDENCE:
            file_name += "_ur"

        file_name += ".png"

        self.sprite = image_cache.load_image(
            f"sprites/faded/{file_name}"
        ).convert_alpha()

    @staticmethod
    def fetch_cat(ID: str):
        """Fetches a cat object. Works for both faded and non-faded cats. Returns none if no cat was found."""
        if not ID or isinstance(ID, Cat):  # Check if argument is None or Cat.
            return ID
        elif not isinstance(ID, str):  # Invalid type
            return None
        if ID in Cat.all_cats:
            return Cat.all_cats[ID]
        else:
            return ob if (ob := Cat.load_faded_cat(ID)) else None

    @staticmethod
    def load_faded_cat(cat: str):
        """Loads a faded cat, returning the cat object. This object is saved nowhere else."""

        # just preventing any attempts to load something that isn't a cat ID
        if not cat.isdigit():
            print(f'ERROR: in loading faded cat: "{cat}" is not a valid cat ID')
            return

        try:
            # todo: why can't this be `get_switch(Switch.clan_name)`?
            clan = (
                switch_get_value(Switch.clan_list)[0]
                if game.clan is None
                else game.clan.save_id
            )

            with open(
                get_save_dir() + "/" + clan + "/faded_cats/" + cat + ".json",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_info = ujson.loads(read_file.read())
                # If loading cats is attempted before the Clan is loaded, we would need to use this.

        except (
            AttributeError
        ):  # NOPE, cats are always loaded before the Clan, so doesn't make sense to throw an error
            with open(
                get_save_dir()
                + "/"
                + switch_get_value(Switch.clan_list)[0]
                + "/faded_cats/"
                + cat
                + ".json",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_info = ujson.loads(read_file.read())
        except Exception as e:
            print(f'ERROR: in loading faded cat "{cat}": {e!r}')
            return False

        if isinstance(cat_info["status"], str):
            status = Status(rank=cat_info["status"])
            # they are definitely dead
            status.send_to_afterlife(
                CatGroup.DARK_FOREST_ID
                if cat_info.get("df", False)
                else CatGroup.STARCLAN_ID
            )
        else:
            status = Status(**cat_info["status"])

        cat_ob = Cat(
            ID=cat_info["ID"],
            gender_dict=GenderDict(sex=None, genderalign=None),
            pelt=None,
            moons=cat_info["moons"],
            status=status,
            backstory="",
            skills=None,
            personality=None,
            mentorship={},
            inheritance=InheritanceDict(
                parent1=cat_info["parent1"],
                parent2=cat_info["parent2"],
                adoptive_parents=cat_info["adoptive_parents"],
                mate=[],
                previous_mates=[],
                faded_offspring=cat_info["faded_offspring"],
            ),
            affinity={},
            toggles={},
            experience=0,
            birth_cooldown=0,
            specsuffix_hidden=False,
            faded=True,
        )

        cat_ob.name = Name(
            prefix=cat_info["name_prefix"],
            suffix=cat_info["name_suffix"],
            specsuffix_hidden=False,
            load_existing_name=True,
            cat=cat_ob,
        )

        return cat_ob

    # ---------------------------------------------------------------------------- #
    #                                  Sorting                                     #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def sort_cats(given_list=None):
        # disable unnecessary lambda in this function
        # pylint: disable=unnecessary-lambda
        if given_list is None:
            given_list = []
        if not given_list:
            given_list = Cat.all_cats_list
        sort_type = switch_get_value(Switch.sort_type)
        if sort_type == "age":
            given_list.sort(key=lambda x: Cat.get_adjusted_age(x))
        elif sort_type == "reverse_age":
            given_list.sort(key=lambda x: Cat.get_adjusted_age(x), reverse=True)
        elif sort_type == "id":
            given_list.sort(key=lambda x: int(x.ID))
        elif sort_type == "reverse_id":
            given_list.sort(key=lambda x: int(x.ID), reverse=True)
        elif sort_type == "rank":
            given_list.sort(
                key=lambda x: (Cat.rank_order(x), Cat.get_adjusted_age(x)), reverse=True
            )
        elif sort_type == "exp":
            given_list.sort(key=lambda x: x.experience, reverse=True)
        elif sort_type == "death":
            given_list.sort(key=lambda x: -1 * int(x.dead_for))
        elif sort_type == "name":
            given_list.sort(key=lambda x: x.name.prefix.lower())
        elif sort_type == "reverse_name":
            given_list.sort(key=lambda x: x.name.prefix.lower(), reverse=True)

        return

    @staticmethod
    def insert_cat(c: Cat):
        sort_type = switch_get_value(Switch.sort_type)
        try:
            if sort_type == "age":
                bisect.insort(
                    Cat.all_cats_list, c, key=lambda x: Cat.get_adjusted_age(x)
                )
            elif sort_type == "reverse_age":
                bisect.insort(
                    Cat.all_cats_list, c, key=lambda x: -1 * Cat.get_adjusted_age(x)
                )
            elif sort_type == "rank":
                bisect.insort(
                    Cat.all_cats_list,
                    c,
                    key=lambda x: (
                        -1 * Cat.rank_order(x),
                        -1 * Cat.get_adjusted_age(x),
                    ),
                )
            elif sort_type == "exp":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: x.experience)
            elif sort_type == "id":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: int(x.ID))
            elif sort_type == "reverse_id":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: -1 * int(x.ID))
            elif sort_type == "death":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: -1 * int(x.dead_for))
            elif sort_type == "name":
                bisect.insort(Cat.all_cats_list, c, key=lambda x: int(x.name.prefix))
            elif sort_type == "reverse_name":
                bisect.insort(
                    Cat.all_cats_list, c, key=lambda x: -1 * int(x.name.prefix)
                )
        except (TypeError, NameError):
            # If you are using python 3.8, key is not a supported parameter into insort. Therefore, we'll need to
            # do the slower option of adding the cat, then resorting
            Cat.all_cats_list.append(c)
            Cat.sort_cats()

    @staticmethod
    def rank_order(cat: Cat):
        if cat.status.rank in Cat.rank_sort_order:
            return Cat.rank_sort_order.index(cat.status.rank)
        else:
            return 0

    @staticmethod
    def get_adjusted_age(cat: Cat):
        """Returns the moons + dead_for moons rather than the moons at death for dead cats, so dead cats are sorted by
        total age, rather than age at death"""
        if cat.dead:
            if constants.CONFIG["sorting"]["sort_rank_by_death"]:
                if switch_get_value(Switch.sort_type) == "rank":
                    return cat.dead_for
                else:
                    if constants.CONFIG["sorting"]["sort_dead_by_total_age"]:
                        return cat.dead_for + cat.moons
                    else:
                        return cat.moons
            else:
                if constants.CONFIG["sorting"]["sort_dead_by_total_age"]:
                    return cat.dead_for + cat.moons
                else:
                    return cat.moons
        else:
            return cat.moons

    # ---------------------------------------------------------------------------- #
    #                                  properties                                  #
    # ---------------------------------------------------------------------------- #

    @property
    def experience(self):
        return self._experience

    @property
    def experience_level(self):
        return next(
            key
            for key, (min_exp, max_exp) in self.experience_levels_range.items()
            if min_exp <= self.experience <= max_exp
        )

    @experience.setter
    def experience(self, exp: int):
        exp = min(exp, self.experience_levels_range["masterful"][1])
        self._experience = int(exp)

    def add_experience(self, amount):
        """adds experience, scaled by progress.difficulty_modifier"""

        ceiling = Cat.experience_levels_range["masterful"][1]
        scaled = scale_progress(self.experience, ceiling, amount)
        # stochastic rounding so experience still increases on average
        gain = int(scaled)
        if random() < scaled - gain:
            gain += 1
        self.experience = self.experience + gain

    @property
    def experience_level_string(self):
        return i18n.t(f"cat.skills.{self.experience_level}")

    @property
    def moons(self):
        return self._moons

    @moons.setter
    def moons(self, value: int):
        self._moons = value

    @property
    def sprite(self):
        if self.faded:
            return self._sprite

        # Update the sprite
        if self.pelt.rebuild_sprite or self.not_working() != self._sprite_working:
            self.pelt.rebuild_sprite = False
            self._sprite_working = self.not_working()
            update_sprite(self)
            update_mask(self)
        return self._sprite

    @sprite.setter
    def sprite(self, new_sprite):
        self._sprite = new_sprite

    @property
    def sprite_mask(self):
        if (
            scripts.game_structure.screen_settings.screen_scale
            != self.pelt.screen_scale
        ):
            self.pelt.screen_scale = scripts.game_structure.screen_settings.screen_scale
            update_mask(self)
        return self._sprite_mask

    @sprite_mask.setter
    def sprite_mask(self, val):
        self._sprite_mask = val

    # ---------------------------------------------------------------------------- #
    #                                  other                                       #
    # ---------------------------------------------------------------------------- #

    def get_info_block(self, *, make_clan=False, patrol=False, relationship=False):
        if make_clan:
            return "\n".join(
                [
                    self.genderalign_string,
                    i18n.t(
                        (
                            f"general.{self.age}"
                            if self.age != "kitten"
                            else "general.kitten_profile"
                        ),
                        count=1,
                    ),
                    i18n.t(f"cat.personality.{self.personality.trait}"),
                    self.skills.skill_string(
                        is_adolescent=(self.age == CatAge.ADOLESCENT)
                    ),
                ]
            )
        elif patrol:
            return "<br>".join(
                [
                    i18n.t(f"general.{self.status.rank.lower()}", count=1),
                    i18n.t(f"cat.personality.{self.personality.trait}"),
                    self.skills.skill_string(short=True),
                    i18n.t(f"cat.skills.{self.experience_level}")
                    + (
                        f" ({str(self.experience)})\n"
                        if get_clan_setting("showxp")
                        else "\n"
                    ),
                ]
            )
        elif relationship:
            return " - ".join(
                [
                    i18n.t("general.moons_age", count=self.moons),
                    self.genderalign_string,
                    i18n.t(f"cat.personality.{self.personality.trait}"),
                ]
            )

        return "\n".join(
            [
                i18n.t("general.moons_age", count=self.moons),
                i18n.t(f"general.{self.status.rank.lower()}", count=1),
                self.genderalign_string,
                i18n.t(f"cat.personality.{self.personality.trait}"),
                self.skills.skill_string(short=True),
            ]
        )

    def get_save_dict(self, faded=False):
        if faded:
            return {
                "ID": self.ID,
                "name_prefix": self.name.prefix,
                "name_suffix": self.name.suffix,
                "status": self.status.get_status_dict(),
                "moons": self.moons,
                "dead_for": self.dead_for,
                "parent1": self.parent1,
                "parent2": self.parent2,
                "adoptive_parents": self.adoptive_parents,
                "faded_offspring": self.faded_offspring,
            }
        else:
            return {
                "ID": self.ID,
                "name_prefix": self.name.prefix,
                "name_suffix": self.name.suffix,
                "specsuffix_hidden": self.name.specsuffix_hidden,
                "gender": self.gender,
                "gender_align": self.genderalign,
                "pronouns": (
                    self._pronouns
                    if self._pronouns is not None
                    else {i18n.config.get("locale"): self.pronouns}
                ),
                "birth_cooldown": self.birth_cooldown,
                "status": self.status.get_status_dict(),
                "dark_forest_affinity": self.dark_forest_affinity,
                "starclan_affinity": self.starclan_affinity,
                "backstory": self.backstory or None,
                "moons": self.moons,
                "trait": self.personality.trait,
                "facets": self.personality.get_facet_string(),
                "parent1": self.parent1,
                "parent2": self.parent2,
                "adoptive_parents": self.adoptive_parents,
                "mentor": self.mentor or None,
                "former_mentor": (
                    list(self.former_mentor) if self.former_mentor else []
                ),
                "patrol_with_mentor": (self.patrol_with_mentor or 0),
                "mate": self.mate,
                "previous_mates": self.previous_mates,
                "paralyzed": self.pelt.paralyzed,
                "no_kits": self.no_kits,
                "no_retire": self.no_retire,
                "no_mates": self.no_mates,
                "pelt_name": self.pelt.name,
                "pelt_color": self.pelt.colour,
                "pelt_length": self.pelt.length,
                "sprite_newborn": self.pelt.cat_sprites["newborn"],
                "sprite_kitten": self.pelt.cat_sprites["kitten"],
                "sprite_adolescent": self.pelt.cat_sprites["adolescent"],
                "sprite_adult": self.pelt.cat_sprites["adult"],
                "sprite_senior": self.pelt.cat_sprites["senior"],
                "sprite_para_adult": self.pelt.cat_sprites["para_adult"],
                "eye_colour": self.pelt.eye_colour,
                "eye_colour2": (self.pelt.eye_colour2 or None),
                "reverse": self.pelt.reverse,
                "white_patches": self.pelt.white_patches,
                "vitiligo": self.pelt.vitiligo,
                "points": self.pelt.points,
                "white_patches_tint": self.pelt.white_patches_tint,
                "tortie_marking": self.pelt.tortie_marking,
                "tortie_base": self.pelt.tortie_base,
                "tortie_color": self.pelt.tortie_colour,
                "tortie_pattern": self.pelt.tortie_pattern,
                "skin": self.pelt.skin,
                "tint": self.pelt.tint,
                "skill_dict": self.skills.get_skill_dict(),
                "scars": self.pelt.scars or [],
                "accessory": self.pelt.accessory,
                "experience": self.experience,
                "current_apprentice": list(self.apprentice),
                "former_apprentices": list(self.former_apprentices),
                "faded_offspring": self.faded_offspring,
                "opacity": self.pelt.opacity,
                "prevent_fading": self.prevent_fading,
                "favourite": self.favourite,
            }

    def determine_next_and_previous_cats(
        self, filter_func: Callable[[Cat], bool] = None
    ):
        """Determines where the next and previous buttons point to, relative to this cat.

        :param filter_func: Allows you to constrain the list by any attribute of
            the Cat object. Takes a function which takes in a Cat instance and
            returns a boolean.
        """

        sorted_specific_list = [
            check_cat
            for check_cat in Cat.all_cats_list
            if check_cat.dead == self.dead
            and check_cat.status.alive_in_player_clan
            == self.status.alive_in_player_clan
            and not check_cat.faded
        ]

        # we're doing this separately so that we don't fuck up other clan cats and cats with no group
        if self.dead:
            sorted_specific_list = [
                check_cat
                for check_cat in sorted_specific_list
                if check_cat.status.group_ID == self.status.group_ID
            ]

        filter_near = (
            not self.dead and (self.status.is_outsider or self.status.is_other_clancat)
        ) or self.status.group == CatGroup.UNKNOWN_RESIDENCE
        if filter_near:
            sorted_specific_list = [
                check_cat
                for check_cat in sorted_specific_list
                if check_cat is self
                or check_cat.status.is_near(CatGroup.PLAYER_CLAN_ID)
            ]

        if filter_func is not None:
            sorted_specific_list = [
                check_cat
                for check_cat in sorted_specific_list
                if filter_func(check_cat)
            ]

        if game.clan.instructor in sorted_specific_list:
            sorted_specific_list.remove(game.clan.instructor)
            sorted_specific_list.insert(0, game.clan.instructor)

        idx = sorted_specific_list.index(self)

        return (
            (
                sorted_specific_list[idx + 1].ID
                if len(sorted_specific_list) > idx + 1
                else 0
            ),
            sorted_specific_list[idx - 1].ID if idx - 1 >= 0 else 0,
        )


# ---------------------------------------------------------------------------- #
#                               END OF CAT CLASS                               #
# ---------------------------------------------------------------------------- #

# CAT CLASS ITEMS
cat_class = Cat
game.cat_class = Cat

# ---------------------------------------------------------------------------- #
#                                load json files                               #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

with open(f"{resource_directory}injuries.json", "r", encoding="utf-8") as read_file:
    INJURIES = ujson.loads(read_file.read())

with open(
    f"{resource_directory}permanent_conditions.json", "r", encoding="utf-8"
) as read_file:
    PERMANENT = ujson.loads(read_file.read())


LEAD_CEREMONY_SC: Optional[Dict] = None
LEAD_CEREMONY_DF: Optional[Dict] = None
lead_ceremony_lang = None


def load_leader_ceremonies():
    global LEAD_CEREMONY_SC, LEAD_CEREMONY_DF, lead_ceremony_lang
    if lead_ceremony_lang == i18n.config.get("locale"):
        return
    LEAD_CEREMONY_SC = load_lang_resource("events/lead_ceremony_sc.json")
    LEAD_CEREMONY_DF = load_lang_resource("events/lead_ceremony_df.json")
    lead_ceremony_lang = i18n.config.get("locale")


load_leader_ceremonies()

with open("resources/dicts/backstories.json", "r", encoding="utf-8") as read_file:
    BACKSTORIES = ujson.loads(read_file.read())
