import unittest

import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.cat.skills import Skill, SkillPath
from scripts.events_module.relationship.group_events import Group_Events, Group_Interaction

class MainCatFiltering(unittest.TestCase):
    def test_main_cat_status_one(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.status = "warrior"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.status_constraint = {"m_c": ["warrior"]}

        interaction2 = Group_Interaction("2")
        interaction2.status_constraint = {"m_c": ["healer"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_status_all(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.status = "warrior"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.status_constraint = {"m_c": ["warrior"]}

        interaction2 = Group_Interaction("2")
        interaction2.status_constraint = {"m_c": ["healer", "warrior"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_main_cat_trait_one(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.personality.trait = "calm"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.trait_constraint = {"m_c": ["calm"]}

        interaction2 = Group_Interaction("2")
        interaction2.trait_constraint = {"m_c": ["troublesome"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_trait_all(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.personality.trait = "calm"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.trait_constraint = {"m_c": ["calm"]}

        interaction2 = Group_Interaction("2")
        interaction2.trait_constraint = {"m_c": ["troublesome", "calm"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_main_cat_skill_one(self):
        # given
        group_events = Group_Events()
        main_cat = Cat(moons=40)
        main_cat.skills.primary = Skill(SkillPath.HUNTER, points=9)
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.skill_constraint = {"m_c": ["HUNTER,1"]}

        interaction2 = Group_Interaction("2")
        interaction2.skill_constraint = {"m_c": ["HUNTER,2"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_skill_all(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.skills.primary = Skill(SkillPath.HUNTER, 9)
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.skill_constraint = {"m_c": ["HUNTER,1"]}

        interaction2 = Group_Interaction("2")
        interaction2.skill_constraint = {"m_c": ["HUNTER,2", "HUNTER,1"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_main_cat_backstory_one(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.backstory = "clanborn"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.backstory_constraint = {"m_c": ["clanborn"]}

        interaction2 = Group_Interaction("2")
        interaction2.backstory_constraint = {"m_c": ["halfclan1"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_main_cat_backstory_all(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.backstory = "clanborn"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.backstory_constraint = {"m_c": ["clanborn"]}

        interaction2 = Group_Interaction("2")
        interaction2.backstory_constraint = {"m_c": ["halfclan1", "clanborn"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any", {"m_c": main_cat.ID})

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)


class OtherFiltering(unittest.TestCase):
    def test_season_one(self):
        # given
        main_cat = Cat()
        abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.season = ["newleaf"]

        interaction2 = Group_Interaction("2")
        interaction2.season = ["green-leaf"]
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = Group_Events().get_main_cat_interactions(all_interactions, "Any", "newleaf", abbreviations_cat_id)

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_season_multiple(self):
        # given
        main_cat = Cat()
        abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.season = ["newleaf"]

        interaction2 = Group_Interaction("2")
        interaction2.season = ["newleaf", "green-leaf"]
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = Group_Events().get_main_cat_interactions(all_interactions, "Any", "newleaf", abbreviations_cat_id)

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_season_any(self):
        # given
        main_cat = Cat()
        abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.season = ["newleaf"]

        interaction2 = Group_Interaction("2")
        interaction2.season = ["Any"]
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = Group_Events().get_main_cat_interactions(all_interactions, "Any", "newleaf", abbreviations_cat_id)

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_biome_one(self):
        # given
        main_cat = Cat()
        abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.biome = ["forest"]

        interaction2 = Group_Interaction("2")
        interaction2.biome = ["beach"]
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = Group_Events().get_main_cat_interactions(all_interactions, "forest", "Any", abbreviations_cat_id)

        # then
        self.assertNotEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)

    def test_biome_multiple(self):
        # given
        main_cat = Cat()
        abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.biome = ["forest"]

        interaction2 = Group_Interaction("2")
        interaction2.biome = ["beach", "forest"]
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = Group_Events().get_main_cat_interactions(all_interactions, "forest", "Any", abbreviations_cat_id)

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)

    def test_biome_any(self):
        # given
        main_cat = Cat()
        abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.biome = ["forest"]

        interaction2 = Group_Interaction("2")
        interaction1.biome = ["Any"]
        
        # when
        all_interactions = [interaction1, interaction2]
        filtered_interactions = Group_Events().get_main_cat_interactions(all_interactions, "forest", "Any", abbreviations_cat_id)

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
        self.assertIn(interaction1, filtered_interactions)
        self.assertIn(interaction2, filtered_interactions)


class Abbreviations(unittest.TestCase):
    def test_get_abbreviation_possibilities_all(self):
        # given
        main_cat = Cat()
        main_cat.status = "warrior"

        random1 = Cat()
        random1.status = "warrior"
        random2 = Cat()
        random2.status = "warrior"
        random3 = Cat()
        random3.status = "warrior"

        interaction1 = Group_Interaction("1")
        interaction1.status_constraint = {"r_c1": ["warrior"]}

        interaction2 = Group_Interaction("2")
        interaction2.status_constraint = {"r_c1": ["healer", "warrior"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        interaction_cats = [random1, random2]
        abbreviations_possibilities, cat_abbreviations_counter = Group_Events().get_abbreviations_possibilities(
            all_interactions, 3, interaction_cats
        )

        # then
        self.assertEqual(len(abbreviations_possibilities), 2)
        # all cats would fit in
        self.assertEqual(len(abbreviations_possibilities["1"]), 3)
        self.assertEqual(len(abbreviations_possibilities["2"]), 3)

    def test_get_abbreviation_possibilities_not_all(self):
        # given
        main_cat = Cat()
        main_cat.status = "warrior"

        random1 = Cat()
        random1.status = "warrior"
        random2 = Cat()
        random2.status = "warrior"
        random3 = Cat()
        random3.status = "medicine cat"

        interaction1 = Group_Interaction("1")
        interaction1.status_constraint = {"r_c1": ["warrior"]}

        interaction2 = Group_Interaction("2")
        interaction2.status_constraint = {"r_c1": ["medicine cat"]}
        
        # when
        all_interactions = [interaction1, interaction2]
        interaction_cats = [random1, random2, random3]
        abbreviations_possibilities, cat_abbreviations_counter = Group_Events().get_abbreviations_possibilities(
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
        new_possibilities = Group_Events().remove_abbreviations_missing_cats(
            abbreviations_possibilities
        )

        # then
        self.assertNotEqual(len(abbreviations_possibilities), len(new_possibilities))
        self.assertIn("1", new_possibilities)
        self.assertNotIn("2", new_possibilities)

    def test_set_abbreviations_cats(self):
        # given
        main_cat = Cat()
        main_cat.status = "warrior"
        abbreviations_cat_id={
            "m_c": main_cat.ID,
            "r_c1": None,
            "r_c2": None
        }

        random1 = Cat()
        random1.status = "warrior"
        random2 = Cat()
        random2.status = "warrior"
        random3 = Cat()
        random3.status = "medicine cat"

        # when
        interaction_cats = [random1, random2, random3]
        cat_abbreviations_counter = {
            random1.ID: {
                "r_c1": 2,
                "r_c2": 2
            },
            random2.ID: {
                "r_c1": 2,
                "r_c2": 2
            },
            random3.ID: {
                "r_c1": 1,
                "r_c2": 2
            }
        }
        abbreviations_cat_id = Group_Events().set_abbreviations_cats(interaction_cats, abbreviations_cat_id, cat_abbreviations_counter)

        # then
        self.assertIsNotNone(abbreviations_cat_id["r_c1"])
        self.assertIsNotNone(abbreviations_cat_id["r_c2"])
        self.assertIn(abbreviations_cat_id["r_c1"], [random1.ID, random2.ID])
        self.assertNotIn(abbreviations_cat_id["r_c1"], [random3.ID])


class OtherCatsFiltering(unittest.TestCase):
    def test_relationship_allow_true(self):
        # given
        parent = Cat()
        main_cat = Cat(parent1=parent.ID)
        main_cat.status = "warrior"
        random1 = Cat(parent1=parent.ID)
        random1.status = "warrior"
        random2 = Cat()
        random2.status = "warrior"
        abbreviations_cat_id={
            "m_c": main_cat.ID,
            "r_c1": random1.ID,
            "r_c2": random2.ID
        }
        # given - relationships
        # order: romantic, platonic, dislike, admiration, comfortable, jealousy, trust
        main_cat.relationships[random1.ID] = Relationship(
            main_cat, random1, False, False, 50, 50, 0, 50, 50, 0, 50
        )
        random1.relationships[main_cat.ID] = Relationship(
            random1, main_cat, False, False, 50, 50, 0, 50, 50, 0, 50
        )

        main_cat.relationships[random2.ID] = Relationship(
            main_cat, random2, False, True, 0, 0, 50, 0, 0, 50, 0
        )
        random2.relationships[main_cat.ID] = Relationship(
            random2, main_cat, False, True, 0, 0, 50, 0, 0, 50, 0
        )


        random1.mate.append(random2.ID)
        random2.mate.append(random1.ID)
        random1.relationships[random2.ID] = Relationship(
            random1, random2, True, False, 50, 50, 0, 0, 0, 0, 50
        )
        random2.relationships[random1.ID] = Relationship(
            random2, random1, True, False, 50, 50, 0, 0, 0, 0, 0
        )

        # summary: 
        #    - random1 and random2 are mates
        #    - random2 and main_cat are siblings
        #    - main_cat has a crush on the siblings mate (random1) + vise versa
        #    - main_cat don't like their sibling because of the crush (random2)
        #    - random2 don't trust their mate (random1) because of sibling (main_cat)
        

        # given - interactions
        # first all true
        interaction1 = Group_Interaction("test")

        interaction2 = Group_Interaction("test")
        interaction2.relationship_constraint = {
            "r_c1_to_r_c2": ["mates"]
        }

        interaction3 = Group_Interaction("test")
        interaction3.relationship_constraint = {
            "m_c_to_r_c1": ["siblings"]
        }

        interaction4 = Group_Interaction("test")
        interaction4.relationship_constraint = {
            "m_c_to_r_c1": ["romantic_40"]
        }

        interaction5 = Group_Interaction("test")
        interaction5.relationship_constraint = {
            "m_c_to_r_c1": ["comfortable_40"]
        }

        interaction6 = Group_Interaction("test")
        interaction6.relationship_constraint = {
            "m_c_to_r_c1": ["comfortable_40", "romantic_40"]
        }

        interaction7 = Group_Interaction("test")
        interaction7.relationship_constraint = {
            "m_c_to_r_c1": ["romantic_60_lower"]
        }

        interaction8 = Group_Interaction("test")
        interaction8.relationship_constraint = {
            "m_c_to_r_c1": ["comfortable_60_lower"]
        }

        interaction9 = Group_Interaction("test")
        interaction9.relationship_constraint = {
            "m_c_to_r_c2": ["dislike_40"]
        }

        interaction10 = Group_Interaction("test")
        interaction10.relationship_constraint = {
            "r_c2_to_m_c": ["dislike_40"]
        }

        # then
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction1, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction2, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction3, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction4, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction5, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction6, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction7, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction8, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction9, abbreviations_cat_id))
        self.assertTrue(Group_Events().relationship_allow_interaction(interaction10, abbreviations_cat_id))

    def test_relationship_allow_false(self):
        # given
        parent = Cat()
        main_cat = Cat(parent1=parent.ID)
        main_cat.status = "warrior"
        random1 = Cat(parent1=parent.ID)
        random1.status = "warrior"
        random2 = Cat()
        random2.status = "warrior"
        abbreviations_cat_id={
            "m_c": main_cat.ID,
            "r_c1": random1.ID,
            "r_c2": random2.ID
        }
        # given - relationships
        # order: romantic, platonic, dislike, admiration, comfortable, jealousy, trust
        main_cat.relationships[random1.ID] = Relationship(
            main_cat, random1, False, False, 50, 50, 0, 50, 50, 0, 50
        )
        random1.relationships[main_cat.ID] = Relationship(
            random1, main_cat, False, False, 50, 50, 0, 50, 50, 0, 50
        )

        main_cat.relationships[random2.ID] = Relationship(
            main_cat, random2, False, True, 0, 0, 50, 0, 0, 50, 0
        )
        random2.relationships[main_cat.ID] = Relationship(
            random2, main_cat, False, True, 0, 0, 50, 0, 0, 50, 0
        )


        random1.mate.append(random2.ID)
        random2.mate.append(random1.ID)
        random1.relationships[random2.ID] = Relationship(
            random1, random2, True, False, 50, 50, 0, 0, 0, 0, 50
        )
        random2.relationships[random1.ID] = Relationship(
            random2, random1, True, False, 50, 50, 0, 0, 0, 0, 0
        )

        # summary: 
        #    - random1 and random2 are mates
        #    - random2 and main_cat are siblings
        #    - main_cat has a crush on the siblings mate (random1) + vise versa
        #    - main_cat don't like their sibling because of the crush (random2)
        #    - random2 don't trust their mate (random1) because of sibling (main_cat)

        # given - interactions
        interaction1 = Group_Interaction("test")
        interaction1.relationship_constraint = {
            "r_c1_to_m_c": ["dislike_40"]
        }

        interaction2 = Group_Interaction("test")
        interaction2.relationship_constraint = {
            "r_c1_to_r_c2": ["not_mates"]
        }

        interaction3 = Group_Interaction("test")
        interaction3.relationship_constraint = {
            "r_c1_to_r_c2": ["romantic_40_lower"]
        }

        interaction4 = Group_Interaction("test")
        interaction4.relationship_constraint = {
            "r_c1_to_r_c2": ["romantic_40_lower"]
        }

        interaction5 = Group_Interaction("test")
        interaction5.relationship_constraint = {
            "r_c1_to_r_c2": ["trust_40_lower"]
        }

        interaction6 = Group_Interaction("test")
        interaction6.relationship_constraint = {
            "r_c1_to_m_c": ["mates"]
        }

        interaction7 = Group_Interaction("test")
        interaction7.relationship_constraint = {
            "m_c_to_r_c1": ["comfortable_60"]
        }

        interaction8 = Group_Interaction("test")
        interaction8.relationship_constraint = {
            "m_c_to_r_c1": ["romantic_40_lower"]
        }

        interaction9 = Group_Interaction("test")
        interaction9.relationship_constraint = {
            "m_c_to_r_c1": ["comfortable_40_lower"]
        }

        interaction10 = Group_Interaction("test")
        interaction10.relationship_constraint = {
            "r_c2_to_r_c1": ["trust_40"]
        }

        # then
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction1, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction2, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction3, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction4, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction5, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction6, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction7, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction8, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction9, abbreviations_cat_id))
        self.assertFalse(Group_Events().relationship_allow_interaction(interaction10, abbreviations_cat_id))
