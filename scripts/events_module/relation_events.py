import itertools
import random
from random import choice

try:
    import ujson
except ImportError:
    import json as ujson
import random

from scripts.game_structure.game_essentials import game
from scripts.events_module.condition_events import Condition_Events
from scripts.utility import (
    add_children_to_cat,
    add_siblings_to_cat,
    get_personality_compatibility,
    get_highest_romantic_relation,
    get_med_cats,
    )
from scripts.utility import event_text_adjust
from scripts.cat.cats import Cat, cat_class
from scripts.event_class import Single_Event
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.relationship.mate_events import Mate_Events


# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them.'],
    "troublesome": ['made (cat) and (cat) start an argument.'],
    "sneaky": ['is gossiping about (cat) and (cat).'],
    "like": '(cat) confesses to (cat) that they think they like (cat).',
    "trick": 'has successfully tricked (cat) into believing a crazy tale about the Clan leader.'
}

EXILED_CATS = {
    "cat_to": ['bumped into (cat) at the Clan border.', 'caught a glimpse of (cat) from the distance.'],
    "cat_from": ['was wandering near the Clan territory and met (cat).'],
    "both": ['ran into (cat) by chance.']
}

OUTSIDE_CATS = {
    "cat_to": ['is thinking about (cat).'],
    "cat_from": ['is thinking about (cat) as they wander far from Clan territory.'],
    "both": ['wonders where (cat) is right now.']
}


