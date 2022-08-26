from .clan import *
from .events import *
from .patrols import *


# SCREENS PARENT CLASS
class Screens(object):
    game_screen = screen
    game_x = screen_x
    game_y = screen_y
    all_screens = {}
    last_screen = ''

    def __init__(self, name=None):
        self.name = name
        if name is not None:
            self.all_screens[name] = self
            game.all_screens[name] = self

    def on_use(self):
        pass

    def screen_switches(self):
        pass


# SCREEN CHILD CLASSES
class StartScreen(Screens):
    def on_use(self):
        # background
        bg = pygame.image.load("resources/menu.png")
        screen.blit(bg, (0, 0))

        # buttons
        if game.clan is not None and game.switches['error_message'] == '':
            buttons.draw_image_button((70, 310), path='continue', text='Continue >', cur_screen='clan screen')
            buttons.draw_image_button((70, 355), path='switch_clan', text='Switch Clan >', cur_screen='switch clan screen')
        elif game.clan is not None and game.switches['error_message']:
            buttons.draw_image_button((70, 310), path='continue', text='Continue >', available=False)
            buttons.draw_image_button((70, 355), path='switch_clan', text='Switch Clan >', cur_screen='switch clan screen')
        else:
            buttons.draw_image_button((70, 310), path='continue', text='Continue >', available=False)
            buttons.draw_image_button((70, 355), path='switch_clan', text='Switch Clan >', available=False)
        buttons.draw_image_button((70, 400), path='new_clan', text='Make New >', cur_screen='make clan screen')
        buttons.draw_image_button((70, 445), path='settings', text='Settings & Info >', cur_screen='settings screen')

        if game.switches['error_message']:
            buttons.draw_button((50, 50), text='There was an error loading the game:', available=False)
            buttons.draw_button((50, 80), text=game.switches['error_message'], available=False)

    def screen_switches(self):
        if game.clan is not None:
            key_copy = tuple(cat_class.all_cats.keys())
            for x in key_copy:
                if x not in game.clan.clan_cats:
                    game.clan.remove_cat(x)

        # SAVE cats
        if game.clan is not None:
            cat_class.save_cats()
            game.clan.save_clan()

        # LOAD settings
        game.load_settings()


class SwitchClanScreen(Screens):
    def on_use(self):
        verdana_big.text('Switch Clan:', ('center', 100))
        verdana.text('Note: this will close the game. When you open it next, it should have the new clan.', ('center', 150))
        game.switches['read_clans'] = True

        y_pos = 200

        for i in range(len(game.switches['clan_list'])):
            if len(game.switches['clan_list'][i]) > 1 and i < 9:
                buttons.draw_button(('center', 50 * i + y_pos), text=game.switches['clan_list'][i] + 'clan', switch_clan=game.switches['clan_list'][i])

        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen')


class SettingsScreen(Screens):
    text_size = {'0': 'small', '1': 'medium', '2': 'big'}  # How text sizes will show up on the screen
    bool = {True: 'Yes', False: 'No', None: 'None'}

    def on_use(self):
        # layout
        buttons.draw_button((310, 100), text='Settings', available=False)
        buttons.draw_button((-360, 100), text='Info', cur_screen='info screen')
        buttons.draw_button((-255, 100), text='Language', cur_screen='language screen')
        verdana.text("Change the setting of your game here.", ('center', 130))

        # Setting names
        verdana.text("Dark mode:", (100, 200))
        verdana.text("Allow couples to have kittens despite same-sex status:", (100, 230))
        verdana.text("Allow unmated cats to have offspring:", (100, 260))
        verdana.text("Enable clan page background:", (100, 290))
        verdana.text("Automatically save every five moons", (100, 320))
        verdana.text("Allow mass extinction events", (100, 350))
        verdana.text("Force cats to retire after severe injury", (100, 380))

        # Setting values
        verdana.text(self.bool[game.settings['dark mode']], (-170, 200))
        buttons.draw_button((-80, 200), text='SWITCH', setting='dark mode')
        verdana.text(self.bool[game.settings['no gendered breeding']], (-170, 230))
        buttons.draw_button((-80, 230), text='SWITCH', setting='no gendered breeding')
        verdana.text(self.bool[game.settings['no unknown fathers']], (-170, 260))
        buttons.draw_button((-80, 260), text='SWITCH', setting='no unknown fathers')
        verdana.text(self.bool[game.settings['backgrounds']], (-170, 290))
        buttons.draw_button((-80, 290), text='SWITCH', setting='backgrounds')
        verdana.text(self.bool[game.settings['autosave']], (-170, 320))
        buttons.draw_button((-80, 320), text='SWITCH', setting='autosave')
        verdana.text(self.bool[game.settings['disasters']], (-170, 350))
        buttons.draw_button((-80, 350), text='SWITCH', setting='disasters')
        verdana.text(self.bool[game.settings['retirement']], (-170, 380))
        buttons.draw_button((-80, 380), text='SWITCH', setting='retirement')

        # other buttons
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen')
        if game.settings_changed:
            buttons.draw_button(('center', -150), text='Save Settings', save_settings=True)
        else:
            buttons.draw_button(('center', -150), text='Save Settings', available=False)


class InfoScreen(Screens):
    def on_use(self):
        # layout
        buttons.draw_button((310, 100), text='Settings', cur_screen='settings screen')
        buttons.draw_button((-360, 100), text='Info', available=False)
        buttons.draw_button((-255, 100), text='Language', cur_screen='language screen')

        verdana.text("Welcome to Warrior Cats clan generator!", ('center', 140))
        verdana.text("This is fan-made generator for the Warrior Cats -book series by Erin Hunter.", ('center', 175))
        verdana.text("Create a new clan in the 'Make New' section. That clan is saved and can be", ('center', 195))
        verdana.text("revisited until you decide the overwrite it with a new one.", ('center', 215))
        verdana.text("You're free to use the characters and sprites generated in this program", ('center', 235))
        verdana.text("as you like, as long as you don't claim the sprites as your own creations.", ('center', 255))
        verdana.text("Original creator: just-some-cat.tumblr.com", ('center', 275))
        verdana.text("Fan edit made by: SableSteel", ('center', 295))

        verdana.text("Thank you for playing!!", ('center', 550))

        # other buttons
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen')

class LanguageScreen(Screens):

    def on_use(self):
        # layout
        buttons.draw_button((310, 100), text='Settings', cur_screen='settings screen')
        buttons.draw_button((-360, 100), text='Info', cur_screen='info screen')
        buttons.draw_button((-255, 100), text='Language', available='false')
        verdana.text("Choose the language of your game here:", ('center', 130))

        # Language options
        a = 200
        for language_name in game.language_list:
            buttons.draw_button(('center', a), text=language_name, language=language_name, available=language_name!=game.switches['language'])
            a += 30

        if game.switches['language']!=game.settings['language']:
            game.settings['language'] = game.switches['language']
            game.settings_changed = True
            if game.settings['language'] != 'english':
                game.switch_language()

        # other buttons
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen')
        if game.settings_changed:
            buttons.draw_button(('center', -150), text='Save Settings', save_settings=True)
        else:
            buttons.draw_button(('center', -150), text='Save Settings', available=False)

