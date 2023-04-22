import pygame.transform
import pygame_gui.elements
from random import choice

from .base_screens import Screens, cat_profiles

from scripts.utility import get_personality_compatibility, get_text_box_theme, scale
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.image_button import UIImageButton, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER
from scripts.game_structure.windows import RelationshipLog


class ChooseMentorScreen(Screens):
    selected_mentor = None
    current_page = 1
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))
    apprentice_details = {}
    selected_details = {}
    cat_list_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.list_page = None
        self.next_cat = None
        self.previous_cat = None
        self.next_page_button = None
        self.previous_page_button = None
        self.current_mentor_warning = None
        self.confirm_mentor = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.mentor_icon = None
        self.app_frame = None
        self.mentor_frame = None
        self.current_mentor_text = None
        self.info = None
        self.heading = None
        self.mentor = None
        self.the_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.cat_list_buttons.values():
                self.selected_mentor = event.ui_element.return_cat_object()
                self.update_selected_cat()
                self.update_buttons()
            elif event.ui_element == self.confirm_mentor:
                self.change_mentor(self.selected_mentor)
                self.update_buttons()
                self.update_selected_cat()
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')
            elif event.ui_element == self.next_cat_button:
                if Cat.fetch_cat(self.next_cat) is not None:
                    game.switches['cat'] = self.next_cat
                    self.update_apprentice()
                    self.update_selected_cat()
                    self.update_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if Cat.fetch_cat(self.previous_cat) is not None:
                    game.switches['cat'] = self.previous_cat
                    self.update_apprentice()
                    self.update_selected_cat()
                    self.update_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()

    def screen_switches(self):
        self.the_cat = Cat.all_cats[game.switches['cat']]
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)

        self.heading = pygame_gui.elements.UITextBox("Choose a new mentor for " + str(self.the_cat.name),
                                                     scale(pygame.Rect((300, 50), (1000, 80))),
                                                     object_id=get_text_box_theme("#text_box_34_horizcenter"),
                                                     manager=MANAGER)
        self.info = pygame_gui.elements.UITextBox("If an apprentice is 6 moons old and their mentor is changed, they "
                                                  "will not be listed as a former apprentice on their old mentor's "
                                                  "profile. An apprentice's mentor can have an influence on their "
                                                  "trait and skill later in life.\nChoose your mentors wisely",
                                                  scale(pygame.Rect((360, 120), (880, 200))),
                                                  object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                                                  manager=MANAGER)
        if self.mentor is not None:
            self.current_mentor_text = pygame_gui.elements.UITextBox(f"{self.the_cat.name}'s current mentor is "
                                                                     f"{self.mentor.name}",
                                                                     scale(pygame.Rect((460, 260), (680, 60))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizcenter")
                                                                     , manager=MANAGER)
        else:
            self.current_mentor_text = pygame_gui.elements.UITextBox(f"{self.the_cat.name} does not have a mentor",
                                                                     scale(pygame.Rect((460, 260), (680, 60))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizcenter")
                                                                     , manager=MANAGER)

        # Layout Images:
        self.mentor_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((80, 226), (562, 394))),
                                                        pygame.transform.scale(
                                                            image_cache.load_image(
                                                                "resources/images/choosing_cat1_frame_ment.png").convert_alpha(),
                                                            (562, 394)), manager=MANAGER)
        self.app_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((960, 226), (562, 394))),
                                                     pygame.transform.scale(
                                                         image_cache.load_image(
                                                             "resources/images/choosing_cat2_frame_ment.png").convert_alpha(),
                                                         (562, 394)), manager=MANAGER)

        self.mentor_icon = pygame_gui.elements.UIImage(scale(pygame.Rect((630, 320), (343, 228))),
                                                       pygame.transform.scale(
                                                           image_cache.load_image(
                                                               "resources/images/mentor.png").convert_alpha(),
                                                           (343, 228)), manager=MANAGER)

        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "",
                                             object_id="#next_cat_button")
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        self.confirm_mentor = UIImageButton(scale(pygame.Rect((652, 620), (296, 60))), "",
                                            object_id="#confirm_mentor_button")
        if self.mentor is not None:
            self.current_mentor_warning = pygame_gui.elements.UITextBox(
                "Current mentor selected",
                scale(pygame.Rect((600, 670), (400, 60))),
                object_id=get_text_box_theme("#text_box_22_horizcenter_red"),
                manager=MANAGER)
        else:
            self.current_mentor_warning = pygame_gui.elements.UITextBox("<font color=#FF0000>No mentor selected</font>"
                                                                        , scale(pygame.Rect((600, 680), (400, 60))),
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_22_horizcenter"),
                                                                        manager=MANAGER)
        self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1160), (68, 68))), "",
                                                  object_id="#relation_list_previous", manager=MANAGER)
        self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1160), (68, 68))), "",
                                              object_id="#relation_list_next", manager=MANAGER)

        self.update_apprentice()  # Draws the current apprentice
        self.update_selected_cat()  # Updates the image and details of selected cat
        self.update_cat_list()
        self.update_buttons()

    def exit_screen(self):
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}

        self.heading.kill()
        del self.heading
        self.info.kill()
        del self.info
        self.current_mentor_text.kill()
        del self.current_mentor_text
        self.mentor_frame.kill()
        del self.mentor_frame
        self.mentor_icon.kill()
        del self.mentor_icon
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.confirm_mentor.kill()
        del self.confirm_mentor
        self.current_mentor_warning.kill()
        del self.current_mentor_warning
        self.previous_page_button.kill()
        del self.previous_page_button
        self.next_page_button.kill()
        del self.next_page_button
        self.app_frame.kill()
        del self.app_frame

    def update_apprentice(self):
        """ Updates the apprentice focused on. """
        for ele in self.apprentice_details:
            self.apprentice_details[ele].kill()
        self.apprentice_details = {}

        self.the_cat = Cat.all_cats[game.switches['cat']]
        self.current_page = 1
        self.selected_mentor = Cat.fetch_cat(self.the_cat.mentor)
        self.mentor = Cat.fetch_cat(self.the_cat.mentor)

        self.heading.set_text(f"Choose a new mentor for {self.the_cat.name}")
        if self.the_cat.mentor:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name}'s current mentor is {self.mentor.name}")
        else:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name} does not have a mentor")
        self.apprentice_details["apprentice_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1200, 300), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite,
                (300, 300)),
            manager=MANAGER)

        info = self.the_cat.age + "\n" + self.the_cat.status + "\n" + self.the_cat.genderalign + \
               "\n" + self.the_cat.trait + "\n" + self.the_cat.skill
        self.apprentice_details["apprentice_info"] = pygame_gui.elements.UITextBox(
            info,
            scale(pygame.Rect((980, 325), (210, 250))),
            object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
            manager=MANAGER)

        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.apprentice_details["apprentice_name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (220, 60))),
            name,
            object_id="#text_box_34_horizcenter", manager=MANAGER)

        self.find_next_previous_cats()  # Determine where the next and previous cat buttons lead

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def find_next_previous_cats(self):
        """Determines where the previous and next buttons lead"""
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        self.previous_cat = 0
        self.next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            self.previous_cat = game.clan.instructor.ID

        if is_instructor:
            self.next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                self.next_cat = 1

            if self.next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.status in \
                    ["apprentice", "medicine cat apprentice", "mediator apprentice"] \
                    and check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.status in \
                    ["apprentice", "medicine cat apprentice", "mediator apprentice"] \
                    and check_cat.df == self.the_cat.df:
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def change_mentor(self, new_mentor=None):
        old_mentor = Cat.fetch_cat(self.the_cat.mentor)
        if new_mentor and old_mentor is not None:
            old_mentor.apprentice.remove(self.the_cat.ID)
            if self.the_cat.moons > 6 and self.the_cat.ID not in old_mentor.former_apprentices:
                old_mentor.former_apprentices.append(self.the_cat.ID)

            self.the_cat.patrol_with_mentor = 0
            self.the_cat.mentor = new_mentor.ID
            new_mentor.apprentice.append(self.the_cat.ID)
            self.mentor = new_mentor

            # They are a current apprentice, not a former one now!
            if self.the_cat.ID in new_mentor.former_apprentices:
                new_mentor.former_apprentices.remove(self.the_cat.ID)

        elif new_mentor:
            self.the_cat.mentor = new_mentor.ID
            new_mentor.apprentice.append(self.the_cat.ID)
            self.mentor = new_mentor

            # They are a current apprentice, not a former one now!
            if self.the_cat.ID in new_mentor.former_apprentices:
                new_mentor.former_apprentices.remove(self.the_cat.ID)

        if self.mentor is not None:
            self.current_mentor_text.set_text(
                f"{self.the_cat.name}'s current mentor is {self.mentor.name}")
        else:
            self.current_mentor_text.set_text(f"{self.the_cat.name} does not have a mentor")

    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if self.selected_mentor:

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((100, 300), (300, 300))),
                pygame.transform.scale(
                    self.selected_mentor.sprite,
                    (300, 300)), manager=MANAGER)

            info = self.selected_mentor.age + "\n" + self.selected_mentor.status + "\n" + \
                   self.selected_mentor.genderalign + "\n" + self.selected_mentor.trait + "\n" + \
                   self.selected_mentor.skill
            if len(self.selected_mentor.former_apprentices) >= 1:
                info += f"\n{len(self.selected_mentor.former_apprentices)} former app(s)"
            if len(self.selected_mentor.apprentice) >= 1:
                info += f"\n{len(self.selected_mentor.apprentice)} current app(s)"
            self.selected_details["selected_info"] = pygame_gui.elements.UITextBox(info,
                                                                                   scale(pygame.Rect((420, 325),
                                                                                                     (210, 250))),
                                                                                   object_id="#text_box_22_horizcenter_vertcenter_spacing_95",
                                                                                   manager=MANAGER)

            name = str(self.selected_mentor.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((130, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter", manager=MANAGER)

    def update_cat_list(self):
        """Updates the cat sprite buttons. """
        valid_mentors = self.chunks(self.get_valid_mentors(), 30)

        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.current_page > len(valid_mentors):
            self.list_page = len(valid_mentors)

        # Handle which next buttons are clickable.
        if len(valid_mentors) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(valid_mentors):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(valid_mentors) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()
        display_cats = []
        if valid_mentors:
            display_cats = valid_mentors[self.current_page - 1]

        # Kill all the currently displayed cats.
        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        pos_x = 0
        pos_y = 40
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                cat.sprite, cat_object=cat, manager=MANAGER)
            pos_x += 120
            if pos_x >= 1100:
                pos_x = 0
                pos_y += 120
            i += 1

    def update_buttons(self):
        """Updates the status of buttons. """
        # Disable to enable the choose mentor button
        if not self.selected_mentor or self.selected_mentor.ID == self.the_cat.mentor:
            self.confirm_mentor.disable()
            self.current_mentor_warning.show()
        else:
            self.confirm_mentor.enable()
            self.current_mentor_warning.hide()

    def get_valid_mentors(self):
        valid_mentors = []

        if self.the_cat.status == "apprentice":
            for cat in Cat.all_cats_list:
                if not cat.dead and not cat.outside and cat.status in [
                    'warrior', 'deputy', 'leader'
                ]:
                    valid_mentors.append(cat)
        elif self.the_cat.status == "medicine cat apprentice":
            for cat in Cat.all_cats_list:
                if not cat.dead and not cat.outside and cat.status == 'medicine cat':
                    valid_mentors.append(cat)
        elif self.the_cat.status == 'mediator apprentice':
            for cat in Cat.all_cats_list:
                if not cat.dead and not cat.outside and cat.status == 'mediator':
                    valid_mentors.append(cat)

        return valid_mentors

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class FamilyTreeScreen(Screens):
    # Page numbers for siblings and offspring

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None
        self.grandkits_tab = None
        self.kits_mates_tab = None
        self.kits_tab = None
        self.mates_tab = None
        self.siblings_kits_tab = None
        self.siblings_mates_tab = None
        self.siblings_tab = None
        self.cousins_tab = None
        self.parents_siblings_tab = None
        self.parents_tab = None
        self.grandparents_tab = None
        self.next_group_page = None
        self.previous_group_page = None
        self.root_cat = None
        self.family_tree = None
        self.center_cat_frame = None
        self.root_cat_frame = None
        self.relation_backdrop = None
        self.grandkits_button = None
        self.kits_mates_button = None
        self.kits_button = None
        self.mates_button = None
        self.sibling_kits_button = None
        self.sibling_mates_button = None
        self.siblings_button = None
        self.cousins_button = None
        self.parents_siblings_button = None
        self.parents_button = None
        self.grandparents_button = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.the_cat = None

        self.grandparents = []
        self.parents = []
        self.parents_siblings = []
        self.cousins = []
        self.siblings = []
        self.siblings_mates = []
        self.siblings_kits = []
        self.mates = []
        self.kits = []
        self.kits_mates = []
        self.grandkits = []

        self.cat_elements = {}
        self.relation_elements = {}
        self.tabs = {}

        self.group_page_number = 1
        self.current_group = None
        self.current_group_name = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
                game.switches['root_cat'] = None
            elif event.ui_element == self.previous_cat_button:
                if Cat.fetch_cat(self.previous_cat) is not None:
                    game.switches['cat'] = self.previous_cat
                    game.switches['root_cat'] = Cat.all_cats[self.previous_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if Cat.fetch_cat(self.next_cat) is not None:
                    game.switches['cat'] = self.next_cat
                    game.switches['root_cat'] = Cat.all_cats[self.next_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.parents_button:
                self.current_group = self.parents
                self.current_group_name = "parents"
                self.handle_relation_groups()
            elif event.ui_element == self.siblings_button:
                self.current_group = self.siblings
                self.current_group_name = "siblings"
                self.handle_relation_groups()
            elif event.ui_element == self.sibling_mates_button:
                self.current_group = self.siblings_mates
                self.current_group_name = "siblings_mates"
                self.handle_relation_groups()
            elif event.ui_element == self.sibling_kits_button:
                self.current_group = self.siblings_kits
                self.current_group_name = "siblings_kits"
                self.handle_relation_groups()
            elif event.ui_element == self.parents_siblings_button:
                self.current_group = self.parents_siblings
                self.current_group_name = "parents_siblings"
                self.handle_relation_groups()
            elif event.ui_element == self.cousins_button:
                self.current_group = self.cousins
                self.current_group_name = "cousins"
                self.handle_relation_groups()
            elif event.ui_element == self.grandparents_button:
                self.current_group = self.grandparents
                self.current_group_name = "grandparents"
                self.handle_relation_groups()
            elif event.ui_element == self.mates_button:
                self.current_group = self.mates
                self.current_group_name = "mates"
                self.handle_relation_groups()
            elif event.ui_element == self.kits_button:
                self.current_group = self.kits
                self.current_group_name = "kits"
                self.handle_relation_groups()
            elif event.ui_element == self.kits_mates_button:
                self.current_group = self.kits_mates
                self.current_group_name = "kits_mates"
                self.handle_relation_groups()
            elif event.ui_element == self.grandkits_button:
                self.current_group = self.grandkits
                self.current_group_name = "grandkits"
                self.handle_relation_groups()
            elif event.ui_element == self.previous_group_page:
                self.group_page_number -= 1
                self.handle_relation_groups()
            elif event.ui_element == self.next_group_page:
                self.group_page_number += 1
                self.handle_relation_groups()
            elif event.ui_element == self.cat_elements["center_cat_image"]:
                self.change_screen('profile screen')
                game.switches['root_cat'] = None
            elif event.ui_element in self.relation_elements.values() or self.cat_elements.values():
                try:
                    id = event.ui_element.return_cat_id()
                    if Cat.fetch_cat(id).faded:
                        return
                    game.switches['cat'] = id
                except AttributeError:
                    return
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.change_screen('profile screen')
                    game.switches['root_cat'] = None
                else:
                    self.exit_screen()
                    self.screen_switches()

    def screen_switches(self):
        """Set up things that are always on the page"""

        self.current_group = None
        self.current_group_name = None
        # prev/next and back buttons
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button", manager=MANAGER)
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "",
                                             object_id="#next_cat_button", manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)

        # our container for the family tree, this will center itself based on visible relation group buttons
        # it starts with just the center cat frame inside it, since that will always be visible
        self.family_tree = pygame_gui.core.UIContainer(
            scale(pygame.Rect((720, 450), (160, 180))),
            MANAGER)

        # now grab the other necessary UI elements
        self.previous_group_page = UIImageButton(scale(pygame.Rect((941, 1281), (68, 68))),
                                                 "",
                                                 object_id="#arrow_left_button",
                                                 manager=MANAGER)
        self.previous_group_page.disable()
        self.next_group_page = UIImageButton(scale(pygame.Rect((1082, 1281), (68, 68))),
                                             "",
                                             object_id="#arrow_right_button",
                                             manager=MANAGER)
        self.next_group_page.disable()
        self.relation_backdrop = pygame_gui.elements.UIImage(scale(pygame.Rect((628, 950), (841, 342))),
                                                             pygame.transform.scale(
                                                                 image_cache.load_image(
                                                                     "resources/images/familytree_relationbackdrop.png").convert_alpha(),
                                                                 (841, 342)), manager=MANAGER)
        self.relation_backdrop.disable()

        if not game.switches['root_cat']:
            game.switches['root_cat'] = Cat.all_cats[game.switches['cat']]
        self.root_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((129, 950), (452, 340))),
                                                          pygame.transform.scale(
                                                              image_cache.load_image(
                                                                  "resources/images/familytree_bigcatbox.png").convert_alpha(),
                                                              (452, 340)), manager=MANAGER)
        self.cat_elements["root_cat_image"] = UISpriteButton(scale(pygame.Rect((462, 1151), (100, 100))),
                                                             game.switches['root_cat'].sprite,
                                                             cat_id=game.switches['root_cat'].ID,
                                                             manager=MANAGER,
                                                             tool_tip_text=f'Started viewing tree at {game.switches["root_cat"].name}')

        self.root_cat_frame.disable()

        self.center_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (160, 180))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/familytree_smallcatbox.png").convert_alpha(),
                                                                (160, 180)),
                                                            manager=MANAGER,
                                                            container=self.family_tree)
        self.center_cat_frame.disable()
        self.group_page_number = 1
        # self.family_setup()
        self.create_family_tree()
        self.get_previous_next_cat()

    def create_family_tree(self):
        """
        this function handles creating the family tree, both collecting the relation groups and displaying the buttons
        """
        # everything in here is held together by duct tape and hope, TAKE CARE WHEN EDITING

        # the cat whose family tree is being viewed
        self.the_cat = Cat.all_cats[game.switches['cat']]

        self.cat_elements["screen_title"] = pygame_gui.elements.UITextBox(f"{self.the_cat.name}'s Family Tree",
                                                                          scale(
                                                                              pygame.Rect((300, 50),
                                                                                          (1000, 100))),
                                                                          object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                                          manager=MANAGER, )

        # will need these later to adjust positioning
        # as the various groups are collected, the x_pos and y_pos are adjusted to account for the new buttons,
        # these affect the positioning of all the buttons
        x_pos = 0
        y_pos = 0

        # as the various groups are collected, the x_dim and y_dim are adjusted to account for the new button,
        # these affect the size and positioning of the UIContainer holding the family tree
        x_dim = 160
        y_dim = 180

        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()

        self.parents = self.the_cat.inheritance.get_parents()
        self.mates = self.the_cat.inheritance.get_mates()
        self.kits = self.the_cat.inheritance.get_kits()
        self.kits_mates = self.the_cat.inheritance.get_kits_mates()
        self.siblings = self.the_cat.inheritance.get_siblings()
        self.siblings_mates = self.the_cat.inheritance.get_siblings_mates()
        self.siblings_kits = self.the_cat.inheritance.get_siblings_kits()
        self.parents_siblings = self.the_cat.inheritance.get_parents_siblings()
        self.cousins = self.the_cat.inheritance.get_cousins()
        self.grandparents = self.the_cat.inheritance.get_grand_parents()
        self.grandkits = self.the_cat.inheritance.get_grand_kits()

        # collect grandparents
        if self.parents:
            y_dim += 196
            y_pos += 196
            if self.grandparents:
                y_dim += 160
                y_pos += 160

            x_dim += 309
            if self.siblings_mates:
                x_dim += 417
            if self.siblings_kits:
                y_dim += 80
                if not self.siblings_mates:
                    x_dim += 417

        # collect cousins
        if self.parents_siblings:
            if not self.siblings_mates and not self.siblings_kits:
                x_dim += 433
        
        # collect mates
        if self.mates or self.kits:
            x_pos += 276
            x_dim += 280
        # collect kits
        if self.kits:
            if not self.siblings_kits:
                y_dim += 80
            if self.kits_mates:
                x_pos += 202
                x_dim += 202
            if self.grandkits:
                y_dim += 140
                if not self.kits_mates:
                    x_pos += 202
                    x_dim += 202

        self.family_tree.kill()
        self.family_tree = pygame_gui.core.UIContainer(
            scale(pygame.Rect((800 - x_dim / 2, 550 - y_dim / 2), (x_dim, y_dim))),
            MANAGER)

        # creating the center frame, cat, and name
        self.cat_elements["the_cat_image"] = UISpriteButton(scale(pygame.Rect((150, 969), (300, 300))),
                                                            self.the_cat.sprite,
                                                            cat_id=self.the_cat.ID,
                                                            manager=MANAGER)
        name = str(self.the_cat.name)
        if len(name) >= 13:
            short_name = name[0:10]
            name = short_name + '...'
        self.cat_elements["viewing_cat_text"] = pygame_gui.elements.UITextBox(f"Viewing {name}'s Lineage",
                                                                              scale(
                                                                                  pygame.Rect((150, 1282), (300, 150))),
                                                                              object_id=get_text_box_theme(
                                                                                  "#text_box_22_horizcenter_spacing_95"),
                                                                              manager=MANAGER, )
        self.center_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((x_pos, y_pos), (160, 180))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/familytree_smallcatbox.png").convert_alpha(),
                                                                (160, 180)),
                                                            manager=MANAGER,
                                                            container=self.family_tree)
        self.center_cat_frame.disable()
        self.cat_elements['center_cat_image'] = UISpriteButton(scale(pygame.Rect((x_pos + 30, y_pos + 20), (100, 100))),
                                                               self.the_cat.sprite,
                                                               cat_id=self.the_cat.ID,
                                                               manager=MANAGER,
                                                               container=self.family_tree)
        name = str(self.the_cat.name)
        if len(name) >= 9:
            short_name = name[0:7]
            name = short_name + '...'
        self.cat_elements["center_cat_name"] = pygame_gui.elements.UITextBox(name,
                                                                             scale(
                                                                                 pygame.Rect((10 + x_pos, 118 + y_pos),
                                                                                             (145, 100))),
                                                                             object_id=get_text_box_theme(
                                                                                 "#text_box_22_horizcenter"),
                                                                             manager=MANAGER,
                                                                             container=self.family_tree)

        if self.parents:
            self.siblings_button = UIImageButton(scale(pygame.Rect((152 + x_pos, 65 + y_pos), (316, 60))),
                                                 "",
                                                 object_id="#siblings_button",
                                                 manager=MANAGER,
                                                 container=self.family_tree)
            if self.siblings:
                if self.siblings_mates or self.siblings_kits:
                    self.sibling_mates_button = UIImageButton(scale(pygame.Rect((464 + x_pos, 65 + y_pos), (418, 60))),
                                                              "",
                                                              object_id="#siblingmates_button",
                                                              manager=MANAGER,
                                                              container=self.family_tree)
                if self.siblings_kits:
                    self.sibling_kits_button = UIImageButton(scale(pygame.Rect((406 + x_pos, 97 + y_pos), (252, 164))),
                                                             "",
                                                             object_id="#siblingkits_button",
                                                             manager=MANAGER,
                                                             container=self.family_tree)
            self.parents_button = UIImageButton(scale(pygame.Rect((136 + x_pos, -196 + y_pos), (176, 288))),
                                                "",
                                                object_id="#parents_button",
                                                manager=MANAGER,
                                                container=self.family_tree)
            self.family_tree.add_element(self.parents_button)
            if self.parents_siblings:
                self.parents_siblings_button = UIImageButton(scale(pygame.Rect((308 + x_pos, -196 + y_pos), (436, 60))),
                                                             "",
                                                             object_id="#parentsiblings_button",
                                                             manager=MANAGER,
                                                             container=self.family_tree)
                if self.cousins:
                    self.cousins_button = UIImageButton(scale(pygame.Rect((504 + x_pos, -139 + y_pos), (170, 164))),
                                                        "",
                                                        object_id="#cousins_button",
                                                        manager=MANAGER,
                                                        container=self.family_tree)
            if self.grandparents:
                self.grandparents_button = UIImageButton(scale(pygame.Rect((94 + x_pos, -355 + y_pos), (260, 164))),
                                                         "",
                                                         object_id="#grandparents_button",
                                                         manager=MANAGER,
                                                         container=self.family_tree)

        if self.mates or self.kits:
            self.mates_button = UIImageButton(scale(pygame.Rect((-276 + x_pos, 65 + y_pos), (288, 60))),
                                              "",
                                              object_id="#mates_button",
                                              manager=MANAGER,
                                              container=self.family_tree)
        if self.kits:
            self.kits_button = UIImageButton(scale(pygame.Rect((-118 + x_pos, 97 + y_pos), (116, 164))),
                                             "",
                                             object_id="#kits_button",
                                             manager=MANAGER,
                                             container=self.family_tree)
            if self.kits_mates or self.grandkits:
                self.kits_mates_button = UIImageButton(scale(pygame.Rect((-477 + x_pos, 198 + y_pos), (364, 60))),
                                                       "",
                                                       object_id="#kitsmates_button",
                                                       manager=MANAGER,
                                                       container=self.family_tree)
            if self.grandkits:
                self.grandkits_button = UIImageButton(scale(pygame.Rect((-282 + x_pos, 233 + y_pos), (202, 164))),
                                                      "",
                                                      object_id="#grandkits_button",
                                                      manager=MANAGER,
                                                      container=self.family_tree)

    def handle_relation_groups(self):
        """Updates the given group"""
        for ele in self.relation_elements:
            self.relation_elements[ele].kill()
        self.relation_elements = {}

        self.update_tab()
        if not self.current_group:
            self.relation_elements["no_cats_notice"] = pygame_gui.elements.UITextBox("None",
                                                                                     scale(
                                                                                         pygame.Rect(
                                                                                             (550, 1080),
                                                                                             (900, 60))),
                                                                                     object_id=get_text_box_theme(
                                                                                         "#text_box_30_horizcenter"),
                                                                                     manager=MANAGER)
        _current_group = self.chunks(self.current_group, 24)

        if self.group_page_number > len(_current_group):
            self.group_page_number = max(len(_current_group), 1)

        if _current_group:
            display_cats = _current_group[self.group_page_number - 1]
        else:
            display_cats = []

        pos_x = 0
        pos_y = 0
        i = 0
        for kitty in display_cats:
            _kitty = Cat.fetch_cat(kitty)
            info_text = f"{str(_kitty.name)}"
            additional_info = self.the_cat.inheritance.get_cat_info(kitty)
            if len(additional_info["type"]) > 0: # types is always real
                rel_types = [str(rel_type.value) for rel_type in additional_info["type"]]
                rel_types = set(rel_types) # remove duplicates
                if "" in rel_types: 
                    rel_types.remove("")       # removes empty
                if len(rel_types) > 0:
                    info_text += "\n"
                    info_text += ', '.join(rel_types)
                if len(additional_info["additional"]) > 0:
                    add_info = set(additional_info["additional"]) # remove duplicates
                    info_text += "\n"
                    info_text += ', '.join(add_info)

            self.relation_elements["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((649 + pos_x, 970 + pos_y), (100, 100))),
                _kitty.sprite,
                cat_id=_kitty.ID,
                manager=MANAGER,
                tool_tip_text=info_text
            )

            pos_x += 100
            if pos_x > 700:
                pos_y += 100
                pos_x = 0
            i += 1

        # Enable and disable page buttons.
        if len(_current_group) <= 1:
            self.previous_group_page.disable()
            self.next_group_page.disable()
        elif self.group_page_number >= len(_current_group):
            self.previous_group_page.enable()
            self.next_group_page.disable()
        elif self.group_page_number == 1 and len(self.current_group) > 1:
            self.previous_group_page.disable()
            self.next_group_page.enable()
        else:
            self.previous_group_page.enable()
            self.next_group_page.enable()

    def update_tab(self):
        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        if self.current_group_name == "grandparents":
            self.tabs['grandparents_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1164, 890), (256, 60))),
                                                                        pygame.transform.scale(
                                                                            image_cache.load_image(
                                                                                "resources/images/grandparents_tab.png").convert_alpha(),
                                                                            (256, 60)),
                                                                        manager=MANAGER)
        elif self.current_group_name == "parents":
            self.tabs['parents_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1246, 890), (174, 60))),
                                                                   pygame.transform.scale(
                                                                       image_cache.load_image(
                                                                           "resources/images/parents_tab.png").convert_alpha(),
                                                                       (174, 60)),
                                                                   manager=MANAGER)
        elif self.current_group_name == "parents_siblings":
            self.tabs['parents_siblings_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1123, 890), (296, 60))),
                                                                            pygame.transform.scale(
                                                                                image_cache.load_image(
                                                                                    "resources/images/parentsibling_tab.png").convert_alpha(),
                                                                                (296, 60)),
                                                                            manager=MANAGER)
        elif self.current_group_name == "cousins":
            self.tabs['cousins_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1254, 890), (166, 60))),
                                                                   pygame.transform.scale(
                                                                       image_cache.load_image(
                                                                           "resources/images/cousins_tab.png").convert_alpha(),
                                                                       (166, 60)),
                                                                   manager=MANAGER)
        elif self.current_group_name == "siblings":
            self.tabs['siblings_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1256, 890), (164, 60))),
                                                                    pygame.transform.scale(
                                                                        image_cache.load_image(
                                                                            "resources/images/siblings_tab.png").convert_alpha(),
                                                                        (164, 60)),
                                                                    manager=MANAGER)
        elif self.current_group_name == "siblings_mates":
            self.tabs['siblings_mates_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1146, 890), (274, 60))),
                                                                          pygame.transform.scale(
                                                                              image_cache.load_image(
                                                                                  "resources/images/siblingsmate_tab.png").convert_alpha(),
                                                                              (274, 60)),
                                                                          manager=MANAGER)
        elif self.current_group_name == "siblings_kits":
            self.tabs['siblings_kits_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1170, 890), (250, 60))),
                                                                         pygame.transform.scale(
                                                                             image_cache.load_image(
                                                                                 "resources/images/siblingkits_tab.png").convert_alpha(),
                                                                             (250, 60)),
                                                                         manager=MANAGER)
        elif self.current_group_name == "mates":
            self.tabs['mates_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1270, 890), (150, 60))),
                                                                 pygame.transform.scale(
                                                                     image_cache.load_image(
                                                                         "resources/images/mates_tab.png").convert_alpha(),
                                                                     (150, 60)),
                                                                 manager=MANAGER)
        elif self.current_group_name == "kits":
            self.tabs['kits_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1306, 890), (114, 60))),
                                                                pygame.transform.scale(
                                                                    image_cache.load_image(
                                                                        "resources/images/kits_tab.png").convert_alpha(),
                                                                    (114, 60)),
                                                                manager=MANAGER)
        elif self.current_group_name == "kits_mates":
            self.tabs['kits_mates_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1196, 890), (224, 60))),
                                                                      pygame.transform.scale(
                                                                          image_cache.load_image(
                                                                              "resources/images/kitsmate_tab.png").convert_alpha(),
                                                                          (224, 60)),
                                                                      manager=MANAGER)
        elif self.current_group_name == "grandkits":
            self.tabs['grandkits_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1220, 890), (200, 60))),
                                                                     pygame.transform.scale(
                                                                         image_cache.load_image(
                                                                             "resources/images/grandkits_tab.png").convert_alpha(),
                                                                         (200, 60)),
                                                                     manager=MANAGER)

    def get_previous_next_cat(self):
        """Determines where the previous and next buttons should lead, and enables/disables them"""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                        check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    previous_cat = check_cat.ID

                elif next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                        check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def exit_screen(self):
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}

        for ele in self.relation_elements:
            self.relation_elements[ele].kill()
        self.relation_elements = {}

        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        self.grandparents = []
        self.parents = []
        self.parents_siblings = []
        self.cousins = []
        self.siblings = []
        self.siblings_mates = []
        self.siblings_kits = []
        self.mates = []
        self.kits = []
        self.kits_mates = []
        self.grandkits = []
        self.current_group = None

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.family_tree.kill()
        del self.family_tree
        self.relation_backdrop.kill()
        del self.relation_backdrop
        self.root_cat_frame.kill()
        del self.root_cat_frame
        self.next_group_page.kill()
        del self.next_group_page
        self.previous_group_page.kill()
        del self.previous_group_page


