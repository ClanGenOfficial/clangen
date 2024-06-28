from typing import List

from scripts.constraintbooster.constrainttypes.baseconstraint import BaseConstraint


class SimpleConstraint(BaseConstraint):
    def __init__(self, name: str, blacklist: List[str]):
        self.name = name
        self.blacklist = blacklist

    def compute(self, option):
        attribute = getattr(option, self.name, None)
        if attribute is None:
            return 0
        if self.blacklist is not None:
            if all(val in self.blacklist for val in attribute):
                return 0

        return 1
