import random

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled
from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                              Scar Event Class                                #
# ---------------------------------------------------------------------------- #

class Scar_Events():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.history = History()
        self.event_sums = 0
        self.had_one_event = False

    def handle_scars(self, cat, injury_name):
        """ 
        This function handles the scars
        """
    
        
        chance = max(int(8 - cat.injuries[injury_name]["moons_with"]), 1)
        if cat.injuries[injury_name]["severity"] == "minor":
            chance += 8
        
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            chance += 3
        if len(cat.pelt.scars) < 4 and not int(random.random() * chance):

            # move potential scar text into displayed scar text
            self.history.add_scar(cat,
                                  f"m_c was scarred from an injury ({injury_name}).",
                                  condition=injury_name)

            specialty = None  # Scar to be set

            # scar pools
            bite_scars = [
                "CATBITE"
            ]
            rat_scars = [
                "RATBITE"
            ]
            beak_scars = [
                'BEAKCHEEK', 'BEAKLOWER'
            ]
            canid_scars = [
                "LEGBITE", "NECKBITE", "TAILSCAR", "BRIGHTHEART"
            ]
            snake_scars = [
                "SNAKE"
            ]
            claw_scars = [
                "ONE", "TWO", "SNOUT", "TAILSCAR", "CHEEK",
                "SIDE", "THROAT", "TAILBASE", "BELLY", "FACE"
            ]
            leg_scars = [
                "NOPAW", "TOETRAP", "MANLEG"
            ]
            tail_scars = [
                "TAILSCAR", "TAILBASE", "NOTAIL", "HALFTAIL", "MANTAIL"
            ]
            ear_scars = [
                "LEFTEAR", "RIGHTEAR", 'NOLEFTEAR', 'NORIGHTEAR'
            ]
            frostbite_scars = [
                "HALFTAIL", "NOTAIL", "NOPAW", 'NOLEFTEAR', 'NORIGHTEAR', 'NOEAR',
                "FROSTFACE", "FROSTTAIL", "FROSTMITT", "FROSTSOCK",
            ]
            eye_scars = [
                "THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND"
            ]
            burn_scars = [
                "BRIGHTHEART", "BURNPAWS", "BURNTAIL", "BURNBELLY", "BURNRUMP"
            ]
            quill_scars = [
                "QUILLCHUNK", "QUILLSCRATCH"
            ]

            scar_pool = []

            if injury_name == "bite-wound":
                scar_pool = canid_scars
            elif injury_name == 'cat bite':
                scar_pool = bite_scars
            elif injury_name == 'beak bite':
                scar_pool = beak_scars
            elif injury_name == 'severe burn':
                scar_pool = burn_scars
            elif injury_name == 'rat bite':
                scar_pool = rat_scars
            elif injury_name == "snake bite":
                scar_pool = snake_scars
            elif injury_name == "claw-wound":
                scar_pool = claw_scars
            elif injury_name == "mangled tail":
                scar_pool = tail_scars
            elif injury_name == "mangled leg":
                scar_pool = leg_scars
            elif injury_name == "torn ear":
                scar_pool = ear_scars
            elif injury_name == "frostbite":
                scar_pool = frostbite_scars
            elif injury_name == "damaged eyes":
                scar_pool = eye_scars
            elif injury_name == "quilled by porcupine":
                scar_pool = quill_scars

            for scar in cat.pelt.scars:
                if scar:
                    try:
                        if scar in scar_pool:
                            scar_pool.remove(scar)  # no duplicate scars
                        if "NOPAW" == scar:
                            for option in ['TOETRAP', 'RATBITE', "FROSTSOCK"]:
                                if option in scar_pool:
                                    scar_pool.remove(option)
                        if "NOTAIL" in scar:
                            for option in ["HALFTAIL", "TAILBASE", "TAILSCAR", "MANTAIL", "BURNTAIL", "FROSTTAIL"]:
                                if option in scar_pool:
                                    scar_pool.remove(option)
                        if "BRIGHTHEART" in scar:
                            for option in ["RIGHTBLIND", "BOTHBLIND"]:
                                if option in scar_pool:
                                    scar_pool.remove(option)
                        if "BOTHBLIND" in scar:
                            for option in ["THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BRIGHTHEART"]:
                                if option in scar_pool:
                                    scar_pool.remove(option)
                        if "NOEAR" in scar:
                            for option in ["LEFTEAR", "RIGHTEAR", 'NOLEFTEAR', 'NORIGHTEAR', "FROSTFACE"]:
                                if option in scar_pool:
                                    scar_pool.remove(option)
                        if 'MANTAIL' in scar:
                            for option in ["BURNTAIL", 'FROSTTAIL']:
                                scar_pool.remove(option)
                        elif 'BURNTAIL' in scar:
                            for option in ["MANTAIL", 'FROSTTAIL']:
                                scar_pool.remove(option)
                        elif 'FROSTTAIL' in scar:
                            for option in ["MANTAIL", 'BURNTAIL']:
                                scar_pool.remove(option)
                        if 'NOLEFT' in scar and 'LEFTEAR' in scar_pool:
                            scar_pool.remove('LEFTEAR')
                        if 'NORIGHT' in scar and 'RIGHTEAR' in scar_pool:
                            scar_pool.remove('RIGHTEAR')

                    except ValueError as e:
                        print(f"ERROR: Failed to exclude scar from pool: {e}")

            if len(scar_pool) > 0:
                specialty = random.choice(scar_pool)
                if specialty in ["NOTAIL", "HALFTAIL"]:
                    if cat.pelt.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.pelt.accessory = None

                # combining left/right variations into the both version
                if "NOLEFTEAR" in cat.pelt.scars and specialty == 'NORIGHTEAR':
                    cat.pelt.scars.remove("NOLEFTEAR")
                    specialty = 'NOEAR'
                elif "NORIGHTEAR" in cat.pelt.scars and specialty == 'NOLEFTEAR':
                    cat.pelt.scars.remove("NORIGHTEAR")
                    specialty = 'NOEAR'

                if 'RIGHTBLIND' in cat.pelt.scars and specialty == 'LEFTBLIND':
                    cat.pelt.scars.remove("LEFTBLIND")
                    specialty = 'BOTHBLIND'
                elif 'LEFTBLIND' in cat.pelt.scars and specialty == 'RIGHTBLIND':
                    cat.pelt.scars.remove("RIGHTBLIND")
                    specialty = 'BOTHBLIND'

                if specialty:
                    if len(cat.pelt.scars) < 4:
                        cat.pelt.scars.append(specialty)

                scar_gain_strings = [
                    f"{cat.name}'s {injury_name} has healed, but they'll always carry evidence of the incident on their pelt.",
                    f"{cat.name} healed from their {injury_name} but will forever be marked by a scar.",
                    f"{cat.name}'s {injury_name} has healed, but the injury left them scarred.",
                ]
                scar_given = specialty
                event_string = random.choice(scar_gain_strings)
            else:
                if injury_name == "poisoned":
                    event_string = f"{cat.name} has recovered fully from the poison."
                else:
                    event_string = f"{cat.name}'s {injury_name} has healed so well that you can't even tell it happened."
                scar_given = None
        else:
            self.history.remove_possible_history(cat, injury_name)
            if injury_name == "poisoned":
                event_string = f"{cat.name} has recovered fully from the poison."
            else:
                event_string = f"{cat.name}'s {injury_name} has healed so well that you can't even tell it happened."

            scar_given = None

        return event_string, scar_given

