from .game_essentials import *

pygame.init()


class Font(object):
    used_screen = screen  # The surface to draw the text on
    extra = 0  # Add extra size to text for readability
    extra_space = 0  # Extra size means extra space between text may be needed

    # all fonts
    all_fonts = []

    def __init__(self, name, size=15, colour=(0, 0, 0)):
        self.name = name
        self.size = size
        self.reset_colour(colour)
        self.font = pygame.font.SysFont(name, size)
        # save font to list of all fonts
        self.all_fonts.append(self)

    def reset_colour(self, colour):
        self.colour = colour

    def text(self, text, pos=None, where=used_screen):
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
        """ Add or reduce the size of all fonts to increase readability for those in need """
        self.extra = extra
        # Go trhoguh all existing fonts and change their sizes accordingly
        for f in self.all_fonts:
            f.font = pygame.font.SysFont(f.name, f.size + self.extra)

    def change_text_brightness(self):
        # change font colors in dark mode. Verdana is used as the generic font
        for font in verdana.all_fonts:
            if game.settings['dark mode'] and font.colour == (0, 0, 0):
                font.reset_colour(colour=(250, 250, 250))
            elif not game.settings['dark mode'] and font.colour == (250, 250, 250):
                font.reset_colour(colour=(0, 0, 0))


# F O N T S
verdana = Font('verdana')
verdana_black = Font('verdana', colour='black')
verdana_red = Font('verdana', colour=(242, 52, 29))
verdana_small = Font('verdana', 11)
verdana_baby = Font('verdana', 11, (100, 100, 250))
verdana_big = Font('verdana', 18)
