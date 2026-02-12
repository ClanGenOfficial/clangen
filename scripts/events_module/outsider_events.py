import random

from typing import TYPE_CHECKING

import i18n

from scripts.cat.enums import CatGroup
from scripts.clan_package.settings import get_clan_setting
from scripts.event_class import Single_Event
from scripts.game_structure import game
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
        if random.getrandbits(6) == 1 and not cat.dead:
            death_history = i18n.t("events.death.outsider_deaths.history.default")

            if cat.status.is_exiled(CatGroup.PLAYER_CLAN_ID):
                text = random.choice(deaths["exiled"])
                death_history = i18n.t("events.death.outsider_deaths.history.exiled")
            elif cat.status.is_lost(CatGroup.PLAYER_CLAN_ID):
                text = random.choice(deaths["lost"])
                death_history = i18n.t("events.death.outsider_deaths.history.lost")
            elif cat.status.is_other_clancat or (
                cat.status.is_former_clancat
                and not cat.status.get_last_valid_group_id() == CatGroup.PLAYER_CLAN_ID
            ):
                group_id = cat.status.get_last_valid_group_id()
                if cat.status.is_exiled(group_id):
                    text = random.choice(deaths["other_clan_exiled"])
                    death_history = i18n.t(
                        "events.death.outsider_deaths.history.other_clan_exiled"
                    )
                elif cat.status.is_lost(group_id):
                    text = random.choice(deaths["other_clan_lost"])
                    death_history = i18n.t(
                        "events.death.outsider_deaths.history.other_clan_lost"
                    )
                else:
                    text = random.choice(deaths["other_clan"])
                    death_history = i18n.t(
                        "events.death.outsider_deaths.history.other_clan"
                    )

                clanname = [
                    c for c in game.clan.all_other_clans if c.group_ID == group_id
                ][0].name
                clanname = i18n.t("general.clan", name=clanname)
                text = text.replace("o_c_n", clanname)
                death_history = death_history.replace("o_c_n", clanname)
            elif cat.status.is_outsider:
                text = random.choice(deaths[cat.status.social.value])
                death_history = i18n.t(
                    f"events.death.outsider_deaths.history.{cat.status.social.value}"
                )
            else:
                text = random.choice(deaths["default"])

            cat.history.add_death(death_text=death_history)
            cat.die()
            game.cur_events_list.append(
                Single_Event(text, "birth_death", cat_dict={"m_c": cat})
            )
