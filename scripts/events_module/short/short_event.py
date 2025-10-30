from random import choice, randrange, choices, sample
from typing import List, Optional

import i18n

from scripts.cat.cats import Cat
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan_package.settings import get_clan_setting
from scripts.event_class import Single_Event
from scripts.events_module.future.prep_and_trigger import prep_future_event
from scripts.events_module.relationship.relation_events import Relation_Events
from scripts.game_structure import localization, game
from scripts.utility import (
    create_new_cat_block,
    event_text_adjust,
    get_leader_life_notice,
    history_text_adjust,
    adjust_list_text,
    unpack_rel_block,
    find_alive_cats_with_rank,
    change_relationship_values,
    change_clan_reputation,
    change_clan_relations,
)

from scripts.cat.enums import CatAge, CatRank
from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath
from scripts.game_structure import constants


class ShortEvent:
    """
    A moon event that only affects the moon it was triggered on.  Can involve two cats directly and be restricted by various constraints.
    - full documentation available on GitHub wiki
    """

    num_of_traits = len(Personality.trait_ranges["normal_traits"].keys()) + len(
        Personality.trait_ranges["kit_traits"].keys()
    )
    num_of_skills = len(SkillPath)

    num_of_ages = len(CatAge)

    num_of_ranks = CatRank.get_num_of_clan_ranks()

    def __init__(
        self,
        event_id: str = "",
        location: List[str] = None,
        season: List[str] = None,
        sub_type: List[str] = None,
        tags: List[str] = None,
        text: str = "",
        new_accessory: List[str] = None,
        m_c=None,
        r_c=None,
        new_cat: List[list] = None,
        injury: list = None,
        exclude_involved: list = None,
        history: list = None,
        relationships: list = None,
        outsider: dict = None,
        other_clan: dict = None,
        supplies: list = None,
        new_gender: List[str] = None,
        future_event: dict = None,
    ):
        if not event_id:
            print("WARNING: moon event has no event_id")

        self.weight = 1

        self.event_id = event_id
        self.location = location if location else ["any"]
        if "any" not in self.location:
            self.weight += 1
        self.season = season if season else ["any"]
        if "any" not in self.season:
            self.weight += len(constants.SEASONS) - len(
                self.season
            )  # this increases the weight inversely to the number of season constraints
        self.sub_type = sub_type if sub_type else []
        self.tags = tags if tags else []
        self.text = text
        self.text_template = text
        self.new_accessory = new_accessory if new_accessory else []
        self.m_c = m_c if m_c else {"age": ["any"]}
        if self.m_c:
            if "age" in self.m_c and "any" not in self.m_c["age"]:
                self.weight += self.num_of_ages - len(self.m_c["age"])
            else:
                self.m_c["age"] = ["any"]
            if "status" in self.m_c and "any" not in self.m_c["status"]:
                self.weight += self.num_of_ranks - len(self.m_c["status"])
            else:
                self.m_c["status"] = ["any"]
            if "relationship_status" in self.m_c:
                self.weight += len(self.m_c["relationship_status"])
            else:
                self.m_c["relationship_status"] = []
            if "skill" in self.m_c:
                self.weight += self.num_of_skills - len(self.m_c["skill"])
            else:
                self.m_c["skill"] = []
            if "not_skill" in self.m_c:
                self.weight += len(self.m_c["not_skill"])
            else:
                self.m_c["not_skill"] = []
            if "trait" in self.m_c:
                self.weight += self.num_of_traits - len(self.m_c["trait"])
            else:
                self.m_c["trait"] = []
            if "not_trait" in self.m_c:
                self.weight += len(self.m_c["not_trait"])
            else:
                self.m_c["not_trait"] = []
            if "backstory" in self.m_c:
                self.weight += 1
            else:
                self.m_c["backstory"] = []
            if "dies" not in self.m_c:
                self.m_c["dies"] = False
            if "gender" not in self.m_c:
                self.m_c["gender"] = []

        self.r_c = r_c if r_c else {}
        if self.r_c:
            if "age" in self.r_c and "any" not in self.r_c["age"]:
                self.weight += self.num_of_ages - len(self.r_c["age"])
            else:
                self.r_c["age"] = ["any"]
            if "status" in self.r_c and "any" not in self.r_c["status"]:
                self.weight += self.num_of_ranks - len(self.r_c["status"])
            else:
                self.r_c["status"] = ["any"]
            if "relationship_status" in self.r_c:
                self.weight += len(self.r_c["relationship_status"])
            else:
                self.r_c["relationship_status"] = []
            if "skill" in self.r_c:
                self.weight += self.num_of_skills - len(self.r_c["skill"])
            else:
                self.r_c["skill"] = []
            if "not_skill" in self.r_c:
                self.weight += len(self.r_c["not_skill"])
            else:
                self.r_c["not_skill"] = []
            if "trait" in self.r_c:
                self.weight += self.num_of_traits - len(self.r_c["trait"])
            else:
                self.r_c["trait"] = []
            if "not_trait" in self.r_c:
                self.weight += len(self.r_c["not_trait"])
            else:
                self.r_c["not_trait"] = []
            if "backstory" in self.r_c:
                self.weight += 1
            else:
                self.r_c["backstory"] = []
            if "dies" not in self.r_c:
                self.r_c["dies"] = False
            if "gender" not in self.r_c:
                self.r_c["gender"] = []

        self.new_cat_attributes = new_cat if new_cat else []
        self.exclude_involved = exclude_involved if exclude_involved else []
        self.injury = injury if injury else []
        self.history = history if history else []
        self.relationships = relationships if relationships else []
        self.outsider = outsider if outsider else {}
        if self.outsider:
            if "current_rep" not in self.outsider:
                self.outsider["current_rep"] = []
            if "changed" not in self.outsider:
                self.outsider["changed"] = 0
        self.other_clan = other_clan if other_clan else {}
        if self.other_clan:
            if (
                "current_rep" in self.other_clan
                and "any" not in self.other_clan["current_rep"]
            ):
                self.weight += (3 - len(self.other_clan["current_rep"])) * 5
            else:
                self.other_clan["current_rep"] = []
            if "changed" not in self.other_clan:
                self.other_clan["changed"] = 0
        self.supplies = supplies if supplies else []
        self.new_gender = new_gender
        self.future_event = future_event if future_event else {}

        self.types: list[str] = []
        self.additional_event_text: str = ""

        self.main_cat: Optional[Cat] = None
        self.random_cat: Optional[Cat] = None
        self.victim_cat: Optional[Cat] = None
        self.new_cats: list[list[Optional[Cat]]] = []
        """
        Because litters are generated as a "single" new cat, this list contains lists of cat objects. These lists will have a single object inside unless it was the result of a litter generation.
        """
        self.multi_cat_objects: list[Optional[Cat]] = []
        self.dead_cat_objects: list[Optional[Cat]] = []

        self.all_involved_cat_ids: list[int] = []

        self.leads_current_life_count: int = 0
        self.other_clan_name: str = ""
        self.chosen_herb: str = ""
        self.herb_notice: str = ""

    def execute_event(self, other_clan=None):
        """
        Handles the execution of this event.
        :param other_clan: the object for the other clan involved in this event
        """
        self.additional_event_text = ""
        self.text = self.text_template
        self.all_involved_cat_ids.clear()
        self.new_cats.clear()
        self.multi_cat_objects.clear()
        self.dead_cat_objects.clear()

        if other_clan:
            self.other_clan_name = f"{other_clan.name}Clan"

        self.all_involved_cat_ids.append(self.main_cat.ID)

        # check if another cat is present
        if self.r_c:
            self.all_involved_cat_ids.append(self.random_cat.ID)
        if self.victim_cat:
            self.all_involved_cat_ids.append(self.victim_cat.ID)

        # checking if a mass death should happen, happens here so that we can toss the event if needed
        if "mass_death" in self.sub_type:
            if game.clan and not get_clan_setting("disasters"):
                return
            self.handle_mass_death()
            if len(self.multi_cat_objects) <= 2:
                return

        # create new cats (must happen here so that new cats can be included in further changes)
        self.handle_new_cats()

        # remove cats from involved_cats if they're supposed to be
        if self.r_c and "r_c" in self.exclude_involved:
            self.all_involved_cat_ids.remove(self.random_cat.ID)
        if "m_c" in self.exclude_involved:
            self.all_involved_cat_ids.remove(self.main_cat.ID)

        for index, n_c in enumerate(self.new_cats):
            if f"n_c:{index}" in self.exclude_involved:
                self.all_involved_cat_ids.remove(n_c[0].ID)

        # give accessory
        if self.new_accessory:
            if self.handle_accessories() is False:
                return

        # change relationships before killing anyone
        if self.relationships:
            # we're doing this here to make sure rel logs get adjusted text
            self.text = event_text_adjust(
                Cat,
                self.text,
                main_cat=self.main_cat,
                random_cat=self.random_cat,
                victim_cat=self.victim_cat,
                new_cats=self.new_cats,
                clan=game.clan,
            )
            for change in self.relationships:
                for group in change.get("log", []):
                    change["log"][group] = event_text_adjust(
                        Cat,
                        group,
                        main_cat=self.main_cat,
                        random_cat=self.random_cat,
                        victim_cat=self.victim_cat,
                        new_cats=self.new_cats,
                    )

            unpack_rel_block(Cat, self.relationships, self)

        # used in some murder events,
        # this kind of sucks tho it would be nice to change how this sort of thing is handled
        if "kit_manipulated" in self.tags:
            kit = Cat.fetch_cat(
                choice(find_alive_cats_with_rank(Cat, [CatRank.KITTEN]))
            )
            self.all_involved_cat_ids.append(kit.ID)
            change_relationship_values(
                [self.random_cat],
                [kit],
                like=-20,
                respect=-30,
                comfort=-30,
                trust=-30,
            )

        # update gender
        if self.new_gender:
            self.handle_transition()

        # kill cats
        self.handle_death()

        # add necessary histories
        self.handle_death_history()

        # handle injuries and injury history
        self.handle_injury()

        # handle murder reveals
        if "murder_reveal" in self.sub_type or "hidden_murder_reveal" in self.sub_type:
            self.main_cat.history.reveal_murder(
                victim=self.victim_cat,
                murderer_id=self.main_cat.ID,
                clan_reveal="clan_wide" in self.tags,
                aware_individuals=[self.random_cat.ID],
            )

        # change outsider rep
        if self.outsider:
            change_clan_reputation(self.outsider["changed"])
            if "misc" not in self.types:
                self.types.append("misc")

        # change other_clan rep
        if self.other_clan:
            change_clan_relations(other_clan, self.other_clan["changed"])
            if "other_clans" not in self.types:
                self.types.append("other_clans")

        # change supplies
        if self.supplies:
            for block in self.supplies:
                if "misc" not in self.types:
                    self.types.append("misc")
                if block["type"] == "freshkill":
                    self.handle_freshkill_supply(block)
                else:  # if freshkill isn't being adjusted, then it must be a herb supply
                    self.handle_herb_supply(block)

        if "clan_wide" in self.tags:
            self.all_involved_cat_ids.clear()

        # adjust text again to account for info that wasn't available when we do rel changes
        self.text = event_text_adjust(
            Cat,
            self.text,
            main_cat=self.main_cat,
            random_cat=self.random_cat,
            victim_cat=self.victim_cat,
            new_cats=self.new_cats,
            multi_cats=self.multi_cat_objects,
            clan=game.clan,
            other_clan=other_clan,
            chosen_herb=self.chosen_herb,
        )

        if self.chosen_herb:
            game.herb_events_list.append(f"{self} {self.herb_notice}.")

        self.gather_future_event()

        game.cur_events_list.append(
            Single_Event(
                self.text + " " + self.additional_event_text,
                self.types,
                self.all_involved_cat_ids,
            )
        )

    def gather_future_event(self):
        """
        Handles gathering information for future event
        """
        if not self.future_event:
            return

        possible_cats = {
            "m_c": self.main_cat,
            "r_c": self.random_cat,
            "mur_c": self.victim_cat,
        }

        for x, newbie in enumerate(self.new_cats):
            possible_cats[f"n_c:{x}"] = newbie[0]

        prep_future_event(
            event=self,
            event_id=self.event_id,
            possible_cats=possible_cats,
        )

    def handle_new_cats(self):
        """
        handles adding new cats to the clan
        """

        if not self.new_cat_attributes:
            return

        if "misc" not in self.types:
            self.types.append("misc")

        extra_text = None

        in_event_cats = {"m_c": self.main_cat}

        if self.random_cat:
            in_event_cats["r_c"] = self.random_cat
        for i, attribute_list in enumerate(self.new_cat_attributes):
            self.new_cats.append(
                create_new_cat_block(
                    Cat, Relationship, self, in_event_cats, i, attribute_list
                )
            )

            # check if we want to add some extra info to the event text and if we need to welcome
            for _c in self.new_cats:
                if not isinstance(_c, list):
                    continue
                first_cat = _c[0]
                if first_cat.dead:
                    extra_text = event_text_adjust(
                        Cat,
                        i18n.t("defaults.event_dead_outsider"),
                        main_cat=first_cat,
                    )
                elif first_cat.status.is_outsider:
                    n_c_index = self.new_cats.index(_c)
                    if (
                        f"n_c:{n_c_index}" in self.exclude_involved
                        or "unknown" in attribute_list
                    ):
                        extra_text = ""
                    else:
                        extra_text = event_text_adjust(
                            Cat,
                            i18n.t("defaults.event_met_outsider"),
                            main_cat=first_cat,
                        )
                else:
                    Relation_Events.welcome_new_cats([first_cat])
                self.all_involved_cat_ids.extend([cat.ID for cat in _c])

        # Check to see if any young litters joined with alive parents.
        # If so, see if recovering from birth condition is needed and give the condition
        for possible_kittens in self.new_cats:
            first_kit = possible_kittens[0]
            if first_kit.moons < 3:
                # search for parent
                for possible_parent in self.new_cats:
                    first_cat = possible_parent[0]
                    if first_cat == first_kit:
                        continue
                    if not first_cat.gender == "female" and not get_clan_setting(
                        "same sex birth"
                    ):
                        continue
                    if (
                        first_cat in (first_kit.parent1, first_kit.parent2)
                        and not first_cat.dead
                        and not "recovering from birth" in first_cat.injuries
                    ):
                        first_cat.get_injured("recovering from birth")
                        # only one parent gives birth, so we break
                        break

        if extra_text and extra_text not in self.text:
            self.text = self.text + " " + extra_text

    def handle_accessories(self):
        """
        handles giving accessories to the main_cat
        """
        if "misc" not in self.types:
            self.types.append("misc")
        acc_list = []
        possible_accs = getattr(self, "new_accessory", [])
        if "WILD" in possible_accs:
            acc_list.extend(Pelt.wild_accessories)
        if "PLANT" in possible_accs:
            acc_list.extend(Pelt.plant_accessories)
        if "COLLAR" in possible_accs:
            acc_list.extend(Pelt.collar_accessories)

        for acc in possible_accs:
            if acc not in ("WILD", "PLANT", "COLLAR"):
                acc_list.append(acc)

        if hasattr(self.main_cat.pelt, "scars"):
            if (
                "NOTAIL" in self.main_cat.pelt.scars
                or "HALFTAIL" in self.main_cat.pelt.scars
            ):
                for acc in Pelt.tail_accessories:
                    if acc in acc_list:
                        acc_list.remove(acc)

        accessory_groups = [
            Pelt.collar_accessories,
            Pelt.head_accessories,
            Pelt.tail_accessories,
            Pelt.body_accessories,
        ]
        if self.main_cat.pelt.accessory:
            for acc in self.main_cat.pelt.accessory:
                # find which accessory group it belongs to
                for i, lst in enumerate(accessory_groups):
                    if acc in lst:
                        # remove that group from possible accessories
                        acc_list = [a for a in acc_list if a not in accessory_groups[i]]
                        break

        if not acc_list:
            return False

        if self.main_cat.pelt.accessory:
            self.main_cat.pelt.accessory.append(choice(acc_list))
            return None
        else:
            self.main_cat.pelt.accessory = [choice(acc_list)]
            return None

    def handle_transition(self):
        """
        handles updating gender_align and pronouns
        """
        possible_genders = getattr(self, "new_gender", [])

        if possible_genders:
            new_gender = choice(possible_genders)
            self.main_cat.genderalign = new_gender

            self.main_cat.pronouns = localization.get_new_pronouns(
                self.main_cat.genderalign
            )

    def handle_death(self):
        """
        handles killing/murdering cats
        """
        if not game.clan:
            # test catch
            return

        dead_list = self.dead_cat_objects if self.dead_cat_objects else []
        self.leads_current_life_count = int(game.clan.leader_lives)

        # check if the bodies are retrievable
        if "no_body" in self.tags:
            body = False
        else:
            body = True
        pass

        if self.m_c["dies"] and self.main_cat not in dead_list:
            dead_list.append(self.main_cat)
        if self.r_c:
            if self.r_c["dies"] and self.random_cat not in dead_list:
                dead_list.append(self.random_cat)

        if not dead_list:
            return

        # kill cats
        for cat in dead_list:
            if "birth_death" not in self.types:
                self.types.append("birth_death")

            if cat.status.is_leader:
                if "all_lives" in self.tags:
                    game.clan.leader_lives -= 10
                elif "some_lives" in self.tags:
                    game.clan.leader_lives -= randrange(
                        2, self.leads_current_life_count - 1
                    )
                else:
                    game.clan.leader_lives -= 1

                cat.die(body)
                self.additional_event_text = get_leader_life_notice()

            else:
                cat.die(body)

    def handle_mass_death(self):
        """
        finds cats eligible for the death, if not enough cats are eligible then event is tossed.
        cats that will die are added to self.dead_cats
        """
        # gather living clan cats except leader bc leader lives would be frustrating to handle in these
        alive_cats = [i for i in Cat.all_cats.values() if i.status.alive_in_player_clan]

        # make sure all cats in the pool fit the event requirements
        requirements = self.m_c
        for kitty in alive_cats:
            if (
                kitty.status.rank not in requirements["status"]
                and "any" not in requirements["status"]
            ):
                alive_cats.remove(kitty)
                continue
            if (
                kitty.age not in requirements["age"]
                and "any" not in requirements["age"]
            ):
                alive_cats.remove(kitty)
        alive_count = len(alive_cats)

        # if there's enough eligible cats, then we KILL
        if alive_count > 15:
            max_deaths = int(alive_count / 2)  # 1/2 of alive cats
            if max_deaths > 10:  # make this into a game config setting?
                max_deaths = 10  # we don't want to have massive events with a wall of names to read
            weights = []
            population = []
            for n in range(2, max_deaths):
                population.append(n)
                weight = 1 / (0.75 * n)  # Lower chance for more dead cats
                weights.append(weight)
            dead_count = choices(population, weights=weights)[0]
            if dead_count < 2:
                dead_count = 2

            self.dead_cat_objects = sample(alive_cats, dead_count)
            if self.main_cat not in self.dead_cat_objects:
                self.dead_cat_objects.append(
                    self.main_cat
                )  # got to include the cat that rolled for death in the first place

            taken_cats = []
            for kitty in self.dead_cat_objects:
                if "lost" in self.tags:
                    kitty.become_lost()
                    taken_cats.append(kitty)
                self.multi_cat_objects.append(kitty)
                if kitty.ID not in self.all_involved_cat_ids:
                    self.all_involved_cat_ids.append(kitty.ID)
            for kitty in taken_cats:
                self.dead_cat_objects.remove(kitty)

        else:
            return

    def handle_death_history(self):
        """
        handles assigning histories
        """
        for block in self.history:
            # main_cat's history
            if "m_c" in block["cats"]:
                # death history
                if self.m_c["dies"]:
                    # handle murder
                    if "murder" in self.sub_type:
                        self.random_cat.history.add_murder(
                            murderer_id=self.random_cat.ID, victim=self.main_cat
                        )

                    # find history
                    if self.main_cat.status.is_leader:
                        death_history = history_text_adjust(
                            block.get("lead_death"),
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )
                    else:
                        death_history = history_text_adjust(
                            block.get("reg_death"),
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )

                    if self.main_cat.status.is_leader:
                        self.leads_current_life_count -= 1
                        if self.leads_current_life_count != game.clan.leader_lives:
                            while (
                                self.leads_current_life_count > game.clan.leader_lives
                            ):
                                self.main_cat.history.add_death(
                                    "multi_lives",
                                    other_cat=self.random_cat,
                                )
                                self.leads_current_life_count -= 1
                    self.main_cat.history.add_death(
                        death_history, other_cat=self.random_cat
                    )

            # random_cat history
            if "r_c" in block["cats"]:
                # death history
                if self.r_c["dies"]:
                    if self.random_cat.status.is_leader:
                        death_history = history_text_adjust(
                            block.get("lead_death"),
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )
                    else:
                        death_history = history_text_adjust(
                            block.get("reg_death"),
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )

                    if self.random_cat.status.is_leader:
                        self.leads_current_life_count -= 1
                        if self.leads_current_life_count != game.clan.leader_lives:
                            while (
                                self.leads_current_life_count > game.clan.leader_lives
                            ):
                                self.random_cat.history.add_death(
                                    "multi_lives",
                                    other_cat=self.random_cat,
                                )
                                self.leads_current_life_count -= 1
                    self.random_cat.history.add_death(
                        death_history, other_cat=self.random_cat
                    )

            # multi_cat history
            if "multi_cat" in block["cats"]:
                for cat in self.multi_cat_objects:
                    if cat.status.is_leader:
                        death_history = history_text_adjust(
                            block.get("lead_death"),
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )
                    else:
                        death_history = history_text_adjust(
                            block.get("reg_death"),
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )

                    if cat.status.is_leader:
                        self.leads_current_life_count -= 1
                        if self.leads_current_life_count != game.clan.leader_lives:
                            while (
                                self.leads_current_life_count > game.clan.leader_lives
                            ):
                                cat.history.add_death("multi_lives")
                                self.leads_current_life_count -= 1
                    cat.history.add_death(death_history)

            # new_cat history
            for abbr in block["cats"]:
                if "n_c" in abbr:
                    for i, new_cat_objects in enumerate(self.new_cats):
                        if new_cat_objects[i].dead:
                            death_history = history_text_adjust(
                                block.get("reg_death"),
                                self.other_clan_name,
                                game.clan,
                                self.random_cat,
                            )
                            new_cat_objects[i].history.add_death(
                                death_history, other_cat=self.random_cat
                            )

    def handle_injury(self):
        """
        assigns an injury to involved cats and then assigns possible histories (if in classic, assigns scar and scar
        history)
        """

        # if no injury block, then no injury gets assigned
        if not self.injury:
            return

        if "health" not in self.types:
            self.types.append("health")

        # now go through each injury block
        for block in self.injury:
            cats_affected = block["cats"]

            # find all possible injuries
            possible_injuries = []
            for injury in block["injuries"]:
                if injury in constants.INJURY_GROUPS:
                    possible_injuries.extend(constants.INJURY_GROUPS[injury])
                else:
                    possible_injuries.append(injury)

            # give the injury
            for abbr in cats_affected:
                # MAIN CAT
                if abbr == "m_c":
                    injury = choice(possible_injuries)
                    self.main_cat.get_injured(injury)
                    self.handle_injury_history(self.main_cat, "m_c", injury)

                # RANDOM CAT
                elif abbr == "r_c":
                    injury = choice(possible_injuries)
                    self.random_cat.get_injured(injury)
                    self.handle_injury_history(self.random_cat, "r_c", injury)

                # NEW CATS
                elif "n_c" in abbr:
                    for i, new_cat_objects in enumerate(self.new_cats):
                        injury = choice(possible_injuries)
                        new_cat_objects[i].get_injured(injury)
                        self.handle_injury_history(new_cat_objects[i], abbr, injury)

    def handle_injury_history(self, cat, cat_abbr, injury=None):
        """
        handle injury histories
        :param cat: the cat object for cat being injured
        :param cat_abbr: the abbreviation used for this cat within the event format (i.e. m_c, r_c, ect)
        :param injury: the injury being given, if in classic then leave this as the default None
        """
        # TODO: problematic as we currently cannot mark who is the r_c and who is the m_c
        #  should consider if we can have history text be converted to use the cat's ID number in place of abbrs

        # if injury is false then this is classic, and they just need scar history

        if not injury:
            for block in self.history:
                if "scar" not in block:
                    return
                elif cat_abbr in block["cats"]:
                    history_text = history_text_adjust(
                        block["scar"], self.other_clan_name, game.clan, self.random_cat
                    )
                    cat.history.add_scar(history_text)
                    break
        else:
            for block in self.history:
                if "scar" not in block:
                    return
                elif cat_abbr in block["cats"]:
                    possible_scar = history_text_adjust(
                        block["scar"], self.other_clan_name, game.clan, self.random_cat
                    )
                    if cat.status.is_leader:
                        possible_death = history_text_adjust(
                            block["lead_death"],
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )
                    else:
                        possible_death = history_text_adjust(
                            block["reg_death"],
                            self.other_clan_name,
                            game.clan,
                            self.random_cat,
                        )
                    if possible_scar or possible_death:
                        cat.history.add_possible_history(
                            injury,
                            scar_text=possible_scar,
                            death_text=possible_death,
                            other_cat=self.random_cat,
                        )

    def handle_freshkill_supply(self, block):
        """
        handles adjusting the amount of freshkill according to info in block
        :param block: supplies block
        """
        if game.clan.game_mode == "classic":
            return

        if "misc" not in self.types:
            self.types.append("misc")

        total_amount = game.clan.freshkill_pile.total_amount
        adjustment = block["adjust"]
        reduce_amount = 0
        increase_amount = 0

        if adjustment == "reduce_full":
            reduce_amount = int(total_amount)
        elif adjustment == "reduce_half":
            reduce_amount = int(total_amount / 2)
        elif adjustment == "reduce_quarter":
            reduce_amount = int(total_amount / 4)
        elif adjustment == "reduce_eighth":
            reduce_amount = -int(total_amount / 8)
        elif "increase" in adjustment:
            increase_amount = adjustment.split("_")[1]
            increase_amount = int(increase_amount)

        if reduce_amount != 0:
            game.clan.freshkill_pile.remove_freshkill(reduce_amount, take_random=True)
        if increase_amount != 0:
            game.clan.freshkill_pile.add_freshkill(increase_amount)

    def handle_herb_supply(self, block):
        """
        handles adjusting herb supply according to info in event block
        :param block: supplies block
        """

        herb_supply = game.clan.herb_supply

        adjustment = block["adjust"]
        supply_type = block["type"]
        trigger = block["trigger"]

        herb_list = []

        # adjust entire herb store
        if supply_type == "all_herb":
            for herb, count in herb_supply.entire_supply.items():
                herb_list.append(herb)
                if adjustment == "reduce_full":
                    herb_supply.remove_herb(herb, count)
                elif adjustment == "reduce_half":
                    herb_supply.remove_herb(herb, count / 2)
                elif adjustment == "reduce_quarter":
                    herb_supply.remove_herb(herb, count / 4)
                elif adjustment == "reduce_eighth":
                    herb_supply.remove_herb(herb, count / 8)
                elif "increase" in adjustment:
                    herb_supply.add_herb(herb, adjustment.split("_")[1])

        # if we weren't adjusted the whole herb store, then adjust an individual
        else:
            # picking a random herb to adjust
            if supply_type == "any_herb":
                possible_herbs = []
                for herb in herb_supply.entire_supply:
                    if "always" in trigger:
                        possible_herbs.append(herb)

                    rating = herb_supply.get_herb_rating(herb)
                    if rating in trigger:
                        possible_herbs.append(herb)

                self.chosen_herb = choice(possible_herbs)

            # if it wasn't a random herb or all herbs, then it's one specific herb
            else:
                self.chosen_herb = supply_type

            herb_list.append(self.chosen_herb)

            # now adjust the supply for the chosen_herb
            total_herb = herb_supply.total_of_herb(self.chosen_herb)
            if adjustment == "reduce_full":
                herb_supply.remove_herb(self.chosen_herb, total_herb)
            elif adjustment == "reduce_half":
                herb_supply.remove_herb(self.chosen_herb, total_herb / 2)
            elif adjustment == "reduce_quarter":
                herb_supply.remove_herb(self.chosen_herb, total_herb / 4)
            elif adjustment == "reduce_eighth":
                herb_supply.remove_herb(self.chosen_herb, total_herb / 8)
            elif "increase" in adjustment:
                herb_supply.add_herb(self.chosen_herb, int(adjustment.split("_")[1]))

        if "reduce" in adjustment:
            self.herb_notice = i18n.t(
                "screens.med_den.loss_event", herbs=adjust_list_text(herb_list)
            )
        elif "increase" in adjustment:
            self.herb_notice = i18n.t(
                "screens.med_den.gain_event", herbs=adjust_list_text(herb_list)
            )

    def __repr__(self):
        return f"{self.event_id} ({self.sub_type})"
