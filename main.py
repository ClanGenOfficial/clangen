# ==== DO NOT MOVE THIS IMPORT!
# ==== DO NOT ADD ANYTHING BEFORE THIS IMPORT!
import init  # isort: skip

# Load game
import logging
import threading

import pygame

import scripts.game_structure.screen_settings
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan import Afterlife, clan_class

from scripts.debug_console import debug_mode
from scripts.game_structure import constants, game
from scripts.game_structure.audio import music_manager, sound_manager
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.game_structure.game.save_load import read_clans
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import (
    Switch,
    switch_get_value,
    switch_set_value,
)
from scripts.game_structure.load_cat import load_cats, version_convert
from scripts.game_structure.screen_settings import MANAGER, screen, screen_scale

# import all screens for initialization (Note - must be done after pygame_gui manager is created)
from scripts.screens import all_screens
from scripts.screens.enums import GameScreen
from scripts.ui.windows.save_check import SaveCheckWindow
from scripts.housekeeping.quit_game import quit_game

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load("resources/images/icon.png"))

game.rpc = _DiscordRPC("1076277970060185701", daemon=True)
game.rpc.start()
game.rpc.start_rpc.set()

# LOAD cats & clan
finished_loading = False


def load_data():
    global finished_loading

    # load in the spritesheets
    sprites.load_all()

    clan_list = read_clans()
    if clan_list:
        switch_set_value(Switch.clan_list, clan_list)
        switch_set_value(Switch.clan_name, clan_list[0])
        try:
            game.starclan = Afterlife()
            game.dark_forest = Afterlife()
            load_cats()
            version_info = clan_class.load_clan()
            version_convert(version_info)
            game.load_events()
            scripts.screens.screens_core.screens_core.rebuild_core()
        except Exception as e:
            logging.exception("File failed to load")
            if switch_get_value(Switch.error_message) is None:
                switch_set_value(
                    Switch.error_message, "There was an error loading the cats file!"
                )
                switch_set_value(Switch.traceback, e)

    finished_loading = True


images = []


def loading_animation(scale: float = 1):
    # Load images, adjust color
    color = pygame.Surface((200 * scale, 210 * scale))
    if game_setting_get("dark mode"):
        color.fill(constants.CONFIG["theme"]["light_mode_background"])
    else:
        color.fill(constants.CONFIG["theme"]["dark_mode_background"])

    if len(images) == 0:
        for i in range(1, 11):
            im = pygame.transform.scale_by(
                pygame.image.load(f"resources/images/loading_animate/startup/{i}.png"),
                screen_scale,
            )
            im.blit(color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            images.append(im)
        del im

    # Cleanup
    del color

    x = screen.get_width() / 2
    y = screen.get_height() / 2

    i = 0
    total_frames = len(images)
    while not finished_loading:
        clock.tick(8)  # Loading screen is 8FPS

        if game_setting_get("dark mode"):
            screen.fill(constants.CONFIG["theme"]["dark_mode_background"])
        else:
            screen.fill(constants.CONFIG["theme"]["light_mode_background"])

        screen.blit(
            images[i], (x - images[i].get_width() / 2, y - images[i].get_height() / 2)
        )

        i += 1
        if i >= total_frames:
            i = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game(savesettings=False)

        pygame.display.update()


def load_game():
    """
    Performs the functions needed to load the game.

    This function is ran when the game loads and whenever the player
    switches clans.
    """
    global finished_loading

    game.cur_events_list.clear()
    game.patrol_cats.clear()
    game.patrolled.clear()
    game.updated_afterlife_cats.clear()
    game.clan = None
    game.starclan = None
    game.dark_forest = None
    switch_set_value(Switch.switch_clan, False)

    finished_loading = False
    loading_thread = threading.Thread(target=load_data)
    loading_thread.start()
    loading_animation(screen_scale)

    # loading thread should be done by now, so just join it for safety.
    loading_thread.join()
    del loading_thread


load_game()

pygame.mixer.pre_init(buffer=44100)
try:
    pygame.mixer.init()
except pygame.error:
    print("Failed to initialize sound. Sound will be disabled.")
    music_manager.audio_disabled = True
    music_manager.muted = True
all_screens.get_screen(GameScreen.START).screen_switches()

# dev screen info now lives in scripts/screens/screens_core

fps = switch_get_value(Switch.fps)
music_manager.check_music(GameScreen.START)

if game_setting_get("custom cursor"):
    MANAGER.set_active_cursor(constants.CUSTOM_CURSOR)
else:
    MANAGER.set_active_cursor(constants.DEFAULT_CURSOR)

while 1:
    time_delta = clock.tick(fps) / 1000.0

    if switch_get_value(Switch.switch_clan):
        load_game()

    # Draw screens
    # This occurs before events are handled to stop pygame_gui buttons from blinking.
    game.all_screens[game.current_screen].on_use()
    # EVENTS
    for event in pygame.event.get():
        if (
            event.type == pygame.KEYDOWN
            and game_setting_get("keybinds")
            and debug_mode.debug_menu.visible
        ):
            pass
        else:
            # todo ...shouldn't this be `get_switch(Switch.cur_screen)`?
            all_screens.get_screen(game.current_screen.replace(" ", "_")).handle_event(
                event
            )

        sound_manager.handle_sound_events(event)

        if event.type == pygame.QUIT:
            # Don't display if on the start screen or there is no clan.
            if (
                switch_get_value(Switch.cur_screen)
                in (
                    GameScreen.START,
                    GameScreen.SWITCH_CLAN,
                    GameScreen.SETTINGS,
                    GameScreen.MAKE_CLAN,
                )
                or not game.clan
            ):
                quit_game(savesettings=False)
            else:
                SaveCheckWindow(switch_get_value(Switch.cur_screen), False, None)

        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

            if MANAGER.visual_debug_active:
                _ = pygame.mouse.get_pos()
                if game_setting_get("fullscreen"):
                    print(f"(x: {_[0]}, y: {_[1]})")
                else:
                    print(f"(x: {_[0] * screen_scale}, y: {_[1] * screen_scale})")
                del _

        # F2 turns toggles visual debug mode for pygame_gui, allowed for easier bug fixes.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                MANAGER.print_layer_debug()
            elif event.key == pygame.K_F3:
                debug_mode.toggle_debug_mode()
                # debugmode.toggle_console()
            elif event.key == pygame.K_F11:
                scripts.game_structure.screen_settings.toggle_fullscreen(
                    source_screen=all_screens.screen_dict[
                        switch_get_value(Switch.cur_screen).replace(" ", "_")
                    ],
                    show_confirm_dialog=False,
                )

        MANAGER.process_events(event)

    MANAGER.update(time_delta)

    # update
    game.update_game()
    if game.switch_screens:
        all_screens.get_screen(
            game.last_screen_forupdate.replace(" ", "_")
        ).exit_screen()
        all_screens.get_screen(game.current_screen.replace(" ", "_")).screen_switches()
        game.switch_screens = False
    if (
        not music_manager.audio_disabled
        and not pygame.mixer.music.get_busy()
        and not music_manager.muted
    ):
        music_manager.play_queued()

    debug_mode.pre_update(clock)
    # END FRAME

    MANAGER.draw_ui(screen)

    debug_mode.post_update(screen)

    pygame.display.update()
