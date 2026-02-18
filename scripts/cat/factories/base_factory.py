from abc import ABC, abstractmethod


class BaseCatFactory(ABC):
    @abstractmethod
    def __init__(self, rng):
        pass

    @abstractmethod
    def create_cat(self, **kwargs):
        pass
