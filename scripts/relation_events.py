from .cats import *

class Relation_Events(object):
    """All relationship events."""
    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: r.dead == False, cat_class.all_cats.copy().values())))
        pass

    def create_interaction(self, cat):
        # if the cat has no relationships, skip
        if len(cat.relationships) < 1 or cat.relationships is None:
            return

        cats_to_choose = list(
            filter(lambda iter_cat_id: iter_cat_id != cat.ID,
                   cat_class.all_cats.copy()))
        # increase chance of cats, which are already befriended
        like_threshold = 50
        relevant_relationships = list(
            filter(lambda relation: relation.platonic_like >= like_threshold,
                   cat.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.platonic_like >= like_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase chance of cats, which are already may be in love
        love_threshold = 40
        relevant_relationships = list(
            filter(lambda relation: relation.romantic_love >= love_threshold,
                   cat.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.romantic_love >= love_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase the chance a kitten interact with other kittens
        if cat.age == "kitten":
            kittens = list(
                filter(
                    lambda cat_id: cat.all_cats.get(cat_id).age == "kitten" and
                    cat_id != cat.ID, cat_class.all_cats.copy()))
            cats_to_choose = cats_to_choose + kittens

        # increase the chance a apprentice interact with otherapprentices
        if cat.age == "adolescent":
            apprentices = list(
                filter(
                    lambda cat_id: cat.all_cats.get(cat_id).age == "adolescent"
                    and cat_id != cat.ID, cat_class.all_cats.copy()))
            cats_to_choose = cats_to_choose + apprentices

        # choose cat and start
        random_id = random.choice(list(cat.all_cats.keys()))
        relevant_relationship_list = list(
            filter(
                lambda relation: str(relation.cat_to) == str(random_id) and
                not relation.cat_to.dead, cat.relationships))
        while len(relevant_relationship_list) < 1 or random_id == cat.ID:
            random_id = random.choice(list(cat.all_cats.keys()))
            relevant_relationship_list = list(
                filter(
                    lambda relation: str(relation.cat_to) == str(random_id) and
                    not relation.cat_to.dead, cat.relationships))
        relevant_relationship = relevant_relationship_list[0]
        relevant_relationship.start_action()

        self.relationship_outcome(relationship=relevant_relationship)

    def handle_relationships(self, cat):
        mate_chance = 50
        if self.living_cats > 60:
            mate_chance = mate_chance + 50
        elif self.living_cats > 120:
            mate_chance = mate_chance + 75
        elif self.living_cats > 300:
            mate_chance = mate_chance * 3
        elif self.living_cats > 500:
            mate_chance = mate_chance * 5

        hit = randint(1, mate_chance)
        if hit == 1:
            if cat.mate == None:
                for i in range(5): # Try assigning a random mate 5 times
                    other_cat = choice(list(cat_class.all_cats.values()))
                    if cat.is_potential_mate(other_cat) == False or other_cat.is_potential_mate(cat) == False:
                        continue
                    else:
                        cat.mate = other_cat.ID
                        other_cat.mate = cat.ID
                        game.cur_events_list.append(
                            f'{str(cat.name)} and {str(other_cat.name)} have become mates')
                        
        elif randint(1, 50) == 1:
            other_cat = choice(list(cat_class.all_cats.values()))
            if cat.mate == other_cat.ID and other_cat.dead == True:
                game.cur_events_list.append(
                    f'{str(cat.name)} will always love {str(other_cat.name)} but has decided to move on'
                )
                cat.mate = None
                other_cat.mate = None
        elif randint(1, 100) == 1:

            other_cat = choice(list(cat_class.all_cats.values()))
            if cat.mate == other_cat.ID:
                game.cur_events_list.append(
                    f'{str(cat.name)} and {str(other_cat.name)} have broken up'
                )
                cat.mate = None
                other_cat.mate = None

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
        if cat_from_mate != None and cat_from_mate.dead and randint(1, 30) == 1:
            game.cur_events_list.append(
                f'{str(cat_from.name)} will always love {str(cat_from_mate.name)} but has decided to move on'
            )
            cat_from.mate = None
            cat_from_mate.mate = None
        if cat_to_mate != None and cat_to_mate.dead and randint(1, 30) == 1:
            game.cur_events_list.append(
                f'{str(cat_to.name)} will always love {str(cat_to_mate.name)} but has decided to move on'
            )
            cat_to.mate = None
            cat_to_mate.mate = None

        # new mates
        if relationship.romantic_love > 20 and relationship.opposit_relationship.romantic_love > 20 and\
            cat_from.is_potential_mate(cat_to):
            self.new_mates(cat_from, cat_to)

        # breakup and new mate
        if cat_from.is_potential_mate(cat_to) and cat_from.mate is not None and cat_to.mate is not None:
            love_over_30 = relationship.romantic_love > 30 and relationship.opposit_relationship.romantic_love > 30
            normal_chance = randint(1, 20)
            # compare love value of current mates
            bigger_than_current = False
            bigger_love_chance = randint(1, 3)
            mate_relationship = list(
                filter(lambda r: r.cat_to.ID == cat_from.mate,
                       cat_from.relationships))

            # check cat from value
            if mate_relationship is not None and len(mate_relationship) > 0:
                bigger_than_current = relationship.romantic_love > mate_relationship[
                    0].romantic_love
            else:
                if cat_from_mate != None:
                    cat_from_mate.relationships.append(
                        Relationship(cat_from, cat_from_mate, True))
                bigger_than_current = True

            # check cat to value
            if cat_to_mate != None:
                opposite_mate_relationship = list(
                    filter(lambda r: r.cat_to.ID == cat_from.ID,
                           cat_to.relationships))
                if opposite_mate_relationship is not None and len(
                        opposite_mate_relationship) > 0:
                    bigger_than_current = bigger_than_current and relationship.romantic_love > opposite_mate_relationship[
                        0].romantic_love
                else:
                    cat_to_mate.relationships.append(
                        Relationship(cat_to, cat_to_mate, True))
                    bigger_than_current = bigger_than_current and True

            if (love_over_30 and normal_chance == 1) or (bigger_than_current
                                                and bigger_love_chance == 1):
                # break up the old relationships
                cat_from_mate = cat_class.all_cats.get(cat_from.mate)
                self.breakup(cat_from, cat_from_mate)

                if cat_to_mate != None:
                    self.breakup(cat_to, cat_to_mate)

                # new relationship
                game.cur_events_list.append(
                    f'{str(cat_from.name)} and {str(cat_to.name)} can\'t ignore their feelings for each other'
                )
                self.new_mates(cat_from, cat_to)

        # breakup
        if relationship.mates and 'negative' in relationship.effect:
            chance_number = 30
            if 'fight' in relationship.current_action_str:
                chance_number = 20
            chance = randint(0, chance_number)
            if chance == 1 or relationship.dislike > 20:
                self.breakup(cat_from, cat_to)

    def new_mates(self, cat1, cat2):
        cat1.set_mate(cat2)
        cat2.set_mate(cat1)
        game.cur_events_list.append(f'{str(cat1.name)} and {str(cat2.name)} have become mates')

    def breakup(self, cat1, cat2):
        cat1.unset_mate(breakup=True)
        cat2.unset_mate(breakup=True)
        game.cur_events_list.append(f'{str(cat1.name)} and {str(cat2.name)} broke up')

    def have_kits(self, cat):
        # decide chances of having kits, and if it's possible at all
        not_correct_age = cat.age in ['kitten', 'adolescent'] or cat.moons < 15
        gender_breeding = (cat.gender == 'male' and not game.settings['no gendered breeding'])
        if not_correct_age or gender_breeding or cat.no_kits or game.switches['birth_cooldown']:
            return

        for kit in cat_class.all_cats.values():
            if str(kit.status) == 'kitten' and kit.parent1 is not None and not kit.dead:
                if cat_class.all_cats.get(kit.parent1) == cat or cat_class.all_cats.get(kit.parent2) == cat:
                    return

        chance = 0
        if cat.mate is not None:
            if cat.mate in cat.all_cats:
                if cat_class.all_cats[cat.mate].dead:
                    return
                elif cat_class.all_cats[cat.mate].gender == cat.gender and not game.settings['no gendered breeding']:
                    return
                elif cat_class.all_cats[cat.mate].age == 'elder' and cat_class.all_cats[cat.mate].gender == 'female' and gender_breeding:
                    return
                elif cat_class.all_cats[cat.mate].age == 'elder' and cat_class.all_cats[cat.mate].gender == 'male':
                    chance = 2
                else:
                    chance = 30
            else:
                game.cur_events_list.append("Warning: " + str(cat.name) +
                                            " has an invalid mate #" +
                                            str(cat.mate) +
                                            ". This has been unset.")
                cat.mate = None
            if cat_class.all_cats[cat.mate].age == 'elder':
                if cat.gender == 'female' and cat_class.all_cats[cat.mate].gender == 'male':
                    chance = 35
                elif cat.gender == 'male' and game.settings['no gendered breeding']:
                    chance = 35
            if cat.age == 'elder':
                if cat.gender == 'male' and cat_class.all_cats[cat.mate].gender == 'female':
                    chance = 35
                elif cat.gender == 'female' and game.settings['no gendered breeding']:
                    chance = 35
            if cat.age == 'elder' and cat_class.all_cats[cat.mate].age == 'elder':
                chance = 0
            
                
        else:
            if not game.settings['no unknown fathers']:
                return
            else:
                chance = 40

        # Decide randomly if kits will be born, if possible
        if chance != 0:
            hit = randint(0, chance)
            if self.living_cats > 50:
                hit = randint(0, chance + 20)
            elif self.living_cats < 10:
                hit = randint(0, chance - 10)

            one_kit = [1] * 8
            two_kits = [2] * 10
            three_kits = [3] * 15
            four_kits = [4] * 12
            five_kits = [5] * 4
            six_kits = [6]
            kits = choice(one_kit + two_kits + three_kits + four_kits + five_kits + six_kits)

            if hit == 1 and cat.mate is not None:
                if not cat.no_kits and not cat_class.all_cats.get(cat.mate).no_kits:
                    if game.cur_events_list is not None:
                        game.cur_events_list.append(str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s) with ' + str(cat_class.all_cats.get(cat.mate).name))
                    else:
                        game.cur_events_list = [str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s) with' + str(cat_class.all_cats.get(cat.mate).name)]

                    # create amount of kits
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
                        
            elif hit == 1:
                name = str(cat.name)
                loner_name = choice(names.loner_names)
                warrior_name = names.prefix + names.suffix
                warrior_name_two = names.prefix + names.suffix
                mate_text = []

                other_cat = choice(list(cat_class.all_cats.values()))
                family = True
                too_young = other_cat.age in ['kitten', 'adolescent']
                same_gender = True
                affair = True
                former_mentor_setting = True                
                too_old = other_cat.age in 'elder' and cat.age not in 'senior adult' or cat.age in 'elder' and other_cat.age not in 'senior adult'
                not_suitable_mate = True
                countdown = int(len(cat_class.all_cats) / 3)
                               
                while (cat == other_cat or not_suitable_mate or family or too_young or too_old or same_gender or affair or former_mentor_setting) and countdown != 0:
                    family = True
                    same_gender = True
                    affair = True
                    not_suitable_mate = True
                    other_cat = choice(list(cat_class.all_cats.values()))
                    countdown -= 1
                    
                    # check if cats are related
                    parents_to = [cat.parent1, cat.parent2, cat]
                    parents_from = [other_cat.parent1, other_cat.parent2, other_cat]
                    parents_to = set([c for c in parents_to if c is not None])
                    parents_from = set([c for c in parents_from if c is not None])
                    # if there is any same element in any of the lists, they are related
                    family = parents_to & parents_from

                    if cat.is_potential_mate(other_cat) and other_cat.is_potential_mate(cat):
                        not_suitable_mate = False                        
                    
                    too_young = other_cat.age in ['kitten', 'adolescent']
                    too_old = other_cat.age in 'elder' and cat.age not in 'senior adult' or cat.age in 'elder' and other_cat.age not in 'senior adult'

                    if cat.gender == other_cat.gender:
                        if game.settings['no gendered breeding']:
                            same_gender = False 
                    else:
                        same_gender = False
                    
                    if other_cat.mate != None and cat.mate != None:
                        if game.settings['affair']:
                            affair = False
                    else:
                        affair = False
                    
                    former_mentor1 = cat.ID in [ inter_cat.ID for inter_cat in other_cat.former_apprentices]
                    former_mentor2 = other_cat.ID in [ inter_cat.ID for inter_cat in cat.former_apprentices]
                    if (former_mentor1 or former_mentor2):
                        if game.settings['romantic with former mentor']:
                            former_mentor_setting = False
                    else:
                        former_mentor_setting = False

                    former_mentor_setting = (former_mentor1 or former_mentor2) and game.settings['romantic with former mentor']


                parentless = randint(0, 2)
                is_parent = randint(0, 3)

                if countdown == 0:
                    parentless = 1
                
                if parentless == 1:
                    mate_text.extend([f'{name} had a litter of {str(kits)} kit(s)', f'{name} had a secret litter of {str(kits)} kit(s)', f'{name} had a litter of {str(kits)} kit(s) with an unknown partner',
                                        f'{name} had a litter of {str(kits)} kit(s) and refused to talk about their progenitor'])
                    game.cur_events_list.append(choice(mate_text))
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
                        
                else:
                    if is_parent == 1:
                        mate_text.extend([f'{name} had a litter of {str(kits)} kit(s) with a ' + choice(['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
                                          f'{name} had a secret litter of {str(kits)} kit(s) with a ' + choice(['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name)])

                    elif is_parent == 2 and len(game.clan.all_clans) > 0:
                        warrior1 = [f'{name} had a secret litter of {str(kits)} kit(s) with a ' + choice(game.clan.all_clans).name + f'Clan warrior named {str(warrior_name)}'] * 10
                        warrior2 = [f'{name} had a secret litter of {str(kits)} kit(s) with {str(warrior_name)} of ' + choice(game.clan.all_clans).name + 'Clan'] * 10
                        deputy = [f'{name} had a secret litter of {str(kits)} kit(s) with ' + choice(game.clan.all_clans).name + f'Clan\'s deputy {str(warrior_name)}'] * 3
                        leader = [f'{name} had a secret litter of {str(kits)} kit(s) with ' + choice(game.clan.all_clans).name + f'Clan\'s leader {str(names.prefix)}star'] 
                        
                        mate_text.extend(warrior1 + warrior2 + deputy + leader)

                    elif is_parent == 2 and len(game.clan.all_clans) == 0:
                        mate_text.extend([f'{name} had a secret litter of {str(kits)} kit(s) with another Clan\'s warrior',
                                            f'{name} had a secret litter of {str(kits)} kit(s) with a warrior named {str(warrior_name_two)}',
                                            f'{name} had a secret litter of {str(kits)} kit(s) with {str(warrior_name_two)} from another Clan\'s'])                          
                    else:
                        if other_cat.status == 'medicine cat':
                            mate_text.extend([f'{name} had a secret litter of {str(kits)} kit(s) with {str(other_cat.name)}',
                                        f'{name} had a secret litter of {str(kits)} kit(s) with the medicine cat {str(other_cat.name)}',
                                        f'{name} had a litter of {str(kits)} kit(s) with {str(other_cat.name)}',
                                        f'{name} had a litter of {str(kits)} kit(s) with the medicine cat {str(other_cat.name)}'])
                        else:
                            mate_text.extend([str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s) with ' + str(other_cat.name)])
                    game.cur_events_list.append(choice(mate_text))      
                    for kit in range(kits):
                        if is_parent == 1:
                            kit = Cat(parent1=cat.ID, moons=0)
                        elif is_parent == 2 and len(game.clan.all_clans) > 0:
                            kit = Cat(parent1=cat.ID, moons=0)
                        elif is_parent == 2 and len(game.clan.all_clans) == 0:
                            kit = Cat(parent1=cat.ID, moons=0)
                        else:
                            kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0)  
                        #create and update relationships
                        relationships = []
                        for cat_id in game.clan.clan_cats:
                            the_cat = cat_class.all_cats.get(cat_id)
                            if the_cat.dead or the_cat.exiled:
                                continue
                            if kit.parent2 != None:
                                if randint(0, 5) == 1:
                                    if the_cat.ID in [kit.parent1, kit.parent2]:
                                        the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                                        relationships.append(Relationship(kit,the_cat,False,True))
                                    else:
                                        the_cat.relationships.append(Relationship(the_cat,kit))
                                        relationships.append(Relationship(kit,the_cat))
                                else:
                                    if the_cat.ID is kit.parent1:
                                        the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                                        relationships.append(Relationship(kit,the_cat,False,True))
                                    else:
                                        the_cat.relationships.append(Relationship(the_cat,kit))
                                        relationships.append(Relationship(kit,the_cat))
                            else:
                                if the_cat.ID is kit.parent1:
                                    the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                                    relationships.append(Relationship(kit,the_cat,False,True))
                                else:
                                    the_cat.relationships.append(Relationship(the_cat,kit))
                                    relationships.append(Relationship(kit,the_cat))
                        kit.relationships = relationships
                        game.clan.add_cat(kit)

    def had_kits(self):
        if has_birth is True:
            game.switches['birth_cooldown'] = True
            has_birth = False
        if self.birth_range <= 0:
            game.switches['birth_cooldown'] = False


relation_events_class = Relation_Events()