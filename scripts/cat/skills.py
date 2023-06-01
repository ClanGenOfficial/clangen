import random
from enum import Enum, Flag, auto

class PathEnum(Enum):
    TEACHER = (
        "quick to help",
        "good teacher",
        "great teacher",
        "excellent teacher"
    )
    HUNTER =  (
        "moss-ball hunter",
        "good hunter",
        "great hunter",
        "renowned hunter"
    )
    FIGHTER = (
        "avid play-fighter",
        "good fighter",
        "formidable fighter",
        "unusually strong fighter"
    )
    RUNNER = (
        "never sits still",
        "fast runner",
        "incredible runner",
        "fast as the wind"
    )
    CLIMBER = (
        "constantly climbing",
        "good climber",
        "great climber",
        "impressive climber"
    )
    SWIMMER = (
        "splashes in puddles",
        "good swimmer",
        "talented swimmer",
        "fish-like swimmer"
    )
    SPEAKER = (
        "confident with words",
        "good speaker",
        "great speaker",
        "eloquent speaker"
    )
    MEDIATOR = (
        "quick to make peace",
        "good mediator",
        "great mediator",
        "skilled mediator"
    )
    CLEVER = (
        "quick witted",
        "clever",
        "very clever",
        "incredibly clever"
    )
    INSIGHTFUL = (
        "careful listener",
        "helpful insight",
        "valuable insight",
        "trusted advisor"
    )
    SENSE = (
        "oddly observant",
        "natural intuition",
        "keen eye",
        "unnatural senses"
    )
    KIT = (
        "active imagination",
        "good kitsitter",
        "great kitsitter",
        "beloved kitsitter"
    )
    STORY = (
        "lover of stories",
        "good storyteller",
        "great storyteller",
        "masterful storyteller"
    )
    LORE = (
        "interested in Clan history",
        "learner of lore",
        "lore keeper",
        "lore master"
    )
    CAMP = (
        "picky nest builder",
        "steady paws",
        "den builder",
        "camp keeper"
    )
    HEALER = (
        "interested in herbs",
        "good healer",
        "great healer",
        "fantastic healer"
    )
    STAR = (
        "curious about StarClan",
        "innate connection to StarClan",
        "strong connection to StarClan",
        "unbreakable connection to StarClan"
    )
    OMEN = (
        "interested in oddities",
        "omen seeker",
        "omen sense",
        "omen sight"
    )
    DREAM = (
        "restless sleeper",
        "strange dreamer",
        "dream walker",
        "dream shaper"
    )
    CLAIRVOYANT = (
        "oddly insightful",
        "somewhat clairvoyant",
        "fairly clairvoyant",
        "incredibly clairvoyant"
    )
    PROPHET = (
        "fascinated by prophecies",
        "prophecy seeker",
        "prophecy interpreter",
        "prophet"
    )
    GHOST = (
        "morbid curiosity",
        "ghost sense",
        "ghost sight",
        "ghost speaker"
    )
    
    @staticmethod
    def get_random(exclude:list=()):
        """Get a random path, with more uncommon paths being less common"""
        
        uncommon_paths = [i for i in [PathEnum.GHOST, PathEnum.PROPHET, 
                          PathEnum.CLAIRVOYANT, PathEnum.DREAM,
                          PathEnum.OMEN, PathEnum.STAR, PathEnum.HEALER]
                          if i not in exclude]
        
        
        if not (random.random() * 20):
            return random.hoice(uncommon_paths)
        else:
            common_paths = [i for i in list(PathEnum) if 
                           i not in exclude and i not in uncommon_paths]
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
    
