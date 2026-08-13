from scripts.cat.enums import CatAge
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.personality import Personality
from scripts.cat.skills import CatSkills, SkillPath
from scripts.cat.status import Status

# this is a patchwork fix for now
# should be replaced with a deterministic random.Random module in future


class TestCatFactory(NewCatFactory):
    @classmethod
    def _get_random_age(cls):
        return CatAge.NEWBORN

    @classmethod
    def _get_random_age_from_rank(cls, rank):
        return CatAge.NEWBORN

    @classmethod
    def _get_random_status_from_age(cls, age):
        status = Status()
        status.generate_new_status(age, disable_random=True)

        return status

    @staticmethod
    def _get_random_backstory_from_status(status: Status, age: CatAge):
        return "clanborn"

    @classmethod
    def _get_random_moons(cls, age: CatAge) -> int:
        """
        Generate random moons appropriate for the given age
        :param age: CatAge
        :return: Appropriate moons
        """
        return 0

    @classmethod
    def _get_random_gender_and_genderalign(cls, age, sex, genderalign) -> dict:
        return {
            "sex": sex if sex else "female",
            "genderalign": genderalign if genderalign else "female",
        }

    @classmethod
    def _get_random_personality(cls, age: CatAge):
        return Personality(
            lawful=8, social=8, aggress=8, stable=8, kit_trait=age.is_baby()
        )

    @classmethod
    def _get_random_experience(cls, age, moons: int) -> int:
        return 0

    @classmethod
    def _get_random_skills_dict(cls, rank, age):
        return CatSkills(
            primary_path=SkillPath.OMEN,
            primary_points=0,
            secondary_path=None,
            secondary_points=0,
            interest_only=False,
        )
