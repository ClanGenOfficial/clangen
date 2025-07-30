import random
from enum import Enum, Flag, auto
from typing import Union

import i18n

from scripts.cat.enums import CatRank, CatAge


class SkillPath(Enum):
    TEACHER = ("quick to help", "good teacher", "great teacher", "excellent teacher")
    HUNTER = ("moss ball hunter", "good hunter", "great hunter", "renowned hunter")
    FIGHTER = (
        "avid play-fighter",
        "good fighter",
        "formidable fighter",
        "unusually strong fighter",
    )
    RUNNER = (
        "never sits still",
        "fast runner",
        "incredible runner",
        "fast as the wind",
    )
    CLIMBER = (
        "constantly climbing",
        "good climber",
        "great climber",
        "impressive climber",
    )
    SWIMMER = (
        "splashes in puddles",
        "good swimmer",
        "talented swimmer",
        "fish-like swimmer",
    )
    SPEAKER = (
        "confident with words",
        "good speaker",
        "great speaker",
        "eloquent speaker",
    )
    MEDIATOR = (
        "quick to make peace",
        "good mediator",
        "great mediator",
        "skilled mediator",
    )
    CLEVER = ("quick witted", "clever", "very clever", "incredibly clever")
    INSIGHTFUL = (
        "careful listener",
        "helpful insight",
        "valuable insight",
        "trusted advisor",
    )
    SENSE = ("oddly observant", "natural intuition", "keen eye", "unnatural senses")
    KIT = (
        "active imagination",
        "good kitsitter",
        "great kitsitter",
        "beloved kitsitter",
    )
    STORY = (
        "lover of stories",
        "good storyteller",
        "great storyteller",
        "masterful storyteller",
    )
    LORE = (
        "interested in Clan history",
        "learner of lore",
        "lore keeper",
        "lore master",
    )
    CAMP = ("picky nest builder", "steady paws", "den builder", "camp keeper")
    HEALER = ("interested in herbs", "good healer", "great healer", "fantastic healer")
    STAR = (
        "curious about StarClan",
        "connection to StarClan",
        "deep StarClan bond",
        "unshakable StarClan link",
    )
    OMEN = ("interested in oddities", "omen seeker", "omen sense", "omen sight")
    DREAM = ("restless sleeper", "strange dreamer", "dream walker", "dream shaper")
    CLAIRVOYANT = (
        "oddly insightful",
        "somewhat clairvoyant",
        "fairly clairvoyant",
        "incredibly clairvoyant",
    )
    PROPHET = (
        "fascinated by prophecies",
        "prophecy seeker",
        "prophecy interpreter",
        "prophet",
    )
    GHOST = ("morbid curiosity", "ghost sense", "ghost sight", "ghost speaker")
    DARK = (
        "interested in the Dark Forest",
        "Dark Forest affinity",
        "deep Dark Forest bond",
        "unshakable Dark Forest link",
    )

    @staticmethod
    def get_random(exclude: list = ()):
        """Get a random path, with more uncommon paths being less common"""

        uncommon_paths = [
            i
            for i in (
                SkillPath.GHOST,
                SkillPath.PROPHET,
                SkillPath.CLAIRVOYANT,
                SkillPath.DREAM,
                SkillPath.OMEN,
                SkillPath.STAR,
                SkillPath.HEALER,
                SkillPath.DARK,
            )
            if i not in exclude
        ]

        if not int(random.random() * 15):
            return random.choice(uncommon_paths)
        else:
            common_paths = [
                i
                for i in list(SkillPath)
                if i not in exclude and i not in uncommon_paths
            ]
            return random.choice(common_paths)


class HiddenSkillEnum(Enum):
    ROGUE = "rogue's knowledge"
    LONER = "loner's knowledge"
    KITTYPET = "kittypet's knowledge"


class SkillTypeFlag(Flag):
    SUPERNATURAL = auto()
    STRONG = auto()
    AGILE = auto()
    SMART = auto()
    OBSERVANT = auto()
    SOCIAL = auto()


