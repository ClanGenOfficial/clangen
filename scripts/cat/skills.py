import random
from enum import Enum, Flag, auto
from typing import Union

class SkillPath(Enum):
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
        
        uncommon_paths = [i for i in [SkillPath.GHOST, SkillPath.PROPHET, 
                          SkillPath.CLAIRVOYANT, SkillPath.DREAM,
                          SkillPath.OMEN, SkillPath.STAR, SkillPath.HEALER]
                          if i not in exclude]
        
        
        if not int(random.random() * 25):
            return random.choice(uncommon_paths)
        else:
            common_paths = [i for i in list(SkillPath) if 
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
    '''Skills handling functions mostly'''
    
    tier_ranges = ((0, 9), (10, 19), (20, 29))
    point_range = (0, 29)
    
    def __init__(self, path:SkillPath, points:int=0, interest_only:bool=False):
        
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
        '''Generates the skill from the save string in the cat data'''
        if not save_string:
            return None
        
        split_values = save_string.split(",")
        if split_values[2].lower() == "true":
            interest = True
        else:
            interest = False
        
        return Skill(SkillPath[split_values[0]], int(split_values[1]), interest)
    
    @staticmethod
    def get_random_skill(points:int = None, point_tier:int = None, exclude=(), interest_only=False):
        """Generates a random skill. If wanted, you can specify a tier for the points
        value to be randomized within. """
        
        if isinstance(points, int):
            points = points
        elif isinstance(point_tier, int) and 1 <= point_tier <= 3:
            points = random.randint(Skill.tier_ranges[point_tier-1][0], Skill.tier_ranges[point_tier-1][1])
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
        '''Skill property'''
        return self.path.value[self.tier]
        
    @skill.setter
    def skill(self):
        '''Can't set the skill directly with this setter'''
        print("Can't set skill directly")
    
    @property
    def tier(self):
        '''Returns the tier level of the skill'''
        if self.interest_only:
            return 0 
        for _ran, i in zip(Skill.tier_ranges, range(1, 4)):
            if _ran[0] <= self.points <= _ran[1]:
                return i
                
        return 1
    
    @tier.setter
    def tier(self):
        print("Can't set tier directly")
    
    def set_points_to_tier(self, tier:int):
        """This is seperate from the tier setter, since it will booonly allow you
        to set points to tier 1, 2, or 3, and never 0. Tier 0 is retricted to interest_only
        skills"""
        
        # Make sure it in the right range. If not, return. 
        if not (1 <= tier <= 3):
            return
        
        # Adjust to 0-indexed ranges list
        self.points = Skill.tier_ranges[tier - 1][0]
        
    def get_save_string(self):
        '''Gets the string that is saved in the cat data'''
        return f"{self.path.name},{self.points},{self.interest_only}"

class CatSkills:
    """
    Holds the cats skills, and handled changes in the skills. 
    """

    #Mentor Inflence groups.
    # pylint: disable=unsupported-binary-operation
    influence_flags = {
        SkillPath.TEACHER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE | SkillTypeFlag.SMART | SkillTypeFlag.OBSERVANT | SkillTypeFlag.SOCIAL,
        SkillPath.HUNTER: SkillTypeFlag.STRONG | SkillTypeFlag.AGILE | SkillTypeFlag.OBSERVANT,
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
        SkillPath.HEALER: SkillTypeFlag.SMART | SkillTypeFlag.OBSERVANT | SkillTypeFlag.SOCIAL,
        SkillPath.STAR: SkillTypeFlag.SUPERNATURAL,
        SkillPath.OMEN: SkillTypeFlag.SUPERNATURAL | SkillTypeFlag.OBSERVANT,
        SkillPath.DREAM: SkillTypeFlag.SUPERNATURAL,
        SkillPath.CLAIRVOYANT: SkillTypeFlag.SUPERNATURAL | SkillTypeFlag.OBSERVANT,
        SkillPath.PROPHET: SkillTypeFlag.SUPERNATURAL,
        SkillPath.GHOST: SkillTypeFlag.SUPERNATURAL
    }
    # pylint: enable=unsupported-binary-operation
    
    def __init__(self,
                 skill_dict=None,
                 primary_path:SkillPath = None,
                 primary_points:int = 0,
                 secondary_path: SkillPath = None,
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
        '''Generates a new skill'''
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
                new_skill.secondary = Skill.get_random_skill(point_tier=1, interest_only=True, exclude=new_skill.primary.path)
        elif moons < 50:
            new_skill.primary = Skill.get_random_skill(point_tier=random.randint(1, 2))
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=random.randint(1, 2), exclude=new_skill.primary.path)
        elif moons < 100:
            new_skill.primary = Skill.get_random_skill(point_tier=random.randint(1, 3))
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=random.randint(1, 2), exclude=new_skill.primary.path)
        elif moons < 150:
            new_skill.primary = Skill.get_random_skill(point_tier=random.randint(2, 3))
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=random.randint(1, 2), exclude=new_skill.primary.path)
        else:
            new_skill.primary = Skill.get_random_skill(point_tier=1)
            if random.randint(1, 2) == 1:
                new_skill.secondary = Skill.get_random_skill(point_tier=1, exclude=new_skill.primary.path)
        
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

    def mentor_influence(self, mentor):
        """
        this function handles mentor influence on the cat's skill
        :param the_cat: the cat object
        :param mentor: the mentor's cat object
        """

        if not mentor:
            return
        
        # Determine if any skills can be effected
        mentor_tags = CatSkills.influence_flags[mentor.skills.primary.path] if mentor.skills.primary else None

        can_primary = bool(
            CatSkills.influence_flags[self.primary.path] | mentor_tags) if self.primary and mentor_tags else False
        can_secondary = bool(
            CatSkills.influence_flags[self.secondary.path] | mentor_tags) if self.secondary and mentor_tags else False
            
        # If nothing can be effected, just return as well.         
        if not (can_primary or can_secondary):
            return

        amount_effect = random.randint(2, 5)
        
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
    
        return (mentor.ID, path, amount_effect)

    def progress_skill(self, the_cat):
        """
        this function should be run every moon for every cat to progress their skills accordingly
        :param the_cat: the cat object for affected cat
        """
        
        if not (the_cat.outside or the_cat.exiled):
            
            if the_cat.status == 'newborn':
                return
            
            # Give a primary is there isn't one already (and the kits is not a newborn)
            if not self.primary:
                parents = [the_cat.fetch_cat(i) for i in [the_cat.parent1, the_cat.parent2] + the_cat.adoptive_parents if 
                        type(the_cat) == type(the_cat.fetch_cat(i))]
                parental_paths = [i.skills.primary.path for i in parents if i.skills.primary] + [i.skills.secondary.path for i in parents if i.skills.secondary]
                        
                # If there are parental paths, flip a coin to determine if they will get a parents path
                if parental_paths and random.randint(0, 1):
                    self.primary = Skill(random.choice(parental_paths), points=0, interest_only=True if the_cat.status in ["apprentice", "kitten"] else False)
                else:
                    self.primary = Skill.get_random_skill(points=0, interest_only=True if the_cat.status in ["apprentice", "kitten"] else False)
            
            if the_cat.status == 'kitten':
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
                    flip = random.choices([False, True], [max(self.primary.points, 1), 
                                                        max(self.secondary.points, 1)])[0]
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
        else:
            # section for outside cats only. Trimmed down, only the basics. 
            if the_cat.moons <= 0:
                return
            
            # Give a primary is there isn't one already, and the cat is older than one moon. 
            if not self.primary:
                parents = [the_cat.fetch_cat(i) for i in [the_cat.parent1, the_cat.parent2] + the_cat.adoptive_parents if 
                        type(the_cat) == type(the_cat.fetch_cat(i))]
                parental_paths = [i.skills.primary.path for i in parents if i.skills.primary] + [i.skills.secondary.path for i in parents if i.skills.secondary]
                        
                # If there are parental paths, flip a coin to determine if they will get a parents path
                if parental_paths and random.randint(0, 1):
                    self.primary = Skill(random.choice(parental_paths), points=0, interest_only=True if the_cat.status in ["apprentice", "kitten"] else False)
                else:
                    self.primary = Skill.get_random_skill(points=0, interest_only=True if the_cat.status in ["apprentice", "kitten"] else False)
            
            # For outside cats, don't worry about secondary skill. 
            if the_cat.age not in ["kitten", "adolescent"]:
                self.primary.interest_only = False
                if self.secondary:
                    self.secondary.interest_only = False
    def meets_skill_requirement(self, path: Union[str, SkillPath, HiddenSkillEnum], min_tier:int=0) -> bool:
        """Checks both primary and seconday, to see if cat matches skill restaint"""
        
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
        
    @staticmethod
    def get_skills_from_old(old_skill, status, moons):
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
            new_skill = CatSkills.generate_new_catskills(status, moons)
        
        return new_skill


        
            

        