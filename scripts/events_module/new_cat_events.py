from scripts.cat.names import names
from scripts.cat_relations.relationship import Relationship

import random

from scripts.cat.cats import Cat, INJURIES, BACKSTORIES
from scripts.events_module.generate_events import GenerateEvents
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values, create_new_cat
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event


# ---------------------------------------------------------------------------- #
#                               New Cat Event Class                              #
# ---------------------------------------------------------------------------- #

class NewCatEvents:
    """All events with a connection to new cats."""

    def __init__(self) -> None:
        self.event_sums = 0
        self.had_one_event = False
        self.generate_events = GenerateEvents()
        pass

    def handle_new_cats(self, cat: Cat, other_cat, war, enemy_clan, alive_kits):
        """ 
        This function handles the new cats
        """
        if war:
            other_clan = enemy_clan
        else:
            other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{other_clan.name}Clan'

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{other_clan.name}Clan'

        
        #Determine
        if self.has_outside_cat():
            if random.randint(1, 3) == 1:
                outside_cat = self.select_outside_cat()
                backstory = outside_cat.status
                outside_cat = self.update_cat_properties(outside_cat)
                event_text = f"A {backstory} named {outside_cat.name} waits on the border, asking to join the Clan."
                name_change = random.choice([1, 2])
                if name_change == 1 or backstory == 'former Clancat':
                    event_text = event_text + f" They decide to keep their name."
                elif name_change == 2 and backstory != 'former Clancat':
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
                    the_cat.create_one_relationship(outside_cat)
                    outside_cat.create_one_relationship(the_cat)

                # takes cat out of the outside cat list
                game.clan.add_to_clan(outside_cat)

                return [outside_cat]

        
        # ---------------------------------------------------------------------------- #
        #                                cat creation                                  #
        # ---------------------------------------------------------------------------- #
        possible_events = self.generate_events.possible_short_events(cat.status, cat.age, "new_cat")
        final_events = self.generate_events.filter_possible_short_events(possible_events, cat, other_cat, war,
                                                                        enemy_clan,
                                                                        other_clan, alive_kits)
        if not final_events:
            print('ERROR: no new cat moon events available')
            return
        else:
            new_cat_event = (random.choice(final_events))

        involved_cats = []
        created_cats = []
        if "m_c" in new_cat_event.tags:
            involved_cats = [cat.ID]

        if "other_cat" in new_cat_event.tags:
            involved_cats = [other_cat.ID]
        else:
            other_cat = None

        status = None
        if "new_warrior" in new_cat_event.tags:
            status = "warrior"
        elif "new_app" in new_cat_event.tags:
            status = "apprentice"
        elif "new_med_app" in new_cat_event.tags:
            status = "medicine cat apprentice"
        elif "new_med" in new_cat_event.tags:
            status = "medicine cat"


        
        created_cats = create_new_cat(Cat,
                                      Relationship,
                                      new_cat_event.new_name,
                                      new_cat_event.loner,
                                      new_cat_event.kittypet,
                                      new_cat_event.kit,
                                      new_cat_event.litter,
                                      new_cat_event.other_clan,
                                      new_cat_event.backstory,
                                      status
                                      )
        
        blood_parent = None
        if new_cat_event.litter:
            # If we have a litter joining, assign them a blood parent for
            # relation-tracking purposes
            thought = "Is happy their kits are safe"
            blood_parent = create_new_cat(Cat, Relationship,
                                          status=random.choice(["loner", "kittypet"]),
                                          alive=False,
                                          thought=thought,
                                          age=random.randint(15,120))[0]
            blood_parent.outside = True
            game.clan.add_to_unknown(blood_parent)
            
            
        for new_cat in created_cats:
            
            involved_cats.append(new_cat.ID)
            
            # Set the blood parent, if one was created.
            # Also set adoptive parents if needed. 
            new_cat.parent1 = blood_parent.ID if blood_parent else None
            if "adoption" in new_cat_event.tags and cat.ID not in new_cat.adoptive_parents:
                new_cat.adoptive_parents.append(cat.ID)
                if len(cat.mate) > 0:
                    for mate_id in cat.mate:
                        if mate_id not in new_cat.adoptive_parents:
                            new_cat.adoptive_parents.extend(cat.mate)
            
            # All parents have been added now, we now create the inheritance. 
            new_cat.create_inheritance_new_cat()

            if "m_c" in new_cat_event.tags:
                # print('moon event new cat rel gain')
                cat.create_one_relationship(new_cat)
                new_cat.create_one_relationship(cat)
                
                new_to_clan_cat = game.config["new_cat"]["rel_buff"]["new_to_clan_cat"]
                clan_cat_to_new = game.config["new_cat"]["rel_buff"]["clan_cat_to_new"]
                change_relationship_values(
                    cats_to=[cat.ID],
                    cats_from=[new_cat],
                    romantic_love=new_to_clan_cat["romantic"],
                    platonic_like=new_to_clan_cat["platonic"],
                    dislike=new_to_clan_cat["dislike"],
                    admiration=new_to_clan_cat["admiration"],
                    comfortable=new_to_clan_cat["comfortable"],
                    jealousy=new_to_clan_cat["jealousy"],
                    trust=new_to_clan_cat["trust"]
                )
                change_relationship_values(
                    cats_to=[new_cat.ID],
                    cats_from=[cat],
                    romantic_love=clan_cat_to_new["romantic"],
                    platonic_like=clan_cat_to_new["platonic"],
                    dislike=clan_cat_to_new["dislike"],
                    admiration=clan_cat_to_new["admiration"],
                    comfortable=clan_cat_to_new["comfortable"],
                    jealousy=clan_cat_to_new["jealousy"],
                    trust=clan_cat_to_new["trust"]
                )

        if "adoption" in new_cat_event.tags:
            if new_cat_event.litter:
                for new_cat in created_cats:
                    # giving relationships for siblings
                    siblings = new_cat.get_siblings()
                    for sibling in siblings:
                        sibling = Cat.fetch_cat(sibling)
                        
                        sibling.create_one_relationship(new_cat)
                        new_cat.create_one_relationship(sibling)
                        
                        cat1_to_cat2 = game.config["new_cat"]["sib_buff"]["cat1_to_cat2"]
                        cat2_to_cat1 = game.config["new_cat"]["sib_buff"]["cat2_to_cat1"]
                        change_relationship_values(
                            cats_to=[sibling.ID],
                            cats_from=[new_cat],
                            romantic_love=cat1_to_cat2["romantic"],
                            platonic_like=cat1_to_cat2["platonic"],
                            dislike=cat1_to_cat2["dislike"],
                            admiration=cat1_to_cat2["admiration"],
                            comfortable=cat1_to_cat2["comfortable"],
                            jealousy=cat1_to_cat2["jealousy"],
                            trust=cat1_to_cat2["trust"]
                        )
                        change_relationship_values(
                            cats_to=[new_cat.ID],
                            cats_from=[sibling],
                            romantic_love=cat2_to_cat1["romantic"],
                            platonic_like=cat2_to_cat1["platonic"],
                            dislike=cat2_to_cat1["dislike"],
                            admiration=cat2_to_cat1["admiration"],
                            comfortable=cat2_to_cat1["comfortable"],
                            jealousy=cat2_to_cat1["jealousy"],
                            trust=cat2_to_cat1["trust"]
                        )

        # give injuries to other cat if tagged as such
        if "injured" in new_cat_event.tags and game.clan.game_mode != "classic":
            major_injuries = []
            if "major_injury" in new_cat_event.tags:
                for injury in INJURIES:
                    if INJURIES[injury]["severity"] == "major" and injury not in ["pregnant", "recovering from birth"]:
                        major_injuries.append(injury)
            for new_cat in created_cats:
                for tag in new_cat_event.tags:
                    if tag in INJURIES:
                        new_cat.get_injured(tag)
                    elif tag == "major_injury":
                        injury = random.choice(major_injuries)
                        new_cat.get_injured(injury)

        if "rel_down" in new_cat_event.tags:
            difference = -1
            change_clan_relations(other_clan, difference=difference)

        elif "rel_up" in new_cat_event.tags:
            difference = 1
            change_clan_relations(other_clan, difference=difference)

        event_text = event_text_adjust(Cat, new_cat_event.event_text, cat, other_cat, other_clan_name,
                                       new_cat=created_cats[0])

        types = ["misc"]
        if "other_clan" in new_cat_event.tags:
            types.append("other_clans")
        game.cur_events_list.append(Single_Event(event_text, types, involved_cats))

        return created_cats

    def has_outside_cat(self):
        outside_cats = [i for i in Cat.all_cats.values() if i.status in ["kittypet", "loner", "rogue", "former Clancat"] and not i.dead and i.outside]
        return any(outside_cats)

    def select_outside_cat(self):
        outside_cats = [i for i in Cat.all_cats.values() if i.status in ["kittypet", "loner", "rogue", "former Clancat"] and not i.dead and i.outside]
        for cat in outside_cats:  # iterating over the generated list
            if cat.status in ["kittypet", "loner", "rogue", "former Clancat"] and not cat.dead:
                return cat

    def update_cat_properties(self, cat):
        if cat.backstory in BACKSTORIES["backstory_categories"]['healer_backstories']:
                cat.status = 'medicine cat'
        else:
            cat.status = "warrior"
        cat.outside = False
        return cat
