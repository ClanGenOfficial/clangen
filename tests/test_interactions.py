import os
import unittest

from scripts.cat_relations.enums import rel_type_tiers

from scripts.cat.enums import CatRank

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.cat.skills import SkillPath, Skill
from scripts.cat_relations.interaction import (
    SingleInteraction,
    cats_fulfill_single_interaction_constraints,
)


class RelationshipConstraints(unittest.TestCase):
    def test_siblings(self):
        # given
        parent = Cat()
        cat_from = Cat(parent1=parent.ID)
        cat_to = Cat(parent1=parent.ID)
        rel = Relationship(cat_from, cat_to, False, True)

        # then
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(rel, ["sibling"], "test")
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(rel, ["not_mates"], "test")
        )

    def test_mates(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        cat_from.mate.append(cat_to.ID)
        cat_to.mate.append(cat_from.ID)
        rel = Relationship(cat_from, cat_to, True, False)

        # then
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(rel, ["mates"], "test")
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(rel, ["not_mates"], "test")
        )

    def test_parent_child_combo(self):
        # given
        parent = Cat()
        child = Cat(parent1=parent.ID)

        child_parent_rel = Relationship(child, parent, False, True)
        parent_child_rel = Relationship(parent, child, False, True)

        # then
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(
                child_parent_rel, ["child/parent"], "test"
            )
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                child_parent_rel, ["parent/child"], "test"
            )
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(
                parent_child_rel, ["parent/child"], "test"
            )
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                parent_child_rel, ["child/parent"], "test"
            )
        )

    def test_rel_values_only_constraint_pos(self):
        # given
        cat_from1 = Cat()
        cat_to1 = Cat()
        low_rel = Relationship(cat_from1, cat_to1)
        low_rel.romance = 10
        low_rel.like = 10
        low_rel.comfort = 10
        low_rel.trust = 10
        low_rel.respect = 10

        cat_from2 = Cat()
        cat_to2 = Cat()
        mid_rel = Relationship(cat_from2, cat_to2)
        mid_rel.romance = 50
        mid_rel.like = 50
        mid_rel.comfort = 50
        mid_rel.trust = 50
        mid_rel.respect = 50

        cat_from3 = Cat()
        cat_to3 = Cat()
        high_rel = Relationship(cat_from3, cat_to3)
        high_rel.romance = 90
        high_rel.like = 90
        high_rel.comfort = 90
        high_rel.trust = 90
        high_rel.respect = 90
        # then
        for level_list in rel_type_tiers.values():
            for l in level_list:
                # last index of the list should be the highest positive
                if l == level_list[-1]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            mid_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            low_rel, [f"{l}_only"], "test"
                        )
                    )
                # next is middle pos
                elif l == level_list[-2]:
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            mid_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            low_rel, [f"{l}_only"], "test"
                        )
                    )
                # next is the lowest pos
                elif l == level_list[-3]:
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            mid_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            low_rel, [f"{l}_only"], "test"
                        )
                    )

    def test_rel_values_only_constraint_neg(self):
        # given
        cat_from1 = Cat()
        cat_to1 = Cat()
        mid_rel = Relationship(cat_from1, cat_to1)
        mid_rel.romance = -50
        mid_rel.like = -50
        mid_rel.comfort = -50
        mid_rel.trust = -50

        cat_from2 = Cat()
        cat_to2 = Cat()
        low_rel = Relationship(cat_from2, cat_to2)
        low_rel.romance = -10
        low_rel.like = -10
        low_rel.comfort = -10
        low_rel.trust = -10

        cat_from3 = Cat()
        cat_to3 = Cat()
        high_rel = Relationship(cat_from3, cat_to3)
        high_rel.romance = -90
        high_rel.like = -90
        high_rel.comfort = -90
        high_rel.trust = -90

        for level_list in rel_type_tiers.values():
            for l in level_list:
                # first index of the list should be the highest negative
                if l == level_list[0]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            mid_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            low_rel, [f"{l}_only"], "test"
                        )
                    )
                # next is middle negative
                elif l == level_list[1]:
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            mid_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            low_rel, [f"{l}_only"], "test"
                        )
                    )
                # next is the lowest neg
                elif l == level_list[2]:
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertFalse(
                        cats_fulfill_single_interaction_constraints(
                            mid_rel, [f"{l}_only"], "test"
                        )
                    )
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            low_rel, [f"{l}_only"], "test"
                        )
                    )

    def test_rel_values_ranged_constraint(self):
        # given
        # pos side
        cat_from1 = Cat()
        cat_to1 = Cat()
        high_rel = Relationship(cat_from1, cat_to1)
        high_rel.romance = 90
        high_rel.like = 90
        high_rel.comfort = 90
        high_rel.trust = 90
        high_rel.respect = 90

        # neg side
        cat_from1 = Cat()
        cat_to1 = Cat()
        high_rel = Relationship(cat_from1, cat_to1)
        high_rel.romance = -90
        high_rel.like = -90
        high_rel.comfort = -90
        high_rel.trust = -90
        high_rel.respect = -90

        # then
        # pos test
        for level_list in rel_type_tiers.values():
            for level in level_list:
                # last index of the list should be the highest positive
                if level == level_list[-1]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{level}"], "test"
                        )
                    )
                # next is middle pos
                elif level == level_list[-2]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{level}"], "test"
                        )
                    )
                # next is the lowest pos
                elif level == level_list[-3]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{level}"], "test"
                        )
                    )

        # neg test
        for level_list in rel_type_tiers.values():
            for level in level_list:
                # first index of the list should be the highest positive
                if level == level_list[0]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{level}"], "test"
                        )
                    )
                # next is middle pos
                elif level == level_list[1]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{level}"], "test"
                        )
                    )
                # next is the lowest pos
                elif level == level_list[2]:
                    self.assertTrue(
                        cats_fulfill_single_interaction_constraints(
                            high_rel, [f"{level}"], "test"
                        )
                    )


