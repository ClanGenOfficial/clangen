import itertools

from scripts.utility import *
from scripts.cat.cats import *


class Relation_Events():
    """All relationship events."""

    MAX_ATTEMPTS = 1000

    def __init__(self) -> None:
        self.event_sums = 0
        self.had_one_event = False
        pass

    def handle_relationships(self, cat):
        """
        Check a certain amount of relationships and trigger events.
        :param cat: cat in question
        """
        if not cat.relationships:
            return
        self.had_one_event = False

        # this has to be handled at first
        if random.random() > 0.8:
            if self.big_love_check(cat):
                return

        cats_amount = len(Cat.all_cats)
        # cap the maximal checks
        if cats_amount >= 30:
            range_number = 20
        else:
            range_number = int(cats_amount / 1.5)  # int(1.9) rounds to 1

        # for i in range(0, range_number):
        for _ in itertools.repeat(None, range_number):
            # random_index = randint(0, len(cat.relationships)-1)
            random_index = int(random.random() * len(cat.relationships))
            current_relationship = list(cat.relationships.values())[random_index]
            # get some cats to make easier checks
            cat_from = current_relationship.cat_from
            cat_from_mate = None
            if cat_from.mate:
                if cat_from.mate not in Cat.all_cats:
                    print(f"Cat #{cat_from} has a invalid mate. It will set to none.")
                    cat_from.mate = None
                    return
                cat_from_mate = Cat.all_cats.get(cat_from.mate)

            cat_to = current_relationship.cat_to
            cat_to_mate = None
            if cat_to.mate:
                if cat_to.mate not in Cat.all_cats:
                    print(f"Cat #{cat_to} has a invalid mate. It will set to none.")
                    cat_to.mate = None
                    return
                cat_to_mate = Cat.all_cats.get(cat_to.mate)

            if not current_relationship.opposite_relationship:
                current_relationship.link_relationship()

            # overcome dead mates
            if cat_from_mate and cat_from_mate.dead and cat_from_mate.dead_for >= 4 and "grief stricken" not in cat_from.illnesses:
                # randint is a slow function, don't call it unless we have to.
                if random.random() > 0.96:  # Roughly 1/25
                    self.had_one_event = True
                    text = f'{cat_from.name} will always love {cat_from_mate.name} but has decided to move on.'
                    game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(text)
                    current_relationship.mate = False
                    cat_from.mate = None
                    cat_from_mate.mate = None

            # new mates
            if not self.had_one_event and not cat_from_mate:
                if cat_to.is_potential_mate(cat_from):
                    self.handle_new_mates(current_relationship, cat_from, cat_to)

            # breakup and new mate
            if (not self.had_one_event and cat_from.mate and
                    cat_from.is_potential_mate(cat_to) and cat_to.is_potential_mate(cat_from)
            ):
                love_over_30 = current_relationship.romantic_love > 30 and current_relationship.opposite_relationship.romantic_love > 30

                normal_chance = int(random.random() * 10)

                # compare love value of current mates
                bigger_than_current = False
                bigger_love_chance = int(random.random() * 3)

                mate_relationship = None
                if cat_from.mate in cat_from.relationships:
                    mate_relationship = cat_from.relationships[cat_from.mate]
                    bigger_than_current = current_relationship.romantic_love > mate_relationship.romantic_love
                else:
                    if cat_from_mate:
                        cat_from_mate.relationships[cat_from.ID] = Relationship(cat_from_mate, cat_from, True)
                    bigger_than_current = True

                # check cat_to values
                if cat_to_mate:
                    if cat_from.ID in cat_to.relationships:
                        other_mate_relationship = cat_to.relationships[cat_to.mate]
                        bigger_than_current = (bigger_than_current and
                                               current_relationship.romantic_love
                                               > other_mate_relationship.romantic_love)
                    else:
                        cat_to_mate.relationships[cat_to.ID] = Relationship(cat_to_mate, cat_to, True)

                if ((love_over_30 and not normal_chance) or (bigger_than_current and not bigger_love_chance)):
                    self.had_one_event = True
                    # break up the old relationships
                    cat_from_mate = Cat.all_cats.get(cat_from.mate)
                    self.handle_breakup(mate_relationship, mate_relationship.opposite_relationship, cat_from,
                                        cat_from_mate)

                    if cat_to_mate:
                        # relationship_from, relationship_to, cat_from, cat_to
                        self.handle_breakup(other_mate_relationship, other_mate_relationship.opposite_relationship,
                                            cat_to, cat_to_mate)

                    # new relationship
                    text = f"{cat_from.name} and {cat_to.name} can't ignore their feelings for each other."
                    game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(text)
                    self.handle_new_mates(cat_from, cat_to)

            # breakup
            if not self.had_one_event and current_relationship.mates and not cat_from.dead and not cat_to.dead:
                if self.check_if_breakup(current_relationship, current_relationship.opposite_relationship, cat_from,
                                         cat_to):
                    self.handle_breakup(current_relationship, current_relationship.opposite_relationship, cat_from,
                                        cat_to)

    def handle_pregnancy_age(self, clan):
        """Increase the moon for each pregnancy in the pregnancy dictionary"""
        for pregnancy_key in clan.pregnancy_data.keys():
            clan.pregnancy_data[pregnancy_key]["moons"] += 1

    def handle_having_kits(self, cat, clan):
        """Handles pregnancy of a cat."""
        if not clan:
            return
        if cat.ID in clan.pregnancy_data:
            moons = clan.pregnancy_data[cat.ID]["moons"]
            if moons == 1:
                self.handle_one_moon_pregnant(cat, clan)
                return
            if moons >= 2:
                self.handle_two_moon_pregnant(cat, clan)
                return

        can_have_kits = self.check_if_can_have_kits(cat, game.settings['no unknown fathers'],
                                                    game.settings['no gendered breeding'])
        if not can_have_kits:
            return

        mate = None
        if cat.mate:
            if cat.mate in Cat.all_cats:
                mate = Cat.all_cats[cat.mate]
            else:
                print(f"WARNING: {cat.name}  has an invalid mate # {cat.mate}. This has been unset.")
                cat.mate = None

        # check if there is a cat in the clan for the second parent
        second_parent = self.get_second_parent(cat, mate, game.settings['affair'])
        second_parent_relation = None
        if second_parent and second_parent.ID in cat.relationships:
            second_parent_relation = cat.relationships[second_parent.ID]
        elif second_parent:
            second_parent_relation = Relationship(cat, second_parent)
            cat.relationships[second_parent.ID] = second_parent_relation

        # check if the second_parent is not none, if they also can have kits
        if second_parent:
            parent2_can_have_kits = self.check_if_can_have_kits(second_parent, game.settings['no unknown fathers'],
                                                                game.settings['no gendered breeding'])
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
            f'{name} had a litter of {str(kits_amount)} kit(s) with a ' + choice(
                ['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
            f'{name} had a secret litter of {str(kits_amount)} kit(s) with a ' + choice(
                ['loner', 'rogue', 'kittypet']) + ' named ' + str(loner_name),
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
        relationship_to = relationship.opposite_relationship
        become_mates, mate_string = self.check_if_new_mate(relationship, relationship_to, cat_from, cat_to)

        if become_mates and mate_string:
            self.had_one_event = True
            cat_from.set_mate(cat_to)
            cat_to.set_mate(cat_from)
            game.cur_events_list.append(mate_string)
            game.relation_events_list.append(mate_string)

    def handle_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        from_mate_in_clan = False
        if cat_from.mate:
            if cat_from.mate not in Cat.all_cats.keys():
                print(f"Cat #{cat_from} has a invalid mate. It will set to none.")
                cat_from.mate = None
                return
            cat_from_mate = Cat.all_cats.get(cat_from.mate)
            from_mate_in_clan = cat_from_mate.is_alive() and not cat_from_mate.outside

        if not self.had_one_event and relationship_from.mates and from_mate_in_clan:
            if self.check_if_breakup(relationship_from, relationship_to, cat_from, cat_to):
                # TODO: filter log to check if last interaction was a fight
                had_fight = False
                self.had_one_event = True
                cat_from.unset_mate(breakup=True, fight=had_fight)
                cat_to.unset_mate(breakup=True, fight=had_fight)
                text = f"{cat_from.name} and {cat_to.name} broke up"
                game.relation_events_list.insert(0, text)
                game.cur_events_list.append(text)

    def big_love_check(self, cat, upper_threshold=40, lower_threshold=15):
        """
        Check if the cat has a high love for another and mate them if there are in the boundaries 
        :param cat: cat in question
        :upper_threshold integer:
        :lower_threshold integer:

        return: bool if event is triggered or not
        """
        # get the highest romantic love relationships and
        highest_romantic_relation = get_highest_romantic_relation(cat.relationships.values())
        max_love_value = 0
        if highest_romantic_relation is not None:
            max_love_value = highest_romantic_relation.romantic_love

        if max_love_value < upper_threshold:
            return False

        cat_to = highest_romantic_relation.cat_to
        if cat_to.is_potential_mate(cat) and cat.is_potential_mate(cat_to):
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
                    text = f"{first_name} confessed their feelings to {second_name}, but they got rejected."
                    game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(text)
                    return False
                else:
                    text = f"{first_name} confessed their feelings to {second_name} and they have become mates."
                    game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(text)
                    return True
        return False

    def handle_zero_moon_pregnant(self, cat, other_cat=None, relation=None, clan=game.clan):
        """Handles if the cat is zero moons pregnant."""
        if other_cat and (other_cat.dead or other_cat.outside or other_cat.birth_cooldown > 0):
            return

        if cat.ID in clan.pregnancy_data:
            return

        if other_cat and other_cat.ID in clan.pregnancy_data:
            return

        chance = self.get_kits_chance(cat, other_cat, relation)
        hit = int(random.random() * chance)
        if hit:
            return
        # print(chance)

        # even with no_gendered_breeding on a male cat with no second parent should not be count as pregnant
        # instead, the cat should get the kit instantly
        if not other_cat and cat.gender == 'male':
            amount = self.get_amount_of_kits(cat)
            self.get_kits(amount, cat, None, clan)
            insert = 'this should not display'
            if amount == 1:
                insert = 'a single kitten'
            if amount > 1:
                insert = f'a litter of {str(amount)} kits'
            print_event = f"{str(cat.name)} brought {insert} back to camp, but refused to talk about their origin."
            game.birth_death_events_list.append(print_event)
            game.cur_events_list.append(print_event)
            # display event
            # if len(print_event) < 100:
            #    game.cur_events_list.append(print_event)
            # else:
            #    cut = print_event.find(' ', int(len(print_event)/2))
            #    first_part = print_event[:cut]
            #    second_part = print_event[cut:]
            #    game.cur_events_list.append(first_part)
            #    game.cur_events_list.append(second_part)
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
        text = f"{pregnant_cat.name} announced that they are expecting kits."
        game.birth_death_events_list.append(text)
        game.cur_events_list.append(text)

    def handle_one_moon_pregnant(self, cat, clan=game.clan):
        """Handles if the cat is one moon pregnant."""
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is outside or killed meanwhile, delete it from the dictionary
        if cat.dead or cat.outside:
            del clan.pregnancy_data[cat.ID]
            return

        amount = self.get_amount_of_kits(cat)
        thinking_amount = choice([amount - 1, amount, amount + 1])
        if thinking_amount < 1:
            thinking_amount = 1

        # add the amount to the pregnancy dict
        clan.pregnancy_data[cat.ID]["amount"] = amount

        if thinking_amount == 1:
            text = f"{cat.name} thinks that they will have one kit."
            game.birth_death_events_list.append(text)
            game.cur_events_list.append(text)
        else:
            text = f"{cat.name} thinks that they will have {thinking_amount} kits."
            game.birth_death_events_list.append(text)
            game.cur_events_list.append(text)

    def handle_two_moon_pregnant(self, cat, clan=game.clan):
        """Handles if the cat is two moons pregnant."""
        # if the pregnant cat is outside or killed meanwhile, delete it from the dictionary
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is outside or killed meanwhile, delete it from the dictionary
        if cat.dead or cat.outside:
            del clan.pregnancy_data[cat.ID]
            return

        kits_amount = clan.pregnancy_data[cat.ID]["amount"]
        other_cat_id = clan.pregnancy_data[cat.ID]["second_parent"]
        other_cat = Cat.all_cats.get(other_cat_id)

        kits_amount = self.get_kits(kits_amount, cat, other_cat, clan)
        kits_amount = len(kits_amount)

        # delete the cat out of the pregnancy dictionary
        del clan.pregnancy_data[cat.ID]

        insert = 'this should not display'
        if kits_amount == 1:
            insert = 'single kitten'
        if kits_amount > 1:
            insert = f'litter of {str(kits_amount)} kits'

        # choose event string
        print_event = ""
        event_list = []
        possible_events = []
        if other_cat is None:
            possible_events = [f"{str(cat.name)} had a {insert}, but refused to talk about their origin.",
                               f"{str(cat.name)} secretly had a {insert}.",
                               f"{str(cat.name)} had a {insert} with an unknown partner.",
                               f"{str(cat.name)} had a {insert} and refused to talk about their progenitor.",
                               f"{str(cat.name)} had a {insert} and is absolutely refusing to talk about it or acknowledge it at all.",
                               f"{str(cat.name)} doesn't feel ready to be a parent of this {insert}. But they promise to the tiny flailing limbs by their side that they'll do their best, they swear on StarClan itself.",
                               f"No one knows who {str(cat.name)} has had their {insert} with, but they seem very happy watching over their little offspring in the nursery",
                               f"Whenever someone asks whether {str(cat.name)} will be alright raising their {insert} alone, they just smile, and reply that everything is going to work out fine.",
                               f"A {insert}! {str(cat.name)} welcomes them happily, and seems unperturbed by the lack of a partner in the nursery with them."
                               ]
        elif cat.mate == other_cat.ID and not other_cat.dead and not other_cat.outside:
            possible_events = [f"{str(cat.name)} had a {insert} with {str(other_cat.name)}.",
                               f"In the nursery, {str(cat.name)} lies suckling a {insert}, {str(other_cat.name)} watching over them and purring so hard their body vibrates.",
                               f"{str(cat.name)} and {str(other_cat.name)}'s eyes meet over their {insert}, full of love for their growing family.",
                               f"In the quiet of the nursery, in the nest they've spent so long preparing, {str(cat.name)} and {str(other_cat.name)} welcome a {insert}.",
                               f"With their {insert} mewling at their belly, {str(cat.name)}'s long pregnancy has finally given them and {str(other_cat.name)} the expansion to their family they've been hoping and waiting for.",
                               f"Even with {str(other_cat.name)} by their side, {str(cat.name)} doesn't feel ready to be a parent of this {insert}. But they promise to the tiny flailing limbs by their side that they'll do their best, they swear on StarClan itself.",
                               f"{str(other_cat.name)} has been waiting eagerly to meet their offspring. At {str(cat.name)}'s invitation, they crawl into the nursery, purring and joining {str(cat.name)} in licking their {insert} clean.",
                               f"{str(other_cat.name)} has been impatient for the end of {str(cat.name)}'s pregnancy, and when they hear {str(cat.name)} has gone into labor they drop what they're doing and sprint for the nursery, where {str(cat.name)} is bringing a {insert} into the world.",
                               f"{str(cat.name)} is so, so grateful that their adorable {insert} is here - both thrilled to meet them, and thrilled that {str(other_cat.name)} can take a turn parenting while {str(cat.name)} finally takes a little break from the stuffy air of the nursery.",
                               f"{str(cat.name)} and {str(other_cat.name)} were so busy worrying about and looking forward to the birth that it's only now that they look at their {insert}, and wonder what to name them.",
                               f"Purring with {str(other_cat.name)} against their back, {str(cat.name)} feels like they're going to explode with love, looking at their tiny new {insert}."
                               ]
        elif cat.mate == other_cat.ID and other_cat.dead or other_cat.outside:
            possible_events = [
                f"{str(cat.name)} looks at their {insert}, choking on both a purr and a wail. How are they supposed to do this without {str(other_cat.name)}?",
                f"{str(cat.name)} sobs and pushes their new {insert} away from them. They look far too much like {str(other_cat.name)} for {str(cat.name)} to stand the sight of them.",
                f"{str(cat.name)} purrs sadly over the tiny {insert} StarClan has blessed them with. They see {str(other_cat.name)} in their little pawpads, in their ears and eyes and mews.",
                f"Cats call out, but {str(cat.name)} can't be convinced to go back to the nursery. Not with the new {insert} made from them and {str(other_cat.name)} there, taunting {str(cat.name)} with what should have been.",
                f"Looking down at {str(other_cat.name)}'s last gift to them, {str(cat.name)} vows to protect their new {insert}.",
                f"It's so hard, so very, very, nearly insurmountably hard doing this without their mate, but {str(cat.name)} wouldn't change it for the world. This {insert} is the last piece of {str(other_cat.name)} they have."

            ]
        elif cat.mate != other_cat.ID and cat.mate is not None:
            possible_events = [f"{str(cat.name)} secretly had a {insert} with {str(other_cat.name)}.",
                               f"{str(cat.name)} hopes that their {insert} doesn't look too much like "
                               f"{str(other_cat.name)}, otherwise questions might follow.",
                               f"{str(other_cat.name)} goes to visit {str(cat.name)} in the nursery with their "
                               f"new {insert}, on a completely innocent mission to deliver food to the new parent.",
                               f"The newly arrived {insert} that {str(cat.name)} has just given birth to looks "
                               f"suspiciously like {str(other_cat.name)}. "
                               ]
        else:
            possible_events = [f"{str(cat.name)} had a {insert}, but refused to talk about their origin.",
                               f"{str(cat.name)} had a {insert} and refused to talk about their progenitor.",
                               f"{str(cat.name)} doesn't feel ready to be a parent of this {insert}. But they promise to the tiny flailing limbs by their side that they'll do their best, they swear on StarClan itself.",
                               f"Whenever someone asks whether {str(cat.name)} will be alright raising their {insert} alone, they just smile, and reply that everything is going to work out fine.",
                               f"A {insert}! {str(cat.name)} welcomes them happily, and seems unperturbed by the lack of a partner in the nursery with them."
                               ]


        event_list.append(choice(possible_events))

        if not int(random.random() * 40):  # 1/40 chance for a cat to die during childbirth
            possible_events = [
                f"Later, as the medicine cat wails with {str(cat.name)}'s blood streaked through their pelt, and a warrior comes to move the body for its vigil, no one knows what to do with the {insert}.",
                f"As the sun tracks across the sky, {str(cat.name)}'s bleeding gets worse and worse. It was still worth it, {str(cat.name)} decides, even as the medicine cat fights an impossible battle to keep them out of StarClan. Still so worth it.",
                f"The birth was stressful, and {str(cat.name)} is exhausted and still bleeding and really just wants to sleep. Unfortunately, they don't ever wake up again.",
                f"{str(cat.name)} wasn't expecting their birth to be so incredibly painful, and as the day wears on their condition deteriorates, leaving their {insert} mewling and trying to suckle a cooling body.",
                f"It breaks their heart that they won't get to be with their {insert} as they grow. {str(cat.name)} pants out instructions and pleads to their friends around them, as the blood loss from birth slowly takes their life.",
                f"However, {str(cat.name)} is too far gone for the herbs they're given to choke down to fix this blood loss, and the cats are helpless as {str(cat.name)} slowly slips to StarClan.",
                f"Later, hours later, eons laters, the {insert} mews. Outside, {str(cat.name)}'s body cools, the toll of birth too much for it.",
                f"Though all looks fine, the clan will wake to discover {str(cat.name)}'s body cold in the nursery, their {insert} mewing in vain for their parent.",
                f"Though birth is always considered a difficult and risky event, no one thought they'd lose {str(cat.name)} to it, not after the {insert} was all born and seemed fine. They thought the blood loss was under control."
            ]
            if len(get_med_cats(Cat)) == 0:  # check number of med cats in the clan
                event_list.append(choice(possible_events[2:]))  # limit possible events to those not mentioned med cats
            else:
                event_list.append(choice(possible_events))
            if cat.status == 'leader':
                game.clan.leader_lives -= 1
            cat.die()
        else:  # if cat doesn't die, give recovering from birth
            cat.get_injured("recovering from birth", event_triggered=True)
            if 'blood loss' in cat.injuries:
                possible_events = [f"The birth was stressful and {str(cat.name)} lost a lot of blood.",
                                   f"{str(cat.name)} pants, looking at their wonderful {insert} and deciding that the pain and blood loss was all worth it.",
                                   f"Weak with blood loss, {str(cat.name)} nevertheless purrs at the sight of their {insert}.",
                                   f"Though the blood loss did not make the birth any easier for {str(cat.name)}.",
                                   f"Though {str(cat.name)} seems overly exhausted and weak from the birth.",
                                   f"{str(cat.name)} wasn't expecting this birth to be so intensely painful.",
                                   f"Everyone says giving birth is difficult, but {str(cat.name)} feels like this one has been worse than most.",
                                   f"This will all be worth it, {str(cat.name)} groans, promising themselves that as the pains of afterbirth rock their exhausted and bleeding body.",
                                   f"{str(cat.name)} chokes down the herbs given to them, retching at the taste but knowing they need them to stop the blood loss."
                                   ]

                event_list.append(choice(possible_events))

        print_event = " ".join(event_list)
        # display event
        game.health_events_list.append(print_event)
        game.birth_death_events_list.append(print_event)
        game.cur_events_list.append(print_event)

    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    def check_if_breakup(self, relationship_from, relationship_to, cat_from, cat_to):
        """ More in depth check if the cats will break up.
            Returns:
                bool (True or False)
        """
        will_break_up = False
        # TODO: Check log for had fight check
        had_fight = False

        chance_number = self.get_breakup_chance(relationship_from, relationship_to, cat_from, cat_to)

        # chance = randint(1, chance_number)
        chance = int(random.random() * chance_number)
        if not chance:
            if relationship_from.dislike > 30:
                will_break_up = True
                relationship_to.romantic_love -= 10
                relationship_from.romantic_love -= 10
            elif relationship_from.romantic_love < 50:
                will_break_up = True
                relationship_to.romantic_love -= 10
                relationship_from.romantic_love -= 10
            elif had_fight:
                text = f"{str(cat_from.name)} and {str(cat_to.name)} had a fight and nearly broke up."
                game.relation_events_list.insert(0, text)
                game.cur_events_list.append(text)
            else:
                text = f"{str(cat_from.name)} and {str(cat_to.name)} have somewhat different views about their relationship."
                game.relation_events_list.insert(0, text)
                game.cur_events_list.append(text)
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

        if 'recovering from birth' in cat.injuries:
            return can_have_kits

        # decide chances of having kits, and if it's possible at all
        not_correct_age = cat.age in ['kitten', 'adolescent'] or cat.moons < 15
        if not_correct_age or cat.no_kits or cat.dead:
            return can_have_kits

        # check for mate
        mate = None
        if cat.mate:
            if cat.mate in cat.all_cats:
                mate = cat.all_cats[cat.mate]
            else:
                print(f"WARNING: {str(cat.name)}  has an invalid mate # {str(cat.mate)}. This has been unset.")
                cat.mate = None

        if mate and mate.dead:
            return can_have_kits

        if mate:
            if mate.gender == cat.gender and not no_gendered_breeding:
                return can_have_kits
        else:
            if not unknown_parent_setting:
                return can_have_kits

        # if function reaches this point, having kits is possible
        can_have_kits = True
        return can_have_kits

    def check_if_new_mate(self, relationship_from, relationship_to, cat_from, cat_to):
        """Checks if the two cats can become mates, or not. Returns: boolean and event_string"""
        become_mates = False
        young_age = ['kitten', 'adolescent']
        if cat_from.age in young_age or cat_to.age in young_age:
            return become_mates

        mate_string = None
        mate_chance = 5
        hit = int(random.random() * mate_chance)

        # has to be high because every moon this will be checked for each relationship in the came
        random_mate_chance = 300
        random_hit = int(random.random() * random_mate_chance)

        low_dislike = relationship_from.dislike < 15 and relationship_to.dislike < 15
        high_like = relationship_from.platonic_like > 30 and relationship_to.platonic_like > 30
        semi_high_like = relationship_from.platonic_like > 20 and relationship_to.platonic_like > 20
        high_comfort = relationship_from.comfortable > 25 and relationship_to.comfortable > 25

        if not hit and relationship_from.romantic_love > 20 and relationship_to.romantic_love > 20 and semi_high_like:
            mate_string = f"{cat_from.name} and {cat_to.name} have become mates."
            become_mates = True
        elif not random_hit and low_dislike and (high_like or high_comfort):
            mate_string = f"{cat_from.name} and {cat_to.name} see each other in a different light and have become mates."
            become_mates = True

        return become_mates, mate_string

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
            last_log = relationship_from.log[len(relationship_from.log) - 1]

            if 'negative' in last_log:
                chance_number -= 30
                if 'fight' in last_log:
                    chance_number -= 20

            # check all interactions - the logs are still buggy
            # negative_interactions = list(filter(lambda inter: 'negative' in inter, relationship_from.log))
            # chance_number -= len(negative_interactions)
            # positive_interactions = list(filter(lambda inter: 'positive' in inter, relationship_from.log))
            # chance_number += len(positive_interactions)

            # if len(negative_interactions) > len(positive_interactions) and len(relationship_from.log) > 5 :
            #    chance_number -= 20

        # this should be nearly impossible, that chance is lower than 0
        if chance_number <= 0:
            chance_number = 1

        return chance_number

    def get_kits_chance(self, cat, other_cat=None, relation=None):
        """ Looks into the current values and calculate the chance of having kittens. The lower, the more likely they will have kittens.
            Returns:
                integer (number)
        """
        living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))

        old_male = False
        if cat.gender == 'male' and cat.age == 'elder':
            old_male = True
        if other_cat is not None and other_cat.gender == 'male' and other_cat.age == 'elder':
            old_male = True

        # calculate the chance of having kits
        chance = 100
        if other_cat is not None:
            chance = 40
            if relation.romantic_love >= 45:
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

        if other_cat is None:
            chance = int(int(living_cats) * 45)
        if chance > 20 > living_cats:
            chance -= 10

        return chance

    def get_affair_chance(self, mate_relation, affair_relation):
        """ Looks into the current values and calculate the chance of having kits with the affair cat.
            The lower, the more likely they will have affairs. This function should only be called when mate 
            and affair_cat are not the same.

            Returns:
                integer (number)
        """
        affair_chance = 10

        if mate_relation is None:
            if affair_relation.romantic_love > 10:
                affair_chance -= 2
            if affair_relation.platonic_like > 20:
                affair_chance -= 2
            if affair_relation.comfortable > 20:
                affair_chance -= 3
            if affair_relation.trust > 20:
                affair_chance -= 3

        else:
            love_diff_mate_other = mate_relation.romantic_love - affair_relation.romantic_love
            if love_diff_mate_other < 0:
                affair_chance = 5
                if abs(love_diff_mate_other) > 20:
                    affair_chance -= 1
                if abs(love_diff_mate_other) > 25:
                    affair_chance -= 3
                if abs(love_diff_mate_other) > 30:
                    affair_chance -= 4
            else:
                affair_chance += love_diff_mate_other

        return affair_chance

    def get_second_parent(self, cat, mate=None, affair=game.settings['affair']):
        """ Return the second parent of a cat, which will have kits."""
        second_parent = mate
        if game.settings['no gendered breeding'] is True:
            samesex = True
        else:
            samesex = False
        if not affair:
            # if affairs setting is OFF, None will be returned
            return second_parent

        mate_relation = None
        if mate and mate.ID in cat.relationships:
            mate_relation = cat.relationships[mate.ID]
        elif mate:
            mate_relation = Relationship(cat, mate, True)
            cat.relationships[mate.ID] = mate_relation

        highest_romantic_relation = get_highest_romantic_relation(cat.relationships.values())
        if highest_romantic_relation is None:
            return second_parent
        if mate:
            if highest_romantic_relation.cat_to.ID == mate.ID:
                return second_parent

        # the function should only call if highest_romantic_cat is not the mate
        chance_affair = self.get_affair_chance(mate_relation, highest_romantic_relation)

        # a chance of 0 should always be a "auto hit"
        # if chance_affair == 0 or randint(1, chance_affair) == 1:
        if not chance_affair or not int(random.random() * chance_affair):
            if highest_romantic_relation.cat_to.is_potential_mate(cat):
                if cat.gender == highest_romantic_relation.cat_to.gender and samesex:
                    second_parent = highest_romantic_relation.cat_to

        return second_parent

    def get_kits(self, kits_amount, cat, other_cat=None, clan=game.clan):
        # create amount of kits
        all_kitten = []
        backstory_choice_1 = choice(['halfclan1', 'outsider_roots1'])
        backstory_choice_2 = choice(['halfclan2', 'outsider_roots2'])
        for kit in range(kits_amount):
            kit = None
            if other_cat is not None:
                if cat.gender == 'female':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0)
                    all_kitten.append(kit)
                    kit.thought = f"Snuggles up to the belly of {cat.name}"
                elif cat.gender == 'male' and other_cat.gender == 'male':
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
                if cat.gender == 'female':
                    backstory = backstory_choice_1
                else:
                    backstory = backstory_choice_2
                kit = Cat(parent1=cat.ID, moons=0, backstory=backstory)
                all_kitten.append(kit)
                cat.birth_cooldown = 6
                kit.thought = f"Snuggles up to the belly of {cat.name}"

            # remove scars
            kit.scars.clear()

            # try to give them a permanent condition. 1/100 chance
            if not int(random.random() * 90) and game.clan.game_mode != 'classic':
                kit.congenital_condition(kit)
                for condition in kit.permanent_condition:
                    if kit.permanent_condition[condition] == 'born without a leg':
                        kit.scars.append('NOPAW')
                    elif kit.permanent_condition[condition] == 'born without a tail':
                        kit.scars.append('NOTAIL')

            # create and update relationships
            for cat_id in clan.clan_cats:
                the_cat = Cat.all_cats.get(cat_id)
                if the_cat.dead or the_cat.outside:
                    continue
                if the_cat.ID in kit.get_parents():
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit, False, True)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat, False, True)
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

        return all_kitten

    def get_amount_of_kits(self, cat):
        """Get the amount of kits which will be born."""
        one_kit_possibility = {"young adult": 8, "adult": 9, "senior adult": 10, "elder": 4}
        two_kit_possibility = {"young adult": 10, "adult": 13, "senior adult": 15, "elder": 3}
        three_kit_possibility = {"young adult": 17, "adult": 15, "senior adult": 5, "elder": 1}
        four_kit_possibility = {"young adult": 12, "adult": 8, "senior adult": 2, "elder": 0}
        five_kit_possibility = {"young adult": 6, "adult": 2, "senior adult": 0, "elder": 0}
        six_kit_possibility = {"young adult": 2, "adult": 0, "senior adult": 0, "elder": 0}
        one_kit = [1] * one_kit_possibility[cat.age]
        two_kits = [2] * two_kit_possibility[cat.age]
        three_kits = [3] * three_kit_possibility[cat.age]
        four_kits = [4] * four_kit_possibility[cat.age]
        five_kits = [5] * five_kit_possibility[cat.age]
        six_kits = [6] * six_kit_possibility[cat.age]
        amount = choice(one_kit + two_kits + three_kits + four_kits + five_kits + six_kits)

        return amount
