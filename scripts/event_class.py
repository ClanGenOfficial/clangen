
class Single_Event():
    """A class to hold info regarding a single event """

    def __init__(self, text, types=None, cats_involved=None):
        """ text: The event text.
        types: Which types of event, in a list or tuple. Current options are:
                "relation", "ceremony", "birth_death", "health", "other_clans", "misc"
        cat_involved: list or tuples of the IDs of cats involved in the event """

        self.text = text

        if type(types) == str:
            self.types = []
            self.types.append(types)
        elif type(types) == list or type(types) == tuple:
            self.types = list(types)
        else:
            self.types = []

        if type(cats_involved) == str:
            self.cats_involved = []
            self.cats_involved.append(cats_involved)
        elif type(cats_involved) == list or type(cats_involved) == tuple:
            self.cats_involved = list(cats_involved)
        else:
            self.cats_involved = []