class ClanScreen(Screens):
    def on_use(self):
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text("Leader\'s Den", game.clan.cur_layout['leader den'])
        verdana.text('Medicine Cat Den', game.clan.cur_layout['medicine den'])
        verdana.text('Nursery', game.clan.cur_layout['nursery'])
        verdana.text('Clearing', game.clan.cur_layout['clearing'])
        verdana.text("Apprentices\' Den", game.clan.cur_layout['apprentice den'])
        verdana.text("Warriors\' Den", game.clan.cur_layout['warrior den'])
        verdana.text("Elders\' Den", game.clan.cur_layout['elder den'])
        for x in game.clan.clan_cats:
            if not cat_class.all_cats[x].dead and cat_class.all_cats[x].in_camp:
                buttons.draw_button(cat_class.all_cats[x].placement, image=cat_class.all_cats[x].sprite, cat=x, cur_screen='profile screen')
        draw_menu_buttons()
        buttons.draw_button(('center', -50), text='Save Clan', save_clan=True)
        pygame.draw.rect(screen, color='gray', rect=pygame.Rect(320,660,160,20))
        if game.switches['save_clan']:
            verdana_green.text('Saved!', ('center', -20))
        else:
            verdana_red.text('Remember to save!', ('center', -20))

    def screen_switches(self):
        cat_profiles()
        self.change_brightness()
        game.switches['cat'] = None
        p = game.clan.cur_layout
        game.clan.leader.placement = choice(p['leader place'])
        game.clan.medicine_cat.placement = choice(p['medicine place'])
        for x in game.clan.clan_cats:
            i = randint(0, 20)
            if cat_class.all_cats[x].status == 'apprentice':
                if i < 13:
                    cat_class.all_cats[x].placement = choice([choice(p['apprentice place']), choice(p['clearing place'])])

                elif i >= 19:
                    cat_class.all_cats[x].placement = choice(p['leader place'])
                else:
                    cat_class.all_cats[x].placement = choice([choice(p['nursery place']), choice(p['warrior place']), choice(p['elder place']), choice(p['medicine place'])])

            elif cat_class.all_cats[x].status == 'deputy':
                if i < 17:
                    cat_class.all_cats[x].placement = choice([choice(p['warrior place']), choice(p['leader place']), choice(p['clearing place'])])

                else:
                    cat_class.all_cats[x].placement = choice(
                        [choice(p['nursery place']), choice(p['leader place']), choice(p['elder place']), choice(p['medicine place']), choice(p['apprentice place'])])

            elif cat_class.all_cats[x].status == 'elder':
                cat_class.all_cats[x].placement = choice(p['elder place'])
            elif cat_class.all_cats[x].status == 'kitten':
                if i < 13:
                    cat_class.all_cats[x].placement = choice(p['nursery place'])
                elif i == 19:
                    cat_class.all_cats[x].placement = choice(p['leader place'])
                else:
                    cat_class.all_cats[x].placement = choice(
                        [choice(p['clearing place']), choice(p['warrior place']), choice(p['elder place']), choice(p['medicine place']), choice(p['apprentice place'])])

            elif cat_class.all_cats[x].status in ['medicine cat apprentice', 'medicine cat']:
                cat_class.all_cats[x].placement = choice(p['medicine place'])
            elif cat_class.all_cats[x].status == 'warrior':
                if i < 15:
                    cat_class.all_cats[x].placement = choice([choice(p['warrior place']), choice(p['clearing place'])])

                else:
                    cat_class.all_cats[x].placement = choice(
                        [choice(p['nursery place']), choice(p['leader place']), choice(p['elder place']), choice(p['medicine place']), choice(p['apprentice place'])])

    def change_brightness(self):
        if game.settings['dark mode']:
            self._extracted_from_change_brightness_3('resources/greenleafcamp_dark.png', 'resources/newleafcamp_dark.png', 'resources/leafbarecamp_dark.png',
                                                     'resources/leaffallcamp_dark.png')

        else:
            self._extracted_from_change_brightness_3('resources/greenleafcamp.png', 'resources/newleafcamp.png', 'resources/leafbarecamp.png', 'resources/leaffallcamp.png')

    # TODO Rename this here and in `change_brightness`
    def _extracted_from_change_brightness_3(self, arg0, arg1, arg2, arg3):
        self.greenleaf_bg = pygame.transform.scale(pygame.image.load(arg0), (800, 700))
        self.newleaf_bg = pygame.transform.scale(pygame.image.load(arg1), (800, 700))
        self.leafbare_bg = pygame.transform.scale(pygame.image.load(arg2), (800, 700))
        self.leaffall_bg = pygame.transform.scale(pygame.image.load(arg3), (800, 700))


class StarClanScreen(Screens):
    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text('StarClan Cat List', ('center', 100))
        dead_cats = [game.clan.instructor]
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID:
                dead_cats.append(the_cat)
        all_pages = int(ceil(len(dead_cats) / 24.0)) if len(dead_cats) > 24 else 1
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(dead_cats)):
            if x + (game.switches['list_page'] - 1) * 24 > len(dead_cats):
                game.switches['list_page'] = 1
            the_cat = dead_cats[x + (game.switches['list_page'] - 1) * 24]
            if the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y), image=the_cat.sprite, cat=the_cat.ID, cur_screen='profile screen')

                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name), (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 24 or x + (game.switches['list_page'] - 1) * 24 == len(dead_cats) - 1:
                    break
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

        draw_menu_buttons()

    def screen_switches(self):
        cat_profiles()


class MakeClanScreen(Screens):
    def first_phase(self):
        # layout
        if game.settings['dark mode']:
            name_clan_img = pygame.image.load('resources/name_clan.png')
        else:
            name_clan_img = pygame.image.load('resources/name_clan_light.png')
        screen.blit(name_clan_img, (0, 0))

        self.game_screen.blit(game.naming_box, (150, 620))
        if game.settings['dark mode']:
            verdana_black.text(game.switches['naming_text'], (155, 620))
        else:
            verdana.text(game.switches['naming_text'], (155, 620))
        verdana.text('-Clan', (290, 620))
        buttons.draw_button((350, 620), text='Randomize', naming_text=choice(names.normal_prefixes))
        buttons.draw_button((450, 620), text='Reset Name', naming_text='')

        # buttons
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((570, 620), text='Name Clan', clan_name=game.switches['naming_text'])

    def second_phase(self):
        game.switches['naming_text'] = ''
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            leader_img = pygame.image.load('resources/leader.png')
        else:
            leader_img = pygame.image.load('resources/leader_light.png')
        screen.blit(leader_img, (0, 400))
        for u in range(6):
            buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
        for u in range(6, 12):
            buttons.draw_button((100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name) + ' --> ' + game.choose_cats[game.switches['cat']].name.prefix + 'star', (420, 200))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (420, 245))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in ['kitten', 'adolescent']:
                verdana_red.text('Too young to become leader.', (420, 300))
            else:
                buttons.draw_button((420, 300), text='Grant this cat their nine lives', leader=game.switches['cat'])
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')

        buttons.draw_button((-50, 50), text='< Last step', clan_name='', cat=None)

    def third_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            deputy_img = pygame.image.load('resources/deputy.png')
        else:
            deputy_img = pygame.image.load('resources/deputy_light.png')
        screen.blit(deputy_img, (0, 400))

        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            else:
                buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            else:
                buttons.draw_button((100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0 and game.switches['cat'] != game.switches['leader']:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name), (420, 200))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (420, 245))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in ['kitten', 'adolescent']:
                verdana_red.text('Too young to become deputy.', (420, 300))
            else:
                buttons.draw_button((420, 300), text='This cat will support the leader', deputy=game.switches['cat'])
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))

        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((-50, 50), text='< Last Step', leader=None, cat=None)

    def fourth_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            medic_img = pygame.image.load('resources/medic.png')
        else:
            medic_img = pygame.image.load('resources/med_light.png')
        screen.blit(medic_img, (0, 400))

        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            else:
                buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)

        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            else:
                buttons.draw_button((100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0 and game.switches['cat'] != game.switches['leader'] and game.switches['cat'] != game.switches[
            'deputy']:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name), (420, 200))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (420, 245))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in ['kitten', 'adolescent']:
                verdana_red.text('Too young to become medicine cat.', (420, 300))
            else:
                buttons.draw_button((420, 300), text='This cat will aid the clan', medicine_cat=game.switches['cat'])
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((-50, 50), text='< Last step', deputy=None, cat=None)

    def fifth_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            clan_img = pygame.image.load('resources/clan.png')
        else:
            clan_img = pygame.image.load('resources/clan_light.png')
        screen.blit(clan_img, (0, 400))
        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            elif game.switches['medicine_cat'] == u:
                game.choose_cats[u].draw((650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
            try:
                if u == game.switches['members'][0]:
                    game.choose_cats[u].draw((700, 100))
                elif u == game.switches['members'][1]:
                    game.choose_cats[u].draw((700, 150))
                elif u == game.switches['members'][2]:
                    game.choose_cats[u].draw((700, 200))
                elif u == game.switches['members'][3]:
                    game.choose_cats[u].draw((700, 250))
                elif u == game.switches['members'][4]:
                    game.choose_cats[u].draw((700, 300))
                elif u == game.switches['members'][5]:
                    game.choose_cats[u].draw((700, 350))
                elif u == game.switches['members'][6]:
                    game.choose_cats[u].draw((700, 400))
            except IndexError:
                pass

        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            elif game.switches['medicine_cat'] == u:
                game.choose_cats[u].draw((650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)
            try:
                if u == game.switches['members'][0]:
                    game.choose_cats[u].draw((700, 100))
                elif u == game.switches['members'][1]:
                    game.choose_cats[u].draw((700, 150))
                elif u == game.switches['members'][2]:
                    game.choose_cats[u].draw((700, 200))
                elif u == game.switches['members'][3]:
                    game.choose_cats[u].draw((700, 250))
                elif u == game.switches['members'][4]:
                    game.choose_cats[u].draw((700, 300))
                elif u == game.switches['members'][5]:
                    game.choose_cats[u].draw((700, 350))
                elif u == game.switches['members'][6]:
                    game.choose_cats[u].draw((700, 400))
            except IndexError:
                pass


        if 12 > game.switches['cat'] >= 0 and game.switches['cat'] not in [game.switches['leader'], game.switches['deputy'], game.switches['medicine_cat']] and game.switches[
            'cat'] not in game.switches['members']:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name), (420, 200))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (420, 245))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if len(game.switches['members']) < 7:
                buttons.draw_button((420, 300), text='Recruit', members=game.switches['cat'], add=True)

        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))

        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')

        buttons.draw_button((-50, 50), text='< Last step', medicine_cat=None, members=[], cat=None)

        if 3 < len(game.switches['members']) < 8:
            buttons.draw_button(('center', 350), text='Done', cur_screen='clan created screen')
        else:
            buttons.draw_button(('center', 350), text='Done', available=False)

    def on_use(self):
        if len(game.switches['clan_name']) == 0:
            self.first_phase()
        elif len(game.switches['clan_name']) > 0 and game.switches['leader'] is None:
            self.second_phase()
        elif game.switches['leader'] is not None and game.switches['deputy'] is None:
            self.third_phase()
        elif game.switches['leader'] is not None and game.switches['medicine_cat'] is None:
            self.fourth_phase()
        else:
            self.fifth_phase()

        buttons.draw_button((250, 50), text='Forest', biome='Forest', available=game.switches['biome']!='Forest')
        buttons.draw_button((325, 50), text='Mountainous', biome='Mountainous', available=game.switches['biome']!='Mountainous')
        buttons.draw_button((450, 50), text='Plains', biome='Plains', available=game.switches['biome']!='Plains')
        buttons.draw_button((525, 50), text='Beach', biome='Beach', available=game.switches['biome']!='Beach')

    def screen_switches(self):
        game.switches['clan_name'] = ''
        game.switches['leader'] = None
        game.switches['cat'] = None
        game.switches['medicine_cat'] = None
        game.switches['deputy'] = None
        game.switches['members'] = []
        create_example_cats()


