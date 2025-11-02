import random

import i18n

from scripts.cat.history import History
from scripts.conditions import (
    get_amount_cat_for_one_medic,
    medicine_cats_can_cover_clan,
)
from scripts.game_structure import game


# ---------------------------------------------------------------------------- #
#                              Scar Event Class                                #
# ---------------------------------------------------------------------------- #


class Scar_Events:
    """All events with a connection to conditions."""

    # scar pools
    bite_scars = ["CATBITE", "CATBITETWO"]
    rat_scars = ["RATBITE", "TOE"]
    beak_scars = ["BEAKCHEEK", "BEAKLOWER", "BEAKSIDE"]
    canid_scars = ["LEGBITE", "NECKBITE", "TAILSCAR", "BRIGHTHEART"]
    snake_scars = ["SNAKE", "SNAKETWO"]
    claw_scars = [
        "ONE",
        "TWO",
        "SNOUT",
        "TAILSCAR",
        "CHEEK",
        "SIDE",
        "THROAT",
        "TAILBASE",
        "BELLY",
        "FACE",
        "BRIDGE",
        "HINDLEG",
        "BACK",
        "SCRATCHSIDE",
    ]
    leg_scars = ["NOPAW", "TOETRAP", "MANLEG", "FOUR"]
    tail_scars = ["TAILSCAR", "TAILBASE", "NOTAIL", "HALFTAIL", "MANTAIL"]
    ear_scars = ["LEFTEAR", "RIGHTEAR", "NOLEFTEAR", "NORIGHTEAR"]
    frostbite_scars = [
        "HALFTAIL",
        "NOTAIL",
        "NOPAW",
        "NOLEFTEAR",
        "NORIGHTEAR",
        "NOEAR",
        "FROSTFACE",
        "FROSTTAIL",
        "FROSTMITT",
        "FROSTSOCK",
    ]
    eye_scars = ["THREE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND"]
    burn_scars = ["BRIGHTHEART", "BURNPAWS", "BURNTAIL", "BURNBELLY", "BURNRUMP"]
    quill_scars = ["QUILLCHUNK", "QUILLSCRATCH", "QUILLSIDE"]
    head_scars = ["SNOUT", "CHEEK", "BRIDGE", "BEAKCHEEK"]
    bone_scars = ["MANLEG", "TOETRAP", "FOUR"]
    back_scars = ["TWO", "TAILBASE", "BACK"]

    scar_allowed = {
        "bite-wound": canid_scars,
        "cat bite": bite_scars,
        "severe burn": burn_scars,
        "rat bite": rat_scars,
        "snake bite": snake_scars,
        "mangled tail": tail_scars,
        "mangled leg": leg_scars,
        "torn ear": ear_scars,
        "frostbite": frostbite_scars,
        "damaged eyes": eye_scars,
        "quilled by porcupine": quill_scars,
        "claw-wound": claw_scars,
        "beak bite": beak_scars,
        "broken jaw": head_scars,
        "broken back": back_scars,
        "broken bone": bone_scars,
    }

    @staticmethod
    def handle_scars(cat, injury_name):
        """
        This function handles the scars
        """

        # If the injury can't give a scar, move return None, None
        if injury_name not in Scar_Events.scar_allowed:
            return None, None

        moons_with = game.clan.age - cat.injuries[injury_name]["moon_start"]
        chance = max(5 - moons_with, 1)

        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medicine_cats_can_cover_clan(
            game.cat_class.all_cats.values(), amount_per_med
        ):
            chance += 2

        if len(cat.pelt.scars) < 4 and not int(random.random() * chance):
            # move potential scar text into displayed scar text

            scar_pool = [
                i
                for i in Scar_Events.scar_allowed[injury_name]
                if i not in cat.pelt.scars
            ]
            if "NOPAW" in cat.pelt.scars:
                scar_pool = [
                    i for i in scar_pool if i not in ("TOETRAP", "RATBITE", "FROSTSOCK")
                ]
            if "NOTAIL" in cat.pelt.scars:
                scar_pool = [
                    i
                    for i in scar_pool
                    if i
                    not in (
                        "HALFTAIL",
                        "TAILBASE",
                        "TAILSCAR",
                        "MANTAIL",
                        "BURNTAIL",
                        "FROSTTAIL",
                    )
                ]
            if "HALFTAIL" in cat.pelt.scars:
                scar_pool = [
                    i
                    for i in scar_pool
                    if i not in ("TAILSCAR", "MANTAIL", "FROSTTAIL")
                ]
            if "BRIGHTHEART" in cat.pelt.scars:
                scar_pool = [
                    i for i in scar_pool if i not in ("RIGHTBLIND", "BOTHBLIND")
                ]
            if "BOTHBLIND" in cat.pelt.scars:
                scar_pool = [
                    i
                    for i in scar_pool
                    if i
                    not in (
                        "THREE",
                        "RIGHTBLIND",
                        "LEFTBLIND",
                        "BOTHBLIND",
                        "BRIGHTHEART",
                    )
                ]
            if "NOEAR" in cat.pelt.scars:
                scar_pool = [
                    i
                    for i in scar_pool
                    if i
                    not in (
                        "LEFTEAR",
                        "RIGHTEAR",
                        "NOLEFTEAR",
                        "NORIGHTEAR",
                        "FROSTFACE",
                    )
                ]
            if "MANTAIL" in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ("BURNTAIL", "FROSTTAIL")]
            if "BURNTAIL" in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ("MANTAIL", "FROSTTAIL")]
            if "FROSTTAIL" in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ("MANTAIL", "BURNTAIL")]
            if "NOLEFT" in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ("LEFTEAR",)]
            if "NORIGHT" in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in ("RIGHTEAR",)]

            # Extra check for disabling scars.
            if int(random.random() * 3):
                condition_scars = {
                    "LEGBITE",
                    "THREE",
                    "NOPAW",
                    "TOETRAP",
                    "NOTAIL",
                    "HALFTAIL",
                    "LEFTEAR",
                    "RIGHTEAR",
                    "MANLEG",
                    "BRIGHTHEART",
                    "NOLEFTEAR",
                    "NORIGHTEAR",
                    "NOEAR",
                    "LEFTBLIND",
                    "RIGHTBLIND",
                    "BOTHBLIND",
                    "RATBITE",
                }

                scar_pool = list(set(scar_pool).difference(condition_scars))

            # If there are no new scars to give them, return None, None.
            if not scar_pool:
                return None, None

            # If we've reached this point, we can move forward with giving history.
            cat.history.add_scar(
                i18n.t(
                    "cat.history.scar_from_injury",
                    injury_name=i18n.t(f"conditions.injuries.{injury_name}"),
                ),
                condition=injury_name,
            )

            specialty = random.choice(scar_pool)
            if specialty in ["NOTAIL", "HALFTAIL"]:
                cat.pelt.accessory = [
                    acc
                    for acc in cat.pelt.accessory
                    if acc
                    not in (
                        "RED FEATHERS",
                        "BLUE FEATHERS",
                        "JAY FEATHERS",
                        "GULL FEATHERS",
                        "SPARROW FEATHERS",
                        "CLOVER",
                        "DAISY",
                    )
                ]

            # combining left/right variations into the both version
            if "NOLEFTEAR" in cat.pelt.scars and specialty == "NORIGHTEAR":
                cat.pelt.scars.remove("NOLEFTEAR")
                specialty = "NOEAR"
            elif "NORIGHTEAR" in cat.pelt.scars and specialty == "NOLEFTEAR":
                cat.pelt.scars.remove("NORIGHTEAR")
                specialty = "NOEAR"

            if "RIGHTBLIND" in cat.pelt.scars and specialty == "LEFTBLIND":
                cat.pelt.scars.remove("LEFTBLIND")
                specialty = "BOTHBLIND"
            elif "LEFTBLIND" in cat.pelt.scars and specialty == "RIGHTBLIND":
                cat.pelt.scars.remove("RIGHTBLIND")
                specialty = "BOTHBLIND"

            cat.pelt.scars.append(specialty)

            scar_gain_strings = [
                "hardcoded.scar_event0",
                "hardcoded.scar_event1",
                "hardcoded.scar_event2",
            ]
            return (
                i18n.t(
                    random.choice(scar_gain_strings),
                    injury=i18n.t(f"conditions.injuries.{injury_name}"),
                ),
                specialty,
            )
        else:
            return None, None
