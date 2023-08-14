# pylint: disable=line-too-long
"""

TODO: Docs


"""

# pylint: enable=line-too-long
import random
import traceback
import time

from scripts.cat.history import History
from scripts.patrol import Patrol

import ujson

from scripts.cat.cats import Cat, cat_class
from scripts.clan import HERBS
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE, FRESHKILL_EVENT_ACTIVE
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.events_module.misc_events import MiscEvents
from scripts.events_module.new_cat_events import NewCatEvents
from scripts.events_module.relation_events import Relation_Events
from scripts.events_module.condition_events import Condition_Events
from scripts.cat.pelts import Pelt
from scripts.events_module.death_events import Death_Events
from scripts.events_module.freshkill_pile_events import Freshkill_Events
from scripts.events_module.disaster_events import DisasterEvents
from scripts.events_module.outsider_events import OutsiderEvents
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.cat_relations.relationship import Relationship
from scripts.utility import get_alive_kits, get_med_cats, ceremony_text_adjust, \
    get_current_season, adjust_list_text, ongoing_event_text_adjust, event_text_adjust, create_new_cat
from scripts.events_module.generate_events import GenerateEvents
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.game_structure.windows import SaveError
from scripts.housekeeping.datadir import get_save_dir
from scripts.game_structure.windows import RetireScreen

