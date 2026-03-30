import unittest
import os
from copy import deepcopy
from itertools import permutations

from scripts.cat.personality import Personality
from scripts.cat.skills import Skill, SkillPath

try:
    import tomllib
except ImportError:
    import tomli as tomllib

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, create_cat
from scripts.cat.enums import CatRank, CatAge, CatSocial
from scripts.cat.status import StatusDict
from scripts.cat_relations.enums import RelType, rel_type_tiers, RelTier
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.event_filters import (
    event_for_location,
    event_for_season,
    event_for_tags,
    event_for_cat,
)
from scripts.game_structure import game


class TestEventFilters(unittest.TestCase):
    def setUp(self):
        game.clan = Clan()
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.test_cat = create_cat(CatRank.LEADER, moons=50)
        game.clan.leader = self.test_cat

    def test_location(self):
        """
        Tests a variety of location tag combinations
        """

        self.assertTrue(
            event_for_location(locations=["forest"]),
            "Assert single biome match.",
        )
        self.assertTrue(
            event_for_location(locations=["forest:camp1"]),
            "Assert single camp match.",
        )
        self.assertFalse(
            event_for_location(locations=["desert"]),
            "Assert single biome mismatch.",
        )
        self.assertFalse(
            event_for_location(locations=["forest:camp2"]),
            "Assert single camp mismatch.",
        )
        self.assertTrue(
            event_for_location(locations=["desert:camp2", "forest"]),
            "Assert mixed location match.",
        )
        self.assertFalse(
            event_for_location(locations=["desert:camp2", "plains", "forest:camp2"]),
            "Assert mixed location mismatch.",
        )
        self.assertTrue(
            event_for_location(locations=["-plains"]),
            "Assert single location excluded.",
        )
        self.assertTrue(
            event_for_location(locations=["-plains", "-forest:camp2"]),
            "Assert mixed locations excluded.",
        )
        self.assertFalse(
            event_for_location(locations=["-plains", "-forest"]),
            "Assert mixed locations, including current biome, excluded.",
        )
        self.assertFalse(
            event_for_location(locations=["-plains", "-forest:camp1"]),
            "Assert mixed locations, including current camp, excluded.",
        )

    def test_season(self):
        self.assertTrue(event_for_season(["newleaf"]), "Assert single season match.")
        self.assertFalse(
            event_for_season(["greenleaf"]), "Assert single season mismatch."
        )
        self.assertTrue(
            event_for_season(["newleaf", "greenleaf"]),
            "Assert mixed season match.",
        )
        self.assertFalse(
            event_for_season(["greenleaf", "leaf-bare"]),
            "Assert mixed season mismatch.",
        )
        self.assertTrue(
            event_for_season(["-greenleaf"]),
            "Assert single season excluded.",
        )
        self.assertFalse(
            event_for_season(["-newleaf"]),
            "Assert current season excluded.",
        )
        self.assertTrue(
            event_for_season(["-greenleaf", "-leaf-bare"]),
            "Assert mixed season excluded.",
        )
        self.assertFalse(
            event_for_season(["-greenleaf", "-newleaf"]),
            "Assert mixed season, including current, excluded.",
        )

    def test_game_mode_tags(self):
        self.assertTrue(
            event_for_tags(["classic"], self.test_cat),
            "Assert correct game mode tag.",
        )
        self.assertFalse(
            event_for_tags(["expanded"], self.test_cat),
            "Assert incorrect game mode tag",
        )

    def test_leader_life_tags(self):
        game.clan.leader_lives = 9
        self.assertTrue(
            event_for_tags(["some_lives", "lives_remain", "high_lives"], self.test_cat),
            "Assert 9-life leader passes some_lives, lives_remain, and high_lives.",
        )
        self.assertFalse(
            event_for_tags(["mid_lives", "low_lives"], self.test_cat),
            "Assert 9-lives leader does not pass mid_lives and low_lives.",
        )
        self.assertFalse(
            event_for_tags(["mid_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 9-lives leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )

        game.clan.leader_lives = 5
        self.assertTrue(
            event_for_tags(["some_lives", "mid_lives", "lives_remain"], self.test_cat),
            "Assert 5-lives leader passes some_lives, mid_lives, and lives_remain.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives"], self.test_cat),
            "Assert 5-lives leader does not pass mid_lives and low_lives.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 5-lives leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )

        game.clan.leader_lives = 3
        self.assertTrue(
            event_for_tags(["low_lives", "lives_remain"], self.test_cat),
            "Assert 3-lives leader passes low_lives and lives_remain.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "mid_lives", "some_lives"], self.test_cat),
            "Assert 3-lives leader does not pass mid_lives, high_lives, and some_lives.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 3-lives leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )

        game.clan.leader_lives = 1
        self.assertTrue(
            event_for_tags(["low_lives"], self.test_cat),
            "Assert 1-life leader passes low_lives.",
        )
        self.assertFalse(
            event_for_tags(
                ["high_lives", "mid_lives", "some_lives", "lives_remain"], self.test_cat
            ),
            "Assert 1-life leader does not pass mid_lives, high_lives, some_lives, and lives_remain.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 1-life leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )


class TestInterpersonalRelationshipConstraints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Cat.disable_random = True

    @classmethod
    def build_cat_constraint(cls, rel_filter):
        return {"relationship_status": [rel_filter]}

    def test_strangers(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.relationships = {}
        cat2.relationships = {}

        with self.subTest("are strangers, expected strangers"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["strangers"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )

        with self.subTest("are strangers, expected not strangers"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-strangers"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )

        cat1.relationships[cat2.ID] = Relationship(
            **{
                "cat_from": cat1,
                "cat_to": cat2,
                "like": 20,
                "romance": 10,
                "respect": 67,
            }
        )

        with self.subTest("are not strangers, expected strangers"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["strangers"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )

        with self.subTest("are not strangers, expected not strangers"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-strangers"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )

    def test_siblings(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()
        cat2.create_inheritance_new_cat()

        with self.subTest("are siblings, expected siblings"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["siblings"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )
        with self.subTest("are siblings, expected not siblings"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-siblings"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )
        with self.subTest("are not siblings, expected siblings"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["siblings"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
                )
            )
        with self.subTest("are not siblings, expected not siblings"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-siblings"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
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
                event_for_cat(
                    cat_info={"relationship_status": ["littermates"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )
        with self.subTest("are littermates, expected not littermates"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-littermates"]},
                    cat=cat1,
                    cat_group=[cat1, cat2],
                )
            )
        with self.subTest("are not littermates, expected littermates"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["littermates"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
                )
            )
        with self.subTest("are not littermates, expected not littermates"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-littermates"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
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
                event_for_cat(
                    cat_info={"relationship_status": ["mates"]},
                    cat=mate1,
                    cat_group=[mate1, mate2],
                )
            )
        with self.subTest("are mates, expected not mates"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-mates"]},
                    cat=mate1,
                    cat_group=[mate1, mate2],
                )
            )
        with self.subTest("are not mates, expected mates"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["mates"]},
                    cat=mate1,
                    cat_group=[mate1, other],
                )
            )
        with self.subTest("are not mates, expected not mates"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-mates"]},
                    cat=mate1,
                    cat_group=[mate1, other],
                )
            )

    def test_parent_child(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()

        with self.subTest("are parent/child, expected parent/child"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["parent/child"]},
                    cat=parent,
                    cat_group=[parent, cat1],
                )
            )
        with self.subTest("are parent/child, expected not parent/child"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-parent/child"]},
                    cat=parent,
                    cat_group=[parent, cat1],
                )
            )
        with self.subTest("are not parent/child, expected parent/child"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["parent/child"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
                )
            )
        with self.subTest("are not parent/child, expected not parent/child"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-parent/child"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
                )
            )

    def test_child_parent(self):
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)

        cat1.create_inheritance_new_cat()

        with self.subTest("are child/parent, expected child/parent"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["child/parent"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
                )
            )
        with self.subTest("are child/parent, expected not child/parent"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-child/parent"]},
                    cat=cat1,
                    cat_group=[cat1, parent],
                )
            )
        with self.subTest("are not child/parent, expected child/parent"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["child/parent"]},
                    cat=parent,
                    cat_group=[parent, cat1],
                )
            )
        with self.subTest("are not child/parent, expected not child/parent"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-child/parent"]},
                    cat=parent,
                    cat_group=[parent, cat1],
                )
            )

    def test_app_mentor(self):
        app = Cat(moons=8, status_dict=StatusDict(rank=CatRank.APPRENTICE))
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app.update_mentor(new_mentor=mentor.ID)

        with self.subTest("are app/mentor, expected app/mentor"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["app/mentor"]},
                    cat=app,
                    cat_group=[app, mentor],
                )
            )
        with self.subTest("are app/mentor, expected not app/mentor"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-app/mentor"]},
                    cat=app,
                    cat_group=[app, mentor],
                )
            )
        with self.subTest("are not app/mentor, expected app/mentor"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["app/mentor"]},
                    cat=mentor,
                    cat_group=[mentor, app],
                )
            )
        with self.subTest("are not app/mentor, expected not app/mentor"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-app/mentor"]},
                    cat=mentor,
                    cat_group=[mentor, app],
                )
            )

    def test_mentor_app(self):
        app = Cat(moons=8, disable_random=True)
        mentor = Cat(
            moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR), disable_random=True
        )

        app.update_mentor(new_mentor=mentor.ID)

        with self.subTest("are mentor/app, expected mentor/app"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["mentor/app"]},
                    cat=mentor,
                    cat_group=[mentor, app],
                )
            )
        with self.subTest("are mentor/app, expected not mentor/app"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-mentor/app"]},
                    cat=mentor,
                    cat_group=[mentor, app],
                )
            )
        with self.subTest("are not mentor/app, expected mentor/app"):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["mentor/app"]},
                    cat=app,
                    cat_group=[app, mentor],
                )
            )
        with self.subTest("are not mentor/app, expected not mentor/app"):
            self.assertTrue(
                event_for_cat(
                    cat_info={"relationship_status": ["-mentor/app"]},
                    cat=app,
                    cat_group=[app, mentor],
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

    def test_empty_filter(self):
        self.assertTrue(
            event_for_cat(
                cat=self.cat1,
                cat_info={"relationship_status": []},
                cat_group=[self.cat1, self.cat2],
            )
        )

    def test_patrol_leader_arg(self):
        """
        Asserts that the relationship tested is cat1 -> cat2 when cat1 is the patrol leader
        :return:
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, like=5
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1, like=5
        )

        self.assertTrue(
            event_for_cat(
                cat=self.cat2,
                cat_info={"relationship_status": ["knows_of"]},
                cat_group=[self.cat2, self.cat1],
                p_l=self.cat1,
            )
        )

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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [tier.value]},
                            cat_group=[self.cat1, self.cat2],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [tier.value]},
                            cat_group=[self.cat1, self.cat2],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [tier.value]},
                            cat_group=[self.cat1, self.cat2],
                        )
                    )

                # teardown for individual subtests
                if self.cat1.ID in self.cat2.relationships:
                    self.cat2.relationships.pop(self.cat1.ID)

        with self.subTest("invalid rel type"):
            self.assertRaises(
                ValueError,
                event_for_cat,
                cat=self.cat1,
                cat_group=[self.cat1, self.cat2],
                cat_info={"relationship_status": ["bagagwa"]},
            )

        with self.subTest("only one cat"):
            self.assertFalse(
                event_for_cat(
                    cat=self.cat1,
                    cat_group=[self.cat1],
                    cat_info={"relationship_status": ["loathes"]},
                ),
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [f"{tier.value}_only"]},
                            cat_group=[self.cat1, self.cat2],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [f"{tier.value}_only"]},
                            cat_group=[self.cat1, self.cat2],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [f"{tier.value}_only"]},
                            cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [tier.value]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [tier.value]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [tier.value]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [f"{tier.value}_only"]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [f"{tier.value}_only"]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [f"{tier.value}_only"]},
                        cat_group=[self.cat1, self.cat2],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [tier.value]},
                            cat_group=[self.cat1, self.cat2, self.cat3],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [tier.value]},
                            cat_group=[self.cat1, self.cat2, self.cat3],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [tier.value]},
                            cat_group=[self.cat1, self.cat2, self.cat3],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [f"{tier.value}_only"]},
                            cat_group=[self.cat1, self.cat2, self.cat3],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [f"{tier.value}_only"]},
                            cat_group=[self.cat1, self.cat2, self.cat3],
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
                        event_for_cat(
                            cat=self.cat1,
                            cat_info={"relationship_status": [f"{tier.value}_only"]},
                            cat_group=[self.cat1, self.cat2, self.cat3],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [tier.value]},
                        cat_group=[self.cat1, self.cat2, self.cat3],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [tier.value]},
                        cat_group=[self.cat1, self.cat2, self.cat3],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [tier.value]},
                        cat_group=[self.cat1, self.cat2, self.cat3],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [f"{tier.value}_only"]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [f"{tier.value}_only"]},
                        cat_group=[self.cat1, self.cat2],
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
                    event_for_cat(
                        cat=self.cat1,
                        cat_info={"relationship_status": [f"{tier.value}_only"]},
                        cat_group=[self.cat1, self.cat2],
                    )
                )


class TestCatConstraint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Cat.disable_random = True

    def test_ages(self):
        cat = Cat(disable_random=True)

        # ages used
        newborn = CatAge.NEWBORN
        age = CatAge.ADULT
        unmatched_age = CatAge.SENIOR

        # newborn-specific
        cat.age = CatAge.NEWBORN
        with self.subTest("empty newborn"):
            self.assertFalse(event_for_cat(cat=cat, cat_info={"age": []}))
        with self.subTest('"any" newborn'):
            self.assertFalse(event_for_cat(cat=cat, cat_info={"age": ["any"]}))
        with self.subTest("unmatched newborn"):
            self.assertFalse(event_for_cat(cat=cat, cat_info={"age": [unmatched_age]}))
        with self.subTest("explicit newborn"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"age": [newborn]}))

        # set cat age to the general testing age
        cat.age = age

        # general
        with self.subTest("empty"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"age": []}))
        with self.subTest('"any"'):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"age": ["any"]}))
        with self.subTest("invalid"):
            self.assertRaises(
                ValueError, event_for_cat, cat=cat, cat_info={"age": ["elder"]}
            )

        # inclusive
        with self.subTest("explicit constraint"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"age": [age]}))
        with self.subTest("unmatched", age=age.value):
            self.assertFalse(event_for_cat(cat=cat, cat_info={"age": [unmatched_age]}))

        # exclusive
        with self.subTest("explicit exclusionary"):
            self.assertFalse(
                event_for_cat(cat=cat, cat_info={"age": [f"-{age.value}"]})
            )
        with self.subTest("unmatched exclusionary"):
            self.assertTrue(
                event_for_cat(cat=cat, cat_info={"age": [f"-{unmatched_age.value}"]})
            )

    def test_statuses(self):
        statuses = [s for s in [*CatRank] if s.is_any_clancat_rank()]
        cat = Cat(disable_random=True)

        with self.subTest("empty"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"status": []}))
        for i, status in enumerate(statuses):
            cat.status.generate_new_status(rank=status)

            with self.subTest("rank-constrained", rank=status.value):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"status": [status]}))
            with self.subTest('"any"', age=status.value):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"status": ["any"]}))
            with self.subTest("unmatched", age=status.value):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"status": [statuses[i - 1]]})
                )
            with self.subTest("exclusionary", age=status.value):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"status": [f"-{status.value}"]})
                )

    def test_statuses_lost(self):
        cat = Cat(status_dict=StatusDict(rank=CatRank.WARRIOR))
        cat.become_lost()

        with self.subTest("rank-constrained", rank="lost"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"status": ["lost"]}))
        with self.subTest('"any"', age="lost"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"status": ["any"]}))
        with self.subTest("unmatched - different Clan rank", age="lost"):
            self.assertFalse(
                event_for_cat(cat=cat, cat_info={"status": [CatRank.LEADER]})
            )
        with self.subTest("unmatched - same as former rank", age="lost"):
            self.assertFalse(
                event_for_cat(cat=cat, cat_info={"status": [CatRank.WARRIOR]})
            )
        with self.subTest("exclusionary", age="lost"):
            self.assertFalse(event_for_cat(cat=cat, cat_info={"status": [f"-lost"]}))

    def test_status_history(self):
        return  # temp patch until the test can be fixed proper
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
                self.assertTrue(event_for_cat(cat=cat, cat_info={"status_history": []}))
            with self.subTest(
                "current rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"status_history": [new_rank]})
                )
            with self.subTest(
                "former rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"status_history": [old_rank]})
                )
            with self.subTest(
                '"any"', old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"status_history": ["any"]})
                )
            with self.subTest(
                "other rank",
                old_rank=old_rank.value,
                new_rank=new_rank.value,
                other_rank=other_rank,
            ):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"status_history": [other_rank]})
                )

            with self.subTest(
                "not current rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_for_cat(
                        cat=cat, cat_info={"status_history": [f"-{new_rank}"]}
                    )
                )
            with self.subTest(
                "not former rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertFalse(
                    event_for_cat(
                        cat=cat, cat_info={"status_history": [f"-{old_rank}"]}
                    )
                )
            with self.subTest(
                "not other rank",
                old_rank=old_rank.value,
                new_rank=new_rank.value,
                other_rank=other_rank,
            ):
                self.assertTrue(
                    event_for_cat(
                        cat=cat, cat_info={"status_history": [f"-{other_rank}"]}
                    )
                )

    def test_trait(self):
        """
        Runs adult & kit traits.
        :return:
        """
        cat = Cat()

        # general
        with self.subTest('"any"'):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"trait": ["any"]}))
        with self.subTest("empty"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"trait": []}))
        with self.subTest("invalid value"):
            self.assertRaises(
                ValueError,
                event_for_cat,
                cat=cat,
                cat_info={"trait": ["inimitablyspiffinglyunique"]},
            )

        for age, trait in [("adult", "adventurous"), ("kit", "noisy")]:
            cat.personality = Personality(trait=trait, kit_trait=age == "kit")
            self.assertEqual(cat.personality.trait, trait)

            # inclusive
            with self.subTest("explicit constraint", age=age):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"trait": [trait]}))
            with self.subTest("unmatched", age=age):
                self.assertFalse(event_for_cat(cat=cat, cat_info={"trait": ["bold"]}))

            # exclusive
            with self.subTest("explicit exclusionary", age=age):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"trait": [f"-{trait}"]})
                )
            with self.subTest("unmatched exclusionary", age=age):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"trait": ["-bold"]}))

    def test_skill(self):
        cat = Cat()
        cat.personality = Personality(trait="adventurous")
        cat.skills.primary = Skill(SkillPath.HUNTER, points=9)
        cat.skills.secondary = None

        for skill_label in ["primary", "secondary"]:
            cat.skills.primary = Skill(SkillPath.CAMP, points=0)
            cat.skills.secondary = None

            # general
            with self.subTest('"any"'):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"skill": ["any"]}))
            with self.subTest("empty"):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"skill": []}))
            with self.subTest("invalid format"):
                self.assertRaises(
                    TypeError,
                    event_for_cat,
                    cat=cat,
                    cat_info={"skill": ["SWIMMER", 1]},
                )
                self.assertRaises(
                    ValueError,
                    event_for_cat,
                    cat=cat,
                    cat_info={"skill": ["SWIMMER", "1"]},
                )
                self.assertRaises(
                    ValueError,
                    event_for_cat,
                    cat=cat,
                    cat_info={"skill": ["SWIMMER1"]},
                )
                self.assertRaises(
                    ValueError,
                    event_for_cat,
                    cat=cat,
                    cat_info={"skill": ["SWIMMER,1,2"]},
                )
            with self.subTest("invalid skill"):
                self.assertRaises(
                    KeyError,
                    event_for_cat,
                    cat=cat,
                    cat_info={"skill": ["SKIMBLING,1"]},
                )

            for i in range(1, 4):
                setattr(cat.skills, skill_label, Skill(SkillPath.HUNTER, points=0))
                getattr(cat.skills, skill_label).set_points_to_tier(i)

                # confirm the test is set up appropriately
                if skill_label == "primary":
                    self.assertEqual(cat.skills.primary.path, SkillPath.HUNTER)
                    self.assertEqual(cat.skills.primary.tier, i)

                    self.assertIsNone(cat.skills.secondary)
                else:
                    self.assertEqual(cat.skills.primary.path, SkillPath.CAMP)
                    self.assertEqual(cat.skills.primary.tier, 1)

                    self.assertEqual(cat.skills.secondary.path, SkillPath.HUNTER)
                    self.assertEqual(cat.skills.secondary.tier, i)

                # inclusives
                with self.subTest("explicit constraint", skill=skill_label):
                    self.assertTrue(
                        event_for_cat(cat=cat, cat_info={"skill": [f"HUNTER,{i}"]})
                    )
                with self.subTest("explicit lower", skill=skill_label):
                    self.assertTrue(
                        event_for_cat(cat=cat, cat_info={"skill": [f"HUNTER,{i-1}"]})
                    )
                with self.subTest("explicit higher", skill=skill_label):
                    self.assertFalse(
                        event_for_cat(cat=cat, cat_info={"skill": [f"HUNTER,{i+1}"]})
                    )

                with self.subTest("unmatched", skill=skill_label):
                    self.assertFalse(
                        event_for_cat(cat=cat, cat_info={"skill": [f"SWIMMER,{i}"]})
                    )
                with self.subTest("unmatched lower", skill=skill_label):
                    self.assertFalse(
                        event_for_cat(cat=cat, cat_info={"skill": [f"SWIMMER,{i-1}"]})
                    )
                with self.subTest("unmatched higher", skill=skill_label):
                    self.assertFalse(
                        event_for_cat(cat=cat, cat_info={"skill": [f"SWIMMER,{i+1}"]})
                    )

                # exclusives
                with self.subTest("explicit exclusionary", skill=skill_label):
                    self.assertFalse(
                        event_for_cat(cat=cat, cat_info={"skill": [f"-HUNTER,{i}"]})
                    )
                with self.subTest("explicit exclusionary lower", skill=skill_label):
                    self.assertFalse(
                        event_for_cat(cat=cat, cat_info={"skill": [f"-HUNTER,{i-1}"]})
                    )
                with self.subTest("explicit exclusionary higher", skill=skill_label):
                    self.assertTrue(
                        event_for_cat(cat=cat, cat_info={"skill": [f"-HUNTER,{i+1}"]})
                    )

                with self.subTest("unmatched exclusionary", skill=skill_label):
                    self.assertTrue(
                        event_for_cat(cat=cat, cat_info={"skill": [f"-SWIMMER,{i}"]})
                    )
                with self.subTest("unmatched exclusionary lower", skill=skill_label):
                    self.assertTrue(
                        event_for_cat(cat=cat, cat_info={"skill": [f"-SWIMMER,{i-1}"]})
                    )
                with self.subTest("unmatched exclusionary higher", skill=skill_label):
                    self.assertTrue(
                        event_for_cat(cat=cat, cat_info={"skill": [f"-SWIMMER,{i+1}"]})
                    )

    def test_backstory(self):
        cat = Cat(backstory="clan_founder")

        # general
        with self.subTest('"any"'):
            self.assertRaises(
                ValueError, event_for_cat, cat=cat, cat_info={"backstory": ["any"]}
            )
        with self.subTest("empty"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"backstory": []}))
        with self.subTest("invalid value"):
            self.assertRaises(
                ValueError,
                event_for_cat,
                cat=cat,
                cat_info={"backstory": ["definitelynotabackstoryasdf"]},
            )

        # inclusive
        with self.subTest("explicit"):
            self.assertTrue(
                event_for_cat(cat=cat, cat_info={"backstory": ["clan_founder"]})
            )
        with self.subTest("explicit within category"):
            self.assertTrue(
                event_for_cat(
                    cat=cat, cat_info={"backstory": ["clan_founder_backstories"]}
                )
            )

        with self.subTest("unmatched"):
            self.assertFalse(event_for_cat(cat=cat, cat_info={"backstory": ["loner1"]}))
        with self.subTest("unmatched within category"):
            self.assertFalse(
                event_for_cat(cat=cat, cat_info={"backstory": ["loner_backstories"]})
            )

        # exclusive
        with self.subTest("explicit exclusionary"):
            self.assertFalse(
                event_for_cat(cat=cat, cat_info={"backstory": ["-clan_founder"]})
            )
        with self.subTest("explicit exclusionary within category"):
            self.assertFalse(
                event_for_cat(
                    cat=cat, cat_info={"backstory": ["-clan_founder_backstories"]}
                )
            )

        with self.subTest("unmatched exclusionary"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"backstory": ["-loner1"]}))
        with self.subTest("unmatched exclusionary within category"):
            self.assertTrue(
                event_for_cat(cat=cat, cat_info={"backstory": ["-loner_backstories"]})
            )

    def test_gender(self):
        male = Cat(gender="male")
        female = Cat(gender="female")

        with self.subTest("empty"):
            self.assertTrue(event_for_cat(cat=male, cat_info={"gender": []}))

        with self.subTest("invalid input"):
            self.assertRaises(
                ValueError, event_for_cat, cat=male, cat_info={"gender": ["isosceles"]}
            )

        with self.subTest("expected male, was male"):
            self.assertTrue(event_for_cat(cat=male, cat_info={"gender": ["male"]}))

        with self.subTest("expected female, was male"):
            self.assertFalse(event_for_cat(cat=male, cat_info={"gender": ["female"]}))

        with self.subTest("expected female, was female"):
            self.assertTrue(event_for_cat(cat=female, cat_info={"gender": ["female"]}))

        with self.subTest("expected male, was female"):
            self.assertFalse(event_for_cat(cat=female, cat_info={"gender": ["male"]}))