class ChooseMateScreen(Screens):
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))
    current_cat_elements = {}
    mate_elements = {}
    mate = None
    current_page = 1
    selected_cat = None
    selected_mate_index = 0

    cat_list_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None
        self.list_page = None
        self.kittens = None
        self.the_cat = None
        self.kitten_message = None
        self.toggle_mate = None
        self.page_number = None
        self.next_page_button = None
        self.previous_page_button = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.mate_frame = None
        self.the_cat_frame = None
        self.info = None
        self.cycle_mate_left_button = None
        self.cycle_mate_right_button = None
        self.all_pages = []

    def handle_event(self, event):
        """ Handles events. """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # Cat buttons list
            if event.ui_element in self.cat_list_buttons.values():
                if len(self.the_cat.mate) < 1 or self.selected_mate_index == len(self.the_cat.mate):
                    self.selected_cat = event.ui_element.return_cat_object()
                    self.update_buttons()
                    self.update_choose_mate()
                else:
                    # if the cat already has a mate, then it lists offspring instead. Take to profile.
                    game.switches['cat'] = event.ui_element.return_cat_object().ID
                    self.update_buttons()
                    self.change_screen("profile screen")
            # return to profile screen
            elif event.ui_element == self.back_button:
                self.selected_mate_index = 0
                self.change_screen('profile screen')

            # Check if mate cycle buttons are clicked.
            if event.ui_element == self.cycle_mate_left_button:
                self.selected_mate_index -= 1
                if self.selected_mate_index < len(self.the_cat.mate):
                    self.selected_cat = self.the_cat.mate[self.selected_mate_index]
                    self.update_mate_screen()
                else:
                    self.selected_cat = None
                    self.update_choose_mate()
                self.update_current_cat_info()
                self.update_buttons()
            elif event.ui_element == self.cycle_mate_right_button:
                self.selected_mate_index += 1
                if self.selected_mate_index < len(self.the_cat.mate):
                    self.selected_cat = self.the_cat.mate[self.selected_mate_index]
                    self.update_mate_screen()
                else:
                    self.selected_cat = None
                    self.update_choose_mate()
                self.update_current_cat_info()
                self.update_buttons()

            elif event.ui_element == self.toggle_mate:
                if self.selected_cat and self.selected_cat.ID not in self.the_cat.mate:
                    self.the_cat.set_mate(self.selected_cat)
                    self.update_mate_screen()
                else:
                    self.the_cat.unset_mate(self.selected_cat, breakup=True)
                    self.update_choose_mate(breakup=True)
                    self.update_current_cat_info()
                self.update_cat_list()
            elif event.ui_element == self.previous_cat_button:
                if Cat.fetch_cat(self.previous_cat) is not None:
                    game.switches["cat"] = self.previous_cat
                    self.selected_mate_index = 0
                    self.update_current_cat_info()
                    self.update_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if Cat.fetch_cat(self.next_cat) is not None:
                    game.switches["cat"] = self.next_cat
                    self.selected_mate_index = 0
                    self.update_current_cat_info()
                    self.update_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()

    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        self.info = pygame_gui.elements.UITextBox(
            "If a cat has a mate, then they will be loyal and only have kittens with their mate"
            " (unless affairs are toggled on.) Potential mates are listed below! The lines "
            "connecting the two cats may give a hint on their compatibility with one another "
            "and any existing romantic feelings will be shown with a small heart.",
            scale(pygame.Rect((360, 120), (880, 200))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95")
        )

        self.the_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((80, 226), (532, 394))),
                                                         pygame.transform.scale(
                                                             image_cache.load_image(
                                                                 "resources/images/choosing_cat1_frame_mate.png").convert_alpha(),
                                                             (532, 394)))
        self.mate_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((988, 226), (532, 394))),
                                                      pygame.transform.scale(
                                                          image_cache.load_image(
                                                              "resources/images/choosing_cat2_frame_mate.png").convert_alpha(),
                                                          (532, 394)))

        self.cycle_mate_left_button = UIImageButton(scale(pygame.Rect((1216, 616), (68, 68))),"",
                            object_id="#arrow_left_button",
                            manager=MANAGER)

        self.cycle_mate_right_button = UIImageButton(scale(pygame.Rect((1416, 616), (68, 68))),"",
                            object_id="#arrow_right_button",
                            manager=MANAGER)

        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "",
                                             object_id="#next_cat_button")
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

        self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1160), (68, 68))), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1160), (68, 68))), "",
                                              object_id="#relation_list_next")
        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((698, 1160), (204, 68))),
                                                         object_id=get_text_box_theme())

        # This may be deleted and changed later.
        self.toggle_mate = UIImageButton(scale(pygame.Rect((646, 620), (306, 60))), "",
                                         object_id="#confirm_mate_button")

        # The text will be changed as needed. This is used for both the "this pair can't have
        # offspring" message, header for the kittens section for mated cats.
        self.kitten_message = pygame_gui.elements.UITextBox("", scale(pygame.Rect((200, 666), (1200, 80))),
                                                            object_id=get_text_box_theme("#text_box_22_horizcenter"))
        self.kitten_message.hide()

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

    def exit_screen(self):
        self.selected_mate_index = 0
        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.mate_elements:
            self.mate_elements[ele].kill()
        self.mate_elements = {}

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        self.info.kill()
        del self.info
        self.the_cat_frame.kill()
        del self.the_cat_frame
        self.mate_frame.kill()
        del self.mate_frame
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.previous_page_button.kill()
        del self.previous_page_button
        self.next_page_button.kill()
        del self.next_page_button
        self.page_number.kill()
        del self.page_number
        self.toggle_mate.kill()
        del self.toggle_mate
        self.kitten_message.kill()
        del self.kitten_message
        self.cycle_mate_left_button.kill()
        del self.cycle_mate_left_button
        self.cycle_mate_right_button.kill()
        del self.cycle_mate_right_button

        self.all_pages = []

    def update_current_cat_info(self):
        """Updates all elements with the current cat, as well as the selected cat.
            Called when the screen switched, and whenever the focused cat is switched"""
        self.the_cat = Cat.all_cats[game.switches['cat']]

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.mate_elements:
            self.mate_elements[ele].kill()
        self.mate_elements = {}

        self.selected_cat = None
        self.current_page = 1

        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            "Choose a mate for " + str(self.the_cat.name),
            scale(pygame.Rect((300, 50), (1000, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"))

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((100, 300), (300, 300))),
                                                                         pygame.transform.scale(
                                                                             self.the_cat.sprite, (300, 300)))
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((130, 230), (240, 60))),
            name,
            object_id="#text_box_34_horizcenter")

        info = str(self.the_cat.moons) + " moons\n" + self.the_cat.status + "\n" + self.the_cat.genderalign + "\n" + \
               self.the_cat.trait
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(info,
                                                                          scale(pygame.Rect((410, 380), (200, 200))),
                                                                          object_id="#text_box_22_horizcenter_spacing_95",
                                                                          manager=MANAGER
                                                                          )

        # Determine what to draw regarding the other cat. If they have a mate, set the screen up for that.
        # if they don't, set the screen up to choose a mate.
        if len(self.the_cat.mate) > 0 and self.selected_mate_index < len(self.the_cat.mate):
            self.update_mate_screen()
        else:
            self.update_choose_mate()

        # Update the list of cats. Will be offspring if they have a mate, and valid mates if they don't
        self.update_cat_list()

        self.get_previous_next_cat()  # Determines where the previous and next cat goes.

        # Enable and disable the next and previous cat buttons as needed.
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

        # allow also one index above the mate amount, to be able to select a new one
        if len(self.the_cat.mate) <= 0:
            self.cycle_mate_left_button.hide()
            self.cycle_mate_right_button.hide()
        else:
            self.cycle_mate_left_button.show()
            self.cycle_mate_right_button.show()
            self.cycle_mate_left_button.enable()
            self.cycle_mate_right_button.enable()
            if self.selected_mate_index == len(self.the_cat.mate): 
                self.cycle_mate_right_button.disable()
            if self.selected_mate_index == 0:
                self.cycle_mate_left_button.disable()

    def update_mate_screen(self):
        """Sets up the screen for a cat with a mate already."""
        for ele in self.mate_elements:
            self.mate_elements[ele].kill()
        self.mate_elements = {}

        self.selected_cat = Cat.fetch_cat(self.the_cat.mate[self.selected_mate_index])

        self.draw_compatible_line_affection()
        self.mate_elements["center_heart"] = pygame_gui.elements.UIImage(scale(pygame.Rect((600, 376), (400, 156))),
                                                                         pygame.transform.scale(
                                                                             image_cache.load_image(
                                                                                 "resources/images/heart_mates.png").convert_alpha(),
                                                                             (400, 156)))

        self.mate_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((1200, 300), (300, 300))),
                                                                  pygame.transform.scale(
                                                                      self.selected_cat.sprite, (300, 300)))
        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.mate_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (220, 60))),
            name,
            object_id="#text_box_34_horizcenter")

        info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
               self.selected_cat.genderalign + "\n" + self.selected_cat.trait
        self.mate_elements["info"] = pygame_gui.elements.UITextBox(info,
                                                                   scale(pygame.Rect((1000, 380), (200, 200))),
                                                                   object_id="#text_box_22_horizcenter_spacing_95",
                                                                   manager=MANAGER
                                                                   )

        # Set the button to say "break-up"
        self.toggle_mate.kill()
        self.toggle_mate = UIImageButton(scale(pygame.Rect((646, 620), (306, 60))), "", object_id="#break_up_button")

        self.update_cat_list()

        # Display message
        if self.kittens:
            self.kitten_message.set_text("Their offspring:")
        else:
            self.kitten_message.set_text("This pair has never had offspring.")
        self.kitten_message.show()

        if len(self.the_cat.mate) <= 0:
            self.cycle_mate_left_button.hide()
            self.cycle_mate_right_button.hide()
        else:
            self.cycle_mate_left_button.show()
            self.cycle_mate_right_button.show()
            self.cycle_mate_left_button.enable()
            self.cycle_mate_right_button.enable()
            if self.selected_mate_index == len(self.the_cat.mate): 
                self.cycle_mate_right_button.disable()
            if self.selected_mate_index == 0:
                self.cycle_mate_left_button.disable()

    def update_cat_list(self):
        """Gathers all the cats to list, then updates the page. Also 
            sets the current page to 1. This should not be called when
            switching the page, but only when a new list of cats needs
            to be displayed. """

        # If the cat already has a mate, we display the children. If not, we display the possible mates
        self.all_pages = []
        if self.selected_cat and self.selected_cat.ID in self.the_cat.mate:
            self.kittens = False
            for x in game.clan.clan_cats:
                if self.the_cat.ID in [
                    Cat.all_cats[x].parent1,
                    Cat.all_cats[x].parent2
                ] and self.selected_cat.ID in [
                    Cat.all_cats[x].parent1,
                    Cat.all_cats[x].parent2
                ]:
                    self.all_pages.append(Cat.all_cats[x])
                    self.kittens = True
        else:
            self.all_pages = self.get_valid_mates()

        self.all_pages = self.chunks(self.all_pages, 30)

        self.update_cat_page()

    def update_cat_page(self):
        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.current_page > len(self.all_pages):
            self.current_page = max(len(self.all_pages), 1)

        # Handle which next buttons are clickable.
        if len(self.all_pages) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(self.all_pages):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(self.all_pages) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()

        # Display the current page and total pages.
        display_total_pages = max(1, len(self.all_pages))
        self.page_number.set_text(f"page {self.current_page} / {display_total_pages}")

        if len(self.all_pages) > 0:
            display_cats = self.all_pages[self.current_page - 1]
        else:
            display_cats = []

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        pos_x = 0
        pos_y = 40
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                cat.sprite, cat_object=cat)
            pos_x += 120
            if pos_x >= 1100:
                pos_x = 0
                pos_y += 120
            i += 1        

    def update_choose_mate(self, breakup=False):
        """This sets up the page for choosing a mate. Called when the current cat doesn't have a mate, or if
            you broke then and their mate up. If 'breakup' is set to true, it will display the break-up
            center heart. """
        for ele in self.mate_elements:
            self.mate_elements[ele].kill()
        self.mate_elements = {}

        if self.selected_cat:
            self.draw_compatible_line_affection()

            if breakup:
                self.selected_mate_index = 0
                self.mate_elements["center_heart"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((600, 376), (400, 156))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/heart_breakup.png").convert_alpha(), (400, 156)))   
            else:
                self.mate_elements["center_heart"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((600, 376), (400, 156))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/heart_maybe.png").convert_alpha(), (400, 156)))
            self.mate_elements["image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1200, 300), (300, 300))),
                pygame.transform.scale(
                    self.selected_cat.sprite, (300, 300)))

            name = str(self.selected_cat.name)
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.mate_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((1240, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter")

            info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n" + self.selected_cat.trait
            self.mate_elements["info"] = pygame_gui.elements.UITextBox(info,
                                                                       scale(pygame.Rect((1000, 380), (200, 200))),
                                                                       object_id="#text_box_22_horizcenter_spacing_95",
                                                                       manager=MANAGER)
            # Display message

            pixel_font_size = int(22 / 1400 * screen_y)
            if self.the_cat.gender == self.selected_cat.gender and not game.settings[
                'no gendered breeding']:
                self.kitten_message.set_text(
                    f"<font pixel_size={pixel_font_size}> (this pair will not be able to have kittens) </font>")
                self.kitten_message.show()
            else:
                self.kitten_message.hide()
        else:
            self.kitten_message.hide()

        self.update_cat_list()

        self.toggle_mate.kill()
        self.toggle_mate = UIImageButton(scale(pygame.Rect((646, 620), (306, 60))), "",
                                         object_id="#confirm_mate_button")

        self.update_buttons()

    def draw_compatible_line_affection(self):
        """Draws the heart-line based on capability, and draws the hearts based on romantic love. """

        # Set the lines
        self.mate_elements["compat_line"] = pygame_gui.elements.UIImage(scale(pygame.Rect((600, 380), (400, 156))),
                                                                        pygame.transform.scale(
                                                                            image_cache.load_image(
                                                                                "resources/images/line_neutral.png").convert_alpha(),
                                                                            (400, 156)))
        if get_personality_compatibility(self.the_cat, self.selected_cat) is True:
            self.mate_elements["compat_line"].set_image(
                pygame.transform.scale(
                    image_cache.load_image("resources/images/line_compatible.png").convert_alpha(),
                    (400, 156)))
        elif get_personality_compatibility(self.the_cat, self.selected_cat) is False:
            self.mate_elements["compat_line"].set_image(
                pygame.transform.scale(
                    image_cache.load_image("resources/images/line_incompatible.png").convert_alpha(),
                    (400, 156)))

        # Set romantic hearts of current cat towards mate or selected cat.
        if self.the_cat.dead:
            romantic_love = 0
        else:
            if self.selected_cat.ID in self.the_cat.relationships:
                relation = self.the_cat.relationships[self.selected_cat.ID]
            else:
                relation = self.the_cat.create_one_relationship(self.selected_cat)
            romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 31 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 420
        for i in range(0, heart_number):
            self.mate_elements["heart1" + str(i)] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_pos, 570), (44, 40))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png").convert_alpha(),
                    (44, 40)))
            x_pos += 54

        # Set romantic hearts of mate/selected cat towards current_cat.
        if self.selected_cat.dead:
            romantic_love = 0
        else:
            if self.the_cat.ID in self.selected_cat.relationships:
                relation = self.selected_cat.relationships[self.the_cat.ID]
            else:
                relation = self.selected_cat.create_one_relationship(self.the_cat)
            romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 31 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 1136
        for i in range(0, heart_number):
            self.mate_elements["heart2" + str(i)] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_pos, 570), (44, 40))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png").convert_alpha(),
                    (44, 40)))
            x_pos -= 54

    def update_buttons(self):
        """This updates the state of buttons. For this screen, it only deals with the toggle-mates button"""
        if self.selected_cat is None:
            self.toggle_mate.disable()
        else:
            self.toggle_mate.enable()

    def get_previous_next_cat(self):
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        self.previous_cat = 0
        self.next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            self.previous_cat = game.clan.instructor.ID

        if is_instructor:
            self.next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                self.next_cat = 1
            if self.next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and not check_cat.outside and \
                    check_cat.age not in ["adolescent", "kitten", "newborn"] and check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and not check_cat.outside and \
                    check_cat.age not in ["adolescent", "kitten", "newborn"] and check_cat.df == self.the_cat.df:
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def on_use(self):

        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))

    def get_valid_mates(self):
        """Get a list of valid mates for the current cat"""
        valid_mates = []
        for relevant_cat in Cat.all_cats_list:
            if relevant_cat.ID == self.the_cat.ID:
                continue
            if self.the_cat.is_potential_mate(
                    relevant_cat,
                    for_love_interest=False,
                    age_restriction=False) and\
                relevant_cat.ID not in self.the_cat.mate:
                valid_mates.append(relevant_cat)
        return valid_mates

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class RelationshipScreen(Screens):
    checkboxes = {}  # To hold the checkboxes.
    focus_cat_elements = {}
    relation_list_elements = {}
    sprite_buttons = {}
    inspect_cat_elements = {}
    previous_search_text = ""

    current_page = 1

    inspect_cat = None

    search_bar = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_search.png").convert_alpha(),
        (456 / 1600 * screen_x, 78 / 1400 * screen_y)
    )
    details_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_details_frame.png").convert_alpha(),
        (508 / 1600 * screen_x,
         688 / 1400 * screen_y)
    )
    toggle_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_toggle_frame.png").convert_alpha(),
        (502 / 1600 * screen_x, 240 / 1400 * screen_y)
    )
    list_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_list_frame.png").convert_alpha(),
        (1004 / 1600 * screen_x, 1000 / 1400 * screen_y)
    )

    def __init__(self, name=None):
        super().__init__(name)
        self.all_relations = None
        self.the_cat = None
        self.previous_cat = None
        self.next_cat = None
        self.view_profile_button = None
        self.switch_focus_button = None
        self.page_number = None
        self.next_page_button = None
        self.previous_page_button = None
        self.show_empty_text = None
        self.show_dead_text = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.log_icon = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.sprite_buttons.values():
                self.inspect_cat = event.ui_element.return_cat_object()
                self.update_inspected_relation()
            elif event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.switch_focus_button:
                game.switches["cat"] = self.inspect_cat.ID
                self.update_focus_cat()
            elif event.ui_element == self.view_profile_button:
                game.switches["cat"] = self.inspect_cat.ID
                self.change_screen('profile screen')
            elif event.ui_element == self.next_cat_button:
                if Cat.fetch_cat(self.next_cat) is not None:
                    game.switches["cat"] = self.next_cat
                    self.update_focus_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if Cat.fetch_cat(self.previous_cat) is not None:
                    game.switches["cat"] = self.previous_cat
                    self.update_focus_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_page()
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_page()
            elif event.ui_element == self.log_icon:
                if self.inspect_cat.ID not in self.the_cat.relationships:
                    return
                RelationshipLog(
                    self.the_cat.relationships[self.inspect_cat.ID],
                    [self.view_profile_button, self.switch_focus_button,\
                        self.next_cat_button,self.previous_cat_button,self.next_page_button],
                    [self.back_button, self.log_icon, self.checkboxes["show_dead"], self.checkboxes["show_empty"],\
                     self.show_dead_text, self.show_empty_text]
                )
            elif event.ui_element == self.checkboxes["show_dead"]:
                if game.settings['show dead relation']:
                    game.settings['show dead relation'] = False
                else:
                    game.settings['show dead relation'] = True
                self.update_checkboxes()
                self.apply_cat_filter()
                self.update_cat_page()
            elif event.ui_element == self.checkboxes["show_empty"]:
                if game.settings['show empty relation']:
                    game.settings['show empty relation'] = False
                else:
                    game.settings['show empty relation'] = True
                self.update_checkboxes()
                self.apply_cat_filter()
                self.update_cat_page()

    def screen_switches(self):

        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "",
                                             object_id="#next_cat_button")
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

        self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((1220, 194), (290, 46))),
                                                              object_id="#search_entry_box")

        self.show_dead_text = pygame_gui.elements.UITextBox("Show Dead", scale(pygame.Rect((220, 1010), (200, 60))),
                                                            object_id="#text_box_30_horizleft")
        self.show_empty_text = pygame_gui.elements.UITextBox("Show Empty", scale(pygame.Rect((220, 1100), (200, 60))),
                                                             object_id="#text_box_30_horizleft")

        # Draw the checkboxes
        self.update_checkboxes()

        self.previous_page_button = UIImageButton(scale(pygame.Rect((880, 1232), (68, 68))), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(scale(pygame.Rect((1160, 1232), (68, 68))), "",
                                              object_id="#relation_list_next")

        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((890, 1234), (300, 68))),
                                                         object_id=get_text_box_theme("#text_box_30_horizcenter"))

        self.switch_focus_button = UIImageButton(scale(pygame.Rect((170, 780), (272, 60))), "",
                                                 object_id="#switch_focus_button")
        self.switch_focus_button.disable()
        self.view_profile_button = UIImageButton(scale(pygame.Rect((170, 840), (272, 60))), "",
                                                 object_id="#view_profile_button")
        self.view_profile_button.disable()

        self.log_icon = UIImageButton(scale(pygame.Rect((445, 808), (68, 68))), "",
                                                 object_id="#log_icon")
        self.log_icon.disable()

        # Updates all info for the currently focused cat.
        self.update_focus_cat()

    def exit_screen(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        for ele in self.focus_cat_elements:
            self.focus_cat_elements[ele].kill()
        self.focus_cat_elements = {}

        for ele in self.relation_list_elements:
            self.relation_list_elements[ele].kill()
        self.relation_list_elements = {}

        for ele in self.sprite_buttons:
            self.sprite_buttons[ele].kill()
        self.sprite_buttons = {}

        for ele in self.inspect_cat_elements:
            self.inspect_cat_elements[ele].kill()
        self.inspect_cat_elements = {}

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.search_bar.kill()
        del self.search_bar
        self.show_dead_text.kill()
        del self.show_dead_text
        self.show_empty_text.kill()
        del self.show_empty_text
        self.previous_page_button.kill()
        del self.previous_page_button
        self.next_page_button.kill()
        del self.next_page_button
        self.page_number.kill()
        del self.page_number
        self.switch_focus_button.kill()
        del self.switch_focus_button
        self.view_profile_button.kill()
        del self.view_profile_button
        self.log_icon.kill()
        del self.log_icon

    def get_previous_next_cat(self):
        """Determines where the previous the next buttons should lead, and enables/diables them"""
        """'Determines where the next and previous buttons point too."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                        check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    previous_cat = check_cat.ID

                elif next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                        check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def update_checkboxes(self):
        # Remove all checkboxes
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        if game.settings['show dead relation']:
            checkbox_type = "#checked_checkbox"
        else:
            checkbox_type = "#unchecked_checkbox"

        self.checkboxes["show_dead"] = UIImageButton(scale(pygame.Rect((156, 1010), (68, 68))), "",
                                                     object_id=checkbox_type)

        if game.settings['show empty relation']:
            checkbox_type = "#checked_checkbox"
        else:
            checkbox_type = "#unchecked_checkbox"

        self.checkboxes["show_empty"] = UIImageButton(scale(pygame.Rect((156, 1100), (68, 68))), "",
                                                      object_id=checkbox_type)

    def update_focus_cat(self):
        for ele in self.focus_cat_elements:
            self.focus_cat_elements[ele].kill()
        self.focus_cat_elements = {}

        self.the_cat = Cat.all_cats.get(game.switches['cat'],
                                        game.clan.instructor
                                        )

        self.current_page = 1
        self.inspect_cat = None

        # Keep a list of all the relations
        self.all_relations = list(self.the_cat.relationships.values()).copy()

        self.focus_cat_elements["header"] = pygame_gui.elements.UITextBox(str(self.the_cat.name) + " Relationships",
                                                                          scale(pygame.Rect((150, 150), (800, 100))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_34_horizleft"))
        self.focus_cat_elements["details"] = pygame_gui.elements.UITextBox(self.the_cat.genderalign + " - " + \
                                                                           str(self.the_cat.moons) + " moons - " + \
                                                                           self.the_cat.trait,
                                                                           scale(pygame.Rect((160, 210), (800, 60))),
                                                                           object_id=get_text_box_theme(
                                                                               "#text_box_22_horizleft"))
        self.focus_cat_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((50, 150), (100, 100))),
                                                                       self.the_cat.sprite)

        self.get_previous_next_cat()
        self.apply_cat_filter(self.search_bar.get_text())
        self.update_inspected_relation()
        self.update_cat_page()

    def update_inspected_relation(self):
        for ele in self.inspect_cat_elements:
            self.inspect_cat_elements[ele].kill()
        self.inspect_cat_elements = {}

        if self.inspect_cat is not None:
            # NAME LENGTH
            chosen_name = str(self.inspect_cat.name)
            if 19 <= len(chosen_name):
                if self.inspect_cat.dead:
                    chosen_short_name = str(self.inspect_cat.name)[0:11]
                    chosen_name = chosen_short_name + '...'
                    chosen_name += " (dead)"
                else:
                    chosen_short_name = str(self.inspect_cat.name)[0:16]
                    chosen_name = chosen_short_name + '...'

            self.inspect_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((150, 590), (300, 80))),
                chosen_name,
                object_id="#text_box_34_horizcenter")

            # Cat Image
            self.inspect_cat_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((150, 290), (300, 300))),
                                                                             pygame.transform.scale(
                                                                                 self.inspect_cat.sprite,
                                                                                 (300, 300)))

            related = False
            # Mate Heart
            # TODO: UI UPDATE IS NEEDED
            if len(self.the_cat.mate) > 0 and self.inspect_cat.ID in self.the_cat.mate:
                self.inspect_cat_elements["mate"] = pygame_gui.elements.UIImage(scale(pygame.Rect((90, 300), (44, 40))),
                                                                                pygame.transform.scale(
                                                                                    image_cache.load_image(
                                                                                        "resources/images/heart_big.png").convert_alpha(),
                                                                                    (44, 40)))
            else:
                # Family Dot
                related = self.the_cat.is_related(self.inspect_cat, game.settings["first_cousin_mates"])
                if related:
                    self.inspect_cat_elements['family'] = pygame_gui.elements.UIImage(
                        scale(pygame.Rect((90, 300), (36, 36))),
                        pygame.transform.scale(
                            image_cache.load_image(
                                "resources/images/dot_big.png").convert_alpha(),
                            (36, 36)))

            # Gender
            if self.inspect_cat.genderalign == 'female':
                gender_icon = image_cache.load_image("resources/images/female_big.png").convert_alpha()
            elif self.inspect_cat.genderalign == 'male':
                gender_icon = image_cache.load_image("resources/images/male_big.png").convert_alpha()
            elif self.inspect_cat.genderalign == 'trans female':
                gender_icon = image_cache.load_image("resources/images/transfem_big.png").convert_alpha()
            elif self.inspect_cat.genderalign == 'trans male':
                gender_icon = image_cache.load_image("resources/images/transmasc_big.png").convert_alpha()
            else:
                # Everyone else gets the nonbinary icon
                gender_icon = image_cache.load_image("resources/images/nonbi_big.png").convert_alpha()

            self.inspect_cat_elements["gender"] = pygame_gui.elements.UIImage(scale(pygame.Rect((470, 290), (68, 68))),
                                                                              pygame.transform.scale(gender_icon,
                                                                                                     (68, 68)))

            # Column One Details:
            col1 = ""
            # Gender-Align
            col1 += self.inspect_cat.genderalign + "\n"

            # Age
            col1 += f"{self.inspect_cat.moons} moons\n"

            # Trait
            col1 += f"{self.inspect_cat.trait}\n"

            self.inspect_cat_elements["col1"] = pygame_gui.elements.UITextBox(col1,
                                                                              scale(pygame.Rect((120, 650), (180, 180))),
                                                                              object_id="#text_box_22_horizleft_spacing_95",
                                                                              manager=MANAGER)

            # Column Two Details:
            col2 = ""

            # Mate
            if len(self.inspect_cat.mate) > 0 and self.the_cat.ID not in self.inspect_cat.mate:
                col2 += "has a mate\n"
            elif len(self.the_cat.mate) > 0 and self.inspect_cat.ID in self.the_cat.mate:
                col2 += f"{self.the_cat.name}'s mate\n"
            else:
                col2 += "mate: none\n"

            # Relation info:
            if related:
                if self.the_cat.is_uncle_aunt(self.inspect_cat):
                    if self.inspect_cat.genderalign in ['female', 'trans female']:
                        col2 += "related: niece"
                    elif self.inspect_cat.genderalign in ['male', 'trans male']:
                        col2 += "related: nephew"
                    else:
                        col2 += "related: sibling's child\n"
                elif self.inspect_cat.is_uncle_aunt(self.the_cat):
                    if self.inspect_cat.genderalign in ['female', 'trans female']:
                        col2 += "related: aunt"
                    elif self.inspect_cat.genderalign in ['male', 'trans male']:
                        col2 += "related: uncle"
                    else:
                        col2 += "related: parent's sibling"
                elif self.inspect_cat.is_grandparent(self.the_cat):
                    col2 += "related: grandparent"
                elif self.the_cat.is_grandparent(self.inspect_cat):
                    col2 += "related: grandchild"
                elif self.inspect_cat.is_parent(self.the_cat):
                    col2 += "related: parent"
                elif self.the_cat.is_parent(self.inspect_cat):
                    col2 += "related: child"
                elif self.inspect_cat.is_sibling(self.the_cat) or self.the_cat.is_sibling(self.inspect_cat):
                    if self.inspect_cat.is_littermate(self.the_cat) or self.the_cat.is_littermate(self.inspect_cat):
                        col2 += "related: sibling (littermate)"
                    else:
                        col2 += "related: sibling"
                elif not game.settings["first_cousin_mates"] and self.inspect_cat.is_cousin(self.the_cat):
                    col2 += "related: cousin"

            self.inspect_cat_elements["col2"] = pygame_gui.elements.UITextBox(col2,
                                                                              scale(pygame.Rect((300, 650), (180, 180))),
                                                                              object_id="#text_box_22_horizleft_spacing_95",
                                                                              manager=MANAGER)

            if self.inspect_cat.dead:
                self.view_profile_button.enable()
                self.switch_focus_button.disable()
                self.log_icon.enable()
            else:
                self.view_profile_button.enable()
                self.switch_focus_button.enable()
                self.log_icon.enable()
        else:
            self.view_profile_button.disable()
            self.switch_focus_button.disable()
            self.log_icon.disable()

    def apply_cat_filter(self, search_text=""):
        # Filter for dead or empty cats
        self.filtered_cats = self.all_relations.copy()
        if not game.settings["show dead relation"]:
            self.filtered_cats = list(
                filter(lambda rel: not rel.cat_to.dead, self.filtered_cats))

        if not game.settings["show empty relation"]:
            self.filtered_cats = list(
                filter(
                    lambda rel: (rel.romantic_love + rel.platonic_like + rel.
                                 dislike + rel.admiration + rel.comfortable +
                                 rel.jealousy + rel.trust) > 0, self.filtered_cats))

        # Filter for search
        search_cats = []
        if search_text.strip() != "":
            for cat in self.filtered_cats:
                if search_text.lower() in str(cat.cat_to.name).lower():
                    search_cats.append(cat)
            self.filtered_cats = search_cats

    def update_cat_page(self):
        for ele in self.relation_list_elements:
            self.relation_list_elements[ele].kill()
        self.relation_list_elements = {}

        for ele in self.sprite_buttons:
            self.sprite_buttons[ele].kill()
        self.sprite_buttons = {}

        all_pages = self.chunks(self.filtered_cats, 8)

        if self.current_page > len(all_pages):
            self.current_page = len(all_pages)

        if self.current_page == 0:
            self.current_page = 1

        if all_pages:
            display_rel = all_pages[self.current_page - 1]
        else:
            display_rel = []

        pos_x = 580
        pos_y = 300
        i = 0
        for rel in display_rel:
            self.generate_relation_block((pos_x, pos_y), rel, i)

            i += 1
            pos_x += 244
            if pos_x > 1400:
                pos_y += 484
                pos_x = 580

        self.page_number.set_text(f"{self.current_page} / {len(all_pages)}")

        # Enable and disable page buttons.
        if len(all_pages) <= 1:
            self.previous_page_button.disable()
            self.next_page_button.disable()
        elif self.current_page >= len(all_pages):
            self.previous_page_button.enable()
            self.next_page_button.disable()
        elif self.current_page == 1 and len(all_pages) > 1:
            self.previous_page_button.disable()
            self.next_page_button.enable()
        else:
            self.previous_page_button.enable()
            self.next_page_button.enable()

    def generate_relation_block(self, pos, the_relationship, i):
        # Generates a relation_block starting at postion, from the relationship object "the_relation"
        # "position" should refer to the top left corner of the *main* relation box, not including the name.
        pos_x = pos[0]
        pos_y = pos[1]

        self.sprite_buttons["image" + str(i)] = UISpriteButton(scale(pygame.Rect((pos_x + 44, pos_y), (100, 100))),
                                                               the_relationship.cat_to.sprite,
                                                               cat_object=the_relationship.cat_to)

        # CHECK NAME LENGTH - SHORTEN IF NECESSARY
        name = str(the_relationship.cat_to.name)  # get name
        if len(name) >= 14:  # check name length
            short_name = str(the_relationship.cat_to.name)[0:11]
            name = short_name + '...'
        self.relation_list_elements["name" + str(i)] = pygame_gui.elements.UITextBox(name,
                                                                                     scale(pygame.Rect(
                                                                                         (pos_x, pos_y - 48),
                                                                                         (204, 60))),
                                                                                     object_id="#text_box_26_horizcenter")

        # Gender alignment
        if the_relationship.cat_to.genderalign == 'female':
            gender_icon = image_cache.load_image("resources/images/female_big.png").convert_alpha()
        elif the_relationship.cat_to.genderalign == 'male':
            gender_icon = image_cache.load_image("resources/images/male_big.png").convert_alpha()
        elif the_relationship.cat_to.genderalign == 'trans female':
            gender_icon = image_cache.load_image("resources/images/transfem_big.png").convert_alpha()
        elif the_relationship.cat_to.genderalign == 'trans male':
            gender_icon = image_cache.load_image("resources/images/transmasc_big.png").convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image("resources/images/nonbi_big.png").convert_alpha()

        self.relation_list_elements["gender" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((pos_x + 160,
                                                                                                        pos_y + 10),
                                                                                                       (36, 36))),
                                                                                     pygame.transform.scale(gender_icon,
                                                                                                            (36, 36)))

        related = False
        # MATE
        if len(self.the_cat.mate) > 0 and the_relationship.cat_to.ID in self.the_cat.mate:

            self.relation_list_elements['mate_icon' + str(i)] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((pos_x + 10, pos_y + 10),
                                  (22, 20))),
                image_cache.load_image(
                    "resources/images/heart_big.png").convert_alpha())
        else:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if game.settings['first_cousin_mates']:
                check_cousins = False
            else:
                check_cousins = the_relationship.cat_to.is_cousin(self.the_cat)

            if the_relationship.cat_to.is_uncle_aunt(self.the_cat) or self.the_cat.is_uncle_aunt(
                    the_relationship.cat_to) \
                    or the_relationship.cat_to.is_grandparent(self.the_cat) or \
                    self.the_cat.is_grandparent(the_relationship.cat_to) or \
                    the_relationship.cat_to.is_parent(self.the_cat) or \
                    self.the_cat.is_parent(the_relationship.cat_to) or \
                    the_relationship.cat_to.is_sibling(self.the_cat) or check_cousins:
                related = True
                self.relation_list_elements['relation_icon' + str(i)] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((pos_x + 10,
                                       pos_y + 10),
                                      (18, 18))),
                    image_cache.load_image(
                        "resources/images/dot_big.png").convert_alpha())

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        barbar = 44
        bar_count = 0

        # ROMANTIC LOVE
        # CHECK AGE DIFFERENCE
        same_age = the_relationship.cat_to.age == self.the_cat.age
        adult_ages = ['young adult', 'adult', 'senior adult', 'senior']
        both_adult = the_relationship.cat_to.age in adult_ages and self.the_cat.age in adult_ages
        check_age = both_adult or same_age

        # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
        # even if they somehow have some. They should not be able to get any, but it never hurts to check.
        if not check_age or related:
            display_romantic = 0
            # Print, just for bug checking. Again, they should not be able to get love towards their relative.
            if the_relationship.romantic_love and related:
                print(
                    f"WARNING: {self.the_cat.name} has {the_relationship.romantic_love} romantic love towards their relative, {the_relationship.cat_to.name}")
        else:
            display_romantic = the_relationship.romantic_love

        if display_romantic > 49:
            text = "romantic love:"
        else:
            text = "romantic like:"

        self.relation_list_elements[f'romantic_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                         scale(pygame.Rect(
                                                                                             (pos_x + 6, pos_y + 87 + (
                                                                                                     barbar * bar_count)),
                                                                                             (170, 60))),
                                                                                         object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'romantic_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                                 pos_y + 130 + (
                                                                                                         barbar * bar_count)),
                                                                                                (188, 20))),
                                                                              display_romantic,
                                                                              positive_trait=True,
                                                                              dark_mode=game.settings['dark mode']
                                                                              )
        bar_count += 1

        # PLANTONIC
        if the_relationship.platonic_like > 49:
            text = "platonic love:"
        else:
            text = "platonic like:"
        self.relation_list_elements[f'plantonic_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                          scale(pygame.Rect((pos_x + 6,
                                                                                                             pos_y + 87 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (160, 60))),
                                                                                          object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'platonic_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                                 pos_y + 130 + (
                                                                                                         barbar * bar_count)),
                                                                                                (188, 20))),
                                                                              the_relationship.platonic_like,
                                                                              positive_trait=True,
                                                                              dark_mode=game.settings['dark mode'])

        bar_count += 1

        # DISLIKE
        if the_relationship.dislike > 49:
            text = "hate:"
        else:
            text = "dislike:"
        self.relation_list_elements[f'dislike_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                        scale(pygame.Rect((pos_x + 6,
                                                                                                           pos_y + 87 + (
                                                                                                                   barbar * bar_count)),
                                                                                                          (160, 60))),
                                                                                        object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'dislike_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                                pos_y + 130 + (
                                                                                                        barbar * bar_count)),
                                                                                               (188, 20))),
                                                                             the_relationship.dislike,
                                                                             positive_trait=False,
                                                                             dark_mode=game.settings['dark mode'])

        bar_count += 1

        # ADMIRE
        if the_relationship.admiration > 49:
            text = "admiration:"
        else:
            text = "respect:"
        self.relation_list_elements[f'admiration_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                           scale(pygame.Rect((pos_x + 6,
                                                                                                              pos_y + 87 + (
                                                                                                                      barbar * bar_count)),
                                                                                                             (
                                                                                                                 160,
                                                                                                                 60))),
                                                                                           object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'admiration_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                                   pos_y + 130 + (
                                                                                                           barbar * bar_count)),
                                                                                                  (188, 20))),
                                                                                the_relationship.admiration,
                                                                                positive_trait=True,
                                                                                dark_mode=game.settings['dark mode'])

        bar_count += 1

        # COMFORTABLE
        if the_relationship.comfortable > 49:
            text = "security:"
        else:
            text = "comfort:"
        self.relation_list_elements[f'comfortable_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                            scale(
                                                                                                pygame.Rect((pos_x + 6,
                                                                                                             pos_y + 87 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (160, 60))),
                                                                                            object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'comfortable_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                                    pos_y + 130 + (
                                                                                                            barbar * bar_count)),
                                                                                                   (188, 20))),
                                                                                 the_relationship.comfortable,
                                                                                 positive_trait=True,
                                                                                 dark_mode=game.settings['dark mode'])

        bar_count += 1

        # JEALOUS
        if the_relationship.jealousy > 49:
            text = "resentment:"
        else:
            text = "jealousy:"
        self.relation_list_elements[f'jealous_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                        scale(pygame.Rect((pos_x + 6,
                                                                                                           pos_y + 87 + (
                                                                                                                   barbar * bar_count)),
                                                                                                          (160, 60))),
                                                                                        object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'jealous_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                                pos_y + 130 + (
                                                                                                        barbar * bar_count)),
                                                                                               (188, 20))),
                                                                             the_relationship.jealousy,
                                                                             positive_trait=False,
                                                                             dark_mode=game.settings['dark mode'])

        bar_count += 1

        # TRUST
        if the_relationship.trust > 49:
            text = "reliance:"
        else:
            text = "trust:"
        self.relation_list_elements[f'trust_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                      scale(pygame.Rect((pos_x + 6,
                                                                                                         pos_y + 87 + (
                                                                                                                 barbar * bar_count)),
                                                                                                        (160, 60))),
                                                                                      object_id="#text_box_22_horizleft")
        self.relation_list_elements[f'trust_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                              pos_y + 130 + (
                                                                                                      barbar * bar_count)),
                                                                                             (188, 20))),
                                                                           the_relationship.trust,
                                                                           positive_trait=True,
                                                                           dark_mode=game.settings['dark mode'])

    def on_use(self):

        # LOAD UI IMAGES
        screen.blit(RelationshipScreen.search_bar, (1070 / 1600 * screen_x, 180 / 1400 * screen_y))
        screen.blit(RelationshipScreen.details_frame, (50 / 1600 * screen_x, 260 / 1400 * screen_y))
        screen.blit(RelationshipScreen.toggle_frame, (90 / 1600 * screen_x, 958 / 1400 * screen_y))
        screen.blit(RelationshipScreen.list_frame, (546 / 1600 * screen_x, 244 / 1400 * screen_y))

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.apply_cat_filter(self.search_bar.get_text())
            self.update_cat_page()
        self.previous_search_text = self.search_bar.get_text()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class MediationScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.selected_mediator = None
        self.selected_cat_1 = None
        self.selected_cat_2 = None
        self.mediator_elements = {}
        self.mediators = []
        self.cat_buttons = []
        self.page = 1
        self.selected_cat_elements = {}
        self.allow_romantic = True

    def handle_event(self, event):

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
            elif event.ui_element == self.last_med:
                self.selected_mediator -= 1
                self.update_mediator_info()
            elif event.ui_element == self.next_med:
                self.selected_mediator += 1
                self.update_mediator_info()
            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.romantic_checkbox:
                if self.allow_romantic:
                    self.allow_romantic = False
                else:
                    self.allow_romantic = True
                self.update_buttons()
            elif event.ui_element == self.deselect_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            elif event.ui_element == self.deselect_2:
                self.selected_cat_2 = None
                self.update_selected_cats()
            elif event.ui_element == self.mediate_button:
                game.mediated.append([self.selected_cat_1.ID, self.selected_cat_2.ID])
                game.patrolled.append(self.mediators[self.selected_mediator])
                output = Cat.mediate_relationship(
                    self.mediators[self.selected_mediator], self.selected_cat_1, self.selected_cat_2,
                    self.allow_romantic)
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.sabotoge_button:
                game.mediated.append(f"{self.selected_cat_1.ID}, {self.selected_cat_2.ID}")
                game.patrolled.append(self.mediators[self.selected_mediator])
                output = Cat.mediate_relationship(
                    self.mediators[self.selected_mediator], self.selected_cat_1, self.selected_cat_2,
                    self.allow_romantic,
                    sabotage=True)
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.random1:
                self.selected_cat_1 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_2 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element == self.random2:
                self.selected_cat_2 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_1 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in [self.selected_cat_1, self.selected_cat_2]:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT or not self.selected_cat_1:
                        self.selected_cat_1 = event.ui_element.return_cat_object()
                    else:
                        self.selected_cat_2 = event.ui_element.return_cat_object()
                    self.update_selected_cats()

    def screen_switches(self):
        # Gather the mediators:
        self.mediators = []
        for cat in Cat.all_cats_list:
            if cat.status in ["mediator", "mediator apprentice"] and not (cat.dead or cat.outside):
                self.mediators.append(cat)

        self.page = 1

        if self.mediators:
            if Cat.fetch_cat(game.switches["cat"]) in self.mediators:
                self.selected_mediator = self.mediators.index(Cat.fetch_cat(game.switches["cat"]))
            else:
                self.selected_mediator = 0
        else:
            self.selected_mediator = None

        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button")

        self.selected_frame_1 = pygame_gui.elements.UIImage(scale(pygame.Rect((100, 160), (400, 700))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/mediator_selected_frame.png"),
                                                                (400, 700))
                                                            )
        self.selected_frame_1.disable()
        self.selected_frame_2 = pygame_gui.elements.UIImage(scale(pygame.Rect((1100, 160), (400, 700))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/mediator_selected_frame.png"),
                                                                (400, 700))
                                                            )
        self.selected_frame_2.disable()

        self.cat_bg = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                        ((100, 940), (1400, 300))),
                                                  pygame.transform.scale(
                                                      pygame.image.load(
                                                          "resources/images/mediation_selection_bg.png").convert_alpha(),
                                                      (1400, 300))
                                                  )
        self.cat_bg.disable()

        # Will be overwritten
        self.romantic_checkbox = None
        self.romantic_checkbox_text = pygame_gui.elements.UILabel(scale(pygame.Rect((737, 650), (200, 40))),
                                                                  "Allow romantic",
                                                                  object_id=get_text_box_theme(
                                                                      "#text_box_22_horizleft"),
                                                                  manager=MANAGER)

        self.mediate_button = UIImageButton(scale(pygame.Rect((560, 700), (210, 60))), "",
                                            object_id="#mediate_button",
                                            manager=MANAGER)
        self.sabotoge_button = UIImageButton(scale(pygame.Rect((800, 700), (218, 60))), "",
                                             object_id="#sabotage_button",
                                             manager=MANAGER)

        self.next_med = UIImageButton(scale(pygame.Rect((952, 540), (68, 68))), "", object_id="#arrow_right_button")
        self.last_med = UIImageButton(scale(pygame.Rect((560, 540), (68, 68))), "", object_id="#arrow_left_button")

        self.next_page = UIImageButton(scale(pygame.Rect((866, 1224), (68, 68))), "", object_id="#relation_list_next")
        self.previous_page = UIImageButton(scale(pygame.Rect((666, 1224), (68, 68))), "",
                                           object_id="#relation_list_previous")

        self.deselect_1 = UIImageButton(scale(pygame.Rect((136, 868), (254, 60))), "",
                                        object_id="#remove_cat_button")
        self.deselect_2 = UIImageButton(scale(pygame.Rect((1210, 868), (254, 60))), "",
                                        object_id="#remove_cat_button")

        self.results = pygame_gui.elements.UITextBox("",
                                                     scale(pygame.Rect((560, 770), (458, 200))),
                                                     object_id=get_text_box_theme(
                                                         "#text_box_22_horizcenter_spacing_95"),
                                                     manager=MANAGER)

        self.error = pygame_gui.elements.UITextBox("",
                                                   scale(pygame.Rect((560, 75), (458, 115))),
                                                   object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
                                                   manager=MANAGER)

        self.random1 = UIImageButton(scale(pygame.Rect((396, 864), (68, 68))), "", object_id="#random_dice_button")
        self.random2 = UIImageButton(scale(pygame.Rect((1136, 864), (68, 68))), "", object_id="#random_dice_button")

        self.update_buttons()
        self.update_mediator_info()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [i for i in self.all_cats_list if i.ID not in self.selected_cat_list()]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_mediator_info(self):
        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        if self.selected_mediator is not None:  # It can be zero, so we must test for not None here.
            x_value = 630
            mediator = self.mediators[self.selected_mediator]

            # Clear mediator as selected cat
            if mediator == self.selected_cat_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            if mediator == self.selected_cat_2:
                self.selected_cat_2 = None
                self.update_selected_cats()

            self.mediator_elements["mediator_image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x_value, 180), (300, 300))),
                pygame.transform.scale(
                    mediator.sprite, (300, 300)))

            name = str(mediator.name)
            if len(name) > 17:
                name = name[:15] + "..."
            self.mediator_elements["name"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((x_value - 10, 480), (320, -1))),
                name,
                object_id=get_text_box_theme())

            text = mediator.trait + "\n" + mediator.experience_level

            if mediator.not_working():
                text += "\nThis cat isn't able to work"
                self.mediate_button.disable()
                self.sabotoge_button.disable()
            else:
                text += "\nThis cat can work"
                self.mediate_button.enable()
                self.sabotoge_button.enable()

            self.mediator_elements["details"] = pygame_gui.elements.UITextBox(text,
                                                                              scale(pygame.Rect((x_value, 520),
                                                                                                (310, 120))),
                                                                              object_id=get_text_box_theme(
                                                                                  "#text_box_22_horizcenter_spacing_95"),
                                                                              manager=MANAGER)

            mediator_number = len(self.mediators)
            if self.selected_mediator < mediator_number - 1:
                self.next_med.enable()
            else:
                self.next_med.disable()

            if self.selected_mediator > 0:
                self.last_med.enable()
            else:
                self.last_med.disable()

        else:
            self.last_med.disable()
            self.next_med.disable()

        self.update_buttons()
        self.update_list_cats()

    def update_list_cats(self):
        self.all_cats_list = [i for i in Cat.all_cats_list if
                              (i.ID != self.mediators[self.selected_mediator].ID) and not (i.dead or i.outside)]
        self.all_cats = self.chunks(self.all_cats_list, 24)

        self.update_page()

    def update_page(self):
        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        if self.page > len(self.all_cats):
            self.page = len(self.all_cats)
        elif self.page < 1:
            self.page = 1

        if self.page >= len(self.all_cats):
            self.next_page.disable()
        else:
            self.next_page.enable()

        if self.page <= 1:
            self.previous_page.disable()
        else:
            self.previous_page.enable()

        x = 130
        y = 970
        for cat in self.all_cats[self.page - 1]:
            self.cat_buttons.append(
                UISpriteButton(scale(pygame.Rect((x, y), (100, 100))), cat.sprite, cat_object=cat)
            )
            x += 110
            if x > 1400:
                y += 110
                x = 130

    def update_selected_cats(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.draw_info_block(self.selected_cat_1, (100, 160))
        self.draw_info_block(self.selected_cat_2, (1100, 160))

        self.update_buttons()

    def draw_info_block(self, cat, starting_pos: tuple):
        if not cat:
            return

        other_cat = [Cat.fetch_cat(i) for i in self.selected_cat_list() if i != cat.ID]
        if other_cat:
            other_cat = other_cat[0]
        else:
            other_cat = None

        tag = str(starting_pos)

        x = starting_pos[0]
        y = starting_pos[1]

        self.selected_cat_elements["cat_image" + tag] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((x + 100, y + 14), (200, 200))),
            pygame.transform.scale(
                cat.sprite, (200, 200)))

        name = str(cat.name)
        if len(name) > 17:
            name = name[:15] + "..."
        self.selected_cat_elements["name" + tag] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((x, y + 200), (400, 60))),
            name,
            object_id="#text_box_30_horizcenter")

        # Gender
        if cat.genderalign == 'female':
            gender_icon = image_cache.load_image("resources/images/female_big.png").convert_alpha()
        elif cat.genderalign == 'male':
            gender_icon = image_cache.load_image("resources/images/male_big.png").convert_alpha()
        elif cat.genderalign == 'trans female':
            gender_icon = image_cache.load_image("resources/images/transfem_big.png").convert_alpha()
        elif cat.genderalign == 'trans male':
            gender_icon = image_cache.load_image("resources/images/transmasc_big.png").convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image("resources/images/nonbi_big.png").convert_alpha()

        self.selected_cat_elements["gender" + tag] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((x + 320, y + 24), (50, 50))),
            pygame.transform.scale(gender_icon,
                                   (50, 50)))

        related = False
        # MATE
        if other_cat and len(cat.mate) > 0 and other_cat.ID in cat.mate:
            self.selected_cat_elements['mate_icon' + tag] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((x + 28, y + 28),
                                  (44, 40))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png").convert_alpha(),
                    (44, 40)))
        elif other_cat:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if game.settings['first_cousin_mates']:
                check_cousins = False
            else:
                check_cousins = other_cat.is_cousin(cat)

            if other_cat.is_uncle_aunt(cat) or cat.is_uncle_aunt(other_cat) \
                    or other_cat.is_grandparent(cat) or \
                    cat.is_grandparent(other_cat) or \
                    other_cat.is_parent(cat) or \
                    cat.is_parent(other_cat) or \
                    other_cat.is_sibling(cat) or check_cousins:
                related = True
                self.selected_cat_elements['relation_icon' + tag] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((x + 28,
                                       y + 28),
                                      (36, 36))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/dot_big.png").convert_alpha(),
                        (36, 36)))

        col1 = str(cat.moons)
        if cat.moons == 1:
            col1 += " moon"
        else:
            col1 += " moons"
        if len(cat.trait) > 15:
            _t = cat.trait[:13] + ".."
        else:
            _t = cat.trait
        col1 += "\n" + _t
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(col1,
                                                                                 scale(pygame.Rect((x + 42, y + 252),
                                                                                                   (180, -1))),
                                                                                 object_id="#text_box_22_horizleft_spacing_95",
                                                                                 manager=MANAGER)

        mates = False
        if len(cat.mate) > 0:
            col2 = "has a mate"
            if other_cat:
                if other_cat.ID in cat.mate:
                    mates = True
                    col2 = f"{other_cat.name}'s mate"
        else:
            col2 = "mate: none"

        # Relation info:
        if related and other_cat and not mates:
            col2 += "\n"
            if other_cat.is_uncle_aunt(cat):
                if cat.genderalign in ['female', 'trans female']:
                    col2 += "niece"
                elif cat.genderalign in ['male', 'trans male']:
                    col2 += "nephew"
                else:
                    col2 += "sibling's child"
            elif cat.is_uncle_aunt(other_cat):
                if cat.genderalign in ['female', 'trans female']:
                    col2 += "aunt"
                elif cat.genderalign in ['male', 'trans male']:
                    col2 += "uncle"
                else:
                    col2 += "related: parent's sibling"
            elif cat.is_grandparent(other_cat):
                col2 += "grandparent"
            elif other_cat.is_grandparent(cat):
                col2 += "grandchild"
            elif cat.is_parent(other_cat):
                col2 += "parent"
            elif other_cat.is_parent(cat):
                col2 += "child"
            elif cat.is_sibling(other_cat) or other_cat.is_sibling(cat):
                col2 += "sibling"
            elif not game.settings["first_cousin_mates"] and other_cat.is_cousin(cat):
                col2 += "cousin"

        self.selected_cat_elements["col2" + tag] = pygame_gui.elements.UITextBox(col2,
                                                                                 scale(pygame.Rect((x + 220, y + 252),
                                                                                                   (161, -1))),
                                                                                 object_id="#text_box_22_horizleft_spacing_95",
                                                                                 manager=MANAGER)

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        if other_cat:

            name = str(cat.name)
            if len(name) > 13:
                name = name[:10] + ".."
            self.selected_cat_elements[f"relation_heading{tag}"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((x + 40, y + 320),
                                  (320, -1))),
                f"~~{name}'s feelings~~",
                object_id="#text_box_22_horizcenter")

            if other_cat.ID in cat.relationships:
                the_relationship = cat.relationships[other_cat.ID]
            else:
                the_relationship = cat.create_one_relationship(other_cat)

            barbar = 42
            bar_count = 0
            y_start = 354
            x_start = 50

            # ROMANTIC LOVE
            # CHECK AGE DIFFERENCE
            same_age = the_relationship.cat_to.age == cat.age
            adult_ages = ['young adult', 'adult', 'senior adult', 'senior']
            both_adult = the_relationship.cat_to.age in adult_ages and cat.age in adult_ages
            check_age = both_adult or same_age

            # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
            # even if they somehow have some. They should not be able to get any, but it never hurts to check.
            if not check_age or related:
                display_romantic = 0
                # Print, just for bug checking. Again, they should not be able to get love towards their relative.
                if the_relationship.romantic_love and related:
                    print(str(cat.name) + " has " + str(the_relationship.romantic_love) + " romantic love "
                                                                                          "towards their relative, " + str(
                        the_relationship.cat_to.name))
            else:
                display_romantic = the_relationship.romantic_love

            if display_romantic > 49:
                text = "romantic love:"
            else:
                text = "romantic like:"

            self.selected_cat_elements[f'romantic_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                (x + x_start, y + y_start + (barbar * bar_count) - 10),
                (300, 60))),
                                                                                              object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'romantic_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                      y + y_start + 30 + (
                                                                                                              barbar * bar_count)),
                                                                                                     (300, 18))),
                                                                                   display_romantic,
                                                                                   positive_trait=True,
                                                                                   dark_mode=game.settings['dark mode']
                                                                                   )
            bar_count += 1

            # PLANTONIC
            if the_relationship.platonic_like > 49:
                text = "platonic love:"
            else:
                text = "platonic like:"
            self.selected_cat_elements[f'plantonic_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                (x + x_start, y + y_start + (barbar * bar_count) - 10),
                (300, 60))),
                                                                                               object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'platonic_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                      y + y_start + 30 + (
                                                                                                              barbar * bar_count)),
                                                                                                     (300, 18))),
                                                                                   the_relationship.platonic_like,
                                                                                   positive_trait=True,
                                                                                   dark_mode=game.settings['dark mode'])

            bar_count += 1

            # DISLIKE
            if the_relationship.dislike > 49:
                text = "hate:"
            else:
                text = "dislike:"
            self.selected_cat_elements[f'dislike_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                (x + x_start, y + y_start + (barbar * bar_count) - 10),
                (300, 60))),
                                                                                             object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'dislike_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                     y + y_start + 30 + (
                                                                                                             barbar * bar_count)),
                                                                                                    (300, 18))),
                                                                                  the_relationship.dislike,
                                                                                  positive_trait=False,
                                                                                  dark_mode=game.settings['dark mode'])

            bar_count += 1

            # ADMIRE
            if the_relationship.admiration > 49:
                text = "admiration:"
            else:
                text = "respect:"
            self.selected_cat_elements[f'admiration_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                (x + x_start, y + y_start + (barbar * bar_count) - 10),
                (300, 60))),
                                                                                                object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'admiration_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                        y + y_start + 30 + (
                                                                                                                barbar * bar_count)),
                                                                                                       (300, 18))),
                                                                                     the_relationship.admiration,
                                                                                     positive_trait=True,
                                                                                     dark_mode=game.settings[
                                                                                         'dark mode'])

            bar_count += 1

            # COMFORTABLE
            if the_relationship.comfortable > 49:
                text = "security:"
            else:
                text = "comfortable:"
            self.selected_cat_elements[f'comfortable_text{tag}'] = pygame_gui.elements.UITextBox(text,
                                                                                                 scale(pygame.Rect(
                                                                                                     (x + x_start,
                                                                                                      y + y_start + (
                                                                                                              barbar * bar_count) - 10),
                                                                                                     (300, 60))),
                                                                                                 object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'comfortable_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                         y + y_start + 30 + (
                                                                                                                 barbar * bar_count)),
                                                                                                        (300, 18))),
                                                                                      the_relationship.comfortable,
                                                                                      positive_trait=True,
                                                                                      dark_mode=game.settings[
                                                                                          'dark mode'])

            bar_count += 1

            # JEALOUS
            if the_relationship.jealousy > 49:
                text = "resentment:"
            else:
                text = "jealousy:"
            self.selected_cat_elements[f'jealous_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                (x + x_start, y + y_start + (barbar * bar_count) - 10),
                (300, 60))),
                                                                                             object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'jealous_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                     y + y_start + 30 + (
                                                                                                             barbar * bar_count)),
                                                                                                    (300, 18))),
                                                                                  the_relationship.jealousy,
                                                                                  positive_trait=False,
                                                                                  dark_mode=game.settings['dark mode'])

            bar_count += 1

            # TRUST
            if the_relationship.trust > 49:
                text = "reliance:"
            else:
                text = "trust:"
            self.selected_cat_elements[f'trust_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                (x + x_start, y + y_start + (barbar * bar_count) - 10),
                (300, 60))),
                                                                                           object_id="#text_box_22_horizleft")
            self.selected_cat_elements[f'trust_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                   y + y_start + 30 + (
                                                                                                           barbar * bar_count)),
                                                                                                  (300, 18))),
                                                                                the_relationship.trust,
                                                                                positive_trait=True,
                                                                                dark_mode=game.settings['dark mode'])

    def selected_cat_list(self):
        output = []
        if self.selected_cat_1:
            output.append(self.selected_cat_1.ID)
        if self.selected_cat_2:
            output.append(self.selected_cat_2.ID)

        return output

    def update_buttons(self):
        error_message = ""

        invalid_mediator = False
        if self.selected_mediator is not None:
            if self.mediators[self.selected_mediator].not_working():
                invalid_mediator = True
                error_message += "This mediator can't work this moon. "
            elif self.mediators[self.selected_mediator] in game.patrolled:
                invalid_mediator = True
                error_message += "This mediator has already worked this moon. "
        else:
            invalid_mediator = True

        invalid_pair = False
        if self.selected_cat_1 and self.selected_cat_2:
            for x in game.mediated:
                if self.selected_cat_1.ID in x and self.selected_cat_2.ID in x:
                    invalid_pair = True
                    error_message += "This pair has already been mediated this moon. "
                    break
        else:
            invalid_pair = True

        self.error.set_text(error_message)

        if invalid_mediator or invalid_pair:
            self.mediate_button.disable()
            self.sabotoge_button.disable()
        else:
            self.mediate_button.enable()
            self.sabotoge_button.enable()

        if self.romantic_checkbox:
            self.romantic_checkbox.kill()

        if self.allow_romantic:
            self.romantic_checkbox = UIImageButton(scale(pygame.Rect((642, 635), (68, 68))), "",
                                                   object_id="#checked_checkbox",
                                                   tool_tip_text="Allow effects on romantic like, if possible. ",
                                                   manager=MANAGER)
        else:
            self.romantic_checkbox = UIImageButton(scale(pygame.Rect((642, 635), (68, 68))), "",
                                                   object_id="#unchecked_checkbox",
                                                   tool_tip_text="Allow effects on romantic like, if possible. ",
                                                   manager=MANAGER)

    def exit_screen(self):
        self.selected_cat_1 = None
        self.selected_cat_2 = None

        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.mediators = []
        self.back_button.kill()
        del self.back_button
        self.selected_frame_1.kill()
        del self.selected_frame_1
        self.selected_frame_2.kill()
        del self.selected_frame_2
        self.cat_bg.kill()
        del self.cat_bg
        self.mediate_button.kill()
        del self.mediate_button
        self.sabotoge_button.kill()
        del self.sabotoge_button
        self.last_med.kill()
        del self.last_med
        self.next_med.kill()
        del self.next_med
        self.deselect_1.kill()
        del self.deselect_1
        self.deselect_2.kill()
        del self.deselect_2
        self.next_page.kill()
        del self.next_page
        self.previous_page.kill()
        del self.previous_page
        self.results.kill()
        del self.results
        self.random1.kill()
        del self.random1
        self.random2.kill()
        del self.random2
        if self.romantic_checkbox:
            self.romantic_checkbox.kill()
            del self.romantic_checkbox
        self.romantic_checkbox_text.kill()
        del self.romantic_checkbox_text
        self.error.kill()
        del self.error

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