class Events:
    """
    TODO: DOCS
    """
    all_events = {}
    game.switches['timeskip'] = False
    # This is so we call the static function needed to clear the events dict.
    generate_events = GenerateEvents()
    

    def __init__(self, e_type=None, **cats):
        self.history = History()
        self.e_type = e_type
        self.ID = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(
            random.randint(0, 9)) + str(random.randint(0, 9))
        if e_type is not None:
            self.all_events[self.ID] = self
        self.cats = cats
        self.new_cat_invited = False
        self.ceremony_accessory = False
        self.relation_events = Relation_Events()
        self.pregnancy_events = Pregnancy_Events()
        self.condition_events = Condition_Events()
        self.death_events = Death_Events()
        self.freshkill_events = Freshkill_Events()
        self.new_cat_events = NewCatEvents()
        self.outsider_events = OutsiderEvents()
        self.misc_events = MiscEvents()
        self.CEREMONY_TXT = None
        self.b_txt = None
        self.WAR_TXT = None
        self.load_ceremonies()
        self.load_war_resources()
        self.disaster_events = DisasterEvents()
        self.c_txt = None
        self.d_txt = None
        self.checks = [-1,-1,-1]

    def one_moon(self):
        """
        TODO: DOCS
        """
        if self.checks == [-1,-1,-1] and game.clan.your_cat and game.clan.your_cat.inheritance:
            self.checks = [len(game.clan.your_cat.apprentice), len(game.clan.your_cat.mate), len(game.clan.your_cat.inheritance.get_blood_kits())]
        else:
            self.checks = [len(game.clan.your_cat.apprentice), len(game.clan.your_cat.mate), 0]
        game.cur_events_list = []
        game.herb_events_list = []
        game.mediated = []
        game.switches['saved_clan'] = False
        self.new_cat_invited = False
        self.relation_events.clear_trigger_dict()
        Patrol.used_patrols.clear()
        game.patrolled.clear()
        game.just_died.clear()
        # 1 = reg patrol 2 = lifegen patrol 3 = df patrol 4 = date
        game.switches['patrolled'] = []

        if any(
                str(cat.status) in {
                    'leader', 'deputy', 'warrior', 'medicine cat',
                    'medicine cat apprentice', 'apprentice', 'mediator',
                    'mediator apprentice', "queen", "queen's apprentice"
                } and not cat.dead and not cat.outside
                for cat in Cat.all_cats.values()):
            game.switches['no_able_left'] = False

        # age up the clan, set current season
        game.clan.age += 1
        get_current_season()
        # print(game.clan.current_season)
        self.pregnancy_events.handle_pregnancy_age(game.clan)
        self.check_war()
        
        rejoin_upperbound = game.config["lost_cat"]["rejoin_chance"]
        if random.randint(1, rejoin_upperbound) == 1:
            self.handle_lost_cats_return()

        # Calling of "one_moon" functions.
        
        for cat in Cat.all_cats.copy().values():
            if not cat.outside or cat.dead:
                self.one_moon_cat(cat)
            else:
                self.one_moon_outside_cat(cat)
                
        if Cat.grief_strings:
            # Grab all the dead or outside cats, who should not have grief text
            for ID in Cat.grief_strings.copy():
                check_cat = Cat.all_cats.get(ID)
                if isinstance(check_cat, Cat):
                    if check_cat.dead or check_cat.outside:
                        Cat.grief_strings.pop(ID)

            # Generate events
            
            for cat_id, values in Cat.grief_strings.items():
                for _val in values:
                    if _val[2] == "minor":
                        # Apply the grief message as a thought to the cat
                        text = event_text_adjust(Cat, _val[0], Cat.fetch_cat(cat_id), Cat.fetch_cat(_val[1][0]))
                        Cat.fetch_cat(cat_id).thought = text
                    else:
                        game.cur_events_list.append(
                            Single_Event(_val[0], ["birth_death", "relation"],
                                        _val[1]))
            
            
                
            Cat.grief_strings.clear()

        if Cat.dead_cats:
            ghost_names = []
            shaken_cats = []
            extra_event = None
            for ghost in Cat.dead_cats:
                ghost_names.append(str(ghost.name))
            insert = adjust_list_text(ghost_names)

            if len(Cat.dead_cats) > 1 and game.clan.game_mode != 'classic':
                event = f"The past moon, {insert} have taken their place in StarClan. {game.clan.name}Clan mourns their " \
                        f"loss, and their Clanmates will miss where they had been in their lives. Moments of their " \
                        f"lives are shared in stories around the circle of mourners as those that were closest to them " \
                        f"take them to their final resting place."

                if len(ghost_names) > 2:
                    alive_cats = list(
                        filter(
                            lambda kitty: (kitty.status != "leader" and not kitty.dead and
                                           not kitty.outside and not kitty.exiled), Cat.all_cats.values()))
                    # finds a percentage of the living Clan to become shaken

                    if len(alive_cats) == 0:
                        return
                    else:
                        shaken_cats = random.sample(alive_cats,
                                                    k=max(int((len(alive_cats) * random.choice([4, 5, 6])) / 100), 1))

                    shaken_cat_names = []
                    for cat in shaken_cats:
                        shaken_cat_names.append(str(cat.name))
                        cat.get_injured("shock", event_triggered=False, lethal=False, severity='minor')

                    insert = adjust_list_text(shaken_cat_names)

                    if len(shaken_cats) == 1:
                        extra_event = f"So much grief and death has taken its toll on the cats of {game.clan.name}Clan. {insert} is particularly shaken by it."
                    else:
                        extra_event = f"So much grief and death has taken its toll on the cats of {game.clan.name}Clan. {insert} are particularly shaken by it. "

            else:
                event = f"The past moon, {insert} has taken their place in StarClan. {game.clan.name}Clan mourns their " \
                        f"loss, and their Clanmates will miss the spot they took up in their lives. Moments of their " \
                        f"life are shared in stories around the circle of mourners as those that were closest to them " \
                        f"take them to their final resting place."

            game.cur_events_list.append(
                Single_Event(event, ["birth_death"],
                             [i.ID for i in Cat.dead_cats]))
            if extra_event:
                game.cur_events_list.append(
                    Single_Event(extra_event, ["birth_death"],
                                 [i.ID for i in shaken_cats]))
            Cat.dead_cats.clear()

        self.herb_destruction()
        self.herb_gather()
        game.switches['have kits'] = True
        if game.clan.game_mode in ["expanded", "cruel season"]:
            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            med_fullfilled = medical_cats_condition_fulfilled(
                Cat.all_cats.values(), amount_per_med)
            if not med_fullfilled:
                string = f"{game.clan.name}Clan does not have enough healthy medicine cats! Cats will be sick/hurt " \
                         f"for longer and have a higher chance of dying. "
                game.cur_events_list.insert(0, Single_Event(string, "health"))                
        
        new_list = []
        other_list = []
        for i in game.cur_events_list:
            if str(game.clan.your_cat.name) in i.text:
                new_list.append(i)
            else:
                other_list.append(i)
        
        # Clear the list of cats that died this moon.
        game.just_died.clear()

        # Promote leader and deputy, if needed.
        self.check_and_promote_leader()
        self.check_and_promote_deputy()

        if game.clan.game_mode in ["expanded", "cruel season"]:
            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            med_fullfilled = medical_cats_condition_fulfilled(
                Cat.all_cats.values(), amount_per_med)
            if not med_fullfilled:
                string = f"{game.clan.name}Clan does not have enough healthy medicine cats! Cats will be sick/hurt " \
                            f"for longer and have a higher chance of dying. "
                game.cur_events_list.insert(0, Single_Event(string, "health"))
        else:
            has_med = any(
                str(cat.status) in {"medicine cat", "medicine cat apprentice"}
                and not cat.dead and not cat.outside
                for cat in Cat.all_cats.values())
            if not has_med:
                string = f"{game.clan.name}Clan has no medicine cat!"
                game.cur_events_list.insert(0, Single_Event(string, "health"))
        
        game.cur_events_list = new_list
        game.other_events_list = other_list
        resource_dir = "resources/dicts/events/lifegen_events/"
        with open(f"{resource_dir}ceremonies.json",
                  encoding="ascii") as read_file:
            self.b_txt = ujson.loads(read_file.read())
        with open(f"{resource_dir}events.json",
                  encoding="ascii") as read_file:
            self.c_txt = ujson.loads(read_file.read())
        with open(f"{resource_dir}events_distrust.json",
                  encoding="ascii") as read_file:
            self.e_txt = ujson.loads(read_file.read())
        with open(f"{resource_dir}df.json",
                  encoding="ascii") as read_file:
            self.df_txt = ujson.loads(read_file.read())
        if not game.clan.your_cat.dead and game.clan.your_cat.status != 'exiled':
            if game.clan.your_cat.revealed != 0 and game.clan.age - 3 <= game.clan.your_cat.revealed and game.clan.your_cat.moons != 0 and game.clan.your_cat.moons != 6 and not (game.clan.your_cat.status in ['warrior', 'medicine cat', 'mediator'] and not game.clan.your_cat.w_done) and not game.clan.your_cat.moons == 120:
                for i in range(random.randint(0,2)):
                    d_e = Single_Event(random.choice(self.e_txt[game.clan.your_cat.status]))
                    if d_e not in game.cur_events_list:
                        game.cur_events_list.append(d_e)
            else:
                if game.clan.your_cat.moons == 0:
                    self.generate_birth()
                elif game.clan.your_cat.moons < 6:
                    self.generate_kit_events() 
                elif game.clan.your_cat.moons == 6:
                    self.generate_app_ceremony()
                elif game.clan.your_cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
                    self.generate_app_events()
                elif game.clan.your_cat.status in ['warrior', 'medicine cat', 'mediator', "queen"] and not game.clan.your_cat.w_done:
                    self.generate_ceremony()
                elif game.clan.your_cat.status != 'elder' and game.clan.your_cat.moons != 119:
                    self.generate_events_adult()
                elif game.clan.your_cat.moons == 119:
                    RetireScreen('events screen')
                elif game.clan.your_cat.moons == 120 and game.clan.your_cat.status == 'elder':
                    self.generate_elder_ceremony()
                elif game.clan.your_cat.status == 'elder':
                    self.generate_elder_events()
            
            if game.clan.your_cat.joined_df:
                self.generate_df_events()
            
            if game.clan.your_cat.moons >= 12:
                self.check_gain_app(self.checks)
                self.check_gain_mate(self.checks)
                # self.check_gain_kits(self.checks)
                self.generate_mate_events()
                self.check_retire()

            if random.randint(1,15) == 1:
                self.gain_acc()

        elif game.clan.your_cat.dead and game.clan.your_cat.dead_for == 0:
            self.generate_death_event()
        
        elif game.clan.your_cat.status == 'exiled':
            self.generate_exile_event()
            
        game.clan.murdered = False
        
        self.check_achievements()
        self.checks = [len(game.clan.your_cat.apprentice), len(game.clan.your_cat.mate), len(game.clan.your_cat.inheritance.get_blood_kits())]

            
        # Resort
        if game.sort_type != "id":
            Cat.sort_cats()

        # Clear all the loaded event dicts.
        Events.generate_events.clear_loaded_events()

        # autosave
        if game.settings.get('autosave') is True and game.clan.age % 5 == 0:
            try:
                game.save_cats()
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_events()
            except:
                SaveError(traceback.format_exc())
                
    def gain_acc(self):
        possible_accs = ["WILD", "PLANT", "COLLAR", "FLOWER", "PLANT2", "SNAKE", "SMALLANIMAL", "DEADINSECT", "ALIVEINSECT", "FRUIT", "CRAFTED", "TAIL2"]
        acc_list = []
        if "WILD" in possible_accs:
            acc_list.extend(Pelt.wild_accessories)
        if "PLANT" in possible_accs:
            acc_list.extend(Pelt.plant_accessories)
        if "COLLAR" in possible_accs:
            acc_list.extend(Pelt.collars)
        if "FLOWER" in possible_accs:
            acc_list.extend(Pelt.flower_accessories)
        if "PLANT2" in possible_accs:
            acc_list.extend(Pelt.plant2_accessories)
        if "SNAKE" in possible_accs:
            acc_list.extend(Pelt.snake_accessories)
        if "SMALLANIMAL" in possible_accs:
            acc_list.extend(Pelt.smallAnimal_accessories)
        if "DEADINSECT" in possible_accs:
            acc_list.extend(Pelt.deadInsect_accessories)
        if "ALIVEINSECT" in possible_accs:
            acc_list.extend(Pelt.aliveInsect_accessories)
        if "FRUIT" in possible_accs:
            acc_list.extend(Pelt.fruit_accessories)
        if "CRAFTED" in possible_accs:
            acc_list.extend(Pelt.crafted_accessories)
        if "TAIL2" in possible_accs:
            acc_list.extend(Pelt.tail2_accessories)
        if "NOTAIL" in game.clan.your_cat.pelt.scars or "HALFTAIL" in game.clan.your_cat.pelt.scars:
            for acc in Pelt.tail_accessories + Pelt.tail2_accessories:
                if acc in acc_list:
                    try:
                        acc_list.remove(acc)
                    except ValueError:
                        print(f'attempted to remove {acc} from possible acc list, but it was not in the list!')

        if not game.clan.your_cat.inventory:
            game.clan.your_cat.inventory = []
        acc = random.choice(acc_list)
        while acc in game.clan.your_cat.inventory:
            acc = random.choice(acc_list)
        game.clan.your_cat.inventory.append(acc)
        string = f"You found a new accessory, {self.accessory_display_name(acc)}! You choose to store it in a safe place for now."
        game.cur_events_list.insert(0, Single_Event(string, "health"))

    def accessory_display_name(self, accessory):
        if accessory is None:
            return ''
        acc_display = accessory.lower()

        if accessory in Pelt.collars:
            collar_colors = {'crimson': 'red', 'blue': 'blue', 'yellow': 'yellow', 'cyan': 'cyan',
                            'red': 'orange', 'lime': 'lime', 'green': 'green', 'rainbow': 'rainbow',
                            'black': 'black', 'spikes': 'spiky', 'white': 'white', 'pink': 'pink',
                            'purple': 'purple', 'multi': 'multi', 'indigo': 'indigo'}
            collar_color = next((color for color in collar_colors if acc_display.startswith(color)), None)

            if collar_color:
                if acc_display.endswith('bow') and not collar_color == 'rainbow':
                    acc_display = collar_colors[collar_color] + ' bow'
                elif acc_display.endswith('bell'):
                    acc_display = collar_colors[collar_color] + ' bell collar'
                else:
                    acc_display = collar_colors[collar_color] + ' collar'

        elif accessory in Pelt.wild_accessories:
            if acc_display == 'blue feathers':
                acc_display = 'crow feathers'
            elif acc_display == 'red feathers':
                acc_display = 'cardinal feathers'

        return acc_display

    
    def check_achievements(self):
        you = game.clan.your_cat
        achievements = set()
        murder_history = History.get_murders(you)
        clan_cats = game.clan.clan_cats
        if murder_history:
            if 'is_murderer' in murder_history:
                num_victims = len(murder_history["is_murderer"])
                if num_victims >= 0:
                    achievements.add("1")
                if num_victims >= 5:
                    achievements.add("2")
                if num_victims >= 20:
                    achievements.add("3")
                if num_victims >= 50:
                    achievements.add("4")
        for cat in clan_cats:
            if Cat.all_cats.get(cat).pelt.tortiebase and Cat.all_cats.get(cat).gender == 'male':
                achievements.add("5")
        
        if you.joined_df:
            achievements.add("7")
        
        if len(you.former_apprentices) >= 1:
            achievements.add("8")
        if len(you.former_apprentices) >= 5:
            achievements.add("9")
        
        if you.inheritance.get_kits():
            achievements.add("10")
        for i in you.relationships.keys():
            if you.relationships.get(i).dislike >= 60:
                achievements.add("11")
            if you.relationships.get(i).romantic_love >= 60:
                achievements.add('12')
            
        if len(you.mate) >= 5:
            achievements.add('13')
        if you.status == 'warrior':
            achievements.add('14')
        elif you.status == 'medicine cat':
            achievements.add('15')
        elif you.status == 'mediator':
            achievements.add('16')
        elif you.status == 'deputy':
            achievements.add('17')
        elif you.status == 'leader':
            achievements.add('18')
        elif you.status == 'elder':
            achievements.add('19')
        
        if you.moons >= 200:
            achievements.add('20')
        if you.exiled:
            achievements.add('21')
        elif you.outside:
            achievements.add('22')
        
        if len(clan_cats) == 1 and not you.dead:
            achievements.add('23')
        
        for i in game.clan.achievements:
            achievements.add(i)
        
        game.clan.achievements = list(achievements)
                
    def pick_valid_parent(self):
        parent = random.choice(Cat.all_cats_list).ID
        while parent == game.clan.your_cat.ID or Cat.all_cats[parent].moons < 14 or Cat.all_cats[parent].moons > 100 or Cat.all_cats[parent].dead:
            parent = random.choice(Cat.all_cats_list).ID
        return parent
        

    def set_birth_text(self, birth_key, replacements):
        birth_txt = random.choice(self.b_txt[birth_key])
        for key, value in replacements.items():
            birth_txt = birth_txt.replace(key, str(value))
        return birth_txt

    def create_inheritance(self, parent_ids):
        for parent_id in parent_ids:
            parent_cat = Cat.all_cats[parent_id]
            parent_cat.create_inheritance_new_cat()
        game.clan.your_cat.create_inheritance_new_cat()
        game.clan.your_cat.init_all_relationships()

    def create_sibling(self):
        sibling = Cat(status='newborn', moons=0)
        sibling.thought = "Snuggles up to you"
        sibling.backstory = game.clan.your_cat.backstory
        game.clan.add_cat(sibling)
        return sibling

    def create_siblings(self, num_siblings):
        siblings = [self.create_sibling() for _ in range(num_siblings)]
        sibling_names = [str(sibling.name) for sibling in siblings]
        sibling_text = ""
        if num_siblings == 1:
            sibling_text = sibling_names[0]
        elif num_siblings == 2:
            sibling_text = ' and '.join(sibling_names)
        elif num_siblings == 3:
            sibling_text = f"{siblings[0].name}, {siblings[1].name}, and {siblings[2].name}"
        
        return siblings, sibling_text

    def get_birth_txt(self):
        num_siblings = random.choice([0,1,2,3])
        siblings, sibling_text = self.create_siblings(num_siblings)
        birth_type = random.randint(1,6)
        if birth_type == 1:
            game.clan.your_cat.backstory = random.choice(["abandoned1", "abandoned2", "abandoned3", "abandoned4", "orphaned1", "orphaned2", "orphaned3", "orphaned4", "orphaned5", "orphaned6"])
            return self.handle_birth_no_parents(siblings, sibling_text)
        elif birth_type in [2, 3, 4]:
            if birth_type == 2:
                game.clan.your_cat.backstory = random.choice(["halfclan1", "clanborn", "outsider_roots1"])
            else:
                game.clan.your_cat.backstory = "clanborn"
            return self.handle_birth_one_or_two_parents(birth_type, siblings, sibling_text)
        else:
            game.clan.your_cat.backstory = random.choice(["abandoned1", "abandoned2", "abandoned3", "abandoned4", "orphaned1", "orphaned2", "orphaned3", "orphaned4", "orphaned5", "orphaned6"])
            return self.handle_birth_adoptive_parents(siblings, sibling_text)

    def handle_birth_no_parents(self, siblings, sibling_text):
        thought = "Is happy their kits are safe"
        blood_parent = create_new_cat(Cat, Relationship,
                                        status='warrior',
                                        alive=True,
                                        thought=thought,
                                        age=random.randint(15,120),
                                        backstory=random.choice(["kittypet1", "kittypet2", "kittypet3", "kittypet4", "refugee3", "loner1", "loner2", "tragedy_survivor3", "guided1", "rogue1", "rogue2", "rogue3", "refugee4", "tragedy_survivor2", "guided2", "refugee5"]))[0]
        if random.randint(1,2) == 1 and not siblings:
            game.clan.add_to_clan(blood_parent)
            game.clan.your_cat.parent1 = blood_parent.ID
            game.clan.your_cat.create_inheritance_new_cat()
            game.clan.your_cat.init_all_relationships()
            blood_parent.create_inheritance_new_cat()
            game.clan.your_cat.backstory = "outsider_roots2"
            return self.set_birth_text("birth_parent_outsider", {"y_c": game.clan.your_cat.name, "parent1": blood_parent.name})
        else:
            blood_parent.outside = True
            game.clan.add_to_unknown(blood_parent)
        if siblings:
            self.add_siblings_and_inheritance(siblings, blood_parent=blood_parent)
            return self.set_birth_text("birth_no_parents_siblings", {"y_c": game.clan.your_cat.name, "insert_siblings": sibling_text})
        else:
            game.clan.your_cat.parent1 = blood_parent.ID
            game.clan.your_cat.create_inheritance_new_cat()
            game.clan.your_cat.init_all_relationships()
            blood_parent.create_inheritance_new_cat()
        return self.set_birth_text("birth_no_parents", {"y_c": game.clan.your_cat.name})

    def handle_birth_one_or_two_parents(self, birth_type, siblings, sibling_text):
        game.clan.your_cat.parent1 = self.pick_valid_parent()
        if birth_type == 2:
            return self.handle_birth_one_parent(siblings, sibling_text)
        else:
            game.clan.your_cat.parent2 = self.pick_valid_parent()
            counter = 0
            while game.clan.your_cat.parent1 == game.clan.your_cat.parent2 or Cat.all_cats[game.clan.your_cat.parent1].age != Cat.all_cats[game.clan.your_cat.parent2].age:
                counter+=1
                if counter > 15:
                    game.clan.your_cat.parent2 = None
                    return self.handle_birth_one_parent(siblings, sibling_text)
                game.clan.your_cat.parent2 = self.pick_valid_parent()
            
            return self.handle_birth_two_parents(siblings, sibling_text)

    def handle_birth_one_parent(self, siblings, sibling_text):
        if siblings:
            self.add_siblings_and_inheritance(siblings, game.clan.your_cat.parent1)
            return self.set_birth_text("birth_one_parent_siblings", {"parent1": Cat.all_cats[game.clan.your_cat.parent1].name, "y_c": game.clan.your_cat.name,"insert_siblings": sibling_text})
        self.create_inheritance([game.clan.your_cat.parent1])
        return self.set_birth_text("birth_one_parent", {"parent1": Cat.all_cats[game.clan.your_cat.parent1].name, "y_c": game.clan.your_cat.name})

    def handle_birth_two_parents(self, siblings, sibling_text):
        Cat.all_cats[game.clan.your_cat.parent1].set_mate(Cat.all_cats[game.clan.your_cat.parent2])
        Cat.all_cats[game.clan.your_cat.parent2].set_mate(Cat.all_cats[game.clan.your_cat.parent1])
        if siblings:
            self.add_siblings_and_inheritance(siblings, game.clan.your_cat.parent1, game.clan.your_cat.parent2)
            return self.set_birth_text("birth_two_parents_siblings", {"parent1": Cat.all_cats[game.clan.your_cat.parent1].name, "parent2": Cat.all_cats[game.clan.your_cat.parent2].name, "y_c": game.clan.your_cat.name,"insert_siblings": sibling_text})
        replacements = {"parent1": Cat.all_cats[game.clan.your_cat.parent1].name, "parent2": Cat.all_cats[game.clan.your_cat.parent2].name, "y_c": game.clan.your_cat.name}
        self.create_inheritance([game.clan.your_cat.parent1, game.clan.your_cat.parent2])
        return self.set_birth_text("birth_two_parents", replacements)

    def handle_birth_adoptive_parents(self, siblings, sibling_text):
        thought = "Is happy their kits are safe"
        blood_parent = create_new_cat(Cat, Relationship,
                                        status=random.choice(["loner", "kittypet"]),
                                        alive=False,
                                        thought=thought,
                                        age=random.randint(15,120))[0]
        blood_parent.outside = True
        game.clan.add_to_unknown(blood_parent)
        parent1, parent2 = self.pick_valid_parent(), self.pick_valid_parent()
        while parent2 == parent1:
            parent2 = self.pick_valid_parent()
        Cat.all_cats[parent1].set_mate(Cat.all_cats[parent2])
        Cat.all_cats[parent2].set_mate(Cat.all_cats[parent1])
        game.clan.your_cat.adoptive_parents.extend([parent1,parent2])
        game.clan.your_cat.parent1 = blood_parent.ID
        if siblings:
            for i in siblings:
                i.adoptive_parents.extend([parent1,parent2])
                i.parent1 = blood_parent.ID
                i.create_inheritance_new_cat()
                i.init_all_relationships()
                game.clan.your_cat.create_inheritance_new_cat()
                game.clan.your_cat.init_all_relationships()
                if parent1:
                    Cat.all_cats[parent1].create_inheritance_new_cat()
                if parent2:
                    Cat.all_cats[parent2].create_inheritance_new_cat()
            blood_parent.create_inheritance_new_cat()
            return self.set_birth_text("birth_adoptive_parents_siblings", {"parent1": Cat.all_cats[parent1].name, "parent2": Cat.all_cats[parent2].name, "y_c": game.clan.your_cat.name,"insert_siblings": sibling_text})
        self.create_inheritance([parent1, parent2])
        blood_parent.create_inheritance_new_cat()
        return self.set_birth_text("birth_adoptive_parents", {"parent1": Cat.all_cats[parent1].name, "parent2": Cat.all_cats[parent2].name, "y_c": game.clan.your_cat.name})

    def add_siblings_and_inheritance(self, siblings, parent1=None, parent2=None, blood_parent=None):
        if blood_parent:
            game.clan.your_cat.parent1 = blood_parent.ID
        for sibling in siblings:
            if parent1: sibling.parent1 = parent1
            if parent2: sibling.parent2 = parent2
            if blood_parent: sibling.parent1 = blood_parent.ID
            sibling.create_inheritance_new_cat()
            sibling.init_all_relationships()
            sibling.backstory = game.clan.your_cat.backstory
        game.clan.your_cat.create_inheritance_new_cat()
        game.clan.your_cat.init_all_relationships()
        if blood_parent:
            blood_parent.create_inheritance_new_cat()
        if parent1:
            Cat.all_cats[parent1].create_inheritance_new_cat()
        if parent2:
            Cat.all_cats[parent2].create_inheritance_new_cat()
            
    def generate_birth(self):
        birth_txt = self.get_birth_txt()
        game.cur_events_list.append(Single_Event(birth_txt))
        self.w_done = False
            
    def generate_kit_events(self):
        for i in range(random.randint(0,2)):
            kit_event = Single_Event(random.choice(self.c_txt["kitten"]))
            if kit_event not in game.cur_events_list:
                game.cur_events_list.append(kit_event)
        if game.clan.your_cat.parent1:
            moons_list = range(2, 6)
            parents_txt = {1: "one_parent", 2: "two_parents"}
            for moons in moons_list:
                if game.clan.your_cat.moons == moons:
                    for parents in parents_txt.keys():
                        if (game.clan.your_cat.parent1 and not game.clan.your_cat.parent2 and not Cat.all_cats[game.clan.your_cat.parent1].dead and not Cat.all_cats[game.clan.your_cat.parent1].outside) or \
                        (parents == 2 and game.clan.your_cat.parent1 and game.clan.your_cat.parent2 and not Cat.all_cats[game.clan.your_cat.parent1].dead and not Cat.all_cats[game.clan.your_cat.parent1].outside and not Cat.all_cats[game.clan.your_cat.parent2].dead and not Cat.all_cats[game.clan.your_cat.parent2].outside):
                            kit_event1 = random.choice(self.c_txt[f"moon_{moons}_{parents_txt[parents]}"])
                            if game.clan.your_cat.parent1:
                                kit_event1 = kit_event1.replace("parent1", str(Cat.all_cats[game.clan.your_cat.parent1].name))
                            if game.clan.your_cat.parent2:
                                kit_event1 = kit_event1.replace("parent2", str(Cat.all_cats[game.clan.your_cat.parent2].name))

                            kit_event = Single_Event(kit_event1)
                            
                            if kit_event not in game.cur_events_list:
                                game.cur_events_list.append(kit_event)
                            break

    def generate_app_ceremony(self):
        game.clan.your_cat.status_change(game.clan.your_cat.status)
        ceremony_txt = ""
        if game.clan.your_cat.mentor:
            ceremony_txt = random.choice(self.b_txt[game.clan.your_cat.status + ' ceremony'])
        else:
            ceremony_txt = random.choice(self.b_txt[game.clan.your_cat.status + ' ceremony no mentor'])
        ceremony_txt = ceremony_txt.replace('c_n', str(game.clan.name))
        ceremony_txt = ceremony_txt.replace('y_c', str(game.clan.your_cat.name))
        ceremony_txt = ceremony_txt.replace('c_l', str(game.clan.leader.name))
        if game.clan.your_cat.mentor:
            ceremony_txt = ceremony_txt.replace('m_n', str(Cat.all_cats[game.clan.your_cat.mentor].name))
        game.cur_events_list.append(Single_Event(ceremony_txt))
        
    def generate_app_events(self):
        for i in range(random.randint(0,5)):
            e_txt = random.choice(self.c_txt[game.clan.your_cat.status])
            if not game.clan.your_cat.mentor:
                while "mentor" in e_txt or "mentor1" in e_txt:
                    e_txt = random.choice(self.c_txt[game.clan.your_cat.status])
            else:
                e_txt = e_txt.replace('mentor1', str(Cat.all_cats[game.clan.your_cat.mentor].name))
            if Single_Event(e_txt) not in game.cur_events_list:
                game.cur_events_list.append(Single_Event(e_txt))
                
    def generate_ceremony(self):
        if game.clan.your_cat.former_mentor:
            if Cat.all_cats[game.clan.your_cat.former_mentor[-1]].dead and game.clan.your_cat.status == 'medicine cat':
                ceremony_txt = random.choice(self.b_txt[game.clan.your_cat.status + '_ceremony_no_mentor'])
            ceremony_txt = random.choice(self.b_txt[game.clan.your_cat.status + '_ceremony'])
            ceremony_txt = ceremony_txt.replace('m_n', str(Cat.all_cats[game.clan.your_cat.former_mentor[-1]].name))
        else:
            ceremony_txt = random.choice(self.b_txt[game.clan.your_cat.status + '_ceremony_no_mentor'])
        
        ceremony_txt = ceremony_txt.replace('c_n', str(game.clan.name))
        ceremony_txt = ceremony_txt.replace('y_c', str(game.clan.your_cat.name))
        ceremony_txt = ceremony_txt.replace('c_l', str(game.clan.leader.name))

        random_honor = None
        resource_dir = "resources/dicts/events/ceremonies/"
        with open(f"{resource_dir}ceremony_traits.json",
                encoding="ascii") as read_file:
            TRAITS = ujson.loads(read_file.read())
        try:
            random_honor = random.choice(TRAITS[game.clan.your_cat.personality.trait])
        except KeyError:
            random_honor = "hard work"
        ceremony_txt = ceremony_txt.replace('honor1', random_honor)
        game.cur_events_list.insert(0, Single_Event(ceremony_txt))
        game.clan.your_cat.w_done = True
        
    def generate_events_adult(self):
        for i in range(random.randint(0,5)):
            evt = Single_Event(random.choice(self.c_txt[game.clan.your_cat.status]))
            if evt not in game.cur_events_list:
                game.cur_events_list.append(evt)
        
    def generate_elder_ceremony(self):
        ceremony_txt = random.choice(self.b_txt['elder_ceremony'])
        ceremony_txt = ceremony_txt.replace('c_n', str(game.clan.name))
        ceremony_txt = ceremony_txt.replace('y_c', str(game.clan.your_cat.name))
        ceremony_txt = ceremony_txt.replace('c_l', str(game.clan.leader.name))
        game.cur_events_list.append(Single_Event(ceremony_txt))
    
    def generate_elder_events(self):
        if game.clan.your_cat.moons < 100:
            evt = Single_Event(random.choice(self.c_txt["young_elder"]))
            if evt not in game.cur_events_list:
                game.cur_events_list.append(evt)
        else:
            for i in range(random.randint(0,5)):
                evt = Single_Event(random.choice(self.c_txt["elder"]))
                if evt not in game.cur_events_list:
                    game.cur_events_list.append(evt)
        
    
    def check_gain_app(self, checks):
        if len(game.clan.your_cat.apprentice) == checks[0] + 1:
            if 'request apprentice' in game.switches:
                game.switches['request apprentice'] = False
            resource_dir = "resources/dicts/events/lifegen_events/"
            with open(f"{resource_dir}ceremonies.json",
                    encoding="ascii") as read_file:
                self.d_txt = ujson.loads(read_file.read())
            ceremony_txt = random.choice(self.d_txt['gain_app ' + game.clan.your_cat.status])
            ceremony_txt = ceremony_txt.replace('c_l', str(game.clan.leader.name))
            ceremony_txt = ceremony_txt.replace('app1', str(Cat.all_cats[game.clan.your_cat.apprentice[-1]].name))
            game.cur_events_list.insert(0, Single_Event(ceremony_txt))

    def check_gain_mate(self, checks):
        
        if len(game.clan.your_cat.mate) == checks[1] + 1:
            try:
                resource_dir = "resources/dicts/events/lifegen_events/"
                with open(f"{resource_dir}ceremonies.json",
                        encoding="ascii") as read_file:
                    self.d_txt = ujson.loads(read_file.read())
                try:
                    ceremony_txt = random.choice(self.d_txt["gain_mate " + game.clan.your_cat.status.replace(" ", "") + " " + Cat.all_cats[game.clan.your_cat.mate[-1]].status.replace(" ", "")])
                except:
                    ceremony_txt = random.choice(self.d_txt["gain_mate general"])

                ceremony_txt = ceremony_txt.replace('mate1', str(Cat.all_cats[game.clan.your_cat.mate[-1]].name))
                game.cur_events_list.insert(0, Single_Event(ceremony_txt))
            except:
                print("You gained a new mate but an event could not be shown1")
        elif 'accept' in game.switches and game.switches['accept']:
            try:
                resource_dir = "resources/dicts/events/lifegen_events/"
                with open(f"{resource_dir}ceremonies.json",
                        encoding="ascii") as read_file:
                    self.d_txt = ujson.loads(read_file.read())
                try:
                    ceremony_txt = random.choice(self.d_txt["gain_mate " + game.clan.your_cat.status.replace(" ", "") + " " + Cat.all_cats[game.clan.your_cat.mate[-1]].status.replace(" ", "")])
                except:
                    ceremony_txt = random.choice(self.d_txt["gain_mate general"])

                ceremony_txt = ceremony_txt.replace('mate1', str(Cat.all_cats[game.clan.your_cat.mate[-1]].name))
                game.cur_events_list.insert(0, Single_Event(ceremony_txt))
                game.switches['accept'] = False
                checks[1] = len(game.clan.your_cat.mate)
            except:
                print("You gained a new mate but an event could not be shown1")

        elif 'reject' in game.switches and game.switches['reject']:
            try:
                resource_dir = "resources/dicts/events/lifegen_events/"
                with open(f"{resource_dir}mate_lifegen.json",
                        encoding="ascii") as read_file:
                    self.f_txt = ujson.loads(read_file.read())
                r = random.randint(1,3)
                if r == 1:
                    game.switches['new_mate'].relationships[game.clan.your_cat.ID].romantic_love -= 8
                elif r == 2:
                    game.switches['new_mate'].relationships[game.clan.your_cat.ID].romantic_love -= 8
                    game.switches['new_mate'].relationships[game.clan.your_cat.ID].platonic_like -= 8
                    game.clan.your_cat.relationships[game.switches['new_mate'].ID].comfortable -= 5
                elif r == 3:
                    game.switches['new_mate'].relationships[game.clan.your_cat.ID].romantic_love -= 5
                    game.switches['new_mate'].relationships[game.clan.your_cat.ID].platonic_like -= 10
                    game.clan.your_cat.relationships[game.switches['new_mate'].ID].platonic_like -= 10
                    game.clan.your_cat.relationships[game.switches['new_mate'].ID].dislike += 10

                ceremony_txt = random.choice(self.f_txt['reject' + str(r)])
                ceremony_txt = ceremony_txt.replace('mate1', str(game.switches['new_mate'].name))
                game.cur_events_list.insert(0, Single_Event(ceremony_txt))
                game.switches['reject'] = False
            except:
                print("You rejected a cat but an event could not be shown")
            
    def check_gain_kits(self, checks):
        if len(game.clan.your_cat.inheritance.get_blood_kits()) > checks[2]:
            insert_kits = []
            for kit in game.clan.your_cat.inheritance.get_blood_kits():
                kit_cat = Cat.all_cats.get(kit)
                if kit_cat.moons == 0:
                    insert_kits.append(str(kit_cat.name))
            resource_dir = "resources/dicts/events/lifegen_events/"
            with open(f"{resource_dir}ceremonies.json",
                    encoding="ascii") as read_file:
                self.z_txt = ujson.loads(read_file.read())
            mate_status = "no mate"
            if len(game.clan.your_cat.mate) == 1:
                mate_status = "mate"
            elif len(game.clan.your_cat.mate) > 1:
                mate_status = "mates"
            
            ceremony_txt = random.choice(self.z_txt['have_kits ' + mate_status])
            kit_names = ""
            if len(insert_kits) == 1:
                kit_names = insert_kits[0]
            elif len(insert_kits) == 2:
                kit_names = insert_kits[0] + " and " + insert_kits[1]
            else:
                for i in range(len(insert_kits)):
                    if i == len(insert_kits) - 1:
                        kit_names += "and " + insert_kits[i]
                    else:
                        kit_names += insert_kits[i] + ", "
            ceremony_txt = ceremony_txt.replace('insert_kits', kit_names)
            game.cur_events_list.insert(0, Single_Event(ceremony_txt))

    def generate_mate_events(self):
        if len(game.clan.your_cat.mate) > 0:
            if random.randint(1,20) == 1:
                mate1 = Cat.all_cats.get(random.choice(game.clan.your_cat.mate))
                if mate1.dead or mate1.outside:
                    return
                ceremony_txt = random.choice(self.c_txt['mate_events'])
                ceremony_txt = ceremony_txt.replace("mate1", str(mate1.name))
                game.cur_events_list.insert(1, Single_Event(ceremony_txt))
            if game.settings['affair']:
                if random.randint(1,50) == 1:
                    mate1 = Cat.all_cats.get(random.choice(game.clan.your_cat.mate))
                    if mate1.dead or mate1.outside:
                        return
                    ceremony_txt = random.choice(self.c_txt['affair_events'])
                    ceremony_txt = ceremony_txt.replace("mate1", str(mate1.name))
                    game.cur_events_list.insert(1, Single_Event(ceremony_txt))
        if random.randint(1,30) == 1:
            if (len(game.clan.your_cat.mate) > 0 and game.settings['affair']) or (len(game.clan.your_cat.mate) == 0):
                if len(game.clan.your_cat.mate) > 0:
                    if random.randint(1,50) != 1:
                        return
                    mate1 = Cat.all_cats.get(random.choice(game.clan.your_cat.mate))
                    if mate1.dead or mate1.outside:
                        return
                c = Cat.all_cats.get(random.choice(game.clan.clan_cats))
                counter = 0
                while not c.relationships.get(game.clan.your_cat.ID) or c.relationships.get(game.clan.your_cat.ID).romantic_love < 10:
                    if counter == 15:
                        return
                    c = Cat.all_cats.get(random.choice(game.clan.clan_cats))
                    counter+=1
                ceremony_txt = random.choice(self.c_txt['crush_events'])
                ceremony_txt = ceremony_txt.replace("crush1", str(c.name))
                game.cur_events_list.insert(1, Single_Event(ceremony_txt))
                
    def check_retire(self):
        if 'retire' in game.switches:
            if game.switches['retire']:
                
                game.switches['retire'] = False
        if 'retire_reject' in game.switches:
            if game.switches['retire_reject']:
                
                game.switches['retire_reject'] = False
    
    def generate_death_event(self):
        if game.clan.your_cat.status == 'kitten':
            ceremony_txt = random.choice(self.b_txt['death_kit'])
            game.cur_events_list.insert(1, Single_Event(ceremony_txt))
        elif game.clan.your_cat.status == 'medicine cat apprentice':
            ceremony_txt = random.choice(self.b_txt['death_medapp'])
            game.cur_events_list.insert(1, Single_Event(ceremony_txt))
        elif game.clan.your_cat.status == 'apprentice':
            ceremony_txt = random.choice(self.b_txt['death_app'])
            game.cur_events_list.insert(1, Single_Event(ceremony_txt))
        elif game.clan.your_cat.status == 'mediator apprentice':
            ceremony_txt = random.choice(self.b_txt['death_mediapp'])
            game.cur_events_list.insert(1, Single_Event(ceremony_txt))
        elif game.clan.your_cat.status == 'elder':
            ceremony_txt = random.choice(self.b_txt['death_elder'])
            game.cur_events_list.insert(1, Single_Event(ceremony_txt))
        else:
            ceremony_txt = random.choice(self.b_txt['death'])
            game.cur_events_list.insert(1, Single_Event(ceremony_txt))
            
    def generate_exile_event(self):
        evt = Single_Event(random.choice(self.c_txt["exiled"]))
        if evt not in game.cur_events_list:
            game.cur_events_list.append(evt)
            
    def generate_df_events(self):
        if random.randint(1,3) == 1:
            evt = Single_Event(random.choice(self.df_txt["general"]))
            if evt not in game.cur_events_list:
                game.cur_events_list.append(evt)
        if random.randint(1,30) == 1:
            r_clanmate = Cat.all_cats.get(random.choice(game.clan.clan_cats))
            counter = 0
            while r_clanmate.dead or r_clanmate.outside or r_clanmate.status in ['kitten', 'newborn', 'deputy', 'leader'] or r_clanmate.joined_df or r_clanmate.ID == game.clan.your_cat.ID:
                counter+=1
                if counter > 15:
                    return
                r_clanmate = Cat.all_cats.get(random.choice(game.clan.clan_cats))
            
            r_clanmate.joined_df = True
            evt_txt = random.choice(self.df_txt["clanmate"]).replace("c_m", str(r_clanmate.name))
            evt = Single_Event(evt_txt)
            if evt not in game.cur_events_list:
                game.cur_events_list.append(evt)

    def mediator_events(self, cat):
        """ Check for mediator events """
        # If the cat is a mediator, check if they visited other clans
        if cat.status in ["mediator", "mediator apprentice"] and not cat.not_working():
            # 1 /10 chance
            if not int(random.random() * 10):
                increase = random.randint(-2, 6)
                clan = random.choice(game.clan.all_clans)
                clan.relations += increase
                dispute_type = random.choice(
                    ["hunting", "border", "personal", "herb-gathering"])
                text = f"{cat.name} travels to {clan} to " \
                       f"resolve some recent {dispute_type} disputes. "
                if increase > 4:
                    text += f"The meeting goes better than expected, and " \
                            f"{cat.name} returns with a plan to solve the " \
                            f"issue for good."
                elif increase == 0:
                    text += "However, no progress was made."
                elif increase < 0:
                    text += f"However, it seems {cat.name} only made {clan} more upset."

                game.cur_events_list.append(
                    Single_Event(text, "other_clans", cat.ID))

        if game.settings['become_mediator']:
            # Note: These chances are large since it triggers every moon.
            # Checking every moon has the effect giving older cats more chances to become a mediator
            _ = game.config["roles"]["become_mediator_chances"]
            if cat.status in _ and \
                    not int(random.random() * _[cat.status]):
                game.cur_events_list.append(
                    Single_Event(
                        f"{cat.name} had chosen to use their skills and experience to help "
                        f"solve the Clan's disagreements. A meeting is called, and they "
                        f"become the Clan's newest mediator. ", "ceremony",
                        cat.ID))
                cat.status_change("mediator")

    def get_moon_freshkill(self):
        """Adding auto freshkill for the current moon."""
        healthy_hunter = list(
            filter(
                lambda c: c.status in
                          ['warrior', 'apprentice', 'leader', 'deputy'] and not c.dead
                          and not c.outside and not c.exiled and not c.not_working(),
                Cat.all_cats.values()))

        prey_amount = 0
        for cat in healthy_hunter:
            lower_value = game.config["freshkill"]["auto_warrior_prey"][0]
            upper_value = game.config["freshkill"]["auto_warrior_prey"][1]
            if cat.status == "apprentice":
                lower_value = game.config["freshkill"]["auto_apprentice_prey"][
                    0]
                upper_value = game.config["freshkill"]["auto_apprentice_prey"][
                    1]

            prey_amount += random.randint(lower_value, upper_value)
        if FRESHKILL_ACTIVE:
            print(f" -- FRESHKILL: added {prey_amount} monthly prey")
        game.clan.freshkill_pile.add_freshkill(prey_amount)

    def herb_gather(self):
        """
        TODO: DOCS
        """
        if game.clan.game_mode == 'classic':
            herbs = game.clan.herbs.copy()
            for herb in herbs:
                adjust_by = random.choices([-2, -1, 0, 1, 2], [1, 2, 3, 2, 1],
                                           k=1)
                game.clan.herbs[herb] += adjust_by[0]
                if game.clan.herbs[herb] <= 0:
                    game.clan.herbs.pop(herb)
            if not int(random.random() * 5):
                new_herb = random.choice(HERBS)
                game.clan.herbs.update({new_herb: 1})
        else:
            event_list = []
            meds_available = get_med_cats(Cat)
            for med in meds_available:
                if game.clan.current_season in ['Newleaf', 'Greenleaf']:
                    amount = random.choices([0, 1, 2, 3], [1, 2, 2, 2], k=1)
                elif game.clan.current_season == 'Leaf-fall':
                    amount = random.choices([0, 1, 2], [3, 2, 1], k=1)
                else:
                    amount = random.choices([0, 1], [3, 1], k=1)
                if amount[0] != 0:
                    herbs_found = random.sample(HERBS, k=amount[0])
                    herb_display = []
                    for herb in herbs_found:
                        if herb in ['blackberry']:
                            continue
                        if game.clan.current_season in [
                            'Newleaf', 'Greenleaf'
                        ]:
                            amount = random.choices([1, 2, 3], [3, 3, 1], k=1)
                        else:
                            amount = random.choices([1, 2], [4, 1], k=1)
                        if herb in game.clan.herbs:
                            game.clan.herbs[herb] += amount[0]
                        else:
                            game.clan.herbs.update({herb: amount[0]})
                        herb_display.append(herb.replace("_", " "))
                else:
                    herbs_found = []
                    herb_display = []
                if not herbs_found:
                    event_list.append(
                        f"{med.name} could not find any herbs this moon.")
                else:
                    try:
                        if len(herbs_found) == 1:
                            insert = f"{herb_display[0]}"
                        elif len(herbs_found) == 2:
                            insert = f"{herb_display[0]} and {herb_display[1]}"
                        else:
                            insert = f"{', '.join(herb_display[:-1])}, and {herb_display[-1]}"
                        event_list.append(
                            f"{med.name} gathered {insert} this moon.")
                    except IndexError:
                        event_list.append(
                            f"{med.name} could not find any herbs this moon.")
                        return
            game.herb_events_list.extend(event_list)

    def herb_destruction(self):
        """
        TODO: DOCS
        """
        allies = []
        for clan in game.clan.all_clans:
            if clan.relations > 17:
                allies.append(clan)

        meds = get_med_cats(Cat, working=False)
        if len(meds) == 1:
            insert = "medicine cat"
        else:
            insert = "medicine cats"
        # herbs = game.clan.herbs

        herbs_lost = []

        # trying to fix consider-using-dict-items makes my brain hurt
        for herb in game.clan.herbs:  # pylint: disable=consider-using-dict-items
            if game.clan.herbs[herb] > 25:
                game.clan.herbs[herb] = 25
                herbs_lost.append(herb)

        if herbs_lost:
            if len(herbs_lost) == 1 and herbs_lost[0] != 'cobwebs':
                insert2 = f"much {herbs_lost[0]}"
            elif len(herbs_lost) == 1 and herbs_lost[0] == 'cobwebs':
                insert2 = f"many {herbs_lost[0]}"
            elif len(herbs_lost) == 2:
                insert2 = f"much {herbs_lost[0]} and {herbs_lost[1]}"
            else:
                insert2 = f"much {', '.join(herbs_lost[:-1])}, and {herbs_lost[-1]}"
            text = f"The herb stores have too {insert2}. The excess is given back to the earth."
            game.herb_events_list.append(text)

        if sum(game.clan.herbs.values()) >= 50:
            chance = 2
        else:
            chance = 5

        if len(game.clan.herbs.keys()) >= 10 and not int(
                random.random() * chance):
            bad_herb = random.choice(list(game.clan.herbs.keys()))

            # Failsafe, since I have no idea why we are getting 0-herb entries.
            while game.clan.herbs[bad_herb] <= 0:
                print(
                    f"Warning: {bad_herb} was chosen to destroy, although you currently have "
                    f"{game.clan.herbs[bad_herb]}. Removing {bad_herb}"
                    f"from herb dict, finding a new herb..."
                )
                game.clan.herbs.pop(bad_herb)
                if game.clan.herbs:
                    bad_herb = random.choice(list(game.clan.herbs.keys()))
                else:
                    print("No herbs to destroy")
                    return
                print(f"New herb found: {bad_herb}")

            herb_amount = random.randrange(1, game.clan.herbs[bad_herb] + 1)
            # deplete the herb
            game.clan.herbs[bad_herb] -= herb_amount
            insert2 = 'some of'
            if game.clan.herbs[bad_herb] <= 0:
                game.clan.herbs.pop(bad_herb)
                insert2 = "all of"

            event = f"As the herb stores are inspected by the {insert}, it's noticed " \
                    f"that {insert2} the {bad_herb.replace('_', ' ')}" \
                    f" went bad. They'll have to be replaced with new ones. "
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif allies and not int(random.random() * 5):
            chosen_ally = random.choice(allies)
            if not game.clan.herbs:
                # If you have no herbs, you can't give any to a clan. Special events for that.
                possible_events = [
                    # pylint: disable=line-too-long
                    f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any herbs to spare. "
                    f"Unfortunately, your stocks are bare, and you are unable to provide any help. ",
                    f"A medicine cat from {chosen_ally.name}Clan comes comes to your Clan, asking for herbs "
                    f"to heal their sick Clanmates. Your Clan quickly shoos them away, not willing to "
                    f"admit that they don't have a single herb in their stores. "
                ]
                # pylint: enable=line-too-long
                chosen_ally.relations -= 2
            else:
                herb_given = random.choice(list(game.clan.herbs.keys()))

                # Failsafe, since I have no idea why we are getting 0-herb entries.
                while game.clan.herbs[herb_given] <= 0:
                    print(
                        f"Warning: {herb_given} was chosen to give to another clan, "
                        f"although you currently have {game.clan.herbs[herb_given]}. "
                        f"Removing {herb_given} from herb dict, finding a new herb..."
                    )
                    game.clan.herbs.pop(herb_given)
                    if game.clan.herbs:
                        herb_given = random.choice(list(
                            game.clan.herbs.keys()))
                    else:
                        print("No herbs to destroy")
                        return
                    print(f"New herb found: {herb_given}")

                if game.clan.herbs[herb_given] > 2:
                    herb_amount = random.randrange(
                        1, int(game.clan.herbs[herb_given] - 1))
                    # deplete the herb
                    game.clan.herbs[herb_given] -= herb_amount
                    possible_events = [
                        f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any {herb_given.replace('_', ' ')} to spare. "  # pylint: disable=line-too-long
                        f"Graciously, your Clan decides to aid their allies and share the herbs.",
                        f"The medicine cat apprentice from {chosen_ally.name}Clan comes asking for {herb_given.replace('_', ' ')}. "  # pylint: disable=line-too-long
                        f"They refuse to say why their Clan needs them but your Clan still provides them with {herb_given.replace('_', ' ')}."
                        # pylint: disable=line-too-long
                    ]
                    if herb_given == 'lungwort':
                        possible_events.extend([
                            f"The {chosen_ally.name}Clan medicine cat apprentice comes to your camp, pleading for help "  # pylint: disable=line-too-long
                            f"with a yellowcough epidemic. Your Clan provides the cat with some of their extra lungwort.",
                            # pylint: disable=line-too-long
                            f"A medicine cat from {chosen_ally.name}Clan comes to your Clan, asking for lungwort to heal a "  # pylint: disable=line-too-long
                            f"case of yellowcough. Your Clan has some extra, and so decides to share with their allies."
                            # pylint: disable=line-too-long
                        ])
                    chosen_ally.relations += 5
                else:
                    possible_events = [
                        f"The {chosen_ally.name}Clan medicine cat comes asking if your Clan has any {herb_given.replace('_', ' ')} to spare. "  # pylint: disable=line-too-long
                        f"However, your Clan only has enough for themselves and they refuse to share.",
                        # pylint: disable=line-too-long
                        f"The medicine cat apprentice from {chosen_ally.name}Clan comes asking for herbs. They refuse to "  # pylint: disable=line-too-long
                        f"say why their Clan needs them and your Clan decides not to share their precious few {herb_given.replace('_', ' ')}."
                        # pylint: disable=line-too-long
                    ]
                    if herb_given == 'lungwort':
                        possible_events.extend([
                            f"The {chosen_ally.name}Clan medicine cat apprentice comes to your camp, pleading for help with"  # pylint: disable=line-too-long
                            f" a yellowcough epidemic. Your Clan can't spare the precious herb however, and turns them away.",
                            # pylint: disable=line-too-long
                            f"A medicine cat from {chosen_ally.name}Clan comes to your Clan, asking for lungwort to heal "  # pylint: disable=line-too-long
                            f"a case of yellowcough. However, your Clan has no extra lungwort to give."
                            # pylint: disable=line-too-long
                        ])
                    chosen_ally.relations -= 5
            event = random.choice(possible_events)
            game.herb_events_list.append(event)
            event_type = "health"
            if f"{chosen_ally.name}Clan" in event:
                event_type = ["health", "other_clans"]
            game.cur_events_list.append(Single_Event(event, event_type))

        elif not int(random.random() * 10) and 'moss' in game.clan.herbs:
            herb_amount = random.randrange(1, game.clan.herbs['moss'] + 1)
            game.clan.herbs['moss'] -= herb_amount
            if game.clan.herbs['moss'] <= 0:
                game.clan.herbs.pop('moss')
            event = "The medicine den nests have been refreshed with new moss from the herb stores."
            game.herb_events_list.append(event)
            game.cur_events_list.append(Single_Event(event, "health"))

        elif not int(random.random() * 80) and sum(
                game.clan.herbs.values()) > 0 and len(meds) > 0:
            possible_events = []
            
            if game.clan.war.get("at_war", False):
                
                # If at war, grab enemy clans
                enemy_clan = None
                for other_clan in game.clan.all_clans:
                    if other_clan.name == game.clan.war["enemy"]:
                        enemy_clan = other_clan
                        break
                
                possible_events.append(
                    f"{enemy_clan} breaks into the camp and ravages the herb stores, "
                    f"taking some for themselves and destroying the rest.")
            
            possible_events.extend([
                f"Some sort of pest got into the herb stores and completely destroyed them. The {insert} will have to "  # pylint: disable=line-too-long
                f"clean it out and start over anew.",  # pylint: disable=line-too-long
                "Abnormally strong winds blew through the camp last night and scattered the herb store into a "  # pylint: disable=line-too-long
                "useless state.",
                f"Some kind of blight has infected the herb stores. The {insert} have no choice but to clear out all "  # pylint: disable=line-too-long
                f"the old herbs."
            ])
            if game.clan.current_season == 'Leaf-bare':
                possible_events.extend([
                    "Freezing temperatures have not just affected the cats. It's also frostbitten the stored herbs. "  # pylint: disable=line-too-long
                    "They're useless now and will have to be replaced.",
                ])
            elif game.clan.current_season == 'Newleaf':
                possible_events.extend([
                    "The newleaf rain has left the air humid and the whole camp damp. The herb stores are found to "  # pylint: disable=line-too-long
                    "be growing mold and have to be thrown out. "
                ])
            elif game.clan.current_season == 'Greenleaf' and game.clan.biome != 'Mountainous':
                possible_events.extend([
                    "The persistent, dry heat managed to cause a small fire in the herb stores. While no one was "  # pylint: disable=line-too-long
                    "injured, the herbs are little more than ashes now."
                ])
            elif game.clan.biome == 'Beach' and game.clan.current_season in [
                "Leaf-fall", "Leaf-bare"
            ]:
                possible_events.extend([
                    "A huge wave crashes into camp, leaving everyone soaked and the herb stores irreparably damaged."
                    # pylint: disable=line-too-long
                ])
            game.clan.herbs.clear()
            chosen_event = random.choice(possible_events)
            game.cur_events_list.append(Single_Event(chosen_event, "health"))
            game.herb_events_list.append(chosen_event)

    def handle_lost_cats_return(self):
        """
        TODO: DOCS
        """
        
        eligable_cats = []
        for cat in Cat.all_cats.values():
            if cat.outside and cat.ID not in Cat.outside_cats:
                # The outside-value must be set to True before the cat can go to cotc
                Cat.outside_cats.update({cat.ID: cat})
                
            if cat.outside and cat.status not in [
                'kittypet', 'loner', 'rogue', 'former Clancat'
            ] and not cat.exiled and not cat.dead:
                eligable_cats.append(cat)
        
        if not eligable_cats:
            return
        
        lost_cat = random.choice(eligable_cats)
        
        text = [
            'After a long journey, m_c has finally returned home to c_n.',
            'm_c was found at the border, tired, but happy to be home.',
            "m_c strides into camp, much to the everyone's suprise. {PRONOUN/m_c/subject/CAP}{VERB/m_c/'re/'s} home!",
            "{PRONOUN/m_c/subject/CAP} met so many friends on {PRONOUN/m_c/poss} jouney, but c_n is where m_c truly belongs. With a tearful goodbye, " 
                "{PRONOUN/m_c/subject} {VERB/m_c/return/returns} home."
        ]
        lost_cat.outside = False
        additional_cats = lost_cat.add_to_clan()
        text = random.choice(text)
        
        if additional_cats:
            text += " {PRONOUN/m_c/subject/CAP} {VERB/m_c/bring/brings} along {PRONOUN/m_c/poss} "
            if len(additional_cats) > 1:
                text += str(len(additional_cats)) + " childen."
            else:
                text += "child."
         
        text = event_text_adjust(Cat, text, lost_cat, clan=game.clan)
        
        game.cur_events_list.append(
                Single_Event(text, "misc", [lost_cat.ID] + additional_cats))
        
        # Proform a ceremony if needed
        for x in [lost_cat] + [Cat.fetch_cat(i) for i in additional_cats]:             
           
            if x.status in ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice" "kitten", "newborn"]: 
                if x.moons >= 15:
                    if x.status == "medicine cat apprentice":
                        self.ceremony(x, "medicine cat")
                    elif x.status == "mediator apprentice":
                        self.ceremony(x, "mediator")
                    elif x.status == "queen's apprentice":
                        self.ceremony(x, "queen")
                    else:
                        self.ceremony(x, "warrior")
                elif x.status in ["kitten", "newborn"] and x.moons >= 6:
                    self.ceremony(x, "apprentice") 
            else:
                if x.moons == 0:
                    x.status = 'newborn'
                elif x.moons < 6:
                    x.status = "kitten"
                elif x.moons < 12:
                    x.status_change('apprentice')
                elif x.moons < 120:
                    x.status_change('warrior')
                else:
                    x.status_change('elder')      

    def handle_fading(self, cat):
        """
        TODO: DOCS
        """
        if game.settings["fading"] and not cat.prevent_fading \
                and cat.ID != game.clan.instructor.ID and not cat.faded:

            age_to_fade = game.config["fading"]["age_to_fade"]
            opacity_at_fade = game.config["fading"]["opacity_at_fade"]
            fading_speed = game.config["fading"]["visual_fading_speed"]
            # Handle opacity
            cat.pelt.opacity = int((100 - opacity_at_fade) *
                              (1 -
                               (cat.dead_for / age_to_fade) ** fading_speed) +
                              opacity_at_fade)

            # Deal with fading the cat if they are old enough.
            if cat.dead_for > age_to_fade:
                # If order not to add a cat to the faded list
                # twice, we can't remove them or add them to
                # faded cat list here. Rather, they are added to
                # a list of cats that will be "faded" at the next save.

                # Remove from med cat list, just in case.
                # This should never be triggered, but I've has an issue or
                # two with this, so here it is.
                if cat.ID in game.clan.med_cat_list:
                    game.clan.med_cat_list.remove(cat.ID)

                # Unset their mate, if they have one
                if len(cat.mate) > 0:
                    for mate_id in cat.mate:
                        if Cat.all_cats.get(mate_id):
                            cat.unset_mate(Cat.all_cats.get(mate_id))

                # If the cat is the current med, leader, or deputy, remove them
                if game.clan.leader:
                    if game.clan.leader.ID == cat.ID:
                        game.clan.leader = None
                if game.clan.deputy:
                    if game.clan.deputy.ID == cat.ID:
                        game.clan.deputy = None
                if game.clan.medicine_cat:
                    if game.clan.medicine_cat.ID == cat.ID:
                        if game.clan.med_cat_list:  # If there are other med cats
                            game.clan.medicine_cat = Cat.fetch_cat(
                                game.clan.med_cat_list[0])
                        else:
                            game.clan.medicine_cat = None

                game.cat_to_fade.append(cat.ID)
                cat.set_faded()

    def one_moon_outside_cat(self, cat):
        """
        exiled cat events
        """
        # aging the cat
        cat.one_moon()
        cat.manage_outside_trait()
            
        cat.skills.progress_skill(cat)
        self.pregnancy_events.handle_having_kits(cat, clan=game.clan)
        
        if not cat.dead:
            self.outsider_events.killing_outsiders(cat)
    
    def one_moon_cat(self, cat):
        """
        Triggers various moon events for a cat.
        -If dead, cat is given thought, dead_for count increased, and fading handled (then function is returned)
        -Outbreak chance is handled, death event is attempted, and conditions are handled (if death happens, return)
        -cat.one_moon() is triggered
        -mediator events are triggered (this includes the cat choosing to become a mediator)
        -freshkill pile events are triggered
        -if the cat is injured or ill, they're given their own set of possible events to avoid unrealistic behavior.
        They will handle disability events, coming out, pregnancy, apprentice EXP, ceremonies, relationship events, and
        will generate a new thought. Then the function is returned.
        -if the cat was not injured or ill, then they will do all of the above *and* trigger misc events, acc events,
        and new cat events
        """
        if cat.dead:
            
            cat.thoughts()
            if cat.ID in game.just_died:
                cat.moons +=1
            else:
                cat.dead_for += 1
            self.handle_fading(cat)  # Deal with fading.
            return

        # all actions, which do not trigger an event display and
        # are connected to cats are located in there
        cat.one_moon()

        # Handle Mediator Events
        self.mediator_events(cat)

        # handle nutrition amount
        # (CARE: the cats has to be fed before - should be handled in "one_moon" function)
        if game.clan.game_mode in ['expanded', 'cruel season'
                                   ] and game.clan.freshkill_pile:
            self.freshkill_events.handle_nutrient(
                cat, game.clan.freshkill_pile.nutrition_info)
            if cat.dead:
                return

        cat.talked_to = False
        cat.insulted = False
        cat.flirted = False
        
        # prevent injured or sick cats from unrealistic Clan events
        if cat.is_ill() or cat.is_injured():
            if cat.is_ill() and cat.is_injured():
                if random.getrandbits(1):
                    triggered_death = self.condition_events.handle_injuries(cat)
                    if not triggered_death:
                        self.condition_events.handle_illnesses(cat)
                else:
                    triggered_death = self.condition_events.handle_illnesses(cat)
                    if not triggered_death:
                        self.condition_events.handle_injuries(cat)
            elif cat.is_ill():
                self.condition_events.handle_illnesses(cat)
            else:
                self.condition_events.handle_injuries(cat)
            game.switches['skip_conditions'].clear()
            if cat.dead:
                return
            self.handle_outbreaks(cat)
        elif cat.ID != game.clan.your_cat.ID and cat.status not in ['kitten', 'elder', 'newborn'] and not cat.outside and not cat.dead:
            cat.experience += random.randint(0,5)

        # newborns don't do much
        if cat.status == 'newborn':
            cat.relationship_interaction()
            cat.thoughts()
            return

        self.handle_apprentice_EX(cat)  # This must be before perform_ceremonies!
        # this HAS TO be before the cat.is_disabled() so that disabled kits can choose a med cat or mediator position
        self.perform_ceremonies(cat)
        cat.skills.progress_skill(cat) # This must be done after ceremonies. 

        # check for death/reveal/risks/retire caused by permanent conditions
        if cat.is_disabled():
            self.condition_events.handle_already_disabled(cat)
            if cat.dead:
                return

        self.coming_out(cat)
        self.pregnancy_events.handle_having_kits(cat, clan=game.clan)
        # Stop the timeskip if the cat died in childbirth
        if cat.dead:
            return

        # this is the new interaction function, currently not active
        cat.relationship_interaction()
        cat.thoughts()

        # relationships have to be handled separately, because of the ceremony name change
        if not cat.dead or cat.outside:
            self.relation_events.handle_relationships(cat)

        # now we make sure ill and injured cats don't get interactions they shouldn't
        if cat.is_ill() or cat.is_injured():
            return

        self.invite_new_cats(cat)
        self.other_interactions(cat)
        self.gain_accessories(cat)

        # switches between the two death handles
        if random.getrandbits(1):
            triggered_death = self.handle_injuries_or_general_death(cat)
            if not triggered_death:
                self.handle_illnesses_or_illness_deaths(cat)
            else:
                game.switches['skip_conditions'].clear()
                return
        else:
            triggered_death = self.handle_illnesses_or_illness_deaths(cat)
            if not triggered_death:
                self.handle_injuries_or_general_death(cat)
            else:
                game.switches['skip_conditions'].clear()
                return

        self.handle_murder(cat)

        game.switches['skip_conditions'].clear()

    def load_war_resources(self):
        resource_dir = "resources/dicts/events/"
        with open(f"{resource_dir}war.json",
                  encoding="ascii") as read_file:
            self.WAR_TXT = ujson.loads(read_file.read())

    def check_war(self):
        """
        interactions with other clans
        """
        # if there are somehow no other clans, don't proceed
        if not game.clan.all_clans:
            return
        
        # Prevent wars from starting super early in the game. 
        if game.clan.age <= 4:
            return

        # check that the save dict has all the things we need
        if "at_war" not in game.clan.war:
            game.clan.war["at_war"] = False
        if "enemy" not in game.clan.war:
            game.clan.war["enemy"] = None
        if "duration" not in game.clan.war:
            game.clan.war["duration"] = 0

        # check if war in progress
        war_events = None
        enemy_clan = None
        if game.clan.war["at_war"]:
            
            # Grab the enemy clan object
            for other_clan in game.clan.all_clans:
                if other_clan.name == game.clan.war["enemy"]:
                    enemy_clan = other_clan
                    break
            
            threshold = 5
            if enemy_clan.temperament == 'bloodthirsty':
                threshold = 10
            if enemy_clan.temperament in ["mellow", "amiable", "gracious"]:
                threshold = 3

            threshold -= int(game.clan.war["duration"])
            if enemy_clan.relations < 0:
                enemy_clan.relations = 0

            # check if war should conclude, if not, continue
            if enemy_clan.relations >= threshold and game.clan.war["duration"] > 1:
                game.clan.war["at_war"] = False
                game.clan.war["enemy"] = None
                game.clan.war["duration"] = 0
                enemy_clan.relations += 12
                war_events = self.WAR_TXT["conclusion_events"]
            else:  # try to influence the relation with warring clan
                game.clan.war["duration"] += 1
                choice = random.choice(["rel_up", "rel_up", "neutral", "rel_down"])
                war_events = self.WAR_TXT["progress_events"][choice]
                if enemy_clan.relations < 0:
                    enemy_clan.relations = 0
                if choice == "rel_up":
                    enemy_clan.relations += 2
                elif choice == "rel_down" and enemy_clan.relations > 1:
                    enemy_clan.relations -= 1

        else:  # try to start a war if no war in progress
            for other_clan in game.clan.all_clans:
                threshold = 5
                if other_clan.temperament == 'bloodthirsty':
                    threshold = 10
                if other_clan.temperament in ["mellow", "amiable", "gracious"]:
                    threshold = 3

                if int(other_clan.relations) <= threshold and not int(random.random() * int(other_clan.relations)):
                    enemy_clan = other_clan
                    game.clan.war["at_war"] = True
                    game.clan.war["enemy"] = other_clan.name
                    war_events = self.WAR_TXT["trigger_events"]

        # if nothing happened, return
        if not war_events or not enemy_clan:
            return

        if not game.clan.leader or not game.clan.deputy or not game.clan.medicine_cat:
            for event in war_events:
                if not game.clan.leader and "lead_name" in event:
                    war_events.remove(event)
                if not game.clan.deputy and "dep_name" in event:
                    war_events.remove(event)
                if not game.clan.medicine_cat and "med_name" in event:
                    war_events.remove(event)

        event = random.choice(war_events)
        event = ongoing_event_text_adjust(Cat, event, other_clan_name=f"{enemy_clan.name}Clan", clan=game.clan)
        game.cur_events_list.append(
            Single_Event(event, "other_clans"))

    def perform_ceremonies(self, cat):
        """
        ceremonies
        """

        # PROMOTE DEPUTY TO LEADER, IF NEEDED -----------------------
        if game.clan.leader:
            leader_dead = game.clan.leader.dead
            leader_outside = game.clan.leader.outside
        else:
            leader_dead = True
            # If leader is None, treat them as dead (since they are dead - and faded away.)
            leader_outside = True

        # If a Clan deputy exists, and the leader is dead,
        #  outside, or doesn't exist, make the deputy leader.
        if game.clan.deputy:
            if game.clan.deputy is not None and \
                    not game.clan.deputy.dead and \
                    not game.clan.deputy.outside and \
                    (leader_dead or leader_outside):
                game.clan.new_leader(game.clan.deputy)
                game.clan.leader_lives = 9
                text = ''
                if game.clan.deputy.personality.trait == 'bloodthirsty':
                    text = f'{game.clan.deputy.name} has become the new leader. ' \
                           f'They stare down at their Clanmates with unsheathed claws, ' \
                           f'promising a new era for the Clans.'
                else:
                    c = random.choice([1, 2, 3])
                    if c == 1:
                        text = str(game.clan.deputy.name.prefix) + str(
                            game.clan.deputy.name.suffix) + \
                               ' has been promoted to the new leader of the Clan. ' \
                               'They travel immediately to the Moonstone to get their ' \
                               'nine lives and are hailed by their new name, ' + \
                               str(game.clan.deputy.name) + '.'
                    elif c == 2:
                        text = f'{game.clan.deputy.name} has become the new leader of the Clan. ' \
                               f'They vow that they will protect the Clan, ' \
                               f'even at the cost of their nine lives.'
                    elif c == 3:
                        text = f'{game.clan.deputy.name} has received ' \
                               f'their nine lives and became the ' \
                               f'new leader of the Clan. They feel like ' \
                               f'they are not ready for this new ' \
                               f'responsibility, but will try their best ' \
                               f'to do what is right for the Clan.'

                # game.ceremony_events_list.append(text)
                text += f"\nVisit {game.clan.deputy.name}'s " \
                        "profile to see their full leader ceremony."
                game.cur_events_list.append(
                    Single_Event(text, "ceremony", game.clan.deputy.ID))
                self.ceremony_accessory = True
                self.gain_accessories(cat)
                game.clan.deputy = None

        # OTHER CEREMONIES ---------------------------------------

        # Protection check, to ensure "None" cats won't cause a crash.
        if cat:
            cat_dead = cat.dead
        else:
            cat_dead = True

        if not cat_dead:
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.status == 'medicine cat' and game.clan.medicine_cat is None:
                game.clan.medicine_cat = cat

            # retiring to elder den
            if cat.status in ['warrior', 'deputy'] and len(cat.apprentice) < 1 and cat.moons > 114:
                # There is some variation in the age. 
                if cat.moons > 140 or not int(random.random() * (-0.7 * cat.moons + 100)):
                    if cat.status == 'deputy':
                        game.clan.deputy = None
                    self.ceremony(cat, 'elder')

            # apprentice a kitten to either med or warrior
            if cat.moons == cat_class.age_moons["adolescent"][0]:
                if cat.status == 'kitten':
                    med_cat_list = [i for i in Cat.all_cats_list if
                                    i.status in ["medicine cat", "medicine cat apprentice"] and not (
                                            i.dead or i.outside)]

                    # check if the medicine cat is an elder
                    has_elder_med = [c for c in med_cat_list if c.age == 'senior' and c.status == "medicine cat"]

                    very_old_med = [
                        c for c in med_cat_list
                        if c.moons >= 150 and c.status == "medicine cat"
                    ]

                    # check if the Clan has sufficient med cats
                    has_med = medical_cats_condition_fulfilled(
                        Cat.all_cats.values(),
                        amount_per_med=get_amount_cat_for_one_medic(game.clan))

                    # check if a med cat app already exists
                    has_med_app = any(cat.status == "medicine cat apprentice"
                                      for cat in med_cat_list)

                    # assign chance to become med app depending on current med cat and traits
                    chance = game.config["roles"]["base_medicine_app_chance"]
                    if has_elder_med == med_cat_list:
                        # These chances apply if all the current medicine cats are elders.
                        if has_med:
                            chance = int(chance / 2.22)
                        else:
                            chance = int(chance / 13.67)
                    elif very_old_med == med_cat_list:
                        # These chances apply is all the current medicine cats are very old.
                        if has_med:
                            chance = int(chance / 3)
                        else:
                            chance = int(chance / 14)
                    # These chances will only be reached if the
                    # Clan has at least one non-elder medicine cat.
                    elif not has_med:
                        chance = int(chance / 7.125)
                    elif has_med:
                        chance = int(chance * 2.22)

                    if cat.personality.trait in [
                        'altruistic', 'compassionate', 'empathetic',
                        'wise', 'faithful'
                    ]:
                        chance = int(chance / 1.3)
                    if cat.is_disabled():
                        chance = int(chance / 2)

                    if chance == 0:
                        chance = 1

                    if not has_med_app and not int(random.random() * chance):
                        self.ceremony(cat, 'medicine cat apprentice')
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    elif random.randint(1,40) == 1:
                        self.ceremony(cat, "queen's apprentice")
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    else:
                        # Chance for mediator apprentice
                        mediator_list = list(
                            filter(
                                lambda x: x.status == "mediator" and not x.dead
                                          and not x.outside, Cat.all_cats_list))

                        # This checks if at least one mediator already has an apprentice.
                        has_mediator_apprentice = False
                        for c in mediator_list:
                            if c.apprentice:
                                has_mediator_apprentice = True
                                break

                        chance = game.config["roles"]["mediator_app_chance"]
                        if cat.personality.trait in [
                            'charismatic', 'empathetic', 'responsible',
                            'wise', 'thoughtful'
                        ]:
                            chance = int(chance / 1.5)
                        if cat.is_disabled():
                            chance = int(chance / 2)

                        if chance == 0:
                            chance = 1

                        # Only become a mediator if there is already one in the clan.
                        if mediator_list and not has_mediator_apprentice and \
                                not int(random.random() * chance):
                            self.ceremony(cat, 'mediator apprentice')
                            self.ceremony_accessory = True
                            self.gain_accessories(cat)
                        else:
                            self.ceremony(cat, 'apprentice')
                            self.ceremony_accessory = True
                            self.gain_accessories(cat)

            # graduate
            if cat.status in [
                "apprentice", "mediator apprentice",
                "medicine cat apprentice", "queen's apprentice"
            ]:

                if game.settings["12_moon_graduation"]:
                    _ready = cat.moons >= 12
                else:
                    _ready = (cat.experience_level not in ["untrained", "trainee"] and
                              cat.moons >= game.config["graduation"]["min_graduating_age"]) \
                             or cat.moons >= game.config["graduation"]["max_apprentice_age"][cat.status]

                if _ready:
                    if game.settings["12_moon_graduation"]:
                        preparedness = "prepared"
                    else:
                        if cat.moons == game.config["graduation"]["min_graduating_age"]:
                            preparedness = "early"
                        elif cat.experience_level in ["untrained", "trainee"]:
                            preparedness = "unprepared"
                        else:
                            preparedness = "prepared"

                    if cat.status == 'apprentice':
                        self.ceremony(cat, 'warrior', preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

                    # promote to med cat
                    elif cat.status == 'medicine cat apprentice':
                        self.ceremony(cat, 'medicine cat', preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

                    elif cat.status == 'mediator apprentice':
                        self.ceremony(cat, 'mediator', preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)
                    
                    elif cat.status == "queen's apprentice":
                        self.ceremony(cat, "queen", preparedness)
                        self.ceremony_accessory = True
                        self.gain_accessories(cat)

    def load_ceremonies(self):
        """
        TODO: DOCS
        """
        if self.CEREMONY_TXT is not None:
            return

        resource_dir = "resources/dicts/events/ceremonies/"
        with open(f"{resource_dir}ceremony-master.json",
                  encoding="ascii") as read_file:
            self.CEREMONY_TXT = ujson.loads(read_file.read())

        self.ceremony_id_by_tag = {}
        # Sorting.
        for ID in self.CEREMONY_TXT:
            for tag in self.CEREMONY_TXT[ID][0]:
                if tag in self.ceremony_id_by_tag:
                    self.ceremony_id_by_tag[tag].add(ID)
                else:
                    self.ceremony_id_by_tag[tag] = {ID}

    def ceremony(self, cat, promoted_to, preparedness="prepared"):
        """
        promote cats and add to event list
        """
        # ceremony = []
        
        _ment = Cat.fetch_cat(cat.mentor) if cat.mentor else None # Grab current mentor, if they have one, before it's removed. 
        old_name = str(cat.name)
        cat.status_change(promoted_to)
        cat.rank_change_traits_skill(_ment)

        involved_cats = [
            cat.ID
        ]  # Clearly, the cat the ceremony is about is involved.

        # Time to gather ceremonies. First, lets gather all the ceremony ID's.
        possible_ceremonies = set()
        dead_mentor = None
        mentor = None
        previous_alive_mentor = None
        dead_parents = []
        living_parents = []
        mentor_type = {
            "medicine cat": ["medicine cat"],
            "queen": ["queen"],
            "warrior": ["warrior", "deputy", "leader", "elder"],
            "mediator": ["mediator"]
        }

        try:
            # Get all the ceremonies for the role ----------------------------------------
            possible_ceremonies.update(self.ceremony_id_by_tag[promoted_to])

            # Get ones for prepared status ----------------------------------------------
            if promoted_to in ["warrior", "medicine cat", "mediator", "queen"]:
                possible_ceremonies = possible_ceremonies.intersection(
                    self.ceremony_id_by_tag[preparedness])

            # Gather ones for mentor. -----------------------------------------------------
            tags = []

            # CURRENT MENTOR TAG CHECK
            if cat.mentor:
                if Cat.fetch_cat(cat.mentor).status == "leader":
                    tags.append("yes_leader_mentor")
                else:
                    tags.append("yes_mentor")
                mentor = Cat.fetch_cat(cat.mentor)
            else:
                tags.append("no_mentor")

            for c in reversed(cat.former_mentor):
                if Cat.fetch_cat(c) and Cat.fetch_cat(c).dead:
                    tags.append("dead_mentor")
                    dead_mentor = Cat.fetch_cat(c)
                    break

            # Unlike dead mentors, living mentors must be VALID
            # they must have the correct status for the role the cat
            # is being promoted too.
            valid_living_former_mentors = []
            for c in cat.former_mentor:
                if not (Cat.fetch_cat(c).dead or Cat.fetch_cat(c).outside):
                    if promoted_to in mentor_type:
                        if Cat.fetch_cat(c).status in mentor_type[promoted_to]:
                            valid_living_former_mentors.append(c)
                    else:
                        valid_living_former_mentors.append(c)

            # ALL FORMER MENTOR TAG CHECKS
            if valid_living_former_mentors:
                #  Living Former mentors. Grab the latest living valid mentor.
                previous_alive_mentor = Cat.fetch_cat(
                    valid_living_former_mentors[-1])
                if previous_alive_mentor.status == "leader":
                    tags.append("alive_leader_mentor")
                else:
                    tags.append("alive_mentor")
            else:
                # This tag means the cat has no living, valid mentors.
                tags.append("no_valid_previous_mentor")

            # Now we add the mentor stuff:
            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_mentor"])

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(
                        self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp

            # Gather for parents ---------------------------------------------------------
            for p in [cat.parent1, cat.parent2]:
                if Cat.fetch_cat(p):
                    if Cat.fetch_cat(p).dead:
                        dead_parents.append(Cat.fetch_cat(p))
                    # For the purposes of ceremonies, living parents
                    # who are also the leader are not counted.
                    elif not Cat.fetch_cat(p).dead and not Cat.fetch_cat(p).outside and \
                            Cat.fetch_cat(p).status != "leader":
                        living_parents.append(Cat.fetch_cat(p))

            tags = []
            if len(dead_parents) >= 1 and "orphaned" not in cat.backstory:
                tags.append("dead1_parents")
            if len(dead_parents) >= 2 and "orphaned" not in cat.backstory:
                tags.append("dead1_parents")
                tags.append("dead2_parents")

            if len(living_parents) >= 1:
                tags.append("alive1_parents")
            if len(living_parents) >= 2:
                tags.append("alive2_parents")

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_parents"])

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(
                        self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp

            # Gather for leader ---------------------------------------------------------

            tags = []
            if game.clan.leader and not game.clan.leader.dead and not game.clan.leader.outside:
                tags.append("yes_leader")
            else:
                tags.append("no_leader")

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_leader"])

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(
                        self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp

            # Gather for backstories.json ----------------------------------------------------
            tags = []
            if cat.backstory == ['abandoned1', 'abandoned2', 'abandoned3']:
                tags.append("abandoned")
            elif cat.backstory == "clanborn":
                tags.append("clanborn")

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["general_backstory"])

            for t in tags:
                temp.update(
                    possible_ceremonies.intersection(
                        self.ceremony_id_by_tag[t]))

            possible_ceremonies = temp
            # Gather for traits --------------------------------------------------------------

            temp = possible_ceremonies.intersection(
                self.ceremony_id_by_tag["all_traits"])

            if cat.personality.trait in self.ceremony_id_by_tag:
                temp.update(
                    possible_ceremonies.intersection(
                        self.ceremony_id_by_tag[cat.personality.trait]))

            possible_ceremonies = temp
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            print("Issue gathering ceremony text.", str(cat.name), promoted_to)

        # getting the random honor if it's needed
        random_honor = None
        if promoted_to in ['warrior', 'mediator', 'medicine cat', "queen"]:
            resource_dir = "resources/dicts/events/ceremonies/"
            with open(f"{resource_dir}ceremony_traits.json",
                      encoding="ascii") as read_file:
                TRAITS = ujson.loads(read_file.read())
            try:
                random_honor = random.choice(TRAITS[cat.personality.trait])
            except KeyError:
                random_honor = "hard work"

        if cat.status in ["warrior", "medicine cat", "mediator", "queen"]:
            self.history.add_app_ceremony(cat, random_honor)
        
        ceremony_tags, ceremony_text = self.CEREMONY_TXT[random.choice(
            list(possible_ceremonies))]

        # This is a bit strange, but it works. If there is
        # only one parent involved, but more than one living
        # or dead parent, the adjust text function will pick
        # a random parent. However, we need to know the
        # parent to include in the involved cats. Therefore,
        # text adjust also returns the random parents it picked,
        # which will be added to the involved cats if needed.
        ceremony_text, involved_living_parent, involved_dead_parent = \
            ceremony_text_adjust(Cat, ceremony_text, cat, dead_mentor=dead_mentor,
                                 random_honor=random_honor, old_name=old_name,
                                 mentor=mentor, previous_alive_mentor=previous_alive_mentor,
                                 living_parents=living_parents, dead_parents=dead_parents)

        # Gather additional involved cats
        for tag in ceremony_tags:
            if tag == "yes_leader":
                involved_cats.append(game.clan.leader.ID)
            elif tag in ["yes_mentor", "yes_leader_mentor"]:
                involved_cats.append(cat.mentor)
            elif tag == "dead_mentor":
                involved_cats.append(dead_mentor.ID)
            elif tag in ["alive_mentor", "alive_leader_mentor"]:
                involved_cats.append(previous_alive_mentor.ID)
            elif tag == "alive2_parents" and len(living_parents) >= 2:
                for c in living_parents[:2]:
                    involved_cats.append(c.ID)
            elif tag == "alive1_parents" and involved_living_parent:
                involved_cats.append(involved_living_parent.ID)
            elif tag == "dead2_parents" and len(dead_parents) >= 2:
                for c in dead_parents[:2]:
                    involved_cats.append(c.ID)
            elif tag == "dead1_parent" and involved_dead_parent:
                involved_cats.append(involved_dead_parent.ID)

        # # remove duplicates
        involved_cats = list(set(involved_cats))
        if str(game.clan.your_cat.name) not in ceremony_text:
            game.cur_events_list.append(
                Single_Event(f'{ceremony_text}', "ceremony", involved_cats))
        game.ceremony_events_list.append(f'{cat.name}{ceremony_text}')

    def gain_accessories(self, cat):
        """
        accessories
        """

        if not cat:
            return

        if cat.dead or cat.outside:
            return

        # check if cat already has acc
        if cat.pelt.accessory:
            self.ceremony_accessory = False
            return

        # find other_cat
        other_cat = random.choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = random.choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                return

        # chance to gain acc
        acc_chances = game.config["accessory_generation"]
        chance = acc_chances["base_acc_chance"]
        if cat.status in ['medicine cat', 'medicine cat apprentice']:
            chance += acc_chances["med_modifier"]
        if cat.age in ['kitten', 'adolescent']:
            chance += acc_chances["baby_modifier"]
        elif cat.age in ['senior adult', 'senior']:
            chance += acc_chances["elder_modifier"]
        if cat.personality.trait in [
            "adventurous", "childish", "confident", "daring", "playful",
            "attention-seeker", "bouncy", "sweet", "troublesome",
            "impulsive", "inquisitive", "strange", "shameless"
        ]:
            chance += acc_chances["happy_trait_modifier"]
        elif cat.personality.trait in [
            "cold", "strict", "bossy", "bullying", "insecure", "nervous"
        ]:
            chance += acc_chances["grumpy_trait_modifier"]
        if self.ceremony_accessory:
            chance += acc_chances["ceremony_modifier"]

        # increase chance of acc if the cat had a ceremony
        if chance <= 0:
            chance = 1
        if not int(random.random() * chance):
            
            enemy_clan = None
            if game.clan.war.get("at_war", False):
                
                for other_clan in game.clan.all_clans:
                    if other_clan.name == game.clan.war["enemy"]:
                        enemy_clan = other_clan
                        break
            
            
            self.misc_events.handle_misc_events(
                cat,
                other_cat,
                game.clan.war.get("at_war", False),
                enemy_clan,
                alive_kits=get_alive_kits(Cat),
                accessory=True,
                ceremony=self.ceremony_accessory)
        self.ceremony_accessory = False

        return

    def handle_apprentice_EX(self, cat):
        """
        TODO: DOCS
        """
        if cat.status in [
            "apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"
        ]:

            if cat.not_working() and int(random.random() * 3):
                return

            if cat.experience > cat.experience_levels_range["trainee"][1]:
                return

            if cat.status == "medicine cat apprentice":
                ran = game.config["graduation"]["base_med_app_timeskip_ex"]
            else:
                ran = game.config["graduation"]["base_app_timeskip_ex"]

            mentor_modifier = 1
            if not cat.mentor or Cat.fetch_cat(cat.mentor).not_working():
                # Sick mentor debuff
                mentor_modifier = 0.7
                mentor_skill_modifier = 0
                
            exp = random.choice(list(range(ran[0][0], ran[0][1] + 1)) + list(range(ran[1][0], ran[1][1] + 1)))

            if game.clan.game_mode == "classic":
                exp += random.randint(0, 3)

            cat.experience += max(exp * mentor_modifier, 1)

    def invite_new_cats(self, cat):
        """
        new cats
        """
        chance = 200

        alive_cats = list(
            filter(
                lambda kitty: (kitty.status != "leader" and not kitty.dead and
                               not kitty.outside), Cat.all_cats.values()))

        clan_size = len(alive_cats)

        base_chance = 700
        if clan_size < 10:
            base_chance = 200
        elif clan_size < 30:
            base_chance = 300

        reputation = game.clan.reputation
        reputation = 80
        # hostile
        if 1 <= reputation <= 30:
            if clan_size < 10:
                chance = base_chance
            else:
                rep_adjust = int(reputation / 2)
                chance = base_chance + int(300 / rep_adjust)
        # neutral
        elif 31 <= reputation <= 70:
            if clan_size < 10:
                chance = base_chance - reputation
            else:
                chance = base_chance
        # welcoming
        elif 71 <= reputation <= 100:
            chance = base_chance - reputation

        chance = max(chance, 1)

        # choose other cat
        possible_other_cats = list(
            filter(
                lambda c: not c.dead and not c.exiled and not c.outside and
                          (c.ID != cat.ID), Cat.all_cats.values()))

        # If there are possible other cats...
        if possible_other_cats:
            other_cat = random.choice(possible_other_cats)

            if cat.status in ["apprentice", "medicine cat apprentice"
                              ] and not int(random.random() * 3):
                if cat.mentor is not None:
                    other_cat = Cat.fetch_cat(cat.mentor)
        else:
            # Otherwise, other_cat is None
            other_cat = None

        if not int(
                random.random() * chance
        ) and cat.age != 'kitten' and cat.age != 'adolescent' and not self.new_cat_invited:
            self.new_cat_invited = True

            enemy_clan = None
            if game.clan.war.get("at_war", False):
                
                for other_clan in game.clan.all_clans:
                    if other_clan.name == game.clan.war["enemy"]:
                        enemy_clan = other_clan
                        break
            
            new_cats = self.new_cat_events.handle_new_cats(
                cat=cat,
                other_cat=other_cat,
                war=game.clan.war.get("at_war", False),
                enemy_clan=enemy_clan,
                alive_kits=get_alive_kits(Cat))
            self.relation_events.welcome_new_cats(new_cats)

    def other_interactions(self, cat):
        """
        TODO: DOCS
        """
        hit = int(random.random() * 30)
        if hit:
            return

        other_cat = random.choice(list(Cat.all_cats.values()))
        countdown = int(len(Cat.all_cats) / 3)
        while cat == other_cat or other_cat.dead or other_cat.outside:
            other_cat = random.choice(list(Cat.all_cats.values()))
            countdown -= 1
            if countdown <= 0:
                other_cat = None
                break

        enemy_clan = None
        if game.clan.war.get("at_war", False):
            
            for other_clan in game.clan.all_clans:
                if other_clan.name == game.clan.war["enemy"]:
                    enemy_clan = other_clan
                    break
        
        self.misc_events.handle_misc_events(cat,
                                            other_cat,
                                            game.clan.war.get("at_war", False),
                                            enemy_clan,
                                            alive_kits=get_alive_kits(Cat))

    def handle_injuries_or_general_death(self, cat):
        """
        decide if cat dies
        """
        # choose other cat
        possible_other_cats = list(
            filter(
                lambda c: not c.dead and not c.exiled and not c.outside and
                          (c.ID != cat.ID), Cat.all_cats.values()))
        
        # If at war, grab enemy clans
        enemy_clan = None
        if game.clan.war.get("at_war", False):
            
            for other_clan in game.clan.all_clans:
                if other_clan.name == game.clan.war["enemy"]:
                    enemy_clan = other_clan
                    break
            


        # If there are possible other cats...
        if possible_other_cats:
            other_cat = random.choice(possible_other_cats)

            if cat.status in ["apprentice", "medicine cat apprentice"
                              ] and not int(random.random() * 3):
                if cat.mentor is not None:
                    other_cat = Cat.fetch_cat(cat.mentor)
        else:
            # Otherwise, other_cat is None
            other_cat = None

        # check if Clan has kits, if True then Clan has kits
        alive_kits = get_alive_kits(Cat)

        # chance to kill leader: 1/125 by default
        if not int(random.random() * game.get_config_value("death_related", "leader_death_chance")) \
                and cat.status == 'leader' \
                and not cat.not_working():
            self.death_events.handle_deaths(cat, other_cat, game.clan.war.get("at_war", False), enemy_clan, alive_kits)
            return True

        # chance to die of old age
        age_chance = game.config["death_related"]["old_age_death_chance"]
        age_start = game.config["death_related"]["old_age_death_start"]
        if cat.moons > int(
                random.random() * age_chance) + age_start:  # cat.moons > 150 <--> 200
            
            self.death_events.handle_deaths(cat, other_cat, game.clan.war.get("at_war", False),
                                            enemy_clan, alive_kits)
            return True

        # disaster death chance
        if game.settings.get('disasters'):
            if not random.getrandbits(9):  # 1/512
                self.handle_mass_extinctions(cat)
                return True
        chance_death = game.get_config_value("death_related", f"{game.clan.game_mode}_death_chance")
        try:
            if cat.status == "kitten" or cat.status == "newborn":
                num_queens = 0
                for c in game.clan.clan_cats:
                    if not Cat.all_cats.get(c).outside and not Cat.all_cats.get(c).dead:
                        if Cat.all_cats.get(c).status == "queen" or Cat.all_cats.get(c).status == "queen's apprentice":
                            num_queens+=1
                chance_death+=(num_queens*5)
        except:
            print("couldn't handle queen mortality")
            
        # final death chance and then, if not triggered, head to injuries
        if not int(random.random() * chance_death) \
                and not cat.not_working():  # 1/400
            self.death_events.handle_deaths(cat, other_cat, game.clan.war.get("at_war", False), enemy_clan, alive_kits)
            return True
        else:
            triggered_death = self.condition_events.handle_injuries(cat, other_cat, alive_kits, game.clan.war.get("at_war", False),
                                                                    enemy_clan, game.clan.current_season)
            return triggered_death

        

    def handle_murder(self, cat):
        ''' Handles murder '''
        relationships = cat.relationships.values()
        targets = []
        
        # if this cat is unstable and aggressive, we lower the random murder chance. 
        random_murder_chance = int(game.config["death_related"]["base_random_murder_chance"])
        random_murder_chance -= 0.5 * ((cat.personality.aggression) + (16 - cat.personality.stability))

        # Check to see if random murder is triggered. If so, we allow targets to be anyone they have even the smallest amount 
        # of dislike for. 
        if random.getrandbits(max(1, int(random_murder_chance))) == 1:
            targets = [i for i in relationships if i.dislike > 1 and not Cat.fetch_cat(i.cat_to).dead and not Cat.fetch_cat(i.cat_to).outside]
            if not targets:
                return
            
            chosen_target = random.choice(targets)
            print("Random Murder!", str(cat.name),  str(Cat.fetch_cat(chosen_target.cat_to).name))
            
            # If at war, grab enemy clans
            enemy_clan = None
            if game.clan.war.get("at_war", False):
                
                for other_clan in game.clan.all_clans:
                    if other_clan.name == game.clan.war["enemy"]:
                        enemy_clan = other_clan
                        break
            
            self.death_events.handle_deaths(Cat.fetch_cat(chosen_target.cat_to), cat, game.clan.war.get("at_war", False),
                                            enemy_clan, alive_kits=get_alive_kits(Cat), murder=True)
            
            return
            
   
        # If random murder is not triggered, targets can only be those they have high dislike for. 
        hate_relation = [i for i in relationships if
                        i.dislike > 50 and not Cat.fetch_cat(i.cat_to).dead and not Cat.fetch_cat(i.cat_to).outside]
        targets.extend(hate_relation)
        resent_relation = [i for i in relationships if
                        i.jealousy > 50 and not Cat.fetch_cat(i.cat_to).dead and not Cat.fetch_cat(i.cat_to).outside]
        targets.extend(resent_relation)

        # if we have some, then we need to decide if this cat will kill
        if targets:
            chosen_target = random.choice(targets)
            
            # print(cat.name, 'TARGET CHOSEN', Cat.fetch_cat(chosen_target.cat_to).name)

            kill_chance = game.config["death_related"]["base_murder_kill_chance"]
            
            # chance to murder grows with the dislike and jealousy value
            kill_chance -= chosen_target.dislike
            # print('DISLIKE MODIFIER', kill_chance)
            kill_chance -= chosen_target.jealousy
            # print('JEALOUS MODIFIER', kill_chance)

            facet_modifiers = cat.personality.aggression + \
                (16 - cat.personality.stability) + (16 - cat.personality.lawfulness)
            
            kill_chance = kill_chance - facet_modifiers
            kill_chance = max(15, kill_chance)
             
            #print("Final kill chance: " + str(kill_chance))
            
            if not int(random.random() * kill_chance):
                # print(cat.name, 'TARGET CHOSEN', Cat.fetch_cat(chosen_target.cat_to).name)
                # print("KILL KILL KILL")
                
                # If at war, grab enemy clans
                enemy_clan = None
                if game.clan.war.get("at_war", False):
                    
                    for other_clan in game.clan.all_clans:
                        if other_clan.name == game.clan.war["enemy"]:
                            enemy_clan = other_clan
                            break
                
                self.death_events.handle_deaths(Cat.fetch_cat(chosen_target.cat_to), cat, game.clan.war.get("at_war", False),
                                                enemy_clan, alive_kits=get_alive_kits(Cat), murder=True)

    def handle_mass_extinctions(self, cat):  # pylint: disable=unused-argument
        """Affects random cats in the clan, no cat needs to be passed to this function."""
        alive_cats = list(
            filter(
                lambda kitty: (kitty.status != "leader" and not kitty.dead and
                               not kitty.outside), Cat.all_cats.values()))
        alive_count = len(alive_cats)
        if alive_count > 15:
            if game.clan.all_clans:
                other_clan = game.clan.all_clans
            else:
                other_clan = [""]

            # Do some population/weight scrunkling to get amount of deaths
            max_deaths = int(alive_count / 2)  # 1/2 of alive cats
            weights = []
            population = []
            for n in range(2, max_deaths):
                population.append(n)
                weight = 1 / (0.75 * n)  # Lower chance for more dead cats
                weights.append(weight)
            dead_count = random.choices(population,
                                        weights=weights)[0]  # the dieded..

            disaster = []
            dead_names = []
            involved_cats = []
            dead_cats = random.sample(alive_cats, dead_count)
            for kitty in dead_cats:  # use "kitty" to not redefine "cat"
                dead_names.append(kitty.name)
                involved_cats.append(kitty.ID)
            names = f"{dead_names.pop(0)}"  # Get first    pylint: disable=redefined-outer-name
            if dead_names:
                last_name = dead_names.pop()  # Get last
                if dead_names:
                    for name in dead_names:  # In-between
                        names += f", {name}"
                    names += f", and {last_name}"
                else:
                    names += f" and {last_name}"
            disaster.extend([
                ' drown after the camp becomes flooded.',
                ' are killed after a fire rages through the camp.',
                ' are killed in an ambush by a group of rogues.',
                ' go missing in the night.',
                ' are killed after a badger attack.',
                ' die to a greencough outbreak.',
                ' are taken away by Twolegs.',
                ' eat tainted fresh-kill and die.',
            ])
            if game.clan.current_season == 'Leaf-bare':
                disaster.extend([' die after freezing from a snowstorm.'])
                if game.clan.game_mode == "classic":
                    disaster.extend(
                        [' starve to death when no prey is found.'])
            elif game.clan.current_season == 'Greenleaf':
                disaster.extend([
                    ' die after overheating.',
                    ' die after the water dries up from drought.'
                ])
            if dead_count >= 2:
                event_string = f'{names}{random.choice(disaster)}'
                if event_string == f'{names} are taken away by Twolegs.':
                    for kitty in dead_cats:
                        self.handle_twoleg_capture(kitty)
                    game.cur_events_list.append(
                        Single_Event(event_string, "birth_death",
                                     involved_cats))
                    # game.birth_death_events_list.append(event_string)
                    return
                game.cur_events_list.append(
                    Single_Event(event_string, "birth_death", involved_cats))
                # game.birth_death_events_list.append(event_string)

            else:
                disaster_str = random.choice(disaster)
                disaster_str = disaster_str.replace('are', 'is')
                disaster_str = disaster_str.replace('go', 'goes')
                disaster_str = disaster_str.replace('die', 'dies')
                disaster_str = disaster_str.replace('drown', 'drowns')
                disaster_str = disaster_str.replace('eat', 'eats')
                disaster_str = disaster_str.replace('starve', 'starves')
                event_string = f'{names}{disaster_str}'
                game.cur_events_list.append(
                    Single_Event(event_string, "birth_death", involved_cats))
                # game.birth_death_events_list.append(event_string)

            for poor_little_meowmeow in dead_cats:
                poor_little_meowmeow.die()
                # this next bit is temporary until we can rework it
                History.add_death(poor_little_meowmeow, 'This cat died after disaster struck the Clan.')

    def handle_illnesses_or_illness_deaths(self, cat):
        """ 
        This function will handle:
            - expanded mode: getting a new illness (extra function in own class)
            - classic mode illness related deaths is already handled in the general death function
        Returns: 
            - boolean if a death event occurred or not
        """
        # ---------------------------------------------------------------------------- #
        #                           decide if cat dies                                 #
        # ---------------------------------------------------------------------------- #
        # if triggered_death is True then the cat will die
        triggered_death = False
        if game.clan.game_mode in ["expanded", "cruel season"]:
            triggered_death = self.condition_events.handle_illnesses(
                cat, game.clan.current_season)
        return triggered_death

    def handle_twoleg_capture(self, cat):
        """
        TODO: DOCS
        """
        cat.outside = True
        cat.gone()
        # The outside-value must be set to True before the cat can go to cotc
        cat.thought = "Is terrified as they are trapped in a large silver Twoleg den"
        # FIXME: Not sure what this is intended to do; 'cat_class' has no 'other_cats' attribute.
        # cat_class.other_cats[cat.ID] = cat

    def handle_outbreaks(self, cat):
        """Try to infect some cats."""
        # check if the cat is ill, if game mode is classic,
        # or if Clan has sufficient med cats in expanded mode
        if not cat.is_ill() or game.clan.game_mode == 'classic':
            return

        # check how many kitties are already ill
        already_sick = list(
            filter(
                lambda kitty:
                (not kitty.dead and not kitty.outside and kitty.is_ill()),
                Cat.all_cats.values()))
        already_sick_count = len(already_sick)

        # round up the living kitties
        alive_cats = list(
            filter(
                lambda kitty:
                (not kitty.dead and not kitty.outside and not kitty.is_ill()),
                Cat.all_cats.values()))
        alive_count = len(alive_cats)

        # if large amount of the population is already sick, stop spreading
        if already_sick_count >= alive_count * .25:
            return

        meds = get_med_cats(Cat)

        for illness in cat.illnesses:
            # check if illness can infect other cats
            if cat.illnesses[illness]["infectiousness"] == 0:
                continue
            chance = cat.illnesses[illness]["infectiousness"]
            chance += len(meds) * 7
            if not int(random.random() * chance):  # 1/chance to infect
                # fleas are the only condition allowed to spread outside of cold seasons
                if game.clan.current_season not in ["Leaf-bare", "Leaf-fall"
                                                    ] and illness != 'fleas':
                    continue
                if illness == 'kittencough':
                    # adjust alive cats list to only include kittens
                    alive_cats = list(
                        filter(
                            lambda kitty:
                            (kitty.status in ['kitten', 'newborn'] and not kitty.dead and
                             not kitty.outside), Cat.all_cats.values()))
                    alive_count = len(alive_cats)

                max_infected = int(alive_count / 2)  # 1/2 of alive cats
                # If there are less than two cat to infect,
                # you are allowed to infect all the cats
                if max_infected < 2:
                    max_infected = alive_count
                # If, event with all the cats, there is less
                # than two cats to infect, cancel outbreak.
                if max_infected < 2:
                    return

                weights = []
                population = []
                for n in range(2, max_infected + 1):
                    population.append(n)
                    weight = 1 / (0.75 * n
                                  )  # Lower chance for more infected cats
                    weights.append(weight)
                infected_count = random.choices(
                    population, weights=weights)[0]  # the infected..

                infected_names = []
                involved_cats = []
                infected_cats = random.sample(alive_cats, infected_count)
                for sick_meowmeow in infected_cats:
                    infected_names.append(str(sick_meowmeow.name))
                    involved_cats.append(sick_meowmeow.ID)
                    sick_meowmeow.get_ill(
                        illness, event_triggered=True)  # SPREAD THE GERMS >:)

                illness_name = str(illness).capitalize()
                if illness == 'kittencough':
                    event = f'{illness_name} has spread around the nursery. ' \
                            f'{", ".join(infected_names[:-1])}, and ' \
                            f'{infected_names[-1]} have been infected.'
                elif illness == 'fleas':
                    event = f'Fleas have been hopping from pelt to pelt and now ' \
                            f'{", ".join(infected_names[:-1])}, ' \
                            f'and {infected_names[-1]} are all infested.'
                else:
                    event = f'{illness_name} has spread around the camp. ' \
                            f'{", ".join(infected_names[:-1])}, and ' \
                            f'{infected_names[-1]} have been infected.'

                game.cur_events_list.append(
                    Single_Event(event, "health", involved_cats))
                # game.health_events_list.append(event)
                break

    def coming_out(self, cat):
        """turnin' the kitties trans..."""
        if cat.genderalign == cat.gender:
            if cat.moons < 6:
                return

            involved_cats = [cat.ID]
            if cat.age == 'adolescent':
                transing_chance = random.getrandbits(8)  # 2/256
            elif cat.age == 'young adult':
                transing_chance = random.getrandbits(9)  # 2/512
            else:
                # adult, senior adult, elder
                transing_chance = random.getrandbits(10)  # 2/1028

            if transing_chance:
                # transing_chance != 0, no trans kitties today...    L
                return

            if random.getrandbits(1):  # 50/50
                if cat.gender == "male":
                    cat.genderalign = "trans female"
                    # cat.pronouns = [cat.default_pronouns[1].copy()]
                else:
                    cat.genderalign = "trans male"
                    # cat.pronouns = [cat.default_pronouns[2].copy()]
            else:
                cat.genderalign = "nonbinary"
                # cat.pronouns = [cat.default_pronouns[0].copy()]

            if cat.gender == 'male':
                gender = 'tom'
            else:
                gender = 'she-cat'
            text = f"{cat.name} has realized that {gender} doesn't describe how they feel anymore."
            game.cur_events_list.append(
                Single_Event(text, "misc", involved_cats))
            # game.misc_events_list.append(text)

    def check_and_promote_leader(self):
        """ Checks if a new leader need to be promoted, and promotes them, if needed.  """
        # check for leader
        if game.clan.leader:
            leader_invalid = game.clan.leader.dead or game.clan.leader.outside
        else:
            leader_invalid = True

        if leader_invalid:
            self.perform_ceremonies(
                game.clan.leader
            )  # This is where the deputy will be make leader

            if game.clan.leader:
                leader_dead = game.clan.leader.dead
                leader_outside = game.clan.leader.outside
            else:
                leader_dead = True
                leader_outside = True

            if leader_dead or leader_outside:
                game.cur_events_list.insert(
                    0, Single_Event(f"{game.clan.name}Clan has no leader!"))

    def check_and_promote_deputy(self):
        """Checks if a new deputy needs to be appointed, and appointed them if needed. """
        if (not game.clan.deputy or game.clan.deputy.dead
                or game.clan.deputy.outside or game.clan.deputy.status == "elder"):
            if game.settings.get('deputy'):

                # This determines all the cats who are eligible to be deputy.
                possible_deputies = list(
                    filter(
                        lambda x: not x.dead and not x.outside and x.status ==
                                  "warrior" and (x.apprentice or x.former_apprentices),
                        Cat.all_cats_list))

                # If there are possible deputies, choose from that list.
                if possible_deputies:
                    random_cat = random.choice(possible_deputies)
                    involved_cats = [random_cat.ID]

                    # Gather deputy and leader status, for determination of the text.
                    if game.clan.leader:
                        if game.clan.leader.dead or game.clan.leader.outside:
                            leader_status = "not_here"
                        else:
                            leader_status = "here"
                    else:
                        leader_status = "not_here"

                    if game.clan.deputy:
                        if game.clan.deputy.dead or game.clan.deputy.outside:
                            deputy_status = "not_here"
                        else:
                            deputy_status = "here"
                    else:
                        deputy_status = "not_here"

                    if leader_status == "here" and deputy_status == "not_here":

                        if random_cat.personality.trait == 'bloodthirsty':
                            text = f"{random_cat.name} has been chosen as the new deputy. " \
                                   f"They look at the Clan leader with an odd glint in their eyes."
                            # No additional involved cats
                        else:
                            if game.clan.deputy:
                                previous_deputy_mention = random.choice([
                                    f"They know that {game.clan.deputy.name} would approve.",
                                    f"They hope that {game.clan.deputy.name} would approve.",
                                    f"They don't know if {game.clan.deputy.name} would approve, "
                                    f"but life must go on. "
                                ])
                                involved_cats.append(game.clan.deputy.ID)

                            else:
                                previous_deputy_mention = ""

                            text = f"{game.clan.leader.name} chooses " \
                                   f"{random_cat.name} to take over " \
                                   f"as deputy. " + previous_deputy_mention

                            involved_cats.append(game.clan.leader.ID)
                    elif leader_status == "not_here" and deputy_status == "here":
                        text = f"The Clan is without a leader, but a " \
                               f"new deputy must still be named.  " \
                               f"{random_cat.name} is chosen as the new deputy. " \
                               f"The retired deputy nods their approval."
                    elif leader_status == "not_here" and deputy_status == "not_here":
                        text = f"Without a leader or deputy, the Clan has been directionless. " \
                               f"They all turn to {random_cat.name} with hope for the future."
                    elif leader_status == "here" and deputy_status == "here":
                        possible_events = [
                            f"{random_cat.name} has been chosen as the new deputy. "  # pylint: disable=line-too-long
                            f"The Clan yowls their name in approval.",  # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. "  # pylint: disable=line-too-long
                            f"Some of the older Clan members question the wisdom in this choice.",
                            # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. "  # pylint: disable=line-too-long
                            f"They hold their head up high and promise to do their best for the Clan.",
                            # pylint: disable=line-too-long
                            f"{game.clan.leader.name} has been thinking deeply all day who they would "  # pylint: disable=line-too-long
                            f"respect and trust enough to stand at their side, and at sunhigh makes the "  # pylint: disable=line-too-long
                            f"announcement that {random_cat.name} will be the Clan's new deputy.",
                            # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. They pray to "  # pylint: disable=line-too-long
                            f"StarClan that they are the right choice for the Clan.",  # pylint: disable=line-too-long
                            f"{random_cat.name} has been chosen as the new deputy. Although"  # pylint: disable=line-too-long
                            f"they are nervous, they put on a brave front and look forward to serving"  # pylint: disable=line-too-long
                            f"the clan.",
                        ]
                        # No additional involved cats
                        text = random.choice(possible_events)
                    else:
                        # This should never happen. Failsafe.
                        text = f"{random_cat.name} becomes deputy. "
                else:
                    # If there are no possible deputies, choose someone else, with special text.
                    all_warriors = list(
                        filter(
                            lambda x: not x.dead and not x.outside and x.status
                                      == "warrior", Cat.all_cats_list))
                    if all_warriors:
                        random_cat = random.choice(all_warriors)
                        involved_cats = [random_cat.ID]
                        text = f"No cat is truly fit to be deputy, " \
                               f"but the position can't remain vacant. " \
                               f"{random_cat.name} is appointed as the new deputy. "

                    else:
                        # Is there are no warriors at all, no one is named deputy.
                        game.cur_events_list.append(
                            Single_Event(
                                "There are no cats fit to become deputy. ",
                                "ceremony"))
                        return

                random_cat.status_change("deputy")
                game.clan.deputy = random_cat

                game.cur_events_list.append(
                    Single_Event(text, "ceremony", involved_cats))

            else:
                game.cur_events_list.insert(
                    0, Single_Event(f"{game.clan.name}Clan has no deputy!"))

events_class = Events()
