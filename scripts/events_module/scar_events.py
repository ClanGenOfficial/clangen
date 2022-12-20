import ujson
import random

from scripts.cat.cats import Cat
from scripts.cat.pelts import scars1, scars2, scars3
from scripts.utility import save_death
from scripts.game_structure.game_essentials import game, SAVE_DEATH


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

        chance = random.choices([1, 2], [2, 1])  # making scars slightly more common
        if not cat.specialty and not cat.specialty2 and not int(random.random() * chance):

            # move potential scar text into displayed scar text
            cat.scar_event.append(scar_text)

            specialty = None  # Scar to be set

            # scar pools
            bite_scars = [
                "LEGBITE", "NECKBITE", "TAILSCAR"
            ]
            snake_scars = [
                "SNAKE"
            ]
            claw_scars = [
                "ONE", "TWO", "SNOUT", "TAILSCAR", "CHEEK",
                "SIDE", "THROAT", "TAILBASE", "BELLY", "FACE"
            ]
            leg_scars = [
                "NOPAW", "TOETRAP"
            ]
            tail_scars = [
                "TAILSCAR", "TAILBASE", "NOTAIL", "HALFTAIL"
            ]
            ear_scars = [
                "LEFTEAR", "RIGHTEAR"
            ]
            frostbite_scars = [
                "HALFTAIL", "NOTAIL", "NOPAW"
            ]
            eye_scars = [
                "THREE"
            ]

            scar_pool = []

            if injury_name in ["bite-wound", "rat bite"]:
                scar_pool = bite_scars
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

            for special in [cat.specialty, cat.specialty2]:
                if special:
                    try:
                        if "NOPAW" == special and 'TOETRAP' in scar_pool:
                            scar_pool.remove('TOETRAP')
                        if "NOTAIL" in special:
                            for scar in ["HALFTAIL", "TAILBASE", "TAILSCAR"]:
                                if scar in scar_pool:
                                    scar_pool.remove(scar)
                        if special in scar_pool:
                            scar_pool.remove(special)  # no duplicate scars
                    except ValueError as e:
                        print(f"Failed to exclude scar from pool: {e}")

            if len(scar_pool) > 0:
                specialty = random.choice(scar_pool)
                if specialty in ["NOTAIL", "HALFTAIL"]:
                    if cat.accessory in ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]:
                        cat.accessory = None

                if specialty:
                    if not cat.specialty:
                        cat.specialty = specialty
                    else:
                        cat.specialty2 = specialty

                scar_gain_strings = [
                    f"{cat.name}'s {injury_name} has healed, but they'll always carry evidence of the incident on their pelt.",
                    f"{cat.name} healed from their {injury_name} but will forever be marked by a scar.",
                    f"{cat.name}'s {injury_name} has healed, but the injury left them scarred.",
                ]
                scar_given = specialty
                event_string = random.choice(scar_gain_strings)
            else:
                event_string = f"{cat.name}'s {injury_name} has healed so well that you can't even tell it happened."
                scar_given = None
        else:
            event_string = f"{cat.name}'s {injury_name} has healed so well that you can't even tell it happened."
            scar_given = None

        cat.possible_scar = None  # reset potential scar text
        return event_string, scar_given

