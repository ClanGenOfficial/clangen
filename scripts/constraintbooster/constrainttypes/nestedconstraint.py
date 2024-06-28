from typing import Union, List

from scripts.constraintbooster.constrainttypes.baseconstraint import BaseConstraint


class NestedConstraint(BaseConstraint):
    def __init__(self, name: str, blacklist: Union[List[str], None] = None):
        self.name = name
        self.blacklist = blacklist

    def compute(self, option):
        if not hasattr(option, self.name):
            return 0
        if self.blacklist is None:
            return len(getattr(option, self.name))

        attribute = getattr(option, self.name)
        valid = [val for val in attribute if val not in self.blacklist]
        return len(valid)
