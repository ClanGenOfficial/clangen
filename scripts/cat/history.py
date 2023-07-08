import random

from scripts.game_structure.game_essentials import game
from scripts.cat.skills import SkillPath


class History:
    """
    this class handles the cat's history!
    """
    def __init__(self,
                 beginning=None,
                 mentor_influence=None,
                 app_ceremony=None,
                 lead_ceremony=None,
                 possible_history=None,
                 died_by=None,
                 scar_events=None,
                 murder=None
                 ):
        self.beginning = beginning if beginning else {}
        self.mentor_influence = mentor_influence if mentor_influence else {"trait": {}, "skill": {}}
        self.app_ceremony = app_ceremony if app_ceremony else {}
        self.lead_ceremony = lead_ceremony if lead_ceremony else None
        self.possible_history = possible_history if possible_history else {}
        self.died_by = died_by if died_by else []
        self.scar_events = scar_events if scar_events else []
        self.murder = murder if murder else {}

        # fix 'old' history save bugs
        if type(self.mentor_influence["trait"]) is type(None):
            self.mentor_influence["trait"] = {}
        if type(self.mentor_influence["skill"]) is type(None):
            self.mentor_influence["skill"] = {}
        if "mentor" in self.mentor_influence:
            del self.mentor_influence["mentor"]

        """ 
        want save to look like
        {
        "beginning":{
            "clan_born": bool,
            "birth_season": season,
            "age": age,
            "moon": moon
            },
        "mentor_influence":{
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
                    "revealed": bool,
                    "moon": moon
                    },
                ]
            "is_victim": [
                    {
                    "murderer": ID,
                    "revealed": bool,
                    "text": same text as the death history for this murder (revealed history)
                    "unrevealed_text": unrevealed death history
                    "moon": moon
                    },
                ]
            }
        }
        """

    # ---------------------------------------------------------------------------- #
    #                                   utility                                    #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def check_load(cat):
        """
        this checks if the cat's history has been loaded and loads it if False
        :param cat: cat object
        :return:
        """
        if not cat.history:
            cat.load_history()

    @staticmethod
    def make_dict(cat):
        history_dict = {
            "beginning": cat.history.beginning,
            "mentor_influence": cat.history.mentor_influence,
            "app_ceremony": cat.history.app_ceremony,
            "lead_ceremony": cat.history.lead_ceremony,
            "possible_history": cat.history.possible_history,
            "died_by": cat.history.died_by,
            "scar_events": cat.history.scar_events,
            "murder": cat.history.murder,
        }
        return history_dict

    # ---------------------------------------------------------------------------- #
    #                            adding and removing                               #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def add_beginning(cat, clan_born=False):
        """
        adds joining age and moon info to the cat's history save
        :param cat: cat object
        """
        if not game.clan:
            return
        History.check_load(cat)

        cat.history.beginning = {
            "clan_born": clan_born,
            "birth_season": game.clan.current_season if clan_born else None,
            "age": cat.moons,
            "moon": game.clan.age
        }

    @staticmethod
    def add_mentor_facet_influence_strings(cat):
        """
        adds mentor influence to the cat's history save
        :param cat: cat object
        """
        History.check_load(cat)
        
        if not cat.history.mentor_influence["trait"]:
            return
        
        if ("Benevolent" or "Abrasive" or "Reserved" or "Outgoing") in cat.history.mentor_influence["trait"]:
            cat.history.mentor_influence["trait"] = None
            return

        # working under the impression that these blurbs will be preceeded by "more likely to"
        facet_influence_text = {
                "lawfulness_raise": [
                    "follow rules", "follow the status quo", "heed their inner compass", "have strong inner morals"
                ],
                "lawfulness_lower": [
                    "bend the rules", "break away from the status quo", "break rules that don't suit them", "make their own rules"
                ],
                "sociability_raise": [
                    "be friendly towards others", "step out of their comfort zone", "interact with others", "put others at ease"
                ],
                "sociability_lower": [
                    "be cold towards others", "refrain from socializing", "bicker with others"
                ],
                "aggression_raise": [
                    "be ready for a fight", "start a fight", "defend their beliefs", "use teeth and claws over words", 
                    "resort to violence"
                ],
                "aggression_lower": [
                    "be slow to anger", "avoid a fight", "use words over teeth and claws", "try to avoid violence"
                ],
                "stability_raise": [
                    "stay collected", "think things through", "be resilient", "have a positive outlook", "be consistent", "adapt easily"
                ],
                "stability_lower": [
                    "behave erratically", "make impulsive decisions", "have trouble adapting", "dwell on things"
                ]
            }
        
        for _ment in cat.history.mentor_influence["trait"]:
            cat.history.mentor_influence["trait"][_ment]["strings"] = []
            for _fac in cat.history.mentor_influence["trait"][_ment]:
                #Check to make sure nothing weird got in there. 
                if _fac in cat.personality.facet_types:
                    if cat.history.mentor_influence["trait"][_ment][_fac] > 0:
                        cat.history.mentor_influence["trait"][_ment]["strings"].append(random.choice(facet_influence_text[_fac + "_raise"]))
                    elif cat.history.mentor_influence["trait"][_ment][_fac] < 0:
                        cat.history.mentor_influence["trait"][_ment]["strings"].append(random.choice(facet_influence_text[_fac + "_lower"]))

    @staticmethod
    def add_mentor_skill_influence_strings(cat):
        """
        adds mentor influence to the cat's history save
        :param cat: cat object
        """
        History.check_load(cat)
        
        if not cat.history.mentor_influence["skill"]:
            return

        # working under the impression that these blurbs will be preceeded by "become better at"
        skill_influence_text = {
                SkillPath.TEACHER: [ "teaching" ],
                SkillPath.HUNTER: [ "hunting" ],
                SkillPath.FIGHTER: [ "fighting" ],
                SkillPath.RUNNER: [ "running" ],
                SkillPath.CLIMBER: [ "climbing" ],
                SkillPath.SWIMMER: [ "swimming" ],
                SkillPath.SPEAKER: [ "arguing" ],
                SkillPath.MEDIATOR: [ "resolving arguments" ],
                SkillPath.CLEVER: [ "solving problems" ],
                SkillPath.INSIGHTFUL: [ "providing insight" ],
                SkillPath.SENSE: [ "noticing small details" ],
                SkillPath.KIT: [ "caring for kittens" ],
                SkillPath.STORY: [ "storytelling" ],
                SkillPath.LORE: [ "remembering lore" ],
                SkillPath.CAMP: [ "caring for camp" ],
                SkillPath.HEALER: [ "healing" ],
                SkillPath.STAR: [ "connecting to starclan" ],
                SkillPath.OMEN: [ "finding omens" ],
                SkillPath.DREAM: [ "understanding dreams" ],
                SkillPath.CLAIRVOYANT: [ "predicting the furture" ],
                SkillPath.PROPHET: [ "understanding prophecies" ],
                SkillPath.GHOST: [ "connecting to the afterlife" ],
            }
        
        for _ment in cat.history.mentor_influence["skill"]:
            cat.history.mentor_influence["skill"][_ment]["strings"] = []
            for _path in cat.history.mentor_influence["skill"][_ment]:
                #Check to make sure nothing weird got in there.
                if _path == "strings":
                    continue
                
                try:
                    if cat.history.mentor_influence["skill"][_ment][_path] > 0:
                        cat.history.mentor_influence["skill"][_ment]["strings"].append(random.choice(skill_influence_text[SkillPath[_path]]))
                except KeyError:
                    print("issue", _path)

    @staticmethod
    def add_facet_mentor_influence(cat, mentor_id, facet, amount):
        """Adds the history information for a single mentor facet change, that occurs after a patrol. """
        
        History.check_load(cat)
        if mentor_id not in cat.history.mentor_influence["trait"]:
            cat.history.mentor_influence["trait"][mentor_id] = {}
        if facet not in cat.history.mentor_influence["trait"][mentor_id]:
            cat.history.mentor_influence["trait"][mentor_id][facet] = 0
        cat.history.mentor_influence["trait"][mentor_id][facet] += amount
    
    @staticmethod
    def add_skill_mentor_influence(cat, mentor_id, path, amount):
        """ Adds mentor influence on skills """
        
        History.check_load(cat)
        
        if not isinstance(path, SkillPath):
            path = SkillPath[path]
        
        if mentor_id not in cat.history.mentor_influence["skill"]:
            cat.history.mentor_influence["skill"][mentor_id] = {}
        if path.name not in cat.history.mentor_influence["skill"][mentor_id]:
            cat.history.mentor_influence["skill"][mentor_id][path.name] = 0
        cat.history.mentor_influence["skill"][mentor_id][path.name] += amount
        
    @staticmethod
    def add_app_ceremony(cat, honor):
        """
        adds ceremony honor to the cat's history
        :param cat: cat object
        :param honor: the honor trait given during the cat's ceremony
        """
        if not game.clan:
            return
        History.check_load(cat)

        cat.history.app_ceremony = {
            "honor": honor,
            "graduation_age": cat.moons,
            "moon": game.clan.age
        }

    @staticmethod
    def add_possible_history(cat, condition:str, death_text:str=None, scar_text:str=None, other_cat=None):
        """
        this adds the possible death/scar to the cat's history
        :param cat: cat object
        :param condition: the condition that is causing the death/scar
        :param death_text: text for death history
        :param scar_text: text for scar history
        :param other_cat: cat object of other cat involved. 
        """
        History.check_load(cat)

        # If the condition already exists, we don't want to overwrite it
        if condition in cat.history.possible_history:
            if death_text is not None:
                cat.history.possible_history[condition]["death_text"] = death_text
            if scar_text is not None:
                cat.history.possible_history[condition]["scar_text"] = scar_text
            if other_cat is not None:
                cat.history.possible_history[condition]["other_cat"] = other_cat.ID
        else:
            # Use a default is none is provided.
            # Will probably sound weird, but it's better than nothing
            if not death_text:
                death_text = f"m_c died from an injury or illness ({condition})."
            if not scar_text:
                scar_text = f"m_c was scarred from an injury or illness ({condition})."
            
            cat.history.possible_history[condition] = {
                "death_text": death_text,
                "scar_text": scar_text,
                "other_cat": other_cat.ID if other_cat is not None else None
            }


    @staticmethod
    def remove_possible_history(cat, condition):
        """
        use to remove possible death/scar histories
        :param cat: cat object
        :param condition: condition linked to the death/scar you're removing
        :param scar: set True if removing scar
        :param death: set True if removing death
        """

        History.check_load(cat)

        if condition in cat.history.possible_history:
            cat.history.possible_history.pop(condition)
    
    @staticmethod
    def add_death(cat, death_text, condition=None, other_cat=None, extra_text=None):
        """ Adds death to cat's history. If a condition is passed, it will look into
            possible_history to see if anything is saved there, and, if so, use the text and 
            other_cat there (overriding the 
            passed death_text and other_cat). """
        
        if not game.clan:
            return
        History.check_load(cat)
        
        if other_cat is not None:
            other_cat = other_cat.ID
        if condition in cat.history.possible_history:
            if cat.history.possible_history[condition]["death_text"]:
                death_text = cat.history.possible_history[condition]["death_text"]
            other_cat = cat.history.possible_history[condition].get("other_cat")
            cat.history.remove_possible_history(cat, condition)
        
        cat.history.died_by.append({
            "involved": other_cat,
            "text": death_text, 
            "moon": game.clan.age
        })
    
    @staticmethod
    def add_scar(cat, scar_text, condition=None, other_cat=None, extra_text=None):
        if not game.clan:
            return
        History.check_load(cat)
        
        if other_cat is not None:
            other_cat = other_cat.ID
        if condition in cat.history.possible_history:
            if cat.history.possible_history[condition]["scar_text"]:
                scar_text = cat.history.possible_history[condition]["scar_text"]
            other_cat = cat.history.possible_history[condition].get("other_cat")
            cat.history.remove_possible_history(cat, condition)
        
        cat.history.scar_events.append({
            "involved": other_cat,
            "text": scar_text, 
            "moon": game.clan.age
        })
    
    @staticmethod
    def add_murders(cat, other_cat, revealed, text=None, unrevealed_text=None):
        """
        this adds murder info
        :param cat: cat object (cat being murdered)
        :param other_cat: cat object (cat doing the murdering)
        :param revealed: True or False depending on if the murderer has been revealed to the player
        :param text: event text for the victim's death (should be same as their death history)
        :param unrevealed_text: unrevealed event text for victim's death (not saved in their death history)
        :return:
        """
        if not game.clan:
            return
        History.check_load(cat)
        History.check_load(other_cat)
        if "is_murderer" not in other_cat.history.murder:
            other_cat.history.murder["is_murderer"] = []
        if 'is_victim' not in cat.history.murder:
            cat.history.murder["is_victim"] = []

        other_cat.history.murder["is_murderer"].append({
            "victim": cat.ID,
            "revealed": revealed,
            "moon": game.clan.age
        })
        cat.history.murder["is_victim"].append({
            "murderer": other_cat.ID,
            "revealed": revealed,
            "text": text,
            "unrevealed_text": unrevealed_text,
            "moon": game.clan.age
        })

    @staticmethod
    def add_lead_ceremony(cat):
        """
        generates and adds lead ceremony to history
        """
        History.check_load(cat)

        cat.history.lead_ceremony = cat.generate_lead_ceremony()

    # ---------------------------------------------------------------------------- #
    #                                 retrieving                                   #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_beginning(cat):
        """
        returns the beginning info, example of structure:

        "beginning":{
            "clan_born": bool,
            "birth_season": season,
            "age": age,
            "moon": moon
            },

        if beginning info is empty, a NoneType is returned
        :param cat: cat object
        """
        History.check_load(cat)
        return cat.history.beginning

    @staticmethod
    def get_mentor_influence(cat):
        """
        Returns mentor influence dict, example of structure:

        "mentor_influence":{
            "mentor": ID
            "skill": skill
            "second_skill": second skill
            "trait": {
                "mentor_id":
                    "lawfulness": 0,
                    ...
                    "strings": []
            },
            "skill": skill
        }

        if mentor influence is empty, a NoneType is returned
        """
        History.check_load(cat)
        return cat.history.mentor_influence

    @staticmethod
    def get_app_ceremony(cat):
        """
        Returns app_ceremony dict, example of structure:

        "app_ceremony": {
            "honor": honor,
            "graduation_age": age,
            "moon": moon
            },

        if app_ceremony is empty, a NoneType is returned
        """
        History.check_load(cat)
        return cat.history.app_ceremony

    @staticmethod
    def get_lead_ceremony(cat):
        """
        returns the leader ceremony text
        :param cat: cat object
        """
        History.check_load(cat)
        if not cat.history.lead_ceremony:
            History.add_lead_ceremony(cat)
        return str(cat.history.lead_ceremony)

    @staticmethod
    def get_possible_history(cat, condition=None):
        """
        Returns the asked for death/scars dict, example of single event structure:

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
        :param cat: cat object
        :param condition: the name of the condition that caused the death/scar (if looking for specific event, else leave None to get all events)
        """
        History.check_load(cat)

        if condition in cat.history.possible_history:
            return cat.history.possible_history[condition]
        elif condition:
            return None
        else:
            return cat.history.possible_history

    @staticmethod
    def get_death_or_scars(cat, death=False, scar=False):
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
        :param cat: cat object
        :param death: set True if you want the deaths
        :param scar: set True if you want the scars
        """

        History.check_load(cat)

        event_type = None
        if scar:
            event_type = "scar_events"
        elif death:
            event_type = "died_by"

        if not event_type:
            print('WARNING: event type was not specified during scar/death history retrieval, '
                  'did you remember to set scar or death as True?')
            return

        if event_type == 'scar_events':
            return cat.history.scar_events
        else:
            return cat.history.died_by

    @staticmethod
    def get_murders(cat):
        """
        this returns the cat's murder dict. example of dict structure:

        "murder": {
            "is_murderer": [
                    {
                    "victim": ID,
                    "revealed": bool,
                    "moon": moon
                    },
                ]
            "is_victim": [
                    {
                    "murderer": ID,
                    "revealed": bool,
                    "text": same text as the death history for this murder (revealed history)
                    "unrevealed_text": unrevealed death history
                    "moon": moon
                    },
                ]
            }

        if murders is empty, a NoneType is returned
        :param cat: cat object
        """

        History.check_load(cat)

        return cat.history.murder

    @staticmethod
    def reveal_murder(cat, other_cat, Cat, victim, murder_index):
        ''' Reveals the murder properly in all of the associated history text
        :param cat: The murderer
        :param other_cat: The cat who discovers the truth about the murder
        :param Cat: The cat class
        :param victim: The victim whose murder is being revealed
        :param murder_index: Index of the murder'''

        victim = Cat.fetch_cat(victim)
        murder_history = History.get_murders(cat)
        victim_history = History.get_murders(victim)

        if murder_history:
            if "is_murderer" in murder_history:
                murder_history = murder_history["is_murderer"][murder_index]
                murder_history["revealed"] = True
                murder_history["revealed_by"] = other_cat.ID
                murder_history["revelation_text"] = "The truth of {PRONOUN/m_c/subject} crime against [victim] was discovered by [discoverer]."

                victim_history = victim_history["is_victim"][0]
                victim_history["revealed"] = True
                victim_history["revealed_by"] = other_cat.ID
                victim_history["revelation_text"] = "The truth of {PRONOUN/m_c/subject} murder was discovered by [discoverer]."

                murder_history["revelation_text"] = murder_history["revelation_text"].replace('[victim]', str(victim.name))
                murder_history["revelation_text"] = murder_history["revelation_text"].replace('[discoverer]', str(other_cat.name))
                victim_history["revelation_text"] = victim_history["revelation_text"].replace('[discoverer]', str(other_cat.name))
