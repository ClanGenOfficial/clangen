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
        other_clan_name = f'{other_clan.name}Clan'
        current_lives = int(game.clan.leader_lives)

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{other_clan.name}Clan'

        possible_events = self.generate_events.possible_events(cat.status, cat.age, "death")
        final_events = self.generate_events.filter_possible_events(possible_events, cat, other_cat, war, enemy_clan,
                                                                   other_clan, alive_kits)


        # ---------------------------------------------------------------------------- #
        #                                  kill cats                                   #
        # ---------------------------------------------------------------------------- #
        death_cause = (random.choice(final_events))

        # check if the cat's body was retrievable
        if "no_body" in death_cause.tags:
            body = False
        else:
            body = True

        if "war" in death_cause.tags and other_clan is not None and enemy_clan is not None:
            other_clan = enemy_clan
            other_clan_name = other_clan.name + "Clan"

        # let's change some relationship values \o/ check if another cat is mentioned and if they live
        if "other_cat" in death_cause.tags and "multi_death" not in death_cause.tags:
            self.handle_relationship_changes(cat, death_cause, other_cat)

        death_text = event_text_adjust(Cat, death_cause.event_text, cat, other_cat, other_clan_name)
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
            for tag in death_cause.tags:
                if tag in INJURIES:
                    other_cat.get_injured(tag)

        # handle leader lives
        additional_event_text = ""
        if cat.status == "leader" and "other_cat_death" not in death_cause.tags:
            if "all_lives" in death_cause.tags:
                game.clan.leader_lives -= 10
                additional_event_text += cat.die(body)
                cat.died_by.append(history_text)
            elif "murder" in death_cause.tags or "some_lives" in death_cause.tags:
                if game.clan.leader_lives > 2:
                    game.clan.leader_lives -= random.randrange(1, current_lives - 1)
                    additional_event_text += cat.die(body)
                    cat.died_by.append(history_text)
                else:
                    game.clan.leader_lives -= 1
                    additional_event_text += cat.die(body)
                    cat.died_by.append(history_text)
            else:
                game.clan.leader_lives -= 1
                additional_event_text += cat.die(body)
                cat.died_by.append(history_text)
        else:
            if ("multi_death" in death_cause.tags or "other_cat_death" in death_cause.tags) \
                    and other_cat.status != 'leader':
                additional_event_text += other_cat.die(body)
                other_cat.died_by.append(other_history_text)
            elif ("multi_death" in death_cause.tags or "other_cat_death" in death_cause.tags) \
                    and other_cat.status == 'leader':
                game.clan.leader_lives -= 1
                additional_event_text += other_cat.die(body)
                other_cat.died_by.append(other_history_text)
            if "other_cat_death" not in death_cause.tags:
                additional_event_text += cat.die(body)
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
        game.cur_events_list.append(Single_Event(death_text + " " + additional_event_text, types, involved_cats))
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

