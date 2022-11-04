from .text import *
from .load_cat import *
from .game_essentials import *

from scripts.cat.cats import Cat


class Button():
    used_screen = screen
    used_mouse = mouse

    def __init__(self, font=verdana, padding=(5, 3)):
        self.text = ''
        self.font = font
        self.padding = padding
        self.unavailable_colour = (120, 120, 120)
        self.clickable_colour = (150, 150, 150)
        self.frame_colour = (200, 200, 200)

    def reset_colour(self, frame_colour, clickable_colour, unavailable_colour):
        """Change colours of automatically drawn buttons. Colours are specified by RGB tuples."""
        self.frame_colour = frame_colour
        self.clickable_colour = clickable_colour
        self.unavailable_colour = unavailable_colour

    def draw_image_button(self, pos, available=True, button_name=None, **values):
        """
        Draw an image button and check for collisions.

        path must specify a .png file inside of the resources folder without the file extension.
            (e.g. if there's a file btn.png, path should be 'btn')
        Unavailable buttons should be named as {path}_unavailable.png and
        Hover buttons should be named as {path}_hover.png,
        where {path} is the name of the file in the resources folder.

        Parameters:
        pos -- Tuple specifying (x,y) position in pixels where to place button
        available -- If button is available for clicking (default: True)
        path -- Path to button image inside of resources
        **values -- Dictionary of values to be passed into activate
        """
        is_clickable = False
        if available:
            image_path = f'resources/images/buttons/{button_name}.png'
        else:
            image_path = f'resources/images/buttons/{button_name}_unavailable.png'
        image = pygame.image.load(image_path).convert_alpha()
        button = pygame.transform.scale(image, (192, 35))
        collided = self.used_screen.blit(button, pos)
        if available and collided.collidepoint(self.used_mouse.pos):
            is_clickable = True
            image_path = f'resources/images/buttons/{button_name}_hover.png'
            image = pygame.image.load(image_path).convert_alpha()
            button = pygame.transform.scale(image, (192, 35))
        self.used_screen.blit(button, pos)
        if game.clicked and is_clickable:
            self.activate(values)

    def calculate_position(self, button, pos):
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - button.get_width() / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - button.get_width()
        if pos[1] == 'center':
            new_pos[1] = screen_y / 2 - button.get_height() / 2
        elif pos[1] < 0:
            new_pos[1] = screen_y + pos[1] - button.get_height()
        return new_pos

    def draw_button(self,
                    pos,
                    available=True,
                    image=None,
                    text='',
                    cat_value=None,
                    arrow=None,
                    apprentice=None,
                    hotkey=None,
                    **values):
        """
        Draw a clickable object and check for its collisions.

        If set, image must specify a file inside of the resources folder.
        If not set, a button is drawn automatically.

        Parameters:
        pos -- Tuple specifying (x,y) position in pixels where to place button
        available -- If button is available for clicking (default: True)
        image -- Path to image inside of resources specifying button background (default: None)
        text -- String to place inside button (default: '')
        cat_value -- Cat referred to if this button refers to a cat (default: None)
        arrow -- Arrow key button pressed for input detection (default: None)
        apprentice -- Apprentice referred to if this button refers to an apprentice (default: None)
        hotkey -- Hotkey pressed for input detection (default: None)
        **values -- Dictionary of values to be passed into activate
        """
        dynamic_image = False
        if image is not None and text != '' and text is not None:
            dynamic_image = True
            image = f"resources/images/{image}"
        colour = self.frame_colour if available else self.unavailable_colour
        if image is None:
            if game.settings['hotkey display'] and hotkey is not None:
                hotkey_text = text
                for i in hotkey:
                    if i == 10:
                        hotkey_text = hotkey_text + " NP0"
                    elif i == 11:
                        hotkey_text = hotkey_text + " NP1"
                    elif i == 12:
                        hotkey_text = hotkey_text + " NP2"
                    elif i == 13:
                        hotkey_text = hotkey_text + " NP3"
                    elif i == 14:
                        hotkey_text = hotkey_text + " NP4"
                    elif i == 15:
                        hotkey_text = hotkey_text + " NP5"
                    elif i == 16:
                        hotkey_text = hotkey_text + " NP6"
                    elif i == 17:
                        hotkey_text = hotkey_text + " NP7"
                    elif i == 18:
                        hotkey_text = hotkey_text + " NP8"
                    elif i == 19:
                        hotkey_text = hotkey_text + " NP9"
                    elif i == 20:
                        hotkey_text = hotkey_text + " ^"
                    elif i == 21:
                        hotkey_text = hotkey_text + " >"
                    elif i == 22:
                        hotkey_text = hotkey_text + " v"
                    elif i == 23:
                        hotkey_text = hotkey_text + " <"
                    else:
                        hotkey_text = hotkey_text + " " + str(i)
                new_button = pygame.Surface(
                    (self.font.text(hotkey_text) + self.padding[0] * 2,
                     self.font.size + self.padding[1] * 2))
            else:
                new_button = pygame.Surface(
                    (self.font.text(text) + self.padding[0] * 2,
                     self.font.size + self.padding[1] * 2))

        elif dynamic_image:
            new_button = pygame.image.load(f"{image}.png").convert_alpha()
            new_button = pygame.transform.scale(new_button, (192, 35))
        else:
            new_button = image
        new_pos = list(pos)
        if pos[0] == 'center':
            new_pos[0] = screen_x / 2 - new_button.get_width() / 2
        elif pos[0] < 0:
            new_pos[0] = screen_x + pos[0] - new_button.get_width()
        if pos[1] == 'center':
            new_pos[1] = screen_y / 2 - new_button.get_height() / 2
        elif pos[1] < 0:
            new_pos[1] = screen_y + pos[1] - new_button.get_height()
        collision = self.used_screen.blit(new_button, new_pos)
        clickable = False
        if available and collision.collidepoint(self.used_mouse.pos):
            colour = self.clickable_colour
            clickable = True
            if dynamic_image:
                image = f'{image}_hover'
        if image is None:
            if game.settings['hotkey display'] and hotkey is not None:
                new_button.fill(colour)
                self.font.text(hotkey_text, (self.padding[0], 0), new_button)
            else:
                new_button.fill(colour)
                self.font.text(text, (self.padding[0], 0), new_button)
        elif dynamic_image:
            new_button = pygame.image.load(f"{image}.png").convert_alpha()
            new_button = pygame.transform.scale(new_button, (192, 35))
        self.used_screen.blit(new_button, new_pos)
        if game.clicked and clickable:
            if apprentice is not None:
                self.choose_mentor(apprentice, cat_value)
            elif text == 'Change Name' and game.switches['naming_text'] != '':
                self.change_name(game.switches['naming_text'],
                                 game.switches['name_cat'])
            elif text == ' Change Gender ' and game.switches[
                    'naming_text'] != '':
                self.change_gender(game.switches['naming_text'],
                                   game.switches['name_cat'])
            elif text in ['Next Cat', 'Previous Cat']:
                game.switches['cat'] = values.get('cat')
            elif text == 'Prevent kits':
                cat_value.no_kits = True
            elif text == 'Allow kits':
                cat_value.no_kits = False
            elif text == 'Exile Cat':
                # it is the leader, manage all the things
                if Cat.all_cats[cat_value].status == 'leader':
                    game.clan.leader.exiled = True
                    game.clan.leader_lives = 1
                if Cat.all_cats[cat_value].status == 'deputy':
                    game.clan.deputy.exiled = True
                    game.clan.deputy = None
                Cat.all_cats[cat_value].exiled = True
                Cat.other_cats[cat_value] = Cat.all_cats[cat_value]
            elif text == 'Change to Trans Male':
                Cat.all_cats[cat_value].genderalign = "trans male"
            elif text == 'Change to Trans Female':
                Cat.all_cats[cat_value].genderalign = "trans female"
            elif text == 'Change to Nonbinary/Specify Gender':
                Cat.all_cats[cat_value].genderalign = "nonbinary"
            elif text == 'Change to Cisgender':
                Cat.all_cats[cat_value].genderalign = Cat.all_cats[
                    cat_value].gender
            elif text == 'Remove accessory':
                Cat.all_cats[str(cat_value)].accessory = None
            elif cat_value is None and arrow is None:
                self.activate(values)
            elif arrow is None:
                self.activate(values, cat_value)
            else:
                self.activate(values, arrow=arrow)
        if available and hotkey is not None:
            if hotkey == game.keyspressed:
                if apprentice is not None:
                    self.choose_mentor(apprentice, cat_value)
                elif text == ' Change Name ' and game.switches[
                        'naming_text'] != '':
                    self.change_name(game.switches['naming_text'],
                                     game.switches['name_cat'])
                elif text == ' Change Gender ' and game.switches[
                        'naming_text'] != '':
                    self.change_gender(game.switches['naming_text'],
                                       game.switches['name_cat'])
                elif text in ['Next Cat', 'Previous Cat']:
                    game.switches['cat'] = values.get('cat')
                elif text == 'Prevent kits':
                    cat_value.no_kits = True
                elif text == 'Allow kits':
                    cat_value.no_kits = False
                elif text == 'Exile Cat':
                    Cat.all_cats[cat_value].exiled = True
                    Cat.other_cats[cat_value] = Cat.all_cats[
                        cat_value]
                    game.switches['cur_screen'] = 'other screen'
                elif text == 'Change to Trans Male':
                    Cat.all_cats[cat_value].genderalign = "trans male"
                elif text == 'Change to Trans Female':
                    Cat.all_cats[cat_value].genderalign = "trans female"
                elif text == 'Change to Nonbinary/Specify Gender':
                    Cat.all_cats[cat_value].genderalign = "nonbinary"
                elif text == 'Change to Cisgender':
                    Cat.all_cats[
                        cat_value].genderalign = Cat.all_cats[
                            cat_value].gender
                elif text == 'Remove accessory':
                    Cat.all_cats[str(cat_value)].accessory = None

                elif cat_value is None and arrow is None:
                    self.activate(values)
                elif arrow is None:
                    self.activate(values, cat_value)
                else:
                    self.activate(values, arrow=arrow)

    def activate(self, values=None, cat_value=None, arrow=None):
        """
        Activates a clicked button.

        Parameters:
        values -- Dict of values to be set as game switches
        cat_value -- Cat being activated
        arrow -- String referring to arrow that has been pressed
        """
        if values is None:
            values = {}
        add = values['add'] if 'add' in values.keys() else False
        for key, value in values.items():
            if cat_value is None:
                if key in game.switches.keys():
                    if not add:
                        if key == 'cur_screen' and game.switches[
                                'cur_screen'] in [
                                    'list screen', 'clan screen',
                                    'starclan screen'
                                ]:
                            game.switches['last_screen'] = game.switches[
                                'cur_screen']
                        game.switches[key] = value
                    else:
                        game.switches[key].append(value)
            elif key == 'mate':
                if value is not None:
                    cat_value.set_mate(value)
                    value.set_mate(cat_value)
                else:
                    cat_mate = Cat.all_cats[cat_value.mate]
                    cat_mate.unset_mate(breakup = True)
                    cat_value.unset_mate(breakup = True)
                game.switches['mate'] = None
        if arrow is not None and game.switches['cur_screen'] == 'events screen':
            max_scroll_direction = len(
                game.cur_events_list) - game.max_events_displayed
            if arrow == "UP" and game.event_scroll_ct < 0:
                game.cur_events_list.insert(0, game.cur_events_list.pop())
                game.event_scroll_ct += 1
            if arrow == "DOWN" and abs(
                    game.event_scroll_ct) < max_scroll_direction:
                game.cur_events_list.append(game.cur_events_list.pop(0))
                game.event_scroll_ct -= 1
        if arrow is not None and game.switches[
                'cur_screen'] == 'allegiances screen':
            max_scroll_direction = len(
                game.allegiance_list) - game.max_allegiance_displayed
            if arrow == "UP" and game.allegiance_scroll_ct < 0:
                game.allegiance_list.insert(0, game.allegiance_list.pop())
                game.allegiance_scroll_ct += 1
            if arrow == "DOWN" and abs(
                    game.allegiance_scroll_ct) < max_scroll_direction:
                game.allegiance_list.append(game.allegiance_list.pop(0))
                game.allegiance_scroll_ct -= 1
        if arrow is not None and game.switches[
                'cur_screen'] == 'relationship event screen':
            max_scroll_direction = len(
                game.relation_events_list) - game.max_relation_events_displayed
            if arrow == "UP" and game.relation_scroll_ct < 0:
                game.relation_events_list.insert(
                    0, game.relation_events_list.pop())
                game.relation_scroll_ct += 1
            if arrow == "DOWN" and abs(
                    game.relation_scroll_ct) < max_scroll_direction:
                game.relation_events_list.append(
                    game.relation_events_list.pop(0))
                game.relation_scroll_ct -= 1

    def change_button_brightness(self):
        """Switches button colours according to screen brightness."""
        if game.settings['dark mode'] and self.frame_colour == (200, 200, 200):
            self.reset_colour(frame_colour=(70, 70, 70),
                              clickable_colour=(10, 10, 10),
                              unavailable_colour=(30, 30, 30))
        elif not game.settings['dark mode'] and self.frame_colour == (70, 70,
                                                                      70):
            self.reset_colour(frame_colour=(200, 200, 200),
                              clickable_colour=(150, 150, 150),
                              unavailable_colour=(120, 120, 120))

    def choose_mentor(self, apprentice, cat_value):
        """Chooses cat_value as mentor for apprentice."""
        if apprentice not in cat_value.apprentice:
            apprentice.mentor.former_apprentices.append(apprentice)
            apprentice.mentor.apprentice.remove(apprentice)
            apprentice.mentor = cat_value
            cat_value.apprentice.append(apprentice)
        game.current_screen = 'clan screen'
        game.save_cats()

    def change_name(self, name, cat_value):
        """Changes name of cat_value to name specified in textbox"""
        cat_value = Cat.all_cats.get(cat_value)
        if game.switches['naming_text'] != '':
            name = game.switches['naming_text'].split(' ')
            cat_value.name.prefix = name[0]
            if len(name) > 1:
                # If cat is an apprentice/kit and new suffix is paw/kit, leave hidden suffix unchanged
                if not (cat_value.name.status == "apprentice" and name[1] == "paw") and \
                    not (cat_value.name.status == "kitten" and name[1] == "kit"):
                    cat_value.name.suffix = name[1]
            game.save_cats()
            game.switches['naming_text'] = ''

    def change_gender(self, name, cat_value):
        cat_value = Cat.all_cats.get(cat_value)
        if game.switches['naming_text'] != '':
            cat_value.genderalign = game.switches['naming_text']
            game.save_cats()
            game.switches['naming_text'] = ''


# BUTTONS
buttons = Button()