class ClanCreatedScreen(Screens):
    def on_use(self):
        # LAYOUT
        verdana.text('Your clan has been created and saved!', ('center', 50))
        game.clan.leader.draw_big((screen_x / 2 - 50, 100))

        # buttons
        buttons.draw_button(('center', 250), text='Continue', cur_screen='clan screen')

    def screen_switches(self):
        game.clan = Clan(game.switches['clan_name'], game.choose_cats[game.switches['leader']], game.choose_cats[game.switches['deputy']],
                         game.choose_cats[game.switches['medicine_cat']], game.switches['biome'])
        game.clan.create_clan()


class EventsScreen(Screens):
    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text('Check this page to see which events are currently happening at the clan.', ('center', 100))

        verdana.text(f'Current season: {str(game.clan.current_season)}', ('center', 130))

        verdana.text(f'Clan age: {str(game.clan.age)} moons', ('center', 160))
        if game.switches['events_left'] == 0:
            buttons.draw_button(('center', 220), text='TIMESKIP ONE MOON', timeskip=True)
            if game.switches['timeskip']:
                game.cur_events_list = []
        else:
            buttons.draw_button(('center', 220), text='TIMESKIP ONE MOON', available=False)
        events_class.one_moon()
        a = 0
        if game.cur_events_list is not None and game.cur_events_list != []:
            for x in range(min(len(game.cur_events_list), game.max_events_displayed)):
                if game.cur_events_list[x] is None:
                    continue
                if "Clan has no " in game.cur_events_list[x]:
                    verdana_red.text(game.cur_events_list[x], ('center', 260 + a * 30))
                else:
                    verdana.text(game.cur_events_list[x], ('center', 260 + a * 30))
                a += 1
        else:
            verdana.text("Nothing significant happened this moon.", ('center', 260 + a * 30))

        draw_menu_buttons()
        if len(game.cur_events_list) > game.max_events_displayed:
            buttons.draw_button((720, 250), image=game.up, arrow="UP")
            buttons.draw_button((700, 550), image=game.down, arrow="DOWN")


