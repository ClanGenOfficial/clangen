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


    def init_inheritance(self, cat):
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
        parent_ids = cat.get_parents()
        for relevant_id in parent_ids:
            # by blood
            self.parents["all"].append(relevant_id)
            self.parents[relevant_id] = {
                "type": RelationType.BLOOD,
                "name": str(relevant_cat.name)
            }
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

            # adoptive parents (mates of blood parents)
            for mate_id in relevant_cat.mate:
                relevant_cat = cat.fetch_cat(mate_id)
                self.parents[relevant_id] = {
                    "type": RelationType.ADOPTIVE,
                    "name": str(relevant_cat.name)
                }
                self.all_but_cousins.append(mate_id)
                self.all_involved.append(mate_id)

        for inter_id, inter_cat in cat.all_cats.items():
            # kits - blood
            inter_blood_parents = inter_cat.get_parents()
            if cat.ID in inter_blood_parents:
                self.kits[inter_id] = {
                    "type": RelationType.BLOOD,
                    "name": str(inter_cat.name)
                }

            # kit - adoptive 
            if cat.ID in inter_cat.adoptive_parents:
                self.kits[inter_id] = {
                    "type": RelationType.ADOPTIVE,
                    "name": str(inter_cat.name)
                }

            # siblings

            # parent_siblings

            # cousins

            # grand_parents

            # grand_kits
