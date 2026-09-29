from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


class EventInformation:
    """A class to hold info regarding a single event"""

    def __init__(
        self,
        text: str,
        types: list[
            Literal[
                "relation", "ceremony", "birth_death", "health", "other_clans", "misc"
            ]
        ] = None,
        cats_involved: list | tuple = None,
        cat_dict: dict = None,
    ):
        """
        :param text: The event text.
        :param types: Which types of event, in a list. Current options are:
                "relation", "ceremony", "birth_death", "health", "other_clans", "misc"
        :param cats_involved: list or tuples of the IDs of cats involved in the event
        :param cat_dict: dict suitable for event_text_adjust containing the cat's text abbreviation as the key and the
        cat object as the value
        """

        self.text = text

        if types:
            self.types = list(types)
        else:
            self.types = []

        self.cat_dict = cat_dict if cat_dict else {}

        if isinstance(cats_involved, str):
            self.cats_involved = []
            self.cats_involved.append(cats_involved)
        elif isinstance(cats_involved, list) or isinstance(cats_involved, tuple):
            self.cats_involved = list(cats_involved)
        else:
            self.cats_involved = []

        # if cats involved wasn't specified but cats dict was, use that as cats involved
        if self.cat_dict and self.cats_involved == []:
            self.cats_involved = [cat.ID for cat in self.cat_dict.values()]

    def to_dict(self):
        """
        Convert EventInformation to dictionary.
        """
        cat_dict = self.cat_dict.copy() if self.cat_dict else {}
        if self.cat_dict:
            for abbr, kitty in self.cat_dict.items():
                cat_dict[abbr] = kitty.ID

        return {
            "text": self.text,
            "types": self.types,
            "cats_involved": self.cats_involved,
            "cat_dict": cat_dict,
        }

    @staticmethod
    def from_dict(info_dict: dict, cat_class: "Cat"):
        """
        Return new EventInformation object based on dict.
        """

        if "text" not in info_dict:
            return None

        cat_dict = info_dict.get("cat_dict", {})
        if cat_dict:
            for abbr, kitty in cat_dict.copy().items():
                cat_dict[abbr] = cat_class.fetch_cat(kitty)

        return EventInformation(
            text=info_dict["text"],
            types=info_dict.get("types", None),
            cats_involved=info_dict.get("cats_involved", None),
            cat_dict=cat_dict,
        )
