import unittest

from itertools import combinations

import ujson

with open(
    "./resources/dicts/traits/trait_ranges.json", "r", encoding="utf-8"
) as read_file:
    FACET_RANGES = ujson.loads(read_file.read())

# range of 0-16
facet_range = range(0, 17)


def check_validity(range_dict, combination) -> bool:
    for trait in range_dict:
        if combination[0] not in range(
            trait["lawfulness"][0], trait["lawfulness"][1] + 1
        ):
            continue
        if combination[1] not in range(
            trait["sociability"][0], trait["sociability"][1] + 1
        ):
            continue
        if combination[2] not in range(
            trait["aggression"][0], trait["aggression"][1] + 1
        ):
            continue
        if combination[3] not in range(
            trait["stability"][0], trait["stability"][1] + 1
        ):
            continue

        return True

    return False


class FacetCoverageTest(unittest.TestCase):
    def test_normal_traits(self):
        """Test that all facets are correct for at least one normal trait"""
        for combo in combinations(facet_range, 4):
            with self.subTest(combo=combo):
                self.assertTrue(
                    check_validity(FACET_RANGES["normal_traits"].values(), combo)
                )

    def test_kit_traits(self):
        """Test that all facets are correct for at least one kit trait"""
        for combo in combinations(facet_range, 4):
            with self.subTest(combo=combo):
                self.assertTrue(
                    check_validity(FACET_RANGES["kit_traits"].values(), combo)
                )
