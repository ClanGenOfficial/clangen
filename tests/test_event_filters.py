import unittest
import os
from copy import deepcopy
from itertools import permutations

from scripts.cat.personality import Personality
from scripts.cat.skills import Skill, SkillPath
from scripts.clan_resources.point_of_interest import (
    add_poi,
    get_poi_names_set,
    get_poi_tags_set,
    clear_pois,
    generate_and_add_new_poi,
)

try:
    import tomllib
except ImportError:
    import tomli as tomllib

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, create_cat
from scripts.cat_relations.inheritance2 import inheritance_db
from scripts.cat.enums import CatRank, CatAge, CatSocial, CatGroup, CatStanding
from scripts.cat.status import StatusDict
from scripts.cat_relations.enums import RelType, rel_type_tiers, RelTier
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.event_filters import (
    event_for_location,
    event_for_season,
    event_for_tags,
    event_for_cat,
    event_for_poi,
    check_rel_constraint_groups,
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


class TestPointsOfInterest(unittest.TestCase):
    def setUp(self):
        game.clan = Clan()
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.test_cat = create_cat(CatRank.LEADER, moons=50)
        game.clan.leader = self.test_cat

        clear_pois()

    def test_add_poi(self):
        # add the POI
        poi_to_add = {
            "test_name": {
                "category": "gathering",
                "biome": ["any"],
                "tags": ["water", "prey:fish"],
            }
        }

        add_poi("test_name", poi_to_add["test_name"])

        # confirm it exists
        self.assertIn("test_name", get_poi_names_set())

        # confirm tags exist appropriately
        self.assertIn("water", get_poi_tags_set())
        self.assertIn("prey:fish", get_poi_tags_set())
        self.assertIn("prey", get_poi_tags_set())
        self.assertNotIn("fish", get_poi_tags_set())

    def test_clear_pois(self):
        poi_to_add = {
            "test_name": {
                "category": "gathering",
                "biome": ["any"],
                "tags": ["water", "prey:fish"],
            }
        }

        add_poi("test_name", poi_to_add["test_name"])

        # clear POI
        clear_pois()

        # confirm it not exists
        self.assertNotIn("test_name", get_poi_names_set())
        # confirm tags removed exist appropriately
        self.assertNotIn("water", get_poi_tags_set())
        self.assertNotIn("prey:fish", get_poi_tags_set())
        self.assertNotIn("prey", get_poi_tags_set())

    def test_choose_poi(self):
        possible_pois = {
            "forest_poi": {
                "category": "gathering",
                "biome": ["forest"],
                "tags": ["trees"],
            },
            "plains_poi": {
                "category": "gathering",
                "biome": ["plains"],
                "tags": ["Twolegs"],
            },
            "terrain_poi": {
                "category": "terrain",
                "biome": ["forest"],
                "tags": ["rocks"],
            },
            "moonplace_poi": {
                "category": "moonplace",
                "biome": ["forest"],
                "tags": ["rocks"],
            },
        }

        # combinations in the order "expected name", "not expected name", "biome", "category"
        combinations = {
            "biome": ["forest_poi", "plains_poi", "Forest", "gathering"],
            "category": ["terrain_poi", "moonpool_poi", "Forest", "terrain"],
        }

        for name, (expected, unexpected, biome, category) in combinations.items():
            with self.subTest(name=name):
                clear_pois()
                generate_and_add_new_poi(
                    biome=biome, category=category, possible_pois=possible_pois
                )

                # confirm it exists
                self.assertIn(expected, get_poi_names_set())
                self.assertNotIn(unexpected, get_poi_names_set())

        with self.subTest(title="file loaded PoIs"):
            clear_pois()
            generate_and_add_new_poi(biome="Forest", category="gathering")
            self.assertEqual(len(get_poi_names_set()), 1)
            self.assertGreater(len(get_poi_tags_set()), 0)

    def test_error_forbid_duplicate_poi(self):
        poi_to_add = {
            "test_name": {
                "category": "gathering",
                "biome": ["any"],
                "tags": ["water", "prey:fish"],
            }
        }

        add_poi("test_name", poi_to_add["test_name"])
        self.assertRaises(
            Exception,
            generate_and_add_new_poi,
            biome="Forest",
            category="gathering",
            possible_pois=poi_to_add,
        )

    def test_error_no_possible_poi(self):
        poi_to_add = {
            "test_name": {
                "category": "gathering",
                "biome": ["any"],
                "tags": ["water", "prey:fish"],
            }
        }

        self.assertRaises(
            Exception,
            generate_and_add_new_poi,
            biome="Forest",
            category="moonplace",
            possible_pois=poi_to_add,
        )

    def test_filter_poi(self):
        # add the POI
        poi_to_add = {
            "test_name": {
                "category": "gathering",
                "biome": ["any"],
                "tags": ["water", "prey:fish"],
            }
        }

        add_poi("test_name", poi_to_add["test_name"])

        # expected True combinations
        combinations = {
            "match name": {"name": ["test_name"]},
            "match name multi": {"name": ["other_possibility", "test_name"]},
            "match tag generic to generic": {"tags": ["water"]},
            "match tag exact to exact": {"tags": ["prey:fish"]},
            "match tag generic to exact": {"tags": ["prey"]},
            "empty all": {"name": [], "tags": []},
            "empty name": {"name": [], "tags": ["water"]},
            "empty tags": {"name": ["test_name"], "tags": []},
        }

        for title, event_poi in combinations.items():
            with self.subTest(title=title):
                self.assertTrue(event_for_poi(event_poi))

        # expected False combinations
        bad_combinations = {
            "no name": {"name": ["something_else", "aint_it_chief"]},
            "no tag": {"tags": ["Twolegs", "cave"]},
            "match generic tag but not exact": {"tags": ["prey:bird"]},
        }

        for title, event_poi in bad_combinations.items():
            with self.subTest(title=title):
                self.assertFalse(event_for_poi(event_poi))


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

        inheritance_db.load_inheritances(Cat)

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
        inheritance_db.load_inheritances(Cat)

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

        inheritance_db.load_inheritances(Cat)

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

        inheritance_db.load_inheritances(Cat)

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

        inheritance_db.load_inheritances(Cat)

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

    def test_multiple(self):
        app = Cat(moons=8, disable_random=True)
        mentor = Cat(
            moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR), disable_random=True
        )

        app.update_mentor(new_mentor=mentor.ID)
        with self.subTest(
            "are mentor/app, expected not mentor/app and not parent/child"
        ):
            self.assertFalse(
                event_for_cat(
                    cat_info={"relationship_status": ["-mentor/app", "-parent/child"]},
                    cat=mentor,
                    cat_group=[mentor, app],
                )
            )


