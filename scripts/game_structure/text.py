import pygame
from .game_essentials import game, screen, screen_x, screen_y

pygame.init()


class Font(object):
    used_screen = screen  # The surface to draw the text on
    extra = 0  # Add extra size to text for readability
    extra_space = 0  # Extra size means extra space between text may be needed

    # all fonts
    all_fonts = []

    def translate(self, text):
        #testing
        #test dictionary
        if game.language and game.settings[
                'language'] != 'english' and text in game.language.keys():
            text = game.language[text]
        return text

    def __init__(self, name, size=15, colour=(0, 0, 0)):
        self.name = name
        self.size = size
        self.reset_colour(colour)
        self.font = pygame.font.SysFont(name, size)
        # save font to list of all fonts
        self.all_fonts.append(self)

    def reset_colour(self, colour):
        """Change colour of text. Colour is specified by an RGB tuple."""
        self.colour = colour

    def text(self, text, pos=None, where=used_screen):
        """
        Blit text onto a screen and return its width.
        
        Doesn't blit if pos is None.
        Setting one or both items in pos to 'center' centers the text to the screen.
        Negative pos value will be taken from the other end of the screen.

        Parameters:
        text -- String to blit
        pos -- Tuple specifying (x,y) position in pixels where to blit text (default: None)
        where -- Screen to draw text onto (default: used_screen)

        Returns:
        int -- Width of text when drawn
        """
        text = self.translate(text)
        t = self.font.render(text, True, self.colour)
        if pos is not None:
            # setting on or both items in tuple to 'center' centers the text to the screen.
            # negative pos value will be taken from the other end of the screen
            new_pos = list(pos)
            if pos[0] == 'center':
                new_pos[0] = screen_x / 2 - t.get_width() / 2
            elif pos[0] < 0:
                new_pos[0] = screen_x + pos[0] - t.get_width()
            if pos[1] == 'center':
                new_pos[1] = screen_y / 2 - t.get_height() / 2
            elif pos[1] < 0:
                new_pos[1] = screen_y + pos[1] - t.get_height()
            where.blit(t, new_pos)
        # returns length, if assigned to a variable
        return t.get_width()

    def change_text_size(self, extra=0):
        """
        Add or reduce the size of all fonts to increase readability for those in need

        Parameters:
        extra -- Number to add or reduce all font sizes by (default: 0)
        """
        self.extra = extra
        # Go through all existing fonts and change their sizes accordingly
        for f in self.all_fonts:
            f.font = pygame.font.SysFont(f.name, f.size + self.extra)

    def change_text_brightness(self):
        """
        Change font colors in dark mode. Verdana is used as the generic font
        """
        for font in verdana.all_fonts:
            if game.settings['dark mode'] and font.colour == (0, 0, 0):
                font.reset_colour(colour=(250, 250, 250))
            elif not game.settings['dark mode'] and font.colour == (250, 250,
                                                                    250):
                font.reset_colour(colour=(0, 0, 0))

    def blit_text(self, text, pos, where=used_screen):
        """
        Blit text with automatically-added linebreaks.

        Parameters:
        text -- String to blit
        pos -- Tuple specifying position to blit text onto (default: None)
        where -- Screen to draw text onto (default: used_screen)
        """
        words = [word.split(' ') for word in text.splitlines()
                 ]  # 2D array where each row is a list of words.
        space = 5  # The width of a space.
        x, y = pos
        for line in words:
            for word in line:
                word_surface = self.font.render(word, True, self.colour)
                word_width, word_height = word_surface.get_size()
                word_height += 5
                if x + word_width >= 400:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                where.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.


# F O N T S
verdana = Font('verdana')
verdana_black = Font('verdana', colour='black')
verdana_white = Font('verdana', colour='white')
verdana_red = Font('verdana', colour=(242, 52, 29))
verdana_small = Font('verdana', 11)
verdana_baby = Font('verdana', 11, (100, 100, 250))
verdana_big = Font('verdana', 18)
verdana_big_white = Font('verdana', 18, colour='white')
verdana_green = Font('verdana', colour='darkgreen')
# for relationships, same color as bar
verdana_dark_margenta = Font('verdana', 11, colour=(226, 65, 103))
verdana_margenta = Font('verdana', 11, colour=(160, 40, 69))
