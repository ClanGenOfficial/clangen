from scripts.utility import *
from scripts.cat.cats import *

class Relation_Events(object):
    """All relationship events."""

    MAX_ATTEMPTS = 1000

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: r.dead == False, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        pass

    def handle_relationships(self, cat):
        """
        Check a certain amount of relationships and trigger events.
        :param cat: cat in question
        """
        if len(cat.relationships) < 1:
            return
        self.had_one_event = False

        # this has to be handled at first
        big_love_chance = 5
        hit = randint(1, big_love_chance)

        if hit == 1 and self.big_love_check(cat):
            return

        # shuffle to not check every x first relationships
        random.shuffle(cat.relationships)
        range_number = int(len(Cat.all_cats.keys()) / 1.5)

        # cap the maximal checks
        if range_number > 20:
            range_number = 20

        for i in range(0, range_number):
            random_index = randint(0,len(cat.relationships)-1)
            relationship = cat.relationships[random_index]
            # get some cats to make easier checks
            cat_from = relationship.cat_from
            cat_from_mate = None
            if cat_from.mate != None:
                if cat_from.mate not in Cat.all_cats.keys():
                    game.cur_events_list.insert(0, f"Cat #{cat_from} has a invalid mate. It will set to none.")
                    cat_from.mate = None
                    return
                cat_from_mate = Cat.all_cats.get(cat_from.mate)

            cat_to = relationship.cat_to
            cat_to_mate = None
            if cat_to.mate != None:
                if cat_to.mate not in Cat.all_cats.keys():
                    game.cur_events_list.insert(0, f"Cat #{cat_to} has a invalid mate. It will set to none.")
                    cat_to.mate = None
                    return
                cat_to_mate = Cat.all_cats.get(cat_to.mate)

            if relationship.opposite_relationship == None:
                relationship.link_relationship()

            # overcome dead mates
            if cat_from_mate != None and cat_from_mate.dead and randint(1, 25) == 1 and cat_from_mate.dead_for >= 4:
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
                self.handle_new_mates(relationship, cat_from, cat_to)

            # breakup and new mate
            if cat_from.is_potential_mate(cat_to) and cat_from.mate is not None and cat_to.mate is not None:
                love_over_30 = relationship.romantic_love > 30 and relationship.opposite_relationship.romantic_love > 30
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
                    cat_from_mate = Cat.all_cats.get(cat_from.mate)
                    self.check_if_breakup(cat_from, cat_from_mate)

                    if cat_to_mate != None:
                        self.check_if_breakup(cat_to, cat_to_mate)

                    # new relationship
                    game.cur_events_list.append(
                        f'{str(cat_from.name)} and {str(cat_to.name)} can\'t ignore their feelings for each other'
                    )
                    self.handle_new_mates(cat_from, cat_to)

            # breakup
            self.handle_breakup(relationship, relationship.opposite_relationship, cat_from, cat_to)

    def handle_having_kits(self, cat):
        """Check if it possible possible to have kits and with which cat."""
        if cat.birth_cooldown > 0:
            cat.birth_cooldown -= 1
            return

        # decide chances of having kits, and if it's possible at all
        not_correct_age = cat.age in ['kitten', 'adolescent'] or cat.moons < 15

        if not_correct_age or cat.no_kits or cat.dead:
            return

        mate = None
        if cat.mate is not None:
            if cat.mate in Cat.all_cats:
                mate = Cat.all_cats[cat.mate]
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
        highest_romantic_relation = get_highest_romantic_relation(cat.relationships)
        mate_relation = None
        if mate != None:
            mate_relation = list(filter(lambda r: r.cat_to.ID == mate.ID, cat.relationships))
            if len(mate_relation) > 0:
                mate_relation = mate_relation[0]
            else:
                mate_relation = Relationship(cat,mate,True)
                cat.relationships.append(mate_relation)

        if highest_romantic_relation != None:
            if mate_relation:
                love_diff_mate_other = mate_relation.romantic_love - highest_romantic_relation.romantic_love
                biggest_love_cat = highest_romantic_relation.cat_to

        if biggest_love_cat:
            if biggest_love_cat.mate != None and not game.settings['affair']:
                biggest_love_cat = None

        # calculate which cat will be the parent
        if mate == None and biggest_love_cat == None:
            self.have_kits(cat)
        elif mate != None and biggest_love_cat != None and mate.ID == biggest_love_cat.ID:
            self.have_kits(cat, mate, mate_relation)
        elif mate != None and biggest_love_cat == None:
            self.have_kits(cat, mate, mate_relation)
        elif biggest_love_cat != None and mate == None:
            self.have_kits(cat, biggest_love_cat, highest_romantic_relation)
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
                    self.have_kits(cat, biggest_love_cat, highest_romantic_relation)
                else:
                    self.have_kits(cat, mate, mate_relation)
            else:
                affair_chance = 100 + love_diff_mate_other
                if randint(1,affair_chance) == 1:
                    self.have_kits(cat, biggest_love_cat, highest_romantic_relation)
                else:
                    self.have_kits(cat, mate, mate_relation)

    # ---------------------------------------------------------------------------- #
    #                                 handle events                                #
    # ---------------------------------------------------------------------------- #
    
    def handle_new_mates(self, relationship, cat_from, cat_to):
        """More in depth check if the cats will become mates."""
        young_age = ['kitten', 'adolescent']
        if cat_from.age in young_age or cat_to.age in young_age:
            return

        become_mates = False
        mate_string = ""
        mate_chance = 5
        hit = randint(1, mate_chance)

        # has to be high because every moon this will be checked for each relationship in the came
        random_mate_chance = 300 
        random_hit = randint(1, random_mate_chance)
        low_dislike = relationship.dislike < 15 and relationship.opposite_relationship.dislike < 15
        high_like = relationship.platonic_like > 30 and relationship.opposite_relationship.platonic_like > 30
        semi_high_like = relationship.platonic_like > 20 and relationship.opposite_relationship.platonic_like > 20
        high_comfort = relationship.comfortable > 25 and relationship.opposite_relationship.comfortable > 25

        if hit == 1 and relationship.romantic_love > 20 and relationship.opposite_relationship.romantic_love > 20 and semi_high_like:
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

    def handle_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        from_mate_in_clan = False
        if cat_from.mate != None:
            if cat_from.mate not in Cat.all_cats.keys():
                game.cur_events_list.insert(0, f"Cat #{cat_from} has a invalid mate. It will set to none.")
                cat_from.mate = None
                return
            cat_from_mate = Cat.all_cats.get(cat_from.mate)
            from_mate_in_clan = cat_from_mate.is_alive() and not cat_from_mate.exiled

        if not self.had_one_event and relationship_from.mates and from_mate_in_clan:
            if self.check_if_breakup(relationship_from, relationship_to, cat_from, cat_to):
                print(cat_from.name, cat_to.name, " - BREAKUP", game.clan.age, "moons")
                #TODO: filter log to check if last interaction was a fight
                had_fight = False
                self.had_one_event = True
                cat_from.unset_mate(breakup=True, fight=had_fight)
                cat_to.unset_mate(breakup=True, fight=had_fight)
                game.cur_events_list.append(f"{str(cat_from.name)} and {str(cat_to.name)} broke up")

    def big_love_check(self, cat, upper_threshold = 40, lower_threshold = 15):
        """
        Check if the cat has a high love for another and mate them if there are in the boundaries 
        :param cat: cat in question
        :upper_threshold integer:
        :lower_threshold integer:

        return: bool if event is triggered or not
        """
        # get the highest romantic love relationships and
        highest_romantic_relation = get_highest_romantic_relation(cat.relationships)
        max_love_value = 0
        if highest_romantic_relation is not None:
            max_love_value = highest_romantic_relation.romantic_love

        if max_love_value < upper_threshold:
            return False

        cat_to = highest_romantic_relation.cat_to
        if cat_to.is_potential_mate(cat, True) and cat.is_potential_mate(cat_to, True):
            if cat_to.mate == None and cat.mate == None:
                print(cat.name, cat_to.name , " - BIG LOVE", game.clan.age, "moons")
                self.had_one_event = True
                cat.set_mate(cat_to)
                cat_to.set_mate(cat)
                first_name = cat.name
                second_name = cat_to.name

                if highest_romantic_relation.opposite_relationship is None:
                    highest_romantic_relation.link_relationship()

                if highest_romantic_relation.opposite_relationship.romantic_love > max_love_value:
                    first_name = cat_to.name
                    second_name = cat.name

                if highest_romantic_relation.opposite_relationship.romantic_love <= lower_threshold:
                    game.cur_events_list.append(f"{first_name} confessed their feelings to {second_name}, but they got rejected")
                    return False
                else:
                    game.cur_events_list.append(f"{first_name} confessed their feelings to {second_name} and they have become mates")
                    return True
        return False

    def have_kits(self, cat, other_cat = None, relation = None):
        """Having kit with the other cat."""
        if other_cat != None and (other_cat.dead or other_cat.exiled or other_cat.birth_cooldown > 0):
            return

        chance = self.get_kits_chance(cat, other_cat, relation)
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
        all_kitten = []
        for kit in range(kits):
            kit = None
            if other_cat != None:
                if cat.gender == 'female':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0)
                    all_kitten.append(kit)
                else:
                    kit = Cat(parent1=other_cat.ID, parent2=cat.ID, moons=0)
                    all_kitten.append(kit)
                cat.birth_cooldown = 6
                other_cat.birth_cooldown = 6
            else:
                kit = Cat(parent1=cat.ID, moons=0)
                all_kitten.append(kit)
                cat.birth_cooldown = 6
            #create and update relationships
            relationships = []
            for cat_id in game.clan.clan_cats:
                the_cat = Cat.all_cats.get(cat_id)
                if the_cat.dead or the_cat.exiled:
                    continue
                if the_cat.ID in kit.get_parents():
                    the_cat.relationships.append(Relationship(the_cat,kit,False,True))
                    relationships.append(Relationship(kit,the_cat,False,True))
                else:
                    the_cat.relationships.append(Relationship(the_cat,kit))
                    relationships.append(Relationship(kit,the_cat))
            kit.relationships = relationships
            # remove accessory
            kit.accessory = None
            game.clan.add_cat(kit)

        # check other cats of clan for siblings
        for kitten in all_kitten:
            add_siblings_to_cat(kitten,cat_class)

        # save old possible strings (will be overworked)
        name = cat.name
        loner_name = choice(names.loner_names)
        warrior_name = Name()
        warrior_name_two = Name()
        possible_strings = [
            f'{name} had a litter of {str(kits)} kit(s) with a ' + choice(['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
            f'{name} had a secret litter of {str(kits)} kit(s) with a ' + choice(['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
            f'{name} had a secret litter of {str(kits)} kit(s) with a ' + choice(game.clan.all_clans).name + f'Clan warrior named {str(warrior_name)}',
            f'{name} had a secret litter of {str(kits)} kit(s) with {str(warrior_name)} of ' + choice(game.clan.all_clans).name + 'Clan',
            f'{name} had a secret litter of {str(kits)} kit(s) with ' + choice(game.clan.all_clans).name + f'Clan\'s deputy {str(warrior_name)}',
            f'{name} had a secret litter of {str(kits)} kit(s) with ' + choice(game.clan.all_clans).name + f'Clan\'s leader {str(names.prefix)}star',
            f'{name} had a secret litter of {str(kits)} kit(s) with another Clan\'s warrior',
            f'{name} had a secret litter of {str(kits)} kit(s) with a warrior named {str(warrior_name_two)}',
            f'{name} had a secret litter of {str(kits)} kit(s) with {str(warrior_name_two)} from another Clan\'s',
            f'{name} had a secret litter of {str(kits)} kit(s) with {str(warrior_name)}',
            f'{name} had a secret litter of {str(kits)} kit(s) with the medicine cat {str(warrior_name)}',
            f'{name} had a litter of {str(kits)} kit(s) with {str(warrior_name_two)}',
            f'{name} had a litter of {str(kits)} kit(s) with the medicine cat {str(warrior_name)}',
            str(cat.name) + ' had a litter of ' + str(kits) + ' kit(s) with ' + str(warrior_name),
            f'{name} had a litter of {str(kits)} kit(s)',
            f'{name} had a secret litter of {str(kits)} kit(s)',
            f'{name} had a litter of {str(kits)} kit(s) with an unknown partner',
            f'{name} had a litter of {str(kits)} kit(s) and refused to talk about their progenitor'
        ]
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

    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    def check_if_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        """ More in depth check if the cats will break up.
            Returns:
                bool (True or False)
        """
        will_break_up = False
        #TODO: Check log for had fight check
        had_fight = False

        chance_number = self.get_breakup_chance(relationship_from, relationship_to, cat_from, cat_to)

        chance = randint(1, chance_number)
        if chance == 1:
            if relationship_from.dislike > 30:
                will_break_up = True
            elif relationship_from.romantic_love < 50:
                will_break_up = True
            elif had_fight:
                game.cur_events_list.append(f"{str(cat_from.name)} and {str(cat_to.name)} had a fight and nearly broke up")
            else:
                game.cur_events_list.append(f"{str(cat_from.name)} and {str(cat_to.name)} have somewhat different views about their relationship")                
                relationship_from.romantic_love -= 10
                relationship_to.romantic_love -= 10
                relationship_from.comfortable -= 20
                relationship_to.comfortable -= 20
                relationship_from.platonic_like -= 20
                relationship_to.platonic_like -= 20
                relationship_from.admiration -= 10
                relationship_to.admiration -= 10

        return will_break_up

    # ---------------------------------------------------------------------------- #
    #                             get/calculate chances                            #
    # ---------------------------------------------------------------------------- #

    def get_breakup_chance(self, relationship_from, relationship_to, cat_from, cat_to):
        """ Looks into the current values and calculate the chance of breaking up. The lower, the more likely they will break up.
            Returns:
                integer (number)
        """
        chance_number = 80

        # change the chance based on the current relationship
        if relationship_from.romantic_love > 80:
            chance_number += 15
        elif relationship_from.romantic_love > 60:
            chance_number += 10
        if relationship_to.romantic_love > 80:
            chance_number += 15
        elif relationship_to.romantic_love > 60:
            chance_number += 10
        
        if relationship_from.platonic_like > 80:
            chance_number += 15
        elif relationship_from.platonic_like > 60:
            chance_number += 10
        if relationship_from.platonic_like > 80:
            chance_number += 15
        elif relationship_from.platonic_like > 60:
            chance_number += 10

        chance_number -= int(relationship_from.dislike / 2)
        chance_number -= int(relationship_from.jealousy / 4)
        chance_number -= int(relationship_to.dislike / 2)
        chance_number -= int(relationship_to.jealousy / 4)

        # change the change based on the personality
        get_along = get_personality_compatibility(cat_from, cat_to)
        if get_along != None and get_along:
            chance_number += 5
        if get_along != None and not get_along:
            chance_number -= 10

        # change the chance based on the last interactions
        if len(relationship_from.log) > 0:
            # check last interaction
            last_log = relationship_from.log[len(relationship_from.log)-1]
            print(last_log)

            if 'negative' in last_log:
                chance_number -= 30
                if 'fight' in last_log:
                    chance_number -= 20

            # check all interactions - the logs are still buggy
            #negative_interactions = list(filter(lambda inter: 'negative' in inter, relationship_from.log))
            #chance_number -= len(negative_interactions)
            #positive_interactions = list(filter(lambda inter: 'positive' in inter, relationship_from.log))
            #chance_number += len(positive_interactions)

            #if len(negative_interactions) > len(positive_interactions) and len(relationship_from.log) > 5 :
            #    chance_number -= 20

        # this should be nearly impossible, that chance is lower than 0
        if chance_number <= 0:
            chance_number = 1
        
        return chance_number

    def get_kits_chance(self, cat, other_cat = None, relation = None):
        """ Looks into the current values and calculate the chance of having kittens. The lower, the more likely they will have kittens.
            Returns:
                integer (number)
        """
        old_male = False
        if cat.gender == 'male' and cat.age == 'elder':
            old_male = True
        if other_cat != None and other_cat.gender == 'male' and other_cat.age == 'elder':
            old_male = True

        # calculate the chance of having kits
        chance = 80
        if other_cat != None:
            chance = 45
            if relation.romantic_love >= 50:
                chance -= 5
            if relation.romantic_love >= 70:
                chance -= 5
            if relation.romantic_love >= 90:
                chance -= 10
            if relation.comfortable >= 50:
                chance -= 5
            if relation.comfortable >= 70:
                chance -= 5
            if relation.comfortable >= 90:
                chance -= 10
        if old_male:
            chance = int(chance * 2)

        if self.living_cats > 30:
            chance += int(int(self.living_cats/2) * int(self.living_cats % 10)) 
        if self.living_cats < 10 and chance > 10:
            chance -= 10
        
        return chance
