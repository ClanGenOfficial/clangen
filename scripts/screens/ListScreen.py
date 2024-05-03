import pygame
from math import ceil
import pygame_gui

from .Screens import Screens
from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UISpriteButton, UIImageButton
from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER


class ListScreen(Screens):
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20
    list_page = 1
    display_cats = []
    cat_names = []

    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.filter_options_visible = True
        self.group_options_visible = False
        self.death_status = "living"
        self.current_group = "clan"
        self.full_cat_list = []

        self.bg = None
        self.df_button = None
        self.ur_button = None
        self.sc_button = None
        self.show_living_button = None
        self.search_bar_image = None
        self.cotc_button = None
        self.choose_group_button = None
        self.show_dead_button = None
        self.filter_by_rank = None
        self.filter_by_ID = None
        self.filter_by_death = None
        self.filter_by_age = None
        self.filter_by_age_reverse = None
        self.filter_by_exp = None
        self.filter_age = None
        self.filter_age_reverse = None
        self.filter_id = None
        self.filter_rank = None
        self.filter_death = None
        self.filter_exp = None
        self.filter_fav = None
        self.filter_not_fav = None
        self.search_bar = None
        self.page_number = None
        self.previous_page_button = None
        self.next_page_button = None
        self.outside_clan_button = None
        self.your_clan_button = None
        self.to_dead_button = None
        self.filter_container = None
        self.all_pages = None
        self.current_listed_cats = None

        self.sc_bg = pygame.transform.scale(
            pygame.image.load("resources/images/starclanbg.png").convert(),
            (screen_x, screen_y))
        self.df_Bg = pygame.transform.scale(
            pygame.image.load("resources/images/darkforestbg.png").convert(),
            (screen_x, screen_y))
        self.ur_bg = pygame.transform.scale(
            pygame.image.load("resources/images/urbg.png").convert(),
            (screen_x, screen_y))

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.choose_group_button and not self.group_options_visible:
                self.update_view_buttons()
            elif event.ui_element == self.choose_group_button and self.group_options_visible:
                self.update_view_buttons()
            elif event.ui_element == self.your_clan_button:
                self.update_view_buttons()
                self.get_your_clan_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.cotc_button:
                self.update_view_buttons()
                self.get_cotc_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.sc_button:
                self.update_view_buttons()
                self.get_sc_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.df_button:
                self.update_view_buttons()
                self.get_df_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.ur_button:
                self.update_view_buttons()
                self.get_ur_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.show_dead_button:
                self.death_status = 'dead'
                self.group_options_visible = True
                self.filter_options_visible = True
                self.update_view_buttons()
                self.update_filter_buttons()
                self.show_dead_button.hide()
                self.show_living_button.show()
                self.get_sc_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.show_living_button:
                if game.sort_type == 'death':
                    game.sort_type = 'rank'
                self.death_status = 'living'
                self.group_options_visible = True
                self.filter_options_visible = True
                self.update_view_buttons()
                self.update_filter_buttons()
                self.update_bg()
                self.show_dead_button.show()
                self.show_living_button.hide()
                self.get_your_clan_cats()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.next_page_button:
                self.list_page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.list_page -= 1
                self.update_page()
            elif event.ui_element == self.filter_fav:
                self.filter_not_fav.show()
                self.filter_fav.hide()
                game.clan.clan_settings["show fav"] = False
                self.update_page()
            elif event.ui_element == self.filter_not_fav:
                self.filter_not_fav.hide()
                self.filter_fav.show()
                game.clan.clan_settings["show fav"] = True
                self.update_page()
            elif event.ui_element in [self.filter_by_death,
                                      self.filter_by_ID,
                                      self.filter_by_exp,
                                      self.filter_by_age,
                                      self.filter_by_age_reverse,
                                      self.filter_by_rank]:
                self.update_filter_buttons()
            elif event.ui_element == self.filter_age:
                game.sort_type = "age"
                self.update_filter_buttons()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_age_reverse:
                game.sort_type = "reverse_age"
                self.update_filter_buttons()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_rank:
                game.sort_type = "rank"
                self.update_filter_buttons()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_id:
                game.sort_type = "id"
                self.update_filter_buttons()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_exp:
                game.sort_type = "exp"
                self.update_filter_buttons()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element == self.filter_death:
                game.sort_type = "death"
                self.update_filter_buttons()
                self.update_search_cats(self.search_bar.get_text())
            elif event.ui_element in self.display_cats:
                game.switches["cat"] = event.ui_element.return_cat_id()
                game.last_list_forProfile = self.current_group
                self.change_screen('profile screen')
            else:
                self.menu_button_pressed(event)

        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if self.search_bar.is_focused:
                return
            if event.key == pygame.K_LEFT:
                self.change_screen('patrol screen')

    def screen_switches(self):
        # Determine the starting list of cats.
        if game.last_list_forProfile:
            if game.last_list_forProfile == 'sc':
                self.get_sc_cats()
            elif game.last_list_forProfile == 'df':
                self.get_df_cats()
            elif game.last_list_forProfile == 'ur':
                self.get_ur_cats()
            elif game.last_list_forProfile == 'cotc':
                self.get_cotc_cats()
            else:
                self.get_your_clan_cats()
        else:
            self.get_your_clan_cats()

        self.set_disabled_menu_buttons(["catlist_screen"])

        self.show_menu_buttons()

        y_pos = 268  # controls y_pos of cat list bar

        # favorite cat view
        self.filter_fav = UIImageButton(scale(pygame.Rect((209, y_pos), (76, 68))), "",
                                        object_id="#fav_cat",
                                        manager=MANAGER,
                                        tool_tip_text='hide favourite cat indicators')

        self.filter_not_fav = UIImageButton(scale(pygame.Rect((209, y_pos), (76, 68))), "",
                                            object_id="#not_fav_cat", manager=MANAGER,
                                            tool_tip_text='show favourite cat indicators')

        if game.clan.clan_settings["show fav"]:
            self.filter_not_fav.hide()
        else:
            self.filter_fav.hide()

        # search bar
        self.search_bar_image = pygame_gui.elements.UIImage(scale(pygame.Rect((279, y_pos), (236, 68))),
                                                            pygame.image.load(
                                                                "resources/images/search_bar.png").convert_alpha(),
                                                            manager=MANAGER)

        self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((299, 277), (230, 55))),
                                                              object_id="#search_entry_box",
                                                              initial_text="name search",
                                                              manager=MANAGER)

        # buttons for choosing which group you are currently viewing
        self.show_dead_button = UIImageButton(scale(pygame.Rect((512, y_pos), (210, 68))), "",
                                              object_id="#show_dead_button", manager=MANAGER,
                                              tool_tip_text='view cats in the afterlife',
                                              starting_height=2)
        self.show_living_button = UIImageButton(scale(pygame.Rect((512, y_pos), (210, 68))), "",
                                                object_id="#show_living_button", manager=MANAGER,
                                                tool_tip_text='view cats currently alive')
        if self.death_status == 'dead':
            self.show_dead_button.hide()
        else:
            self.show_living_button.hide()
            if game.sort_type == 'death':
                game.sort_type = 'rank'

        x_pos = 717
        self.choose_group_button = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (380, 68))), "",
                                                 object_id="#choose_group_button",
                                                 manager=MANAGER,
                                                 )
        y_pos += 64
        self.your_clan_button = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (380, 68))), "",
                                              object_id="#view_your_clan_button",
                                              starting_height=2,
                                              manager=MANAGER
                                              )
        self.your_clan_button.hide()
        self.sc_button = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (380, 68))), "",
                                       object_id="#view_starclan_button",
                                       starting_height=2,
                                       manager=MANAGER
                                       )
        self.sc_button.hide()
        y_pos += 64
        self.cotc_button = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (380, 68))), "",
                                         object_id="#view_cotc_button",
                                         starting_height=2,
                                         manager=MANAGER
                                         )
        self.cotc_button.hide()
        self.ur_button = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (380, 68))), "",
                                       object_id="#view_unknown_residence_button",
                                       starting_height=2,
                                       manager=MANAGER
                                       )
        self.ur_button.hide()
        y_pos += 64
        self.df_button = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (380, 68))), "",
                                       object_id="#view_dark_forest_button",
                                       starting_height=2,
                                       manager=MANAGER
                                       )
        self.df_button.hide()

        # next/prev page
        self.next_page_button = UIImageButton(scale(pygame.Rect((912, 1190), (68, 68))), "",
                                              object_id="#arrow_right_button"
                                              , manager=MANAGER)
        self.previous_page_button = UIImageButton(scale(pygame.Rect((620, 1190), (68, 68))), "",
                                                  object_id="#arrow_left_button", manager=MANAGER)

        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((680, 1190), (220, 60))),
                                                         object_id=get_text_box_theme("#text_box_30_horizcenter")
                                                         , manager=MANAGER)  # Text will be filled in later

        x_pos = 1093
        y_pos = 267

        # filter buttons ... there's a lot of them
        self.filter_by_rank = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (296, 68))),
            "",
            object_id="#filter_by_rank_button", manager=MANAGER
        )
        self.filter_by_exp = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (296, 68))),
            "",
            object_id="#filter_by_exp_button", manager=MANAGER
        )
        self.filter_by_ID = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (296, 68))),
            "",
            object_id="#filter_by_ID_button", manager=MANAGER
        )
        self.filter_by_death = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (296, 68))),
            "",
            object_id="#filter_by_death_button", manager=MANAGER
        )
        self.filter_by_age = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (296, 68))),
            "",
            object_id="#filter_by_age_button", manager=MANAGER
        )
        self.filter_by_age_reverse = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (296, 68))),
            "",
            object_id="#filter_by_age_reverse_button", manager=MANAGER
        )
        y_pos += 64

        x_pos = 1274

        self.filter_rank = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (114, 68))),
            "",
            object_id="#filter_rank_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_rank.hide()
        y_pos += 64
        self.filter_age = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos + 1), (114, 68))),
            "",
            object_id="#filter_age_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_age.hide()
        y_pos += 64
        self.filter_age_reverse = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos + 1), (114, 68))),
            "",
            object_id="#filter_age_reverse_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_age.hide()
        y_pos += 64
        self.filter_id = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (114, 68))),
            "",
            object_id="#filter_ID_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_id.hide()
        y_pos += 62
        self.filter_exp = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (114, 68))),
            "",
            object_id="#filter_exp_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_exp.hide()
        y_pos += 60
        self.filter_death = UIImageButton(
            scale(pygame.Rect((x_pos, y_pos), (114, 68))),
            "",
            object_id="#filter_death_button",
            starting_height=2, manager=MANAGER
        )
        self.filter_death.hide()
        self.filter_options_visible = True
        self.group_options_visible = False

        self.update_filter_buttons()

        self.update_search_cats("")  # This will list all the cats, and create the button objects.

    def update_bg(self):
        if self.current_group == 'sc':
            screen.blit(self.sc_bg, (0, 0))
        elif self.current_group == 'df':
            screen.blit(self.df_Bg, (0, 0))
        elif self.current_group == 'ur':
            screen.blit(self.ur_bg, (0, 0))

    def update_filter_buttons(self):
        # hide them all now
        self.filter_by_rank.hide()
        self.filter_by_ID.hide()
        self.filter_by_age.hide()
        self.filter_by_age_reverse.hide()
        self.filter_by_death.hide()
        self.filter_by_exp.hide()

        # find which one should be shown
        if game.sort_type == 'rank':
            self.filter_by_rank.show()
        elif game.sort_type == 'id':
            self.filter_by_ID.show()
        elif game.sort_type == 'age':
            self.filter_by_age.show()
        elif game.sort_type == 'reverse_age':
            self.filter_by_age_reverse.show()
        elif game.sort_type == 'exp':
            self.filter_by_exp.show()
        elif game.sort_type == 'death':
            self.filter_by_death.show()

        if self.filter_options_visible:  # closing filter dropdown
            self.filter_options_visible = False
            self.filter_id.hide()
            self.filter_age.hide()
            self.filter_age_reverse.hide()
            self.filter_rank.hide()
            self.filter_exp.hide()
            self.filter_death.hide()

        else:  # opening filter dropdown
            self.filter_options_visible = True
            self.filter_rank.show()
            self.filter_id.show()
            self.filter_age.show()
            self.filter_age_reverse.show()
            self.filter_exp.show()
            if self.death_status == "dead":
                self.filter_death.show()

    def update_view_buttons(self):
        if self.group_options_visible:
            self.group_options_visible = False
            self.your_clan_button.hide()
            self.cotc_button.hide()
            self.sc_button.hide()
            self.df_button.hide()
            self.ur_button.hide()
        else:
            self.group_options_visible = True
            if self.death_status == 'living':
                self.your_clan_button.show()
                self.cotc_button.show()
            else:
                self.sc_button.show()
                self.df_button.show()
                self.ur_button.show()

    def exit_screen(self):
        self.hide_menu_buttons()
        self.choose_group_button.kill()
        self.your_clan_button.kill()
        self.cotc_button.kill()
        self.sc_button.kill()
        self.df_button.kill()
        self.ur_button.kill()
        self.show_dead_button.kill()
        self.show_living_button.kill()
        self.next_page_button.kill()
        self.previous_page_button.kill()
        self.page_number.kill()
        self.search_bar.kill()
        self.search_bar_image.kill()
        self.filter_by_age.kill()
        self.filter_by_age_reverse.kill()
        self.filter_by_exp.kill()
        self.filter_by_death.kill()
        self.filter_by_ID.kill()
        self.filter_by_rank.kill()
        self.filter_rank.kill()
        self.filter_age.kill()
        self.filter_age_reverse.kill()
        self.filter_id.kill()
        self.filter_exp.kill()
        self.filter_death.kill()
        self.filter_fav.kill()
        self.filter_not_fav.kill()

        # Remove currently displayed cats and cat names.
        for cat in self.display_cats:
            cat.kill()
        self.display_cats = []

        for name in self.cat_names:
            name.kill()
        self.cat_names = []

    def get_your_clan_cats(self):
        self.current_group = 'clan'
        self.death_status = 'living'
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and not the_cat.outside:
                self.full_cat_list.append(the_cat)

    def get_cotc_cats(self):
        self.current_group = 'cotc'
        self.death_status = 'living'
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and the_cat.outside:
                self.full_cat_list.append(the_cat)

    def get_sc_cats(self):
        self.current_group = 'sc'
        self.death_status = 'dead'
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.outside and not the_cat.df and \
                    not the_cat.faded:
                self.full_cat_list.append(the_cat)

    def get_df_cats(self):
        self.current_group = 'df'
        self.death_status = 'dead'
        self.full_cat_list = []

        for the_cat in Cat.all_cats_list:
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and the_cat.df and \
                    not the_cat.faded:
                self.full_cat_list.append(the_cat)

    def get_ur_cats(self):
        self.current_group = 'ur'
        self.death_status = 'dead'
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if the_cat.ID in game.clan.unknown_cats and not the_cat.faded:
                self.full_cat_list.append(the_cat)

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        Cat.sort_cats(self.full_cat_list)

        # adding in the guide if necessary, this ensures the guide isn't affected by sorting as we always want them to
        # be the first cat on the list
        if (self.current_group == 'df' and game.clan.instructor.df) or (self.current_group == 'sc' and not game.clan.instructor.df):
            if game.clan.instructor in self.full_cat_list:
                self.full_cat_list.remove(game.clan.instructor)
            self.full_cat_list.insert(0, game.clan.instructor)


        search_text = search_text.strip()
        if search_text not in ['', 'name search']:
            for cat in self.full_cat_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.full_cat_list.copy()

        self.all_pages = int(ceil(len(self.current_listed_cats) /
                                  20.0)) if len(self.current_listed_cats) > 20 else 1

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_page()

    def update_page(self):
        """Run this function when page changes."""

        # update title
        if self.current_group == 'clan':
            self.update_heading_text(f'{game.clan.name}Clan')
        elif self.current_group == 'cotc':
            self.update_heading_text(f'Cats Outside the Clan')
        elif self.current_group == 'sc':
            self.update_heading_text(f'StarClan')
        elif self.current_group == 'ur':
            self.update_heading_text(f'Unknown Residence')
        elif self.current_group == 'df':
            self.update_heading_text(f'Dark Forest')

        # clamp current page to a valid page number
        self.list_page = max(1, min(self.list_page, self.all_pages))

        # Handle which next buttons are clickable.
        if self.all_pages <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.list_page >= self.all_pages:
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.list_page == 1 and self.all_pages > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()

        self.page_number.set_text(str(self.list_page) + "/" + str(self.all_pages))

        # Remove the images for currently listed cats
        for cat in self.display_cats:
            cat.kill()
        self.display_cats = []

        for name in self.cat_names:
            name.kill()
        self.cat_names = []

        # Generate object for the current cats

        if self.death_status == 'living':
            text_theme = get_text_box_theme("#text_box_30_horizcenter")
        else:
            text_theme = "#text_box_30_horizcenter_light"

        pos_x = 0
        pos_y = 10
        if self.current_listed_cats:
            for cat in self.chunks(self.current_listed_cats, 20)[self.list_page - 1]:

                # update_sprite(cat)
                if game.clan.clan_settings["show fav"] and cat.favourite:

                    _temp = pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png").convert_alpha(),
                        (100, 100))

                    if game.settings["dark mode"]:
                        _temp.set_alpha(150)

                    self.display_cats.append(
                        pygame_gui.elements.UIImage(
                            scale(pygame.Rect((270 + pos_x, 360 + pos_y), (100, 100))),
                            _temp))
                    self.display_cats[-1].disable()

                self.display_cats.append(
                    UISpriteButton(scale(pygame.Rect
                                         ((270 + pos_x, 360 + pos_y), (100, 100))),
                                   cat.sprite,
                                   cat.ID,
                                   starting_height=0, manager=MANAGER))

                name = str(cat.name)
                short_name = shorten_text_to_fit(name, 220, 30)

                self.cat_names.append(
                    pygame_gui.elements.ui_label.UILabel(scale(pygame.Rect((170 + pos_x, 460 + pos_y), (300, 60))),
                                                         short_name,
                                                         object_id=text_theme,
                                                         manager=MANAGER))
                pos_x += 240
                if pos_x >= 1200:
                    pos_x = 0
                    pos_y += 200

    def on_use(self):
        # Only update the positions if the search text changes
        if self.search_bar.is_focused and self.search_bar.get_text() == "name search":
            self.search_bar.set_text("")
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()

        self.update_bg()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
