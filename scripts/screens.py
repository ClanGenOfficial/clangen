from .clan import *
from .events import *
from .patrols import *


# SCREENS PARENT CLASS
class Screens(object):
    game_screen = screen
    game_x = screen_x
    game_y = screen_y
    all_screens = {}
    last_screen = ''  # store the screen that the user will go back to after clicking 'back' button

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
        # example_cat.draw_big((350, 150))

        # buttons
        if game.clan is not None and game.switches['error_message'] == '':
            buttons.draw_button((70, 310), image='continue', text='Continue >', cur_screen='clan screen')
            buttons.draw_button((70, 355), image='switch_clan', text='Switch Clan >', cur_screen='switch clan screen')
        elif game.clan is not None and game.switches['error_message']:
            buttons.draw_button((70, 310), image='continue', text='Continue >', available=False)
            buttons.draw_button((70, 355), image='switch_clan', text='Switch Clan >', cur_screen='switch clan screen')
        else:
            buttons.draw_button((70, 310), image='continue', text='Continue >', available=False)
            buttons.draw_button((70, 355), image='switch_clan', text='Switch Clan >', available=False)
        buttons.draw_button((70, 400), image='new_clan', text='Make New >', cur_screen='make clan screen')
        buttons.draw_button((70, 445), image='settings', text='Settings & Info >', cur_screen='settings screen')

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
        buttons.draw_button((330, 100), text='Settings', available=False)
        buttons.draw_button((-340, 100), text='Info', cur_screen='info screen')
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
        buttons.draw_button((330, 100), text='Settings', cur_screen='settings screen')
        buttons.draw_button((-340, 100), text='Info', available=False)
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


class ClanScreen(Screens):
    def on_use(self):
        # layout
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))

        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('Leader\'s Den', game.clan.cur_layout['leader den'])
        verdana.text('Medicine Cat Den', game.clan.cur_layout['medicine den'])
        verdana.text('Nursery', game.clan.cur_layout['nursery'])
        verdana.text('Clearing', game.clan.cur_layout['clearing'])
        verdana.text('Apprentices\' Den', game.clan.cur_layout['apprentice den'])
        verdana.text('Warriors\' Den', game.clan.cur_layout['warrior den'])
        verdana.text('Elders\' Den', game.clan.cur_layout['elder den'])

        for x in game.clan.clan_cats:
            if not cat_class.all_cats[x].dead and cat_class.all_cats[x].in_camp:
                buttons.draw_button(cat_class.all_cats[x].placement, image=cat_class.all_cats[x].sprite, cat=x, cur_screen='profile screen')

        # buttons
        draw_menu_buttons()
        buttons.draw_button(('center', -50), text='Save Clan', save_clan=True)
        verdana.text('Remember to save!', ('center', -20))

    def screen_switches(self):
        cat_profiles()
        self.change_brightness()
        game.switches['cat'] = None

        p = game.clan.cur_layout
        game.clan.leader.placement = choice(p['leader place'])
        game.clan.medicine_cat.placement = choice(p['medicine place'])

        for x in game.clan.clan_cats:
            i = randint(0, 20)
            if cat_class.all_cats[x].status == 'warrior':
                if i < 15:  # higher chance for warriors to end up in warriors den or the clearing
                    cat_class.all_cats[x].placement = choice([choice(p['warrior place']), choice(p['clearing place'])])
                else:
                    cat_class.all_cats[x].placement = choice(
                        [choice(p['nursery place']), choice(p['leader place']), choice(p['elder place']), choice(p['medicine place']), choice(p['apprentice place'])])
            elif cat_class.all_cats[x].status == 'deputy':
                if i < 17:  # higher chance for deputies to end up in warrior den, clearing OR leader den
                    cat_class.all_cats[x].placement = choice([choice(p['warrior place']), choice(p['leader place']), choice(p['clearing place'])])
                else:
                    cat_class.all_cats[x].placement = choice(
                        [choice(p['nursery place']), choice(p['leader place']), choice(p['elder place']), choice(p['medicine place']), choice(p['apprentice place'])])
            elif cat_class.all_cats[x].status == 'kitten':
                if i < 13:
                    cat_class.all_cats[x].placement = choice(p['nursery place'])
                elif i == 19:
                    cat_class.all_cats[x].placement = choice(p['leader place'])
                else:
                    cat_class.all_cats[x].placement = choice(
                        [choice(p['clearing place']), choice(p['warrior place']), choice(p['elder place']), choice(p['medicine place']), choice(p['apprentice place'])])
            elif cat_class.all_cats[x].status == 'elder':
                cat_class.all_cats[x].placement = choice(p['elder place'])
            elif cat_class.all_cats[x].status == 'apprentice':
                if i < 13:
                    cat_class.all_cats[x].placement = choice([choice(p['apprentice place']), choice(p['clearing place'])])
                elif i >= 19:
                    cat_class.all_cats[x].placement = choice(p['leader place'])
                else:
                    cat_class.all_cats[x].placement = choice([choice(p['nursery place']), choice(p['warrior place']), choice(p['elder place']), choice(p['medicine place'])])
            elif cat_class.all_cats[x].status == 'medicine cat apprentice':
                cat_class.all_cats[x].placement = choice(p['medicine place'])
            elif cat_class.all_cats[x].status == 'medicine cat':
                cat_class.all_cats[x].placement = choice(p['medicine place'])

    def change_brightness(self):
        if game.settings['dark mode']:
            self.greenleaf_bg = pygame.transform.scale(pygame.image.load('resources/greenleafcamp_dark.png'), (800, 700))
            self.newleaf_bg = pygame.transform.scale(pygame.image.load('resources/newleafcamp_dark.png'), (800, 700))
            self.leafbare_bg = pygame.transform.scale(pygame.image.load('resources/leafbarecamp_dark.png'), (800, 700))
            self.leaffall_bg = pygame.transform.scale(pygame.image.load('resources/leaffallcamp_dark.png'), (800, 700))
        else:
            self.greenleaf_bg = pygame.transform.scale(pygame.image.load('resources/greenleafcamp.png'), (800, 700))
            self.newleaf_bg = pygame.transform.scale(pygame.image.load('resources/newleafcamp.png'), (800, 700))
            self.leafbare_bg = pygame.transform.scale(pygame.image.load('resources/leafbarecamp.png'), (800, 700))
            self.leaffall_bg = pygame.transform.scale(pygame.image.load('resources/leaffallcamp.png'), (800, 700))


