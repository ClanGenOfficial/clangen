from math import ceil

from .base_screens import Screens, cat_profiles, draw_next_prev_cat_buttons

from scripts.utility import draw_large, draw, update_sprite, get_personality_compatibility
from scripts.game_structure.buttons import buttons
from scripts.game_structure.text import *
from scripts.cat.cats import Cat
import scripts.game_structure.image_cache as image_cache


def draw_choosing_bg(arg0, arg1):
    list_frame = image_cache.load_image("resources/images/choosing_frame.png").convert_alpha()
    cat1_frame_arg1 = image_cache.load_image(f"resources/images/choosing_cat1_frame_{arg1}.png").convert_alpha()
    cat2_frame_arg1 = image_cache.load_image(f"resources/images/choosing_cat2_frame_{arg1}.png").convert_alpha()

    y_value = 113

    screen.blit(list_frame, (75, 360))
    screen.blit(cat1_frame_arg1, (40, y_value))
    screen.blit(cat2_frame_arg1, (arg0, y_value))  # mate = 494, mentor = 480


class ChooseMentorScreen(Screens):

    def on_use(self):
        # APPRENTICE SELECTED
        the_cat = Cat.all_cats[game.switches['cat']]
        game.switches['apprentice'] = the_cat

        # USER INTERFACE
        draw_next_prev_cat_buttons(the_cat)
        draw_choosing_bg(480, 'ment')
        buttons.draw_image_button((25, 645),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  apprentice=None,
                                  )
        y_value = 30
        mentor = None
        verdana_big.text(f'Choose a new mentor for {str(the_cat.name)}',
                         ('center', y_value))
        y_value += 30
        verdana_small.text(f'If an apprentice is 6 moons old and their mentor is changed, they will',
                           ('center', y_value))
        y_value += 15
        verdana_small.text(f'not be listed as a former apprentice on their old mentor\'s profile.',
                           ('center', y_value))
        y_value += 15
        verdana_small.text(f'An apprentices mentor can have an influence on their trait and skill later in life.',
                           ('center', y_value))
        y_value += 15
        verdana_small.text(f'Choose your mentors wisely.',
                           ('center', y_value))
        y_value += 25
        verdana_small.text(f'{str(the_cat.name)}\'s current mentor is {str(the_cat.mentor.name)}.',
                           ('center', y_value))

        # DRAW APPRENTICE AND SHOW THEIR INFO
        if game.switches['apprentice'] is not None:
            draw_large(the_cat, (600, 150))
            show_mentor_cat_info(the_cat, 490, 620)

        # FIND MENTOR
        if game.switches['mentor'] is not None:
            mentor = Cat.all_cats[game.switches['mentor']]
        elif the_cat.mentor is not None:
            if the_cat.mentor in Cat.all_cats:
                mentor = Cat.all_cats[the_cat.mentor]

        # DRAW MENTOR AND SHOW THEIR INFO
        if mentor is not None and game.switches['apprentice'] is not None:
            draw_large(mentor, (50, 150))
            show_mentor_cat_info(mentor, 210, 71)

        valid_mentors = []
        pos_x = 0
        pos_y = 20

        if game.switches['apprentice'] is not None:
            self.get_valid_mentors(the_cat, valid_mentors, pos_x, pos_y)

        if mentor is not None and mentor != the_cat.mentor:
            buttons.draw_button(
                ('center', 310),
                image='buttons/change_mentor2',
                text='Change Mentor',
                cat_value=mentor,
                apprentice=the_cat)
        else:
            buttons.draw_button(
                ('center', 310),
                image='buttons/change_mentor2',
                text='Change Mentor',
                available=False)

    def get_valid_mentors(self, the_cat, valid_mentors, pos_x, pos_y):

        if the_cat.status == "apprentice":
            for cat in Cat.all_cats.values():
                if not cat.dead and not cat.exiled and cat.status in [
                            'warrior', 'deputy', 'leader'
                        ]:
                    valid_mentors.append(cat)
        elif the_cat.status == "medicine cat apprentice":
            for cat in Cat.all_cats.values():
                if not cat.dead and not cat.exiled and cat.status == 'medicine cat':
                    valid_mentors.append(cat)


        all_pages = 1
        if len(valid_mentors) > 30:
            all_pages = int(ceil(len(valid_mentors) / 30.0))

        cats_on_page = 0

        for x in range(len(valid_mentors)):
            if x + (game.switches['list_page'] - 1) * 30 > len(valid_mentors):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            new_mentor = valid_mentors[x + (game.switches['list_page'] - 1) * 30]
            if not new_mentor.dead or new_mentor.exiled:
                buttons.draw_button((100 + pos_x, 365 + pos_y),
                                    image=new_mentor.sprite,
                                    mentor=new_mentor.ID,
                                    )

                cats_on_page += 1
                pos_x += 60
                if pos_x >= 550:
                    pos_x = 0
                    pos_y += 60
                if cats_on_page >= 30 or x + (game.switches['list_page'] -
                                              1) * 30 == len(valid_mentors) - 1:
                    break
            all_pages = int(ceil(len(valid_mentors) / 30.0))

        verdana.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 590))

        if game.switches['list_page'] > 1:
            buttons.draw_image_button((315, 580),
                                      button_name='relationship_list_arrow_l',
                                      text='<',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] - 1,
                                      hotkey=[23]
                                      )
        else:
            buttons.draw_image_button((315, 580),
                                      button_name='relationship_list_arrow_l',
                                      text='<',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] - 1,
                                      hotkey=[23],
                                      available=False
                                      )

        if game.switches['list_page'] < all_pages:
            buttons.draw_image_button((451, 580),
                                      button_name='relationship_list_arrow_r',
                                      text='>',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] + 1,
                                      hotkey=[21]
                                      )
        else:
            buttons.draw_image_button((451, 580),
                                      button_name='relationship_list_arrow_r',
                                      text='>',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] + 1,
                                      hotkey=[21],
                                      available=False
                                      )

