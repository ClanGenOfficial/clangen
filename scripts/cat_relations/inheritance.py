# pylint: disable=line-too-long
"""

This file is the file which contains information about the inheritance of a cat.
Each cat has one instance of the inheritance class.
The inheritance class has a dictionary for all instances of the inheritance class, to easily manipulate and update the inheritance.
This class will be used to check for relations while mating and for the display of the family tree screen.

"""  # pylint: enable=line-too-long
from enum import StrEnum, auto  # pylint: disable=no-name-in-module

class RelationType(StrEnum):
    """An enum representing the possible age groups of a cat"""

    BLOOD = auto()              # direct blood related
    ADOPTIVE = auto()           # not blood related but close (parents, kits)
    HALF_BLOOD = 'half blood'   # only one blood parent is the same
    NOT_BLOOD = 'not blood'     # not blood related for parent siblings

class Inheritance():
    
    def __init__(self, cat, new=True):
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

        # SAVE INHERITANCE INTO ALL_INHERITANCES DICTIONARY 
        self.all_inheritances[self.ID] = self

        if new:
            self.init_inheritance(cat)

    def init_inheritance(self):
        """Update inheritance of the given cat."""
        how_it_looks = {
            "cat.ID":{
                "parents": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "adoptive",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    }
                },
                "kits": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "adoptive",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    }
                },
                "siblings": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "adoptive",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "half_blood",
                        "name": "cat.name"
                    }
                },
                "parent_siblings": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "not_blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "half_blood",
                        "name": "cat.name"
                    }
                },
                "cousins": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "not_blood",
                        "name": "cat.name"
                    }
                },
                "grand_parents": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "not_blood",
                        "name": "cat.name"
                    }
                },
                "grand_kits": {
                    "all": ["cat.ID"],
                    "cat.ID": {
                        "type": "blood",
                        "name": "cat.name"
                    },
                    "cat.ID": {
                        "type": "adoptive",
                        "name": "cat.name"
                    }
                },
                "not_cousins": [],
                "all_involved": ["parent.ID", "parent.ID", "and so on"]
            }
        }

        # parents
        current_parent_ids = self.get_blood_parents()
        self.init_parents()

        # grandparents
        self.init_grandparents()

        for inter_id, inter_cat in self.cat.all_cats.items():
            # kits
            self.init_kits(inter_id, inter_cat)

            # siblings
            self.init_siblings(inter_id, inter_cat)

            # parent_siblings
            self.init_parent_siblings(inter_id, inter_cat)

            # cousins

            # grand_kits

    def init_parents(self):
        """Initial the class, with the focus of the parent relation."""
        current_parent_ids = self.get_blood_parents()
        for relevant_id in current_parent_ids:
            # by blood
            relevant_cat =self.cat.fetch_cat(relevant_id)
            self.parents[relevant_id] = {
                "type": RelationType.BLOOD,
                "name": str(relevant_cat.name),
                "additional": []
            }
            self.parents["all"].append(relevant_id)
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

            # adoptive parents (mates of blood parents)
            for mate_id in relevant_cat.mate:
                mate_cat = self.cat.fetch_cat(mate_id)
                if mate_id not in self.parents:
                    self.parents[mate_id] = {
                        "type": RelationType.ADOPTIVE,
                        "name": str(mate_cat.name),
                        "additional": [f"mate from {str(relevant_cat.name)}"]
                    }
                else:
                    self.parents[mate_id]["additional"].append(f"mate from {str(relevant_cat.name)}")
                self.parents["all"].append(relevant_id)
                self.all_but_cousins.append(mate_id)
                self.all_involved.append(mate_id)

    def init_grandparents(self):
        """Initial the class, with the focus of the grand parent relation."""
        for parent_id, value in self.parents.items():
            if parent_id == "all":
                continue
            parent_cat = self.cat.all_cat.fetch(parent_id)
            grandparents = self.get_parents(parent_cat)
            for grand_id in grandparents:
                grand_cat = self.cat.all_cat.fetch(grand_id)
                grand_type = RelationType.BLOOD if value["type"] == RelationType.BLOOD else RelationType.NOT_BLOOD
                if grand_id not in self.grand_parents:
                    self.grand_parents[grand_id] = {
                        "type": grand_type,
                        "name": str(grand_cat.name),
                        "additional": []
                    }
                    self.grand_parents["all"].append(grand_id)
                    self.all_involved.append(grand_id)
                    self.all_but_cousins.append(grand_id)
                self.grand_parents[grand_id].append(f"parent of {str(parent_cat.name)}")

    def init_kits(self, inter_id, inter_cat):
        """Initial the class, with the focus of the kits relation."""
        # kits - blood
        self.kits["all"] = []
        inter_blood_parents = inter_cat.get_parents()
        if self.cat.ID in inter_blood_parents:
            self.kits[inter_id] = {
                "type": RelationType.BLOOD,
                "name": str(inter_cat.name),
                "additional": []
            }
            self.kits["all"].append(inter_id)
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
                "name": str(inter_cat.name),
                "additional": []
            }
            self.kits["all"].append(inter_id)
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
        self.siblings["all"] = []
        blood_parent_overlap = set(current_parent_ids) & set(inter_parent_ids)
        if len(blood_parent_overlap) == 2:
            self.siblings[inter_id] = {
                "type": RelationType.BLOOD,
                "name": str(inter_cat.name),
                "additional": []
            }
            self.siblings["all"].append(inter_id)
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)
            if inter_cat.moons == self.cat.moons:
                self.siblings[inter_id]["additional"].append("litter mates")
        if len(blood_parent_overlap) == 1:
            self.siblings[inter_id] = {
                "type": RelationType.HALF_BLOOD,
                "name": str(inter_cat.name),
                "additional": []
            }
            self.siblings["all"].append(inter_id)
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)

        # siblings - adoptive
        adoptive_overlap1 = set(current_parent_ids) & set(inter_cat.adoptive_parents)
        adoptive_overlap2 = set(self.cat.adoptive_parents) & set(inter_parent_ids)
        adoptive_overlap3 = set(self.cat.adoptive_parents) & set(inter_cat.adoptive_parents)
        if len(adoptive_overlap1) > 0 or len(adoptive_overlap2) > 0 or len(adoptive_overlap3) > 0:
            self.siblings[inter_id] = {
                "type": RelationType.ADOPTIVE,
                "name": str(inter_cat.name),
                "additional": []
            }
            self.siblings["all"].append(inter_id)
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)

    def init_parent_siblings(self, inter_id, inter_cat):
        """Initial the class, with the focus of the kits relation."""
        inter_parent_ids = self.get_blood_parents(inter_cat)
        for inter_parent_id in inter_parent_ids:
            inter_parent_cat = self.cat.fetch_cat(inter_parent_id)
            inter_grandparents = self.get_parents(inter_parent_cat)

            # check if the parent of the inter cat is the grand parent of the relevant cat
            for inter_grand_id in inter_grandparents:
                if inter_grand_id in self.grand_parents["all"]:
                    # the inter cat is an uncle/aunt of the current cat
                    # only create a new entry if there is no entry for this cat - should no be but safety check
                    if inter_id not in self.parent_siblings:
                        # get the relation type of the grandparent to assume how they are related
                        rel_type = RelationType.BLOOD

                        # create new entity
                        self.parent_siblings[inter_id] = {
                            "type": rel_type,
                            "name": str(inter_cat.name),
                            "additional": []
                        }
                        self.parent_siblings["all"].append(inter_id)
                        self.all_involved.append(inter_id)
                        self.all_but_cousins.append(inter_id)
                    else:
                        print("id already in dict, additional info?")

    # ---------------------------------------------------------------------------- #
    #                             all getter functions                             #
    # ---------------------------------------------------------------------------- #

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
        if cat:
            blood_parents = self.get_blood_parents(cat)
            no_blood_parents = self.get_no_blood_parents(cat)
            return blood_parents + no_blood_parents
        return self.parents["all"]

    # ---------------------------------------------------------------------------- #
    #                                     kits                                     #
    # ---------------------------------------------------------------------------- #

    def get_blood_kits(self) -> list:
        """Returns a list of blood related kits id's."""
        return [key for key, value in self.kits.items() if key != "all" and value["type"] in [RelationType.BLOOD, RelationType.HALF_BLOOD]]

    def get_not_blood_kits(self) -> list:
        """Returns a list of id's of kits, which are not related by blood to the cat."""
        return [key for key, value in self.kits.items() if key != "all" and value["type"] in [RelationType.ADOPTIVE, RelationType.NOT_BLOOD]]

    def get_kits(self) -> list:
        """Returns a list of id's which are kits to the cat, according to the inheritance hierarchy."""
        return self.kits["all"]

    # ---------------------------------------------------------------------------- #
    #                                   siblings                                   #
    # ---------------------------------------------------------------------------- #

    def get_blood_siblings(self) -> list:
        """Returns a list of id's of blood related siblings."""
        return [key for key, value in self.siblings.items() if key != "all" and value["type"] in [RelationType.BLOOD, RelationType.HALF_BLOOD]]

    def get_no_blood_siblings(self) -> list:
        """Returns a list of id's of siblings, which are not directly related to the cat."""
        return [key for key, value in self.siblings.items() if key != "all" and value["type"] in [RelationType.ADOPTIVE, RelationType.NOT_BLOOD]]

    def get_siblings(self) -> list:
        """Returns a list of id's which are siblings to the cat, according to the inheritance hierarchy."""
        return self.siblings["all"]

