from math import ceil

import pygame
import pygame_gui.elements

from .base_screens import Screens, cat_profiles

from scripts.utility import draw_large, draw, update_sprite, get_personality_compatibility, get_text_box_theme
# from scripts.game_structure.text import *
from scripts.cat.cats import Cat
import scripts.game_structure.image_cache as image_cache
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton, UIRelationStatusBar
from scripts.game_structure.game_essentials import *


class ChooseMentorScreen(Screens):
    selected_mentor = None
    current_page = 1
    list_frame = image_cache.load_image("resources/images/choosing_frame.png").convert_alpha()
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
        self.mentor = self.the_cat.mentor

        self.heading = pygame_gui.elements.UITextBox("Choose a new mentor for " + str(self.the_cat.name),
                                                     pygame.Rect((150, 25), (500, 40)),
                                                     object_id=get_text_box_theme("#header_text_box"))
        self.info = UITextBoxTweaked("If an apprentice is 6 moons old and their mentor is changed, they "
                                     "will not be listed as a former apprentice on their old mentor's "
                                     "profile. An apprentices mentor can have an influence on their "
                                     "trait and skill later in life.\nChoose your mentors wisely",
                                     pygame.Rect((180, 60), (440, 100)), line_spacing=0.95,
                                     object_id=get_text_box_theme("#cat_patrol_info_box"))
        if self.mentor is not None:
            self.current_mentor_text = pygame_gui.elements.UITextBox(f"{str(self.the_cat.name)}'s current mentor is "
                                                                    f"{str(self.mentor.name)}",
                                                                    pygame.Rect((230, 130), (340, 30)),
                                                                    object_id=get_text_box_theme("#cat_patrol_info_box"))
        else:
            self.current_mentor_text = pygame_gui.elements.UITextBox(f"{str(self.the_cat.name)} does not have a mentor",
                                                                    pygame.Rect((230, 130), (340, 30)),
                                                                    object_id=get_text_box_theme("#cat_patrol_info_box"))

        # Layout Images:
        self.mentor_frame = pygame_gui.elements.UIImage(pygame.Rect((40, 113), (281, 197)),
                                                        image_cache.load_image(
                                                            "resources/images/choosing_cat1_frame_ment.png").convert_alpha())
        self.app_frame = pygame_gui.elements.UIImage(pygame.Rect((480, 113), (281, 197)),
                                                     image_cache.load_image(
                                                         "resources/images/choosing_cat2_frame_ment.png").convert_alpha())

        self.mentor_icon = pygame_gui.elements.UIImage(pygame.Rect((315, 160), (171, 114)),
                                                       image_cache.load_image(
                                                           "resources/images/mentor.png").convert_alpha())

        self.previous_cat_button = UIImageButton(pygame.Rect((25, 25), (153, 30)), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(pygame.Rect((622, 25), (153, 30)), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(pygame.Rect((25, 645), (105, 30)), "", object_id="#back_button")
        self.confirm_mentor = UIImageButton(pygame.Rect((326, 310), (148, 30)), "", object_id="#confirm_mentor_button")
        if (self.mentor is not None):
            self.current_mentor_warning = pygame_gui.elements.UITextBox("<font color=#FF0000>Current mentor selected</font>"
                                                                        , pygame.Rect((300, 340), (200, 30)),
                                                                        object_id=get_text_box_theme(
                                                                            "#cat_patrol_info_box"))
        else:
            self.current_mentor_warning = pygame_gui.elements.UITextBox("<font color=#FF0000>No mentor selected</font>"
                                                                        , pygame.Rect((300, 340), (200, 30)),
                                                                        object_id=get_text_box_theme(
                                                                            "#cat_patrol_info_box"))
        self.previous_page_button = UIImageButton(pygame.Rect((315, 580), (34, 34)), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(pygame.Rect((451, 580), (34, 34)), "", object_id="#relation_list_next")

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
        self.selected_mentor = self.the_cat.mentor

        self.heading.set_text(f"Choose a new mentor for {str(self.the_cat.name)}")
        if self.the_cat.mentor is not None:
            self.current_mentor_text.set_text(
                f"{str(self.the_cat.name)}'s current mentor is {str(self.the_cat.mentor.name)}")
        else:
            self.current_mentor_text.set_text(
                f"{str(self.the_cat.name)} does not have a mentor")
        self.apprentice_details["apprentice_image"] = pygame_gui.elements.UIImage(pygame.Rect((600, 150), (150, 150)),
                                                                                  self.the_cat.large_sprite)

        info = self.the_cat.age + "\n" + self.the_cat.status + "\n" + self.the_cat.genderalign + \
               "\n" + self.the_cat.trait + "\n" + self.the_cat.skill
        self.apprentice_details["apprentice_info"] = UITextBoxTweaked(
            info,
            pygame.Rect((490, 170), (100, 100)),
            object_id="#cat_patrol_info_box",
            line_spacing=0.95)

        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.apprentice_details["apprentice_name"] = pygame_gui.elements.ui_label.UILabel(
            pygame.Rect((620, 115), (110, 30)),
            name,
            object_id="#header_text_box")

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

        for check_cat in Cat.all_cats:
            if Cat.all_cats[check_cat].ID == self.the_cat.ID:
                self.next_cat = 1

            if self.next_cat == 0 and Cat.all_cats[
                check_cat].ID != self.the_cat.ID and Cat.all_cats[
                check_cat].dead == self.the_cat.dead and Cat.all_cats[
                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                check_cat].exiled and Cat.all_cats[check_cat].mentor is not None and Cat.all_cats[
                check_cat].df == self.the_cat.df:
                self.previous_cat = Cat.all_cats[check_cat].ID

            elif self.next_cat == 1 and Cat.all_cats[
                check_cat].ID != self.the_cat.ID and Cat.all_cats[
                check_cat].dead == self.the_cat.dead and Cat.all_cats[
                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                check_cat].exiled and Cat.all_cats[check_cat].mentor is not None and Cat.all_cats[
                check_cat].df == self.the_cat.df:
                self.next_cat = Cat.all_cats[check_cat].ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def change_mentor(self, new_mentor=None):
        if new_mentor and self.the_cat.mentor is not None:
            self.the_cat.mentor.apprentice.remove(self.the_cat)
            if self.the_cat.moons > 6:
                self.the_cat.mentor.former_apprentices.append(self.the_cat)

            self.the_cat.patrol_with_mentor = 0
            self.the_cat.mentor = new_mentor
            new_mentor.apprentice.append(self.the_cat)
            self.mentor = self.the_cat.mentor
            if (self.mentor is not None):
                self.current_mentor_text.set_text(
                    f"{str(self.the_cat.name)}'s current mentor is {str(self.the_cat.mentor.name)}")
            else:
                self.current_mentor_text.set_text(
                f"{str(self.the_cat.name)} does not have a mentor")

    def update_selected_cat(self):
        """Updates the image and information on the currently selected mentor"""
        for ele in self.selected_details:
            self.selected_details[ele].kill()
        self.selected_details = {}
        if (self.selected_mentor is not None):

            self.selected_details["selected_image"] = pygame_gui.elements.UIImage(pygame.Rect((50, 150), (150, 150)),
                                                                                self.selected_mentor.large_sprite)

            info = self.selected_mentor.age + "\n" + self.selected_mentor.status + "\n" + \
                self.selected_mentor.genderalign + "\n" + self.selected_mentor.trait + "\n" + \
                self.selected_mentor.skill
            if len(self.selected_mentor.former_apprentices) >= 1:
                info += f"\n{len(self.selected_mentor.former_apprentices)} former app(s)"
            if len(self.selected_mentor.apprentice) >= 1:
                info += f"\n{len(self.selected_mentor.apprentice)} current app(s)"
            self.selected_details["selected_info"] = UITextBoxTweaked(info,
                                                                    pygame.Rect((210, 170), (105, 115)),
                                                                    object_id="#cat_patrol_info_box",
                                                                    line_spacing=0.95)

            name = str(self.selected_mentor.name)  # get name
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.selected_details["mentor_name"] = pygame_gui.elements.ui_label.UILabel(
                pygame.Rect((65, 115), (110, 30)),
                name,
                object_id="#header_text_box")

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
        pos_y = 20
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(pygame.Rect((100 + pos_x, 365 + pos_y), (50, 50)),
                                                                   cat.sprite, cat_object=cat)
            pos_x += 60
            if pos_x >= 550:
                pos_x = 0
                pos_y += 60
            i += 1

    def update_buttons(self):
        """Updates the status of buttons. """
        # Disable to enable the choose mentor button
        if self.selected_mentor == self.the_cat.mentor or not self.selected_mentor:
            self.confirm_mentor.disable()
            self.current_mentor_warning.show()
        else:
            self.confirm_mentor.enable()
            self.current_mentor_warning.hide()

    def get_valid_mentors(self):
        valid_mentors = []

        if self.the_cat.status == "apprentice":
            for cat in Cat.all_cats.values():
                if not cat.dead and not cat.outside and cat.status in [
                            'warrior', 'deputy', 'leader'
                        ]:
                    valid_mentors.append(cat)
        elif self.the_cat.status == "medicine cat apprentice":
            for cat in Cat.all_cats.values():
                if not cat.dead and not cat.outside and cat.status == 'medicine cat':
                    valid_mentors.append(cat)

        return valid_mentors

    def on_use(self):
        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (75, 360))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class ViewChildrenScreen(Screens):
    parents = pygame.image.load("resources/images/family_parents.png").convert_alpha()
    mate = pygame.image.load("resources/images/family_mate.png").convert_alpha()
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
                self.change_screen("profile screen")
            elif event.ui_element == self.previous_cat_button:
                game.switches['cat'] = self.previous_cat
                self.family_setup()
            elif event.ui_element == self.next_cat_button:
                game.switches['cat'] = self.next_cat
                self.family_setup()

    def screen_switches(self):
        """Set up things that are always on the page"""

        cat_profiles()
        self.previous_cat_button = UIImageButton(pygame.Rect((25, 25), (153, 30)), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(pygame.Rect((622, 25), (153, 30)), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(pygame.Rect((25, 645), (105, 30)), "", object_id="#back_button")

        self.previous_sibling_page = UIImageButton(pygame.Rect((400, 300), (34, 34)), "",
                                                   object_id="#relation_list_previous")
        self.next_sibling_page = UIImageButton(pygame.Rect((500, 300), (34, 34)), "",
                                               object_id="#relation_list_next")

        self.previous_offspring_page = UIImageButton(pygame.Rect((400, 580), (34, 34)), "",
                                                     object_id="#relation_list_previous")
        self.next_offspring_page = UIImageButton(pygame.Rect((500, 580), (34, 34)), "",
                                                 object_id="#relation_list_next")

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
                                                                       pygame.Rect((100, 28), (600, 50)),
                                                                       object_id=get_text_box_theme("#header_text_box"))

        # Draw parents
        # Parent 1
        if self.the_cat.parent1 is None:
            self.family_elements['parent1'] = pygame_gui.elements.UITextBox("Unknown", pygame.Rect((90, 195), (60, 40)),
                                                                            object_id="#cat_patrol_info_box")
        elif self.the_cat.parent1 in Cat.all_cats:
            self.family_elements['parent1_image'] = UISpriteButton(pygame.Rect((95, 145), (50, 50)),
                                                                   Cat.all_cats[self.the_cat.parent1].sprite,
                                                                   cat_id=self.the_cat.parent1)
            if Cat.all_cats[self.the_cat.parent1].faded:
                #Disable the button for tagged, but not yet saved, faded cats
                self.family_elements['parent1_image'].disable()

            name = str(Cat.all_cats[self.the_cat.parent1].name)
            if 8 <= len(name) >= 10:
                short_name = str(Cat.all_cats[self.the_cat.parent1].name)[0:7]
                name = short_name + '...'
            self.family_elements["parent1_name"] = pygame_gui.elements.UITextBox(name,
                                                                                 pygame.Rect((90, 195), (60, 30)),
                                                                                 object_id="#cat_patrol_info_box")
        else:
            parent_ob = Cat.load_faded_cat(self.the_cat.parent1)
            if parent_ob:
                self.family_elements['parent1_image'] = UISpriteButton(pygame.Rect((95, 145), (50, 50)),
                                                                       parent_ob.sprite)
                self.family_elements["parent1_image"].disable() #There is no profile for faded cats.

                name = str(parent_ob.name)
                if 8 <= len(name) >= 10:
                    short_name = str(parent_ob.name)[0:7]
                    name = short_name + '...'
                self.family_elements["parent1_name"] = pygame_gui.elements.UITextBox(name,
                                                                                     pygame.Rect((90, 195), (60, 30)),
                                                                                     object_id="#cat_patrol_info_box")
            else:
                self.family_elements["parent1"] = pygame_gui.elements.UITextBox(
                    f'Error: cat {str(self.the_cat.parent1)} not found',
                    pygame.Rect((90, 165), (60, 30)),
                    object_id="#cat_patrol_info_box")

        # Parent 2
        if self.the_cat.parent2 is None:
            self.family_elements['parent2'] = pygame_gui.elements.UITextBox("Unknown", pygame.Rect((90, 258), (60, 40)),
                                                                            object_id="#cat_patrol_info_box")
        elif self.the_cat.parent2 in Cat.all_cats:
            self.family_elements['parent2_image'] = UISpriteButton(pygame.Rect((95, 210), (50, 50)),
                                                                   Cat.all_cats[self.the_cat.parent2].sprite,
                                                                   cat_id=self.the_cat.parent2)
            if Cat.all_cats[self.the_cat.parent2].faded:
                # Disable the button for tagged, but not yet saved, faded cats
                self.family_elements['parent2_image'].disable()

            name = str(Cat.all_cats[self.the_cat.parent2].name)
            if 8 <= len(name) >= 10:
                short_name = str(Cat.all_cats[self.the_cat.parent2].name)[0:7]
                name = short_name + '...'
            self.family_elements["parent2_name"] = pygame_gui.elements.UITextBox(name,
                                                                                 pygame.Rect((90, 258), (60, 30)),
                                                                                 object_id="#cat_patrol_info_box")
        else:
            # Check for faded parent
            parent_ob = Cat.load_faded_cat(self.the_cat.parent2)
            if parent_ob:
                self.family_elements['parent2_image'] = UISpriteButton(pygame.Rect((95, 210), (50, 50)),
                                                                       parent_ob.sprite)
                self.family_elements["parent2_image"].disable()  # There is no profile for faded cats.

                name = str(parent_ob.name)
                if 8 <= len(name) >= 10:
                    short_name = str(parent_ob.name)[0:7]
                    name = short_name + '...'
                self.family_elements["parent2_name"] = pygame_gui.elements.UITextBox(name,
                                                                                     pygame.Rect((90, 258), (60, 30)),
                                                                                     object_id="#cat_patrol_info_box")
            else:
                self.family_elements["parent2"] = pygame_gui.elements.UITextBox(
                    f'Error: cat {str(self.the_cat.parent2)} not found',
                    pygame.Rect((90, 250), (60, 30)),
                    object_id="#cat_patrol_info_box")

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
            self.family_elements["mate"] = pygame_gui.elements.UITextBox("Unknown", pygame.Rect((93, 508), (60, 40)),
                                                                         object_id="#cat_patrol_info_box")
        elif self.the_cat.mate in Cat.all_cats:
            self.family_elements["mate_image"] = UISpriteButton(pygame.Rect((98, 458), (50, 50)),
                                                                Cat.all_cats[self.the_cat.mate].sprite,
                                                                cat_id=self.the_cat.mate)

            name = str(Cat.all_cats[self.the_cat.mate].name)
            if 8 <= len(name) >= 10:
                short_name = str(Cat.all_cats[self.the_cat.mate].name)[0:7]
                name = short_name + '...'
            self.family_elements["mate_name"] = pygame_gui.elements.UITextBox(name,
                                                                              pygame.Rect((90, 508), (60, 30)),
                                                                              object_id="#cat_patrol_info_box")

        else:
            print(f'Error: cat {str(self.the_cat.mate)} not found',
                  (342, 165))

        # OFFSPRING
        # Get offspring
        for x in game.clan.clan_cats:
            if self.the_cat.ID in [
                Cat.all_cats[x].parent1,
                Cat.all_cats[x].parent2
            ]:
                self.all_offspring.append(Cat.all_cats[x])

        # Add faded offspring
        for cat in self.the_cat.faded_offspring:
            cat_ob = Cat.load_faded_cat(cat)
            if cat_ob:
                self.all_offspring.append(cat_ob)

        self.offspring_page_number = 1  # Current sibling page
        self.all_offspring = self.chunks(self.all_offspring, 16)
        self.update_offspring_page()

        # Determine where the previous and next cat buttons lead, and disable if needed
        self.get_previous_next_cat()

    def get_previous_next_cat(self):
        """Determines where the previous the next buttons should lead, and enables/diables them"""
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats:
            if Cat.all_cats[check_cat].ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and Cat.all_cats[
                        check_cat].ID != self.the_cat.ID and Cat.all_cats[
                        check_cat].dead == self.the_cat.dead and Cat.all_cats[
                        check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                        check_cat].exiled and Cat.all_cats[
                        check_cat].df == self.the_cat.df and not Cat.all_cats[check_cat].faded:
                    previous_cat = Cat.all_cats[check_cat].ID

                elif next_cat == 1 and Cat.all_cats[
                        check_cat].ID != self.the_cat.ID and Cat.all_cats[
                        check_cat].dead == self.the_cat.dead and Cat.all_cats[
                        check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                        check_cat].exiled and Cat.all_cats[
                        check_cat].df == self.the_cat.df and not Cat.all_cats[check_cat].faded:
                    next_cat = Cat.all_cats[check_cat].ID

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

        pos_x = 229
        pos_y = 135
        i = 0
        for cat in display_cats:
            self.sibling_elements["sibling" + str(i)] = UISpriteButton(pygame.Rect((pos_x, pos_y), (50, 50)),
                                                                       cat.sprite,
                                                                       cat_id=cat.ID)
            if cat.faded:
                self.sibling_elements["sibling" + str(i)].disable()

            name = str(cat.name)
            if 6 <= len(name) >= 9:
                short_name = str(cat.name)[0:5]
                name = short_name + '...'
            self.sibling_elements["sibling_name" + str(i)] = pygame_gui.elements.UITextBox(name,
                                                                                           pygame.Rect(
                                                                                               (pos_x, pos_y + 50),
                                                                                               (60, 20)),
                                                                                           object_id="#cat_patrol_info_box")
            pos_x += 60
            if pos_x > 700:
                pos_y += 70
                pos_x = 229
            i += 1

        # Enable and disable page buttons.
        if len(self.all_siblings) <= 1:
            self.previous_sibling_page.disable()
            self.next_sibling_page.disable()
        elif self.sibling_page_number >= len(self.all_siblings):
            self.previous_sibling_page.enable()
            self.next_sibling_page.disable()
        elif self.sibling_page_number == 1 and len(self.all_siblings) > 1:
            self.previous_sibling_page.disable()
            self.next_sibling_page.enable()
        else:
            self.previous_offspring_page.enable()
            self.next_offspring_page.enable()

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

        pos_x = 229
        pos_y = 415
        i = 0
        for cat in display_cats:
            self.offspring_elements["offspring" + str(i)] = UISpriteButton(pygame.Rect((pos_x, pos_y), (50, 50)),
                                                                           cat.sprite,
                                                                           cat_id=cat.ID)
            if cat.faded:
                self.offspring_elements["offspring" + str(i)].disable()

            name = str(cat.name)
            if 6 <= len(name) >= 9:
                short_name = str(cat.name)[0:5]
                name = short_name + '...'
            self.offspring_elements["offspring_name" + str(i)] = pygame_gui.elements.UITextBox(name,
                                                                                               pygame.Rect(
                                                                                                   (pos_x, pos_y + 50),
                                                                                                   (60, 20)),
                                                                                               object_id="#cat_profile_info_box")
            pos_x += 60
            if pos_x > 700:
                pos_y += 70
                pos_x = 229
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
        screen.blit(ViewChildrenScreen.parents, (76, 80))
        screen.blit(ViewChildrenScreen.mate, (80, 360))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]


class ChooseMateScreen(Screens):
    list_frame = image_cache.load_image("resources/images/choosing_frame.png").convert_alpha()
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
                    self.selected_cat.mate = None
                    self.the_cat.mate = None
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
                                     "with anyone else, when if having kittens in their relationship is "
                                     "impossible. However, their change of having kittens if heightened, "
                                     "when possible. If affairs are toggled on, the cats may not be loyal "
                                     "in their relationships. ", pygame.Rect((180, 60), (440, 100)),
                                     object_id=get_text_box_theme("#cat_patrol_info_box"), line_spacing=0.95)

        self.the_cat_frame = pygame_gui.elements.UIImage(pygame.Rect((40, 113), (266, 197)),
                                                         image_cache.load_image(
                                                             "resources/images/choosing_cat1_frame_mate.png").convert_alpha())
        self.mate_frame = pygame_gui.elements.UIImage(pygame.Rect((494, 113), (266, 197)),
                                                      image_cache.load_image(
                                                          "resources/images/choosing_cat2_frame_mate.png").convert_alpha())

        self.previous_cat_button = UIImageButton(pygame.Rect((25, 25), (153, 30)), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(pygame.Rect((622, 25), (153, 30)), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(pygame.Rect((25, 645), (105, 30)), "", object_id="#back_button")

        self.previous_page_button = UIImageButton(pygame.Rect((315, 580), (34, 34)), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(pygame.Rect((451, 580), (34, 34)), "", object_id="#relation_list_next")
        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((349, 580), (102, 34)),
                                                         object_id=get_text_box_theme())

        # This may be deleted and changed later.
        self.toggle_mate = UIImageButton(pygame.Rect((323, 310), (153, 30)), "",
                                         object_id="#confirm_mate_button")

        # The text will be changed as needed. This is used for both the "this pair can't have
        # offspring" message, header for the kittens section for mated cats.
        self.kitten_message = pygame_gui.elements.UITextBox("", pygame.Rect((100, 333), (600, 40)),
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
            pygame.Rect((150, 25), (500, 40)),
            object_id=get_text_box_theme("#header_text_box"))

        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(pygame.Rect((50, 150), (150, 150)),
                                                                         self.the_cat.large_sprite)
        name = str(self.the_cat.name)  # get name
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.current_cat_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            pygame.Rect((65, 115), (120, 30)),
            name,
            object_id="#header_text_box")

        info = str(self.the_cat.moons) + " moons\n" + self.the_cat.status + "\n" + self.the_cat.genderalign + "\n" + \
               self.the_cat.trait
        self.current_cat_elements["info"] = UITextBoxTweaked(info, pygame.Rect((205, 190), (100, 100)),
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
        self.mate_elements["center_heart"] = pygame_gui.elements.UIImage(pygame.Rect((300, 188), (200, 78)),
                                                                         image_cache.load_image(
                                                                             "resources/images/heart_mates.png").convert_alpha())

        self.mate_elements["image"] = pygame_gui.elements.UIImage(pygame.Rect((600, 150), (150, 150)),
                                                                  self.selected_cat.large_sprite)
        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.mate_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            pygame.Rect((620, 115), (110, 30)),
            name,
            object_id="#header_text_box")

        info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
               self.selected_cat.genderalign + "\n" + self.selected_cat.trait
        self.mate_elements["info"] = UITextBoxTweaked(info, pygame.Rect((500, 190), (100, 100)),
                                                      object_id="#cat_patrol_info_box",
                                                      line_spacing=0.95)

        # Set the button to say "break-up"
        self.toggle_mate.kill()
        self.toggle_mate = UIImageButton(pygame.Rect((323, 310), (153, 30)), "", object_id="#break_up_button")

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
        pos_y = 20
        i = 0
        for cat in display_cats:
            self.cat_list_buttons["cat" + str(i)] = UISpriteButton(pygame.Rect((100 + pos_x, 365 + pos_y), (50, 50)),
                                                                   cat.sprite, cat_object=cat)
            pos_x += 60
            if pos_x >= 550:
                pos_x = 0
                pos_y += 60
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
                    pygame.Rect((300, 188), (200, 78)),
                    image_cache.load_image(
                        "resources/images/heart_breakup.png").convert_alpha())
            else:
                self.mate_elements["center_heart"] = pygame_gui.elements.UIImage(
                    pygame.Rect((300, 188), (200, 78)),
                    image_cache.load_image(
                        "resources/images/heart_maybe.png").convert_alpha())
            self.mate_elements["image"] = pygame_gui.elements.UIImage(
                pygame.Rect((600, 150), (150, 150)),
                self.selected_cat.large_sprite)

            name = str(self.selected_cat.name)
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.mate_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                pygame.Rect((620, 115), (110, 30)),
                name,
                object_id="#header_text_box")

            info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n" + self.selected_cat.trait
            self.mate_elements["info"] = UITextBoxTweaked(info, pygame.Rect((500, 190), (100, 100)),
                                                          object_id="#cat_patrol_info_box",
                                                          line_spacing=0.95)
            # Display message
            if self.the_cat.gender == self.selected_cat.gender and not game.settings[
                'no gendered breeding']:
                self.kitten_message.set_text(
                    "<font pixel_size=11> (this pair will not be able to have kittens) </font>")
                self.kitten_message.show()
            else:
                self.kitten_message.hide()
        else:
            self.kitten_message.hide()

        self.update_cat_list()

        self.toggle_mate.kill()
        self.toggle_mate = UIImageButton(pygame.Rect((323, 310), (153, 30)), "",
                                         object_id="#confirm_mate_button")

        self.update_buttons()

    def draw_compatible_line_affection(self):
        """Draws the heart-line based on capability, and draws the hearts based on romantic love. """

        # Set the lines
        self.mate_elements["compat_line"] = pygame_gui.elements.UIImage(pygame.Rect((300, 190), (200, 78)),
                                                                        image_cache.load_image(
                                                                            "resources/images/line_neutral.png").convert_alpha())
        if get_personality_compatibility(self.the_cat, self.selected_cat) is True:
            self.mate_elements["compat_line"].set_image(
                image_cache.load_image("resources/images/line_compatible.png").convert_alpha())
        elif get_personality_compatibility(self.the_cat, self.selected_cat) is False:
            self.mate_elements["compat_line"].set_image(
                image_cache.load_image("resources/images/line_incompatible.png").convert_alpha())

        # Set romantic hearts of current cat towards mate or selected cat.
        if self.selected_cat.ID in self.the_cat.relationships:
            relation = self.the_cat.relationships[self.selected_cat.ID]
        else:
            relation = self.the_cat.create_one_relationship(self.selected_cat)
        romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 41 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 210
        for i in range(0, heart_number):
            self.mate_elements["heart1" + str(i)] = pygame_gui.elements.UIImage(pygame.Rect((x_pos, 285), (22, 20)),
                                                                                image_cache.load_image(
                                                                                    "resources/images/heart_big.png").convert_alpha())
            x_pos += 27

        # Set romantic hearts of mate/selected cat towards current_cat.
        if self.the_cat.ID in self.selected_cat.relationships:
            relation = self.selected_cat.relationships[self.the_cat.ID]
        else:
            relation = self.selected_cat.create_one_relationship(self.the_cat)
        romantic_love = relation.romantic_love

        if 10 <= romantic_love <= 30:
            heart_number = 1
        elif 41 <= romantic_love <= 80:
            heart_number = 2
        elif 81 <= romantic_love:
            heart_number = 3
        else:
            heart_number = 0

        x_pos = 568
        for i in range(0, heart_number):
            self.mate_elements["heart2" + str(i)] = pygame_gui.elements.UIImage(
                pygame.Rect((x_pos, 285), (22, 20)),
                image_cache.load_image("resources/images/heart_big.png").convert_alpha())
            x_pos -= 27

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
            next_cat = 1

        for check_cat in Cat.all_cats:
            if Cat.all_cats[check_cat].ID == self.the_cat.ID:
                self.next_cat = 1
            if self.next_cat == 0 and Cat.all_cats[
                check_cat].ID != self.the_cat.ID and Cat.all_cats[
                check_cat].dead == self.the_cat.dead and Cat.all_cats[
                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                check_cat].exiled and Cat.all_cats[
                check_cat].status not in ['apprentice', 'medicine cat apprentice', 'kitten'] and Cat.all_cats[
                check_cat].df == self.the_cat.df:
                self.previous_cat = Cat.all_cats[check_cat].ID

            elif self.next_cat == 1 and Cat.all_cats[
                check_cat].ID != self.the_cat.ID and Cat.all_cats[
                check_cat].dead == self.the_cat.dead and Cat.all_cats[
                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                check_cat].exiled and Cat.all_cats[
                check_cat].status not in ['apprentice', 'medicine cat apprentice', 'kitten'] and Cat.all_cats[
                check_cat].df == self.the_cat.df:
                self.next_cat = Cat.all_cats[check_cat].ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def on_use(self):

        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (75, 360))

    def get_valid_mates(self):
        """Get a list of valid mates for the current cat"""
        valid_mates = []
        for x in game.clan.clan_cats:
            relevant_cat = Cat.all_cats[x]
            invalid_age = relevant_cat.age not in ['kitten', 'adolescent']

            direct_related = self.the_cat.is_sibling(relevant_cat) or self.the_cat.is_parent(relevant_cat) \
                             or relevant_cat.is_parent(self.the_cat)
            indirect_related = self.the_cat.is_uncle_aunt(relevant_cat) or relevant_cat.is_uncle_aunt(self.the_cat)
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

    search_bar = image_cache.load_image("resources/images/relationship_search.png").convert_alpha()
    details_frame = image_cache.load_image("resources/images/relationship_details_frame.png").convert_alpha()
    toggle_frame = image_cache.load_image("resources/images/relationship_toggle_frame.png").convert_alpha()
    list_frame = image_cache.load_image("resources/images/relationship_list_frame.png").convert_alpha()

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

        self.previous_cat_button = UIImageButton(pygame.Rect((25, 25), (153, 30)), "", object_id="#previous_cat_button")
        self.next_cat_button = UIImageButton(pygame.Rect((622, 25), (153, 30)), "", object_id="#next_cat_button")
        self.back_button = UIImageButton(pygame.Rect((25, 645), (105, 30)), "", object_id="#back_button")

        self.search_bar = pygame_gui.elements.UITextEntryLine(pygame.Rect((610, 97), (145, 23)),
                                                              object_id="#search_entry_box")

        self.show_dead_text = pygame_gui.elements.UITextBox("Show Dead", pygame.Rect((100, 505), (100, 30)),
                                                            object_id="#relation_list_name")
        self.show_empty_text = pygame_gui.elements.UITextBox("Show Empty", pygame.Rect((100, 550), (100, 30)),
                                                             object_id="#relation_list_name")
        # Draw the checkboxes
        self.update_checkboxes()

        self.previous_page_button = UIImageButton(pygame.Rect((440, 616), (34, 34)), "",
                                                  object_id="#relation_list_previous")
        self.next_page_button = UIImageButton(pygame.Rect((580, 616), (34, 34)), "", object_id="#relation_list_next")

        self.page_number = pygame_gui.elements.UITextBox("", pygame.Rect((445, 616), (150, 34)),
                                                         object_id=get_text_box_theme())

        self.switch_focus_button = UIImageButton(pygame.Rect((85, 390), (136, 30)), "",
                                                 object_id="#switch_focus_button")
        self.switch_focus_button.disable()
        self.view_profile_button = UIImageButton(pygame.Rect((85, 420), (136, 30)), "",
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
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats:
            if Cat.all_cats[check_cat].ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and Cat.all_cats[
                    check_cat].ID != self.the_cat.ID and Cat.all_cats[
                    check_cat].dead == self.the_cat.dead and Cat.all_cats[
                    check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                    check_cat].exiled and Cat.all_cats[
                    check_cat].df == self.the_cat.df:
                    previous_cat = Cat.all_cats[check_cat].ID

                elif next_cat == 1 and Cat.all_cats[
                    check_cat].ID != self.the_cat.ID and Cat.all_cats[
                    check_cat].dead == self.the_cat.dead and Cat.all_cats[
                    check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                    check_cat].exiled and Cat.all_cats[
                    check_cat].df == self.the_cat.df:
                    next_cat = Cat.all_cats[check_cat].ID

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

        self.checkboxes["show_dead"] = UIImageButton(pygame.Rect((76, 505), (34, 34)), "",
                                                     object_id=checkbox_type)

        if game.settings['show empty relation']:
            checkbox_type = "#checked_checkbox"
        else:
            checkbox_type = "#unchecked_checkbox"

        self.checkboxes["show_empty"] = UIImageButton(pygame.Rect((76, 550), (34, 34)), "",
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
                                                                          pygame.Rect((75, 75), (400, 50)),
                                                                          object_id=get_text_box_theme("#header_left"))
        self.focus_cat_elements["details"] = pygame_gui.elements.UITextBox(self.the_cat.genderalign + " - " + \
                                                                           str(self.the_cat.moons) + " moons - " + \
                                                                           self.the_cat.trait,
                                                                           pygame.Rect((80, 105), (400, 30)),
                                                                           object_id=get_text_box_theme(
                                                                               "#cat_profile_info_box"))
        self.focus_cat_elements["image"] = pygame_gui.elements.UIImage(pygame.Rect((25, 75), (50, 50)),
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
                pygame.Rect((75, 295), (150, 40)),
                chosen_name,
                object_id="#header_text_box")

            # Cat Image
            self.inspect_cat_elements["image"] = pygame_gui.elements.UIImage(pygame.Rect((75, 145), (150, 150)),
                                                                             self.inspect_cat.large_sprite)

            # Family Dot
            if self.inspect_cat.is_uncle_aunt(self.the_cat) or self.the_cat.is_uncle_aunt(
                    self.inspect_cat) or \
                    self.inspect_cat.is_grandparent(self.the_cat) or self.the_cat.is_grandparent(
                self.inspect_cat) or \
                    self.inspect_cat.is_parent(self.the_cat) or self.the_cat.is_parent(
                self.inspect_cat) or \
                    self.inspect_cat.is_sibling(self.the_cat):
                self.inspect_cat_elements['family'] = pygame_gui.elements.UIImage(pygame.Rect((45, 150), (18, 18)),
                                                                                  image_cache.load_image(
                                                                                      "resources/images/dot_big.png").convert_alpha())

            # Mate Heart
            if self.the_cat.mate is not None and self.the_cat.mate != '' and self.inspect_cat.ID == self.the_cat.mate:
                self.inspect_cat_elements["mate"] = pygame_gui.elements.UIImage(pygame.Rect((45, 150), (22, 20)),
                                                                                image_cache.load_image(
                                                                                    "resources/images/heart_big.png").convert_alpha())

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

            self.inspect_cat_elements["gender"] = pygame_gui.elements.UIImage(pygame.Rect((235, 145), (34, 34)),
                                                                              gender_icon)

            # Column One Details:
            col1 = ""
            # Gender-Align
            col1 += self.inspect_cat.genderalign + "\n"

            # Age
            col1 += f"{self.inspect_cat.moons} moons\n"

            # Trait
            col1 += f"{self.inspect_cat.trait}\n"

            self.inspect_cat_elements["col1"] = UITextBoxTweaked(col1, pygame.Rect((60, 335), (70, -1)),
                                                                 object_id="#cat_profile_info_box",
                                                                 line_spacing=0.95)

            # Column Two Details:
            col2 = ""

            # Mate
            if self.inspect_cat.mate is not None and self.the_cat.ID != self.inspect_cat.mate:
                col2 += "has a mate\n"
            elif self.the_cat.mate is not None and self.the_cat.mate != '' and self.inspect_cat.ID == self.the_cat.mate:
                col2 += f"{str(self.the_cat.name)}'s mate\n"
            else:
                col2 += "mate: none\n"

            # Relation info:
            if self.inspect_cat.is_uncle_aunt(self.the_cat) or self.the_cat.is_uncle_aunt(self.inspect_cat):
                col2 += "related\n"
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

            self.inspect_cat_elements["col2"] = UITextBoxTweaked(col2, pygame.Rect((150, 335), (80, -1)),
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

        pos_x = 290
        pos_y = 150
        i = 0
        for rel in display_rel:
            self.generate_relation_block((pos_x, pos_y), rel, i)

            i += 1
            pos_x += 122
            if pos_x > 700:
                pos_y += 242
                pos_x = 290

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
        # "postion" should refer to the top left corner of the *main* relation box, not including the name.
        pos_x = pos[0]
        pos_y = pos[1]

        self.sprite_buttons["image" + str(i)] = UISpriteButton(pygame.Rect((pos_x + 22, pos_y), (50, 50)),
                                                               the_relationship.cat_to.sprite,
                                                               cat_object=the_relationship.cat_to)

        # CHECK NAME LENGTH - SHORTEN IF NECESSARY
        name = str(the_relationship.cat_to.name)  # get name
        if 12 <= len(name) >= 13:  # check name length
            short_name = str(the_relationship.cat_to.name)[0:10]
            name = short_name + '...'
        self.relation_list_elements["name" + str(i)] = pygame_gui.elements.UITextBox(name, pygame.Rect(
            (pos_x, pos_y - 24), (102, 30)),
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

        self.relation_list_elements["gender" + str(i)] = pygame_gui.elements.UIImage(pygame.Rect((pos_x + 80,
                                                                                                  pos_y + 5),
                                                                                                 (18, 18)),
                                                                                     gender_icon)

        # FAMILY DOT
        if the_relationship.cat_to.is_uncle_aunt(self.the_cat) or self.the_cat.is_uncle_aunt(the_relationship.cat_to) or \
                the_relationship.cat_to.is_grandparent(self.the_cat) or self.the_cat.is_grandparent(
            the_relationship.cat_to) or \
                the_relationship.cat_to.is_parent(self.the_cat) or self.the_cat.is_parent(the_relationship.cat_to) or \
                the_relationship.cat_to.is_sibling(self.the_cat):
            self.relation_list_elements['relation_icon' + str(i)] = pygame_gui.elements.UIImage(pygame.Rect((pos_x + 5,
                                                                                                             pos_y + 5),
                                                                                                            (9, 9)),
                                                                                                image_cache.load_image(
                                                                                                    "resources/images/dot_big.png").convert_alpha())

        # MATE
        if self.the_cat.mate is not None and self.the_cat.mate != '' and the_relationship.cat_to.ID == self.the_cat.mate:
            self.relation_list_elements['mate_icon' + str(i)] = pygame_gui.elements.UIImage(
                pygame.Rect((pos_x + 5, pos_y + 5),
                            (11, 10)),
                image_cache.load_image(
                    "resources/images/heart_big.png").convert_alpha())

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        barbar = 22
        bar_count = 0

        # ROMANTIC LOVE
        # CHECK AGE DIFFERENCE
        different_age = the_relationship.cat_to.age != self.the_cat.age
        adult_ages = ['young adult', 'adult', 'senior adult', 'elder']
        both_adult = the_relationship.cat_to.age in adult_ages and self.the_cat.age in adult_ages
        check_age = both_adult or not different_age

        if the_relationship.romantic_love > 49 and check_age:
            text = "romantic love:"
        else:
            text = "romantic like:"

        self.relation_list_elements[f'romantic_text{i}'] = pygame_gui.elements.UITextBox(text, pygame.Rect(
            (pos_x + 3, pos_y + 50 + (barbar * bar_count)),
            (80, 30)),
                                                                                         object_id="#cat_profile_info_box")
        self.relation_list_elements[f'romantic_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                           pos_y + 65 + (
                                                                                                   barbar * bar_count)),
                                                                                          (94, 10)),
                                                                              the_relationship.romantic_love,
                                                                              positive_trait=True,
                                                                              dark_mode=game.settings['dark mode']
                                                                              )
        bar_count += 1

        # PLANTONIC
        if the_relationship.platonic_like > 49:
            text = "platonic love:"
        else:
            text = "platonic like:"
        self.relation_list_elements[f'plantonic_text{i}'] = pygame_gui.elements.UITextBox(text, pygame.Rect((pos_x + 3,
                                                                                                             pos_y + 50 + (
                                                                                                                     barbar * bar_count)),
                                                                                                            (74, 30)),
                                                                                          object_id="#cat_profile_info_box")
        self.relation_list_elements[f'platonic_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                           pos_y + 65 + (
                                                                                                   barbar * bar_count)),
                                                                                          (94, 10)),
                                                                              the_relationship.platonic_like,
                                                                              positive_trait=True,
                                                                              dark_mode=game.settings['dark mode'])

        bar_count += 1

        # DISLIKE
        if the_relationship.dislike > 49:
            text = "hate:"
        else:
            text = "dislike:"
        self.relation_list_elements[f'dislike_text{i}'] = pygame_gui.elements.UITextBox(text, pygame.Rect((pos_x + 3,
                                                                                                           pos_y + 50 + (
                                                                                                                   barbar * bar_count)),
                                                                                                          (74, 30)),
                                                                                        object_id="#cat_profile_info_box")
        self.relation_list_elements[f'dislike_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                          pos_y + 65 + (
                                                                                                  barbar * bar_count)),
                                                                                         (94, 10)),
                                                                             the_relationship.dislike,
                                                                             positive_trait=False,
                                                                             dark_mode=game.settings['dark mode'])

        bar_count += 1

        # ADMIRE
        if the_relationship.admiration > 49:
            text = "admiration:"
        else:
            text = "respect:"
        self.relation_list_elements[f'admiration_text{i}'] = pygame_gui.elements.UITextBox(text, pygame.Rect((pos_x + 3,
                                                                                                              pos_y + 50 + (
                                                                                                                      barbar * bar_count)),
                                                                                                             (74, 30)),
                                                                                           object_id="#cat_profile_info_box")
        self.relation_list_elements[f'admiration_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                             pos_y + 65 + (
                                                                                                     barbar * bar_count)),
                                                                                            (94, 10)),
                                                                                the_relationship.admiration,
                                                                                positive_trait=True,
                                                                                dark_mode=game.settings['dark mode'])

        bar_count += 1

        # COMFORTABLE
        if the_relationship.comfortable > 49:
            text = "secure:"
        else:
            text = "comfortable:"
        self.relation_list_elements[f'comfortable_text{i}'] = pygame_gui.elements.UITextBox(text,
                                                                                            pygame.Rect((pos_x + 3,
                                                                                                         pos_y + 50 + (
                                                                                                                 barbar * bar_count)),
                                                                                                        (74, 30)),
                                                                                            object_id="#cat_profile_info_box")
        self.relation_list_elements[f'comfortable_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                              pos_y + 65 + (
                                                                                                      barbar * bar_count)),
                                                                                             (94, 10)),
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
                                                                                        pygame.Rect((pos_x + 3,
                                                                                                     pos_y + 50 + (
                                                                                                             barbar * bar_count)),
                                                                                                    (74, 30)),
                                                                                        object_id="#cat_profile_info_box")
        self.relation_list_elements[f'jealous_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                          pos_y + 65 + (
                                                                                                  barbar * bar_count)),
                                                                                         (94, 10)),
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
                                                                                      pygame.Rect((pos_x + 3,
                                                                                                   pos_y + 50 + (
                                                                                                           barbar * bar_count)),
                                                                                                  (74, 30)),
                                                                                      object_id="#cat_profile_info_box")
        self.relation_list_elements[f'trust_bar{i}'] = UIRelationStatusBar(pygame.Rect((pos_x + 3,
                                                                                        pos_y + 65 + (
                                                                                                barbar * bar_count)),
                                                                                       (94, 10)),
                                                                           the_relationship.trust,
                                                                           positive_trait=True,
                                                                           dark_mode=game.settings['dark mode'])

    def on_use(self):

        # LOAD UI IMAGES
        screen.blit(RelationshipScreen.search_bar, (536, 90))
        screen.blit(RelationshipScreen.details_frame, (25, 130))
        screen.blit(RelationshipScreen.toggle_frame, (45, 484))
        screen.blit(RelationshipScreen.list_frame, (273, 122))

        # Only update the postions if the search text changes
        if self.search_bar.get_text() != self.previous_search_text:
            self.apply_cat_filter(self.search_bar.get_text())
            self.update_cat_page()
        self.previous_search_text = self.search_bar.get_text()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
