# Tests for localization
import unittest

import i18n
import ujson

from scripts.cat.cats import Cat
from scripts.game_structure.localization import (
    get_new_pronouns,
    determine_plural_pronouns,
    set_lang_config_directory,
)
from scripts.utility import event_text_adjust


class TestLocalisation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(
            "resources/lang/en/pronouns.en.json", "r", encoding="utf-8"
        ) as read_file:
            cls.pronouns = ujson.loads(read_file.read())["en"]

        male_cat = Cat(gender="male")
        female_cat = Cat(gender="female")
        nonbinary_cat = Cat()
        nonbinary_cat.genderalign = "nonbinary"
        mystery_cat = Cat(gender="potato")
        cls.cat_combos_two = {
            "male-male": [[male_cat, male_cat], cls.pronouns["1"]],
            "male-female": [[male_cat, female_cat], cls.pronouns["1"]],
            "male-nonbinary": [[male_cat, nonbinary_cat], cls.pronouns["1"]],
            "female-male": [[female_cat, male_cat], cls.pronouns["1"]],
            "female-female": [[female_cat, female_cat], cls.pronouns["2"]],
            "female-nonbinary": [[female_cat, nonbinary_cat], cls.pronouns["2"]],
            "nonbinary-male": [[nonbinary_cat, male_cat], cls.pronouns["1"]],
            "nonbinary-female": [[nonbinary_cat, female_cat], cls.pronouns["2"]],
            "nonbinary-nonbinary": [[nonbinary_cat, nonbinary_cat], cls.pronouns["0"]],
            "unknown": [[mystery_cat, mystery_cat], cls.pronouns["0"]],
        }

    def tearDown(self):
        i18n.config.set("locale", "en")
        set_lang_config_directory("resources/lang/en/config.json")

    def test_get_singular_pronouns(self):
        for i, gender in enumerate(["nonbinary", "male", "female"]):
            with self.subTest("get pronouns", gender=gender):
                self.assertDictEqual(self.pronouns[str(i)], get_new_pronouns(gender)[0])
        for i, gender in enumerate(["trans male", "trans female"]):
            with self.subTest("get trans pronouns", gender=gender):
                self.assertDictEqual(
                    self.pronouns[str(i + 1)], get_new_pronouns(gender)[0]
                )

    def test_get_plural_pronouns(self):
        """
        Test whether getting the plural pronoun set is working as expected
        :return:
        """
        set_lang_config_directory("tests/prereqs/test_lang/plural_pronoun_config.json")

        for key, value in self.cat_combos_two.items():
            input = []
            for cat in value[0]:
                input.append(cat.pronouns[0])
            with self.subTest("two cat combination", combination=key):
                self.assertDictEqual(
                    determine_plural_pronouns(input),
                    value[1],
                )

    def test_insert_singular_pronouns(self):
        male_cat = Cat(gender="male")
        female_cat = Cat(gender="female")
        nb_cat = Cat()
        nb_cat.genderalign = "nonbinary"

        for cat in [male_cat, female_cat, nb_cat]:
            for pronoun in ["subject", "object", "poss", "inposs", "self"]:
                with self.subTest(
                    "singular pronouns", cat=cat.genderalign, pronoun=pronoun
                ):
                    text = f"{{PRONOUN/m_c/{pronoun}}}"
                    self.assertEqual(
                        event_text_adjust(Cat, text, main_cat=cat),
                        cat.pronouns[0][pronoun],
                    )

    def test_insert_plural_pronouns(self):
        set_lang_config_directory("tests/prereqs/test_lang/plural_pronoun_config.json")
        text = "{PRONOUN/PLURAL/m_c+r_c/subject}"
        for key, value in self.cat_combos_two.items():
            with self.subTest("plural pronouns", combination=key):
                self.assertEqual(
                    event_text_adjust(
                        Cat, text, main_cat=value[0][0], random_cat=value[0][1]
                    ),
                    value[1]["subject"],
                )