class Relation_Events():
    """All relationship events."""
    def __init__(self) -> None:
        self.had_one_event = False
        self.condition_events = Condition_Events()
        self.mate_events_class = Mate_Events()
        self.cats_triggered_events = {}
        pass

    def handle_relationships(self, cat: Cat):
        """Checks the relationships of the cat and trigger events if possible.

            Parameters
            ----------
            cat : Cat
                the cat where the relationships should be checked

            Returns
            -------
        """
        if not cat.relationships:
            return
        self.had_one_event = False

        # this has to be handled at first
        if random.random() > 0.8:
            if self.mate_events_class.big_love_check(cat):
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
                    print(f"WARNING: Cat #{cat_from} has a invalid mate. It will set to none.")
                    cat_from.mate = None
                    return
                cat_from_mate = Cat.all_cats.get(cat_from.mate)

            cat_to = current_relationship.cat_to
            cat_to_mate = None
            if cat_to.mate:
                if cat_to.mate not in Cat.all_cats:
                    print(f"WARNING: Cat #{cat_to} has a invalid mate. It will set to none.")
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
                    # game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_from_mate.ID]))
                    current_relationship.mate = False
                    cat_from.mate = None
                    cat_from_mate.mate = None

            # new mates
            if not self.had_one_event and not cat_from_mate:
                if cat_to.is_potential_mate(cat_from):
                    self.mate_events_class.handle_new_mates(current_relationship, cat_from, cat_to)

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
                        other_mate_relationship = cat_to.relationships[cat_to.mate]

                if ((love_over_30 and not normal_chance) or (bigger_than_current and not bigger_love_chance)):
                    self.had_one_event = True
                    # break up the old relationships
                    cat_from_mate = Cat.all_cats.get(cat_from.mate)
                    self.mate_events_class.handle_breakup(mate_relationship, mate_relationship.opposite_relationship, cat_from,
                                        cat_from_mate)

                    if cat_to_mate:
                        # relationship_from, relationship_to, cat_from, cat_to
                        self.mate_events_class.handle_breakup(other_mate_relationship, other_mate_relationship.opposite_relationship,
                                            cat_to, cat_to_mate)

                    # new relationship
                    text = f"{cat_from.name} and {cat_to.name} can't ignore their feelings for each other."
                    # game.relation_events_list.insert(0, text)
                    game.cur_events_list.append(Single_Event(text, "relation", [cat_from.ID, cat_to.ID]))
                    self.mate_events_class.handle_new_mates(current_relationship, cat_from, cat_to)

            # breakup
            if not self.had_one_event and current_relationship.mates and not cat_from.dead and not cat_to.dead:
                if self.check_if_breakup(current_relationship, current_relationship.opposite_relationship, cat_from,
                                         cat_to):
                    self.mate_events_class.handle_breakup(current_relationship, current_relationship.opposite_relationship, cat_from,
                                        cat_to)

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
            living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))

            if not affair:
                if second_parent:
                    chance = 10
                    if second_parent_relation.romantic_love >= 35:
                        chance += 20
                    elif second_parent_relation.romantic_love >= 55:
                        chance += 30
                    elif second_parent_relation.romantic_love >= 85:
                        chance += 40

                    if second_parent_relation.comfortable >= 35:
                        chance += 20
                    elif second_parent_relation.comfortable >= 55:
                        chance += 30
                    elif second_parent_relation.comfortable >= 85:
                        chance += 40
                else:
                    chance = int(200/living_cats) + 2
                old_male = False
                if cat.gender == 'male' and cat.age == 'elder':
                    old_male = True
                if second_parent is not None and second_parent.gender == 'male' and second_parent.age == 'elder':
                    old_male = True

                if old_male:
                    chance = int(chance / 2)
            else:
                # Affairs never cancel - it makes setting affairs number easier.
                chance = 0

            # print("Kit cancel chance", chance)
            if int(random.random() * chance) == 1:
                # Cancel having kits.
                print("kits canceled")
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
            self.get_kits(amount, cat, None, clan)
            insert = 'this should not display'
            if amount == 1:
                insert = 'a single kitten'
            if amount > 1:
                insert = f'a litter of {amount} kits'
            print_event = f"{cat.name} brought {insert} back to camp, but refused to talk about their origin."
            # game.birth_death_events_list.append(print_event)
            game.cur_events_list.append(Single_Event(print_event, "birth_death", cat.ID))
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
        # game.birth_death_events_list.append(text)
        game.cur_events_list.append(Single_Event(text, "birth_death", pregnant_cat.ID))

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
            # game.birth_death_events_list.append(text)
            game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))
        else:
            text = f"{cat.name} thinks that they will have {thinking_amount} kits."
            # game.birth_death_events_list.append(text)
            game.cur_events_list.append(Single_Event(text, "birth_death", cat.ID))

    def handle_two_moon_pregnant(self, cat, clan=game.clan):
        """Handles if the cat is two moons pregnant."""
        # if the pregnant cat is outside or killed meanwhile, delete it from the dictionary
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is outside or killed meanwhile, delete it from the dictionary
        if cat.dead or cat.outside:
            del clan.pregnancy_data[cat.ID]
            return

        involved_cats = [cat.ID]

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
            insert = f'litter of {kits_amount} kits'

        # choose event string
        print_event = ""
        event_list = []
        possible_events = []
        if other_cat is None:
            possible_events = [f"{cat.name} had a {insert}, but refused to talk about their origin.",
                               f"{cat.name} secretly had a {insert}.",
                               f"{cat.name} had a {insert} with an unknown partner.",
                               f"{cat.name} had a {insert} and refused to talk about their progenitor.",
                               f"{cat.name} had a {insert} and is absolutely refusing to talk about it or acknowledge it at all.",
                               f"{cat.name} doesn't feel ready to be a parent of this {insert}. But they promise to the tiny flailing limbs by their side that they'll do their best, they swear on StarClan itself.",
                               f"No one knows who {cat.name} has had their {insert} with, but they seem very happy watching over their little offspring in the nursery.",
                               f"Whenever someone asks whether {cat.name} will be alright raising their {insert} alone, they just smile, and reply that everything is going to work out fine.",
                               f"A {insert}! {cat.name} welcomes them happily, and seems unperturbed by the lack of a partner in the nursery with them."
                               ]
        elif cat.mate == other_cat.ID and not other_cat.dead and not other_cat.outside:
            involved_cats.append(other_cat.ID)
            possible_events = [f"{cat.name} had a {insert} with {other_cat.name}.",
                               f"In the nursery, {cat.name} lies suckling a {insert}, {other_cat.name} watching over them and purring so hard their body vibrates.",
                               f"{cat.name} and {other_cat.name}'s eyes meet over their {insert}, full of love for their growing family.",
                               f"In the quiet of the nursery, in the nest they've spent so long preparing, {cat.name} and {other_cat.name} welcome a {insert}.",
                               f"With their {insert} mewling at their belly, {cat.name}'s long pregnancy has finally given them and {other_cat.name} the expansion to their family they've been hoping and waiting for.",
                               f"Even with {other_cat.name} by their side, {cat.name} doesn't feel ready to be a parent of this {insert}. But they promise to the tiny flailing limbs by their side that they'll do their best, they swear on StarClan itself.",
                               f"{other_cat.name} has been waiting eagerly to meet their offspring. At {cat.name}'s invitation, they crawl into the nursery, purring and joining {cat.name} in licking their {insert} clean.",
                               f"{other_cat.name} has been impatient for the end of {cat.name}'s pregnancy, and when they hear {cat.name} has gone into labor they drop what they're doing and sprint for the nursery, where {cat.name} is bringing a {insert} into the world.",
                               f"{cat.name} is so, so grateful that their adorable {insert} is here - both thrilled to meet them, and thrilled that {other_cat.name} can take a turn parenting while {cat.name} finally takes a little break from the stuffy air of the nursery.",
                               f"{cat.name} and {other_cat.name} were so busy worrying about and looking forward to the birth that it's only now that they look at their {insert}, and wonder what to name them.",
                               f"Purring with {other_cat.name} against their back, {cat.name} feels like they're going to explode with love, looking at their tiny new {insert}."
                               ]
        elif cat.mate == other_cat.ID and other_cat.dead or other_cat.outside:
            involved_cats.append(other_cat.ID)
            possible_events = [
                f"{cat.name} looks at their {insert}, choking on both a purr and a wail. How are they supposed to do this without {other_cat.name}?",
                f"{cat.name} sobs and pushes their new {insert} away from them. They look far too much like {other_cat.name} for {cat.name} to stand the sight of them.",
                f"{cat.name} purrs sadly over the tiny {insert} StarClan has blessed them with. They see {other_cat.name} in their little pawpads, in their ears and eyes and mews.",
                f"Cats call out, but {cat.name} can't be convinced to go back to the nursery. Not with the new {insert} made from them and {other_cat.name} there, taunting {cat.name} with what should have been.",
                f"Looking down at {other_cat.name}'s last gift to them, {cat.name} vows to protect their new {insert}.",
                f"It's so hard, so very, very, nearly insurmountably hard doing this without their mate, but {cat.name} wouldn't change it for the world. This {insert} is the last piece of {other_cat.name} they have."

            ]
        elif cat.mate != other_cat.ID and cat.mate is not None:
            involved_cats.append(other_cat.ID)
            possible_events = [f"{cat.name} secretly had a {insert} with {other_cat.name}.",
                               f"{cat.name} hopes that their {insert} doesn't look too much like "
                               f"{other_cat.name}, otherwise questions might follow.",
                               f"{other_cat.name} goes to visit {cat.name} in the nursery with their "
                               f"new {insert}, on a completely innocent mission to deliver food to the new parent.",
                               f"The newly arrived {insert} that {cat.name} has just given birth to looks "
                               f"suspiciously like {other_cat.name}. "
                               ]
        else:
            possible_events = [f"{cat.name} had a {insert}, but refused to talk about their origin.",
                               f"{cat.name} had a {insert} and refused to talk about their progenitor.",
                               f"{cat.name} doesn't feel ready to be a parent of this {insert}. But they promise to the tiny flailing limbs by their side that they'll do their best, they swear on StarClan itself.",
                               f"Whenever someone asks whether {cat.name} will be alright raising their {insert} alone, they just smile, and reply that everything is going to work out fine.",
                               f"A {insert}! {cat.name} welcomes them happily, and seems unperturbed by the lack of a partner in the nursery with them."
                               ]


        event_list.append(choice(possible_events))

        if not int(random.random() * 40):  # 1/40 chance for a cat to die during childbirth
            possible_events = [
                f"Later, as the medicine cat wails with {cat.name}'s blood streaked through their pelt, and a "
                f"warrior comes to move the body for its vigil, no one knows what to do with the {insert}.",

                f"As the sun tracks across the sky, {cat.name}'s bleeding gets worse and worse. It was still "
                f"worth it, {cat.name} decides, even as the medicine cat fights an impossible battle to keep "
                f"them out of StarClan. Still so worth it.",

                f"The birth was stressful, and {cat.name} is exhausted and still bleeding and really just wants "
                f"to sleep. Unfortunately, they don't ever wake up again.",

                f"{cat.name} wasn't expecting their birth to be so incredibly painful, and as the day wears on "
                f"their condition deteriorates, leaving their {insert} mewling and trying to suckle a cooling body.",

                f"It breaks their heart that they won't get to be with their {insert} as they grow. {cat.name}"
                f" pants out instructions and pleads to their friends around them, as the blood loss from birth "
                f"slowly takes their life.",

                f"However, {cat.name} is too far gone for the herbs they're given to choke down to fix this "
                f"blood loss, and the cats are helpless as {cat.name} slowly slips to StarClan.",

                f"Later, hours later, eons later, the {insert} mews. Outside, {cat.name}'s body cools, the toll "
                f"of birth too much for it.",

                f"Though all looks fine, the Clan will wake to discover {cat.name}'s body cold in the nursery, "
                f"their {insert} mewing in vain for their parent.",

                f"Though birth is always considered a difficult and risky event, no one thought they'd lose "
                f"{cat.name} to it, not after the {insert} was all born and seemed fine. "
                f"They thought the blood loss was under control."
            ]
            if len(get_med_cats(Cat)) == 0 or (len(get_med_cats(Cat)) == 1 and cat.status == 'medicine cat'):  # check number of med cats in the clan
                event_list.append(choice(possible_events[2:]))  # limit possible events to those not mentioned med cats
            else:
                event_list.append(choice(possible_events))
            if cat.status == 'leader':
                game.clan.leader_lives -= 1
                cat.die()
                cat.died_by.append(f" died shortly after kitting")
            else:
                cat.die()
                cat.died_by.append(f"{cat.name} died while kitting.")
        elif game.clan.game_mode != 'classic':  # if cat doesn't die, give recovering from birth
            cat.get_injured("recovering from birth", event_triggered=True)
            if 'blood loss' in cat.injuries:
                possible_events = [f"The birth was stressful and {cat.name} lost a lot of blood.",

                                   f"{cat.name} pants, looking at their wonderful {insert} and deciding that the "
                                   f"pain and blood loss was all worth it.",

                                   f"Weak with blood loss, {cat.name} nevertheless purrs at the sight of "
                                   f"their {insert}.",

                                   f"Though the blood loss did not make the birth any easier for {cat.name}.",

                                   f"Though {cat.name} seems overly exhausted and weak from the birth.",

                                   f"{cat.name} wasn't expecting this birth to be so intensely painful.",

                                   f"Everyone says giving birth is difficult, but {cat.name} feels like this one "
                                   f"has been worse than most.",

                                   f"This will all be worth it, {cat.name} groans, promising themselves that as "
                                   f"the pains of afterbirth rock their exhausted and bleeding body.",

                                   f"{cat.name} chokes down the herbs given to them, retching at the taste but "
                                   f"knowing they need them to stop the blood loss. "
                                   ]

                event_list.append(choice(possible_events))

        print_event = " ".join(event_list)
        # display event
        # game.health_events_list.append(print_event)
        # game.birth_death_events_list.append(print_event)
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

    def get_love_affair_chance(self, mate_relation, affair_relation):
        """ Looks into the current values and calculate the chance of having kits with the affair cat.
            The lower, the more likely they will have affairs. This function should only be called when mate 
            and affair_cat are not the same.

            Returns:
                integer (number)
        """
        affair_chance = 10

        if mate_relation is None:
            if affair_relation.romantic_love > 10:
                affair_chance -= 1
            elif affair_relation.platonic_like > 20:
                affair_chance -= 2
            elif affair_relation.comfortable > 20:
                affair_chance -= 3
            elif affair_relation.trust > 20:
                affair_chance -= 4

        else:
            love_diff_mate_other = mate_relation.romantic_love - affair_relation.romantic_love
            if love_diff_mate_other < 0:
                affair_chance = 8
                if abs(love_diff_mate_other) > 10:
                    affair_chance -= 2
                elif abs(love_diff_mate_other) > 15:
                    affair_chance -= 4
                elif abs(love_diff_mate_other) > 25:
                    affair_chance -= 6
            else:
                # This chance should never be used.
                affair_chance = 100

        if affair_chance < 0:
            affair_chance = 0

        print("Love Affair Chance", affair_chance)
        return affair_chance

    def get_second_parent(self, cat, mate=None, affair=game.settings['affair']):
        """ Return the second parent of a cat, which will have kits. Also returns a bool
         that is true if an affair was triggered"""

        is_affair = False

        second_parent = mate
        if game.settings['no gendered breeding'] is True:
            samesex = True
        else:
            samesex = False

        if not affair:
            # if affairs setting is OFF, second parent will be returned always.
            return second_parent, is_affair

        mate_relation = None
        if mate and mate.ID in cat.relationships:
            mate_relation = cat.relationships[mate.ID]
        elif mate:
            mate_relation = Relationship(cat, mate, True)
            cat.relationships[mate.ID] = mate_relation


        # Handle love affair chance.
        highest_romantic_relation = get_highest_romantic_relation(cat.relationships.values())
        if mate and highest_romantic_relation:
            if highest_romantic_relation.cat_to.ID != mate.ID:
                chance_love_affair = self.get_love_affair_chance(mate_relation, highest_romantic_relation)
                if not chance_love_affair or not int(random.random() * chance_love_affair):
                    print("love affair?")
                    if highest_romantic_relation.cat_to.is_potential_mate(cat, for_love_interest=True):
                        if samesex or cat.gender != highest_romantic_relation.cat_to.gender:
                            print("love affair", str(cat.name), str(highest_romantic_relation.cat_to.name))
                            is_affair = True
                            return highest_romantic_relation.cat_to, is_affair

        # If the love affair chance did not trigger, this code will be reached.
        chance_random_affair = game.config["pregnancy"]["random_affair_chance"]
        if not int(random.random() * chance_random_affair):
            possible_affair_partners = list(filter(lambda x: x.is_potential_mate(cat, for_love_interest=True) and
                                                             (samesex or cat.gender != x.gender) and
                                                              cat.mate != x.ID, Cat.all_cats_list))
            if possible_affair_partners:
                chosen_affair = choice(possible_affair_partners)
                print("random affair", str(cat.name), str(chosen_affair.name))
                is_affair = True
                return chosen_affair, is_affair

        is_affair = False
        return second_parent, is_affair

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
                    kit.thought = f"Snuggles up to the belly of {cat.name}"
                elif cat.gender == 'male' and other_cat.gender == 'male':
                    kit = Cat(parent1=cat.ID, parent2=other_cat.ID, moons=0)
                    kit.thought = f"Snuggles up to the belly of {cat.name}"
                else:
                    kit = Cat(parent1=other_cat.ID, parent2=cat.ID, moons=0)
                    kit.thought = f"Snuggles up to the belly of {other_cat.name}"
                cat.birth_cooldown = 6
                other_cat.birth_cooldown = 6
            else:
                if cat.gender == 'female':
                    backstory = backstory_choice_1
                else:
                    backstory = backstory_choice_2
                kit = Cat(parent1=cat.ID, moons=0, backstory=backstory)
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

    # ---------------------------------------------------------------------------- #
    #                                new event types                               #
    # ---------------------------------------------------------------------------- #

    def mate_events(self):
        """Description will follow."""
        """
        > events unique to mates
        """
        print("TODO")

    def same_age_events(self):
        """Description will follow."""
        """
        > uses the same events as normal interactions but only with cats the same age
        """
        print("TODO")

    def group_events(self):
        """Description will follow."""
        """
        > different outcomes for the cats should be possible
        > should be possible with different amount of cats (dynamically)
        """
        print("TODO")

    def family_events(self):
        """Description will follow."""
        """
        - parent + child
        - siblings
        - grand parents/children
        """
        print("TODO")

    def outsider_events(self):
        """Description will follow."""
        print("TODO")

    def welcome_new_cats(self, new_cats = None):
        """This function will handle the welcome of new cats, if there are new cats in the clan."""
        if new_cats is None or len(new_cats) <= 0:
            return

        for new_cat in new_cats:
            print(new_cat.name)

        print("HERE")

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/relationship_events/"
