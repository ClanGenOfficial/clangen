from dataclasses import dataclass

from scripts.cat.conditions.base_condition_class import BaseCondition


@dataclass(slots=True)
class PermanentCondition(BaseCondition):
    is_congenital: bool
    removed_on_death: bool
    moons_until_discovery: int

    def __eq__(self, other):
        return other == self.name

    def __repr__(self):
        return self.name
