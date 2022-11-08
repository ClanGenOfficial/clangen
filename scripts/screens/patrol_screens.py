from math import ceil
from random import choice, choices

from .base_screens import Screens, draw_menu_buttons, cat_profiles, draw_clan_name

from scripts.utility import draw, draw_large, draw_big
from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat

class PatrolScreen(Screens):

    able_box = pygame.image.load("resources/images/patrol_able_cats.png").convert_alpha()
    patrol_box = pygame.image.load("resources/images/patrol_cats.png").convert_alpha()
    cat_frame = pygame.image.load("resources/images/patrol_cat_frame.png").convert_alpha()
    app_frame = pygame.image.load("resources/images/patrol_app_frame.png").convert_alpha()
    mate_frame = pygame.image.load("resources/images/patrol_mate_frame.png").convert_alpha()

    def on_use(self):
        # USER INTERFACE
        draw_clan_name()
        y_value = 110
        verdana.text(
            'Chose up to six cats to take on patrol.',
            ('center', y_value))
        y_value += 20
        verdana.text(
            'Smaller patrols help cats gain more experience, but larger patrols are safer.',
            ('center', y_value))

        screen.blit(PatrolScreen.able_box, (40, 460))
        screen.blit(PatrolScreen.patrol_box, (490, 460))
        screen.blit(PatrolScreen.cat_frame, (300, 165))

        draw_menu_buttons()

        # CATS WHO CAN PATROL
        able_cats = []


        # ASSIGN TO ABLE CATS AND SORT BY RANK
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and the_cat.in_camp and the_cat not in game.patrolled and the_cat.status in [
                    'leader', 'deputy', 'warrior', 'apprentice'
            ] and not the_cat.exiled and the_cat not in game.switches['current_patrol']:
                if the_cat.status == 'leader':
                    able_cats.insert(0, the_cat)
                elif the_cat.status == 'deputy':
                    able_cats.insert(1, the_cat)
                elif the_cat.status == 'warrior':
                    able_cats.insert(2, the_cat)
                elif the_cat.status == 'apprentice':
                    able_cats.append(the_cat)

        # PAGE COUNT
        all_pages = 1
        if len(able_cats) > 15:
            all_pages = int(ceil(len(able_cats) / 15.0))

        # CATS ON PAGE COUNT
        cats_on_page = 0

        # POSITION OF ABLE CAT SPRITES START
        pos_y = 500
        pos_x = 50


        # DRAW ABLE CATS
        for x in range(len(able_cats)):
            if x + (game.switches['list_page'] - 1) * 15 > len(able_cats):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1

            patrol_cat = able_cats[x + (game.switches['list_page'] - 1) * 15]

            if patrol_cat not in game.switches['current_patrol']:
                buttons.draw_button((0 + pos_x, pos_y),
                                    image=patrol_cat.sprite,
                                    cat=patrol_cat,
                                    hotkey=[x + 1, 11])
            else:
                cats_on_page -= 1
                pos_x -= 50

            cats_on_page += 1
            pos_x += 50
            if pos_x >= 300:
                pos_x = 50
                pos_y += 50
            if cats_on_page >= 15 or x + (game.switches['list_page'] - 1) * 15 == len(able_cats) - 1:
                break

        # CAT LIST ARROWS
        if game.switches['list_page'] > 1:
            buttons.draw_image_button((75, 462),
                                      button_name='patrol_arrow_l',
                                      text='<',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] - 1,
                                      hotkey=[23]
                                      )
        else:
            buttons.draw_image_button((75, 462),
                                      button_name='patrol_arrow_l',
                                      text='<',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] - 1,
                                      hotkey=[23],
                                      available=False
                                      )

        if game.switches['list_page'] < all_pages:
            buttons.draw_image_button((241, 462),
                                      button_name='patrol_arrow_r',
                                      text='>',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] + 1,
                                      hotkey=[21]
                                      )
        else:
            buttons.draw_image_button((241, 462),
                                      button_name='patrol_arrow_r',
                                      text='>',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] + 1,
                                      hotkey=[21],
                                      available=False
                                      )

        # CURRENT PATROL CAT SPRITE START
        pos_y1 = 508
        pos_x1 = 525

        # DRAW CURRENT PATROL CAT SPRITES
        if game.switches['show_info'] is False:
            for x in range(len(game.switches['current_patrol'])):

                patrol_cat = game.switches['current_patrol'][x]
                game.switches['patrol_remove'] = False

                buttons.draw_button((0 + pos_x1, 0 + pos_y1),
                                    image=patrol_cat.sprite,
                                    patrol_remove=True,
                                    )
                if game.switches['patrol_remove'] is True:
                    game.switches['cat'] = patrol_cat

                pos_x1 += 75
                if pos_x1 >= 725:
                    pos_x1 = 525
                    pos_y1 += 50



        # REMOVE ALL CATS FROM CURRENT PATROL LIST
        buttons.draw_image_button((560, 627),
                                  button_name='remove_all',
                                  size=(124, 35),
                                  current_patrol=[],
                                  )

        # BUTTON TO SHOW SPRITES OF CATS IN CURRENT PATROL
        buttons.draw_image_button((505, 460),
                                  button_name='patrol2',
                                  size=(80, 35),
                                  show_info=False
                                  )
        # BUTTON TO SHOW SKILLS AND TRAITS OF CATS IN CURRENT PATROL
        buttons.draw_image_button((590, 460),
                                  button_name='skills_traits',
                                  size=(154, 35),
                                  show_info=True
                                  )

        # PATROL TYPE BUTTONS - purely aesthetic atm until we have patrol type functionality
        if game.game_mode != 'classic':
            x_value = 323
            y_value = 550
            buttons.draw_image_button((x_value, y_value),
                                      button_name='button_paw',
                                      size=(34, 34),
                                      available=False
                                      )
            x_value += 40
            buttons.draw_image_button((x_value, y_value),
                                      button_name='button_mouse',
                                      size=(34, 34),
                                      available=False
                                      )
            x_value += 40
            buttons.draw_image_button((x_value, y_value),
                                      button_name='button_claws',
                                      size=(34, 34),
                                      available=False
                                      )
            x_value += 40
            buttons.draw_image_button((x_value, y_value),
                                      button_name='button_herb',
                                      size=(34, 34),
                                      available=False
                                      )

        # SHOW CAT INFO
        if game.switches['cat'] is not None:
            self.show_info(able_cats)

        # DRAW GREYED OUT ADD CAT BUTTON IF NO CAT SELECTED
        else:
            buttons.draw_button(
                ('center', 460),
                image='buttons/add_cat',
                text='Add to Patrol',
                available=False)

        # ---------------------------------------------------------------------------- #
        #                             roll a random cat                                #
        # ---------------------------------------------------------------------------- #
        # DRAW AVAILABLE RANDOM ROLL BUTTON IF AT LEAST TWO CATS ARE IN ABLE CATS
        if len(game.switches['current_patrol']) < 6 and len(able_cats) > 1:
            buttons.draw_image_button((323, 495),
                                      button_name='random_dice',
                                      size=(34, 34),
                                      cat=choice(able_cats),
                                      hotkey=[12])

        # DRAW AVAILABLE RANDOM ROLL BUTTON IF ONLY ONE CAT IS IN ABLE CATS
        elif len(game.switches['current_patrol']) < 6 and len(able_cats) == 1:
            buttons.draw_image_button((323, 495),
                                      button_name='random_dice',
                                      size=(34, 34),
                                      cat=able_cats[0],
                                      hotkey=[12])
        else:
            buttons.draw_image_button((323, 495),
                                      button_name='random_dice',
                                      size=(34, 34),
                                      hotkey=[12],
                                      available=False)

        # ---------------------------------------------------------------------------- #
        #                         add 1 random cat to patrol                           #
        # ---------------------------------------------------------------------------- #
        # DRAW ADD 1 RANDOM CAT BUTTON IF PATROL STILL HAS SPACE
        if len(game.switches['current_patrol']) <= 5 and len(able_cats) >= 1:
            buttons.draw_button((363, 495),
                                image='buttons/add_1',
                                text='add 1',
                                cat=choice(able_cats),
                                fill_patrol=True)

            if game.switches['fill_patrol'] is True:
                game.switches['current_patrol'].append(game.switches['cat'])
                game.switches['fill_patrol'] = False

        # DRAW ADD 1 RANDOM CAT BUTTON IF ONLY ONE CAT IS IN ABLE CATS
        elif len(game.switches['current_patrol']) < 6 and len(able_cats) == 1:
            buttons.draw_button((403, 495),
                                image='buttons/add_1',
                                text='add 1',
                                cat=able_cats[0],
                                fill_patrol=True)

            if game.switches['fill_patrol'] is True:
                game.switches['current_patrol'].append(game.switches['cat'])
                game.switches['fill_patrol'] = False

        else:
            buttons.draw_button((363, 495),
                                image='buttons/add_1',
                                text='add 1',
                                available=False)

        # ---------------------------------------------------------------------------- #
        #                        add 3 random cats to patrol                           #
        # ---------------------------------------------------------------------------- #
        # DRAW ADD 3 RANDOM CATS BUTTON IF PATROL STILL HAS SPACE
        if len(game.switches['current_patrol']) <= 3 and len(able_cats) > 3:
            buttons.draw_image_button((403, 495),
                                      button_name='add_3',
                                      size=(34, 34),
                                      fill_patrol=True,)

            if game.switches['fill_patrol'] is True:
                count = 3
                for x in range(count):
                    random_cat = choice(able_cats)
                    if random_cat not in game.switches['current_patrol']:
                        game.switches['current_patrol'].append(random_cat)
                        able_cats.remove(random_cat)

                game.switches['fill_patrol'] = False

        elif len(game.switches['current_patrol']) <= 3 and len(able_cats) == 3:
            buttons.draw_image_button((403, 495),
                                      button_name='add_3',
                                      size=(34, 34),
                                      fill_patrol=True, )

            if game.switches['fill_patrol'] is True:
                for x in range(3):
                    random_cat = able_cats[x]
                    game.switches['current_patrol'].append(random_cat)

                game.switches['fill_patrol'] = False
        else:
            buttons.draw_image_button((403, 495),
                                      button_name='add_3',
                                      size=(34, 34),
                                      available=False)

        # ---------------------------------------------------------------------------- #
        #                        add 6 random cats to patrol                           #
        # ---------------------------------------------------------------------------- #
        # DRAW ADD 6 RANDOM CATS BUTTON IF PATROL STILL HAS SPACE
        if len(game.switches['current_patrol']) == 0 and len(able_cats) > 6:
            buttons.draw_image_button((443, 495),
                                      button_name='add_6',
                                      size=(34, 34),
                                      fill_patrol=True,)
            if game.switches['fill_patrol'] is True:
                for x in range(6):
                    random_cat = choice(able_cats)
                    game.switches['current_patrol'].append(random_cat)
                    able_cats.remove(random_cat)

                game.switches['fill_patrol'] = False

        elif len(game.switches['current_patrol']) == 0 and len(able_cats) == 6:
            buttons.draw_image_button((443, 495),
                                      button_name='add_6',
                                      size=(34, 34),
                                      fill_patrol=True,)
            if game.switches['fill_patrol'] is True:
                for x in range(6):
                    random_cat = able_cats[x]
                    game.switches['current_patrol'].append(random_cat)

                game.switches['fill_patrol'] = False
        else:
            buttons.draw_image_button((443, 495),
                                      button_name='add_6',
                                      size=(34, 34),
                                      available=False)

        # ---------------------------------------------------------------------------- #
        #                                 go on patrol                                 #
        # ---------------------------------------------------------------------------- #
        if len(game.switches['current_patrol']) > 0:
            buttons.draw_button(('center', 589),
                                image='buttons/go_patrol',
                                text='Start Patrol',
                                cur_screen='patrol event screen',
                                hotkey=[13])
        else:
            buttons.draw_button(('center', 589),
                                image='buttons/go_patrol',
                                text='Start Patrol',
                                available=False)

    def show_info(self, able_cats):

        # ---------------------------------------------------------------------------- #
        #                               info on chosen cat                             #
        # ---------------------------------------------------------------------------- #
        # CHOSEN CAT INFO
        chosen_cat = game.switches['cat']  # cat

        y_value = 175
        draw_large(chosen_cat, (320, y_value))  # sprite

        y_value += 150

        name = str(chosen_cat.name)  # get name
        if 14 <= len(name) >= 16:  # check name length
            short_name = str(chosen_cat.name)[0:15]
            name = short_name + '...'

        verdana.text(str(name),  # display name
                     ('center', y_value),
                     x_start=320,
                     x_limit=480)

        y_value += 25

        verdana_small.text(str(chosen_cat.status),  # rank
                           ('center', y_value))
        y_value += 15

        verdana_small.text(str(chosen_cat.trait),  # trait
                           ('center', y_value))
        y_value += 15

        verdana_small.text(str(chosen_cat.skill),  # skill
                           ('center', y_value))
        y_value += 15

        verdana_small.text(
            'experience: ' +
            str(chosen_cat.experience_level),  # exp
            ('center', y_value))
        y_value += 15

        # ---------------------------------------------------------------------------- #
        #                         show mate if they have one                           #
        # ---------------------------------------------------------------------------- #
        # SHOW MATE SPRITE AND BUTTON
        if chosen_cat.status != 'apprentice':
            if chosen_cat.mate is not None:
                mate = Cat.all_cats[chosen_cat.mate]
                screen.blit(PatrolScreen.mate_frame, (140, 190))
                draw_big(mate, (150, 200))
                if mate in able_cats:
                    buttons.draw_image_button(
                        (148, 356),
                        button_name='patrol_select',
                        size=(104, 26),
                        cat=mate
                        )
                else:
                    buttons.draw_image_button(
                        (148, 356),
                        button_name='patrol_select',
                        size=(104, 26),
                        cat=mate,
                        available=False
                        )
                name = str(mate.name)  # get name
                if 10 <= len(name) >= 12:  # check name length
                    short_name = str(mate.name)[0:9]
                    name = short_name + '...'
                verdana.text(str(name),
                             ('center', 310),
                             x_start=150,
                             x_limit=250)
                verdana_small.text('mate',
                             ('center', 330),
                             x_start=150,
                             x_limit=250)
        # ---------------------------------------------------------------------------- #
        #                        show mentor if they have one                          #
        # ---------------------------------------------------------------------------- #
        # SHOW MENTOR SPRITE AND BUTTON
        if chosen_cat.status == 'apprentice':
            if chosen_cat.mentor is not None:
                screen.blit(PatrolScreen.app_frame, (494, 190))
                draw_big(chosen_cat.mentor, (550, 200))
                if chosen_cat.mentor in able_cats:
                    buttons.draw_image_button(
                        (548, 356),
                        button_name='patrol_select',
                        size=(104, 26),
                        cat=chosen_cat.mentor
                        )
                else:
                    buttons.draw_image_button(
                        (548, 356),
                        button_name='patrol_select',
                        size=(104, 26),
                        cat=chosen_cat.mentor,
                        available=False
                        )
                name = str(chosen_cat.mentor.name)  # get name
                if 10 <= len(name) >= 12:  # check name length
                    short_name = str(chosen_cat.mentor.name)[0:9]
                    name = short_name + '...'
                verdana.text(str(name),
                             ('center', 310),
                             x_start=550,
                             x_limit=650)
                verdana_small.text('mentor',
                             ('center', 330),
                             x_start=550,
                             x_limit=650)
                verdana_small.text(f'mentor: {str(chosen_cat.mentor.name)}', ('center', y_value))

        # ---------------------------------------------------------------------------- #
        #                     show apprentice if they have one                         #
        # ---------------------------------------------------------------------------- #
        # SHOW APPRENTICE SPRITE AND BUTTON
        if chosen_cat.apprentice != []:

            screen.blit(PatrolScreen.app_frame, (495, 190))
            draw_big(chosen_cat.apprentice[0], (550, 200))
            if chosen_cat.apprentice[0] in able_cats:
                buttons.draw_image_button(
                    (548, 356),
                    button_name='patrol_select',
                    size=(104, 26),
                    cat=chosen_cat.apprentice[0]
                    )
            else:
                buttons.draw_image_button(
                    (548, 356),
                    button_name='patrol_select',
                    size=(104, 26),
                    cat=chosen_cat.apprentice[0],
                    available=False
                    )
            name = str(chosen_cat.apprentice[0].name)  # get name
            if 10 <= len(name) >= 12:  # check name length
                short_name = str(chosen_cat.apprentice[0].name)[0:9]
                name = short_name + '...'
            verdana.text(str(name),
                              ('center', 310),
                              x_start=550,
                              x_limit=650)
            verdana_small.text('apprentice',
                              ('center', 330),
                              x_start=550,
                              x_limit=650)
        # ---------------------------------------------------------------------------- #
        #                 add and remove chosen cat from the patrol                    #
        # ---------------------------------------------------------------------------- #
        # BUTTON TO ADD CAT TO PATROL
        if len(game.switches['current_patrol']) < 6 and chosen_cat is not None\
                and chosen_cat not in game.switches['current_patrol'] and game.switches['patrol_remove'] is False:
            buttons.draw_button(
                ('center', 460),
                image='buttons/add_cat',
                text='Add to Patrol',
                current_patrol=chosen_cat,
                add=True,
                hotkey=[11],)

        # BUTTON TO REMOVE CAT FROM PATROL
        elif len(game.switches['current_patrol']) > 0 and chosen_cat is not None\
                and chosen_cat in game.switches['current_patrol']:
            buttons.draw_image_button((336, 460),
                                      button_name='remove_cat',
                                      size=(127, 30),
                                      cat_remove=True,
                                      )
            # REMOVE FROM PATROL, ADD TO ABLE CATS
            if game.switches['cat_remove'] is True:
                game.switches['current_patrol'].remove(chosen_cat)
                able_cats.append(chosen_cat)
                game.switches['patrol_remove'] = False
                game.switches['cat_remove'] = False

        # MAKE ADD CAT BUTTON UNAVAILABLE IF NO SPACE IS LEFT IN PATROL
        elif len(game.switches['current_patrol']) == 6 and chosen_cat not in game.switches['current_patrol']\
                and game.switches['patrol_remove'] is False:
            buttons.draw_button(
                ('center', 460),
                image='buttons/add_cat',
                text='Add to Patrol',
                current_patrol=chosen_cat,
                available=False,
                hotkey=[11],)

        # ---------------------------------------------------------------------------- #
        #                      show patrol skills and traits                           #
        # ---------------------------------------------------------------------------- #
        # SHOW CURRENT PATROL SKILLS AND TRAITS
        if game.switches['show_info'] is True:
            if game.switches['current_patrol'] is not []:
                patrol_skills = []
                patrol_traits = []
                for x in game.switches['current_patrol']:
                    if x.skill not in patrol_skills:
                        patrol_skills.append(x.skill)
                    if x.trait not in patrol_traits:
                        patrol_traits.append(x.trait)

                pos_x = 510
                pos_y = 510

                verdana_small_dark.blit_text(
                    f'current patrol skills: {self.get_list_text(patrol_skills)}',
                    (pos_x, pos_y),
                    x_limit=750
                )

                pos_y = 575

                verdana_small_dark.blit_text(
                    f'current patrol traits: {self.get_list_text(patrol_traits)}',
                    (pos_x, pos_y),
                    x_limit=750
                )

    def get_list_text(self, patrol_list):
        if not patrol_list:
            return ""
        patrol_set = list(patrol_list)
        return ", ".join(patrol_set)

    def screen_switches(self):
        game.switches['current_patrol'] = []
        game.switches['cat'] = None
        game.patrol_cats = {}
        game.switches['event'] = 0
        cat_profiles()
