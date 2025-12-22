import os
import unittest

from scripts.cat.enums import CatRank

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.clan import Clan
from scripts.events_module.patrol.patrol import Patrol


class TestCondition(unittest.TestCase):
    condition_lists = {
        "battle_injury": [
            "claw-wound",
            "mangled leg",
            "mangled tail",
            "torn pelt",
            "cat bite",
        ],
        "minor_injury": ["sprain", "sore", "bruises", "scrapes"],
        "blunt_force_injury": [
            "broken bone",
            "broken back",
            "head damage",
            "broken jaw",
        ],
        "hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
        "cold_injury": ["shivering", "frostbite"],
        "big_bite_injury": [
            "bite-wound",
            "broken bone",
            "torn pelt",
            "mangled leg",
            "mangled tail",
        ],
        "small_bite_injury": ["bite-wound", "torn ear", "torn pelt", "scrapes"],
        "beak_bite": ["beak bite", "torn ear", "scrapes"],
        "rat_bite": ["rat bite", "torn ear", "torn pelt"],
        "sickness": ["greencough", "redcough", "whitecough", "yellowcough"],
    }

    cold_patrol = {
        "patrol_id": "fst_med_gatheringdandelion_leaf-bare1",
        "biome": ["forest"],
        "season": ["leaf-bare"],
        "types": ["herb_gathering"],
        "tags": [],
        "patrol_art": "med_general_intro",
        "min_cats": 1,
        "max_cats": 1,
        "min_max_status": {
            "apprentice": [-1, -1],
            "healer cats": [1, 6],
            "normal adult": [-1, -1],
        },
        "weight": 20,
        "intro_text": "The cold of leaf-bare might have killed off a lot of greenery, but p_l knows that the"
        " dandelions are only playing dead. If they can get their paws on a plant,"
        " the roots will still hold fresh, milky-white sap.",
        "decline_text": "{PRONOUN/p_l/subject/CAP} {VERB/p_l/have/has} second thoughts about leaving {PRONOUN/p_l/poss} patients behind and {VERB/p_l/decide/decides} to go another day.",
        "chance_of_success": 40,
        "success_outcomes": [
            {
                "text": "p_l can't say it's <i>fun,</i> swiping away snow to scrounge for the stems and roots"
                " of wilted dandelions below, but what matters currently is that it's <i>possible.</i>",
                "exp": 10,
                "weight": 20,
                "herbs": ["dandelion"],
            },
            {
                "text": "It's a truly miserable, gray day, but even the colds of leaf-bare can't dampen"
                " p_l's joy when they manage to uncover a couple good dandelion plants.",
                "exp": 10,
                "weight": 5,
                "herbs": ["dandelion"],
            },
            {
                "text": "It's not just spotting things that s_c is talented at - finding dandelions"
                " in leaf-bare is hard enough, but finding good, non-wilted leaves is next to"
                " impossible, and it's a mark of s_c's unique skills that {PRONOUN/s_c/subject} {VERB/s_c/manage/manages} it.",
                "exp": 10,
                "weight": 20,
                "stat_skill": ["SENSE,2"],
                "herbs": ["dandelion"],
            },
        ],
        "fail_outcomes": [
            {
                "text": "Not only does p_l end up soaked to the skin, but they can't even find any dandelions"
                " under the snow. A wasted and horribly chilly day.",
                "exp": 0,
                "weight": 20,
            },
            {
                "text": "Not only does r_c end up soaked to the skin, they can't even find any dandelions"
                " under the snow, and they're left shivering violently by the time they return to camp.",
                "exp": 0,
                "weight": 10,
                "injury": [
                    {
                        "cats": ["r_c"],
                        "injuries": ["cold_injury"],
                        "scars": ["FROSTFACE"],
                    }
                ],
                "history_text": {
                    "scar": "m_c was scarred by frostbite from searching for herbs in leaf-bare."
                },
            },
        ],
    }

    def test_cold_injury(self):
        # GIVEN
        clan = Clan()
        patrol_cat = Cat(
            moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True
        )
        patrol_cat.history = History(cat=patrol_cat)
        patrol = Patrol()
        patrol.add_patrol_cats([patrol_cat], clan)
        patrol_event = patrol.generate_patrol_events([self.cold_patrol])

        # WHEN - THEN
        injury_outcome = patrol_event[0].fail_outcomes[1]
        self.assertEqual(len(patrol_cat.injuries), 0)
        self.assertEqual(len(patrol_cat.illnesses), 0)
        outcome = injury_outcome._handle_condition_and_scars(patrol)

        self.assertEqual(len(patrol_event), 1)
        self.assertGreater(len(patrol_cat.injuries), 0)
