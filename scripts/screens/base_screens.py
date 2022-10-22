from scripts.utility import update_sprite
from scripts.cat.cats import cat_class
from scripts.game_structure.buttons import buttons
from scripts.game_structure.game_essentials import *
from scripts.clan import map_available

class Screens(object):
    game_screen = screen
    game_x = screen_x
    game_y = screen_y
    last_screen = ''

    def __init__(self, name=None):
        self.name = name
        if name is not None:
            game.all_screens[name] = self

    def fill(self, tuple):
        pygame.Surface.fill(color=tuple)

    def on_use(self):
        """Runs every frame this screen is used."""
        pass

    def screen_switches(self):
        """Runs when this screen is switched to."""
        pass


# CAT PROFILES
def cat_profiles():
    game.choose_cats.clear()
    game.cat_buttons.clear()
    for x in game.clan.clan_cats:
        game.choose_cats[x] = cat_class.all_cats[x]
        update_sprite(game.choose_cats[x])


def draw_menu_buttons():
    buttons.draw_button((260, 70),
                        text='EVENTS',
                        cur_screen='events screen',
                        hotkey=[2])
    buttons.draw_button((340, 70),
                        text='CLAN',
                        cur_screen='clan screen',
                        hotkey=[3])
    buttons.draw_button((400, 70),
                        text='STARCLAN',
                        cur_screen='starclan screen',
                        hotkey=[4])
    buttons.draw_button((500, 70),
                        text='PATROL',
                        cur_screen='patrol screen',
                        hotkey=[5])
    buttons.draw_button((50, 50),
                        text='< Back to Main Menu',
                        cur_screen='start screen',
                        hotkey=[0])
    buttons.draw_button((-70, 50),
                        text='List Cats',
                        cur_screen='list screen',
                        hotkey=[6])
    buttons.draw_button((-70, 80),
                        text='Allegiances',
                        cur_screen='allegiances screen',
                        hotkey=[7])
    buttons.draw_button((-70, 110),
                        text='Map',
                        cur_screen='map screen',
                        available=map_available,
                        hotkey=[8])
    buttons.draw_button((50, 80),
                        text='Stats',
                        cur_screen='stats screen',
                        hotkey=[1])