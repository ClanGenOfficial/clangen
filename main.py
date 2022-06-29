# Make cats and start clans with them
from scripts.screens import *
import sys


# P Y G A M E
clock = pygame.time.Clock()

# LOAD cats & clan
with open('saves/clanlist.txt', 'r') as read_file:
    clan_list = read_file.read()
    if_clans = len(clan_list)
if if_clans > 0:
    game.switches['clan_list'] = clan_list.split('\n')
    cat_class.load_cats()
    clan_class.load_clan()

# LOAD settings
game.load_settings()

# give thoughts/actions to already existing cats
cat_class.thoughts()

while True:
    screen.fill((255, 255, 255))
    mouse.check_pos()

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            # close pygame
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                for x in cat_class.all_cats.values():
                    print(x.name)

        """if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()"""

        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

    # SCREENS
    game.all_screens[game.current_screen].on_use()

    # update
    game.update_game()
    if game.switch_screens:
        # print screens.all_screens[game.current_screen].name
        screens.all_screens[game.current_screen].screen_switches()
        game.switch_screens = False

    # END FRAME
    clock.tick(60)

    pygame.display.update()
