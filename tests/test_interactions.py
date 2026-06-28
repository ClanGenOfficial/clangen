import os
import unittest

from scripts.cat.status import StatusDict
from scripts.cat_relations.enums import rel_type_tiers, RelType

from scripts.cat.enums import CatRank
from scripts.events_module.event_filters import filter_relationship_type
from scripts.events_module.parameter_dicts import InvolvedCatDict, StatDict
from scripts.events_module.relationship import generate_pair_event
from scripts.events_module.text_pool_event import TextPoolEvent

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.cat.skills import SkillPath, Skill


class RelationshipConstraints(unittest.TestCase):
    def test_siblings(self):
        # given
        parent = Cat()
        cat_from = Cat(parent1=parent.ID)
        cat_to = Cat(parent1=parent.ID)

        # then
        self.assertTrue(filter_relationship_type([cat_from, cat_to], ["sibling"]))
        self.assertTrue(filter_relationship_type([cat_from, cat_to], ["-mates"]))

    def test_mates(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        cat_from.mate.append(cat_to.ID)
        cat_to.mate.append(cat_from.ID)

        # then
        self.assertTrue(filter_relationship_type([cat_from, cat_to], ["mates"]))
        self.assertFalse(filter_relationship_type([cat_from, cat_to], ["-mates"]))

    def test_parent_child_combo(self):
        # given
        parent = Cat()
        child = Cat(parent1=parent.ID)

        # then
        self.assertTrue(filter_relationship_type([child, parent], ["child/parent"]))
        self.assertFalse(filter_relationship_type([child, parent], ["parent/child"]))
        self.assertTrue(filter_relationship_type([parent, child], ["parent/child"]))
        self.assertFalse(filter_relationship_type([parent, child], ["child/parent"]))

    def test_rel_values_only_constraint_pos(self):
        # given
        cat_from1 = Cat()
        cat_to1 = Cat()
        low_rel = Relationship(cat_from1, cat_to1)
        low_rel.romance = 10
        low_rel.like = 10
        low_rel.comfort = 10
        low_rel.trust = 10
        low_rel.respect = 10
        cat_from1.relationships.update({cat_to1.ID: low_rel})

        cat_from2 = Cat()
        cat_to2 = Cat()
        mid_rel = Relationship(cat_from2, cat_to2)
        mid_rel.romance = 50
        mid_rel.like = 50
        mid_rel.comfort = 50
        mid_rel.trust = 50
        mid_rel.respect = 50
        cat_from2.relationships.update({cat_to2.ID: mid_rel})

        cat_from3 = Cat()
        cat_to3 = Cat()
        high_rel = Relationship(cat_from3, cat_to3)
        high_rel.romance = 90
        high_rel.like = 90
        high_rel.comfort = 90
        high_rel.trust = 90
        high_rel.respect = 90
        cat_from3.relationships.update({cat_to3.ID: high_rel})

        # then
        for level_list in rel_type_tiers.values():
            for l in level_list:
                # last index of the list should be the highest positive
                if l == level_list[-1]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from3, cat_to3],
                            [f"{l}_only"],
                        )
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from2, cat_to2],
                            [f"{l}_only"],
                        )
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{l}_only"],
                        )
                    )
                # next is middle pos
                elif l == level_list[-2]:
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from3, cat_to3],
                            [f"{l}_only"],
                        )
                    )
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from2, cat_to2],
                            [f"{l}_only"],
                        )
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{l}_only"],
                        )
                    )
                # next is the lowest pos
                elif l == level_list[-3]:
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from3, cat_to3],
                            [f"{l}_only"],
                        )
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from2, cat_to2],
                            [f"{l}_only"],
                        )
                    )
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{l}_only"],
                        )
                    )

    def test_rel_values_only_constraint_neg(self):
        # given
        cat_from1 = Cat()
        cat_to1 = Cat()
        mid_rel = Relationship(cat_from1, cat_to1)
        mid_rel.romance = -50
        mid_rel.like = -50
        mid_rel.comfort = -50
        mid_rel.trust = -50
        mid_rel.respect = -50
        cat_from1.relationships.update({cat_to1.ID: mid_rel})

        cat_from2 = Cat()
        cat_to2 = Cat()
        low_rel = Relationship(cat_from2, cat_to2)
        low_rel.romance = -10
        low_rel.like = -10
        low_rel.comfort = -10
        low_rel.trust = -10
        low_rel.respect = -10
        cat_from2.relationships.update({cat_to2.ID: low_rel})

        cat_from3 = Cat()
        cat_to3 = Cat()
        high_rel = Relationship(cat_from3, cat_to3)
        high_rel.romance = -90
        high_rel.like = -90
        high_rel.comfort = -90
        high_rel.trust = -90
        high_rel.respect = -90
        cat_from3.relationships.update({cat_to3.ID: high_rel})

        for level_list in rel_type_tiers.values():
            # no negs for romance
            if level_list == rel_type_tiers[RelType.ROMANCE]:
                continue
            for l in level_list:
                # first index of the list should be the highest negative
                if l == level_list[0]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from3, cat_to3],
                            [f"{l}_only"],
                        ),
                        f"{l}",
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{l}_only"],
                        ),
                        f"{l}",
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from2, cat_to2],
                            [f"{l}_only"],
                        ),
                        f"{l}",
                    )
                # next is middle negative
                elif l == level_list[1]:
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from3, cat_to3],
                            [f"{l}_only"],
                        ),
                        f"{l}",
                    )
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{l}_only"],
                        ),
                        f"{l}",
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from2, cat_to2],
                            [f"{l}_only"],
                        ),
                        f"{l}",
                    )
                # next is the lowest neg
                elif l == level_list[2]:
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from3, cat_to3],
                            [f"{l}_only"],
                        )
                    )
                    self.assertFalse(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{l}_only"],
                        )
                    )
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from2, cat_to2],
                            [f"{l}_only"],
                        )
                    )

    def test_rel_values_ranged_constraint(self):
        # given
        # pos side
        cat_from1 = Cat()
        cat_to1 = Cat()
        high_rel = Relationship(cat_from1, cat_to1)
        high_rel.romance = 90
        high_rel.like = 90
        high_rel.comfort = 90
        high_rel.trust = 90
        high_rel.respect = 90

        # neg side
        cat_from1 = Cat()
        cat_to1 = Cat()
        high_rel = Relationship(cat_from1, cat_to1)
        high_rel.romance = -90
        high_rel.like = -90
        high_rel.comfort = -90
        high_rel.trust = -90
        high_rel.respect = -90

        # then
        # pos test
        for level_list in rel_type_tiers.values():
            for level in level_list:
                # last index of the list should be the highest positive
                if level == level_list[-1]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{level}"],
                        )
                    )
                # next is middle pos
                elif level == level_list[-2]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{level}"],
                        )
                    )
                # next is the lowest pos
                elif level == level_list[-3]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{level}"],
                        )
                    )

        # neg test
        for level_list in rel_type_tiers.values():
            for level in level_list:
                # first index of the list should be the highest positive
                if level == level_list[0]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{level}"],
                        )
                    )
                # next is middle pos
                elif level == level_list[1]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{level}"],
                        )
                    )
                # next is the lowest pos
                elif level == level_list[2]:
                    self.assertTrue(
                        filter_relationship_type(
                            [cat_from1, cat_to1],
                            [f"{level}"],
                        )
                    )


