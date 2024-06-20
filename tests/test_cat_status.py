import unittest

from scripts.cat import enums
from scripts.cat.cats import Cat


class TestCatStatus(unittest.TestCase):

    def test_newborn(self):
        test_cat = Cat(status=enums.Status.NEWBORN)
        self.assertEqual(test_cat.status, enums.Status.NEWBORN)
        self.assertTrue(test_cat.status.is_kit_any())

    def test_kitten(self):
        test_cat = Cat(status=enums.Status.KITTEN)
        self.assertEqual(test_cat.status, enums.Status.KITTEN)

        self.assertTrue(test_cat.status.is_kit_any())

    def test_apprentice(self):
        test_cat = Cat(status=enums.Status.WARRIORAPP)
        self.assertEqual(test_cat.status, enums.Status.WARRIORAPP)

        self.assertTrue(test_cat.status.is_app_any)
        self.assertTrue(test_cat.status.is_warrior_any)

    def test_medcat_apprentice(self):
        test_cat = Cat(status=enums.Status.MEDCATAPP)
        self.assertEqual(test_cat.status, enums.Status.MEDCATAPP)

        self.assertTrue(test_cat.status.is_app_any())
        self.assertTrue(test_cat.status.is_medcat_any())

    def test_mediator_apprentice(self):
        test_cat = Cat(status=enums.Status.MEDIATORAPP)
        self.assertEqual(test_cat.status, enums.Status.MEDIATORAPP)

        self.assertTrue(test_cat.status.is_app_any())
        self.assertTrue(test_cat.status.is_mediator_any())

    def test_warrior(self):
        test_cat = Cat(status=enums.Status.WARRIOR)
        self.assertEqual(test_cat.status, enums.Status.WARRIOR)

        self.assertTrue(test_cat.status.is_warrior_any)

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_medcat(self):
        test_cat = Cat(status=enums.Status.MEDCAT)
        self.assertEqual(test_cat.status, enums.Status.MEDCAT)

        self.assertTrue(test_cat.status.is_medcat_any())

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_warrior_any())

    def test_deputy(self):
        test_cat = Cat(status=enums.Status.DEPUTY)
        self.assertEqual(test_cat.status, enums.Status.DEPUTY)

        self.assertTrue(test_cat.status.is_warrior_any)
        self.assertTrue(test_cat.status.is_deputy_or_leader())

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_leader(self):
        test_cat = Cat(status=enums.Status.LEADER)
        self.assertEqual(test_cat.status, enums.Status.LEADER)

        self.assertTrue(test_cat.status.is_warrior_any)
        self.assertTrue(test_cat.status.is_deputy_or_leader())

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_elder(self):
        test_cat = Cat(status=enums.Status.ELDER)
        self.assertEqual(test_cat.status, enums.Status.ELDER)

        self.assertFalse(test_cat.status.is_kit_any())
        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_warrior_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())


if __name__ == '__main__':
    unittest.main()
