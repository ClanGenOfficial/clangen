from distutils.util import change_root
from .cats import *
from .utility import *

class Relation_Events(object):
    """All relationship events."""

    MAX_ATTEMPTS = 1000

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: r.dead == False, cat_class.all_cats.copy().values())))
        self.event_sums = 0
        self.had_one_event = False
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
        random_cat = cat.all_cats.get(random_id)
        kitten_and_exiled = random_cat.exiled and cat.age == "kitten"
        attempts_left = Relation_Events.MAX_ATTEMPTS
        while len(relevant_relationship_list) < 1 or random_id == cat.ID or kitten_and_exiled:
            random_id = random.choice(list(cat.all_cats.keys()))
            random_cat = cat.all_cats.get(random_id)
            kitten_and_exiled = random_cat.exiled and cat.age == "kitten"
            relevant_relationship_list = list(
                filter(
                    lambda relation: str(relation.cat_to) == str(random_id) and
                    not relation.cat_to.dead, cat.relationships))
            attempts_left -= 1
            if attempts_left <= 0:
                return
        relevant_relationship = relevant_relationship_list[0]
        relevant_relationship.start_action()

    def handle_relationships(self, cat):
        """Iterate over all relationships and trigger different events."""
        if len(cat.relationships) < 1:
            return
        self.had_one_event = False
        big_love_chance = 5
        hit = randint(1, big_love_chance)

        if hit == 1 and not self.had_one_event:
            self.big_love_check(cat)

        random.shuffle(cat.relationships)
        for i in range(0,15):
            random_index = randint(0,len(cat.relationships)-1)
            relationship = cat.relationships[random_index]
            # get some cats to make easier checks
            cat_from = relationship.cat_from
            cat_from_mate = None
            from_mate_in_clan = False
            if cat_from.mate != None:
                if cat_from.mate not in cat_class.all_cats.keys():
                    game.cur_events_list.insert(0, f"Cat #{cat_from} has a invalid mate. It will set to none.")
                    cat_from.mate = None
                    return
                cat_from_mate = cat_class.all_cats.get(cat_from.mate)
                from_mate_in_clan = not cat_from_mate.dead and not cat_from_mate.exiled

            cat_to = relationship.cat_to
            cat_to_mate = None
            to_mate_in_clan = False
            if cat_to.mate != None:
                if cat_to.mate not in cat_class.all_cats.keys():
                    game.cur_events_list.insert(0, f"Cat #{cat_to} has a invalid mate. It will set to none.")
                    cat_to.mate = None
                    return
                cat_to_mate = cat_class.all_cats.get(cat_to.mate)
                to_mate_in_clan = not cat_to_mate.dead and not cat_to_mate.exiled

            if relationship.opposit_relationship == None:
                relationship.link_relationship()

            # overcome dead mates
            if cat_from_mate != None and cat_from_mate.dead and randint(1, 25) == 1:
                self.had_one_event = True
                print(cat_from.name, cat_from_mate.name , " - OVERCOME", game.clan.age, "moons")
                game.cur_events_list.append(
                    f'{str(cat_from.name)} will always love {str(cat_from_mate.name)} but has decided to move on'
                )
                relationship.mate = False
                cat_from.mate = None
                cat_from_mate.mate = None

            # new mates
            if not self.had_one_event and cat_from_mate is None and cat_to.is_potential_mate(cat_from):
                self.check_if_new_mates(relationship, cat_from, cat_to)

            # breakup and new mate
            if cat_from.is_potential_mate(cat_to) and cat_from.mate is not None and cat_to.mate is not None:
                love_over_30 = relationship.romantic_love > 30 and relationship.opposit_relationship.romantic_love > 30
                normal_chance = randint(1, 10)
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
                    self.check_if_breakup(cat_from, cat_from_mate)

                    if cat_to_mate != None:
                        self.check_if_breakup(cat_to, cat_to_mate)

                    # new relationship
                    game.cur_events_list.append(
                        f'{str(cat_from.name)} and {str(cat_to.name)} can\'t ignore their feelings for each other'
                    )
                    self.check_if_new_mates(cat_from, cat_to)

            # breakup
            if not self.had_one_event and relationship.mates and from_mate_in_clan:
                self.check_if_breakup(relationship, cat_from, cat_to)

    def check_if_new_mates(self, relationship, cat_from, cat_to):
        """More in depth check if the cats will become mates."""
        become_mates = False
        mate_string = ""
        mate_chance = 5
        hit = randint(1, mate_chance)

        # has to be high because every moon this will be checked for each relationship in the came
        random_mate_chance = 300 
        random_hit = randint(1, random_mate_chance)
        low_dislike = relationship.dislike < 15 and relationship.opposit_relationship.dislike < 15
        high_like = relationship.platonic_like > 30 and relationship.opposit_relationship.platonic_like > 30
        semi_high_like = relationship.platonic_like > 20 and relationship.opposit_relationship.platonic_like > 20
        high_comfort = relationship.comfortable > 25 and relationship.opposit_relationship.comfortable > 25

        if hit == 1 and relationship.romantic_love > 20 and relationship.opposit_relationship.romantic_love > 20 and semi_high_like:
            print(cat_from.name, cat_to.name , " - LOVE", game.clan.age, "moons")
            mate_string = f"{str(cat_from.name)} and {str(cat_to.name)} have become mates"
            become_mates = True
        elif random_hit == 1 and low_dislike and (high_like or high_comfort):
            print(cat_from.name, cat_to.name , " - RANDOM", game.clan.age, "moons")
            mate_string = f"{str(cat_from.name)} and {str(cat_to.name)} see each other in a different light and have become mates"
            become_mates = True
        
        if become_mates:
            self.had_one_event = True
            cat_from.set_mate(cat_to)
            cat_to.set_mate(cat_from)
            game.cur_events_list.append(mate_string)

    def check_if_breakup(self, relationship, cat_from, cat_to):
        """More in depth check if the cats will break up."""
        will_break_up = False
        fight = False

        if len(relationship.log) > 0:
            last_log = relationship.log[len(relationship.log)-1]
            if 'negative' in last_log:
                chance_number = 40
                if relationship.romantic_love > 80:
                        chance_number += 30
                if 'fight' in last_log:
                    chance_number -= 20
                    fight = True
                chance = randint(1, chance_number)
                if chance == 1 or relationship.dislike > 20:
                    if relationship.romantic_love < 50:
                        will_break_up = True
        
        if will_break_up:
            print(cat_from.name, cat_to.name, " - BREAKUP", game.clan.age, "moons")
            self.had_one_event = True
            cat_from.unset_mate(breakup=True, fight=fight)
            cat_to.unset_mate(breakup=True, fight=fight)
            game.cur_events_list.append(f'{str(cat_from.name)} and {str(cat_to.name)} broke up')

    def check_if_having_kits(self, cat):
        """Check if it possible possible to have kits and with which cat."""
        if cat.birth_cooldown > 0:
            cat.birth_cooldown -= 1

        # decide chances of having kits, and if it's possible at all
        not_correct_age = cat.age in ['kitten', 'adolescent'] or cat.moons < 15

        if not_correct_age or cat.no_kits or game.switches['birth_cooldown'] or cat.dead:
            return

        mate = None
        if cat.mate is not None:
            if cat.mate in cat_class.all_cats:
                mate = cat_class.all_cats[cat.mate]
            else:
                game.cur_events_list.append(
                    f"Warning: {str(cat.name)}  has an invalid mate # {str(cat.mate)}. This has been unset.")
                cat.mate = None

        if mate:
            if mate.gender == cat.gender and not game.settings['no gendered breeding']:
                return
            if cat.gender == 'female' and cat.age == 'elder' or mate.gender == 'female' and mate.age == 'elder':
                return
        else:
            if not game.settings['no unknown fathers']:
                return
            if cat.gender == 'female' and cat.age == 'elder':
                return

        # check if there is a cat in the clan for the second parent
        biggest_love_cat = None
        love_diff_mate_other = 0
        highes_romantic_relation = get_highes_romantic_relation(cat.relationships)
        mate_relation = None
        if mate != None:
            mate_relation = list(filter(lambda r: r.cat_to.ID == mate.ID, cat.relationships))
            if len(mate_relation) > 0:
                mate_relation = mate_relation[0]
            else:
                mate_relation = Relationship(cat,mate,True)
                cat.relationships.append(mate_relation)

        if highes_romantic_relation != None:
            if mate_relation:
                love_diff_mate_other = mate_relation.romantic_love - highes_romantic_relation.romantic_love
                biggest_love_cat = highes_romantic_relation.cat_to

        if biggest_love_cat:
            if biggest_love_cat.mate != None and not game.settings['affair']:
                biggest_love_cat = None

        # calculate which cat will be the parent
        if mate == None and biggest_love_cat == None:
            self.new_have_kits(cat)
        elif mate != None and biggest_love_cat != None and mate.ID == biggest_love_cat.ID:
            self.new_have_kits(cat, mate, mate_relation)
        elif mate != None and biggest_love_cat == None:
            self.new_have_kits(cat, mate, mate_relation)
        elif biggest_love_cat != None and mate == None:
            self.new_have_kits(cat, biggest_love_cat, highes_romantic_relation)
        else:
            # if the difference of the romantic love is lower than 0, an affair is more possible
            if love_diff_mate_other < 0:
                affair_chance = 30
                if abs(love_diff_mate_other) > 20:
                    affair_chance -= 5
                if abs(love_diff_mate_other) > 30:
                    affair_chance -= 10
                if abs(love_diff_mate_other) > 40:
                    affair_chance -= 10
                if randint(1,affair_chance) == 1:
                    self.new_have_kits(cat, biggest_love_cat, highes_romantic_relation)
                else:
                    self.new_have_kits(cat, mate, mate_relation)
            else:
                affair_chance = 100 + love_diff_mate_other
                if randint(1,affair_chance) == 1:
                    self.new_have_kits(cat, biggest_love_cat, highes_romantic_relation)
                else:
                    self.new_have_kits(cat, mate, mate_relation)

    def new_have_kits(self, cat, other_cat = None, relation = None):
        """Having kit with the other cat."""
        old_male = False
        if cat.gender == 'male' and cat.age == 'elder':
            old_male = True
        if other_cat != None and other_cat.gender == 'male' and other_cat.age == 'elder':
            old_male = True

        # calculate the chance of having kits
        chance = 60
        if other_cat != None:
            chance = 35
            if relation.romantic_love > 50:
                chance -= 5
            if relation.romantic_love > 60:
                chance -= 5
            if relation.romantic_love > 70:
                chance -= 5
            if relation.comfortable > 50:
                chance -= 5
            if relation.comfortable > 60:
                chance -= 5
            if relation.comfortable > 70:
                chance -= 5
        if old_male:
            chance = int(chance * 2)

        if self.living_cats > 50:
            chance += 20
        elif self.living_cats < 10 and chance > 10:
            chance -= 10

        if other_cat != None and (other_cat.dead or other_cat.exiled or other_cat.birth_cooldown > 0):
            return

        hit = randint(1, chance)
        if hit != 1:
            return

        print("CHANCE", chance)
        print(cat.name, " - HAVE KITS", game.clan.age, "moons")
        one_kit_possibility = {"young adult": 8,"adult": 9,"senior adult": 10,"elder" : 1}
        two_kit_possibility = {"young adult": 10,"adult": 14,"senior adult": 15,"elder" : 1}
        three_kit_possibility = {"young adult": 15,"adult": 15,"senior adult": 5,"elder" : 0}
        four_kit_possibility = {"young adult": 12,"adult": 6,"senior adult": 0,"elder" : 0}
        five_kit_possibility = {"young adult": 4,"adult": 1,"senior adult": 0,"elder" : 0}
        six_kit_possibility = {"young adult": 1,"adult": 0,"senior adult": 0,"elder" : 0}
        one_kit = [1] * one_kit_possibility[cat.age]
        two_kits = [2] * two_kit_possibility[cat.age]
        three_kits = [3] * three_kit_possibility[cat.age]
        four_kits = [4] * four_kit_possibility[cat.age]
        five_kits = [5] * five_kit_possibility[cat.age]
        six_kits = [6] * six_kit_possibility[cat.age]
        kits = choice(one_kit + two_kits + three_kits + four_kits + five_kits + six_kits)

        # create amount of kits
        for kit in range(kits):
            kit = None
            if other_cat != None:
                if cat.gender == 'female':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0)
                else:
                    kit = Cat(parent1=other_cat.ID, parent2=cat.ID, moons=0)
                cat.birth_cooldown = 6
                other_cat.birth_cooldown = 6
            else:
                kit = Cat(parent1=cat.ID, moons=0)
                cat.birth_cooldown = 6
            #create and update relationships
            relationships = []
            for cat_id in game.clan.clan_cats:
                the_cat = cat_class.all_cats.get(cat_id)
                if the_cat.dead or the_cat.exiled:
                    continue
                if the_cat.ID in kit.get_parents():
                    the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                    relationships.append(Relationship(kit,the_cat,False,True))
                else:
                    the_cat.relationships.append(Relationship(the_cat,kit))
                    relationships.append(Relationship(kit,the_cat))
            kit.relationships = relationships
            # remove accesiory
            kit.accessory = None
            game.clan.add_cat(kit)

        # choose event string
        print_event = ""
        if other_cat == None:
            print_event = f"{str(cat.name)} brought a litter of {str(kits)} kit(s) back to camp, but refused to talk about their origin"
        elif cat.mate == other_cat.ID:
            if cat.gender == 'female':
                print_event = f"{str(cat.name)} had a litter of {str(kits)} kit(s) with {str(other_cat.name)}"
            else:
                print_event = f"{str(other_cat.name)} had a litter of {str(kits)} kit(s) with {str(cat.name)}"
        else:
            print_event = f"{str(cat.name)} had a secret litter of {str(kits)} kit(s) with {str(other_cat.name)}"

        # display event
        if len(print_event) < 100:
            game.cur_events_list.append(print_event)
        else:
            cut = print_event.find(' ', int(len(print_event)/2))
            first_part = print_event[:cut]
            second_part = print_event[cut:]
            game.cur_events_list.append(first_part)
            game.cur_events_list.append(second_part)

    def old_have_kits(self, cat):
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

    def big_love_check(self, cat):
        # check romantic love
        upper_love_threshhold = 40
        lower_love_threshhold = 10

        highes_romantic_relation = get_highes_romantic_relation(cat.relationships)
        max_love_value = 0
        if highes_romantic_relation is not None:
            max_love_value = highes_romantic_relation.romantic_love

        if max_love_value < upper_love_threshhold:
            return

        cat_to = highes_romantic_relation.cat_to
        if cat_to.is_potential_mate(cat, True) and cat.is_potential_mate(cat_to, True):
            if cat_to.mate == None and cat.mate == None:
                print(cat.name, cat_to.name , " - BIG LOVE", game.clan.age, "moons")
                self.had_one_event = True
                cat.set_mate(cat_to)
                cat_to.set_mate(cat)
                first_name = cat.name
                second_name = cat_to.name

                if highes_romantic_relation.opposit_relationship is None:
                    highes_romantic_relation.link_relationship()

                if highes_romantic_relation.opposit_relationship.romantic_love > max_love_value:
                    first_name = cat_to.name
                    second_name = cat.name

                if highes_romantic_relation.opposit_relationship.romantic_love <= lower_love_threshhold:
                    game.cur_events_list.append(f"{first_name} confessed their feelings to {second_name}, but they got rejected")
                else:
                    game.cur_events_list.append(f"{first_name} confessed their feelings to {second_name} and they have become mates")


relation_events_class = Relation_Events()