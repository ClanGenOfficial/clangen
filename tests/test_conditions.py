import unittest

from scripts.cat.conditions.condition_state import ConditionState
from scripts.cat.conditions.coverage_check import medicine_cats_can_cover_clan
from scripts.cat.conditions.gain_conditions import (
    gain_temporary_condition,
    gain_permanent_condition,
)
from scripts.cat.constants import TEMPORARY_CONDITIONS, PERMANENT_CONDITIONS
from scripts.cat.enums import CatRank
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.events_module.condition import handle_existing_conditions
from scripts.events_module.condition.handle_existing_conditions import (
    handle_temporary_conditions,
    handle_permanent_conditions,
)

cat_factory = TestCatFactory()


class TestsMedCondition(unittest.TestCase):
    def test_fulfilled(self):
        cat1 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )
        med = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.MEDICINE_CAT},
            disable_random=True,
        )

        all_cats = [cat1, med]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats))

    def test_fulfilled_many_cats(self):
        cat1 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )
        cat2 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )
        cat3 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )
        cat4 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )

        med1 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.MEDICINE_CAT},
            disable_random=True,
        )
        med2 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.MEDICINE_CAT},
            disable_random=True,
        )

        all_cats = [cat1, cat2, cat3, cat4, med1, med2]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats))

    def test_injured_fulfilled(self):
        cat1 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )

        med = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.MEDICINE_CAT},
            disable_random=True,
        )
        gain_temporary_condition(med, "small_cut")

        all_cats = [cat1, med]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats))

    def test_illness_fulfilled(self):
        cat1 = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.WARRIOR},
            disable_random=True,
        )

        med = cat_factory.create_cat(
            moons=20,
            status_dict={"rank": CatRank.MEDICINE_CAT},
            disable_random=True,
        )
        gain_temporary_condition(med, "running_nose")

        all_cats = [cat1, med]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats))


class TestTemporaryCondition(unittest.TestCase):
    def test_gain(self):
        for c in TEMPORARY_CONDITIONS:
            with self.subTest(f"Test gain {c}"):
                cat1 = cat_factory.create_cat()
                gain_temporary_condition(cat1, c, allow_side_effects=False)

                self.assertTrue(
                    c in cat1.temporary_conditions,
                    msg=f"{c} was not in {cat1.temporary_conditions}",
                )

    def test_state_change(self):
        """
        Tests that conditions are able to progress through their various states correctly
        """
        for c in TEMPORARY_CONDITIONS:
            if c == "pregnant":
                # this is a weird one that has very specialized behavior
                # so we skip it for this
                continue

            if TEMPORARY_CONDITIONS[c]["mortality"]:
                with self.subTest(f"Test state change (FATAL) for {c}"):
                    cat1 = cat_factory.create_cat()
                    gain_temporary_condition(cat1, c, allow_side_effects=False)

                    handle_temporary_conditions(cat1, forced_state=ConditionState.FATAL)
                    self.assertTrue(cat1.dead, msg=f"cat did not die to {c}")
                    self.assertTrue(
                        not cat1.temporary_conditions,
                        msg=f"cat's conditions were not cleared on death to {c}",
                    )

            with self.subTest(f"Test state change (HEALED) for {c}"):
                cat1 = cat_factory.create_cat()
                gain_temporary_condition(cat1, c, allow_side_effects=False)

                handle_temporary_conditions(cat1, forced_state=ConditionState.HEALED)

                self.assertFalse(
                    cat1.dead, msg=f"cat died to {c} when they should have healed"
                )
                self.assertTrue(
                    not cat1.temporary_conditions,
                    msg=f"cat's healed condition: {c}, was not removed",
                )

            with self.subTest(f"Test state change (CONTINUING: risk gain) for {c}"):
                if not TEMPORARY_CONDITIONS[c]["risks"]:
                    continue

                for r in TEMPORARY_CONDITIONS[c]["risks"]:
                    cat1 = cat_factory.create_cat()
                    gain_temporary_condition(cat1, c, allow_side_effects=False)

                    handle_existing_conditions.force_risk = r

                    handle_temporary_conditions(
                        cat1, forced_state=ConditionState.CONTINUING
                    )
                    self.assertTrue(
                        r in cat1.temporary_conditions,
                        msg=f"{r} was not in cat's conditions: {cat1.temporary_conditions}",
                    )
                    self.assertTrue(
                        c in cat1.temporary_conditions,
                        msg=f"{c} was not in cat's conditions: {cat1.temporary_conditions}",
                    )

                    if TEMPORARY_CONDITIONS[r].get("is_complication", False):
                        self.assertEqual(
                            r,
                            cat1.get_condition(c).current_complication,
                            msg=f"{r} is a complication, but was not added to {c} as such.",
                        )

                handle_existing_conditions.force_risk = ""

            with self.subTest(f"Test progression gain for {c}"):
                if not TEMPORARY_CONDITIONS[c]["progression"]:
                    continue

                for p, info in TEMPORARY_CONDITIONS[c]["progression"].items():
                    cat1 = cat_factory.create_cat()
                    gain_temporary_condition(cat1, c, allow_side_effects=False)

                    handle_existing_conditions.force_progression = p

                    handle_temporary_conditions(cat1, forced_state=info["when"])
                    self.assertTrue(
                        p in cat1.temporary_conditions + cat1.permanent_conditions,
                        msg=f"{p} was not in cat's conditions: {cat1.temporary_conditions + cat1.permanent_conditions}",
                    )
                    self.assertFalse(
                        c in cat1.temporary_conditions + cat1.permanent_conditions,
                        msg=f"{c} was not removed from cat's conditions, even though it progressed into {p}",
                    )
                handle_existing_conditions.force_progression = ""


