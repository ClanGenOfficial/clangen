"""
Base command class for debug mode.
"""

from abc import ABC, abstractmethod


class Command(ABC):

    @property
    @abstractmethod
    def name(self):
        """The name of the command"""

    @property
    @abstractmethod
    def description(self):
        """The description of the command"""

    @property
    def usage(self):
        """The usage of the command"""
        return ""

    def help(self):
        """The help of the command"""
        return self.description

    @property
    def aliases(self):
        """The aliases of the command"""
        return []

    @property
    def bypassConjoinedStrings(self):
        """Bypasses arguments wrapped in quotes being joined together"""
        return False

    @property
    def _aliases(self):
        return [self.name] + self.aliases

    @abstractmethod
    def callback(self, args: list[str]):
        """The callback of the command"""
