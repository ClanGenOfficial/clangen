from math import ceil

from .base_screens import Screens, draw_menu_buttons, cat_profiles, draw_next_prev_cat_buttons

from scripts.utility import draw_large, draw, update_sprite
from scripts.game_structure.buttons import buttons
from scripts.game_structure.text import *
from scripts.cat.cats import Cat


def draw_choosing_bg(self):
    list_frame = pygame.image.load("resources/images/choosing_frame.png").convert_alpha()
    cat1_frame = pygame.image.load("resources/images/choosing_cat1_frame.png").convert_alpha()
    cat2_frame = pygame.image.load("resources/images/choosing_cat2_frame.png").convert_alpha()

    screen.blit(list_frame, (75, 360))
    screen.blit(cat1_frame, (40, 113))
    screen.blit(cat2_frame, (494, 113))


class ChooseMentorScreen(Screens):
    ui = None
    def on_use(self):

        if ChooseMentorScreen.ui is None:
            draw_choosing_bg(self)
            ChooseMentorScreen.ui = draw_choosing_bg(self)

        buttons.draw_image_button((25, 645),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  chosen_cat=None,
                                  show_details=False)

        verdana_big.text('Choose Mentor', ('center', 30))
        living_cats = []
        for cat in Cat.all_cats.values():
            if not cat.dead and cat != game.switches[
                    'apprentice'].mentor and cat.status in [
                        'warrior', 'deputy', 'leader'
                    ]:
                living_cats.append(cat)
        all_pages = 1
        if len(living_cats) > 20:
            all_pages = int(ceil(len(living_cats) / 20.0))
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(living_cats)):
            if x + (game.switches['list_page'] - 1) * 20 > len(living_cats):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_cat = living_cats[x + (game.switches['list_page'] - 1) * 20]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y),
                                    image=the_cat.sprite,
                                    cat=the_cat.ID,
                                    cur_screen='choose mentor screen2')

                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name),
                             (130 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 20 or x + (game.switches['list_page'] -
                                              1) * 20 == len(living_cats) - 1:
                    break
        verdana.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600),
                                text='<',
                                list_page=game.switches['list_page'] - 1,
                                hotkey=[23])

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600),
                                text='>',
                                list_page=game.switches['list_page'] + 1,
                                hotkey=[21])


