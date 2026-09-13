import abc
import random
from typing import Tuple, Literal

from abc import ABC, abstractmethod
from scripts.cat import save_load
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.enums import CatAge, CatRank, CatSocial
from scripts.cat.factories.base_factory import BaseCatFactory
from scripts.cat.factories.typed_dicts import (
    MentorshipDict,
    CatTogglesDict,
    InheritanceDict,
    AfterlifeAffinityDict,
)
from scripts.cat.names import Name
from scripts.cat.pelts import Pelt
from scripts.cat.personality import Personality
from scripts.cat.skills import CatSkills
from scripts.cat.status import Status
from scripts.game_structure import game, constants

BASE_RNG = random.Random


class NewCatFactory(BaseCatFactory, ABC):
    rng = BASE_RNG()

    @classmethod
    def create_cat(cls, **overrides):
        """
        Create a new cat with randomness. Override any elements of the creation with keyword arguments
        :param overrides: Any desired overrides to the random generation
        :return: Cat object
        """
        # remove all values that are empty
        overrides = {k: v for k, v in overrides.items() if v is not None}

        status_dict = overrides.get("status_dict", {})
        if "rank" in overrides:
            status_dict["rank"] = overrides.get("rank")

        # the worst combined dependency ever
        age, moons, status = cls._determine_age_moons_and_status(
            moons=overrides.get("moons"), status_dict=status_dict
        )

        gender_dict = cls._get_random_gender_and_genderalign(
            age, sex=overrides.get("gender"), genderalign=overrides.get("genderalign")
        )

        if pelt := overrides.get("pelt"):
            if not isinstance(pelt, Pelt):
                pelt = Pelt(pelt)
            else:
                pelt = pelt
        else:
            pelt = cls._get_random_pelt(
                gender_dict["sex"],
                (overrides.get("parent1"), overrides.get("parent2")),
                age,
                no_disabling_scars=overrides.get("no_disabling_scars", False),
            )

        skills = overrides.get(
            "skill_dict", cls._get_random_skills_dict(status.rank, age)
        )
        if not isinstance(skills, CatSkills):
            skills = CatSkills(skill_dict=skills)

        mate = overrides.get("mate", [])
        if isinstance(mate, str):
            mate = [mate]

        cat_params = {
            "ID": cls.get_free_id(),
            "gender_dict": gender_dict,
            "pelt": pelt,
            "moons": moons,
            "status": status,
            "backstory": overrides.get(
                "backstory",
                cls._get_random_backstory_from_status(status, age),
            ),
            "skills": skills,
            "personality": cls._get_random_personality(age),
            "mentorship": MentorshipDict(
                mentor=None,
                former_mentor=[],
                patrol_with_mentor=0,
                apprentice=[],
                former_apprentices=[],
            ),
            "inheritance": InheritanceDict(
                parent1=overrides.get("parent1"),
                parent2=overrides.get("parent2"),
                adoptive_parents=overrides.get("adoptive_parents", []),
                faded_offspring=[],
                mate=mate,
                previous_mates=[],
            ),
            "affinity": AfterlifeAffinityDict(starclan=0, dark_forest=0),
            "toggles": CatTogglesDict(
                no_kits=False,
                no_mates=False,
                no_retire=False,
                prevent_fading=False,
                favourite=False,
            ),
            "experience": overrides.get(
                "experience", cls._get_random_experience(age, moons)
            ),
            "birth_cooldown": overrides.get("birth_cooldown", 0),
            "faded": False,
            "specsuffix_hidden": False,
        }

        cat = Cat(**cat_params)

        cat.name = Name(
            prefix=overrides.get("prefix"),
            suffix=overrides.get("suffix"),
            specsuffix_hidden=overrides.get("specsuffix_hidden", False),
            load_existing_name=True,
            cat=cat,
        )

        Cat.all_cats[cat.ID] = cat

        return cat

    @classmethod
    @abstractmethod
    def _get_random_age(cls) -> CatAge:
        return cls.rng.choice([*CatAge])

    @classmethod
    @abstractmethod
    def _get_random_age_from_rank(cls, rank) -> CatAge:
        """
        :param rank: Provided cat's rank
        :return: Random CatAge appropriate for the cat's rank
        """
        if not isinstance(rank, CatRank):
            rank = CatRank(rank)

        if rank == CatRank.NEWBORN:
            return CatAge.NEWBORN
        if rank == CatRank.KITTEN:
            return CatAge.KITTEN
        if rank == CatRank.ELDER:
            return CatAge.SENIOR
        if rank.is_any_apprentice_rank():
            return CatAge.ADOLESCENT

        return cls.rng.choice(
            [
                CatAge.YOUNG_ADULT,
                CatAge.ADULT,
                CatAge.ADULT,
                CatAge.SENIOR_ADULT,
            ]
        )

    @classmethod
    @abstractmethod
    def _get_random_status_from_age(cls, age) -> Status:
        status = Status()
        status.generate_new_status(age)

        return status

    @staticmethod
    @abstractmethod
    def _get_random_backstory_from_status(status: Status, age: CatAge):
        if status.social == CatSocial.CLANCAT:
            return "clanborn"

        social_category = str(status.rank) + "_backstories"

        if age.is_baby():
            social_category = f"baby_{social_category}"
        possible_backstories = BACKSTORIES["backstory_categories"][social_category]

        return random.choice(possible_backstories)

    @classmethod
    @abstractmethod
    def _get_random_moons(cls, age: CatAge) -> int:
        """
        Generate random moons appropriate for the given age
        :param age: CatAge
        :return: Appropriate moons
        """
        return cls.rng.randint(Cat.age_moons[age][0], Cat.age_moons[age][1])

    @classmethod
    def _determine_age_moons_and_status(
        cls, moons, status_dict
    ) -> Tuple[CatAge, int, Status]:
        """
        Figure out the age, moons and status of a cat depending on what's provided

        :param moons: Moons of the cat
        :param status_dict: Status dict describing the cat
        :return: CatAge, moons and Status that all agree with one another
        """
        age = None
        if status_dict and moons is not None:
            return CatAge.get_from_moons(moons), moons, Status(**status_dict)
        if not status_dict and moons is None:
            age = cls._get_random_age()
            status = cls._get_random_status_from_age(age)
            moons = cls._get_random_moons(age)
        elif not status_dict and moons is not None:
            age = CatAge.get_from_moons(moons)
            status = cls._get_random_status_from_age(age)
        elif status_dict and moons is None:
            if "rank" in status_dict:
                age = cls._get_random_age_from_rank(status_dict["rank"])
            elif (
                "group_history" in status_dict
                and "rank" in status_dict["group_history"][-1]
            ):
                age = cls._get_random_age_from_rank(
                    status_dict["group_history"][-1]["rank"]
                )
            else:
                age = cls._get_random_age()
            status = Status(**status_dict)
            moons = cls._get_random_moons(age)
        else:
            status = None

        if not isinstance(moons, int) or not status or not age:
            raise Exception("Something went wrong generating age, moons or status_dict")

        return age, moons, status

    @classmethod
    @abstractmethod
    def _get_random_gender_and_genderalign(cls, age, sex, genderalign) -> dict:
        gender = {
            "sex": sex if sex else cls.rng.choice(("male", "female")),
        }
        gender["genderalign"] = genderalign if genderalign else gender["sex"]

        if genderalign and "trans" in genderalign:
            gender["sex"] = "female" if genderalign == "trans male" else "male"
            return gender

        if age.is_baby():
            return gender

        trans_chance = cls.rng.randint(0, 50)
        nb_chance = cls.rng.randint(0, 75)

        if nb_chance == 1:
            gender["genderalign"] = "nonbinary"
        elif trans_chance == 1:
            gender["genderalign"] = (
                "trans male" if gender["sex"] == "female" else "trans female"
            )

        return gender

    @staticmethod
    def _get_random_pelt(gender, parents, age, no_disabling_scars: bool):
        pelt = Pelt.generate_new_pelt(
            gender,
            tuple(Cat.fetch_cat(i) for i in parents if i),
            age,
        )
        if no_disabling_scars:
            # code copied from removed create_cat function
            # used for generating new cats for a fresh Clan
            not_allowed_scars = (
                "NOPAW",
                "NOTAIL",
                "HALFTAIL",
                "NOEAR",
                "BOTHBLIND",
                "RIGHTBLIND",
                "LEFTBLIND",
                "BRIGHTHEART",
                "NOLEFTEAR",
                "NORIGHTEAR",
                "MANLEG",
            )

            pelt.scars = tuple(
                scar for scar in pelt.scars if scar not in not_allowed_scars
            )
        return pelt

    @classmethod
    @abstractmethod
    def _get_random_personality(cls, age: CatAge):
        return Personality(kit_trait=age.is_baby())

    @classmethod
    @abstractmethod
    def _get_random_experience(cls, age, moons: int) -> int:
        if age.is_baby():
            return 0

        if age == CatAge.ADOLESCENT:
            experience = 0
            ran = constants.CONFIG["graduation"]["base_app_timeskip_ex"]
            for i in range(Cat.age_moons[CatAge.ADOLESCENT][0], moons, -1):
                exp = cls.rng.choice(
                    list(range(ran[0][0], ran[0][1] + 1))
                    + list(range(ran[1][0], ran[1][1] + 1))
                )
                experience += exp + 3
            return experience
        elif age in (CatAge.YOUNG_ADULT, CatAge.ADULT):
            return cls.rng.randint(
                Cat.experience_levels_range["prepared"][0],
                Cat.experience_levels_range["proficient"][1],
            )
        elif age == CatAge.SENIOR_ADULT:
            return cls.rng.randint(
                Cat.experience_levels_range["proficient"][0],
                Cat.experience_levels_range["adept"][1],
            )
        elif age == CatAge.SENIOR:
            return cls.rng.randint(
                Cat.experience_levels_range["adept"][0],
                Cat.experience_levels_range["masterful"][1],
            )
        else:
            return 0

    @classmethod
    @abstractmethod
    def _get_random_skills_dict(cls, rank, age):
        skills = CatSkills.generate_new_catskills(rank, age, rng=cls.rng)
        return skills

    @staticmethod
    def get_free_id():
        potential_id = str(next(Cat.id_iter))

        if game.clan:
            faded_cats = save_load.get_faded_ids()
        else:
            faded_cats = []

        while potential_id in Cat.all_cats or potential_id in faded_cats:
            potential_id = str(next(Cat.id_iter))
        return potential_id
