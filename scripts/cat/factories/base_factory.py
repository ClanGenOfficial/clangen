from abc import ABC, abstractmethod

from scripts.cat.cats import Cat


class BaseCatFactory(ABC):
    @abstractmethod
    def __init__(self, rng):
        pass

    @abstractmethod
    def create_cat(self, **kwargs) -> Cat:
        pass
