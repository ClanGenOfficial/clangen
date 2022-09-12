from .cats import *
from .buttons import *


class Events(object):
    all_events = {}

    def __init__(self, e_type=None, **cats):
        self.e_type = e_type
        self.ID = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9))
        if e_type is not None:
            # Leave "e_type" empty for example class
            self.all_events[self.ID] = self
        self.cats = cats
        self.at_war = False
        self.time_at_war = False
        self.enemy_clan = None
        self.living_cats = 0
        self.new_cat_invited = False

    def one_moon(self):
        if game.switches['timeskip']:
            game.switches['save_clan'] = False
            self.living_cats = 0
            self.new_cat_invited = False
            game.patrolled.clear()
            for cat in cat_class.all_cats.copy().values():
                if not cat.dead and not cat.exiled:
                    self._extracted_from_one_moon_7(cat)
                elif cat.exiled:
                    cat.moons+=1
                    if cat.moons == 6:
                        cat.age = 'adolescent'
                    elif cat.moons == 12:
                        cat.age = 'adult'
                    elif cat.moons == 100:
                        cat.age = 'elder'
                    if cat.moons > randint(100,200):
                        if choice([1, 2, 3, 4, 5]) == 1:
                            cat.dead = True
                    if cat.exiled and cat.status == 'leader' and randint(1, 10) == 1:
                        game.clan.leader_lives -= 1
                        if game.clan.leader_lives <= 0:
                            cat.dead = True
                            game.clan.leader_lives = 0
                    elif cat.exiled and cat.status == 'leader' and randint(1, 45) == 1:
                        game.clan.leader_lives -= 10
                        cat.dead = True
                        game.clan.leader_lives = 0
                else:
                    cat.dead_for += 1
            # interaction here so every cat may have got a new name 
            for cat in cat_class.all_cats.copy().values(): 
                if not cat.dead and not cat.exiled:
                    self.create_interaction(cat)
            cat_class.thoughts()
            self.check_clan_relations()
            game.clan.age += 1
            if game.settings.get('autosave') is True and game.clan.age % 5 == 0:
                cat_class.save_cats()
                game.clan.save_clan()
            game.clan.current_season = game.clan.seasons[game.clan.age % 12]
            game.event_scroll_ct = 0
            has_med = any(str(cat.status) in {"medicine cat", "medicine cat apprentice"} and not cat.dead and not cat.exiled for cat in cat_class.all_cats.values())

            if not has_med:
                game.cur_events_list.insert(0, f"{game.clan.name}Clan has no medicine cat!")
            if game.clan.deputy == 0 or game.clan.deputy is None or game.clan.deputy.dead or game.clan.deputy.exiled:
                game.cur_events_list.insert(0, f"{game.clan.name}Clan has no deputy!")
            if game.clan.leader.dead or game.clan.leader.exiled:
                game.cur_events_list.insert(0, f"{game.clan.name}Clan has no leader!")
        game.switches['timeskip'] = False

    # TODO Rename this here and in `one_moon`
    def _extracted_from_one_moon_7(self, cat):
        self.living_cats += 1
        cat.in_camp = 1
        self.perform_ceremonies(cat)
        self.handle_relationships(cat)
        if self.new_cat_invited == False or self.living_cats < 10:
            self.invite_new_cats(cat)
        self.have_kits(cat)
        self.other_interactions(cat)
        self.gain_scars(cat)
        self.handle_deaths(cat)
        self.check_age(cat)

    def check_clan_relations(self):
        if len(game.clan.all_clans) > 0 and randint(1,5) == 1:
            war_notice = ''
            for other_clan in game.clan.all_clans:
                if int(other_clan.relations) <= 7:
                    if randint(1,5) == 1 and self.time_at_war > 2:
                        self.at_war = False
                        self.time_at_war = 0
                        other_clan.relations = 10
                        game.cur_events_list.append('The war against ' + str(other_clan.name) + 'Clan has ended')
                    elif self.time_at_war == 0:
                        game.cur_events_list.append('The war against ' + str(other_clan.name) + 'Clan has begun')
                        self.time_at_war+=1
                    else:
                        self.enemy_clan = f'{str(other_clan.name)}Clan'
                        possible_text = [f'War rages between {game.clan.name}Clan and {other_clan.name}Clan', f'{other_clan.name}Clan has taken some of {game.clan.name}' + "Clan\'s territory",
                            f'{game.clan.name}Clan has claimed some of {other_clan.name}' + "Clan\'s territory",
                            f'{other_clan.name}Clan attempted to break into your camp during the war', f'The war against {other_clan.name}Clan continues',
                            f'{game.clan.name}Clan is starting to get tired of the war against {other_clan.name}Clan', f'{game.clan.name}Clan warriors plan new battle strategies for the war', f'{game.clan.name}Clan warriors reinforce the camp walls']
                        if game.clan.medicine_cat is not None:
                            possible_text.extend(['The medicine cats worry about having enough herbs to treat their clan\'s wounds'])
                        war_notice = choice(possible_text)
                        self.time_at_war+=1
                    break
                else:
                    self.at_war = False
                    r_num = choice([-1, 1])
                    other_clan.relations = str(int(other_clan.relations) + r_num)
            if war_notice:
                game.cur_events_list.append(war_notice)

    def perform_ceremonies(self, cat):
        if (game.clan.leader.dead or game.clan.leader.exiled) and game.clan.deputy is not None and not game.clan.deputy.dead:
            game.cur_events_list.append(str(game.clan.leader.name) + ' has lost their last life and has travelled to StarClan' )

            game.clan.new_leader(game.clan.deputy)
            game.clan.leader_lives += 9
            game.cur_events_list.append(f'{str(game.clan.deputy.name)} has been promoted to the new leader of the clan')
            game.clan.deputy = None
        if not cat.dead:
            cat.moons += 1
            if cat.status == 'deputy' and game.clan.deputy is None:
                game.clan.deputy = cat
            if cat.moons > cat_class.age_moons[cat.age][1]:
                if cat.age != 'elder':
                    cat.age = cat_class.ages[cat_class.ages.index(cat.age) + 1]
                if cat.status == 'kitten' and cat.age == 'adolescent':
                    cat.status_change('apprentice')
                    game.cur_events_list.append(f'{str(cat.name)} has started their apprenticeship')
                    cat.update_mentor()
                elif cat.status == 'apprentice' and cat.age == 'young adult':
                    self._extracted_from_perform_ceremonies_19(cat, 'warrior', ' has earned their warrior name')
                elif cat.status == 'medicine cat apprentice' and cat.age == 'young adult':
                    self._extracted_from_perform_ceremonies_19(cat, 'medicine cat', ' has earned their medicine cat name')
                    game.clan.new_medicine_cat(cat)
                elif cat.status == 'warrior' and cat.age == 'elder' and len(cat.apprentice) < 1:
                    cat.status_change('elder')
                    game.cur_events_list.append(f'{str(cat.name)} has retired to the elder den')
                elif cat.status == 'deputy' and cat.age == 'elder' and len(cat.apprentice) < 1:
                    cat.status_change('elder')
                    game.clan.deputy = None
                    game.cur_events_list.append(f'The deputy {str(cat.name)} has retired to the elder den')
            if cat.status in ['warrior', 'deputy'] and cat.age == 'elder' and len(cat.apprentice) < 1:
                cat.status_change('elder')
                if cat.status == 'deputy':
                    game.clan.deputy = None
                game.cur_events_list.append(f'{str(cat.name)} has retired to the elder den')

    # TODO Rename this here and in `perform_ceremonies`
    def _extracted_from_perform_ceremonies_19(self, cat, arg1, arg2):
        cat.status_change(arg1)
        cat.update_mentor()
        game.cur_events_list.append(f'{str(cat.name)}{arg2}')

    def gain_scars(self, cat):
        if cat.specialty is not None and cat.specialty2 is not None or cat.age == 'kitten':
            return
        name = str(cat.name)
        other_cat = choice(list(cat_class.all_cats.values()))
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(cat_class.all_cats.values()))
        other_name = str(other_cat.name)
        scar_text = []
        if cat.age in ['adolescent', 'young adult']:
            chance = randint(0, 50)
        elif cat.age in ['adult', 'senior adult']:
            chance = randint(0, 70)
        elif cat.age in ['aprentice', 'medicine cat apprentice'] and cat.mentor.ID == other_cat.ID and other_cat.trait in ['bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'cold',
                                                                                                                            'tough', 'clumsy', 'controlling', 'fierce', 'petty', 'strict']:
            chance = randint(0, 20)
        elif other_cat.status in ['leader', 'deputy'] and other_cat.trait in ['bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'cold', 'tough', 'clumsy', 'controlling', 'fierce', 'petty', 'strict']:
            chance = randint(0, 30) 
        else:
            chance = randint(0, 90)
        if chance == 1:
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2), choice(scars4), choice(scars5)])
                if cat.specialty == 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']))
                elif cat.specialty == 'SNAKE':
                    scar_text.append(f'{name} was bit by a snake but lived')
                elif cat.specialty == 'TOETRAP':
                    scar_text.append(f'{name} got their paw stuck in a twoleg trap and earned a scar')
                else:
                    scar_text.extend([f'{name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                        f'{name} earned a scar defending the territory', f'{name} earned a scar protecting the kits', f'{name} is injured after falling into a river',
                                        f'{name} is injured by enemy warriors after accidentally wandering over the border', f'{name} is injured after messing with a twoleg object'])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2), choice(scars4), choice(scars5)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']))
                elif cat.specialty == 'SNAKE':
                    scar_text.append(f'{name} was bit by a snake but lived')
                elif cat.specialty == 'TOETRAP':
                    scar_text.append(f'{name} got their paw stuck in a twoleg trap and earned a scar')
                else:
                    scar_text.extend([f'{name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                        f'{name} earned a scar defending the territory', f'{name} earned a scar protecting the kits', f'{name} is injured after falling into a river',
                                        f'{name} is injured by enemy warriors after accidentally wandering over the border', f'{name} is injured after messing with a twoleg object',
                                        f'{name} is injured after a fight broke out with ' + other_name])
                                        

        elif chance == 1 and cat.status in ['aprentice', 'medicine cat apprentice'] and cat.mentor.ID == other_cat.ID and other_cat.trait in ['bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'cold', 'tough',
                                                                                                                                                'clumsy', 'controlling', 'fierce', 'petty', 'strict']:
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    scar_text.append(f'{name} recklessly lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']) + ' encouraged by their mentor')
                else:
                    scar_text.extend([f'{name} earned a scar  recklessly fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']) + ' encouraged by their mentor',
                                            f'{name} earned a scar for not defending the territory well enough', f'{name} earned a scar protecting the kits', f'{name} is injured after being pushed into a river',
                                            f'{name} is punished by their mentor after accidentally wandering over the border', f'{name} is injured by their mentor after being caught messing with a twoleg object'
                                            f'{name} is injured by their mentor while practicing with their claws out', f'{name}\' mentor punished them for disobeying', f'{name} gained a scar while fighting their mentor',
                                            f'{name} is injured while practicing their batle moves with ' + other_name, f'{name} is injured after a fight broke out with ' + other_name,
                                            f'{name} could not handle their mentor\'s harsh training and got injured as a result', f'{name} could not handle their mentor\'s harsh training and got injured as a result'])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']) + ' encouraged by their mentor')
                else:
                    scar_text.extend([f'{name} earned a scar recklessly fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']) + ' encouraged by their mentor',
                                            f'{name} earned a scar for not defending the territory well enough', f'{name} earned a scar protecting the kits', f'{name} is injured after being pushed into a river',
                                            f'{name} is punished by their mentor after accidentally wandering over the border', f'{name} is injured by their mentor after being caught messing with a twoleg object'
                                            f'{name} is injured by their mentor while practicing with their claws out', f'{name}\' mentor punished them for disobeying', f'{name} gained a scar while fighting their mentor',
                                            f'{name} is injured while practicing their batle moves with ' + other_name, f'{name} is injured after a fight broke out with ' + other_name,
                                            f'{name} could not handle their mentor\'s harsh training and got injured as a result'])
                                      
        elif chance == 1 and cat.status in ['warrior', 'deputy', 'medicine cat'] and other_cat.status == 'leader':
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']) + ' while following orders')
                else:
                    scar_text.extend([f'While following orders {name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                            f'{name} earned a scar defending the territory from outsiders', f'{name} earned a scar protecting the leader', f'{name} is injured after falling into a river',
                                            f'{name} is injured by enemy warriors after being ordered to go over the border', f'{name} is injured after being ordered to check out a twoleg object'])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']) + ' while following orders')
                else:
                    scar_text.extend([f'While following orders {name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                            f'{name} earned a scar defending the territory from outsiders', f'{name} earned a scar protecting the leader', f'{name} is injured after falling into a river',
                                            f'{name} is injured by enemy warriors after being ordered to go over the border', f'{name} is injured after being ordered to check out a twoleg object'])
                                            
        elif chance == 1 and other_cat.status == 'leader' and other_cat.trait in ['bloodthirsty', 'ambitious', 'vengeful', 'sadistic', 'controlling', 'fierce', 'petty']:
            if cat.specialty is None:
                cat.specialty = choice([choice(scars1), choice(scars2)])
                if cat.specialty == 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']) + ' while following orders')
                else:
                    scar_text.extend([f'While following orders {name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                            f'{name} earned a scar defending the territory from outsiders', f'{name} earned a scar protecting the leader', f'{name} is injured after falling into a river',
                                            f'{name} is injured by enemy warriors after being ordered to go over the border', f'{name} is injured after being ordered to check out a twoleg object',
                                            f'{name} is injured while fighting a clanmate encouraged by ' + other_name, f'{name} is injured by ' + other_name + ' for disobeying orders',
                                            f'{name} is injured by ' + other_name + ' for speaking out against them', f'{name} is cruelly injured by ' + other_name + ' to make an example out of them'])
            elif cat.specialty2 is None:
                cat.specialty2 = choice([choice(scars1), choice(scars2)])
                if cat.specialty2 == 'NOTAIL' and cat.specialty != 'NOTAIL':
                    scar_text.append(f'{name} lost their tail to a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger', 'tree', 'twoleg trap']) + ' while following orders')
                else:
                    scar_text.extend([f'While following orders {name} earned a scar fighting a ' + choice(['rogue', 'dog', 'fox', 'otter', 'rat', 'hawk', 'enemy warrior', 'badger']),
                                            f'{name} earned a scar defending the territory from outsiders', f'{name} earned a scar protecting the leader', f'{name} is injured after falling into a river',
                                            f'{name} is injured by enemy warriors after being ordered to go over the border', f'{name} is injured after being ordered to check out a twoleg object',
                                            f'{name} is injured while fighting a clanmate encouraged by ' + other_name, f'{name} is injured by ' + other_name + ' for disobeying orders',
                                            f'{name} is injured by ' + other_name + ' for speaking out against them', f'{name} is cruelly injured by ' + other_name + ' to make an example out of them']) 

        if scar_text:
            game.cur_events_list.append(choice(scar_text))

    def handle_relationships(self, cat):
        if randint(1, 100) == 1 and cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice', 'medicine cat'] and cat.age in ['young adult', 'adult', 'senior adult'] and cat.mate is None:
            other_cat = choice(list(cat_class.all_cats.values()))
            parents = [cat.ID]
            if cat.parent1 is not None:
                parents.append(cat.parent1)
                if cat.parent2 is not None:
                    parents.append(cat.parent2)
            other_parents = [other_cat.ID]
            if other_cat.parent1 is not None:
                other_parents.append(other_cat.parent1)
                if other_cat.parent2 is not None:
                    other_parents.append(other_cat.parent2)
            count = 0
            while cat == other_cat or other_cat.dead or other_cat.exiled or other_cat.status in [
            'kitten', 'apprentice', 'medicine cat apprentice', 'medicine cat'] or other_cat.age not in ['young adult', 'adult', 'senior adult'] or other_cat.mate is not None or other_cat.ID in cat.former_apprentices or cat.ID in other_cat.former_apprentices or not set(parents).isdisjoint(set(other_parents)):
                other_cat = choice(list(cat_class.all_cats.values()))
                other_parents = [other_cat.ID]
                if other_cat.parent1 is not None:
                    other_parents.append(other_cat.parent1)
                    if other_cat.parent2 is not None:
                        other_parents.append(other_cat.parent2)
                count += 1
                if count == 5:
                    return
            game.cur_events_list.append(f'{str(cat.name)} and {str(other_cat.name)} have become mates') 
            cat.mate = other_cat.ID
            other_cat.mate = cat.ID

            # affect relationship
            cat_relationship = list(filter(lambda r: r.cat_to.ID == other_cat.ID , cat.relationships))
            if cat_relationship is not None and len(cat_relationship) > 0:
                cat_relationship[0].romantic_love = 20
                cat_relationship[0].comfortable = 20
                cat_relationship[0].trust = 10
            else:
                cat.relationships.append(Relationship(cat,other_cat,True))
            
            ohter_cat_relationship = list(filter(lambda r: r.cat_to.ID == cat.ID , other_cat.relationships))
            if ohter_cat_relationship is not None and len(ohter_cat_relationship) > 0:
                ohter_cat_relationship[0].romantic_love = 20
                ohter_cat_relationship[0].comfortable = 20
                ohter_cat_relationship[0].trust = 10
            else:
                other_cat.relationships.append(Relationship(other_cat,cat,True))
                    
        elif randint(1, 50) == 1:
            other_cat = choice(list(cat_class.all_cats.values()))
            if cat.mate == other_cat.ID:
                game.cur_events_list.append(f'{str(cat.name)} and {str(other_cat.name)} have broken up')
                cat.mate = None
                other_cat.mate = None
        elif randint(1, 50) == 1:
            other_cat = choice(list(cat_class.all_cats.values()))
            if cat.mate == other_cat.ID and other_cat.dead == True:
                game.cur_events_list.append(f'{str(cat.name)} will always love {str(other_cat.name)} but has decided to move on')
                cat.mate = None
                other_cat.mate = None

    def invite_new_cats(self, cat):
        chance = 100
        if self.living_cats < 10:
            chance = 100
        elif self.living_cats > 50:
            chance = 700
        elif self.living_cats > 30:
            chance = 300
        if randint(1, chance) == 1 and cat.age != 'kitten' and cat.age != 'adolescent':
            self.new_cat_invited = True
            name = str(cat.name)
            type_of_new_cat = choice([1, 2, 3, 4, 5, 6, 7])
            if type_of_new_cat == 1:
                kit = Cat(moons=0)
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat,kit))
                    relationships.append(Relationship(kit,the_cat))
                kit.relationships = relationships
                game.clan.add_cat(kit)
                kit_text = [f'{name} finds an abandoned kit and names them {str(kit.name)}',
                            f'A loner brings their kit named {str(kit.name.prefix)} to the clan, stating they no longer can care for them']
                game.cur_events_list.append(choice(kit_text))
                self.check_age(kit)

            elif type_of_new_cat == 2:
                self._extracted_from_invite_new_cats_19(name)

            elif type_of_new_cat == 3:
                loner = Cat(status='warrior', moons=randint(12, 120))
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat,loner))
                    relationships.append(Relationship(loner,the_cat))
                loner.relationships = relationships
                loner.skill = 'formerly a loner'
                game.clan.add_cat(loner)
                loner_text = [f'{name} finds a loner who joins the clan', f'A loner says that they are interested in clan life and joins the clan']
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append('The loner changes their name to ' + str(loner.name))
                self.check_age(loner)

            elif type_of_new_cat == 4:
                warrior = Cat(status='warrior', moons=randint(12, 150))
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat, warrior))
                    relationships.append(Relationship(warrior,the_cat))
                warrior.relationships = relationships
                game.clan.add_cat(warrior)
                warrior_text = []
                if len(game.clan.all_clans) > 0:
                    warrior_text.extend([f'{name} finds a warrior from {str(choice(game.clan.all_clans).name)}Clan named {str(warrior.name)} who asks to join the clan',
                                         f'An injured warrior from {str(choice(game.clan.all_clans).name)}Clan asks to join in exchange for healing'])
                else:
                    warrior_text.extend([f'{name} finds a warrior from a different clan named {str(warrior.name)} who asks to join the clan'])
                game.cur_events_list.append(choice(warrior_text))
                self.check_age(warrior)

            elif type_of_new_cat == 5:
                self._extracted_from_invite_new_cats_47(name)
            elif type_of_new_cat == 6:
                loner = Cat(status='warrior', moons=randint(12, 120))
                #create and update relationships
                relationships = []
                for cat_id in game.clan.clan_cats:
                    the_cat = cat_class.all_cats.get(cat_id)
                    if the_cat.dead or the_cat.exiled:
                        continue
                    the_cat.relationships.append(Relationship(the_cat,loner))
                    relationships.append(Relationship(loner,the_cat))
                loner.relationships = relationships
                self._extracted_from_invite_new_cats_59(loner)
                loner_text = [f'{name} finds a kittypet named {choice(names.loner_names)} who wants to join the clan']
                game.cur_events_list.append(choice(loner_text))
                game.cur_events_list.append('The kittypet changes their name to ' + str(loner.name))
                self.check_age(loner)
                
            elif type_of_new_cat == 7:
                parent1 = cat.name
                kits = choice([1, 1, 2, 2, 2, 3])
                for kit in range(kits):
                    if cat.mate is not None:
                        kit = Cat(parent1=cat.ID, parent2=cat.mate, moons=0)
                        game.clan.add_cat(kit)
                        #create and update relationships
                        relationships = []
                        for cat_id in game.clan.clan_cats:
                            the_cat = cat_class.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if the_cat.ID in [kit.parent1, kit.parent2]:
                                the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                                relationships.append(Relationship(kit,the_cat,False,True))
                            else:
                                the_cat.relationships.append(Relationship(the_cat,kit))
                                relationships.append(Relationship(kit,the_cat))
                        kit.relationships = relationships
                    else:
                        kit = Cat(parent1=cat.ID, moons=0)
                        #create and update relationships
                        relationships = []
                        for cat_id in game.clan.clan_cats:
                            the_cat = cat_class.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if the_cat.ID == kit.parent1:
                                the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                                relationships.append(Relationship(kit,the_cat,False,True))
                            else:
                                the_cat.relationships.append(Relationship(the_cat,kit))
                                relationships.append(Relationship(kit,the_cat))
                        kit.relationships = relationships
                        game.clan.add_cat(kit)
                if len(game.clan.all_clans) > 0:
                    Akit_text = ([f'{parent1} finds an abandoned litter and decides to adopt them',
                                    f'A loner leaves their litter to the clan. {str(parent1)} decides to adopt them as their own',
                                    f'A {str(choice(game.clan.all_clans).name)}Clan queen decides to leave their litter with you. {str(parent1)} adopts them'])
                else:
                    Akit_text = ([f'{parent1} finds an abandoned litter and decides to adopt them as their own',
                                    f'A loner leaves their litter to the clan. {str(parent1)} decides to adopt them as their own'])
                game.cur_events_list.append(choice(Akit_text))
                self.check_age(kit) 

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_59(self, loner):
        loner.skill = 'formerly a kittypet'
        if choice([1, 2]) == 1:
            loner.specialty2 = choice(scars3)
        game.clan.add_cat(loner)
        self.check_age(loner)

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_47(self, name):
        loner_name = choice(names.loner_names)
        loner = Cat(prefix=loner_name, gender=choice(['female', 'male']), status='warrior', moons=randint(12, 120), suffix='')
        #create and update relationships
        relationships = []
        for cat_id in game.clan.clan_cats:
            the_cat = cat_class.all_cats.get(cat_id)
            if the_cat.dead or the_cat.exiled:
                continue
            the_cat.relationships.append(Relationship(the_cat,loner))
            relationships.append(Relationship(loner,the_cat))
        loner.relationships = relationships
        self._extracted_from_invite_new_cats_59(loner)
        loner_text = [f'{name} finds a kittypet named {str(loner_name)} who wants to join the clan', f'A kittypet named {str(loner_name)} stops {name} and asks to join the clan']
        game.cur_events_list.append(choice(loner_text))
        game.cur_events_list.append(str(loner_name) + ' decides to keep their name')

    # TODO Rename this here and in `invite_new_cats`
    def _extracted_from_invite_new_cats_19(self, name):
        loner_name = choice(names.loner_names)
        loner = Cat(prefix=loner_name, gender=choice(['female', 'male']), status='warrior', moons=randint(12, 120), suffix='')
        loner.skill = 'formerly a loner'
        #create and update relationships
        relationships = []
        for cat_id in game.clan.clan_cats:
            the_cat = cat_class.all_cats.get(cat_id)
            if the_cat.dead or the_cat.exiled:
                continue
            the_cat.relationships.append(Relationship(the_cat,loner))
            relationships.append(Relationship(loner,the_cat))
        loner.relationships = relationships
        game.clan.add_cat(loner)
        loner_text = [f'{name} finds a loner named {str(loner.name)} who joins the clan',
                      f'A loner named {str(loner.name)} waits on the border for a patrol, asking to join the clan']
        game.cur_events_list.append(choice(loner_text))
        game.cur_events_list.append(str(loner_name) + ' decides to keep their name')
        self.check_age(loner)

    def other_interactions(self, cat):
        if randint(1, 100) != 1:
            return
        interactions = []
        other_cat = choice(list(cat_class.all_cats.values()))
        while cat == other_cat or other_cat.dead or other_cat.exiled:
            other_cat = choice(list(cat_class.all_cats.values()))
        name = str(cat.name)
        other_name = str(other_cat.name)
        if cat.status in ['warrior', 'deputy'] and randint(1, 4) == 1 and game.settings.get('retirement') is True:
            game.cur_events_list.append(f'{name} retires to the elders den after injuries sustained defending {other_name}')
            cat.status_change('elder')
            return
        if cat.status == 'kitten':
            interactions.extend([f'{name} is scolded after sneaking out of camp', f'{name} falls into a river but is saved by {other_name}'])
        elif cat.status in ['apprentice', 'medicine cat apprentice']:
            interactions.extend([f'{name} is scolded after sneaking out of camp', f'{name} falls into a river but is saved by {other_name}',
                                 name + " accidentally trespasses onto another clan\'s territory"])
            if other_cat.status == 'apprentice':
                interactions.append(f'{name} sneaks out of camp with {other_name}')
        elif cat.status == 'warrior':
            interactions.extend([name + " is caught outside of the Clan\'s territory", f'{name} is caught breaking the Warrior Code', f'{name} went missing for a few days',
                                 f'{name} believes they are a part of the new prophecy'])
        elif cat.status == 'medicine cat':
            interactions.extend(
                [f'{name} learns of a new prophecy', f'{name} is worried about an outbreak of greencough', f'{name} is worried about how low their herb stores has gotten',
                 f'{name} visits the other medicine cats'])
        elif cat.status == 'deputy':
            interactions.extend([f'{name} thinks about retiring', f'{name} travels to the other clans to bring them an important message'])
        elif cat.status == 'leader':
            if game.clan.leader_lives <= 5:
                interactions.extend(
                    [f'{name} thinks about retiring', name + " confesses they don\'t have many lives left"])
            if other_cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice']:
                interactions.append(f'{name} confesses to {other_name} that the responsibility of leadership is crushing them')
            elif other_cat.status == 'apprentice':
                interactions.append(f'{name} assesses {other_name}' + "\'s progress")
            interactions.extend([f'{name} calls a clan meeting to give an important announcement'])
        elif cat.status == 'elder':
            interactions.extend([f'{name} is brought back to camp after wandering off'])
        if cat.age == other_cat.age:
            interactions.extend([f'{name} tries to convince {other_name} to run away together'])

        game.cur_events_list.append(choice(interactions))

    def handle_deaths(self, cat):
        #Leader lost a life EVENTS
        if randint(1, 100) == 1:
            name = str(cat.name)
            other_cat = choice(list(cat_class.all_cats.values()))
            while cat == other_cat or other_cat.dead or other_cat.status == 'leader' or other_cat.exiled:
                other_cat = choice(list(cat_class.all_cats.values()))
            other_name = str(other_cat.name)
            if cat.status == 'leader':
                cause_of_death = [name + ' lost a life after falling into a river', name + ' lost a life due to greencough', name + ' lost a life due to whitecough', 'Lightning fell in camp and ' + name + ' lost a life', name + ' was mortally wounded by a fox',
                                    name + ' lost a life to a dog', name + ' lost a life to a badger', name + ' lost a life to a hawk', name + ' lost a life due to yellowcough', name + ' lost a life while fighting off a rogue',
                                    name + ' lost a life to an eagle', name + ' was grabbed and dropped by an eagle, losing a life', name + ' was grabbed and dropped by a hawk, losing a life', name + ' lost a life after being swept away by a flood',
                                    name + ' lost a life after falling off a tree', name + ' was bit by a venomous spider and lost a life', name + ' was bit by a venomous snake and lost a life', name + ' ate poisoned fresh-kill and lost a life',
                                    name + ' failed to interpret a warning sign from StarClan and lost a life as a result', name + ' lost a life defending ' + other_name + ' from a dog', name + ' lost a life defending ' + other_name + ' from a badger',
                                    name + ' lost a life defending ' + other_name + ' from a fox', name + ' lost a life defending ' + other_name + ' from a hawk', name + ' lost a life defending ' + other_name + ' from an eagle',
                                    name + ' lost a life while saving ' + other_name + ' from drowning', name + ' lost a life while saving ' + other_name + ' from a monster', name + ' was pushed under a monster and lost a life']
                if len(game.clan.all_clans) > 0:
                    cause_of_death.extend([name + ' lost a life defending the kits from ' + choice(game.clan.all_clans).name + 'Clan warriors', name + ' lost a life defending ' + other_name + ' from ' + choice(game.clan.all_clans).name + 'Clan warriors',
                                        name + ' lost a life to a ' + choice(game.clan.all_clans).name + 'Clan apprentice', name + ' lost a life to a ' + choice(game.clan.all_clans).name + 'Clan warrior']) 
                game.clan.leader_lives -= 1
                self.dies(cat)
                game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons) + ' moons old')
            
        elif randint(1, 200) == 1 and cat.status == 'leader': #Several/All Lives loss
            name = str(cat.name)
            allorsome = randint(1, 10)
            if cat.status == 'leader':
                if allorsome == 1:
                    cause_of_death = [name + ' was brutally attacked by a rogue and lost all of their lives', name + ' was mauled by dogs and lost all of their lives', name + ' was carried off by an eagle, never to be seen again',
                                            name + ' was carried off by a hawk, never to be seen again', name + ' was taken by twolegs, never to be seen again', name + ' fell into a river and was swept away by the current, never to be seen again',
                                            name + ' was burnt alive while trying to save their clanmates from a fire']
                    if self.at_war and len(game.clan.all_clans) > 0:
                        cause_of_death.extend([name + ' was brutally murdered by a ' + choice(game.clan.all_clans).name + 'Clan warrior and lost all of their lives', name + ' was brutally murdered by the ' + choice(game.clan.all_clans).name + 'Clan deputy and lost all of their lives',
                                                name + ' was brutally murdered by the ' + choice(game.clan.all_clans).name + 'Clan leader and lost all of their lives'])
                    if game.clan.biome == "Mountainous":
                        cause_of_death.extend([name + ' was buried alive in an avalanche', name + ' was buried alive by a landslide', name + ' was pushed off a cliff with sharp rocks at the bottom', name + ' accidentally fell off a cliff with sharp rocks at the bottom'])
                    if game.clan.biome == "Beach":
                        cause_of_death.extend([name + ' was washed out to sea and was never seen again', name + ' was lost to sea while saving a clanmate from drowning'])
                    if game.clan.biome == "Plains":
                        cause_of_death.extend([name + ' fell into a sinkhole and was never seen again', name + ' fell into a hidden burrow and was buried alive', name + ' was buried alive when a burrow collapsed on them'])
                    game.clan.leader_lives -= 10
                else:
                    lostlives = choice([2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6])
                    cause_of_death = [name + ' lost ' + str(lostlives) + ' lives due to greencough', name + ' lost ' + str(lostlives) + ' lives due to whitecough', name + ' lost ' + str(lostlives) + ' lives due to yellowcough', name + ' lost ' + str(lostlives) + ' lives due to an illness',
                                        name + ' lost ' + str(lostlives) + ' lives due to an infection']
                    game.clan.leader_lives = game.clan.leader_lives - lostlives
                self.dies(cat)
                game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons) + ' moons old')   
                
        elif randint(1, 400) == 1:
            name = str(cat.name)
            cause_of_death = [name + ' was murdered', name + ' died of greencough', 'A tree fell in camp and killed ' + name, name + ' was found dead near a fox den']
            if cat.status == 'kitten':
                cause_of_death.extend([name + ' fell into a river and drowned', name + ' was taken by a hawk', name + ' grew weak as the days passed and died',
                                       name + ' was killed after sneaking out of camp', name + ' died after accidentally eating deathberries', name + ' was killed in their sleep after a snake snuck into camp'])
                if game.clan.current_season == 'Leaf-bare':
                    cause_of_death.extend([name + ' was found dead in the snow', name + ' froze to death in a harsh snowstorm',
                                           name + ' disappeared from the nursery and was found dead in the territory', name + ' was playing on the ice when the ice cracked and they drowned'])
                if game.clan.current_season == 'Greenleaf':
                    cause_of_death.extend([name + ' died to overheating'])
            elif cat.status == 'apprentice':
                cause_of_death.extend([name + ' died in a training accident', name + ' was killed by enemy warriors after accidentally wandering over the border',
                                       name + ' went missing and was found dead', name + ' died in a border skirmish'])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([name + ' was crushed to death by an avalanche', name + ' fell from a cliff and died'])
                if game.clan.biome == "Beach":
                    cause_of_death.extend([name + ' was washed out to sea and drowned', name + ' was poisoned by a sea creature and died'])
            elif cat.status == 'warrior' or cat.status == 'deputy':
                if len(game.clan.all_clans) > 0:
                    cause_of_death.append(name + ' was found dead near the ' + choice(game.clan.all_clans).name + 'Clan border')
                cause_of_death.extend([name + ' died from infected wounds', name + ' went missing and was found dead'])
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by enemy ' + self.enemy_clan + ' warriors', name + ' was killed by enemy ' + self.enemy_clan + ' warriors',
                                           name + ' was killed by enemy ' + self.enemy_clan + ' warriors', name + ' died in a border skirmish'])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([name + ' was crushed by an avalanche', name + ' fell from a cliff and died'])
                if game.clan.biome == "Beach":
                    cause_of_death.extend([name + ' was washed out to sea and drowned', name + ' was poisoned by a sea creature and died'])
                if game.clan.biome == "Plains":
                    cause_of_death.extend([name + ' fell into a sinkhole and died', name + ' fell into a hidden burrow and could not get out', name + ' was buried alive when a burrow collapsed on them'])
            #Leader loses a life
            elif cat.status == 'leader':
                if len(game.clan.all_clans) > 0:
                    cause_of_death.append(name + ' was found dead near the ' + choice(game.clan.all_clans).name + 'Clan border mortally injured')
                    cause_of_death.extend([name + ' lost a life from infected wounds', name + ' went missing and was later found mortally wounded'])
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by enemy ' + self.enemy_clan + ' warriors and lost a life', name + ' was killed by enemy ' + self.enemy_clan + ' warriors and lost a life',
                                           name + ' was killed by enemy ' + self.enemy_clan + ' warriors and lost a life', name + ' lost a life in a border skirmish'])
                if game.clan.biome == "Mountainous":
                    cause_of_death.extend([name + ' lost a life in an avalanche', name + ' lost a life in a landslide', name + ' was pushed off a cliff and lost a life', name + ' accidentally fell off a cliff and lost a life'])
                elif game.clan.biome == "Beach":
                    cause_of_death.extend([name + ' was washed out to sea and lost a life', name + ' was poisoned by a sea creature and lost a life'])
                elif game.clan.biome == "Plains":
                    cause_of_death.extend([name + ' fell into a sinkhole and lost a life', name + ' fell into a hidden burrow and lost a life', name + ' lost a life when a burrow collapsed on them'])
                elif self.at_war:
                    cause_of_death.extend([name + ' was killed by the ' + self.enemy_clan + ' deputy and lost a life', name + ' was killed by the ' + self.enemy_clan + ' leader and lost a life'])
                    
            elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
                cause_of_death.extend(['The herb stores were damaged and ' + name + ' was murdered by an enemy warrior'])
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by a ' + self.enemy_clan + ' warrior while pulling an injured cat out of the battlefield'])
            if cat.status == 'deputy':
                if self.at_war:
                    cause_of_death.extend([name + ' was killed by the ' + self.enemy_clan + ' deputy', name + ' was killed by the ' + self.enemy_clan + ' leader'])
                    
            if cat.status == 'leader':
                game.clan.leader_lives -= 1
            self.dies(cat)
            game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(cat.moons) + ' moons old')
            
        elif randint(1, 500) == 1:  # multiple deaths
            name = str(cat.name)
            other_cat = choice(list(cat_class.all_cats.values()))
            while cat == other_cat or other_cat.dead or other_cat.exiled:
                other_cat = choice(list(cat_class.all_cats.values()))
            other_name = str(other_cat.name)
            cause_of_death = [name + ' and ' + other_name + ' die of greencough', name + ' and ' + other_name + ' die of yellowcough', name + ' and ' + other_name + ' die of whitecough',
                              name + ' and ' + other_name + ' die from eating poisoned prey']
            if cat.status != 'kitten' or 'leader' and other_cat.status != 'kitten' or 'leader':
                cause_of_death.extend(
                    [name + ' and ' + other_name + ' are killed in a border skirmish', name + ' and ' + other_name + ' are killed in a battle against a gang of rogues'])
            if cat.mate is not None and cat.age == other_cat.age and other_cat.mate is None:
                if cat.status == 'leader':
                    game.clan.leader_lives -= 10
                game.cur_events_list.append(name + ' is killed by ' + other_name + ' in an argument over ' + str(cat_class.all_cats.get(cat.mate).name))
                self.dies(cat)

                return
            self.dies(cat)
            self.dies(other_cat)
            if cat.status != 'leader':
                game.cur_events_list.append(choice(cause_of_death))
            elif cat.status == 'leader' and other_cat.status != 'leader':
                game.clan.leader_lives -= 1
                game.cur_events_list.append(choice(cause_of_death) + ' and the leader lost a life')
            elif other_cat.status == 'leader' and cat.status != 'leader':
                game.clan.leader_lives -= 1
                game.cur_events_list.append(choice(cause_of_death) + ' and the leader lost a life')
                    
        elif randint(1, 5) == 1: #Death with Personalities
            murder_chance = 20
            name = str(cat.name)
            other_cat = choice(list(cat_class.all_cats.values()))
            while cat == other_cat or other_cat.dead or other_cat.exiled:
                other_cat = choice(list(cat_class.all_cats.values()))
            other_name = str(other_cat.name)
            if cat.trait in ['bloodthirsty', 'ambitious', 'vengeful', 'sneaky', 'sadistic', 'greedy', 'selfish'] and other_cat.status in ['leader', 'deputy']:
                if cat.status == 'deputy' and other_cat.status == 'leader':
                    if randint(1, murder_chance - 15) == 1:
                        cause_of_death = [name + ' murdered ' + other_name + ' in cold blood to take their place', name + ' murdered ' + other_name + ' to take their place and made it look like an accident']
                        game.clan.leader_lives -= 10
                        self.dies(other_cat)
                        game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(other_cat.moons)+ ' moons old')
                elif cat.status == 'warrior':
                    if randint(1, murder_chance - 15) == 1:
                        cause_of_death = [name + ' murdered ' + other_name + ' in cold blood in hopes of taking their place', name + ' murdered ' + other_name + ' in cold blood and made it look accidental in hopes of taking their place']
                        if other_cat == 'leader':
                            game.clan.leader_lives -= 10
                        self.dies(other_cat)
                        game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(other_cat.moons)+ ' moons old')
            elif cat.trait in ['bloodthirsty', 'vengeful', 'sadistic']:
                if randint(1, murder_chance) == 1:
                    cause_of_death = [name + ' murdered ' + other_name + ' in cold blood', name + ' murdered ' + other_name + ' in cold blood and made it look accidental']
                    if other_cat == 'leader':
                        game.clan.leader_lives -= 10
                    self.dies(other_cat)
                    game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(other_cat.moons)+ ' moons old')
            elif cat.status in ['medicine cat', 'medicine cat apprentice'] and cat.trait in ['bloodthirsty', 'vengeful', 'sadistic']:
                if randint(1, murder_chance) == 1:
                    cause_of_death = [name + ' killed ' + other_name + ' by giving them deathberries', name + ' killed ' + other_name + ' by giving them foxglove seeds', name + ' killed ' + other_name + ' by giving them nightshade berries',
                                    name + ' killed ' + other_name + ' by giving them water hemlock', name + ' killed ' + other_name + ' by consciously giving them the wrong herbs']
                    if other_cat == 'leader':
                        game.clan.leader_lives -= 10
                    self.dies(other_cat)
                    game.cur_events_list.append(choice(cause_of_death) + ' at ' + str(other_cat.moons)+ ' moons old')
        
        elif cat.moons > randint(150, 200):  # extra chance of cat dying to age
            if choice([1, 2, 3, 4, 5, 6]) == 1:
                if cat.status != 'leader':
                    self.dies(cat)
                    game.cur_events_list.append(str(cat.name) + ' has passed due to their old age at ' + str(cat.moons) + ' moons old')
                else:
                    game.clan.leader_lives -= 1
                    self.dies(cat)
                    game.cur_events_list.append(str(cat.name) + ' has lost a life due to their old age at ' + str(cat.moons) + ' moons old')
            if cat.status == 'leader' and cat.moons > 269:
                game.clan.leader_lives -= 10
                self.dies(cat)
                game.cur_events_list.append(str(cat.name) + ' has passed due to their old age at ' + str(cat.moons) + ' moons old')
                
        if game.settings.get('disasters') is True:
            alive_count = 0
            alive_cats = []
            for cat in list(cat_class.all_cats.values()):
                if not cat.dead:
                    alive_count += 1
                    alive_cats.append(cat)
            if alive_count > 10:
                chance = int(alive_count / 10)
                if randint(chance, 1000) == 999:
                    disaster = []
                    dead_cats = random.sample(alive_cats, 5)
                    name1 = str(dead_cats[0].name)
                    name2 = str(dead_cats[1].name)
                    name3 = str(dead_cats[2].name)
                    name4 = str(dead_cats[3].name)
                    name5 = str(dead_cats[4].name)
                    disaster.extend([' drown after the camp becomes flooded', ' are killed in a battle against ' + choice(names.normal_prefixes) + 'Clan',
                                     ' are killed after a fire rages through the camp', ' are killed in an ambush by a group of rogues', ' go missing in the night',
                                     ' are killed after a badger attack', ' die to a greencough outbreak', ' are taken away by twolegs', ' eat poisoned freshkill and die'])
                    if game.clan.current_season == 'Leaf-bare':
                        disaster.extend([' die after freezing from a snowstorm', ' starve to death when no prey is found'])
                    elif game.clan.current_season == 'Greenleaf':
                        disaster.extend([' die after overheating', ' die after the water dries up from drought'])

                    game.cur_events_list.append(name1 + ', ' + name2 + ', ' + name3 + ', ' + name4 + ', and ' + name5 + choice(disaster))
                    for cat in dead_cats:
                        if cat.status != 'leader':
                            self.dies(cat)
                        else:
                            game.clan.leader_lives -= 1
                            self.dies(cat)

    def dies(self, cat):  # This function is called every time a cat dies
        if cat.status == 'leader' and game.clan.leader_lives > 0:
            return
        if cat.status != 'leader':
            cat.dead = True
        elif cat.status == 'leader' and game.clan.leader_lives <= 0:
            cat.dead = True
            game.clan.leader_lives = 0
        if cat.mate != None:
            cat.mate = None
            if type(cat.mate) == str:
                mate = cat_class.all_cats.get(cat.mate)
                mate.mate = None
            elif type(cat.mate) == Cat:
                cat.mate.mate = None

        for app in cat.apprentice.copy():
            app.update_mentor()
        cat.update_mentor()
        game.clan.add_to_starclan(cat)

    def have_kits(self, cat):
        # decide chances of having kits, and if it's possible at all
        chance = 0
        for kit in cat_class.all_cats.values():
            if str(kit.status) == 'kitten' and kit.parent1 is not None and not kit.dead:
                if cat_class.all_cats.get(kit.parent1) == cat or cat_class.all_cats.get(kit.parent2) == cat:
                    return
        if cat.mate is not None:
            if cat.mate in cat.all_cats:
                if cat_class.all_cats[cat.mate].dead:
                    chance = 0
                elif cat_class.all_cats[cat.mate].gender != cat.gender and cat_class.all_cats[cat.mate].age != 'elder':
                    chance = 25
                elif game.settings['no gendered breeding'] and cat_class.all_cats[cat.mate].age != 'elder' and chance is not None:
                    chance = 25
                else:
                    chance = 0
            else:
                game.cur_events_list.append("Warning: " + str(cat.name) + " has an invalid mate #" + str(cat.mate) + ". This has been unset.")
                cat.mate = None
        else:
            chance = 50
            if not game.settings['no unknown fathers']:
                chance = 0

        if cat.age in ['kitten', 'adolescent', 'elder'] or cat.example or (not game.settings['no gendered breeding'] and cat.gender == 'male'):
            chance = 0

        # Decide randomly if kits will be born, if possible
        if chance != 0:
            hit = randint(0, chance)
            if self.living_cats > 50:
                hit = randint(0, chance + 20)
            elif self.living_cats < 10:
                hit = randint(0, chance - 10)
            kits = choice([1, 1, 2, 2, 3, 3, 4])
            if hit == 1 and cat.mate is not None:
                if not cat.no_kits and not cat_class.all_cats.get(cat.mate).no_kits:
                    if game.cur_events_list is not None:
                        game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)')
                    else:
                        game.cur_events_list = [str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)']

                    for kit in range(kits):
                        kit = Cat(parent1=cat.ID, parent2=cat.mate, moons=0)
                        #create and update relationships
                        relationships = []
                        for cat_id in game.clan.clan_cats:
                            the_cat = cat_class.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if the_cat.ID in [kit.parent1, kit.parent2]:
                                the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                                relationships.append(Relationship(kit,the_cat,False,True))
                            else:
                                the_cat.relationships.append(Relationship(the_cat,kit))
                                relationships.append(Relationship(kit,the_cat))
                        kit.relationships = relationships
                        game.clan.add_cat(kit)
            elif hit == 1 and not cat.no_kits:
                game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s)')

                for kit in range(kits):
                    kit = Cat(parent1=cat.ID, moons=0)
                    #create and update relationships
                    relationships = []
                    for cat_id in game.clan.clan_cats:
                        the_cat = cat_class.all_cats.get(cat_id)
                        if the_cat.dead or the_cat.exiled:
                            continue
                        if the_cat.ID is kit.parent1:
                            the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                            relationships.append(Relationship(kit,the_cat,False,True))
                        else:
                            the_cat.relationships.append(Relationship(the_cat,kit))
                            relationships.append(Relationship(kit,the_cat))
                    kit.relationships = relationships
                    game.clan.add_cat(kit)

    def check_age(self, cat):
        if 0 <= cat.moons <= 5:
            cat.age = 'kitten'
        elif 6 <= cat.moons <= 11:
            cat.age = 'adolescent'
        elif 12 <= cat.moons <= 47:
            cat.age = 'young adult'
        elif 48 <= cat.moons <= 95:
            cat.age = 'adult'
        elif 96 <= cat.moons <= 119:
            cat.age = 'senior adult'
        else:
            cat.age = 'elder'

    def create_interaction(self, cat):
        # if the cat has no relationships, skip
        if len(cat.relationships) < 1 or cat.relationships is None:
            return

        cats_to_choose = list(filter(lambda iter_cat_id: iter_cat_id != cat.ID, cat_class.all_cats.copy()))
        # increase chance of cats, which are already befriended
        like_threshold = 50
        relevant_relationships = list(filter(lambda relation: relation.platonic_like >= like_threshold, cat.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.platonic_like >= like_threshold * 2:
                cats_to_choose.append(relationship.cat_to)
        

        # increase chance of cats, which are already may be in love
        love_threshold = 40
        relevant_relationships = list(filter(lambda relation: relation.romantic_love >= love_threshold, cat.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.romantic_love >= love_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase the chance a kitten interact with other kittens
        if cat.age == "kitten":
            kittens = list(filter(lambda cat_id: cat.all_cats.get(cat_id).age == "kitten" and cat_id != cat.ID, cat_class.all_cats.copy()))
            cats_to_choose = cats_to_choose + kittens

        # increase the chance a apprentice interact with otherapprentices
        if cat.age == "adolescent":
            apprentices = list(filter(lambda cat_id: cat.all_cats.get(cat_id).age == "adolescent" and cat_id != cat.ID, cat_class.all_cats.copy()))
            cats_to_choose = cats_to_choose + apprentices

        # choose cat and start
        random_id = random.choice(list(cat.all_cats.keys()))
        relevant_relationship_list = list(filter(lambda relation: str(relation.cat_to) == str(random_id) and not relation.cat_to.dead, cat.relationships))
        while len(relevant_relationship_list) < 1 or random_id == cat.ID:
            random_id = random.choice(list(cat.all_cats.keys()))
            relevant_relationship_list = list(filter(lambda relation: str(relation.cat_to) == str(random_id) and not relation.cat_to.dead, cat.relationships))
        relevant_relationship = relevant_relationship_list[0]
        relevant_relationship.start_action()

        # self.relationship_outcome(relationship=relevant_relationship)

    def relationship_outcome(self, relationship):
        """Things that can happen, after relationship changes."""
        cat_from = relationship.cat_from
        cat_from_mate = None
        if cat_from.mate != None or cat_from.mate != '':
            cat_from_mate = cat_class.all_cats.get(cat_from.mate)
        
        cat_to = relationship.cat_to
        cat_to_mate = None
        if cat_to.mate != None or cat_to.mate != '':
            cat_to_mate = cat_class.all_cats.get(cat_to.mate)

        if relationship.opposit_relationship == None:
            relationship.link_relationship()

        # overcome dead mates
        if cat_from_mate != None and cat_from_mate.dead and randint(1, 20):
            game.cur_events_list.append(f'{str(cat_from.name)} will always love {str(cat_from_mate.name)} but has decided to move on')
            cat_from.mate = None
            cat_from_mate.mate = None
        if cat_to_mate != None and cat_to_mate.dead and randint(1, 20):
            game.cur_events_list.append(f'{str(cat_to.name)} will always love {str(cat_to_mate.name)} but has decided to move on')
            cat_to.mate = None
            cat_to_mate.mate = None

        # new mates
        both_no_mates = cat_to_mate == None and cat_from_mate == None
        # check ages of cats
        age_group1 = ['adolescent','young adult', 'adult']
        age_group2 = ['adult', 'senior adult', 'elder']
        both_in_same_age_group = (cat_from.age in age_group1 and cat_to.age in age_group1) or\
            (cat_from.age in age_group2 and cat_to.age in age_group2)
        random_mates = randint(1,200)
        if (relationship.romantic_love > 20 and relationship.opposit_relationship.romantic_love > 20 and both_no_mates)\
            or (random_mates == 1 and both_in_same_age_group):
            self.new_mates(cat_from, cat_to)
        
        # breakup and new mate
        if game.settings['affair'] and not relationship.mates and cat_from_mate != None:
            love_over_30 = relationship.romantic_love > 30 and relationship.opposit_relationship.romantic_love > 30
            normal_chance = randint(1,10)
            # compare love value of current mates
            bigger_than_current = False
            bigger_love_chance = randint(1,3)
            mate_relationship = list(filter(lambda r: r.cat_to.ID == cat_from.mate , cat_from.relationships))

            # check cat from value
            if mate_relationship is not None and len(mate_relationship) > 0:
                bigger_than_current = relationship.romantic_love > mate_relationship[0].romantic_love
            else:
                if cat_from_mate != None:
                    cat_from_mate.relationships.append(Relationship(cat_from, cat_from_mate, True))
                bigger_than_current = True

            # check cat to value
            if cat_to_mate != None:
                opposite_mate_relationship = list(filter(lambda r: r.cat_to.ID == cat_from.ID , cat_to.relationships))
                if opposite_mate_relationship is not None and len(opposite_mate_relationship) > 0:
                    bigger_than_current = bigger_than_current and relationship.romantic_love > opposite_mate_relationship[0].romantic_love
                else:
                    cat_to_mate.relationships.append(Relationship(cat_to, cat_to_mate, True))
                    bigger_than_current = bigger_than_current and True
            
            if (love_over_30 and normal_chance == 1) or (bigger_than_current and bigger_love_chance == 1):
                # break up the old relationships
                cat_from_mate = cat_class.all_cats.get(cat_from.mate)
                self.breakup(cat_from, cat_from_mate)

                if cat_to_mate != None:
                    self.breakup(cat_to, cat_to_mate)

                # new relationship
                game.cur_events_list.append(f'{str(cat_from.name)} and {str(cat_to.name)} can\'t ignore their feelings for each other')
                self.new_mates(cat_from, cat_to)

        # breakup
        if relationship.mates and 'negative' in relationship.effect:
            chance_number = 30
            if 'fight' in relationship.current_action_str:
                chance_number = 20
            chance = randint(0,chance_number)
            if chance == 1 or relationship.dislike > 20:
                self.breakup(cat_from,cat_to)

    def new_mates(self, cat1, cat2):
        # change cat 1
        cat1_relation = list(filter(lambda r: r.cat_to.ID == cat2.ID, cat1.relationships))
        cat1.mate = cat2.ID
        if cat1_relation is not None and len(cat1_relation) > 0:
            cat1_relation = cat1_relation[0]
            cat1_relation.mates = True
            cat1_relation.romantic_love += 15
            cat1_relation.comfortable += 10
            cat1_relation.trust += 10
        else:
            cat1.relationships.append(Relationship(cat1,cat2,True))

        # change cat 2
        cat2_relation = list(filter(lambda r: r.cat_to.ID == cat1.ID, cat2.relationships))
        cat2.mate = cat1.ID
        if cat2_relation is not None and len(cat2_relation) > 0:
            cat2_relation = cat2_relation[0]
            cat2_relation.mates = True
            cat2_relation.romantic_love += 15
            cat2_relation.comfortable += 10
            cat2_relation.trust += 10
        else:
            cat1.relationships.append(Relationship(cat1,cat2,True))

        game.cur_events_list.append(f'{str(cat1.name)} and {str(cat2.name)} have become mates')

    def breakup(self, cat1, cat2):
        # change cat 1
        cat1_relation = list(filter(lambda r: r.cat_to.ID == cat2.ID, cat1.relationships))
        cat1.mate = None
        if cat1_relation is not None and len(cat1_relation) > 0:
            cat1_relation = cat1_relation[0]
            cat1_relation.mates = False
            cat1_relation.romantic_love = 5
            cat1_relation.comfortable -= 20
            cat1_relation.trust -= 10
        else:
            cat1.relationships.append(Relationship(cat1,cat2))

        # change cat 2
        cat2_relation = list(filter(lambda r: r.cat_to.ID == cat1.ID, cat2.relationships))
        cat2.mate = None
        if cat2_relation is not None and len(cat2_relation) > 0:
            cat2_relation = cat2_relation[0]
            cat2_relation.mates = False
            cat2_relation.romantic_love = 5
            cat2_relation.comfortable -= 20
            cat2_relation.trust -= 10
        else:
            cat1.relationships.append(Relationship(cat1,cat2))

        game.cur_events_list.append(f'{str(cat1.name)} and {str(cat2.name)} broke up')

events_class = Events()