class ProfileScreen(Screens):
    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = cat_class.all_cats.get(game.switches['cat'], game.clan.instructor)
        # use these attributes to create differing profiles for starclan cats etc.
        is_instructor = False
        if the_cat.dead and game.clan.instructor.ID == the_cat.ID:
            is_instructor = True

        # back and next buttons on the profile page
        previous_cat = 0
        next_cat = 0

        if the_cat.dead and not is_instructor:
            previous_cat = game.clan.instructor.ID
        if is_instructor:
            next_cat = 1
        for check_cat in cat_class.all_cats:
            if cat_class.all_cats[check_cat].ID == the_cat.ID:
                next_cat = 1
            if next_cat == 0 and cat_class.all_cats[check_cat].ID != the_cat.ID and cat_class.all_cats[check_cat].dead == the_cat.dead and cat_class.all_cats[
                check_cat].ID != game.clan.instructor.ID:
                previous_cat = cat_class.all_cats[check_cat].ID
            elif next_cat == 1 and cat_class.all_cats[check_cat].ID != the_cat.ID and cat_class.all_cats[check_cat].dead == the_cat.dead and cat_class.all_cats[
                check_cat].ID != game.clan.instructor.ID:
                next_cat = cat_class.all_cats[check_cat].ID
            elif int(next_cat) > 1:
                break
        if next_cat == 1:
            next_cat = 0
        if next_cat != 0:
            buttons.draw_button((-40, 40), text='Next Cat', cat=next_cat)
        if previous_cat != 0:
            buttons.draw_button((40, 40), text='Previous Cat', cat=previous_cat)
        # Info in string
        cat_name = str(the_cat.name)  # name
        cat_thought = the_cat.thought  # thought
        if the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_instructor:
            cat_thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 150))  # NAME
        the_cat.draw_large((100, 200))  # IMAGE
        verdana.text(cat_thought, ('center', 180))  # THOUGHT / ACTION
        verdana_small.text(the_cat.gender, (300, 230 + count * 15))
        count += 1  # SEX / GENDER
        verdana_small.text(the_cat.status, (490, 230 + count2 * 15))
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is None:
                the_cat.update_mentor()
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name), (490, 230 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            if len(the_cat.apprentice) == 1:
                apps = 'apprentice: ' + str(the_cat.apprentice[0].name)
            else:
                apps = 'apprentices: '
                num = 1
                for cat in the_cat.apprentice:
                    if num % 2 == 0:
                        apps += str(cat.name) + ', '
                    else:
                        apps += str(cat.name) + ', '
                    num += 1
                apps = apps[:len(apps) - 2]
            verdana_small.text(apps, (490, 230 + count2 * 15))
            count2 += 1
        if len(the_cat.former_apprentices) != 0 and the_cat.former_apprentices[0] is not None:
            if len(the_cat.former_apprentices) == 1:
                former_apps = 'former apprentice: ' + str(the_cat.former_apprentices[0].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
            elif len(the_cat.former_apprentices) == 2:
                former_apps = 'former apprentices: ' + str(the_cat.former_apprentices[0].name) + ', ' + str(the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
            else:
                num = 1
                rows = []
                name = ''
                for cat in the_cat.former_apprentices:
                    name = name + str(cat.name) + ', '
                    if num == 2:
                        rows.append(name)
                        name = ''
                        num+=1
                    if num % 3 == 0 and name != '':
                        rows.append(name)
                        name = ''
                    num += 1
                for ind in range(len(rows)):
                    if ind == 0:
                        verdana_small.text('former apprentices: ' + rows[ind], (490, 230 + count2 * 15))
                    elif ind == len(rows) - 1:
                        verdana_small.text(rows[ind][:-2], (490, 230 + count2 * 15))
                    else:
                        verdana_small.text(rows[ind], (490, 230 + count2 * 15))
                    count2+=1
        if the_cat.age == 'kitten':
            verdana_small.text('young', (300, 230 + count * 15))
        elif the_cat.age == 'elder':
            verdana_small.text('senior', (300, 230 + count * 15))
        else:
            verdana_small.text(the_cat.age, (300, 230 + count * 15))
        count += 1  # AGE
        verdana_small.text(the_cat.trait, (490, 230 + count2 * 15))
        count2 += 1  # CHARACTER TRAIT
        verdana_small.text(the_cat.skill, (490, 230 + count2 * 15))
        count2 += 1  # SPECIAL SKILL
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(), (300, 230 + count * 15))
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(), (300, 230 + count * 15))
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length, (300, 230 + count * 15))
        count += 1  # PELT LENGTH

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (300, 230 + count * 15))
            count += 1
        elif the_cat.parent2 is None and the_cat.parent1 in the_cat.all_cats:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown', (300, 230 + count * 15))
            count += 1
        elif the_cat.parent2 is None:
            par2 = "unknown"
            par1 = "Error: Cat#" + the_cat.parent1 + " not found"
            verdana_small.text('parents: ' + par1 + ', unknown', (300, 230 + count * 15))
            count += 1
        else:
            if the_cat.parent1 in the_cat.all_cats and the_cat.parent2 in the_cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            elif the_cat.parent1 in the_cat.all_cats:
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            elif the_cat.parent2 in the_cat.all_cats:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            else:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            verdana_small.text('parents: ' + par1 + ' and ' + par2, (300, 230 + count * 15))
            count += 1

        # MOONS
        if the_cat.dead:
            verdana_small.text(str(the_cat.moons) + ' moons (in life)', (300, 230 + count * 15))
            count += 1
            verdana_small.text(str(the_cat.dead_for) + ' moons (in death)', (300, 230 + count * 15))
            count += 1
        else:
            verdana_small.text(str(the_cat.moons) + ' moons', (300, 230 + count * 15))
            count += 1

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in cat_class.all_cats:
                if cat_class.all_cats.get(the_cat.mate).dead:  # TODO: fix when mate dies mate becomes none
                    verdana_small.text('former mate: ' + str(cat_class.all_cats[the_cat.mate].name), (300, 230 + count * 15))
                else:
                    verdana_small.text('mate: ' + str(cat_class.all_cats[the_cat.mate].name), (300, 230 + count * 15))
                count += 1
            else:
                verdana_small.text('Error: mate: ' + str(the_cat.mate) + " not found", ('center', 495))

        # experience
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level), (490, 230 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level), (490, 230 + count2 * 15))
            count2 += 1

        # buttons
        buttons.draw_button((400, 400), text='Options', cur_screen='options screen')

        buttons.draw_button((325, 400), text='Back', cur_screen=game.switches['last_screen'])

    def screen_switches(self):
        cat_profiles()


class SingleEventScreen(Screens):
    def on_use(self):
        # LAYOUT
        if game.switches['event'] is not None:
            events_class.all_events[game.switches['event']].page()

        # buttons
        buttons.draw_button(('center', -150), text='Continue', cur_screen='events screen')

    def screen_switches(self):
        pass


class ViewChildrenScreen(Screens):
    def on_use(self):
        the_cat = cat_class.all_cats[game.switches['cat']]
        verdana_big.text(f'Family of {str(the_cat.name)}', ('center', 50))
        verdana.text('Parents:', ('center', 85))
        if the_cat.parent1 is None:
            verdana_small.text('Unknown', (342, 165))
        elif the_cat.parent1 in cat_class.all_cats:
            buttons.draw_button((350, 120), image=cat_class.all_cats[the_cat.parent1].sprite, cat=the_cat.parent1, cur_screen='profile screen')

            name_len = verdana.text(str(cat_class.all_cats[the_cat.parent1].name))
            verdana_small.text(str(cat_class.all_cats[the_cat.parent1].name), (375 - name_len / 2, 185))

        else:
            verdana_small.text(f'Error: cat {str(the_cat.parent1)} not found', (342, 165))
        if the_cat.parent2 is None:
            verdana_small.text('Unknown', (422, 165))
        elif the_cat.parent2 in cat_class.all_cats:
            buttons.draw_button((430, 120), image=cat_class.all_cats[the_cat.parent2].sprite, cat=the_cat.parent2, cur_screen='profile screen')

            name_len = verdana.text(str(cat_class.all_cats[the_cat.parent2].name))
            verdana_small.text(str(cat_class.all_cats[the_cat.parent2].name), (455 - name_len / 2, 185))

        else:
            verdana_small.text('Error: cat ' + str(the_cat.parent2) + ' not found', (342, 165))

        pos_x = 0
        pos_y = 20
        siblings = False
        for x in game.clan.clan_cats:
            if (cat_class.all_cats[x].parent1 in (the_cat.parent1, the_cat.parent2) or cat_class.all_cats[x].parent2 in (
                    the_cat.parent1, the_cat.parent2) and the_cat.parent2 is not None) and the_cat.ID != cat_class.all_cats[x].ID and the_cat.parent1 is not None and \
                    cat_class.all_cats[x].parent1 is not None:
                buttons.draw_button((40 + pos_x, 220 + pos_y), image=cat_class.all_cats[x].sprite, cat=cat_class.all_cats[x].ID, cur_screen='profile screen')

                name_len = verdana.text(str(cat_class.all_cats[x].name))
                verdana_small.text(str(cat_class.all_cats[x].name), (65 + pos_x - name_len / 2, 280 + pos_y))

                siblings = True
                pos_x += 80
                if pos_x > 640:
                    pos_y += 70
                    pos_x = 0
        if siblings:
            verdana.text('Siblings:', ('center', 210))
        else:
            verdana.text('This cat has no siblings.', ('center', 210))
        buttons.draw_button(('center', -100), text='Back', cur_screen='profile screen')
        pos_x = 0
        pos_y = 60
        kittens = False
        for x in game.clan.clan_cats:
            if the_cat.ID in [cat_class.all_cats[x].parent1, cat_class.all_cats[x].parent2]:
                buttons.draw_button((40 + pos_x, 370 + pos_y), image=cat_class.all_cats[x].sprite, cat=cat_class.all_cats[x].ID, cur_screen='profile screen')

                name_len = verdana.text(str(cat_class.all_cats[x].name))
                verdana_small.text(str(cat_class.all_cats[x].name), (65 + pos_x - name_len / 2, 430 + pos_y))

                kittens = True
                pos_x += 80
                if pos_x > 640:
                    pos_y += 70
                    pos_x = 0
        if kittens:
            verdana.text('Offspring:', ('center', 400))
        else:
            verdana.text('This cat has never had offspring.', ('center', 400))
        buttons.draw_button(('center', -100), text='Back', cur_screen='profile screen')

    def screen_switches(self):
        cat_profiles()


