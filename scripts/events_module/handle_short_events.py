import random
from typing import List

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan_resources.freshkill import (
    FreshkillPile,
    FRESHKILL_EVENT_ACTIVE,
    FRESHKILL_EVENT_TRIGGER_FACTOR,
)
from scripts.event_class import Single_Event
from scripts.events_module.generate_events import GenerateEvents
from scripts.events_module.relation_events import Relation_Events
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
    get_alive_status_cats,
    get_living_clan_cat_count,
    adjust_list_text,
)


# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #


class HandleShortEvents:
    """Handles generating and executing ShortEvents"""

    def __init__(self):
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

    def handle_event(
        self,
        event_type: str,
        main_cat: Cat,
        random_cat: Cat,
        freshkill_pile: FreshkillPile,
        sub_type: list = None,
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

        self.main_cat = main_cat
        self.random_cat = random_cat

        # random cat gets added to involved later on, only if the event chosen requires a random cat
        self.involved_cats = [self.main_cat.ID]

        # check for war and assign self.other_clan accordingly
        if game.clan.war.get("at_war", False):
            enemy_clan = get_warring_clan()
            self.other_clan = enemy_clan
            self.other_clan_name = f"{self.other_clan.name}Clan"
            self.sub_types.append("war")
        else:
            self.other_clan = random.choice(
                game.clan.all_clans if game.clan.all_clans else None
            )
            self.other_clan_name = f"{self.other_clan.name}Clan"

        # checking if a murder reveal should happen
        if event_type == "misc":
            self.victim_cat = None
            cat_history = History.get_murders(self.main_cat)
            if cat_history:
                if "is_murderer" in cat_history:
                    murder_history = cat_history["is_murderer"]
                    for murder in murder_history:
                        self.murder_index = murder_history.index(murder)
                        if murder_history[self.murder_index]["revealed"] is True:
                            continue
                        self.victim_cat = Cat.fetch_cat(
                            murder_history[self.murder_index]["victim"]
                        )
                        self.sub_types.append("murder_reveal")
                        break

        # NOW find the possible events and filter
        if event_type == "birth_death":
            event_type = "death"
        elif event_type == "health":
            event_type = "injury"
        possible_short_events = GenerateEvents.possible_short_events(event_type)

        final_events = GenerateEvents.filter_possible_short_events(
            Cat_class=Cat,
            possible_events=possible_short_events,
            cat=self.main_cat,
            random_cat=self.random_cat,
            other_clan=self.other_clan,
            freshkill_active=FRESHKILL_EVENT_ACTIVE,
            freshkill_trigger_factor=FRESHKILL_EVENT_TRIGGER_FACTOR,
            sub_types=self.sub_types,
        )

        if isinstance(game.config["event_generation"]["debug_ensure_event_id"], str):
            found = False
            for _event in final_events:
                if (
                    _event.event_id
                    == game.config["event_generation"]["debug_ensure_event_id"]
                ):
                    final_events = [_event]
                    print(
                        f"FOUND debug_ensure_event_id: {game.config['event_generation']['debug_ensure_event_id']} "
                        f"was set as the only event option"
                    )
                    found = True
                    break
            if not found:
                # this print is very spammy, but can be helpful if unsure why a debug event isn't triggering
                # print(f"debug_ensure_event_id: {game.config['event_generation']['debug_ensure_event_id']} "
                #      f"was not possible for {self.main_cat.name}.  {self.main_cat.name} was looking for a {event_type}: {self.sub_types} event")
                pass
        # ---------------------------------------------------------------------------- #
        #                               do the event                                   #
        # ---------------------------------------------------------------------------- #
        try:
            self.chosen_event = random.choice(final_events)
            # this print is good for testing, but gets spammy in large clans
            # print(f"CHOSEN: {self.chosen_event.event_id}")
        except IndexError:
            # this doesn't necessarily mean there's a problem, but can be helpful for narrowing down possibilities
            print(
                f"WARNING: no {event_type}: {self.sub_types} events found for {self.main_cat.name} "
                f"and {self.random_cat.name if self.random_cat else 'no random cat'}"
            )
            return

        self.text = self.chosen_event.text

        self.additional_event_text = ""

        # check if another cat is present
        if self.chosen_event.r_c:
            self.involved_cats.append(self.random_cat.ID)

        # checking if a mass death should happen, happens here so that we can toss the event if needed
        if "mass_death" in self.chosen_event.sub_type:
            if not game.clan.clan_settings["disasters"]:
                return
            self.handle_mass_death()
            if len(self.multi_cat) <= 2:
                return

        # create new cats (must happen here so that new cats can be included in further changes)
        self.handle_new_cats()

        # give accessory
        if self.chosen_event.new_accessory:
            self.handle_accessories()

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

        # used in some murder events, this kinda sucks tho it would be nice to change how this sort of thing is handled
        if "kit_manipulated" in self.chosen_event.tags:
            kit = Cat.fetch_cat(random.choice(get_alive_status_cats(Cat, ["kitten"])))
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

        # kill cats
        self.handle_death()

        # add necessary histories
        self.handle_death_history()

        # handle injuries and injury history
        self.handle_injury()

        # handle murder reveals
        if "murder_reveal" in self.chosen_event.sub_type:
            if "clan_wide" in self.chosen_event.tags:
                other_cat = None
            else:
                other_cat = self.random_cat
            History.reveal_murder(
                cat=self.main_cat,
                other_cat=other_cat,
                cat_class=Cat,
                victim=self.victim_cat,
                murder_index=self.murder_index,
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
            game.herb_events_list.append(f"{self.chosen_event} {self.herb_notice}.")

        game.cur_events_list.append(
            Single_Event(
                self.text + " " + self.additional_event_text,
                self.types,
                self.involved_cats,
            )
        )

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
                    extra_text = f"{cat.name}'s ghost now wanders."
                elif cat.outside:
                    extra_text = f"The Clan has encountered {cat.name}."
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
                            or game.clan.clan_settings["same sex birth"]
                        )
                        and sub_sub[0].ID in (sub[0].parent1, sub[0].parent2)
                        and not (sub_sub[0].dead or sub_sub[0].outside)
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
            if acc not in ["WILD", "PLANT", "COLLAR"]:
                acc_list.append(acc)

        if hasattr(self.main_cat.pelt, "scars"):
            if (
                "NOTAIL" in self.main_cat.pelt.scars
                or "HALFTAIL" in self.main_cat.pelt.scars
            ):
                for acc in pelts.tail_accessories:
                    if acc in acc_list:
                        acc_list.remove(acc)

        if acc_list:
            self.main_cat.pelt.accessory = random.choice(acc_list)

    def handle_death(self):
        """
        handles killing/murdering cats
        """
        dead_list = self.dead_cats if self.dead_cats else []
        current_lives = int(game.clan.leader_lives)

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

            if cat.status == "leader":
                if "all_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= 10
                elif "some_lives" in self.chosen_event.tags:
                    game.clan.leader_lives -= random.randrange(2, current_lives - 1)
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
        alive_cats = [
            i
            for i in Cat.all_cats.values()
            if not i.dead and not i.outside and not i.exiled
        ]

        # make sure all cats in the pool fit the event requirements
        requirements = self.chosen_event.m_c
        for kitty in alive_cats:
            if (
                kitty.status not in requirements["status"]
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
            dead_count = random.choices(population, weights=weights)[0]
            if dead_count < 2:
                dead_count = 2

            self.dead_cats = random.sample(alive_cats, dead_count)
            if self.main_cat not in self.dead_cats:
                self.dead_cats.append(
                    self.main_cat
                )  # got to include the cat that rolled for death in the first place

            taken_cats = []
            for kitty in self.dead_cats:
                if "lost" in self.chosen_event.tags:
                    kitty.gone()
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
                    # find history
                    if self.main_cat.status == "leader":
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

                    # handle murder
                    if "murder" in self.chosen_event.sub_type:
                        revealed = False
                        History.add_murders(
                            self.main_cat, self.random_cat, revealed, death_history
                        )
                    History.add_death(
                        self.main_cat, death_history, other_cat=self.random_cat
                    )

            # random_cat history
            if "r_c" in block["cats"]:
                # death history
                if self.chosen_event.r_c["dies"]:
                    if self.random_cat.status == "leader":
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

                    History.add_death(
                        self.random_cat, death_history, other_cat=self.random_cat
                    )

            # multi_cat history
            if "multi_cat" in block["cats"]:
                for cat in self.multi_cat:
                    if cat.status == "leader":
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

                    History.add_death(cat, death_history)

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
                            History.add_death(
                                new_cats[i], death_history, other_cat=self.random_cat
                            )

    def handle_injury(self):
        """
        assigns an injury to involved cats and then assigns possible histories (if in classic, assigns scar and scar history)
        """

        # if no injury block, then no injury gets assigned
        if not self.chosen_event.injury:
            return

        if "health" not in self.types:
            self.types.append("health")

        # now go through each injury block
        for block in self.chosen_event.injury:
            cats_affected = block["cats"]

            # classic mode only gains scars, not injuries
            if game.clan.game_mode == "classic" and "scars" in block:
                for abbr in cats_affected:
                    # MAIN CAT
                    if abbr == "m_c":
                        if block["scars"] and len(self.main_cat.pelt.scars) < 4:
                            # add a scar
                            self.main_cat.pelt.scars.append(
                                random.choice(block["scars"])
                            )
                            self.handle_injury_history(self.main_cat, "m_c")

                    # RANDOM CAT
                    elif abbr == "r_c":
                        if block["scars"] and len(self.random_cat.pelt.scars) < 4:
                            # add a scar
                            self.random_cat.pelt.scars.append(
                                random.choice(block["scars"])
                            )
                            self.handle_injury_history(self.random_cat, "r_c")

                    # NEW CATS
                    elif "n_c" in abbr:
                        for i, new_cats in enumerate(self.new_cats):
                            if block["scars"] and len(new_cats[i].pelt.scars) < 4:
                                # add a scar
                                new_cats[i].pelt.scars.append(
                                    random.choice(block["scars"])
                                )
                                self.handle_injury_history(new_cats[i], abbr)

            # now give injuries to other modes
            else:
                # find all possible injuries
                possible_injuries = []
                for injury in block["injuries"]:
                    if injury in INJURY_GROUPS:
                        possible_injuries.extend(INJURY_GROUPS[injury])
                    else:
                        possible_injuries.append(injury)

                # give the injury
                for abbr in cats_affected:
                    # MAIN CAT
                    if abbr == "m_c":
                        injury = random.choice(possible_injuries)
                        self.main_cat.get_injured(injury)
                        self.handle_injury_history(self.main_cat, "m_c", injury)

                    # RANDOM CAT
                    elif abbr == "r_c":
                        injury = random.choice(possible_injuries)
                        self.random_cat.get_injured(injury)
                        self.handle_injury_history(self.random_cat, "r_c", injury)

                    # NEW CATS
                    elif "n_c" in abbr:
                        for i, new_cats in enumerate(self.new_cats):
                            injury = random.choice(possible_injuries)
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

        # if injury is false, then this is classic and they just need scar history
        if not injury:
            for block in self.chosen_event.history:
                if "scar" not in block:
                    return
                elif cat_abbr in block["cats"]:
                    history_text = history_text_adjust(
                        block["scar"], self.other_clan_name, game.clan, self.random_cat
                    )
                    History.add_scar(cat, history_text)
                    break
        else:
            for block in self.chosen_event.history:
                if "scar" not in block:
                    return
                elif cat_abbr in block["cats"]:
                    possible_scar = history_text_adjust(
                        block["scar"], self.other_clan_name, game.clan, self.random_cat
                    )
                    if cat.status == "leader":
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
                        History.add_possible_history(
                            cat,
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

        if reduce_amount != 0:
            freshkill_pile.remove_freshkill(reduce_amount, take_random=True)
        if increase_amount != 0:
            freshkill_pile.add_freshkill(increase_amount)

    def handle_herb_supply(self, block):
        """
        handles adjusting herb supply according to info in event block
        :param block: supplies block
        """

        herbs = game.clan.herbs

        adjustment = block["adjust"]
        supply_type = block["type"]
        trigger = block["trigger"]

        clan_size = get_living_clan_cat_count(Cat)
        needed_amount = int(clan_size * 3)

        self.herb_notice = "Lost "
        herb_list = []

        if "reduce" in adjustment:
            self.herb_notice = "Lost "
        elif "increase" in adjustment:
            self.herb_notice = "Gained "

        # adjust entire herb store
        if supply_type == "all_herb":
            for herb in herbs:
                herb_list.append(herb)
                if adjustment == "reduce_full":
                    herbs[herb] = 0
                elif adjustment == "reduce_half":
                    herbs[herb] = int(game.clan.herbs[herb] / 2)
                elif adjustment == "reduce_quarter":
                    herbs[herb] = int(game.clan.herbs[herb] / 4)
                elif adjustment == "reduce_eighth":
                    herbs[herb] = int(game.clan.herbs[herb] / 8)
                elif "increase" in adjustment:
                    herbs[herb] += adjustment.split("_")[1]

        # if we weren't adjusted the whole herb store, then adjust an individual
        else:
            # picking a random herb to adjust
            if supply_type == "any_herb":
                possible_herbs = []
                for herb in herbs:
                    if "always" in trigger:
                        possible_herbs.append(herb)
                    if "low" in trigger and herbs[herb] < needed_amount / 2:
                        possible_herbs.append(herb)
                    if (
                        "adequate" in trigger
                        and needed_amount / 2 < herbs[herb] < needed_amount
                    ):
                        possible_herbs.append(herb)
                    if (
                        "full" in trigger
                        and needed_amount < herbs[herb] < needed_amount * 2
                    ):
                        possible_herbs.append(herb)
                    if "excess" in trigger and needed_amount * 2 < herbs[herb]:
                        possible_herbs.append(herb)
                self.chosen_herb = random.choice(possible_herbs)

            # if it wasn't a random herb or all herbs, then it's one specific herb
            else:
                self.chosen_herb = supply_type

            # now adjust the supply for the chosen_herb
            if adjustment == "reduce_full":
                herbs[self.chosen_herb] = 0
            elif adjustment == "reduce_half":
                herbs[self.chosen_herb] = int(game.clan.herbs[self.chosen_herb] / 2)
            elif adjustment == "reduce_quarter":
                herbs[self.chosen_herb] = int(game.clan.herbs[self.chosen_herb] / 4)
            elif adjustment == "reduce_eighth":
                herbs[self.chosen_herb] = int(game.clan.herbs[self.chosen_herb] / 8)
            elif "increase" in adjustment:
                herbs[self.chosen_herb] += int(adjustment.split("_")[1])

        if not self.chosen_herb:
            self.chosen_herb = random.choice(list(herbs.keys()))
        if self.chosen_herb:
            herb_list.append(self.chosen_herb)

        if herb_list:
            for herb in herb_list:
                if herb in herbs and herbs[herb] == 0:
                    herbs.pop(herb)

        self.herb_notice = self.herb_notice + adjust_list_text(herb_list)

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

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

INJURY_GROUPS = {
    "battle_injury": [
        "claw-wound",
        "mangled leg",
        "mangled tail",
        "torn pelt",
        "cat bite",
    ],
    "minor_injury": ["sprain", "sore", "bruises", "scrapes"],
    "blunt_force_injury": ["broken bone", "broken back", "head damage", "broken jaw"],
    "hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
    "cold_injury": ["shivering", "frostbite"],
    "big_bite_injury": [
        "bite-wound",
        "broken bone",
        "torn pelt",
        "mangled leg",
        "mangled tail",
    ],
    "small_bite_injury": ["bite-wound", "torn ear", "torn pelt", "scrapes"],
    "beak_bite": ["beak bite", "torn ear", "scrapes"],
    "rat_bite": ["rat bite", "torn ear", "torn pelt"],
    "sickness": ["greencough", "redcough", "whitecough", "yellowcough"],
}
