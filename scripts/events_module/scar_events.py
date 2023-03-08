import random

from scripts.cat.cats import Cat
from scripts.conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled
from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                              Scar Event Class                                #
# ---------------------------------------------------------------------------- #

class Scar_Events():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        pass

    def handle_scars(self, cat, injury_name):
        """ 
        This function handles the scars
        """
        
        scar_text = cat.possible_scar

        chance = int(random.random() * 13 - cat.injuries[injury_name]["moons_with"])
        if chance <= 0:
            chance = 1
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            chance += 3
        if len(cat.scars) < 4 and chance <= 6:

            # move potential scar text into displayed scar text
            cat.scar_event.append(scar_text)

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

            for scar in cat.scars:
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
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                # combining left/right variations into the both version
                if "NOLEFTEAR" in cat.scars and specialty == 'NORIGHTEAR':
                    cat.scars.remove("NOLEFTEAR")
                    specialty = 'NOEAR'
                elif "NORIGHTEAR" in cat.scars and specialty == 'NOLEFTEAR':
                    cat.scars.remove("NORIGHTEAR")
                    specialty = 'NOEAR'

                if 'RIGHTBLIND' in cat.scars and specialty == 'LEFTBLIND':
                    cat.scars.remove("LEFTBLIND")
                    specialty = 'BOTHBLIND'
                elif 'LEFTBLIND' in cat.scars and specialty == 'RIGHTBLIND':
                    cat.scars.remove("RIGHTBLIND")
                    specialty = 'BOTHBLIND'

                if specialty:
                    if len(cat.scars) < 4:
                        cat.scars.append(specialty)

                scar_gain_strings = [
                    f"{cat.name}'s {injury_name} has healed, but they'll always carry evidence of the incident on their pelt.",
                    f"{cat.name} healed from their {injury_name} but will forever be marked by a scar.",
                    f"{cat.name}'s {injury_name} has healed, but the injury left them scarred.",
                ]
                scar_given = specialty
                event_string = random.choice(scar_gain_strings)
            else:
                if (injury_name == "poisoned"):
                    event_string = f"{cat.name} has recovered fully from the poison."
                else:
                    event_string = f"{cat.name}'s {injury_name} has healed so well that you can't even tell it happened."
                scar_given = None
        else:
            if (injury_name == "poisoned"):
                event_string = f"{cat.name} has recovered fully from the poison."
            else:
                event_string = f"{cat.name}'s {injury_name} has healed so well that you can't even tell it happened."
            scar_given = None

        cat.possible_scar = None  # reset potential scar text
        return event_string, scar_given

