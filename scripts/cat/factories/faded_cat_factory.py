from scripts.cat.cats import Cat
from scripts.cat.enums import CatGroup
from scripts.cat.factories.base_factory import BaseCatFactory
from scripts.cat.factories.typed_dicts import InheritanceDict, GenderDict
from scripts.cat.names import Name
from scripts.cat.status import Status

# be aware that there are many, many warnings in this file.
# this will continue to be the case until someone makes faded cats separate from regular cats.

# it's also not usable until the registry is implemented, so enjoy this little teaser


class FadedCatFactory(BaseCatFactory):
    @classmethod
    def create_cat(cls, **kwargs) -> Cat:
        if isinstance(kwargs["status"], str):
            status = Status(rank=kwargs["status"])
            # they are definitely dead
            status.send_to_afterlife(
                CatGroup.DARK_FOREST_ID
                if kwargs.get("df", False)
                else CatGroup.UNKNOWN_RESIDENCE
                if status.is_outsider and not status.is_former_clancat
                else CatGroup.STARCLAN_ID
            )
        else:
            status = Status(**kwargs["status"])

        cat = Cat(
            ID=kwargs["ID"],
            gender_dict=GenderDict(sex=None, genderalign=None),
            pelt=None,
            moons=kwargs["moons"],
            status=status,
            backstory="",
            skills=None,
            personality=None,
            mentorship={},
            inheritance=InheritanceDict(
                parent1=kwargs["parent1"],
                parent2=kwargs["parent2"],
                adoptive_parents=kwargs["adoptive_parents"],
                mate=[],
                previous_mates=[],
                faded_offspring=kwargs["faded_offspring"],
            ),
            affinity={},
            toggles={},
            experience=0,
            birth_cooldown=0,
            specsuffix_hidden=False,
            faded=True,
        )
        cat.name = Name(
            prefix=kwargs["name_prefix"], suffix=kwargs["name_suffix"], cat=cat
        )
        cat.dead_for = kwargs.get("dead_for", 0)

        cat.set_faded()
        return cat
