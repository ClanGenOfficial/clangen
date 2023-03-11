from scripts.cat.names import names
from scripts.cat.pelts import collars
from scripts.cat_relations.relationship import Relationship

import random

from scripts.cat.cats import Cat, INJURIES, PERMANENT, cat_class
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values, add_siblings_to_cat, \
    add_children_to_cat
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event


# ---------------------------------------------------------------------------- #
#                               New Cat Event Class                              #
# ---------------------------------------------------------------------------- #

class NewCatEvents:
    """All events with a connection to new cats."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        self.generate_events = GenerateEvents()
        pass

    def handle_new_cats(self, cat, other_cat, war, enemy_clan, alive_kits):
        """ 
        This function handles the new cats
        """
        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{other_clan.name}Clan'

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{other_clan.name}Clan'

        possible_events = self.generate_events.possible_short_events(cat.status, cat.age, "new_cat")
        final_events = self.generate_events.filter_possible_short_events(possible_events, cat, other_cat, war, enemy_clan,
                                                                   other_clan, alive_kits)
        if self.has_outside_cat():
            if random.randint(1,3) == 1:
                outside_cat = self.select_outside_cat()
                backstory = outside_cat.status
                self.update_cat_properties(outside_cat)
                game.clan.add_cat(outside_cat)
                Cat.outside_cats.pop(outside_cat.ID)
                event_text = f"A {backstory} named {outside_cat.name} waits on the border, asking to join the Clan."
                name_change = random.choice([1,2])
                if name_change == 1:
                    event_text = event_text + f" They decide to keep their name."
                elif name_change == 2:
                    outside_cat.name.status = 'warrior'
                    outside_cat.name.prefix = random.choice(names.names_dict["normal_prefixes"])
                    outside_cat.name.suffix = random.choice(names.names_dict["normal_suffixes"])
                    event_text = event_text + f" They decide to take a new name, {outside_cat.name}."
                outside_cat.thought = "Is looking around the camp with wonder"
                involved_cats = [outside_cat.ID]
                game.cur_events_list.append(Single_Event(event_text, ["misc"], involved_cats))
                
                # add them 
                for the_cat in outside_cat.all_cats.values():
                    if the_cat.dead or the_cat.outside or the_cat.ID == outside_cat.ID:
                        continue
                    the_cat.relationships[outside_cat.ID] = Relationship(the_cat, outside_cat)
                    outside_cat.relationships[the_cat.ID] = Relationship(outside_cat, the_cat)

                return [outside_cat]
        # ---------------------------------------------------------------------------- #
        #                                cat creation                                  #
        # ---------------------------------------------------------------------------- #
        try:
            new_cat_event = (random.choice(final_events))
        except:
            print('ERROR: no new cat moon events available')
            return

        involved_cats = []
        if "m_c" in new_cat_event.tags:
            involved_cats = [cat.ID]

        if "other_cat" in new_cat_event.tags:
            involved_cats = [other_cat.ID]
        else:
            other_cat = None

        if "parent" in new_cat_event.tags:
            parent = True
        else:
            parent = False

        status = None
        if "new_warrior" in new_cat_event.tags:
            status = "warrior"
        elif "new_app" in new_cat_event.tags:
            status = "apprentice"
        elif "new_med_app" in new_cat_event.tags:
            status = "medicine cat apprentice"
        elif "new_med" in new_cat_event.tags:
            status = "medicine cat"

        created_cats = self.create_new_cat(new_cat_event.loner,
                                           new_cat_event.new_name,
                                           new_cat_event.kittypet,
                                           new_cat_event.kit,
                                           new_cat_event.litter,
                                           involved_cats[0] if involved_cats else None,
                                           new_cat_event.backstory,
                                           new_cat_event.other_clan,
                                           parent,
                                           status
                                           )

        for new_cat in created_cats:
            involved_cats.append(new_cat.ID)

        # give injuries to other cat if tagged as such
        if "injured" in new_cat_event.tags and game.clan.game_mode != "classic":
            major_injuries = []
            if "major_injury" in new_cat_event.tags:
                for injury in INJURIES:
                    if INJURIES[injury]["severity"] == "major":
                        major_injuries.append(injury)
            for new_cat in created_cats:
                for tag in new_cat_event.tags:
                    if tag in INJURIES:
                        new_cat.get_injured(tag)
                    elif tag == "major_injury":
                        injury = random.choice(major_injuries)
                        new_cat.get_injured(injury)

        # handle other clan shenanigans
        if "war" in new_cat_event.tags and other_clan is not None and enemy_clan is not None:
            other_clan = enemy_clan
            other_clan_name = other_clan.name + "clan"

        if "rel_down" in new_cat_event.tags:
            difference = -5
            change_clan_relations(other_clan, difference=difference)

        elif "rel_up" in new_cat_event.tags:
            difference = 5
            change_clan_relations(other_clan, difference=difference)

        event_text = event_text_adjust(Cat, new_cat_event.event_text, cat, other_cat, other_clan_name, new_cat=created_cats[0])

        types = ["misc"]
        if "other_clan" in new_cat_event.tags:
            types.append("other_clans")
        game.cur_events_list.append(Single_Event(event_text, types, involved_cats))

        return created_cats
        # game.birth_death_events_list.append(death_text)

    def create_new_cat(self,
                       loner=False,
                       new_name=False,
                       kittypet=False,
                       kit=False,
                       litter=False,
                       relevant_cat=None,
                       backstory=None,
                       other_clan=None,
                       parent=False,
                       status=None):
        accessory = None
        backstory = random.choice(backstory)
        relevant_cat = Cat.fetch_cat(relevant_cat)
        age = None

        created_cats = []

        if not litter:
            number_of_cats = 1
        else:
            number_of_cats = random.choices([1, 2, 3, 4, 5], [2, 5, 4, 1, 1], k=1)
            number_of_cats = number_of_cats[0]
            if parent:
                number_of_cats += 1
        # setting age
        if (litter or kit) and not parent:
            age = random.randint(0, 5)
        elif status == 'apprentice':
            age = random.randint(6, 11)
        elif status == 'warrior' or ((litter or kit) and parent):
            age = random.randint(16, 120)
        else:
            age = random.randint(6, 120)
        # setting status
        if not status:
            if age < 6:
                status = "kitten"
            elif 6 <= age <= 11:
                status = "apprentice"
            elif age >= 12:
                status = "warrior"

        for index in range(number_of_cats):
            # cat creation and naming time
            if other_clan or ((kit or litter) and not parent):
                new_cat = Cat(moons=age, status=status, gender=random.choice(['female', 'male']),
                              backstory=backstory)
                print('other clan')
            else:
                if kittypet:
                    print('kittypet')
                    name = random.choice(names.names_dict["loner_names"])
                    if random.choice([1, 2]) == 1:
                        accessory = random.choice(collars)
                elif loner and random.choice([1, 2]) == 1:
                    print('loner')
                    name = random.choice(names.names_dict["loner_names"])
                else:
                    name = random.choice(names.names_dict["normal_prefixes"])

                if new_name:
                    print('new name')
                    if random.choice([1, 2]) == 1:  # adding suffix to OG name
                        spaces = name.count(" ")
                        if spaces > 0:
                            # make a list of the words within the name, then add the OG name back in the list
                            words = name.split(" ")
                            words.append(name)
                            new_prefix = random.choice(words)  # pick new prefix from that list
                            name = new_prefix
                        new_cat = Cat(moons=age, prefix=name, status=status, gender=random.choice(['female', 'male']),
                                      backstory=backstory)
                    else:  # completely new name
                        new_cat = Cat(moons=age, status=status, gender=random.choice(['female', 'male']),
                                      backstory=backstory)
                else:  # keeping old name
                    print('old name')
                    new_cat = Cat(moons=age, prefix=name, suffix="", status=status,
                                  gender=random.choice(['female', 'male']),
                                  backstory=backstory)

            # give em a collar if they got one
            if accessory:
                new_cat.accessory = accessory

            # parents for the babies
            if (kit or litter) and relevant_cat and relevant_cat.ID in Cat.all_cats:
                new_cat.parent1 = relevant_cat.ID
                if relevant_cat.mate:
                    new_cat.parent2 = relevant_cat.mate

            # create and update relationships
            for the_cat in new_cat.all_cats.values():
                if the_cat.dead or the_cat.outside:
                    continue
                the_cat.relationships[new_cat.ID] = Relationship(the_cat, new_cat)
                new_cat.relationships[the_cat.ID] = Relationship(new_cat, the_cat)
            if relevant_cat:
                new_to_clan_cat = game.config["new_cat"]["rel_buff"]["new_to_clan_cat"]
                clan_cat_to_new = game.config["new_cat"]["rel_buff"]["clan_cat_to_new"]
                change_relationship_values(
                    cats_to=        [relevant_cat.ID], 
                    cats_from=      [new_cat],
                    romantic_love=  new_to_clan_cat["romantic"],
                    platonic_like=  new_to_clan_cat["platonic"],
                    dislike=        new_to_clan_cat["dislike"],
                    admiration=     new_to_clan_cat["admiration"],
                    comfortable=    new_to_clan_cat["comfortable"],
                    jealousy=       new_to_clan_cat["jealousy"],
                    trust=          new_to_clan_cat["trust"]
                )
                change_relationship_values(
                    cats_to=        [new_cat.ID], 
                    cats_from=      [relevant_cat],
                    romantic_love=  clan_cat_to_new["romantic"],
                    platonic_like=  clan_cat_to_new["platonic"],
                    dislike=        clan_cat_to_new["dislike"],
                    admiration=     clan_cat_to_new["admiration"],
                    comfortable=    clan_cat_to_new["comfortable"],
                    jealousy=       clan_cat_to_new["jealousy"],
                    trust=          clan_cat_to_new["trust"]
                )

            # newbie thought
            new_cat.thought = 'Is looking around the camp with wonder'

            # give apprentice aged cat a mentor
            if new_cat.age == 'adolescent':
                new_cat.update_mentor()

            # Remove disabling scars, if they generated.
            not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 'LEFTBLIND',
                           'BRIGHTHEART', 'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
            for scar in new_cat.scars:
                if scar in not_allowed:
                    new_cat.scars.remove(scar)

            # chance to give the new cat a permanent condition, higher chance for found kits and litters
            if game.clan.game_mode != 'classic':
                if kit or litter:
                    chance = int(game.config["cat_generation"]["base_permanent_condition"] / 11.25)
                else:
                    chance = game.config["cat_generation"]["base_permanent_condition"] + 10
                if not int(random.random() * chance):
                    possible_conditions = []
                    for condition in PERMANENT:
                        possible_conditions.append(condition)
                    chosen_condition = random.choice(possible_conditions)
                    born_with = False
                    if PERMANENT[chosen_condition]['congenital'] in ['always', 'sometimes']:
                        born_with = True

                    new_cat.get_permanent_condition(chosen_condition, born_with)

                    # assign scars
                    if chosen_condition in ['lost a leg', 'born without a leg']:
                        new_cat.scars.append('NOPAW')
                    elif chosen_condition in ['lost their tail', 'born without a tail']:
                        new_cat.scars.append("NOTAIL")

            # set this as false to indicate that a parent has been created if they joined w their kits
            parent = False

            # and they exist now
            created_cats.append(new_cat)

        for new_cat in created_cats:
            add_siblings_to_cat(new_cat, cat_class)
            add_children_to_cat(new_cat, cat_class)
            game.clan.add_cat(new_cat)

        return created_cats

    def has_outside_cat(self):
        outside_cats = (cat for id, cat in Cat.outside_cats.items() if cat.status in ['kittypet', 'loner', 'rogue'] and not cat.dead)
        return any(outside_cats)
    
    def select_outside_cat(self):
        for cat_id, cat in Cat.outside_cats.items():
            if cat.status in ["kittypet", "loner", "rogue"] and not cat.dead:
                return cat

    def update_cat_properties(self, cat):
        cat.backstory = cat.status + str(random.choice([1, 2]))
        cat.status = "warrior"
        cat.outside = False
