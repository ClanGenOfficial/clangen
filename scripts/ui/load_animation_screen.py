import pygame
import threading
from scripts.game_input import controller_manager
from scripts.game_structure import constants
from scripts.game_structure.screen_settings import window
from scripts.housekeeping.quit_game import quit_game

images = []
image_scale = 0

clock = pygame.time.Clock()

FINISHED_LOADING = pygame.event.custom_type()


def loading_animation(scale: float = 1, theme: str = "light", ticks=-1):
    # Load images, adjust color
    global image_scale
    color = pygame.Surface((200 * scale, 210 * scale))
    color.fill(
        constants.CONFIG["theme"][
            ("dark" if theme == "light" else "light") + "_mode_background"
        ]
    )

    if len(images) == 0 or image_scale != scale:
        for i in range(1, 11):
            im = pygame.transform.scale_by(
                pygame.image.load(f"resources/images/loading_animate/startup/{i}.png"),
                scale,
            )
            im.blit(color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            images.append(im)
        del im
        image_scale = scale

    # Cleanup
    del color

    x = window.size[0] / 2
    y = window.size[1] / 2

    i = 0
    total_frames = len(images)

    loading_thread = threading.Thread(target=_queue_thread)
    loading_thread.start()
    while 1:
        clock.tick(8)  # Loading screen is 8FPS

        window.get_surface().fill(constants.CONFIG["theme"][theme + "_mode_background"])

        window.get_surface().blit(
            images[i], (x - images[i].get_width() / 2, y - images[i].get_height() / 2)
        )

        i += 1
        if i >= total_frames:
            i = 0
        window.flip()
        if pygame.event.peek(pygame.QUIT):
            loading_thread.join()
            quit_game(savesettings=False)
        if pygame.event.peek(FINISHED_LOADING):
            pygame.event.clear(FINISHED_LOADING)
            break

        ticks -= 1
        if ticks == 0:
            break
    # loading thread should be done by now, so just join it for safety.
    loading_thread.join()
    del loading_thread


def _queue_thread():
    for event in pygame.event.get():
        controller_manager.process_event(event)
        if event.type == pygame.QUIT:
            quit_game(savesettings=False)
        if event.type == pygame.WINDOWRESIZED:
            from scripts.game_structure.screen_settings import set_display_mode
            from scripts.game_structure.game import Switch
            from scripts.screens import all_screens
            from scripts.game_structure.game import switch_get_value

            set_display_mode(
                source_screen=all_screens.screen_dict[
                    switch_get_value(Switch.cur_screen).replace(" ", "_")
                ],
                show_confirm_dialog=False,
                ingame_switch=True,
            )
            pygame.event.post(pygame.event.Event(FINISHED_LOADING))
            return
