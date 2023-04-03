from random import choice
import random

from scripts.utility import (
    get_highest_romantic_relation,
    get_med_cats,
    add_children_to_cat,
    add_siblings_to_cat, event_text_adjust
)
from scripts.game_structure.game_essentials import game
from scripts.cat.cats import Cat, cat_class
from scripts.event_class import Single_Event
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.condition_events import Condition_Events
from scripts.cat.names import names, Name

import ujson

class Pregnancy_Events():
    """All events which are related to pregnancy such as kitting and defining who are the parents."""
    
    def __init__(self) -> None:
        self.condition_events = Condition_Events()
        pass


    def handle_pregnancy_age(self, clan):
        """Increase the moon for each pregnancy in the pregnancy dictionary"""
        for pregnancy_key in clan.pregnancy_data.keys():
            clan.pregnancy_data[pregnancy_key]["moons"] += 1

    def handle_having_kits(self, cat, clan):
        """Handles pregnancy of a cat."""
        if not clan:
            return

        #Handles if a cat is already pregnant
        if cat.ID in clan.pregnancy_data:
            moons = clan.pregnancy_data[cat.ID]["moons"]
            if moons == 1:
                self.handle_one_moon_pregnant(cat, clan)
                return
            if moons >= 2:
                self.handle_two_moon_pregnant(cat, clan)
                #events.ceremony_accessory = True
                return

        if cat.outside:
            return

        # Check if they can have kits.
        can_have_kits = self.check_if_can_have_kits(cat, game.settings['no unknown fathers'])
        if not can_have_kits:
            return

        # Roll to see if the cat will have kits.
        if cat.mate:
            chance = game.config["pregnancy"]["primary_chance_mated"]
        else:
            chance = game.config["pregnancy"]["primary_chance_unmated"]

        # This is the first chance. Other checks will then be made that can "cancel" this roll.
        if not int(random.random() * chance):
            # print(f"primary kit roll triggered for {cat.name}")

            # DETERMINE THE SECOND PARENT
            mate = None
            if cat.mate:
                if cat.mate in Cat.all_cats:
                    mate = Cat.all_cats[cat.mate]
                else:
                    print(f"WARNING: {cat.name}  has an invalid mate # {cat.mate}. This has been unset.")
                    cat.mate = None

            # check if there is a cat in the clan for the second parent
            second_parent, affair = self.get_second_parent(cat, mate, game.settings['affair'])
            second_parent_relation = None
            if second_parent and second_parent.ID in cat.relationships:
                second_parent_relation = cat.relationships[second_parent.ID]
            elif second_parent:
                second_parent_relation = Relationship(cat, second_parent)
                cat.relationships[second_parent.ID] = second_parent_relation

            # check if the second_parent is not none, if they also can have kits
            if second_parent:
                # This is a special check that could be an affair partner.
                parent2_can_have_kits = self.check_second_parent(cat, second_parent)
                if not parent2_can_have_kits:
                    # print("chosen second parent can't have kits")
                    return
            else:
                if not game.settings['no unknown fathers']:
                    return

            # Now that the second parent is determined, and we have exited if that second parent cannot have kits,
            # we have some chances

            # If an affair was triggered, bypass the love check. They already had an affair - sometimes, there
            # is no love in an affair.
            living_cats = len([i for i in Cat.all_cats.values() if not (i.dead or i.outside or i.exiled)])

            if not affair:
                if second_parent:
                    if not second_parent_relation.opposite_relationship:
                        second_parent_relation.link_relationship()

                    average_romantic_love = (second_parent_relation.romantic_love +
                                             second_parent_relation.opposite_relationship.romantic_love) / 2
                    average_comfort = (second_parent_relation.comfortable +
                                       second_parent_relation.opposite_relationship.comfortable) / 2
                    average_trust = (second_parent_relation.trust +
                                     second_parent_relation.opposite_relationship.trust) / 2

                    chance = 8
                    if average_romantic_love >= 85:
                        chance += 26
                    elif average_romantic_love >= 55:
                        chance += 20
                    elif average_romantic_love >= 35:
                        chance += 13

                    if average_comfort >= 85:
                        chance += 26
                    elif average_comfort >= 55:
                        chance += 20
                    elif average_comfort >= 35:
                        chance += 13

                    if average_trust >= 85:
                        chance += 26
                    elif average_trust >= 55:
                        chance += 20
                    elif average_trust >= 35:
                        chance += 13
                else:
                    chance = int(75/living_cats) + 2

                if cat.gender == 'male' and cat.age == 'senior':
                    chance = int(chance / 2)
                elif second_parent is not None and second_parent.gender == 'male' and second_parent.age == 'senior':
                    chance = int(chance / 2)

            else:
                # Affairs never cancel - it makes setting affairs number easier.
                chance = 0

            # print("Kit cancel chance", chance)
            if int(random.random() * chance) == 1:
                # Cancel having kits.
                return

            # If you've reached here - congrats, kits!
            self.handle_zero_moon_pregnant(cat, second_parent, second_parent_relation, clan)

    # ---------------------------------------------------------------------------- #
    #                                 handle events                                #
    # ---------------------------------------------------------------------------- #

    def handle_zero_moon_pregnant(self, cat, other_cat=None, relation=None, clan=game.clan):
        """Handles if the cat is zero moons pregnant."""
        if other_cat and (other_cat.dead or other_cat.outside or other_cat.birth_cooldown > 0):
            return

        if cat.ID in clan.pregnancy_data:
            return

        if other_cat and other_cat.ID in clan.pregnancy_data:
            return

        # even with no_gendered_breeding on a male cat with no second parent should not be count as pregnant
        # instead, the cat should get the kit instantly
        if not other_cat and cat.gender == 'male':
            amount = self.get_amount_of_kits(cat)
            kits = self.get_kits(amount, cat, None, clan)
            insert = 'this should not display'
            if amount == 1:
                insert = 'a single kitten'
            if amount > 1:
                insert = f'a litter of {amount} kits'
            print_event = f"{cat.name} brought {insert} back to camp, but refused to talk about their origin."
            cats_involved = [cat.ID]
            for kit in kits:
                cats_involved.append(kit.ID)
            game.cur_events_list.append(Single_Event(print_event, "birth_death", cats_involved))
            return

        # if the other cat is a female and the current cat is a male, make the female cat pregnant
        pregnant_cat = cat
        second_parent = other_cat
        if cat.gender == 'male' and other_cat is not None and other_cat.gender == 'female':
            pregnant_cat = other_cat
            second_parent = cat

        clan.pregnancy_data[pregnant_cat.ID] = {
            "second_parent": str(second_parent.ID) if second_parent else None,
            "moons": 0,
            "amount": 0
        }

        text = choice(PREGNANT_STRINGS["announcement"])
        if clan.game_mode != 'classic':
            severity = random.choices(["minor", "major"], [3, 1], k=1)
            pregnant_cat.get_injured("pregnant", severity=severity[0])
            text += choice(PREGNANT_STRINGS[f"{severity[0]}_severity"])
        text = event_text_adjust(Cat, text, pregnant_cat, clan=clan)
        game.cur_events_list.append(Single_Event(text, "birth_death", pregnant_cat.ID))

    def handle_one_moon_pregnant(self, cat, clan=game.clan):
        """Handles if the cat is one moon pregnant."""
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat killed meanwhile, delete it from the dictionary
        if cat.dead:
            del clan.pregnancy_data[cat.ID]
            return

        amount = self.get_amount_of_kits(cat)
        text = 'This should not appear (pregnancy_events.py)'

        # add the amount to the pregnancy dict
        clan.pregnancy_data[cat.ID]["amount"] = amount

        # if the cat is outside of the clan, they won't guess how many kits they will have
        if cat.outside:
            return

        thinking_amount = random.choices(["correct", "incorrect", "unsure"], [4, 1, 1], k=1)
        if amount <= 3:
            correct_guess = "small"
        else:
            correct_guess = "large"

        if thinking_amount[0] == "correct":
            if correct_guess == "small":
                text = PREGNANT_STRINGS["litter_guess"][0]
            else:
                text = PREGNANT_STRINGS["litter_guess"][1]
        elif thinking_amount[0] == 'incorrect':
            if correct_guess == "small":
                text = PREGNANT_STRINGS["litter_guess"][1]
            else:
                text = PREGNANT_STRINGS["litter_guess"][0]
        else:
            text = PREGNANT_STRINGS["litter_guess"][2]

        if clan.game_mode != 'classic':
            try:
                if cat.injuries["pregnant"]["severity"] == "minor":
                    cat.injuries["pregnant"]["severity"] = "major"
                    text += choice(PREGNANT_STRINGS["major_severity"])
                cat.injuries["pregnant"]["duration"] -= 1
                cat.injuries["pregnant"]["moons_with"] += 1
            except:
                print("Is this an old save? Cat does not have the pregnant condition")

        text = event_text_adjust(Cat, text, cat, clan=clan)
        game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))

    def handle_two_moon_pregnant(self, cat, clan=game.clan):
        """Handles if the cat is two moons pregnant."""
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is killed meanwhile, delete it from the dictionary
        if cat.dead:
            del clan.pregnancy_data[cat.ID]
            return

        involved_cats = [cat.ID]

        kits_amount = clan.pregnancy_data[cat.ID]["amount"]
        other_cat_id = clan.pregnancy_data[cat.ID]["second_parent"]
        other_cat = Cat.all_cats.get(other_cat_id)

        kits = self.get_kits(kits_amount, cat, other_cat, clan)
        kits_amount = len(kits)

        # delete the cat out of the pregnancy dictionary
        del clan.pregnancy_data[cat.ID]

        if cat.outside:
            for kit in kits:
                kit.outside = True
                game.clan.add_to_outside(kit)
                kit.backstory = "outsider"
                if cat.exiled:
                    kit.status = 'loner'
                    name = choice(names.names_dict["normal_prefixes"])
                    kit.name = Name('loner', prefix=name, suffix="")
                if other_cat and not other_cat.outside:
                    kit.backstory = "outsider2"
                if cat.outside and not cat.exiled:
                    kit.backstory = "outsider3"
                kit.relationships = {}
                kit.relationships[cat.ID] = Relationship(kit, cat)

        if kits_amount == 1:
            insert = 'single kitten'
        else:
            insert = f'litter of {kits_amount} kits'

        # choose event string
        events = PREGNANT_STRINGS
        event_list = []
        if not cat.outside and other_cat is None:
            event_list.append(choice(events["birth"]["unmated_parent"]))
        elif cat.outside:
            adding_text = choice(events["birth"]["outside_alone"])
            if other_cat and not other_cat.outside:
                adding_text = choice(events["birth"]["outside_in_clan"])
            event_list.append(adding_text)
        elif cat.mate == other_cat.ID and not other_cat.dead and not other_cat.outside:
            involved_cats.append(other_cat.ID)
            event_list.append(choice(events["birth"]["two_parents"]))
        elif cat.mate == other_cat.ID and other_cat.dead or other_cat.outside:
            involved_cats.append(other_cat.ID)
            event_list.append(choice(events["birth"]["dead_mate"]))
        elif not cat.mate and not other_cat.mate and not other_cat.dead:
            involved_cats.append(other_cat.ID)
            event_list.append(choice(events["birth"]["both_unmated"]))
        elif (cat.mate and cat.mate != other_cat.ID and not other_cat.dead) or (other_cat.mate and other_cat.mate != cat.ID and not other_cat.dead):
            involved_cats.append(other_cat.ID)
            event_list.append(choice(events["birth"]["affair"]))
        else:
            event_list.append(choice(events["birth"]["unmated_parent"]))

        if clan.game_mode != 'classic':
            try:
                death_chance = cat.injuries["pregnant"]["mortality"]
            except:
                death_chance = 40
        else:
            death_chance = 40
        if not int(random.random() * death_chance):  # chance for a cat to die during childbirth
            possible_events = events["birth"]["death"]
            # just makin sure meds aren't mentioned if they aren't around or if they are a parent
            meds = get_med_cats(Cat, working=False)
            if not meds or (cat or cat.mate) in meds:
                for event in possible_events:
                    if "medicine cat" in event:
                        possible_events.remove(event)

            if cat.outside:
                possible_events = events["birth"]["outside_death"]
            event_list.append(choice(possible_events))

            if cat.status == 'leader':
                clan.leader_lives -= 1
                cat.die()
                cat.died_by.append(f" died shortly after kitting.")
            else:
                cat.die()
                cat.died_by.append(f"{cat.name} died while kitting.")
        elif clan.game_mode != 'classic' and not cat.outside:  # if cat doesn't die, give recovering from birth
            cat.get_injured("recovering from birth", event_triggered=True)
            if 'blood loss' in cat.injuries:
                possible_events = events["birth"]["difficult_birth"]
                # just makin sure meds aren't mentioned if they aren't around or if they are a parent
                meds = get_med_cats(Cat, working=False)
                if not meds or (cat or cat.mate) in meds:
                    for event in possible_events:
                        if "medicine cat" in event:
                            possible_events.remove(event)

                event_list.append(choice(possible_events))
        if clan.game_mode != 'classic':
            try:
                cat.injuries.pop("pregnant")
            except:
                print("Is this an old save? Your cat didn't have the pregnant condition!")
        print_event = " ".join(event_list)
        print_event = print_event.replace("{insert}", insert)
        print_event = event_text_adjust(Cat, print_event, cat, other_cat, clan=clan)
        # display event
        game.cur_events_list.append(Single_Event(print_event, ["health", "birth_death"], involved_cats))

    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    def check_if_can_have_kits(self, cat, unknown_parent_setting):

        if cat.birth_cooldown > 0:
            cat.birth_cooldown -= 1
            return False

        if 'recovering from birth' in cat.injuries:
            return False

        # decide chances of having kits, and if it's possible at all.
        # Including - age, dead statis, having kits turned off.
        not_correct_age = cat.age in ['kitten', 'adolescent'] or cat.moons < 15
        if not_correct_age or cat.no_kits or cat.dead:
            return False

        # check for mate
        mate = None
        if cat.mate:
            if cat.mate not in cat.all_cats:
                print(f"WARNING: {cat.name}  has an invalid mate # {cat.mate}. This has been unset.")
                cat.mate = None

        # If the "no unknown fathers setting in on, we should only allow cats that have mates to have kits.
        if not unknown_parent_setting and not cat.mate:
            return False

        # if function reaches this point, having kits is possible
        can_have_kits = True
        return can_have_kits

    def check_second_parent(self, cat: Cat, second_parent: Cat):
        """ This checks to see if the chosen second parent and CAT can have kits. It assumes CAT can have kits. """

        # Checks for second parent alone:
        if second_parent.birth_cooldown > 0:
            return False

        if 'recovering from birth' in second_parent.injuries:
            return False

        # decide chances of having kits, and if it's possible at all.
        # Including - age, dead statis, having kits turned off.
        not_correct_age = second_parent.age in ['kitten', 'adolescent'] or second_parent.moons < 15
        if not_correct_age or second_parent.no_kits or second_parent.dead or second_parent.outside:
            return False

        # Check to see if the pair can have kits.
        if not game.settings["no gendered breeding"]:
            if cat.gender == second_parent.gender:
                return False

        return True

    # ---------------------------------------------------------------------------- #
    #                             get/calculate chances                            #
    # ---------------------------------------------------------------------------- #

    def get_love_affair_chance(self, mate_relation: Relationship, affair_relation: Relationship):
        """ Looks into the current values and calculate the chance of having kits with the affair cat.
            The lower, the more likely they will have affairs. This function should only be called when mate 
            and affair_cat are not the same.

            Returns:
                integer (number)
        """
        if not mate_relation.opposite_relationship:
            mate_relation.link_relationship()

        if not affair_relation.opposite_relationship:
            affair_relation.link_relationship()

        average_mate_love = (mate_relation.romantic_love + mate_relation.opposite_relationship.romantic_love) / 2
        average_affair_love = (affair_relation.romantic_love + affair_relation.opposite_relationship.romantic_love) / 2

        difference = average_mate_love - average_affair_love

        if difference < 0:
            # If the average love between affair partner is greater than the average love between the mate
            affair_chance = 10
            difference = -difference

            if difference > 30:
                affair_chance -= 7
            elif difference > 20:
                affair_chance -= 6
            elif difference > 15:
                affair_chance -= 5
            elif difference > 10:
                affair_chance -= 4

        elif difference > 0:
            # If the average love between the mate is greater than the average relationship between the affair
            affair_chance = 30

            if difference > 30:
                affair_chance += 8
            elif difference > 20:
                affair_chance += 5
            elif difference > 15:
                affair_chance += 3
            elif difference > 10:
                affair_chance += 5

        else:
            # For difference = 0 or some other weird stuff
            affair_chance = 15

        return affair_chance

    def get_unmated_love_affair_chance(self, relation: Relationship):
        """ Get the "love affair" change when neither the cat nor the highest romantic relation have a mate"""

        if not relation.opposite_relationship:
            relation.link_relationship()

        affair_chance = 15
        average_romantic_love = (relation.romantic_love + relation.opposite_relationship.romantic_love) / 2

        # If the highest romantic reltaion has a mate, increase the chance. 
        if relation.cat_to.mate:
            affair_chance = 30

        if average_romantic_love > 50:
            affair_chance -= 12
        elif average_romantic_love > 40:
            affair_chance -= 10
        elif average_romantic_love > 30:
            affair_chance -= 7
        elif average_romantic_love > 10:
            affair_chance -= 5

        return affair_chance

    def _determine_love_affair(self, cat, mate, mate_relation, samesex):
        """ Function to handle everything around love affairs. Will return a second parent if a love
         affair is triggerd, and none otherwise. """

        highest_romantic_relation = get_highest_romantic_relation(cat.relationships.values(), exclude_mate=True,
                                                                  potential_mate=True)

        if mate and highest_romantic_relation:
            # Love affair calculation when the cat has a mate
            chance_love_affair = self.get_love_affair_chance(mate_relation, highest_romantic_relation)
            if not chance_love_affair or not int(random.random() * chance_love_affair):
                if samesex or cat.gender != highest_romantic_relation.cat_to.gender:
                    return highest_romantic_relation.cat_to
        elif highest_romantic_relation:
            # Love affair change if the cat doesn't have a mate:
            chance_love_affair = self.get_unmated_love_affair_chance(highest_romantic_relation)
            if not chance_love_affair or not int(random.random() * chance_love_affair):
                if samesex or cat.gender != highest_romantic_relation.cat_to.gender:
                    return highest_romantic_relation.cat_to

        return None
    def get_second_parent(self, cat, mate=None, affair=game.settings['affair']):
        """ Return the second parent of a cat, which will have kits. Also returns a bool
         that is true if an affair was triggered"""

        second_parent = mate
        if game.settings['no gendered breeding'] is True:
            samesex = True
        else:
            samesex = False

        if not affair:
            # if affairs setting is OFF, second parent will be returned always.
            return second_parent, False

        mate_relation = None
        if mate and mate.ID in cat.relationships:
            mate_relation = cat.relationships[mate.ID]
        elif mate:
            mate_relation = Relationship(cat, mate, True)
            cat.relationships[mate.ID] = mate_relation


        # LOVE AFFAIR
        # Handle love affair chance.
        affair_partner = self._determine_love_affair(cat, mate, mate_relation, samesex)
        if affair_partner:
            return affair_partner, True

        # RANDOM AFFAIR
        # "regular" random affair
        if not int(random.random() * game.config["pregnancy"]["random_affair_chance"]):
            possible_affair_partners = [i for i in Cat.all_cats_list if 
                                        i.is_potential_mate(cat, for_love_interest=True) 
                                        and (samesex or i.gender != cat.gender) 
                                        and cat.mate != i.ID] 
            if possible_affair_partners:
                chosen_affair = choice(possible_affair_partners)
                return chosen_affair, True
        
        # SPECIAL UNMATED RANDOM AFFAIR
        # Special random affair check only for unmated cats. For this check, only
        # other unmated cats can be the affair partner. 
        if not cat.mate and not int(random.random() * game.config["pregnancy"]["unmated_random_affair_chance"]):
            possible_affair_partners = [i for i in Cat.all_cats_list if 
                                        i.is_potential_mate(cat, for_love_interest=True) 
                                        and (samesex or i.gender != cat.gender) 
                                        and not i.mate] 
            if possible_affair_partners:
                chosen_affair = choice(possible_affair_partners)
                return chosen_affair, True

        return second_parent, False

    def get_kits(self, kits_amount, cat, other_cat=None, clan=game.clan):
        # create amount of kits
        all_kitten = []
        backstory_choice_1 = choice(['halfclan1', 'outsider_roots1'])
        backstory_choice_2 = choice(['halfclan2', 'outsider_roots2'])
        for kit in range(kits_amount):
            kit = None
            if other_cat is not None:
                if cat.gender == 'female':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0, status='newborn')
                    kit.thought = f"Snuggles up to the belly of {cat.name}"
                elif cat.gender == 'male' and other_cat.gender == 'male':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0, status='newborn')
                    kit.thought = f"Snuggles up to the belly of {cat.name}"
                else:
                    kit = Cat(parent1=other_cat.ID, parent2=cat.ID, moons=0, status='newborn')
                    kit.thought = f"Snuggles up to the belly of {other_cat.name}"
                cat.birth_cooldown = 6
                other_cat.birth_cooldown = 6
            else:
                if cat.gender == 'female':
                    backstory = backstory_choice_1
                else:
                    backstory = backstory_choice_2
                kit = Cat(parent1=cat.ID, moons=0, backstory=backstory, status='newborn')
                cat.birth_cooldown = 6
                kit.thought = f"Snuggles up to the belly of {cat.name}"
            all_kitten.append(kit)

            # remove scars
            kit.scars.clear()

            # try to give them a permanent condition. 1/90 chance
            # don't delete the game.clan condition, this is needed for a test
            if game.clan and not int(random.random() * game.config["cat_generation"]["base_permanent_condition"]) \
                    and game.clan.game_mode != 'classic':
                kit.congenital_condition(kit)
                for condition in kit.permanent_condition:
                    if kit.permanent_condition[condition] == 'born without a leg':
                        kit.scars.append('NOPAW')
                    elif kit.permanent_condition[condition] == 'born without a tail':
                        kit.scars.append('NOTAIL')
                self.condition_events.handle_already_disabled(kit)

            # create and update relationships
            for cat_id in clan.clan_cats:
                if cat_id == kit.ID:
                    continue
                the_cat = Cat.all_cats.get(cat_id)
                if the_cat.dead or the_cat.outside:
                    continue
                if the_cat.ID in kit.get_parents():
                    y = random.randrange(0, 20)
                    start_relation = Relationship(the_cat, kit, False, True)
                    start_relation.platonic_like += 30 + y
                    start_relation.comfortable = 10 + y
                    start_relation.admiration = 15 + y
                    start_relation.trust = 10 + y
                    the_cat.relationships[kit.ID] = start_relation
                    y = random.randrange(0, 20)
                    start_relation = Relationship(kit, the_cat, False, True)
                    start_relation.platonic_like += 30 + y
                    start_relation.comfortable = 10 + y
                    start_relation.admiration = 15 + y
                    start_relation.trust = 10 + y
                    kit.relationships[the_cat.ID] = start_relation
                else:
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat)
            # remove accessory
            kit.accessory = None
            clan.add_cat(kit)

        # check other cats of clan for siblings
        for kitten in all_kitten:
            add_siblings_to_cat(kitten, cat_class)
            add_children_to_cat(kitten, cat_class)
            # update/buff the relationship towards the siblings
            for second_kitten in all_kitten:
                y = random.randrange(0, 10)
                if second_kitten.ID == kitten.ID:
                    continue
                kitten.relationships[second_kitten.ID].platonic_like += 20 + y
                kitten.relationships[second_kitten.ID].comfortable += 10 + y
                kitten.relationships[second_kitten.ID].trust += 10 + y

        return all_kitten

    def get_amount_of_kits(self, cat):
        """Get the amount of kits which will be born."""
        min_kits = game.config["pregnancy"]["min_kits"]
        min_kit = [min_kits] * game.config["pregnancy"]["one_kit_possibility"][cat.age]
        two_kits = [min_kits + 1] * game.config["pregnancy"]["two_kit_possibility"][cat.age]
        three_kits = [min_kits + 2] * game.config["pregnancy"]["three_kit_possibility"][cat.age]
        four_kits = [min_kits + 3] * game.config["pregnancy"]["four_kit_possibility"][cat.age]
        five_kits = [min_kits + 4] * game.config["pregnancy"]["five_kit_possibility"][cat.age]
        max_kits = [game.config["pregnancy"]["max_kits"]] * game.config["pregnancy"]["max_kit_possibility"][cat.age]
        amount = choice(min_kit + two_kits + three_kits + four_kits + five_kits + max_kits)

        return amount


PREGNANT_STRINGS = None
with open(f"resources/dicts/conditions/pregnancy.json", 'r') as read_file:
    PREGNANT_STRINGS = ujson.loads(read_file.read())