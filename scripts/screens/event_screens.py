from random import choice

from .base_screens import Screens, draw_menu_buttons, cat_profiles

from scripts.events import events_class
from scripts.patrol import patrol
from scripts.utility import draw
from scripts.game_structure.buttons import buttons
from scripts.game_structure.text import *

class SingleEventScreen(Screens):

    def on_use(self):
        # LAYOUT
        if game.switches['event'] is not None:
            events_class.all_events[game.switches['event']].page()

        # buttons
        buttons.draw_button(('center', -150),
                            text='Continue',
                            cur_screen='events screen')

    def screen_switches(self):
        pass

class RelationshipEventScreen(Screens):

    def on_use(self):
        a = 0
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text(
            'Check this page to see which events are currently happening at the Clan.',
            ('center', 110))

        verdana.text(f'Current season: {str(game.clan.current_season)}',
                     ('center', 140))

        if game.clan.age == 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moon',
                         ('center', 170))
        if game.clan.age != 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moons',
                         ('center', 170))

        if game.switches['events_left'] == 0:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                timeskip=True,
                                hotkey=[11])
            if game.switches['timeskip']:
                game.cur_events_list = []
                game.relation_events_list = []
        else:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                available=False)
        events_class.one_moon()

        # show the clan events
        buttons.draw_button((-250, 220),
                            text='CLAN EVENTS',
                            cur_screen='events screen',
                            hotkey=[12])

        if game.relation_events_list is not None and game.relation_events_list != []:
            for x in range(
                    min(len(game.relation_events_list),
                        game.max_relation_events_displayed)):
                if game.relation_events_list[x] is None:
                    continue
                verdana.text(game.relation_events_list[x],
                             ('center', 260 + a * 30))
                a += 1
        else:
            verdana.text("Nothing significant happened this moon.",
                         ('center', 260 + a * 30))
        # buttons
        draw_menu_buttons()

        if len(game.relation_events_list) > game.max_relation_events_displayed:
            buttons.draw_button((700, 180),
                                image=game.up,
                                arrow="UP",
                                hotkey=[20])
            buttons.draw_button((700, 630),
                                image=game.down,
                                arrow="DOWN",
                                hotkey=[22])

    def screen_switches(self):
        cat_profiles()

class EventsScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text(
            'Check this page to see which events are currently happening at the Clan.',
            ('center', 110))

        verdana.text(f'Current season: {str(game.clan.current_season)}',
                     ('center', 140))

        if game.clan.age == 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moon',
                         ('center', 170))
        if game.clan.age != 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moons',
                         ('center', 170))

        if game.switches['events_left'] == 0:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                timeskip=True,
                                hotkey=[11])
            if game.switches['timeskip']:
                game.cur_events_list = []
                game.relation_events_list = []
        else:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                available=False)
        events_class.one_moon()

        # show the Relationshipevents
        buttons.draw_button((-200, 220),
                            text='RELATIONSHIP EVENTS',
                            cur_screen='relationship event screen',
                            hotkey=[12])

        a = 0
        if game.cur_events_list is not None and game.cur_events_list != []:
            for x in range(min(len(game.cur_events_list), game.max_events_displayed)):
                #TODO: Find the real cause for game.cur_events_list[x] being a function sometimes
                if game.cur_events_list[x] is None or not isinstance(game.cur_events_list[x], str):
                    continue
                if "Clan has no " in game.cur_events_list[x]:
                    verdana_red.text(game.cur_events_list[x],
                                     ('center', 260 + a * 30))
                else:
                    verdana.text(game.cur_events_list[x],
                                 ('center', 260 + a * 30))
                a += 1
        else:
            verdana.text("Nothing significant happened this moon.",
                         ('center', 260 + a * 30))

        draw_menu_buttons()
        if len(game.cur_events_list) > game.max_events_displayed:
            buttons.draw_button((700, 180),
                                image=game.up,
                                arrow="UP",
                                hotkey=[20])
            buttons.draw_button((700, 630),
                                image=game.down,
                                arrow="DOWN",
                                hotkey=[22])

