import os
import shutil
import unittest

from scripts.game_structure.game.save_load import read_clans

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.game_structure import game
from scripts.housekeeping.datadir import get_save_dir

if not os.path.exists("tests/testSaves"):
    num_example_saves = 0
else:
    _tmp = os.listdir("tests/testSaves")
    num_example_saves = 0
    for i in _tmp:
        if i.startswith("save"):
            num_example_saves += 1


@unittest.skipIf(
    num_example_saves == 0,
    "No example saves found. Download the contents of "
    "https://github.com/ImLvna/clangen-unittest-saves into tests/testSaves to run unittest",
)
class LoadSave(unittest.TestCase):
    def setUp(self):
        if os.path.exists(get_save_dir()):
            shutil.move(get_save_dir(), "saves_backup")

    def tearDown(self):
        if os.path.exists(get_save_dir()):
            shutil.rmtree(get_save_dir())
        if os.path.exists("saves_backup"):
            shutil.move("saves_backup", get_save_dir())

    def old_implimentation(self):
        with open(get_save_dir() + "/clanlist.txt", "r") as read_file:
            clan_list = read_file.read()
            if_clans = len(clan_list)
        if if_clans > 0:
            clan_list = clan_list.split("\n")
            clan_list = [
                i.strip() for i in clan_list if i
            ]  # Remove empty and whitespace
            return clan_list
        else:
            return None

    def new_implimentation(self):
        return read_clans()

    def example_save(self, id):
        if os.path.exists(get_save_dir()):
            shutil.rmtree(get_save_dir())

        # copy tests/testSaves/save<id> to saves
        shutil.copytree("tests/testSaves/save" + str(id), get_save_dir())

    def test_check_current_clan(self):
        for i in range(1, num_example_saves + 1):
            with self.subTest(i=i):
                print("Checking current Clan for save " + str(i))
                self.example_save(i)
                file_list = os.listdir(get_save_dir())
                if "currentclan.txt" in file_list:
                    self.skipTest("Save " + str(i) + " already migrated")
                old_out = self.old_implimentation()
                self.example_save(i)
                new_out = self.new_implimentation()

                self.assertEqual(
                    old_out[0],
                    new_out[0],
                    "Current Clan not saved correctly for save " + str(i),
                )

    def test_check_clan_list(self):
        for i in range(1, num_example_saves + 1):
            with self.subTest(i=i):
                print("Checking clan list for save " + str(i))
                self.example_save(i)
                file_list = os.listdir(get_save_dir())
                if "currentclan.txt" in file_list:
                    self.skipTest("Save " + str(i) + " already migrated")
                old_out = self.old_implimentation().sort()
                self.example_save(i)
                new_out = self.new_implimentation().sort()

                self.assertEqual(
                    old_out, new_out, "Clan list not saved correctly for save " + str(i)
                )


@unittest.skipIf(
    num_example_saves == 0,
    "No example saves found. Download the contents of "
    "https://github.com/ImLvna/clangen-unittest-saves into tests/testSaves to run unittest",
)
class MigrateSave(unittest.TestCase):
    def setUp(self):
        if os.path.exists(get_save_dir()):
            shutil.move(get_save_dir(), "saves_backup")

    def tearDown(self):
        if os.path.exists(get_save_dir()):
            shutil.rmtree(get_save_dir())
        if os.path.exists("saves_backup"):
            shutil.move("saves_backup", get_save_dir())

    def example_save(self, id):
        if os.path.exists(get_save_dir()):
            shutil.rmtree(get_save_dir())

        # copy tests/testSaves/save<id> to saves
        shutil.copytree("tests/testSaves/save" + str(id), get_save_dir())

    def test_migrate_save_onread(self):
        for i in range(1, num_example_saves + 1):
            with self.subTest(i=i):
                print("Checking migration for save " + str(i))
                self.example_save(i)
                file_list = os.listdir(get_save_dir())
                if "currentclan.txt" in file_list:
                    self.skipTest("Save " + str(i) + " already migrated")

                with open(get_save_dir() + "/clanlist.txt", "r") as read_file:
                    clan_name = read_file.read().strip().splitlines()[0]

                read_clans()  # the load save function should migrate the save

                file_list = os.listdir(get_save_dir())
                self.assertIn(
                    "currentclan.txt", file_list, "Save " + str(i) + " not migrated"
                )

                with open(get_save_dir() + "/currentclan.txt", "r") as read_file:
                    curclan = read_file.read().strip()

                self.assertEqual(
                    curclan, clan_name, "Save " + str(i) + " not migrated correctly"
                )
                self.assertNotIn(
                    "clanlist.txt",
                    file_list,
                    "Save " + str(i) + " not migrated correctly",
                )
