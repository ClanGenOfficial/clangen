from scripts.utility import *
from scripts.cat.cats import *

class Relation_Events():
    """All relationship events."""

    MAX_ATTEMPTS = 1000

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
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
            if cat_from.mate is not None:
                if cat_from.mate not in Cat.all_cats.keys():
                    game.cur_events_list.insert(0, f"Cat #{cat_from} has a invalid mate. It will set to none.")
                    cat_from.mate = None
                    return
                cat_from_mate = Cat.all_cats.get(cat_from.mate)

            cat_to = relationship.cat_to
            cat_to_mate = None
            if cat_to.mate is not None:
                if cat_to.mate not in Cat.all_cats.keys():
                    game.cur_events_list.insert(0, f"Cat #{cat_to} has a invalid mate. It will set to none.")
                    cat_to.mate = None
                    return
                cat_to_mate = Cat.all_cats.get(cat_to.mate)

            if relationship.opposite_relationship is None:
                relationship.link_relationship()

            # overcome dead mates
            if cat_from_mate is not None and cat_from_mate.dead and randint(1, 25) == 1 and cat_from_mate.dead_for >= 4:
                self.had_one_event = True
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
                    if cat_from_mate is not None:
                        cat_from_mate.relationships.append(
                            Relationship(cat_from, cat_from_mate, True))
                    bigger_than_current = True

                # check cat to value
                if cat_to_mate is not None:
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

                    if cat_to_mate is not None:
                        self.check_if_breakup(cat_to, cat_to_mate)

                    # new relationship
                    game.cur_events_list.append(
                        f'{str(cat_from.name)} and {str(cat_to.name)} can\'t ignore their feelings for each other'
                    )
                    self.handle_new_mates(cat_from, cat_to)

            # breakup
            self.handle_breakup(relationship, relationship.opposite_relationship, cat_from, cat_to)

    def handle_pregnancy_age(self, clan = game.clan):
        """Increase the moon for each pregnancy in the pregnancy dictionary"""
        for pregnancy_key in clan.pregnancy_data.keys():
            clan.pregnancy_data[pregnancy_key]["moons"] += 1

    def handle_having_kits(self, cat, clan):
        """Handles pregnancy of a cat."""
        if clan is None:
            return
        if cat.ID in clan.pregnancy_data.keys():
            moons = clan.pregnancy_data[cat.ID]["moons"]
            if moons == 1:
                self.handle_one_moon_pregnant(cat, clan)
                return
            if moons >= 2:
                self.handle_two_moon_pregnant(cat, clan)
                return
        
        can_have_kits = self.check_if_can_have_kits(cat, game.settings['no unknown fathers'], game.settings['no gendered breeding'])
        if not can_have_kits:
            return

        mate = None
        if cat.mate is not None:
            if cat.mate in Cat.all_cats:
                mate = Cat.all_cats[cat.mate]
            else:
                game.cur_events_list.append(
                    f"WARNING: {str(cat.name)}  has an invalid mate # {str(cat.mate)}. This has been unset.")
                cat.mate = None

        # check if there is a cat in the clan for the second parent
        second_parent = self.get_second_parent(cat, mate, game.settings['affair'])
        second_parent_relation = None
        if second_parent is not None:
            second_parent_relation = list(filter(lambda r: r.cat_to.ID == second_parent.ID ,cat.relationships))
            if len(second_parent_relation) > 0:
                second_parent_relation = second_parent_relation[0]
            else: 
                second_parent_relation = None
        
        # check if the second_parent is not none, if they also can have kits
        if second_parent:
            parent2_can_have_kits = self.check_if_can_have_kits(second_parent, game.settings['no unknown fathers'], game.settings['no gendered breeding'])
            if not parent2_can_have_kits:
                return
        
        self.handle_zero_moon_pregnant(cat, second_parent, second_parent_relation, clan)

        # save old possible strings (will be overworked)
        name = cat.name
        loner_name = choice(names.loner_names)
        warrior_name = Name()
        warrior_name_two = Name()
        kits_amount = 0
        other_clan_name = "FILLER_CLAN"
        possible_strings = [
            f'{name} had a litter of {str(kits_amount)} kit(s) with a ' + choice(['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with a ' + choice(['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with a ' + other_clan_name + f'Clan warrior named {str(warrior_name)}',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with {str(warrior_name)} of ' + other_clan_name + 'Clan',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with ' + other_clan_name + f'Clan\'s deputy {str(warrior_name)}',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with ' + other_clan_name + f'Clan\'s leader {str(names.prefix)}star',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with another Clan\'s warrior',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with a warrior named {str(warrior_name_two)}',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with {str(warrior_name_two)} from another Clan\'s',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with {str(warrior_name)}',
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with the medicine cat {str(warrior_name)}',
            f'{name} had a litter of {str(kits_amount)} kit(s) with {str(warrior_name_two)}',
            f'{name} had a litter of {str(kits_amount)} kit(s) with the medicine cat {str(warrior_name)}',
            str(cat.name) + ' had a litter of ' + str(kits_amount) + ' kit(s) with ' + str(warrior_name),
            f'{name} had a litter of {str(kits_amount)} kit(s)',
            f'{name} had a secret litter of {str(kits_amount)} kit(s)',
            f'{name} had a litter of {str(kits_amount)} kit(s) with an unknown partner',
            f'{name} had a litter of {str(kits_amount)} kit(s) and refused to talk about their progenitor'
        ]

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
            mate_string = f"{str(cat_from.name)} and {str(cat_to.name)} have become mates"
            become_mates = True
        elif random_hit == 1 and low_dislike and (high_like or high_comfort):
            mate_string = f"{str(cat_from.name)} and {str(cat_to.name)} see each other in a different light and have become mates"
            become_mates = True

        if become_mates:
            self.had_one_event = True
            cat_from.set_mate(cat_to)
            cat_to.set_mate(cat_from)
            game.cur_events_list.append(mate_string)

    def handle_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        from_mate_in_clan = False
        if cat_from.mate is not None:
            if cat_from.mate not in Cat.all_cats.keys():
                game.cur_events_list.insert(0, f"Cat #{cat_from} has a invalid mate. It will set to none.")
                cat_from.mate = None
                return
            cat_from_mate = Cat.all_cats.get(cat_from.mate)
            from_mate_in_clan = cat_from_mate.is_alive() and not cat_from_mate.exiled

        if not self.had_one_event and relationship_from.mates and from_mate_in_clan:
            if self.check_if_breakup(relationship_from, relationship_to, cat_from, cat_to):
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
            if cat_to.mate is None and cat.mate is None:
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

    def handle_zero_moon_pregnant(self, cat, other_cat = None, relation = None, clan = game.clan):
        """Handles if the cat is zero moons pregnant."""
        if other_cat is not None and (other_cat.dead or other_cat.exiled or other_cat.birth_cooldown > 0):
            return

        chance = self.get_kits_chance(cat, other_cat, relation)
        hit = randint(1, chance)
        if hit != 1:
            return
        
        # even with no_gendered_breeding on a male cat with no second parent should not be count as pregnant
        # instead, the cat should get the kit instantly
        if cat.gender == 'male' and other_cat is None:
            amount = self.get_amount_of_kits(cat)
            self.get_kits(amount, cat, None, clan)
            print_event = f"{str(cat.name)} brought a litter of {str(amount)} kit(s) back to camp, but refused to talk about their origin"

            # display event
            if len(print_event) < 100:
                game.cur_events_list.append(print_event)
            else:
                cut = print_event.find(' ', int(len(print_event)/2))
                first_part = print_event[:cut]
                second_part = print_event[cut:]
                game.cur_events_list.append(first_part)
                game.cur_events_list.append(second_part)
            return

        # if the other cat is a female and the current cat is a male, make the female cat pregnant
        pregnant_cat = cat
        if cat.gender == 'male' and other_cat is not None and other_cat.gender == 'female':
            pregnant_cat = other_cat
            clan.pregnancy_data[other_cat.ID] = {
                "second_parent": str(cat.ID),
                "moons": 0,
                "amount": 0
            }
        else:
            clan.pregnancy_data[cat.ID] = {
                "second_parent": str(other_cat),
                "moons": 0,
                "amount": 0
            }

        game.cur_events_list.append(f"{pregnant_cat.name} announced that they are expecting kits")

    def handle_one_moon_pregnant(self, cat, clan = game.clan):
        """Handles if the cat is one moon pregnant."""
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is exiled or killed meanwhile, delete it from the dictionary
        if cat.dead or cat.exiled:
            del clan.pregnancy_data[cat.ID]
            return
        
        amount = self.get_amount_of_kits(cat)
        thinking_amount = choice([amount-1,amount,amount+1])
        if thinking_amount < 1:
            thinking_amount = 1

        # add the amount to the pregnancy dict
        clan.pregnancy_data[cat.ID]["amount"] = amount

        if thinking_amount == 1:
            game.cur_events_list.append(f"{cat.name} thinks that they will have one kit")
        else:
            game.cur_events_list.append(f"{cat.name} thinks that they will have {thinking_amount} kits")

    def handle_two_moon_pregnant(self, cat, clan = game.clan):
        """Handles if the cat is two moons pregnant."""
        # if the pregnant cat is exiled or killed meanwhile, delete it from the dictionary
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is exiled or killed meanwhile, delete it from the dictionary
        if cat.dead or cat.exiled:
            del clan.pregnancy_data[cat.ID]
            return

        kits_amount = clan.pregnancy_data[cat.ID]["amount"]
        other_cat_id = clan.pregnancy_data[cat.ID]["second_parent"]
        other_cat = Cat.all_cats.get(other_cat_id)

        kits_amount = self.get_kits(kits_amount, cat, other_cat, clan)
        kits_amount = len(kits_amount)

        # delete the cat out of the pregnancy dictionary
        del clan.pregnancy_data[cat.ID]

        # choose event string
        print_event = ""
        if other_cat is None:
            print_event = f"{str(cat.name)} had a litter of {str(kits_amount)} kit(s), but refused to talk about their origin"
        elif cat.mate == other_cat.ID:
            if cat.gender == 'female':
                print_event = f"{str(cat.name)} had a litter of {str(kits_amount)} kit(s) with {str(other_cat.name)}"
            else:
                print_event = f"{str(other_cat.name)} had a litter of {str(kits_amount)} kit(s) with {str(cat.name)}"
        else:
            print_event = f"{str(cat.name)} had a secret litter of {str(kits_amount)} kit(s) with {str(other_cat.name)}"

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

    def check_if_can_have_kits(
        self,
        cat,
        unknown_parent_setting,
        no_gendered_breeding
    ):
        can_have_kits = False
        if cat.birth_cooldown > 0:
            cat.birth_cooldown -= 1
            return can_have_kits

        # decide chances of having kits, and if it's possible at all
        not_correct_age = cat.age in ['kitten', 'adolescent'] or cat.moons < 15
        if not_correct_age or cat.no_kits or cat.dead:
            return can_have_kits

        # check for mate
        mate = None
        if cat.mate is not None:
            if cat.mate in Cat.all_cats:
                mate = Cat.all_cats[cat.mate]
            else:
                game.cur_events_list.append(
                    f"WARNING: {str(cat.name)}  has an invalid mate # {str(cat.mate)}. This has been unset.")
                cat.mate = None

        if mate and mate.dead:
            return can_have_kits

        if mate:
            if mate.gender == cat.gender and not no_gendered_breeding:
                return can_have_kits
            if cat.gender == 'female' and cat.age == 'elder' or mate.gender == 'female' and mate.age == 'elder':
                return can_have_kits
        else:
            if not unknown_parent_setting:
                return can_have_kits
            if cat.gender == 'female' and cat.age == 'elder':
                return can_have_kits

        # if function reaches this point, having kits is possible
        can_have_kits = True
        return can_have_kits

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
        if get_along is not None and get_along:
            chance_number += 5
        if get_along is not None and not get_along:
            chance_number -= 10

        # change the chance based on the last interactions
        if len(relationship_from.log) > 0:
            # check last interaction
            last_log = relationship_from.log[len(relationship_from.log)-1]

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
        if other_cat is not None and other_cat.gender == 'male' and other_cat.age == 'elder':
            old_male = True

        # calculate the chance of having kits
        chance = 80
        if other_cat is not None:
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

    def get_affair_chance(self, mate_relation, affair_relation):
        """ Looks into the current values and calculate the chance of having kits with the affair cat.
            The lower, the more likely they will have affairs. This function should only be called when mate 
            and affair_cat are not the same.

            Returns:
                integer (number)
        """
        if mate_relation is None:
            return 0

        affair_chance = 100

        love_diff_mate_other = mate_relation.romantic_love - affair_relation.romantic_love
        if love_diff_mate_other < 0:
            affair_chance = 25
            if abs(love_diff_mate_other) > 20:
                affair_chance -= 5
            if abs(love_diff_mate_other) > 25:
                affair_chance -= 10
            if abs(love_diff_mate_other) > 30:
                affair_chance -= 10
        else:
            affair_chance += love_diff_mate_other

        return affair_chance

    def get_second_parent(self, cat, mate = None, affair = game.settings['affair']):
        """ Return the second parent of a cat, which will have kits."""
        second_parent = mate
        if not affair or mate is None:
            # if the cat has no mate, None will be returned
            return second_parent

        mate_relation = list(filter(lambda r: r.cat_to.ID == mate.ID, cat.relationships))
        if len(mate_relation) > 0:
            mate_relation = mate_relation[0]
        else:
            mate_relation = Relationship(cat,mate,True)
            cat.relationships.append(mate_relation)

        highest_romantic_relation = get_highest_romantic_relation(cat.relationships)
        if highest_romantic_relation is None:
            return second_parent

        if highest_romantic_relation.cat_to.ID == mate.ID:
            return second_parent

        # the function should only called if highest_romantic_cat is not the mate
        chance_affair = self.get_affair_chance(
            mate_relation,
            highest_romantic_relation
        )

        # a chance of 0 should always be a "auto hit"
        if chance_affair == 0 or randint(1, chance_affair) == 1:
            second_parent = highest_romantic_relation.cat_to

        return second_parent

    def get_kits(self, kits_amount, cat, other_cat = None, clan = game.clan):
        # create amount of kits
        all_kitten = []
        for kit in range(kits_amount):
            kit = None
            if other_cat is not None:
                if cat.gender == 'female':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0)
                    all_kitten.append(kit)
                    kit.thought = f"Snuggles up to the belly of {cat.name}"
                else:
                    kit = Cat(parent1=other_cat.ID, parent2=cat.ID, moons=0)
                    all_kitten.append(kit)
                    kit.thought = f"Snuggles up to the belly of {other_cat.name}"
                cat.birth_cooldown = 6
                other_cat.birth_cooldown = 6
            else:
                kit = Cat(parent1=cat.ID, moons=0)
                all_kitten.append(kit)
                cat.birth_cooldown = 6
                kit.thought = f"Snuggles up to the belly of {cat.name}"
            #create and update relationships
            relationships = []
            for cat_id in clan.clan_cats:
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
            clan.add_cat(kit)

        # check other cats of clan for siblings
        for kitten in all_kitten:
            add_siblings_to_cat(kitten, cat_class)
            add_children_to_cat(kitten, cat_class)

        return all_kitten

    def get_amount_of_kits(self, cat):
        """Get the amount of kits which will be born."""
        one_kit_possibility = {"young adult": 8,"adult": 9,"senior adult": 10,"elder" : 4}
        two_kit_possibility = {"young adult": 10,"adult": 13,"senior adult": 15,"elder" : 3}
        three_kit_possibility = {"young adult": 17,"adult": 15,"senior adult": 5,"elder" : 1}
        four_kit_possibility = {"young adult": 12,"adult": 8,"senior adult": 2,"elder" : 0}
        five_kit_possibility = {"young adult": 6,"adult": 2,"senior adult": 0,"elder" : 0}
        six_kit_possibility = {"young adult": 2,"adult": 0,"senior adult": 0,"elder" : 0}
        one_kit = [1] * one_kit_possibility[cat.age]
        two_kits = [2] * two_kit_possibility[cat.age]
        three_kits = [3] * three_kit_possibility[cat.age]
        four_kits = [4] * four_kit_possibility[cat.age]
        five_kits = [5] * five_kit_possibility[cat.age]
        six_kits = [6] * six_kit_possibility[cat.age]
        amount = choice(one_kit + two_kits + three_kits + four_kits + five_kits + six_kits)

        return amount