class StarClanScreen(Screens):
    def on_use(self):
        # layout
        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('StarClan Cat List', ('center', 100))

        # make a list of just dead cats
        dead_cats = [game.clan.instructor]
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID:
                dead_cats.append(the_cat)

        # pages
        all_pages = 1  # amount of pages
        if len(dead_cats) > 24:
            all_pages = int(ceil(len(dead_cats) / 24.0))

        # dead cats
        pos_x = 0
        pos_y = 0
        cats_on_page = 0  # how many are on page already
        for x in range(len(dead_cats)):
            if (x + (game.switches['list_page'] - 1) * 24) > len(dead_cats):
                game.switches['list_page'] = 1

            the_cat = dead_cats[x + (game.switches['list_page'] - 1) * 24]
            if the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y), image=the_cat.sprite, cat=the_cat.ID, cur_screen='profile screen')
                # name length
                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name), (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

                if cats_on_page >= 24 or x + (game.switches['list_page'] - 1) * 24 == len(dead_cats) - 1:
                    break

        # page buttons
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))
        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)
        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

        # buttons
        draw_menu_buttons()

    def screen_switches(self):
        cat_profiles()


class MakeClanScreen(Screens):
    def first_phase(self):
        # layout
        verdana_big.text('NAME YOUR CLAN!', ('center', 150))
        self.game_screen.blit(game.naming_box, (310, 200))
        if game.settings['dark mode']:
            verdana_black.text(game.switches['naming_text'], (315, 200))
        else:
            verdana.text(game.switches['naming_text'], (315, 200))
        verdana.text('-Clan', (455, 200))
        verdana.text('Max ten letters long. Don\'t include "Clan" in it.', ('center', 250))
        buttons.draw_button(('center', 300), text='Randomize', naming_text=choice(names.normal_prefixes))
        buttons.draw_button(('center', 350), text='Reset Name', naming_text='')

        # buttons
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button(('center', 500), text='Name Clan', clan_name=game.switches['naming_text'])

    def second_phase(self):
        # LAYOUT
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        verdana.text('These twelve cats are your potential clan members.', ('center', 115))
        verdana.text('Some of them will be left behind.', ('center', 135))
        verdana.text('First, pick a leader to lead ' + game.switches['clan_name'] + 'Clan through any difficulties.', ('center', 160))

        # cat buttons / small sprites
        for u in range(6):
            buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
        for u in range(6, 12):
            buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        # cat profiles
        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0:
            game.choose_cats[game.switches['cat']].draw_large((320, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name) + ' --> ' + game.choose_cats[game.switches['cat']].name.prefix + 'star', ('center', 360))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (330, 385))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (330, 405))
            if game.choose_cats[game.switches['cat']].age == 'kitten':
                verdana_baby.text(str(game.choose_cats[game.switches['cat']].trait), (330, 425))
            else:
                verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (330, 425))

            if game.choose_cats[game.switches['cat']].age in ['kitten', 'adolescent']:
                verdana_red.text('Too young to become leader.', ('center', 490))
            else:
                buttons.draw_button(('center', 490), text='Grant this cat their nine lives', leader=game.switches['cat'])

        # buttons
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((-50, 50), text='< Last step', clan_name='', cat=None)

    def third_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        verdana.text('Second, choose your deputy. This cat will support their leader and take over if things go awry.', ('center', 120))

        # cat buttons / small sprites
        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 25, 550))
            else:
                buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 25, 550))
            else:
                buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        # cat profiles
        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0 and game.switches['cat'] != game.switches['leader']:
            game.choose_cats[game.switches['cat']].draw_large((320, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name), ('center', 360))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (330, 385))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (330, 405))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (330, 425))

            if game.choose_cats[game.switches['cat']].age == 'kitten' or game.choose_cats[game.switches['cat']].age == 'adolescent':
                verdana_red.text('Too young to become deputy.', ('center', 490))
            else:
                buttons.draw_button(('center', 490), text='This cat will support the leader', deputy=game.switches['cat'])

        # buttons
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((-50, 50), text='< Last Step', leader=None, cat=None)

    def fourth_phase(self):
        # LAYOUT
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        verdana.text('Third, pick your medicine cat. They will aid the sick and wounded and communicate with StarClan.', ('center', 120))

        # cat buttons / small sprites
        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 25, 550))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 50 * (u + 2), 550))
            else:
                buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 25, 550))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((screen_x / 2 + 50 * (u - 5), 550))
            else:
                buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        # cat profiles
        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0 and game.switches['cat'] != game.switches['leader'] and game.switches['cat'] != game.switches[
            'deputy']:
            game.choose_cats[game.switches['cat']].draw_large((320, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name), ('center', 360))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (330, 385))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (330, 405))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (330, 425))

            if game.choose_cats[game.switches['cat']].age == 'kitten' or game.choose_cats[game.switches['cat']].age == 'adolescent':
                verdana_red.text('Too young to become medicine cat.', ('center', 490))
            else:
                buttons.draw_button(('center', 490), text='This cat will take care of the clan', medicine_cat=game.switches['cat'])

        # buttons
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((-50, 50), text='< Last step', deputy=None, cat=None)

    def fifth_phase(self):
        # LAYOUT
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        verdana.text('Finally, recruit from 4 to 7 more members to your clan.', ('center', 120))
        verdana.text('Choose wisely...', ('center', 150))

        # cat buttons / small sprites
        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 25, 550))
            elif game.switches['deputy'] == u or game.switches['medicine_cat'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 50 * (u + 2), 550))
            elif u in game.switches['members']:
                game.choose_cats[u].draw((screen_x / 2 - 50 * (u + 2), 550))
            else:
                buttons.draw_button((50, 150 + 50 * u), image=game.choose_cats[u].sprite, cat=u)
        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((screen_x / 2 - 25, 550))
            elif game.switches['deputy'] == u or game.switches['medicine_cat'] == u:
                game.choose_cats[u].draw((screen_x / 2 + 50 * (u - 5), 550))
            elif u in game.switches['members']:
                game.choose_cats[u].draw((screen_x / 2 + 50 * (u - 5), 550))
            else:
                buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)), image=game.choose_cats[u].sprite, cat=u)

        # cat profiles
        if 12 > game.switches['cat'] >= 0 and game.switches['cat'] not in [game.switches['leader'], game.switches['deputy'], game.switches['medicine_cat']] and game.switches[
            'cat'] not in game.switches['members']:
            game.choose_cats[game.switches['cat']].draw_large((320, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name), ('center', 360))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].gender), (330, 385))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age), (330, 405))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].trait), (330, 425))

            if len(game.switches['members']) < 7:
                buttons.draw_button(('center', 490), text='Recruit', members=game.switches['cat'], add=True)

        verdana_small.text('Note: if you have more than 8 clans, clicking done deletes the least recently used clan.', ('center', 660))

        # buttons
        verdana_small.text('Note: going back to main menu resets the generated cats.', (50, 25))
        buttons.draw_button((50, 50), text='<< Back to Main Menu', cur_screen='start screen', naming_text='')
        buttons.draw_button((-50, 50), text='< Last step', medicine_cat=None, members=[], cat=None)
        if len(game.switches['members']) > 3:
            buttons.draw_button(('center', 630), text='Done', cur_screen='clan created screen')
        else:
            buttons.draw_button(('center', 630), text='Done', available=False)

    def on_use(self):
        if len(game.switches['clan_name']) == 0:
            self.first_phase()
        elif len(game.switches['clan_name']) > 0 and game.switches['leader'] is None:
            self.second_phase()
        elif game.switches['leader'] is not None and game.switches['deputy'] is None:
            self.third_phase()
        elif game.switches['leader'] is not None and game.switches['deputy'] is not None and game.switches['medicine_cat'] is None:
            self.fourth_phase()
        else:
            self.fifth_phase()

    def screen_switches(self):
        game.switches['clan_name'] = ''
        writer.upper = True
        game.switches['leader'] = None
        game.switches['cat'] = None
        game.switches['medicine_cat'] = None
        game.switches['deputy'] = None
        game.switches['members'] = []
        example_cats()


