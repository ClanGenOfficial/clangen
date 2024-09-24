# pylint: disable=line-too-long
"""

TODO: Docs


"""

import random
# pylint: enable=line-too-long
import traceback
from collections import Counter

import ujson

from scripts.cat.cats import Cat, cat_class, BACKSTORIES
from scripts.cat.history import History
from scripts.cat.names import Name
from scripts.clan import HERBS
from scripts.clan_resources.freshkill import FRESHKILL_EVENT_ACTIVE
from scripts.conditions import (
    medical_cats_condition_fulfilled,
    get_amount_cat_for_one_medic,
)
from scripts.event_class import Single_Event
from scripts.events_module.condition_events import Condition_Events
from scripts.events_module.generate_events import GenerateEvents, generate_events
from scripts.events_module.handle_short_events import handle_short_events
from scripts.events_module.outsider_events import OutsiderEvents
from scripts.events_module.relation_events import Relation_Events
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.game_structure.game_essentials import game
from scripts.game_structure.windows import SaveError
from scripts.patrol.patrol import Patrol
from scripts.utility import (
    change_clan_relations,
    change_clan_reputation,
    get_alive_status_cats,
    get_living_clan_cat_count,
    get_random_moon_cat,
    ceremony_text_adjust,
    get_current_season,
    adjust_list_text,
    ongoing_event_text_adjust,
    event_text_adjust,
    get_other_clan,
    history_text_adjust,
    unpack_rel_block
)


