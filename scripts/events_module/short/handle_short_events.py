from random import choice, choices, randrange, sample, randint
from typing import List

import i18n

from scripts.clan_resources.herb.herb import HERBS
from scripts.events_module.future.future_event import prep_event
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan_package.settings import get_clan_setting
from scripts.clan_resources.freshkill import (
    FreshkillPile,
    FRESHKILL_EVENT_ACTIVE,
    FRESHKILL_EVENT_TRIGGER_FACTOR,
)
from scripts.event_class import Single_Event
from scripts.events_module.generate_events import GenerateEvents
from scripts.events_module.relationship.relation_events import Relation_Events
from scripts.game_structure import localization, constants
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.game_essentials import game
from scripts.utility import (
    event_text_adjust,
    change_clan_relations,
    change_relationship_values,
    history_text_adjust,
    get_warring_clan,
    unpack_rel_block,
    change_clan_reputation,
    create_new_cat_block,
    get_leader_life_notice,
    find_alive_cats_with_rank,
    adjust_list_text,
)


class HandleShortEvents:
    """Handles generating and executing ShortEvents"""

    supply_types = ["fresh_kill", "all_herb", "any_herb"]
    supply_types.extend(HERBS)
    supply_triggers = ["always", "low", "adequate", "full", "excess"]
    supply_adjustments = [
        "reduce_eighth",
        "reduce_quarter",
        "reduce_half",
        "reduce_full",
        "increase_#",
    ]

    def __init__(self):
        self.future_event_failed = None
        self.current_lives = None
        self.herb_notice = None
        self.types = []
        self.sub_types = []
        self.text = None

        # cats
        self.involved_cats = []
        self.main_cat = None
        self.random_cat = None
        self.new_cat_objects = []
        self.new_cats: List[List[Cat]] = []
        self.victim_cat = None
        self.murder_index = None
        self.multi_cat: List = []
        self.dead_cats = []
        self.chosen_herb = None

        self.other_clan = None
        self.other_clan_name = None

        self.chosen_event = None
        self.additional_event_text = ""
        self.allowed_events = None
        self.excluded_events = None
        self.future_event = None

    def handle_event(
        self,
        event_type: str,
        main_cat: Cat,
        freshkill_pile: FreshkillPile,
        random_cat: Cat = None,
        victim_cat: Cat = None,
        sub_type: list = None,
        ignore_subtyping: bool = False,
    ):
        """
        This function handles the generation and execution of the event
        """

        # ---------------------------------------------------------------------------- #
        #                                gather info                                   #
        # ---------------------------------------------------------------------------- #

        self.reset()

        self.types.append(event_type)
        if sub_type:
            self.sub_types.extend(sub_type)

        if not main_cat.status.alive_in_player_clan or (
            random_cat and not random_cat.status.alive_in_player_clan
        ):
            self.future_event_failed = True
            return
        self.main_cat = main_cat
        self.random_cat = random_cat
        self.victim_cat = victim_cat

        # random cat gets added to involved later on, only if the event chosen requires a random cat
        self.involved_cats = [self.main_cat.ID]

        # check for war and assign self.other_clan accordingly
        war_chance = 5
        # if the war didn't go badly, then we decrease the chance of this event being war-focused
        if switch_get_value(Switch.war_rel_change_type) != "rel_down":
            war_chance = 2
        if game.clan.war.get("at_war", False) and randint(1, war_chance) != 1:
            enemy_clan = get_warring_clan()
            self.other_clan = enemy_clan
            self.other_clan_name = f"{self.other_clan.name}Clan"
            self.sub_types.append("war")
        else:
            self.other_clan = choice(
                game.clan.all_clans if game.clan.all_clans else None
            )
            self.other_clan_name = f"{self.other_clan.name}Clan"

        # NOW find the possible events and filter
        if event_type == "birth_death":
            event_type = "death"
        elif event_type == "health":
            event_type = "injury"

        # choosing frequency
        # think of it as "in a span of 10 moons, in how many moons should this sort of event appear?"
        frequency_roll = randint(1, 10)
        if frequency_roll <= 4:
            frequency = 4
        elif frequency_roll <= 7:
            frequency = 3
        elif frequency_roll <= 9:
            frequency = 2
        else:
            frequency = 1

        chosen_event = None
        while not chosen_event and frequency < 5:
            possible_short_events = GenerateEvents.possible_short_events(
                frequency,
                event_type,
            )

            chosen_event, random_cat = GenerateEvents.filter_possible_short_events(
                Cat_class=Cat,
                possible_events=possible_short_events,
                cat=self.main_cat,
                random_cat=self.random_cat,
                other_clan=self.other_clan,
                freshkill_active=FRESHKILL_EVENT_ACTIVE,
                freshkill_trigger_factor=FRESHKILL_EVENT_TRIGGER_FACTOR,
                sub_types=self.sub_types,
                allowed_events=self.allowed_events,
                excluded_events=self.excluded_events,
                ignore_subtyping=ignore_subtyping,
            )
            if not chosen_event:
                # we'll see if any more common events are available
                frequency += 1

        # ---------------------------------------------------------------------------- #
        #                               do the event                                   #
        # ---------------------------------------------------------------------------- #
        if chosen_event:
            self.chosen_event = chosen_event
            self.random_cat = random_cat
            self.future_event_failed = False
        else:
            # this doesn't necessarily mean there's a problem, but can be helpful for narrowing down possibilities
            print(
                f"WARNING: no {event_type}: {self.sub_types} events found for {self.main_cat.name}"
            )
            return

        self.text = self.chosen_event.text

        self.additional_event_text = ""

        # check if another cat is present
        if self.random_cat:
            self.involved_cats.append(self.random_cat.ID)

        # checking if a mass death should happen, happens here so that we can toss the event if needed
        if "mass_death" in self.chosen_event.sub_type:
            if not get_clan_setting("disasters"):
                return
            self.handle_mass_death()
            if len(self.multi_cat) <= 2:
                return

        # create new cats (must happen here so that new cats can be included in further changes)
        self.handle_new_cats()

        # remove cats from involved_cats if they're supposed to be
        if self.random_cat and "r_c" in self.chosen_event.exclude_involved:
            self.involved_cats.remove(self.random_cat.ID)
        if "m_c" in self.chosen_event.exclude_involved:
            self.involved_cats.remove(self.main_cat.ID)

        for n_c in self.new_cats:
            nc_index = self.new_cats.index(n_c)
            n_c_string = f"n_c:{nc_index}"
            if n_c_string in self.chosen_event.exclude_involved:
                if n_c[0].ID in self.involved_cats:
                    self.involved_cats.remove(str(n_c[0].ID))

        # give accessory
        if self.chosen_event.new_accessory:
            if self.handle_accessories() is False:
                return

        # change relationships before killing anyone
        if self.chosen_event.relationships:
            # we're doing this here to make sure rel logs get adjusted text
            self.text = event_text_adjust(
                Cat,
                self.chosen_event.text,
                main_cat=self.main_cat,
                random_cat=self.random_cat,
                victim_cat=self.victim_cat,
                new_cats=self.new_cat_objects,
                clan=game.clan,
                other_clan=self.other_clan,
            )
            unpack_rel_block(Cat, self.chosen_event.relationships, self)

        # used in some murder events,
        # this kind of sucks tho it would be nice to change how this sort of thing is handled
        if "kit_manipulated" in self.chosen_event.tags:
            kit = Cat.fetch_cat(
                choice(find_alive_cats_with_rank(Cat, [CatRank.KITTEN]))
            )
            self.involved_cats.append(kit.ID)
            change_relationship_values(
                [self.random_cat],
                [kit],
                platonic_like=-20,
                dislike=40,
                admiration=-30,
                comfortable=-30,
                jealousy=0,
                trust=-30,
            )

        # update gender
        if self.chosen_event.new_gender:
            self.handle_transition()

        # kill cats
        self.handle_death()

        # add necessary histories
        self.handle_death_history()

        # handle injuries and injury history
        self.handle_injury()

        # handle murder reveals
        if "murder_reveal" in self.chosen_event.sub_type:
            self.main_cat.history.reveal_murder(
                victim=self.victim_cat,
                murderer_id=self.main_cat.ID,
                clan_reveal="clan_wide" in self.chosen_event.tags,
                aware_individuals=[self.random_cat.ID],
            )

        # change outsider rep
        if self.chosen_event.outsider:
            change_clan_reputation(self.chosen_event.outsider["changed"])
            if "misc" not in self.types:
                self.types.append("misc")

        # change other_clan rep
        if self.chosen_event.other_clan:
            change_clan_relations(
                self.other_clan, self.chosen_event.other_clan["changed"]
            )
            if "other_clans" not in self.types:
                self.types.append("other_clans")

        # change supplies
        if self.chosen_event.supplies:
            for block in self.chosen_event.supplies:
                if "misc" not in self.types:
                    self.types.append("misc")
                if block["type"] == "freshkill":
                    self.handle_freshkill_supply(block, freshkill_pile)
                else:  # if freshkill isn't being adjusted, then it must be a herb supply
                    self.handle_herb_supply(block)

        if "clan_wide" in self.chosen_event.tags:
            self.involved_cats.clear()

        # adjust text again to account for info that wasn't available when we do rel changes
        self.text = event_text_adjust(
            Cat,
            self.chosen_event.text,
            main_cat=self.main_cat,
            random_cat=self.random_cat,
            victim_cat=self.victim_cat,
            new_cats=self.new_cats,
            multi_cats=self.multi_cat,
            clan=game.clan,
            other_clan=self.other_clan,
            chosen_herb=self.chosen_herb,
        )

        if self.chosen_herb:
            game.herb_events_list.append(f"{self.text} {self.herb_notice}")

        self.gather_future_event()

        game.cur_events_list.append(
            Single_Event(
                self.text + " " + self.additional_event_text,
                self.types,
                self.involved_cats,
            )
        )

    def gather_future_event(self):
        """
        Handles gathering information for future event
        """
        if not self.chosen_event.future_event:
            return

        possible_cats = {
            "m_c": self.main_cat,
            "r_c": self.random_cat,
            "mur_c": self.victim_cat,
        }

        for x, newbie in enumerate(self.new_cats):
            possible_cats[f"n_c:{x}"] = newbie

        prep_event(
            event=self.chosen_event,
            event_id=self.chosen_event.event_id,
            possible_cats=possible_cats,
        )

    def trigger_future_event(self, event):
        self.allowed_events = event.pool.get("event_id")
        self.excluded_events = event.pool.get("excluded_event_id")

        self.future_event_failed = True
        self.handle_event(
            event_type=event.event_type,
            main_cat=Cat.fetch_cat(event.involved_cats.get("m_c")),
            random_cat=Cat.fetch_cat(event.involved_cats.get("r_c")),
            freshkill_pile=game.clan.freshkill_pile,
            victim_cat=Cat.fetch_cat(event.involved_cats.get("mur_c")),
            sub_type=event.pool.get("subtype"),
            ignore_subtyping="subtype" not in event.pool,
        )

        self.allowed_events = []
        self.excluded_events = []

        if self.future_event_failed:
            self.future_event_failed = False
            return True
        return False

    def handle_new_cats(self):
        """
        handles adding new cats to the clan
        """

        if not self.chosen_event.new_cat:
            return

        if "misc" not in self.types:
            self.types.append("misc")

        extra_text = None

        in_event_cats = {"m_c": self.main_cat}

        if self.random_cat:
            in_event_cats["r_c"] = self.random_cat
        for i, attribute_list in enumerate(self.chosen_event.new_cat):
            self.new_cats.append(
                create_new_cat_block(
                    Cat, Relationship, self, in_event_cats, i, attribute_list
                )
            )

            # check if we want to add some extra info to the event text and if we need to welcome
            for cat in self.new_cats[-1]:
                if cat.dead:
                    extra_text = event_text_adjust(
                        Cat, i18n.t("defaults.event_dead_outsider"), main_cat=cat
                    )
                elif cat.status.is_outsider:
                    n_c_index = self.new_cats.index([cat])
                    if (
                        f"n_c:{n_c_index}" in self.chosen_event.exclude_involved
                        or "unknown" in attribute_list
                    ):
                        extra_text = ""
                    else:
                        extra_text = event_text_adjust(
                            Cat, i18n.t("defaults.event_met_outsider"), main_cat=cat
                        )
                else:
                    Relation_Events.welcome_new_cats([cat])
                self.involved_cats.append(cat.ID)
                self.new_cat_objects.append([cat])

        # Check to see if any young litters joined with alive parents.
        # If so, see if recovering from birth condition is needed and give the condition
        for sub in self.new_cats:
            if sub[0].moons < 3:
                # Search for parent
                for sub_sub in self.new_cats:
                    if (
                        sub_sub[0] != sub[0]
                        and (
                            sub_sub[0].gender == "female"
                            or get_clan_setting("same sex birth")
                        )
                        and sub_sub[0].ID in (sub[0].parent1, sub[0].parent2)
                        and sub_sub[0].status.alive_in_player_clan
                    ):
                        sub_sub[0].get_injured("recovering from birth")
                        break  # Break - only one parent ever gives birth

        if extra_text and extra_text not in self.chosen_event.text:
            self.chosen_event.text = self.chosen_event.text + " " + extra_text

    def handle_accessories(self, pelts=Pelt):
        """
        handles giving accessories to the main_cat
        """
        if "misc" not in self.types:
            self.types.append("misc")
        acc_list = []
        possible_accs = getattr(self.chosen_event, "new_accessory", [])
        if "WILD" in possible_accs:
            acc_list.extend(pelts.wild_accessories)
        if "PLANT" in possible_accs:
            acc_list.extend(pelts.plant_accessories)
        if "COLLAR" in possible_accs:
            acc_list.extend(pelts.collars)

        for acc in possible_accs:
            if acc not in ("WILD", "PLANT", "COLLAR"):
                acc_list.append(acc)

        if hasattr(self.main_cat.pelt, "scars"):
            if (
                "NOTAIL" in self.main_cat.pelt.scars
                or "HALFTAIL" in self.main_cat.pelt.scars
            ):
                for acc in pelts.tail_accessories:
                    if acc in acc_list:
                        acc_list.remove(acc)

        accessory_groups = [
            pelts.collars,
            pelts.head_accessories,
            pelts.tail_accessories,
            pelts.body_accessories,
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
        else:
            self.main_cat.pelt.accessory = [choice(acc_list)]

    def handle_transition(self):
        """
        handles updating gender_align and pronouns
        """
        possible_genders = getattr(self.chosen_event, "new_gender", [])

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
        dead_list = self.dead_cats if self.dead_cats else []
        self.current_lives = int(game.clan.leader_lives)

        # check if the bodies are retrievable
        if "no_body" in self.chosen_event.tags:
            body = False
        else:
            body = True
        pass

        if self.chosen_event.m_c["dies"] and self.main_cat not in dead_list:
            dead_list.append(self.main_cat)
        if self.chosen_event.r_c:
            if self.chosen_event.r_c["dies"] and self.random_cat not in dead_list:
                dead_list.append(self.random_cat)

        if not dead_list:
            return

        # kill cats
        for cat in dead_list:
            if "birth_death" not in self.types:
                self.types.append("birth_death")

            if cat.status.is_leader:
                if "all_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= 10
                elif "some_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= randrange(2, self.current_lives - 1)
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
        requirements = self.chosen_event.m_c
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
            if max_deaths > 10:  # make this into a constants.CONFIG setting?
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

            self.dead_cats = sample(alive_cats, dead_count)
            if self.main_cat not in self.dead_cats:
                self.dead_cats.append(
                    self.main_cat
                )  # got to include the cat that rolled for death in the first place

            taken_cats = []
            for kitty in self.dead_cats:
                if "lost" in self.chosen_event.tags:
                    kitty.become_lost()
                    taken_cats.append(kitty)
                self.multi_cat.append(kitty)
                if kitty.ID not in self.involved_cats:
                    self.involved_cats.append(kitty.ID)
            for kitty in taken_cats:
                self.dead_cats.remove(kitty)

        else:
            return

    def handle_death_history(self):
        """
        handles assigning histories
        """
        for block in self.chosen_event.history:
            # main_cat's history
            if "m_c" in block["cats"]:
                # death history
                if self.chosen_event.m_c["dies"]:
                    # handle murder
                    if "murder" in self.chosen_event.sub_type:
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
                        self.current_lives -= 1
                        if self.current_lives != game.clan.leader_lives:
                            while self.current_lives > game.clan.leader_lives:
                                self.main_cat.history.add_death(
                                    "multi_lives",
                                    other_cat=self.random_cat,
                                )
                                self.current_lives -= 1
                    self.main_cat.history.add_death(
                        death_history, other_cat=self.random_cat
                    )

            # random_cat history
            if "r_c" in block["cats"]:
                # death history
                if self.chosen_event.r_c["dies"]:
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
                        self.current_lives -= 1
                        if self.current_lives != game.clan.leader_lives:
                            while self.current_lives > game.clan.leader_lives:
                                self.random_cat.history.add_death(
                                    "multi_lives",
                                    other_cat=self.random_cat,
                                )
                                self.current_lives -= 1
                    self.random_cat.history.add_death(
                        death_history, other_cat=self.random_cat
                    )

            # multi_cat history
            if "multi_cat" in block["cats"]:
                for cat in self.multi_cat:
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
                        self.current_lives -= 1
                        if self.current_lives != game.clan.leader_lives:
                            while self.current_lives > game.clan.leader_lives:
                                cat.history.add_death("multi_lives")
                                self.current_lives -= 1
                    cat.history.add_death(death_history)

            # new_cat history
            for abbr in block["cats"]:
                if "n_c" in abbr:
                    for i, new_cats in enumerate(self.new_cats):
                        if new_cats[i].dead:
                            death_history = history_text_adjust(
                                self.chosen_event.history_text.get("reg_death"),
                                self.other_clan_name,
                                game.clan,
                                self.random_cat,
                            )
                            new_cats[i].history.add_death(
                                death_history, other_cat=self.random_cat
                            )

    def handle_injury(self):
        """
        assigns an injury to involved cats and then assigns possible histories (if in classic, assigns scar and scar
        history)
        """

        # if no injury block, then no injury gets assigned
        if not self.chosen_event.injury:
            return

        if "health" not in self.types:
            self.types.append("health")

        # now go through each injury block
        for block in self.chosen_event.injury:
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
                    for i, new_cats in enumerate(self.new_cats):
                        injury = choice(possible_injuries)
                        new_cats[i].get_injured(injury)
                        self.handle_injury_history(new_cats[i], abbr, injury)

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
            for block in self.chosen_event.history:
                if "scar" not in block:
                    return
                elif cat_abbr in block["cats"]:
                    history_text = history_text_adjust(
                        block["scar"], self.other_clan_name, game.clan, self.random_cat
                    )
                    cat.history.add_scar(history_text)
                    break
        else:
            for block in self.chosen_event.history:
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

    def handle_freshkill_supply(self, block, freshkill_pile: FreshkillPile):
        """
        handles adjusting the amount of freshkill according to info in block
        :param block: supplies block
        :param freshkill_pile: Freshkill_Pile for clan
        """
        if game.clan.game_mode == "classic":
            return

        if "misc" not in self.types:
            self.types.append("misc")

        adjustment = block["adjust"]
        reduce_amount = 0
        increase_amount = 0

        if adjustment == "reduce_full":
            reduce_amount = int(freshkill_pile.total_amount)
        elif adjustment == "reduce_half":
            reduce_amount = int(freshkill_pile.total_amount / 2)
        elif adjustment == "reduce_quarter":
            reduce_amount = int(freshkill_pile.total_amount / 4)
        elif adjustment == "reduce_eighth":
            reduce_amount = -int(freshkill_pile.total_amount / 8)
        elif "increase" in adjustment:
            increase_amount = adjustment.split("_")[1]
            increase_amount = int(increase_amount)

        if reduce_amount != 0:
            freshkill_pile.remove_freshkill(reduce_amount, take_random=True)
        if increase_amount != 0:
            freshkill_pile.add_freshkill(increase_amount)

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

    def reset(self):
        """
        resets class attributes
        """
        self.herb_notice = None
        self.types = []
        self.sub_types = []
        self.text = None

        # cats
        self.involved_cats = []
        self.main_cat = None
        self.random_cat = None
        self.new_cat_objects = []
        self.new_cats: List[List[Cat]] = []
        self.victim_cat = None
        self.murder_index = None
        self.multi_cat: List = []
        self.dead_cats = []
        self.chosen_herb = None

        self.other_clan = None
        self.other_clan_name = None

        self.chosen_event = None
        self.additional_event_text = ""


handle_short_events = HandleShortEvents()
