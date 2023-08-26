# pylint: disable=line-too-long
import logging
import os
import platform
import subprocess
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.utility import get_text_box_theme, scale  # pylint: disable=redefined-builtin
from .Screens import Screens


class StatsScreen(Screens):
    """
    TODO: DOCS
    """

    def screen_switches(self):
        """
        TODO: DOCS
        """

        self.set_disabled_menu_buttons(["stats"])
        self.show_menu_buttons()
        self.update_heading_text(f'{game.clan.name}Clan')

        # Determine stats
        living_num = 0
        warriors_num = 0
        app_num = 0
        kit_num = 0
        elder_num = 0
        starclan_num = 0
        medcat_num = 0
        other_num = 0
        for cat in Cat.all_cats.values():
            if not cat.dead and not (cat.outside or cat.exiled):
                living_num += 1
                if cat.status == 'warrior':
                    warriors_num += 1
                elif cat.status in ['apprentice', 'medicine cat apprentice']:
                    app_num += 1
                elif cat.status in ['kitten', 'newborn']:
                    kit_num += 1
                elif cat.status == 'elder':
                    elder_num += 1
                elif cat.status == 'medicine cat':
                    medcat_num += 1
            elif (cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']
                  or cat.outside) and not cat.dead:
                other_num += 1
            else:
                starclan_num += 1

        stats_text = f"Number of Living Cats: {living_num}\n\n" + \
                     f"Number of Med. Cats: {medcat_num}\n\n" + \
                     f"Number of Warriors: {warriors_num}\n\n" + \
                     f"Number of Apprentices: {app_num}\n\n" + \
                     f"Number of Kits: {kit_num}\n\n" + \
                     f"Number of Elders: {elder_num}\n\n" + \
                     f"Number of Cats Outside the Clans: {other_num}\n\n" + \
                     f"Number of Dead Cats: {starclan_num}"

        self.stats_box = pygame_gui.elements.UITextBox(
            stats_text,
            scale(pygame.Rect((200, 300), (1200, 1000))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizcenter"))

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.stats_box.kill()
        del self.stats_box

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        """
        TODO: DOCS
        """