class ChooseMateScreen(Screens):
    def on_use(self):
        the_cat = cat_class.all_cats[game.switches['cat']]
        verdana_big.text(f'Choose mate for {str(the_cat.name)}', ('center', 50))
        verdana_small.text('If the cat has chosen a mate, they will stay loyal and not have kittens with anyone else,', ('center', 80))
        verdana_small.text('even if having kittens in said relationship is impossible.', ('center', 95))
        verdana_small.text('Chances of having kittens when possible is heightened though.', ('center', 110))

        the_cat.draw_large((200, 130))
        self._extracted_from_on_use_29(the_cat, 70)
        mate = None
        if game.switches['mate'] is not None and the_cat.mate is None:
            mate = cat_class.all_cats[game.switches['mate']]
        elif the_cat.mate is not None:
            if the_cat.mate in cat_class.all_cats:
                mate = cat_class.all_cats[the_cat.mate]
            else:
                the_cat.mate = None
        if mate is not None:
            mate.draw_large((450, 130))
            verdana.text(str(mate.name), ('center', 300))
            self._extracted_from_on_use_29(mate, -100)
            if the_cat.gender == mate.gender and not game.settings['no gendered breeding']:
                verdana_small.text('(this pair will not be able to have kittens)', ('center', 320))

        valid_mates = []
        pos_x = 0
        pos_y = 20
        if the_cat.mate is None:
            self._extracted_from_on_use_42(the_cat, valid_mates, pos_x, pos_y)
        else:
            verdana.text('Already in a relationship.', ('center', 340))
            kittens = False
            for x in game.clan.clan_cats:
                if the_cat.ID in [cat_class.all_cats[x].parent1, cat_class.all_cats[x].parent2] and mate.ID in [cat_class.all_cats[x].parent1, cat_class.all_cats[x].parent2]:
                    buttons.draw_button((200 + pos_x, 370 + pos_y), image=cat_class.all_cats[x].sprite, cat=cat_class.all_cats[x].ID, cur_screen='profile screen')

                    kittens = True
                    pos_x += 50
                    if pos_x > 400:
                        pos_y += 50
                        pos_x = 0
            if kittens:
                verdana.text('Their offspring:', ('center', 360))
            else:
                verdana.text('This pair has never had offspring.', ('center', 360))
        if mate is not None and the_cat.mate is None:
            buttons.draw_button(('center', -130), text="It\'s official!", cat_value=the_cat, mate=mate)

        elif the_cat.mate is not None:
            buttons.draw_button(('center', -130), text="Break it up...", cat_value=the_cat, mate=None)

        buttons.draw_button(('center', -100), text='Back', cur_screen='profile screen')

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_42(self, the_cat, valid_mates, pos_x, pos_y):
        for x in game.clan.clan_cats:
            pos_mate = cat_class.all_cats[x]
            if not pos_mate.dead and pos_mate.age in ['young adult', 'adult', 'senior adult', 'elder'] and the_cat != pos_mate and the_cat.ID not in [pos_mate.parent1,
                                                                                                                                                      pos_mate.parent2] and \
                    pos_mate.ID not in [
                the_cat.parent1, the_cat.parent2] and pos_mate.mate is None and (pos_mate.parent1 is None or pos_mate.parent1 not in [the_cat.parent1, the_cat.parent2]) and (
                    pos_mate.parent2 is None or pos_mate.parent2 not in [the_cat.parent1, the_cat.parent2]) and (
                    the_cat.age in ['senior adult', 'elder'] and cat_class.all_cats[x].age in ['senior adult', 'elder'] or cat_class.all_cats[x].age != 'elder' and
                    cat_class.all_cats[x].age != 'adolescent' and the_cat.age != 'elder' and the_cat.age != 'adolescent'):
                valid_mates.append(cat_class.all_cats[x])
        all_pages = int(ceil(len(valid_mates) / 27.0)) if len(valid_mates) > 27 else 1
        cats_on_page = 0
        for x in range(len(valid_mates)):
            if x + (game.switches['list_page'] - 1) * 27 > len(valid_mates):
                game.switches['list_page'] = 1
            pot_mate = valid_mates[x + (game.switches['list_page'] - 1) * 27]
            buttons.draw_button((100 + pos_x, 320 + pos_y), image=pot_mate.sprite, mate=pot_mate.ID)

            pos_x += 50
            cats_on_page += 1
            if pos_x > 400:
                pos_y += 50
                pos_x = 0
            if cats_on_page >= 27 or x + (game.switches['list_page'] - 1) * 27 == len(valid_mates) - 1:
                break
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_29(self, arg0, arg1):
        verdana_small.text(arg0.age, (arg1, 200))
        verdana_small.text(arg0.gender, (arg1, 215))
        verdana_small.text(arg0.trait, (arg1, 230))

    def screen_switches(self):
        game.switches['mate'] = None
        cat_profiles()


class ListScreen(Screens):
    # page can be found in game.switches['list_page']
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20

    def on_use(self):
        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('ALL CATS LIST', ('center', 100))
        living_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead:
                living_cats.append(the_cat)
        all_pages = int(ceil(len(living_cats) / 24.0)) if len(living_cats) > 24 else 1
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(living_cats)):
            if x + (game.switches['list_page'] - 1) * 24 >= len(living_cats):
                game.switches['list_page'] -= 1
            the_cat = living_cats[x + (game.switches['list_page'] - 1) * 24]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y), image=the_cat.sprite, cat=the_cat.ID, cur_screen='profile screen')

                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name), (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 24 or x + (game.switches['list_page'] - 1) * 24 == len(living_cats) - 1:
                    break
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

        draw_menu_buttons()

    def screen_switches(self):
        cat_profiles()


# def choose_banner():
# if game.clan is not None:
#     # if game.clan.current_season == 'Leaf-fall':
#     fall = pygame.image.load('resources/seasonbanners/fall/fall banner.png')
#     fall_fog = pygame.image.load('resources/seasonbanners/fall/fall banner fog.png')
#     fall_night = pygame.image.load('resources/seasonbanners/fall/fall banner night.png')
#     fall_night_fog = pygame.image.load('resources/seasonbanners/fall/fall banner night fog.png')
#     fall_night_overcast = pygame.image.load('resources/seasonbanners/fall/fall banner night overcast.png')
#     fall_night_rain = pygame.image.load('resources/seasonbanners/fall/fall banner night rain.png')
#     fall_overcast = pygame.image.load('resources/seasonbanners/fall/fall banner overcast.png')
#     fall_rain = pygame.image.load('resources/seasonbanners/fall/fall banner rain.png')
#     leaffall = [fall, fall_fog, fall_night, fall_night_fog, fall_night_overcast, fall_night_rain, fall_overcast,
#                 fall_rain]
#     return choice(leaffall)


class PatrolScreen(Screens):
    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text('These cats are currently in the camp, ready for a patrol.', ('center', 115))

        verdana.text('Choose up to six to take on patrol.', ('center', 135))
        verdana.text('Smaller patrols help cats gain more experience, but larger patrols are safer.', ('center', 155))

        draw_menu_buttons()
        able_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead and the_cat.in_camp and the_cat.status in ['leader', 'deputy', 'warrior', 'apprentice']:
                able_cats.append(the_cat)
        if not game.patrol_cats:
            i_max = min(len(able_cats), 12)
            for i in range(i_max):
                test_cat = random.choice(able_cats)
                able_cats.remove(test_cat)
                game.patrol_cats[i] = test_cat
        else:
            i_max = len(game.patrol_cats)
        random_options = []
        for u in range(6):
            if u < i_max:
                if game.patrol_cats[u] in game.switches['current_patrol']:
                    game.patrol_cats[u].draw((screen_x / 2 - 50 * (u + 2), 550))
                else:
                    buttons.draw_button((50, 150 + 50 * u), image=game.patrol_cats[u].sprite, cat=u)
                    random_options.append(game.patrol_cats[u])
        for u in range(6, 12):
            if u < i_max:
                if game.patrol_cats[u] in game.switches['current_patrol']:
                    game.patrol_cats[u].draw((screen_x / 2 + 50 * (u - 5), 550))
                else:
                    buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)), image=game.patrol_cats[u].sprite, cat=u)
                    random_options.append(game.patrol_cats[u])
        if random_options and len(game.switches['current_patrol']) < 6:
            random_patrol = choice(random_options)
            buttons.draw_button(('center', 530), text='Add Random', current_patrol=random_patrol, add=True)

        else:
            buttons.draw_button(('center', 530), text='Add Random', available=False)
        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0 and game.patrol_cats[game.switches['cat']] not in game.switches['current_patrol']:
            self._extracted_from_on_use_58()
        if len(game.switches['current_patrol']) > 0:
            buttons.draw_button(('center', 630), text='Start Patrol', cur_screen='patrol event screen')

        else:
            buttons.draw_button(('center', 630), text='Start Patrol', available=False)

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_58(self):
        game.patrol_cats[game.switches['cat']].draw_large((320, 200))
        verdana.text(str(game.patrol_cats[game.switches['cat']].name), ('center', 360))
        verdana_small.text(str(game.patrol_cats[game.switches['cat']].status), ('center', 385))

        verdana_small.text(str(game.patrol_cats[game.switches['cat']].trait), ('center', 405))

        verdana_small.text(str(game.patrol_cats[game.switches['cat']].skill), ('center', 425))

        verdana_small.text('experience: ' + str(game.patrol_cats[game.switches['cat']].experience_level), ('center', 445))

        if game.patrol_cats[game.switches['cat']].status == 'apprentice':
            verdana_small.text('mentor: ' + str(game.patrol_cats[game.switches['cat']].mentor.name), ('center', 465))

        if len(game.switches['current_patrol']) < 6:
            buttons.draw_button(('center', 500), text='Add to Patrol', current_patrol=game.patrol_cats[game.switches['cat']], add=True)

    def screen_switches(self):
        game.switches['current_patrol'] = []
        game.switches['cat'] = None
        game.patrol_cats = {}
        game.switches['event'] = 0
        cat_profiles()


