from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from random import Random

from scripts.cat.cats import Cat


class BaseCatFactory(ABC):
    @abstractmethod
    def create_cat(self, **kwargs) -> Cat:
        pass
