import logging

logger = logging.getLogger(__name__)

import pygame
from pygame._sdl2 import controller

from typing import Literal, Union, Dict
from abc import ABC, abstractmethod

from scripts.game_structure.game.settings import game_setting_get
from scripts.game_input.action import Action
from scripts.game_input import custom_events


class InputManager(ABC):
    """
    Abstract class for input reading.
    """

    def _post_action(self, action: Union[Action, None], event: int):
        """
        Posts Action to Pygame events.
        Event should be one of INPUT_ACTION_PRESSED, INPUT_ACTION_RELEASED.
        """
        posted_event = pygame.event.Event(event, {"action": action})
        pygame.event.post(posted_event)

    @abstractmethod
    def process_event(self, event: pygame.Event):
        """
        :param event: Pygame Event to process.
        """

    @abstractmethod
    def set_action_maps(self, pygame_key_to_action: Dict[int, Action]):
        """
        Remaps controls. Will entirely replace the existing input map with the provided one,
        so watch out.
        :param pygame_key_to_action: Map of Pygame Key events (e.g. pygame.K_DOWN) to Actions
        """


class KeyboardManager(InputManager):
    """
    Input manager for keyboard inputs.
    """

    action_map = {
        pygame.K_ESCAPE: Action.BACK,
        pygame.K_RETURN: Action.CONFIRM,
        pygame.K_LEFT: Action.PREVIOUS,
        pygame.K_RIGHT: Action.NEXT,
        pygame.K_SPACE: Action.SAVE,
        pygame.K_UP: Action.UP,
        pygame.K_DOWN: Action.DOWN,
    }

    def __init__(self):
        pass

    def _get_action_from_event(self, event: pygame.Event) -> Union[Action, None]:
        """
        :param event: Event to get corresponding Action of.
        :return: Corresponding Action, or `None` if there's no corresponding Action.
        """
        return KeyboardManager.action_map.get(event.key)

    def process_event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            action = self._get_action_from_event(event)
            if action:
                self._post_action(action, custom_events.INPUT_ACTION_PRESSED)
        if event.type == pygame.KEYUP and game_setting_get("keybinds"):
            action = self._get_action_from_event(event)
            if action:
                self._post_action(action, custom_events.INPUT_ACTION_RELEASED)

    def set_action_maps(self, pygame_key_to_action: Dict[int, Action]):
        KeyboardManager.action_map = pygame_key_to_action


