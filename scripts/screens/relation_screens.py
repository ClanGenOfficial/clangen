import pygame.transform
import pygame_gui.elements
from random import choice

from .base_screens import Screens, cat_profiles

from scripts.utility import get_personality_compatibility, get_text_box_theme, scale
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER


class ChooseMentorScreen(Screens):
    selected_mentor = None
    current_page = 1
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300/1600 * screen_x, 452/1400 * screen_y))
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
                game.switches['cat'] = self.next_cat
                self.update_apprentice()
                self.update_selected_cat()
                self.update_buttons()
            elif event.ui_element == self.previous_cat_button:
                game.switches['cat'] = self.previous_cat
                self.update_apprentice()
                self.update_selected_cat()
                self.update_buttons()
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
                                                     object_id=get_text_box_theme("#header_text_box"), manager=MANAGER)
        self.info = UITextBoxTweaked("If an apprentice is 6 moons old and their mentor is changed, they "
                                     "will not be listed as a former apprentice on their old mentor's "
                                     "profile. An apprentice's mentor can have an influence on their "
                                     "trait and skill later in life.\nChoose your mentors wisely",
                                     scale(pygame.Rect((360, 120), (880, 200))), line_spacing=0.95,
                                     object_id=get_text_box_theme("#cat_patrol_info_box"), manager=MANAGER)
        if self.mentor is not None:
            self.current_mentor_text = pygame_gui.elements.UITextBox(f"{self.the_cat.name}'s current mentor is "
                                                                    f"{self.mentor.name}",
                                                                    scale(pygame.Rect((460, 260), (680, 60))),
                                                                    object_id=get_text_box_theme("#cat_patrol_info_box")
                                                                    , manager=MANAGER)
        else:
            self.current_mentor_text = pygame_gui.elements.UITextBox(f"{self.the_cat.name} does not have a mentor",
                                                                    scale(pygame.Rect((460, 260), (680, 60))),
                                                                    object_id=get_text_box_theme("#cat_patrol_info_box")
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

        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")
        self.confirm_mentor = UIImageButton(scale(pygame.Rect((652, 620), (296, 60))), "", object_id="#confirm_mentor_button")
        if self.mentor is not None:
            self.current_mentor_warning = pygame_gui.elements.UITextBox("<font color=#FF0000>Current mentor selected</font>"
                                                                        , scale(pygame.Rect((600, 680), (400, 60))),
                                                                        object_id=get_text_box_theme(
                                                                            "#cat_patrol_info_box"), manager=MANAGER)
        else:
            self.current_mentor_warning = pygame_gui.elements.UITextBox("<font color=#FF0000>No mentor selected</font>"
                                                                        , scale(pygame.Rect((600, 680), (400, 60))),
                                                                        object_id=get_text_box_theme(
                                                                            "#cat_patrol_info_box"), manager=MANAGER)
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
        self.apprentice_details["apprentice_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((1200, 300), (300, 300))),
                                                                                  pygame.transform.scale(
                                                                                  self.the_cat.large_sprite,
                                                                                      (300, 300)),
                                                                                  manager=MANAGER)

        info = self.the_cat.age + "\n" + self.the_cat.status + "\n" + self.the_cat.genderalign + \
               "\n" + self.the_cat.trait + "\n" + self.the_cat.skill
        self.apprentice_details["apprentice_info"] = UITextBoxTweaked(
            info,
            scale(pygame.Rect((980, 340), (200, 200))),
            object_id="#cat_patrol_info_box",
            line_spacing=0.95, manager=MANAGER)

        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.apprentice_details["apprentice_name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (220, 60))),
            name,
            object_id="#header_text_box", manager=MANAGER)

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
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.mentor is not None \
                    and check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and check_cat.mentor is not None \
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

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((100, 300), (300, 300))),
                                                                                  pygame.transform.scale(
                                                                                  self.selected_mentor.large_sprite,
                                                                                      (300, 300)), manager=MANAGER)

            info = self.selected_mentor.age + "\n" + self.selected_mentor.status + "\n" + \
                self.selected_mentor.genderalign + "\n" + self.selected_mentor.trait + "\n" + \
                self.selected_mentor.skill
            if len(self.selected_mentor.former_apprentices) >= 1:
                info += f"\n{len(self.selected_mentor.former_apprentices)} former app(s)"
            if len(self.selected_mentor.apprentice) >= 1:
                info += f"\n{len(self.selected_mentor.apprentice)} current app(s)"
            self.selected_details["selected_info"] = UITextBoxTweaked(info,
                                                                    scale(pygame.Rect((420, 340), (210, 230))),
                                                                    object_id="#cat_patrol_info_box",
                                                                    line_spacing=0.95, manager=MANAGER)

            name = str(self.selected_mentor.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((130, 230), (220, 60))),
                name,
                object_id="#header_text_box", manager=MANAGER)

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
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                                                                   cat.big_sprite, cat_object=cat, manager=MANAGER)
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
        screen.blit(self.list_frame, (150/1600 * screen_x, 720/1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class ViewChildrenScreen(Screens):
    parents = pygame.transform.scale(pygame.image.load("resources/images/family_parents.png").convert_alpha(),
                                     (1288/1600 * screen_x, 460/1400 * screen_y))
    mate = pygame.transform.scale(pygame.image.load("resources/images/family_mate.png").convert_alpha(),
                                  (1280/1600 * screen_x, 460/1400 * screen_y))
    family_elements = {}
    offspring_elements = {}
    sibling_elements = {}

    all_siblings = []
    all_offspring = []

    # Page numbers for siblings and offspring
    siblings_page_number = 1
    offspring_page_number = 2

    def __init__(self, name=None):
        super().__init__(name)
        self.the_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
            elif event.ui_element == self.previous_sibling_page:
                self.siblings_page_number -= 1
                self.update_siblings_page()
            elif event.ui_element == self.next_sibling_page:
                self.siblings_page_number += 1
                self.update_siblings_page()
            elif event.ui_element == self.previous_offspring_page:
                self.offspring_page_number -= 1
                self.update_offspring_page()
            elif event.ui_element == self.next_offspring_page:
                self.offspring_page_number += 1
                self.update_offspring_page()
            elif event.ui_element in self.offspring_elements.values() or event.ui_element in self.sibling_elements.values() \
                    or event.ui_element in self.family_elements.values():
                game.switches['cat'] = event.ui_element.return_cat_id()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.change_screen('profile screen')
                else:
                    self.family_setup()
            elif event.ui_element == self.previous_cat_button:
                game.switches['cat'] = self.previous_cat
                self.family_setup()
            elif event.ui_element == self.next_cat_button:
                game.switches['cat'] = self.next_cat
                self.family_setup()

    def screen_switches(self):
        """Set up things that are always on the page"""

        cat_profiles()
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button", manager=MANAGER)
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 60), (306, 60))), "",
                                             object_id="#next_cat_button", manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)

        self.previous_sibling_page = UIImageButton(scale(pygame.Rect((800, 600), (68, 68))), "",
                                                   object_id="#relation_list_previous", manager=MANAGER)
        self.next_sibling_page = UIImageButton(scale(pygame.Rect((1000, 600), (68, 68))), "",
                                               object_id="#relation_list_next", manager=MANAGER)

        self.previous_offspring_page = UIImageButton(scale(pygame.Rect((800, 1160), (68, 68))), "",
                                                     object_id="#relation_list_previous", manager=MANAGER)
        self.next_offspring_page = UIImageButton(scale(pygame.Rect((1000, 1160), (68, 68))), "",
                                                 object_id="#relation_list_next", manager=MANAGER)

        self.family_setup()

    def exit_screen(self):
        for ele in self.family_elements:
            self.family_elements[ele].kill()
        self.family_elements = {}

        for ele in self.sibling_elements:
            self.sibling_elements[ele].kill()
        self.sibling_elements = {}

        for ele in self.offspring_elements:
            self.offspring_elements[ele].kill()
        self.offspring_elements = {}

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.previous_sibling_page.kill()
        del self.previous_sibling_page
        self.next_sibling_page.kill()
        del self.next_sibling_page
        self.previous_offspring_page.kill()
        del self.previous_offspring_page
        self.next_offspring_page.kill()
        del self.next_offspring_page

    def family_setup(self):
        for ele in self.family_elements:
            self.family_elements[ele].kill()
        self.family_elements = {}

        # Determine all the siblings and offspring.
        self.all_siblings = []
        self.all_offspring = []

        self.the_cat = Cat.all_cats[game.switches['cat']]

        # heading
        self.family_elements["header"] = pygame_gui.elements.UITextBox(f"Family of {self.the_cat.name}",
                                                                       scale(pygame.Rect((200, 56), (1200, 100))),
                                                                       object_id=get_text_box_theme("#header_text_box")
                                                                       , manager=MANAGER)

        # Draw parents
        # Parent 1
        if self.the_cat.parent1 is None:
            self.family_elements['parent1'] = pygame_gui.elements.UITextBox("Unknown", scale(pygame.Rect((180, 390), (120, 80))),
                                                                            object_id="#cat_patrol_info_box"
                                                                            , manager=MANAGER)
        elif self.the_cat.parent1 in Cat.all_cats:
            self.family_elements['parent1_image'] = UISpriteButton(scale(pygame.Rect((190, 290), (100, 100))),
                                                                   Cat.all_cats[self.the_cat.parent1].sprite,
                                                                   cat_id=self.the_cat.parent1, manager=MANAGER)
            if Cat.all_cats[self.the_cat.parent1].faded:
                #Disable the button for tagged, but not yet saved, faded cats
                self.family_elements['parent1_image'].disable()

            name = str(Cat.all_cats[self.the_cat.parent1].name)
            if len(name) >= 8:
                short_name = name[0:7]
                name = short_name + '..'
            self.family_elements["parent1_name"] = pygame_gui.elements.UITextBox(name,
                                                                                 scale(pygame.Rect((180, 390), (120, 60))),
                                                                                 object_id="#cat_patrol_info_box"
                                                                                 , manager=MANAGER)
        else:
            parent_ob = Cat.load_faded_cat(self.the_cat.parent1)
            if parent_ob:
                self.family_elements['parent1_image'] = UISpriteButton(scale(pygame.Rect((180, 290), (100, 100))),
                                                                       parent_ob.big_sprite, manager=MANAGER)
                self.family_elements["parent1_image"].disable() #There is no profile for faded cats.

                name = str(parent_ob.name)
                if 8 <= len(name) >= 8:
                    short_name = name[0:7]
                    name = short_name + '..'
                self.family_elements["parent1_name"] = pygame_gui.elements.UITextBox(name,
                                                                                     scale(pygame.Rect((180, 390), (120, 60))),
                                                                                     object_id="#cat_patrol_info_box"
                                                                                     , manager=MANAGER)
            else:
                self.family_elements["parent1"] = pygame_gui.elements.UITextBox(
                    f'Error: cat {self.the_cat.parent1} not found',
                    scale(pygame.Rect((90, 165), (60, 30))),
                    object_id="#cat_patrol_info_box", manager=MANAGER)

        # Parent 2
        if self.the_cat.parent2 is None:
            self.family_elements['parent2'] = pygame_gui.elements.UITextBox("Unknown", scale(pygame.Rect((180, 516), (120, 80))),
                                                                            object_id="#cat_patrol_info_box",
                                                                            manager=MANAGER)
        elif self.the_cat.parent2 in Cat.all_cats:
            self.family_elements['parent2_image'] = UISpriteButton(scale(pygame.Rect((190, 420), (100, 100))),
                                                                   Cat.all_cats[self.the_cat.parent2].big_sprite,
                                                                   cat_id=self.the_cat.parent2, manager=MANAGER)
            if Cat.all_cats[self.the_cat.parent2].faded:
                # Disable the button for tagged, but not yet saved, faded cats
                self.family_elements['parent2_image'].disable()

            name = str(Cat.all_cats[self.the_cat.parent2].name)
            if len(name) >= 8:
                short_name = name[0:7]
                name = short_name + '..'
            self.family_elements["parent2_name"] = pygame_gui.elements.UITextBox(name,
                                                                                 scale(pygame.Rect((180, 516), (120, 60))),
                                                                                 object_id="#cat_patrol_info_box"
                                                                                 , manager=MANAGER)
        else:
            # Check for faded parent
            parent_ob = Cat.load_faded_cat(self.the_cat.parent2)
            if parent_ob:
                self.family_elements['parent2_image'] = UISpriteButton(scale(pygame.Rect((190, 420), (100, 100))),
                                                                       parent_ob.big_sprite, manager=MANAGER)
                self.family_elements["parent2_image"].disable()  # There is no profile for faded cats.

                name = str(parent_ob.name)
                if len(name) >= 8:
                    short_name = name[0:7]
                    name = short_name + '..'
                self.family_elements["parent2_name"] = pygame_gui.elements.UITextBox(name,
                                                                                     scale(pygame.Rect((180, 516), (120, 60))),
                                                                                     object_id="#cat_patrol_info_box"
                                                                                     , manager=MANAGER)
            else:
                self.family_elements["parent2"] = pygame_gui.elements.UITextBox(
                    f'Error: cat {self.the_cat.parent2} not found',
                    scale(pygame.Rect((180, 500), (120, 60))),
                    object_id="#cat_patrol_info_box", manager=MANAGER)

        # Siblings
        # Get siblings.
        for x in game.clan.clan_cats:
            if (Cat.all_cats[x].parent1 in (self.the_cat.parent1, self.the_cat.parent2) or Cat.all_cats[
                x].parent2 in (
                        self.the_cat.parent1, self.the_cat.parent2) and self.the_cat.parent2 is not None) and \
                    self.the_cat.ID != Cat.all_cats[x].ID and self.the_cat.parent1 is not None and \
                    Cat.all_cats[x].parent1 is not None:
                self.all_siblings.append(Cat.all_cats[x])

        # Check for faded siblings through parent 1
        if self.the_cat.parent1 not in Cat.all_cats and self.the_cat.parent1:
            parent_ob = Cat.load_faded_cat(self.the_cat.parent1)
            if parent_ob:
                #Check to see if the faded offspring list is empty or not
                for sib in parent_ob.faded_offspring:
                    sib_ob = Cat.load_faded_cat(sib)
                    if sib:
                        self.all_siblings.append(sib_ob)

        #Check for siblings through parent 1, but we need to make sure we don't have duplicates.
        sibling_ids = [i.ID for i in self.all_siblings]

        if self.the_cat.parent2 not in Cat.all_cats and self.the_cat.parent2:
            parent_ob = Cat.load_faded_cat(self.the_cat.parent2)
            if parent_ob:
                for sib in parent_ob.faded_offspring:
                    if sib not in sibling_ids:
                        sib_ob = Cat.load_faded_cat(sib)
                        if sib:
                            self.all_siblings.append(sib_ob)


        self.siblings_page_number = 1  # Current sibling page
        self.all_siblings = self.chunks(self.all_siblings, 16)
        self.update_siblings_page()

        # MATE
        if self.the_cat.mate is None:
            self.family_elements["mate"] = pygame_gui.elements.UITextBox("Unknown", scale(pygame.Rect((180, 1016), (120, 80))),
                                                                         object_id="#cat_patrol_info_box")
        elif self.the_cat.mate in Cat.all_cats:
            self.family_elements["mate_image"] = UISpriteButton(scale(pygame.Rect((196, 916), (100, 100))),
                                                                Cat.all_cats[self.the_cat.mate].big_sprite,
                                                                cat_id=self.the_cat.mate, manager=MANAGER)

            name = str(Cat.all_cats[self.the_cat.mate].name)
            if len(name) >= 9:
                short_name = str(Cat.all_cats[self.the_cat.mate].name)[0:7]
                name = short_name + '...'
            self.family_elements["mate_name"] = pygame_gui.elements.UITextBox(name,
                                                                              scale(pygame.Rect((180, 1016), (120, 60))),
                                                                              object_id="#cat_patrol_info_box"
                                                                              , manager=MANAGER)

        else:
            print(f'ERROR: cat {self.the_cat.mate} not found')

        # OFFSPRING
        # Get offspring
        for x in game.clan.clan_cats:
            if self.the_cat.ID in [
                Cat.all_cats[x].parent1,
                Cat.all_cats[x].parent2
            ] and Cat.all_cats[x] not in self.all_offspring:
                self.all_offspring.append(Cat.all_cats[x])

        # Add faded offspring
        for cat in self.the_cat.faded_offspring:
            cat_ob = Cat.load_faded_cat(cat)
            if cat_ob and cat_ob not in self.all_offspring:
                self.all_offspring.append(cat_ob)

        self.offspring_page_number = 1  # Current sibling page
        self.all_offspring = self.chunks(self.all_offspring, 16)
        self.update_offspring_page()

        # Determine where the previous and next cat buttons lead, and disable if needed
        self.get_previous_next_cat()

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

    def update_siblings_page(self):
        """Updates the siblings page"""
        for ele in self.sibling_elements:
            self.sibling_elements[ele].kill()
        self.sibling_elements = {}

        if self.siblings_page_number > len(self.all_siblings):
            self.siblings_page_number = len(self.all_siblings)

        if self.all_siblings:
            display_cats = self.all_siblings[self.siblings_page_number - 1]
        else:
            display_cats = []

        pos_x = 458
        pos_y = 270
        i = 0
        for cat in display_cats:
            self.sibling_elements["sibling" + str(i)] = UISpriteButton(scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                                                                       cat.big_sprite,
                                                                       cat_id=cat.ID, manager=MANAGER)
            if cat.faded:
                self.sibling_elements["sibling" + str(i)].disable()

            name = str(cat.name)
            if len(name) >= 7:
                short_name = name[0:6]
                name = short_name + '..'
            self.sibling_elements["sibling_name" + str(i)] = pygame_gui.elements.UILabel(scale(pygame.Rect(
                                                                                               (pos_x - 5, pos_y + 100),
                                                                                               (110, 40))), name,
                                                                                           object_id="#cat_patrol_info_box"
                                                                                           , manager=MANAGER)

            pos_x += 120
            if pos_x > 1400:
                pos_y += 120
                pos_x = 458
            i += 1

        # Enable and disable page buttons.
        if len(self.all_siblings) <= 1:
            self.previous_sibling_page.disable()
            self.next_sibling_page.disable()
        elif self.siblings_page_number >= len(self.all_siblings):
            self.previous_sibling_page.enable()
            self.next_sibling_page.disable()
        elif self.siblings_page_number == 1 and len(self.all_siblings) > 1:
            self.previous_sibling_page.disable()
            self.next_sibling_page.enable()
        else:
            self.previous_sibling_page.enable()
            self.next_sibling_page.enable()

    def update_offspring_page(self):
        """Updates the offspring page"""
        for ele in self.offspring_elements:
            self.offspring_elements[ele].kill()
        self.offspring_elements = {}

        if self.offspring_page_number > len(self.all_offspring):
            self.offspring_page_number = len(self.all_offspring)

        if self.all_offspring:
            display_cats = self.all_offspring[self.offspring_page_number - 1]
        else:
            display_cats = []

        pos_x = 458
        pos_y = 830
        i = 0
        for cat in display_cats:
            self.offspring_elements["offspring" + str(i)] = UISpriteButton(scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                                                                           cat.big_sprite,
                                                                           cat_id=cat.ID, manager=MANAGER)
            if cat.faded:
                self.offspring_elements["offspring" + str(i)].disable()

            name = str(cat.name)
            if len(name) >= 7:
                short_name = name[0:6]
                name = short_name + '...'
            self.offspring_elements["offspring_name" + str(i)] = pygame_gui.elements.UILabel(scale(pygame.Rect(
                                                                                                   (pos_x - 5, pos_y + 100),
                                                                                                   (110, 40))), name,
                                                                                               object_id="#cat_patrol_info_box"
                                                                                               , manager=MANAGER)

            pos_x += 120
            if pos_x > 1400:
                pos_y += 140
                pos_x = 458
            i += 1

        # Enable and disable page buttons.
        if len(self.all_offspring) <= 1:
            self.previous_offspring_page.disable()
            self.next_offspring_page.disable()
        elif self.offspring_page_number >= len(self.all_offspring):
            self.previous_offspring_page.enable()
            self.next_offspring_page.disable()
        elif self.offspring_page_number == 1 and len(self.all_offspring) > 1:
            self.previous_offspring_page.disable()
            self.next_offspring_page.enable()
        else:
            self.previous_offspring_page.enable()
            self.next_offspring_page.enable()

    def on_use(self):
        screen.blit(ViewChildrenScreen.parents, (152/1600 * screen_x, 160/1400 * screen_y))
        screen.blit(ViewChildrenScreen.mate, (160/1600 * screen_x, 720/1400 * screen_y))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class ChooseMateScreen(Screens):
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300/1600 * screen_x, 452/1400 * screen_y))
    current_cat_elements = {}
    mate_elements = {}
    mate = None
    current_page = 1
    selected_cat = None

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

    def handle_event(self, event):
        """ Handles events. """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # Cat buttons list
            if event.ui_element in self.cat_list_buttons.values():
                if self.the_cat.mate is None:
                    self.selected_cat = event.ui_element.return_cat_object()
                    self.update_buttons()
                    self.update_choose_mate()
                else:
                    # if the cat already has a mate, then it lists offspring instead. Take to profile.
                    game.switches['cat'] = event.ui_element.return_cat_object().ID
                    self.change_screen("profile screen")
            # return to profile screen
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')

            if event.ui_element == self.toggle_mate:
                if self.the_cat.mate is None:
                    Cat.set_mate(self.the_cat, self.selected_cat)
                    Cat.set_mate(self.selected_cat, self.the_cat)
                    self.update_mate_screen()
                else:
                    Cat.unset_mate(self.the_cat, breakup=True)
                    Cat.unset_mate(self.selected_cat, breakup=True)
                    self.update_choose_mate(breakup=True)
                self.update_cat_list()
            elif event.ui_element == self.previous_cat_button:
                game.switches["cat"] = self.previous_cat
                self.update_current_cat_info()
                self.update_buttons()
            elif event.ui_element == self.next_cat_button:
                game.switches["cat"] = self.next_cat
                self.update_current_cat_info()
                self.update_buttons()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_list()
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_list()

    def screen_switches(self):
        """Sets up the elements that are always on the page"""
        self.info = UITextBoxTweaked("If the cat has chosen a mate, they will stay loyal and not have kittens "
                                     "with anyone else, even when having kittens in their relationship is "
                                     "impossible. However, their chance of having kittens is heightened, "
                                     "when possible. If affairs are toggled on, the cats may not be loyal "
                                     "in their relationships. ", scale(pygame.Rect((360, 120), (880, 200))),
                                     object_id=get_text_box_theme("#cat_patrol_info_box"), line_spacing=0.95)

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

        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

        self.previous_page_button = UIImageButton(scale(pygame.Rect((630, 1160), (68, 68))), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(scale(pygame.Rect((902, 1160), (68, 68))), "", object_id="#relation_list_next")
        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((698, 1160), (204, 68))),
                                                         object_id=get_text_box_theme())

        # This may be deleted and changed later.
        self.toggle_mate = UIImageButton(scale(pygame.Rect((646, 620), (306, 60))), "",
                                         object_id="#confirm_mate_button")

        # The text will be changed as needed. This is used for both the "this pair can't have
        # offspring" message, header for the kittens section for mated cats.
        self.kitten_message = pygame_gui.elements.UITextBox("", scale(pygame.Rect((200, 666), (1200, 80))),
                                                            object_id=get_text_box_theme())
        self.kitten_message.hide()

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

    def exit_screen(self):
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
            object_id=get_text_box_theme("#header_text_box"))

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((100, 300), (300, 300))),
                                                                         pygame.transform.scale(
                                                                         self.the_cat.large_sprite, (300, 300)))
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((130, 230), (240, 60))),
            name,
            object_id="#header_text_box")

        info = str(self.the_cat.moons) + " moons\n" + self.the_cat.status + "\n" + self.the_cat.genderalign + "\n" + \
               self.the_cat.trait
        self.current_cat_elements["info"] = UITextBoxTweaked(info, scale(pygame.Rect((410, 380), (200, 200))),
                                                             object_id="#cat_patrol_info_box",
                                                             line_spacing=0.95)

        # Determine what to draw regarding the othe cat. If they have a mate, set the screen up for that.
        # if they don't, set the screen up to choose a mate.
        if self.the_cat.mate is not None:
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

    def update_mate_screen(self):
        """Sets up the screen for a cat with a mate already."""
        for ele in self.mate_elements:
            self.mate_elements[ele].kill()
        self.mate_elements = {}

        self.selected_cat = Cat.all_cats[self.the_cat.mate]

        self.draw_compatible_line_affection()
        self.mate_elements["center_heart"] = pygame_gui.elements.UIImage(scale(pygame.Rect((600, 376), (400, 156))),
                                                                         pygame.transform.scale(
                                                                         image_cache.load_image(
                                                                             "resources/images/heart_mates.png").convert_alpha(),
                                                                             (400, 156)))

        self.mate_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((1200, 300), (300, 300))),
                                                                  pygame.transform.scale(
                                                                  self.selected_cat.large_sprite, (300, 300)))
        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.mate_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (220, 60))),
            name,
            object_id="#header_text_box")

        info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
               self.selected_cat.genderalign + "\n" + self.selected_cat.trait
        self.mate_elements["info"] = UITextBoxTweaked(info, scale(pygame.Rect((1000, 380), (200, 200))),
                                                      object_id="#cat_patrol_info_box",
                                                      line_spacing=0.95)

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

    def update_cat_list(self):
        # If the cat already has a mate, we display the children. If not, we display the possible mates
        all_pages = []
        if self.selected_cat and self.the_cat.mate:
            self.kittens = False
            for x in game.clan.clan_cats:
                if self.the_cat.ID in [
                    Cat.all_cats[x].parent1,
                    Cat.all_cats[x].parent2
                ] and self.selected_cat.ID in [
                    Cat.all_cats[x].parent1,
                    Cat.all_cats[x].parent2
                ]:
                    all_pages.append(Cat.all_cats[x])
                    self.kittens = True
        else:
            all_pages = self.get_valid_mates()

        all_pages = self.chunks(all_pages, 30)

        # If the number of pages becomes smaller than the number of our current page, set
        #   the current page to the last page
        if self.current_page > len(all_pages):
            self.list_page = len(all_pages)

        # Handle which next buttons are clickable.
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

        # Display the current page and total pages.
        total_pages = len(all_pages)
        if total_pages == 0:
            display_total_pages = 1
        else:
            display_total_pages = total_pages
        self.page_number.set_text(f"page {self.current_page} / {display_total_pages}")

        if total_pages != 0:
            display_cats = all_pages[self.current_page - 1]
        else:
            display_cats = []

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        pos_x = 0
        pos_y = 40
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(scale(pygame.Rect((200 + pos_x, 730 + pos_y), (100, 100))),
                                                                   cat.big_sprite, cat_object=cat)
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
                self.selected_cat.large_sprite, (300, 300)))

            name = str(self.selected_cat.name)
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.mate_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((1240, 230), (220, 60))),
                name,
                object_id="#header_text_box")

            info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n" + self.selected_cat.trait
            self.mate_elements["info"] = UITextBoxTweaked(info, scale(pygame.Rect((1000, 380), (200, 200))),
                                                          object_id="#cat_patrol_info_box",
                                                          line_spacing=0.95)
            # Display message

            pixel_font_size = int(22/1400 * screen_y)
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
            self.mate_elements["heart1" + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((x_pos, 570), (44, 40))),
                                                                                pygame.transform.scale(
                                                                                image_cache.load_image(
                                                                                    "resources/images/heart_big.png").convert_alpha(),
                                                                                    (44, 40)))
            x_pos += 54

        # Set romantic hearts of mate/selected cat towards current_cat.
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
                    check_cat.age not in ["adolescent", "kitten"] and check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and not check_cat.outside and \
                    check_cat.age not in ["adolescent", "kitten"] and check_cat.df == self.the_cat.df:
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def on_use(self):

        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150/1600 * screen_x, 720/1400 * screen_y))

    def get_valid_mates(self):
        """Get a list of valid mates for the current cat"""
        valid_mates = []
        for relevant_cat in Cat.all_cats_list:
            invalid_age = relevant_cat.age not in ['kitten', 'adolescent']

            # cat.is_potential_mate() is not used here becuase that restricts to the same age catagory, which we
            # don't want here.
            direct_related = self.the_cat.is_sibling(relevant_cat) or self.the_cat.is_parent(relevant_cat) \
                             or relevant_cat.is_parent(self.the_cat)
            indirect_related = self.the_cat.is_uncle_aunt(relevant_cat) or relevant_cat.is_uncle_aunt(self.the_cat)

            if not game.settings["first_cousin_mates"]:
                indirect_related = indirect_related or relevant_cat.is_cousin(self.the_cat)

            related = direct_related or indirect_related

            not_available = relevant_cat.dead or relevant_cat.outside

            if not related and relevant_cat.ID != self.the_cat.ID and invalid_age \
                    and not not_available and relevant_cat.mate is None:
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
        (456/1600 * screen_x, 78/1400 * screen_y)
    )
    details_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_details_frame.png").convert_alpha(), (508/1600 * screen_x,
                                                                                                    688/1400 * screen_y)
    )
    toggle_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_toggle_frame.png").convert_alpha(),
        (502/1600 * screen_x, 240/1400 * screen_y)
    )
    list_frame = pygame.transform.scale(
        image_cache.load_image("resources/images/relationship_list_frame.png").convert_alpha(),
        (1004/1600 * screen_x, 1000/1400 * screen_y)
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
                game.switches["cat"] = self.next_cat
                self.update_focus_cat()
            elif event.ui_element == self.previous_cat_button:
                game.switches["cat"] = self.previous_cat
                self.update_focus_cat()
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_cat_page()
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_cat_page()
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
        cat_profiles()

        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(scale(pygame.Rect((50, 1290), (210, 60))), "", object_id="#back_button")

        self.search_bar = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((1220, 194), (290, 46))),
                                                              object_id="#search_entry_box")

        self.show_dead_text = pygame_gui.elements.UITextBox("Show Dead", scale(pygame.Rect((200, 1010), (200, 60))),
                                                            object_id="#relation_list_name")
        self.show_empty_text = pygame_gui.elements.UITextBox("Show Empty", scale(pygame.Rect((200, 1100), (200, 60))),
                                                             object_id="#relation_list_name")
        # Draw the checkboxes
        self.update_checkboxes()

        self.previous_page_button = UIImageButton(scale(pygame.Rect((880, 1232), (68, 68))), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(scale(pygame.Rect((1160, 1232), (68, 68))), "", object_id="#relation_list_next")

        self.page_number = pygame_gui.elements.UITextBox("", scale(pygame.Rect((890, 1234), (300, 68))),
                                                         object_id=get_text_box_theme())

        self.switch_focus_button = UIImageButton(scale(pygame.Rect((170, 780), (272, 60))), "",
                                                 object_id="#switch_focus_button")
        self.switch_focus_button.disable()
        self.view_profile_button = UIImageButton(scale(pygame.Rect((170, 840), (272, 60))), "",
                                                 object_id="#view_profile_button")
        self.view_profile_button.disable()

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
                                                                          object_id=get_text_box_theme("#header_left"))
        self.focus_cat_elements["details"] = pygame_gui.elements.UITextBox(self.the_cat.genderalign + " - " + \
                                                                           str(self.the_cat.moons) + " moons - " + \
                                                                           self.the_cat.trait,
                                                                           scale(pygame.Rect((160, 210), (800, 60))),
                                                                           object_id=get_text_box_theme(
                                                                               "#cat_profile_info_box"))
        self.focus_cat_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((50, 150), (100, 100))),
                                                                       self.the_cat.big_sprite)

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
                object_id="#header_text_box")

            # Cat Image
            self.inspect_cat_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((150, 290), (300, 300))),
                                                                             pygame.transform.scale(
                                                                             self.inspect_cat.large_sprite,(300,300)))

            related = False
            # Mate Heart
            if self.the_cat.mate is not None and self.the_cat.mate != '' and self.inspect_cat.ID == self.the_cat.mate:
                self.inspect_cat_elements["mate"] = pygame_gui.elements.UIImage(scale(pygame.Rect((90, 300), (44, 40))),
                                                                                pygame.transform.scale(
                                                                                    image_cache.load_image(
                                                                                        "resources/images/heart_big.png").convert_alpha(),
                                                                                    (44, 40)))
            else:
                # Family Dot
                # Only show family dot on cousins if first cousin mates are disabled.
                if game.settings['first_cousin_mates']:
                    check_cousins = False
                else:
                    check_cousins = self.inspect_cat.is_cousin(self.the_cat)

                if self.inspect_cat.is_uncle_aunt(self.the_cat) or self.the_cat.is_uncle_aunt(self.inspect_cat) \
                        or self.inspect_cat.is_grandparent(self.the_cat) or \
                        self.the_cat.is_grandparent(self.inspect_cat) or \
                        self.inspect_cat.is_parent(self.the_cat) or \
                        self.the_cat.is_parent(self.inspect_cat) or \
                        self.inspect_cat.is_sibling(self.the_cat) or check_cousins:
                    related = True
                    self.inspect_cat_elements['family'] = pygame_gui.elements.UIImage(scale(pygame.Rect((90, 300), (36, 36))),
                                                                                      pygame.transform.scale(
                                                                                          image_cache.load_image(
                                                                                              "resources/images/dot_big.png").convert_alpha(),
                                                                                          (36,36)))



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

            self.inspect_cat_elements["col1"] = UITextBoxTweaked(col1, scale(pygame.Rect((120, 670), (160, -1))),
                                                                 object_id="#cat_profile_info_box",
                                                                 line_spacing=0.95)

            # Column Two Details:
            col2 = ""

            # Mate
            if self.inspect_cat.mate is not None and self.the_cat.ID != self.inspect_cat.mate:
                col2 += "has a mate\n"
            elif self.the_cat.mate is not None and self.the_cat.mate != '' and self.inspect_cat.ID == self.the_cat.mate:
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
                    col2 += "related: sibling"
                elif not game.settings["first_cousin_mates"] and self.inspect_cat.is_cousin(self.the_cat):
                    col2 += "related: cousin"

            self.inspect_cat_elements["col2"] = UITextBoxTweaked(col2, scale(pygame.Rect((300, 670), (170, -1))),
                                                                 object_id="#cat_profile_info_box",
                                                                 line_spacing=0.95)

            if self.inspect_cat.dead:
                self.view_profile_button.enable()
                self.switch_focus_button.disable()
            else:
                self.view_profile_button.enable()
                self.switch_focus_button.enable()
        else:
            self.view_profile_button.disable()
            self.switch_focus_button.disable()

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
                                                               the_relationship.cat_to.big_sprite,
                                                               cat_object=the_relationship.cat_to)

        # CHECK NAME LENGTH - SHORTEN IF NECESSARY
        name = str(the_relationship.cat_to.name)  # get name
        if 12 <= len(name) >= 13:  # check name length
            short_name = str(the_relationship.cat_to.name)[0:10]
            name = short_name + '...'
        self.relation_list_elements["name" + str(i)] = pygame_gui.elements.UITextBox(name, scale(pygame.Rect(
            (pos_x, pos_y - 48), (204, 60))),
            object_id="#relation_list_name")

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
        if self.the_cat.mate is not None and self.the_cat.mate != '' and the_relationship.cat_to.ID == self.the_cat.mate:

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

            if the_relationship.cat_to.is_uncle_aunt(self.the_cat) or self.the_cat.is_uncle_aunt(the_relationship.cat_to) \
                    or the_relationship.cat_to.is_grandparent(self.the_cat) or \
                    self.the_cat.is_grandparent(the_relationship.cat_to) or \
                    the_relationship.cat_to.is_parent(self.the_cat) or \
                    self.the_cat.is_parent(the_relationship.cat_to) or \
                    the_relationship.cat_to.is_sibling(self.the_cat) or check_cousins:
                related = True
                self.relation_list_elements['relation_icon' + str(i)] = pygame_gui.elements.UIImage(scale(pygame.Rect((pos_x + 10,
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
        adult_ages = ['young adult', 'adult', 'senior adult', 'elder']
        both_adult = the_relationship.cat_to.age in adult_ages and self.the_cat.age in adult_ages
        check_age = both_adult or same_age

        # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
        # even if they somehow have some. They should not be able to get any, but it never hurts to check.
        if not check_age or related:
            display_romantic = 0
            # Print, just for bug checking. Again, they should not be able to get love towards their relative.
            if the_relationship.romantic_love and related:
                print(f"WARNING: {self.the_cat.name} has {the_relationship.romantic_love} romantic love towards their relative, {the_relationship.cat_to.name}")
        else:
            display_romantic = the_relationship.romantic_love

        if display_romantic > 49:
            text = "romantic love:"
        else:
            text = "romantic like:"

        self.relation_list_elements[f'romantic_text{i}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
            (pos_x + 6, pos_y + 100 + (barbar * bar_count)),
            (160, 60))),
                                                                                         object_id="#cat_profile_info_box")
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
        self.relation_list_elements[f'plantonic_text{i}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect((pos_x + 6,
                                                                                                             pos_y + 100 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (160, 60))),
                                                                                          object_id="#cat_profile_info_box")
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
        self.relation_list_elements[f'dislike_text{i}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect((pos_x + 6,
                                                                                                             pos_y + 100 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (160, 60))),
                                                                                        object_id="#cat_profile_info_box")
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
        self.relation_list_elements[f'admiration_text{i}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect((pos_x + 6,
                                                                                                             pos_y + 100 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (160, 60))),
                                                                                           object_id="#cat_profile_info_box")
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
                                                                                            scale(pygame.Rect((pos_x + 6,
                                                                                                             pos_y + 100 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (160, 60))),
                                                                                            object_id="#cat_profile_info_box")
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
                                                                                                     pos_y + 100 + (
                                                                                                             barbar * bar_count)),
                                                                                                    (160, 60))),
                                                                                        object_id="#cat_profile_info_box")
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
                                                                                                 pos_y + 100 + (
                                                                                                         barbar * bar_count)),
                                                                                                (160, 60))),
                                                                                      object_id="#cat_profile_info_box")
        self.relation_list_elements[f'trust_bar{i}'] = UIRelationStatusBar(scale(pygame.Rect((pos_x + 6,
                                                                                           pos_y + 130 + (
                                                                                                   barbar * bar_count)),
                                                                                          (188, 20))),
                                                                           the_relationship.trust,
                                                                           positive_trait=True,
                                                                           dark_mode=game.settings['dark mode'])

    def on_use(self):

        # LOAD UI IMAGES
        screen.blit(RelationshipScreen.search_bar, (1070/1600 * screen_x, 180/1400 * screen_y))
        screen.blit(RelationshipScreen.details_frame, (50/1600 * screen_x, 260/1400 * screen_y))
        screen.blit(RelationshipScreen.toggle_frame, (90/1600 * screen_x, 958/1400 * screen_y))
        screen.blit(RelationshipScreen.list_frame, (546/1600 * screen_x, 244/1400 * screen_y))

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
                game.patrolled.append(self.mediators[self.selected_mediator].ID)
                output = Cat.mediate_relationship(
                    self.mediators[self.selected_mediator], self.selected_cat_1, self.selected_cat_2,
                    self.allow_romantic)
                self.results.set_text(output)
                self.update_selected_cats()
                self.update_mediator_info()
            elif event.ui_element == self.sabotoge_button:
                game.mediated.append(f"{self.selected_cat_1.ID}, {self.selected_cat_2.ID}")
                game.patrolled.append(self.mediators[self.selected_mediator].ID)
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
                                                                image_cache.load_image("resources/images/mediator_selected_frame.png"),
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
                                                                  object_id=get_text_box_theme("#cat_profile_info_box"),
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
        self.previous_page = UIImageButton(scale(pygame.Rect((666, 1224), (68, 68))), "", object_id="#relation_list_previous")

        self.deselect_1 = UIImageButton(scale(pygame.Rect((136, 868), (254, 60))), "",
                                                       object_id="#remove_cat_button")
        self.deselect_2 = UIImageButton(scale(pygame.Rect((1210, 868), (254, 60))), "",
                                                       object_id="#remove_cat_button")

        self.results = UITextBoxTweaked("", scale(pygame.Rect((560, 770), (458, 200))),
                                        object_id=get_text_box_theme("#cat_patrol_info_box"),
                                        line_spacing=0.75)

        self.error = UITextBoxTweaked("", scale(pygame.Rect((560, 100), (458, 100))),
                                        object_id=get_text_box_theme("#cat_patrol_info_box"),
                                        line_spacing=0.75)

        self.random1 = UIImageButton(scale(pygame.Rect((396, 864), (68, 68))), "", object_id="#random_dice_button")
        self.random2 = UIImageButton(scale(pygame.Rect((1136, 864), (68, 68))), "", object_id="#random_dice_button")

        self.update_buttons()
        self.update_mediator_info()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = list(filter(lambda x: x.ID not in self.selected_cat_list(), self.all_cats_list))
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_mediator_info(self):
        for ele in self.mediator_elements:
            self.mediator_elements[ele].kill()
        self.mediator_elements = {}

        if self.selected_mediator is not None: # It can be zero, so we must test for not None here.
            x_value = 630
            mediator = self.mediators[self.selected_mediator]

            # Clear mediator as selected cat
            if mediator == self.selected_cat_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            if mediator == self.selected_cat_2:
                self.selected_cat_2 = None
                self.update_selected_cats()

            self.mediator_elements["mediator_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((x_value, 180), (300, 300))),
                                                                                   pygame.transform.scale(
                                                                                   mediator.large_sprite, (300,300)))

            name = str(mediator.name)
            if len(name) > 17:
                name = name[:15] + "..."
            self.mediator_elements["name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((x_value - 10, 480), (320, -1))),
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

            self.mediator_elements["details"] = UITextBoxTweaked(text,
                                                                 scale(pygame.Rect((x_value, 540), (310, 100))),
                                                                 object_id=get_text_box_theme("#cat_patrol_info_box"),
                                                                 line_spacing=0.75)

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
        self.all_cats_list = list(filter(lambda x: (x.ID != self.mediators[self.selected_mediator].ID)
                                    and not x.dead and not x.outside, Cat.all_cats_list))
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
                UISpriteButton(scale(pygame.Rect((x, y), (100, 100))), cat.big_sprite, cat_object=cat)
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

        self.selected_cat_elements["cat_image" + tag] = pygame_gui.elements.UIImage(scale(pygame.Rect((x + 100, y + 14), (200, 200))),
                                                                                    pygame.transform.scale(
                                                                                    cat.big_sprite, (200, 200)))

        name = str(cat.name)
        if len(name) > 17:
            name = name[:15] + "..."
        self.selected_cat_elements["name" + tag] = pygame_gui.elements.UILabel(scale(pygame.Rect((x, y + 200), (400, 60))),
                                                                               name,
                                                                               object_id="text_box")

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

        self.selected_cat_elements["gender" + tag] = pygame_gui.elements.UIImage(scale(pygame.Rect((x + 320, y + 24), (50, 50))),
                                                                                 pygame.transform.scale(gender_icon,
                                                                                                        (50, 50)))

        related = False
        # MATE
        if other_cat and cat.mate and cat.mate == other_cat.ID:
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
        col1 += "\n" + cat.trait
        self.selected_cat_elements["col1" + tag] = UITextBoxTweaked(col1, scale(pygame.Rect((x + 42, y + 252), (160, -1))),
                                                                    object_id="#cat_profile_info_box",
                                                                    line_spacing=0.75)

        mates = False
        if cat.mate:
            col2 = "has a mate"
            if other_cat:
                if cat.mate == other_cat.ID:
                    mates = True
                    col2 = f"{Cat.fetch_cat(cat.mate).name}'s mate"
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

        self.selected_cat_elements["col2" + tag] = UITextBoxTweaked(col2, scale(pygame.Rect((x + 220, y + 252), (161, -1))),
                                                                    object_id="#cat_profile_info_box",
                                                                    line_spacing=0.75)

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        if other_cat:


            name = str(cat.name)
            if len(name) > 13:
                name = name[:10] + ".."
            self.selected_cat_elements[f"relation_heading{tag}"] = pygame_gui.elements.UILabel(scale(pygame.Rect((x + 40, y + 314),
                                                                                                           (320, -1))),
                                                                                               f"~~{name}'s feelings~~",
                                                                                               object_id="#cat_patrol_info_box")

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
            adult_ages = ['young adult', 'adult', 'senior adult', 'elder']
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
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
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
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
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
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
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
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
            self.selected_cat_elements[f'admiration_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                  y + y_start + 30 + (
                                                                                                          barbar * bar_count)),
                                                                                                 (300, 18))),
                                                                                    the_relationship.admiration,
                                                                                    positive_trait=True,
                                                                                    dark_mode=game.settings['dark mode'])

            bar_count += 1

            # COMFORTABLE
            if the_relationship.comfortable > 49:
                text = "secure:"
            else:
                text = "comfortable:"
            self.selected_cat_elements[f'comfortable_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
            self.selected_cat_elements[f'comfortable_bar{tag}'] = UIRelationStatusBar(scale(pygame.Rect((x + x_start,
                                                                                                   y + y_start + 30 + (
                                                                                                           barbar * bar_count)),
                                                                                                  (300, 18))),
                                                                                     the_relationship.comfortable,
                                                                                     positive_trait=True,
                                                                                     dark_mode=game.settings['dark mode'])

            bar_count += 1

            # JEALOUS
            if the_relationship.jealousy > 49:
                text = "resentment:"
            else:
                text = "jealousy:"
            self.selected_cat_elements[f'jealous_text{tag}'] = pygame_gui.elements.UITextBox(text, scale(pygame.Rect(
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
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
                                                                                              (x + x_start, y + y_start + (barbar * bar_count)),
                                                                                              (300, 60))),
                                                                                              object_id="#cat_profile_info_box")
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
            elif self.mediators[self.selected_mediator].ID in game.patrolled:
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
            self.romantic_checkbox = UIImageButton(scale(pygame.Rect((642, 635),(68, 68))), "",
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
