import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.screens.ChangeGenderScreen import ChangeGenderScreen


class TestPronounGetCases(unittest.TestCase):
    def setUp(self):
        # `pronoun_get_cases` does not touch instance state, and building a real
        # screen would require a running UI manager.
        self.screen = object.__new__(ChangeGenderScreen)

    def test_custom_pronoun_id_not_displayed(self):
        """A custom pronoun set carries an "ID" key, which is not a case."""
        pronounset = {
            "subject": "it",
            "object": "it",
            "poss": "its",
            "inposs": "its",
            "self": "itself",
            "conju": 2,
            "gender": 0,
            "ID": "custom0",
        }

        self.assertEqual(
            self.screen.pronoun_get_cases(pronounset),
            "it/it/its/its/itself",
        )

    def test_default_pronoun_cases(self):
        """A default pronoun set has no "ID" and is unaffected."""
        pronounset = {
            "subject": "they",
            "object": "them",
            "poss": "their",
            "inposs": "theirs",
            "self": "themself",
            "conju": 1,
            "gender": 0,
        }

        self.assertEqual(
            self.screen.pronoun_get_cases(pronounset),
            "they/them/their/theirs/themself",
        )