class ClanCreatedScreen(Screens):
    def on_use(self):
        # LAYOUT
        verdana.text('Your clan has been created and saved!', ('center', 50))
        game.clan.leader.draw_big((screen_x / 2 - 50, 100))

        # buttons
        buttons.draw_button(('center', 250), text='Continue', cur_screen='clan screen')

    def screen_switches(self):
        game.clan = Clan(game.switches['clan_name'], game.choose_cats[game.switches['leader']], game.choose_cats[game.switches['deputy']],
                         game.choose_cats[game.switches['medicine_cat']])
        game.clan.create_clan()


class EventsScreen(Screens):
    def on_use(self):
        # LAYOUT
        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('Check this page to see which events are currently happening at the clan.', ('center', 100))
        verdana.text('Current season: ' + str(game.clan.current_season), ('center', 130))
        verdana.text('Clan age: ' + str(game.clan.age) + ' moons', ('center', 160))

        if game.switches['events_left'] == 0:
            buttons.draw_button(('center', 220), text='TIMESKIP ONE MOON', timeskip=True)
            if game.switches['timeskip']:
                game.cur_events_list = []
        else:
            buttons.draw_button(('center', 220), text='TIMESKIP ONE MOON', available=False)
        events_class.one_moon()

        # Maximum events on the screen is 12
        a = 0

        if game.cur_events_list is not None and game.cur_events_list != []:
            for x in range(min(len(game.cur_events_list), game.max_events_displayed)):
                if game.cur_events_list[x] == None:
                    continue
                if "Clan has no " in game.cur_events_list[x]:
                    verdana_red.text(game.cur_events_list[x], ('center', 260 + a * 30))
                else:
                    verdana.text(game.cur_events_list[x], ('center', 260 + a * 30))
                a += 1
        else:
            verdana.text("Nothing significant happened this moon.", ('center', 260 + a * 30))
        # buttons
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
        verdana_big.text(cat_name, ('center', 70))  # NAME
        the_cat.draw_large(('center', 100))  # IMAGE
        verdana.text(cat_thought, ('center', 300))  # THOUGHT / ACTION
        verdana_small.text(the_cat.gender, (250, 330 + count * 15));
        count += 1  # SEX / GENDER
        verdana_small.text(the_cat.status, (450, 330 + count2 * 15));
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is None:
                the_cat.update_mentor()
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name), (450, 330 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            apps = ''
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
            former_apps = ''
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
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(), (250, 330 + count * 15));
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(), (250, 330 + count * 15));
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length, (250, 330 + count * 15));
        count += 1  # PELT LENGTH

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (250, 330 + count * 15));
            count += 1
        elif the_cat.parent2 is None:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown', (250, 330 + count * 15));
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
            verdana_small.text('experience: ' + str(the_cat.experience_level), (450, 330 + count2 * 15));
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level), (450, 330 + count2 * 15));
            count2 += 1

        # buttons
        buttons.draw_button(('center', 10), text=' Change Name ', cur_screen='change name screen')
        game.switches['cat'] = the_cat.ID
        buttons.draw_button((300, -160), text='See Family', cur_screen='see kits screen')
        if not the_cat.dead:
            buttons.draw_button((-300, -160), text='Kill Cat', kill_cat=the_cat)
        if the_cat.status == 'apprentice' and not the_cat.dead:
            game.switches['apprentice'] = the_cat
            buttons.draw_button(('center', -130), text='Change Mentor', cur_screen='choose mentor screen')
        # buttons.draw_button(('center', -130), text='Family Tree')
        if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'] and not the_cat.dead:
            buttons.draw_button(('center', -130), text='Pick mate for ' + str(the_cat.name), cur_screen='choose mate screen')

        if game.switches['new_leader'] is not False and game.switches['new_leader'] is not None:
            game.clan.new_leader(game.switches['new_leader'])

        if the_cat.status in ['warrior'] and not the_cat.dead and game.clan.leader.dead:
            buttons.draw_button(('center', -70), text='Promote to Leader', new_leader=the_cat)
        elif the_cat.status in ['warrior'] and not the_cat.dead and game.clan.deputy is None:
            buttons.draw_button(('center', -70), text='Promote to Deputy', deputy_switch=the_cat)
        elif the_cat.status in ['deputy'] and not the_cat.dead:
            buttons.draw_button(('center', -70), text='Demote from Deputy', deputy_switch=the_cat)
        elif the_cat.status in ['warrior'] and not the_cat.dead and game.clan.deputy:
            if game.clan.deputy.dead:
                buttons.draw_button(('center', -70), text='Promote to Deputy', deputy_switch=the_cat)

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

        if game.switches['kill_cat'] is not False and game.switches['kill_cat'] is not None:
            events_class.dies(game.switches['kill_cat'])
            game.switches['kill_cat'] = False

        if the_cat.status in ['apprentice'] and not the_cat.dead:
            buttons.draw_button(('center', -70), text='Switch to medicine cat apprentice', apprentice_switch=the_cat)

        if the_cat.status in ['medicine cat apprentice'] and not the_cat.dead:
            buttons.draw_button(('center', -70), text='Switch to warrior apprentice', apprentice_switch=the_cat)

        buttons.draw_button(('center', -100), text='Back', cur_screen=game.switches['last_screen'])

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

        verdana_big.text('Family of ' + str(the_cat.name), ('center', 50))

        verdana.text('Parents:', ('center', 85))
        # the_cat.all_cats[the_cat.parent1].name
        if the_cat.parent1 is None:
            verdana_small.text('Unknown', (342, 165))
        elif the_cat.parent1 in cat_class.all_cats:
            buttons.draw_button((350, 120), image=cat_class.all_cats[the_cat.parent1].sprite, cat=the_cat.parent1, cur_screen='profile screen')
            name_len = verdana.text(str(cat_class.all_cats[the_cat.parent1].name))
            verdana_small.text(str(cat_class.all_cats[the_cat.parent1].name), (375 - name_len / 2, 185))
        else:
            verdana_small.text('Error: cat ' + str(the_cat.parent1) + ' not found', (342, 165))

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
            if (cat_class.all_cats[x].parent1 in (the_cat.parent1, the_cat.parent2) or (
                    cat_class.all_cats[x].parent2 in (the_cat.parent1, the_cat.parent2) and the_cat.parent2 is not None)) and the_cat.ID != cat_class.all_cats[
                x].ID and the_cat.parent1 is not None and cat_class.all_cats[x].parent1 is not None:
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
        # use this variable to point to the cat object in question
        the_cat = cat_class.all_cats[game.switches['cat']]

        # LAYOUT
        # cat's info
        verdana_big.text('Choose mate for ' + str(the_cat.name), ('center', 50))
        verdana_small.text('If the cat has chosen a mate, they will stay loyal and not have kittens with anyone else,', ('center', 80))
        verdana_small.text('even if having kittens in said relationship is impossible.', ('center', 95))
        verdana_small.text('Chances of having kittens when possible is heightened though.', ('center', 110))
        the_cat.draw_large((200, 130))
        verdana_small.text(the_cat.age, (70, 200))
        verdana_small.text(the_cat.gender, (70, 215))
        verdana_small.text(the_cat.trait, (70, 230))

        # mate's/potential mate's info
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
            verdana_small.text(mate.age, (-100, 200))
            verdana_small.text(mate.gender, (-100, 215))
            verdana_small.text(mate.trait, (-100, 230))

            if the_cat.gender == mate.gender or 'elder' in [the_cat.age, mate.age]:
                if the_cat.gender == mate.gender and not game.settings['no gendered breeding']:
                    verdana_small.text('(this pair will not be able to have kittens)', ('center', 320))

        valid_mates = []
        pos_x = 0
        pos_y = 20
        if the_cat.mate is None:  # if the cat doesn't already have a mate

            for x in game.clan.clan_cats:
                # possible mate as a Cat object
                pos_mate = cat_class.all_cats[x]

                # makign sure the pairing is possible and appropriate
                if not pos_mate.dead and pos_mate.age in ['young adult', 'adult', 'senior adult', 'elder'] and the_cat != pos_mate and the_cat.ID not in [pos_mate.parent1,
                                                                                                                                                          pos_mate.parent2] and \
                        pos_mate.ID not in [
                    the_cat.parent1, the_cat.parent2] and pos_mate.mate is None and (pos_mate.parent1 is None or pos_mate.parent1 not in [the_cat.parent1, the_cat.parent2]) and (
                        pos_mate.parent2 is None or pos_mate.parent2 not in [the_cat.parent1, the_cat.parent2]):

                    # Making sure the ages are appropriate
                    if (the_cat.age in ['senior adult', 'elder'] and cat_class.all_cats[x].age in ['senior adult', 'elder']) or (
                            cat_class.all_cats[x].age != 'elder' and cat_class.all_cats[x].age != 'adolescent' and the_cat.age != 'elder' and the_cat.age != 'adolescent'):
                        valid_mates.append(cat_class.all_cats[x])

            all_pages = 1  # amount of pages
            if len(valid_mates) > 27:
                all_pages = int(ceil(len(valid_mates) / 27.0))

                # dead cats

            cats_on_page = 0  # how many are on page already
            for x in range(len(valid_mates)):
                if (x + (game.switches['list_page'] - 1) * 27) > len(valid_mates):
                    game.switches['list_page'] = 1
                pot_mate = valid_mates[x + (game.switches['list_page'] - 1) * 27]
                ## draw mates
                buttons.draw_button((100 + pos_x, 320 + pos_y), image=pot_mate.sprite, mate=pot_mate.ID)
                pos_x += 50
                cats_on_page += 1
                if pos_x > 400:
                    pos_y += 50
                    pos_x = 0
                if cats_on_page >= 27 or x + (game.switches['list_page'] - 1) * 27 == len(valid_mates) - 1:
                    break

            # page buttons
            verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))
            if game.switches['list_page'] > 1:
                buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)
            if game.switches['list_page'] < all_pages:
                buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)





        else:
            verdana.text('Already in a relationship.', ('center', 340))
            # draw kittens, if any
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

        # buttons
        if mate is not None and the_cat.mate is None:
            buttons.draw_button(('center', -130), text="It\'s official!", cat_value=the_cat, mate=mate)
        elif the_cat.mate is not None:
            buttons.draw_button(('center', -130), text="Break it up...", cat_value=the_cat, mate=None)
        buttons.draw_button(('center', -100), text='Back', cur_screen='profile screen')

    def screen_switches(self):
        game.switches['mate'] = None
        cat_profiles()


