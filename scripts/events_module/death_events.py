try:
    import ujson
except ImportError:
    import json as ujson
import random

from scripts.cat.cats import Cat, INJURIES
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event

# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class Death_Events():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        self.generate_events = GenerateEvents()
        pass

    def handle_deaths(self, cat, other_cat, war, enemy_clan, alive_kits):
        """ 
        This function handles the deaths
        """
        involved_cats = [cat.ID]
        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{str(other_clan.name)}Clan'
        current_lives = int(game.clan.leader_lives)

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{str(other_clan.name)}Clan'

        possible_events = self.generate_events.possible_death_events(cat.status, cat.age)
        final_events = []

        for event in possible_events:

            if game.clan.game_mode in ["expanded", "cruel season"] and "classic" in event.tags:
                continue

            if "all_lives" in event.tags and int(random.random() * 10):
                continue

            # check season
            if game.clan.current_season not in event.tags:
                continue

            # check that war events only happen when at war
            if "war" in event.tags and not war:
                continue

            # check if clan has kits
            if "clan_kits" in event.tags and not alive_kits:
                continue

            # check for old age
            if "old_age" in event.tags and cat.moons < 150:
                continue

            # check other_cat rank
            if "other_cat_leader" in event.tags and other_cat.status != "leader":
                continue
            elif "other_cat_dep" in event.tags and other_cat.status != "deputy":
                continue
            elif "other_cat_med" in event.tags and \
                    other_cat.status not in ["medicine cat", "medicine cat apprentice"]:
                continue
            elif "other_cat_adult" in event.tags and other_cat.age in ["elder", "kitten"]:
                continue
            elif "other_cat_kit" in event.tags and other_cat.status != "kitten":
                continue

            # check for mate if the event requires one
            if "mate" in event.tags and cat.mate is None:
                continue

            # check cat trait
            if event.cat_trait is not None:
                if cat.trait not in event.cat_trait and int(random.random() * 10):
                    continue

            # check cat skill
            if event.cat_skill is not None:
                if cat.skill not in event.cat_skill and int(random.random() * 10):
                    continue

            # check other_cat trait
            if event.other_cat_trait is not None:
                if other_cat.trait not in event.other_cat_trait and int(random.random() * 10):
                    continue

            # check other_cat skill
            if event.other_cat_skill is not None:
                if other_cat.skill not in event.other_cat_skill and int(random.random() * 10):
                    continue

            final_events.append(event)

        # ---------------------------------------------------------------------------- #
        #                                  kill cats                                   #
        # ---------------------------------------------------------------------------- #
        #print('DEATH:', cat.name, cat.status, len(final_events), other_cat.name, other_cat.status)
        death_cause = (random.choice(final_events))

        # check if the cat's body was retrievable
        if "no_body" in death_cause.tags:
            body = False
        else:
            body = True

        if "war" in death_cause.tags and other_clan is not None and enemy_clan is not None:
            other_clan = enemy_clan
            other_clan_name = other_clan.name + "clan"

        # let's change some relationship values \o/ check if another cat is mentioned and if they live
        if "other_cat" in death_cause.tags and "multi_death" not in death_cause.tags:
            self.handle_relationship_changes(cat, death_cause, other_cat)

        death_text = event_text_adjust(Cat, death_cause.death_text, cat, other_cat, other_clan_name)
        history_text = 'this should not show up - history text'
        other_history_text = 'this should not show up - other_history text'

        # give history to cat if they die
        if cat.status != "leader" and death_cause.history_text[0] is not None and "other_cat_death" not in death_cause.tags:
            history_text = event_text_adjust(Cat, death_cause.history_text[0], cat, other_cat, other_clan_name)
        elif cat.status == "leader" and death_cause.history_text[1] is not None and "other_cat_death" not in death_cause.tags:
            history_text = event_text_adjust(Cat, death_cause.history_text[1], cat, other_cat, other_clan_name)

        # give death history to other cat if they die
        if "other_cat_death" in death_cause.tags or "multi_death" in death_cause.tags:
            involved_cats.append(other_cat.ID)
            if other_cat.status != "leader" and death_cause.history_text[0] is not None:
                other_history_text = event_text_adjust(Cat, death_cause.history_text[0], other_cat, cat, other_clan_name)
            elif other_cat.status == "leader" and death_cause.history_text[1] is not None:
                other_history_text = event_text_adjust(Cat, death_cause.history_text[1], other_cat, cat, other_clan_name)

        # give injuries to other cat if tagged as such
        if "other_cat_injured" in death_cause.tags:
            involved_cats.append(other_cat.ID)
            print("TAG DETECTED", other_cat.name)
            for tag in death_cause.tags:
                if tag in INJURIES:
                    other_cat.get_injured(tag)
                    print("INJURED IN EVENT")

        # handle leader lives
        if cat.status == "leader" and "other_cat_death" not in death_cause.tags:
            if "all_lives" in death_cause.tags:
                game.clan.leader_lives -= 10
                cat.die(body)
                cat.died_by.append(history_text)
            elif "murder" in death_cause.tags or "some_lives" in death_cause.tags:
                if game.clan.leader_lives > 2:
                    game.clan.leader_lives -= random.randrange(1, current_lives - 1)
                    cat.die(body)
                    cat.died_by.append(history_text)
                else:
                    game.clan.leader_lives -= 1
                    cat.die(body)
                    cat.died_by.append(history_text)
            else:
                game.clan.leader_lives -= 1
                cat.die(body)
                cat.died_by.append(history_text)
        else:
            if ("multi_death" in death_cause.tags or "other_cat_death" in death_cause.tags) \
                    and other_cat.status != 'leader':
                other_cat.die(body)
                other_cat.died_by.append(other_history_text)
            elif ("multi_death" in death_cause.tags or "other_cat_death" in death_cause.tags) \
                    and other_cat.status == 'leader':
                game.clan.leader_lives -= 1
                other_cat.die(body)
                other_cat.died_by.append(other_history_text)
            if "other_cat_death" not in death_cause.tags:
                cat.die(body)
                cat.died_by.append(history_text)

        if "rel_down" in death_cause.tags:
            difference = -5
            change_clan_relations(other_clan, difference=difference)

        elif "rel_up" in death_cause.tags:
            difference = 5
            change_clan_relations(other_clan, difference=difference)

        types = ["birth_death"]
        if "other_clan" in death_cause.tags:
            types.append("other_clans")
        game.cur_events_list.append(Single_Event(death_text, types, involved_cats))
        # game.birth_death_events_list.append(death_text)

    def handle_relationship_changes(self, cat, death_cause, other_cat):
        cat_to = None
        cat_from = None
        n = 20
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "rc_to_mc" in death_cause.tags:
            cat_to = [cat.ID]
            cat_from = [other_cat]
        elif "mc_to_rc" in death_cause.tags:
            cat_to = [other_cat.ID]
            cat_from = [cat]
        elif "to_both" in death_cause.tags:
            cat_to = [cat.ID, other_cat.ID]
            cat_from = [other_cat, cat]
        if "romantic" in death_cause.tags:
            romantic = n
        elif "neg_romantic" in death_cause.tags:
            romantic = -n
        if "platonic" in death_cause.tags:
            platonic = n
        elif "neg_platonic" in death_cause.tags:
            platonic = -n
        if "dislike" in death_cause.tags:
            dislike = n
        elif "neg_dislike" in death_cause.tags:
            dislike = -n
        if "respect" in death_cause.tags:
            admiration = n
        elif "neg_respect" in death_cause.tags:
            admiration = -n
        if "comfort" in death_cause.tags:
            comfortable = n
        elif "neg_comfort" in death_cause.tags:
            comfortable = -n
        if "jealousy" in death_cause.tags:
            jealousy = n
        elif "neg_jealousy" in death_cause.tags:
            jealousy = -n
        if "trust" in death_cause.tags:
            trust = n
        elif "neg_trust" in death_cause.tags:
            trust = -n
        change_relationship_values(
            cat_to,
            cat_from,
            romantic,
            platonic,
            dislike,
            admiration,
            comfortable,
            jealousy,
            trust)

