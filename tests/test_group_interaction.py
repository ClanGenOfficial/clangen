import os
import unittest

from scripts.cat.status import StatusDict
from scripts.clan import Clan

from scripts.cat.enums import CatRank
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
)
from scripts.events_module.relationship import generate_group_event
from scripts.events_module.text_pool_event import TextPoolEvent
from scripts.game_structure import game

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship


class MainCatFiltering(unittest.TestCase):
    test_clan = Clan(
        save_id="Test",
        leader=None,
        deputy=None,
        medicine_cat=None,
        biome="Forest",
        camp_bg=None,
        cruel_cards=[],
        game_mode="expanded",
        starting_season="Newleaf",
    )
    game.clan = test_clan

    def test_cat_constraints(self):
        # this is really just to test that the involved cat constraints are being detected and filtered
        # the filtering is already tested in test_event_filters.py, so I don't feel the need to rehash all of it in detail

        main_cat = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.WARRIOR)
        )
        rand_medicine1 = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.MEDICINE_CAT)
        )
        rand_medicine2 = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.MEDICINE_CAT)
        )
        rand_warrior = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.WARRIOR)
        )
        rand_apprentice = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.APPRENTICE)
        )

        other_cats = [rand_medicine2, rand_medicine1, rand_warrior, rand_apprentice]

        # test main cat needs a status and no one else
        with self.subTest("main cat needs certain status"):
            event1 = TextPoolEvent(
                id="warrior",
                strings=["status"],
                involved_cats={
                    "m_c": InvolvedCatDict(status=["warrior"]),
                    "r_c1": {},
                    "multi_cat": {},
                },
            )
            event2 = TextPoolEvent(
                id="leader",
                strings=["status"],
                involved_cats={
                    "m_c": InvolvedCatDict(status=["leader"]),
                    "r_c1": {},
                    "multi_cat": {},
                },
            )

            chosen_event, involved_cats = generate_group_event._get_event(
                [event1, event2], other_cats, main_cat
            )

            self.assertEqual(event1, chosen_event)

        # test main cat and 2 random cats need a status
        with self.subTest("main cat and random cats need certain status"):
            event1 = TextPoolEvent(
                id="2war_1app",
                strings=["status"],
                involved_cats={
                    "m_c": InvolvedCatDict(status=["warrior"]),
                    "r_c1": InvolvedCatDict(status=["warrior"]),
                    "r_c2": InvolvedCatDict(status=["apprentice"]),
                },
            )
            event2 = TextPoolEvent(
                id="lead_dep_war",
                strings=["status"],
                involved_cats={
                    "m_c": InvolvedCatDict(status=["leader"]),
                    "r_c1": InvolvedCatDict(status=["deputy"]),
                    "r_c2": InvolvedCatDict(status=["warrior"]),
                },
            )

            chosen_event, involved_cats = generate_group_event._get_event(
                [event1, event2], other_cats, main_cat
            )

            self.assertEqual(event1, chosen_event)
            self.assertEqual(
                involved_cats,
                {"m_c": main_cat, "r_c1": rand_warrior, "r_c2": rand_apprentice},
            )

        # test main cat and multi_cat needs a status
        with self.subTest("main cat and multi cats need certain status"):
            event1 = TextPoolEvent(
                id="war_meddies",
                strings=["status"],
                involved_cats={
                    "m_c": InvolvedCatDict(status=["warrior"]),
                    "multi_cat": InvolvedCatDict(status=["medicine cat"]),
                },
            )
            event2 = TextPoolEvent(
                id="leader_war",
                strings=["status"],
                involved_cats={
                    "m_c": InvolvedCatDict(status=["leader"]),
                    "multi_cat": InvolvedCatDict(status=["warrior"]),
                },
            )

            chosen_event, involved_cats = generate_group_event._get_event(
                [event1, event2], other_cats, main_cat
            )

            self.assertEqual(event1, chosen_event)
            self.assertEqual(involved_cats["m_c"], main_cat)
            self.assertCountEqual(
                involved_cats["multi_cat"], [rand_medicine1, rand_medicine2]
            )

    def test_relationship_constraints(self):
        main_cat = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.WARRIOR)
        )
        rand1 = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.MEDICINE_CAT)
        )
        rand2 = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.MEDICINE_CAT)
        )
        rand3 = Cat(disable_random=True, status_dict=StatusDict(rank=CatRank.WARRIOR))
        rand4 = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.APPRENTICE)
        )

        other_cats = [rand1, rand2, rand3, rand4]

        with self.subTest("m_c likes r_c1 and dislikes r_c2"):
            main_cat.relationships[rand1.ID] = Relationship(
                cat_from=main_cat, cat_to=rand1, like=30
            )
            main_cat.relationships[rand2.ID] = Relationship(
                cat_from=main_cat, cat_to=rand2, like=-30
            )
            event1 = TextPoolEvent(
                id="main_likes_random1",
                strings=["test"],
                involved_cats={
                    "m_c": {},
                    "r_c1": {},
                    "r_c2": {},
                },
                relationship_constraint=[
                    RelationshipConstraintDict(
                        cats_from=["m_c"],
                        cats_to=["r_c1"],
                        mutual=False,
                        constraints=["likes"],
                    ),
                    RelationshipConstraintDict(
                        cats_from=["m_c"],
                        cats_to=["r_c2"],
                        mutual=False,
                        constraints=["dislikes"],
                    ),
                ],
            )
            event2 = TextPoolEvent(
                id="random2_likes_main",
                strings=["test"],
                involved_cats={
                    "m_c": {},
                    "r_c1": {},
                    "r_c2": {},
                },
                relationship_constraint=[
                    RelationshipConstraintDict(
                        cats_from=["r_c2"],
                        cats_to=["m_c"],
                        mutual=False,
                        constraints=["likes"],
                    )
                ],
            )

            chosen_event, involved_cats = generate_group_event._get_event(
                [event1, event2], other_cats, main_cat
            )

            self.assertEqual(event1, chosen_event)
            self.assertDictEqual(
                involved_cats,
                {"m_c": main_cat, "r_c1": rand1, "r_c2": rand2},
            )

        with self.subTest("m_c and multi_cat likes r_c1 and dislikes r_c2"):
            rand3.relationships[rand1.ID] = Relationship(
                cat_from=main_cat, cat_to=rand1, like=30
            )
            rand3.relationships[rand2.ID] = Relationship(
                cat_from=main_cat, cat_to=rand2, like=-30
            )
            rand4.relationships[rand1.ID] = Relationship(
                cat_from=main_cat, cat_to=rand1, like=30
            )
            rand4.relationships[rand2.ID] = Relationship(
                cat_from=main_cat, cat_to=rand2, like=-30
            )

            event1 = TextPoolEvent(
                id="many_likes_random1",
                strings=["test"],
                involved_cats={"m_c": {}, "r_c1": {}, "r_c2": {}, "multi_cat": {}},
                relationship_constraint=[
                    RelationshipConstraintDict(
                        cats_from=["m_c", "multi_cat"],
                        cats_to=["r_c1"],
                        mutual=False,
                        constraints=["likes"],
                    ),
                    RelationshipConstraintDict(
                        cats_from=["m_c", "multi_cat"],
                        cats_to=["r_c2"],
                        mutual=False,
                        constraints=["dislikes"],
                    ),
                ],
            )
            event2 = TextPoolEvent(
                id="many_likes_main",
                strings=["test"],
                involved_cats={"m_c": {}, "r_c1": {}, "r_c2": {}, "multi_cat": {}},
                relationship_constraint=[
                    RelationshipConstraintDict(
                        cats_from=["r_c2", "multi_cat"],
                        cats_to=["m_c"],
                        mutual=False,
                        constraints=["likes"],
                    )
                ],
            )

            chosen_event, involved_cats = generate_group_event._get_event(
                [event1, event2], other_cats, main_cat
            )

            self.assertEqual(event1, chosen_event)
            self.assertEqual(involved_cats["m_c"], main_cat)
            self.assertEqual(involved_cats["r_c1"], rand1)
            self.assertEqual(involved_cats["r_c2"], rand2)
            self.assertCountEqual(involved_cats["multi_cat"], [rand3, rand4])

        with self.subTest("m_c and multi_cat likes r_c1 and dislikes + begrudges r_c2"):
            main_cat.relationships[rand2.ID] = Relationship(
                cat_from=main_cat, cat_to=rand2, like=-30, respect=-30
            )
            rand3.relationships[rand1.ID] = Relationship(
                cat_from=main_cat, cat_to=rand1, like=30
            )
            rand3.relationships[rand2.ID] = Relationship(
                cat_from=main_cat, cat_to=rand2, like=-30, respect=-30
            )
            rand4.relationships[rand1.ID] = Relationship(
                cat_from=main_cat, cat_to=rand1, like=30
            )
            rand4.relationships[rand2.ID] = Relationship(
                cat_from=main_cat, cat_to=rand2, like=-30, respect=-30
            )

            event1 = TextPoolEvent(
                id="many_likes_random1",
                strings=["test"],
                involved_cats={"m_c": {}, "r_c1": {}, "r_c2": {}, "multi_cat": {}},
                relationship_constraint=[
                    RelationshipConstraintDict(
                        cats_from=["m_c", "multi_cat"],
                        cats_to=["r_c1"],
                        mutual=False,
                        constraints=["likes"],
                    ),
                    RelationshipConstraintDict(
                        cats_from=["m_c", "multi_cat"],
                        cats_to=["r_c2"],
                        mutual=False,
                        constraints=["dislikes", "begrudges"],
                    ),
                ],
            )
            event2 = TextPoolEvent(
                id="many_likes_main",
                strings=["test"],
                involved_cats={"m_c": {}, "r_c1": {}, "r_c2": {}, "multi_cat": {}},
                relationship_constraint=[
                    RelationshipConstraintDict(
                        cats_from=["r_c2", "multi_cat"],
                        cats_to=["m_c"],
                        mutual=False,
                        constraints=["likes"],
                    )
                ],
            )

            chosen_event, involved_cats = generate_group_event._get_event(
                [event1, event2], other_cats, main_cat
            )

            self.assertEqual(event1, chosen_event)
            self.assertEqual(involved_cats["m_c"], main_cat)
            self.assertEqual(involved_cats["r_c1"], rand1)
            self.assertEqual(involved_cats["r_c2"], rand2)
            self.assertCountEqual(involved_cats["multi_cat"], [rand3, rand4])
