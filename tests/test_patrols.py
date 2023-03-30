import unittest
from unittest.mock import patch

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts import events
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.events_module.relationship.romantic_events import Romantic_Events
from scripts.cat.cats import Cat
from scripts.clan import Clan

class Patols(unittest.TestCase):
    