class PatrolEventScreen(Screens):
    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        if game.switches['event'] == 0:
            verdana.text(str(patrol.patrol_event[1]), ('center', 200))
            # if patrol.patrol_event[0] == 35:
            #     patrol_img = pygame.image.load('resources/rogue.png')
            #     patrol_img = pygame.transform.scale(patrol_img, (340,200))
            #     screen.blit(patrol_img, (500, 200))
            # elif patrol.patrol_event[0] == 44:
            #     patrol_img = pygame.image.load('resources/kittypet.png')
            #     patrol_img = pygame.transform.scale(patrol_img, (320, 200))
            #     screen.blit(patrol_img, (500, 200))
            # elif patrol.patrol_event[0] == 6 or patrol.patrol_event[0] == 7:
            #     patrol_img = pygame.image.load('resources/fox.png')
            #     patrol_img = pygame.transform.scale(patrol_img, (320, 200))
            #     screen.blit(patrol_img, (500, 200))
            buttons.draw_button(('center', 300), text='Proceed', event=1)
            buttons.draw_button(('center', 340), text='Do Not Proceed', event=2)
            if patrol.patrol_event[0] in patrol.failable_patrols:
                buttons.draw_button(('center', 380), text='Antagonize', event=3)
        if game.switches['event'] > 0:
            if game.switches['event'] < 3 or (game.switches['event'] <4 and patrol.patrol_event[0] in patrol.failable_patrols):
                patrol.calculate()

            verdana.text(str(patrol.patrol_result_text), ('center', 200))
            buttons.draw_button(('center', 320), text='Return to Clan', cur_screen='clan screen')

        for u in range(6):
            if u < patrol.patrol_size:
                patrol.patrol_cats[u].draw((screen_x / 2 - 50 * (u + 2), 550))
        verdana_small.text('season: ' + str(game.clan.current_season), ('center', 400))
        verdana_small.text('patrol leader: ' + str(patrol.patrol_leader.name), ('center', 420))

        verdana_small.text('patrol skills: ' + str(patrol.patrol_skills), ('center', 440))

        verdana_small.text('patrol traits: ' + str(patrol.patrol_traits), ('center', 460))

        draw_menu_buttons()

    def screen_switches(self):
        patrol.new_patrol()
        game.switches['event'] = 0
        cat_profiles()