class PatrolEventScreen(Screens):

    def get_list_text(self, patrol_list):
        if not patrol_list:
            return "None"
        # Removes duplicates.
        patrol_set = list(patrol_list)
        return ", ".join(patrol_set)

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        if game.switches['event'] == 0:
            patrol.add_patrol_cats()
            possible_events = patrol.get_possible_patrols(
                game.clan.current_season,
                game.clan.biome,
                game.clan.all_clans,
                game.settings.get('disasters')
            )
            patrol.patrol_event = choice(possible_events)
            if patrol.patrol_event.win_trait is not None:
                win_trait = patrol.patrol_event.win_trait
                patrol_trait = patrol.patrol_traits.index(win_trait)
                patrol.patrol_stat_cat = patrol.patrol_cats[patrol_trait]
            game.switches['event'] = -1
        if game.switches['event'] == -1:
            intro_text = patrol.patrol_event.intro_text
            patrol_size = len(patrol.patrol_cats)
            if patrol_size < 2: # adjusting text for solo patrols
                intro_text = intro_text.replace('Your patrol',
                                                str(patrol.patrol_leader.name))
                intro_text = intro_text.replace('The patrol',
                                                str(patrol.patrol_leader.name))
            intro_text = patrol.patrol_event.intro_text
            intro_text = intro_text.replace('r_c',
                                            str(patrol.patrol_random_cat.name))
            intro_text = intro_text.replace('p_l',
                                            str(patrol.patrol_leader.name))
            intro_text = intro_text.replace('o_c_n', str(patrol.other_clan.name) + 'Clan')
            intro_text = intro_text.replace('c_n', str(game.clan.name) + 'Clan')
            if patrol.patrol_stat_cat is not None:
                intro_text = intro_text.replace('s_c', str(patrol.patrol_stat_cat.name))
            verdana.blit_text(intro_text, (150, 200))
            buttons.draw_button((290, 320), text='Proceed', event=-2)
            buttons.draw_button((150, 320), text='Do Not Proceed', event=2)
            if patrol.patrol_event.patrol_id in [500, 501, 502, 503, 510, 800, 801, 802, 803, 804, 805]:
                buttons.draw_button((150, 290), text='Antagonize', event=3)

        if game.switches['event'] == -2:
            patrol.calculate_success()
            game.switches['event'] = 1
        elif game.switches['event'] == 3:
            patrol.calculate_success_antagonize()
            game.switches['event'] = 4
        if game.switches['event'] > 0:
            if game.switches['event'] == 1:
                if patrol.success:
                    success_text = patrol.patrol_event.success_text
                    patrol_size = len(patrol.patrol_cats)
                    if patrol_size < 2:  # adjusting text for solo patrols
                        success_text = success_text.replace('Your patrol',
                                                        str(patrol.patrol_leader.name))
                        success_text = success_text.replace('The patrol',
                                                        str(patrol.patrol_leader.name))
                    success_text = success_text.replace(
                        'r_c', str(patrol.patrol_random_cat.name))
                    success_text = success_text.replace(
                        'p_l', str(patrol.patrol_leader.name))
                    success_text = success_text.replace(
                        'o_c_n', str(patrol.other_clan.name) + 'Clan')
                    success_text = success_text.replace(
                        'c_n', str(game.clan.name) + 'Clan')
                    if patrol.patrol_stat_cat is not None:
                        success_text = success_text.replace(
                        's_c', str(patrol.patrol_stat_cat.name))
                    verdana.blit_text(success_text, (150, 200))
                else:
                    fail_text = patrol.patrol_event.fail_text
                    patrol_size = len(patrol.patrol_cats)
                    if patrol_size < 2:  # adjusting text for solo patrols
                        fail_text = fail_text.replace('Your patrol',
                                                            str(patrol.patrol_leader.name))
                        fail_text = fail_text.replace('The patrol',
                                                            str(patrol.patrol_leader.name))
                    fail_text = fail_text.replace(
                        'r_c', str(patrol.patrol_random_cat.name))
                    fail_text = fail_text.replace(
                        'p_l', str(patrol.patrol_leader.name))
                    fail_text = fail_text.replace(
                        'o_c_n', str(patrol.other_clan.name) + 'Clan')
                    fail_text = fail_text.replace(
                        'c_n', str(game.clan.name) + 'Clan')
                    if patrol.patrol_stat_cat is not None:
                        fail_text = fail_text.replace(
                        's_c', str(patrol.patrol_stat_cat.name))
                    verdana.blit_text(fail_text, (150, 200))
            elif game.switches['event'] == 2:
                decline_text = patrol.patrol_event.decline_text
                patrol_size = len(patrol.patrol_cats)
                if patrol_size < 2:  # adjusting text for solo patrols
                    decline_text = decline_text.replace('Your patrol',
                                                        str(patrol.patrol_leader.name))
                    decline_text = decline_text.replace('The patrol',
                                                        str(patrol.patrol_leader.name))
                decline_text = decline_text.replace(
                    'r_c', str(patrol.patrol_random_cat.name))
                decline_text = decline_text.replace(
                    'p_l', str(patrol.patrol_leader.name))
                decline_text = decline_text.replace(
                        'o_c_n', str(patrol.other_clan.name) + 'Clan')
                decline_text = decline_text.replace(
                        'c_n', str(game.clan.name) + 'Clan')
                if patrol.patrol_stat_cat is not None:
                        decline_text = decline_text.replace(
                        's_c', str(patrol.patrol_stat_cat.name))
                verdana.blit_text(decline_text, (150, 200))
            elif game.switches['event'] == 4:
                antagonize_text = patrol.patrol_event.antagonize_text
                patrol_size = len(patrol.patrol_cats)
                if patrol.success:
                    if patrol_size < 2:  # adjusting text for solo patrols
                        antagonize_text = antagonize_text.replace('Your patrol',
                                                            str(patrol.patrol_leader.name))
                        antagonize_text = antagonize_text.replace('The patrol',
                                                            str(patrol.patrol_leader.name))
                    antagonize_text = antagonize_text.replace(
                        'r_c', str(patrol.patrol_random_cat.name))
                    antagonize_text = antagonize_text.replace(
                        'p_l', str(patrol.patrol_leader.name))
                    antagonize_text = antagonize_text.replace(
                            'o_c_n', str(patrol.other_clan.name) + 'Clan')
                    antagonize_text = antagonize_text.replace(
                            'c_n', str(game.clan.name) + 'Clan')
                    if patrol.patrol_stat_cat is not None:
                            antagonize_text = antagonize_text.replace(
                            's_c', str(patrol.patrol_stat_cat.name))
                else:
                    antagonize_fail_text = patrol.patrol_event.antagonize_fail_text
                    if patrol_size < 2:  # adjusting text for solo patrols
                        antagonize_fail_text = antagonize_fail_text.replace('Your patrol',
                                                            str(patrol.patrol_leader.name))
                        antagonize_fail_text = antagonize_fail_text.replace('The patrol',
                                                            str(patrol.patrol_leader.name))
                    antagonize_fail_text = antagonize_fail_text.replace(
                        'r_c', str(patrol.patrol_random_cat.name))
                    antagonize_fail_text = antagonize_fail_text.replace(
                        'p_l', str(patrol.patrol_leader.name))
                    antagonize_fail_text = antagonize_fail_text.replace(
                            'o_c_n', str(patrol.other_clan.name) + 'Clan')
                    antagonize_fail_text = antagonize_fail_text.replace(
                            'c_n', str(game.clan.name) + 'Clan')
                    if patrol.patrol_stat_cat is not None:
                            antagonize_fail_text = antagonize_fail_text.replace(
                            's_c', str(patrol.patrol_stat_cat.name))
                verdana.blit_text(antagonize_text, (150, 200))
            buttons.draw_button((150, 350),
                                text='Return to Clan',
                                cur_screen='clan screen')
            buttons.draw_button((280, 350),
                                text='Patrol Again',
                                cur_screen='patrol screen')

        for u in range(6):
            if u < len(patrol.patrol_cats):
                draw(patrol.patrol_cats[u],(50, 200 + 50 * (u)))
        verdana_small.blit_text('season: ' + str(game.clan.current_season),
                                (150, 400))
        verdana_small.blit_text(
            'patrol leader: ' + patrol.patrol_leader_name, (150, 430))
        verdana_small.blit_text(
            'patrol members: ' + self.get_list_text(patrol.patrol_names),
            (150, 460))
        verdana_small.blit_text(
            'patrol skills: ' + self.get_list_text(patrol.patrol_skills),
            (150, 510))
        verdana_small.blit_text(
            'patrol traits: ' + self.get_list_text(patrol.patrol_traits),
            (150, 560))
        draw_menu_buttons()

    def screen_switches(self):
        game.switches['event'] = 0
        cat_profiles()

