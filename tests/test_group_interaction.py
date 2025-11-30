import os
import unittest

from scripts.clan import Clan

from scripts.cat.enums import CatRank

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.cat.skills import Skill, SkillPath
from scripts.events_module.relationship.group_events import (
    GroupEvents,
    GroupInteraction,
)


class MainCatFiltering(unittest.TestCase):
    test_clan = Clan(
        name="Test",
        leader=None,
        deputy=None,
        medicine_cat=None,
        biome="Forest",
        camp_bg=None,
        game_mode="expanded",
        starting_season="Newleaf",
    )

    def test_main_cat_status_one(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat(status_dict={"rank": CatRank.WARRIOR})
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.status_constraint = {"m_c": ["warrior"]}

        interaction2 = GroupInteraction("2")
        interaction2.status_constraint = {"m_c": ["healer"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_status_all(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat(status_dict={"rank": CatRank.WARRIOR})
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.status_constraint = {"m_c": ["warrior"]}

        interaction2 = GroupInteraction("2")
        interaction2.status_constraint = {"m_c": ["healer", "warrior"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_main_cat_trait_one(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat()
        main_cat.personality.trait = "calm"
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.trait_constraint = {"m_c": ["calm"]}

        interaction2 = GroupInteraction("2")
        interaction2.trait_constraint = {"m_c": ["troublesome"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_trait_all(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat()
        main_cat.personality.trait = "calm"
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.trait_constraint = {"m_c": ["calm"]}

        interaction2 = GroupInteraction("2")
        interaction2.trait_constraint = {"m_c": ["troublesome", "calm"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_main_cat_skill_one(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat(moons=40)
        main_cat.skills.primary = Skill(SkillPath.HUNTER, points=9)
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.skill_constraint = {"m_c": ["HUNTER,1"]}

        interaction2 = GroupInteraction("2")
        interaction2.skill_constraint = {"m_c": ["HUNTER,2"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_skill_all(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat()
        main_cat.skills.primary = Skill(SkillPath.HUNTER, 9)
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.skill_constraint = {"m_c": ["HUNTER,1"]}

        interaction2 = GroupInteraction("2")
        interaction2.skill_constraint = {"m_c": ["HUNTER,2", "HUNTER,1"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_main_cat_backstory_one(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat()
        main_cat.backstory = "clanborn"
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.backstory_constraint = {"m_c": ["clanborn"]}

        interaction2 = GroupInteraction("2")
        interaction2.backstory_constraint = {"m_c": ["halfclan1"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_backstory_all(self):
        # given
        group_events = GroupEvents()
        main_cat = Cat()
        main_cat.backstory = "clanborn"
        group_events.abbreviations_cat_id = {"m_c": main_cat.ID}

        interaction1 = GroupInteraction("1")
        interaction1.backstory_constraint = {"m_c": ["clanborn"]}

        interaction2 = GroupInteraction("2")
        interaction2.backstory_constraint = {"m_c": ["halfclan1", "clanborn"]}

        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(
            all_interactions, {"m_c": main_cat.ID}
        )

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)


class Abbreviations(unittest.TestCase):
    def test_get_abbreviation_possibilities_all(self):
        # given
        main_cat = Cat(status_dict={"rank": CatRank.WARRIOR})

        random1 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random2 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random3 = Cat(status_dict={"rank": CatRank.WARRIOR})

        interaction1 = GroupInteraction("1")
        interaction1.status_constraint = {"r_c1": ["warrior"]}

        interaction2 = GroupInteraction("2")
        interaction2.status_constraint = {"r_c1": ["healer", "warrior"]}

        # when
        all_interactions = [interaction1, interaction2]
        interaction_cats = [random1, random2]
        (
            abbreviations_possibilities,
            cat_abbreviations_counter,
        ) = GroupEvents().get_abbreviations_possibilities(
            all_interactions, 3, interaction_cats
        )

        # then
        self.assertEqual(len(abbreviations_possibilities), 2)
        # all cats would fit in
        self.assertEqual(len(abbreviations_possibilities["1"]), 3)
        self.assertEqual(len(abbreviations_possibilities["2"]), 3)

    def test_get_abbreviation_possibilities_not_all(self):
        # given
        main_cat = Cat(status_dict={"rank": CatRank.WARRIOR})

        random1 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random2 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random3 = Cat(status_dict={"rank": CatRank.MEDICINE_CAT})

        interaction1 = GroupInteraction("1")
        interaction1.status_constraint = {"r_c1": ["warrior"]}

        interaction2 = GroupInteraction("2")
        interaction2.status_constraint = {"r_c1": ["medicine cat"]}

        # when
        all_interactions = [interaction1, interaction2]
        interaction_cats = [random1, random2, random3]
        (
            abbreviations_possibilities,
            cat_abbreviations_counter,
        ) = GroupEvents().get_abbreviations_possibilities(
            all_interactions, 3, interaction_cats
        )

        # then
        self.assertEqual(len(abbreviations_possibilities), 2)
        # all cats would fit in
        self.assertEqual(len(abbreviations_possibilities["1"]["r_c1"]), 2)
        self.assertEqual(len(abbreviations_possibilities["2"]["r_c1"]), 1)

    def test_remove_abbreviations_missing_cats(self):
        # given
        abbreviations_possibilities = {
            "1": {
                "r_c1": ["1", "2"],
                "r_c2": ["1", "2"],
            },
            "2": {
                "r_c1": ["1", "2"],
                "r_c2": [],
            },
        }

        # when
        new_possibilities = GroupEvents().remove_abbreviations_missing_cats(
            abbreviations_possibilities
        )

        # then
        self.assertNotEqual(len(abbreviations_possibilities), len(new_possibilities))
        self.assertIn("1", new_possibilities)
        self.assertNotIn("2", new_possibilities)

    def test_set_abbreviations_cats(self):
        # given
        main_cat = Cat(status_dict={"rank": CatRank.WARRIOR})
        abbreviations_cat_id = {"m_c": main_cat.ID, "r_c1": None, "r_c2": None}

        random1 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random2 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random3 = Cat(status_dict={"rank": CatRank.MEDICINE_CAT})

        # when
        interaction_cats = [random1, random2, random3]
        cat_abbreviations_counter = {
            random1.ID: {"r_c1": 2, "r_c2": 2},
            random2.ID: {"r_c1": 2, "r_c2": 2},
            random3.ID: {"r_c1": 1, "r_c2": 2},
        }
        abbreviations_cat_id = GroupEvents().set_abbreviations_cats(
            interaction_cats, abbreviations_cat_id, cat_abbreviations_counter
        )

        # then
        self.assertIsNotNone(abbreviations_cat_id["r_c1"])
        self.assertIsNotNone(abbreviations_cat_id["r_c2"])
        self.assertIn(abbreviations_cat_id["r_c1"], [random1.ID, random2.ID])
        self.assertNotIn(abbreviations_cat_id["r_c1"], [random3.ID])


class OtherCatsFiltering(unittest.TestCase):
    def test_relationship_allow_true(self):
        # given
        parent = Cat()
        main_cat = Cat(parent1=parent.ID, status_dict={"rank": CatRank.WARRIOR})
        random1 = Cat(status_dict={"rank": CatRank.WARRIOR})
        random2 = Cat(parent1=parent.ID, status_dict={"rank": CatRank.WARRIOR})
        abbreviations_cat_id = {
            "m_c": main_cat.ID,
            "r_c1": random1.ID,
            "r_c2": random2.ID,
        }
        # given - relationships
        # order: romance, like, respect, trust, comfort
        main_cat.relationships[random1.ID] = Relationship(
            cat_from=main_cat,
            cat_to=random1,
            mates=False,
            family=False,
            romance=50,
            like=50,
            respect=50,
            trust=50,
            comfort=50,
        )
        random1.relationships[main_cat.ID] = Relationship(
            cat_from=random1,
            cat_to=main_cat,
            mates=False,
            family=False,
            romance=50,
            like=50,
            respect=50,
            trust=50,
            comfort=50,
        )

        main_cat.relationships[random2.ID] = Relationship(
            cat_from=main_cat,
            cat_to=random2,
            mates=False,
            family=True,
            romance=0,
            like=-50,
            respect=-50,
            trust=0,
            comfort=0,
        )
        random2.relationships[main_cat.ID] = Relationship(
            cat_from=random2,
            cat_to=main_cat,
            mates=False,
            family=True,
            romance=0,
            like=-50,
            respect=-50,
            trust=0,
            comfort=0,
        )

        random1.mate.append(random2.ID)
        random2.mate.append(random1.ID)
        random1.relationships[random2.ID] = Relationship(
            cat_from=random1,
            cat_to=random2,
            mates=True,
            family=False,
            romance=50,
            like=50,
            respect=0,
            trust=50,
            comfort=0,
        )
        random2.relationships[random1.ID] = Relationship(
            cat_from=random2,
            cat_to=random1,
            mates=True,
            family=False,
            romance=50,
            like=50,
            respect=0,
            trust=-50,
            comfort=0,
        )

        # summary:
        #    - random1 and random2 are mates
        #    - random2 and main_cat are siblings
        #    - main_cat has a crush on the siblings mate (random1) + vise versa
        #    - main_cat don't like their sibling because of the crush (random2)
        #    - random2 don't trust their mate (random1) because of sibling (main_cat)

        # given - interactions
        # first all true
        interaction1 = GroupInteraction("test")

        interaction2 = GroupInteraction("test")
        interaction2.relationship_constraint = {"r_c1_to_r_c2": ["mates"]}

        interaction3 = GroupInteraction("test")
        interaction3.relationship_constraint = {"m_c_to_r_c2": ["siblings"]}

        interaction4 = GroupInteraction("test")
        interaction4.relationship_constraint = {"m_c_to_r_c1": ["adores"]}

        interaction5 = GroupInteraction("test")
        interaction5.relationship_constraint = {
            "m_c_to_r_c1": ["understands", "adores"]
        }

        interaction6 = GroupInteraction("test")
        interaction6.relationship_constraint = {"m_c_to_r_c2": ["hates"]}

        interaction7 = GroupInteraction("test")
        interaction7.relationship_constraint = {"r_c2_to_r_c1": ["distrusts"]}

        # then
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction1, abbreviations_cat_id
            )
        )
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction2, abbreviations_cat_id
            )
        )
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction3, abbreviations_cat_id
            )
        )
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction4, abbreviations_cat_id
            )
        )
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction5, abbreviations_cat_id
            )
        )
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction6, abbreviations_cat_id
            )
        )
        self.assertTrue(
            GroupEvents().relationship_allow_interaction(
                interaction7, abbreviations_cat_id
            )
        )

    def test_relationship_allow_false(self):
        # given
        parent = Cat()
        main_cat = Cat(parent1=parent.ID, status_dict={"rank": CatRank.WARRIOR})
        random1 = Cat(parent1=parent.ID, status_dict={"rank": CatRank.WARRIOR})
        random2 = Cat(status_dict={"rank": CatRank.WARRIOR})
        abbreviations_cat_id = {
            "m_c": main_cat.ID,
            "r_c1": random1.ID,
            "r_c2": random2.ID,
        }
        # given - relationships
        main_cat.relationships[random1.ID] = Relationship(
            cat_from=main_cat,
            cat_to=random1,
            mates=False,
            family=False,
            romance=50,
            like=50,
            respect=50,
            trust=50,
            comfort=50,
        )
        random1.relationships[main_cat.ID] = Relationship(
            cat_from=random1,
            cat_to=main_cat,
            mates=False,
            family=False,
            romance=50,
            like=50,
            respect=50,
            trust=50,
            comfort=50,
        )

        main_cat.relationships[random2.ID] = Relationship(
            cat_from=main_cat,
            cat_to=random2,
            mates=False,
            family=True,
            romance=0,
            like=-50,
            respect=-50,
            trust=50,
            comfort=0,
        )
        random2.relationships[main_cat.ID] = Relationship(
            cat_from=random2,
            cat_to=main_cat,
            mates=False,
            family=True,
            romance=0,
            like=-50,
            respect=-50,
            trust=50,
            comfort=0,
        )

        random1.mate.append(random2.ID)
        random2.mate.append(random1.ID)
        random1.relationships[random2.ID] = Relationship(
            cat_from=random1,
            cat_to=random2,
            mates=True,
            family=False,
            romance=50,
            like=50,
            respect=0,
            trust=50,
            comfort=0,
        )
        random2.relationships[random1.ID] = Relationship(
            cat_from=random2,
            cat_to=random1,
            mates=True,
            family=False,
            romance=50,
            like=50,
            respect=0,
            trust=-50,
            comfort=0,
        )

        # summary:
        #    - random1 and random2 are mates
        #    - random2 and main_cat are siblings
        #    - main_cat has a crush on the siblings mate (random1) + vise versa
        #    - main_cat don't like their sibling because of the crush (random2)
        #    - random2 don't trust their mate (random1) because of sibling (main_cat)

        # given - interactions
        interaction1 = GroupInteraction("test")
        interaction1.relationship_constraint = {"r_c1_to_m_c": ["hates"]}

        interaction2 = GroupInteraction("test")
        interaction2.relationship_constraint = {"r_c1_to_r_c2": ["not_mates"]}

        interaction3 = GroupInteraction("test")
        interaction3.relationship_constraint = {"r_c1_to_r_c2": ["fancies_only"]}

        interaction4 = GroupInteraction("test")
        interaction4.relationship_constraint = {"r_c1_to_r_c2": ["distrusts"]}

        interaction5 = GroupInteraction("test")
        interaction5.relationship_constraint = {"r_c1_to_m_c": ["mates"]}

        interaction6 = GroupInteraction("test")
        interaction6.relationship_constraint = {"m_c_to_r_c1": ["prefers_only"]}

        interaction7 = GroupInteraction("test")
        interaction7.relationship_constraint = {"m_c_to_r_c1": ["fancies_only"]}

        interaction8 = GroupInteraction("test")
        interaction8.relationship_constraint = {"r_c2_to_r_c1": ["trusts"]}

        # then
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction1, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction2, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction3, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction4, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction5, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction6, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction7, abbreviations_cat_id
            )
        )
        self.assertFalse(
            GroupEvents().relationship_allow_interaction(
                interaction8, abbreviations_cat_id
            )
        )