class AllegiancesScreen(Screens):
    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))

        verdana_big.text(f'{game.clan.name}Clan Allegiances', (30, 110))
        a = 0
        if game.allegiance_list is not None and game.allegiance_list != []:
            for x in range(min(len(game.allegiance_list), game.max_allegiance_displayed)):
                if game.allegiance_list[x] is None:
                    continue
                verdana.text(game.allegiance_list[x][0], (30, 140 + a * 30))
                verdana.text(game.allegiance_list[x][1], (170, 140 + a * 30))
                a += 1
        if len(game.allegiance_list) > game.max_allegiance_displayed:
            buttons.draw_button((720, 250), image=game.up, arrow="UP")
            buttons.draw_button((700, 550), image=game.down, arrow="DOWN")
        draw_menu_buttons()

    def screen_switches(self):
        living_cats = []
        game.allegiance_scroll_ct = 0
        game.allegiance_list = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead:
                living_cats.append(the_cat)
        if not game.clan.leader.dead:
            game.allegiance_list.append(['LEADER:', f"{str(game.clan.leader.name)} - a {game.clan.leader.describe_cat()}"])
            if len(game.clan.leader.apprentice) > 0:
                if len(game.clan.leader.apprentice) == 1:
                    game.allegiance_list.append(['', '      Apprentice: ' + str(game.clan.leader.apprentice[0].name)])
                else:
                    app_names = ''
                    for app in game.clan.leader.apprentice:
                        app_names += str(app.name) + ', '
                    game.allegiance_list.append(['', '      Apprentices: ' + app_names[:-2]])
        if game.clan.deputy != 0 and game.clan.deputy is not None and not game.clan.deputy.dead:
            game.allegiance_list.append(['DEPUTY:', f"{str(game.clan.deputy.name)} - a {game.clan.deputy.describe_cat()}"])
            if len(game.clan.deputy.apprentice) > 0:
                if len(game.clan.deputy.apprentice) == 1:
                    game.allegiance_list.append(['', '      Apprentice: ' + str(game.clan.deputy.apprentice[0].name)])
                else:
                    app_names = ''
                    for app in game.clan.deputy.apprentice:
                        app_names += str(app.name) + ', '
                    game.allegiance_list.append(['', '      Apprentices: ' + app_names[:-2]])
        cat_count = self._extracted_from_screen_switches_24(living_cats, 'medicine cat', 'MEDICINE CAT:')
        queens = []
        for living_cat_ in living_cats:
            if str(living_cat_.status) == 'kitten' and living_cat_.parent1 is not None:
                if cat_class.all_cats[living_cat_.parent1].gender == 'male':
                    if living_cat_.parent2 is None or cat_class.all_cats[living_cat_.parent2].gender == 'male':
                        queens.append(living_cat_.parent1)
                else:
                    queens.append(living_cat_.parent1)
        cat_count = 0
        for living_cat__ in living_cats:
            if str(living_cat__.status) == 'warrior' and living_cat__.ID not in queens:
                if not cat_count:
                    game.allegiance_list.append(['WARRIORS:', f"{str(living_cat__.name)} - a {living_cat__.describe_cat()}"])
                else:
                    game.allegiance_list.append(['', f"{str(living_cat__.name)} - a {living_cat__.describe_cat()}"])
                if len(living_cat__.apprentice) > 0:
                    if len(living_cat__.apprentice) == 1:
                        game.allegiance_list.append(['', '      Apprentice: ' + str(living_cat__.apprentice[0].name)])
                    else:
                        app_names = ''
                        for app in living_cat__.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(['', '      Apprentices: ' + app_names[:-2]])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['WARRIORS:', ''])
        cat_count = 0
        for living_cat___ in living_cats:
            if str(living_cat___.status) in ['apprentice', 'medicine cat apprentice']:
                if cat_count == 0:
                    game.allegiance_list.append(['APPRENTICES:', f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"])
                else:
                    game.allegiance_list.append(['', f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['APPRENTICES:', ''])
        cat_count = 0
        for living_cat____ in living_cats:
            if living_cat____.ID in queens:
                if cat_count == 0:
                    game.allegiance_list.append(['QUEENS:', f"{str(living_cat____.name)} - a {living_cat____.describe_cat()}"])
                else:
                    game.allegiance_list.append(['', f"{str(living_cat____.name)} - a {living_cat____.describe_cat()}"])
                cat_count += 1
                if len(living_cat____.apprentice) > 0:
                    if len(living_cat____.apprentice) == 1:
                        game.allegiance_list.append(['', '      Apprentice: ' + str(living_cat____.apprentice[0].name)])
                    else:
                        app_names = ''
                        for app in living_cat____.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(['', '      Apprentices: ' + app_names[:-2]])
        if not cat_count:
            game.allegiance_list.append(['QUEENS:', ''])
        cat_count = self._extracted_from_screen_switches_24(living_cats, 'elder', 'ELDERS:')
        cat_count = self._extracted_from_screen_switches_24(living_cats, 'kitten', 'KITS:')

        draw_menu_buttons()

    # TODO Rename this here and in `screen_switches`
    def _extracted_from_screen_switches_24(self, living_cats, arg1, arg2):
        result = 0
        for living_cat in living_cats:
            if str(living_cat.status) == arg1:
                if result == 0:
                    game.allegiance_list.append([arg2, f"{str(living_cat.name)} - a {living_cat.describe_cat()}"])
                else:
                    game.allegiance_list.append(["", f"{str(living_cat.name)} - a {living_cat.describe_cat()}"])
                result += 1
                if len(living_cat.apprentice) > 0:
                    if len(living_cat.apprentice) == 1:
                        game.allegiance_list.append(['', '      Apprentice: ' + str(living_cat.apprentice[0].name)])
                    else:
                        app_names = ''
                        for app in living_cat.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(['', '      Apprentices: ' + app_names[:-2]])
        if not result:
            game.allegiance_list.append([arg2, ''])
        return result


class ChooseMentorScreen(Screens):
    def on_use(self):
        verdana_big.text('Choose Mentor', ('center', 30))
        living_cats = []
        for cat in cat_class.all_cats.values():
            if not cat.dead and cat != game.switches['apprentice'].mentor and cat.status in ['warrior', 'deputy', 'leader']:
                living_cats.append(cat)
        all_pages = 1
        if len(living_cats) > 24:
            all_pages = int(ceil(len(living_cats) / 24.0))
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(living_cats)):
            if x + (game.switches['list_page'] - 1) * 24 > len(living_cats):
                game.switches['list_page'] = 1
            the_cat = living_cats[x + (game.switches['list_page'] - 1) * 24]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y), image=the_cat.sprite, cat=the_cat.ID, cur_screen='choose mentor screen2')

                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name), (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 24 or x + (game.switches['list_page'] - 1) * 24 == len(living_cats) - 1:
                    break
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

        draw_menu_buttons()


class ChooseMentorScreen2(Screens):
    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = cat_class.all_cats.get(game.switches['cat'])

        # back and next buttons on the profile page
        previous_cat = 0
        next_cat = 0

        for check_cat in cat_class.all_cats:
            if cat_class.all_cats[check_cat].ID == the_cat.ID:
                next_cat = 1

            if next_cat == 0 and cat_class.all_cats[check_cat].ID != the_cat.ID and not cat_class.all_cats[check_cat].dead and cat_class.all_cats[
                check_cat].status in ['warrior', 'deputy', 'leader'] and cat_class.all_cats[check_cat] != game.switches['apprentice'].mentor:
                previous_cat = cat_class.all_cats[check_cat].ID
            elif next_cat == 1 and cat_class.all_cats[check_cat].ID != the_cat.ID and not cat_class.all_cats[check_cat].dead and cat_class.all_cats[
                check_cat].status in ['warrior', 'deputy', 'leader'] and cat_class.all_cats[check_cat] != game.switches['apprentice'].mentor:
                next_cat = cat_class.all_cats[check_cat].ID
            elif int(next_cat) > 1:
                break

        if next_cat == 1:
            next_cat = 0

        if next_cat != 0:
            buttons.draw_button((-40, 40), text='Next Cat', cat=next_cat)
        if previous_cat != 0:
            buttons.draw_button((40, 40), text='Previous Cat', cat=previous_cat)

        # Info in string
        cat_name = str(the_cat.name)  # name
        cat_thought = the_cat.thought  # thought

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 70))  # NAME
        the_cat.draw_large(('center', 100))  # IMAGE
        verdana_small.text(the_cat.gender, (250, 330 + count * 15))
        count += 1  # SEX / GENDER
        verdana_small.text(the_cat.status, (450, 330 + count2 * 15))
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name), (450, 330 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            if len(the_cat.apprentice) == 1:
                apps = 'apprentice: ' + str(the_cat.apprentice[0].name)
            else:
                apps = 'apprentices: '
                for cat in the_cat.apprentice:
                    apps += str(cat.name) + ', '
                apps = apps[:len(apps) - 2]
            verdana_small.text(apps, (450, 330 + count2 * 15))
            count2 += 1
        if len(the_cat.former_apprentices) != 0 and the_cat.former_apprentices[0] is not None:
            if len(the_cat.former_apprentices) == 1:
                former_apps = 'former apprentice: ' + str(the_cat.former_apprentices[0].name)
            else:
                former_apps = 'former apprentices: '
                for cat in the_cat.former_apprentices:
                    former_apps += str(cat.name) + ', '
                former_apps = former_apps[:len(former_apps) - 2]
            verdana_small.text(former_apps, (450, 330 + count2 * 15))
            count2 += 1
        if the_cat.age == 'kitten':
            verdana_small.text('young', (250, 330 + count * 15))
        elif the_cat.age == 'elder':
            verdana_small.text('senior', (250, 330 + count * 15))
        else:
            verdana_small.text(the_cat.age, (250, 330 + count * 15))
        count += 1  # AGE
        verdana_small.text(the_cat.trait, (450, 330 + count2 * 15))
        count2 += 1  # CHARACTER TRAIT
        verdana_small.text(the_cat.skill, (450, 330 + count2 * 15))
        count2 += 1  # SPECIAL SKILL
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(), (250, 330 + count * 15))
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(), (250, 330 + count * 15))
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length, (250, 330 + count * 15))
        count += 1  # PELT LENGTH

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (250, 330 + count * 15))
            count += 1
        elif the_cat.parent2 is None:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown', (250, 330 + count * 15))
            count += 1
        else:
            if the_cat.parent1 in the_cat.all_cats and the_cat.parent2 in the_cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            elif the_cat.parent1 in the_cat.all_cats:
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            elif the_cat.parent2 in the_cat.all_cats:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            else:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            verdana_small.text('parents: ' + par1 + ' and ' + par2, (250, 330 + count * 15))
            count += 1

        # MOONS
        if the_cat.dead:
            verdana_small.text(str(the_cat.moons) + ' moons (in life)', (250, 330 + count * 15))
            count += 1
            verdana_small.text(str(the_cat.dead_for) + ' moons (in death)', (250, 330 + count * 15))
            count += 1
        else:
            verdana_small.text(str(the_cat.moons) + ' moons', (250, 330 + count * 15))
            count += 1

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in cat_class.all_cats:
                if cat_class.all_cats.get(the_cat.mate).dead:  # TODO: fix when mate dies mate becomes none
                    verdana_small.text('former mate: ' + str(cat_class.all_cats[the_cat.mate].name), (250, 330 + count * 15))
                else:
                    verdana_small.text('mate: ' + str(cat_class.all_cats[the_cat.mate].name), (250, 330 + count * 15))
                count += 1
            else:
                verdana_small.text('Error: mate: ' + str(the_cat.mate) + " not found", ('center', 495))

        # experience
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level), (450, 330 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level), (450, 330 + count2 * 15))
            count2 += 1

        # buttons

        buttons.draw_button(('center', -100), text='Choose as ' + str(game.switches['apprentice'].name) + '\'s mentor', cur_screen=game.switches['last_screen'], cat_value=the_cat,
                            apprentice=game.switches['apprentice'])
        buttons.draw_button(('center', -50), text='Back', cur_screen='clan screen')


class ChangeNameScreen(Screens):
    def on_use(self):
        if game.settings['dark mode']:
            pygame.draw.rect(screen, 'white', pygame.Rect((300, 200), (200, 20)))
            verdana_black.text(game.switches['naming_text'], (315, 200))
        else:
            pygame.draw.rect(screen, 'gray', pygame.Rect((300, 200), (200, 20)))
            verdana.text(game.switches['naming_text'], (315, 200))
        verdana.text('Change Name', ('center', 50))
        verdana.text('Add a space between the new prefix and suffix', ('center', 70))
        verdana.text('i.e. Fire heart', ('center', 90))
        buttons.draw_button(('center', -100), text=' Change Name ', cur_screen='change name screen', cat_value=game.switches['name_cat'])
        buttons.draw_button(('center', -50), text='Back', cur_screen='profile screen')