class ChooseMentorScreen2(Screens):

    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = Cat.all_cats.get(game.switches['cat'])

        # back and next buttons on the profile page
        previous_cat = 0
        next_cat = 0

        for check_cat in Cat.all_cats:
            if Cat.all_cats[check_cat].ID == the_cat.ID:
                next_cat = 1

            if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != the_cat.ID and not Cat.all_cats[
                        check_cat].dead and Cat.all_cats[
                            check_cat].status in [
                                'warrior', 'deputy', 'leader'
                            ] and Cat.all_cats[check_cat] != game.switches[
                                'apprentice'].mentor and not Cat.all_cats[
                                    check_cat].exiled:
                previous_cat = Cat.all_cats[check_cat].ID
            elif next_cat == 1 and Cat.all_cats[check_cat].ID != the_cat.ID and not Cat.all_cats[check_cat].dead and Cat.all_cats[check_cat].status in ['warrior',
                                                                                                                                                                          'deputy',
                                                                                                                                                                          'leader'] and \
                    Cat.all_cats[check_cat] != game.switches['apprentice'].mentor and not Cat.all_cats[
                    check_cat].exiled:
                next_cat = Cat.all_cats[check_cat].ID
            elif int(next_cat) > 1:
                break

        if next_cat == 1:
            next_cat = 0

        if next_cat != 0:
            buttons.draw_button((-40, 40),
                                text='Next Cat',
                                cat=next_cat,
                                hotkey=[21])
        if previous_cat != 0:
            buttons.draw_button((40, 40),
                                text='Previous Cat',
                                cat=previous_cat,
                                hotkey=[23])

        # Info in string
        cat_name = str(the_cat.name)  # name
        cat_thought = the_cat.thought  # thought

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 70))  # NAME
        draw_large(the_cat, ('center', 100))  # IMAGE
        verdana_small.text(the_cat.genderalign, (250, 330 + count * 15))
        count += 1  # SEX / GENDER
        verdana_small.text(the_cat.status, (450, 330 + count2 * 15))
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name),
                                   (450, 330 + count2 * 15))
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
        if len(the_cat.former_apprentices
               ) != 0 and the_cat.former_apprentices[0] is not None:
            if len(the_cat.former_apprentices) == 1:
                former_apps = 'former apprentice: ' + str(
                    the_cat.former_apprentices[0].name)
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
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(),
                           (250, 330 + count * 15))
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(),
                           (250, 330 + count * 15))
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length,
                           (250, 330 + count * 15))
        count += 1  # PELT LENGTH

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (250, 330 + count * 15))
            count += 1
        elif the_cat.parent2 is None:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown',
                               (250, 330 + count * 15))
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

            verdana_small.text('parents: ' + par1 + ' and ' + par2,
                               (250, 330 + count * 15))
            count += 1

        # MOONS
        if the_cat.dead:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moon) + ' moons (in life)',
                    (250, 330 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons (in life)',
                    (250, 330 + count * 15))
                count += 1
            if the_cat.dead_for == 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moon (in death)',
                    (250, 330 + count * 15))
                count += 1
            elif the_cat.dead_for != 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moons (in death)',
                    (250, 330 + count * 15))
                count += 1
        else:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moon', (250, 330 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons', (250, 330 + count * 15))
                count += 1

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in Cat.all_cats:
                if Cat.all_cats.get(
                        the_cat.mate
                ).dead:  # TODO: fix when mate dies mate becomes none
                    verdana_small.text(
                        'former mate: ' +
                        str(Cat.all_cats[the_cat.mate].name),
                        (250, 330 + count * 15))
                else:
                    verdana_small.text(
                        'mate: ' + str(Cat.all_cats[the_cat.mate].name),
                        (250, 330 + count * 15))
                count += 1
            else:
                verdana_small.text(
                    'Error: mate: ' + str(the_cat.mate) + " not found",
                    ('center', 495))

        # experience
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (450, 330 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (450, 330 + count2 * 15))
            count2 += 1

        # buttons

        buttons.draw_button(
            ('center', -100),
            text='Choose as ' + str(game.switches['apprentice'].name) +
            '\'s mentor',
            cur_screen=game.switches['last_screen'],
            cat_value=the_cat,
            apprentice=game.switches['apprentice'])
        buttons.draw_button(('center', -50),
                            text='Back',
                            cur_screen='clan screen',
                            hotkey=[0])

class ViewChildrenScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats[game.switches['cat']]
        verdana_big.text(f'Family of {str(the_cat.name)}', ('center', 50))
        verdana.text('Parents:', ('center', 85))
        if the_cat.parent1 is None:
            verdana_small.text('Unknown', (342, 165))
        elif the_cat.parent1 in Cat.all_cats:
            buttons.draw_button(
                (350, 120),
                image=Cat.all_cats[the_cat.parent1].sprite,
                cat=the_cat.parent1,
                cur_screen='profile screen')

            name_len = verdana.text(
                str(Cat.all_cats[the_cat.parent1].name))
            verdana_small.text(str(Cat.all_cats[the_cat.parent1].name),
                               (375 - name_len / 2, 185))

        else:
            verdana_small.text(f'Error: cat {str(the_cat.parent1)} not found',
                               (342, 165))
        if the_cat.parent2 is None:
            verdana_small.text('Unknown', (422, 165))
        elif the_cat.parent2 in Cat.all_cats:
            buttons.draw_button(
                (430, 120),
                image=Cat.all_cats[the_cat.parent2].sprite,
                cat=the_cat.parent2,
                cur_screen='profile screen')

            name_len = verdana.text(
                str(Cat.all_cats[the_cat.parent2].name))
            verdana_small.text(str(Cat.all_cats[the_cat.parent2].name),
                               (455 - name_len / 2, 185))

        else:
            verdana_small.text(
                'Error: cat ' + str(the_cat.parent2) + ' not found',
                (342, 165))

        pos_x = 0
        pos_y = 20
        siblings = False
        for x in game.clan.clan_cats:
            if (Cat.all_cats[x].parent1 in (the_cat.parent1, the_cat.parent2) or Cat.all_cats[x].parent2 in (
                    the_cat.parent1, the_cat.parent2) and the_cat.parent2 is not None) and the_cat.ID != Cat.all_cats[x].ID and the_cat.parent1 is not None and \
                    Cat.all_cats[x].parent1 is not None:
                buttons.draw_button((40 + pos_x, 220 + pos_y),
                                    image=Cat.all_cats[x].sprite,
                                    cat=Cat.all_cats[x].ID,
                                    cur_screen='profile screen')

                name_len = verdana.text(str(Cat.all_cats[x].name))
                verdana_small.text(str(Cat.all_cats[x].name),
                                   (65 + pos_x - name_len / 2, 280 + pos_y))

                siblings = True
                pos_x += 80
                if pos_x > 640:
                    pos_y += 70
                    pos_x = 0
        if siblings:
            verdana.text('Siblings:', ('center', 210))
        else:
            verdana.text('This cat has no siblings.', ('center', 210))
        buttons.draw_button(('center', -100),
                            text='Back',
                            cur_screen='profile screen')
        pos_x = 0
        pos_y = 60
        kittens = False
        for x in game.clan.clan_cats:
            if the_cat.ID in [
                    Cat.all_cats[x].parent1,
                    Cat.all_cats[x].parent2
            ]:
                buttons.draw_button((40 + pos_x, 370 + pos_y),
                                    image=Cat.all_cats[x].sprite,
                                    cat=Cat.all_cats[x].ID,
                                    cur_screen='profile screen')

                name_len = verdana.text(str(Cat.all_cats[x].name))
                verdana_small.text(str(Cat.all_cats[x].name),
                                   (65 + pos_x - name_len / 2, 430 + pos_y))

                kittens = True
                pos_x += 80
                if pos_x > 640:
                    pos_y += 70
                    pos_x = 0
        if kittens:
            verdana.text('Offspring:', ('center', 400))
        else:
            verdana.text('This cat has never had offspring.', ('center', 400))
        buttons.draw_button(('center', -100),
                            text='Back',
                            cur_screen='profile screen')

    def screen_switches(self):
        cat_profiles()

class ChooseMateScreen(Screens):

    ui = None
    def on_use(self):
        the_cat = Cat.all_cats[game.switches['cat']]

        if ChooseMateScreen.ui is None:
            ChooseMateScreen.ui = draw_choosing_bg(self)

        y_value = 30
        verdana_big.text(f'Choose mate for {str(the_cat.name)}',
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
            'is heightened.',
            ('center', y_value))

        draw_large(the_cat, (50, 150))
        self.show_cat_info(the_cat, 212, 71)
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
            self.show_cat_info(mate, 506, 622)
            if the_cat.gender == mate.gender and not game.settings[
                    'no gendered breeding'] and the_cat.mate is None:
                verdana_small.text(
                    '(this pair will not be able to have kittens)',
                    ('center', 310))

        valid_mates = []
        pos_x = 0
        pos_y = 20
        if the_cat.mate is None:
            self.get_valid_mates(the_cat, valid_mates, pos_x, pos_y)
        else:
            verdana.text('Already in a relationship.', ('center', 313))
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
            buttons.draw_button((323, 278),
                                      image='buttons/its_official',
                                      text="It\'s official!",
                                      cat_value=the_cat,
                                      mate=mate
                                      )

        elif the_cat.mate is not None:
            buttons.draw_button((323, 278),
                                      image='buttons/break_up',
                                      text="Break it up...",
                                      cat_value=the_cat,
                                      mate=None)

        buttons.draw_image_button((25, 645),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  )


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
                                mate=pot_mate.ID)

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
            ('center', 600))

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
    def show_cat_info(self, arg0, arg1, arg2):
        name = str(arg0.name)  # get name
        if len(name) >= 10:  # check name length
            short_name = str(arg0.name)[0:9]
            name = short_name + '...'
        verdana.text(str(name).center(16), (arg2, 121))

        y_value = 193

        verdana_small.text(arg0.age, (arg1, y_value))
        y_value += 15

        if arg0.age != 'elder':
            verdana_small.text(str(arg0.status), (arg1, y_value))
            y_value += 15

        if arg0.genderalign is not None:
            verdana_small.text(arg0.genderalign, (arg1, y_value))
        else:
            verdana_small.text(arg0.gender, (arg1, y_value))
        y_value += 15

        verdana_small.text(arg0.trait, (arg1, y_value))




