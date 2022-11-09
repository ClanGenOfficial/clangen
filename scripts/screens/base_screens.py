from scripts.utility import update_sprite
from scripts.cat.cats import Cat
from scripts.game_structure.buttons import Button, buttons
from scripts.game_structure.game_essentials import *
from scripts.clan import map_available
from scripts.game_structure.text import *
import scripts.game_structure.image_cache as image_cache


class Screens():
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
        game.choose_cats[x] = Cat.all_cats[x]
        update_sprite(game.choose_cats[x])


# ---------------------------------------------------------------------------- #
#                               menu buttons                                   #
# ---------------------------------------------------------------------------- #
def draw_menu_buttons():
    buttons.draw_image_button((246, 60),
                              button_name='events',
                              text='EVENTS',
                              cur_screen='events screen',
                              size=(82, 30),
                              hotkey=[2])
    buttons.draw_image_button((328, 60),
                              button_name='clan',
                              text='CLAN',
                              cur_screen='clan screen',
                              size=(58, 30),
                              hotkey=[3])
    buttons.draw_image_button((386, 60),
                              button_name='starclan',
                              text='STARCLAN',
                              cur_screen='starclan screen',
                              size=(88, 30),
                              hotkey=[4])

    buttons.draw_image_button((474, 60),
                              button_name='patrol',
                              text='PATROL',
                              cur_screen='patrol screen',
                              size=(80, 30),
                              hotkey=[5])
    buttons.draw_image_button((25, 25),
                              button_name='main_menu',
                              text='< Back to Main Menu',
                              cur_screen='start screen',
                              size=(153, 30),
                              hotkey=[0])
    buttons.draw_image_button((676, 60),
                              button_name='list_cats',
                              text='List Cats',
                              cur_screen='list screen',
                              size=(99, 30),
                              hotkey=[6])
    buttons.draw_image_button((657, 25),
                              button_name='allegiances',
                              text='Allegiances',
                              cur_screen='allegiances screen',
                              size=(118, 30),
                              hotkey=[7])
    buttons.draw_image_button((25, 60),
                              button_name='stats',
                              text='Stats',
                              cur_screen='stats screen',
                              size=(81, 30),
                              hotkey=[1])

    #buttons.draw_button((-70, 110),
    #                    text='Map',
    #                    cur_screen='map screen',
    #                    available=map_available,
    #                    hotkey=[8])



# ---------------------------------------------------------------------------- #
#                      draw clan name with bg frame                            #
# ---------------------------------------------------------------------------- #
def draw_clan_name():
    clan_name_bg = pygame.transform.scale(
        image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))
    screen.blit(clan_name_bg, (310, 25))

    verdana_big_light.text(f'{game.clan.name}Clan', ('center', 32))


# ---------------------------------------------------------------------------- #
#                    next and previous cat buttons                             #
# ---------------------------------------------------------------------------- #
def draw_next_prev_cat_buttons(the_cat):
    is_instructor = False
    if the_cat.dead and game.clan.instructor.ID == the_cat.ID:
        is_instructor = True

    previous_cat = 0
    next_cat = 0
    if the_cat.dead and not is_instructor and not the_cat.df:
        previous_cat = game.clan.instructor.ID

    if is_instructor:
        next_cat = 1

    for check_cat in Cat.all_cats:
        if Cat.all_cats[check_cat].ID == the_cat.ID:
            next_cat = 1

        if game.switches['apprentice'] is not None:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].exiled and Cat.all_cats[check_cat].mentor is not None and Cat.all_cats[
                    check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].exiled and Cat.all_cats[check_cat].mentor is not None and Cat.all_cats[
                    check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

        elif game.switches['choosing_mate'] is True:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].exiled and Cat.all_cats[
                                    check_cat].status not in ['apprentice', 'medicine cat apprentice', 'kitten'] and Cat.all_cats[
                    check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].exiled and Cat.all_cats[
                                    check_cat].status not in ['apprentice', 'medicine cat apprentice', 'kitten'] and Cat.all_cats[
                    check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

        else:
            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].exiled and Cat.all_cats[
                    check_cat].df == the_cat.df:
                previous_cat = Cat.all_cats[check_cat].ID

            elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and Cat.all_cats[
                        check_cat].dead == the_cat.dead and Cat.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                check_cat].exiled and Cat.all_cats[
                    check_cat].df == the_cat.df:
                next_cat = Cat.all_cats[check_cat].ID

            elif int(next_cat) > 1:
                break

    if next_cat == 1:
        next_cat = 0

# ---------------------------------------------------------------------------- #
#                               the buttons                                    #
# ---------------------------------------------------------------------------- #
    if next_cat != 0:
        buttons.draw_image_button((622, 25),
                                  button_name='next_cat',
                                  text='Next Cat',
                                  cat=next_cat,
                                  size=(153, 30),
                                  hotkey=[21],
                                  show_details=False,
                                  chosen_cat=None,
                                  mate=None
                                  )
    else:
        buttons.draw_image_button((622, 25),
                                  button_name='next_cat',
                                  text='Next Cat',
                                  cat=next_cat,
                                  size=(153, 30),
                                  hotkey=[21],
                                  show_details=False,
                                  available=False
                                  )
    if previous_cat != 0:
        buttons.draw_image_button((25, 25),
                                  button_name='previous_cat',
                                  text='Previous Cat',
                                  cat=previous_cat,
                                  size=(153, 30),
                                  hotkey=[23],
                                  show_details=False,
                                  mate=None
                                  )
    else:
        buttons.draw_image_button((25, 25),
                                  button_name='previous_cat',
                                  text='Previous Cat',
                                  cat=previous_cat,
                                  size=(153, 30),
                                  hotkey=[23],
                                  available=False
                                  )