class OptionsScreen(Screens):
    def on_use(self):
        the_cat = cat_class.all_cats.get(game.switches['cat'])
        verdana_big.text('Options - ' + str(the_cat.name), ('center', 80))
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50
        buttons.draw_button((x_value, y_value + button_count * y_change), text='Change Name', cur_screen='change name screen')
        button_count+=1
        game.switches['name_cat'] = the_cat.ID
        buttons.draw_button((x_value, y_value + button_count * y_change), text='See Family', cur_screen='see kits screen')
        button_count+=1

        if the_cat.status == 'apprentice' and not the_cat.dead:
            game.switches['apprentice'] = the_cat
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Change Mentor', cur_screen='choose mentor screen')
            button_count += 1

        buttons.draw_button((x_value, y_value + button_count * y_change), text='Family Tree')
        button_count+=1

        if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'] and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Pick mate for ' + str(the_cat.name), cur_screen='choose mate screen')
            button_count += 1

            if the_cat.age in ['young adult', 'adult', 'senior adult'] and not the_cat.no_kits:
                buttons.draw_button((x_value, y_value + button_count * y_change), text='Prevent kits', no_kits=True, cat_value=the_cat)
                button_count += 1

            elif the_cat.age in ['young adult', 'adult', 'senior adult'] and the_cat.no_kits:
                buttons.draw_button((x_value, y_value + button_count * y_change), text='Allow kits', no_kits=False, cat_value=the_cat)
                button_count += 1

        if game.switches['new_leader'] is not False and game.switches['new_leader'] is not None:
            game.clan.new_leader(game.switches['new_leader'])
        if the_cat.status in ['warrior'] and not the_cat.dead and game.clan.leader.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Promote to Leader', new_leader=the_cat)
            button_count += 1

        elif the_cat.status in ['warrior'] and not the_cat.dead and game.clan.deputy is None:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Promote to Deputy', deputy_switch=the_cat)
            button_count += 1

        elif the_cat.status in ['deputy'] and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Demote from Deputy', deputy_switch=the_cat)
            button_count += 1

        elif the_cat.status in ['warrior'] and not the_cat.dead and game.clan.deputy:
            if game.clan.deputy.dead:
                buttons.draw_button((x_value, y_value + button_count * y_change), text='Promote to Deputy', deputy_switch=the_cat)
                button_count += 1

        if not the_cat.dead:
            buttons.draw_button((x_value, 650), text='Kill Cat', kill_cat=the_cat)

        buttons.draw_button((x_value, 600), text='Exile Cat')

        if game.switches['deputy_switch'] is not False and game.switches['deputy_switch'] is not None and game.switches['deputy_switch'].status == 'warrior':
            game.clan.deputy = game.switches['deputy_switch']
            game.switches['deputy_switch'].status_change('deputy')
            game.switches['deputy_switch'] = False
        elif game.switches['deputy_switch'] is not False and game.switches['deputy_switch'] is not None and game.switches['deputy_switch'].status == 'deputy':
            game.clan.deputy = None
            game.switches['deputy_switch'].status_change('warrior')
            game.switches['deputy_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches['apprentice_switch'] is not None and game.switches['apprentice_switch'].status == 'apprentice':
            game.switches['apprentice_switch'].status_change('medicine cat apprentice')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches['apprentice_switch'] is not None and game.switches[
            'apprentice_switch'].status == 'medicine cat apprentice':
            game.switches['apprentice_switch'].status_change('apprentice')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches['apprentice_switch'] is not None and game.switches[
            'apprentice_switch'].status == 'warrior':
            game.switches['apprentice_switch'].status_change('medicine cat')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches['apprentice_switch'] is not None and game.switches[
            'apprentice_switch'].status == 'medicine cat':
            game.switches['apprentice_switch'].status_change('warrior')
            game.switches['apprentice_switch'] = False

        if game.switches['kill_cat'] is not False and game.switches['kill_cat'] is not None:
            events_class.dies(game.switches['kill_cat'])
            game.switches['kill_cat'] = False

        if the_cat.status in ['apprentice'] and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Switch to medicine cat apprentice', apprentice_switch=the_cat)
            button_count+=1
        elif the_cat.status in ['medicine cat apprentice'] and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Switch to warrior apprentice', apprentice_switch=the_cat)
            button_count+=1
        elif the_cat.status == 'warrior' and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Switch to medicine cat', apprentice_switch=the_cat)
            button_count += 1
        elif the_cat.status == 'medicine cat' and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change), text='Switch to warrior', apprentice_switch=the_cat)
            button_count += 1
        buttons.draw_button((x_value, y_value + button_count * y_change + 30), text='Back', cur_screen='profile screen')

class StatsScreen(Screens):
    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        living_num = 0
        warriors_num = 0
        app_num = 0
        kit_num = 0
        elder_num = 0
        starclan_num = 0
        for cat in cat_class.all_cats.values():
            if not cat.dead:
                living_num+=1
                if cat.status == 'warrior':
                    warriors_num+=1
                elif cat.status in ['apprentice', 'medicine cat apprentice']:
                    app_num+=1
                elif cat.status == 'kitten':
                    kit_num+=1
                elif cat.status == 'elder':
                    elder_num+=1
            else:
                starclan_num+=1

        verdana.text('Number of Living Cats: ' + str(living_num), (100, 150))
        verdana.text('Number of Warriors: ' + str(warriors_num), (100, 200))
        verdana.text('Number of Apprentices: ' + str(app_num), (100, 250))
        verdana.text('Number of Kits: ' + str(kit_num), (100, 300))
        verdana.text('Number of Elders: ' + str(elder_num), (100, 350))
        verdana.text('Number of StarClan Cats: ' + str(starclan_num), (100, 400))
        draw_menu_buttons()






# SCREENS
screens = Screens()

start_screen = StartScreen('start screen')
settings_screen = SettingsScreen('settings screen')
info_screen = InfoScreen('info screen')
clan_screen = ClanScreen('clan screen')
patrol_screen = PatrolScreen('patrol screen')  # for picking cats to go on patrol
patrol_event_screen = PatrolEventScreen('patrol event screen')  # for seeing the events of the patrol
starclan_screen = StarClanScreen('starclan screen')
make_clan_screen = MakeClanScreen('make clan screen')
clan_created_screen = ClanCreatedScreen('clan created screen')
events_screen = EventsScreen('events screen')
profile_screen = ProfileScreen('profile screen')
single_event_screen = SingleEventScreen('single event screen')
choose_mate_screen = ChooseMateScreen('choose mate screen')
view_children_screen = ViewChildrenScreen('see kits screen')
list_screen = ListScreen('list screen')
switch_clan_screen = SwitchClanScreen('switch clan screen')
allegiances_screen = AllegiancesScreen('allegiances screen')
choose_mentor_screen = ChooseMentorScreen('choose mentor screen')
choose_mentor_screen2 = ChooseMentorScreen2('choose mentor screen2')
change_name_screen = ChangeNameScreen('change name screen')
option_screen = OptionsScreen('options screen')
language_screen = LanguageScreen('language screen')
stats_screen = StatsScreen('stats screen')

# CAT PROFILES
def cat_profiles():
    game.choose_cats.clear()
    game.cat_buttons.clear()
    for x in game.clan.clan_cats:
        game.choose_cats[x] = cat_class.all_cats[x]
        game.choose_cats[x].update_sprite()


def draw_menu_buttons():
    buttons.draw_button((260, 70), text='EVENTS', cur_screen='events screen')
    buttons.draw_button((340, 70), text='CLAN', cur_screen='clan screen')
    buttons.draw_button((400, 70), text='STARCLAN', cur_screen='starclan screen')
    buttons.draw_button((500, 70), text='PATROL', cur_screen='patrol screen')
    buttons.draw_button((50, 50), text='< Back to Main Menu', cur_screen='start screen')
    buttons.draw_button((-70, 50), text='List Cats', cur_screen='list screen')
    buttons.draw_button((-70, 80), text='Allegiances', cur_screen='allegiances screen')
    buttons.draw_button((50, 80), text='Stats', cur_screen='stats screen')

