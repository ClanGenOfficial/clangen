import pygame
from .game_essentials import game, screen, screen_x, screen_y

pygame.init()


class Font():
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

    def text(self, text, pos=None, where=used_screen, x_start=0, x_limit=800):
        """
        Blit text onto a screen and return its width.
        
        Doesn't blit if pos is None.
        Setting one or both items in pos to 'center' centers the text to the screen by default.
        Else, specify the x margins to center between using x_limit and x_start.
        Negative pos value will be taken from the other end of the screen.

        Parameters:
        text -- String to blit
        pos -- Tuple specifying (x,y) position in pixels where to blit text (default: None)
        where -- Screen to draw text onto (default: used_screen)
        x_start -- The right x-axis margin to center text within (default: 0)
        x_limit -- The left x-axis margin to center text within (default: 800)

        Returns:
        int -- Width of text when drawn
        """
        text = self.translate(text)
        t = self.font.render(text, True, self.colour)
        if pos is not None:
            # setting on or both items in tuple to 'center' centers the text to the screen by default.
            # negative pos value will be taken from the other end of the screen
            new_pos = list(pos)
            if pos[0] == 'center':
                x_margins = x_limit - x_start
                new_pos[0] = x_margins / 2 - t.get_width() / 2 + x_start
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
                font.reset_colour(colour=(239, 229, 206))
            elif not game.settings['dark mode'] and font.colour == (239, 229, 206):
                font.reset_colour(colour=(0, 0, 0))

    def blit_text(self, text, pos, where=used_screen, x_limit=800, line_break=0, line_spacing=0):
        """
        Blit text with automatically-added linebreaks.

        Parameters:
        text -- String to blit
        pos -- Tuple specifying position to blit text onto.  Use 'center' for x_pos to center text. (default: None)
        where -- Screen to draw text onto (default: used_screen)
        x_limit -- The farthest x_value that the text should reach (default: 800)
        line_break -- Specify the amount of pixels that should be between paragraphs.  Leave default to have the space
                      between paragraphs be the same as the space between lines.
                      Use \n to make a new paragraph. (default: word_width)
        line_spacing -- Specify space between the lines of a paragraph.  (default: word_height + 5px)

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
                if line_spacing != 0:
                    word_height = line_spacing
                if line_break == 0:
                    line_break = word_width
                if x + word_width >= x_limit:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                where.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += line_break  # Start on new row.


# F O N T S
verdana = Font('verdana')
verdana_black = Font('verdana', colour='black')
verdana_white = Font('verdana', colour='white')
verdana_red = Font('verdana', colour=(242, 52, 29))
verdana_light = Font('verdana', colour=(239, 229, 207))
verdana_dark = Font('verdana', colour=(35, 30, 17))
verdana_small = Font('verdana', 11)
verdana_baby = Font('verdana', 11, (100, 100, 250))
verdana_big = Font('verdana', 18)
verdana_mid = Font('verdana', 13)
verdana_big_white = Font('verdana', 18, colour='white')
verdana_green = Font('verdana', colour='darkgreen')

verdana_big_light = Font('verdana', 18, colour=(239, 229, 207))
verdana_small_light = Font('verdana', 11, colour=(239, 229, 207))

verdana_big_dark = Font('verdana', 18, colour=(57, 50, 36))
verdana_small_dark = Font('verdana', 11, colour=(57, 50, 36))
verdana_mid_dark = Font('verdana', 13, colour=(57, 50, 36))

# for relationships, same color as bar
verdana_dark_magenta = Font('verdana', 11, colour=(226, 65, 103))
verdana_magenta = Font('verdana', 11, colour=(133, 49, 40))
