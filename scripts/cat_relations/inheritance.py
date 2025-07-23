"""

This file is the file which contains information about the inheritance of a cat.
Each cat has one instance of the inheritance class.
The inheritance class has a dictionary for all instances of the inheritance class, to
easily manipulate and update the inheritance. This class will be used to check for relations
while mating and for the display of the family tree screen.

"""

import i18n
from strenum import StrEnum  # pylint: disable=no-name-in-module

from scripts.utility import adjust_list_text


class RelationType(StrEnum):
    """An enum representing the possible relationships of a cat"""

    BLOOD = ""  # direct blood related - do not need a special print
    ADOPTIVE = "adoptive"  # not blood related but close (parents, kits, siblings)
    HALF_BLOOD = "half sibling"  # only one blood parent is the same (siblings only)
    NOT_BLOOD = "not blood related"  # not blood related for parent siblings
    RELATED = "blood related"  # related by blood (different mates only)


BLOOD_RELATIVE_TYPES = [
    RelationType.BLOOD,
    RelationType.HALF_BLOOD,
    RelationType.RELATED,
]


class Inheritance:
    all_inheritances = {}  # ID: object

    def __init__(self, cat, born=False):
        self.need_update = False
        self.mates = None
        self.other_mates = None
        self.kits = {}
        self.kits_mates = {}
        self.siblings = {}
        self.siblings_mates = {}
        self.siblings_kits = {}
        self.parents = {}
        self.parents_siblings = {}
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
        self.mates = {}
        self.kits = {}
        self.kits_mates = {}
        self.siblings = {}
        self.siblings_mates = {}
        self.siblings_kits = {}
        self.parents_siblings = {}
        self.cousins = {}
        self.grand_parents = {}
        self.grand_kits = {}
        self.all_involved = []
        self.all_but_cousins = []
        self.other_mates = []

        # helping variables
        self.need_update = []

        # parents
        self.init_parents()

        # grandparents
        self.init_grandparents()

        # mates
        self.init_mates()

        for inter_id, inter_cat in self.cat.all_cats.items():
            if inter_id == self.cat.ID:
                continue

            # kits + their mates
            self.init_kits(inter_id, inter_cat)

            # siblings + their mates
            self.init_siblings(inter_id, inter_cat)

            # parents_siblings
            self.init_parents_siblings(inter_id, inter_cat)

            # cousins
            self.init_cousins(inter_id, inter_cat)

        # since grand kits depending on kits, ALL KITS HAVE TO BE SET FIRST!
        for inter_id, inter_cat in self.cat.all_cats.items():
            if inter_id == self.cat.ID:
                continue

            # grand kits
            self.init_grand_kits(inter_id, inter_cat)

        # relations to faded cats - these must occur after all non-faded
        # cats have been handled, and in the following order.
        self.init_faded_kits()

        self.init_faded_siblings()

        self.init_faded_parents_siblings()

        self.init_faded_grandkits()

        self.init_faded_cousins()

        if len(self.need_update) > 1:
            for update_id in self.need_update:
                if update_id in self.all_inheritances:
                    self.all_inheritances[update_id].update_inheritance()
                    # if the inheritance is updated, remove the id of the need_update list
                    self.need_update.remove(update_id)

    def update_all_related_inheritance(self):
        """Update all the inheritances of the cats, which are related to the current cat."""
        # only adding/removing parents or kits will use this function, because all inheritances are based on parents
        for cat_id in self.all_involved:
            # Don't update the inheritance of faded cats
            # They are not viewable by the player and won't be used in any checks.
            if (
                cat_id in self.all_inheritances
                and self.cat.fetch_cat(cat_id)
                and not self.cat.fetch_cat(cat_id).faded
            ):
                self.all_inheritances[cat_id].update_inheritance()

    def update_all_mates(self):
        """
        This function should be called, when the cat breaks up.
        It renews all inheritances, where this cat is listed as a mate of a kit or sibling.
        """
        self.update_inheritance()
        for inter_inheritances in self.all_inheritances.values():
            if (
                self.cat.ID in inter_inheritances.other_mates
                or self.cat.ID in inter_inheritances.all_involved
            ):
                inter_inheritances.update_inheritance()

    def get_cat_info(self, cat_id) -> dict:
        """Returns a list of the additional information of the given cat id."""
        info = {
            "additional": [],
            "type": [],
        }
        if cat_id in self.parents:
            info["type"].append(self.parents[cat_id]["type"])
            info["additional"].extend(self.parents[cat_id]["additional"])
        if cat_id in self.kits:
            info["type"].append(self.kits[cat_id]["type"])
            info["additional"].extend(self.kits[cat_id]["additional"])
        if cat_id in self.siblings:
            info["type"].append(self.siblings[cat_id]["type"])
            info["additional"].extend(self.siblings[cat_id]["additional"])
        if cat_id in self.parents_siblings:
            info["type"].append(self.parents_siblings[cat_id]["type"])
            info["additional"].extend(self.parents_siblings[cat_id]["additional"])
        if cat_id in self.cousins:
            info["type"].append(self.cousins[cat_id]["type"])
            info["additional"].extend(self.cousins[cat_id]["additional"])
        if cat_id in self.grand_parents:
            info["type"].append(self.grand_parents[cat_id]["type"])
            info["additional"].extend(self.grand_parents[cat_id]["additional"])
        if cat_id in self.grand_kits:
            info["type"].append(self.grand_kits[cat_id]["type"])
            info["additional"].extend(self.grand_kits[cat_id]["additional"])
        if cat_id in self.siblings_kits:
            info["type"].append(self.siblings_kits[cat_id]["type"])
            info["additional"].extend(self.siblings_kits[cat_id]["additional"])
        if cat_id in self.siblings_mates:
            info["type"].append(self.siblings_mates[cat_id]["type"])
            info["additional"].extend(self.siblings_mates[cat_id]["additional"])
        if cat_id in self.kits_mates:
            info["type"].append(self.kits_mates[cat_id]["type"])
            info["additional"].extend(self.kits_mates[cat_id]["additional"])
        if cat_id in self.mates:
            info["type"].append(self.mates[cat_id]["type"])
            info["additional"].extend(self.mates[cat_id]["additional"])
        return info

    def remove_parent(self, cat):
        """Remove the cat the parent dictionary - used to 'update' the adoptive parents."""
        if cat.ID in self.parents:
            del self.parents[cat.ID]
            self.update_all_related_inheritance()

    def add_parent(self, parent, rel_type=RelationType.ADOPTIVE):
        """Add a parent entry with the given relation type.

        Used to add adoptive parents, if the parent gets a new mate.

        :param parent: the soon-to-be parent
        :param RelationType rel_type: the type of relation, default `RelationType.ADOPTIVE`
        """
        # the default is adoptive, because there should only be 2 blood parents per default
        self.parents[parent.ID] = {"type": rel_type, "additional": []}
        if (
            rel_type == RelationType.ADOPTIVE
            and parent.ID not in self.cat.adoptive_parents
        ):
            self.cat.adoptive_parents.append(parent.ID)
        self.all_involved.append(parent.ID)
        self.all_but_cousins.append(parent.ID)
        self.update_all_related_inheritance()

    # ---------------------------------------------------------------------------- #
    #                            different init function                           #
    # ---------------------------------------------------------------------------- #

    def init_faded_kits(self):
        for inter_id in self.cat.faded_offspring:
            inter_cat = self.cat.fetch_cat(inter_id)
            if not inter_cat:
                continue
            self.init_kits(inter_id, inter_cat)

    def init_faded_siblings(self):
        for inter_id in self.get_blood_parents() + self.cat.adoptive_parents:
            inter_cat = self.cat.fetch_cat(inter_id)
            if not inter_cat:
                continue
            for inter_sibling_id in inter_cat.faded_offspring:
                inter_sibling = self.cat.fetch_cat(inter_sibling_id)
                self.init_siblings(inter_sibling_id, inter_sibling)

    def init_faded_parents_siblings(self):
        for inter_id in self.get_blood_parents() + self.cat.adoptive_parents:
            inter_parent = self.cat.fetch_cat(inter_id)
            if not inter_parent:
                continue
            for inter_grand_id in (
                self.get_blood_parents(inter_parent) + inter_parent.adoptive_parents
            ):
                inter_grand = self.cat.fetch_cat(inter_grand_id)
                if not inter_grand:
                    continue
                for inter_parent_sibling_id in inter_grand.faded_offspring:
                    inter_parent_sibling = self.cat.fetch_cat(inter_parent_sibling_id)
                    self.init_parents_siblings(
                        inter_parent_sibling_id, inter_parent_sibling
                    )

    def init_faded_grandkits(self):
        """This must occur after all kits, faded and otherwise, have been gathered."""
        for inter_id in self.get_children():
            inter_cat = self.cat.fetch_cat(inter_id)
            if not inter_cat:
                continue
            for inter_grandkit_id in inter_cat.faded_offspring:
                inter_grandkit = self.cat.fetch_cat(inter_grandkit_id)
                self.init_grand_kits(inter_grandkit_id, inter_grandkit)

    def init_faded_cousins(self):
        """This must occur after all parent's siblings, faded and otherwise, have been gathered."""
        for inter_id in self.get_parents_siblings():
            inter_cat = self.cat.fetch_cat(inter_id)
            if not inter_cat:
                continue
            for inter_cousin_id in inter_cat.faded_offspring:
                inter_cousin = self.cat.fetch_cat(inter_cousin_id)
                self.init_cousins(inter_cousin_id, inter_cousin)

    def init_parents(self):
        """Create parent relationships"""
        # by blood
        current_parent_ids = self.get_blood_parents()
        for relevant_id in current_parent_ids:
            relevant_cat = self.cat.fetch_cat(relevant_id)
            if not relevant_cat:
                continue
            self.parents[relevant_id] = {"type": RelationType.BLOOD, "additional": []}
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

        # adoptive
        current_parent_ids = self.get_adoptive_parents()
        for relevant_id in current_parent_ids:
            # if the cat is already a parent, continue
            if relevant_id in self.parents.keys():
                continue
            self.parents[relevant_id] = {
                "type": RelationType.ADOPTIVE,
                "additional": [],
            }
            self.all_involved.append(relevant_id)
            self.all_but_cousins.append(relevant_id)

    def init_mates(self):
        """Create a mate relationship"""
        for relevant_id in self.cat.mate:
            mate_rel = RelationType.NOT_BLOOD
            # they might be related, but only if it is not an adoption
            if relevant_id in self.all_involved:
                mate_rel = self.get_exact_rel_type(relevant_id)
            self.mates[relevant_id] = {
                "type": mate_rel,
                "additional": [i18n.t("inheritance.current_mate")],
            }
            self.other_mates.append(relevant_id)

        for relevant_id in self.cat.previous_mates:
            mate_rel = RelationType.NOT_BLOOD
            # they might be related, but only if it is not an adoption
            if relevant_id in self.all_involved:
                mate_rel = self.get_exact_rel_type(relevant_id)
            self.mates[relevant_id] = {
                "type": mate_rel,
                "additional": [i18n.t("inheritance.prev_mate")],
            }
            self.other_mates.append(relevant_id)

    def init_grandparents(self):
        """Create a grandparent relationship."""
        for parent_id, value in self.parents.items():
            parent_cat = self.cat.fetch_cat(parent_id)
            if parent_cat is None:
                continue
            grandparents = self.get_parents(parent_cat)
            for grand_id in grandparents:
                if grand_id in self.parents.keys():
                    parent_relation = self.parents[grand_id]
                    if parent_relation["type"] == RelationType.BLOOD:
                        print(
                            "WARNING - How did this happen? "
                            "A grandparent is also the blood parent? Please report this!"
                        )
                    continue  # even it is not blood related, it is confusing
                grand_type = (
                    RelationType.BLOOD
                    if value["type"] == RelationType.BLOOD
                    else RelationType.NOT_BLOOD
                )
                if grand_id not in self.grand_parents:
                    self.grand_parents[grand_id] = {
                        "type": grand_type,
                        "additional": [],
                    }
                    self.all_involved.append(grand_id)
                    self.all_but_cousins.append(grand_id)
                self.grand_parents[grand_id]["additional"].append(
                    i18n.t("inheritance.parent_of_inter", name=str(parent_cat.name))
                )

    def init_kits(self, inter_id, inter_cat):
        """Create a kit relationship."""
        if not inter_cat:
            return
        # kits - blood
        inter_blood_parents = self.get_blood_parents(inter_cat)
        if self.cat.ID in inter_blood_parents:
            self.kits[inter_id] = {"type": RelationType.BLOOD, "additional": []}
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)
            if len(inter_blood_parents) > 1:
                inter_blood_parents.remove(self.cat.ID)
                other_id = inter_blood_parents.pop()
                other_cat = self.cat.fetch_cat(other_id)
                self.kits[inter_id]["additional"].append(
                    i18n.t("inheritance.second_parent", name=str(other_cat.name))
                )

        # kit - adoptive
        if self.cat.ID in inter_cat.adoptive_parents:
            self.kits[inter_id] = {"type": RelationType.ADOPTIVE, "additional": []}
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)
            if len(inter_blood_parents) > 0:
                name = []
                for blood_parent_id in inter_blood_parents:
                    blood_parent_cat = self.cat.fetch_cat(blood_parent_id)
                    if blood_parent_cat is None:
                        print(f"ERROR: the blood_parent of {str(inter_cat.name)}")
                    else:
                        name.append(str(blood_parent_cat.name))
                self.kits[inter_id]["additional"].append(
                    i18n.t(
                        "inheritance.blood_parent",
                        count=len(name),
                        name=adjust_list_text(name),
                    )
                )

        # check for mates
        if inter_id in self.kits:
            for mate_id in inter_cat.mate:
                rel_type = RelationType.NOT_BLOOD
                # they might be related, but only if it is not an adoption
                if mate_id in self.all_involved:
                    if mate_id in self.parents.keys():
                        rel_type = self.parents[mate_id]["type"]
                    else:
                        rel_type = self.get_exact_rel_type(mate_id)
                self.kits_mates[mate_id] = {
                    "type": rel_type,
                    "additional": [
                        i18n.t("inheritance.mate_of_inter", name=str(inter_cat.name))
                    ],
                }

    def init_siblings(self, inter_id, inter_cat):
        """Create a sibling relationship."""
        if not inter_cat:
            return

        # if the cat is in the parents, don't continue
        if inter_id in self.parents.keys():
            return

        # blood / half-blood
        current_parent_ids = self.get_blood_parents()
        inter_parent_ids = self.get_blood_parents(inter_cat)
        blood_parent_overlap = set(current_parent_ids) & set(inter_parent_ids)

        # adopt
        adoptive_overlap1 = set(current_parent_ids) & set(inter_cat.adoptive_parents)
        adoptive_overlap2 = set(self.cat.adoptive_parents) & set(inter_parent_ids)
        adoptive_overlap3 = set(self.cat.adoptive_parents) & set(
            inter_cat.adoptive_parents
        )

        siblings = False
        rel_type = RelationType.BLOOD
        additional_info = []
        if len(blood_parent_overlap) == 2:
            siblings = True
            if (
                inter_cat.moons + inter_cat.dead_for
                == self.cat.moons + self.cat.dead_for
            ):
                additional_info.append(i18n.t("inheritance.littermates"))
        elif (
            len(blood_parent_overlap) == 1
            and len(inter_parent_ids) == 1
            and len(current_parent_ids) == 1
        ):
            siblings = True
            if (
                inter_cat.moons + inter_cat.dead_for
                == self.cat.moons + self.cat.dead_for
            ):
                additional_info.append(i18n.t("inheritance.littermates"))
        elif len(blood_parent_overlap) == 1 and (
            len(inter_parent_ids) > 1 or len(current_parent_ids) > 1
        ):
            siblings = True
            rel_type = RelationType.HALF_BLOOD
        elif (
            len(adoptive_overlap1) > 0
            or len(adoptive_overlap2) > 0
            or len(adoptive_overlap3) > 0
        ):
            siblings = True
            rel_type = RelationType.ADOPTIVE

        if siblings:
            self.siblings[inter_id] = {"type": rel_type, "additional": additional_info}
            self.all_involved.append(inter_id)
            self.all_but_cousins.append(inter_id)

            for mate_id in inter_cat.mate:
                mate_rel = RelationType.NOT_BLOOD
                # they might be related, but only if it is not an adoption
                if mate_id in self.all_involved:
                    if mate_id in self.parents.keys():
                        mate_rel = self.parents[mate_id]["type"]
                    else:
                        mate_rel = self.get_exact_rel_type(mate_id)
                self.siblings_mates[mate_id] = {
                    "type": mate_rel,
                    "additional": [
                        i18n.t("inheritance.mate_of_inter", name=str(inter_cat.name))
                    ],
                }
                self.other_mates.append(mate_id)

            # iterate over all cats, to get the children of the sibling
            for _c in self.cat.all_cats.values():
                _c_parents = self.get_parents(_c)
                _c_adoptive = self.get_adoptive_parents(_c)
                if inter_id in _c_parents:
                    parents_cats = [self.cat.fetch_cat(c_id) for c_id in _c_parents]
                    parent_cats_names = [str(c.name) for c in parents_cats]
                    kit_rel_type = (
                        RelationType.BLOOD
                        if rel_type in BLOOD_RELATIVE_TYPES
                        else RelationType.NOT_BLOOD
                    )
                    if inter_id in _c_adoptive:
                        kit_rel_type = RelationType.ADOPTIVE

                    add_info = ""
                    if len(parent_cats_names) > 0:
                        add_info = i18n.t(
                            "inheritance.child_of_inter",
                            name=adjust_list_text(parent_cats_names),
                        )
                    self.siblings_kits[_c.ID] = {
                        "type": kit_rel_type,
                        "additional": [add_info],
                    }
                    self.all_involved.append(_c.ID)
                    self.all_but_cousins.append(_c.ID)

    def init_parents_siblings(self, inter_id, inter_cat):
        """Create an aunt/uncle (pibling) relationship."""
        if not inter_cat:
            return
        inter_parent_ids = self.get_parents(inter_cat)
        for inter_parent_id in inter_parent_ids:
            # check if the parent of the inter cat is the grandparent of the relevant cat
            if (
                inter_parent_id in self.grand_parents.keys()
                and inter_id not in self.parents.keys()
            ):
                # the inter cat is an uncle/aunt of the current cat
                # only create a new entry if there is no entry for this cat - shouldn't be but safety check
                if inter_id not in self.parents_siblings:
                    # get the relation type of the grandparent to assume how they are related
                    rel_type = RelationType.BLOOD

                    # create new entity
                    self.parents_siblings[inter_id] = {
                        "type": rel_type,
                        "additional": [],
                    }
                    self.all_involved.append(inter_id)
                    self.all_but_cousins.append(inter_id)

                grand_parent_cat = self.cat.fetch_cat(inter_parent_id)
                if len(self.parents_siblings[inter_id]["additional"]) > 0:
                    add_info = self.parents_siblings[inter_id]["additional"][0]
                    self.parents_siblings[inter_id]["additional"][0] = (
                        add_info + ", " + str(grand_parent_cat.name)
                    )
                else:
                    self.parents_siblings[inter_id]["additional"].append(
                        i18n.t(
                            "inheritance.child_of_inter",
                            name=str(grand_parent_cat.name),
                        )
                    )

    def init_cousins(self, inter_id, inter_cat):
        """Create a cousin relationship."""
        # because the parent siblings are already set
        # we only need to check if the inter cat has a parent which is also in the parents_siblings dict
        if not inter_cat:
            return
        inter_parent_ids = self.get_parents(inter_cat)
        parents_cats = [self.cat.fetch_cat(c_id) for c_id in inter_parent_ids]
        parent_cats_names = [str(c.name) for c in parents_cats]

        for inter_parent_id in inter_parent_ids:
            if inter_parent_id in self.parents_siblings.keys():
                rel_type = RelationType.BLOOD
                if (
                    self.parents_siblings[inter_parent_id]["type"]
                    not in BLOOD_RELATIVE_TYPES
                ):
                    rel_type = RelationType.NOT_BLOOD
                add_info = ""
                if len(parent_cats_names) > 0:
                    add_info = i18n.t(
                        "inheritance.child_of_inter",
                        name=adjust_list_text(parent_cats_names),
                    )

                self.cousins[inter_id] = {"type": rel_type, "additional": [add_info]}
                self.all_involved.append(inter_id)

    def init_grand_kits(self, inter_id, inter_cat):
        """Create a grandkit relationship."""
        # because the kits of this cat are already set
        # we only need to check if the inter cat has a parent which is in the kits dict
        if not inter_cat:
            return
        inter_parent_ids = self.get_parents(inter_cat)
        parents_cats = [self.cat.fetch_cat(c_id) for c_id in inter_parent_ids]
        parent_cats_names = [str(c.name) for c in parents_cats if c]

        add_info = ""
        if len(parent_cats_names) > 0:
            add_info = i18n.t(
                "inheritance.child_of_inter", name=adjust_list_text(parent_cats_names)
            )

        for inter_parent_id in inter_parent_ids:
            if inter_parent_id in self.kits.keys():
                rel_type = (
                    RelationType.BLOOD
                    if self.kits[inter_parent_id]["type"] in BLOOD_RELATIVE_TYPES
                    else RelationType.NOT_BLOOD
                )

                if inter_id not in self.grand_kits:
                    self.grand_kits[inter_id] = {
                        "type": rel_type,
                        "additional": [add_info],
                    }
                    self.all_but_cousins.append(inter_id)
                    self.all_involved.append(inter_id)

    # ---------------------------------------------------------------------------- #
    #                             all getter functions                             #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_blood_relatives(relatives_dict):
        """Returns the keys (ids) of the dictionary entries with a blood relation."""
        return [
            key
            for key, value in relatives_dict.items()
            if value["type"] in BLOOD_RELATIVE_TYPES
        ]

    @staticmethod
    def get_no_blood_relatives(relatives_dict):
        """Returns the keys (ids) of the dictionary entries without a blood relation."""
        return [
            key
            for key, value in relatives_dict.items()
            if value["type"] not in BLOOD_RELATIVE_TYPES
        ]

    # ---------------------------------------------------------------------------- #
    #                                    parents                                   #
    # ---------------------------------------------------------------------------- #

    def get_blood_parents(self, cat=None) -> list:
        """Get the IDs of the biological parents of a cat.
        :param cat: the cat whose parents you want to find, default None"""
        relevant_cat = self.cat
        if cat:
            relevant_cat = cat
        if relevant_cat.parent1:
            if relevant_cat.parent2:
                return [relevant_cat.parent1, relevant_cat.parent2]
            return [relevant_cat.parent1]
        return []

    def get_adoptive_parents(self, cat=None) -> list:
        """Returns a list of IDs which are adoptive parents of the current cat."""
        relevant_cat = cat if cat else self.cat
        return relevant_cat.adoptive_parents

    # TODO - refactor these to just use one
    def get_parents(self, cat=None) -> list:
        """Returns a list of IDs which are parents to the cat, according to the inheritance hierarchy.
        :param cat: The cat whose parents you want to return"""
        relevant_cat = self.cat
        if cat:
            relevant_cat = cat
        blood_parents = self.get_blood_parents(relevant_cat)
        no_blood_parents = self.get_adoptive_parents(relevant_cat)
        return blood_parents + no_blood_parents

    # ---------------------------------------------------------------------------- #
    #                                     kits                                     #
    # ---------------------------------------------------------------------------- #

    def get_blood_kits(self) -> list:
        """Returns a list of blood related kits IDs."""
        return self.get_blood_relatives(self.kits)

    def get_not_blood_kits(self) -> list:
        """Returns a list of IDs of adopted kits who are not related by blood to the cat."""
        return self.get_no_blood_relatives(self.kits)

    def get_children(self) -> list:
        """Returns a list of IDs corresponding to the cat's kits, according to the inheritance hierarchy."""
        return self.get_blood_relatives(self.kits) + self.get_no_blood_relatives(
            self.kits
        )

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
        return self.get_blood_relatives(self.siblings) + self.get_no_blood_relatives(
            self.siblings
        )

    # ---------------------------------------------------------------------------- #
    #                                parents_siblings                               #
    # ---------------------------------------------------------------------------- #

    def get_blood_parents_siblings(self) -> list:
        """Returns a list of blood related parents_siblings id's."""
        return self.get_blood_relatives(self.parents_siblings)

    def get_not_blood_parents_siblings(self) -> list:
        """Returns a list of id's of parents_siblings, which are not related by blood to the cat."""
        return self.get_no_blood_relatives(self.parents_siblings)

    def get_parents_siblings(self) -> list:
        """Returns a list of id's which are parents_siblings to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(
            self.parents_siblings
        ) + self.get_no_blood_relatives(self.parents_siblings)

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
        return self.get_blood_relatives(self.cousins) + self.get_no_blood_relatives(
            self.cousins
        )

    # ---------------------------------------------------------------------------- #
    #                                 grand_parents                                #
    # ---------------------------------------------------------------------------- #

    def get_blood_grandparents(self) -> list:
        """Returns a list of blood related grand_parents id's."""
        return self.get_blood_relatives(self.grand_parents)

    def get_not_blood_grandparents(self) -> list:
        """Returns a list of id's of grand_parents, which are not related by blood to the cat."""
        return self.get_no_blood_relatives(self.grand_parents)

    def get_grandparents(self) -> list:
        """Returns a list of IDs which are grand_parents to the cat, according to the inheritance hierarchy."""
        return self.get_blood_relatives(
            self.grand_parents
        ) + self.get_no_blood_relatives(self.grand_parents)

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
        return self.get_blood_relatives(self.grand_kits) + self.get_no_blood_relatives(
            self.grand_kits
        )

    # ---------------------------------------------------------------------------- #
    #                                 other related                                #
    # ---------------------------------------------------------------------------- #

    def get_kits_mates(self) -> list:
        """Returns a list of id's which are mates of a kit, according to the inheritance hierarchy."""
        return [key for key in self.kits_mates.keys()]

    def get_siblings_mates(self) -> list:
        """Returns a list of id's which are mates of a sibling, according to the inheritance hierarchy."""
        return [key for key in self.siblings_mates.keys()]

    def get_siblings_kits(self) -> list:
        """Returns a list of id's which are kits of a sibling, according to the inheritance hierarchy."""
        return [key for key in self.siblings_kits.keys()]

    def get_mates(self) -> list:
        """Returns a list of id's which are kits of a sibling, according to the inheritance hierarchy."""
        return [key for key in self.mates.keys()]

    def get_exact_rel_type(self, cat_id):
        all_relations = []
        if cat_id in self.parents:
            all_relations.append(self.parents[cat_id])
        if cat_id in self.mates:
            all_relations.append(self.mates[cat_id])
        if cat_id in self.kits:
            all_relations.append(self.kits[cat_id])
        if cat_id in self.kits_mates:
            all_relations.append(self.kits_mates[cat_id])
        if cat_id in self.siblings:
            all_relations.append(self.siblings[cat_id])
        if cat_id in self.siblings_mates:
            all_relations.append(self.siblings_mates[cat_id])
        if cat_id in self.siblings_kits:
            all_relations.append(self.siblings_kits[cat_id])
        if cat_id in self.parents_siblings:
            all_relations.append(self.parents_siblings[cat_id])
        if cat_id in self.cousins:
            all_relations.append(self.cousins[cat_id])
        if cat_id in self.grand_parents:
            all_relations.append(self.grand_parents[cat_id])
        if cat_id in self.grand_kits:
            all_relations.append(self.grand_kits[cat_id])

        if any(relation["type"] in BLOOD_RELATIVE_TYPES for relation in all_relations):
            return RelationType.RELATED
        else:
            return RelationType.NOT_BLOOD
