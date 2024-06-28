from typing import Dict

from scripts.constraintbooster.constrainttypes.baseconstraint import BaseConstraint


class SplitConstraint(BaseConstraint):
    def __init__(self, name, separator, field, point_array, blacklist: Dict):
        self.name = name
        self.separator = separator
        self.field = field
        self.point_array = point_array
        self.blacklist = blacklist

    def compute(self, option) -> int:
        if not hasattr(option, self.name):
            return 0
        value = 0
        for record in getattr(option, self.name):
            if self.blacklist is not None:
                if record in self.blacklist.keys():
                    value += self.blacklist[record]

            split = record.split(self.separator)
            if len(split) - 1 < self.field:
                continue
            value += (
                self.point_array[split[self.field]]
                if split[self.field] in self.point_array
                else 0
            )
        return value
