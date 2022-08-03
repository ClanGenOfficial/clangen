from .text import *
from .cats import *
from .game_essentials import *


class Button(object):
    used_screen = screen
    used_mouse = mouse

    def __init__(self, font=verdana, frame_colour=(200, 200, 200), clickable_colour=(150, 150, 150),
                 unavailable_colour=(230, 230, 230)):
        self.text = ''
        self.font = font
        self.reset_colour(frame_colour, clickable_colour, unavailable_colour)

    def reset_colour(self, frame_colour, clickable_colour, unavailable_colour):
        self.frame_colour = frame_colour
        self.clickable_colour = clickable_colour
        self.unavailable_colour = unavailable_colour

    def draw_button(self, pos, available=True, image=None, text='', cat_value=None, arrow=None, **values):
        # cat_value takes a cat object. if it isn't None, the keys and values are determined by which attributes of
        # the cat are changed and doesn't have an effect on game switches

        if not available:
            colour = self.unavailable_colour
        else:
            colour = self.frame_colour

        # creating visible button
        if image is None:
            new_button = pygame.Surface((self.font.text(text) + 10, self.font.size + 6))
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

        # Check collision
        collision = self.used_screen.blit(new_button, new_pos)
        clickable = False
        if available and collision.collidepoint(self.used_mouse.pos):
            colour = self.clickable_colour
            clickable = True

        # fill in non-image button
        if image is None:
            new_button.fill(colour)
            self.font.text(text, (5, 0), new_button)
            self.used_screen.blit(new_button, new_pos)
        else:
            self.used_screen.blit(new_button, new_pos)

        # CLICK
        if game.clicked and clickable and cat_value is None and arrow is None:
            self.activate(values)
        elif game.clicked and clickable and arrow is None:  # if cat_value is not None
            self.activate(values, cat_value)
        elif game.clicked and clickable:
            self.activate(values, arrow=arrow)

    def activate(self, values=None, cat_value=None, arrow=None):  # cat value points to a Cat object
        if values is None:
            values = {}
        add = False
        if 'add' in values.keys():
            add = values['add']
        for key, value in values.items():
            if cat_value is None:
                if key in game.switches.keys() and not add:
                    if key == 'cur_screen' and game.switches['cur_screen'] in ['list screen', 'clan screen',
                                                                               'starclan screen']:
                        game.switches['last_screen'] = game.switches['cur_screen']
                    game.switches[key] = value
                elif key in game.switches.keys() and add:
                    game.switches[key].append(value)
            else:
                if key == 'mate':
                    if value is not None:
                        cat_value.mate = value.ID
                        value.mate = cat_value.ID
                    else:
                        cat_class.all_cats[cat_value.mate].mate = None
                        cat_value.mate = None
                    game.switches['mate'] = None

        if arrow is not None:
            max_scroll_direction = len(game.cur_events_list) - game.max_events_displayed
            if arrow == "UP" and game.event_scroll_ct < 0:
                game.cur_events_list.insert(0, game.cur_events_list.pop())
                game.event_scroll_ct += 1
            if arrow == "DOWN" and abs(game.event_scroll_ct) < max_scroll_direction:
                game.cur_events_list.append(game.cur_events_list.pop(0))
                game.event_scroll_ct -= 1

    def change_button_brightness(self):
        if game.settings['dark mode'] and self.frame_colour == (200, 200, 200):
            self.reset_colour(frame_colour=(70, 70, 70), clickable_colour=(10, 10, 10),
                 unavailable_colour=(50, 50, 50))
        elif not game.settings['dark mode'] and self.frame_colour == (70, 70, 70):
            self.reset_colour(frame_colour=(200, 200, 200), clickable_colour=(150, 150, 150),
                 unavailable_colour=(230, 230, 230))


class Writer(Button):
    button_type = 'writer'
    abc = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
           'z', 'x', 'c', 'v', 'b', 'n', 'm']
    # abc.sort()
    for i in ['\'', '-', '.', 'DEL', 'upper', 'lower']:
        abc.append(i)
    letters = abc
    # letter size is opposite to the current size
    letter_size = 'lower'
    length = 12
    upper = True
    target = 'naming_text'

    def init(self, included_letters=None, letters_x=10, target=None):
        if included_letters is not None:
            self.letters = included_letters
        else:
            self.letters = self.abc
        if target is not None:
            self.target = target
        else:
            self.target = 'naming_text'

        self.length = letters_x
        self.letter_size = 'lower'
        self.upper = True

    def draw(self, pos, available=True):
        cur_length = 0
        space_y = 0
        space_x = 0
        x = 0
        y = 0

        if self.upper:
            self.letter_size = 'upper'
        else:
            self.letter_size = 'lower'

        # Is writer available?
        if available:
            colour = self.frame_colour
        else:
            colour = self.unavailable_colour

        for letter in self.letters:
            if letter != self.letter_size:
                if self.upper and letter.isalpha():
                    new_letter = letter.upper()
                else:
                    new_letter = letter
                new_button = pygame.Surface((self.font.text(new_letter) + 10, self.font.size + 6))

                # Check collision
                collision = self.used_screen.blit(new_button, (pos[0] + cur_length + space_x,
                                                               pos[1] + (self.font.size + 6) * y + space_y))
                clickable = False
                if available and collision.collidepoint(self.used_mouse.pos):
                    colour = self.clickable_colour
                    clickable = True
                else:
                    colour = self.frame_colour

                # Fill in letter and blit
                new_button.fill(colour)
                self.font.text(new_letter, (5, 0), new_button)
                self.used_screen.blit(new_button, (pos[0] + cur_length + space_x,
                                                   pos[1] + (self.font.size + 6) * y + space_y))

                # CLICK
                if game.clicked and clickable:
                    self.activate(new_letter)

                # Add pixels for the next letter to follow
                cur_length += self.font.text(new_letter) + 10
                space_x += 2
                x += 1

            if x >= self.length:
                x = 0
                cur_length = 0
                space_x = 0
                space_y += 2
                y += 1

    def activate(self, values=None, cat_value=None):
        if values not in ['upper', 'LOWER', 'DEL'] and len(game.switches[self.target]) < game.max_name_length \
                and values is not None:
            if self.upper:
                game.switches[self.target] += values.upper()
            else:
                game.switches[self.target] += values
        elif values == 'upper':
            self.upper = True
            self.letter_size = 'lower'
        elif values == 'LOWER':
            self.upper = False
            self.letter_size = 'upper'
        elif values == 'DEL' and len(game.switches[self.target]) > 0:
            game.switches[self.target] = game.switches[self.target][:-1]


# BUTTONS
buttons = Button()

# WRITER
writer = Writer()
writer.init()
