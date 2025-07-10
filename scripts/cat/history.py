import random

from scripts.cat.enums import CatRank
from scripts.cat.skills import SkillPath
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import load_lang_resource


class History:
    """
    this class handles the cat's history!
    """

    def __init__(
        self,
        beginning=None,
        mentor_influence=None,
        app_ceremony=None,
        lead_ceremony=None,
        possible_history=None,
        died_by=None,
        scar_events=None,
        murder=None,
        cat=None,
    ):
        self.beginning = beginning if beginning else {}
        self.mentor_influence = (
            mentor_influence if mentor_influence else {"trait": {}, "skill": {}}
        )
        self.app_ceremony = app_ceremony if app_ceremony else {}
        self.lead_ceremony = lead_ceremony if lead_ceremony else None
        self.possible_history = possible_history if possible_history else {}
        self.died_by = died_by if died_by else []
        self.scar_events = scar_events if scar_events else []
        self.murder = murder if murder else {}
        self.cat = cat

        # fix 'old' history save bugs
        if self.mentor_influence["trait"] is None:
            self.mentor_influence["trait"] = {}
        if self.mentor_influence["skill"] is None:
            self.mentor_influence["skill"] = {}
        if "mentor" in self.mentor_influence:
            del self.mentor_influence["mentor"]

        """ 
        want save to look like
        {
            "beginning": {
                "clan_born": bool,
                "birth_season": season,
                "age": age,
                "moon": moon
            },
            "mentor_influence": {
                "trait": {
                    "mentor_id": {
                        "lawfulness": 0,
                        ...
                        "strings": []
                    }
                },
                "skill": {
                    "mentor_id": {
                        "path": 0,
                        string: []
                    }
                }
            },
            "app_ceremony": {
                "honor": honor,
                "graduation_age": age,
                "moon": moon
            },
            "lead_ceremony": full ceremony text,
            "possible_history": {
                "condition name": {
                    "involved": ID
                    "death_text": text
                    "scar_text": text
                },
                "condition name": {
                    "involved": ID
                    "death_text": text
                    "scar_text": text
                }
            },
            "died_by": [
                {
                    "involved": ID,
                    "text": text,
                    "moon": moon
                }
            ],
            "scar_events": [
                {
                    "involved": ID,
                    "text": text,
                    "moon": moon
                },
                {
                    "involved": ID,
                    "text": text,
                    "moon": moon
                }
            ],
            "murder": {
                "is_murderer": [
                    {
                        "victim": ID,
                        "revealed": bool,
                        "moon": moon the murder occurred,
                        "revealed_by": ID of the discoverer,
                        "revelation_moon": moon the murder was revealed,
                        "revelation_text": revealed murder history
                    }
                ],
                "is_victim": [
                    {
                        "murderer": ID,
                        "revealed": bool,
                        "text": same text as the death history for this murder (revealed history),
                        "unrevealed_text": unrevealed death history,
                        "moon": moon the murder occurred,
                        "revealed_by": ID of the discoverer,
                        "revelation_moon": moon the murder was revealed,
                        "revelation_text": revealed death history
                    }
                ]
            }
        }
        """

    # ---------------------------------------------------------------------------- #
    #                                   utility                                    #
    # ---------------------------------------------------------------------------- #

    def make_dict(self):
        history_dict = {
            "beginning": self.beginning,
            "mentor_influence": self.mentor_influence,
            "app_ceremony": self.app_ceremony,
            "lead_ceremony": self.lead_ceremony,
            "possible_history": self.possible_history,
            "died_by": self.died_by,
            "scar_events": self.scar_events,
            "murder": self.murder,
        }
        return history_dict

    # ---------------------------------------------------------------------------- #
    #                            adding and removing                               #
    # ---------------------------------------------------------------------------- #

    def add_beginning(self, clan_born=False):
        """
        adds joining age and moon info to the cat's history save
        :param clan_born: default False, set True if the cat was not born in the Clan
        """
        if not game.clan:
            return

        self.beginning = {
            "clan_born": clan_born,
            "birth_season": game.clan.current_season if clan_born else None,
            "age": self.cat.moons,
            "moon": game.clan.age,
        }

    def add_mentor_facet_influence_strings(self):
        """
        adds mentor influence to the cat's history save
        """

        if not self.mentor_influence["trait"]:
            return

        if (
            "Benevolent" or "Abrasive" or "Reserved" or "Outgoing"
        ) in self.mentor_influence["trait"]:
            self.mentor_influence["trait"] = {}
            return

        for _ment in self.mentor_influence["trait"]:
            self.mentor_influence["trait"][_ment]["strings"] = []
            for _fac in self.mentor_influence["trait"][_ment]:
                # Check to make sure nothing weird got in there.
                if _fac in self.cat.personality.facet_types:
                    if self.mentor_influence["trait"][_ment][_fac] > 0:
                        self.mentor_influence["trait"][_ment]["strings"].append(
                            random.choice(
                                MENTOR_FACET_INFLUENCE_STRINGS[_fac + "_raise"]
                            )
                        )
                    elif self.mentor_influence["trait"][_ment][_fac] < 0:
                        self.mentor_influence["trait"][_ment]["strings"].append(
                            random.choice(
                                MENTOR_FACET_INFLUENCE_STRINGS[_fac + "_lower"]
                            )
                        )

    def add_mentor_skill_influence_strings(self):
        """
        adds mentor influence to the cat's history save
        """

        if not self.mentor_influence["skill"]:
            return

        for _ment in self.mentor_influence["skill"]:
            self.mentor_influence["skill"][_ment]["strings"] = []
            for _path in self.mentor_influence["skill"][_ment]:
                # Check to make sure nothing weird got in there.
                if _path == "strings":
                    continue

                try:
                    if self.mentor_influence["skill"][_ment][_path] > 0:
                        self.mentor_influence["skill"][_ment]["strings"].append(
                            random.choice(
                                MENTOR_SKILL_INFLUENCE_STRINGS[SkillPath[_path]]
                            )
                        )
                except KeyError:
                    print("issue", _path)

    def add_facet_mentor_influence(self, mentor_id, facet, amount):
        """Adds the history information for a single mentor facet change, that occurs after a patrol."""

        if mentor_id not in self.mentor_influence["trait"]:
            self.mentor_influence["trait"][mentor_id] = {}

        if facet not in self.mentor_influence["trait"][mentor_id]:
            self.mentor_influence["trait"][mentor_id][facet] = 0

        self.mentor_influence["trait"][mentor_id][facet] += amount

    def add_skill_mentor_influence(self, mentor_id, path, amount):
        """Adds mentor influence on skills."""

        if not isinstance(path, SkillPath):
            path = SkillPath[path]

        if mentor_id not in self.mentor_influence["skill"]:
            self.mentor_influence["skill"][mentor_id] = {}

        if path.name not in self.mentor_influence["skill"][mentor_id]:
            self.mentor_influence["skill"][mentor_id][path.name] = 0

        self.mentor_influence["skill"][mentor_id][path.name] += amount

    def add_app_ceremony(self, honor):
        """
        adds ceremony honor to the cat's history
        :param honor: the honor trait given during the cat's ceremony
        """
        if not game.clan:
            return

        self.app_ceremony = {
            "honor": honor,
            "graduation_age": self.cat.moons,
            "moon": game.clan.age,
        }

    def add_possible_history(
        self,
        condition: str,
        death_text: str = None,
        scar_text: str = None,
        other_cat=None,
    ):
        """
        this adds the possible death/scar to the cat's history
        :param condition: the condition that is causing the death/scar
        :param death_text: text for death history
        :param scar_text: text for scar history
        :param other_cat: cat object of other cat involved.
        """

        # If the condition already exists, we don't want to overwrite it
        if condition in self.possible_history:
            if death_text is not None:
                self.possible_history[condition]["death_text"] = death_text
            if scar_text is not None:
                self.possible_history[condition]["scar_text"] = scar_text
            if other_cat is not None:
                self.possible_history[condition]["other_cat"] = other_cat.ID
        else:
            # Use a default is none is provided.
            # Will probably sound weird, but it's better than nothing
            if not death_text:
                death_text = f"m_c died from an injury or illness ({condition})."
            if not scar_text:
                scar_text = f"m_c was scarred from an injury or illness ({condition})."

            self.possible_history[condition] = {
                "death_text": death_text,
                "scar_text": scar_text,
                "other_cat": other_cat.ID if other_cat else None,
            }

    def remove_possible_history(self, condition):
        """
        use to remove possible death/scar histories
        :param condition: condition linked to the death/scar you're removing
        """

        if condition in self.possible_history:
            self.possible_history.pop(condition)

    def add_death(self, death_text, condition=None, other_cat=None):
        """Adds death to cat's history. If a condition is passed, it will look into
        possible_history to see if anything is saved there, and, if so, use the text and
        other_cat there (overriding the
        passed death_text and other_cat)."""

        if not game.clan:
            return

        if other_cat is not None:
            other_cat = other_cat.ID

        if condition in self.possible_history:
            if self.possible_history[condition]["death_text"]:
                death_text = self.possible_history[condition]["death_text"]
            other_cat = self.possible_history[condition].get("other_cat")
            self.remove_possible_history(condition)

        self.died_by.append(
            {"involved": other_cat, "text": death_text, "moon": game.clan.age}
        )

    def add_scar(self, scar_text, condition=None, other_cat=None):
        if not game.clan:
            return

        if other_cat is not None:
            other_cat = other_cat.ID
        if condition in self.possible_history:
            if self.possible_history[condition]["scar_text"]:
                scar_text = self.possible_history[condition]["scar_text"]
            other_cat = self.possible_history[condition].get("other_cat")
            self.remove_possible_history(condition)

        self.scar_events.append(
            {"involved": other_cat, "text": scar_text, "moon": game.clan.age}
        )

    @staticmethod
    def add_murders(victim, murderer, revealed, text=None, unrevealed_text=None):
        """
        this adds murder info
        :param victim: cat object (cat being murdered)
        :param murderer: cat object (cat doing the murdering)
        :param revealed: True or False depending on if the murderer has been revealed to the player
        :param text: event text for the victim's death (should be same as their death history)
        :param unrevealed_text: unrevealed event text for victim's death (not saved in their death history)
        :return:
        """
        if not game.clan:
            return
        if "is_murderer" not in murderer.history.murder:
            murderer.history.murder["is_murderer"] = []
        if "is_victim" not in victim.history.murder:
            victim.history.murder["is_victim"] = []

        murderer.history.murder["is_murderer"].append(
            {"victim": victim.ID, "revealed": revealed, "moon": game.clan.age}
        )
        victim.history.murder["is_victim"].append(
            {
                "murderer": murderer.ID,
                "revealed": revealed,
                "text": text,
                "unrevealed_text": unrevealed_text,
                "moon": game.clan.age,
            }
        )

    def add_lead_ceremony(self):
        """
        generates and adds lead ceremony to history
        """

        self.lead_ceremony = self.cat.generate_lead_ceremony()

    # ---------------------------------------------------------------------------- #
    #                                 retrieving                                   #
    # ---------------------------------------------------------------------------- #

    def get_lead_ceremony(self):
        """
        returns the leader ceremony text
        """

        if not self.lead_ceremony:
            self.add_lead_ceremony()
        return str(self.lead_ceremony)

    def get_possible_history(self, condition=None):
        """
        Returns the requested death/scars dict, example of single event structure:

        {
            "involved": ID,
            "death_text": text,
            "scar_text": text
        },

        example of multi event structure:

        {
            "condition name": {
                "involved": ID,
                "death_text": text,
                "scar_text": text
            },
            "condition name": {
                "involved": ID,
                "death_text": text,
                "scar_text": text
            }
        },

        if possible scar/death is empty, None is returned
        :param condition: which condition that caused the death/scar, default None
        """

        if condition in self.possible_history:
            return self.possible_history[condition]
        elif condition:
            return None
        else:
            return self.possible_history

    """
    example of list structure for below two functions
    
    [
        {
            "involved": ID,
            "text": text,
            "moon": moon
        },
        {
            "involved": ID,
            "text": text,
            "moon": moon
        }
    ]
    """

    def get_death(self):
        return self.died_by

    def get_scars(self):
        return self.scar_events

    @staticmethod
    def reveal_murder(cat_class, murderer, discoverer, victim):
        """Reveals the murder properly in all associated history text.

        :param cat_class: The cat class
        :param murderer: The murderer
        :param discoverer: The cat who discovers the truth about the murder
        :param victim: The victim whose murder is being revealed"""

        victim = cat_class.fetch_cat(victim)
        murder_history = murderer.history.murder
        victim_history = victim.history.murder

        murder_index = None

        for i in murder_history:
            if murder_history[i]["victim"] == victim.ID:
                murder_index = i
                break

        if murder_history:
            if "is_murderer" in murder_history:
                murder_history = murder_history["is_murderer"][murder_index]
                murder_history["revealed"] = True
                murder_history["revealed_by"] = discoverer.ID if discoverer else None
                murder_history["revelation_moon"] = game.clan.age
                if not discoverer:
                    murder_history[
                        "revelation_text"
                    ] = "The truth of {PRONOUN/m_c/poss} crime against [victim] is known to the Clan."
                else:
                    murder_history[
                        "revelation_text"
                    ] = "The truth of {PRONOUN/m_c/poss} crime against [victim] was discovered by [discoverer]."

                victim_history = victim_history["is_victim"][0]
                victim_history["revealed"] = True
                victim_history["revealed_by"] = discoverer.ID if discoverer else None
                victim_history["revelation_moon"] = game.clan.age
                if not discoverer:
                    victim_history[
                        "revelation_text"
                    ] = "The truth of {PRONOUN/m_c/poss} murder is known to the Clan."
                else:
                    victim_history[
                        "revelation_text"
                    ] = "The truth of {PRONOUN/m_c/poss} murder was discovered by [discoverer]."

                discoverer_text: str = ""
                if discoverer:
                    discoverer_text = str(discoverer.name)
                if "clan_discovery" in murder_history:
                    discoverer_text = game.clan.name + "Clan"

                murder_history["revelation_text"] = murder_history[
                    "revelation_text"
                ].replace("[victim]", str(victim.name))
                murder_history["revelation_text"] = murder_history[
                    "revelation_text"
                ].replace("[discoverer]", discoverer_text)
                victim_history["revelation_text"] = victim_history[
                    "revelation_text"
                ].replace("[discoverer]", discoverer_text)


MENTOR_INFLUENCE_STRINGS: dict = load_lang_resource("cat/mentor_influence.json")
MENTOR_FACET_INFLUENCE_STRINGS: dict[str, list[str]] = MENTOR_INFLUENCE_STRINGS["facet"]
MENTOR_SKILL_INFLUENCE_STRINGS: dict[SkillPath, list[str]] = {
    SkillPath[skill]: strings
    for skill, strings in MENTOR_INFLUENCE_STRINGS["skill"].items()
}
