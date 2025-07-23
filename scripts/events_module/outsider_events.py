import random

from typing import TYPE_CHECKING

import i18n

from scripts.cat.enums import CatGroup, CatStanding, CatRank
from scripts.clan_package.settings import get_clan_setting
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import load_lang_resource

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

# ---------------------------------------------------------------------------- #
#                               New Cat Event Class                              #
# ---------------------------------------------------------------------------- #


class OutsiderEvents:
    """All events with a connection to outsiders."""

    @staticmethod
    def killing_outsiders(cat: "Cat"):
        if info_dict := get_clan_setting("lead_den_outsider_event"):
            if cat.ID == info_dict["cat_ID"]:
                return

        deaths = load_lang_resource("events/death/outsider_deaths/outsider_deaths.json")

        # killing outside cats
        if cat.status.is_outsider:
            if random.getrandbits(6) == 1 and not cat.dead:
                death_history = "events.death.outsider_deaths.history.default"
                if cat.status.is_exiled(CatGroup.PLAYER_CLAN):
                    text = random.choice(deaths["exiled"])
                elif cat.status.is_lost():
                    text = random.choice(deaths["lost"])
                    death_history = "events.death.outsider_deaths.history.lost"
                else:
                    text = random.choice(deaths[cat.status.social.value])
                    death_history = f"events.death.outsider_deaths.history.{cat.status.social.value}"

                death_history = i18n.t(death_history)
                cat.history.add_death(death_text=death_history)
                cat.die()
                game.cur_events_list.append(
                    Single_Event(text, "birth_death", cat_dict={"m_c": cat})
                )
