from abc import ABC


class BaseConstraint(ABC):
    def compute(self, option):
        pass
