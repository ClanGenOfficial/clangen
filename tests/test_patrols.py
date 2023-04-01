import unittest
from unittest.mock import patch

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.patrol import Patrol, PatrolEvent
from scripts.clan import Clan
from scripts.game_structure.game_essentials import game
from scripts.cat.cats import Cat

class Patols(unittest.TestCase):
    
    @patch('scripts.patrol.Patrol.get_possible_patrols')
    def test_success_failure(self, get_possible_patrols):
        # given
        cats = [Cat()]
        game.clan = Clan(
            name = "",
        )
        game.clan.leader = None
        game.clan.deputy = None
        game.clan.biome = ""
        test_patrol = PatrolEvent(
            patrol_id = "test123",
            intro_text="!DEFAULT PATROL! The patrol heads out for a uneventful walk.",
            chance_of_success=100,
            exp=0,
            success_text=["!DEFAULT PATROL! Nothing interesting happens"],
            fail_text=["!DEFAULT PATROL! Nothing interesting happens, but you still failed. "],
            decline_text=["!DEFAULT PATROL! The patrol decided to head home. "],
            min_cats=1,
            max_cats=6
        )
        patrol = Patrol()
        
        #When
        get_possible_patrols.return_value = ([test_patrol], None)
        patrol.patrol_setup(cats)
        
        self.assertEqual(patrol.patrol_event, test_patrol)
        
        

