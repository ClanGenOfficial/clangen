import random

import i18n
from typing import Literal

from scripts.cat.skills import SkillPath
from scripts.game_structure import game
from scripts.utility import adjust_list_text


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
        afterlife_acceptance=None,
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
        self.afterlife_acceptance = afterlife_acceptance if afterlife_acceptance else None

        # fix 'old' history save bugs
        if self.mentor_influence["trait"] is None:
            self.mentor_influence["trait"] = {}
        if self.mentor_influence["skill"] is None:
            self.mentor_influence["skill"] = {}
        if "mentor" in self.mentor_influence:
            del self.mentor_influence["mentor"]
        # converting old murder saves
        if self.murder:
            for killed in self.murder.get("is_murderer", []):
                if isinstance(killed["revealed"], bool):
                    new_dict = {"to_clan": killed["revealed"], "aware_individuals": []}
                    killed["revealed"] = new_dict
            for death in self.murder.get("is_victim", []):
                if isinstance(death["revealed"], bool):
                    new_dict = {"to_clan": death["revealed"], "aware_individuals": []}
                    death["revealed"] = new_dict

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
                    "lawfulness": 0
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
                },
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
                'involved': ID,
                'text': text,
                "moon": moon
            },
            {
                'involved': ID,
                "text": text,
                "moon": moon
            }
            ]
        "murder": {
            "is_murderer": [
                    {
                    "victim": ID,
                    "moon": moon the murder occurred
                    "revealed": {
                        "to_clan": bool,
                        "aware_individuals": [ID]
                        },
                    },
                ]
            "is_victim": [
                    {
                    "murderer": ID,
                    "moon": moon the murder occurred
                    "revealed": {
                        "to_clan": bool,
                        "aware_individuals": [ID]
                        },
                    },
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
            "afterlife_acceptance": self.afterlife_acceptance,
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
            self.mentor_influence["trait"] = None
            return

        # working under the impression that these blurbs will be preceded by "more likely to"
        facet_influence_text = {
            "lawfulness_raise": [
                "follow rules",
                "follow the status quo",
                "heed {PRONOUN/m_c/poss} inner compass",
                "have strong inner morals",
            ],
            "lawfulness_lower": [
                "bend the rules",
                "break away from the status quo",
                "break rules that don't suit {PRONOUN/m_c/object}",
                "make {PRONOUN/m_c/poss} own rules",
            ],
            "sociability_raise": [
                "be friendly towards others",
                "step out of {PRONOUN/m_c/poss} comfort zone",
                "interact with others",
                "put others at ease",
            ],
            "sociability_lower": [
                "be cold towards others",
                "refrain from socializing",
                "bicker with others",
            ],
            "aggression_raise": [
                "be ready for a fight",
                "start a fight",
                "defend {PRONOUN/m_c/poss} beliefs",
                "use teeth and claws over words",
                "resort to violence",
            ],
            "aggression_lower": [
                "be slow to anger",
                "avoid a fight",
                "use words over teeth and claws",
                "try to avoid violence",
            ],
            "stability_raise": [
                "stay collected",
                "think things through",
                "be resilient",
                "have a positive outlook",
                "be consistent",
                "adapt easily",
            ],
            "stability_lower": [
                "behave erratically",
                "make impulsive decisions",
                "have trouble adapting",
                "dwell on things",
            ],
        }

        for _ment in self.mentor_influence["trait"]:
            self.mentor_influence["trait"][_ment]["strings"] = []
            for _fac in self.mentor_influence["trait"][_ment]:
                # Check to make sure nothing weird got in there.
                if _fac in self.cat.personality.facet_types:
                    if self.mentor_influence["trait"][_ment][_fac] > 0:
                        self.mentor_influence["trait"][_ment]["strings"].append(
                            random.choice(facet_influence_text[_fac + "_raise"])
                        )
                    elif self.mentor_influence["trait"][_ment][_fac] < 0:
                        self.mentor_influence["trait"][_ment]["strings"].append(
                            random.choice(facet_influence_text[_fac + "_lower"])
                        )

    def add_mentor_skill_influence_strings(self):
        """
        adds mentor influence to the cat's history save
        """

        if not self.mentor_influence["skill"]:
            return

        # working under the impression that these blurbs will be preceded by "become better at"
        skill_influence_text = {
            SkillPath.TEACHER: ["teaching"],
            SkillPath.HUNTER: ["hunting"],
            SkillPath.FIGHTER: ["fighting"],
            SkillPath.RUNNER: ["running"],
            SkillPath.CLIMBER: ["climbing"],
            SkillPath.SWIMMER: ["swimming"],
            SkillPath.SPEAKER: ["arguing"],
            SkillPath.MEDIATOR: ["resolving arguments"],
            SkillPath.CLEVER: ["solving problems"],
            SkillPath.INSIGHTFUL: ["providing insight"],
            SkillPath.SENSE: ["noticing small details"],
            SkillPath.KIT: ["caring for kittens"],
            SkillPath.STORY: ["storytelling"],
            SkillPath.LORE: ["remembering lore"],
            SkillPath.CAMP: ["caring for camp"],
            SkillPath.HEALER: ["healing"],
            SkillPath.STAR: ["connecting to StarClan"],
            SkillPath.OMEN: ["finding omens"],
            SkillPath.DREAM: ["understanding dreams"],
            SkillPath.CLAIRVOYANT: ["predicting the future"],
            SkillPath.PROPHET: ["understanding prophecies"],
            SkillPath.GHOST: ["connecting to the afterlife"],
        }

        for _ment in self.mentor_influence["skill"]:
            self.mentor_influence["skill"][_ment]["strings"] = []
            for _path in self.mentor_influence["skill"][_ment]:
                # Check to make sure nothing weird got in there.
                if _path == "strings":
                    continue

                try:
                    if self.mentor_influence["skill"][_ment][_path] > 0:
                        self.mentor_influence["skill"][_ment]["strings"].append(
                            random.choice(skill_influence_text[SkillPath[_path]])
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
        # :param scar: set True if removing scar
        # :param death: set True if removing death
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

    def add_afterlife_acceptance(self, afterlife: Literal["starclan", "dark_forest"], is_kit=False, contentious=False, rejected=False):
        """
        Adds afterlife acceptance text to the cat's history. If using an optional parameter, should set only one out of
        `is_kit`, `contentious`, and `rejected` to `True`, since the rest will be ignored.

        :param afterlife: The afterlife of the guide.
        :param is_kit: `True` if the cat is a kit. Gives kinder acceptance text referring to kits.
        :param contentious: `True` if the acceptance is supposed to be contentious. Afterlife will seem iffy about the cat.
        :param rejected: `True` if cat is rejected from `afterlife`. They will go to the opposite one instead.
        """

        starclan_default_text = [
            "m_c breathed in deep, {PRONOUN/m_c/poss} spirit settled as {PRONOUN/m_c/subject} finally joined the home waiting for {PRONOUN/m_c/object} in the stars.",
            "The life m_c lived led to the stars, inevitably.",
            "m_c joined the ancestors of c_n in the stars, ready to watch over those who lived on.",
            "There was little fuss or debate. m_c's place in the stars was assured.",
            "At the close of m_c's life, a new star burned in the night sky and a new spirit padded in StarClan.",
            "Welcomed into StarClan, m_c took {PRONOUN/m_c/poss} place among the ancestors of the Clans.",
            "m_c's spirits was bathed in starlight, gently cradled away from the struggles of the living and into the resting place of the spirits.",
            "StarClan leapt to offer m_c a place among them.",
            "After a lifetime of service, m_c was welcomed into StarClan for the rest {PRONOUN/m_c/poss} soul needs.",
        ]
        starclan_rejected_text = [
            "No matter how far m_c chased the light, all {PRONOUN/m_c/subject} found was darkness.",
            "m_c knew where {PRONOUN/m_c/subject} {VERB/m_c/were/was} headed when {PRONOUN/m_c/poss} eyes closed for the final time, yet the darkness still frightened {PRONOUN/m_c/object}.",
            "m_c wonders if {PRONOUN/m_c/subject}'ll see {PRONOUN/m_c/poss} kin again as {PRONOUN/m_c/subject} {VERB/m_c/wake/wakes} in the Dark Forest, pondering if {PRONOUN/m_c/subject}{VERB/m_c/'re/'s} the only one there.",
            "StarClan turned their nose up regarding m_c. They had no desire to allow {PRONOUN/m_c/object} into their ranks.",
            "StarClan knew where m_c's morality lies. {PRONOUN/m_c/subject/CAP} {VERB/m_c/do/does} not belong among the stars.",
        ]
        starclan_contentious_text = [
            "m_c was untrusting of the stars, but quickly learned to accept {PRONOUN/m_c/poss} hesitant welcoming.",
            "As m_c approached the stars in skepticism, the stars were just as wary, though they did not refuse {PRONOUN/m_c/object}.",
            "Though m_c was accepted among the stars, {PRONOUN/m_c/subject} soon found that the judgement of their ancestors is hard to bear.",
            "Despite some very passionate protests, m_c is accepted into StarClan."
        ]
        starclan_kit_text = [
            "m_c was guided into StarClan, where the life denied to {PRONOUN/m_c/object} by the real world can be played out in paradise as much as possible.",
            "m_c's life was too short. It's not fair, but StarClan will make up for the lack as much as they can.",
            "StarClan will shelter m_c, and {PRONOUN/m_c/subject} will see {PRONOUN/m_c/poss} family again one day.",
            "StarClan welcomed m_c not with debate, but with the sorrow of a life taken before it could fully flower.",
            "m_c will never grow old in the real world, but in the fields of StarClan {PRONOUN/m_c/subject} can act out the shadows of who {PRONOUN/m_c/subject} could have been.",
            "StarClan welcomed m_c, though they did not want to welcome {PRONOUN/m_c/object} so soon.",
            "The stars reassured m_c that {PRONOUN/m_c/subject} will be cared for.",
            "m_c had no deeds to note, no legacy to leave behind, but StarClan welcomed {PRONOUN/m_c/object} to their ranks.",
        ]

        dark_forest_default_text = [
            "Power and authority, confidence and excitement - it called to m_c, pulled {PRONOUN/m_c/object} like magnets in {PRONOUN/m_c/poss} blood. Now {PRONOUN/m_c/subject} {VERB/m_c/walk/walks} the dark forest, raising {PRONOUN/m_c/poss} voice to call to others in turn.",
            "m_c's spirit lies in the endless solitude of the deep woods, {PRONOUN/m_c/poss} soul watching the stars in envy.",
            "The shadows of the deeps woods hide nothing from m_c, who stepped down the path to the dark forest with eyes open and tail held high.",
            "m_c's spirit waked in the dark forest upon death.",
            "The gnarled branches, the thick silence, the shadowed murk - it suits m_c far better than starlight ever could.",
            "m_c slipped into the dark forest the way a stream joined a river, seamlessly and completely.",
            "The stories told, the legacy made, the legend they left behind - all of that matters to m_c far more than the dark forest that greets {PRONOUN/m_c/poss} spirit at death.",
            "The earthly loam of the forest floor filled m_c's nose upon waking. Even before opening {PRONOUN/m_c/poss} eyes, {PRONOUN/m_c/subject} knew where {PRONOUN/m_c/poss} affinity has led {PRONOUN/m_c/poss} soul.",
        ]
        dark_forest_rejected_text = [
            "m_c was not worth investing in. The dark forest turned away from {PRONOUN/m_c/poss} spirit, leaving the weakling to be scavenged by StarClan.",
            "Power and authority, confidence and excitement - none of that came to mind when presented with m_c. Better for the stars to take the leftovers that the forest does not value.",
            "m_c's spirit slipped from the grasping claws of the dark forest, rising to StarClan.",
            "There was nothing in the dark forest that could tempt m_c, and {PRONOUN/m_c/subject} became a star instead.",
            "There is worth in scorn, and m_c was proud to be rejected by these ancestors. {PRONOUN/m_c/poss/CAP} path lies in starlight, not darkness.",
            "As the life of the living ends, the life of the next world begins - and m_c began {PRONOUN/m_c/inposs} by fleeing, escaping the forest to rise in starlight.",
            "Not all see the value in the strength of the deep woods. It is difficult to say - did m_c escape to StarClan, or did the forest let {PRONOUN/m_c/object} go?",
            "If the denizens of the dark forest catch m_c, they will kill {PRONOUN/m_c/object}. But first, they have to catch {PRONOUN/m_c/object} - and m_c has already escaped to the stars.",
        ]
        dark_forest_contentious_text = [
            "The forest's souls whisper with uncertainty, like wind brushing gently through branches. But m_c is welcomed into the deep woods nonetheless.",
            "m_c's spirit twangs, a note out of tune with the whole. Yet in such a silent world as is held in the deep worlds, there is room for such spirits.",
            "Though there is the quiver of uncertainty in their soul, exposed and easy to see, m_c still covets what the forest offers, and steps into its depths.",
            "There is something in m_c worth the trouble {PRONOUN/m_c/poss} spirit is sure to bring with {PRONOUN/m_c/object}. {PRONOUN/m_c/subject/CAP} {VERB/m_c/are/is} welcomed into the dark forest.",
            "The dark forest called to m_c. Not overwhelmingly, not drowning out all others - but it called nonetheless, and m_c's spirit answered.",
            "The path to the dark forest is imprinted with the pawprints of m_c's good intentions.",
        ]
        dark_forest_kit_text = [
            "m_c followed the well-worn paths into the darkened woods around {PRONOUN/m_c/object} without question.",
            "m_c reached a shadowed hollow, still and quiet. {PRONOUN/m_c/subject/CAP} hadn't seen any cat, and didn't know how {PRONOUN/m_c/subject} got so far from camp.",
            "The wind rustled through the trees, shadowed tangled on the ground, and m_c stepped into an afterlife peaceful, still, and quiet.",
            "This new world is damp and dark, but not unwelcoming to m_c.",
            "m_c wanders the dark forest, a little confused, but mostly curious.",
        ]

        if afterlife == "starclan":
            if is_kit:
                self.afterlife_acceptance = random.choice(starclan_kit_text)
            elif contentious:
                self.afterlife_acceptance = random.choice(starclan_contentious_text)
            elif rejected:
                self.afterlife_acceptance = random.choice(starclan_rejected_text)
            else:
                self.afterlife_acceptance = random.choice(starclan_default_text)
        elif afterlife == "dark_forest":
            if is_kit:
                self.afterlife_acceptance = random.choice(dark_forest_kit_text)
            elif contentious:
                self.afterlife_acceptance = random.choice(dark_forest_contentious_text)
            elif rejected:
                self.afterlife_acceptance = random.choice(dark_forest_rejected_text)
            else:
                self.afterlife_acceptance = random.choice(dark_forest_default_text)

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

    def add_murder(self, murderer_id, victim):
        """
        This adds murder info for both the murderer and the victim. This should be called from the murderer's history
        object.
        :param victim: cat object for the victim
        :param murderer_id: murderer's cat ID
        """
        if not game.clan:
            return
        if "is_murderer" not in self.murder:
            self.murder["is_murderer"] = []
        if "is_victim" not in victim.history.murder:
            victim.history.murder["is_victim"] = []
        else:
            print(
                f"WARNING: victim cat: {victim.ID} already has a murder history - as the victim!"
            )

        self.murder["is_murderer"].append(
            {
                "victim": victim.ID,
                "moon": game.clan.age,
                "revealed": {"to_clan": False, "aware_individuals": []},
            }
        )

        victim.history.murder["is_victim"].append(
            {
                "murderer": murderer_id,
                "revealed": {"to_clan": False, "aware_individuals": []},
                "moon": game.clan.age,
            }
        )

    def reveal_murder(
        self,
        victim,
        murderer_id,
        clan_reveal: bool = False,
        aware_individuals: list = None,
    ):
        """
        This adds reveal information to both the murderer and victim's history. This should be called from the murderer's history.
        :param victim: cat object for the victim
        :param clan_reveal: set to True if the whole Clan now knows about the murder
        :param aware_individuals: if only individual cats are learning about the murder, give a list of their cat objects
        """
        if aware_individuals is None:
            aware_individuals = []

        for murder in self.murder["is_murderer"]:
            if murder["victim"] == victim.ID:
                if clan_reveal:
                    murder["revealed"]["to_clan"] = True
                else:
                    murder["revealed"]["aware_individuals"].extend(aware_individuals)

        for murder in victim.history.murder["is_victim"]:
            if murder["murderer"] == murderer_id:
                if clan_reveal:
                    murder["revealed"]["to_clan"] = True
                else:
                    murder["revealed"]["aware_individuals"].extend(aware_individuals)

    @staticmethod
    def get_murder_status_text(murder: dict, Cat) -> str:
        """
        Returns the complete murder reveal status text for this cat.
        :param murder: the murder history to pull status text from
        :param Cat: cat object
        """
        text = ""
        if murder["revealed"]["to_clan"]:
            return i18n.t("cat.history.murder_revealed_to_clan")
        if murder["revealed"]["aware_individuals"]:
            individuals = [
                Cat.fetch_cat(c).name for c in murder["revealed"]["aware_individuals"]
            ]
            names = adjust_list_text(individuals)
            text = f"{i18n.t('cat.history.murder_revealed_to_individual', name=names)} "

        text += i18n.t("cat.history.murder_not_revealed_to_clan")
        return text

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
            self.cat.generate_lead_ceremony()
        return str(self.lead_ceremony)

    def get_possible_history(self, condition=None):
        """
        Returns the requested death/scars dict, example of single event structure:

        {
        "involved": ID
        "death_text": text
        "scar_text": text
        },

        example of multi event structure:

        {
        "condition name": {
            "involved": ID
            "death_text": text
            "scar_text": text
            },
        "condition name": {
            "involved": ID
            "death_text": text
            "scar_text": text
            },
        },

        if possible scar/death is empty, a NoneType is returned
        :param condition: which condition that caused the death/scar, default None
        """

        if condition in self.possible_history:
            return self.possible_history[condition]
        elif condition:
            return None
        else:
            return self.possible_history

    def get_death_or_scars(self, death=False, scar=False):
        """
        This returns the death/scar history list for the cat.  example of list structure:

        [
            {
                'involved': ID,
                'text': text,
                "moon": moon
            },
            {
                'involved': ID,
                "text": text,
                "moon": moon
            }
            ]

        if scar/death is empty, a NoneType is returned
        :param death: request a death, default False
        :param scar: request scars, default False
        """

        if not death and not scar:
            print(
                "WARNING: event type was not specified during scar/death history retrieval, "
                "did you remember to set scar or death as True?"
            )
        elif scar:
            return self.scar_events
        elif death:
            return self.died_by
