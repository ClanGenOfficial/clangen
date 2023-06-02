import pygame.transform
import pygame_gui.elements


from scripts.screens.base_screens import Screens
from scripts.game_structure import image_cache
from scripts.game_structure.image_button import UIImageButton, UISpriteButton
from scripts.game_structure.game_essentials import game, screen, screen_x, screen_y, MANAGER

from scripts.utility import get_text_box_theme, scale
from scripts.cat.cats import Cat


class ChooseAdoptiveParentScreen(Screens):
    list_frame = pygame.transform.scale(image_cache.load_image("resources/images/choosing_frame.png").convert_alpha(),
                                        (1300 / 1600 * screen_x, 452 / 1400 * screen_y))
    current_cat_elements = {}
    parent_elements = {}
    adopt_parent = None
    current_page = 1
    selected_cat = None
    selected_parent_index = 0

    cat_list_buttons = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None
        self.list_page = None
        self.kittens = None
        self.the_cat = None
        self.kitten_message = None
        self.toggle_parent = None
        self.page_number = None
        self.next_page_button = None
        self.previous_page_button = None
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.parent_frame = None
        self.the_cat_frame = None
        self.info = None
        self.mentor_icon = None
        self.cycle_parent_left_button = None
        self.cycle_parent_right_button = None
        self.all_pages = []
        self.help_button = None

    def handle_event(self, event):
        """ Handles events. """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # Cat buttons list
            if event.ui_element in self.cat_list_buttons.values():
                if len(self.the_cat.adoptive_parents) < 1 or self.selected_parent_index == len(self.the_cat.adoptive_parents):
                    self.selected_cat = event.ui_element.return_cat_object()
                    self.update_buttons()
                    self.update_choose_adoptive_parent()
                else:
                    # if the cat already has a adoptive parent, then it lists offspring instead. Take to profile.
                    game.switches['cat'] = event.ui_element.return_cat_object().ID
                    self.update_buttons()
                    self.change_screen("profile screen")
            # return to profile screen
            elif event.ui_element == self.back_button:
                self.selected_parent_index = 0
                self.change_screen('profile screen')

            # Check if adoptive parent cycle buttons are clicked.
            if event.ui_element == self.cycle_parent_left_button:
                self.selected_parent_index -= 1
                if self.selected_parent_index < len(self.the_cat.adoptive_parents):
                    self.selected_cat = self.the_cat.adoptive_parents[self.selected_parent_index]
                    self.update_screen()
                else:
                    self.selected_cat = None
                    self.update_choose_adoptive_parent()
                self.update_current_cat_info()
                self.update_buttons()
            elif event.ui_element == self.cycle_parent_right_button:
                self.selected_parent_index += 1
                if self.selected_parent_index < len(self.the_cat.adoptive_parents):
                    self.selected_cat = self.the_cat.adoptive_parents[self.selected_parent_index]
                    self.update_screen()
                else:
                    self.selected_cat = None
                    self.update_choose_adoptive_parent()
                self.update_current_cat_info()
                self.update_buttons()

            elif event.ui_element == self.toggle_parent:
                if self.selected_cat and self.selected_cat.ID not in self.the_cat.adoptive_parents:
                    self.the_cat.adoptive_parents.append(self.selected_cat.ID)
                    self.the_cat.create_inheritance_new_cat()
                    self.update_screen()
                else:
                    self.the_cat.adoptive_parents.remove(self.selected_cat.ID)
                    self.the_cat.create_inheritance_new_cat()
                    self.update_choose_adoptive_parent()
                    self.update_current_cat_info()
                self.update_cat_list()
            elif event.ui_element == self.previous_cat_button:
                if Cat.fetch_cat(self.previous_cat) is not None:
                    game.switches["cat"] = self.previous_cat
                    self.selected_parent_index = 0
                    self.update_current_cat_info()
                    self.update_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if Cat.fetch_cat(self.next_cat) is not None:
                    game.switches["cat"] = self.next_cat
                    self.selected_parent_index = 0
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
            "If a cat is added as an adoptive parent, they will be displayed on the family page and considered a full relative. "
            "Adoptive and blood parents will be treated the same, this also applies to siblings. ",
            scale(pygame.Rect((400, 120), (800, 200))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95")
        )

        self.help_button = UIImageButton(scale(pygame.Rect(
                (1450, 140), (68, 68))),
                "",
                object_id="#help_button", manager=MANAGER,
                tool_tip_text=  "A cat's adoptive parents are set automatically when the cat is born. "
                                "Any cats that are mates with the parents at the time of birth are considered adoptive parents."
                                "<br><br>"
                                "To be a possible adoptive parent, the cat has to be 14 moons older than the child.",
            )

        self.the_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((80, 226), (562, 394))),
                                                         pygame.transform.scale(
                                                             image_cache.load_image(
                                                                 "resources/images/choosing_cat1_frame_mate.png").convert_alpha(),
                                                             (562, 394)))
        self.parent_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((960, 226), (562, 394))),
                                                      pygame.transform.scale(
                                                          image_cache.load_image(
                                                              "resources/images/choosing_cat2_frame_mate.png").convert_alpha(),
                                                          (562, 394)))

        
        self.mentor_icon = pygame_gui.elements.UIImage(scale(pygame.Rect((630, 320), (342, 266))),
                                                       pygame.transform.scale(
                                                           image_cache.load_image(
                                                               "resources/images/adoption_flip.png").convert_alpha(),
                                                           (343, 228)), manager=MANAGER)
        
        self.cycle_parent_left_button = UIImageButton(scale(pygame.Rect((1216, 616), (68, 68))),"",
                            object_id="#arrow_left_button",
                            manager=MANAGER)

        self.cycle_parent_right_button = UIImageButton(scale(pygame.Rect((1416, 616), (68, 68))),"",
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
        self.toggle_parent = UIImageButton(scale(pygame.Rect((607, 620), (384, 60))), "",
                                         object_id="#set_adoptive_parent")

        # The text will be changed as needed. This is used for both the "this pair can't have
        # offspring" message, header for the kittens section for adoptive parent.
        self.kitten_message = pygame_gui.elements.UITextBox("", scale(pygame.Rect((200, 666), (1200, 80))),
                                                            object_id=get_text_box_theme("#text_box_22_horizcenter"))
        self.kitten_message.hide()

        # This will set up everything else on the page. Basically everything that changed with selected or
        # current cat
        self.update_current_cat_info()

    def exit_screen(self):
        self.selected_parent_index = 0
        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.parent_elements:
            self.parent_elements[ele].kill()
        self.parent_elements = {}

        for ele in self.cat_list_buttons:
            self.cat_list_buttons[ele].kill()
        self.cat_list_buttons = {}

        self.info.kill()
        del self.info
        self.the_cat_frame.kill()
        del self.the_cat_frame
        self.parent_frame.kill()
        del self.parent_frame
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
        self.toggle_parent.kill()
        del self.toggle_parent
        self.kitten_message.kill()
        del self.kitten_message
        self.mentor_icon.kill()
        del self.mentor_icon
        self.cycle_parent_left_button.kill()
        del self.cycle_parent_left_button
        self.cycle_parent_right_button.kill()
        del self.cycle_parent_right_button
        self.help_button.kill()
        del self.help_button

        self.all_pages = []

    def update_current_cat_info(self):
        """Updates all elements with the current cat, as well as the selected cat.
            Called when the screen switched, and whenever the focused cat is switched"""
        self.the_cat = Cat.all_cats[game.switches['cat']]

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.parent_elements:
            self.parent_elements[ele].kill()
        self.parent_elements = {}

        self.selected_cat = None
        self.current_page = 1

        self.current_cat_elements["heading"] = pygame_gui.elements.UITextBox(
            "Choose a adoptive parent for " + str(self.the_cat.name),
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
               self.the_cat.personality.trait
        self.current_cat_elements["info"] = pygame_gui.elements.UITextBox(info,
                                                                          scale(pygame.Rect((420, 370), (210, 250))),
                                                                          object_id="#text_box_22_horizcenter_spacing_95",
                                                                          manager=MANAGER
                                                                          )

        # Determine what to draw regarding the other cat. If they have a adoptive parent, set the screen up for that.
        # if they don't, set the screen up to choose a adoptive parent.
        if len(self.the_cat.adoptive_parents) > 0 and self.selected_parent_index < len(self.the_cat.adoptive_parents):
            self.update_screen()
        else:
            self.update_choose_adoptive_parent()

        # Update the list of cats. Will be offspring if they have a adoptive parent, and valid adoptive parents if they don't
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

        # allow also one index above the adoptive parent amount, to be able to select a new one
        if len(self.the_cat.adoptive_parents) <= 0:
            self.cycle_parent_left_button.hide()
            self.cycle_parent_right_button.hide()
        else:
            self.cycle_parent_left_button.show()
            self.cycle_parent_right_button.show()
            self.cycle_parent_left_button.enable()
            self.cycle_parent_right_button.enable()
            if self.selected_parent_index == len(self.the_cat.adoptive_parents): 
                self.cycle_parent_right_button.disable()
            if self.selected_parent_index == 0:
                self.cycle_parent_left_button.disable()

    def update_screen(self):
        """Sets up the screen for a cat with a adoptive parent already."""
        for ele in self.parent_elements:
            self.parent_elements[ele].kill()
        self.parent_elements = {}

        self.selected_cat = Cat.fetch_cat(self.the_cat.adoptive_parents[self.selected_parent_index])
        
        self.parent_elements["image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((1200, 300), (300, 300))),
                                                                  pygame.transform.scale(
                                                                      self.selected_cat.sprite, (300, 300)))
        name = str(self.selected_cat.name)
        if 11 <= len(name):  # check name length
            short_name = str(name)[0:9]
            name = short_name + '...'
        self.parent_elements["name"] = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect((1240, 230), (220, 60))),
            name,
            object_id="#text_box_34_horizcenter")

        info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
               self.selected_cat.genderalign + "\n" + self.selected_cat.personality.trait
        self.parent_elements["info"] = pygame_gui.elements.UITextBox(info,
                                                                   scale(pygame.Rect((970, 370), (210, 250))),
                                                                   object_id="#text_box_22_horizcenter_spacing_95",
                                                                   manager=MANAGER
                                                                   )

        # Set the button to say "unset adoptive parent"
        self.toggle_parent.kill()
        self.toggle_parent = UIImageButton(scale(pygame.Rect((607, 620), (384, 60))), "", object_id="#unset_adoptive_parent")

        self.update_cat_list()

        # Display message
        if self.kittens:
            self.kitten_message.set_text("The offsprings of the shown adoptive parent:")
        else:
            self.kitten_message.set_text("The adoptive parent has no offsprings.")
        self.kitten_message.show()

        if len(self.the_cat.adoptive_parents) <= 0:
            self.cycle_parent_left_button.hide()
            self.cycle_parent_right_button.hide()
        else:
            self.cycle_parent_left_button.show()
            self.cycle_parent_right_button.show()
            self.cycle_parent_left_button.enable()
            self.cycle_parent_right_button.enable()
            if self.selected_parent_index == len(self.the_cat.adoptive_parents): 
                self.cycle_parent_right_button.disable()
            if self.selected_parent_index == 0:
                self.cycle_parent_left_button.disable()

    def update_cat_list(self):
        """Gathers all the cats to list, then updates the page. Also 
            sets the current page to 1. This should not be called when
            switching the page, but only when a new list of cats needs
            to be displayed.
        """

        # If the cat already has a adoptive parent, we display the children. If not, we display the possible adoptive parents
        self.all_pages = []
        if self.selected_cat and self.selected_cat.ID in self.the_cat.adoptive_parents:
            self.kittens = False
            for cat_id in game.clan.clan_cats:
                fetched_cat = Cat.fetch_cat(cat_id)
                if not fetched_cat or cat_id == self.the_cat.ID:
                    continue
                if self.selected_cat.ID in [
                    fetched_cat.parent1,
                    fetched_cat.parent2
                ] or self.selected_cat.ID in fetched_cat.adoptive_parents:
                    self.all_pages.append(fetched_cat)
                    self.kittens = True
        else:
            self.all_pages = self.get_valid_adoptive_parents()

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

    def update_choose_adoptive_parent(self):
        """This sets up the page for adding one or more adoptive parents."""
        for ele in self.parent_elements:
            self.parent_elements[ele].kill()
        self.parent_elements = {}

        if self.selected_cat:
            self.parent_elements["image"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1200, 300), (300, 300))),
                pygame.transform.scale(
                    self.selected_cat.sprite, (300, 300)))

            name = str(self.selected_cat.name)
            if 11 <= len(name):  # check name length
                short_name = str(name)[0:9]
                name = short_name + '...'
            self.parent_elements["name"] = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((1240, 230), (220, 60))),
                name,
                object_id="#text_box_34_horizcenter")

            info = str(self.selected_cat.moons) + " moons\n" + self.selected_cat.status + "\n" + \
                   self.selected_cat.genderalign + "\n" + self.selected_cat.personality.trait
            self.parent_elements["info"] = pygame_gui.elements.UITextBox(info,
                                                                       scale(pygame.Rect((970, 370), (210, 250))),
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

        self.toggle_parent.kill()
        self.toggle_parent = UIImageButton(scale(pygame.Rect((607, 620), (384, 60))), "",
                                         object_id="#set_adoptive_parent")

        self.update_buttons()

    def update_buttons(self):
        """This updates the state of buttons. For this screen, it only deals with the toggle-mates button"""
        if self.selected_cat is None:
            self.toggle_parent.disable()
        else:
            self.toggle_parent.enable()

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
                    check_cat.df == self.the_cat.df:
                self.previous_cat = check_cat.ID

            elif self.next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                    check_cat.ID != game.clan.instructor.ID and not check_cat.exiled and not check_cat.outside and \
                    check_cat.df == self.the_cat.df:
                self.next_cat = check_cat.ID

            elif int(self.next_cat) > 1:
                break

        if self.next_cat == 1:
            self.next_cat = 0

    def on_use(self):

        # Due to a bug in pygame, any image with buttons over it must be blited
        screen.blit(self.list_frame, (150 / 1600 * screen_x, 720 / 1400 * screen_y))

    def get_valid_adoptive_parents(self):
        """Get a list of valid mates for the current cat"""
        valid_parents = []
        for relevant_cat in Cat.all_cats_list:
            if relevant_cat.ID == self.the_cat.ID:
                continue
            if relevant_cat.dead:
                continue
            if self.the_cat.ID not in self.the_cat.adoptive_parents and\
                self.the_cat.ID not in [relevant_cat.parent1, relevant_cat.parent2] and\
                self.the_cat.moons < relevant_cat.moons and relevant_cat.moons - self.the_cat.moons >= 14:
                # 14 moons is for the minimal age of a cat to be a parent
                valid_parents.append(relevant_cat)
        return valid_parents

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

