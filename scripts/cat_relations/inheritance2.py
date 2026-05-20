from typing import TypedDict, Dict, List, Set, Tuple
from enum import StrEnum
from dataclasses import dataclass, field
from collections import defaultdict


class RelationType(StrEnum):
    """An enum representing the possible relationships of a cat"""

    BLOOD = "direct_related"  # direct blood related - do not need a special print
    ADOPTIVE = "adoptive"  # not blood related but close (parents, kits, siblings)

    HALF_BLOOD = "half_sibling"  # only one blood parent is the same (siblings only)
    NOT_BLOOD = "not_blood_related"  # not blood related for parent siblings
    RELATED = "blood_related"  # related by blood (different mates only)


class FamilyRelationLink(TypedDict):
    relation_type: RelationType
    cat_id: str


@dataclass
class FamilyRelations:
    parents: List[FamilyRelationLink] = field(default_factory=lambda: [])
    children: List[FamilyRelationLink] = field(default_factory=lambda: [])
    mates: List[FamilyRelationLink] = field(default_factory=lambda: [])


class InheritanceDb:
    def __init__(self):
        self._cat_to_rels: Dict[
            str,
            FamilyRelations,
        ] = defaultdict(FamilyRelations)
        self._cat_to_litter: Dict[str, Tuple] = {}
        self._saved_family_rels: Dict[str, FamilyRelations] = {}

    def __getitem__(self, arg: str):
        return self._cat_to_rels.get(arg)

    def __repr__(self):
        return str(self._cat_to_rels)

    def _load_inheritance(self, cat, save=False):
        """
        Loads inheritance for a single cat.

        :param Cat cat: A cat object to load inheritance for.
        :param bool save: If `True`, this inheritance data will be restored
        when `load_inheritances()` is called again, as long as `clear_stored_data()`
        has not been called.
        """
        for parent_id in cat.adoptive_parents:
            self._cat_to_rels[cat.ID].parents.append(
                {"relation_type": RelationType.ADOPTIVE, "cat_id": parent_id}
            )
            self._cat_to_rels[parent_id].children.append(
                {"relation_type": RelationType.ADOPTIVE, "cat_id": cat.ID}
            )

        for parent_id in (cat.parent1, cat.parent2):
            if parent_id:
                self._cat_to_rels[cat.ID].parents.append(
                    {"relation_type": RelationType.BLOOD, "cat_id": parent_id}
                )
                self._cat_to_rels[parent_id].children.append(
                    {"relation_type": RelationType.BLOOD, "cat_id": cat.ID}
                )
        if cat.parent1 or cat.parent2:
            self._cat_to_litter[cat.ID] = (
                frozenset((cat.parent1, cat.parent2)),
                cat.moons + cat.dead_for,
            )

        try:
            previous_mates = cat.previous_mates
        except AttributeError:
            previous_mates = []
        for mates_list in (cat.mate, previous_mates):
            for m in mates_list:
                self._cat_to_rels[cat.ID].mates.append(
                    {"relation_type": RelationType.NOT_BLOOD, "cat_id": m}
                )

        if save:
            self._saved_family_rels[cat.ID] = self._cat_to_rels[cat.ID]

    def clear_stored_data(self):
        """
        Clears "stored" data when loaded inheritances, such as the
        data of faded cats and which litter a cat belongs to.
        Does NOT clear the inheritance data itself, which is automatically
        cleared and reloaded when calling `load_inheritances()`

        Make sure to call this when loading new Clans.
        """
        self._cat_to_litter = {}
        self._saved_family_rels = {}

    def load_inheritances(self, Cat, get_faded_ids=None):
        """
        Loads inheritance for every cat.

        :Cat: The Cat object. Required for the all_cats_list and cat fetching.
        :get_faded_ids: (Optional) A function that will return a list of all faded IDs.
        """
        self._cat_to_rels = defaultdict(FamilyRelations)
        for cat in Cat.all_cats_list:
            self._load_inheritance(cat)

        if get_faded_ids:
            for cat_id in get_faded_ids():
                cat = Cat.fetch_cat(cat_id)
                if not cat:
                    continue
                # "save" the inheritances of faded cats bc they're static
                self._load_inheritance(cat, True)
        else:  # not loading faded cats; restore the "saved" inheritances
            for cat_id, saved_family_rel in self._saved_family_rels.items():
                self._cat_to_rels[cat_id] = saved_family_rel

    def get_parents(self, cat_id: str) -> Set[str]:
        return {p["cat_id"] for p in self._cat_to_rels[cat_id].parents}

    def get_mates(self, cat_id: str) -> Set[str]:
        return {m["cat_id"] for m in self._cat_to_rels[cat_id].mates}

    def get_children(self, cat_id: str) -> Set[str]:
        return {k["cat_id"] for k in self._cat_to_rels[cat_id].children}

    def get_siblings(self, cat_id: str) -> Set[str]:
        siblings = set()
        for p in self.get_parents(cat_id):
            siblings.update(self.get_children(p))
        # don't be your own sibling
        siblings.discard(cat_id)
        return siblings

    def get_grandparents(self, cat_id: str) -> Set[str]:
        grandparents = set()
        for p in self.get_parents(cat_id):
            grandparents.update(self.get_parents(p))
        return grandparents

    def get_grandchildren(self, cat_id: str) -> Set[str]:
        grandchildren = set()
        for c in self.get_children(cat_id):
            grandchildren.update(self.get_children(c))
        return grandchildren

    def get_siblings_mates(self, cat_id: str) -> Set[str]:
        siblings_mates = set()
        for s in self.get_siblings(cat_id):
            siblings_mates.update(self.get_mates(s))
        return siblings_mates

    def get_childrens_mates(self, cat_id: str) -> Set[str]:
        childrens_mates = set()
        for c in self.get_children(cat_id):
            childrens_mates.update(self.get_mates(c))
        return childrens_mates

    def get_siblings_children(self, cat_id: str) -> Set[str]:
        siblings_children = set()
        for s in self.get_siblings(cat_id):
            siblings_children.update(self.get_children(s))
        return siblings_children

    def get_parents_siblings(self, cat_id: str) -> Set[str]:
        parents_siblings = set()
        for p in self.get_parents(cat_id):
            parents_siblings.update(self.get_siblings(p))
        return parents_siblings

    def get_cousins(self, cat_id: str) -> Set[str]:
        cousins = set()
        for ps in self.get_parents_siblings(cat_id):
            cousins.update(self.get_children(ps))
        # don't be your own cousin
        cousins.discard(cat_id)
        return cousins

    def get_relatives(self, cat_id: str, exclude_cousins: bool) -> Set[str]:
        get_relative_functions = (
            self.get_parents,
            self.get_children,
            self.get_siblings,
            self.get_grandparents,
            self.get_grandchildren,
            self.get_siblings_children,
            self.get_parents_siblings,
        )

        relatives = set()
        for get_relative_function in get_relative_functions:
            relatives.update(get_relative_function(cat_id))

        if exclude_cousins:
            return relatives
        else:
            relatives.update(self.get_cousins(cat_id))
        return relatives

    def is_related(self, cat_a: str, cat_b: str, exclude_cousins) -> bool:
        return cat_b in self.get_relatives(
            cat_a, exclude_cousins
        ) or cat_a in self.get_relatives(cat_b, exclude_cousins)

    def is_grandparent(self, maybe_grandparent: str, cat_a: str) -> bool:
        return maybe_grandparent in self.get_grandparents(cat_a)

    def is_parent(self, maybe_parent: str, cat_a: str) -> bool:
        return maybe_parent in self.get_parents(cat_a)

    def is_sibling(self, cat_a: str, cat_b: str) -> bool:
        return cat_b in self.get_siblings(cat_a)

    def is_uncle_aunt(self, maybe_uncle_aunt: str, cat_a: str) -> bool:
        return cat_a in self.get_siblings_children(maybe_uncle_aunt)

    def is_cousin(self, cat_a: str, cat_b: str) -> bool:
        return cat_b in self.get_cousins(cat_a)

    def is_littermate(self, cat_a: str, cat_b: str) -> bool:
        try:
            return self._cat_to_litter[cat_a] == self._cat_to_litter[cat_b]
        except KeyError:
            return False

    def compare_to_inheritance(self, cat_id: str, inheritance):
        """
        This is a helper function for testing `inheritance2` by comparing it to the
        previous `Inheritance` code. It's not used anywhere, but you can call/modify
        it if you want to compare `inheritance2` data to old `Inheritance` data.

        Currently, it checks that `inheritance2` contains all the cats that
        corresponding `Inheritance` does
            (i.e. that `Inheritance` data is a subset of `inheritance2` data).
        Note that this does NOT mean that they are equal!
        For example, `inheritance2` can also contain cats that AREN'T in `Inheritance`.
        If this happens, a warning message will be printed to console, and you can evaluate
        it really is an error or not.

        `FamilyTreeScreen.py` is a good place to use this, since it still
        uses the `Inheritance` code due to `inheritance2` not yet implementing
        some data that's displayed on that screen.

        This function should be removed when the original `Inheritance`
        code is phased out.

        Example Usage:
        ```
        from scripts.cat_relations.inheritance2 import inheritance_db
        # ...

        cat.create_inheritance_new_cat() # cat is a Cat
        if not inheritance_db.compare_to_inheritance(cat.ID, cat.inheritance):
            print(f"inheritance_db is not a subset of Inheritance for {cat.ID}!")
        ```

        :param inheritance: The `Inheritance` data you want to compare.
        :param cat_id: The ID of the cat whose `Inheritance` it is.
        :return bool: If the `inheritance2` data contains all the
                      `Inheritance` data. This does NOT mean they are equal!
        """

        inheritance_db_to_inheritance_functions = [
            (inheritance.get_parents, self.get_parents),
            (inheritance.get_children, self.get_children),
            (inheritance.get_siblings, self.get_siblings),
            (inheritance.get_parents_siblings, self.get_parents_siblings),
            (inheritance.get_cousins, self.get_cousins),
            (inheritance.get_grandparents, self.get_grandparents),
            (inheritance.get_grand_kits, self.get_grandchildren),
            (inheritance.get_siblings_kits, self.get_siblings_children),
            (inheritance.get_mates, self.get_mates),
        ]

        for t in inheritance_db_to_inheritance_functions:
            original = set(t[0]())
            sequel = t[1](cat_id)
            if original != sequel:
                print(
                    f"WARNING: inheritance.{t[0].__name__} differs from inheritance_db.{t[1].__name__} for cat {cat_id}!"
                )
                print(f"    inheritance.{t[0].__name__}: {original}")
                print(f"    inheritance_db.{t[1].__name__}: {sequel}")
            if not original.issubset(sequel):
                return False

        if not set(inheritance.all_involved).issubset(self.get_relatives(cat_id, True)):
            return False
        if not set(inheritance.all_but_cousins).issubset(
            self.get_relatives(cat_id, False)
        ):
            return False
        return True


inheritance_db = InheritanceDb()