class ListScreen(Screens):
    # page can be found in game.switches['list_page']
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20

    def on_use(self):
        # layout
        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('ALL CATS LIST', ('center', 100))

        # make a list of just living cats
        living_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead:
                living_cats.append(the_cat)

        # pages
        all_pages = 1  # amount of pages
        if len(living_cats) > 24:
            all_pages = int(ceil(len(living_cats) / 24.0))

        # dead cats
        pos_x = 0
        pos_y = 0
        cats_on_page = 0  # how many are on page already
        for x in range(len(living_cats)):
            if (x + (game.switches['list_page'] - 1) * 24) >= len(living_cats):
                game.switches['list_page'] -= 1 

            the_cat = living_cats[x + (game.switches['list_page'] - 1) * 24]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y), image=the_cat.sprite, cat=the_cat.ID, cur_screen='profile screen')
                # name length
                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name), (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

                if cats_on_page >= 24 or x + (game.switches['list_page'] - 1) * 24 == len(living_cats) - 1:
                    break

        # page buttons
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))
        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)
        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

        # buttons
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
        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('These cats are currently in the camp, ready for a patrol.', ('center', 115))
        verdana.text('Choose up to six to take on patrol.', ('center', 135))
        verdana.text('Smaller patrols help cats gain more experience, but larger patrols are safer.', ('center', 155))

        # buttons
        draw_menu_buttons()

        # make a list of patrol eligible cats
        able_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead and the_cat.in_camp:
                if the_cat.status in ['leader', 'deputy', 'warrior', 'apprentice']:
                    able_cats.append(the_cat)

        # pick up to 12 random cats (warriors/leader/deputy/apprentice) from the clan
        if not game.patrol_cats:
            if len(able_cats) < 12:
                i_max = len(able_cats)
            else:
                i_max = 12

            for i in range(i_max):
                test_cat = random.choice(able_cats)
                able_cats.remove(test_cat)
                game.patrol_cats[i] = test_cat
        else:
            i_max = len(game.patrol_cats)

        random_options = []
        # cat buttons / small sprites
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

        if len(random_options) > 0 and len(game.switches['current_patrol']) < 6:
            random_patrol = choice(random_options)
            buttons.draw_button(('center', 530), text='Add Random', current_patrol=random_patrol, add=True)
        else:
            buttons.draw_button(('center', 530), text='Add Random', available=False)

        # display cat profile
        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0 and game.patrol_cats[game.switches['cat']] not in game.switches['current_patrol']:
            game.patrol_cats[game.switches['cat']].draw_large((320, 200))
            verdana.text(str(game.patrol_cats[game.switches['cat']].name), ('center', 360))
            verdana_small.text(str(game.patrol_cats[game.switches['cat']].status), (330, 385))
            verdana_small.text(str(game.patrol_cats[game.switches['cat']].trait), (330, 405))
            verdana_small.text(str(game.patrol_cats[game.switches['cat']].skill), (330, 425))
            verdana_small.text('experience: ' + str(game.patrol_cats[game.switches['cat']].experience_level), (330, 445))

            if len(game.switches['current_patrol']) < 6:
                buttons.draw_button(('center', 490), text='Add to Patrol', current_patrol=game.patrol_cats[game.switches['cat']], add=True)

        if len(game.switches['current_patrol']) > 0:
            buttons.draw_button(('center', 630), text='Start Patrol', cur_screen='patrol event screen')
        else:
            buttons.draw_button(('center', 630), text='Start Patrol', available=False)

    def screen_switches(self):
        game.switches['current_patrol'] = []
        game.switches['cat'] = None
        game.patrol_cats = {}
        game.switches['event'] = 0
        cat_profiles()


