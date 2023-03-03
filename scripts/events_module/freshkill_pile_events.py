import random
from typing import Union

from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.game_essentials import game
from scripts.utility import event_text_adjust
from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.clan_resources.freshkill import Freshkill_Pile, MAL_PERCENTAGE , STARV_PERCENTAGE, FRESHKILL_ACTIVE, FRESHKILL_EVENT_TRIGGER_FACTOR, FRESHKILL_EVENT_ACTIVE

class Freshkill_Events():
    """All events with a connection to freshkill pile or the nutrition of cats."""

    def __init__(self) -> None:
        self.generate_events = GenerateEvents()

    def handle_nutrient(self, cat: Cat, nutrition_info: dict) -> None:
        """
        Handles gaining conditions or death for cats with low nutrient.
        This function should only be called if the game is in 'expanded' or 'cruel season' mode.

            Parameters
            ----------
            cat : Cat
                the cat which has to be checked and updated
            nutrition_info : dict
                dictionary of all nutrition information (can be found in the freshkill pile)
        """
        if not FRESHKILL_ACTIVE:
            return

        if cat.ID not in nutrition_info.keys():
            print(f"WARNING: Could not find cat with ID {cat.ID}({cat.name}) in the nutrition information.")
            return

        # get all events for a certain status of a cat
        cat_nutrition = nutrition_info[cat.ID]
        possible_events = self.generate_events.possible_events(cat.status, cat.age, "nutrition")


        # get the other needed information and values to create a event
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.outside and c.ID != cat.ID, Cat.all_cats.values()
        ))
        if len(possible_other_cats) <= 0:
            other_cat = None
        else:
            other_cat = random.choice(possible_other_cats)
        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{other_clan.name}Clan'

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{other_clan.name}Clan'

        needed_tags = []
        illness = None
        heal = False

        # handle death first, if percentage is 0 or lower, the cat will die
        if cat_nutrition.percentage <= 0:
            # this statement above will prevent, that a dead cat will get an illness
            final_events = self.get_filtered_possibilities(possible_events, ["death"], cat, other_cat)
            if len(final_events) <= 0:
                return
            chosen_event = (random.choice(final_events))

            # set up all the text's
            death_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
            history_text = 'this should not show up - history text'

            # give history to cat if they die
            if cat.status != "leader" and chosen_event.history_text[0] is not None:
                history_text = event_text_adjust(Cat, chosen_event.history_text[0], cat, other_cat, other_clan_name)
            elif cat.status == "leader" and chosen_event.history_text[1] is not None:
                history_text = event_text_adjust(Cat, chosen_event.history_text[1], cat, other_cat, other_clan_name)

            if cat.status == "leader":
                game.clan.leader_lives -= 1
            cat.die()
            cat.died_by.append(history_text)

            types = ["birth_death"]
            game.cur_events_list.append(Single_Event(death_text, types, [cat.ID]))
            return

        # heal cat if percentage is high enough and cat is ill
        elif cat_nutrition.percentage > MAL_PERCENTAGE and cat.is_ill() and "malnourished" in cat.illnesses:
            needed_tags = ["malnourished_healed"]
            illness = "malnourished"
            heal = True

        # heal cat if percentage is high enough and cat is ill
        elif cat_nutrition.percentage > STARV_PERCENTAGE and cat.is_ill() and "starving" in cat.illnesses:
            if cat_nutrition.percentage < MAL_PERCENTAGE:
                if "malnourished" not in cat.illnesses:
                    cat.get_ill("malnourished")
                needed_tags = ["starving_healed"]
                illness = "starving"
                heal = True
            else:
                needed_tags = ["starving_healed"]
                illness = "starving"
                heal = True

        elif cat_nutrition.percentage <= MAL_PERCENTAGE and cat_nutrition.percentage > STARV_PERCENTAGE:
            # because of the smaller 'nutrition buffer', kitten and elder should get the starving condition.
            if cat.status in ["kitten", "elder"]:
                needed_tags = ["starving"]
                illness = "starving"
            else:        
                needed_tags = ["malnourished"]
                illness = "malnourished"

        elif cat_nutrition.percentage <= STARV_PERCENTAGE:
            needed_tags = ["starving"]
            illness = "starving"

        # handle the gaining/healing illness
        if heal:
            cat.illnesses.pop(illness)
        elif not heal and illness:
            cat.get_ill(illness)

        # filter the events according to the needed tags 
        final_events = self.get_filtered_possibilities(possible_events, needed_tags, cat, other_cat)        
        if len(final_events) <= 0:
            return

        chosen_event = (random.choice(final_events))
        event_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
        types = ["health"]
        game.cur_events_list.append(Single_Event(event_text, types, [cat.ID]))

    def handle_amount_freshkill_pile(self, freshkill_pile: Freshkill_Pile, living_cats: list) -> None:
        """
        Handles events (eg. a fox is attacking the camp), which are related to the freshkill pile.
        This function should only be called if the game is in 'expanded' or 'cruel season' mode.

            Parameters
            ----------
            freshkill_pile : Freshkill_Pile
                the freshkill pile which is used to calculate the event
            living_cats : list
                a list of cats which have to be feed
        """

        if not living_cats:
            # End if there are no living cats left.
            return

        # return if settings turned freshkill events off
        if not FRESHKILL_EVENT_ACTIVE:
            return

        # check if amount of the freshkill pile is too big and a event will be triggered
        needed_amount = freshkill_pile.amount_food_needed()
        trigger_value = FRESHKILL_EVENT_TRIGGER_FACTOR * needed_amount
        #print(f" -- FRESHKILL: amount {trigger_value} to trigger freshkill event. current amount {freshkill_pile.total_amount}")
        if freshkill_pile.total_amount < trigger_value:
            return

        factor = int(freshkill_pile.total_amount / needed_amount)
        chance = 10 - factor
        if chance <= 0:
            chance = 1
        #print(f" -- FRESHKILL: trigger chance of 1/{chance}")
        choice = random.randint(1,chance)
        if choice != 1:
            return

        # check if there is much more prey than needed, to filter the events
        much_prey = False
        if freshkill_pile.total_amount >= (trigger_value + needed_amount):
            much_prey = True

        # get different resources, which are later needed
        cat = random.choice(living_cats)
        other_cat = None
        if len(living_cats) > 1:
            other_cat = random.choice(living_cats)
            while other_cat.ID == cat.ID:
                other_cat = random.choice(living_cats)

        possible_events = self.generate_events.possible_events(cat.status, cat.age, "freshkill_pile")
        possible_tasks = ["death", "reduce", "reduce", "reduce", "reduce", "injury", "injury", "injury"]
        needed_tags = []

        # randomly choose which tags are used for the event
        choice = random.choice(possible_tasks)
        double_event = random.choice([True, False])
        if choice == "death":
            needed_tags.append("death")
            needed_tags.append("multi_death")
        elif choice == "injury":
            needed_tags.append("injury")
            needed_tags.append("multi_injury")
        if (double_event and choice != "reduce") or choice == "reduce":
            needed_tags.append("reduce_half")
            needed_tags.append("reduce_quarter")
            if double_event and choice == "reduce":
                injury = random.choice([True, False])
                if injury:
                    needed_tags.append("injury")
                else:
                    needed_tags.append("death")
                    needed_tags.append("multi_death")

        # remove events with the "much_prey" tag, if the condition is not fulfilled
        final_events = []
        for event in possible_events:
            if (not much_prey and "much_prey" not in event.tags) or much_prey:
                final_events.append(event)

        final_events = self.get_filtered_possibilities(final_events, needed_tags, cat, other_cat)  

        # if there are no events available, return
        if len(final_events) <= 0:
            return

        # get the event and trigger certain things
        chosen_event = (random.choice(final_events))
        event_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat)
        self.handle_history_death(chosen_event,cat,other_cat)

        # if a food is stolen, remove the food
        reduce_amount = 0
        if "reduce_half" in chosen_event.tags:
            reduce_amount = int(freshkill_pile.total_amount / 2)
        elif "reduce_quarter" in chosen_event.tags:
            reduce_amount = int(freshkill_pile.total_amount / 4)
        elif "reduce_eighth" in chosen_event.tags:
            reduce_amount = int(freshkill_pile.total_amount / 8)
        freshkill_pile.remove_freshkill(reduce_amount, take_random=True)

        # add it to the event screens
        types = ["misc"]
        if chosen_event.injury:
            types.append("health")
        if "death" in chosen_event.tags:
            types.append("birth_death")

        if "m_c" not in chosen_event.event_text:
            game.cur_events_list.append(Single_Event(event_text, types, []))
        elif "other_cat" in chosen_event.tags and other_cat:
            game.cur_events_list.append(Single_Event(event_text, types, [cat.ID, other_cat.ID]))
        else:
            game.cur_events_list.append(Single_Event(event_text, types, [cat.ID]))

    # ---------------------------------------------------------------------------- #
    #                                helper function                               #
    # ---------------------------------------------------------------------------- #

    def get_filtered_possibilities(self, possible_events: list, needed_tags: list, cat: Cat, other_cat: Union[Cat, None]) -> list:
        """
        Returns a filtered list of possible events for a given list of tags.

            Parameters
            ----------
            possible_events : list
                a list of events to filter
            needed_tags : list
                a list of tags, which should be in the event
            cat : Cat
                the main cat of the provided possible event list  
            other_cat : Cat
                the other cat in the possible event list

            Returns
            -------
            final_events : list
                all events, which fulfill the needed tags
        """
        final_events = []
        for event in possible_events:
            if any(x in event.tags for x in needed_tags):
                if event.other_cat_trait and other_cat and \
                   other_cat.trait in event.other_cat_trait:
                    final_events.append(event)
                    continue

                if event.cat_trait and cat.trait in event.cat_trait:
                    final_events.append(event)
                    continue

                if event.other_cat_skill and other_cat and \
                   other_cat.skill in event.other_cat_skill:
                    final_events.append(event)
                    continue

                if event.cat_skill and cat.skill in event.cat_skill:
                    final_events.append(event)
                    continue

                # if this event has no specification, but one of the needed tags, the event should be considered to be chosen
                if not event.other_cat_trait and not event.cat_trait and \
                    not event.other_cat_skill and not event.cat_skill:
                    final_events.append(event)
        return final_events

    def handle_history_death(self, event: Single_Event, cat: Cat, other_cat: Union[Cat, None]) -> None:
        """
        Handles death and history for a given event.

            Parameters
            ----------
            event : Single_Event
                the event which is be chosen
            cat : Cat
                the main cat of the provided possible event list  
            other_cat : Cat
                the other cat in the possible event list
        """

        if event.injury:
            scar_text = None
            history_normal = None
            history_leader = None
            if event.history_text[0] is not None:
                scar_text = event_text_adjust(Cat, event.history_text[0], cat, other_cat)
            if event.history_text[1] is not None:
                history_normal = event_text_adjust(Cat, event.history_text[1], cat, other_cat)
            elif event.history_text[2] is not None:
                history_leader = event_text_adjust(Cat, event.history_text[2], cat, other_cat)
            
            if cat.status == "leader":
                cat.possible_death = str(history_leader)
            else:
                cat.possible_scar = str(scar_text)
                cat.possible_death = str(history_normal)
        
            cat.get_injured(event.injury, event_triggered=True)
            if "multi_injury" in event.tags and other_cat:
                if other_cat.status == "leader":
                    other_cat.possible_death = str(history_leader)
                else:
                    other_cat.possible_scar = str(scar_text)
                    other_cat.possible_death = str(history_normal)
                other_cat.get_injured(event.injury, event_triggered=True)
            

        # if the length of the history text is 2, this means the event is a instant death event
        if "death" in event.tags or "multi_death" in event.tags:
            history_normal = None
            history_leader = None
            if event.history_text[0] is not None:
                history_normal = event_text_adjust(Cat, event.history_text[0], cat, other_cat)
            if event.history_text[1] is not None:
                history_leader = event_text_adjust(Cat, event.history_text[1], cat, other_cat)

            if cat.status == "leader":
                game.clan.leader_lives -= 1
                cat.died_by.append(history_leader)
            else:
                cat.died_by.append(history_normal)

            cat.die()
            if "multi_death" in event.tags and other_cat:
                if other_cat.status == "leader":
                    game.clan.leader_lives -= 1
                    other_cat.died_by.append(history_leader)
                else:
                    other_cat.died_by.append(history_normal)
                other_cat.die()
            if "multi_death" in event.tags and not other_cat:
                print("WARNING: multi_death event in freshkill pile was triggered, but no other cat was given.")
