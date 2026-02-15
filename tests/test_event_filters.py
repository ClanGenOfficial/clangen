import unittest
import os
from copy import deepcopy
from itertools import permutations

from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath, Skill

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from scripts.cat_relations.relationship import Relationship
from scripts.cat.enums import CatRank, CatAge, CatSocial
from scripts.cat.status import StatusDict
from scripts.cat_relations.enums import RelTier, rel_type_tiers, RelType

from scripts.cat.cats import Cat
import scripts.events_module.event_filters as event_filters

Cat.disable_random = True


class TestInterpersonalRelationshipConstraints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Cat.disable_random = True

    def test_siblings(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()
        cat2.create_inheritance_new_cat()

        with self.subTest("are siblings, expected siblings"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[cat1, cat2], filter_types=["siblings"]
                )
            )
        with self.subTest("are siblings, expected not siblings"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[cat1, cat2], filter_types=["-siblings"]
                )
            )
        with self.subTest("are not siblings, expected siblings"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["siblings"]
                )
            )
        with self.subTest("are not siblings, expected not siblings"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["-siblings"]
                )
            )

    def test_littermates(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID, moons=1)
        cat2 = Cat(parent1=parent.ID, moons=1)

        cat1.create_inheritance_new_cat()
        cat2.create_inheritance_new_cat()

        with self.subTest("are littermates, expected littermates"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[cat1, cat2], filter_types=["littermates"]
                )
            )
        with self.subTest("are littermates, expected not littermates"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[cat1, cat2], filter_types=["-littermates"]
                )
            )
        with self.subTest("are not littermates, expected littermates"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["littermates"]
                )
            )
        with self.subTest("are not littermates, expected not littermates"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["-littermates"]
                )
            )

    def test_mates(self):
        mate1 = Cat()
        mate2 = Cat()

        other = Cat()

        mate1.mate.append(mate2.ID)
        mate2.mate.append(mate1.ID)

        with self.subTest("are mates, expected mates"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[mate1, mate2], filter_types=["mates"]
                )
            )
        with self.subTest("are mates, expected not mates"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[mate1, mate2], filter_types=["-mates"]
                )
            )
        with self.subTest("are not mates, expected mates"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[mate1, other], filter_types=["mates"]
                )
            )
        with self.subTest("are not mates, expected not mates"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[mate1, other], filter_types=["-mates"]
                )
            )

    def test_parent_child(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()

        with self.subTest("are parent/child, expected parent/child"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[parent, cat1], filter_types=["parent/child"]
                )
            )
        with self.subTest("are parent/child, expected not parent/child"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[parent, cat1], filter_types=["-parent/child"]
                )
            )
        with self.subTest("are not parent/child, expected parent/child"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["parent/child"]
                )
            )
        with self.subTest("are not parent/child, expected not parent/child"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["-parent/child"]
                )
            )

    def test_child_parent(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()

        with self.subTest("are child/parent, expected child/parent"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["child/parent"]
                )
            )
        with self.subTest("are child/parent, expected not child/parent"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[cat1, parent], filter_types=["-child/parent"]
                )
            )
        with self.subTest("are not child/parent, expected child/parent"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[parent, cat1], filter_types=["child/parent"]
                )
            )
        with self.subTest("are not child/parent, expected not child/parent"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[parent, cat1], filter_types=["-child/parent"]
                )
            )

    def test_app_mentor(self):
        app = Cat(moons=8)
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app.update_mentor(new_mentor=mentor.ID)

        with self.subTest("are app/mentor, expected app/mentor"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[app, mentor], filter_types=["app/mentor"]
                )
            )
        with self.subTest("are app/mentor, expected not app/mentor"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[app, mentor], filter_types=["-app/mentor"]
                )
            )
        with self.subTest("are not app/mentor, expected app/mentor"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[mentor, app], filter_types=["app/mentor"]
                )
            )
        with self.subTest("are not app/mentor, expected not app/mentor"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[mentor, app], filter_types=["-app/mentor"]
                )
            )

    def test_mentor_app(self):
        app = Cat(moons=8)
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app.update_mentor(new_mentor=mentor.ID)

        with self.subTest("are mentor/app, expected mentor/app"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[mentor, app], filter_types=["mentor/app"]
                )
            )
        with self.subTest("are mentor/app, expected not mentor/app"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[mentor, app], filter_types=["-mentor/app"]
                )
            )
        with self.subTest("are not mentor/app, expected mentor/app"):
            self.assertFalse(
                event_filters.filter_relationship_type(
                    group=[app, mentor], filter_types=["mentor/app"]
                )
            )
        with self.subTest("are not mentor/app, expected not mentor/app"):
            self.assertTrue(
                event_filters.filter_relationship_type(
                    group=[app, mentor], filter_types=["-mentor/app"]
                )
            )


class TestRelationshipTiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("resources/game_config.toml", "r", encoding="utf-8") as read_file:
            config = tomllib.loads(read_file.read())

        cls.thresholds = list(config["relationship"]["value_intervals"].values())

        Cat.disable_random = True
        cls.cat1 = Cat()
        cls.cat2 = Cat()

    def tearDown(self):
        self.cat1.relationships = {}
        self.cat2.relationships = {}

    def test_full_tiers(self):
        reltypes = deepcopy(rel_type_tiers)
        reltypes.pop(RelType.ROMANCE)

        for reltype, tiers in reltypes.items():
            for i, tier in enumerate(tiers):
                with self.subTest("normal pass", tier=tier.value):
                    if tier.is_extreme_neg:
                        points = (-100 + self.thresholds[i]) / 2
                    elif tier.is_extreme_pos:
                        points = (100 + self.thresholds[i - 1]) / 2
                    else:
                        points = (self.thresholds[i - 1] + self.thresholds[i]) / 2

                    rel = {
                        "cat_from": self.cat1,
                        "cat_to": self.cat2,
                        reltype: int(points),
                    }
                    self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2], filter_types=[tier.value]
                        )
                    )

                with self.subTest("boundary pass", tier=tier.value):
                    rel = {
                        "cat_from": self.cat1,
                        "cat_to": self.cat2,
                        reltype: self.thresholds[i],
                    }
                    self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2], filter_types=[tier.value]
                        )
                    )

                with self.subTest("fail", tier=tier.value):
                    rel = {
                        "cat_from": self.cat1,
                        "cat_to": self.cat2,
                        reltype: self.thresholds[i - 3],
                    }
                    self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                    self.assertFalse(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2], filter_types=[tier.value]
                        )
                    )

                # teardown for individual subtests
                if self.cat1.ID in self.cat2.relationships:
                    self.cat2.relationships.pop(self.cat1.ID)

        with self.subTest("invalid rel type"):
            self.assertRaises(
                ValueError,
                event_filters.filter_relationship_type,
                group=[self.cat1, self.cat2],
                filter_types=["bagagwa"],
            )

        with self.subTest("only one cat"):
            self.assertRaises(
                ValueError,
                event_filters.filter_relationship_type,
                group=[self.cat1],
                filter_types=["loathes"],
            )

    def test_full_only_tiers(self):
        reltypes = deepcopy(rel_type_tiers)
        reltypes.pop(RelType.ROMANCE)

        for reltype, tiers in reltypes.items():
            for i, tier in enumerate(tiers):
                with self.subTest("normal pass", tier=tier.value):
                    if tier.is_extreme_neg:
                        points = (-100 + self.thresholds[i]) / 2
                    elif tier.is_extreme_pos:
                        points = (100 + self.thresholds[i - 1]) / 2
                    else:
                        points = (self.thresholds[i - 1] + self.thresholds[i]) / 2

                    rel = {
                        "cat_from": self.cat1,
                        "cat_to": self.cat2,
                        reltype: points,
                    }
                    self.cat1.relationships = {self.cat2.ID: Relationship(**rel)}

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2],
                            filter_types=[f"{tier.value}_only"],
                        )
                    )

                with self.subTest("boundary pass", tier=tier.value):
                    rel = {
                        "cat_from": self.cat1,
                        "cat_to": self.cat2,
                        reltype: self.thresholds[i],
                    }
                    self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2],
                            filter_types=[f"{tier.value}_only"],
                        )
                    )

                with self.subTest("fail", tier=tier.value):
                    rel = {
                        "cat_from": self.cat1,
                        "cat_to": self.cat2,
                        reltype: self.thresholds[i - 3],
                    }
                    self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                    self.assertFalse(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2],
                            filter_types=[f"{tier.value}_only"],
                        )
                    )

    def test_romance_tiers(self):
        reltype = "romance"
        tiers = [l for l in [*RelTier] if l.is_romance_level]

        for i, tier in enumerate(tiers):
            offset = i + 3  # to account for the lack of negative romance
            with self.subTest("normal pass", tier=tier.value):
                if tier.is_extreme_pos:
                    points = (100 + self.thresholds[offset - 1]) / 2
                else:
                    points = (self.thresholds[offset - 1] + self.thresholds[offset]) / 2

                rel = {
                    "cat_from": self.cat1,
                    "cat_to": self.cat2,
                    reltype: int(points),
                }
                self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2], filter_types=[tier.value]
                    )
                )

            with self.subTest("boundary pass", tier=tier.value):
                rel = {
                    "cat_from": self.cat1,
                    "cat_to": self.cat2,
                    reltype: self.thresholds[offset],
                }
                self.cat1.relationships = {self.cat2.ID: Relationship(**rel)}

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2], filter_types=[tier.value]
                    )
                )

            with self.subTest("fail", tier=tier.value):
                rel = {
                    "cat_from": self.cat1,
                    "cat_to": self.cat2,
                    reltype: self.thresholds[offset - 4],
                }
                self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                self.assertFalse(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2], filter_types=[tier.value]
                    )
                )

    def test_romance_only_tiers(self):
        reltype = "romance"
        tiers = [l for l in [*RelTier] if l.is_romance_level]

        for i, tier in enumerate(tiers):
            offset = i + 3  # to account for the lack of negative romance
            with self.subTest("normal pass", tier=tier.value):
                if tier.is_extreme_neg:
                    points = (-100 + self.thresholds[offset]) / 2
                elif tier.is_extreme_pos:
                    points = (100 + self.thresholds[offset - 1]) / 2
                else:
                    points = (self.thresholds[offset - 1] + self.thresholds[offset]) / 2

                rel = {
                    "cat_from": self.cat1,
                    "cat_to": self.cat2,
                    reltype: points,
                }
                self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )

            with self.subTest("boundary pass", tier=tier.value):
                rel = {
                    "cat_from": self.cat1,
                    "cat_to": self.cat2,
                    reltype: self.thresholds[offset],
                }
                self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )

            with self.subTest("fail", tier=tier.value):
                if tier.is_extreme_pos:
                    points = 0
                else:
                    points = self.thresholds[offset + 1]

                rel = {
                    "cat_from": self.cat1,
                    "cat_to": self.cat2,
                    reltype: points,
                }
                self.cat1.relationships[self.cat2.ID] = Relationship(**rel)

                self.assertFalse(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )


class TestRelationshipTiersMultiCat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("resources/game_config.toml", "r", encoding="utf-8") as read_file:
            config = tomllib.loads(read_file.read())

        cls.thresholds = list(config["relationship"]["value_intervals"].values())

        Cat.disable_random = True
        cls.cat1 = Cat()
        cls.cat2 = Cat()
        cls.cat3 = Cat()

    def tearDown(self):
        self.cat1.relationships = {}
        self.cat2.relationships = {}
        self.cat3.relationships = {}

    def test_full_tiers_multicat(self):
        reltypes = deepcopy(rel_type_tiers)
        reltypes.pop(RelType.ROMANCE)

        for reltype, tiers in reltypes.items():
            for i, tier in enumerate(tiers):
                with self.subTest("normal pass", tier=tier.value):
                    if tier.is_extreme_neg:
                        points = (-100 + self.thresholds[i]) / 2
                    elif tier.is_extreme_pos:
                        points = (100 + self.thresholds[i - 1]) / 2
                    else:
                        points = (self.thresholds[i - 1] + self.thresholds[i]) / 2

                    for cat_from, cat_to in permutations(
                        [self.cat1, self.cat2, self.cat3], 2
                    ):
                        rel = {
                            "cat_from": cat_from,
                            "cat_to": cat_to,
                            reltype: int(points),
                        }
                        cat_from.relationships[cat_to.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2, self.cat3],
                            filter_types=[tier.value],
                        )
                    )

                with self.subTest("boundary pass", tier=tier.value):
                    for cat_from, cat_to in permutations(
                        [self.cat1, self.cat2, self.cat3], 2
                    ):
                        rel = {
                            "cat_from": cat_from,
                            "cat_to": cat_to,
                            reltype: self.thresholds[i],
                        }
                        cat_from.relationships[cat_to.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2, self.cat3],
                            filter_types=[tier.value],
                        )
                    )

                with self.subTest("fail", tier=tier.value):
                    for cat_from, cat_to in permutations(
                        [self.cat1, self.cat2, self.cat3], 2
                    ):
                        rel = {
                            "cat_from": cat_from,
                            "cat_to": cat_to,
                            reltype: self.thresholds[i - 3],
                        }
                        cat_from.relationships[cat_to.ID] = Relationship(**rel)

                    self.assertFalse(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2, self.cat3],
                            filter_types=[tier.value],
                        )
                    )

    def test_full_only_tiers_multicat(self):
        reltypes = deepcopy(rel_type_tiers)
        reltypes.pop(RelType.ROMANCE)

        for reltype, tiers in reltypes.items():
            for i, tier in enumerate(tiers):
                with self.subTest("normal pass", tier=tier.value):
                    if tier.is_extreme_neg:
                        points = (-100 + self.thresholds[i]) / 2
                    elif tier.is_extreme_pos:
                        points = (100 + self.thresholds[i - 1]) / 2
                    else:
                        points = (self.thresholds[i - 1] + self.thresholds[i]) / 2

                    for cat_from, cat_to in permutations(
                        [self.cat1, self.cat2, self.cat3], 2
                    ):
                        rel = {
                            "cat_from": cat_from,
                            "cat_to": cat_to,
                            reltype: points,
                        }
                        cat_from.relationships[cat_to.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2, self.cat3],
                            filter_types=[f"{tier.value}_only"],
                        )
                    )

                with self.subTest("boundary pass", tier=tier.value):
                    for cat_from, cat_to in permutations(
                        [self.cat1, self.cat2, self.cat3], 2
                    ):
                        rel = {
                            "cat_from": cat_from,
                            "cat_to": cat_to,
                            reltype: self.thresholds[i],
                        }
                        cat_from.relationships[cat_to.ID] = Relationship(**rel)

                    self.assertTrue(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2, self.cat3],
                            filter_types=[f"{tier.value}_only"],
                        )
                    )

                with self.subTest("fail", tier=tier.value):
                    for cat_from, cat_to in permutations(
                        [self.cat1, self.cat2, self.cat3], 2
                    ):
                        rel = {
                            "cat_from": cat_from,
                            "cat_to": cat_to,
                            reltype: self.thresholds[i - 3],
                        }
                        cat_from.relationships[cat_to.ID] = Relationship(**rel)

                    self.assertFalse(
                        event_filters.filter_relationship_type(
                            group=[self.cat1, self.cat2, self.cat3],
                            filter_types=[f"{tier.value}_only"],
                        )
                    )

    def test_romance_tiers_multicat(self):
        reltype = "romance"
        tiers = [l for l in [*RelTier] if l.is_romance_level]

        for i, tier in enumerate(tiers):
            offset = i + 3  # to account for the lack of negative romance
            with self.subTest("normal pass", tier=tier.value):
                if tier.is_extreme_pos:
                    points = (100 + self.thresholds[offset - 1]) / 2
                else:
                    points = (self.thresholds[offset - 1] + self.thresholds[offset]) / 2

                for cat_from, cat_to in permutations(
                    [self.cat1, self.cat2, self.cat3], 2
                ):
                    rel = {
                        "cat_from": cat_from,
                        "cat_to": cat_to,
                        reltype: points,
                    }
                    cat_from.relationships[cat_to.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2, self.cat3],
                        filter_types=[tier.value],
                    )
                )

            with self.subTest("boundary pass", tier=tier.value):
                for cat_from, cat_to in permutations(
                    [self.cat1, self.cat2, self.cat3], 2
                ):
                    rel = {
                        "cat_from": cat_from,
                        "cat_to": cat_to,
                        reltype: self.thresholds[offset],
                    }
                    cat_from.relationships[cat_to.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2, self.cat3],
                        filter_types=[tier.value],
                    )
                )

            with self.subTest("fail", tier=tier.value):
                for cat_from, cat_to in permutations(
                    [self.cat1, self.cat2, self.cat3], 2
                ):
                    rel = {
                        "cat_from": cat_from,
                        "cat_to": cat_to,
                        reltype: self.thresholds[offset - 4],
                    }
                    cat_from.relationships[cat_to.ID] = Relationship(**rel)

                self.assertFalse(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2, self.cat3],
                        filter_types=[tier.value],
                    )
                )

    def test_romance_only_tiers_multicat(self):
        reltype = "romance"
        tiers = [l for l in [*RelTier] if l.is_romance_level]

        for i, tier in enumerate(tiers):
            offset = i + 3  # to account for the lack of negative romance
            with self.subTest("normal pass", tier=tier.value):
                if tier.is_extreme_pos:
                    points = (100 + self.thresholds[offset - 1]) / 2
                else:
                    points = (self.thresholds[offset - 1] + self.thresholds[offset]) / 2

                for cat_from, cat_to in permutations(
                    [self.cat1, self.cat2, self.cat3], 2
                ):
                    rel = {
                        "cat_from": cat_from,
                        "cat_to": cat_to,
                        reltype: points,
                    }
                    cat_from.relationships[cat_to.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )

            with self.subTest("boundary pass", tier=tier.value):
                for cat_from, cat_to in permutations(
                    [self.cat1, self.cat2, self.cat3], 2
                ):
                    rel = {
                        "cat_from": cat_from,
                        "cat_to": cat_to,
                        reltype: self.thresholds[offset],
                    }
                    cat_from.relationships[cat_to.ID] = Relationship(**rel)

                self.assertTrue(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )

            with self.subTest("fail", tier=tier.value):
                if tier.is_extreme_pos:
                    points = 0
                else:
                    points = self.thresholds[offset + 1]

                for cat_from, cat_to in permutations(
                    [self.cat1, self.cat2, self.cat3], 2
                ):
                    rel = {
                        "cat_from": cat_from,
                        "cat_to": cat_to,
                        reltype: points,
                    }
                    cat_from.relationships[cat_to.ID] = Relationship(**rel)

                self.assertFalse(
                    event_filters.filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )


class TestCatConstraint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Cat.disable_random = True

    def test_ages(self):
        ages = [*CatAge]
        cat = Cat(disable_random=True)

        # ages used
        newborn = CatAge.NEWBORN
        age = CatAge.ADULT
        unmatched_age = CatAge.SENIOR

        # newborn-specific
        cat.age = CatAge.NEWBORN
        with self.subTest("empty newborn"):
            self.assertFalse(event_filters._check_cat_age(cat, []))
        with self.subTest('"any" newborn'):
            self.assertFalse(event_filters._check_cat_age(cat, ["any"]))
        with self.subTest("unmatched newborn"):
            self.assertFalse(event_filters._check_cat_age(cat, [unmatched_age]))
        with self.subTest("explicit newborn"):
            self.assertTrue(event_filters._check_cat_age(cat, [newborn]))

        # set cat age to the general testing age
        cat.age = age

        # general
        with self.subTest("empty"):
            self.assertTrue(event_filters._check_cat_age(cat, []))
        with self.subTest('"any"'):
            self.assertTrue(event_filters._check_cat_age(cat, ["any"]))
        with self.subTest("invalid"):
            self.assertRaises(ValueError)
            self.assertFalse(event_filters._check_cat_age(cat, ["elder"]))

        # inclusive
        with self.subTest("explicit constraint"):
            self.assertTrue(event_filters._check_cat_age(cat, [age]))
        with self.subTest("unmatched", age=age.value):
            self.assertFalse(event_filters._check_cat_age(cat, [unmatched_age]))

        # exclusive
        with self.subTest("explicit exclusionary"):
            self.assertFalse(event_filters._check_cat_age(cat, [f"-{age.value}"]))
        with self.subTest("unmatched exclusionary"):
            self.assertTrue(
                event_filters._check_cat_age(cat, [f"-{unmatched_age.value}"])
            )

    def test_statuses(self):
        statuses = [s for s in [*CatRank] if s.is_any_clancat_rank()]
        cat = Cat(disable_random=True)

        with self.subTest("empty"):
            self.assertTrue(event_filters._check_cat_status(cat, []))
        for i, status in enumerate(statuses):
            cat.status.generate_new_status(rank=status)

            with self.subTest("rank-constrained", rank=status.value):
                self.assertTrue(event_filters._check_cat_status(cat, [status]))
            with self.subTest('"any"', age=status.value):
                self.assertTrue(event_filters._check_cat_status(cat, ["any"]))
            with self.subTest("unmatched", age=status.value):
                self.assertFalse(
                    event_filters._check_cat_status(cat, [statuses[i - 1]])
                )
            with self.subTest("exclusionary", age=status.value):
                self.assertFalse(
                    event_filters._check_cat_status(cat, [f"-{status.value}"])
                )

    def test_statuses_lost(self):
        cat = Cat(status_dict=StatusDict(rank=CatRank.WARRIOR))
        cat.become_lost()

        with self.subTest("rank-constrained", rank="lost"):
            self.assertTrue(event_filters._check_cat_status(cat, ["lost"]))
        with self.subTest('"any"', age="lost"):
            self.assertTrue(event_filters._check_cat_status(cat, ["any"]))
        with self.subTest("unmatched - different Clan rank", age="lost"):
            self.assertFalse(event_filters._check_cat_status(cat, [CatRank.LEADER]))
        with self.subTest("unmatched - same as former rank", age="lost"):
            self.assertFalse(event_filters._check_cat_status(cat, [CatRank.WARRIOR]))
        with self.subTest("exclusionary", age="lost"):
            self.assertFalse(event_filters._check_cat_status(cat, [f"-lost"]))

    def test_status_history(self):
        ranks = [*CatRank]

        cat = Cat()
        for old_rank, new_rank in permutations(ranks, 2):
            cat.status.generate_new_status(rank=old_rank)

            # this is an xnor in python. good god.
            if not (old_rank.is_any_clancat_rank() ^ new_rank.is_any_clancat_rank()):
                cat.rank_change(new_rank=new_rank)
            elif old_rank.is_any_clancat_rank():
                cat.leave_clan(new_social_status=CatSocial(new_rank.value))
            elif new_rank.is_any_clancat_rank():
                cat.add_to_clan()
                cat.rank_change(new_rank=new_rank)
            else:
                raise Exception(
                    f"Impossible ranks found: old = {old_rank}, new = {new_rank}"
                )
            other_rank = [r for r in ranks if r != old_rank and r != new_rank][-1]

            with self.subTest(
                "empty", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(event_filters._check_cat_status_history(cat, []))
            with self.subTest(
                "current rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertFalse(
                    event_filters._check_cat_status_history(cat, [new_rank])
                )
            with self.subTest(
                "former rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_filters._check_cat_status_history(cat, [old_rank])
                )
            with self.subTest(
                '"any"', old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(event_filters._check_cat_status_history(cat, ["any"]))
            with self.subTest(
                "other rank",
                old_rank=old_rank.value,
                new_rank=new_rank.value,
                other_rank=other_rank,
            ):
                self.assertFalse(
                    event_filters._check_cat_status_history(cat, [other_rank])
                )

            with self.subTest(
                "not current rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_filters._check_cat_status_history(cat, [f"-{new_rank}"])
                )
            with self.subTest(
                "not former rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertFalse(
                    event_filters._check_cat_status_history(cat, [f"-{old_rank}"])
                )
            with self.subTest(
                "not other rank",
                old_rank=old_rank.value,
                new_rank=new_rank.value,
                other_rank=other_rank,
            ):
                self.assertTrue(
                    event_filters._check_cat_status_history(cat, [f"-{other_rank}"])
                )

    def test_trait(self):
        """
        I have made this run just the one as they should all be functionally identical.
        :return:
        """
        cat = Cat()
        cat.personality = Personality(trait="adventurous")

        # general
        with self.subTest('"any"'):
            self.assertTrue(event_filters._check_cat_trait(cat, ["any"]))
        with self.subTest("empty"):
            self.assertTrue(event_filters._check_cat_trait(cat, []))

        # inclusive
        with self.subTest("explicit constraint"):
            self.assertTrue(event_filters._check_cat_trait(cat, ["adventurous"]))
        with self.subTest("unmatched"):
            self.assertFalse(event_filters._check_cat_trait(cat, ["bold"]))

        # exclusive
        with self.subTest("explicit exclusionary"):
            self.assertFalse(event_filters._check_cat_trait(cat, ["-adventurous"]))
        with self.subTest("unmatched exclusionary"):
            self.assertTrue(event_filters._check_cat_trait(cat, ["-bold"]))

    def test_skill(self):
        cat = Cat()
        cat.personality = Personality(trait="adventurous")
        cat.skills.primary = Skill(SkillPath.HUNTER, points=9)
        cat.skills.secondary = None

        for i in range(1, 4):
            cat.skills.primary.set_points_to_tier(i)

            # general
            with self.subTest('"any"'):
                self.assertTrue(event_filters._check_cat_skills(cat, ["any"]))
            with self.subTest("empty"):
                self.assertTrue(event_filters._check_cat_skills(cat, []))

            # inclusives
            with self.subTest("explicit constraint"):
                self.assertTrue(event_filters._check_cat_skills(cat, [f"HUNTER,{i}"]))
            with self.subTest("explicit lower"):
                self.assertTrue(event_filters._check_cat_skills(cat, [f"HUNTER,{i-1}"]))
            with self.subTest("explicit higher"):
                self.assertFalse(
                    event_filters._check_cat_skills(cat, [f"HUNTER,{i+1}"])
                )

            with self.subTest("unmatched"):
                self.assertFalse(event_filters._check_cat_skills(cat, [f"SWIMMER,{i}"]))
            with self.subTest("unmatched lower"):
                self.assertFalse(
                    event_filters._check_cat_skills(cat, [f"SWIMMER,{i-1}"])
                )
            with self.subTest("unmatched higher"):
                self.assertFalse(
                    event_filters._check_cat_skills(cat, [f"SWIMMER,{i+1}"])
                )

            # exclusives
            with self.subTest("explicit exclusionary"):
                self.assertFalse(event_filters._check_cat_skills(cat, [f"-HUNTER,{i}"]))
            with self.subTest("explicit exclusionary lower"):
                self.assertTrue(
                    event_filters._check_cat_skills(cat, [f"-HUNTER,{i-1}"])
                )
            with self.subTest("explicit exclusionary higher"):
                self.assertFalse(
                    event_filters._check_cat_skills(cat, [f"-HUNTER,{i+1}"])
                )

            with self.subTest("unmatched exclusionary"):
                self.assertTrue(event_filters._check_cat_skills(cat, [f"SWIMMER,{i}"]))
            with self.subTest("unmatched exclusionary lower"):
                self.assertTrue(
                    event_filters._check_cat_skills(cat, [f"SWIMMER,{i-1}"])
                )
            with self.subTest("unmatched exclusionary higher"):
                self.assertTrue(
                    event_filters._check_cat_skills(cat, [f"SWIMMER,{i+1}"])
                )
