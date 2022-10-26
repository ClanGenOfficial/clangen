from random import choice

from .base_screens import Screens, draw_menu_buttons, cat_profiles, draw_clan_name

from scripts.utility import draw, draw_large
from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat

class PatrolScreen(Screens):

    def on_use(self):
        draw_clan_name()
        verdana.text(
            'These cats are currently in the camp, ready for a patrol.',
            ('center', 115))
        verdana.text('Choose up to six to take on patrol.', ('center', 135))
        verdana.text(
            'Smaller patrols help cats gain more experience, but larger patrols are safer.',
            ('center', 155))

        draw_menu_buttons()
        able_cats = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and the_cat.in_camp and the_cat not in game.patrolled and the_cat.status in [
                    'leader', 'deputy', 'warrior', 'apprentice'
            ] and not the_cat.exiled:

                able_cats.append(the_cat)
        if not game.patrol_cats:
            i_max = min(len(able_cats), 12)
            for i in range(i_max):
                test_cat = choice(able_cats)
                able_cats.remove(test_cat)
                game.patrol_cats[i] = test_cat
        else:
            i_max = len(game.patrol_cats)
        random_options = []
        for u in range(6):
            if u < i_max:
                if game.patrol_cats[u] in game.switches['current_patrol']:
                    draw(game.patrol_cats[u],(screen_x / 2 - 50 * (u + 2), 550))
                else:
                    buttons.draw_button((50, 150 + 50 * u),
                                        image=game.patrol_cats[u].sprite,
                                        cat=u,
                                        hotkey=[u + 1, 11])
                    random_options.append(game.patrol_cats[u])
        for u in range(6, 12):
            if u < i_max:
                if game.patrol_cats[u] in game.switches['current_patrol']:
                    draw(game.patrol_cats[u],(screen_x / 2 + 50 * (u - 5), 550))
                else:
                    buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)),
                                        image=game.patrol_cats[u].sprite,
                                        cat=u,
                                        hotkey=[u + 1, 12])
                    random_options.append(game.patrol_cats[u])
        if random_options and len(game.switches['current_patrol']) < 6:
            random_patrol = choice(random_options)
            buttons.draw_button(('center', 530),
                                text='Add Random',
                                current_patrol=random_patrol,
                                add=True,
                                hotkey=[12])

        else:
            buttons.draw_button(('center', 530),
                                text='Add Random',
                                available=False)
        if game.switches['cat'] is not None and 12 > game.switches[
                'cat'] >= 0 and game.patrol_cats[game.switches[
                    'cat']] not in game.switches['current_patrol']:
            self._extracted_from_on_use_58()
        if len(game.switches['current_patrol']) > 0:
            buttons.draw_button(('center', 630),
                                text='Start Patrol',
                                cur_screen='patrol event screen',
                                hotkey=[13])

        else:
            buttons.draw_button(('center', 630),
                                text='Start Patrol',
                                available=False)

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_58(self):
        chosen_cat = game.patrol_cats[game.switches['cat']]
        draw_large(chosen_cat,(320, 200))
        verdana.text(str(game.patrol_cats[game.switches['cat']].name),
                     ('center', 360))
        verdana_small.text(str(game.patrol_cats[game.switches['cat']].status),
                           ('center', 385))

        verdana_small.text(str(game.patrol_cats[game.switches['cat']].trait),
                           ('center', 405))

        verdana_small.text(str(game.patrol_cats[game.switches['cat']].skill),
                           ('center', 425))

        verdana_small.text(
            'experience: ' +
            str(game.patrol_cats[game.switches['cat']].experience_level),
            ('center', 445))

        if game.patrol_cats[game.switches['cat']].status == 'apprentice':
            if game.patrol_cats[game.switches['cat']].mentor is not None:
                verdana_small.text(
                    'mentor: ' +
                    str(game.patrol_cats[game.switches['cat']].mentor.name),
                    ('center', 465))

        if len(game.switches['current_patrol']) < 6:
            buttons.draw_button(
                ('center', 500),
                text='Add to Patrol',
                current_patrol=game.patrol_cats[game.switches['cat']],
                add=True,
                hotkey=[11])

    def screen_switches(self):
        game.switches['current_patrol'] = []
        game.switches['cat'] = None
        game.patrol_cats = {}
        game.switches['event'] = 0
        cat_profiles()
