from .text import *
from .cats import *
from .game_essentials import *


class Button(object):
    used_screen = screen
    used_mouse = mouse

    def __init__(self, font=verdana, frame_colour=(200, 200, 200), clickable_colour=(150, 150, 150), unavailable_colour=(120, 120, 120), padding=(5, 3)):
        self.text = ''
        self.font = font
        self.reset_colour(frame_colour, clickable_colour, unavailable_colour)
        self.padding = padding

    def reset_colour(self, frame_colour, clickable_colour, unavailable_colour):
        self.frame_colour = frame_colour
        self.clickable_colour = clickable_colour
        self.unavailable_colour = unavailable_colour

    def draw_button(self, pos, available=True, image=None, text='', cat_value=None, arrow=None, name='', apprentice=None, **values):
        dynamic_image = False
        if image is not None and text != '' and text is not None:
            dynamic_image = True
            image = f"resources/{image}"
        if not available:
            colour = self.unavailable_colour
            if image is not None:
                image = f'{image}_unavailable'
        else:
            colour = self.frame_colour
        if image is None:
            new_button = pygame.Surface((self.font.text(text) + self.padding[0] * 2, self.font.size + self.padding[1] * 2))

        elif dynamic_image:
            new_button = pygame.image.load(f"{image}.png")
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
            new_button.fill(colour)
            self.font.text(text, (self.padding[0], 0), new_button)
        elif dynamic_image:
            new_button = pygame.image.load(f"{image}.png")
            new_button = pygame.transform.scale(new_button, (192, 35))
        self.used_screen.blit(new_button, new_pos)
        if game.clicked:
            if apprentice is not None:
                self.choose_mentor(apprentice, cat_value)
            elif text == 'Change Name':
                self.change_name(game.switches['naming_text'], cat_value)
            elif clickable and cat_value is None and arrow is None:
                self.activate(values)
            elif clickable and arrow is None:
                self.activate(values, cat_value)
            elif clickable:
                self.activate(values, arrow=arrow)

    def activate(self, values=None, cat_value=None, arrow=None):
        if values is None:
            values = {}
        add = values['add'] if 'add' in values.keys() else False
        for key, value in values.items():
            if cat_value is None:
                if key in game.switches.keys():
                    if not add:
                        if key == 'cur_screen' and game.switches['cur_screen'] in ['list screen', 'clan screen', 'starclan screen']:
                            game.switches['last_screen'] = game.switches['cur_screen']
                        game.switches[key] = value
                    else:
                        game.switches[key].append(value)
            elif key == 'mate':
                if value is not None:
                    cat_value.mate = value.ID
                    value.mate = cat_value.ID
                else:
                    cat_class.all_cats[cat_value.mate].mate = None
                    cat_value.mate = None
                game.switches['mate'] = None
        if arrow is not None and game.switches['cur_screen'] == 'events screen':
            max_scroll_direction = len(game.cur_events_list) - game.max_events_displayed
            if arrow == "UP" and game.event_scroll_ct < 0:
                game.cur_events_list.insert(0, game.cur_events_list.pop())
                game.event_scroll_ct += 1
            if arrow == "DOWN" and abs(game.event_scroll_ct) < max_scroll_direction:
                game.cur_events_list.append(game.cur_events_list.pop(0))
                game.event_scroll_ct -= 1
        if arrow is not None and game.switches['cur_screen'] == 'allegiances screen':
            max_scroll_direction = len(game.allegiance_list) - game.max_allegiance_displayed

            if arrow == "UP" and game.allegiance_scroll_ct < 0:
                game.allegiance_list.insert(0, game.allegiance_list.pop())
                game.allegiance_scroll_ct += 1
            if arrow == "DOWN" and abs(game.allegiance_scroll_ct) < max_scroll_direction:
                game.allegiance_list.append(game.allegiance_list.pop(0))
                game.allegiance_scroll_ct -= 1

    def change_button_brightness(self):
        if game.settings['dark mode'] and self.frame_colour == (200, 200, 200):
            self.reset_colour(frame_colour=(70, 70, 70), clickable_colour=(10, 10, 10), unavailable_colour=(30, 30, 30))
        elif not game.settings['dark mode'] and self.frame_colour == (70, 70, 70):
            self.reset_colour(frame_colour=(200, 200, 200), clickable_colour=(150, 150, 150), unavailable_colour=(120, 120, 120))

    def choose_mentor(self, apprentice, cat_value):
        if apprentice not in cat_value.apprentice:
            apprentice.mentor.former_apprentices.append(apprentice)
            apprentice.mentor.apprentice.remove(apprentice)
            apprentice.mentor = cat_value
            cat_value.apprentice.append(apprentice)
        game.current_screen = 'clan screen'
        cat_class.save_cats()

    def change_name(self, name, cat_value):
        cat_value = cat_class.all_cats.get(cat_value)
        if game.switches['naming_text'] != '':
            name = game.switches['naming_text'].split(' ')
            cat_value.name.prefix = name[0]
            if len(name) > 1:
                cat_value.name.suffix = name[1]
            cat_class.save_cats()


class Writer(Button):
    button_type = 'writer'
    abc = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
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
        self.letters = included_letters if included_letters is not None else self.abc
        self.target = target if target is not None else 'naming_text'
        self.length = letters_x
        self.letter_size = 'lower'
        self.upper = True

    def draw(self, pos, available=True):
        cur_length = 0
        space_y = 0
        space_x = 0
        x = 0
        y = 0
        self.letter_size = 'upper' if self.upper else 'lower'
        for letter in self.letters:
            if letter != self.letter_size:
                new_letter = letter.upper() if self.upper and letter.isalpha() else letter
                new_button = pygame.Surface((self.font.text(new_letter) + 10, self.font.size + 6))

                collision = self.used_screen.blit(new_button, (pos[0] + cur_length + space_x, pos[1] + (self.font.size + 6) * y + space_y))

                clickable = False
                if available and collision.collidepoint(self.used_mouse.pos):
                    colour = self.clickable_colour
                    clickable = True
                else:
                    colour = self.frame_colour
                new_button.fill(colour)
                self.font.text(new_letter, (5, 0), new_button)
                self.used_screen.blit(new_button, (pos[0] + cur_length + space_x, pos[1] + (self.font.size + 6) * y + space_y))

                if game.clicked and clickable:
                    self.activate(new_letter)
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
        if values not in ['upper', 'LOWER', 'DEL'] and len(game.switches[self.target]) < game.max_name_length and values is not None:
            game.switches[self.target] += values.upper() if self.upper else values
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