class PatrolEventScreen(Screens):
    def on_use(self):
        # LAYOUT

        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        if game.switches['event'] == 0:
            verdana.text(str(patrol.patrol_event[1]), ('center', 200))

            buttons.draw_button(('center', 300), text='Proceed', event=1)
            buttons.draw_button(('center', 340), text='Do Not Proceed', event=2)

        if game.switches['event'] > 0:
            if game.switches['event'] < 3:
                patrol.calculate()
            verdana.text(str(patrol.patrol_result_text), ('center', 200))
            buttons.draw_button(('center', 320), text='Return to Clan', cur_screen='clan screen')

        # cat buttons / small sprites
        for u in range(6):
            if u < patrol.patrol_size:
                patrol.patrol_cats[u].draw((screen_x / 2 - 50 * (u + 2), 550))
        verdana_small.text('season: ' + str(game.clan.current_season), ('center', 400))
        verdana_small.text('patrol leader: ' + str(patrol.patrol_leader.name), ('center', 420))
        verdana_small.text('patrol skills: ' + str(patrol.patrol_skills), ('center', 440))
        verdana_small.text('patrol traits: ' + str(patrol.patrol_traits), ('center', 460))

        # buttons
        draw_menu_buttons()

    def screen_switches(self):
        patrol.new_patrol()
        game.switches['event'] = 0
        cat_profiles()