class Events:
    """
    TODO: DOCS
    """

    all_events = {}
    game.switches["timeskip"] = False
    new_cat_invited = False
    ceremony_accessory = False
    CEREMONY_TXT = None
    WAR_TXT = None

    def __init__(self):
        self.load_ceremonies()
        self.load_war_resources()

    def one_moon(self):
        """
        Handles the moon skipping of the whole Clan.
        """
        game.cur_events_list = []
        game.herb_events_list = []
        game.freshkill_events_list = []
        game.mediated = []
        game.switches["saved_clan"] = False
        self.new_cat_invited = False
        Relation_Events.clear_trigger_dict()
        Patrol.used_patrols.clear()
        game.patrolled.clear()
        game.just_died.clear()

        if any(
            str(cat.status)
            in {
                "leader",
                "deputy",
                "warrior",
                "medicine cat",
                "medicine cat apprentice",
                "apprentice",
                "mediator",
                "mediator apprentice",
            }
            and not cat.dead
            and not cat.outside
            for cat in Cat.all_cats.values()
        ):
            game.switches["no_able_left"] = False

        # age up the clan, set current season
        game.clan.age += 1
        get_current_season()
        Pregnancy_Events.handle_pregnancy_age(game.clan)
        self.check_war()

        if (
            game.clan.game_mode in ["expanded", "cruel season"]
            and game.clan.freshkill_pile
        ):
            # feed the cats and update the nutrient status
            relevant_cats = list(
                filter(
                    lambda _cat: _cat.is_alive()
                    and not _cat.exiled
                    and not _cat.outside,
                    Cat.all_cats.values(),
                )
            )
            game.clan.freshkill_pile.time_skip(relevant_cats, game.freshkill_event_list)
            # get the moonskip freshkill
            self.get_moon_freshkill()


        # checking if a lost cat returns on their own
        rejoin_upperbound = game.config["lost_cat"]["rejoin_chance"]
        if random.randint(1, rejoin_upperbound) == 1:
            self.handle_lost_cats_return()

        # Calling of "one_moon" functions.
        for cat in Cat.all_cats.copy().values():
            if not cat.outside or cat.dead:
                self.one_moon_cat(cat)
            else:
                self.one_moon_outside_cat(cat)

        # Adding in any potential lead den events that have been saved
        if "lead_den_interaction" in game.clan.clan_settings:
            if game.clan.clan_settings["lead_den_interaction"]:
                self.handle_lead_den_event()

        # keeping this commented out till disasters are more polished
        # self.disaster_events.handle_disasters()

        # Handle grief events.
        if Cat.grief_strings:
            # Grab all the dead or outside cats, who should not have grief text
            for ID in Cat.grief_strings.copy():
                check_cat = Cat.all_cats.get(ID)
                if isinstance(check_cat, Cat):
                    if check_cat.dead or check_cat.outside:
                        Cat.grief_strings.pop(ID)

            # Generate events

            for cat_id, values in Cat.grief_strings.items():
                for _val in values:
                    if _val[2] == "minor":
                        # Apply the grief message as a thought to the cat
                        text = event_text_adjust(
                            Cat,
                            _val[0],
                            main_cat=Cat.fetch_cat(cat_id),
                            random_cat=Cat.fetch_cat(_val[1][0]))

                        Cat.fetch_cat(cat_id).thought = text
                    else:
                        game.cur_events_list.append(
                            Single_Event(_val[0], ["birth_death", "relation"], _val[1])
                        )

            Cat.grief_strings.clear()

        if Cat.dead_cats:
            ghost_names = []
            shaken_cats = []
            extra_event = None
            for ghost in Cat.dead_cats:
                ghost_names.append(str(ghost.name))
            insert = adjust_list_text(ghost_names)

            if len(Cat.dead_cats) > 1:
                event = f"The past moon, {insert} have taken their place in StarClan. {game.clan.name}Clan mourns their " \
                        f"loss, and their Clanmates will miss where they had been in their lives. Moments of their " \
                        f"lives are shared in stories around the circle of mourners as those that were closest to them " \
                        f"take them to their final resting place."

                if len(ghost_names) > 2:
                    alive_cats = list(
                        filter(
                            lambda kitty: (
                                kitty.status != "leader"
                                and not kitty.dead
                                and not kitty.outside
                                and not kitty.exiled
                            ),
                            Cat.all_cats.values(),
                        )
                    )
                    # finds a percentage of the living Clan to become shaken

                    if len(alive_cats) == 0:
                        return
                    else:
                        shaken_cats = random.sample(
                            alive_cats,
                            k=max(
                                int((len(alive_cats) * random.choice([4, 5, 6])) / 100),
                                1,
                            ),
                        )

                    shaken_cat_names = []
                    for cat in shaken_cats:
                        shaken_cat_names.append(str(cat.name))
                        cat.get_injured(
                            "shock",
                            event_triggered=False,
                            lethal=False,
                            severity="minor",
                        )

                    insert = adjust_list_text(shaken_cat_names)

                    if len(shaken_cats) == 1:
                        extra_event = f"So much grief and death has taken its toll on the cats of {game.clan.name}Clan. {insert} is particularly shaken by it."
                    else:
                        extra_event = f"So much grief and death has taken its toll on the cats of {game.clan.name}Clan. {insert} are particularly shaken by it. "

            else:
                event = (
                    f"The past moon, {insert} has taken their place in StarClan. {game.clan.name}Clan mourns their "
                    f"loss, and their Clanmates will miss the spot they took up in their lives. Moments of their "
                    f"life are shared in stories around the circle of mourners as those that were closest to them "
                    f"take them to their final resting place."
                )

            game.cur_events_list.append(
                Single_Event(event, ["birth_death"], [i.ID for i in Cat.dead_cats])
            )
            if extra_event:
                game.cur_events_list.append(
                    Single_Event(
                        extra_event, ["birth_death"], [i.ID for i in shaken_cats]
                    )
                )
            Cat.dead_cats.clear()

        if game.clan.game_mode in ['expanded', 'cruel season'] and game.clan.freshkill_pile:
            # make a notification if the Clan does not have enough prey
            if FRESHKILL_EVENT_ACTIVE and not game.clan.freshkill_pile.clan_has_enough_food():
                event_string = f"{game.clan.name}Clan doesn't have enough prey for next moon!"
                game.cur_events_list.insert(0, Single_Event(event_string))
                game.freshkill_event_list.append(event_string)

        self.herb_gather()
        self.handle_focus()

        if game.clan.game_mode in ["expanded", "cruel season"]:
            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            med_fullfilled = medical_cats_condition_fulfilled(
                Cat.all_cats.values(), amount_per_med
            )
            if not med_fullfilled:
                string = (
                    f"{game.clan.name}Clan does not have enough healthy medicine cats! Cats will be sick/hurt "
                    f"for longer and have a higher chance of dying. "
                )
                game.cur_events_list.insert(0, Single_Event(string, "health"))
        else:
            has_med = any(
                str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                and not cat.dead
                and not cat.outside
                for cat in Cat.all_cats.values()
            )
            if not has_med:
                string = f"{game.clan.name}Clan has no medicine cat!"
                game.cur_events_list.insert(0, Single_Event(string, "health"))

        # Clear the list of cats that died this moon.
        game.just_died.clear()

        # Promote leader and deputy, if needed.
        self.check_and_promote_leader()
        self.check_and_promote_deputy()

        # Resort
        if game.sort_type != "id":
            Cat.sort_cats()

        # Clear all the loaded event dicts.
        GenerateEvents.clear_loaded_events()

        # autosave
        if game.clan.clan_settings.get("autosave") and game.clan.age % 5 == 0:
            try:
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_events()
            except:
                SaveError(traceback.format_exc())

    def handle_lead_den_event(self):
        """
        Handles the events that are chosen in the leaders den the previous moon and resets the relevant clan settings
        """
        if game.clan.clan_settings["lead_den_clan_event"]:
            info_dict = game.clan.clan_settings["lead_den_clan_event"]
            gathering_cat = Cat.fetch_cat(info_dict["cat_ID"])

            # drop the event if the gathering cat is no longer available
            if gathering_cat.exiled or gathering_cat.dead or gathering_cat.outside:
                return

            other_clan = get_other_clan(info_dict["other_clan"])

            # get events
            events = generate_events.possible_lead_den_events(
                cat=gathering_cat,
                other_clan_temper=other_clan.temperament,
                player_clan_temper=info_dict["player_clan_temper"],
                event_type="other_clan",
                interaction_type=info_dict["interaction_type"],
                success=info_dict["success"],
            )
            chosen_event = random.choice(events)

            # get text
            event_text = chosen_event["event_text"]

            # change relations and append relation text
            rel_change = chosen_event["rel_change"]
            other_clan.relations += rel_change
            if rel_change > 0:
                event_text += f" (o_c_n relations improved.)"
            elif rel_change == 0:
                event_text += f" (o_c_n relations unchanged.)"
            else:
                event_text += f" (o_c_n relations worsened.)"

            # adjust text and add to event list
            event_text = event_text_adjust(
                Cat,
                event_text,
                main_cat=gathering_cat,
                other_clan=other_clan,
                clan=game.clan)
            game.cur_events_list.insert(4, Single_Event(event_text, "other_clans", [gathering_cat.ID]))

            game.clan.clan_settings["lead_den_clan_event"] = {}

        if game.clan.clan_settings["lead_den_outsider_event"]:
            info_dict = game.clan.clan_settings["lead_den_outsider_event"]
            outsider_cat = Cat.fetch_cat(info_dict["cat_ID"])
            involved_cats = [outsider_cat.ID]
            invited_cats = []

            events = generate_events.possible_lead_den_events(
                cat=outsider_cat,
                event_type="outsider",
                interaction_type=info_dict["interaction_type"],
                success=info_dict["success"],
            )
            chosen_event = random.choice(events)

            # get event text
            event_text = chosen_event["event_text"]
            cat_dict = chosen_event["m_c"]

            # ADJUST REP
            game.clan.reputation += chosen_event["rep_change"]

            additional_kits = None
            # SUCCESS/FAIL
            if info_dict["success"]:
                if info_dict["interaction_type"] == "hunt":
                    History.add_death(
                        outsider_cat,
                        death_text=history_text_adjust(
                            "m_c was killed by c_n.",
                            other_clan_name=None,
                            clan=game.clan,
                        ),
                    )
                    outsider_cat.die()

                elif info_dict["interaction_type"] == "drive":
                    outsider_cat.status = "exiled"
                    outsider_cat.exiled = True
                    outsider_cat.driven_out = True

                elif info_dict["interaction_type"] in ["invite", "search"]:
                    # ADD TO CLAN AND CHECK FOR KITS
                    additional_kits = outsider_cat.add_to_clan()

                    if additional_kits:
                        event_text += " m_c brings along {PRONOUN/m_c/poss} "
                        if len(additional_kits) > 1:
                            event_text += str(len(additional_kits)) + " kittens."
                        else:
                            event_text += "kit."

                        for kit_ID in additional_kits:
                            # add to involved cat list
                            involved_cats.append(kit_ID)
                            kit = Cat.fetch_cat(kit_ID)

                    invited_cats = [outsider_cat.ID]
                    invited_cats.extend(additional_kits)

                    for cat_ID in invited_cats:
                        invited_cat = Cat.fetch_cat(cat_ID)
                        if invited_cat.status.lower() in [
                            "kittypet",
                            "loner",
                            "rogue",
                            "former clancat",
                            "exiled",
                        ]:
                            if (
                                "guided" in invited_cat.backstory
                                and invited_cat.status != "exiled"
                            ):
                                invited_cat.backstory = "outsider1"

                            if (
                                invited_cat.backstory
                                in BACKSTORIES["backstory_categories"][
                                    "healer_backstories"
                                ]
                            ):
                                invited_cat.status = "medicine cat"

                            elif invited_cat.age in ["newborn", "kitten"]:
                                invited_cat.status = invited_cat.age
                                if not invited_cat.name.suffix:
                                    invited_cat.name = Name(
                                        invited_cat.status,
                                        invited_cat.name.prefix,
                                        invited_cat.name.suffix,
                                        invited_cat.pelt.colour,
                                        invited_cat.pelt.name,
                                        invited_cat.pelt.tortiepattern,
                                        game.clan.biome,
                                    )
                                    invited_cat.name.give_suffix(
                                        pelt=None,
                                        biome=game.clan.biome,
                                        tortiepattern=None,
                                    )
                                    invited_cat.specsuffix_hidden = False

                            elif invited_cat.age == "senior":
                                invited_cat.status = "elder"
                            elif invited_cat.age == "adolescent":
                                invited_cat.status = "apprentice"
                                invited_cat.update_mentor()
                            else:
                                invited_cat.status = "warrior"

                        invited_cat.create_relationships_new_cat()

                # this handles ceremonies for cats coming into the clan
                if invited_cats:
                    self.handle_lost_cats_return(invited_cats)

            # give new thought to cats
            if "new_thought" in cat_dict:
                outsider_cat.thought = event_text_adjust(
                    Cat,
                    text=cat_dict["new_thought"],
                    main_cat=outsider_cat,
                    clan=game.clan)

            if "kit_thought" in cat_dict:
                if additional_kits is None:
                    additional_kits = outsider_cat.get_children()
                if additional_kits:
                    for kit_ID in additional_kits:
                        kit = Cat.fetch_cat(kit_ID)
                        kit.thought = event_text_adjust(
                            Cat,
                            text=cat_dict["kit_thought"],
                            main_cat=kit,
                            clan=game.clan)

            if "relationships" in cat_dict:
                unpack_rel_block(Cat, cat_dict["relationships"], extra_cat=outsider_cat)

                pass

            # adjust text and add to event list
            event_text = event_text_adjust(
                Cat,
                text=event_text,
                main_cat=outsider_cat,
                clan=game.clan)

            game.cur_events_list.insert(4, Single_Event(event_text, "misc", involved_cats))

            game.clan.clan_settings["lead_den_outsider_event"] = {}

        game.clan.clan_settings["lead_den_interaction"] = False

    def mediator_events(self, cat):
        """Check for mediator events"""
        # If the cat is a mediator, check if they visited other clans
        if cat.status in ["mediator", "mediator apprentice"] and not cat.not_working():
            # 1 /10 chance
            if not int(random.random() * 10):
                increase = random.randint(-2, 6)
                clan = random.choice(game.clan.all_clans)
                clan.relations += increase
                dispute_type = random.choice(
                    ["hunting", "border", "personal", "herb-gathering"]
                )
                text = (
                    f"{cat.name} travels to {clan} to "
                    f"resolve some recent {dispute_type} disputes. "
                )
                if increase > 4:
                    text += (
                        f"The meeting goes better than expected, and "
                        f"{cat.name} returns with a plan to solve the "
                        f"issue for good."
                    )
                elif increase == 0:
                    text += "However, no progress was made."
                elif increase < 0:
                    text += f"However, it seems {cat.name} only made {clan} more upset."

                game.cur_events_list.append(Single_Event(text, "other_clans", cat.ID))

        if game.clan.clan_settings["become_mediator"]:
            # Note: These chances are large since it triggers every moon.
            # Checking every moon has the effect giving older cats more chances to become a mediator
            _ = game.config["roles"]["become_mediator_chances"]
            if cat.status in _ and not int(random.random() * _[cat.status]):
                game.cur_events_list.append(
                    Single_Event(
                        f"{cat.name} had chosen to use their skills and experience to help "
                        f"solve the Clan's disagreements. A meeting is called, and they "
                        f"become the Clan's newest mediator. ",
                        "ceremony",
                        cat.ID,
                    )
                )
                cat.status_change("mediator")

    def get_moon_freshkill(self):
        """Adding auto freshkill for the current moon."""
        healthy_hunter = list(
            filter(
                lambda c: c.status in ["warrior", "apprentice", "leader", "deputy"]
                and not c.dead
                and not c.outside
                and not c.exiled
                and not c.not_working(),
                Cat.all_cats.values(),
            )
        )

        prey_amount = 0
        for cat in healthy_hunter:
            lower_value = game.prey_config["auto_warrior_prey"][0]
            upper_value = game.prey_config["auto_warrior_prey"][1]
            if cat.status == "apprentice":
                lower_value = game.prey_config["auto_apprentice_prey"][0]
                upper_value = game.prey_config["auto_apprentice_prey"][1]

            prey_amount += random.randint(lower_value, upper_value)
        game.freshkill_event_list.append(
            f"The clan managed to catch {prey_amount} pieces of prey in this moon."
        )
        game.clan.freshkill_pile.add_freshkill(prey_amount)

    def herb_gather(self):
        """
        TODO: DOCS
        """
        if game.clan.game_mode == "classic":
            # in classic, you have a random amount of herbs.
            # the actual herb doesn't matter; it's just the count.
            herb_owned = random.choice(HERBS)
            # values that will change the text that is displayed to say how many herbs you have
            required_herbs = get_living_clan_cat_count(Cat) * 4
            adjustment_factor = random.choices([0.25, 0.5, 1, 2, 3], weights=[1, 2, 3, 2, 1], k=1)[0]
            herb_amount = int(required_herbs * adjustment_factor)
            game.clan.herbs = {
                herb_owned: herb_amount
            }
        else:
            event_list = []
            meds_available = get_alive_status_cats(Cat, ["medicine cat", "medicine cat apprentice"], working=True,
                                                   sort=True)
            for med in meds_available:
                if game.clan.current_season in ["Newleaf", "Greenleaf"]:
                    amount = random.choices([1, 2, 3, 4], [1, 2, 2, 2], k=1)
                elif game.clan.current_season == "Leaf-fall":
                    amount = random.choices([0, 1, 2], [3, 2, 1], k=1)
                else:
                    amount = random.choices([0, 1], [3, 1], k=1)
                if amount[0] != 0:
                    herbs_found = random.sample(HERBS, k=amount[0])
                    herb_display = []
                    for herb in herbs_found:
                        if herb in ["blackberry"]:
                            continue
                        if game.clan.current_season in ["Newleaf", "Greenleaf"]:
                            amount = random.choices([2, 5, 8], [3, 3, 1], k=1)
                        else:
                            amount = random.choices([2, 4], [4, 1], k=1)
                        if herb in game.clan.herbs:
                            game.clan.herbs[herb] += amount[0]
                        else:
                            game.clan.herbs.update({herb: amount[0]})
                        herb_display.append(herb.replace("_", " "))
                else:
                    herbs_found = []
                    herb_display = []
                if not herbs_found:
                    event_list.append(f"{med.name} could not find any herbs this moon.")
                else:
                    try:
                        if len(herbs_found) == 1:
                            insert = f"{herb_display[0]}"
                        elif len(herbs_found) == 2:
                            insert = f"{herb_display[0]} and {herb_display[1]}"
                        else:
                            insert = f"{', '.join(herb_display[:-1])}, and {herb_display[-1]}"
                        event_list.append(f"{med.name} gathered {insert} this moon.")
                    except IndexError:
                        event_list.append(
                            f"{med.name} could not find any herbs this moon."
                        )
                        return
            game.herb_events_list.extend(event_list)

    def handle_focus(self):
        """
        This function should be called late in the 'one_moon' function and handles all focuses which are possible to handle here:
            - business as usual
            - hunting
            - herb gathering
            - threaten outsiders
            - seek outsiders
            - sabotage other clans
            - aid other clans
            - raid other clans
            - hoarding
        Focus which are not able to be handled here:
            rest and recover - handled in:
                - 'self.handle_outbreaks'
                - 'condition_events.handle_injuries'
                - 'condition_events.handle_illnesses'
                - 'cat.moon_skip_illness'
                - 'cat.moon_skip_injury'
        """
        # if no focus is selected, skip all other
        focus_text = "This shouldn't show up, report a bug for the focus feature."
        if game.clan.clan_settings.get(
            "business as usual"
        ) or game.clan.clan_settings.get("rest and recover"):
            return
        elif game.clan.clan_settings.get("hunting"):
            # handle warrior
            healthy_warriors = list(
                filter(
                    lambda c: c.status in ["warrior", "leader", "deputy"]
                    and not c.dead
                    and not c.outside
                    and not c.exiled
                    and not c.not_working(),
                    Cat.all_cats.values(),
                )
            )
            warrior_amount = (
                len(healthy_warriors) * game.config["focus"]["hunting"]["warrior"]
            )

            # handle apprentices
            healthy_apprentices = list(
                filter(
                    lambda c: c.status == "apprentice"
                    and not c.dead
                    and not c.outside
                    and not c.exiled
                    and not c.not_working(),
                    Cat.all_cats.values(),
                )
            )
            app_amount = (
                len(healthy_apprentices) * game.config["focus"]["hunting"]["apprentice"]
            )

            # finish
            total_amount = warrior_amount + app_amount
            game.clan.freshkill_pile.add_freshkill(total_amount)
            if total_amount > 1:
                focus_text = f"With the heightened focus of the Clan, {total_amount} additional pieces of prey were gathered."
            elif total_amount == 1:
                focus_text = f"With the heightened focus of the Clan, {total_amount} additional piece of prey was gathered."
            else:
                focus_text = "Despite the additional focus of the Clan, no prey could be gathered."
            game.freshkill_event_list.append(focus_text)

        elif game.clan.clan_settings.get("herb gathering"):
            herbs_found = []

            # handle medicine cats
            healthy_meds = list(
                filter(
                    lambda c: c.status == "medicine cat"
                    and not c.dead
                    and not c.outside
                    and not c.exiled
                    and not c.not_working(),
                    Cat.all_cats.values(),
                )
            )
            med_amount = game.config["focus"]["herb gathering"]["med"]
            for med in healthy_meds:
                herbs_found.extend(random.sample(HERBS, k=med_amount))

            # handle medicine cat apprentices
            healthy_med_apps = list(
                filter(
                    lambda c: c.status == "medicine cat apprentice"
                    and not c.dead
                    and not c.outside
                    and not c.exiled
                    and not c.not_working(),
                    Cat.all_cats.values(),
                )
            )
            med_amount = game.config["focus"]["herb gathering"]["med_apprentice"]
            for med in healthy_med_apps:
                herbs_found.extend(random.sample(HERBS, k=med_amount))

            # finish
            herb_amount = len(herbs_found)
            herb_counter = Counter(herbs_found)
            game.clan.herbs.update(herb_counter)
            if herb_amount > 1:
                focus_text = f"With the additional focus of the Clan, {herb_amount} herbs were gathered."
            elif herb_amount == 1:
                focus_text = f"With the additional focus of the Clan, {herb_amount} herb was gathered."
            else:
                focus_text = f"Despite the additional focus of the Clan, no herbs could be gathered."

            log_text = (
                "With the additional focus of the Clan, following herbs were gathered: "
            )
            idx = 0
            for herb, amount in herb_counter.items():
                log_text += str(amount) + " " + herb.replace("_", " ")
                idx += 1
                if idx < len(herb_counter) - 1:
                    log_text += ", "
                elif idx < len(herb_counter):
                    log_text += " and "
            log_text += "."
            game.herb_events_list.append(log_text)

        elif game.clan.clan_settings.get("threaten outsiders"):
            amount = game.config["focus"]["outsiders"]["reputation"]
            change_clan_reputation(-amount)
            focus_text = None

        elif game.clan.clan_settings.get("seek outsiders"):
            amount = game.config["focus"]["outsiders"]["reputation"]
            change_clan_reputation(amount)
            focus_text = None

        elif game.clan.clan_settings.get(
            "sabotage other clans"
        ) or game.clan.clan_settings.get("aid other clans"):
            amount = game.config["focus"]["other clans"]["relation"]
            if game.clan.clan_settings.get("sabotage other clans"):
                amount = amount * -1
            for name in game.clan.clans_in_focus:
                clan = [clan for clan in game.clan.all_clans if clan.name == name][0]
                sabotage = game.clan.clan_settings.get("sabotage other clans")
                change_clan_relations(clan, amount)
            focus_text = None

        elif game.clan.clan_settings.get("hoarding") or game.clan.clan_settings.get(
            "raid other clans"
        ):
            info_dict = game.config["focus"]["hoarding"]
            if game.clan.clan_settings.get("raid other clans"):
                info_dict = game.config["focus"]["raid other clans"]

            involved_cats = {"injured": [], "sick": []}
            # handle prey
            healthy_warriors = list(
                filter(
                    lambda c: c.status in ["warrior", "leader", "deputy"]
                    and not c.dead
                    and not c.outside
                    and not c.exiled
                    and not c.not_working(),
                    Cat.all_cats.values(),
                )
            )
            warrior_amount = len(healthy_warriors) * info_dict["prey_warrior"]
            game.clan.freshkill_pile.add_freshkill(warrior_amount)
            if warrior_amount > 1:
                game.freshkill_event_list.append(
                    f"With the additional focus of the Clan, {warrior_amount} prey pieces were caught."
                )
            else:
                game.freshkill_event_list.append(
                    f"With the additional focus of the Clan, {warrior_amount} prey piece was caught."
                )

            # handle herbs
            herbs_found = []
            healthy_meds = list(
                filter(
                    lambda c: c.status == "medicine cat"
                    and not c.dead
                    and not c.outside
                    and not c.exiled
                    and not c.not_working(),
                    Cat.all_cats.values(),
                )
            )
            med_amount = info_dict["herb_medicine"]
            for med in healthy_meds:
                herbs_found.extend(random.sample(HERBS, k=med_amount))
            herb_amount = len(herbs_found)
            if herb_amount > 0:
                herb_counter = Counter(herbs_found)
                game.clan.herbs.update(herb_counter)
                log_text = "With the additional focus of the Clan, following herbs were gathered: "
                idx = 0
                for herb, amount in herb_counter.items():
                    log_text += str(amount) + " " + herb.replace("_", " ")
                    idx += 1
                    if idx < len(herb_counter) - 1:
                        log_text += ", "
                    elif idx < len(herb_counter):
                        log_text += " and "
                log_text += "."
                game.herb_events_list.append(log_text)

            # handle injuries / illness
            relevant_cats = healthy_warriors + healthy_meds
            if game.clan.clan_settings.get("raid other clans"):
                chance = info_dict[f"injury_chance_warrior"]
                # increase the chance of injuries depending on how many clans are raided
                increase = info_dict["chance_increase_per_clan"]
                chance -= increase * len(game.clan.clans_in_focus)
            for cat in relevant_cats:
                # if the raid setting or 50/50 for hoarding to get to the injury part
                if game.clan.clan_settings.get(
                    "raid other clans"
                ) or random.getrandbits(1):
                    status_use = cat.status
                    if status_use in ["deputy", "leader"]:
                        status_use = "warrior"
                    chance = info_dict[f"injury_chance_{status_use}"]
                    if game.clan.clan_settings.get("raid other clans"):
                        # increase the chance of injuries depending on how many clans are raided
                        increase = info_dict["chance_increase_per_clan"]
                        chance -= increase * len(game.clan.clans_in_focus)

                    if not int(random.random() * chance):  # 1/chance
                        possible_injuries = []
                        injury_dict = info_dict["injuries"]
                        for injury, amount in injury_dict.items():
                            possible_injuries.extend([injury] * amount)
                        chosen_injury = random.choice(possible_injuries)
                        cat.get_injured(chosen_injury)
                        involved_cats["injured"].append(cat.ID)
                else:
                    chance = game.config["focus"]["hoarding"]["illness_chance"]
                    if not int(random.random() * chance):  # 1/chance
                        possible_illnesses = []
                        injury_dict = game.config["focus"]["hoarding"]["illnesses"]
                        for illness, amount in injury_dict.items():
                            possible_illnesses.extend([illness] * amount)
                        chosen_illness = random.choice(possible_illnesses)
                        cat.get_ill(chosen_illness)
                        involved_cats["sick"].append(cat.ID)

            # if it is raiding, lower the relation to other clans
            if game.clan.clan_settings.get("raid other clans"):
                for name in game.clan.clans_in_focus:
                    clan = [clan for clan in game.clan.all_clans if clan.name == name][
                        0
                    ]
                    amount = -game.config["focus"]["raid other clans"]["relation"]
                    change_clan_relations(clan, amount)

            # finish
            text_snippet = "due the additional work of hoarding herbs and prey."
            if game.clan.clan_settings.get("raid other clans"):
                text_snippet = "while raiding other Clans to get additional prey."
            for condition_type, value in involved_cats.items():
                if len(value) == 1:
                    game.cur_events_list.append(
                        Single_Event(
                            f"One cat got {condition_type} during {text_snippet}",
                            "health",
                            value,
                        )
                    )
                elif len(value) > 1:
                    game.cur_events_list.append(
                        Single_Event(
                            f"Multiple cats got {condition_type} {text_snippet}",
                            "health",
                            value,
                        )
                    )

            if warrior_amount > 1 and herb_amount > 1:
                focus_text = f"With the additional focus of the Clan, {warrior_amount} pieces of prey and {herb_amount} herbs were gathered."
            elif warrior_amount > 1 and herb_amount == 1:
                focus_text = f"With the additional focus of the Clan, {warrior_amount} pieces of prey and {herb_amount} herb were gathered."
            elif warrior_amount > 1 and herb_amount <= 0:
                focus_text = f"With the additional focus of the Clan, {warrior_amount} pieces of prey and no herbs were gathered."
            elif warrior_amount == 1 and herb_amount > 1:
                focus_text = f"With the additional focus of the Clan, {warrior_amount} piece of prey and {herb_amount} herbs were gathered."
            elif warrior_amount <= 0 and herb_amount > 1:
                focus_text = f"With the additional focus of the Clan, no prey and {herb_amount} herbs were gathered."
            elif warrior_amount == 1 and herb_amount == 1:
                focus_text = f"With the additional focus of the Clan, {warrior_amount} piece of prey and {herb_amount} herb were gathered."
            elif warrior_amount <= 0 and herb_amount <= 0:
                focus_text = "Despite the additional focus of the Clan, neither prey nor herbs could be gathered."
            else:
                focus_text = "This is a bug, report it - focus feature"

        if focus_text:
            game.cur_events_list.insert(0, Single_Event(focus_text, "misc"))

    def handle_lost_cats_return(self, predetermined_cat_IDs: list = None):
        """
        TODO: DOCS
        """
        cat_IDs = []
        if predetermined_cat_IDs:
            cat_IDs = predetermined_cat_IDs

        if not predetermined_cat_IDs:
            eligible_cats = []
            for cat in Cat.all_cats.values():
                if cat.outside and cat.ID not in Cat.outside_cats:
                    # The outside-value must be set to True before the cat can go to cotc
                    Cat.outside_cats.update({cat.ID: cat})

                if (
                    cat.outside
                    and cat.status
                    not in [
                        "kittypet",
                        "loner",
                        "rogue",
                        "former Clancat",
                        "driven off",
                    ]
                    and not cat.exiled
                    and not cat.dead
                ):
                    eligible_cats.append(cat)

            if not eligible_cats:
                return

            lost_cat = random.choice(eligible_cats)
            cat_IDs.append(lost_cat.ID)

            text = [
                "After a long journey, m_c has finally returned home to c_n.",
                "m_c was found at the border, tired, but happy to be home.",
                "m_c strides into camp, much to the everyone's surprise. {PRONOUN/m_c/subject/CAP}{VERB/m_c/'re/'s} home!",
                "{PRONOUN/m_c/subject/CAP} met so many friends on {PRONOUN/m_c/poss} journey, but c_n is where m_c truly belongs. With a tearful goodbye, "
                "{PRONOUN/m_c/subject} {VERB/m_c/return/returns} home.",
            ]
            lost_cat.outside = False
            additional_cats = lost_cat.add_to_clan()
            cat_IDs.extend(additional_cats)
            text = random.choice(text)

            if additional_cats:
                text += " {PRONOUN/m_c/subject/CAP} {VERB/m_c/bring/brings} along {PRONOUN/m_c/poss} "
                if len(additional_cats) > 1:
                    text += str(len(additional_cats)) + " children."
                else:
                    text += "child."

            text = event_text_adjust(Cat, text, main_cat=lost_cat, clan=game.clan)

            game.cur_events_list.append(Single_Event(text, "misc", cat_IDs))

        # Perform a ceremony if needed
        for cat_ID in cat_IDs:
            x = Cat.fetch_cat(cat_ID)
            if x.status in [
                "apprentice",
                "medicine cat apprentice",
                "mediator apprentice",
                "kitten",
                "newborn",
            ]:
                if x.moons >= 15:
                    if x.status == "medicine cat apprentice":
                        self.ceremony(x, "medicine cat")
                    elif x.status == "mediator apprentice":
                        self.ceremony(x, "mediator")
                    else:
                        self.ceremony(x, "warrior")
                elif (
                    x.status
                    not in [
                        "apprentice",
                        "medicine cat apprentice",
                        "mediator apprentice",
                    ]
                    and x.moons >= 6
                ):
                    self.ceremony(x, "apprentice")
            elif x.status != "medicine cat":
                if x.moons == 0:
                    x.status = "newborn"
                elif x.moons < 6:
                    x.status = "kitten"
                elif x.moons < 12 and x.status != "apprentice":
                    x.status_change("apprentice")
                elif x.moons < 120 and x.status != "warrior":
                    x.status_change("warrior")
                elif x.moons > 120:
                    x.status_change("elder")

    def handle_fading(self, cat):
        """
        TODO: DOCS
        """
        if (
            game.clan.clan_settings["fading"]
            and not cat.prevent_fading
            and cat.ID != game.clan.instructor.ID
            and not cat.faded
        ):

            age_to_fade = game.config["fading"]["age_to_fade"]
            opacity_at_fade = game.config["fading"]["opacity_at_fade"]
            fading_speed = game.config["fading"]["visual_fading_speed"]
            # Handle opacity
            cat.pelt.opacity = int(
                (100 - opacity_at_fade)
                * (1 - (cat.dead_for / age_to_fade) ** fading_speed)
                + opacity_at_fade
            )

            # Deal with fading the cat if they are old enough.
            if cat.dead_for > age_to_fade:
                # If order not to add a cat to the faded list
                # twice, we can't remove them or add them to
                # faded cat list here. Rather, they are added to
                # a list of cats that will be "faded" at the next save.

                # Remove from med cat list, just in case.
                # This should never be triggered, but I've has an issue or
                # two with this, so here it is.
                if cat.ID in game.clan.med_cat_list:
                    game.clan.med_cat_list.remove(cat.ID)

                # Unset their mate, if they have one
                if len(cat.mate) > 0:
                    for mate_id in cat.mate:
                        if Cat.all_cats.get(mate_id):
                            cat.unset_mate(Cat.all_cats.get(mate_id))

                # If the cat is the current med, leader, or deputy, remove them
                if game.clan.leader:
                    if game.clan.leader.ID == cat.ID:
                        game.clan.leader = None
                if game.clan.deputy:
                    if game.clan.deputy.ID == cat.ID:
                        game.clan.deputy = None
                if game.clan.medicine_cat:
                    if game.clan.medicine_cat.ID == cat.ID:
                        if game.clan.med_cat_list:  # If there are other med cats
                            game.clan.medicine_cat = Cat.fetch_cat(
                                game.clan.med_cat_list[0]
                            )
                        else:
                            game.clan.medicine_cat = None

                game.cat_to_fade.append(cat.ID)
                cat.set_faded()

    def one_moon_outside_cat(self, cat):
        """
        exiled cat events
        """
        # aging the cat
        cat.one_moon()
        cat.manage_outside_trait()

        self.handle_outside_EX(cat)

        cat.skills.progress_skill(cat)
        Pregnancy_Events.handle_having_kits(cat, clan=game.clan)

        if not cat.dead:
            OutsiderEvents.killing_outsiders(cat)

    def one_moon_cat(self, cat):
        """
        Triggers various moon events for a cat.
        -If dead, cat is given thought, dead_for count increased, and fading handled (then function is returned)
        -Outbreak chance is handled, death event is attempted, and conditions are handled (if death happens, return)
        -cat.one_moon() is triggered
        -mediator events are triggered (this includes the cat choosing to become a mediator)
        -freshkill pile events are triggered
        -if the cat is injured or ill, they're given their own set of possible events to avoid unrealistic behavior.
        They will handle disability events, coming out, pregnancy, apprentice EXP, ceremonies, relationship events, and
        will generate a new thought. Then the function is returned.
        -if the cat was not injured or ill, then they will do all of the above *and* trigger misc events, acc events,
        and new cat events
        """
        if cat.dead:

            cat.thoughts()
            if cat.ID in game.just_died:
                cat.moons += 1
            else:
                cat.dead_for += 1
            self.handle_fading(cat)  # Deal with fading.
            return

        # all actions, which do not trigger an event display and
        # are connected to cats are located in there
        cat.one_moon()

        # Handle Mediator Events
        # TODO: this is not a great way to handle them, ideally they should be converted to ShortEvent format
        self.mediator_events(cat)

        # handle nutrition amount
        # (CARE: the cats have to be fed before this happens - should be handled in "one_moon" function)
        if game.clan.game_mode in ['expanded', 'cruel season'
                                   ] and game.clan.freshkill_pile:
            Condition_Events.handle_nutrient(cat, game.clan.freshkill_pile.nutrition_info)

            if cat.dead:
                return

        # prevent injured or sick cats from unrealistic Clan events
        if cat.is_ill() or cat.is_injured():
            if cat.is_ill() and cat.is_injured():
                if random.getrandbits(1):
                    triggered_death = Condition_Events.handle_injuries(cat)
                    if not triggered_death:
                        Condition_Events.handle_illnesses(cat)
                else:
                    triggered_death = Condition_Events.handle_illnesses(cat)
                    if not triggered_death:
                        Condition_Events.handle_injuries(cat)
            elif cat.is_ill():
                Condition_Events.handle_illnesses(cat)
            else:
                Condition_Events.handle_injuries(cat)
            game.switches["skip_conditions"].clear()
            if cat.dead:
                return
            self.handle_outbreaks(cat)

        # newborns don't do much
        if cat.status == "newborn":
            cat.relationship_interaction()
            cat.thoughts()
            return

        self.handle_apprentice_EX(cat)  # This must be before perform_ceremonies!
        # this HAS TO be before the cat.is_disabled() so that disabled kits can choose a med cat or mediator position
        self.perform_ceremonies(cat)
        cat.skills.progress_skill(cat)  # This must be done after ceremonies.

        # check for death/reveal/risks/retire caused by permanent conditions
        if cat.is_disabled():
            Condition_Events.handle_already_disabled(cat)
            if cat.dead:
                return

        self.coming_out(cat)
        Pregnancy_Events.handle_having_kits(cat, clan=game.clan)
        # Stop the timeskip if the cat died in childbirth
        if cat.dead:
            return

        cat.relationship_interaction()
        cat.thoughts()

        # relationships have to be handled separately, because of the ceremony name change
        if not cat.dead and not cat.outside:
            Relation_Events.handle_relationships(cat)

        # now we make sure ill and injured cats don't get interactions they shouldn't
        if cat.is_ill() or cat.is_injured():
            return

        self.invite_new_cats(cat)
        self.other_interactions(cat)
        self.gain_accessories(cat)

        # switches between the two death handles
        if random.getrandbits(1):
            triggered_death = self.handle_injuries_or_general_death(cat)
            if not triggered_death:
                self.handle_illnesses_or_illness_deaths(cat)
            else:
                game.switches["skip_conditions"].clear()
                return
        else:
            triggered_death = self.handle_illnesses_or_illness_deaths(cat)
            if not triggered_death:
                self.handle_injuries_or_general_death(cat)
            else:
                game.switches["skip_conditions"].clear()
                return

        self.handle_murder(cat)

        game.switches["skip_conditions"].clear()

    def load_war_resources(self):
        resource_dir = "resources/dicts/events/"
        with open(f"{resource_dir}war.json", encoding="ascii") as read_file:
            self.WAR_TXT = ujson.loads(read_file.read())

    def check_war(self):
        """
        interactions with other clans
        """
        # if there are somehow no other clans, don't proceed
        if not game.clan.all_clans:
            return

        # Prevent wars from starting super early in the game.
        if game.clan.age <= 4:
            return

        # check that the save dict has all the things we need
        if "at_war" not in game.clan.war:
            game.clan.war["at_war"] = False
        if "enemy" not in game.clan.war:
            game.clan.war["enemy"] = None
        if "duration" not in game.clan.war:
            game.clan.war["duration"] = 0

        # check if war in progress
        war_events = None
        enemy_clan = None
        if game.clan.war["at_war"]:

            # Grab the enemy clan object
            for other_clan in game.clan.all_clans:
                if other_clan.name == game.clan.war["enemy"]:
                    enemy_clan = other_clan
                    break

            threshold = 5
            if enemy_clan.temperament == "bloodthirsty":
                threshold = 10
            if enemy_clan.temperament in ["mellow", "amiable", "gracious"]:
                threshold = 3

            threshold -= int(game.clan.war["duration"])
            if enemy_clan.relations < 0:
                enemy_clan.relations = 0

            # check if war should conclude, if not, continue
            if enemy_clan.relations >= threshold and game.clan.war["duration"] > 1:
                game.clan.war["at_war"] = False
                game.clan.war["enemy"] = None
                game.clan.war["duration"] = 0
                enemy_clan.relations += 12
                war_events = self.WAR_TXT["conclusion_events"]
            else:  # try to influence the relation with warring clan
                game.clan.war["duration"] += 1
                choice = random.choice(["rel_up", "rel_up", "neutral", "rel_down"])
                game.switches["war_rel_change_type"] = choice
                war_events = self.WAR_TXT["progress_events"][choice]
                if enemy_clan.relations < 0:
                    enemy_clan.relations = 0
                if choice == "rel_up":
                    enemy_clan.relations += 2
                elif choice == "rel_down" and enemy_clan.relations > 1:
                    enemy_clan.relations -= 1

        else:  # try to start a war if no war in progress
            for other_clan in game.clan.all_clans:
                threshold = 5
                if other_clan.temperament == "bloodthirsty":
                    threshold = 10
                if other_clan.temperament in ["mellow", "amiable", "gracious"]:
                    threshold = 3

                if int(other_clan.relations) <= threshold and not int(
                    random.random() * int(other_clan.relations)
                ):
                    enemy_clan = other_clan
                    game.clan.war["at_war"] = True
                    game.clan.war["enemy"] = other_clan.name
                    war_events = self.WAR_TXT["trigger_events"]

        # if nothing happened, return
        if not war_events or not enemy_clan:
            return

        if not game.clan.leader or not game.clan.deputy or not game.clan.medicine_cat:
            for event in war_events:
                if not game.clan.leader and "lead_name" in event:
                    war_events.remove(event)
                if not game.clan.deputy and "dep_name" in event:
                    war_events.remove(event)
                if not game.clan.medicine_cat and "med_name" in event:
                    war_events.remove(event)

        event = random.choice(war_events)
        event = ongoing_event_text_adjust(
            Cat, event, other_clan_name=f"{enemy_clan.name}Clan", clan=game.clan
        )
        game.cur_events_list.append(Single_Event(event, "other_clans"))

    def perform_ceremonies(self, cat):
        """
        ceremonies
        """
        # TODO: hardcoded events, not good, consider how to convert to ShortEvent
        #  we *do* have a ceremony dict and format, not sure why it isn't being used here
        # PROMOTE DEPUTY TO LEADER, IF NEEDED -----------------------
        if game.clan.leader:
            leader_dead = game.clan.leader.dead
            leader_outside = game.clan.leader.outside
        else:
            leader_dead = True
            # If leader is None, treat them as dead (since they are dead - and faded away.)
            leader_outside = True

        # If a Clan deputy exists, and the leader is dead,
        #  outside, or doesn't exist, make the deputy leader.
        if game.clan.deputy:
            if (
                game.clan.deputy is not None
                and not game.clan.deputy.dead
                and not game.clan.deputy.outside
                and (leader_dead or leader_outside)
            ):
                game.clan.new_leader(game.clan.deputy)
                game.clan.leader_lives = 9
                text = ""
                if game.clan.deputy.personality.trait == "bloodthirsty":
                    text = (
                        f"{game.clan.deputy.name} has become the new leader. "
                        f"They stare down at their Clanmates with unsheathed claws, "
                        f"promising a new era for the Clans."
                    )
                else:
                    c = random.choice([1, 2, 3])
                    if c == 1:
                        text = (
                            str(game.clan.deputy.name.prefix)
                            + str(game.clan.deputy.name.suffix)
                            + " has been promoted to the new leader of the Clan. "
                            "They travel immediately to the Moonstone to get their "
                            "nine lives and are hailed by their new name, "
                            + str(game.clan.deputy.name)
                            + "."
                        )
                    elif c == 2:
                        text = (
                            f"{game.clan.deputy.name} has become the new leader of the Clan. "
                            f"They vow that they will protect the Clan, "
                            f"even at the cost of their nine lives."
                        )
                    elif c == 3:
                        text = (
                            f"{game.clan.deputy.name} has received "
                            f"their nine lives and became the "
                            f"new leader of the Clan. They feel like "
                            f"they are not ready for this new "
                            f"responsibility, but will try their best "
                            f"to do what is right for the Clan."
                        )

                # game.ceremony_events_list.append(text)
                text += (
                    f"\nVisit {game.clan.deputy.name}'s "
                    "profile to see their full leader ceremony."
                )

                game.cur_events_list.append(
                    Single_Event(text, "ceremony", game.clan.deputy.ID)
                )
                self.ceremony_accessory = True
                self.gain_accessories(cat)
                game.clan.deputy = None

        # OTHER CEREMONIES ---------------------------------------

        # Protection check, to ensure "None" cats won't cause a crash.
        if cat:
            cat_dead = cat.dead
        else:
            cat_dead = True

        if not cat_dead:
            if cat.status == "deputy" and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.status == "medicine cat" and game.clan.medicine_cat is None:
                game.clan.medicine_cat = cat

            # retiring to elder den
            if (
                not cat.no_retire
                and cat.status in ["warrior", "deputy"]
                and len(cat.apprentice) < 1
                and cat.moons > 114
            ):
                # There is some variation in the age.
                if cat.moons > 140 or not int(
                    random.random() * (-0.7 * cat.moons + 100)
                ):
                    if cat.status == "deputy":
                        game.clan.deputy = None
                    self.ceremony(cat, "elder")

            # apprentice a kitten to either med or warrior
            if cat.moons == cat_class.age_moons["adolescent"][0]:
                if cat.status == "kitten":
                    med_cat_list = [
                        i
                        for i in Cat.all_cats_list
                        if i.status in ["medicine cat", "medicine cat apprentice"]
                        and not (i.dead or i.outside)
                    ]

                    # check if the medicine cat is an elder
                    has_elder_med = [
                        c
                        for c in med_cat_list
                        if c.age == "senior" and c.status == "medicine cat"
                    ]

                    very_old_med = [
                        c
                        for c in med_cat_list
                        if c.moons >= 150 and c.status == "medicine cat"
                    ]

                    # check if the Clan has sufficient med cats
                    has_med = medical_cats_condition_fulfilled(
                        Cat.all_cats.values(),
                        amount_per_med=get_amount_cat_for_one_medic(game.clan),
                    )

                    # check if a med cat app already exists
                    has_med_app = any(
                        cat.status == "medicine cat apprentice" for cat in med_cat_list
                    )

                    # assign chance to become med app depending on current med cat and traits
                    chance = game.config["roles"]["base_medicine_app_chance"]
                    if has_elder_med == med_cat_list:
                        # These chances apply if all the current medicine cats are elders.
                        if has_med:
                            chance = int(chance / 2.22)
                        else:
                            chance = int(chance / 13.67)
                    elif very_old_med == med_cat_list:
                        # These chances apply is all the current medicine cats are very old.
                        if has_med:
                            chance = int(chance / 3)
                        else:
                            chance = int(chance / 14)
                    # These chances will only be reached if the
                    # Clan has at least one non-elder medicine cat.
                    elif not has_med:
                        chance = int(chance / 7.125)
                    elif has_med:
                        chance = int(chance * 2.22)

                    if cat.personality.trait in [
                        "altruistic",
                        "compassionate",
                        "empathetic",
                        "wise",
                        "faithful",
                    ]:
                        chance = int(chance / 1.3)
                    if cat.is_disabled():
                        chance = int(chance / 2)

                    if chance == 0:
                        chance = 1

                    if not has_med_app and not int(random.random() * chance):
                        self.ceremony(cat, "medicine cat apprentice")
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    else:
                        # Chance for mediator apprentice
                        mediator_list = list(
                            filter(
                                lambda x: x.status == "mediator"
                                and not x.dead
                                and not x.outside,
                                Cat.all_cats_list,
                            )
                        )

                        # This checks if at least one mediator already has an apprentice.
                        has_mediator_apprentice = False
                        for c in mediator_list:
                            if c.apprentice:
                                has_mediator_apprentice = True
                                break

                        chance = game.config["roles"]["mediator_app_chance"]
                        if cat.personality.trait in [
                            "charismatic",
                            "empathetic",
                            "responsible",
                            "wise",
                            "thoughtful",
                        ]:
                            chance = int(chance / 1.5)
                        if cat.is_disabled():
                            chance = int(chance / 2)

                        if chance == 0:
                            chance = 1

                        # Only become a mediator if there is already one in the clan.
                        if (
                            mediator_list
                            and not has_mediator_apprentice
                            and not int(random.random() * chance)
                        ):
                            self.ceremony(cat, "mediator apprentice")
                            self.ceremony_accessory = True
                            self.gain_accessories(cat)
                        else:
                            self.ceremony(cat, "apprentice")
                            self.ceremony_accessory = True
                            self.gain_accessories(cat)

            # graduate
            if cat.status in [
                "apprentice",
                "mediator apprentice",
                "medicine cat apprentice",
            ]:

                if game.clan.clan_settings["12_moon_graduation"]:
                    _ready = cat.moons >= 12
                else:
                    _ready = (
                        cat.experience_level not in ["untrained", "trainee"]
                        and cat.moons >= game.config["graduation"]["min_graduating_age"]
                    ) or cat.moons >= game.config["graduation"]["max_apprentice_age"][
                        cat.status
                    ]

                if _ready:
                    if game.clan.clan_settings["12_moon_graduation"]:
                        preparedness = "prepared"
                    else:
                        if cat.moons == game.config["graduation"]["min_graduating_age"]:
                            preparedness = "early"
                        elif cat.experience_level in ["untrained", "trainee"]:
                            preparedness = "unprepared"
                        else:
                            preparedness = "prepared"

                    if cat.status == "apprentice":
                        self.ceremony(cat, "warrior", preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

                    # promote to med cat
                    elif cat.status == "medicine cat apprentice":
                        self.ceremony(cat, "medicine cat", preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

                    elif cat.status == "mediator apprentice":
                        self.ceremony(cat, "mediator", preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

    def load_ceremonies(self):
        """
        TODO: DOCS
        """
        if self.CEREMONY_TXT is not None:
            return

        resource_dir = "resources/dicts/events/ceremonies/"
        with open(f"{resource_dir}ceremony-master.json", encoding="ascii") as read_file:
            self.CEREMONY_TXT = ujson.loads(read_file.read())

        self.ceremony_id_by_tag = {}
        # Sorting.
        for ID in self.CEREMONY_TXT:
            for tag in self.CEREMONY_TXT[ID][0]:
                if tag in self.ceremony_id_by_tag:
                    self.ceremony_id_by_tag[tag].add(ID)
                else:
                    self.ceremony_id_by_tag[tag] = {ID}

    def ceremony(self, cat, promoted_to, preparedness="prepared"):
        """
        promote cats and add to event list
        """
        # ceremony = []

        _ment = (
            Cat.fetch_cat(cat.mentor) if cat.mentor else None
        )  # Grab current mentor, if they have one, before it's removed.
        old_name = str(cat.name)
        cat.status_change(promoted_to)
        cat.rank_change_traits_skill(_ment)

        involved_cats = [cat.ID]  # Clearly, the cat the ceremony is about is involved.

        # Time to gather ceremonies. First, lets gather all the ceremony ID's.
        possible_ceremonies = set()
        dead_mentor = None
        mentor = None
        previous_alive_mentor = None
        dead_parents = []
        living_parents = []
        mentor_type = {
            "medicine cat": ["medicine cat"],
            "warrior": ["warrior", "deputy", "leader", "elder"],
            "mediator": ["mediator"],
        }

        try:
            # Get all the ceremonies for the role ----------------------------------------
            possible_ceremonies.update(self.ceremony_id_by_tag[promoted_to])

            # Get ones for prepared status ----------------------------------------------
            if promoted_to in ["warrior", "medicine cat", "mediator"]:
                possible_ceremonies = possible_ceremonies.intersection(
                    self.ceremony_id_by_tag[preparedness]
                )

            # Gather ones for mentor. -----------------------------------------------------
            tags = []

            # CURRENT MENTOR TAG CHECK
            if cat.mentor:
                if Cat.fetch_cat(cat.mentor).status == "leader":
                    tags.append("yes_leader_mentor")
                else:
                    tags.append("yes_mentor")
                mentor = Cat.fetch_cat(cat.mentor)
            else:
                tags.append("no_mentor")

            for c in reversed(cat.former_mentor):
                if Cat.fetch_cat(c) and Cat.fetch_cat(c).dead:
                    tags.append("dead_mentor")
                    dead_mentor = Cat.fetch_cat(c)
                    break

            # Unlike dead mentors, living mentors must be VALID
            # they must have the correct status for the role the cat
            # is being promoted too.
            valid_living_former_mentors = []
            for c in cat.former_mentor:
                if not (Cat.fetch_cat(c).dead or Cat.fetch_cat(c).outside):
                    if promoted_to in mentor_type:
                        if Cat.fetch_cat(c).status in mentor_type[promoted_to]:
                            valid_living_former_mentors.append(c)
                    else:
                        valid_living_former_mentors.append(c)

            # ALL FORMER MENTOR TAG CHECKS
            if valid_living_former_mentors:
                #  Living Former mentors. Grab the latest living valid mentor.
                previous_alive_mentor = Cat.fetch_cat(valid_living_former_mentors[-1])
                if previous_alive_mentor.status == "leader":
                    tags.append("alive_leader_mentor")
                else:
                    tags.append("alive_mentor")
            else:
                # This tag means the cat has no living, valid mentors.
                tags.append("no_valid_previous_mentor")

            # Now we add the mentor stuff:
            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_mentor"]
            )

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(self.ceremony_id_by_tag[t])
                )

            possible_ceremonies = temp

            # Gather for parents ---------------------------------------------------------
            for p in [cat.parent1, cat.parent2]:
                if Cat.fetch_cat(p):
                    if Cat.fetch_cat(p).dead:
                        dead_parents.append(Cat.fetch_cat(p))
                    # For the purposes of ceremonies, living parents
                    # who are also the leader are not counted.
                    elif (
                        not Cat.fetch_cat(p).dead
                        and not Cat.fetch_cat(p).outside
                        and Cat.fetch_cat(p).status != "leader"
                    ):
                        living_parents.append(Cat.fetch_cat(p))

            tags = []
            if len(dead_parents) >= 1 and "orphaned" not in cat.backstory:
                tags.append("dead1_parents")
            if len(dead_parents) >= 2 and "orphaned" not in cat.backstory:
                tags.append("dead1_parents")
                tags.append("dead2_parents")

            if len(living_parents) >= 1:
                tags.append("alive1_parents")
            if len(living_parents) >= 2:
                tags.append("alive2_parents")

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_parents"]
            )

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(self.ceremony_id_by_tag[t])
                )

            possible_ceremonies = temp

            # Gather for leader ---------------------------------------------------------

            tags = []
            if (
                game.clan.leader
                and not game.clan.leader.dead
                and not game.clan.leader.outside
            ):
                tags.append("yes_leader")
            else:
                tags.append("no_leader")

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_leader"]
            )

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(self.ceremony_id_by_tag[t])
                )

            possible_ceremonies = temp

            # Gather for backstories.json ----------------------------------------------------
            tags = []
            if cat.backstory == ["abandoned1", "abandoned2", "abandoned3"]:
                tags.append("abandoned")
            elif cat.backstory == "clanborn":
                tags.append("clanborn")

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_backstory"]
            )

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(self.ceremony_id_by_tag[t])
                )

            possible_ceremonies = temp
            # Gather for traits --------------------------------------------------------------

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["all_traits"]
            )

            if cat.personality.trait in self.ceremony_id_by_tag:
                temp.update(
                    possible_ceremonies.intersection(
                        self.ceremony_id_by_tag[cat.personality.trait]
                    )
                )

            possible_ceremonies = temp
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            print("Issue gathering ceremony text.", str(cat.name), promoted_to)

        # getting the random honor if it's needed
        random_honor = None
        if promoted_to in ["warrior", "mediator", "medicine cat"]:
            resource_dir = "resources/dicts/events/ceremonies/"
            with open(
                f"{resource_dir}ceremony_traits.json", encoding="ascii"
            ) as read_file:
                TRAITS = ujson.loads(read_file.read())
            try:
                random_honor = random.choice(TRAITS[cat.personality.trait])
            except KeyError:
                random_honor = "hard work"

        if cat.status in ["warrior", "medicine cat", "mediator"]:
            History.add_app_ceremony(cat, random_honor)

        ceremony_tags, ceremony_text = self.CEREMONY_TXT[
            random.choice(list(possible_ceremonies))
        ]

        # This is a bit strange, but it works. If there is
        # only one parent involved, but more than one living
        # or dead parent, the adjust text function will pick
        # a random parent. However, we need to know the
        # parent to include in the involved cats. Therefore,
        # text adjust also returns the random parents it picked,
        # which will be added to the involved cats if needed.
        ceremony_text, involved_living_parent, involved_dead_parent = (
            ceremony_text_adjust(
                Cat,
                ceremony_text,
                cat,
                dead_mentor=dead_mentor,
                random_honor=random_honor,
                old_name=old_name,
                mentor=mentor,
                previous_alive_mentor=previous_alive_mentor,
                living_parents=living_parents,
                dead_parents=dead_parents,
            )
        )

        # Gather additional involved cats
        for tag in ceremony_tags:
            if tag == "yes_leader":
                involved_cats.append(game.clan.leader.ID)
            elif tag in ["yes_mentor", "yes_leader_mentor"]:
                involved_cats.append(cat.mentor)
            elif tag == "dead_mentor":
                involved_cats.append(dead_mentor.ID)
            elif tag in ["alive_mentor", "alive_leader_mentor"]:
                involved_cats.append(previous_alive_mentor.ID)
            elif tag == "alive2_parents" and len(living_parents) >= 2:
                for c in living_parents[:2]:
                    involved_cats.append(c.ID)
            elif tag == "alive1_parents" and involved_living_parent:
                involved_cats.append(involved_living_parent.ID)
            elif tag == "dead2_parents" and len(dead_parents) >= 2:
                for c in dead_parents[:2]:
                    involved_cats.append(c.ID)
            elif tag == "dead1_parent" and involved_dead_parent:
                involved_cats.append(involved_dead_parent.ID)

        # remove duplicates
        involved_cats = list(set(involved_cats))

        game.cur_events_list.append(
            Single_Event(f"{ceremony_text}", "ceremony", involved_cats)
        )
        # game.ceremony_events_list.append(f'{cat.name}{ceremony_text}')

    def gain_accessories(self, cat):
        """
        accessories
        """

        if not cat:
            return

        if cat.dead or cat.outside:
            return

        # check if cat already has acc
        if cat.pelt.accessory:
            self.ceremony_accessory = False
            return

        # find random_cat
        random_cat = get_random_moon_cat(Cat, main_cat=cat)

        # chance to gain acc
        acc_chances = game.config["accessory_generation"]
        chance = acc_chances["base_acc_chance"]
        if cat.status in ["medicine cat", "medicine cat apprentice"]:
            chance += acc_chances["med_modifier"]
        if cat.age in ["kitten", "adolescent"]:
            chance += acc_chances["baby_modifier"]
        elif cat.age in ["senior adult", "senior"]:
            chance += acc_chances["elder_modifier"]
        if cat.personality.trait in [
            "adventurous",
            "childish",
            "confident",
            "daring",
            "playful",
            "attention-seeker",
            "bouncy",
            "sweet",
            "troublesome",
            "impulsive",
            "inquisitive",
            "strange",
            "shameless",
        ]:
            chance += acc_chances["happy_trait_modifier"]
        elif cat.personality.trait in [
            "cold",
            "strict",
            "bossy",
            "bullying",
            "insecure",
            "nervous",
        ]:
            chance += acc_chances["grumpy_trait_modifier"]
        if self.ceremony_accessory:
            chance += acc_chances["ceremony_modifier"]

        # increase chance of acc if the cat had a ceremony
        if chance <= 0:
            chance = 1
        if not int(random.random() * chance):

            sub_type = ["accessory"]
            if self.ceremony_accessory:
                sub_type.append("ceremony")

            handle_short_events.handle_event(event_type="misc",
                                             main_cat=cat,
                                             random_cat=random_cat,
                                             sub_type=sub_type,
                                             freshkill_pile=game.clan.freshkill_pile)

        self.ceremony_accessory = False

        return

    # This gives outsiders exp. There may be a better spot for it to go,
    # but I put it here to keep the exp functions together
    def handle_outside_EX(self, cat):
        if cat.outside:

            if cat.not_working() and int(random.random() * 3):
                return

            if cat.age == "kitten":
                return

            if cat.age == "adolescent":
                ran = game.config["outside_ex"]["base_adolescent_timeskip_ex"]
            elif cat.age == "senior":
                ran = game.config["outside_ex"]["base_senior_timeskip_ex"]
            else:
                ran = game.config["outside_ex"]["base_adult_timeskip_ex"]

            role_modifier = 1
            if cat.status == "kittypet":
                # Kittypets will gain exp at 2/3 the rate of loners or exiled cats, as this assumes they are
                # kept indoors at least part of the time and can't hunt/fight as much
                role_modifier = 0.6

            exp = random.choice(
                list(range(ran[0][0], ran[0][1] + 1))
                + list(range(ran[1][0], ran[1][1] + 1))
            )

            if game.clan.game_mode == "classic":
                exp += random.randint(0, 3)

            cat.experience += max(exp * role_modifier, 1)

    def handle_apprentice_EX(self, cat):
        """
        TODO: DOCS
        """
        if cat.status in [
            "apprentice",
            "medicine cat apprentice",
            "mediator apprentice",
        ]:

            if cat.not_working() and int(random.random() * 3):
                return

            if cat.experience > cat.experience_levels_range["trainee"][1]:
                return

            if cat.status == "medicine cat apprentice":
                ran = game.config["graduation"]["base_med_app_timeskip_ex"]
            else:
                ran = game.config["graduation"]["base_app_timeskip_ex"]

            mentor_modifier = 1
            if not cat.mentor or Cat.fetch_cat(cat.mentor).not_working():
                # Sick mentor debuff
                mentor_modifier = 0.7
                mentor_skill_modifier = 0

            exp = random.choice(
                list(range(ran[0][0], ran[0][1] + 1))
                + list(range(ran[1][0], ran[1][1] + 1))
            )

            if game.clan.game_mode == "classic":
                exp += random.randint(0, 3)

            cat.experience += max(exp * mentor_modifier, 1)

    def invite_new_cats(self, cat):
        """
        new cats
        """
        chance = 200

        alive_cats = list(
            filter(
                lambda kitty: (
                    kitty.status != "leader" and not kitty.dead and not kitty.outside
                ),
                Cat.all_cats.values(),
            )
        )

        clan_size = len(alive_cats)

        base_chance = 700
        if clan_size < 10:
            base_chance = 200
        elif clan_size < 30:
            base_chance = 300

        reputation = game.clan.reputation
        # hostile
        if 1 <= reputation <= 30:
            if clan_size < 10:
                chance = base_chance
            else:
                rep_adjust = int(reputation / 2)
                if rep_adjust == 0:
                    rep_adjust = 1
                chance = base_chance + int(300 / rep_adjust)
        # neutral
        elif 31 <= reputation <= 70:
            if clan_size < 10:
                chance = base_chance - reputation
            else:
                chance = base_chance
        # welcoming
        elif 71 <= reputation <= 100:
            chance = base_chance - reputation

        chance = max(chance, 1)

        # choose other cat
        random_cat = get_random_moon_cat(Cat, main_cat=cat, parent_child_modifier=True, mentor_app_modifier=True)


        if (
            not int(random.random() * chance)
            and cat.age != "kitten"
            and cat.age != "adolescent"
            and not self.new_cat_invited
        ):
            self.new_cat_invited = True

            handle_short_events.handle_event(event_type="new_cat",
                                             main_cat=cat,
                                             random_cat=random_cat,
                                             freshkill_pile=game.clan.freshkill_pile)

    def other_interactions(self, cat):
        """
        TODO: DOCS
        """
        hit = int(random.random() * 30)
        if hit:
            return

        random_cat = get_random_moon_cat(Cat, main_cat=cat)

        handle_short_events.handle_event(event_type="misc",
                                         main_cat=cat,
                                         random_cat=random_cat,
                                         freshkill_pile=game.clan.freshkill_pile)

    def handle_injuries_or_general_death(self, cat):
        """
        decide if cat dies
        """

        # try to get the random_cat
        random_cat = get_random_moon_cat(Cat, cat, parent_child_modifier=True, mentor_app_modifier=True)

        # chance to kill leader: 1/50 by default
        if not int(random.random() * game.get_config_value("death_related", "leader_death_chance")) \
                and cat.status == 'leader' \
                and not cat.not_working():
            handle_short_events.handle_event(event_type="birth_death",
                                             main_cat=cat,
                                             random_cat=random_cat,
                                             freshkill_pile=game.clan.freshkill_pile)

            return True

        # chance to die of old age
        age_start = game.config["death_related"]["old_age_death_start"]
        death_curve_setting = game.config["death_related"]["old_age_death_curve"]
        death_curve_value = 0.001 * death_curve_setting
        # made old_age_death_chance into a separate value to make testing with print statements easier
        old_age_death_chance = ((1 + death_curve_value) ** (cat.moons - age_start)) - 1
        if random.random() <= old_age_death_chance:
            handle_short_events.handle_event(event_type="birth_death",
                                             main_cat=cat,
                                             random_cat=random_cat,
                                             sub_type=["old_age"],
                                             freshkill_pile=game.clan.freshkill_pile)
            return True
        # max age has been indicated to be 300, so if a cat reaches that age, they die of old age
        elif cat.moons >= 300:
            handle_short_events.handle_event(event_type="birth_death",
                                             main_cat=cat,
                                             random_cat=random_cat,
                                             sub_type=["old_age"],
                                             freshkill_pile=game.clan.freshkill_pile)
            return True

        # disaster death chance
        if game.clan.clan_settings.get('disasters'):
            if not random.getrandbits(10):  # 1/1010
                handle_short_events.handle_event(event_type="birth_death",
                                                 main_cat=cat,
                                                 random_cat=random_cat,
                                                 sub_type=["mass_death"],
                                                 freshkill_pile=game.clan.freshkill_pile)
                return True

        # final death chance and then, if not triggered, head to injuries
        if not int(random.random() * game.get_config_value("death_related", f"{game.clan.game_mode}_death_chance")) \
                and not cat.not_working():  # 1/400
            handle_short_events.handle_event(event_type="birth_death",
                                             main_cat=cat,
                                             random_cat=random_cat,
                                             freshkill_pile=game.clan.freshkill_pile)
            return True
        else:
            triggered_death = Condition_Events.handle_injuries(cat, random_cat)

            return triggered_death

    def handle_murder(self, cat):
        """ Handles murder """
        relationships = cat.relationships.values()
        targets = []

        if cat.age in ["kitten", "newborn"]:
            return

        # if this cat is unstable and aggressive, we lower the random murder chance
        random_murder_chance = int(
            game.config["death_related"]["base_random_murder_chance"]
        )
        random_murder_chance -= 0.5 * (
            (cat.personality.aggression) + (16 - cat.personality.stability)
        )

        # Check to see if random murder is triggered.
        # If so, we allow targets to be anyone they have even the smallest amount of dislike for
        if random.getrandbits(max(1, int(random_murder_chance))) == 1:
            targets = [
                i
                for i in relationships
                if i.dislike > 1
                and not Cat.fetch_cat(i.cat_to).dead
                and not Cat.fetch_cat(i.cat_to).outside
            ]
            if not targets:
                return

            chosen_target = random.choice(targets)

            handle_short_events.handle_event(event_type="birth_death",
                                             main_cat=Cat.fetch_cat(chosen_target.cat_to),
                                             random_cat=cat,
                                             sub_type=["murder"],
                                             freshkill_pile=game.clan.freshkill_pile)

            return

        # will this cat actually murder? this takes into account stability and lawfulness
        murder_capable = 7
        if cat.personality.stability < 6:
            murder_capable -= 3
        if cat.personality.lawfulness < 6:
            murder_capable -= 2
        if cat.personality.aggression > 10:
            murder_capable -= 1
        elif cat.personality.aggression > 12:
            murder_capable -= 3

        murder_capable = max(1, murder_capable)

        if random.getrandbits(murder_capable) != 1:
            return

        # If random murder is not triggered, targets can only be those they have some dislike for
        hate_relation = [
            i
            for i in relationships
            if i.dislike > 15
            and not Cat.fetch_cat(i.cat_to).dead
            and not Cat.fetch_cat(i.cat_to).outside
        ]
        targets.extend(hate_relation)
        resent_relation = [
            i
            for i in relationships
            if i.jealousy > 15
            and not Cat.fetch_cat(i.cat_to).dead
            and not Cat.fetch_cat(i.cat_to).outside
        ]
        targets.extend(resent_relation)

        # if we have some, then we need to decide if this cat will kill
        if targets:
            chosen_target = random.choice(targets)

            kill_chance = game.config["death_related"]["base_murder_kill_chance"]

            relation_modifier = int(
                0.5 * int(chosen_target.dislike + chosen_target.jealousy)
            ) - int(
                0.5
                * int(
                    chosen_target.platonic_like
                    + chosen_target.trust
                    + chosen_target.comfortable
                )
            )
            kill_chance -= relation_modifier

            if (
                len(chosen_target.log) > 0
                and "(high negative effect)" in chosen_target.log[-1]
            ):
                kill_chance -= 50

            if (
                len(chosen_target.log) > 0
                and "(medium negative effect)" in chosen_target.log[-1]
            ):
                kill_chance -= 20

            # little easter egg just for fun
            if (
                cat.personality.trait == "ambitious"
                and Cat.fetch_cat(chosen_target.cat_to).status == "leader"
            ):
                kill_chance -= 10

            kill_chance = max(1, int(kill_chance))

            if not int(random.random() * kill_chance):
                print(
                    cat.name, "TARGET CHOSEN", Cat.fetch_cat(chosen_target.cat_to).name
                )
                print("KILL KILL KILL")

                handle_short_events.handle_event(event_type="birth_death",
                                                 main_cat=Cat.fetch_cat(chosen_target.cat_to),
                                                 random_cat=cat,
                                                 sub_type=["murder"],
                                                 freshkill_pile=game.clan.freshkill_pile)

    def handle_illnesses_or_illness_deaths(self, cat):
        """
        This function will handle:
            - expanded mode: getting a new illness (extra function in own class)
        Returns:
            - boolean if a death event occurred or not
        """
        # ---------------------------------------------------------------------------- #
        #                           decide if cat dies                                 #
        # ---------------------------------------------------------------------------- #
        # if triggered_death is True then the cat will die
        triggered_death = False
        triggered_death = Condition_Events.handle_illnesses(
            cat, game.clan.current_season
        )
        return triggered_death

    def handle_twoleg_capture(self, cat):
        """
        TODO: DOCS
        """
        cat.outside = True
        cat.gone()
        # The outside-value must be set to True before the cat can go to cotc
        cat.thought = "Is terrified as they are trapped in a large silver Twoleg den"
        # FIXME: Not sure what this is intended to do; 'cat_class' has no 'other_cats' attribute.
        # cat_class.other_cats[cat.ID] = cat

    def handle_outbreaks(self, cat):
        """Try to infect some cats."""
        # check if the cat is ill,
        # or if Clan has sufficient med cats
        if not cat.is_ill():
            return

        # check how many kitties are already ill
        already_sick = list(
            filter(
                lambda kitty: (not kitty.dead and not kitty.outside and kitty.is_ill()),
                Cat.all_cats.values(),
            )
        )
        already_sick_count = len(already_sick)

        # round up the living kitties
        alive_cats = list(
            filter(
                lambda kitty: (
                    not kitty.dead and not kitty.outside and not kitty.is_ill()
                ),
                Cat.all_cats.values(),
            )
        )
        alive_count = len(alive_cats)

        # if large amount of the population is already sick, stop spreading
        if already_sick_count >= alive_count * 0.25:
            return

        meds = get_alive_status_cats(Cat, ["medicine cat", "medicine cat apprentice"], working=True, sort=True)

        for illness in cat.illnesses:
            # check if illness can infect other cats
            if cat.illnesses[illness]["infectiousness"] == 0:
                continue
            chance = cat.illnesses[illness]["infectiousness"]
            chance += len(meds) * 7
            if not int(random.random() * chance):  # 1/chance to infect
                # fleas are the only condition allowed to spread outside of cold seasons
                if (
                    game.clan.current_season not in ["Leaf-bare", "Leaf-fall"]
                    and illness != "fleas"
                ):
                    continue

                if game.clan.clan_settings.get("rest and recover"):
                    stopping_chance = game.config["focus"]["rest and recover"][
                        "outbreak_prevention"
                    ]
                    if not int(random.random() * stopping_chance):
                        continue

                if illness == "kittencough":
                    # adjust alive cats list to only include kittens
                    alive_cats = list(
                        filter(
                            lambda kitty: (
                                kitty.status in ["kitten", "newborn"]
                                and not kitty.dead
                                and not kitty.outside
                            ),
                            Cat.all_cats.values(),
                        )
                    )
                    alive_count = len(alive_cats)

                max_infected = int(alive_count / 2)  # 1/2 of alive cats
                # If there are less than two cat to infect,
                # you are allowed to infect all the cats
                if max_infected < 2:
                    max_infected = alive_count
                # If, event with all the cats, there is less
                # than two cats to infect, cancel outbreak.
                if max_infected < 2:
                    return

                weights = []
                population = []
                for n in range(2, max_infected + 1):
                    population.append(n)
                    weight = 1 / (0.75 * n)  # Lower chance for more infected cats
                    weights.append(weight)
                infected_count = random.choices(population, weights=weights)[
                    0
                ]  # the infected..

                infected_names = []
                involved_cats = []
                infected_cats = random.sample(alive_cats, infected_count)
                for sick_meowmeow in infected_cats:
                    infected_names.append(str(sick_meowmeow.name))
                    involved_cats.append(sick_meowmeow.ID)
                    sick_meowmeow.get_ill(
                        illness, event_triggered=True
                    )  # SPREAD THE GERMS >:)

                # TODO: hardcoded text events, not good, need to consider how to convert
                #  should this be handled in condition_events.py?
                illness_name = str(illness).capitalize()
                if illness == "kittencough":
                    event = (
                        f"{illness_name} has spread around the nursery. "
                        f'{", ".join(infected_names[:-1])}, and '
                        f"{infected_names[-1]} have been infected."
                    )
                elif illness == "fleas":
                    event = (
                        f"Fleas have been hopping from pelt to pelt and now "
                        f'{", ".join(infected_names[:-1])}, '
                        f"and {infected_names[-1]} are all infested."
                    )
                else:
                    event = (
                        f"{illness_name} has spread around the camp. "
                        f'{", ".join(infected_names[:-1])}, and '
                        f"{infected_names[-1]} have been infected."
                    )

                game.cur_events_list.append(
                    Single_Event(event, "health", involved_cats)
                )
                # game.health_events_list.append(event)
                break

    def coming_out(self, cat):
        """turnin' the kitties trans..."""
        # TODO: should figure out how to handle these as a ShortEvent, we don't want hardcoded text
        if cat.genderalign == cat.gender:
            if cat.moons < 6:
                return

            involved_cats = [cat.ID]
            if cat.age == "adolescent":
                transing_chance = random.getrandbits(8)  # 2/256
            elif cat.age == "young adult":
                transing_chance = random.getrandbits(9)  # 2/512
            else:
                # adult, senior adult, elder
                transing_chance = random.getrandbits(10)  # 2/1028

            if transing_chance:
                # transing_chance != 0, no trans kitties today...    L
                return

            if random.getrandbits(1):  # 50/50
                if cat.gender == "male":
                    cat.genderalign = "trans female"
                    cat.pronouns = [cat.default_pronouns[1].copy()]
                else:
                    cat.genderalign = "trans male"
                    cat.pronouns = [cat.default_pronouns[2].copy()]
            else:
                cat.genderalign = "nonbinary"
                cat.pronouns = [cat.default_pronouns[0].copy()]

            if cat.gender == "male":
                gender = "tom"
            else:
                gender = "she-cat"
            text = f"{cat.name} has realized that {gender} doesn't describe how they feel anymore."
            game.cur_events_list.append(Single_Event(text, "misc", involved_cats))
            # game.misc_events_list.append(text)

    def check_and_promote_leader(self):
        """Checks if a new leader need to be promoted, and promotes them, if needed."""
        # check for leader
        if game.clan.leader:
            leader_invalid = game.clan.leader.dead or game.clan.leader.outside
        else:
            leader_invalid = True

        if leader_invalid:
            self.perform_ceremonies(
                game.clan.leader
            )  # This is where the deputy will be make leader

            if game.clan.leader:
                leader_dead = game.clan.leader.dead
                leader_outside = game.clan.leader.outside
            else:
                leader_dead = True
                leader_outside = True

            if leader_dead or leader_outside:
                game.cur_events_list.insert(
                    0, Single_Event(f"{game.clan.name}Clan has no leader!")
                )

    def check_and_promote_deputy(self):
        # TODO: can these events be handled as ceremony events?

        """Checks if a new deputy needs to be appointed, and appointed them if needed."""
        if (
            not game.clan.deputy
            or game.clan.deputy.dead
            or game.clan.deputy.outside
            or game.clan.deputy.status == "elder"
        ):
            if game.clan.clan_settings.get("deputy"):

                # This determines all the cats who are eligible to be deputy.
                possible_deputies = list(
                    filter(
                        lambda x: not x.dead
                        and not x.outside
                        and x.status == "warrior"
                        and (x.apprentice or x.former_apprentices),
                        Cat.all_cats_list,
                    )
                )

                # If there are possible deputies, choose from that list.
                if possible_deputies:
                    random_cat = random.choice(possible_deputies)
                    involved_cats = [random_cat.ID]

                    # Gather deputy and leader status, for determination of the text.
                    if game.clan.leader:
                        if game.clan.leader.dead or game.clan.leader.outside:
                            leader_status = "not_here"
                        else:
                            leader_status = "here"
                    else:
                        leader_status = "not_here"

                    if game.clan.deputy:
                        if game.clan.deputy.dead or game.clan.deputy.outside:
                            deputy_status = "not_here"
                        else:
                            deputy_status = "here"
                    else:
                        deputy_status = "not_here"

                    if leader_status == "here" and deputy_status == "not_here":

                        if random_cat.personality.trait == "bloodthirsty":
                            text = (
                                f"{random_cat.name} has been chosen as the new deputy. "
                                f"They look at the Clan leader with an odd glint in their eyes."
                            )
                            # No additional involved cats
                        else:
                            if game.clan.deputy:
                                previous_deputy_mention = random.choice(
                                    [
                                        f"They know that {game.clan.deputy.name} would approve.",
                                        f"They hope that {game.clan.deputy.name} would approve.",
                                        f"They don't know if {game.clan.deputy.name} would approve, "
                                        f"but life must go on. ",
                                    ]
                                )
                                involved_cats.append(game.clan.deputy.ID)

                            else:
                                previous_deputy_mention = ""

                            text = (
                                f"{game.clan.leader.name} chooses "
                                f"{random_cat.name} to take over "
                                f"as deputy. " + previous_deputy_mention
                            )

                            involved_cats.append(game.clan.leader.ID)
                    elif leader_status == "not_here" and deputy_status == "here":
                        text = (
                            f"The Clan is without a leader, but a "
                            f"new deputy must still be named.  "
                            f"{random_cat.name} is chosen as the new deputy. "
                            f"The retired deputy nods their approval."
                        )
                    elif leader_status == "not_here" and deputy_status == "not_here":
                        text = (
                            f"Without a leader or deputy, the Clan has been directionless. "
                            f"They all turn to {random_cat.name} with hope for the future."
                        )
                    elif leader_status == "here" and deputy_status == "here":
                        possible_events = [
                            f"{random_cat.name} has been chosen as the new deputy. "  # pylint: disable=line-too-long
                            f"The Clan yowls their name in approval.",  # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. "  # pylint: disable=line-too-long
                            f"Some of the older Clan members question the wisdom in this choice.",
                            # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. "  # pylint: disable=line-too-long
                            f"They hold their head up high and promise to do their best for the Clan.",
                            # pylint: disable=line-too-long
                            f"{game.clan.leader.name} has been thinking deeply all day who they would "  # pylint: disable=line-too-long
                            f"respect and trust enough to stand at their side, and at sunhigh makes the "  # pylint: disable=line-too-long
                            f"announcement that {random_cat.name} will be the Clan's new deputy.",
                            # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. They pray to "  # pylint: disable=line-too-long
                            f"StarClan that they are the right choice for the Clan.",  # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. Although"  # pylint: disable=line-too-long
                            f"they are nervous, they put on a brave front and look forward to serving"  # pylint: disable=line-too-long
                            f"the clan.",
                        ]
                        # No additional involved cats
                        text = random.choice(possible_events)
                    else:
                        # This should never happen. Failsafe.
                        text = f"{random_cat.name} becomes deputy. "
                else:
                    # If there are no possible deputies, choose someone else, with special text.
                    all_warriors = list(
                        filter(
                            lambda x: not x.dead
                            and not x.outside
                            and x.status == "warrior",
                            Cat.all_cats_list,
                        )
                    )
                    if all_warriors:
                        random_cat = random.choice(all_warriors)
                        involved_cats = [random_cat.ID]
                        text = (
                            f"No cat is truly fit to be deputy, "
                            f"but the position can't remain vacant. "
                            f"{random_cat.name} is appointed as the new deputy. "
                        )

                    else:
                        # Is there are no warriors at all, no one is named deputy.
                        game.cur_events_list.append(
                            Single_Event(
                                "There are no cats fit to become deputy. ", "ceremony"
                            )
                        )
                        return

                random_cat.status_change("deputy")
                game.clan.deputy = random_cat

                game.cur_events_list.append(
                    Single_Event(text, "ceremony", involved_cats)
                )

            else:
                game.cur_events_list.insert(
                    0, Single_Event(f"{game.clan.name}Clan has no deputy!")
                )


events_class = Events()