def draw_bg_ui(self):  # USER INTERFACE ART

    # SEARCH BAR
    search_bar = pygame.transform.scale(
        pygame.image.load("resources/images/relationship_search.png").convert_alpha(), (228, 39))
    screen.blit(search_bar, (536, 90))

    # LOAD AND BLIT BG FRAMES
    details_frame = pygame.transform.scale(
        pygame.image.load("resources/images/relationship_details_frame.png").convert_alpha(), (254, 344))

    toggle_frame = pygame.transform.scale(
        pygame.image.load("resources/images/relationship_toggle_frame.png").convert_alpha(), (251, 120))

    list_frame = pygame.transform.scale(
        pygame.image.load("resources/images/relationship_list_frame.png").convert_alpha(), (502, 500))

    screen.blit(details_frame, (25, 130))
    screen.blit(toggle_frame, (45, 484))
    screen.blit(list_frame, (273, 122))



class RelationshipScreen(Screens):
    bool = {True: 'on', False: 'off', None: 'None'}
    ui = None

    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                   game.clan.instructor
                                   )
        # this cat is the current cat in focus - aka the cat we're viewing the relationships of

        # back and next buttons on the relationships page, these will reset the show_details cat
        draw_next_prev_cat_buttons(the_cat)

        # LOAD UI IMAGES
        if RelationshipScreen.ui is None:
            RelationshipScreen.ui = draw_bg_ui(self)

        # SEARCH TEXT
        search_text = game.switches['search_text']

        verdana_black.text(game.switches['search_text'], (612, 97))

        # MAKE A LIST OF RELATIONSHIPS
        search_relations = []
        if search_text.strip() != '':
            for rel in the_cat.relationships:
                if search_text.lower() in str(rel.cat_to.name).lower():
                    search_relations.append(rel)
        else:
            search_relations = the_cat.relationships.copy()

        # VIEW TOGGLES
        verdana_mid_dark.text(
            f"Show Dead",
            (70, 513))

        if game.settings['show dead relation'] is False:
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

        if game.settings['show dead relation'] is True:
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

        if game.settings['show empty relation'] is False:
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

        if game.settings['show empty relation'] is True:
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
                    f"{str(the_cat.genderalign)} - {str(the_cat.age)} - {str(the_cat.trait)} - mate: {str(mate.name)}",
                    (80, 100))
            else:
                verdana_small.text(
                    f"{str(the_cat.genderalign)}  - {str(the_cat.age)} - {str(the_cat.trait)}",
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
            # BUG: clicking this button also causes the chosen_cat to overwrite the last cat on the list pages

            # CHECK NAME LENGTH - SHORTEN IF NECESSARY
            name = str(the_relationship.cat_to.name)  # get name
            if len(name) >= 12:  # check name length
                short_name = str(the_relationship.cat_to.name)[0:11]
                name = short_name + '...'

            verdana_mid_dark.text(name, (290 + pos_x, 131 + pos_y))  # display name


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
            verdana_small_dark.text(
                'comfortable:',  # eventual progression to 'secure'?
                (292 + pos_x, 173 + pos_y + count))
            count += 20
            current_x = 294 + pos_x
            current_y = 172 + pos_y + count
            self.draw_bar(the_relationship.comfortable, current_x, current_y)

            count += 5

            # JEALOUS DISPLAY
            verdana_small_dark.text(
                'jealousy:',  # eventual progression to 'resentment'?
                (292 + pos_x, 171 + pos_y + count))
            count += 20
            current_x = 294 + pos_x
            current_y = 170 + pos_y + count
            self.draw_bar(the_relationship.jealousy, current_x, current_y)

            count += 5

            # TRUST DISPLAY
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
            if len(chosen_name) >= 17:
                chosen_short_name = str(game.switches['chosen_cat'].name)[0:16]
                chosen_name = chosen_short_name + '...'

            # NAME
            if game.switches['chosen_cat'].dead:
                verdana_big_dark.text(
                    f"{chosen_name} (dead)",
                    (60, 295)
                )
            else:
                verdana_big_dark.text(
                    f"{chosen_name}",
                    (60, 295)
                )

            # DRAW CAT
            draw_large(game.switches['chosen_cat'], (75, 145))

            # GENDER
            verdana_small_dark.text(
                f"{str(game.switches['chosen_cat'].genderalign)}",
                (60, 325))
            self.draw_gender_icon(235, 145)

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
                self.draw_mate_icon()

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
                self.draw_relation_icon()

            elif game.switches['chosen_cat'].is_grandparent(the_cat):
                verdana_small_dark.text(
                    'related: grandparent',
                    (x_value, y_value))
                self.draw_relation_icon()

            elif the_cat.is_grandparent(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related: grandchild',
                    (x_value, y_value))
                self.draw_relation_icon()

            elif game.switches['chosen_cat'].is_parent(the_cat):
                verdana_small_dark.text(
                    'related: parent',
                    (x_value, y_value))
                self.draw_relation_icon()

            elif the_cat.is_parent(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related: child',
                    (x_value, y_value))
                self.draw_relation_icon()

            elif game.switches['chosen_cat'].is_sibling(the_cat) or the_cat.is_sibling(game.switches['chosen_cat']):
                verdana_small_dark.text(
                    'related: sibling',
                    (x_value, y_value))
                self.draw_relation_icon()



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

    def draw_gender_icon(self, x_pos, y_pos):

        female_icon = pygame.image.load("resources/images/female_big.png").convert_alpha()
        male_icon = pygame.image.load("resources/images/male_big.png").convert_alpha()
        nonbi_icon = pygame.image.load("resources/images/nonbi_big.png").convert_alpha()
        transfem_icon = pygame.image.load("resources/images/transfem_big.png").convert_alpha()
        transmasc_icon = pygame.image.load("resources/images/transmasc_big.png").convert_alpha()

        if game.switches['chosen_cat'].genderalign == 'female':
            screen.blit(female_icon, (x_pos, y_pos))
        if game.switches['chosen_cat'].genderalign == 'male':
            screen.blit(male_icon, (x_pos, y_pos))
        if game.switches['chosen_cat'].genderalign != 'female' and game.switches['chosen_cat'].genderalign != 'male' \
                and game.switches['chosen_cat'].genderalign != 'trans female' and game.switches['chosen_cat'].genderalign != 'trans male':
            screen.blit(nonbi_icon, (x_pos, y_pos))
        if game.switches['chosen_cat'].genderalign == 'trans female':
            screen.blit(transfem_icon, (x_pos, y_pos))
        if game.switches['chosen_cat'].genderalign == 'trans  male':
            screen.blit(transmasc_icon, (x_pos, y_pos))

    def draw_mate_icon(self):

        mate_icon = pygame.image.load("resources/images/heart_big.png").convert_alpha()
        screen.blit(mate_icon, (45, 150))


    def draw_relation_icon(self):

        family_icon = pygame.image.load("resources/images/dot_big.png").convert_alpha()
        screen.blit(family_icon, (45, 150))

    def draw_bar(self, value, pos_x, pos_y):
        # Loading Bar and variables
        bar_bg = pygame.image.load(
            "resources/images/relations_border.png").convert_alpha()
        bar_bg_dark = pygame.image.load(
            "resources/images/relations_border_dark.png").convert_alpha()
        original_bar = pygame.image.load(
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

    def screen_switches(self):
        cat_profiles()
