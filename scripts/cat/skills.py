import random

import ujson

class CatSkills:
    """
    Handles the cat's skills.
    the path is the group that the skill belongs to
    the tier is the index of the skill within the path with 0 being an Interest and 3 being the highest tier of that path
    the points are the "experience" of the skill, skills with 10 points get moved up to the next tier
    """

    def __init__(self,
                 primary_path=None,
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

            self.hidden_skill = skill_dict["hidden"]
        else:
            self.primary_path = primary_path
            self.primary_tier = primary_tier
            self.primary_points = primary_points

            self.secondary_path = secondary_path
            self.secondary_tier = secondary_tier
            self.secondary_points = secondary_points

            self.hidden_skill = hidden_skill

        self.primary_skill = '???'
        self.secondary_skill = None

        self.update_skill()

    def update_skill(self):
        """
        this function just refreshes the cat's primary and secondary skills, use after changing tiers
        """
        if self.primary_path:
            self.primary_skill = self.all_paths[self.primary_path][self.primary_tier]
        else:
            self.primary_skill = '???'
        if self.secondary_path:
            self.secondary_skill = self.all_paths[self.secondary_path][self.secondary_tier]
        else:
            self.secondary_skill = None

    def influence_skill(self, the_cat, mentor):
        """
        this function handles mentor influence on the cat's skill
        :param the_cat: the cat object
        :param mentor: the mentor's cat object
        """
        # non apprentices and mentor-less babies not allowed
        if "apprentice" not in the_cat.status or the_cat.mentor is None:
            return

        influenced = False
        influence_groups = SKILLS["influence_groups"][mentor.skills.primary_path]
        if self.primary_path in influence_groups and self.secondary_path in influence_groups:
            influenced = True
            if random.randint(1, 2) == 1:
                self.primary_points += 1
            else:
                self.secondary_points += 1
        elif self.primary_path in influence_groups:
            influenced = True
            self.primary_points += 1
        elif self.secondary_path in influence_groups:
            influenced = True
            self.secondary_points += 1
        if influenced:
            the_cat.history.add_mentor_influence(the_cat, mentor)


    def progress_skill(self, the_cat, mentor, parent1, parent2):
        """
        this function should be run every moon for every cat to progress their skills accordingly
        :param the_cat: the cat object for affected cat
        :param mentor: the cat object for mentor
        :param parent1: the cat object for parent1
        :param parent2: the cat object for parent2
        """
        if the_cat.status == 'newborn':
            pass
        elif the_cat.status == 'kitten':
            # if the the_cat has skills, check if they get any points this moon
            if self.primary_skill and self.secondary_skill:
                if not int(random.random() * 4):
                    if random.randint(1, 2) == 1:
                        self.primary_points += 1
                    else:
                        self.secondary_points += 1
            elif self.primary_skill:
                if not int(random.random() * 4):
                    self.primary_points += 1

                # if there's no secondary skill, try to give one!
                if not self.secondary_skill and not int(random.random() * 6):
                    self.secondary_path = random.choice(
                        [path for path in self.all_paths if path != self.primary_path])
                    self.secondary_tier = 0
                    self.secondary_skill = self.secondary_path[self.secondary_tier]

            # give a path if kit is still pathless
            else:
                # collect the parent's skill paths
                parental_paths = []
                if parent1:
                    parental_paths.append(parent1.skills.primary_path)
                if parent2:
                    parental_paths.append(parent2.skills.primary_path)

                # if parental paths were available, try to assign one
                if parental_paths and not int(random.random() * 4):
                    self.primary_path = random.choice(parental_paths)
                # else assign a random primary path
                else:
                    self.primary_path = random.choice([path for path in self.all_paths])
                self.primary_tier = 0
                self.primary_skill = self.secondary_path[self.secondary_tier]

        elif 'apprentice' in the_cat.status or the_cat.age == 'adolescent':
            # try to increase a point in either skill path
            if self.primary_skill and self.secondary_skill:
                if not int(random.random() * 4):
                    if random.randint(1, 2) == 1:
                        self.primary_points += 1
                    else:
                        self.secondary_points += 1
            elif self.primary_skill:
                if not int(random.random() * 4):
                    self.primary_points += 1

            # check if they got a secondary skill, if not then try to give one
            if not self.secondary_skill and not int(random.random() * 2):
                # if they have a mentor, give them a matching path to the mentor
                if mentor:
                    self.secondary_path = mentor.skills.primary_path
                else:
                    self.secondary_path = random.choice(
                        [path for path in self.all_paths if path not in ['hidden', self.primary_path]])
                self.secondary_tier = 0
                self.secondary_skill = self.secondary_path[self.secondary_tier]

        elif the_cat.age in ['young adult', 'adult', 'senior adult']:
            # if they haven't specialized yet, then give them a specialization
            if self.primary_tier == 0:
                if self.primary_skill and self.secondary_skill:
                    # pick which skill is specialized
                    chosen_special = random.choices(["primary", "secondary"],
                                                    [self.primary_points, self.secondary_points])
                    if chosen_special[0] == 'secondary':
                        new_secondary_path = self.primary_path
                        self.primary_path = self.secondary_path
                        self.secondary_path = new_secondary_path
                    # now check if they get to have a secondary at all
                    if int(random.random() * 10):
                        self.secondary_path = None

                    # set tiers and reset points
                    self.primary_tier = 1
                    self.primary_points = 0
                    self.secondary_path = 1
                    self.secondary_points = 0
                else:
                    self.primary_tier = 1
                    self.primary_points = 0

                # refresh the the_cat's skills to match new tier
                self.update_skill()
                the_cat.history.add_mentor_influence(self, the_cat, self.primary_skill, self.secondary_skill)

            # attempt to add points to the skill:
            elif self.primary_points < 10:
                # the_cat will have, on average, 20 skill improvements before hitting senior (100 moons / 5)
                if not int(random.random() * 5):
                    # they have a 1/45 chance of hitting the 10, which jumps them up a tier immediately
                    # keep in mind that points over the 10 total don't roll over to the next tier
                    # majority of the_cats should be getting to 2nd or 3rd around senior adult
                    amount_improved = random.choices([1, 2, 3, 10], [25, 15, 4, 1])
                    self.primary_points += amount_improved
            # check if they need to jump to the next tier
            elif self.primary_points >= 10 and self.primary_tier != 3:
                self.primary_tier += 1
                self.primary_points = 0
                self.update_skill()

        else:
            # for old cats, we want to check if the skills start to degrade at all, age is the great equalizer
            if not int(random.random() * 300 - the_cat.moons):  # chance increases as the_cat ages
                if self.primary_tier != 1:
                    self.primary_tier -= 1
                    self.update_skill()

    def convert_old_skills(self, old_skill, the_cat):
        if old_skill in SKILLS["conversion"]:
            print(the_cat.ID, 'converted')
            new_skill = SKILLS["conversion"][old_skill]
            for path in SKILLS["paths"]:
                if new_skill in SKILLS["paths"][path]:
                    self.primary_path = path
                    self.primary_tier = SKILLS["paths"][path].index(new_skill)
        else:
            self.generate_cat_skill(the_cat.status, the_cat.moons)

        self.update_skill()

    def generate_cat_skill(self, status, moons):
        """
        this handles giving newly generated the_cats a skill - will not give hidden skills
        """
        print('generate skill')
        if moons == 0:
            pass
        elif status == 'kitten':
            self.primary_path = random.choice([path for path in self.all_paths if path != 'hidden'])
            self.primary_tier = 0
        elif status == 'apprentice':
            self.primary_path = random.choice([path for path in self.all_paths if path != 'hidden'])
            self.primary_tier = 0
            if random.randint(1, 2) == 1:
                self.secondary_path = random.choice([path for path in self.all_paths if path not in ['hidden', self.primary_path]])
                self.secondary_tier = 0
        elif moons < 50:
            self.primary_path = random.choice([path for path in self.all_paths if path != 'hidden'])
            self.primary_tier = 1
            if random.randint(1, 3) == 1:
                self.secondary_path = random.choice([path for path in self.all_paths if path not in ['hidden', self.primary_path]])
                self.secondary_tier = 1
        elif moons < 100:
            self.primary_path = random.choice([path for path in self.all_paths if path != 'hidden'])
            self.primary_tier = random.randint(1, 3)
            if random.randint(1, 3) == 1:
                self.secondary_path = random.choice([path for path in self.all_paths if path not in ['hidden', self.primary_path]])
                self.secondary_tier = 1
        elif moons < 150:
            self.primary_path = random.choice([path for path in self.all_paths if path != 'hidden'])
            self.primary_tier = random.randint(2, 3)
            if random.randint(1, 3) == 1:
                self.secondary_path = random.choice([path for path in self.all_paths if path not in ['hidden', self.primary_path]])
                self.secondary_tier = 1
        else:
            self.primary_path = random.choice([path for path in self.all_paths if path != 'hidden'])
            self.primary_tier = random.randint(1, 2)
            if random.randint(1, 3) == 1:
                self.secondary_path = random.choice([path for path in self.all_paths if path not in ['hidden', self.primary_path]])
                self.secondary_tier = 1

        self.update_skill()

    def skill_list(self):
        if self.secondary_skill and self.hidden_skill:
            return [self.primary_skill, self.secondary_skill, self.hidden_skill]
        elif self.secondary_skill:
            return [self.primary_skill, self.secondary_skill]
        elif self.hidden_skill:
            return [self.primary_skill, None, self.hidden_skill]
        else:
            return [self.primary_skill]
        
    def skill_string(self):
        output = None
        skills = self.skill_list()
        output = skills[0]
        if len(skills) > 1:
            if skills[1]:
                output += f" + {skills[1]}"
        return output


with open(f"resources/dicts/skills.json", 'r') as read_file:
    SKILLS = ujson.loads(read_file.read())