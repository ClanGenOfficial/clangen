import ujson
import unittest

from scripts.cat.cats import Cat
from scripts.conditions import Illness, Injury

class TestsIllnesses(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        ILLNESSES = None
        with open(f"{resource_directory}Illnesses.json", 'r') as read_file:
            ILLNESSES = ujson.loads(read_file.read())
        return ILLNESSES

    def test_get_ill_unknown_name(self):
        cat = Cat()
        no_name = "NotExisting"

        try:
            cat.get_ill(no_name)
        except BaseException as exc:
            assert False, f"Unknown illness name raises an exception: {exc}"


class TestInjury(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        INJURIES = None
        with open(f"{resource_directory}Injuries.json", 'r') as read_file:
            INJURIES = ujson.loads(read_file.read())
        return INJURIES
    
    def test_get_injured_unknown_name(self):
        cat = Cat()
        no_name = "NotExisting"

        try:
            cat.get_injured(no_name)
        except BaseException as exc:
            assert False, f"Unknown injury name raises an exception: {exc}"