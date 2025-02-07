import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.cat.skills import SkillPath, Skill
from scripts.cat_relations.interaction import (
    SingleInteraction,
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints
)


class RelationshipConstraints(unittest.TestCase):
    def test_siblings(self):
        # given
        parent = Cat()
        cat_from = Cat(parent1=parent.ID)
        cat_to = Cat(parent1=parent.ID)
        rel = Relationship(cat_from, cat_to, False, True)
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["sibling"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["not_mates"], "test"))

    def test_mates(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        cat_from.mate.append(cat_to.ID)
        cat_to.mate.append(cat_from.ID)
        rel = Relationship(cat_from, cat_to, True, False)
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["mates"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["not_mates"], "test"))

    def test_parent_child_combo(self):
        # given
        parent = Cat()
        child = Cat(parent1=parent.ID)

        child_parent_rel = Relationship(child, parent, False, True)
        parent_child_rel = Relationship(parent, child, False, True)
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(child_parent_rel, ["child/parent"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(child_parent_rel, ["parent/child"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(parent_child_rel, ["parent/child"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(parent_child_rel, ["child/parent"], "test"))

    def test_rel_values_above(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        rel = Relationship(cat_from, cat_to)
        rel.romantic_love = 50
        rel.platonic_like = 50
        rel.dislike = 50
        rel.comfortable = 50
        rel.jealousy = 50
        rel.trust = 50
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["romantic_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["romantic_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["platonic_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["platonic_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["comfortable_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["comfortable_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["jealousy_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["jealousy_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["trust_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["trust_60"], "test"))

    def test_rel_values_under(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        rel = Relationship(cat_from, cat_to)
        rel.romantic_love = 50
        rel.platonic_like = 50
        rel.dislike = 50
        rel.comfortable = 50
        rel.jealousy = 50
        rel.trust = 50
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["romantic_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["romantic_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["platonic_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["platonic_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["comfortable_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["comfortable_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["jealousy_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["jealousy_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["trust_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["trust_30_lower"], "test"))


class SingleInteractionCatConstraints(unittest.TestCase):
    def test_status(self):
        # given
        warrior = Cat()
        warrior.status = "warrior"
        medicine = Cat()
        medicine.status = "medicine cat"

        # when
        warrior_to_all = SingleInteraction("test")
        warrior_to_all.main_status_constraint = ["warrior"]
        warrior_to_all.random_status_constraint = ["warrior", "medicine cat"]

        warrior_to_warrior = SingleInteraction("test")
        warrior_to_warrior.main_status_constraint = ["warrior"]
        warrior_to_warrior.random_status_constraint = ["warrior"]

        medicine_to_warrior = SingleInteraction("test")
        medicine_to_warrior.main_status_constraint = ["medicine cat"]
        medicine_to_warrior.random_status_constraint = ["warrior"]

        # then
        for game_mode in ["classic", "expanded", "cruel season"]:
            self.assertTrue(cats_fulfill_single_interaction_constraints(
                warrior, warrior, warrior_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(
                warrior, warrior, warrior_to_warrior, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(
                warrior, warrior, medicine_to_warrior, game_mode))

            self.assertTrue(cats_fulfill_single_interaction_constraints(
                warrior, medicine, warrior_to_all, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(
                warrior, medicine, warrior_to_warrior, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(
                warrior, medicine, medicine_to_warrior, game_mode))

            self.assertFalse(cats_fulfill_single_interaction_constraints(
                medicine, warrior, warrior_to_all, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(
                medicine, warrior, warrior_to_warrior, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(
                medicine, warrior, medicine_to_warrior, game_mode))

    def test_trait(self):
        # given
        calm = Cat()
        calm.personality.trait = "calm"
        troublesome = Cat()
        troublesome.personality.trait = "troublesome"

        # when
        calm_to_all = SingleInteraction("test")
        calm_to_all.main_trait_constraint = ["calm"]
        calm_to_all.random_trait_constraint = []

        all_to_calm = SingleInteraction("test")
        all_to_calm.main_trait_constraint = ["troublesome", "calm"]
        all_to_calm.random_trait_constraint = ["calm"]

        # then
        for game_mode in ["classic", "expanded", "cruel season"]:
            self.assertTrue(cats_fulfill_single_interaction_constraints(calm, troublesome, calm_to_all, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(calm, troublesome, all_to_calm, game_mode))

            self.assertFalse(cats_fulfill_single_interaction_constraints(troublesome, calm, calm_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(troublesome, calm, all_to_calm, game_mode))

            self.assertTrue(cats_fulfill_single_interaction_constraints(calm, calm, calm_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(calm, calm, all_to_calm, game_mode))

    def test_skill(self):
        # given
        hunter = Cat()
        hunter.skills.primary = Skill(SkillPath.HUNTER, points=9)
        fighter = Cat()
        fighter.skills.primary = Skill(SkillPath.FIGHTER, points=9)

        # when
        hunter_to_all = SingleInteraction("test")
        hunter_to_all.main_skill_constraint = ["good hunter"]
        hunter_to_all.random_skill_constraint = []

        all_to_hunter = SingleInteraction("test")
        all_to_hunter.main_skill_constraint = ["good fighter", "good hunter"]
        all_to_hunter.random_skill_constraint = ["good hunter"]

        # then
        for game_mode in ["classic", "expanded", "cruel season"]:
            self.assertTrue(cats_fulfill_single_interaction_constraints(hunter, fighter, hunter_to_all, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(hunter, fighter, all_to_hunter, game_mode))

            self.assertFalse(cats_fulfill_single_interaction_constraints(fighter, hunter, hunter_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(fighter, hunter, all_to_hunter, game_mode))

            self.assertTrue(cats_fulfill_single_interaction_constraints(hunter, hunter, hunter_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(hunter, hunter, all_to_hunter, game_mode))

    def test_background(self):
        # given
        clan = Cat()
        clan.backstory = "clanborn"
        half = Cat()
        half.backstory = "halfclan1"

        # when
        clan_to_all = SingleInteraction("test")
        clan_to_all.backstory_constraint = {
            "m_c": ["clanborn"]
        }

        all_to_clan = SingleInteraction("test")
        all_to_clan.backstory_constraint = {
            "m_c": ["halfclan1", "clanborn"],
            "r_c": ["clanborn"]
        }

        # then
        for game_mode in ["classic", "expanded", "cruel season"]:
            self.assertTrue(cats_fulfill_single_interaction_constraints(clan, half, clan_to_all, game_mode))
            self.assertFalse(cats_fulfill_single_interaction_constraints(clan, half, all_to_clan, game_mode))

            self.assertFalse(cats_fulfill_single_interaction_constraints(half, clan, clan_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(half, clan, all_to_clan, game_mode))

            self.assertTrue(cats_fulfill_single_interaction_constraints(clan, clan, clan_to_all, game_mode))
            self.assertTrue(cats_fulfill_single_interaction_constraints(clan, clan, all_to_clan, game_mode))
