import os
import unittest
from unittest.mock import MagicMock

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.screens.RelationshipScreen import RelationshipScreen


class TestRelationshipScreenPageNumber(unittest.TestCase):
    @staticmethod
    def _make_screen(chunks):
        screen = RelationshipScreen.__new__(RelationshipScreen)
        screen.chunks = chunks
        screen.current_page = 1
        screen.relation_elements = {}
        screen.prior_chunk = []

        page_number = MagicMock()
        page_number.text = "test/test"
        page_number.set_text = lambda text: setattr(page_number, "text", text)

        screen.elements = {
            "page_number": page_number,
            "next_page_button": MagicMock(),
            "previous_page_button": MagicMock(),
        }
        return screen

    def test_page_number_with_no_visible_relationships(self):
        """No relationship passes the current filters, so the page counter must
        not keep the placeholder text it was created with."""
        screen = self._make_screen([])

        screen.update_relationships()

        self.assertEqual(screen.elements["page_number"].text, "0/0")
        screen.elements["next_page_button"].disable.assert_called_once()
        screen.elements["previous_page_button"].disable.assert_called_once()