class Skill():
    
    tier_ranges = ((0, 9), (10, 19), (20, 29))
    point_range = (0, 29)
    
    def __init__(self, path:PathEnum, points:int=0, interest_only:bool=False):
        
        self.path = path
        self.interest_only = interest_only
        if points > self.point_range[1]:
            self._p = self.point_range[1]
        elif points < self.point_range[0]:
            self._p = self.point_range[0]
        else:
            self._p = points
    
    @staticmethod
    def generate_from_save_string(save_string:str):
        if not save_string:
            return None
        
        split_values = save_string.split(",")
        if split_values[2].lower() == "true":
            interest = True
        else:
            interest = False
        
        return Skill(PathEnum[split_values[0]], int(split_values[1]), interest)
    
    @staticmethod
    def get_random_skill(points:int = 0, point_tier:int = None, exclude:list=(), interest_only=False):
        """Generates a random skill. If wanted, you can specify a teir for the points
        value to be randomized within. """
        
        if isinstance(points, int):
            points = points
        elif isinstance(point_tier, int) and 1 <= point_tier <= 3:
            points = random.randint(Skill.tier_ranges[point_tier-1][0], Skill.tier_ranges[point_tier-1][1])
        else:
            points = random.randint(Skill.point_range[0], Skill.point_range[1])
        
        return Skill(PathEnum.get_random(exclude=exclude), points, interest_only)
    
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
        if self.interest_only:
            return self.path.value[0]
        else:
            return self.path.value[self.tier]
        
    @skill.setter
    def skill(self):
        print("Can't set skill directly")
        return
    
    @property
    def tier(self):
        if self.interest_only:
            return 0
        
        for _ran, i in zip(Skill.tier_ranges, range(1, 4)):
                if _ran[0] <= self.points <= _ran[1]:
                    return i
                
        return 1
    
    @tier.setter
    def tier(self, val):
        print("Can't set tier directly")
        return
    
    def set_points_to_tier(self, teir:int):
        """This is seperate from the tier setter, since it will booonly allow you
        to set points to teir 1, 2, or 3, and never 0. Tier 0 is retricted to interest_only
        skills"""
        
        # Make sure it in the right range. If not, return. 
        if not (1 <= teir <= 3):
            return
        
        # Adjust to 0-indexed ranges list
        self.points = Skill.point_range[teir - 1][0]
        
    def get_save_string(self):
        return f"{self.path.name},{self.points},{self.interest_only}"