class SingleInteractionCatConstraints(unittest.TestCase):
    def test_status(self):
        # given
        warrior = Cat(status_dict=StatusDict(rank=CatRank.WARRIOR))
        medicine = Cat(status_dict=StatusDict(rank=CatRank.MEDICINE_CAT))

        # when
        warrior_to_all = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(status=[CatRank.WARRIOR]),
                "r_c": InvolvedCatDict(status=[CatRank.MEDICINE_CAT, CatRank.WARRIOR]),
            },
        )

        warrior_to_warrior = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(status=[CatRank.WARRIOR]),
                "r_c": InvolvedCatDict(status=[CatRank.WARRIOR]),
            },
        )

        medicine_to_warrior = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(status=[CatRank.MEDICINE_CAT]),
                "r_c": InvolvedCatDict(status=[CatRank.WARRIOR]),
            },
        )

        # then
        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_all, medicine_to_warrior],
            main_cat=warrior,
            other_cat=warrior,
        )
        self.assertEqual(chosen_event, warrior_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_warrior, medicine_to_warrior],
            main_cat=warrior,
            other_cat=warrior,
        )
        self.assertEqual(chosen_event, warrior_to_warrior)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_warrior, medicine_to_warrior],
            main_cat=warrior,
            other_cat=warrior,
        )
        self.assertNotEqual(chosen_event, medicine_to_warrior)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_all, medicine_to_warrior],
            main_cat=warrior,
            other_cat=medicine,
        )
        self.assertEqual(chosen_event, warrior_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_warrior, warrior_to_all],
            main_cat=warrior,
            other_cat=medicine,
        )
        self.assertNotEqual(chosen_event, warrior_to_warrior)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_all, medicine_to_warrior],
            main_cat=warrior,
            other_cat=medicine,
        )
        self.assertNotEqual(chosen_event, medicine_to_warrior)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_all, medicine_to_warrior],
            main_cat=medicine,
            other_cat=warrior,
        )
        self.assertNotEqual(chosen_event, warrior_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_warrior, medicine_to_warrior],
            main_cat=medicine,
            other_cat=warrior,
        )
        self.assertNotEqual(chosen_event, warrior_to_warrior)

        chosen_event = generate_pair_event._get_event(
            events=[warrior_to_warrior, medicine_to_warrior],
            main_cat=medicine,
            other_cat=warrior,
        )
        self.assertEqual(chosen_event, medicine_to_warrior)

    def test_trait(self):
        # given
        calm = Cat()
        calm.personality.trait = "calm"
        troublesome = Cat()
        troublesome.personality.trait = "troublesome"

        # when
        calm_to_all = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(stat=StatDict(trait=["calm"])),
            },
        )

        all_to_calm = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(stat=StatDict(trait=["calm", "troublesome"])),
                "r_c": InvolvedCatDict(stat=StatDict(trait=["calm"])),
            },
        )

        rebels = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(stat=StatDict(trait=["rebellious"])),
                "r_c": InvolvedCatDict(stat=StatDict(trait=["rebellious"])),
            },
        )

        # then
        chosen_event = generate_pair_event._get_event(
            events=[calm_to_all, rebels],
            main_cat=calm,
            other_cat=troublesome,
        )
        self.assertEqual(chosen_event, calm_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[calm_to_all, all_to_calm],
            main_cat=calm,
            other_cat=troublesome,
        )
        self.assertNotEqual(chosen_event, all_to_calm)

        chosen_event = generate_pair_event._get_event(
            events=[calm_to_all, all_to_calm],
            main_cat=troublesome,
            other_cat=calm,
        )
        self.assertNotEqual(chosen_event, calm_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[all_to_calm, rebels],
            main_cat=troublesome,
            other_cat=calm,
        )
        self.assertEqual(chosen_event, all_to_calm)

        chosen_event = generate_pair_event._get_event(
            events=[calm_to_all, rebels],
            main_cat=calm,
            other_cat=calm,
        )
        self.assertEqual(chosen_event, calm_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[calm_to_all, rebels],
            main_cat=calm,
            other_cat=calm,
        )
        self.assertEqual(chosen_event, calm_to_all)

    def test_skill(self):
        # given
        hunter = Cat(disable_random=True)
        hunter.skills.primary = Skill(SkillPath.HUNTER, points=9)
        hunter.skills.secondary = Skill(SkillPath.CLIMBER, points=9)
        fighter = Cat(disable_random=True)
        fighter.skills.primary = Skill(SkillPath.FIGHTER, points=9)
        fighter.skills.secondary = Skill(SkillPath.CLIMBER, points=9)

        # when
        hunter_to_all = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(stat=StatDict(skill=["HUNTER,1"])),
            },
        )

        all_to_hunter = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(stat=StatDict(skill=["FIGHTER,1", "HUNTER,1"])),
                "r_c": InvolvedCatDict(stat=StatDict(skill=["HUNTER,1"])),
            },
        )

        storytellers = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(stat=StatDict(skill=["STORY,1"])),
                "r_c": InvolvedCatDict(stat=StatDict(skill=["STORY,1"])),
            },
        )

        # then
        chosen_event = generate_pair_event._get_event(
            events=[hunter_to_all, all_to_hunter],
            main_cat=hunter,
            other_cat=fighter,
        )
        self.assertEqual(chosen_event, hunter_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[all_to_hunter, storytellers],
            main_cat=fighter,
            other_cat=hunter,
        )
        self.assertEqual(chosen_event, all_to_hunter)

        chosen_event = generate_pair_event._get_event(
            events=[hunter_to_all, storytellers],
            main_cat=hunter,
            other_cat=hunter,
        )
        self.assertEqual(chosen_event, hunter_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[all_to_hunter, storytellers],
            main_cat=hunter,
            other_cat=hunter,
        )
        self.assertEqual(chosen_event, all_to_hunter)

    def test_background(self):
        # given
        clan = Cat()
        clan.backstory = "clanborn"
        half = Cat()
        half.backstory = "halfclan1"

        # when
        clan_to_all = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(backstory=["clanborn"]),
            },
        )

        all_to_clan = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(backstory=["clanborn", "halfclan1"]),
                "r_c": InvolvedCatDict(backstory=["clanborn"]),
            },
        )
        all_half2 = TextPoolEvent(
            id="test",
            strings=["test"],
            involved_cats={
                "m_c": InvolvedCatDict(backstory=["halfclan2"]),
                "r_c": InvolvedCatDict(backstory=["halfclan2"]),
            },
        )
        # then
        chosen_event = generate_pair_event._get_event(
            events=[clan_to_all, all_to_clan],
            main_cat=clan,
            other_cat=half,
        )
        self.assertEqual(chosen_event, clan_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[clan_to_all, all_to_clan],
            main_cat=half,
            other_cat=clan,
        )
        self.assertEqual(chosen_event, all_to_clan)

        chosen_event = generate_pair_event._get_event(
            events=[clan_to_all, all_half2],
            main_cat=clan,
            other_cat=clan,
        )
        self.assertEqual(chosen_event, clan_to_all)

        chosen_event = generate_pair_event._get_event(
            events=[all_to_clan, all_half2],
            main_cat=clan,
            other_cat=clan,
        )
        self.assertEqual(chosen_event, all_to_clan)
