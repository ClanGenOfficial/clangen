from random import choice, randint

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat
from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton, UISpriteButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.utility import scale, get_text_box_theme, shorten_text_to_fit

class NurseryScreen(Screens):
    """
    Screen for the Nursery, in which play-sessions can be held for kittens, functioning similarly to patrols.
    """

    def __init__(self, name=None):
        super().__init__(name)

        self.current_adult_page = 1
        self.current_kit_page = 1

        self.screen_elements = {}

        self.adult_selection_container = None
        self.adult_selection_elements = {}
        self.adult_cat_buttons = {}
        self.available_adults = {}  # TODO: make available adults save for the moon

        self.kits_selection_container = None
        self.kits_selection_elements = {}
        self.kits_cat_buttons = {}
        self.available_kittens = {}

        self.focus_frame_container = None
        self.focus_frame_elements = {}
        self.focus_container = None
        self.focus_elements = {}
        self.focus_cat = None

        self.chosen_kits = []
        self.chosen_adult = None
        self.chosen_cats_container = None
        self.chosen_cats_elements = {}

    def screen_switches(self):
        """Runs when this screen is switched to."""

        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        
        # BACKGROUND FLOWERS
        try:
            if game.settings["dark mode"]:
                self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((0, 0), (1600, 1400))),
                    pygame.image.load(
                        f"resources/images/nursery_flowers_dark.png").convert_alpha(),
                    object_id="#nursery_flowers_bg",
                    starting_height=1,
                    manager=MANAGER)
            else:
                self.screen_elements["bg_image"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((0, 0), (1600, 1400))),
                    pygame.image.load(
                        f"resources/images/nursery_flowers_light.png").convert_alpha(),
                    object_id="#nursery_flowers_bg",
                    starting_height=1,
                    manager=MANAGER)
        except FileNotFoundError:
            print("WARNING: Nursery background images not found.")
        
        # FOCUS FRAME
        self.create_focus_frame()
        self.focus_frame_elements["add_cat"].disable()
        self.focus_frame_elements["remove"].hide()

        # CHOSEN CATS
        self.create_chosen_cats()
        self.chosen_cats_elements["begin_playtime"].disable()
        
        # ADULT SELECTION
        self.create_available_adults()
        self.create_adult_selection()
        self.update_adult_list()

        # KITS SELECTION
        self.create_available_kittens()
        self.create_kits_selection()
        self.update_kits_list()

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. """

        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.kits_selection_elements["page_right"]:
                self.current_kit_page += 1
                self.update_kits_list()
            elif event.ui_element == self.kits_selection_elements["page_left"]:
                self.current_kit_page -= 1
                self.update_kits_list()
            elif event.ui_element == self.adult_selection_elements["page_right"]:
                self.current_adult_page += 1
                self.update_adult_list()
            elif event.ui_element == self.adult_selection_elements["page_left"]:
                self.current_adult_page -= 1
                self.update_adult_list()
            elif event.ui_element == self.focus_frame_elements["random_dice"]:
                self.randomize_focus_cat()
                self.update_focus()
            elif event.ui_element in self.adult_cat_buttons.values() or event.ui_element in self.kits_cat_buttons.values():
                self.focus_cat = event.ui_element.return_cat_object()
                self.update_focus()
            elif event.ui_element == self.focus_frame_elements["add_cat"]:
                if self.focus_cat.age != "kitten":
                    self.chosen_adult = self.focus_cat
                else:
                    self.chosen_kits.append(self.focus_cat)
                self.focus_cat = None
                self.update_focus()
                self.update_chosen_cats()
            elif event.ui_element == self.focus_frame_elements["remove"]:
                if self.focus_cat.age != "kitten":
                    self.chosen_adult = None
                else:
                    self.chosen_kits.remove(self.focus_cat)
                self.update_focus()
                self.update_chosen_cats()

    def exit_screen(self):
        """Runs when screen exits"""
        self.back_button.kill()

        for ele in self.screen_elements:
            self.screen_elements[ele].kill()
        
        self.adult_selection_container.kill()
        self.kits_selection_container.kill()
        self.focus_frame_container.kill()
        self.focus_container.kill()
        self.chosen_cats_container.kill()

        self.focus_cat = None
        self.chosen_adult = None
        self.chosen_kits = []
        self.available_adults = {}
    
    def create_available_adults(self):
        """
        Creates a dict of available adults. It will consider randomized volunteers, caretakers, and parents with kittens.
        """
        self.available_adults = {
            "parents": [],
            "caretakers": [],
            "volunteers": [],
            "all": []
        }

        # get adult clan cats
        adults = [i for i in Cat.all_cats.values() if i.age not in ["kitten", "newborn"] and not i.dead and not i.not_working() and not i.outside]

        # get kittens in the nursery
        kittens = [i for i in Cat.all_cats.values() if i.age == "kitten" and not i.dead and not i.not_working()]

        # add parents to list
        for a in adults:
            for k in kittens:
                if (a.ID in [k.parent1, k.parent2] or a.ID in k.adoptive_parents) and a not in self.available_adults["all"]:
                    self.available_adults["parents"].append(a)
                    self.available_adults["all"].append(a)
        
        # add caretakers to list
        # TODO: add caretaker role first.
        
        # add volunteers to list
        for c in range(randint(0, 3 if len(adults) > 3 else len(adults))):
            while True:
                vol = choice(adults)
                if  vol not in self.available_adults["all"]:
                    self.available_adults["volunteers"].append(vol)
                    self.available_adults["all"].append(vol)
                    break

    def create_available_kittens(self):
        """
        Creates a dict of available kittens. Kittens are the keys, values are their parents.
        """
        # get kittens
        kittens = [i for i in Cat.all_cats.values() if i.age == "kitten" and not i.dead and not i.not_working()]

        # adding parents to list
        for k in kittens:
            self.available_kittens[k] = []
            for a in self.available_adults["parents"]:
                if a.ID in [k.parent1, k.parent2] or a.ID in k.adoptive_parents:
                    self.available_kittens[k].append(a)
    
    def create_adult_selection(self):
        """
        Handles creating a container for the available adults.
        """
        self.adult_selection_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((196, 890), (100, 100))),
            object_id="#adult_selection_container",
            starting_height=1,
            manager=MANAGER
        )
        self.adult_selection_elements["page_left"] = UIImageButton(
            scale(pygame.Rect((60, 0), (68, 68))),
            "",
            object_id="#arrow_left_button",
            container=self.adult_selection_container,
            starting_height=1,
            manager=MANAGER
        )
        self.adult_selection_elements["page_right"] = UIImageButton(
            scale(pygame.Rect((420, 0), (68, 68))),
            "",
            object_id="#arrow_right_button",
            container=self.adult_selection_container,
            starting_height=1,
            manager=MANAGER
        )
        self.adult_selection_elements["frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (540, 402))),
            pygame.image.load(
                "resources/images/nursery_adults_frame.png").convert_alpha(),
            object_id="#adult_selection_frame",
            container=self.adult_selection_container,
            starting_height=1,
            manager=MANAGER
        )
    
    def create_kits_selection(self):
        """
        Handles creating a container for the available kittens.
        """
        self.kits_selection_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((868, 890), (100, 100))),
            object_id="#kits_selection_container",
            starting_height=1,
            manager=MANAGER
        )
        self.kits_selection_elements["page_left"] = UIImageButton(
            scale(pygame.Rect((60, 0), (68, 68))),
            "",
            object_id="#arrow_left_button",
            container=self.kits_selection_container,
            starting_height=1,
            manager=MANAGER
        )
        self.kits_selection_elements["page_right"] = UIImageButton(
            scale(pygame.Rect((420, 0), (68, 68))),
            "",
            object_id="#arrow_right_button",
            container=self.kits_selection_container,
            starting_height=1,
            manager=MANAGER
        )
        self.kits_selection_elements["frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (540, 402))),
            pygame.image.load(
                "resources/images/nursery_kits_frame.png").convert_alpha(),
            object_id="#kits_selection_frame",
            container=self.kits_selection_container,
            starting_height=1,
            manager=MANAGER
        )
    
    def update_kits_list(self):
        """
        Handles creating and updating the list of available kittens.
        """
        # get kittens
        kittens = []
        for k in self.available_kittens.keys():
            kittens.append(k)

        # separate them into chunks for the pages
        kitten_chunks = self.chunks(kittens, 8)

        # clamp current page to a valid page number
        self.current_kit_page = max(1, min(self.current_kit_page, len(kitten_chunks)))

        # handles which arrow buttons are clickable
        if len(kitten_chunks) <= 1:
            self.kits_selection_elements["page_left"].disable()
            self.kits_selection_elements["page_right"].disable()
        elif self.current_kit_page >= len(kitten_chunks):
            self.kits_selection_elements["page_left"].enable()
            self.kits_selection_elements["page_right"].disable()
        elif self.current_kit_page == 1 and len(kitten_chunks) > 1:
            self.kits_selection_elements["page_left"].disable()
            self.kits_selection_elements["page_right"].enable()
        else:
            self.kits_selection_elements["page_left"].enable()
            self.kits_selection_elements["page_right"].enable()
        
        # CREATE DISPLAY
        display_cats = []
        if kitten_chunks:
            display_cats = kitten_chunks[self.current_kit_page - 1]

        # container for all the cat sprites and names
        self.kits_cat_list_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((30, 100), (0, 0))),
            container=self.kits_selection_container,
            starting_height=3,
            object_id="#kits_cat_list",
            manager=MANAGER
        )

        # Kill all currently displayed cats
        for ele in self.kits_cat_buttons:
            self.kits_cat_buttons[ele].kill()
        self.kits_cat_buttons = {}

        pos_x = 0
        pos_y = 0
        i = 0
        for cat in display_cats:
            self.kits_cat_buttons[f"sprite{str(i)}"] = UISpriteButton(
                scale(pygame.Rect((10 + pos_x, 0 + pos_y), (100, 100))),
                cat.sprite,
                cat_object=cat,
                container=self.kits_cat_list_container,
                object_id=f"#sprite{str(i)}",
                tool_tip_text=str(cat.name),
                starting_height=2,
                manager=MANAGER
            )

            # changing pos
            pos_x += 120
            if pos_x >= 480:  # checks if row is full
                pos_x = 0
                pos_y += 120

            i += 1
    
    def update_adult_list(self):
        """
        Handles creating and updating the list of available adults.
        """
        # get cats
        adults = self.available_adults["all"]

        # separate them into chunks for the pages
        adult_chunks = self.chunks(adults, 8)

        # clamp current page to a valid page number
        self.current_adult_page = max(1, min(self.current_adult_page, len(adult_chunks)))

        # handles which arrow buttons are clickable
        if len(adult_chunks) <= 1:
            self.adult_selection_elements["page_left"].disable()
            self.adult_selection_elements["page_right"].disable()
        elif self.current_adult_page >= len(adult_chunks):
            self.adult_selection_elements["page_left"].enable()
            self.adult_selection_elements["page_right"].disable()
        elif self.current_adult_page == 1 and len(adult_chunks) > 1:
            self.adult_selection_elements["page_left"].disable()
            self.adult_selection_elements["page_right"].enable()
        else:
            self.adult_selection_elements["page_left"].enable()
            self.adult_selection_elements["page_right"].enable()
        
        # CREATE DISPLAY
        display_cats = []
        if adult_chunks:
            display_cats = adult_chunks[self.current_adult_page - 1]

        # container for all the cat sprites and names
        self.adult_cat_list_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((30, 100), (0, 0))),
            container=self.adult_selection_container,
            starting_height=3,
            object_id="#adult_cat_list",
            manager=MANAGER
        )

        # Kill all currently displayed cats
        for ele in self.adult_cat_buttons:
            self.adult_cat_buttons[ele].kill()
        self.adult_cat_buttons = {}

        pos_x = 0
        pos_y = 0
        i = 0
        for cat in display_cats:
            self.adult_cat_buttons[f"sprite{str(i)}"] = UISpriteButton(
                scale(pygame.Rect((10 + pos_x, 0 + pos_y), (100, 100))),
                cat.sprite,
                cat_object=cat,
                container=self.adult_cat_list_container,
                object_id=f"#sprite{str(i)}",
                tool_tip_text=str(cat.name),
                starting_height=2,
                manager=MANAGER
            )

            # changing pos
            pos_x += 120
            if pos_x >= 480:  # checks if row is full
                pos_x = 0
                pos_y += 120

            i += 1
    
    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]
    
    def create_focus_frame(self):
        """
        handles the creation of focus_container_frame
        """
        self.focus_frame_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((1000, 240), (0, 0))),
            object_id="#focus_frame_container",
            starting_height=3,
            manager=MANAGER
        )
        self.focus_frame_elements["random_dice"] = UIImageButton(
            scale(pygame.Rect((60, 532), (68, 68))),
            "",
            object_id="#random_dice_button",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER
        )
        self.focus_frame_elements["add_cat"] = UIImageButton(
            scale(pygame.Rect((168, 532), (182, 68))),
            "",
            object_id="#add_cat_nursery_button",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER
        )
        self.focus_frame_elements["remove"] = UIImageButton(
            scale(pygame.Rect((174, 532), (174, 68))),
            "",
            object_id="#remove_button",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER
        )
        self.focus_frame_elements["frame"] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (400, 550))),
                                                                         pygame.image.load(
                                                                             "resources/images/nursery_focus_frame.png").convert_alpha(),
                                                                         object_id="#nursery_focus_frame",
                                                                         container=self.focus_frame_container,
                                                                         starting_height=1,
                                                                         manager=MANAGER
        )
        self.focus_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#focus_container",
            container=self.focus_frame_container,
            starting_height=1,
            manager=MANAGER,
        )
    
    def update_focus(self):
        """
        Handles creating and updating the elements inside focus frame.
        """
        # clearing/resetting
        if self.focus_container:
            for ele in self.focus_elements:
                self.focus_elements[ele].kill()
            self.focus_elements = {}
        else:
            self.focus_container = pygame_gui.elements.UIAutoResizingContainer(
                scale(pygame.Rect((0, 0), (0, 0))),
                object_id="#focus_container",
                container=self.focus_frame_container,
                starting_height=1,
                manager=MANAGER,
            )
        
        if self.focus_cat != None:
            # Update availability of cat
            if self.focus_cat.age == "kitten" and len(self.chosen_kits) == 3 and self.focus_cat not in self.chosen_kits:
                self.focus_frame_elements["add_cat"].disable()
            elif self.focus_cat.age != "kitten" and self.chosen_adult != None and self.focus_cat != self.chosen_adult:
                self.focus_frame_elements["add_cat"].disable()
            else:
                self.focus_frame_elements["add_cat"].enable()
            
            if self.focus_cat in self.chosen_kits or self.focus_cat == self.chosen_adult:
                self.focus_frame_elements["add_cat"].hide()
                self.focus_frame_elements["remove"].show()
            else:
                self.focus_frame_elements["add_cat"].show()
                self.focus_frame_elements["remove"].hide()
            
            # Cat info
            self.focus_elements["cat_sprite"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((50, 30), (300, 300))),
                pygame.transform.scale(self.focus_cat.sprite, (300, 300)),
                object_id="#focus_cat_sprite",
                container=self.focus_container,
                starting_height=1,
                manager=MANAGER,
            )
            self.focus_elements["cat_name"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((0, 350), (400, -1))),
                text=shorten_text_to_fit(str(self.focus_cat.name), 400, 30),
                object_id="#text_box_30_horizcenter",
                container=self.focus_container,
                manager=MANAGER,
            )
            self.focus_elements["cat_status"] = pygame_gui.elements.UILabel(
                relative_rect=scale(pygame.Rect((0, 395), (400, -1))),
                text=f"{self.focus_cat.status}",
                object_id="#text_box_22_horizcenter",
                container=self.focus_container,
                manager=MANAGER,
            )

            # Role in the nursery
            role = ""
            if self.focus_cat in self.available_adults["volunteers"]:
                role = "volunteer"
            elif self.focus_cat in self.available_adults["parents"]:
                role = "parent"
            elif self.focus_cat in self.available_kittens.keys():
                if len(self.available_kittens[self.focus_cat]) == 1:
                    role = "child of " + str(self.available_kittens[self.focus_cat][0].name)
                elif len(self.available_kittens[self.focus_cat]) > 1:
                    role = "child of " + str(self.available_kittens[self.focus_cat][0].name) + " and others"

            self.focus_elements["role"] = pygame_gui.elements.UILabel(
                relative_rect=scale(pygame.Rect((0, 425), (400, -1))),
                text=role,
                object_id="#text_box_22_horizcenter",
                container=self.focus_container,
                manager=MANAGER,
            )
            
        else:
            self.focus_frame_elements["add_cat"].disable()

    def randomize_focus_cat(self):
        """
        Handles picking a random, available cat from kittens and adults when clicking randomize -button.
        Returns the random cat.
        """
        able_cats = {
            "unadded kittens": [],
            "unadded adults": [],
            "unadded all": [],
            "all": []
        }

        # Fetching cats
        kittens = []
        for k in self.available_kittens.keys():
            kittens.append(k)
        adults = self.available_adults["all"]

        for k in kittens:
            if k not in self.chosen_kits:
                able_cats["unadded kittens"].append(k)
                able_cats["unadded all"].append(k)
            able_cats["all"].append(k)
        
        for a in adults:
            if a != self.chosen_adult:
                able_cats["unadded adults"].append(a)
                able_cats["unadded all"].append(a)
            able_cats["all"].append(a)
        
        # Choosing cat
        if self.chosen_adult != None and len(self.chosen_kits) == 3:
            # All playmate spots are already filled
            self.focus_cat = choice(able_cats["all"])
        elif self.chosen_adult != None or len(able_cats["unadded adults"]) == 0:
            self.focus_cat = choice(able_cats["unadded kittens"])
        elif len(self.chosen_kits) == 3 or len(able_cats["unadded kittens"]) == 0:
            self.focus_cat = choice(able_cats["unadded adults"])
        elif len(able_cats["unadded adults"]) == 0 and len(able_cats["unadded kittens"]) == 0:
            self.focus_cat = choice(able_cats["all"])
        else:
            self.focus_cat = choice(able_cats["unadded all"])

    def create_chosen_cats(self):
        """
        Handles the creation of the container that holds the chosen cats and playtime button.
        """
        self.chosen_cats_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((250, 120), (0, 0))),
            object_id="#chosen_cats_container",
            starting_height=3,
            manager=MANAGER
        )
        self.chosen_cats_elements["begin_playtime"] = UIImageButton(
            scale(pygame.Rect((200, 660), (284, 60))),
            "",
            object_id="#begin_playtime_button",
            container=self.chosen_cats_container,
            starting_height=1,
            manager=MANAGER
        )
        self.chosen_cats_elements["intro_text"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((0, 0), (684, -1))),
                text=shorten_text_to_fit(str("Who will play today?"), 684, 30),
                object_id="#text_box_40_horizcenter",
                container=self.chosen_cats_container,
                manager=MANAGER,
        )
        self.chosen_cats_elements["explanation"] = pygame_gui.elements.UILabel(
                scale(pygame.Rect((0, 62), (684, -1))),
                text="Choose kittens to play together, with or without a kitsitter.",
                object_id="#text_box_26_horizcenter",
                container=self.chosen_cats_container,
                manager=MANAGER,
        )
    
    def update_chosen_cats(self):
        """
        Handles updating and creating elements inside the chosen cats container.
        """
        # If at least 1 kitten has been picked, enable playtime button
        if len(self.chosen_kits) > 0:
            self.chosen_cats_elements["begin_playtime"].enable()
        else:
            self.chosen_cats_elements["begin_playtime"].disable()
        
        # reset/clear cat sprites
        for ele in self.chosen_cats_elements:
            if ele not in ["begin_playtime", "intro_text", "explanation"]:
                self.chosen_cats_elements[ele].kill()

        # Draw adult
        if self.chosen_adult != None:
            self.chosen_cats_elements["adult_sprite"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((192, 130), (300, 300))),
                pygame.transform.scale(self.chosen_adult.sprite, (300, 300)),
                object_id="#chosen_adult_sprite",
                container=self.chosen_cats_container,
                starting_height=1,
                manager=MANAGER,
            )
        
        # Draw kittens
        kit_placements = [(0, 230), (192, 330), (384, 230)]
        
        if len(self.chosen_kits) != 0:
            for n in range(len(self.chosen_kits)):
                self.chosen_cats_elements["kitten_sprite" + str(n)] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect(kit_placements[n], (300, 300))),
                    pygame.transform.scale(self.chosen_kits[n].sprite, (300, 300)),
                    object_id="#chosen_kitten_sprite" + str(n),
                    container=self.chosen_cats_container,
                    starting_height=1,
                    manager=MANAGER,
                )
    
    def reset_top_part(self):
        """
        Handles resetting the top-most containers whenever playtime activity is started or ended,
        so that other containers can take their place.
        """
        if self.focus_frame_container:
            self.focus_frame_container.kill()
        if self.chosen_cats_container:
            self.chosen_cats_container.kill()
    
    def playtime_frame_container(self):
        pass
    
    
