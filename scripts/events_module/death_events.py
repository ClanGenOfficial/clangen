import ujson
import random

from scripts.cat.cats import Cat
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import save_death, event_text_adjust
from scripts.game_structure.game_essentials import game, SAVE_DEATH

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

        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{str(other_clan.name)}Clan'
        enemy_clan = f'{str(enemy_clan)}'
        current_lives = int(game.clan.leader_lives)

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{str(other_clan.name)}Clan'

        possible_events = self.generate_events.possible_death_events(cat.status, cat.age)
        final_events = []

        for event in possible_events:

            if game.clan.game_mode in ["expanded", "cruel season"] and "classic" in event.tags:
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
        print('DEATH:', cat.name, cat.status, len(final_events), other_cat.name, other_cat.status)
        death_cause = (random.choice(final_events))

        if "war" in death_cause.tags:
            other_clan_name = enemy_clan

        death_text = event_text_adjust(Cat, death_cause.death_text, cat, other_cat, other_clan_name)
        history_text = 'this should not show up'
        other_history_text = 'this should not show up'

        if cat.status != "leader" and death_cause.history_text[0] is not None:
            history_text = event_text_adjust(Cat, death_cause.history_text[0], cat, other_cat, other_clan_name)
        elif cat.status == "leader" and death_cause.history_text[1] is not None:
            history_text = event_text_adjust(Cat, death_cause.history_text[1], cat, other_cat, other_clan_name)

        # check if other_cat dies and kill them
        if "other_cat_death" in death_cause.tags or "multi_death" in death_cause.tags:
            if cat.status != "leader" and death_cause.history_text[0] is not None:
                other_history_text = event_text_adjust(Cat, death_cause.history_text[0], cat, other_cat, other_clan_name)
            elif cat.status == "leader" and death_cause.history_text[1] is not None:
                other_history_text = event_text_adjust(Cat, death_cause.history_text[1], cat, other_cat, other_clan_name)

        # handle leader lives
        if cat.status == "leader" and "other_cat_death" not in death_cause.tags:
            if "all_lives" in death_cause.tags:
                game.clan.leader_lives -= 10
                cat.die()
                cat.died_by.append(history_text)
            elif "murder" in death_cause.tags or "some_lives" in death_cause.tags:
                if game.clan.leader_lives > 2:
                    game.clan.leader_lives -= random.randrange(2, current_lives - 1)
                    cat.die()
                    cat.died_by.append(history_text)
                else:
                    game.clan.leader_lives -= 3
                    cat.die()
                    cat.died_by.append(history_text)
            else:
                game.clan.leader_lives -= 1
                cat.die()
                cat.died_by.append(history_text)
        else:
            if ("multi_death" in death_cause.tags or "other_cat_death" in death_cause.tags) \
                    and other_cat.status != 'leader':
                other_cat.die()
                other_cat.died_by.append(other_history_text)
            elif ("multi_death" in death_cause.tags or "other_cat_death" in death_cause.tags) \
                    and other_cat.status == 'leader':
                game.clan.leader_lives -= 1
                other_cat.die()
                other_cat.died_by.append(other_history_text)
            if "other_cat_death" not in death_cause.tags:
                cat.die()
                cat.died_by.append(history_text)

        # if "rel_down" in death_cause.tags:
        #    other_clan.relations -= 5

        game.cur_events_list.append(death_text)
        game.birth_death_events_list.append(death_text)
        if "other_clan" in death_cause.tags:
            game.other_clans_events_list.append(death_text)

        if SAVE_DEATH:
            save_death(cat, death_text)




