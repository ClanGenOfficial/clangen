import unittest
from unittest.mock import patch

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat_relations.interaction import Group_Interaction
from scripts.events_module.relationship.group_events import Group_Events
from scripts.cat.cats import Cat

class Filtering(unittest.TestCase):
    def main_cat(self):
        # given
        group_events = Group_Events()
        main_cat = Cat()
        main_cat.status = "warrior"
        group_events.abbreviations_cat_id={"m_c": main_cat.ID}

        interaction1 = Group_Interaction("1")
        interaction1.status_constraint = {"m_c": ["warrior"]}

        interaction2 = Group_Interaction("1")
        interaction2.status_constraint = {"m_c": ["healer"]}
        
        all_interactions = [interaction1, interaction2]

        # when
        filtered_interactions = group_events.get_main_cat_interactions(all_interactions, "Any", "Any")

        # then
        self.assertEqual(len(filtered_interactions), len(all_interactions))