class Skill:
    """Skills handling functions mostly"""

    tier_ranges = ((0, 9), (10, 19), (20, 29))
    point_range = (0, 29)

    short_strings = {
        SkillPath.TEACHER: "teaching",
        SkillPath.HUNTER: "hunting",
        SkillPath.FIGHTER: "fighting",
        SkillPath.RUNNER: "running",
        SkillPath.CLIMBER: "climbing",
        SkillPath.SWIMMER: "swimming",
        SkillPath.SPEAKER: "speaking",
        SkillPath.MEDIATOR: "mediating",
        SkillPath.CLEVER: "clever",
        SkillPath.INSIGHTFUL: "advising",
        SkillPath.SENSE: "observing",
        SkillPath.KIT: "caretaking",
        SkillPath.STORY: "storytelling",
        SkillPath.LORE: "lorekeeping",
        SkillPath.CAMP: "campkeeping",
        SkillPath.HEALER: "healing",
        SkillPath.STAR: "StarClan",
        SkillPath.OMEN: "omen",
        SkillPath.DREAM: "dreaming",
        SkillPath.CLAIRVOYANT: "predicting",
        SkillPath.PROPHET: "prophesying",
        SkillPath.GHOST: "ghosts",
        SkillPath.DARK: "dark forest",
    }

    def __init__(self, path: SkillPath, points: int = 0, interest_only: bool = False):
        self.path = path
        self.interest_only = interest_only
        if points > self.point_range[1]:
            self._p = self.point_range[1]
        elif points < self.point_range[0]:
            self._p = self.point_range[0]
        else:
            self._p = points

    def __repr__(self) -> str:
        return f"<Skill: {self.path}, {self.points}, {self.tier}, {self.interest_only}>"

    def get_short_skill(self):
        return Skill.short_strings.get(self.path, "???")

    @staticmethod
    def generate_from_save_string(save_string: str):
        """Generates the skill from the save string in the cat data"""
        if not save_string:
            return None

        split_values = save_string.split(",")
        if split_values[2].lower() == "true":
            interest = True
        else:
            interest = False

        return Skill(SkillPath[split_values[0]], int(split_values[1]), interest)

    @staticmethod
    def get_random_skill(
        points: int = None, point_tier: int = None, exclude=(), interest_only=False
    ):
        """Generates a random skill. If wanted, you can specify a tier for the points
        value to be randomized within."""

        if isinstance(points, int):
            points = points
        elif isinstance(point_tier, int) and 1 <= point_tier <= 3:
            points = random.randint(
                Skill.tier_ranges[point_tier - 1][0],
                Skill.tier_ranges[point_tier - 1][1],
            )
        else:
            points = random.randint(Skill.point_range[0], Skill.point_range[1])

        if isinstance(exclude, SkillPath):
            exclude = [exclude]

        return Skill(SkillPath.get_random(exclude), points, interest_only)

    @property
    def points(self):
        return self._p

    @points.setter
    def points(self, val):
        if val > self.point_range[1]:
            self._p = self.point_range[1]
        elif val < self.point_range[0]:
            self._p = self.point_range[0]
        else:
            self._p = val

    @property
    def skill(self):
        """Skill property"""
        return self.path.value[self.tier]

    @skill.setter
    def skill(self):
        """Can't set the skill directly with this setter"""
        print("Can't set skill directly")

    @property
    def tier(self):
        """Returns the tier level of the skill"""
        if self.interest_only:
            return 0
        for _ran, i in zip(Skill.tier_ranges, range(1, 4)):
            if _ran[0] <= self.points <= _ran[1]:
                return i

        return 1

    @tier.setter
    def tier(self):
        print("Can't set tier directly")

    def set_points_to_tier(self, tier: int):
        """This is separate from the tier setter, since it will only allow you
        to set points to tier 1, 2, or 3, and never 0. Tier 0 is restricted to interest_only
        skills"""

        # Make sure it in the right range. If not, return.
        if not (1 <= tier <= 3):
            return

        # Adjust to 0-indexed ranges list
        self.points = Skill.tier_ranges[tier - 1][0]

    def get_save_string(self):
        """Gets the string that is saved in the cat data"""
        return f"{self.path.name},{self.points},{self.interest_only}"


