import unittest

from scripts.cat.cats import Cat
from scripts.cat.enums.status import Status


class TestCatStatus(unittest.TestCase):

    def test_newborn(self):
        test_cat = Cat(status=Status.NEWBORN)
        self.assertEqual(test_cat.status, Status.NEWBORN)
        self.assertTrue(test_cat.status.is_kit_any())
    def test_kitten(self):
        test_cat = Cat(status=Status.KITTEN)
        self.assertEqual(test_cat.status, Status.KITTEN)

        self.assertTrue(test_cat.status.is_kit_any())
    def test_apprentice(self):
        test_cat = Cat(status=Status.APP)
        self.assertEqual(test_cat.status, Status.APP)

        self.assertTrue(test_cat.status.is_apprentice_any)
        self.assertTrue(test_cat.status.is_warrior_any)
    def test_medcat_apprentice(self):
        test_cat = Cat(status=Status.MEDCATAPP)
        self.assertEqual(test_cat.status, Status.MEDCATAPP)

        self.assertTrue(test_cat.status.is_apprentice_any())
        self.assertTrue(test_cat.status.is_medcat_any())
    def test_mediator_apprentice(self):
        test_cat = Cat(status=Status.MEDIATORAPP)
        self.assertEqual(test_cat.status, Status.MEDIATORAPP)

        self.assertTrue(test_cat.status.is_apprentice_any())
        self.assertTrue(test_cat.status.is_mediator_any())
    def test_warrior(self):
        test_cat = Cat(status=Status.WARRIOR)
        self.assertEqual(test_cat.status, Status.WARRIOR)

        self.assertTrue(test_cat.status.is_warrior_any)

        self.assertFalse(test_cat.status.is_apprentice_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_medcat(self):
        test_cat = Cat(status=Status.MEDCAT)
        self.assertEqual(test_cat.status, Status.MEDCAT)

        self.assertTrue(test_cat.status.is_medcat_any())

        self.assertFalse(test_cat.status.is_apprentice_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_warrior_any())

    def test_deputy(self):
        test_cat = Cat(status=Status.DEPUTY)
        self.assertEqual(test_cat.status, Status.DEPUTY)

        self.assertTrue(test_cat.status.is_warrior_any)
        self.assertTrue(test_cat.status.is_deputy_or_leader())

        self.assertFalse(test_cat.status.is_apprentice_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_leader(self):
        test_cat = Cat(status=Status.LEADER)
        self.assertEqual(test_cat.status, Status.LEADER)

        self.assertTrue(test_cat.status.is_warrior_any)
        self.assertTrue(test_cat.status.is_deputy_or_leader())

        self.assertFalse(test_cat.status.is_apprentice_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())

    def test_elder(self):
        test_cat = Cat(status=Status.ELDER)
        self.assertEqual(test_cat.status, Status.ELDER)

        self.assertFalse(test_cat.status.is_kit_any())
        self.assertFalse(test_cat.status.is_apprentice_any())
        self.assertFalse(test_cat.status.is_warrior_any())
        self.assertFalse(test_cat.status.is_mediator_any())
        self.assertFalse(test_cat.status.is_medcat_any())





if __name__ == '__main__':
    unittest.main()
