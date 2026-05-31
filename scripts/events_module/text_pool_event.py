from dataclasses import dataclass

from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
)


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class TextPoolEvent:
    id: str
    location: list[str]
    season: list[str]
    tags: list[str]
    strings: list[str]
    involved_cats: dict[str, InvolvedCatDict]
    relationship_constraint: [list[RelationshipConstraintDict]]

    def __repr__(self):
        return self.id
