from random import choice
import i18n

from scripts.cat.skills import SkillPath
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import leader_ceremony_text_adjust


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
                    },
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
                            choice(facet_influence_text[_fac + "_raise"])
                        )
                    elif self.mentor_influence["trait"][_ment][_fac] < 0:
                        self.mentor_influence["trait"][_ment]["strings"].append(
                            choice(facet_influence_text[_fac + "_lower"])
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
                            choice(skill_influence_text[SkillPath[_path]])
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
                if self.cat.status == "leader":
                    death_text = f"died from an injury or illness ({condition})"
                else:
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

        for murder in murder_history:
            if murder["victim"] == victim.ID:
                murder_index = murder_history.index(murder)
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

    def generate_lead_ceremony(self):
        """Create a leader ceremony and add it to the history"""

        # determine which dict we're pulling from
        if game.clan.instructor.df:
            starclan = False
            ceremony_dict = LEAD_CEREMONY_DF
        else:
            starclan = True
            ceremony_dict = LEAD_CEREMONY_SC

        # ---------------------------------------------------------------------------- #
        #                                    INTRO                                     #
        # ---------------------------------------------------------------------------- #
        all_intros = ceremony_dict["intros"]

        # filter the intros
        possible_intros = []
        for intro in all_intros:
            tags = all_intros[intro]["tags"]

            if game.clan.age != 0 and "new_clan" in tags:
                continue
            elif game.clan.age == 0 and "new_clan" not in tags:
                continue

            if (
                all_intros[intro]["lead_trait"]
                and self.cat.personality.trait not in all_intros[intro]["lead_trait"]
            ):
                continue
            possible_intros.append(all_intros[intro])

        if chosen_intro := choice(possible_intros):
            intro = choice(chosen_intro["text"])
            intro = leader_ceremony_text_adjust(
                type(self.cat),
                intro,
                self.cat,
            )
        else:
            intro = "this should not appear"

        # ---------------------------------------------------------------------------- #
        #                                 LIFE GIVING                                  #
        # ---------------------------------------------------------------------------- #
        life_givers = []
        dead_relations = []
        life_giving_leader = None

        # grab life givers that the cat actually knew in life and sort by amount of relationship!
        relationships = self.cat.relationships.values()

        for rel in relationships:
            kitty = self.cat.fetch_cat(rel.cat_to)
            if kitty and kitty.dead and kitty.status != "newborn":
                # check where they reside
                if starclan:
                    if kitty.ID not in game.clan.starclan_cats:
                        continue
                else:
                    if kitty.ID not in game.clan.darkforest_cats:
                        continue
                # guides aren't allowed here
                if kitty == game.clan.instructor:
                    continue
                else:
                    dead_relations.append(rel)

        # sort relations by the strength of their relationship
        dead_relations.sort(
            key=(
                lambda rel: rel.romantic_love
                + rel.platonic_like
                + rel.admiration
                + rel.comfortable
                + rel.trust
            ),
            reverse=True,
        )

        # if we have relations, then make sure we only take the top 8
        if dead_relations:
            i = 0
            for rel in dead_relations:
                if i == 8:
                    break
                if rel.cat_to.status == "leader":
                    life_giving_leader = rel.cat_to
                    continue
                life_givers.append(rel.cat_to.ID)
                i += 1
        # check amount of life givers, if we need more, then grab from the other dead cats
        if len(life_givers) < 8:
            amount = 8 - len(life_givers)

            if starclan:
                # this part just checks how many SC cats are available, if there aren't enough to fill all the slots,
                # then we just take however many are available

                possible_sc_cats = [
                    i
                    for i in game.clan.starclan_cats
                    if self.cat.fetch_cat(i)
                    and i not in life_givers
                    and self.cat.fetch_cat(i).status not in ("leader", "newborn")
                ]

                if len(possible_sc_cats) - 1 < amount:
                    extra_givers = possible_sc_cats
                else:
                    extra_givers = sample(possible_sc_cats, k=amount)
            else:
                possible_df_cats = [
                    i
                    for i in game.clan.darkforest_cats
                    if self.cat.fetch_cat(i)
                    and i not in life_givers
                    and self.cat.fetch_cat(i).status not in ("leader", "newborn")
                ]
                if len(possible_df_cats) - 1 < amount:
                    extra_givers = possible_df_cats
                else:
                    extra_givers = sample(possible_df_cats, k=amount)

            life_givers.extend(extra_givers)

        # making sure we have a leader at the end
        ancient_leader = False
        if not life_giving_leader:
            # choosing if the life giving leader will be the oldest leader or previous leader
            coin_flip = randint(1, 2)
            if coin_flip == 1:
                # pick the oldest leader in SC
                ancient_leader = True
                if starclan:
                    sc_cats = game.clan.starclan_cats.copy()
                    sc_cats.sort(key=lambda x: -1 * int(self.cat.fetch_cat(x).dead_for))
                    for kitty in sc_cats:
                        if (
                            self.cat.fetch_cat(kitty)
                            and self.cat.fetch_cat(kitty).status == "leader"
                        ):
                            life_giving_leader = kitty
                            break
                else:
                    df_kitties = game.clan.darkforest_cats.copy()
                    df_kitties.sort(
                        key=lambda x: -1 * int(self.cat.fetch_cat(x).dead_for)
                    )
                    for kitty in df_kitties:
                        if (
                            self.cat.fetch_cat(kitty)
                            and self.cat.fetch_cat(kitty).status == "leader"
                        ):
                            life_giving_leader = kitty
                            break
            else:
                # pick previous leader
                if starclan:
                    sc_cats = game.clan.starclan_cats.copy()
                    sc_cats.sort(key=lambda x: int(self.cat.fetch_cat(x).dead_for))
                    for kitty in sc_cats:
                        if (
                            self.cat.fetch_cat(kitty)
                            and self.cat.fetch_cat(kitty).status == "leader"
                        ):
                            life_giving_leader = kitty
                            break
                else:
                    df_kitties = game.clan.darkforest_cats.copy()
                    df_kitties.sort(key=lambda x: int(self.cat.fetch_cat(x).dead_for))
                    for kitty in df_kitties:
                        if (
                            self.cat.fetch_cat(kitty)
                            and self.cat.fetch_cat(kitty).status == "leader"
                        ):
                            life_giving_leader = kitty
                            break

        if life_giving_leader:
            life_givers.append(life_giving_leader)

        # check amount again, if more are needed then we'll add the ghost-y cats at the end
        if len(life_givers) < 9:
            unknown_blessing = True
        else:
            unknown_blessing = False
        extra_lives = str(9 - len(life_givers))
        possible_lives = ceremony_dict["lives"]
        lives = []
        used_lives = []
        used_virtues = []
        for giver in life_givers:
            giver_cat = self.cat.fetch_cat(giver)
            if not giver_cat:
                continue
            life_list = []
            for life in possible_lives:
                tags = possible_lives[life]["tags"]
                rank = giver_cat.status

                if "unknown_blessing" in tags:
                    continue

                if "guide" in tags and giver_cat != game.clan.instructor:
                    continue
                if game.clan.age != 0 and "new_clan" in tags:
                    continue
                elif game.clan.age == 0 and "new_clan" not in tags:
                    continue
                if "old_leader" in tags and not ancient_leader:
                    continue
                if (
                    "leader_parent" in tags
                    and giver_cat.ID not in self.cat.get_parents()
                ):
                    continue
                elif (
                    "leader_child" in tags
                    and giver_cat.ID not in self.cat.get_children()
                ):
                    continue
                elif (
                    "leader_sibling" in tags
                    and giver_cat.ID not in self.cat.get_siblings()
                ):
                    continue
                elif "leader_mate" in tags and giver_cat.ID not in self.cat.mate:
                    continue
                elif (
                    "leader_former_mate" in tags
                    and giver_cat.ID not in self.cat.previous_mates
                ):
                    continue
                if (
                    "leader_mentor" in tags
                    and giver_cat.ID not in self.cat.former_mentor
                ):
                    continue
                if (
                    "leader_apprentice" in tags
                    and giver_cat.ID not in self.cat.former_apprentices
                ):
                    continue
                if (
                    possible_lives[life]["rank"]
                    and rank not in possible_lives[life]["rank"]
                ):
                    continue
                if (
                    possible_lives[life]["lead_trait"]
                    and self.cat.personality.trait
                    not in possible_lives[life]["lead_trait"]
                ):
                    continue
                if possible_lives[life]["star_trait"] and (
                    giver_cat.personality.trait
                    not in possible_lives[life]["star_trait"]
                ):
                    continue
                life_list.extend(list(possible_lives[life]["life_giving"]))

            i = 0
            chosen_life = {}
            while i < 10:
                attempted = []
                if life_list:
                    chosen_life = choice(life_list)
                    if chosen_life not in used_lives and chosen_life not in attempted:
                        break
                    attempted.append(chosen_life)
                    i += 1
                else:
                    print(
                        f"WARNING: life list had no items for giver #{giver_cat.ID}. Using default life. "
                        f"If you are a beta tester, please report and ping scribble along with "
                        f"all the info you can about the giver cat mentioned in this warning."
                    )
                    chosen_life = ceremony_dict["default_life"]
                    break

            used_lives.append(chosen_life)
            if "virtue" in chosen_life:
                poss_virtues = [
                    i for i in chosen_life["virtue"] if i not in used_virtues
                ] or ["faith", "friendship", "love", "strength"]
                virtue = choice(poss_virtues)
                used_virtues.append(virtue)
            else:
                virtue = None

            lives.append(
                leader_ceremony_text_adjust(
                    type(self.cat),
                    chosen_life["text"],
                    leader=self.cat,
                    life_giver=giver,
                    virtue=virtue,
                )
            )
        if unknown_blessing:
            possible_blessing = []
            for life in possible_lives:
                tags = possible_lives[life]["tags"]

                if "unknown_blessing" not in tags:
                    continue

                if (
                    possible_lives[life]["lead_trait"]
                    and self.cat.personality.trait
                    not in possible_lives[life]["lead_trait"]
                ):
                    continue
                possible_blessing.append(possible_lives[life])
            chosen_blessing = choice(possible_blessing)
            chosen_text = choice(chosen_blessing["life_giving"])
            lives.append(
                leader_ceremony_text_adjust(
                    type(self.cat),
                    chosen_text["text"],
                    leader=self.cat,
                    virtue=chosen_text["virtue"],
                    extra_lives=extra_lives,
                )
            )
        all_lives = "<br><br>".join(lives)

        # ---------------------------------------------------------------------------- #
        #                                    OUTRO                                     #
        # ---------------------------------------------------------------------------- #

        # get the outro
        all_outros = ceremony_dict["outros"]

        possible_outros = []
        for outro in all_outros:
            tags = all_outros[outro]["tags"]

            if game.clan.age != 0 and "new_clan" in tags:
                continue
            elif game.clan.age == 0 and "new_clan" not in tags:
                continue

            if (
                all_outros[outro]["lead_trait"]
                and self.cat.personality.trait not in all_outros[outro]["lead_trait"]
            ):
                continue
            possible_outros.append(all_outros[outro])

        chosen_outro = choice(possible_outros)

        if chosen_outro:
            if life_givers:
                giver = life_givers[-1]
            else:
                giver = None
            outro = choice(chosen_outro["text"])
            outro = leader_ceremony_text_adjust(
                type(self.cat),
                outro,
                leader=self.cat,
                life_giver=giver,
            )
        else:
            outro = "this should not appear"

        full_ceremony = "<br><br>".join([intro, all_lives, outro])
        return full_ceremony


## Loading for ceremonies

LEAD_CEREMONY_SC: dict = None
LEAD_CEREMONY_DF: dict = None
lead_ceremony_lang: str = None

if lead_ceremony_lang != i18n.config.get("locale"):
    LEAD_CEREMONY_SC = load_lang_resource("events/lead_ceremony_sc.json")
    LEAD_CEREMONY_DF = load_lang_resource("events/lead_ceremony_df.json")
    lead_ceremony_lang = i18n.config.get("locale")