class TestInterpersonalRelationshipConstraints2(unittest.TestCase):
    """
    This one specifically tests with the updated RelationshipConstraintDict usage and function.
    Since it can handle more specific configurations of cats it could use different test coverage.
    """

    def test_strangers(self):
        cat1 = Cat(disable_random=True)
        cat2 = Cat(disable_random=True)
        cat3 = Cat(disable_random=True)

        cat1.relationships[cat2.ID] = Relationship(
            **{
                "cat_from": cat1,
                "cat_to": cat2,
                "like": 20,
                "romance": 10,
                "respect": 67,
            }
        )
        cat2.relationships = {}
        cat3.relationships = {}
        involved_cats = {
            "c1": cat1,
            "c2": cat2,
            "c3": cat3,
        }
        inheritance_db.load_inheritances(Cat)

        with self.subTest("are strangers, expected strangers"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1", "c2"],
                        "cats_to": ["c3"],
                        "mutual": False,
                        "constraints": ["strangers"],
                    },
                    involved_cats=involved_cats,
                )
            )

        with self.subTest("are strangers, expected not strangers"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1", "c2"],
                        "cats_to": ["c3"],
                        "mutual": False,
                        "constraints": ["-strangers"],
                    },
                    involved_cats=involved_cats,
                )
            )

        with self.subTest("are not strangers, expected strangers"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["c3", "c2"],
                        "mutual": False,
                        "constraints": ["strangers"],
                    },
                    involved_cats=involved_cats,
                )
            )

        with self.subTest("are not strangers, expected not strangers"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["c3", "c2"],
                        "mutual": False,
                        "constraints": ["-strangers"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_siblings(self):
        parent = Cat(disable_random=True)
        cat1 = Cat(disable_random=True, parent1=parent.ID)
        cat2 = Cat(disable_random=True, parent1=parent.ID)
        inheritance_db.load_inheritances(Cat)

        involved_cats = {
            "parent": parent,
            "c1": cat1,
            "c2": cat2,
        }

        with self.subTest("are siblings, expected siblings"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["c2"],
                        "mutual": False,
                        "constraints": ["siblings"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are siblings, expected not siblings"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["c2"],
                        "mutual": False,
                        "constraints": ["-siblings"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not siblings, expected siblings"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["parent"],
                        "mutual": False,
                        "constraints": ["siblings"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not siblings, expected not siblings"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["parent"],
                        "mutual": False,
                        "constraints": ["-siblings"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("some, but not all, are siblings. expected siblings."):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1", "parent"],
                        "cats_to": ["c2"],
                        "mutual": False,
                        "constraints": ["siblings"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("some, but not all, are siblings. expected not siblings."):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1", "parent"],
                        "cats_to": ["c2"],
                        "mutual": False,
                        "constraints": ["-siblings"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_littermates(self):
        parent = Cat(disable_random=True)
        cat1 = Cat(parent1=parent.ID, moons=1, disable_random=True)
        cat2 = Cat(parent1=parent.ID, moons=1, disable_random=True)
        sib = Cat(parent1=parent.ID, moons=10, disable_random=True)

        inheritance_db.load_inheritances(Cat)

        involved_cats = {"parent": parent, "c1": cat1, "c2": cat2, "sib": sib}

        with self.subTest("are littermates, expected littermates"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["c2"],
                        "mutual": False,
                        "constraints": ["littermates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are littermates, expected not littermates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["c2"],
                        "mutual": False,
                        "constraints": ["-littermates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not littermates, expected littermates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["sib"],
                        "mutual": False,
                        "constraints": ["littermates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not littermates, expected not littermates"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["sib"],
                        "mutual": False,
                        "constraints": ["-littermates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("some, but not all, are littermates, expected littermates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["sib", "c2"],
                        "mutual": False,
                        "constraints": ["littermates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest(
            "some, but not all, are littermates, expected not littermates"
        ):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["sib", "c2"],
                        "mutual": False,
                        "constraints": ["-littermates"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_mates(self):
        mate1 = Cat(disable_random=True)
        mate2 = Cat(disable_random=True)
        other = Cat(disable_random=True)

        involved_cats = {"mate1": mate1, "mate2": mate2, "other": other}

        mate1.mate.append(mate2.ID)
        mate2.mate.append(mate1.ID)

        with self.subTest("are mates, expected mates"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["mate2"],
                        "mutual": False,
                        "constraints": ["mates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are mates, expected not mates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["mate2"],
                        "mutual": False,
                        "constraints": ["-mates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not mates, expected mates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["other"],
                        "mutual": False,
                        "constraints": ["mates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not mates, expected not mates"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["other"],
                        "mutual": False,
                        "constraints": ["-mates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not all mates, expected mates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["mate2", "other"],
                        "mutual": False,
                        "constraints": ["mates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not all mates, expected not mates"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["mate2", "other"],
                        "mutual": False,
                        "constraints": ["-mates"],
                    },
                    involved_cats=involved_cats,
                )
            )

        mate1.mate.append(other.ID)
        with self.subTest(
            "all cat_to are mated to cat_from, expected non-mutual mates"
        ):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["mate2", "other"],
                        "mutual": False,
                        "constraints": ["mates"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("all cat_to are mated to cat_from, expected mutual mates"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mate1"],
                        "cats_to": ["mate2", "other"],
                        "mutual": True,
                        "constraints": ["mates"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_parent_child(self):
        parent = Cat(disable_random=True)
        cat1 = Cat(parent1=parent.ID, disable_random=True)
        cat2 = Cat(disable_random=True)

        inheritance_db.load_inheritances(Cat)
        involved_cats = {"parent": parent, "c1": cat1, "c2": cat2}

        with self.subTest("are parent/child, expected parent/child"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["parent"],
                        "cats_to": ["c1"],
                        "mutual": False,
                        "constraints": ["parent/child"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are parent/child, expected not parent/child"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["parent"],
                        "cats_to": ["c1"],
                        "mutual": False,
                        "constraints": ["-parent/child"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not parent/child, expected parent/child"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["parent", "c2"],
                        "cats_to": ["c1"],
                        "mutual": False,
                        "constraints": ["parent/child"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not parent/child, expected not parent/child"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c2"],
                        "cats_to": ["c1"],
                        "mutual": False,
                        "constraints": ["-parent/child"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_child_parent(self):
        parent = Cat(disable_random=True)
        cat1 = Cat(parent1=parent.ID, disable_random=True)
        cat2 = Cat(disable_random=True)

        inheritance_db.load_inheritances(Cat)
        involved_cats = {"parent": parent, "c1": cat1, "c2": cat2}

        with self.subTest("are child/parent, expected child/parent"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["parent"],
                        "mutual": False,
                        "constraints": ["child/parent"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are child/parent, expected not child/parent"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1"],
                        "cats_to": ["parent"],
                        "mutual": False,
                        "constraints": ["-child/parent"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not child/parent, expected child/parent"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c1", "c2"],
                        "cats_to": ["parent"],
                        "mutual": False,
                        "constraints": ["child/parent"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not child/parent, expected not child/parent"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["c2"],
                        "cats_to": ["parent"],
                        "mutual": False,
                        "constraints": ["-child/parent"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_app_mentor(self):
        app = Cat(moons=8, status_dict=StatusDict(rank=CatRank.APPRENTICE))
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app2 = Cat(moons=8, status_dict=StatusDict(rank=CatRank.APPRENTICE))

        app.update_mentor(new_mentor=mentor.ID)

        involved_cats = {"app": app, "mentor": mentor, "app2": app2}

        with self.subTest("are app/mentor, expected app/mentor"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app"],
                        "cats_to": ["mentor"],
                        "mutual": False,
                        "constraints": ["app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )

        with self.subTest("are app/mentor, expected not app/mentor"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app"],
                        "cats_to": ["mentor"],
                        "mutual": False,
                        "constraints": ["-app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not app/mentor, expected app/mentor"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app"],
                        "mutual": False,
                        "constraints": ["app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not app/mentor, expected not app/mentor"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app"],
                        "mutual": False,
                        "constraints": ["-app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not all app/mentor, expected app/mentor"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app", "app2"],
                        "cats_to": ["mentor"],
                        "mutual": False,
                        "constraints": ["app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("some but not all app/mentor, expected not app/mentor"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app", "app2"],
                        "cats_to": ["mentor"],
                        "mutual": False,
                        "constraints": ["-app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("trying to find app with 2 mentors, and expects app/mentor"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app"],
                        "cats_to": ["mentor", "app2"],
                        "mutual": False,
                        "constraints": ["app/mentor"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_mentor_app(self):
        app = Cat(moons=8, status_dict=StatusDict(rank=CatRank.APPRENTICE))
        mentor = Cat(moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR))

        app2 = Cat(moons=8, status_dict=StatusDict(rank=CatRank.APPRENTICE))

        app.update_mentor(new_mentor=mentor.ID)

        involved_cats = {"app": app, "mentor": mentor, "app2": app2}

        with self.subTest("are mentor/app, expected mentor/app"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app"],
                        "mutual": False,
                        "constraints": ["mentor/app"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are mentor/app, expected not mentor/app"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app"],
                        "mutual": False,
                        "constraints": ["-mentor/app"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not mentor/app, expected mentor/app"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app"],
                        "cats_to": ["mentor"],
                        "mutual": False,
                        "constraints": ["mentor/app"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not mentor/app, expected not mentor/app"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["app"],
                        "cats_to": ["mentor"],
                        "mutual": False,
                        "constraints": ["-mentor/app"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not all mentor/app, expected mentor/app"):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app", "app2"],
                        "mutual": False,
                        "constraints": ["mentor/app"],
                    },
                    involved_cats=involved_cats,
                )
            )
        with self.subTest("are not all mentor/app, expected not any mentor/app"):
            self.assertTrue(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app", "app2"],
                        "mutual": False,
                        "constraints": ["-mentor/app"],
                    },
                    involved_cats=involved_cats,
                )
            )

    def test_multiple(self):
        app = Cat(moons=8, disable_random=True)
        mentor = Cat(
            moons=26, status_dict=StatusDict(rank=CatRank.WARRIOR), disable_random=True
        )
        involved_cats = {"mentor": mentor, "app": app}

        app.update_mentor(new_mentor=mentor.ID)
        with self.subTest(
            "are mentor/app, expected not mentor/app and not parent/child"
        ):
            self.assertFalse(
                check_rel_constraint_groups(
                    {
                        "cats_from": ["mentor"],
                        "cats_to": ["app"],
                        "mutual": False,
                        "constraints": ["-mentor/app", "-parent/child"],
                    },
                    involved_cats=involved_cats,
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

    def test_group(self):
        cat = Cat()
        test_dict = {
            CatGroup.STARCLAN: CatGroup.STARCLAN_ID,
            CatGroup.DARK_FOREST: CatGroup.DARK_FOREST_ID,
            CatGroup.UNKNOWN_RESIDENCE: CatGroup.UNKNOWN_RESIDENCE_ID,
        }
        for group, group_id in test_dict.items():
            cat.status.add_to_group(group_id)
            # is dead
            with self.subTest(f"is part of afterlife"):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"group": ["afterlife"]})
                )

            # is alive
            with self.subTest(f"isn't part of afterlife"):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"group": [f"-afterlife"]})
                )

        # no group
        cat.status.leave_group(CatSocial.LONER)
        with self.subTest(f"isn't part of a group"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"group": ["no_group"]}))

        # yes group
        cat.status.add_to_group(CatGroup.PLAYER_CLAN_ID)
        with self.subTest(f"is part of a group"):
            self.assertTrue(event_for_cat(cat=cat, cat_info={"group": ["-no_group"]}))

        # doesn't match another cat
        other_cat = Cat()
        other_cat.status.add_to_group(CatGroup.STARCLAN_ID)
        with self.subTest(f"doesn't match other cat's group"):
            self.assertTrue(
                event_for_cat(
                    cat=cat,
                    cat_info={"group": ["-match:r_c"]},
                    involved_cat_dict={"m_c": cat, "r_c": other_cat},
                )
            )

        # matches another cat
        cat.status.add_to_group(CatGroup.STARCLAN_ID)
        with self.subTest(f"does match other cat's group"):
            self.assertTrue(
                event_for_cat(
                    cat=cat,
                    cat_info={"group": ["match:r_c"]},
                    involved_cat_dict={"m_c": cat, "r_c": other_cat},
                )
            )

        test_dict = {
            CatGroup.PLAYER_CLAN: CatGroup.PLAYER_CLAN_ID,
            CatGroup.STARCLAN: CatGroup.STARCLAN_ID,
            CatGroup.DARK_FOREST: CatGroup.DARK_FOREST_ID,
            CatGroup.UNKNOWN_RESIDENCE: CatGroup.UNKNOWN_RESIDENCE_ID,
            CatGroup.OTHER_CLAN: "5",
        }
        game.used_group_IDs["5"] = CatGroup.OTHER_CLAN

        for group, group_id in test_dict.items():
            cat.status.add_to_group(group_id)
            # is part of specific group
            with self.subTest(f"is part of {group}"):
                self.assertTrue(event_for_cat(cat=cat, cat_info={"group": [group]}))

            # isn't part of specific group
            with self.subTest(f"isn't part of {group}"):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"group": [f"-{group}"]})
                )

    def test_standing(self):
        standings = [CatStanding.LEFT, CatStanding.LOST, CatStanding.EXILED]
        test_dict = {
            CatGroup.PLAYER_CLAN: CatGroup.PLAYER_CLAN_ID,
            CatGroup.STARCLAN: CatGroup.STARCLAN_ID,
            CatGroup.DARK_FOREST: CatGroup.DARK_FOREST_ID,
            CatGroup.UNKNOWN_RESIDENCE: CatGroup.UNKNOWN_RESIDENCE_ID,
            CatGroup.OTHER_CLAN: "5",
            "afterlife": CatGroup.STARCLAN_ID,
            "match:r_c": CatGroup.PLAYER_CLAN_ID,
        }
        game.used_group_IDs["5"] = CatGroup.OTHER_CLAN
        cat = Cat()
        other_cat = Cat()

        # checking current standing
        for group, ID in test_dict.items():
            for standing in standings:
                cat.status.change_standing(standing, ID)
                other_cat.status.add_to_group(ID)
                test_dict["match:r_c"] = ID
                with self.subTest(
                    f"has current standing: {standing} with group: {group}"
                ):
                    self.assertTrue(
                        event_for_cat(
                            cat=cat,
                            cat_info={
                                "standing": {"group": [group], "currently": [standing]}
                            },
                            other_involved_clan_id="5",
                            involved_cat_dict={"m_c": cat, "r_c": other_cat},
                        )
                    )
                with self.subTest(
                    f"shouldn't have current standing: {standing} with group: {group}"
                ):
                    self.assertFalse(
                        event_for_cat(
                            cat=cat,
                            cat_info={
                                "standing": {
                                    "group": [group],
                                    "currently": [f"-{standing}"],
                                }
                            },
                            other_involved_clan_id="5",
                            involved_cat_dict={"m_c": cat, "r_c": other_cat},
                        )
                    )

        # checking past standing
        for group, ID in test_dict.items():
            for standing in standings:
                cat.status.change_standing(standing, ID)
                cat.status.change_standing(CatStanding.MEMBER, ID)
                other_cat.status.add_to_group(ID)
                test_dict["match:r_c"] = ID
                with self.subTest(f"has past standing: {standing} with group: {group}"):
                    self.assertTrue(
                        event_for_cat(
                            cat=cat,
                            cat_info={
                                "standing": {"group": [group], "past": [standing]}
                            },
                            other_involved_clan_id="5",
                            involved_cat_dict={"m_c": cat, "r_c": other_cat},
                        )
                    )
                with self.subTest(
                    f"shouldn't have past standing: {standing} with group: {group}"
                ):
                    self.assertFalse(
                        event_for_cat(
                            cat=cat,
                            cat_info={
                                "standing": {
                                    "group": [group],
                                    "past": [f"-{standing}"],
                                }
                            },
                            other_involved_clan_id="5",
                            involved_cat_dict={"m_c": cat, "r_c": other_cat},
                        )
                    )

        # checking past and current
        for group, ID in test_dict.items():
            for standing in standings:
                cat.status.change_standing(CatStanding.MEMBER, ID)
                cat.status.change_standing(standing, ID)
                other_cat.status.add_to_group(ID)
                test_dict["match:r_c"] = ID
                with self.subTest(
                    f"has current standing: {standing} and is past member with group: {group}"
                ):
                    self.assertTrue(
                        event_for_cat(
                            cat=cat,
                            cat_info={
                                "standing": {
                                    "group": [group],
                                    "currently": [standing],
                                    "past": ["member"],
                                }
                            },
                            other_involved_clan_id="5",
                            involved_cat_dict={"m_c": cat, "r_c": other_cat},
                        )
                    )
                with self.subTest(
                    f"has current standing: {standing} but can't be past member with group: {group}"
                ):
                    self.assertFalse(
                        event_for_cat(
                            cat=cat,
                            cat_info={
                                "standing": {
                                    "group": [group],
                                    "currently": [standing],
                                    "past": ["-member"],
                                }
                            },
                            other_involved_clan_id="5",
                            involved_cat_dict={"m_c": cat, "r_c": other_cat},
                        )
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
                self.assertTrue(event_for_cat(cat=cat, cat_info={"past_status": []}))
            with self.subTest(
                "current rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"past_status": [new_rank]})
                )
            with self.subTest(
                "former rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"past_status": [old_rank]})
                )
            with self.subTest(
                '"any"', old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"past_status": ["any"]})
                )
            with self.subTest(
                "other rank",
                old_rank=old_rank.value,
                new_rank=new_rank.value,
                other_rank=other_rank,
            ):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"past_status": [other_rank]})
                )

            with self.subTest(
                "not current rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"past_status": [f"-{new_rank}"]})
                )
            with self.subTest(
                "not former rank", old_rank=old_rank.value, new_rank=new_rank.value
            ):
                self.assertFalse(
                    event_for_cat(cat=cat, cat_info={"past_status": [f"-{old_rank}"]})
                )
            with self.subTest(
                "not other rank",
                old_rank=old_rank.value,
                new_rank=new_rank.value,
                other_rank=other_rank,
            ):
                self.assertTrue(
                    event_for_cat(cat=cat, cat_info={"past_status": [f"-{other_rank}"]})
                )

    def test_stat(self):
        """
        Checks if the `must_have_both` works.
        """
        cat = Cat()

        # has both
        with self.subTest("has both"):
            cat.personality = Personality(trait="arrogant")
            cat.skills.primary = Skill(SkillPath.CAMP, points=0)
            cat.skills.secondary = Skill(SkillPath.HUNTER, points=0)

            self.assertTrue(
                event_for_cat(
                    cat=cat,
                    cat_info={
                        "stat": {
                            "skill": ["CAMP, 0"],
                            "trait": ["arrogant"],
                            "must_have_both": True,
                        }
                    },
                )
            )

        # has none
        with self.subTest("has neither"):
            cat.personality = Personality(trait="daring")
            cat.skills.primary = Skill(SkillPath.SENSE, points=0)
            cat.skills.secondary = Skill(SkillPath.HUNTER, points=0)

            self.assertFalse(
                event_for_cat(
                    cat=cat,
                    cat_info={
                        "stat": {
                            "skill": ["CAMP, 0"],
                            "trait": ["arrogant"],
                            "must_have_both": True,
                        }
                    },
                )
            )

        # missing skill allowed
        with self.subTest("missing skill allowed"):
            cat.personality = Personality(trait="arrogant")
            cat.skills.primary = Skill(SkillPath.SENSE, points=0)
            cat.skills.secondary = Skill(SkillPath.HUNTER, points=0)

            self.assertTrue(
                event_for_cat(
                    cat=cat,
                    cat_info={
                        "stat": {
                            "skill": ["CAMP, 0"],
                            "trait": ["arrogant"],
                            "must_have_both": False,
                        }
                    },
                )
            )

        # missing skill not allowed
        with self.subTest("missing skill not allowed"):
            cat.personality = Personality(trait="arrogant")
            cat.skills.primary = Skill(SkillPath.SENSE, points=0)
            cat.skills.secondary = Skill(SkillPath.HUNTER, points=0)

            self.assertFalse(
                event_for_cat(
                    cat=cat,
                    cat_info={
                        "stat": {
                            "skill": ["CAMP, 0"],
                            "trait": ["arrogant"],
                            "must_have_both": True,
                        }
                    },
                )
            )

        # missing trait allowed
        with self.subTest("missing trait allowed"):
            cat.personality = Personality(trait="daring")
            cat.skills.primary = Skill(SkillPath.CAMP, points=0)
            cat.skills.secondary = Skill(SkillPath.HUNTER, points=0)

            self.assertTrue(
                event_for_cat(
                    cat=cat,
                    cat_info={
                        "stat": {
                            "skill": ["CAMP, 0"],
                            "trait": ["arrogant"],
                            "must_have_both": False,
                        }
                    },
                )
            )

        # missing trait not allowed
        with self.subTest("missing trait not allowed"):
            cat.personality = Personality(trait="daring")
            cat.skills.primary = Skill(SkillPath.CAMP, points=0)

            self.assertFalse(
                event_for_cat(
                    cat=cat,
                    cat_info={
                        "stat": {
                            "skill": ["CAMP, 0"],
                            "trait": ["arrogant"],
                            "must_have_both": True,
                        }
                    },
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

    def test_health(self):
        working_cat = Cat()
        broken_cat = Cat()
        Cat.disable_random = True
        broken_cat.get_injured(name="broken bone")
        ill_cat = Cat()
        ill_cat.get_ill(name="greencough")
        born_para_cat = Cat()
        born_para_cat.get_permanent_condition(name="paralyzed", born_with=True)
        acquired_para_cat = Cat()
        acquired_para_cat.get_permanent_condition(name="paralyzed", born_with=False)

        # cat must be working and is
        with self.subTest("must work and is working"):
            self.assertTrue(
                event_for_cat(cat=working_cat, cat_info={"health": {"working": True}})
            )

        # cat must be working and isn't
        with self.subTest("must work and isn't working"):
            self.assertFalse(
                event_for_cat(cat=broken_cat, cat_info={"health": {"working": True}})
            )

        # cat can't be working and is
        with self.subTest("can't work and is working"):
            self.assertFalse(
                event_for_cat(cat=working_cat, cat_info={"health": {"working": False}})
            )

        # cat can't be working and isn't
        with self.subTest("can't work and isn't working"):
            self.assertTrue(
                event_for_cat(cat=broken_cat, cat_info={"health": {"working": False}})
            )

        # cat should have a condition and does
        test_dict = {
            broken_cat: ["broken bone"],
            ill_cat: ["greencough"],
            born_para_cat: ["paralyzed"],
        }
        for cat, condition in test_dict.items():
            with self.subTest(f"has required condition: {condition}"):
                self.assertTrue(
                    event_for_cat(
                        cat=cat, cat_info={"health": {"condition": condition}}
                    )
                )

        # cat has the wrong condition
        test_dict = {
            broken_cat: ["whitecough"],
            ill_cat: ["whitecough"],
            born_para_cat: ["whitecough"],
        }
        for cat, condition in test_dict.items():
            with self.subTest(f"does not have required condition: {condition}"):
                self.assertFalse(
                    event_for_cat(
                        cat=cat, cat_info={"health": {"condition": condition}}
                    )
                )

        # cat has no condition but needs one
        with self.subTest(f"does not have any condition"):
            self.assertFalse(
                event_for_cat(
                    cat=working_cat, cat_info={"health": {"condition": ["greencough"]}}
                )
            )

        # condition must be acquired and is
        with self.subTest(f"condition must be acquired and is"):
            self.assertTrue(
                event_for_cat(
                    cat=acquired_para_cat,
                    cat_info={
                        "health": {"condition": ["paralyzed"], "must_be_acquired": True}
                    },
                )
            )

        # condition must be acquired and isn't
        with self.subTest(f"condition must be acquired and isn't"):
            self.assertFalse(
                event_for_cat(
                    cat=born_para_cat,
                    cat_info={
                        "health": {"condition": ["paralyzed"], "must_be_acquired": True}
                    },
                )
            )

        # condition must be congenital and is
        with self.subTest(f"condition must be congenital and is"):
            self.assertTrue(
                event_for_cat(
                    cat=born_para_cat,
                    cat_info={
                        "health": {
                            "condition": ["paralyzed"],
                            "must_be_congenital": True,
                        }
                    },
                )
            )

        # condition must be congenital and isn't
        with self.subTest(f"condition must be congenital and isn't"):
            self.assertFalse(
                event_for_cat(
                    cat=acquired_para_cat,
                    cat_info={
                        "health": {
                            "condition": ["paralyzed"],
                            "must_be_congenital": True,
                        }
                    },
                )
            )
