import random

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.event_class import Single_Event
from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure import game
from scripts.utility import find_alive_cats_with_rank


# ---------------------------------------------------------------------------- #
#                            Disaster Event Class                              #
# ---------------------------------------------------------------------------- #


class DisasterEvents:
    """All events with a connection to disasters."""

    @staticmethod
    def handle_disasters(self):
        """
        This function handles the disasters
        """

        if game.clan.primary_disaster or game.clan.secondary_disaster:
            if game.clan.secondary_disaster:
                self.handle_current_secondary_disaster()
            if game.clan.primary_disaster:
                self.handle_current_primary_disaster()

            return

        # if the chance isn't hit, don't cause a disaster
        if int(random.random() * 1):
            return

        print("new disaster")

        possible_events = GenerateEvents.possible_ongoing_events("disasters")
        final_events = []

        for event in possible_events:
            if event.priority == "secondary":
                print("priority")
                continue
            if game.clan.current_season not in event.season:
                print("season")
                continue
            if (game.clan.camp_bg and "any") not in event.camp:
                print("camp")
                continue

            print("still valid")
            chance = 1
            if event.rarity == "uncommon":
                chance = 10
            elif event.rarity == "rare":
                chance = 20

            if int(random.random() * chance):
                continue

            final_events.append(event)

        # choose and save disaster
        chosen_disaster = random.choice(final_events)
        print("chosen disaster", chosen_disaster.event)
        game.clan.primary_disaster = chosen_disaster

        # display trigger event
        event = self.disaster_text(chosen_disaster.trigger_events)
        event.replace("c_n", f"{game.clan.displayname}Clan")
        game.cur_events_list.append(Single_Event(event, "misc"))

    def handle_current_primary_disaster(self):
        """
        handles the progression for a primary disaster
        """
        # decreasing duration, default decrease is 1 with a chance to decrease by 2
        if not int(random.random() * 10):
            game.clan.primary_disaster.current_duration += 2
        else:
            game.clan.primary_disaster.current_duration += 1

        # triggering conclusion if duration reaches 0
        if (
            game.clan.primary_disaster.current_duration
            >= game.clan.primary_disaster.duration
        ):
            event = self.disaster_text(game.clan.primary_disaster.conclusion_events)
            game.cur_events_list.append(Single_Event(event, "misc"))
            game.clan.primary_disaster = None
            return
        else:
            # giving a progression event
            event_list = game.clan.primary_disaster.progress_events[
                f"moon{game.clan.primary_disaster.current_duration}"
            ]
            event = self.disaster_text(event_list)
            game.cur_events_list.append(Single_Event(event, "misc"))

            # checking if a secondary disaster is triggered
            if game.clan.primary_disaster.secondary_disasters:
                print("secondary disaster rolling")
                picked_disasters = []
                for (
                    potential_disaster
                ) in game.clan.primary_disaster.secondary_disasters:
                    current_primary_duration = (
                        game.clan.primary_disaster.current_duration
                    )
                    default_primary_duration = game.clan.primary_disaster.duration
                    chance = potential_disaster["chance"]

                    # check when the secondary disaster is allowed to trigger
                    if (
                        potential_disaster["triggers_during"] == "start"
                        and current_primary_duration != 1
                    ):
                        continue
                    elif (
                        potential_disaster["triggers_during"] == "end"
                        and current_primary_duration + 1 != default_primary_duration
                    ):
                        continue

                    if not int(random.random() * chance):
                        picked_disasters.append(potential_disaster)

                if picked_disasters:
                    # choose disaster and display trigger event
                    secondary_disaster = random.choice(picked_disasters)
                    print("chosen secondary", secondary_disaster)
                    event = self.disaster_text(secondary_disaster["trigger_events"])
                    game.cur_events_list.append(Single_Event(event, "misc"))

                    # now grab all the disaster's info and save it
                    secondary_disaster = GenerateEvents.possible_ongoing_events(
                        "disasters", specific_event=secondary_disaster["disaster"]
                    )
                    game.clan.secondary_disaster = secondary_disaster
            return

    def handle_current_secondary_disaster(self):
        """
        handles the progression for a secondary disaster
        """
        if not int(random.random() * 10):
            game.clan.secondary_disaster.current_duration += 2
        else:
            game.clan.secondary_disaster.current_duration += 1

        # triggering conclusion if duration reaches 0
        if (
            game.clan.secondary_disaster.current_duration
            >= game.clan.secondary_disaster.duration
        ):
            event = self.disaster_text(game.clan.secondary_disaster.conclusion_events)
            game.cur_events_list.append(Single_Event(event, "misc"))
            game.clan.secondary_disaster = None
            return
        else:
            # giving a progression event
            event_list = game.clan.secondary_disaster.progress_events[
                f"moon{game.clan.secondary_disaster.current_duration}"
            ]
            event = self.disaster_text(event_list)
            game.cur_events_list.append(Single_Event(event, "misc"))

        return

    def disaster_text(self, text_list):
        leader_exists = False
        dep_exists = False
        med_exists = False

        leader = Cat.fetch_cat(game.clan.leader)
        deputy = Cat.fetch_cat(game.clan.deputy)
        med_cats = find_alive_cats_with_rank(
            Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
        )

        # checking if there are cats of the specified rank
        if leader.status.alive_in_player_clan:
            leader_exists = True
        if deputy.status.alive_in_player_clan:
            dep_exists = True
        if med_cats:
            med_exists = True

        # removing events that mention ranks if those ranks are not currently filled in the clan
        for event in text_list:
            if (
                event.find("med_name") == -1 or event.find("medicine cat") == -1
            ) and not med_exists:
                text_list.remove(event)
            if (
                event.find("dep_name") == -1 or event.find("deputy") == -1
            ) and not dep_exists:
                text_list.remove(event)
            if (
                event.find("lead_name") == -1 or event.find("leader") == -1
            ) and not leader_exists:
                text_list.remove(event)

        text = random.choice(text_list)

        text = text.replace("lead_name", str(leader.name))
        text = text.replace("dep_name", str(deputy.name))
        text = text.replace("med_name", str(random.choice(med_cats).name))
        text = text.replace("c_n", f"{game.clan.displayname}Clan")

        return text
