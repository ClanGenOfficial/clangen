from dataclasses import dataclass, field
from typing import Union

from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
    RelationshipChangeDict,
)


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class TextPoolEvent:
    id: str
    strings: list[str]
    location: list[str] = field(default_factory=list)
    season: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    involved_cats: dict[str, Union[InvolvedCatDict, dict]] = field(default_factory=dict)
    relationship_constraint: list[RelationshipConstraintDict] = field(
        default_factory=list[RelationshipConstraintDict]
    )
    relationship_changes: list[RelationshipChangeDict] = field(
        default_factory=list[RelationshipChangeDict]
    )

    def __repr__(self):
        return self.id
