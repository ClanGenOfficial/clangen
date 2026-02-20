from scripts.cat.enums import CatAge
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.personality import Personality
from scripts.cat.skills import CatSkills, SkillPath
from scripts.cat.status import Status

# this is a patchwork fix for now
# should be replaced with a deterministic random.Random module in future


class TestCatFactory(NewCatFactory):
    def _random_age(self):
        return CatAge.NEWBORN

    def _random_age_from_rank(self, rank):
        return CatAge.NEWBORN

    def _random_status_from_age(self, age):
        # it's a bit silly that we do this, then undo it,  and finally redo in Cat() but i don't want this refactor getting huge
        status = Status()
        status.generate_new_status(age, disable_random=True)

        return status

    def _random_moons(self, age: CatAge) -> int:
        """
        Generate random moons appropriate for the given age
        :param age: CatAge
        :return: Appropriate moons
        """
        return 0

    def _random_gender_and_genderalign(self, age) -> dict:
        return {"sex": "female", "genderalign": "female"}

    def _random_personality(self, age: CatAge):
        return Personality(
            lawful=8, social=8, aggress=8, stable=8, kit_trait=age.is_baby()
        )

    def _random_experience(self, age, moons: int) -> int:
        return 0

    def _random_skills_dict(self, rank, age):
        return CatSkills(
            primary_path=SkillPath.OMEN,
            primary_points=0,
            secondary_path=None,
            secondary_points=0,
            interest_only=False,
        )
