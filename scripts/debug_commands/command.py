"""
Base command class for debug mode.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    @property
    @abstractmethod
    def name(self):
        """The name of the command"""

    @property
    @abstractmethod
    def description(self):
        """The description of the command"""

    """
    Usage Formatting:
        Flag arguments (such as the get command's "game" flag) should be wrapped in brackets:
          * [flag]
        
        Value arguments (such as the set command's "setting" value) should be wrapped like this:
          * <value>
          Value arguments can also have a type assigned to them:
          * <value: type>
            * Typically int, str, or bool
        
        Multiple possible values for a flag/value should be wrapped together and unionized:
          * [flag|flag2] or <value|value2>
        
        If one flag accepts more arguments than another, it should be unionized but not wrapped together:
          * [flag] | [flag2] <value>
        
        Groups of arguments should be grouped together by parentheses:
          * ([flag] <value>) | ([flag2] <value> <value2>)
        
        Optional arguments are denoted by a question mark at the end:
          * [flag] <value>?
          Groups may also be optional:
          * [flag] (<value> <value2> [flag2] <value3>)?
          Unions too:
          * [flag|flag2]?
    
    Notes:
        Groups should only be used to clarify the order of arguments:
            * [flag] | [flag2] <value> shouldn't be ([flag]) | ([flag2] <value>)
                * Doing ([flag] | [flag2]) <value> is equivalent to [flag|flag2] <value>
            * [flag] <value> | [flag2] <value2> should be ([flag] <value>) | ([flag2] <value2>)
        
        It is assumed that a flag is to be typed out literally:
            * command [do_smth] shouldn't be typed out as "command do"
            * Instead it should be typed out as "command do_smth"
        
        A value argument with only some accepted options should be written as a unionized flag:
            * command [flag] <value: int> encompasses all integer values, however, the actual command only accepts
            3 integers as valid
            * The command should then be rewritten as command [flag] [0|1|2]
            * However, if you still wish to name the flag, you can wrap it as a value argument with the flag union
            contained within:
                * command [flag] <value: int [0|1|2]>
            * Unionized value arguments generally shouldn't only accept a few options
    """

    @property
    def usage(self):
        """The usage of the command."""
        return ""

    def help(self):
        """The help of the command"""
        return self.description

    @property
    def aliases(self):
        """The aliases of the command"""
        return []

    @property
    def sub_commands(self):
        """The sub commands of the command"""
        return []

    @property
    def bypass_conjoined_strings(self):
        """Bypasses arguments wrapped in quotes being joined together"""
        return False

    @property
    def _aliases(self):
        return [self.name] + self.aliases

    @abstractmethod
    def callback(self, args: List[str]):
        """The callback of the command"""
