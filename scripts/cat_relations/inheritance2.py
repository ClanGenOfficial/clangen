from scripts.cat.cats import Cat
from scripts.cat.save_load import get_faded_ids
from typing import TypedDict, Dict, List, Literal, Set, Tuple
from enum import StrEnum
from dataclasses import dataclass, field
from collections import defaultdict


class RelationType(StrEnum):
    """An enum representing the possible relationships of a cat"""

    BLOOD = "direct related"  # direct blood related - do not need a special print
    ADOPTIVE = "adoptive"  # not blood related but close (parents, kits, siblings)

    HALF_BLOOD = "half sibling"  # only one blood parent is the same (siblings only)
    NOT_BLOOD = "not blood related"  # not blood related for parent siblings
    RELATED = "blood related"  # related by blood (different mates only)


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
        ] = {}

    def __getitem__(self, arg: str):
        return self._cat_to_rels.get(arg)

    def __repr__(self):
        return str(self._cat_to_rels)

    def load_inheritance(self, cat: Cat):
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

        for m in cat.mate:
            self._cat_to_rels[cat.ID].mates.append(
                {"relation_type": RelationType.NOT_BLOOD, "cat_id": m}
            )

    def load_inheritances(self, load_faded=False):
        self._cat_to_rels = defaultdict(FamilyRelations)

        for cat in Cat.all_cats_list:
            self.load_inheritance(cat)

        if load_faded:
            for cat_id in get_faded_ids():
                cat = Cat.fetch_cat(cat_id)
                if not cat:
                    continue
                self.load_inheritance(cat)

    def get_parents(self, cat_id: str) -> Set[str]:
        return {p["cat_id"] for p in self._cat_to_rels[cat_id].parents}

    def get_mates(self, cat_id: str) -> Set[str]:
        return {m["cat_id"] for m in self._cat_to_rels[cat_id].mates}

    def get_children(self, cat_id: str) -> Set[str]:
        return {k["cat_id"] for k in self._cat_to_rels[cat_id].children}

    def get_siblings(self, cat_id: str) -> Set[str]:
        siblings = set()
        for p in self.get_parents(cat_id):
            for c in self.get_children(p):
                siblings.add(c)

        if cat_id in siblings:
            siblings.remove(cat_id)
        return siblings

    def get_grandparents(self, cat_id: str) -> Set[str]:
        grandparents = set()
        for p in self.get_parents(cat_id):
            for gp in self.get_parents(p):
                grandparents.add(gp)
        return grandparents

    def get_grandchildren(self, cat_id: str) -> Set[str]:
        grandchildren = set()
        for c in self.get_children(cat_id):
            for gc in self.get_children(c):
                grandchildren.add(gc)
        return grandchildren

    def get_siblings_mates(self, cat_id: str) -> Set[str]:
        siblings_mates = set()
        for s in self.get_siblings(cat_id):
            for m in self.get_mates(s):
                siblings_mates.add(m)
        return siblings_mates

    def get_childrens_mates(self, cat_id: str) -> Set[str]:
        childrens_mates = set()
        for c in self.get_children(cat_id):
            for m in self.get_mates(c):
                childrens_mates.add(m)
        return childrens_mates

    def get_siblings_children(self, cat_id: str) -> Set[str]:
        siblings_children = set()
        for s in self.get_siblings(cat_id):
            for c in self.get_children(s):
                siblings_children.add(c)
        return siblings_children

    def get_parents_siblings(self, cat_id: str) -> Set[str]:
        parents_siblings = set()
        for p in self.get_parents(cat_id):
            for s in self.get_siblings(p):
                parents_siblings.add(s)
        return parents_siblings

    def get_cousins(self, cat_id: str) -> Set[str]:
        cousins = set()
        for ps in self.get_parents_siblings(cat_id):
            for c in self.get_children(ps):
                cousins.add(c)
        return cousins

    def get_relatives(self, cat_id: str, cousin_allowed: bool) -> Set[str]:
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
        if cousin_allowed:
            relatives.update(self.get_cousins(cat_id))
        return relatives

    def is_related(self, cat_a: str, cat_b: str, cousin_allowed) -> bool:
        shared_parents = self.get_parents(cat_a).intersection(self.get_parents(cat_b))
        if not cousin_allowed:
            return shared_parents

        # checking for cousins
        if shared_parents:  # shared parents, don't have to check grandparents
            return True
        return self.get_grandparents(cat_a).intersection(self.get_grandparents(cat_b))

    def is_grandparent(self, cat_a: str, maybe_grandparent: str) -> bool:
        return maybe_grandparent in self.get_grandparents(cat_a)

    def is_parent(self, cat_a: str, maybe_parent: str) -> bool:
        return maybe_parent in self.get_parents(cat_a)

    def is_sibling(self, cat_a: str, maybe_sibling: str) -> bool:
        return maybe_sibling in self.get_siblings(cat_a)

    def is_uncle_aunt(self, cat_a: str, maybe_uncle_aunt: str) -> bool:
        return cat_a in self.get_siblings_children(maybe_uncle_aunt)

    def is_cousins(self, cat_a: str, maybe_cousin: str) -> bool:
        return maybe_cousin in self.get_cousins(cat_a)


inheritance_db = InheritanceDb()
