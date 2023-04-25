import random

from scripts.cat.cats import SKILLS


class Skills:
    """
    Handles the cat's skills.
    the path is the group that the skill belongs to
    the tier is the index of the skill within the path with 0 being an Interest and 3 being the highest tier of that path
    the points are the "experience" of the skill, skills with 10 points get moved up to the next tier

    cat.skills returns a list of all the cat's skills
    """
    def __init__(self,
                 primary_path='???',
                 primary_tier=None,
                 primary_points=0,
                 secondary_path=None,
                 secondary_tier=None,
                 secondary_points=0,
                 hidden_skill=None,
                 skill_dict=None):
        self.all_paths = SKILLS['paths']

        if skill_dict:
            self.primary_path = skill_dict["primary"]["path"]
            self.primary_skill = self.all_paths[self.primary_path][self.primary_tier]
            self.primary_tier = skill_dict["primary"]["tier"]
            self.primary_points = skill_dict["primary"]["points"]

            self.secondary_path = skill_dict["secondary"]["path"]
            self.secondary_skill = self.all_paths[self.secondary_path][self.secondary_tier]
            self.secondary_tier = skill_dict["secondary"]["tier"]
            self.secondary_points = skill_dict["secondary"]["points"]

            self.hidden_skill = skill_dict["hidden"]
        else:
            self.primary_path = primary_path
            self.primary_tier = primary_tier
            self.primary_points = primary_points

            self.secondary_path = secondary_path
            self.secondary_tier = secondary_tier
            self.secondary_points = secondary_points

            self.hidden_skill = hidden_skill

    def generate_cat_skill(self, cat):
        if cat.moons == 0:
            pass
        elif cat.status == 'kitten':
            self.primary_path = choice(SKILLS[])
            self.primary_skill

    def __repr__(self):
        if self.secondary_skill and self.hidden_skill:
            return [self.primary_skill, self.secondary_skill, self.hidden_skill]
        elif self.secondary_skill:
            return [self.primary_skill, self.secondary_skill]
        elif self.hidden_skill:
            return [self.primary_skill, self.hidden_skill]
        else:
            return [self.primary_skill]
