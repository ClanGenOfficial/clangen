import unittest
from scripts.cats import Cat
from scripts.utility import get_personality_compatibility

class TestPersonalityCompatibility(unittest.TestCase):

    current_traits = [
        'adventurous', 'altruistic', 'ambitious', 'bloodthirsty', 'bold',
        'calm', 'careful', 'charismatic', 'childish', 'cold', 'compassionate',
        'confident', 'daring', 'empathetic', 'faithful', 'fierce', 'insecure',
        'lonesome', 'loving', 'loyal', 'nervous', 'patient', 'playful',
        'responsible', 'righteous', 'shameless', 'sneaky', 'strange', 'strict',
        'thoughtful', 'troublesome', 'vengeful', 'wise'
    ]

    def test_some_neutral_combinations(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = self.current_traits[0]
        cat2.trait = self.current_traits[1]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[3]
        cat2.trait = self.current_traits[5]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[7]
        cat2.trait = self.current_traits[10]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

    def test_some_positive_combinations(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = self.current_traits[1]
        cat2.trait = self.current_traits[18]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[3]
        cat2.trait = self.current_traits[4]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[5]
        cat2.trait = self.current_traits[17]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

    def test_some_negative_combinations(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = self.current_traits[1]
        cat2.trait = self.current_traits[2]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[3]
        cat2.trait = self.current_traits[6]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[8]
        cat2.trait = self.current_traits[9]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

    def test_not_existing_trait(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = 'testing'
        cat2.trait = 'testing'
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

    def test_false_trait(self):
        cat1 = Cat()
        cat2 = Cat()
        cat1.trait = None
        cat2.trait = None
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))