from unittest import TestCase

from scripts.constraintbooster.constraintbooster import ConstraintBooster
from scripts.patrol.patrol import PatrolEvent
from scripts.patrol.patrol_outcome import PatrolOutcome


class TestConstraintBooster(TestCase):
    def setUp(self):
        self.test_item = PatrolEvent(
            "bch_med_greenleaf_daisy_lorestoryhealinglocked1",
            biome=["any", "Mountainous"],
            pl_skill_constraints=["LORE,1", "HEALER3", "2,FORBIDDEN", ",SNACC,2"],
            success_outcomes=[PatrolOutcome()] * 3,
        )

        self.options = [self.test_item]

    def test_get_choice(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")
        items = [self.test_item] * 3

        result = booster.get_choice(items)

        self.assertIn(result, items)

    def test_get_choice_flat(self):
        # This is essentially the above test, but forcing it to
        # run as though all the priority rolls failed
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")
        items = [self.test_item] * 3

        result = booster.get_choice(items, debug_force_flat=True)

        self.assertIn(result, items)


class TestConstraintBoosterSimpleConstraint(TestCase):
    def setUp(self):
        self.test_item = PatrolEvent(
            "bch_med_greenleaf_daisy_lorestoryhealinglocked1",
            biome=["any"],
            pl_skill_constraints=["LORE,1", "HEALER3", "2,FORBIDDEN", ",SNACC,2"],
            success_outcomes=[PatrolOutcome()] * 3,
        )

        self.options = [self.test_item]

    def test_add_simple(self):
        booster = ConstraintBooster()

        booster.add_simple_constraint("biome")

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(1, result.keys())

    def test_simple_missing(self):
        booster = ConstraintBooster()

        booster.add_simple_constraint("not_a_value")

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(0, result.keys())

    def test_simple_blacklist(self):
        booster = ConstraintBooster()

        booster.add_simple_constraint("biome", ["any"])

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(0, result.keys())


class TestConstraintBoosterNestedConstraint(TestCase):
    def setUp(self):
        self.test_item = PatrolEvent(
            "bch_med_greenleaf_daisy_lorestoryhealinglocked1",
            biome=["any", "Mountainous"],
            pl_skill_constraints=["LORE,1", "HEALER3", "2,FORBIDDEN", ",SNACC,2"],
            success_outcomes=[PatrolOutcome()] * 3,
        )

        self.options = [self.test_item]

    def test_add_nested_constraint(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("pl_skill_constraints")

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(4, result.keys())

    def test_add_nested_missing(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("not_a_value")

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(0, result.keys())

    def test_add_nested_blacklist(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("pl_skill_constraints", ["2,FORBIDDEN"])

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(3, result.keys())


class TestConstraintBoosterSplitConstraint(TestCase):
    def setUp(self):
        self.test_item = PatrolEvent(
            "bch_med_greenleaf_daisy_lorestoryhealinglocked1",
            biome=["any", "Mountainous"],
            pl_skill_constraints=["LORE,1", "HEALER3", "2,FORBIDDEN", ",SNACC,2"],
            success_outcomes=[PatrolOutcome()] * 3,
        )

        self.options = [self.test_item]

    def test_add_split_constraint(self):
        booster = ConstraintBooster()
        point_array = {"1": 1, "2": 2, "3": 3, "4": 4}
        booster.add_split_constraint("pl_skill_constraints", ",", 1, point_array)

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(1, result.keys())

    def test_add_split_missing(self):
        booster = ConstraintBooster()
        point_array = {"1": 1, "2": 2, "3": 3, "4": 4}
        booster.add_split_constraint("not_a_record", ",", 1, point_array)

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(0, result.keys())

    def test_add_split_blacklist(self):
        booster = ConstraintBooster()
        point_array = {"1": 1, "2": 2, "3": 3, "4": 4}
        booster.add_split_constraint(
            "pl_skill_constraints", ",", 1, point_array, blacklist={"HEALER3": 3}
        )

        result = dict(booster._get_constraint_points(self.options))

        self.assertIn(4, result.keys())


class TestConstraintBoosterMakeGroups(TestCase):
    def setUp(self):
        self.test_item1 = {
            "test_basic": ["1", "2", "3"],
            "test_nested": ["1", "2", "3"],
            "test_split": ["word,1", "2,word", "word3", "word,sad"],
        }
        self.test_item2 = {
            "test_basic": ["1", "2", "3"],
            "test_nested": ["1", "2", "3", "4", "5"],
            "test_split": ["word,1", "2,word", "word3", "word,sad"],
        }
        self.test_item3 = {
            "test_basic": ["1", "2", "3"],
            "test_nested": ["1", "2", "3", "4", "5", "6", "7"],
            "test_split": ["word,1", "2,word", "word3", "word,sad"],
        }

    def test_base(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")
        items = [
            self.test_item1
        ] * 12  # making 12 of the same item because it divides evenly

        items_zip = booster._get_constraint_points(items)
        groups = booster._make_groups(items_zip)

        self.assertEqual(len(groups), 3)
        for i, groups in enumerate(groups):
            with self.subTest("group size", group=i):
                self.assertEqual(len(groups), 4)

    def test_tiered(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")

        # making 12 items because it divides evenly
        items = [self.test_item1] * 10
        extra = [self.test_item2] * 2
        items = items + extra

        items_zip = booster._get_constraint_points(items)
        groups = booster._make_groups(items_zip)

        self.assertEqual(len(groups), 3)

        self.assertIn(self.test_item2, groups[0])
        self.assertNotIn(self.test_item2, groups[1])
        self.assertNotIn(self.test_item2, groups[2])

        for i, groups in enumerate(groups):
            with self.subTest("group size", group=i):
                self.assertEqual(len(groups), 4)

    def test_exactly_enough_items(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")
        # making 3 of the same item because it divides evenly
        items = [self.test_item1] * 3

        items_zip = booster._get_constraint_points(items)
        groups = booster._make_groups(items_zip)

        self.assertEqual(len(groups), 3)
        for i, groups in enumerate(groups):
            with self.subTest("group size", group=i):
                self.assertEqual(len(groups), 1)

    def test_not_enough_items(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")

        items = [self.test_item1] * 2

        items_zip = booster._get_constraint_points(items)
        groups = booster._make_groups(items_zip)

        self.assertEqual(len(groups), 2)

    def test_non_divisible_group(self):
        booster = ConstraintBooster()
        booster.add_nested_constraint("test_nested")

        items = [self.test_item1] * 7

        items_zip = booster._get_constraint_points(items)
        groups = booster._make_groups(items_zip)

        self.assertEqual(len(groups), 3)
        self.assertEqual(len(groups[2]), 3)
        for group in groups[0:2]:
            self.assertEqual(len(group), 2)
