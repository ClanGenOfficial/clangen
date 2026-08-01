import os
import unittest
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.clan_package.clan_names import get_possible_clan_names
from scripts.screens.make_clan_screens.MakeClanScreenBase import (
    ClanInfo,
    MakeClanScreenBase,
)


class TestRandomClanName(unittest.TestCase):
    def test_custom_display_name_does_not_crash(self):
        """A player-typed name is not in the possible names, so it cannot be removed."""
        custom_name = "Zzqxvw"
        self.assertNotIn(custom_name, get_possible_clan_names())

        screen = SimpleNamespace(clan_info=ClanInfo(display_name=custom_name))
        name = MakeClanScreenBase.random_clan_name(screen)

        self.assertIn(name, get_possible_clan_names())

    def test_random_name_differs_from_current_name(self):
        current = get_possible_clan_names()[0]
        screen = SimpleNamespace(clan_info=ClanInfo(display_name=current))

        for _ in range(20):
            self.assertNotEqual(MakeClanScreenBase.random_clan_name(screen), current)


if __name__ == "__main__":
    unittest.main()
