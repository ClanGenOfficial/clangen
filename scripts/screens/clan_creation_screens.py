import pygame
from random import choice, randrange

from .base_screens import Screens

from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.utility import draw, draw_big, draw_large
from scripts.clan import Clan, map_available
from scripts.cat.cats import create_example_cats
from scripts.cat.names import names
from scripts.cat.sprites import tiles
import scripts.game_structure.image_cache as image_cache
#from scripts.world import World, save_map
map_available = False

def roll_button(self, x_value, y_value, arg0):
    buttons.draw_image_button((x_value, y_value),
                              button_name='random_dice',
                              re_roll=True,
                              size=(34, 34),
                              available=arg0)
def draw_main_menu(self):
    verdana_small.text(
        'Note: going back to main menu resets the generated cats.',
        (25, 25))
    buttons.draw_image_button((25, 50),
                              button_name='main_menu',
                              text='<< Back to Main Menu',
                              cur_screen='start screen',
                              naming_text='',
                              set_game_mode=False,
                              size=(153, 30)
                              )


class MakeClanScreen(Screens):

    # UI images
    clan_frame_img = pygame.image.load(
        'resources/images/pick_clan_screen/clan_name_frame.png').convert_alpha()
    name_clan_img = pygame.image.load(
        'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha()
    leader_img = pygame.image.load(
        'resources/images/pick_clan_screen/leader_light.png').convert_alpha()
    deputy_img = pygame.image.load(
        'resources/images/pick_clan_screen/deputy_light.png').convert_alpha()
    medic_img = pygame.image.load(
        'resources/images/pick_clan_screen/med_light.png').convert_alpha()
    clan_img = pygame.image.load(
        'resources/images/pick_clan_screen/clan_light.png').convert_alpha()
    bg_preview_border = pygame.transform.scale(
        pygame.image.load("resources/images/bg_preview_border.png").convert_alpha(), (466, 416))
    def draw_clan_name(self):
        # draw name and frame
        screen.blit(MakeClanScreen.clan_frame_img, (292, 100))
        verdana_light.text(game.switches['clan_name'] + 'Clan', ('center', 115))

    def game_mode(self):
        # ---------------------------------------------------------------------------- #
        #                                    layout                                    #
        # ---------------------------------------------------------------------------- #
        draw_main_menu(self)
        text_box = image_cache.load_image(
            'resources/images/game_mode_text_box.png').convert_alpha()
        screen.blit(text_box, (325, 130))

        y_value = 240

        # ---------------------------------------------------------------------------- #
        #                              mode selection                                  #
        # ---------------------------------------------------------------------------- #
        if game.switches['game_mode'] is None:
            game.switches['game_mode'] = 'classic'

        buttons.draw_image_button((109, y_value),
                                  button_name='classic_mode',
                                  size=(132, 30),
                                  game_mode='classic',
                                  )
        y_value += 80
        buttons.draw_image_button((94, y_value),
                                  button_name='expanded_mode',
                                  size=(162, 34),
                                  game_mode='expanded',
                                  )
        y_value += 80
        buttons.draw_image_button((100, y_value),
                                  button_name='cruel_season',
                                  size=(150, 30),
                                  game_mode='cruel season',
                                  )

        # ---------------------------------------------------------------------------- #
        #                                 classic text                                 #
        # ---------------------------------------------------------------------------- #
        if game.switches['game_mode'] == 'classic':
            y_value = 136
            x_value = 345
            verdana_big_light.text("Classic Mode", (465, y_value))
            y_value += 50

            verdana_dark.blit_text("Sit back and relax. \n"
                                   "This mode is Clan Generator at it's most basic. The player is not expected to "
                                   "manage the minutia of clan life. Perfect for a relaxing game session or for "
                                   "focusing on storytelling. \nWith this mode you are the eye in the sky, "
                                   "watching the clan as their story unfolds.",
                                   (x_value, y_value),
                                   line_break=40,
                                   x_limit=700
                                   )

        # ---------------------------------------------------------------------------- #
        #                                expanded text                                 #
        # ---------------------------------------------------------------------------- #
        if game.switches['game_mode'] == 'expanded':
            y_value = 136
            x_value = 345

            verdana_big_light.text("Expanded Mode", (453, y_value))
            y_value += 50

            verdana_dark.blit_text("A more hands-on experience. \nThis mode has everything in Classic Mode as well as "
                                   "more management focused features. \nNew features include: \n"
                                   "----no new features as of yet---- \nWith this mode you'll be making the important "
                                   "clan-life decisions.",
                                   (x_value, y_value),
                                   line_break=40,
                                   x_limit=700)

        # ---------------------------------------------------------------------------- #
        #                              cruel season text                               #
        # ---------------------------------------------------------------------------- #
        if game.switches['game_mode'] == 'cruel season':
            y_value = 136
            x_value = 345

            verdana_big_light.text("Cruel Season", (464, y_value))
            y_value += 50

            verdana_dark.blit_text("This mode has all the features of Expanded mode, but is significantly "
                                   "more difficult.  If you'd like a challenge, then this mode is for you. \n \n"
                                   "---this mode is currently unavailable--- \n \nYou heard the warnings... "
                                   "a Cruel Season is coming. \nWill you survive?",
                                   (x_value, y_value),
                                   line_break=40,
                                   x_limit=700)

        buttons.draw_image_button((253, 620),
                                  button_name='last_step',
                                  text='< Last step',
                                  hotkey=[0],
                                  size=(147, 30),
                                  available=False
                                  )

        # ---------------------------------------------------------------------------- #
        #                             next and prev step                               #
        # ---------------------------------------------------------------------------- #
        if game.switches['game_mode'] != 'cruel season':
            buttons.draw_image_button((400, 620),
                                      button_name='next_step',
                                      text='Next Step',
                                      set_game_mode=True,
                                      available=True,
                                      size=(147, 30)
                                      )
        else:
            buttons.draw_image_button((400, 620),
                                      button_name='next_step',
                                      text='Next Step',
                                      set_game_mode=True,
                                      available=False,
                                      size=(147, 30)
                                      )

        verdana.text("Your clan's game mode is permanent and cannot be changed after clan creation.", ('center', 581))


    def first_phase(self):
        # layout
        draw_main_menu(self)

        screen.blit(MakeClanScreen.name_clan_img, (0, 0))

        # color and placement of user input text
        self.game_screen.blit(game.naming_box, (265, 600))
        verdana_dark.text(game.switches['naming_text'], (265, 600))

        # choose random prefix
        verdana_light.text('-Clan', (410, 600))

        buttons.draw_image_button((222, 593),
                                  button_name='random_dice',
                                  text='Randomize',
                                  naming_text=choice(names.normal_prefixes),
                                  size=(34, 34),
                                  hotkey=[1]
                                  )
        # reset clan name
        buttons.draw_image_button((455, 595),
                                  button_name='reset_name',
                                  text='Reset Name',
                                  naming_text='',
                                  size=(134, 30),
                                  hotkey=[2]
                                  )

        # ---------------------------------------------------------------------------- #
        #                             next and prev step                               #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((253, 635),
                                  button_name='last_step',
                                  text='< Last step',
                                  set_game_mode=False,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )

        if game.switches['naming_text'] != '':
            buttons.draw_image_button((400, 635),
                                      button_name='next_step',
                                      text='Next Step',
                                      clan_name=game.switches['naming_text'],
                                      available=True,
                                      size=(147, 30)
                                      )
        else:
            buttons.draw_image_button((400, 635),
                                      button_name='next_step',
                                      text='Next Step',
                                      clan_name=game.switches['naming_text'],
                                      available=False,
                                      size=(147, 30)
                                      )

    def second_phase(self):
        game.switches['naming_text'] = ''

        self.draw_clan_name()

        draw_main_menu(self)

        screen.blit(MakeClanScreen.leader_img, (0, 414))

        if len(game.switches['clan_list']) >= 3:
            roll_button(self, 83, 440, True)

        else:
            if game.switches['roll_count'] == 0:
                x_pos = 155
                y_pos = 235
                roll_button(self, x_pos, y_pos, True)
                y_pos += 40
                roll_button(self, x_pos, y_pos, True)
                y_pos += 40
                roll_button(self, x_pos, y_pos, True)
                y_pos += 40

            if game.switches['roll_count'] == 1:
                x_pos = 155
                y_pos = 235
                roll_button(self, x_pos, y_pos, True)
                y_pos += 40
                roll_button(self, x_pos, y_pos, True)
                y_pos += 40
                roll_button(self, x_pos, y_pos, False)
                y_pos += 40

            if game.switches['roll_count'] == 2:
                x_pos = 155
                y_pos = 235
                roll_button(self, x_pos, y_pos, True)
                y_pos += 40
                roll_button(self, x_pos, y_pos, False)
                y_pos += 40
                roll_button(self, x_pos, y_pos, False)
                y_pos += 40

            if game.switches['roll_count'] == 3:
                x_pos = 155
                y_pos = 235
                roll_button(self, x_pos, y_pos, False)
                y_pos += 40
                roll_button(self, x_pos, y_pos, False)
                y_pos += 40
                roll_button(self, x_pos, y_pos, False)
                y_pos += 40

        if game.switches['re_roll'] is True:
            create_example_cats()
            game.switches['roll_count'] += 1
            game.switches['re_roll'] = False

        # draw cats to choose from
        for u in range(6):
            buttons.draw_button((50, 130 + 50 * u),
                                image=game.choose_cats[u].sprite,
                                cat=u,
                                hotkey=[1, u + 10])
        for u in range(6, 12):
            buttons.draw_button((100, 130 + 50 * (u - 6)),
                                image=game.choose_cats[u].sprite,
                                cat=u,
                                hotkey=[2, u + 4])

        # draw clicked cat
        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0:
            chosen_cat = game.choose_cats[game.switches['cat']]
            draw_large(chosen_cat, (270, 200))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana.text(str(game.choose_cats[game.switches['cat']].name),
                             ('center', 175))
            else:
                verdana.text(
                    str(game.choose_cats[game.switches['cat']].name) +
                    ' --> ' +
                    game.choose_cats[game.switches['cat']].name.prefix +
                    'star', ('center', 175))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (440, 260))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (440, 275))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (440, 290))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become leader.', ('center', 360))
            else:
                buttons.draw_image_button((234, 348),
                                          button_name='grant_lives',
                                          text='Grant this cat their nine lives',
                                          leader=game.switches['cat'],
                                          size=(332, 52),
                                          hotkey=[1]
                                          )

        # ---------------------------------------------------------------------------- #
        #                             next and prev step                               #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((253, 400),
                                  button_name='last_step',
                                  text='< Last step',
                                  clan_name='',
                                  cat=None,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )

        buttons.draw_image_button((400, 400),
                                  button_name='next_step',
                                  text='Next Step',
                                  clan_name='',
                                  available=False,
                                  size=(147, 30)
                                  )

    def third_phase(self):
        self.draw_clan_name()
        draw_main_menu(self)

        screen.blit(MakeClanScreen.deputy_img, (0, 414))

        for u in range(6):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            else:
                buttons.draw_button((50, 130 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])
        for u in range(6, 12):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            else:
                buttons.draw_button((100, 130 + 50 * (u - 6)),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[2, u + 4])

        if game.switches['cat'] is not None and 12 > game.switches[
                'cat'] >= 0 and game.switches['cat'] != game.switches['leader']:
            chosen_cat = game.choose_cats[game.switches['cat']]
            draw_large(chosen_cat,(270, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         ('center', 175))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (440, 260))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (440, 275))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (440, 290))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become deputy.', ('center', 360))
            else:
                buttons.draw_image_button((209, 348),
                                          button_name='support_leader',
                                          text='This cat will support the leader',
                                          deputy=game.switches['cat'],
                                          size=(384, 52),
                                          hotkey=[1])
        # ---------------------------------------------------------------------------- #
        #                             next and prev step                               #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((253, 400),
                                  button_name='last_step',
                                  text='< Last step',
                                  leader=None,
                                  cat=None,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )
        buttons.draw_image_button((400, 400),
                                  button_name='next_step',
                                  text='Next Step',
                                  clan_name='',
                                  available=False,
                                  size=(147, 30)
                                  )

    def fourth_phase(self):
        self.draw_clan_name()
        draw_main_menu(self)

        screen.blit(MakeClanScreen.medic_img, (0, 414))

        for u in range(6):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            else:
                buttons.draw_button((50, 130 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])

        for u in range(6, 12):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            else:
                buttons.draw_button((100, 130 + 50 * (u - 6)),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[2, u + 4])

        if game.switches['cat'] is not None and 12 > game.switches[
                'cat'] >= 0 and game.switches['cat'] != game.switches[
                    'leader'] and game.switches['cat'] != game.switches[
                        'deputy']:
            chosen_cat = game.choose_cats[game.switches['cat']]
            draw_large(chosen_cat,(270, 200))
            verdana.text(str(chosen_cat.name),
                         ('center', 175))
            verdana_small.text(
                str(chosen_cat.gender), (440, 260))
            verdana_small.text(str(chosen_cat.age),
                               (440, 275))
            verdana_small.text(
                str(chosen_cat.trait), (440, 290))
            if chosen_cat.age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become medicine cat.',
                                 ('center', 360))
            else:
                buttons.draw_image_button((252, 342),
                                          button_name='aid_clan',
                                          text='This cat will aid the clan',
                                          medicine_cat=game.switches['cat'],
                                          hotkey=[1],
                                          size=(306, 58))

        # ---------------------------------------------------------------------------- #
        #                             next and prev step                               #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((253, 400),
                                  button_name='last_step',
                                  text='< Last step',
                                  deputy=None,
                                  cat=None,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )
        buttons.draw_image_button((400, 400),
                                  button_name='next_step',
                                  text='Next Step',
                                  clan_name='',
                                  available=False,
                                  size=(147, 30)
                                  )

    def fifth_phase(self):
        self.draw_clan_name()
        draw_main_menu(self)

        screen.blit(MakeClanScreen.clan_img, (0, 414))

        for u in range(6):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            elif game.switches['medicine_cat'] == u:
                draw(game.choose_cats[u],(650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((50, 130 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])
            try:
                if u == game.switches['members'][0]:
                    draw(game.choose_cats[u],(700, 100))
                elif u == game.switches['members'][1]:
                    draw(game.choose_cats[u],(700, 150))
                elif u == game.switches['members'][2]:
                    draw(game.choose_cats[u],(700, 200))
                elif u == game.switches['members'][3]:
                    draw(game.choose_cats[u],(700, 250))
                elif u == game.switches['members'][4]:
                    draw(game.choose_cats[u],(700, 300))
                elif u == game.switches['members'][5]:
                    draw(game.choose_cats[u],(700, 350))
                elif u == game.switches['members'][6]:
                    draw(game.choose_cats[u],(700, 400))
            except IndexError:
                pass

        for u in range(6, 12):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            elif game.switches['medicine_cat'] == u:
                draw(game.choose_cats[u],(650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((100, 130 + 50 * (u - 6)),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[2, u + 4])
            try:
                if u == game.switches['members'][0]:
                    draw(game.choose_cats[u],(700, 100))
                elif u == game.switches['members'][1]:
                    draw(game.choose_cats[u],(700, 150))
                elif u == game.switches['members'][2]:
                    draw(game.choose_cats[u],(700, 200))
                elif u == game.switches['members'][3]:
                    draw(game.choose_cats[u],(700, 250))
                elif u == game.switches['members'][4]:
                    draw(game.choose_cats[u],(700, 300))
                elif u == game.switches['members'][5]:
                    draw(game.choose_cats[u],(700, 350))
                elif u == game.switches['members'][6]:
                    draw(game.choose_cats[u],(700, 400))
            except IndexError:
                pass

        if 12 > game.switches['cat'] >= 0 and game.switches['cat'] not in [
                game.switches['leader'], game.switches['deputy'],
                game.switches['medicine_cat']
        ] and game.switches['cat'] not in game.switches['members']:
            chosen_cat = game.choose_cats[game.switches['cat']]
            draw_large(chosen_cat, (270, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         ('center', 175))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (440, 260))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (440, 275))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (440, 290))
            if len(game.switches['members']) < 7:
                buttons.draw_image_button((353, 360),
                                          button_name='recruit',
                                          text='Recruit',
                                          members=game.switches['cat'],
                                          add=True,
                                          size=(95, 30),
                                          hotkey=[1])



        # Would be nice to make this button remove the last added member rather than all the members
        buttons.draw_image_button((253, 400),
                                  button_name='last_step',
                                  text='< Last step',
                                  medicine_cat=None,
                                  members=[],
                                  cat=None,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )

        if 0 == len(game.switches['members']):
            clan_none_img = image_cache.load_image(
                'resources/images/pick_clan_screen/clan_none_light.png').convert_alpha()
            screen.blit(clan_none_img, (0, 414))
        elif 1 == len(game.switches['members']):
            clan_one_img = image_cache.load_image(
                'resources/images/pick_clan_screen/clan_one_light.png').convert_alpha()
            screen.blit(clan_one_img, (0, 414))
        elif 2 == len(game.switches['members']):
            clan_two_img = image_cache.load_image(
                'resources/images/pick_clan_screen/clan_two_light.png').convert_alpha()
            screen.blit(clan_two_img, (0, 414))
        elif 3 == len(game.switches['members']):
            clan_three_img = image_cache.load_image(
                'resources/images/pick_clan_screen/clan_three_light.png').convert_alpha()
            screen.blit(clan_three_img, (0, 414))
        elif 3 < len(game.switches['members']) < 7:
            clan_four_img = image_cache.load_image(
                'resources/images/pick_clan_screen/clan_four_light.png').convert_alpha()
            screen.blit(clan_four_img, (0, 414))
        elif 7 == len(game.switches['members']):
            clan_full_img = image_cache.load_image(
                'resources/images/pick_clan_screen/clan_full_light.png').convert_alpha()
            screen.blit(clan_full_img, (0, 414))


        if 3 < len(game.switches['members']) < 8:
            buttons.draw_image_button((400, 400),
                                      button_name='next_step',
                                      text='Next Step',
                                      choosing_camp=True,
                                      biome='forest',
                                      camp_bg='camp1',
                                      hotkey=[2],
                                      size=(147, 30)
                                      )
        else:
            buttons.draw_image_button((400, 400),
                                      button_name='next_step',
                                      text='Next Step',
                                      available=False,
                                      size=(147, 30),
                                      hotkey=[2]
                                      )

    def sixth_phase(self):
        if map_available:
            for y in range(44):
                for x in range(40):
                    noise_value = self.world.check_noise_tile(x, y)
                    if noise_value > 0.1:
                        #buttons.draw_maptile_button((x*TILESIZE,y*TILESIZE),image=(pygame.transform.scale(terrain.images[1],(TILESIZE,TILESIZE))))
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain1'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Desert", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'low', 'low', 'medium', 'medium',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium', 'high']),
                            'Prey Levels: ' +
                            choice(['none', 'low', 'medium']),
                            'Plant Cover: ' +
                            choice(['none', 'low', 'medium'])
                        ]
                    elif noise_value < -0.015:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain3'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Forest", "Unclaimed",
                            'Twoleg Activity: ' + choice(
                                ['none', 'low', 'low', 'medium', 'high']),
                            'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium']),
                            'Prey Levels: ' +
                            choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['low', 'medium', 'high'])
                        ]
                    else:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain0'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Plains", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'low', 'medium', 'medium', 'high',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium', 'high']),
                            'Prey Levels: ' +
                            choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['low', 'medium', 'high'])
                        ]
            for y in range(44):
                for x in range(40):
                    height = self.world.check_heighttile(x, y)
                    if height < 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif x == 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif x == 39:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif y == 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif y == 43:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + choice(['none']),
                            'Thunderpath Traffic: ' + choice(['none']),
                            'Prey Levels: ' + choice(['none']),
                            'Plant Cover: ' + choice(['none'])
                        ]
                    elif height < 0.03:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain6'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Beach", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'low', 'medium', 'medium', 'high',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            choice(['none', 'low', 'medium']),
                            'Prey Levels: ' +
                            choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['none', 'low', 'medium'])
                        ]
                    elif height > 0.35:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain5'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Mountainous", "Unclaimed",
                            'Twoleg Activity: ' + choice([
                                'none', 'none', 'low', 'low', 'medium', 'high'
                            ]), 'Thunderpath Traffic: ' + choice([
                                'none', 'none', 'low', 'low', 'medium',
                                'medium', 'high'
                            ]), 'Prey Levels: ' +
                            choice(['none', 'low', 'medium', 'high']),
                            'Plant Cover: ' +
                            choice(['none', 'low', 'medium', 'high'])
                        ]
                    if (x, y) == game.switches['map_selection']:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo0'],
                                                (16, 16)),
                                            camp_site=(x, y))
            verdana_big.text('Map', (-16, 50))
            verdana.text(
                str(game.map_info[game.switches['map_selection']][0]) + ", " +
                str(game.map_info[game.switches['map_selection']][1]),
                (-16, 100))
            verdana.text(str(game.map_info[game.switches['map_selection']][2]),
                         (-16, 150))
            verdana.text(str(game.map_info[game.switches['map_selection']][3]),
                         (-16, 200))
            verdana.text(str(game.switches['camp_site']), (-16, 250))

            if game.map_info[game.switches['map_selection']][3] == 'Unclaimed':

                # ensures a camp bg is chosen
                random_camp_options = ['camp1', 'camp2']
                random_camp = choice(random_camp_options)

                buttons.draw_button(
                    (-16, 300),
                    text='Done',
                    choosing_camp=False,
                    biome=game.map_info[game.switches['map_selection']][2],
                    world_seed=self.worldseed,
                    camp_bg = random_camp,
                    cur_screen='clan created screen')

            else:
                buttons.draw_button((-16, 300),
                                    text='Done',
                                    available=False)
        else:
            self.choose_camp()

    def choose_camp(self):
        # MAIN AND BACK BUTTONS
        draw_main_menu(self)

        buttons.draw_image_button((253, 645),
                                  button_name='last_step',
                                  text='< Last step',
                                  choosing_camp=False,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )

        # BIOME BUTTONS
        buttons.draw_image_button((196, 100),
                                  button_name='forest',
                                  text='Forest',
                                  biome='Forest',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Forest',
                                  size=(100, 46),
                                  hotkey=[1])
        buttons.draw_image_button((304, 100),
                                  button_name='mountain',
                                  text='Mountainous',
                                  biome='Mountainous',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Mountainous',
                                  size=(106, 46),
                                  hotkey=[2])
        buttons.draw_image_button((424, 100),
                                  button_name='plains',
                                  text='Plains',
                                  biome='Plains',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Plains',
                                  size=(88, 46),
                                  hotkey=[3])
        buttons.draw_image_button((520, 100),
                                  button_name='beach',
                                  text='Beach',
                                  biome='Beach',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Beach',
                                  size=(82, 46),
                                  hotkey=[4])

        # CHOOSING CAMP ART
        self.camp_art()
        if game.settings['backgrounds']:

            buttons.draw_image_button((400, 645),
                                      button_name='done_creation',
                                      text='Next Step',
                                      available=game.switches['camp_bg'] is not None,
                                      cur_screen='clan created screen',
                                      size=(147, 30)
                                      )

            if game.switches['biome'] == 'Forest':
                buttons.draw_image_button((95, 180),
                                          button_name='classic_camp',
                                          text='Classic',
                                          camp_bg='camp1',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp1'
                                          )
                buttons.draw_image_button((108, 215),
                                          button_name='gully_camp',
                                          text='Gully',
                                          camp_bg='camp2',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp2'
                                          )

                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (175, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (175, 170))

            elif game.switches['biome'] == 'Mountainous':
                buttons.draw_image_button((111, 180),
                                          button_name='cliff_camp',
                                          text='Cliff',
                                          camp_bg='camp1',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp1')
                buttons.draw_image_button((101, 215),
                                          button_name='cave_camp',
                                          text='Caves',
                                          camp_bg='camp2',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp2')

                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (175, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (175, 170))

            elif game.switches['biome'] == 'Plains':
                buttons.draw_image_button((64, 180),
                                          button_name='grasslands_camp',
                                          text='Grasslands',
                                          camp_bg='camp1',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp1'
                                          )
                buttons.draw_image_button((89, 215),
                                          button_name='tunnel_camp',
                                          text='Tunnels',
                                          camp_bg='camp2',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp2'
                                          )

                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (175, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (175, 170))

            elif game.switches['biome'] == 'Beach':
                buttons.draw_image_button((76, 180),
                                          button_name='tidepool_camp',
                                          text='Tidepools',
                                          camp_bg='camp1',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp1')
                buttons.draw_image_button((65, 215),
                                          button_name='tidal_cave_camp',
                                          text='Tidal Cave',
                                          camp_bg='camp2',
                                          size=(154, 30),
                                          available=game.switches['camp_bg'] != 'camp2')
                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (175, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (175, 170))

            # PREVIEW BORDER
            screen.blit(MakeClanScreen.bg_preview_border, (167, 162))

            # CHOOSE RANDOM CAMP
            random_biome_options = ['Forest', 'Mountainous', 'Plains', 'Beach']
            random_biome = choice(random_biome_options)
            random_camp_options = ['camp1', 'camp2']
            random_camp = choice(random_camp_options)
            buttons.draw_image_button((255, 595),
                                      button_name='random_bg',
                                      text='Choose Random Camp Background',
                                      biome=random_biome,
                                      camp_bg=random_camp,
                                      available=True,
                                      size=(290, 30),
                                      cur_screen='clan created screen')

        else:
            buttons.draw_image_button((400, 645),
                                      button_name='done_creation',
                                      text='Next Step',
                                      available=game.switches['biome'] is not None,
                                      cur_screen='clan created screen',
                                      size=(147, 30)
                                      )

    def camp_art(self):
        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = "newleaf"
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.switches['biome']
        if biome not in available_biome:
            biome = available_biome[0]
        biome = biome.lower()

        camp_bg_path_1 = f'{camp_bg_base_dir}/{biome}/{start_leave}_camp1_{light_dark}.png'
        camp_bg_path_2 = f'{camp_bg_base_dir}/{biome}/{start_leave}_camp2_{light_dark}.png'
        self.change_camp_art(camp_bg_path_1,camp_bg_path_2)

    def change_camp_art(self, arg0, arg1):
        self.camp1 = pygame.transform.scale(
            image_cache.load_image(arg0).convert(), (450, 400))
        self.camp2 = pygame.transform.scale(
            image_cache.load_image(arg1).convert(), (450, 400))


    def on_use(self):

        if game.switches['set_game_mode'] is False:
            self.game_mode()
        elif len(game.switches['clan_name']) == 0 and game.switches['set_game_mode'] is True:
            self.first_phase()
        elif len(game.switches['clan_name']
                 ) > 0 and game.switches['leader'] is None:
            self.second_phase()
        elif game.switches[
                'leader'] is not None and game.switches['deputy'] is None:
            Clan.leader_lives = 9
            self.third_phase()
        elif game.switches['leader'] is not None and game.switches[
                'medicine_cat'] is None:
            self.fourth_phase()
        elif game.switches['medicine_cat'] is not None and game.switches[
                'choosing_camp'] is False:
            self.fifth_phase()
        elif len(game.switches['members']) != 0:
            self.sixth_phase()
        else:
            self.first_phase()

    def screen_switches(self):
        game.switches['game_mode'] = None
        game.switches['clan_name'] = ''
        game.switches['leader'] = None
        game.switches['cat'] = None
        game.switches['medicine_cat'] = None
        game.switches['deputy'] = None
        game.switches['members'] = []
        game.switches['choosing_camp'] = False
        game.switches['roll_count'] = 0
        create_example_cats()
        self.worldseed = randrange(10000)
        #if map_available:
        #   self.world = World((44, 44), self.worldseed)

class ClanCreatedScreen(Screens):

    def on_use(self):
        # LAYOUT
        verdana.text('Your clan has been created and saved!', ('center', 50))
        draw_big(game.clan.leader,(screen_x / 2 - 50, 100))

        # buttons
        buttons.draw_image_button((349, 250),
                                  button_name='continue_small',
                                  text='Continue',
                                  cur_screen='clan screen',
                                  size=(102, 30),
                                  hotkey=[1])

    def screen_switches(self):
        game.clan = Clan(game.switches['clan_name'],
                         game.choose_cats[game.switches['leader']],
                         game.choose_cats[game.switches['deputy']],
                         game.choose_cats[game.switches['medicine_cat']],
                         game.switches['biome'], game.switches['world_seed'],
                         game.switches['camp_site'], game.switches['camp_bg'],
                         game.switches['game_mode'])
        game.clan.create_clan()
        if map_available:
            territory_claim = str(game.clan.name) + 'Clan Territory'
            otherclan_campsite = {}
            for clan in game.clan.all_clans:
                x = randrange(40)
                y = randrange(44)
                clan_camp = self.choose_other_clan_territory(x, y)
                territory_biome = str(game.map_info[clan_camp][2])
                territory_twolegs = str(game.map_info[clan_camp][4])
                territory_thunderpath = str(game.map_info[clan_camp][5])
                territory_prey = str(game.map_info[clan_camp][6])
                territory_plants = str(game.map_info[clan_camp][7])
                game.map_info[clan_camp] = [
                    clan_camp[0], clan_camp[1], territory_biome,
                    str(clan) + " Camp", territory_twolegs,
                    territory_thunderpath, territory_prey, territory_plants
                ]
                otherclan_campsite[str(clan)] = clan_camp
            for y in range(44):
                for x in range(40):
                    if (x, y) == (game.switches['camp_site'][0] - 1,
                                  game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] - 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0] + 1,
                                    game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] + 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    for clan in game.clan.all_clans:
                        if (x, y) == (otherclan_campsite[str(clan)][0] - 1,
                                      otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] - 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0] + 1,
                                        otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] + 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
            #save_map(game.map_info, game.switches['clan_name'])

    def choose_other_clan_territory(self, x, y):
        self.x = x
        self.y = y
        if game.map_info[(self.x, self.y)][3] != "Unclaimed":
            self.x = randrange(40)
            self.y = randrange(44)
            if game.map_info[(self.x, self.y)][3] == "Unclaimed":
                return self.x, self.y
            else:
                self.x = randrange(40)
                self.y = randrange(44)
                return self.x, self.y
        else:
            return self.x, self.y

