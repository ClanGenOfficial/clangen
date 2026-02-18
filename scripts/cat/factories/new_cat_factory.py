import random
from typing import Tuple, Dict, Any

from scripts.cat import save_load
from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge, CatRank
from scripts.cat.factories.base_factory import BaseCatFactory
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
        age, moons, status_dict = self._determine_moons_and_status(
            moons=overrides.get("moons"), status_dict=overrides.get("status_dict", {})
        )

        gender_dict = self._random_gender(age)

        init_params: Dict[str, Any] = {
            "personality": self._random_personality(age),
            "experience": self._random_experience(age, moons),
        }

        cat_params = {
            "ID": self.get_free_id(),
            "gender": overrides.get("gender", self._random_gender_and_genderalign(age)),
            "status_dict": status_dict,
            "moons": moons,
            "backstory": overrides.get("backstory", "clanborn"),
            "parent1": overrides.get("parent1"),
            "parent2": overrides.get("parent2"),
            "adoptive_parents": overrides.get("adoptive_parents", []),
            "mate": overrides.get("mate", []),
            "skill_dict": overrides.get(
                "skill_dict", self._random_skills_dict(status_dict["rank"], age)
            ),
            "pelt": overrides.get(
                "pelt",
                self._random_pelt(
                    gender_dict["sex"],
                    (overrides.get("parent1"), overrides.get("parent2")),
                    age,
                ),
            ),
        }

        if game.clan is not None:
            biome = (
                game.clan.biome
                if not game.clan.override_biome
                else game.clan.override_biome
            )
        else:
            biome = None

        init_params["name"] = Name(
            prefix=overrides.get("prefix"),
            suffix=overrides.get("suffix"),
            specsuffix_hidden=overrides.get("specsuffix_hidden"),
            biome=biome,
        )

        cat_params["init_params"] = init_params

        return Cat(**cat_params)

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

        return StatusDict(
            social=status.social, group_ID=status.group_ID, rank=status.rank
        )

    def _random_moons(self, age: CatAge) -> int:
        """
        Generate random moons appropriate for the given age
        :param age: CatAge
        :return: Appropriate moons
        """
        return self.rng.randint(Cat.age_moons[age][0], Cat.age_moons[age][1])

    def _determine_moons_and_status(
        self, moons, status_dict
    ) -> Tuple[CatAge, int, dict]:
        """

        :param moons:
        :param status_dict:
        :return: moons and status_dict
        """
        age = None
        if not status_dict and not moons:
            age = self._random_age()
            status_dict = self._random_status_from_age(age)
            moons = self._random_moons(age)
        elif not status_dict and moons:
            age = CatAge.get_from_moons(moons)
            status_dict = self._random_status_from_age(age)
        elif status_dict and "rank" in status_dict and not moons:
            age = self._random_age_from_rank(status_dict["rank"])
            moons = self._random_moons(age)

        if not isinstance(moons, int) or not status_dict or not age:
            raise Exception("Something went wrong generating age, moons or status_dict")

        return age, moons, status_dict

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
        return skills.get_skill_dict()

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
