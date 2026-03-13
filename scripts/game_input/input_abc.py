import pygame
from scripts.game_input import Action
from typing import Union
from abc import ABC, abstractmethod

class InputManager(ABC):
    """
    Abstract class for input reading.
    """

    @abstractmethod
    def _get_action_from_event(self, event: pygame.Event) -> Union[Action, None]:
        """
        :param event: Event to get corresponding Action of.
        :return: Corresponding Action, or `None` if there's no corresponding Action.
        """

    def _post_action(self, action: Union[Action, None], event: int):
        """
        Posts Action to Pygame events.
        Event should be one of INPUT_ACTION_PRESSED, BUTTON_PRESSED or BUTTON_RELEASED.
        """
        posted_event = pygame.event.Event(event, {"action": action})
        pygame.event.post(posted_event)

    @abstractmethod
    def process_event(self, event: pygame.Event):
        """
        :param event: Pygame Event to process.
        """
