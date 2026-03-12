import logging
logger = logging.getLogger(__name__)

import pygame

from typing import Union

from scripts.game_structure.game.settings import game_setting_get
from scripts.game_input.action import Action
from scripts.game_input import custom_events


action_map = {
    pygame.K_z: Action.CONFIRM,
    pygame.K_x: Action.BACK,
    pygame.K_UP: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT,
}

class KeyboardManager:
    def __init__(self):
        pass

    def _get_action_from_event(self, event: pygame.Event) -> Union[Action, None]:
        """
        :param event: Event to get corresponding Action of.
        :return: Corresponding Action, or `None` if there's no corresponding Action.
        """
        return action_map.get(event.button)

    def _post_action(self, action: Union[Action, None], event: int):
        """
        Posts Action to Pygame events.
        Event should be one of INPUT_ACTION_PRESSED, BUTTON_PRESSED or BUTTON_RELEASED.
        """
        posted_event = pygame.event.Event(event, {"action": action})
        pygame.event.post(posted_event)

    def process_event(self, event: pygame.Event):
        """
        :param event: Pygame Event to process.
        """
        if event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            action = self._get_action_from_event(event)
            if action:
                self._post_action(action, custom_events.INPUT_ACTION_PRESSED)

keyboard_manager = KeyboardManager()
