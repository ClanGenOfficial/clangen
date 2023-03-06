import unittest
from unittest.mock import patch
import os
import shutil

from scripts.game_structure.game_essentials import Game


_tmp = os.listdir('tests/testSaves')
num_example_saves = 0
for i in _tmp:
    if i.startswith('save'):
        num_example_saves += 1


@unittest.skipIf(num_example_saves == 0, "No example saves found. Run 'git submodule update --init --recursive' to download example saves")
class LoadSave(unittest.TestCase):

    def setUp(self):
        if os.path.exists('saves'):
            shutil.move('saves', 'saves_backup')

    def tearDown(self):
        if os.path.exists('saves'):
            shutil.rmtree('saves')
        if os.path.exists('saves_backup'):
            shutil.move('saves_backup', 'saves')

    def old_implimentation(self):
        with open('saves/clanlist.txt', 'r') as read_file:
            clan_list = read_file.read()
            if_clans = len(clan_list)
        if if_clans > 0:
            clan_list = clan_list.split('\n')
            clan_list = [i.strip() for i in clan_list if i]  # Remove empty and whitespace
            return clan_list
        else:
            return None
        
    def new_implimentation(self):
        return Game().read_clans()
    
    def example_save(self, id):
        if os.path.exists('saves'):
            shutil.rmtree('saves')

        #copy tests/testSaves/save<id> to saves
        shutil.copytree('tests/testSaves/save' + str(id), 'saves')
    

    def test_check_current_clan(self):
        for i in range(1, num_example_saves + 1):
            with self.subTest(i=i):
                print("Checking current clan for save " + str(i))
                self.example_save(i)
                fileList = os.listdir('saves')
                if 'currentclan.txt' in fileList:
                    self.skipTest("Save " + str(i) + " already migrated")
                old_out = self.old_implimentation()
                self.example_save(i)
                new_out = self.new_implimentation()
                

                self.assertEqual(old_out[0], new_out[0], "Current clan not saved correctly for save " + str(i))
    
    
    
    def test_check_clan_list(self):

        for i in range(1, num_example_saves + 1):
            with self.subTest(i=i):
                print("Checking clan list for save " + str(i))
                self.example_save(i)
                fileList = os.listdir('saves')
                if 'currentclan.txt' in fileList:
                    self.skipTest("Save " + str(i) + " already migrated")
                old_out = self.old_implimentation().sort()
                self.example_save(i)
                new_out = self.new_implimentation().sort()

                self.assertEqual(old_out, new_out, "Clan list not saved correctly for save " + str(i))

@unittest.skipIf(num_example_saves == 0, "No example saves found. Run 'git submodule update --init --recursive' to download example saves")
class MigrateSave(unittest.TestCase):
    def setUp(self):
        if os.path.exists('saves'):
            shutil.move('saves', 'saves_backup')

    def tearDown(self):
        if os.path.exists('saves'):
            shutil.rmtree('saves')
        if os.path.exists('saves_backup'):
            shutil.move('saves_backup', 'saves')

    def example_save(self, id):
        if os.path.exists('saves'):
            shutil.rmtree('saves')

        #copy tests/testSaves/save<id> to saves
        shutil.copytree('tests/testSaves/save' + str(id), 'saves')

    def test_migrate_save_onread(self):
        
        for i in range(1, num_example_saves + 1):
            with self.subTest(i=i):
                print("Checking migration for save " + str(i))
                self.example_save(i)
                fileList = os.listdir('saves')
                if 'currentclan.txt' in fileList:
                    self.skipTest("Save " + str(i) + " already migrated")
                
                with open('saves/clanlist.txt', 'r') as read_file:
                    clan_name = read_file.read().strip().splitlines()[0]

                Game().read_clans() # the load save function should migrate the save

                fileList = os.listdir('saves')
                self.assertIn('currentclan.txt', fileList, "Save " + str(i) + " not migrated")

                with open('saves/currentclan.txt', 'r') as read_file:
                    curclan = read_file.read().strip()

                self.assertEqual(curclan, clan_name, "Save " + str(i) + " not migrated correctly")
                self.assertNotIn('clanlist.txt', fileList, "Save " + str(i) + " not migrated correctly")