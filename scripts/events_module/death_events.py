import ujson
import random

from scripts.cat.cats import Cat
from scripts.utility import save_death
from scripts.game_structure.game_essentials import game, SAVE_DEATH

# ---------------------------------------------------------------------------- #
#                             Condition Event Class                            #
# ---------------------------------------------------------------------------- #

class Death_Events():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        pass

    def handle_deaths(self, cat, other_cat, war, enemy_clan, alive_kits):
        """ 
        This function handles the deaths
        """

        name = str(cat.name)
        other_name = str(other_cat.name)
        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{str(other_clan.name)}Clan'
        enemy_clan = f'{str(enemy_clan)}'
        current_lives = int(game.clan.leader_lives)

        possible_deaths = []
        final_deaths = []

        # assign events to correct ranks
        if cat.status == "kitten":
            possible_deaths.extend(self.generate_death_events(KIT_DEATH))
        elif cat.status == "apprentice":
            possible_deaths.extend(self.generate_death_events(GEN_DEATH))
            possible_deaths.extend(self.generate_death_events(APP_DEATH))
        elif cat.status == "warrior":
            possible_deaths.extend(self.generate_death_events(GEN_DEATH))
        elif cat.status == "elder":
            possible_deaths.extend(self.generate_death_events(ELDER_DEATH))
            possible_deaths.extend(self.generate_death_events(AGE_DEATH))
        elif cat.status == "deputy":
            possible_deaths.extend(self.generate_death_events(GEN_DEATH))
            possible_deaths.extend(self.generate_death_events(DEP_DEATH))
        elif cat.status == "leader":
            possible_deaths.extend(self.generate_death_events(GEN_DEATH))
            possible_deaths.extend(self.generate_death_events(LEADER_DEATH))
            possible_deaths.extend(self.generate_death_events(AGE_DEATH))
        elif cat.status in ["medicine cat", "medicine cat apprentice"]:
            possible_deaths.extend(self.generate_death_events(GEN_DEATH))
            possible_deaths.extend(self.generate_death_events(MED_DEATH))
            possible_deaths.extend(self.generate_death_events(AGE_DEATH))

        # everyone gets multi death
        possible_deaths.extend(self.generate_death_events(MULTI_DEATH))

        correct_rank = True
        correct_biome = False
        correct_season = False
        chance_add = False
        mate_check = False
        war_check = False
        kit_check = False
        age_check = False

        for death in possible_deaths:
            # check biome
            if str(game.clan.biome) in death.death_tags:
                correct_biome = True

            # check season
            if str(game.clan.current_season) in death.death_tags:
                correct_season = True

            # check that war events only happen when at war
            if "war" in death.death_tags and war:
                war_check = True
            elif "war" not in death.death_tags:
                war_check = True

            # check if clan has kits
            if "clan_kits" in death.death_tags and alive_kits:
                kit_check = True
            if "clan_kits" not in death.death_tags:
                kit_check = True

            # check for old age
            if "old_age" in death.death_tags and cat.moons > 150:
                age_check = True
            elif "old_age" not in death.death_tags:
                age_check = True

            # check other_cat rank
            if "other_cat_leader" in death.death_tags and other_cat.status != "leader":
                correct_rank = False
            elif "other_cat_dep" in death.death_tags and other_cat.status != "deputy":
                correct_rank = False
            elif "other_cat_med" in death.death_tags and \
                    other_cat.status not in ["medicine cat", "medicine cat apprentice"]:
                correct_rank = False
            elif "other_cat_adult" in death.death_tags and other_cat.age in ["elder", "kitten"]:
                correct_rank = False
            elif "other_cat_kit" in death.death_tags and other_cat.status != "kitten":
                correct_rank = False

            # check for mate if the death requires one
            if "mate" in death.death_tags and cat.mate is not None:
                mate_check = True
            elif "mate" in death.death_tags and cat.mate is None:
                mate_check = False
            elif "mate" not in death.death_tags:
                mate_check = True

            # check cat trait
            if death.cat_trait is not None:
                if cat.trait in death.cat_trait:
                    chance_add = True
                elif not int(random.random() * 5):  # 1/5 chance to add death that doesn't align with trait
                    chance_add = True
            else:
                chance_add = True

            # check cat skill
            if death.cat_skill is not None:
                if cat.skill in death.cat_skill:
                    chance_add = True
                elif not int(random.random() * 5):  # 1/5 chance to add death that doesn't align with skill
                    chance_add = True
            else:
                chance_add = True

            # check other_cat trait
            if death.other_cat_trait is not None:
                if other_cat.trait in death.other_cat_trait:
                    chance_add = True
                elif not int(random.random() * 5):  # 1/5 chance to add death that doesn't align with trait
                    chance_add = True
            else:
                chance_add = True

            # check other_cat skill
            if death.other_cat_skill is not None:
                if other_cat.skill in death.other_cat_skill:
                    chance_add = True
                elif not int(random.random() * 5):  # 1/5 chance to add death that doesn't align with skill
                    chance_add = True
            else:
                chance_add = True

            if correct_rank and \
                    correct_season and \
                    correct_biome and \
                    chance_add and \
                    mate_check and \
                    war_check and \
                    kit_check and \
                    age_check:
                final_deaths.append(death)

        # ---------------------------------------------------------------------------- #
        #                                  kill cats                                   #
        # ---------------------------------------------------------------------------- #
        print(cat.name, cat.status, len(final_deaths), other_cat.name)
        death_cause = (random.choice(final_deaths))

        # text adjust
        death_text = death_cause.death_text
        death_text = death_text.replace("d_c", str(name))
        death_text = death_text.replace("r_c", str(other_name))
        if war:
            death_text = death_text.replace("o_c", str(enemy_clan))
        else:
            death_text = death_text.replace("o_c", str(other_clan_name))

        if "mate" in death_cause.death_tags:
            death_text = death_text.replace("c_m", str(Cat.all_cats.get(cat.mate).name))

        history_text = death_cause.history_text
        history_text = history_text.replace("d_c", str(name))
        history_text = history_text.replace("r_c", str(other_name))
        if war:
            history_text = history_text.replace("o_c", str(enemy_clan))
        else:
            history_text = history_text.replace("o_c", str(other_clan_name))
        if "mate" in death_cause.death_tags:
            history_text = history_text.replace("c_m", str(Cat.all_cats.get(cat.mate).name))

        # check if other_cat dies and kill them
        if "other_cat_death" in death_cause.death_tags or "multi_death" in death_cause.death_tags:
            other_cat.die()
            other_cat.died_by.append(f'{other_name} {history_text}')

        # handle leader lives
        if cat.status == "leader":
            if "all_lives" in death_cause.death_tags:
                game.clan.leader_lives -= 10
                cat.die()
                cat.died_by.append(history_text)
            elif "murder" in death_cause.death_tags or "some_lives" in death_cause.death_tags:
                game.clan.leader_lives -= random.randrange(2, current_lives - 1)
                cat.die()
                cat.died_by.append(history_text)
            else:
                game.clan.leader_lives -= 1
                cat.die()
                cat.died_by.append(history_text)

        else:
            if "multi_death" in death_cause.death_tags:
                cat.die()
                cat.died_by.append(f'{name} {history_text}')
            else:
                cat.die()
                cat.died_by.append(history_text)

        # if "rel_down" in death_cause.death_tags:
        #    other_clan.relations -= 5

        game.cur_events_list.append(death_text)

        if SAVE_DEATH:
            save_death(cat, death_text)

    def generate_death_events(self, events_dict):
        all_death_events = []
        for death in events_dict:
            death_event = DeathEvent(
                death_tags=death["death_tags"],
                death_text=death["death_text"],
                history_text=death["history_text"],
                cat_trait=death["cat_trait"],
                cat_skill=death["cat_skill"],
                other_cat_trait=death["other_cat_trait"],
                other_cat_skill=death["other_cat_skill"]
            )
            all_death_events.append(death_event)

        return all_death_events


