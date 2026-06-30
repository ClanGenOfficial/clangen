import unittest


class TestNewCatCreation(unittest.TestCase):
    # This is just for testing the `updated_new_cat_creation` func

    def test_status_assignment(self):
        # test various rank assignments

        # test that age is being assigned, especially for babies

        # test that group IDs are being given correctly

        # test that past statuses are applied

        # test that past and current standings are applied

        pass

    def test_litter_creation(self):
        # test that multiple cats are made for a litter

        # test that they are all counted as littermates

        # test that they have established relationships

        pass

    def test_gender_assignment(self):
        # test male works

        # test female works

        # test that can_birth works with the toggle

        pass

    def test_mate_assignment(self):
        # test that a single mate can be assigned

        # test that multiple can be assigned

        # test that they have established relationships

        pass

    def test_stat_assignment(self):
        # test that a trait can be chosen

        # test that a skill can be chosen

        # test that both can be chosen

        # test that when both are given but both are not required, that only one is chosen

        pass

    def test_health_assignment(self):
        # test that injury is applied

        # test that illness is applied

        # test that perm condition is applied and can be congenital/not congenital

        # test scar application for missing limbs

        pass

    def test_backstory_assignment(self):
        # test that a category can be used for assignment

        # test that normal names can be used

        # test that various socials get appropriate backstories when no specific backstory was applied

        pass

    def test_name_assignment(self):
        # test that non-clan cats only get a prefix

        # test that clan cats get a full clan name

        pass
