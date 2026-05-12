from scripts.cat.cats import Cat
from typing import TypedDict, Dict, List, Literal, Set
from enum import StrEnum
from dataclasses import dataclass, field


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
    siblings: List[FamilyRelationLink] = field(default_factory=lambda: [])
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

    def load_inheritances(self):
        cat_to_rel: Dict[
            str,
            FamilyRelations,
        ] = {}

        # add parents
        for c in Cat.all_cats_list:
            if c.ID not in cat_to_rel:
                cat_to_rel[c.ID] = FamilyRelations()

            for p in c.adoptive_parents:
                cat_to_rel[c.ID].parents.append(
                    {"relation_type": RelationType.ADOPTIVE, "cat_id": p}
                )
            for p in [c.parent1, c.parent2]:
                if p:
                    cat_to_rel[c.ID].parents.append(
                        {"relation_type": RelationType.BLOOD, "cat_id": p}
                    )

            for m in c.mate:
                cat_to_rel[c.ID].mates.append(
                    {"relation_type": RelationType.NOT_BLOOD, "cat_id": m}
                )

        # add kits
        # in a separate loop so that we're sure we already know about their parents
        for c in Cat.all_cats_list:
            for parent_rel in cat_to_rel[c.ID].parents:
                parent_id = parent_rel["cat_id"]
                parent = Cat.fetch_cat(parent_id)
                if parent:
                    rel: FamilyRelationLink = {"cat_id": c.ID}
                    if parent_rel["relation_type"] == RelationType.BLOOD:
                        rel["relation_type"] = RelationType.BLOOD
                    else:  # RelationType.ADOPTIVE
                        rel["relation_type"] = RelationType.ADOPTIVE

                    # might not exist if you're faded, so we have to do. this.
                    if parent_id not in cat_to_rel:
                        cat_to_rel[parent_id] = FamilyRelations()

                    cat_to_rel[parent_id].children.append(rel)

        self._cat_to_rels = cat_to_rel

    def get_parents(self, cat_id: str) -> Set[str]:
        return {p["cat_id"] for p in self._cat_to_rels[cat_id].parents}

    def get_mates(self, cat_id: str) -> Set[str]:
        return {m["cat_id"] for m in self._cat_to_rels[cat_id].mates}

    def get_children(self, cat_id: str) -> Set[str]:
        return {k["cat_id"] for k in self._cat_to_rels[cat_id].children}

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

    def get_siblings(self, cat_id: str) -> Set[str]:
        siblings = set()
        for p in self.get_parents(cat_id):
            for c in self.get_children(p):
                siblings.add(c)

        if cat_id in siblings:
            siblings.remove(cat_id)
        return siblings


inheritance_db = InheritanceDb()
