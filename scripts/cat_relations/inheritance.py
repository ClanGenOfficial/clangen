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

        # SAVE INHERITANCE INTO ALL_INHERITANCES DICTIONARY 
        self.all_inheritances[self.ID] = self

        if new:
            self.init_inheritance(cat)


    def init_inheritance(self, current_cat):
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
        current_parent_ids = current_cat.get_parents()
        for relevant_id in current_parent_ids:
            # by blood
            relevant_cat =current_cat.fetch_cat(relevant_id)
            self.parents["all"].append(relevant_id)
            self.parents[relevant_id] = {
                "type": RelationType.BLOOD,
                "name": str(relevant_cat.name),
                "additional": []
            }
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

            # adoptive parents (mates of blood parents)
            for mate_id in relevant_cat.mate:
                mate_cat = current_cat.fetch_cat(mate_id)
                if mate_id not in self.parents:
                    self.parents[mate_id] = {
                        "type": RelationType.ADOPTIVE,
                        "name": str(mate_cat.name),
                        "additional": [f"mate from {str(relevant_cat.name)}"]
                    }
                else:
                    self.parents[mate_id]["additional"].append(f"mate from {str(relevant_cat.name)}")
                self.all_but_cousins.append(mate_id)
                self.all_involved.append(mate_id)

        for inter_id, inter_cat in current_cat.all_cats.items():
            # kits - blood
            self.kits["all"] = []
            inter_blood_parents = inter_cat.get_parents()
            if current_cat.ID in inter_blood_parents:
                self.kits[inter_id] = {
                    "type": RelationType.BLOOD,
                    "name": str(inter_cat.name),
                    "additional": []
                }
                self.kits["all"].append(inter_id)
                self.all_involved.append(inter_id)
                self.all_but_cousins.append(inter_id)
                if len(inter_blood_parents) > 1:
                    inter_blood_parents.remove(current_cat.ID)
                    other_id = inter_blood_parents.pop()
                    other_cat = current_cat.fetch_cat(other_id)
                    self.kits[inter_id]["additional"].append(f"second parent: {str(other_cat.name)}")

            # kit - adoptive 
            if current_cat.ID in inter_cat.adoptive_parents:
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
                        blood_parent_cat = current_cat.fetch_cat(blood_parent_id)
                        if blood_parent_cat is None:
                            print(f"ERROR: the blood_parent of {str(inter_cat.name)}")
                        else:
                            name.append(blood_parent_cat.name)
                    if len(name) > 0 and len(name) < 2:
                        self.kits[inter_id]["additional"].append(f"blood parent: {name[0]}")
                    elif len(name) > 0 and len(name) < 3:
                        self.kits[inter_id]["additional"].append(f"blood parent: {name[0]}, {name[1]}")

            # siblings - blood / half-blood
            self.siblings["all"] = []
            inter_parent_ids = current_cat.get_parents()
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
            adoptive_overlap2 = set(current_cat.adoptive_parents) & set(inter_parent_ids)
            adoptive_overlap3 = set(current_cat.adoptive_parents) & set(inter_cat.adoptive_parents)
            if len(adoptive_overlap1) > 0 or len(adoptive_overlap2) > 0 or len(adoptive_overlap3) > 0:
                self.siblings[inter_id] = {
                    "type": RelationType.ADOPTIVE,
                    "name": str(inter_cat.name),
                    "additional": []
                }
                self.siblings["all"].append(inter_id)
                self.all_involved.append(inter_id)
                self.all_but_cousins.append(inter_id)


            # parent_siblings

            # cousins

            # grand_parents

            # grand_kits
