
import ujson
from scripts.housekeeping.datadir import get_save_dir
from scripts.models.clan_cat import *
import unittest
TESTED_CLAN_NAME = ''


with open(f'{get_save_dir()}/{TESTED_CLAN_NAME}/clan_cats.json', 'r') as read_file:
    convert = ujson.loads(read_file.read())
class testValidationData(unittest.TestCase):
    def test_validate_clan_cat_data():
        get_validated_clan_cat_data()