class TestPermanentCondition(unittest.TestCase):
    def test_gain(self):
        for c in PERMANENT_CONDITIONS:
            with self.subTest(f"Test gain {c}"):
                congenital = PERMANENT_CONDITIONS[c]["can_be_congenital"]
                acquired = PERMANENT_CONDITIONS[c]["can_be_acquired"]

                if congenital:
                    cat1 = cat_factory.create_cat()
                    gain_permanent_condition(cat1, c, is_congenital=True)

                    self.assertTrue(
                        c in cat1.permanent_conditions,
                        msg=f"{c} (congenital) was not in {cat1.permanent_conditions}",
                    )
                    self.assertTrue(
                        cat1.get_condition(c).is_congenital,
                        msg=f"{c} (congenital) was not marked as congenital.",
                    )

                if acquired:
                    cat1 = cat_factory.create_cat()
                    gain_permanent_condition(cat1, c, is_congenital=False)

                    self.assertTrue(
                        c in cat1.permanent_conditions,
                        msg=f"{c} (acquired) was not in {cat1.permanent_conditions}",
                    )
                    self.assertFalse(
                        cat1.get_condition(c).is_congenital,
                        msg=f"{c} (acquired) was marked as congenital.",
                    )

    def test_state_change(self):
        """
        Tests that conditions are able to progress through their various states correctly
        """
        for c in PERMANENT_CONDITIONS:
            if PERMANENT_CONDITIONS[c]["mortality"]:
                with self.subTest(f"Test state change (FATAL) for {c}"):
                    cat1 = cat_factory.create_cat()
                    gain_permanent_condition(cat1, c)

                    handle_permanent_conditions(cat1, forced_state=ConditionState.FATAL)
                    self.assertTrue(cat1.dead, msg=f"cat did not die to {c}")
                    self.assertTrue(
                        not cat1.temporary_conditions,
                        msg=f"cat's conditions were not cleared on death to {c}",
                    )

            if PERMANENT_CONDITIONS[c]["can_be_congenital"]:
                with self.subTest(f"Test state change (REVEALED) for {c}"):
                    cat1 = cat_factory.create_cat()
                    gain_permanent_condition(
                        cat1, c, is_congenital=True, set_moons_until=0
                    )

                    handle_permanent_conditions(cat1)

                    self.assertTrue(
                        cat1.get_condition(c).moons_until_discovery < 0,
                    )

            with self.subTest(f"Test state change (CONTINUING: risk gain) for {c}"):
                if not PERMANENT_CONDITIONS[c]["risks"]:
                    continue

                for r in PERMANENT_CONDITIONS[c]["risks"]:
                    cat1 = cat_factory.create_cat()
                    gain_permanent_condition(cat1, c)

                    handle_existing_conditions.force_risk = r
                    handle_permanent_conditions(
                        cat1, forced_state=ConditionState.CONTINUING
                    )
                    self.assertTrue(
                        r in cat1.temporary_conditions + cat1.permanent_conditions,
                        msg=f"{r} was not in cat's conditions: {cat1.temporary_conditions + cat1.permanent_conditions}",
                    )
                    self.assertTrue(
                        c in cat1.permanent_conditions,
                        msg=f"{c} was not in cat's conditions: {cat1.permanent_conditions}",
                    )

                handle_existing_conditions.force_risk = ""

            with self.subTest(f"Test progression for {c}"):
                if not PERMANENT_CONDITIONS[c]["progression"]:
                    continue

                for p, info in PERMANENT_CONDITIONS[c]["progression"].items():
                    cat1 = cat_factory.create_cat()
                    gain_permanent_condition(cat1, c)

                    handle_existing_conditions.force_progression = p

                    handle_permanent_conditions(cat1, forced_state=info["when"])
                    self.assertTrue(
                        p in cat1.temporary_conditions + cat1.permanent_conditions,
                        msg=f"{p} was not in cat's conditions: {cat1.temporary_conditions + cat1.permanent_conditions}",
                    )
                    self.assertFalse(
                        c in cat1.temporary_conditions + cat1.permanent_conditions,
                        msg=f"{c} was not removed from cat's conditions, even though it progressed into {p}",
                    )
                handle_existing_conditions.force_progression = ""