def show_mentor_cat_info(arg0, arg1, arg2):
    name = str(arg0.name)  # get name
    if 10 <= len(name) >= 16:  # check name length
        short_name = str(arg0.name)[0:9]
        name = short_name + '...'
    verdana_dark.text(str(name),
                      ('center', 121),
                      x_start=arg2,
                      x_limit=arg2+110
                      )

    y_value = 168

    if arg0.status != 'elder':
        verdana_small_dark.text(arg0.age,
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1+100
                                )
        y_value += 15

    if arg0.status != 'medicine cat apprentice':
        verdana_small_dark.text(str(arg0.status),
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
        y_value += 15
    else:
        verdana_small_dark.text('medicine cat',
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
        y_value += 15

        verdana_small_dark.text('apprentice',
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
        y_value += 15

    if arg0.genderalign is not None:
        verdana_small_dark.text(arg0.genderalign,
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
    else:
        verdana_small_dark.text(arg0.gender,
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
    y_value += 15

    verdana_small_dark.text(arg0.trait,
                            ('center', y_value),
                            x_start=arg1,
                            x_limit=arg1 + 100
                            )
    y_value += 15

    if arg0.skill == 'formerly a kittypet':
        verdana_small_dark.text('former kittypet',
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
    elif arg0.skill == 'strong connection to StarClan':
        verdana_small_dark.text('strong connection',
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
        y_value += 15
        verdana_small_dark.text('to StarClan',
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
    else:
        verdana_small_dark.text(arg0.skill,
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
    y_value += 15
    if len(arg0.former_apprentices) >= 1:
        verdana_small_dark.text(f"{len(arg0.former_apprentices)} former app(s)",
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )
        y_value += 15

    if len(arg0.apprentice) >= 1:
        verdana_small_dark.text(f"{len(arg0.apprentice)} current app(s)",
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 100
                                )

    mentor_icon = image_cache.load_image("resources/images/mentor.png")
    screen.blit(mentor_icon, (315, 160))


class ViewChildrenScreen(Screens):
    parents = pygame.image.load("resources/images/family_parents.png").convert_alpha()
    mate = pygame.image.load("resources/images/family_mate.png").convert_alpha()

    def on_use(self):
        the_cat = Cat.all_cats[game.switches['cat']]

        verdana_big.text(f'Family of {str(the_cat.name)}', ('center', 28))

        screen.blit(ViewChildrenScreen.parents, (76, 80))
        screen.blit(ViewChildrenScreen.mate, (80, 360))

        draw_next_prev_cat_buttons(the_cat)

        # SHOW PARENTS
        if the_cat.parent1 is None:
            verdana_small_dark.text('Unknown',
                               ('center', 195),
                               x_limit=150,
                               x_start=90)
        elif the_cat.parent1 in Cat.all_cats:
            buttons.draw_button(
                (95, 145),
                image=Cat.all_cats[the_cat.parent1].sprite,
                cat=the_cat.parent1,
                cur_screen='profile screen')

            name = str(Cat.all_cats[the_cat.parent1].name)
            if 8 <= len(name) >= 10:
                short_name = str(Cat.all_cats[the_cat.parent1].name)[0:7]
                name = short_name + '...'
            verdana_small_dark.text(str(name),
                               ('center', 195),
                               x_limit=150,
                               x_start=90)


        else:
            verdana_small.text(f'Error: cat {str(the_cat.parent1)} not found',
                               (342, 165))
        if the_cat.parent2 is None:
            verdana_small_dark.text('Unknown',
                               ('center', 258),
                               x_limit=150,
                               x_start=90)
        elif the_cat.parent2 in Cat.all_cats:
            buttons.draw_button(
                (95, 210),
                image=Cat.all_cats[the_cat.parent2].sprite,
                cat=the_cat.parent2,
                cur_screen='profile screen')

            name = str(Cat.all_cats[the_cat.parent2].name)
            if 8 <= len(name) >= 10:
                short_name = str(Cat.all_cats[the_cat.parent2].name)[0:7]
                name = short_name + '...'
            verdana_small_dark.text(str(name),
                               ('center', 258),
                               x_limit=150,
                               x_start=90)

        else:
            verdana_small.text(
                'Error: cat ' + str(the_cat.parent2) + ' not found',
                (342, 165))

        # SHOW SIBLINGS
        pos_x = 229
        pos_y = 120
        siblings = False
        for x in game.clan.clan_cats:
            if (Cat.all_cats[x].parent1 in (the_cat.parent1, the_cat.parent2) or Cat.all_cats[x].parent2 in (
                    the_cat.parent1, the_cat.parent2) and the_cat.parent2 is not None) and the_cat.ID != Cat.all_cats[x].ID and the_cat.parent1 is not None and \
                    Cat.all_cats[x].parent1 is not None:
                buttons.draw_button((pos_x, pos_y),
                                    image=Cat.all_cats[x].sprite,
                                    cat=Cat.all_cats[x].ID,
                                    cur_screen='profile screen')

                name = str(Cat.all_cats[x].name)
                if 6 <= len(name) >= 9:
                    short_name = str(Cat.all_cats[x].name)[0:5]
                    name = short_name + '...'
                verdana_small_dark.text(str(name),
                                        ('center', pos_y + 50),
                                        x_start=pos_x,
                                        x_limit=pos_x + 60)

                siblings = True
                pos_x += 60
                if pos_x > 700:
                    pos_y += 60
                    pos_x = 0

        if siblings is False:
            verdana.text('This cat has no siblings.', (380, 200))


        pos_x = 0
        pos_y = 60
        # SHOW MATE
        if the_cat.mate is None:
            verdana_small_dark.text('Unknown', (93, 508))
        elif the_cat.mate in Cat.all_cats:
            buttons.draw_button(
                (98, 458),
                image=Cat.all_cats[the_cat.mate].sprite,
                cat=the_cat.mate,
                cur_screen='profile screen')

            name = str(Cat.all_cats[the_cat.mate].name)
            if 8 <= len(name) >= 11:
                short_name = str(Cat.all_cats[the_cat.mate].name)[0:7]
                name = short_name + '...'
            verdana_small_dark.text(str(name),
                               ('center', 508),
                               x_limit=150,
                               x_start=90
            )

        else:
            verdana_small.text(f'Error: cat {str(the_cat.mate)} not found',
                               (342, 165))

        #SHOW KITS
        pos_x = 229
        pos_y = 400

        kittens = False
        for x in game.clan.clan_cats:
            if the_cat.ID in [
                    Cat.all_cats[x].parent1,
                    Cat.all_cats[x].parent2
            ]:
                buttons.draw_button((pos_x, pos_y),
                                    image=Cat.all_cats[x].sprite,
                                    cat=Cat.all_cats[x].ID,
                                    cur_screen='profile screen')

                name = str(Cat.all_cats[x].name)
                if 6 <= len(name) >= 9:
                    short_name = str(Cat.all_cats[x].name)[0:5]
                    name = short_name + '...'
                verdana_small_dark.text(str(name),
                                        ('center', pos_y + 50),
                                        x_start=pos_x,
                                        x_limit=pos_x + 60
                                        )

                kittens = True
                pos_x += 60
                if pos_x > 700:
                    pos_y += 60
                    pos_x = 0

        if kittens is False:
            verdana.text('This cat has never had offspring.', (350, 480))


        if the_cat.exiled:
            buttons.draw_image_button((25, 645),
                                      button_name='back',
                                      text='Back',
                                      size=(105, 30),
                                      cur_screen='outside profile screen',
                                      chosen_cat=None,
                                      show_details=False)
        else:
            buttons.draw_image_button((25, 645),
                                      button_name='back',
                                      text='Back',
                                      size=(105, 30),
                                      cur_screen='profile screen',
                                      chosen_cat=None,
                                      show_details=False)

    def screen_switches(self):
        cat_profiles()

class ChooseMateScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats[game.switches['cat']]

        game.switches['choosing_mate'] = True

        draw_choosing_bg(494, 'mate')

        draw_next_prev_cat_buttons(the_cat)

        y_value = 30
        verdana_big.text(f'Choose a mate for {str(the_cat.name)}',
                         ('center', y_value))
        y_value += 30

        verdana_small.text(
            'If the cat has chosen a mate, they will stay loyal and not have kittens ',
            ('center', y_value))
        y_value += 15

        verdana_small.text(
            'with anyone else, even if having kittens in said relationship is ',
            ('center', y_value))
        y_value += 15

        verdana_small.text(
            'impossible.  However, their chances of having kittens when possible',
            ('center', y_value))
        y_value += 15

        verdana_small.text(
            'is heightened.  If affairs are toggled on, cats may not be loyal in ',
            ('center', y_value))
        y_value += 15

        verdana_small.text(
            'their relationships.',
            ('center', y_value))
        draw_large(the_cat, (50, 150))
        show_mate_cat_info(the_cat, 212, 71)
        mate = None
        if game.switches['mate'] is not None and the_cat.mate is None:
            mate = Cat.all_cats[game.switches['mate']]
        elif the_cat.mate is not None:
            if the_cat.mate in Cat.all_cats:
                mate = Cat.all_cats[the_cat.mate]
            else:
                the_cat.mate = None
        if mate is not None:
            draw_large(mate, (600, 150))
            show_mate_cat_info(mate, 506, 622)
            if the_cat.gender == mate.gender and not game.settings[
                    'no gendered breeding'] and the_cat.mate is None:
                verdana_small.text(
                    '(this pair will not be able to have kittens)',
                    ('center', 333))
            self.show_compatibility(the_cat, mate)

        self.heart_status(the_cat, mate)

        valid_mates = []
        pos_x = 0
        pos_y = 20
        if the_cat.mate is None:
            self.get_valid_mates(the_cat, valid_mates, pos_x, pos_y)
        else:
            #  verdana.text('Already in a relationship.', ('center', 313))
            kittens = False
            for x in game.clan.clan_cats:
                if the_cat.ID in [
                        Cat.all_cats[x].parent1,
                        Cat.all_cats[x].parent2
                ] and mate.ID in [
                        Cat.all_cats[x].parent1,
                        Cat.all_cats[x].parent2
                ]:
                    buttons.draw_button((100 + pos_x, 365 + pos_y),
                                        image=Cat.all_cats[x].sprite,
                                        cat=Cat.all_cats[x].ID,
                                        cur_screen='profile screen')

                    kittens = True
                    pos_x += 60
                    if pos_x > 550:
                        pos_y += 60
                        pos_x = 0
            if kittens:
                verdana.text('Their offspring:', ('center', 333))
            else:
                verdana.text('This pair has never had offspring.',
                             ('center', 333))
        if mate is not None and the_cat.mate is None:
            buttons.draw_button((323, 295),  # cannot be a draw_image_button, it will break
                                image='buttons/its_official',
                                text="It\'s official!",
                                cat_value=the_cat,
                                mate=mate,
                                )

        elif the_cat.mate is not None:
            buttons.draw_button((323, 295),  # cannot be a draw_image_button, it will break
                                image='buttons/break_up',
                                text="Break it up...",
                                cat_value=the_cat,
                                mate=None,
                                )

        if the_cat.exiled:
            buttons.draw_image_button((25, 645),
                                      button_name='back',
                                      text='Back',
                                      size=(105, 30),
                                      cur_screen='outside the profile screen',
                                      broke_up=False,
                                      choosing_mate=False
                                      )
        else:
            buttons.draw_image_button((25, 645),
                                      button_name='back',
                                      text='Back',
                                      size=(105, 30),
                                      cur_screen='profile screen',
                                      broke_up=False,
                                      choosing_mate=False
                                      )



    def heart_status(self, the_cat, mate):
        q_heart = image_cache.load_image("resources/images/heart_maybe.png").convert_alpha()
        heart = image_cache.load_image("resources/images/heart_mates.png").convert_alpha()
        b_heart = image_cache.load_image("resources/images/heart_breakup.png").convert_alpha()

        x_value = 300
        y_value = 188
        if game.switches['broke_up'] is True:
            screen.blit(b_heart, (x_value, y_value))

        elif game.switches['mate'] is not None and the_cat.mate is None and game.switches['broke_up'] is False:
            screen.blit(q_heart, (x_value, y_value))

        elif the_cat.mate is not None:
            screen.blit(heart, (x_value, y_value))

    def show_compatibility(self, arg1, arg2):
        # compatible = pygame.image.load("resources/images/pers_compatible.png")
        # incompatible = pygame.image.load("resources/images/pers_incompatible.png")
        # neutral = pygame.image.load("resources/images/pers_neutral.png")

        compatible = image_cache.load_image("resources/images/line_compatible.png").convert_alpha()
        incompatible = image_cache.load_image("resources/images/line_incompatible.png").convert_alpha()
        neutral = image_cache.load_image("resources/images/line_neutral.png").convert_alpha()
        s_heart = image_cache.load_image("resources/images/heart_big.png").convert_alpha()
        x_value = 300
        y_value = 190

        if get_personality_compatibility(arg1, arg2) is True:
            screen.blit(compatible, (x_value, y_value))

        if get_personality_compatibility(arg1, arg2) is False:
            screen.blit(incompatible, (x_value, y_value))

        if get_personality_compatibility(arg1, arg2) is None:
            screen.blit(neutral, (x_value, y_value))

        y_value = 285

        if arg2.ID in arg1.relationships:
            relation = arg1.relationships[arg2.ID]
        else:
            relation = arg1.create_one_relationship(arg2)
        romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            screen.blit(s_heart, (210, y_value))
        elif 41 <= romantic_love <= 80:
            screen.blit(s_heart, (210, y_value))
            screen.blit(s_heart, (237, y_value))
        elif 81 <= romantic_love:
            screen.blit(s_heart, (210, y_value))
            screen.blit(s_heart, (237, y_value))
            screen.blit(s_heart, (264, y_value))

        if arg1.ID in arg2.relationships:
            relation = arg2.relationships[arg1.ID]
        else:
            relation = arg2.create_one_relationship(arg1)
        romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            screen.blit(s_heart, (568, y_value))
        elif 41 <= romantic_love <= 80:
            screen.blit(s_heart, (568, y_value))
            screen.blit(s_heart, (541, y_value))
        elif 81 <= romantic_love:
            screen.blit(s_heart, (568, y_value))
            screen.blit(s_heart, (541, y_value))
            screen.blit(s_heart, (514, y_value))

    def get_valid_mates(self, the_cat, valid_mates, pos_x, pos_y):
        for x in game.clan.clan_cats:
            relevant_cat = Cat.all_cats[x]
            invalid_age = relevant_cat.age not in ['kitten', 'adolescent']

            direct_related = the_cat.is_sibling(relevant_cat) or the_cat.is_parent(relevant_cat) or relevant_cat.is_parent(the_cat)
            indirect_related = the_cat.is_uncle_aunt(relevant_cat) or relevant_cat.is_uncle_aunt(the_cat)
            related = direct_related or indirect_related

            not_available = relevant_cat.dead or relevant_cat.exiled

            if not related and relevant_cat.ID != the_cat.ID and invalid_age and not not_available and relevant_cat.mate == None:

                valid_mates.append(relevant_cat)
        all_pages = int(ceil(len(valid_mates) /
                             30.0)) if len(valid_mates) > 30 else 1
        cats_on_page = 0
        for x in range(len(valid_mates)):
            if x + (game.switches['list_page'] - 1) * 30 > len(valid_mates):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            pot_mate = valid_mates[x + (game.switches['list_page'] - 1) * 30]
            buttons.draw_button((100 + pos_x, 365 + pos_y),
                                image=pot_mate.sprite,
                                mate=pot_mate.ID,
                                broke_up=False)

            pos_x += 60
            cats_on_page += 1
            if pos_x > 550:
                pos_y += 60
                pos_x = 0
            if cats_on_page >= 30 or x + (game.switches['list_page'] -
                                          1) * 30 == len(valid_mates) - 1:
                break
        verdana.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 590))

        if game.switches['list_page'] > 1:
            buttons.draw_image_button((315, 580),
                                      button_name='relationship_list_arrow_l',
                                      text='<',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] - 1,
                                      hotkey=[23]
                                      )
        else:
            buttons.draw_image_button((315, 580),
                                      button_name='relationship_list_arrow_l',
                                      text='<',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] - 1,
                                      hotkey=[23],
                                      available=False
                                      )

        if game.switches['list_page'] < all_pages:
            buttons.draw_image_button((451, 580),
                                      button_name='relationship_list_arrow_r',
                                      text='>',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] + 1,
                                      hotkey=[21]
                                      )
        else:
            buttons.draw_image_button((451, 580),
                                      button_name='relationship_list_arrow_r',
                                      text='>',
                                      size=(34, 34),
                                      list_page=game.switches['list_page'] + 1,
                                      hotkey=[21],
                                      available=False
                                      )


def show_mate_cat_info(arg0, arg1, arg2):
    name = str(arg0.name)  # get name
    if 10 <= len(name) >= 16:  # check name length
        short_name = str(arg0.name)[0:9]
        name = short_name + '...'
    verdana_dark.text(str(name),
                      ('center', 121),
                      x_start=arg2,
                      x_limit=arg2 + 110
                      )

    y_value = 193

    verdana_small_dark.text(f'{str(arg0.moons)} moons',
                            ('center', y_value),
                            x_start=arg1,
                            x_limit=arg1 + 80
                            )
    y_value += 15

    verdana_small_dark.text(str(arg0.status),
                            ('center', y_value),
                            x_start=arg1,
                            x_limit=arg1 + 80
                            )
    y_value += 15

    if arg0.genderalign is not None:
        verdana_small_dark.text(arg0.genderalign,
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 80
                                )
    else:
        verdana_small_dark.text(arg0.gender,
                                ('center', y_value),
                                x_start=arg1,
                                x_limit=arg1 + 80
                                )
    y_value += 15

    verdana_small_dark.text(arg0.trait,
                            ('center', y_value),
                            x_start=arg1,
                            x_limit=arg1 + 80
                            )


class RelationshipScreen(Screens):
    bool = {True: 'on', False: 'off', None: 'None'}

    search_bar = image_cache.load_image("resources/images/relationship_search.png").convert_alpha()
    details_frame = image_cache.load_image("resources/images/relationship_details_frame.png").convert_alpha()
    toggle_frame = image_cache.load_image("resources/images/relationship_toggle_frame.png").convert_alpha()
    list_frame = image_cache.load_image("resources/images/relationship_list_frame.png").convert_alpha()

    female_icon = image_cache.load_image("resources/images/female_big.png").convert_alpha()
    male_icon = image_cache.load_image("resources/images/male_big.png").convert_alpha()
    nonbi_icon = image_cache.load_image("resources/images/nonbi_big.png").convert_alpha()
    transfem_icon = image_cache.load_image("resources/images/transfem_big.png").convert_alpha()
    transmasc_icon = image_cache.load_image("resources/images/transmasc_big.png").convert_alpha()

    female_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/female_big.png").convert_alpha(), (18, 18))
    male_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/male_big.png").convert_alpha(), (18, 18))
    nonbi_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/nonbi_big.png").convert_alpha(), (18, 18))
    transfem_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/transfem_big.png").convert_alpha(), (18, 18))
    transmasc_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/transmasc_big.png").convert_alpha(), (18, 18))

    mate_icon = image_cache.load_image("resources/images/heart_big.png").convert_alpha()
    family_icon = image_cache.load_image("resources/images/dot_big.png").convert_alpha()

    mate_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/heart_big.png").convert_alpha(), (11, 10))
    family_icon_small = pygame.transform.scale(image_cache.load_image("resources/images/dot_big.png").convert_alpha(), (9, 9))

    def on_use(self):
        # use this variable to point to the cat object in question
        # this cat is the current cat in focus - aka the cat we're viewing the relationships of
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                   game.clan.instructor
                                   )

        # back and next buttons on the relationships page, these will reset the show_details cat
        draw_next_prev_cat_buttons(the_cat)


        # LOAD UI IMAGES
        screen.blit(RelationshipScreen.search_bar, (536, 90))
        screen.blit(RelationshipScreen.details_frame, (25, 130))
        screen.blit(RelationshipScreen.toggle_frame, (45, 484))
        screen.blit(RelationshipScreen.list_frame, (273, 122))

        # SEARCH TEXT
        search_text = game.switches['search_text']

        verdana_black.text(game.switches['search_text'], (612, 97))

        # MAKE A LIST OF RELATIONSHIPS
        search_relations = []
        if search_text.strip() != '':
            for rel in the_cat.relationships.values():
                if search_text.lower() in str(rel.cat_to.name).lower():
                    search_relations.append(rel)
        else:
            search_relations = list(the_cat.relationships.values()).copy()

        # VIEW TOGGLES
        verdana_mid_dark.text(
            f"Show Dead",
            (70, 513))


        if game.settings['show dead relation'] is True:
            buttons.draw_image_button((169, 505),
                                      button_name='on',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show dead relation',
                                      )
            buttons.draw_image_button((215, 505),
                                      button_name='off',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show dead relation',
                                      available=False
                                      )

        if game.settings['show dead relation'] is False:
            buttons.draw_image_button((169, 505),
                                      button_name='on',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show dead relation',
                                      available=False
                                      )
            buttons.draw_image_button((215, 505),
                                      button_name='off',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show dead relation',
                                      )

        verdana_mid_dark.text(
            f"Show Empty",
            (70, 558))

        if game.settings['show empty relation'] is True:
            buttons.draw_image_button((169, 550),
                                      button_name='on',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show empty relation'
                                      )
            buttons.draw_image_button((215, 550),
                                      button_name='off',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show empty relation',
                                      available=False
                                      )

        if game.settings['show empty relation'] is False:
            buttons.draw_image_button((169, 550),
                                      button_name='on',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show empty relation',
                                      available=False
                                      )
            buttons.draw_image_button((215, 550),
                                      button_name='off',
                                      size=(46, 34),
                                      text='switch',
                                      setting='show empty relation',
                                      )

        # TOGGLE FILTERS
        if not game.settings['show dead relation']:
            search_relations = list(
                filter(lambda rel: not rel.cat_to.dead, search_relations))

        if not game.settings['show empty relation']:
            search_relations = list(
                filter(
                    lambda rel: (rel.romantic_love + rel.platonic_like + rel.
                                 dislike + rel.admiration + rel.comfortable +
                                 rel.jealousy + rel.trust) > 0, search_relations))

        # NAME AND SPRITE OF FOCUS CAT
        if game.settings['dark mode'] is True:
            verdana_big.text(str(the_cat.name) + ' Relationships', (80, 75))
        else:
            verdana_big_dark.text(str(the_cat.name) + ' Relationships', (80, 75))
        draw(the_cat, (25, 70))

        # FOCUS CAT DETAILS
        if the_cat is not None:
            mate = Cat.all_cats.get(the_cat.mate)
            if mate is not None:
                verdana_small.text(
                    f"{str(the_cat.genderalign)} - {str(the_cat.moons)} moons - {str(the_cat.trait)} - mate: {str(mate.name)}",
                    (80, 100))
            else:
                verdana_small.text(
                    f"{str(the_cat.genderalign)}  - {str(the_cat.moons)} moons - {str(the_cat.trait)}",
                    (80, 100))

        # PAGES
        all_pages = 1  # amount of pages
        if len(search_relations) > 8:
            all_pages = int(ceil(len(search_relations) / 8))

        pos_x = 0
        pos_y = 0
        cats_on_page = 0  # how many are on page already

        for x in range(len(search_relations)):
            if (x +
                    (game.switches['list_page'] - 1) * 8) > len(search_relations):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_relationship = search_relations[x +
                                                (game.switches['list_page'] - 1) *
                                                8]

            # CAT LIST SPRITES
            update_sprite(the_relationship.cat_to)

            # MAKES SPRITES INTO BUTTONS
            buttons.draw_button((312 + pos_x, 150 + pos_y),  # if button clicked, show chosen_cat's details
                                image=the_relationship.cat_to.sprite,
                                chosen_cat=the_relationship.cat_to,
                                show_details=True
                                )

            # CHECK NAME LENGTH - SHORTEN IF NECESSARY
            name = str(the_relationship.cat_to.name)  # get name
            if 12 <= len(name) >= 14:  # check name length
                short_name = str(the_relationship.cat_to.name)[0:11]
                name = short_name + '...'

            # display name
            verdana_mid_dark.text(name, ('center', 131 + pos_y),
                                  x_start=300 + pos_x,
                                  x_limit=300 + pos_x + 82)

            if the_relationship.cat_to.genderalign == 'female':
                screen.blit(RelationshipScreen.female_icon_small, (370 + pos_x, 155 + pos_y))
            if the_relationship.cat_to.genderalign == 'male':
                screen.blit(RelationshipScreen.male_icon_small, (370 + pos_x, 155 + pos_y))
            if the_relationship.cat_to.genderalign != 'female' and the_relationship.cat_to.genderalign != 'male' \
                    and the_relationship.cat_to.genderalign != 'trans female' and the_relationship.cat_to.genderalign != 'trans male':
                screen.blit(RelationshipScreen.nonbi_icon_small, (370 + pos_x, 155 + pos_y))
            if the_relationship.cat_to.genderalign == 'trans female':
                screen.blit(RelationshipScreen.transfem_icon_small, (370 + pos_x, 155 + pos_y))
            if the_relationship.cat_to.genderalign == 'trans male':
                screen.blit(RelationshipScreen.transmasc_icon_small, (370 + pos_x, 155 + pos_y))

            if the_cat.mate is not None and the_cat.mate != '' and the_relationship.cat_to.ID == the_cat.mate:
                screen.blit(RelationshipScreen.mate_icon_small, (297 + pos_x, 158 + pos_y))

            if the_relationship.cat_to.is_uncle_aunt(the_cat) or the_cat.is_uncle_aunt(the_relationship.cat_to):
                screen.blit(RelationshipScreen.family_icon_small, (297 + pos_x, 158 + pos_y))
            elif the_relationship.cat_to.is_grandparent(the_cat) or the_cat.is_grandparent(the_relationship.cat_to):
                screen.blit(RelationshipScreen.family_icon_small, (297 + pos_x, 158 + pos_y))
            elif the_relationship.cat_to.is_parent(the_cat) or the_cat.is_parent(the_relationship.cat_to):
                screen.blit(RelationshipScreen.family_icon_small, (297 + pos_x, 158 + pos_y))
            elif the_relationship.cat_to.is_sibling(the_cat) or the_cat.is_sibling(the_relationship.cat_to):
                screen.blit(RelationshipScreen.family_icon_small, (297 + pos_x, 158 + pos_y))

            count = 17

            # CHECK AGE DIFFERENCE
            different_age = the_relationship.cat_to.age != the_relationship.cat_to.age
            adult_ages = ['young adult', 'adult', 'senior adult', 'elder']
            both_adult = the_relationship.cat_to.age in adult_ages and the_relationship.cat_to.age in adult_ages
            check_age = (different_age and both_adult) or both_adult or not different_age

            # ROMANTIC DISPLAY
            if the_relationship.romantic_love > 49 and check_age:
                verdana_small_dark.text(
                    'romantic love:',
                    (292 + pos_x, 181 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 180 + pos_y + count
                if check_age:
                    self.draw_green_bar(the_relationship.romantic_love, current_x, current_y)
                else:
                    self.draw_bar(0, current_x, current_y)
            else:
                verdana_small_dark.text(
                    'romantic like:',
                    (292 + pos_x, 181 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 180 + pos_y + count
                if check_age:
                    self.draw_bar(the_relationship.romantic_love, current_x, current_y)
                else:
                    self.draw_bar(0, current_x, current_y)

            count += 5

            # PLATONIC DISPLAY
            if the_relationship.platonic_like > 49:
                verdana_small_dark.text(
                    'platonic love:',
                    (292 + pos_x, 179 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 178 + pos_y + count
                self.draw_green_bar(the_relationship.platonic_like, current_x, current_y)
            else:
                verdana_small_dark.text(
                    'platonic like:',
                    (292 + pos_x, 179 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 178 + pos_y + count
                self.draw_bar(the_relationship.platonic_like, current_x, current_y)

            count += 5

            # DISLIKE DISPLAY
            if the_relationship.dislike > 49:
                verdana_small_dark.text(
                    'hate:',
                    (292 + pos_x, 177 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 176 + pos_y + count
                self.draw_red_bar(the_relationship.dislike, current_x, current_y)
            else:
                verdana_small_dark.text(
                    'dislike:',
                    (292 + pos_x, 177 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 176 + pos_y + count
                self.draw_bar(the_relationship.dislike, current_x, current_y)

            count += 5

            # ADMIRE DISPLAY
            if the_relationship.admiration > 49:
                verdana_small_dark.text(
                    'admiration:',
                    (292 + pos_x, 175 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 174 + pos_y + count
                self.draw_green_bar(the_relationship.admiration, current_x, current_y)

            else:
                verdana_small_dark.text(
                    'respect:',
                    (292 + pos_x, 175 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 174 + pos_y + count
                self.draw_bar(the_relationship.admiration, current_x, current_y)

            count += 5

            # COMFORTABLE DISPLAY
            if the_relationship.comfortable > 49:
                verdana_small_dark.text(
                    'secure:',  # eventual progression to 'secure'?
                    (292 + pos_x, 173 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 172 + pos_y + count
                self.draw_green_bar(the_relationship.comfortable, current_x, current_y)
            else:
                verdana_small_dark.text(
                    'comfortable:',  # eventual progression to 'secure'?
                    (292 + pos_x, 173 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 172 + pos_y + count
                self.draw_bar(the_relationship.comfortable, current_x, current_y)

            count += 5

            # JEALOUS DISPLAY
            if the_relationship.jealousy > 49:
                verdana_small_dark.text(
                    'resentment:',  # eventual progression to 'resentment'?
                    (292 + pos_x, 171 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 170 + pos_y + count
                self.draw_red_bar(the_relationship.jealousy, current_x, current_y)
            else:
                verdana_small_dark.text(
                        'jealousy:',  # eventual progression to 'resentment'?
                        (292 + pos_x, 171 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 170 + pos_y + count
                self.draw_bar(the_relationship.jealousy, current_x, current_y)

            count += 5

            # TRUST DISPLAY
            if the_relationship.trust > 49:
                verdana_small_dark.text(
                    'reliance:',  # eventual progression to 'reliance'?
                    (294 + pos_x, 169 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 168 + pos_y + count
                self.draw_green_bar(the_relationship.trust, current_x, current_y)
            else:
                verdana_small_dark.text(
                    'trust:',  # eventual progression to 'reliance'?
                    (294 + pos_x, 169 + pos_y + count))
                count += 20
                current_x = 294 + pos_x
                current_y = 168 + pos_y + count
                self.draw_bar(the_relationship.trust, current_x, current_y)

            # CAT COUNT
            cats_on_page += 1
            pos_x += 122
            if pos_x >= 400:
                pos_x = 0
                pos_y += 55 + count

            if cats_on_page >= 8 or x + (game.switches['list_page'] -
                                          1) * 8 == len(search_relations) - 1:
                break

        # SHOW CAT DETAILS
        if game.switches['show_details'] is True:

            # NAME LENGTH
            chosen_name = str(game.switches['chosen_cat'].name)
            if 17 <= len(chosen_name) >= 19:
                chosen_short_name = str(game.switches['chosen_cat'].name)[0:16]
                chosen_name = chosen_short_name + '...'

            # NAME
            if game.switches['chosen_cat'].dead:
                verdana_big_dark.text(
                    f"{chosen_name} (dead)",
                    ('center', 295),
                    x_limit=225,
                    x_start=75
                )
            else:
                verdana_big_dark.text(
                    f"{chosen_name}",
                    ('center', 295),
                    x_limit=225,
                    x_start=75
                )

            # DRAW CAT
            draw_large(game.switches['chosen_cat'], (75, 145))

            # GENDER
            verdana_small_dark.text(
                f"{str(game.switches['chosen_cat'].genderalign)}",
                (60, 325))
            self.draw_gender_icon(235, 145, game.switches['chosen_cat'])

            # AGE
            verdana_small_dark.text(
                f"{str(game.switches['chosen_cat'].moons)} moons",
                (60, 340))

            # MATE
            if game.switches['chosen_cat'].mate is not None and the_cat.ID != game.switches['chosen_cat'].mate:
                verdana_small_dark.text(
                    'has a mate',
                    (150, 325)
                )

            elif the_cat.mate is not None and the_cat.mate != '' and game.switches['chosen_cat'].ID == the_cat.mate:
                verdana_small_dark.text(
                    f"{str(the_cat.name)}'s mate",
                    (150, 325)
                )
                screen.blit(RelationshipScreen.mate_icon, (45, 150))

            else:
                verdana_small_dark.text(
                    'mate: none',
                    (150, 325)
                )

            # TRAIT
            verdana_small_dark.text(
                f"{str(game.switches['chosen_cat'].trait)}",
                (60, 355))

            # RELATED
            x_value = 150
            y_value = 340
            if game.switches['chosen_cat'].is_uncle_aunt(the_cat) or the_cat.is_uncle_aunt(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related',
                    (x_value, y_value))
                screen.blit(RelationshipScreen.family_icon, (45, 150))

            elif game.switches['chosen_cat'].is_grandparent(the_cat):
                verdana_small_dark.text(
                    'related: grandparent',
                    (x_value, y_value))
                screen.blit(RelationshipScreen.family_icon, (45, 150))

            elif the_cat.is_grandparent(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related: grandchild',
                    (x_value, y_value))
                screen.blit(RelationshipScreen.family_icon, (45, 150))

            elif game.switches['chosen_cat'].is_parent(the_cat):
                verdana_small_dark.text(
                    'related: parent',
                    (x_value, y_value))
                screen.blit(RelationshipScreen.family_icon, (45, 150))

            elif the_cat.is_parent(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related: child',
                    (x_value, y_value))
                screen.blit(RelationshipScreen.family_icon, (45, 150))

            elif game.switches['chosen_cat'].is_sibling(the_cat) or the_cat.is_sibling(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related: sibling',
                    (x_value, y_value))
                screen.blit(RelationshipScreen.family_icon, (45, 150))

        # PAGE ARROW BUTTONS
        verdana.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            (488, 625))

        if game.switches['list_page'] > 1:
            buttons.draw_image_button((440, 616),
                                      button_name='relationship_list_arrow_l',
                                      list_page=game.switches['list_page'] - 1,
                                      size=(34, 34),
                                      hotkey=[23])
        else:
            buttons.draw_image_button((440, 616),
                                      button_name='relationship_list_arrow_l',
                                      list_page=game.switches['list_page'] - 1,
                                      size=(34, 34),
                                      available=False,
                                      hotkey=[23])

        if game.switches['list_page'] < all_pages:

            buttons.draw_image_button((580, 616),
                                      button_name='relationship_list_arrow_r',
                                      list_page=game.switches['list_page'] + 1,
                                      size=(34, 34),
                                      hotkey=[21])
        else:
            buttons.draw_image_button((580, 616),
                                      button_name='relationship_list_arrow_r',
                                      list_page=game.switches['list_page'] + 1,
                                      size=(34, 34),
                                      available=False,
                                      hotkey=[21])

        # CHANGE FOCUS CAT AND VIEW PROFILE
        # CHANGE FOCUS CAT AND VIEW PROFILE
        if game.switches['chosen_cat'] is not None and not game.switches['chosen_cat'].dead:
            to_switch_id = game.switches['chosen_cat'].ID
            buttons.draw_image_button((85, 390),
                                      button_name='switch_focus',
                                      size=(136, 30),
                                      cat=to_switch_id,
                                      cur_screen='relationship screen',
                                      show_details=None,
                                      chosen_cat=None
                                      )
            buttons.draw_image_button((85, 420),
                                      button_name='view_profile',
                                      size=(136, 30),
                                      cat=to_switch_id,
                                      cur_screen='profile screen',
                                      show_details=None,
                                      chosen_cat=None
                                      )
        elif game.switches['chosen_cat'] is not None and game.switches['chosen_cat'].dead:
            to_switch_id = game.switches['chosen_cat'].ID
            buttons.draw_image_button((85, 390),
                                      button_name='switch_focus',
                                      size=(136, 30),
                                      cat=to_switch_id,
                                      cur_screen='relationship screen',
                                      show_details=None,
                                      chosen_cat=None,
                                      available=False
                                      )
            buttons.draw_image_button((85, 420),
                                      button_name='view_profile',
                                      size=(136, 30),
                                      cat=to_switch_id,
                                      cur_screen='profile screen',
                                      show_details=None,
                                      chosen_cat=None
                                      )

        else:
            buttons.draw_image_button((85, 390),
                                      button_name='switch_focus',
                                      size=(136, 30),
                                      available=False
                                      )
            buttons.draw_image_button((85, 420),
                                      button_name='view_profile',
                                      size=(136, 30),
                                      available=False
                                      )
        buttons.draw_image_button((25, 645),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  chosen_cat=None,
                                  show_details=False)

    def draw_gender_icon(self, x_pos, y_pos, arg0):

        if arg0.genderalign is not None:
            cat_gender = arg0.genderalign
        else:
            cat_gender = arg0.gender

        if cat_gender == 'female':
            screen.blit(RelationshipScreen.female_icon, (x_pos, y_pos))
        if cat_gender == 'male':
            screen.blit(RelationshipScreen.male_icon, (x_pos, y_pos))
        if cat_gender != 'female' and cat_gender != 'male' \
                and cat_gender != 'trans female' and cat_gender != 'trans male':
            screen.blit(RelationshipScreen.nonbi_icon, (x_pos, y_pos))
        if cat_gender == 'trans female':
            screen.blit(RelationshipScreen.transfem_icon, (x_pos, y_pos))
        if cat_gender == 'trans  male':
            screen.blit(RelationshipScreen.transmasc_icon, (x_pos, y_pos))


    def draw_bar(self, value, pos_x, pos_y):
        # Loading Bar and variables
        bar_bg = image_cache.load_image(
            "resources/images/relations_border.png").convert_alpha()
        bar_bg_dark = image_cache.load_image(
            "resources/images/relations_border_dark.png").convert_alpha()
        original_bar = image_cache.load_image(
            "resources/images/relation_bar.png").convert_alpha()


        bg_rect = bar_bg.get_rect(midleft=(pos_x, pos_y))
        if game.settings['dark mode'] is True:
            screen.blit(bar_bg_dark, bg_rect)
        else:
            screen.blit(bar_bg, bg_rect)
        x_pos = 0
        bar_length_per_snippet = 8
        number_of_bars = 10
        for i in range(int(value / number_of_bars)):
            x_pos = i * (bar_length_per_snippet + 1)
            bar_rect = original_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
            bar = pygame.transform.scale(original_bar, (bar_length_per_snippet, 10))
            screen.blit(bar, bar_rect)
        x_pos = (bar_length_per_snippet + 1) * int(value / number_of_bars)
        bar_rect = original_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
        bar = pygame.transform.scale(original_bar, (value % number_of_bars, 10))
        screen.blit(bar, bar_rect)


    def draw_green_bar(self, value, pos_x, pos_y):
        # Loading Bar and variables
        bar_bg = pygame.image.load(
            "resources/images/relations_border.png").convert_alpha()
        bar_bg_dark = pygame.image.load(
            "resources/images/relations_border_dark.png").convert_alpha()
        green_bar = pygame.image.load(
            "resources/images/relation_bar_green.png").convert_alpha()

        bg_rect = bar_bg.get_rect(midleft=(pos_x, pos_y))
        if game.settings['dark mode'] is True:
            screen.blit(bar_bg_dark, bg_rect)
        else:
            screen.blit(bar_bg, bg_rect)
        x_pos = 0
        bar_length_per_snippet = 8
        number_of_bars = 10
        for i in range(int(value / number_of_bars)):
            x_pos = i * (bar_length_per_snippet + 1)
            bar_rect = green_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
            bar = pygame.transform.scale(green_bar, (bar_length_per_snippet, 10))
            screen.blit(bar, bar_rect)
        x_pos = (bar_length_per_snippet + 1) * int(value / number_of_bars)
        bar_rect = green_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
        bar = pygame.transform.scale(green_bar, (value % number_of_bars, 10))
        screen.blit(bar, bar_rect)

    def draw_red_bar(self, value, pos_x, pos_y):
        # Loading Bar and variables
        bar_bg = pygame.image.load(
            "resources/images/relations_border.png").convert_alpha()
        bar_bg_dark = pygame.image.load(
            "resources/images/relations_border_dark.png").convert_alpha()
        red_bar = pygame.image.load(
            "resources/images/relation_bar_red.png").convert_alpha()

        bg_rect = bar_bg.get_rect(midleft=(pos_x, pos_y))
        if game.settings['dark mode'] is True:
            screen.blit(bar_bg_dark, bg_rect)
        else:
            screen.blit(bar_bg, bg_rect)
        x_pos = 0
        bar_length_per_snippet = 8
        number_of_bars = 10
        for i in range(int(value / number_of_bars)):
            x_pos = i * (bar_length_per_snippet + 1)
            bar_rect = red_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
            bar = pygame.transform.scale(red_bar, (bar_length_per_snippet, 10))
            screen.blit(bar, bar_rect)
        x_pos = (bar_length_per_snippet + 1) * int(value / number_of_bars)
        bar_rect = red_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
        bar = pygame.transform.scale(red_bar, (value % number_of_bars, 10))
        screen.blit(bar, bar_rect)

    def screen_switches(self):
        cat_profiles()