class DeathEvent:
    def __init__(self,
                 death_tags=None,
                 death_text='',
                 history_text='',
                 cat_trait=None,
                 cat_skill=None,
                 other_cat_trait=None,
                 other_cat_skill=None,
                 ):
        self.death_tags = death_tags
        self.death_text = death_text
        self.history_text = history_text
        self.cat_trait = cat_trait
        self.cat_skill = cat_skill
        self.other_cat_trait = other_cat_trait
        self.other_cat_skill = other_cat_skill


"""
possible tags: 
"illness", "multi_death", "old_age", "all_lives", "some_lives", "murder", "war"
"leader", "kitten", "deputy", "medicine_cat", "apprentice", "elder"
"other_cat", "other_cat_med", "other_cat_app", "other_cat_kit", "other_cat_dep",  
"other_clan", "rel_down", "rel_up", 
"Forest", "Plains", "Mountainous", "Beach", 
"Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare"
"""

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #
resource_directory = "resources/dicts/events/"

GEN_DEATH = None
with open(f"{resource_directory}gen_death.json", 'r') as read_file:
    GEN_DEATH = ujson.loads(read_file.read())

ELDER_DEATH = None
with open(f"{resource_directory}elder_death.json", 'r') as read_file:
    ELDER_DEATH = ujson.loads(read_file.read())

LEADER_DEATH = None
with open(f"{resource_directory}leader_death.json", 'r') as read_file:
    LEADER_DEATH = ujson.loads(read_file.read())

DEP_DEATH = None
with open(f"{resource_directory}dep_death.json", 'r') as read_file:
    DEP_DEATH = ujson.loads(read_file.read())

MED_DEATH = None
with open(f"{resource_directory}med_death.json", 'r') as read_file:
    MED_DEATH = ujson.loads(read_file.read())

APP_DEATH = None
with open(f"{resource_directory}app_death.json", 'r') as read_file:
    APP_DEATH = ujson.loads(read_file.read())

KIT_DEATH = None
with open(f"{resource_directory}kit_death.json", 'r') as read_file:
    KIT_DEATH = ujson.loads(read_file.read())

MULTI_DEATH = None
with open(f"{resource_directory}multi_death.json", 'r') as read_file:
    MULTI_DEATH = ujson.loads(read_file.read())

AGE_DEATH = None
with open(f"{resource_directory}age_death.json", 'r') as read_file:
    AGE_DEATH = ujson.loads(read_file.read())
