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
#from scripts.world import World, save_map
map_available = False

class MakeClanScreen(Screens):

    def first_phase(self):
        # layout
        if game.settings['dark mode']:
            name_clan_img = pygame.image.load(
                'resources/images/pick_clan_screen/name_clan.png').convert_alpha()
        else:
            name_clan_img = pygame.image.load(
                'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha()
        screen.blit(name_clan_img, (0, 0))

        self.game_screen.blit(game.naming_box, (265, 620))
        if game.settings['dark mode']:
            verdana_black.text(game.switches['naming_text'], (265, 620))
        else:
            verdana.text(game.switches['naming_text'], (265, 620))
        verdana.text('-Clan', (410, 620))
        buttons.draw_image_button((222, 613),
                                  button_name='random_dice',
                                  text='Randomize',
                                  naming_text=choice(names.normal_prefixes),
                                  size=(34, 34),
                                  hotkey=[1]
                                  )
        buttons.draw_image_button((455, 615),
                                  button_name='reset_name',
                                  text='Reset Name',
                                  naming_text='',
                                  size=(134, 30),
                                  hotkey=[2]
                                  )

        # buttons
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (25, 25))
        buttons.draw_image_button((25, 50),
                                  button_name='main_menu',
                                  text='<< Back to Main Menu',
                                  cur_screen='start screen',
                                  naming_text='',
                                  size=(153, 30)
                                  )
        buttons.draw_image_button((333, 655),
                                  button_name='name_clan',
                                  text='Name Clan',
                                  clan_name=game.switches['naming_text'],
                                  size=(134, 30),
                                  hotkey=[3]
                                  )

    def second_phase(self):
        game.switches['naming_text'] = ''
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            leader_img = pygame.image.load(
                'resources/images/pick_clan_screen/leader.png').convert_alpha()
        else:
            leader_img = pygame.image.load(
                'resources/images/pick_clan_screen/leader_light.png').convert_alpha()
        screen.blit(leader_img, (0, 414))
        for u in range(6):
            buttons.draw_button((50, 150 + 50 * u),
                                image=game.choose_cats[u].sprite,
                                cat=u,
                                hotkey=[1, u + 10])
        for u in range(6, 12):
            buttons.draw_button((100, 150 + 50 * (u - 6)),
                                image=game.choose_cats[u].sprite,
                                cat=u,
                                hotkey=[2, u + 4])

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

        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (25, 25))
        buttons.draw_image_button((25, 50),
                                  button_name='main_menu',
                                  text='<< Back to Main Menu',
                                  cur_screen='start screen',
                                  naming_text='',
                                  size=(153, 30)
                                  )

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
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            deputy_img = pygame.image.load(
                'resources/images/pick_clan_screen/deputy.png').convert_alpha()
        else:
            deputy_img = pygame.image.load(
                'resources/images/pick_clan_screen/deputy_light.png').convert_alpha()
        screen.blit(deputy_img, (0, 414))

        for u in range(6):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            else:
                buttons.draw_button((50, 150 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])
        for u in range(6, 12):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            else:
                buttons.draw_button((100, 150 + 50 * (u - 6)),
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
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (25, 25))
        buttons.draw_image_button((25, 50),
                                  button_name='main_menu',
                                  text='<< Back to Main Menu',
                                  cur_screen='start screen',
                                  naming_text='',
                                  size=(153, 30)
                                  )
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
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            medic_img = pygame.image.load(
                'resources/images/pick_clan_screen/medic.png').convert_alpha()
        else:
            medic_img = pygame.image.load(
                'resources/images/pick_clan_screen/med_light.png').convert_alpha()
        screen.blit(medic_img, (0, 414))

        for u in range(6):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            else:
                buttons.draw_button((50, 150 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])

        for u in range(6, 12):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            else:
                buttons.draw_button((100, 150 + 50 * (u - 6)),
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
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (25, 25))
        buttons.draw_image_button((25, 50),
                                  button_name='main_menu',
                                  text='<< Back to Main Menu',
                                  cur_screen='start screen',
                                  naming_text='',
                                  size=(153, 30)
                                  )
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
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            clan_img = pygame.image.load('resources/images/pick_clan_screen/clan.png').convert_alpha()
        else:
            clan_img = pygame.image.load(
                'resources/images/pick_clan_screen/clan_light.png').convert_alpha()
        screen.blit(clan_img, (0, 414))
        for u in range(6):
            if game.switches['leader'] == u:
                draw(game.choose_cats[u],(650, 200))
            elif game.switches['deputy'] == u:
                draw(game.choose_cats[u],(650, 250))
            elif game.switches['medicine_cat'] == u:
                draw(game.choose_cats[u],(650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((50, 150 + 50 * u),
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
                buttons.draw_button((100, 150 + 50 * (u - 6)),
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

        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (25, 25))
        buttons.draw_image_button((25, 50),
                                  button_name='main_menu',
                                  text='<< Back to Main Menu',
                                  cur_screen='start screen',
                                  naming_text='',
                                  size=(153, 30)
                                  )
        buttons.draw_image_button((253, 400),
                                  button_name='last_step',
                                  text='< Last step',
                                  medicine_cat=None,
                                  members=[],
                                  cat=None,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )

        if 3 < len(game.switches['members']) < 8:
            buttons.draw_image_button((400, 400),
                                      button_name='next_step',
                                      text='Next Step',
                                      choosing_camp=True,
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
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (25, 25))
        buttons.draw_image_button((25, 50),
                                  button_name='main_menu',
                                  text='<< Back to Main Menu',
                                  cur_screen='start screen',
                                  naming_text='',
                                  size=(153, 30)
                                  )
        buttons.draw_image_button((253, 650),
                                  button_name='last_step',
                                  text='< Last step',
                                  choosing_camp=False,
                                  hotkey=[0],
                                  size=(147, 30)
                                  )

        # BIOME BUTTONS
        buttons.draw_image_button((196, 90),
                                  button_name='forest',
                                  text='Forest',
                                  biome='Forest',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Forest',
                                  size=(100, 46),
                                  hotkey=[1])
        buttons.draw_image_button((304, 90),
                                  button_name='mountain',
                                  text='Mountainous',
                                  biome='Mountainous',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Mountainous',
                                  size=(106, 46),
                                  hotkey=[2])
        buttons.draw_image_button((424, 90),
                                  button_name='plains',
                                  text='Plains',
                                  biome='Plains',
                                  camp_bg='camp1',
                                  available=game.switches['biome'] != 'Plains',
                                  size=(88, 46),
                                  hotkey=[3])
        buttons.draw_image_button((520, 90),
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

            buttons.draw_image_button((400, 650),
                                      button_name='done_creation',
                                      text='Next Step',
                                      available=game.switches['camp_bg'] is not None,
                                      cur_screen='clan created screen',
                                      size=(147, 30)
                                      )

            if game.switches['biome'] == 'Forest':
                buttons.draw_button((100, 180),
                                    text='Classic',
                                    camp_bg='camp1',
                                    available=game.switches['camp_bg'] != 'camp1')
                buttons.draw_button((100, 230),
                                    text='Gully',
                                    camp_bg='camp2',
                                    available=game.switches['camp_bg'] != 'camp2')

                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (250, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (250, 170))

            elif game.switches['biome'] == 'Mountainous':
                buttons.draw_button((100, 180),
                                    text='Cliff',
                                    camp_bg='camp1',
                                    available=game.switches['camp_bg'] != 'camp1')
                buttons.draw_button((100, 230),
                                    text='Caves',
                                    camp_bg='camp2',
                                    available=game.switches['camp_bg'] != 'camp2')

                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (250, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (250, 170))

            elif game.switches['biome'] == 'Plains':
                buttons.draw_button((100, 180),
                                    text='Grasslands',
                                    camp_bg='camp1',
                                    available=game.switches['camp_bg'] != 'camp1')
                buttons.draw_button((100, 230),
                                    text='Tunnels',
                                    camp_bg='camp2',
                                    available=game.switches['camp_bg'] != 'camp2')

                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (250, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (250, 170))

            elif game.switches['biome'] == 'Beach':
                buttons.draw_button((100, 180),
                                    text='Tidepools',
                                    camp_bg='camp1',
                                    available=game.switches['camp_bg'] != 'camp1')
                buttons.draw_button((100, 230),
                                    text='Tidal Cave',
                                    camp_bg='camp2',
                                    available=game.switches['camp_bg'] != 'camp2')
                if game.switches['camp_bg'] == 'camp1':
                    screen.blit(self.camp1, (250, 170))
                elif game.switches['camp_bg'] == 'camp2':
                    screen.blit(self.camp2, (250, 170))

            # CHOOSE RANDOM CAMP
            random_biome_options = ['Forest', 'Mountainous', 'Plains', 'Beach']
            random_biome = choice(random_biome_options)
            random_camp_options = ['camp1', 'camp2']
            random_camp = choice(random_camp_options)
            buttons.draw_image_button((255, 610),
                                      button_name='random_bg',
                                      text='Choose Random Camp Background',
                                      biome=random_biome,
                                      camp_bg=random_camp,
                                      available=True,
                                      size=(290, 30),
                                      cur_screen='clan created screen')

        else:
            buttons.draw_image_button((400, 650),
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
        biome.lower()

        camp_bg_path_1 = f'{camp_bg_base_dir}/{biome}/{start_leave}_camp1_{light_dark}.png'
        camp_bg_path_2 = f'{camp_bg_base_dir}/{biome}/{start_leave}_camp2_{light_dark}.png'
        self.change_camp_art(camp_bg_path_1,camp_bg_path_2)

    def change_camp_art(self, arg0, arg1):
        self.camp1 = pygame.transform.scale(
            pygame.image.load(arg0).convert(), (450, 400))
        self.camp2 = pygame.transform.scale(
            pygame.image.load(arg1).convert(), (450, 400))

    def on_use(self):
        if len(game.switches['clan_name']) == 0:
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
        game.switches['clan_name'] = ''
        game.switches['leader'] = None
        game.switches['cat'] = None
        game.switches['medicine_cat'] = None
        game.switches['deputy'] = None
        game.switches['members'] = []
        game.switches['choosing_camp'] = False
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
        buttons.draw_button(('center', 250),
                            text='Continue',
                            cur_screen='clan screen',
                            hotkey=[1])

    def screen_switches(self):
        game.clan = Clan(game.switches['clan_name'],
                         game.choose_cats[game.switches['leader']],
                         game.choose_cats[game.switches['deputy']],
                         game.choose_cats[game.switches['medicine_cat']],
                         game.switches['biome'], game.switches['world_seed'],
                         game.switches['camp_site'], game.switches['camp_bg'])
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