class AllegiancesScreen(Screens):
    def on_use(self):
        # layout
        verdana_big.text(game.clan.name + 'Clan Allegiances', (30, 110))

        a = 0
        if game.allegiance_list is not None and game.allegiance_list != []:
            for x in range(min(len(game.allegiance_list), game.max_allegiance_displayed)):
                if game.allegiance_list[x] == None:
                    continue
                else:
                    verdana.text(game.allegiance_list[x][0], (30, 140 + a * 30))
                    verdana.text(game.allegiance_list[x][1], (170, 140 + a * 30))
                a += 1

        if len(game.allegiance_list) > game.max_allegiance_displayed:
            buttons.draw_button((720, 250), image=game.up, arrow="UP")
            buttons.draw_button((700, 550), image=game.down, arrow="DOWN")

        draw_menu_buttons()

    def screen_switches(self):
        # make a list of just living cats
        living_cats = []
        game.allegiance_scroll_ct = 0
        game.allegiance_list = []
        dep = None
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if the_cat.status == 'deputy':
                dep = the_cat
            elif not the_cat.dead:
                living_cats.append(the_cat)

        if not game.clan.leader.dead:
            game.allegiance_list.append(['LEADER:', str(game.clan.leader.name) + " - a " + game.clan.leader.describe_cat()])
        else:
            game.allegiance_list.append(['LEADER:', ''])

        if game.clan.deputy != 0 and game.clan.deputy is not None and not game.clan.deputy.dead:
            game.allegiance_list.append(['DEPUTY:', str(game.clan.deputy.name) + " - a " + game.clan.deputy.describe_cat()])
        else:
            game.allegiance_list.append(['DEPUTY:', ''])

        cat_count = 0
        for j in range(len(living_cats)):
            if str(living_cats[j].status) == 'medicine cat':
                if not cat_count:
                    game.allegiance_list.append(['MEDICINE CAT:', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                else:
                    game.allegiance_list.append(['', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])

                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['MEDICINE CAT:', ''])

        queens = []
        for j in range(len(living_cats)):
            if str(living_cats[j].status) == 'kitten':
                if living_cats[j].parent1 is not None:
                    if cat_class.all_cats[living_cats[j].parent1].gender == 'male':
                        if living_cats[j].parent2 is None or cat_class.all_cats[living_cats[j].parent2].gender == 'male':
                            queens.append(living_cats[j].parent1)
                        elif cat_class.all_cats[living_cats[j].parent2].gender == 'male':
                            queens.append(living_cats[j].parent2)
                    else:
                        queens.append(living_cats[j].parent1)

        cat_count = 0
        for j in range(len(living_cats)):
            if str(living_cats[j].status) == 'warrior' and living_cats[j].ID not in queens:
                if not cat_count:
                    game.allegiance_list.append(['WARRIORS:', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                else:
                    game.allegiance_list.append(['', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['WARRIORS:', ''])

        cat_count = 0
        for j in range(len(living_cats)):
            if str(living_cats[j].status) == 'apprentice' or str(living_cats[j].status) == 'medicine cat apprentice':
                if not cat_count:
                    game.allegiance_list.append(['APPRENTICES:', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                else:
                    game.allegiance_list.append(['', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['APPRENTICES:', ''])

        cat_count = 0
        for j in range(len(living_cats)):
            if living_cats[j].ID in queens:
                if not cat_count:
                    game.allegiance_list.append(['QUEENS:', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                else:
                    game.allegiance_list.append(['', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['QUEENS:', ''])

        cat_count = 0
        for j in range(len(living_cats)):
            if str(living_cats[j].status) == 'elder':
                if not cat_count:
                    game.allegiance_list.append(['ELDERS:', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                else:
                    game.allegiance_list.append(['', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['ELDERS:', ''])

        cat_count = 0
        for j in range(len(living_cats)):
            if str(living_cats[j].status) == 'kitten':
                if not cat_count:
                    game.allegiance_list.append(['KITS:', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                else:
                    game.allegiance_list.append(['', str(living_cats[j].name) + " - a " + living_cats[j].describe_cat()])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['KITS:', ''])

        # buttons
        draw_menu_buttons()


class ChooseMentorScreen(Screens):
    def on_use(self):
        # layout
        verdana_big.text('Choose Mentor', ('center', 30))
        # make a list of just living cats
        living_cats = []
        for cat in cat_class.all_cats.values():
            if not cat.dead and cat != game.switches['apprentice'].mentor and (cat.status == 'warrior' or cat.status == 'deputy' or cat.status == 'leader'):
                living_cats.append(cat)

        # pages
        all_pages = 1  # amount of pages
        if len(living_cats) > 24:
            all_pages = int(ceil(len(living_cats) / 24.0))

        # dead cats
        pos_x = 0
        pos_y = 0
        cats_on_page = 0  # how many are on page already
        for x in range(len(living_cats)):
            if (x + (game.switches['list_page'] - 1) * 24) > len(living_cats):
                game.switches['list_page'] = 1

            the_cat = living_cats[x + (game.switches['list_page'] - 1) * 24]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y), image=the_cat.sprite, cat=the_cat.ID, cur_screen='choose mentor screen2')
                # name length
                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name), (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100

                if cats_on_page >= 24 or x + (game.switches['list_page'] - 1) * 24 == len(living_cats) - 1:
                    break

        # page buttons
        verdana.text('page ' + str(game.switches['list_page']) + ' / ' + str(all_pages), ('center', 600))
        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600), text='<', list_page=game.switches['list_page'] - 1)
        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600), text='>', list_page=game.switches['list_page'] + 1)

        # buttons
        draw_menu_buttons()


class ChooseMentorScreen2(Screens):
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

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 70))  # NAME
        the_cat.draw_large(('center', 100))  # IMAGE
        verdana_small.text(the_cat.gender, (250, 330 + count * 15));
        count += 1  # SEX / GENDER
        verdana_small.text(the_cat.status, (450, 330 + count2 * 15));
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name), (450, 330 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            apps = ''
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
            former_apps = ''
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
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(), (250, 330 + count * 15));
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(), (250, 330 + count * 15));
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length, (250, 330 + count * 15));
        count += 1  # PELT LENGTH

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (250, 330 + count * 15));
            count += 1
        elif the_cat.parent2 is None:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown', (250, 330 + count * 15));
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
            verdana_small.text('experience: ' + str(the_cat.experience_level), (450, 330 + count2 * 15));
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level), (450, 330 + count2 * 15));
            count2 += 1

        # buttons

        buttons.draw_button(('center', -100), text='Choose as ' + str(game.switches['apprentice'].name) + '\'s mentor', cur_screen=game.switches['last_screen'], cat_value=the_cat,
                            apprentice=game.switches['apprentice'])
        buttons.draw_button(('center', -50), text='Back', cur_screen='clan screen')


class ChangeNameScreen(Screens):
    def on_use(self):
        if game.settings['dark mode']:
            verdana_black.text(game.switches['naming_text'], (315, 200))
        else:
            verdana.text(game.switches['naming_text'], (315, 200))
        verdana.text('Change Name', ('center', 50))
        buttons.draw_button(('center', -100), text='Change Name', cur_screen='change name screen', cat_value=game.switches['cat'], name=game.switches['naming_text'])
        buttons.draw_button(('center', -50), text='Back', cur_screen=game.switches['last_screen'])




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
