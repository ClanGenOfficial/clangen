# pylint: disable=line-too-long
"""

TODO: Docs


"""


# pylint: enable=line-too-long
class Single_Event():
    """A class to hold info regarding a single event """

    def __init__(self, text, types=None, cats_involved=None):
        """ text: The event text.
        types: Which types of event, in a list or tuple. Current options are:
                "relation", "ceremony", "birth_death", "health", "other_clans", "misc"
        cat_involved: list or tuples of the IDs of cats involved in the event """

        self.text = text

        if isinstance(types, str):
            self.types = []
            self.types.append(types)
        elif isinstance(types, list) or isinstance(types, tuple):
            self.types = list(types)
        else:
            self.types = []

        if isinstance(cats_involved, str):
            self.cats_involved = []
            self.cats_involved.append(cats_involved)
        elif isinstance(cats_involved, list) or isinstance(
                cats_involved, tuple):
            self.cats_involved = list(cats_involved)
        else:
            self.cats_involved = []

    def to_dict(self):
        """
        Convert Single_Event to dictionary.
        """

        return {
            "text": self.text,
            "types": self.types,
            "cats_involved": self.cats_involved
        }

    @staticmethod
    def from_dict(dict):
        """
        Return new Single_Event based on dict.

        dict: The dictionary to convert to Single_Event.
        """

        if "text" not in dict:
            return None
        return Single_Event(
            text=dict["text"],
            types=dict.get("types", None),
            cats_involved=dict.get("cats_involved", None)
        )
