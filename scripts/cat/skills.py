import random

from scripts.cat.cats import SKILLS


class CatSkills:
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
            self.primary_tier = skill_dict["primary"]["tier"]
            self.primary_points = skill_dict["primary"]["points"]

            self.secondary_path = skill_dict["secondary"]["path"]
            self.secondary_tier = skill_dict["secondary"]["tier"]
            self.secondary_points = skill_dict["secondary"]["points"]

            # these are not saved in the skill dict to make it easy for us to change skill names in the future
            if self.primary_path != '???':
                self.primary_skill = self.all_paths[self.primary_path][self.primary_tier]
            else:
                self.primary_skill = None
            if self.secondary_path:
                self.secondary_skill = self.all_paths[self.secondary_path][self.secondary_tier]
            else:
                self.secondary_skill = None

            self.hidden_skill = skill_dict["hidden"]
        else:
            self.primary_path = primary_path
            self.primary_tier = primary_tier
            self.primary_points = primary_points

            self.secondary_path = secondary_path
            self.secondary_tier = secondary_tier
            self.secondary_points = secondary_points

            self.hidden_skill = hidden_skill

    @staticmethod
    def update_skill(the_cat):
        """
        this function just refreshes the cat's primary and secondary skills, use after changing tiers
        """
        if the_cat.skills.primary_path != '???':
            the_cat.skills.primary_skill = the_cat.skills.all_paths[the_cat.skills.primary_path][
                the_cat.skills.primary_tier]
        else:
            the_cat.skills.primary_skill = None
        if the_cat.skills.secondary_path:
            the_cat.skills.secondary_skill = the_cat.skills.all_paths[the_cat.skills.secondary_path][
                the_cat.skills.secondary_tier]
        else:
            the_cat.skills.secondary_skill = None

    def influence_skill(self, Cat, the_cat):
        """
        this function handles mentor influence on the cat's skill
        """
        # non apprentices and mentor-less babies not allowed
        if "apprentice" not in the_cat.status or the_cat.mentor is None:
            return

        mentor = Cat.fetch_cat(the_cat.mentor)
        influence_groups = SKILLS["influence_groups"][mentor.skills.primary_path]
        if the_cat.skills.primary_path in influence_groups and the_cat.skills.secondary_path in influence_groups:
            if random.randint(1, 2) == 1:
                the_cat.skills.primary_points += 1
            else:
                the_cat.skills.secondary_points += 1
        elif the_cat.skills.primary_path in influence_groups:
            the_cat.skills.primary_points += 1
        elif the_cat.skills.secondary_path in influence_groups:
            the_cat.skills.secondary_points += 1

    def progress_skill(self, Cat, the_cat):
        """
        this function should be run every moon for every cat to progress their skills accordingly
        """
        if the_cat.status == 'newborn':
            pass
        elif the_cat.status == 'kitten':
            # if the the_cat has skills, check if they get any points this moon
            if the_cat.skills.primary_skill and the_cat.skills.secondary_skill:
                if not int(random.random() * 4):
                    if random.randint(1, 2) == 1:
                        the_cat.skills.primary_points += 1
                    else:
                        the_cat.skills.secondary_points += 1
            elif the_cat.skills.primary_skill:
                if not int(random.random() * 4):
                    the_cat.skills.primary_points += 1

                # if there's no secondary skill, try to give one!
                if not the_cat.secondary_skill and not int(random.random() * 6):
                    the_cat.skills.secondary_path = random.choice(
                        [path for path in self.all_paths if path != the_cat.skills.primary_path])
                    the_cat.skills.secondary_tier = 0
                    the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]

            # give a path if kit is still pathless
            else:
                # collect the parent's skill paths
                parental_paths = []
                if the_cat.parent1:
                    parent1 = Cat.fetch_the_cat(the_cat.parent1)
                    parental_paths.append(parent1.skills.primary_path)
                if the_cat.parent2:
                    parent2 = Cat.fetch_the_cat(the_cat.parent2)
                    parental_paths.append(parent2.skills.primary_path)

                # if parental paths were available, try to assign one
                if parental_paths and not int(random.random() * 4):
                    the_cat.skills.primary_path = random.choice(parental_paths)
                # else assign a random primary path
                else:
                    the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
                the_cat.skills.primary_tier = 0
                the_cat.skills.primary_skill = the_cat.skills.secondary_path[the_cat.secondary_tier]

        elif 'apprentice' in the_cat.status or the_cat.age == 'adolescent':
            # if the cat can work, try to increase a point in either skill path
            if the_cat.skills.primary_skill and the_cat.skills.secondary_skill and not the_cat.not_working():
                if not int(random.random() * 4):
                    if random.randint(1, 2) == 1:
                        the_cat.skills.primary_points += 1
                    else:
                        the_cat.skills.secondary_points += 1
            elif the_cat.skills.primary_skill and not the_cat.not_working():
                if not int(random.random() * 4):
                    the_cat.skills.primary_points += 1

            # check if they got a secondary skill, if not then try to give one
            if not the_cat.secondary_skill and not int(random.random() * 2):
                # if they have a mentor, give them a matching path to the mentor
                if the_cat.mentor:
                    mentor = Cat.fetch_the_cat(the_cat.mentor)
                    the_cat.skills.secondary_path = mentor.skills.primary_path
                else:
                    the_cat.skills.secondary_path = random.choice(
                        [path for path in self.all_paths if path != the_cat.skills.primary_path])
                the_cat.skills.secondary_tier = 0
                the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]

        elif the_cat.age in ['young adult', 'adult', 'senior adult']:
            # if they haven't specialized yet, then give them a specialization
            if the_cat.skills.primary_tier == 0:
                if the_cat.skills.primary_skill and the_cat.skills.secondary_skill:
                    # pick which skill is specialized
                    chosen_special = random.choices(["primary", "secondary"],
                                                    [the_cat.skills.primary_points, the_cat.skills.secondary_points])
                    if chosen_special[0] == 'secondary':
                        new_secondary_path = the_cat.skills.primary_path
                        the_cat.skills.primary_path = the_cat.skills.secondary_path
                        the_cat.skills.secondary_path = new_secondary_path
                    # now check if they get to have a secondary at all
                    if int(random.random() * 10):
                        the_cat.skills.secondary_path = None

                    # set tiers and reset points
                    the_cat.skills.primary_tier = 1
                    the_cat.skills.primary_points = 0
                    the_cat.skills.secondary_path = 1
                    the_cat.skills.secondary_points = 0
                else:
                    the_cat.skills.primary_tier = 1
                    the_cat.skills.primary_points = 0

                # refresh the the_cat's skills to match new tier
                self.update_skill(the_cat)

            # attempt to add points to the skill:
            elif the_cat.skills.primary_points < 10:
                # the_cat will have, on average, 20 skill improvements before hitting senior (100 moons / 5)
                if not int(random.random() * 5):
                    # they have a 1/45 chance of hitting the 10, which jumps them up a tier immediately
                    # keep in mind that points over the 10 total don't roll over to the next tier
                    # majority of the_cats should be getting to 2nd or 3rd around senior adult
                    amount_improved = random.choices([1, 2, 3, 10], [25, 15, 4, 1])
                    the_cat.skills.primary_points += amount_improved
            # check if they need to jump to the next tier
            elif the_cat.skills.primary_points >= 10 and the_cat.skills.primary_tier != 3:
                the_cat.skills.primary_tier += 1
                self.update_skill(the_cat)

        else:
            # for old cats, we want to check if the skills start to degrade at all, age is the great equalizer
            if not int(random.random() * 300 - the_cat.moons):  # chance increases as the_cat ages
                if the_cat.skills.primary_tier != 1:
                    the_cat.skills.primary_tier -= 1
                    self.update_skill(the_cat)

    def generate_cat_skill(self, the_cat):
        """
        this handles giving newly generated the_cats a skill - will not give hidden skills
        """
        if the_cat.moons == 0:
            pass
        elif the_cat.status == 'kitten':
            the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
            the_cat.skills.primary_tier = 0
            the_cat.skills.primary_skill = the_cat.skills.primary_path[the_cat.skills.primary_tier]
        elif the_cat.status == 'apprentice':
            the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
            the_cat.skills.primary_tier = 0
            the_cat.skills.primary_skill = the_cat.skills.primary_path[the_cat.skills.primary_tier]
            if random.randint(1, 2) == 1:
                the_cat.skills.secondary_path = random.choice([path for path in self.all_paths])
                the_cat.skills.secondary_tier = 0
                the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]
        elif the_cat.moons < 50:
            the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
            the_cat.skills.primary_tier = 1
            the_cat.skills.primary_skill = the_cat.skills.primary_path[the_cat.skills.primary_tier]
            if random.randint(1, 3) == 1:
                the_cat.skills.secondary_path = random.choice([path for path in self.all_paths])
                the_cat.skills.secondary_tier = 1
                the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]
        elif the_cat.moons < 100:
            the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
            the_cat.skills.primary_tier = random.randint(1, 3)
            the_cat.skills.primary_skill = the_cat.skills.primary_path[the_cat.skills.primary_tier]
            if random.randint(1, 3) == 1:
                the_cat.skills.secondary_path = random.choice([path for path in self.all_paths])
                the_cat.skills.secondary_tier = 1
                the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]
        elif the_cat.moons < 150:
            the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
            the_cat.skills.primary_tier = random.randint(2, 3)
            the_cat.skills.primary_skill = the_cat.skills.primary_path[the_cat.skills.primary_tier]
            if random.randint(1, 3) == 1:
                the_cat.skills.secondary_path = random.choice([path for path in self.all_paths])
                the_cat.skills.secondary_tier = 1
                the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]
        else:
            the_cat.skills.primary_path = random.choice([path for path in self.all_paths])
            the_cat.skills.primary_tier = random.randint(1, 2)
            the_cat.skills.primary_skill = the_cat.skills.primary_path[the_cat.skills.primary_tier]
            if random.randint(1, 3) == 1:
                the_cat.skills.secondary_path = random.choice([path for path in self.all_paths])
                the_cat.skills.secondary_tier = 1
                the_cat.skills.secondary_skill = the_cat.skills.secondary_path[the_cat.skills.secondary_tier]

    def __repr__(self):
        if self.secondary_skill and self.hidden_skill:
            return [self.primary_skill, self.secondary_skill, self.hidden_skill]
        elif self.secondary_skill:
            return [self.primary_skill, self.secondary_skill]
        elif self.hidden_skill:
            return [self.primary_skill, self.hidden_skill]
        else:
            return [self.primary_skill]