class ControllerManager(InputManager):
    """
    Input manager for controller inputs.
    """

    # deadzone
    CONTROLLER_DEADZONE = 0.35

    # CONTROLLER LAYOUT FOR XBOX AND PS4:
    #   Y
    # X   B
    #   A
    #
    # CONTROLLER LAYOUT FOR NINTENDO
    #   X
    # Y   A
    #   B
    action_map = {
        pygame.CONTROLLER_BUTTON_A: Action.CONFIRM,
        pygame.CONTROLLER_BUTTON_B: Action.BACK,
        pygame.CONTROLLER_BUTTON_DPAD_UP: Action.UP,
        pygame.CONTROLLER_BUTTON_DPAD_DOWN: Action.DOWN,
        pygame.CONTROLLER_BUTTON_DPAD_LEFT: Action.LEFT,
        pygame.CONTROLLER_BUTTON_DPAD_RIGHT: Action.RIGHT,
        pygame.CONTROLLER_BUTTON_LEFTSHOULDER: Action.PREVIOUS,
        pygame.CONTROLLER_BUTTON_RIGHTSHOULDER: Action.NEXT,
    }

    def __init__(self):
        self.controllers: dict[str, controller.Controller] = {}
        self._last_used_controller: Union[str, None] = None

        self.controller_maps = {}

    def init(self):
        """
        Initializes controller module if that hasn't happened yet.
        Make sure this is called AFTER Pygame is initialized or controllers won't work.
        """
        if not controller.get_init():
            controller.init()

    def get_last_used_controller(self) -> Union[controller.Controller, None]:
        """
        Gets controller that last had had an input event.

        :return: `None` if controller is no longer connected,
        or no controller had any input event.
        """
        return self.controllers.get(self._last_used_controller)

    def _get_action_from_event(self, event: pygame.Event) -> Union[Action, None]:
        """
        :param event: Event to get corresponding Action of.
        :return: Corresponding Action, or `None` if there's no corresponding Action.
        """
        return ControllerManager.action_map.get(event.button)

    def _normalize_axis(
        self, axis_value: int, axis: Literal["joystick", "trigger"]
    ) -> float:
        """
        Normalizes axis value to be [-1, 1] (for joysticks)
        or [0, 1] (for triggers).

        You shouldn't use raw joystick values because they're very noisy, so you should
        call this and then only use it if abs(value) >= CONTROLLER_DEADZONE.

        :param axis_value: Raw axis input value.
        :param axis: Which axis is being used. Either "`joystick`" (thumbstick) or
                    "`trigger`" (L/R).
        """
        # joysticks can return a value between -32768 and 32767.
        if axis == "joystick":
            if axis_value < 0:
                return axis_value / 32768
            else:
                return axis_value / 32767
        # triggers can return a value between 0 and 32768
        else:  # axis == "trigger"
            return axis_value / 32768

    def process_event(self, event: pygame.Event):
        # have to listen for the joydevice events or else you can't get the instance_id
        if event.type == pygame.JOYDEVICEADDED:
            if controller.is_controller(event.device_index):
                new_controller = pygame.joystick.Joystick(event.device_index)
                instance_id = new_controller.get_instance_id()
                self.controllers[instance_id] = controller.Controller.from_joystick(
                    new_controller
                )
                self._last_used_controller = instance_id
                logger.info("Registered controller with instance_id %s", instance_id)
        if event.type == pygame.JOYDEVICEREMOVED:
            if event.instance_id in self.controllers:
                del self.controllers[event.instance_id]
                logger.info(
                    "Deregistered controller with instance_id %s", event.instance_id
                )

        if event.type == pygame.CONTROLLERBUTTONDOWN:
            self._last_used_controller = event.instance_id
            action = self._get_action_from_event(event)
            self._post_action(action, custom_events.INPUT_ACTION_PRESSED)
        if event.type == pygame.CONTROLLERBUTTONUP:
            # don't think people will consider letting go of a button as "using" the controller
            action = self._get_action_from_event(event)
            self._post_action(action, custom_events.INPUT_ACTION_RELEASED)

        if event.type == pygame.CONTROLLERAXISMOTION:
            self._last_used_controller = event.instance_id
            if (
                event.axis == pygame.CONTROLLER_AXIS_TRIGGERLEFT
                or event.axis == pygame.CONTROLLER_AXIS_TRIGGERRIGHT
            ):
                return

            if (
                event.axis == pygame.CONTROLLER_AXIS_LEFTX
                or event.axis == pygame.CONTROLLER_AXIS_RIGHTX
            ):
                normalized_axis_motion = self._normalize_axis(event.value, "joystick")
                if abs(normalized_axis_motion) < ControllerManager.CONTROLLER_DEADZONE:
                    return

                if normalized_axis_motion > 0:
                    self._post_action(Action.RIGHT, custom_events.INPUT_ACTION_PRESSED)
                else:
                    self._post_action(Action.LEFT, custom_events.INPUT_ACTION_PRESSED)

            if (
                event.axis == pygame.CONTROLLER_AXIS_LEFTY
                or event.axis == pygame.CONTROLLER_AXIS_RIGHTY
            ):
                normalized_axis_motion = self._normalize_axis(event.value, "joystick")
                if abs(normalized_axis_motion) < ControllerManager.CONTROLLER_DEADZONE:
                    return

                if normalized_axis_motion > 0:
                    self._post_action(Action.UP, custom_events.INPUT_ACTION_PRESSED)
                else:
                    self._post_action(Action.DOWN, custom_events.INPUT_ACTION_PRESSED)

    def rumble(self, duration, low_freq=0, high_freq=1) -> bool:
        """
        Attempts to rumble the last used controller.

        :param duration: Duration to rumble in milliseconds. 0 will do nothing and return False.
        :param low_freq: Lower bound of rumble frequency. Should be in range [0, 1].
        :param high_freq: Upper bound of rumble frequency. Should be in range [0, 1].
        :return: `True` if rumble attempt was successful.
        """
        if duration == 0:
            return False
        last_used_controller = self.get_last_used_controller()
        if last_used_controller:
            return last_used_controller.rumble(low_freq, high_freq, duration)
        return False

    def set_action_maps(self, pygame_key_to_action: Dict[int, Action]):
        ControllerManager.action_map = pygame_key_to_action

    def set_led(self, color: pygame.Color):
        """
        Attempts to set LED light of the last used controller.

        :param color: Color to set LED light to.
        :return: `True` if LED setting attempt was successful.
        """
        last_used_controller = self.get_last_used_controller()
        if last_used_controller:
            return last_used_controller.set_led(color)
        return False


controller_manager = ControllerManager()
keyboard_manager = KeyboardManager()