class SingleInteractionCatConstraints(unittest.TestCase):
    def test_status(self):
        # given
        warrior = Cat(status_dict={"rank": CatRank.WARRIOR})
        medicine = Cat(status_dict={"rank": CatRank.MEDICINE_CAT})

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
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(
                warrior, warrior, warrior_to_all
            )
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(
                warrior, warrior, warrior_to_warrior
            )
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                warrior, warrior, medicine_to_warrior
            )
        )

        self.assertTrue(
            cats_fulfill_single_interaction_constraints(
                warrior, medicine, warrior_to_all
            )
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                warrior, medicine, warrior_to_warrior
            )
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                warrior, medicine, medicine_to_warrior
            )
        )

        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                medicine, warrior, warrior_to_all
            )
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(
                medicine, warrior, warrior_to_warrior
            )
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(
                medicine, warrior, medicine_to_warrior
            )
        )

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
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(calm, troublesome, calm_to_all)
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(calm, troublesome, all_to_calm)
        )

        self.assertFalse(
            cats_fulfill_single_interaction_constraints(troublesome, calm, calm_to_all)
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(troublesome, calm, all_to_calm)
        )

        self.assertTrue(
            cats_fulfill_single_interaction_constraints(calm, calm, calm_to_all)
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(calm, calm, all_to_calm)
        )

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
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(hunter, fighter, hunter_to_all)
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(hunter, fighter, all_to_hunter)
        )

        self.assertFalse(
            cats_fulfill_single_interaction_constraints(fighter, hunter, hunter_to_all)
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(fighter, hunter, all_to_hunter)
        )

        self.assertTrue(
            cats_fulfill_single_interaction_constraints(hunter, hunter, hunter_to_all)
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(hunter, hunter, all_to_hunter)
        )

    def test_background(self):
        # given
        clan = Cat()
        clan.backstory = "clanborn"
        half = Cat()
        half.backstory = "halfclan1"

        # when
        clan_to_all = SingleInteraction("test")
        clan_to_all.backstory_constraint = {"m_c": ["clanborn"]}

        all_to_clan = SingleInteraction("test")
        all_to_clan.backstory_constraint = {
            "m_c": ["halfclan1", "clanborn"],
            "r_c": ["clanborn"],
        }

        # then
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(clan, half, clan_to_all)
        )
        self.assertFalse(
            cats_fulfill_single_interaction_constraints(clan, half, all_to_clan)
        )

        self.assertFalse(
            cats_fulfill_single_interaction_constraints(half, clan, clan_to_all)
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(half, clan, all_to_clan)
        )

        self.assertTrue(
            cats_fulfill_single_interaction_constraints(clan, clan, clan_to_all)
        )
        self.assertTrue(
            cats_fulfill_single_interaction_constraints(clan, clan, all_to_clan)
        )
