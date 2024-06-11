import unittest

from scripts.cat.cats import Cat
from scripts.cat.enums.status import StatusEnum


class TestCatStatus(unittest.TestCase):

    def test_newborn(self):
        test_cat = Cat(status=StatusEnum.NEWBORN)
        self.assertEqual(test_cat.status, StatusEnum.NEWBORN)
        self.assertTrue(test_cat.status.is_kit_any())

    def test_kitten(self):
        test_cat = Cat(status=StatusEnum.KITTEN)
        self.assertEqual(test_cat.status, StatusEnum.KITTEN)

        self.assertTrue(test_cat.status.is_kit_any())

    def test_apprentice(self):
        test_cat = Cat(status=StatusEnum.WARRIORAPP)
        self.assertEqual(test_cat.status, StatusEnum.WARRIORAPP)

        self.assertTrue(test_cat.status.is_app_any)
        self.assertTrue(test_cat.status.is_warrior_any)

    def test_medcat_apprentice(self):
        test_cat = Cat(status=StatusEnum.MEDCATAPP)
        self.assertEqual(test_cat.status, StatusEnum.MEDCATAPP)

        self.assertTrue(test_cat.status.is_app_any())
        self.assertTrue(test_cat.status.is_medcat_any())

    def test_mediator_apprentice(self):
        test_cat = Cat(status=StatusEnum.MEDIATORAPP)
        self.assertEqual(test_cat.status, StatusEnum.MEDIATORAPP)

        self.assertTrue(test_cat.status.is_app_any())
        self.assertTrue(test_cat.status.is_mediator_any())

    def test_warrior(self):
        test_cat = Cat(status=StatusEnum.WARRIOR)
        self.assertEqual(test_cat.status, StatusEnum.WARRIOR)

        self.assertTrue(test_cat.status.is_warrior_any)

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_medcat(self):
        test_cat = Cat(status=StatusEnum.MEDCAT)
        self.assertEqual(test_cat.status, StatusEnum.MEDCAT)

        self.assertTrue(test_cat.status.is_medcat_any())

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_warrior_any())

    def test_deputy(self):
        test_cat = Cat(status=StatusEnum.DEPUTY)
        self.assertEqual(test_cat.status, StatusEnum.DEPUTY)

        self.assertTrue(test_cat.status.is_warrior_any)
        self.assertTrue(test_cat.status.is_deputy_or_leader())

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_leader(self):
        test_cat = Cat(status=StatusEnum.LEADER)
        self.assertEqual(test_cat.status, StatusEnum.LEADER)

        self.assertTrue(test_cat.status.is_warrior_any)
        self.assertTrue(test_cat.status.is_deputy_or_leader())

        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_elder(self):
        test_cat = Cat(status=StatusEnum.ELDER)
        self.assertEqual(test_cat.status, StatusEnum.ELDER)

        self.assertFalse(test_cat.status.is_kit_any())
        self.assertFalse(test_cat.status.is_app_any())
        self.assertFalse(test_cat.status.is_warrior_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())


if __name__ == '__main__':
    unittest.main()
