from .buttons import *
from .cats import *


class Events(object):
    all_events = {}

    def __init__(self, e_type=None, **cats):
        self.e_type = e_type
        self.ID = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9))
        if e_type is not None:
            # Leave "e_type" empty for example class
            self.all_events[self.ID] = self
        self.cats = cats

    def kits_born(self, pos, parent1, parent2=None):
        if parent2 is not None:
            verdana.text('Kittens were born to ' + str(parent1.name) + ' and ' + str(parent2.name) + '!', pos)
        else:
            verdana.text('Kittens were born to ' + str(parent1.name) + '!', pos)


events_class = Events()
