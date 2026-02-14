import unittest
import os
from copy import deepcopy
from itertools import permutations

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from scripts.cat_relations.relationship import Relationship
from scripts.cat.enums import CatRank
from scripts.cat.status import StatusDict
from scripts.cat_relations.enums import RelTier, rel_type_tiers, RelType

from scripts.cat.cats import Cat
from scripts.events_module.event_filters import filter_relationship_type


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
                filter_relationship_type(group=[cat1, cat2], filter_types=["siblings"])
            )
        with self.subTest("are siblings, expected not siblings"):
            self.assertFalse(
                filter_relationship_type(group=[cat1, cat2], filter_types=["-siblings"])
            )
        with self.subTest("are not siblings, expected siblings"):
            self.assertFalse(
                filter_relationship_type(
                    group=[cat1, parent], filter_types=["siblings"]
                )
            )
        with self.subTest("are not siblings, expected not siblings"):
            self.assertTrue(
                filter_relationship_type(
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
                filter_relationship_type(
                    group=[cat1, cat2], filter_types=["littermates"]
                )
            )
        with self.subTest("are littermates, expected not littermates"):
            self.assertFalse(
                filter_relationship_type(
                    group=[cat1, cat2], filter_types=["-littermates"]
                )
            )
        with self.subTest("are not littermates, expected littermates"):
            self.assertFalse(
                filter_relationship_type(
                    group=[cat1, parent], filter_types=["littermates"]
                )
            )
        with self.subTest("are not littermates, expected not littermates"):
            self.assertTrue(
                filter_relationship_type(
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
                filter_relationship_type(group=[mate1, mate2], filter_types=["mates"])
            )
        with self.subTest("are mates, expected not mates"):
            self.assertFalse(
                filter_relationship_type(group=[mate1, mate2], filter_types=["-mates"])
            )
        with self.subTest("are not mates, expected mates"):
            self.assertFalse(
                filter_relationship_type(group=[mate1, other], filter_types=["mates"])
            )
        with self.subTest("are not mates, expected not mates"):
            self.assertTrue(
                filter_relationship_type(group=[mate1, other], filter_types=["-mates"])
            )

    def test_parent_child(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()

        with self.subTest("are parent/child, expected parent/child"):
            self.assertTrue(
                filter_relationship_type(
                    group=[parent, cat1], filter_types=["parent/child"]
                )
            )
        with self.subTest("are parent/child, expected not parent/child"):
            self.assertFalse(
                filter_relationship_type(
                    group=[parent, cat1], filter_types=["-parent/child"]
                )
            )
        with self.subTest("are not parent/child, expected parent/child"):
            self.assertFalse(
                filter_relationship_type(
                    group=[cat1, parent], filter_types=["parent/child"]
                )
            )
        with self.subTest("are not parent/child, expected not parent/child"):
            self.assertTrue(
                filter_relationship_type(
                    group=[cat1, parent], filter_types=["-parent/child"]
                )
            )

    def test_child_parent(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()

        with self.subTest("are child/parent, expected child/parent"):
            self.assertTrue(
                filter_relationship_type(
                    group=[cat1, parent], filter_types=["child/parent"]
                )
            )
        with self.subTest("are child/parent, expected not child/parent"):
            self.assertFalse(
                filter_relationship_type(
                    group=[cat1, parent], filter_types=["-child/parent"]
                )
            )
        with self.subTest("are not child/parent, expected child/parent"):
            self.assertFalse(
                filter_relationship_type(
                    group=[parent, cat1], filter_types=["child/parent"]
                )
            )
        with self.subTest("are not child/parent, expected not child/parent"):
            self.assertTrue(
                filter_relationship_type(
                    group=[parent, cat1], filter_types=["-child/parent"]
                )
            )

    def test_app_mentor(self):
        app = Cat(moons=8)
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app.update_mentor(new_mentor=mentor.ID)

        with self.subTest("are app/mentor, expected app/mentor"):
            self.assertTrue(
                filter_relationship_type(
                    group=[app, mentor], filter_types=["app/mentor"]
                )
            )
        with self.subTest("are app/mentor, expected not app/mentor"):
            self.assertFalse(
                filter_relationship_type(
                    group=[app, mentor], filter_types=["-app/mentor"]
                )
            )
        with self.subTest("are not app/mentor, expected app/mentor"):
            self.assertFalse(
                filter_relationship_type(
                    group=[mentor, app], filter_types=["app/mentor"]
                )
            )
        with self.subTest("are not app/mentor, expected not app/mentor"):
            self.assertTrue(
                filter_relationship_type(
                    group=[mentor, app], filter_types=["-app/mentor"]
                )
            )

    def test_mentor_app(self):
        app = Cat(moons=8)
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app.update_mentor(new_mentor=mentor.ID)

        with self.subTest("are mentor/app, expected mentor/app"):
            self.assertTrue(
                filter_relationship_type(
                    group=[mentor, app], filter_types=["mentor/app"]
                )
            )
        with self.subTest("are mentor/app, expected not mentor/app"):
            self.assertFalse(
                filter_relationship_type(
                    group=[mentor, app], filter_types=["-mentor/app"]
                )
            )
        with self.subTest("are not mentor/app, expected mentor/app"):
            self.assertFalse(
                filter_relationship_type(
                    group=[app, mentor], filter_types=["mentor/app"]
                )
            )
        with self.subTest("are not mentor/app, expected not mentor/app"):
            self.assertTrue(
                filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
                            group=[self.cat1, self.cat2], filter_types=[tier.value]
                        )
                    )

                # teardown for individual subtests
                if self.cat1.ID in self.cat2.relationships:
                    self.cat2.relationships.pop(self.cat1.ID)
                    self.cat2.relationships.pop(self.cat3.ID)

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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                        filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                if tier.is_extreme_neg:
                    points = (-100 + self.thresholds[offset]) / 2
                elif tier.is_extreme_pos:
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
                    filter_relationship_type(
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
                    filter_relationship_type(
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
                    filter_relationship_type(
                        group=[self.cat1, self.cat2],
                        filter_types=[f"{tier.value}_only"],
                    )
                )
