import random

import ujson

from scripts.game_structure.game_essentials import game


class History:
    """
    this class handles the cat's history!
    """
    def __init__(self,
                 beginning=None,
                 mentor_influence=None,
                 app_ceremony=None,
                 lead_ceremony=None,
                 possible_death=None,
                 died_by=None,
                 possible_scar=None,
                 scar_events=None,
                 murder=None
                 ):
        self.beginning = beginning if beginning else {}
        self.mentor_influence = mentor_influence if mentor_influence else {}
        self.app_ceremony = app_ceremony if app_ceremony else {}
        self.lead_ceremony = lead_ceremony if lead_ceremony else None
        self.possible_death = possible_death if possible_death else {}
        self.died_by = died_by if died_by else []
        self.possible_scar = possible_scar if possible_scar else {}
        self.scar_events = scar_events if scar_events else []
        self.murder = murder if murder else {}

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
            "mentor": ID
            "skill": skill
            "trait": trait
            },
        "app_ceremony": {
            "honor": honor,
            "graduation_age": age,
            "moon": moon
            },
        "lead_ceremony": full ceremony text,
        "possible_death": {
            "condition name": {
                "involved": ID
                "text": text
                },
            "condition name": {
                "involved": ID
                "text": text
                },
            },
        "died_by": [
            {
                "involved": ID,
                "text": text,
                "moon": moon
            }
            ],
        "possible_scar": {
            "condition name": {
                "involved": ID
                "text": text
                },
            "condition name": {
                "involved": ID
                "text": text
                },
            },
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
            "possible_death": cat.history.possible_death,
            "died_by": cat.history.died_by,
            "possible_scar": cat.history.possible_scar,
            "scar_events": cat.history.scar_events,
            "murder": cat.history.murder,
        }
        return history_dict

    # ---------------------------------------------------------------------------- #
    #                            adding and removing                               #
    # ---------------------------------------------------------------------------- #

    def add_beginning(self, cat, clan_born=False):
        """
        adds joining age and moon info to the cat's history save
        :param cat: cat object
        """
        if not game.clan:
            return
        self.check_load(cat)

        cat.history.beginning = {
            "clan_born": clan_born,
            "birth_season": game.clan.current_season if clan_born else None,
            "age": cat.moons,
            "moon": game.clan.age
        }

    def add_mentor_influence(self, cat, mentor, skill, trait):
        """
        adds mentor influence to the cat's history save
        :param cat: cat object
        :param mentor: the ID of the mentor who influenced the cat
        :param skill: the skill that was given by the mentor
        :param trait: the personality group given by the mentor
        """
        self.check_load(cat)

        if mentor:
            mentor = mentor.ID
            cat.history.mentor_influence["mentor"] = mentor if mentor else None
        if skill:
            cat.history.mentor_influence["skill"] = skill if skill else None
        if trait:
            cat.history.mentor_influence["trait"] = trait if trait else None

        if "mentor" not in cat.history.mentor_influence:
            cat.history.mentor_influence["mentor"] = None
        if "skill" not in cat.history.mentor_influence:
            cat.history.mentor_influence["skill"] = None
        if "trait" not in cat.history.mentor_influence:
            cat.history.mentor_influence["trait"] = None

    def add_app_ceremony(self, cat, honor):
        """
        adds ceremony honor to the cat's history
        :param cat: cat object
        :param honor: the honor trait given during the cat's ceremony
        """
        if not game.clan:
            return
        self.check_load(cat)

        cat.history.app_ceremony = {
            "honor": honor,
            "graduation_age": cat.moons,
            "moon": game.clan.age
        }

    def add_possible_death_or_scars(self, cat, condition, text, other_cat=None, scar=False, death=False):
        """
        this adds the possible death/scar to the cat's history
        :param cat: cat object
        :param other_cat: if another cat is mentioned in the history, include them here
        :param condition: the condition that is causing the death/scar
        :param text: the history text for the death/scar
        :param scar: set to True if this is a scar event
        :param death: set to True if this is a death event
        """
        self.check_load(cat)

        event_type = None
        if scar:
            event_type = "possible_scar"
        elif death:
            event_type = "possible_death"

        if not event_type:
            print('WARNING: event type was not specified during possible scar/death history writing, '
                  'did you remember to set scar or death as True?')
            return

        # now just make sure the names aren't actually in the text and replace as necessary
        # we can't have the names in the text bc names change over time and so would eventually be out of date
        # on the history display
        if str(cat.name) in text:
            text = text.replace(str(cat.name), "m_c")
        if other_cat:
            if str(other_cat.name) in text:
                text = text.replace(str(other_cat.name), "r_c")

        if event_type == "possible_scar":
            cat.history.possible_scar[condition] = {
                "involved": other_cat.ID if other_cat else None,
                "text": text
            }
        elif event_type == 'possible_death':
            cat.history.possible_death[condition] = {
                "involved": other_cat.ID if other_cat else None,
                "text": text
            }

    def remove_possible_death_or_scars(self, cat, condition):
        """
        use to remove possible death/scar histories
        :param cat: cat object
        :param condition: condition linked to the death/scar you're removing
        :param scar: set True if removing scar
        :param death: set True if removing death
        """

        self.check_load(cat)

        if condition in cat.history.possible_scar:
            cat.history.possible_scar.pop(condition)
        if condition in cat.history.possible_death:
            cat.history.possible_death.pop(condition)

    def add_death_or_scars(self, cat, other_cat=None, text=None, extra_text=None, condition=None, scar=False, death=False):
        """
        this adds death or scar events to the cat's history, if the condition
         was already in possible death/scars then it's info is moved to this list
         and removed from the old dict
        :param cat: cat object
        :param other_cat: if another cat is involved in the event, add them here
        :param text: event history text
        :param extra_text: the second event string if one exists, this is for use with the murder reveal system
        :param condition: if it was caused by a condition, add name here
        :param scar: set True if scar
        :param death: set True if death
        """
        if not game.clan:
            return
        self.check_load(cat)

        event_type = None
        old_event_type = None
        other_cat_ID = None
        if scar:
            event_type = "scar_events"
            old_event_type = "possible_scar"
        elif death:
            event_type = "died_by"
            old_event_type = "possible_death"

        if not event_type or not old_event_type:
            print('WARNING: event type was not specified during scar/death history writing, '
                  'did you remember to set scar or death as True?')
            return

        # if this was caused by a condition, then we need to get info from the possible scar/death dicts
        if condition:
            try:
                if old_event_type == 'possible_scar':
                    old_event = cat.history.possible_scar
                else:
                    old_event = cat.history.possible_death
                other_cat_ID = old_event[condition]["involved"]
                text = old_event[condition]["text"]
                # and then remove from possible scar/death dict
                if condition in old_event:
                    old_event.pop(condition)
            except KeyError:
                print(f"WARNING: could not find {condition} in cat's possible death/scar history,"
                      f" this maybe be due to an expected save conversion change.")
                return

        # now just make sure the names aren't actually in the text and replace as necessary
        # we can't have the names in the text bc names change over time and so would eventually be out of date
        # on the history display
        if str(cat.name) in text:
            text = text.replace(str(cat.name), "m_c")
        if other_cat:
            if str(other_cat.name) in text:
                text = text.replace(str(other_cat.name), "r_c")
            other_cat_ID = other_cat.ID

        history_dict = {
            "involved": other_cat_ID,
            "text": text,
            "moon": game.clan.age
        }

        if event_type == 'scar_events':
            cat.history.scar_events.append(history_dict)
        elif event_type == 'died_by':
            cat.history.died_by.append(history_dict)

    def add_murders(self, cat, other_cat, revealed, text=None, unrevealed_text=None):
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
        self.check_load(cat)
        self.check_load(other_cat)
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

    def add_lead_ceremony(self, cat):
        """
        generates and adds lead ceremony to history
        """
        self.check_load(cat)

        cat.history.lead_ceremony = cat.generate_lead_ceremony()

    # ---------------------------------------------------------------------------- #
    #                                 retrieving                                   #
    # ---------------------------------------------------------------------------- #

    def get_beginning(self, cat):
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
        self.check_load(cat)
        return cat.history.beginning

    def get_mentor_influence(self, cat):
        """
        Returns mentor influence dict, example of structure:

        "mentor_influence":{
            "mentor": ID
            "skill": skill
            "trait": trait
            },

        if mentor influence is empty, a NoneType is returned
        """
        self.check_load(cat)
        return cat.history.mentor_influence

    def get_app_ceremony(self, cat):
        """
        Returns app_ceremony dict, example of structure:

        "app_ceremony": {
            "honor": honor,
            "graduation_age": age,
            "moon": moon
            },

        if app_ceremony is empty, a NoneType is returned
        """
        self.check_load(cat)
        return cat.history.app_ceremony

    def get_lead_ceremony(self, cat):
        """
        returns the leader ceremony text
        :param cat: cat object
        """
        self.check_load(cat)
        if not cat.history.lead_ceremony:
            self.add_lead_ceremony(cat)
        return str(cat.history.lead_ceremony)

    def get_possible_death_or_scars(self, cat, condition=None, death=False, scar=False):
        """
        Returns the asked for death/scars dict, example of single event structure:

        {
        "involved": ID
        "text": text
        },

        example of multi event structure:

        {
        "condition name": {
            "involved": ID
            "text": text
            },
        "condition name": {
            "involved": ID
            "text": text
            },
        },

        if possible scar/death is empty, a NoneType is returned
        :param cat: cat object
        :param condition: the name of the condition that caused the death/scar (if looking for specific event, else leave None to get all events)
        :param death: set True to get deaths
        :param scar: set True to get scars
        """
        self.check_load(cat)

        event_type = None
        if scar:
            event_type = "possible_scar"
        elif death:
            event_type = "possible_death"

        if not event_type:
            print('WARNING: event type was not specified during possible scar/death history retrieval, '
                  'did you remember to set scar or death as True?')
            return

        if condition:
            if event_type == 'possible_scar':
                if condition in cat.history.possible_scar:
                    return cat.history.possible_scar[condition]
            elif event_type == 'possible_death':
                if condition in cat.history.possible_death:
                    return cat.history.possible_death[condition]
            else:
                return None

        if event_type == 'possible_scar':
            return cat.history.possible_scar
        else:
            return cat.history.possible_death

    def get_death_or_scars(self, cat, death=False, scar=False):
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

        self.check_load(cat)

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

    def get_murders(self, cat):
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

        self.check_load(cat)

        return cat.history.murder



