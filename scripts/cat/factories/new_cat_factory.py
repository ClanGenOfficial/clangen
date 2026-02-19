import random
from typing import Tuple, Dict, Any

from scripts.cat import save_load
from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge, CatRank
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
from scripts.cat.status import Status, StatusDict
from scripts.game_structure import game, constants

BASE_RNG = random.Random


class NewCatFactory(BaseCatFactory):
    def __init__(self, rng):
        self.rng = rng if rng else BASE_RNG()

    def create_cat(self, **overrides):
        # remove all values that are empty
        overrides = {k: v for k, v in overrides.items() if v}

        # the worst combined dependency ever
        age, moons, status = self._determine_age_moons_and_status(
            moons=overrides.get("moons"), status_dict=overrides.get("status_dict", {})
        )

        gender_dict = self._random_gender_and_genderalign(age)
        # if specified, override the randomizer
        gender_dict["sex"] = overrides.get("gender", gender_dict["sex"])
        gender_dict["genderalign"] = overrides.get(
            "genderalign", gender_dict["genderalign"]
        )

        if pelt := overrides.get("pelt"):
            pelt = Pelt(pelt)
        else:
            pelt = self._random_pelt(
                gender_dict["sex"],
                (overrides.get("parent1"), overrides.get("parent2")),
                age,
            )

        skills = overrides.get("skill_dict", self._random_skills_dict(status.rank, age))
        if not isinstance(skills, CatSkills):
            skills = CatSkills(skill_dict=skills)

        mate = overrides.get("mate", [])
        if isinstance(mate, str):
            mate = [mate]

        cat_params = {
            "ID": self.get_free_id(),
            "gender_dict": gender_dict,
            "pelt": pelt,
            "moons": moons,
            "status": status,
            "backstory": overrides.get("backstory", "clanborn"),
            "catskills": skills,
            "personality": self._random_personality(age),
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
                "experience", self._random_experience(age, moons)
            ),
            "birth_cooldown": overrides.get("birth_cooldown", 0),
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

    def _random_age(self):
        return self.rng.choice([*CatAge])

    def _random_age_from_rank(self, rank):
        """
        :param rank: Provided cat's rank
        :return: Age the cat should be
        """
        if not isinstance(rank, CatRank):
            rank = CatRank(rank)

        if rank == CatRank.NEWBORN or type(self.rng) != BASE_RNG:
            return CatAge.NEWBORN
        if rank == CatRank.KITTEN:
            return CatAge.KITTEN
        if rank == CatRank.ELDER:
            return CatAge.SENIOR
        if rank.is_any_apprentice_rank():
            return CatAge.ADOLESCENT

        return self.rng.choice(
            [
                CatAge.YOUNG_ADULT,
                CatAge.ADULT,
                CatAge.ADULT,
                CatAge.SENIOR_ADULT,
            ]
        )

    def _random_status_from_age(self, age):
        # it's a bit silly that we do this, then undo it,  and finally redo in Cat() but i don't want this refactor getting huge
        status = Status()
        status.generate_new_status(age, disable_random=type(self.rng) != BASE_RNG)

        return status

    def _random_moons(self, age: CatAge) -> int:
        """
        Generate random moons appropriate for the given age
        :param age: CatAge
        :return: Appropriate moons
        """
        return self.rng.randint(Cat.age_moons[age][0], Cat.age_moons[age][1])

    def _determine_age_moons_and_status(
        self, moons, status_dict
    ) -> Tuple[CatAge, int, Status]:
        """

        :param moons:
        :param status_dict:
        :return: moons and status_dict
        """
        age = None
        if status_dict and moons:
            return CatAge.get_from_moons(moons), moons, Status(**status_dict)
        if not status_dict and not moons:
            age = self._random_age()
            status = self._random_status_from_age(age)
            moons = self._random_moons(age)
        elif not status_dict and moons:
            age = CatAge.get_from_moons(moons)
            status = self._random_status_from_age(age)
        elif status_dict and not moons:
            if "rank" in status_dict:
                age = self._random_age_from_rank(status_dict["rank"])
            elif (
                "group_history" in status_dict
                and "rank" in status_dict["group_history"][-1]
            ):
                age = self._random_age_from_rank(
                    status_dict["group_history"][-1]["rank"]
                )
            else:
                age = self._random_age()
            status = Status(**status_dict)
            moons = self._random_moons(age)
        else:
            status = None

        if not isinstance(moons, int) or not status or not age:
            raise Exception("Something went wrong generating age, moons or status_dict")

        return age, moons, status

    def _random_gender_and_genderalign(self, age) -> dict:
        gender = {
            "sex": self.rng.choice(("male", "female")),
        }
        gender["genderalign"] = gender["sex"]

        if age.is_baby() or type(self.rng) != BASE_RNG:
            return gender

        trans_chance = self.rng.randint(0, 50)
        nb_chance = self.rng.randint(0, 75)

        if nb_chance == 1:
            gender["genderalign"] = "nonbinary"
        elif trans_chance == 1:
            gender["genderalign"] = (
                "trans male" if gender["sex"] == "female" else "trans female"
            )

        return gender

    @staticmethod
    def _random_pelt(gender, parents, age):
        return Pelt.generate_new_pelt(
            gender,
            tuple(Cat.fetch_cat(i) for i in parents if i),
            age,
        )

    def _random_personality(self, age: CatAge):
        if type(self.rng) != BASE_RNG:
            return Personality(
                lawful=8, social=8, aggress=8, stable=8, kit_trait=age.is_baby()
            )
        return Personality(kit_trait=age.is_baby())

    def _random_experience(self, age, moons: int) -> int:
        if age.is_baby() or type(self.rng) != BASE_RNG:
            return 0

        if age == CatAge.ADOLESCENT:
            experience = 0
            ran = constants.CONFIG["graduation"]["base_app_timeskip_ex"]
            for i in range(Cat.age_moons[CatAge.ADOLESCENT][0], moons, -1):
                exp = self.rng.choice(
                    list(range(ran[0][0], ran[0][1] + 1))
                    + list(range(ran[1][0], ran[1][1] + 1))
                )
                experience += exp + 3
            return experience
        elif age in (CatAge.YOUNG_ADULT, CatAge.ADULT):
            return self.rng.randint(
                Cat.experience_levels_range["prepared"][0],
                Cat.experience_levels_range["proficient"][1],
            )
        elif age == CatAge.SENIOR_ADULT:
            return self.rng.randint(
                Cat.experience_levels_range["competent"][0],
                Cat.experience_levels_range["expert"][1],
            )
        elif age == CatAge.SENIOR:
            return self.rng.randint(
                Cat.experience_levels_range["expert"][0],
                Cat.experience_levels_range["master"][1],
            )
        else:
            return 0

    def _random_skills_dict(self, rank, age):
        skills = CatSkills.generate_new_catskills(rank, age, rng=self.rng)
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