class CatSkills:
    """
    Holds the cats skills, and handled changes in the skills.
    """

    # Mentor Inflence groups.
    # pylint: disable=unsupported-binary-operation
    influence_flags = {
        SkillPath.TEACHER: SkillTypeFlag.STRONG
        | SkillTypeFlag.AGILE
        | SkillTypeFlag.SMART
        | SkillTypeFlag.OBSERVANT
        | SkillTypeFlag.SOCIAL,
        SkillPath.HUNTER: SkillTypeFlag.STRONG
        | SkillTypeFlag.AGILE
        | SkillTypeFlag.OBSERVANT,
        SkillPath.FIGHTER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE,
        SkillPath.RUNNER: SkillTypeFlag.AGILE,
        SkillPath.CLIMBER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE,
        SkillPath.SWIMMER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE,
        SkillPath.SPEAKER: SkillTypeFlag.SOCIAL | SkillTypeFlag.SMART,
        SkillPath.MEDIATOR: SkillTypeFlag.SMART | SkillTypeFlag.SOCIAL,
        SkillPath.CLEVER: SkillTypeFlag.SMART,
        SkillPath.INSIGHTFUL: SkillTypeFlag.SMART | SkillTypeFlag.OBSERVANT,
        SkillPath.SENSE: SkillTypeFlag.OBSERVANT,
        SkillPath.KIT: SkillTypeFlag.SOCIAL,
        SkillPath.STORY: SkillTypeFlag.SMART | SkillTypeFlag.SOCIAL,
        SkillPath.LORE: SkillTypeFlag.SMART | SkillTypeFlag.SOCIAL,
        SkillPath.CAMP: SkillTypeFlag.OBSERVANT | SkillTypeFlag.SOCIAL,
        SkillPath.HEALER: SkillTypeFlag.SMART
        | SkillTypeFlag.OBSERVANT
        | SkillTypeFlag.SOCIAL,
        SkillPath.STAR: SkillTypeFlag.SUPERNATURAL,
        SkillPath.OMEN: SkillTypeFlag.SUPERNATURAL | SkillTypeFlag.OBSERVANT,
        SkillPath.DREAM: SkillTypeFlag.SUPERNATURAL,
        SkillPath.CLAIRVOYANT: SkillTypeFlag.SUPERNATURAL | SkillTypeFlag.OBSERVANT,
        SkillPath.PROPHET: SkillTypeFlag.SUPERNATURAL,
        SkillPath.GHOST: SkillTypeFlag.SUPERNATURAL,
        SkillPath.DARK: SkillTypeFlag.SUPERNATURAL,
    }

    # pylint: enable=unsupported-binary-operation

    def __init__(
        self,
        skill_dict=None,
        primary_path: SkillPath = None,
        primary_points: int = 0,
        secondary_path: SkillPath = None,
        secondary_points: int = 0,
        hidden_skill: HiddenSkillEnum = None,
        interest_only=False,
    ):
        if skill_dict:
            self.primary = Skill.generate_from_save_string(skill_dict["primary"])
            self.secondary = Skill.generate_from_save_string(skill_dict["secondary"])
            self.hidden = (
                HiddenSkillEnum[skill_dict["hidden"]] if skill_dict["hidden"] else None
            )
        else:
            if primary_path:
                self.primary = Skill(primary_path, primary_points, interest_only)
            else:
                self.primary = None
            if secondary_path:
                self.secondary = Skill(secondary_path, secondary_points, interest_only)
            else:
                self.secondary = None

            self.hidden = hidden_skill

    def __repr__(self) -> str:
        return f"<CatSkills: Primary: |{self.primary}|, Secondary: |{self.secondary}|, Hidden: |{self.hidden}|>"

    @staticmethod
    def generate_new_catskills(
        rank: CatRank, age: CatAge, hidden_skill: HiddenSkillEnum = None
    ):
        """Generates a new skill"""
        new_skill = CatSkills()

        new_skill.hidden = hidden_skill

        if rank == CatRank.NEWBORN or age == CatAge.NEWBORN:
            pass
        elif rank == CatRank.KITTEN or age == CatAge.KITTEN:
            new_skill.primary = Skill.get_random_skill(points=0, interest_only=True)
        elif rank.is_any_apprentice_rank() or age == CatAge.ADOLESCENT:
            new_skill.primary = Skill.get_random_skill(point_tier=1, interest_only=True)
            if random.randint(1, 3) == 1:
                new_skill.secondary = Skill.get_random_skill(
                    point_tier=1, interest_only=True, exclude=new_skill.primary.path
                )
        else:
            primary_tier = 1
            secondary_tier = 1
            if age == CatAge.YOUNG_ADULT:
                primary_tier += random.randint(0, 1)
                secondary_tier += random.randint(0, 1)
            elif age == CatAge.ADULT:
                primary_tier += random.randint(0, 2)
                secondary_tier += random.randint(0, 1)
            elif age == CatAge.SENIOR_ADULT:
                primary_tier += random.randint(1, 2)
                secondary_tier += random.randint(0, 1)
            elif age == CatAge.SENIOR:
                primary_tier -= random.randint(0, 1)

            new_skill.primary = Skill.get_random_skill(point_tier=primary_tier)
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(
                    point_tier=secondary_tier, exclude=new_skill.primary.path
                )

        return new_skill

    def get_skill_dict(self):
        return {
            "primary": self.primary.get_save_string() if self.primary else None,
            "secondary": self.secondary.get_save_string() if self.secondary else None,
            "hidden": self.hidden.name if self.hidden else None,
        }

    def skill_string(self, short=False):
        output = []

        if short:
            if self.primary:
                output.append(i18n.t(f"cat.skills.{self.primary.get_short_skill()}"))
            if self.secondary:
                output.append(i18n.t(f"cat.skills.{self.secondary.get_short_skill()}"))
        else:
            if self.primary:
                output.append(i18n.t(f"cat.skills.{self.primary.skill}"))
            if self.secondary:
                output.append(i18n.t(f"cat.skills.{self.secondary.skill}"))

        if not output:
            return "???"

        out = " & ".join(output)
        return out

    def mentor_influence(self, mentor):
        """Handles mentor influence on the cat's skill
        :param mentor: the mentor's cat object
        """

        if not mentor:
            return

        # Determine if any skills can be effected
        mentor_tags = (
            CatSkills.influence_flags[mentor.skills.primary.path]
            if mentor.skills.primary
            else None
        )

        can_primary = (
            bool(CatSkills.influence_flags[self.primary.path] & mentor_tags)
            if self.primary and mentor_tags
            else False
        )
        can_secondary = (
            bool(CatSkills.influence_flags[self.secondary.path] & mentor_tags)
            if self.secondary and mentor_tags
            else False
        )

        # If nothing can be effected, just return as well.
        if not (can_primary or can_secondary):
            return

        amount_effect = random.randint(1, 4)

        if can_primary and can_secondary:
            if random.randint(1, 2) == 1:
                self.primary.points += amount_effect
                path = self.primary.path
            else:
                self.secondary.points += amount_effect
                path = self.secondary.path
        elif can_primary:
            self.primary.points += amount_effect
            path = self.primary.path
        else:
            self.secondary.points += amount_effect
            path = self.secondary.path

        return mentor.ID, path, amount_effect

    def progress_skill(self, the_cat):
        """
        this function should be run every moon for every cat to progress their skills accordingly
        :param the_cat: the cat object for affected cat
        """
        if the_cat.status.rank == CatRank.NEWBORN or the_cat.moons <= 0:
            return

        # Give a primary is there isn't one already, and the cat is older than one moon.
        if not self.primary:
            parents = [
                the_cat.fetch_cat(i)
                for i in [the_cat.parent1, the_cat.parent2] + the_cat.adoptive_parents
                if type(the_cat) == type(the_cat.fetch_cat(i))
            ]
            parental_paths = [
                i.skills.primary.path for i in parents if i.skills.primary
            ] + [i.skills.secondary.path for i in parents if i.skills.secondary]

            # If there are parental paths, flip a coin to determine if they will get a parents path
            if parental_paths and random.randint(0, 1):
                self.primary = Skill(
                    random.choice(parental_paths),
                    points=0,
                    interest_only=the_cat.status.rank.is_any_apprentice_rank()
                    or the_cat.status.rank == CatRank.KITTEN,
                )
            else:
                self.primary = Skill.get_random_skill(
                    points=0,
                    interest_only=the_cat.status.rank.is_any_apprentice_rank()
                    or the_cat.status.rank == CatRank.KITTEN,
                )

        if the_cat.status.is_clancat:
            if the_cat.status.rank == CatRank.KITTEN:
                # Check to see if the cat gains a secondary
                if not self.secondary and not int(random.random() * 22):
                    # if there's no secondary skill, try to give one!
                    self.secondary = Skill.get_random_skill(
                        points=0, interest_only=True, exclude=self.primary.path
                    )

                # if the the_cat has skills, check if they get any points this moon
                if not int(random.random() * 4):
                    amount_effect = random.randint(1, 4)
                    if self.primary and self.secondary:
                        if random.randint(1, 2) == 1:
                            self.primary.points += amount_effect
                        else:
                            self.secondary.points += amount_effect
                    elif self.primary:
                        self.primary.points += amount_effect

            elif the_cat.status.rank.is_any_apprentice_rank():
                # Check to see if the cat gains a secondary
                if not self.secondary and not int(random.random() * 22):
                    # if there's no secondary skill, try to give one!
                    self.secondary = Skill.get_random_skill(
                        points=0, interest_only=True, exclude=self.primary.path
                    )

                # Check if they get any points this moon
                if not int(random.random() * 4):
                    amount_effect = random.randint(2, 5)
                    if self.primary and self.secondary:
                        if random.randint(1, 2) == 1:
                            self.primary.points += amount_effect
                        else:
                            self.secondary.points += amount_effect
                    elif self.primary:
                        self.primary.points += amount_effect

            elif the_cat.moons > 120:
                # for old cats, we want to check if the skills start to degrade at all, age is the great equalizer

                self.primary.interest_only = False
                if self.secondary:
                    self.secondary.interest_only = False

                chance = max(1, 160 - the_cat.moons)
                if not int(
                    random.random() * chance
                ):  # chance increases as the_cat ages
                    self.primary.points -= 1
                    if self.secondary:
                        self.secondary.points -= 1
            else:
                # If they are still in "interest" stage, there is a change to swap primary and secondary
                # If they are still in "interest" but reached this part, they just graduated.
                if self.primary.interest_only and self.secondary:
                    flip = random.choices(
                        [False, True],
                        [self.primary.points + 1, self.secondary.points + 1],
                    )[0]
                    if flip:
                        _temp = self.primary
                        self.primary = self.secondary
                        self.secondary = _temp

                self.primary.interest_only = False
                if self.secondary:
                    self.secondary.interest_only = False

                # If a cat doesn't can a secondary, have a small change for them to get one.
                # but, only a first-tier skill.
                if not self.secondary and not int(random.random() * 300):
                    self.secondary = Skill.get_random_skill(
                        exclude=self.primary.path, point_tier=1
                    )

                # There is a change for primary to continue to improve throughout life
                # That chance decreases as the cat gets older.
                # This is to simulate them reaching their "peak"
                if not int(random.random() * int(the_cat.moons / 4)):
                    self.primary.points += 1
        else:
            # For outside cats, just check interest and flip it if needed.
            # Going on age, rather than status here.
            if the_cat.age not in (CatAge.KITTEN, CatAge.ADOLESCENT):
                self.primary.interest_only = False
                if self.secondary:
                    self.secondary.interest_only = False

    def meets_skill_requirement(
        self, path: Union[str, SkillPath, HiddenSkillEnum], min_tier: int = 0
    ) -> bool:
        """Check if a cat meets a given skill requirement.

        :param Union[str, SkillPath, HiddenSkillEnum] path: todo: someone describe this amalgam
        :param int min_tier: the lowest tier of skill that will pass this test
        :return bool: True if cat meets skill requirement
        """

        if isinstance(path, str):
            # Try to conter to Skillpath or HiddenSkillEnum
            try:
                path = SkillPath[path]
            except KeyError:
                try:
                    path = HiddenSkillEnum[path]
                except KeyError:
                    print(f"{path} is not a real skill path")
                    return False

        if isinstance(path, HiddenSkillEnum):
            if path == self.hidden:
                return True
        elif isinstance(path, SkillPath):
            if self.primary:
                if path == self.primary.path and self.primary.tier >= min_tier:
                    return True

            if self.secondary:
                if path == self.secondary.path and self.secondary.tier >= min_tier:
                    return True

        return False

    def check_skill_requirement_list(self, skill_list: list) -> int:
        """Takes a whole list of skill requirements in the form
        [ "SKILL_PATH,MIN_TIER" ... ] and determines how many skill
        requirements are met. The list format is used in all patrol and event skill
        restrictions. Returns an integer value of how many skills requirements are met.
        """
        skills_meet = 0
        min_tier = 0
        for _skill in skill_list:
            spl = _skill.split(",")

            if len(spl) != 2:
                print("Incorrectly formatted skill restriction", _skill)
                continue
            try:
                min_tier = int(spl[1])
            except ValueError:
                print("Min Skill Tier cannot be converted to int", _skill)
                continue

            if self.meets_skill_requirement(spl[0], min_tier):
                skills_meet += 1

        return skills_meet

    @staticmethod
    def get_skills_from_old(old_skill, rank: CatRank, age: CatAge):
        """Generates a CatSkill object"""
        new_skill = CatSkills()
        conversion = {
            "strong connection to StarClan": (SkillPath.STAR, 2),
            "good healer": (SkillPath.HEALER, 1),
            "great healer": (SkillPath.HEALER, 2),
            "fantastic healer": (SkillPath.HEALER, 3),
            "good teacher": (SkillPath.TEACHER, 1),
            "great teacher": (SkillPath.TEACHER, 2),
            "fantastic teacher": (SkillPath.TEACHER, 3),
            "good mediator": (SkillPath.MEDIATOR, 1),
            "great mediator": (SkillPath.MEDIATOR, 2),
            "excellent mediator": (SkillPath.MEDIATOR, 3),
            "smart": (SkillPath.CLEVER, 1),
            "very smart": (SkillPath.CLEVER, 2),
            "extremely smart": (SkillPath.CLEVER, 3),
            "good hunter": (SkillPath.HUNTER, 1),
            "great hunter": (SkillPath.HUNTER, 2),
            "fantastic hunter": (SkillPath.HUNTER, 3),
            "good fighter": (SkillPath.FIGHTER, 1),
            "great fighter": (SkillPath.FIGHTER, 2),
            "excellent fighter": (SkillPath.FIGHTER, 3),
            "good speaker": (SkillPath.SPEAKER, 1),
            "great speaker": (SkillPath.SPEAKER, 2),
            "excellent speaker": (SkillPath.SPEAKER, 3),
            "good storyteller": (SkillPath.STORY, 1),
            "great storyteller": (SkillPath.STORY, 2),
            "fantastic storyteller": (SkillPath.STORY, 3),
            "smart tactician": (SkillPath.INSIGHTFUL, 1),
            "valuable tactician": (SkillPath.INSIGHTFUL, 2),
            "valuable insight": (SkillPath.INSIGHTFUL, 3),
            "good kitsitter": (SkillPath.KIT, 1),
            "great kitsitter": (SkillPath.KIT, 2),
            "beloved kitsitter": (SkillPath.KIT, 3),
            "camp keeper": (SkillPath.CAMP, 3),
            "den builder": (SkillPath.CAMP, 2),
            "omen sight": (SkillPath.OMEN, 3),
            "dream walker": (SkillPath.DREAM, 2),
            "clairvoyant": (SkillPath.CLAIRVOYANT, 2),
            "prophet": (SkillPath.PROPHET, 3),
            "lore keeper": (SkillPath.LORE, 2),
            "keen eye": (SkillPath.SENSE, 2),
        }

        old_skill = old_skill.strip()
        if old_skill in conversion:
            new_skill.primary = Skill(conversion[old_skill][0])
            new_skill.primary.set_points_to_tier(conversion[old_skill][1])
        else:
            new_skill = CatSkills.generate_new_catskills(rank, age)

        return new_skill