class CatSkills:
    """
    Holds the cats skills, and handled changes in the skills. 
    """
    
    #Mentor Inflence groups. 
    influence_flags = {
        PathEnum.TEACHER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE | SkillTypeFlag.SMART | SkillTypeFlag.OBSERVANT | SkillTypeFlag.SOCIAL, 
        PathEnum.HUNTER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE | SkillTypeFlag.OBSERVANT,
        PathEnum.FIGHTER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE,
        PathEnum.RUNNER: SkillTypeFlag.AGILE,
        PathEnum.CLIMBER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE,
        PathEnum.SWIMMER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE,
        PathEnum.SPEAKER: SkillTypeFlag.SOCIAL | SkillTypeFlag.SMART,
        PathEnum.MEDIATOR: SkillTypeFlag.SMART | SkillTypeFlag.SOCIAL,
        PathEnum.CLEVER: SkillTypeFlag.SMART,
        PathEnum.INSIGHTFUL: SkillTypeFlag.SMART | SkillTypeFlag.OBSERVANT,
        PathEnum.SENSE: SkillTypeFlag.OBSERVANT,
        PathEnum.KIT: SkillTypeFlag.SOCIAL,
        PathEnum.STORY: SkillTypeFlag.SMART | SkillTypeFlag.SOCIAL,
        PathEnum.LORE: SkillTypeFlag.SMART | SkillTypeFlag.SOCIAL,
        PathEnum.CAMP: SkillTypeFlag.OBSERVANT | SkillTypeFlag.SOCIAL,
        PathEnum.HEALER: SkillTypeFlag.SMART | SkillTypeFlag.OBSERVANT | SkillTypeFlag.SOCIAL,
        PathEnum.STAR: SkillTypeFlag.SUPERNATURAL,
        PathEnum.OMEN: SkillTypeFlag.SUPERNATURAL | SkillTypeFlag.OBSERVANT,
        PathEnum.DREAM: SkillTypeFlag.SUPERNATURAL,
        PathEnum.CLAIRVOYANT: SkillTypeFlag.SUPERNATURAL | SkillTypeFlag.OBSERVANT,
        PathEnum.PROPHET: SkillTypeFlag.SUPERNATURAL,
        PathEnum.GHOST: SkillTypeFlag.SUPERNATURAL
    }
    
    def __init__(self,
                 skill_dict=None,
                 primary_path:PathEnum = None,
                 primary_points:int = 0,
                 secondary_path: PathEnum = None,
                 secondary_points:int = 0,
                 hidden_skill:HiddenSkillEnum = None,
                 interest_only=False):
        

        if skill_dict:
            self.primary = Skill.generate_from_save_string(skill_dict["primary"])
            self.secondary = Skill.generate_from_save_string(skill_dict["secondary"])
            self.hidden = HiddenSkillEnum[skill_dict["hidden"]] if skill_dict["hidden"] else None
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
    
    @staticmethod
    def generate_new_catskills(status, moons, hidden_skill:HiddenSkillEnum=None):
        new_skill = CatSkills()
        
        new_skill.hidden = hidden_skill       

        #TODO: Make this nicer
        if status == "newborn" or moons <= 0:
            pass
        elif status == 'kitten' or moons < 6:
            new_skill.primary = Skill.get_random_skill(points=0, interest_only=True)
        elif status == 'apprentice':
            new_skill.primary = Skill.get_random_skill(point_tier=1, interest_only=True)
            if random.randint(1, 3) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=1, interest_only=True)
        elif moons < 50:
            new_skill.primary = Skill.get_random_skill(point_tier=random.randint(1, 2))
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=random.randint(1, 2))
        elif moons < 100:
            new_skill.primary = Skill.get_random_skill(point_tier=random.randint(1, 3))
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=random.randint(1, 3))
        elif moons < 150:
            new_skill.primary = Skill.get_random_skill(point_tier=random.randint(2, 3))
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=random.randint(2, 3))
        else:
            new_skill.primary = Skill.get_random_skill(point_tier=1)
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=1)
        
        return new_skill
            
    def get_skill_dict(self):
        return {
            "primary": self.primary.get_save_string() if self.primary else None,
            "secondary": self.secondary.get_save_string() if self.secondary else None, 
            "hidden": self.hidden.name if self.hidden else None
        }

    def skill_string(self):
        output = []
        if self.primary:
            output.append(self.primary.skill)
        if self.secondary:
            output.append(self.secondary.skill)
        
        if not output:
            return "???"
        else:
            return " + ".join(output) 

    def mentor_influence(self, the_cat, mentor):
        """
        this function handles mentor influence on the cat's skill
        :param the_cat: the cat object
        :param mentor: the mentor's cat object
        """
        # non apprentices and mentor-less babies not allowed
        if "apprentice" not in the_cat.status or the_cat.mentor is None:
            return
        
        # Determine if any skills can be effected
        mentor_tags = CatSkills.influence_flags[mentor.skills.primary.path] if mentor.skills.primary else None

        can_primary = bool(
            CatSkills.influence_flags[self.primary.path] & mentor_tags) if self.primary and mentor_tags else False
        can_secondary = bool(
            CatSkills.influence_flags[self.secondary.path] & mentor_tags) if self.secondary and mentor_tags else False
            
        # If nothing can be effected, just return as well.         
        if not can_primary or can_secondary:
            return

        amount_effect = random.randint(2, 5)
        
        if can_primary and can_secondary:
            if random.randint(1, 2) == 1:
                self.primary.points += amount_effect
                path = self.primary.path
            else:
                self.secondary += amount_effect
                path = self.secondary.path
        elif can_primary:
            self.primary.points += amount_effect
            path = self.primary.path
        else:
            self.secondary.points += amount_effect
            path = self.secondary.path
    
        return (mentor.ID, path, amount_effect)

    def progress_skill(self, the_cat):
        """
        this function should be run every moon for every cat to progress their skills accordingly
        :param the_cat: the cat object for affected cat
        """
        if the_cat.status == 'newborn':
            return
        
        # Give a primary is there isn't one already (and the kits is not a newborn)
        if not self.primary:
            parents = [the_cat.fetch_cat(i) for i in [the_cat.parent1, the_cat.parent2] + the_cat.adoptive_parents if 
                    type(the_cat) == type(the_cat.fetch_cat(i))]
            parental_paths = [i.skill.primary.path for i in parents if i.skill.primary] + [i.skill.secondary.path for i in parents if i.skill.secondary]
                    
             # If there are parental paths, flip a coin to determine if they will get a parents path
            if parental_paths and random.random(0, 1):
                self.primary = Skill(random.choice(parental_paths), points=0, interest_only=True if the_cat in ["apprentice", "kitten"] else False)
            else:
                self.primary = Skill.get_random_skill(points=0, interest_only=True if the_cat in ["apprentice", "kitten"] else False)
        
        if the_cat.status == 'kitten':
            # Give them a primary path if they don't have one already
            if not self.primary:
                parents = [the_cat.fetch_cat(i) for i in [self.the_cat.parent1, self.the_cat.parent2] + the_cat.adoptive_parents if 
                           type(the_cat) == type(the_cat.fetch_cat(i))]
                parental_paths = [i.skill.primary.path for i in parents if i.skill.primary] + [i.skill.secondary.path for i in parents if i.skill.secondary]
                
               
            
            # Check to see if the cat gains a secondary
            if not self.secondary and not int(random.random() * 6):
                # if there's no secondary skill, try to give one!
                self.secondary = Skill.get_random_skill(points=0, interest_only=True, exclude=self.primary.path)
            
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

        elif 'apprentice' in the_cat.status:
            # Check to see if the cat gains a secondary
            if not self.secondary and not int(random.random() * 6):
                # if there's no secondary skill, try to give one!
                self.secondary = Skill.get_random_skill(points=0, interest_only=True, exclude=self.primary.path)
            
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

        elif the_cat.moons > 150:
            # for old cats, we want to check if the skills start to degrade at all, age is the great equalizer
            if not int(random.random() * 300 - the_cat.moons):  # chance increases as the_cat ages
                self.primary.points -= 1
        else:
            #If they are still in "interest" stage, there is a change to swap primary and secondary
            if self.primary.interest_only and self.secondary:
                flip = random.choices([False, True], [self.primary.points, self.secondary.points])[0]
                if flip:
                    _temp = self.primary
                    self.primary = self.secondary
                    self.secondary = _temp
            
            self.primary.interest_only = False
            if self.secondary:
                self.secondary.interest_only = False
                
            # If a cat doesn't can a secondary, have a small change for them to get one. 
            if not int(random.random() * 200):
                self.secondary = Skill.get_random_skill(exclude=self.primary.path)
            
             # If a cat is not an apprentice or kit, 
             # only has a change for primary to level up. 
            if not int(random.random() * 4):
                self.primary.points += 1

    @staticmethod
    def get_skills_from_old(old_skill):
        """Generates a CatSkill object"""
        
        new_skill = CatSkills()
        
        conversion = {
            "strong connection to StarClan": (PathEnum.STAR, 2), 
            "good healer": (PathEnum.HEALER, 1),
            "great healer": (PathEnum.HEALER, 2),
            "fantastic healer": (PathEnum.HEALER, 3),
            "good teacher": (PathEnum.TEACHER, 1),
            "great teacher": (PathEnum.TEACHER, 2),
            "fantastic teacher": (PathEnum.TEACHER, 3),
            "good mediator": (PathEnum.MEDIATOR, 1),
            "great mediator": (PathEnum.MEDIATOR, 2),
            "excellent mediator": (PathEnum.MEDIATOR, 3),
            "smart": (PathEnum.CLEVER, 1),
            "very smart": (PathEnum.CLEVER, 2),
            "extremely smart": (PathEnum.CLEVER, 3),
            "good hunter": (PathEnum.HUNTER, 1),
            "great hunter": (PathEnum.HUNTER, 2),
            "fantastic hunter": (PathEnum.HUNTER, 3),
            "good fighter": (PathEnum.FIGHER, 1),
            "great fighter": (PathEnum.FIGHER, 2),
            "excellent fighter": (PathEnum.FIGHER, 3),
            "good speaker": (PathEnum.SPEAKER, 1),
            "great speaker": (PathEnum.SPEAKER, 2),
            "excellent speaker": (PathEnum.SPEAKER, 3),
            "good storyteller": (PathEnum.STORY, 1),
            "great storyteller": (PathEnum.STORY, 2),
            "fantastic storyteller": (PathEnum.STORY, 3),
            "smart tactician": (PathEnum.INSIGHTFUL, 1),
            "valuable tactician": (PathEnum.INSIGHTFUL, 2),
            "valuable insight": (PathEnum.INSIGHTFUL, 3),
            "good kitsitter": (PathEnum.KIT, 1),
            "great kitsitter": (PathEnum.KIT, 2),
            "beloved kitsitter": (PathEnum.KIT, 3),
            "camp keeper": (PathEnum.CAMP, 3),
            "den builder": (PathEnum.CAMP, 2),
            "omen sight": (PathEnum.OMEN, 3),
            "dream walker": (PathEnum.DREAM, 2),
            "clairvoyant": (PathEnum.CLAIRVOYANT, 2),
            "prophet": (PathEnum.PROPHET, 3),
            "lore keeper": (PathEnum.LORE, 2),
            "keen eye": (PathEnum.SENSE, 2),
        },
        
        if old_skill in conversion:
            new_skill.primary = Skill(conversion[old_skill][0])
            new_skill.primary.set_points_to_tier(conversion[old_skill][1])
        
        return new_skill


        
            

        