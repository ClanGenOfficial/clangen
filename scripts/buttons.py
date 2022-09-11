from .text import *
from .cats import *
from .game_essentials import *


class Button(object):
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
        self.frame_colour = frame_colour
        self.clickable_colour = clickable_colour
        self.unavailable_colour = unavailable_colour

    def draw_button(self, pos, available=True, text='', **values):
        print('a')

    def draw_image_button(self, pos, available=True, path=None, **values):
        is_clickable = False
        if available:
            image_path = f'resources/{path}.png'
        else:
            image_path = f'resources/{path}_unavailable.png'
        image = pygame.image.load(image_path).convert_alpha()
        button = pygame.transform.scale(image, (192, 35))
        collided = self.used_screen.blit(button, pos)
        if available and collided.collidepoint(self.used_mouse.pos):
            is_clickable = True
            image_path = f'resources/{path}_hover.png'
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

    def draw_button(self, pos, available=True, image=None, text='', cat_value=None, arrow=None, apprentice=None, hotkey=None, **values):
        dynamic_image = False
        if image is not None and text != '' and text is not None:
            dynamic_image = True
            image = f"resources/{image}"
        colour = self.frame_colour if available else self.unavailable_colour
        if image is None:
            # Add hotkey name to button text if setting is turned on 
            if game.settings['hotkey display'] and hotkey is not None:
                hotkey_text = text
                for i in hotkey:
                    # Hotkey code between 10 and 19 refers to a numpad key
                    if 10 <= i <= 19:
                        numpad_number = str(i-10)
                        hotkey_text = hotkey_text + " NP" + numpad_number

                    # Hotkey code between 20 and 23 refers to an arrow key 
                    elif 20 <= i <= 23:
                        arrowkey_number = i-20
                        hotkey_text = hotkey_text + [" ^", ">", " v", " <"][arrowkey_number]

                    # Other hotkey codes are unspecified 
                    else:
                        hotkey_text = hotkey_text + " " + str(i)
                new_button = pygame.Surface((self.font.text(hotkey_text) + self.padding[0] * 2, self.font.size + self.padding[1] * 2))
            else:
                new_button = pygame.Surface((self.font.text(text) + self.padding[0] * 2, self.font.size + self.padding[1] * 2))

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
        
        # Two possibilities for a button: either it was clicked or the hotkey was pressed 
        if (game.clicked and clickable) or (available and hotkey is not None and hotkey == game.keyspressed):
            if apprentice is not None:
                self.choose_mentor(apprentice, cat_value)
            elif text == ' Change Name ' and game.switches['naming_text'] != '':
                self.change_name(game.switches['naming_text'], game.switches['name_cat'])
            elif text == ' Change Gender ' and game.switches['naming_text'] != '':
                self.change_gender(game.switches['naming_text'], game.switches['name_cat'])
            elif text in ['Next Cat', 'Previous Cat']:
                game.switches['cat'] = values.get('cat')
            elif text == 'Prevent kits':
                cat_value.no_kits = True
            elif text == 'Allow kits':
                cat_value.no_kits = False
            elif text == 'Exile Cat':
                cat_class.all_cats[cat_value].exiled = True
                cat_class.other_cats[cat_value] =  cat_class.all_cats[cat_value]
                game.switches['cur_screen'] = 'other screen'
            elif text == 'Change to Trans Male':
                cat_class.all_cats[cat_value].genderalign = "trans male"
            elif text == 'Change to Trans Female':
                cat_class.all_cats[cat_value].genderalign = "trans female"
            elif text == 'Change to Nonbinary':
                cat_class.all_cats[cat_value].genderalign = "nonbinary"
            elif text == 'Change Back to Cisgender':
                cat_class.all_cats[cat_value].genderalign = cat_class.all_cats[cat_value].gender
            elif cat_value is None and arrow is None:
                self.activate(values)
            elif arrow is None:
                self.activate(values, cat_value)
            else:
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
                    # affect relationship
                    cat_relationship = list(filter(lambda r: r.cat_to.ID == value.ID , cat_value.relationships))
                    if cat_relationship is not None and len(cat_relationship) > 0:
                        cat_relationship[0].romantic_love += 20
                        cat_relationship[0].comfortable += 20
                        cat_relationship[0].trust += 10
                    else:
                        cat_value.relationships.append(Relationship(cat_value,value,True))
    
                    other_cat_relationship = list(filter(lambda r: r.cat_to.ID == cat_value.ID , value.relationships))
                    if other_cat_relationship is not None and len(other_cat_relationship) > 0:
                        other_cat_relationship[0].romantic_love += 20
                        other_cat_relationship[0].comfortable += 20
                        other_cat_relationship[0].trust += 10
                    else:
                        value.relationships.append(Relationship(value,cat_value,True))
                else:
                    # affect relationship
                    cat_mate = cat_class.all_cats[cat_value.mate]
                    cat_relationship = list(filter(lambda r: r.cat_to.ID == cat_mate.ID , cat_value.relationships))
                    if cat_relationship is not None and len(cat_relationship) > 0:
                        cat_relationship[0].romantic_love = 5
                        cat_relationship[0].comfortable -= 20
                        cat_relationship[0].trust -= 10
                    else:
                        cat_value.relationships.append(Relationship(cat_value,cat_mate,True))
    
                    other_cat_relationship = list(filter(lambda r: r.cat_to.ID == cat_value.ID , cat_mate.relationships))
                    if other_cat_relationship is not None and len(other_cat_relationship) > 0:
                        other_cat_relationship[0].romantic_love = 5
                        other_cat_relationship[0].comfortable -= 20
                        other_cat_relationship[0].trust -= 10
                    else:
                        cat_mate.relationships.append(Relationship(cat_mate,cat_value,True))
                    cat_mate.mate = None
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
        if arrow is not None and game.switches['cur_screen'] == 'relationship event screen':
            max_scroll_direction = len(game.relation_events_list) - game.max_events_displayed
            if arrow == "UP" and game.relation_scroll_ct < 0:
                game.relation_events_list.insert(0, game.relation_events_list.pop())
                game.relation_scroll_ct += 1
            if arrow == "DOWN" and abs(game.relation_scroll_ct) < max_scroll_direction:
                game.relation_events_list.append(game.relation_events_list.pop(0))
                game.relation_scroll_ct -= 1

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
            game.switches['naming_text'] = ''
            
    def change_gender(self, name, cat_value):
        cat_value = cat_class.all_cats.get(cat_value)
        if game.switches['naming_text'] != '':
            cat_value.genderalign = game.switches['naming_text']
            cat_class.save_cats()
            game.switches['naming_text'] = ''


# BUTTONS
buttons = Button()

def draw_bar(value, pos_x, pos_y):
    # Loading Bar and variables
    bar_bg = pygame.image.load("resources/relations_border.png").convert_alpha()
    original_bar = pygame.image.load("resources/relation_bar.png").convert_alpha()

    if game.settings['dark mode']:
        bar_bg = pygame.image.load("resources/relations_border_dark.png").convert_alpha()
        original_bar = pygame.image.load("resources/relation_bar_dark.png").convert_alpha()
    
    bg_rect = bar_bg.get_rect(midleft=(pos_x, pos_y))
    screen.blit(bar_bg, bg_rect)
    x_pos = 0
    for i in range(int(value / 10)):
        x_pos = i * 11
        bar_rect = original_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
        bar = pygame.transform.scale(original_bar, (10, 12))
        screen.blit(bar, bar_rect)
    x_pos = 11 * int(value / 10)
    bar_rect = original_bar.get_rect(midleft=(pos_x + x_pos + 2, pos_y))
    bar = pygame.transform.scale(original_bar, (value % 10, 12))
    screen.blit(bar, bar_rect)