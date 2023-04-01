# pylint: disable=line-too-long
"""

This file is the file which contains information about the inheritance of a cat.
Each cat has one instance of the inheritance class.
The inheritance class has a dictionary for all instances of the inheritance class, to easily manipulate and update the inheritance.
This class will be used to check for relations while mating and for the display of the family tree screen.

"""  # pylint: enable=line-too-long
from enum import StrEnum, auto  # pylint: disable=no-name-in-module
from typing import Dict

class RelationType(StrEnum):
    """An enum representing the possible age groups of a cat"""

    BLOOD = auto()              # direct blood related
    ADOPTIVE = auto()           # not blood related but close (parents, kits, siblings)
    HALF_BLOOD = 'half blood'   # only one blood parent is the same (siblings only)
    NOT_BLOOD = 'not blood'     # not blood related for parent siblings

BLOOD_RELATIVE_TYPES = [RelationType.BLOOD, RelationType.HALF_BLOOD]

class Inheritance():
    all_inheritances = {}  # ID: object

    def __init__(self, cat, born=False):
        self.parents = {}
        self.kits = {}
        self.siblings = {}
        self.parent_siblings = {}
        self.cousins = {}
        self.grand_parents = {}
        self.grand_kits = {}
        self.all_involved = []
        self.all_but_cousins = []

        self.cat = cat
        self.update_inheritance()

        # if the cat is newly born, update all the related cats
        if born:
            self.update_all_related_inheritance()

        # SAVE INHERITANCE INTO ALL_INHERITANCES DICTIONARY
        self.all_inheritances[cat.ID] = self

    def update_inheritance(self):
        """Update inheritance of the given cat."""
        self.parents = {}
        self.kits = {}
        self.siblings = {}
        self.parent_siblings = {}
        self.cousins = {}
        self.grand_parents = {}
        self.grand_kits = {}
        self.all_involved = []
        self.all_but_cousins = []

        # parents
        self.init_parents()

        # grandparents
        self.init_grand_parents()

        for inter_id, inter_cat in self.cat.all_cats.items():
            # kits
            self.init_kits(inter_id, inter_cat)

            # siblings
            self.init_siblings(inter_id, inter_cat)

            # parent_siblings
            self.init_parent_siblings(inter_id, inter_cat)

            # cousins
            self.init_cousins(inter_id, inter_cat)

            # grand_kits
            self.init_cousins(inter_id, inter_cat)

    def update_all_related_inheritance(self):
        """Update all the inheritances of the cats, which are related to the current cat."""
        # only adding/removing parents or kits will use this function, because all inheritances are based on parents
        for cat_id in self.all_involved:
            self.all_inheritances[cat_id].update_inheritance()

    def remove_parent(self, cat):
        """Remove the cat the parent dictionary - used to 'update' the adoptive parents."""
        if cat.ID in self.parents:
            del self.parents[cat.ID]
            self.update_all_related_inheritance()

    def add_parent(self, parent, rel_type = RelationType.ADOPTIVE):
        """Adding a parent entry with the given rel_type - used to add adoptive parents, if the parent gets a new mate."""
        # the default is adoptive, because the there should only be 2 blood parents per default
        self.parents[parent.ID] = {
            "type": rel_type,
            "additional": []
        }
        if rel_type == RelationType.ADOPTIVE and parent.ID not in self.cat.adoptive_parents:
            self.cat.adoptive_parents.append(parent.ID)
        self.all_involved.append(parent.ID)
        self.all_but_cousins.append(parent.ID)
        self.update_all_related_inheritance()

    # ---------------------------------------------------------------------------- #
    #                            different init function                           #
    # ---------------------------------------------------------------------------- #

    def init_parents(self):
        """Initial the class, with the focus of the parent relation."""
        new_adoptive_parents = []
        # by blood
        current_parent_ids = self.get_blood_parents()
        for relevant_id in current_parent_ids:
            relevant_cat = self.cat.fetch_cat(relevant_id)
            self.parents[relevant_id] = {
                "type": RelationType.BLOOD,
                "additional": []
            }
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

            # adoptive parents (mates of blood parents)
            for mate_id in relevant_cat.mate:
                # add it also to the list of adoptive parents of the cat itself
                if mate_id not in self.cat.adoptive_parents:
                    new_adoptive_parents.append(mate_id)
                mate_cat = self.cat.fetch_cat(mate_id)
                if mate_id not in self.parents:
                    self.parents[mate_id] = {
                        "type": RelationType.ADOPTIVE,
                        "additional": [f"mate from {str(relevant_cat.name)}"]
                    }
                else:
                    self.parents[mate_id]["additional"].append(f"mate from {str(relevant_cat.name)}")
                self.all_but_cousins.append(mate_id)
                self.all_involved.append(mate_id)

        # adoptive
        current_parent_ids = self.get_no_blood_parents()
        for relevant_id in current_parent_ids:
            # if the cat is already a parent, continue
            if relevant_id in self.parents.keys():
                continue
            relevant_cat =self.cat.fetch_cat(relevant_id)
            self.parents[relevant_id] = {
                "type": RelationType.ADOPTIVE,
                "additional": []
            }
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

        # update the adoptive parents of the current cat
        for new_adoptive_parent_id in new_adoptive_parents:
            if new_adoptive_parent_id not in self.cat.adoptive_parents:
                self.cat.adoptive_parents.append(new_adoptive_parent_id)

    def init_grand_parents(self):
        """Initial the class, with the focus of the grand parent relation."""
        for parent_id, value in self.parents.items():
            if parent_id == "all":
                continue
            parent_cat = self.cat.all_cat.fetch(parent_id)
            grandparents = self.get_parents(parent_cat)
            for grand_id in grandparents:
                grand_type = RelationType.BLOOD if value["type"] == RelationType.BLOOD else RelationType.NOT_BLOOD
                if grand_id not in self.grand_parents:
                    self.grand_parents[grand_id] = {
                        "type": grand_type,
                        "additional": []
                    }
                    self.all_involved.append(grand_id)
                    self.all_but_cousins.append(grand_id)
                self.grand_parents[grand_id].append(f"parent of {str(parent_cat.name)}")

    def init_kits(self, inter_id, inter_cat):
        """Initial the class, with the focus of the kits relation."""
        # kits - blood
        inter_blood_parents = inter_cat.get_blood_parents()
        if self.cat.ID in inter_blood_parents:
            self.kits[inter_id] = {
                "type": RelationType.BLOOD,
                "additional": []
            }
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)
            if len(inter_blood_parents) > 1:
                inter_blood_parents.remove(self.cat.ID)
                other_id = inter_blood_parents.pop()
                other_cat = self.cat.fetch_cat(other_id)
                self.kits[inter_id]["additional"].append(f"second parent: {str(other_cat.name)}")

        # kit - adoptive
        if self.cat.ID in inter_cat.adoptive_parents:
            self.kits[inter_id] = {
                "type": RelationType.ADOPTIVE,
                "additional": []
            }
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)
            if len(inter_blood_parents) > 0:
                name = []
                for blood_parent_id in inter_blood_parents:
                    blood_parent_cat = self.cat.fetch_cat(blood_parent_id)
                    if blood_parent_cat is None:
                        print(f"ERROR: the blood_parent of {str(inter_cat.name)}")
                    else:
                        name.append(blood_parent_cat.name)
                if len(name) > 0 and len(name) < 2:
                    self.kits[inter_id]["additional"].append(f"blood parent: {name[0]}")
                elif len(name) > 0 and len(name) < 3:
                    self.kits[inter_id]["additional"].append(f"blood parent: {name[0]}, {name[1]}")

    def init_siblings(self, inter_id, inter_cat):
        """Initial the class, with the focus of the siblings relation."""
        # siblings - blood / half-blood
        current_parent_ids = self.get_blood_parents()
        inter_parent_ids = self.get_blood_parents(inter_cat)
        blood_parent_overlap = set(current_parent_ids) & set(inter_parent_ids)
        if len(blood_parent_overlap) == 2:
            self.siblings[inter_id] = {
                "type": RelationType.BLOOD,
                "additional": []
            }
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)
            if inter_cat.moons == self.cat.moons:
                self.siblings[inter_id]["additional"].append("litter mates")
        if len(blood_parent_overlap) == 1:
            self.siblings[inter_id] = {
                "type": RelationType.HALF_BLOOD,
                "additional": []
            }
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)

        # siblings - adoptive
        adoptive_overlap1 = set(current_parent_ids) & set(inter_cat.adoptive_parents)
        adoptive_overlap2 = set(self.cat.adoptive_parents) & set(inter_parent_ids)
        adoptive_overlap3 = set(self.cat.adoptive_parents) & set(inter_cat.adoptive_parents)
        if len(adoptive_overlap1) > 0 or len(adoptive_overlap2) > 0 or len(adoptive_overlap3) > 0:
            self.siblings[inter_id] = {
                "type": RelationType.ADOPTIVE,
                "additional": []
            }
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)

    def init_parent_siblings(self, inter_id, inter_cat):
        """Initial the class, with the focus of the parents siblings relation."""
        inter_parent_ids = self.get_parents(inter_cat)
        for inter_parent_id in inter_parent_ids:
            inter_parent_cat = self.cat.fetch_cat(inter_parent_id)
            inter_grandparents = self.get_parents(inter_parent_cat)

            # check if the parent of the inter cat is the grand parent of the relevant cat
            for inter_grand_id in inter_grandparents:
                if inter_grand_id in self.grand_parents.keys():
                    # the inter cat is an uncle/aunt of the current cat
                    # only create a new entry if there is no entry for this cat - should no be but safety check
                    if inter_id not in self.parent_siblings:
                        # get the relation type of the grandparent to assume how they are related
                        rel_type = RelationType.BLOOD

                        # create new entity
                        self.parent_siblings[inter_id] = {
                            "type": rel_type,
                            "additional": []
                        }
                        self.all_involved.append(inter_id)
                        self.all_but_cousins.append(inter_id)
                    else:
                        print("id already in dict, additional info?")

    def init_cousins(self, inter_id, inter_cat):
        """Initial the class, with the focus of the cousin relation."""
        # the parent siblings already set
        # so it is only needed to check if the inter cat has a parent which is also in the parent_siblings dict
        inter_parent_ids = self.get_parents(inter_cat)

        for inter_parent_id in inter_parent_ids:
            if inter_parent_id in self.parent_siblings.keys():
                rel_type = RelationType.BLOOD if self.parent_siblings[inter_parent_id]["type"] == RelationType.BLOOD else RelationType.NOT_BLOOD
                self.cousins[inter_id] = {
                    "type": rel_type,
                    "additional": []
                }
                self.all_involved.append(inter_id)

    def init_grand_kits(self, inter_id, inter_cat):
        """Initial the class, with the focus of the grand kits relation."""
        # the kits of this cat are already set
        # so it we only need to check if the inter cat has a parent which is in the kits dict
        inter_parent_ids = self.get_parents(inter_cat)

        for inter_parent_id in inter_parent_ids:
            if inter_parent_id in self.kits.keys():
                rel_type = RelationType.BLOOD if self.kits[inter_parent_id]["type"] == RelationType.BLOOD else RelationType.NOT_BLOOD
                self.cousins[inter_id] = {
                    "type": rel_type,
                    "additional": []
                }
                self.all_but_cousins.append(inter_cat)
                self.all_involved.append(inter_id)

    # ---------------------------------------------------------------------------- #
    #                             all getter functions                             #
    # ---------------------------------------------------------------------------- #

    def get_blood_relatives(self, dict):
        """Returns the keys (ids) of the dictionary entries with a blood relation."""
        return [key for key, value in dict.items() if key != "all" and value["type"] in BLOOD_RELATIVE_TYPES]

    def get_no_blood_relatives(self, dict):
        """Returns the keys (ids) of the dictionary entries without a blood relation."""
        return [key for key, value in dict.items() if key != "all" and value["type"] not in BLOOD_RELATIVE_TYPES]

    # ---------------------------------------------------------------------------- #
    #                                    parents                                   #
    # ---------------------------------------------------------------------------- #

    def get_blood_parents(self, cat = None) -> list:
        """Returns a list of id's which are the blood parents of the current cat."""
        relevant_cat = self.cat
        if cat:
            relevant_cat = cat
        if relevant_cat.parent1:
            if relevant_cat.parent2:
                return [relevant_cat.parent1, relevant_cat.parent2]
            return [relevant_cat.parent1]
        return []

    def get_no_blood_parents(self, cat = None) -> list:
        """Returns a list of id's which are adoptive parents of the current cat."""
        relevant_cat = cat if cat else self.cat
        return relevant_cat.adoptive_parents

    def get_parents(self, cat = None) -> list:
        """Returns a list of id's which are parents to the cat, according to the inheritance hierarchy."""
        relevant_cat = self.cat
        if cat:
            relevant_cat = cat
        blood_parents = self.get_blood_parents(relevant_cat)
        no_blood_parents = self.get_no_blood_parents(relevant_cat)
        return blood_parents + no_blood_parents

    # ---------------------------------------------------------------------------- #
    #                                     kits                                     #
    # ---------------------------------------------------------------------------- #

    def get_blood_kits(self) -> list:
        """Returns a list of blood related kits id's."""
        return self.get_blood_relatives(self.kits)

    def get_not_blood_kits(self) -> list:
        """Returns a list of id's of kits, which are not related by blood to the cat."""
        return self.get_no_blood_relatives(self.kits)

    def get_kits(self) -> list:
        """Returns a list of id's which are kits to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.kits) + self.get_no_blood_relatives(self.kits)

    # ---------------------------------------------------------------------------- #
    #                                   siblings                                   #
    # ---------------------------------------------------------------------------- #

    def get_blood_siblings(self) -> list:
        """Returns a list of id's of blood related siblings."""
        return self.get_blood_relatives(self.siblings)

    def get_no_blood_siblings(self) -> list:
        """Returns a list of id's of siblings, which are not directly related to the cat."""
        return self.get_no_blood_relatives(self.siblings)

    def get_siblings(self) -> list:
        """Returns a list of id's which are siblings to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.siblings) + self.get_no_blood_relatives(self.siblings)

    # ---------------------------------------------------------------------------- #
    #                                parent_siblings                               #
    # ---------------------------------------------------------------------------- #

    def get_blood_parent_siblings(self) -> list:
        """Returns a list of blood related parent_siblings id's."""
        return self.get_blood_relatives(self.parent_siblings)

    def get_not_blood_parent_siblings(self) -> list:
        """Returns a list of id's of parent_siblings, which are not related by blood to the cat."""
        return self.get_no_blood_relatives(self.parent_siblings)

    def get_parent_siblings(self) -> list:
        """Returns a list of id's which are parent_siblings to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.parent_siblings) + self.get_no_blood_relatives(self.parent_siblings)

    # ---------------------------------------------------------------------------- #
    #                                    cousins                                   #
    # ---------------------------------------------------------------------------- #

    def get_blood_cousins(self) -> list:
        """Returns a list of id's of blood related cousins."""
        return self.get_blood_relatives(self.cousins)

    def get_no_blood_cousins(self) -> list:
        """Returns a list of id's of cousins, which are not directly related to the cat."""
        return self.get_no_blood_relatives(self.cousins)

    def get_cousins(self) -> list:
        """Returns a list of id's which are cousins to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.cousins) + self.get_no_blood_relatives(self.cousins)

    # ---------------------------------------------------------------------------- #
    #                                 grand_parents                                #
    # ---------------------------------------------------------------------------- #

    def get_blood_grand_parents(self) -> list:
        """Returns a list of blood related grand_parents id's."""
        return self.get_blood_relatives(self.grand_parents)

    def get_not_blood_grand_parents(self) -> list:
        """Returns a list of id's of grand_parents, which are not related by blood to the cat."""
        return self.get_no_blood_relatives(self.grand_parents)

    def get_grand_parents(self) -> list:
        """Returns a list of id's which are grand_parents to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.grand_parents) + self.get_no_blood_relatives(self.grand_parents)

    # ---------------------------------------------------------------------------- #
    #                                  grand_kits                                  #
    # ---------------------------------------------------------------------------- #

    def get_blood_grand_kits(self) -> list:
        """Returns a list of id's of blood related grand_kits."""
        return self.get_blood_relatives(self.grand_kits)

    def get_no_blood_grand_kits(self) -> list:
        """Returns a list of id's of grand_kits, which are not directly related to the cat."""
        return self.get_no_blood_relatives(self.grand_kits)

    def get_grand_kits(self) -> list:
        """Returns a list of id's which are grand_kits to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.grand_kits) + self.get_no_blood_relatives(self.grand_kits)
