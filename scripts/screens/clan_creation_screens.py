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

        self.game_screen.blit(game.naming_box, (150, 620))
        if game.settings['dark mode']:
            verdana_black.text(game.switches['naming_text'], (155, 620))
        else:
            verdana.text(game.switches['naming_text'], (155, 620))
        verdana.text('-Clan', (290, 620))
        buttons.draw_button((350, 620),
                            text='Randomize',
                            naming_text=choice(names.normal_prefixes),
                            hotkey=[1])
        buttons.draw_button((450, 620),
                            text='Reset Name',
                            naming_text='',
                            hotkey=[2])

        # buttons
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')
        buttons.draw_button((570, 620),
                            text='Name Clan',
                            clan_name=game.switches['naming_text'],
                            hotkey=[3])

    def second_phase(self):
        game.switches['naming_text'] = ''
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            leader_img = pygame.image.load(
                'resources/images/pick_clan_screen/leader.png').convert_alpha()
        else:
            leader_img = pygame.image.load(
                'resources/images/pick_clan_screen/leader_light.png').convert_alpha()
        screen.blit(leader_img, (0, 400))
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
            draw_large(chosen_cat,(250, 200))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana.text(str(game.choose_cats[game.switches['cat']].name),
                             (420, 200))
            else:
                verdana.text(
                    str(game.choose_cats[game.switches['cat']].name) +
                    ' --> ' +
                    game.choose_cats[game.switches['cat']].name.prefix +
                    'star', (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become leader.', (420, 300))
            else:
                buttons.draw_button((420, 300),
                                    text='Grant this cat their nine lives',
                                    leader=game.switches['cat'],
                                    hotkey=[1])
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')

        buttons.draw_button((-50, 50),
                            text='< Last step',
                            clan_name='',
                            cat=None,
                            hotkey=[0])

    def third_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            deputy_img = pygame.image.load(
                'resources/images/pick_clan_screen/deputy.png').convert_alpha()
        else:
            deputy_img = pygame.image.load(
                'resources/images/pick_clan_screen/deputy_light.png').convert_alpha()
        screen.blit(deputy_img, (0, 400))

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
            draw_large(chosen_cat,(250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become deputy.', (420, 300))
            else:
                buttons.draw_button((420, 300),
                                    text='This cat will support the leader',
                                    deputy=game.switches['cat'],
                                    hotkey=[1])
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))

        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')
        buttons.draw_button((-50, 50),
                            text='< Last Step',
                            leader=None,
                            cat=None,
                            hotkey=[0])

    def fourth_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            medic_img = pygame.image.load(
                'resources/images/pick_clan_screen/medic.png').convert_alpha()
        else:
            medic_img = pygame.image.load(
                'resources/images/pick_clan_screen/med_light.png').convert_alpha()
        screen.blit(medic_img, (0, 400))

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
            draw_large(chosen_cat,(250, 200))
            verdana.text(str(chosen_cat.name),
                         (420, 200))
            verdana_small.text(
                str(chosen_cat.gender), (420, 230))
            verdana_small.text(str(chosen_cat.age),
                               (420, 245))
            verdana_small.text(
                str(chosen_cat.trait), (420, 260))
            if chosen_cat.age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become medicine cat.',
                                 (420, 300))
            else:
                buttons.draw_button((420, 300),
                                    text='This cat will aid the clan',
                                    medicine_cat=game.switches['cat'],
                                    hotkey=[1])
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')
        buttons.draw_button((-50, 50),
                            text='< Last step',
                            deputy=None,
                            cat=None,
                            hotkey=[0])

    def fifth_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            clan_img = pygame.image.load('resources/images/pick_clan_screen/clan.png').convert_alpha()
        else:
            clan_img = pygame.image.load(
                'resources/images/pick_clan_screen/clan_light.png').convert_alpha()
        screen.blit(clan_img, (0, 400))
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
            draw_large(chosen_cat,(250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if len(game.switches['members']) < 7:
                buttons.draw_button((420, 300),
                                    text='Recruit',
                                    members=game.switches['cat'],
                                    add=True,
                                    hotkey=[1])

        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))

        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')

        buttons.draw_button((-50, 50),
                            text='< Last step',
                            medicine_cat=None,
                            members=[],
                            cat=None,
                            hotkey=[0])

        if 3 < len(game.switches['members']) < 8:
            buttons.draw_button(('center', 350),
                                text='Done',
                                choosing_camp=True,
                                hotkey=[2])
        else:
            buttons.draw_button(('center', 350), text='Done', available=False)

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

            buttons.draw_button((250, 50),
                                text='Forest',
                                biome='Forest',
                                camp_bg='camp1',
                                available=game.switches['biome'] != 'Forest',
                                hotkey=[1])
            buttons.draw_button((325, 50),
                                text='Mountainous',
                                biome='Mountainous',
                                camp_bg='camp1',
                                available=game.switches['biome'] != 'Mountainous',
                                hotkey=[2])
            buttons.draw_button((450, 50),
                                text='Plains',
                                biome='Plains',
                                camp_bg='camp1',
                                available=game.switches['biome'] != 'Plains',
                                hotkey=[3])
            buttons.draw_button((525, 50),
                                text='Beach',
                                biome='Beach',
                                camp_bg='camp1',
                                available=game.switches['biome'] != 'Beach',
                                hotkey=[4])

            # CHOOSING CAMP ART

            self.camp_art()
            if game.settings['backgrounds']:

                buttons.draw_button(('center', 630),
                                    text='Done',
                                    available=game.switches['camp_bg'] is not None,
                                    cur_screen='clan created screen')

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
                        screen.blit(self.camp1, (250, 150))
                    elif game.switches['camp_bg'] == 'camp2':
                        screen.blit(self.camp2, (250, 150))

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
                        screen.blit(self.camp1, (250, 150))
                    elif game.switches['camp_bg'] == 'camp2':
                        screen.blit(self.camp2, (250, 150))

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
                        screen.blit(self.camp1, (250, 150))
                    elif game.switches['camp_bg'] == 'camp2':
                        screen.blit(self.camp2, (250, 150))

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
                        screen.blit(self.camp1, (250, 150))
                    elif game.switches['camp_bg'] == 'camp2':
                        screen.blit(self.camp2, (250, 150))

                # CHOOSE RANDOM CAMP
                random_biome_options = ['Forest', 'Mountainous', 'Plains', 'Beach']
                random_biome = choice(random_biome_options)
                random_camp_options = ['camp1', 'camp2']
                random_camp = choice(random_camp_options)
                buttons.draw_button(('center', 580),
                                    text='Choose Random Camp Background',
                                    biome=random_biome,
                                    camp_bg=random_camp,
                                    available=True,
                                    cur_screen='clan created screen')

            else:
                buttons.draw_button(('center', 600),
                                    text='Done',
                                    available=game.switches['biome'] is not None,
                                    cur_screen='clan created screen')

    def camp_art(self):
        if game.settings['dark mode']:
            if game.switches['biome'] == "Forest":
                self.change_camp_art(
                    'resources/images/camp_bg/forest/greenleaf_camp1_dark.png',
                    'resources/images/camp_bg/forest/greenleaf_camp2_dark.png')
            elif game.switches['biome'] == "Plains":
                try:
                    self.change_camp_art(
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains_dark.png',
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains2_dark.png')
                except:
                    self.change_camp_art(
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains_dark.png',
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains_dark.png')
            elif game.switches['biome'] == "Beach":
                try:
                    self.change_camp_art(
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach_dark.png',
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach2_dark.png')
                except:
                    self.change_camp_art(
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach_dark.png',
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach_dark.png')
            elif game.switches['biome'] == "Mountainous":
                try:
                    self.change_camp_art(
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain_dark.png',
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain2_dark.png')
                except:
                    self.change_camp_art(
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain_dark.png',
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain_dark.png')

            else:
                self.change_camp_art(
                    'resources/images/camp_bg/forest/greenleaf_camp1_dark.png',
                    'resources/images/camp_bg/forest/greenleaf_camp2_dark.png')

        else:
            if game.switches['biome'] == "Forest":
                self.change_camp_art(
                    'resources/images/camp_bg/forest/greenleafcamp.png',
                    'resources/images/camp_bg/forest/greenleaf_camp2.png')
            elif game.switches['biome'] == "Plains":
                try:
                    self.change_camp_art(
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains.png',
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains2.png')
                except:
                    self.change_camp_art(
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains.png',
                        'resources/images/camp_bg/plains/greenleaf_camp1_plains.png')
            elif game.switches['biome'] == "Beach":
                try:
                    self.change_camp_art(
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach.png',
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach2.png')
                except:
                    self.change_camp_art(
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach.png',
                        'resources/images/camp_bg/beach/greenleaf_camp1_beach.png')
            elif game.switches['biome'] == "Mountainous":
                try:
                    self.change_camp_art(
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain.png',
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain2.png')
                except:
                    self.change_camp_art(
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain.png',
                        'resources/images/camp_bg/mountainous/greenleaf_camp1_mountain.png')

            else:
                self.change_camp_art(
                    'resources/images/camp_bg/forest/greenleaf_camp1.png',
                    'resources/images/camp_bg/forest/greenleaf_camp2.png')

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
        else:
            self.sixth_phase()

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

