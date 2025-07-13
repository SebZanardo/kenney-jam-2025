import pygame
from enum import IntEnum, auto

import core.constants as c


class InputState(IntEnum):
    NOTHING = 0  # released for >1 frame
    PRESSED = auto()  # just pressed, active for 1 frame
    HELD = auto()  # pressed for >1 frame
    RELEASED = auto()  # just released, active for 1 frame


class MouseButton(IntEnum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class Action(IntEnum):
    LEFT = 0
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    A = auto()
    B = auto()
    SELECT = auto()
    START = auto()


InputBuffer = list[InputState]


def is_pressed(action_buffer: InputBuffer, input_enum: IntEnum) -> bool:
    return action_buffer[input_enum] == InputState.PRESSED


def is_held(action_buffer: InputBuffer, input_enum: IntEnum) -> bool:
    return action_buffer[input_enum] == InputState.HELD


def is_released(action_buffer: InputBuffer, input_enum: IntEnum) -> bool:
    return action_buffer[input_enum] == InputState.RELEASED


def is_nothing(action_buffer: InputBuffer, input_enum: IntEnum) -> bool:
    return action_buffer[input_enum] == InputState.NOTHING


def input_event_queue(action_buffer: InputBuffer) -> bool:
    """
    Pumps the event queue and handles application events
    Returns False if application should terminate, else True
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEWHEEL and not c.IS_WEB:
            if event.y < 0:
                action_buffer[Action.RIGHT] = InputState.PRESSED
            elif event.y > 0:
                action_buffer[Action.LEFT] = InputState.PRESSED

        elif event.type == pygame.WINDOWFOCUSGAINED:
            pygame.mixer.music.unpause()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not c.IS_WEB:
                return False

    return True


def update_action_buffer(
    action_buffer: InputBuffer, last_action_mapping_pressed: list[int]
) -> None:
    # get_just_pressed() and get_just_released() do not work with web ;(
    keys_held = pygame.key.get_pressed()
    for action in Action:
        if action_buffer[action] == InputState.NOTHING:
            # Check if any alternate keys for the action were just pressed
            for mapping in action_mappings[action]:
                if mapping == last_action_mapping_pressed[action]:
                    continue

                # If an alternate key was pressed than last recorded key
                if keys_held[mapping]:
                    # Set that key bind as the current bind to 'track'
                    last_action_mapping_pressed[action] = mapping

        if keys_held[last_action_mapping_pressed[action]]:
            if (
                action_buffer[action] == InputState.NOTHING
                or action_buffer[action] == InputState.RELEASED
            ):
                action_buffer[action] = InputState.PRESSED
            elif action_buffer[action] == InputState.PRESSED:
                action_buffer[action] = InputState.HELD
        else:
            if (
                action_buffer[action] == InputState.PRESSED
                or action_buffer[action] == InputState.HELD
            ):
                action_buffer[action] = InputState.RELEASED
            elif action_buffer[action] == InputState.RELEASED:
                action_buffer[action] = InputState.NOTHING


def update_mouse_buffer(mouse_buffer: InputBuffer) -> None:
    # get_just_pressed() and get_just_released() do not work with web ;(
    mouse_pressed = pygame.mouse.get_pressed()
    for button in MouseButton:
        if mouse_pressed[button]:
            if (
                mouse_buffer[button] == InputState.NOTHING
                or mouse_buffer[button] == InputState.RELEASED
            ):
                mouse_buffer[button] = InputState.PRESSED
            elif mouse_buffer[button] == InputState.PRESSED:
                mouse_buffer[button] = InputState.HELD
        else:
            if (
                mouse_buffer[button] == InputState.PRESSED
                or mouse_buffer[button] == InputState.HELD
            ):
                mouse_buffer[button] = InputState.RELEASED
            elif mouse_buffer[button] == InputState.RELEASED:
                mouse_buffer[button] = InputState.NOTHING


action_mappings = {
    Action.LEFT: [pygame.K_a, pygame.K_LEFT],
    Action.RIGHT: [pygame.K_d, pygame.K_RIGHT],
    Action.UP: [pygame.K_w, pygame.K_UP],
    Action.DOWN: [pygame.K_s, pygame.K_DOWN],
    Action.A: [pygame.K_z, pygame.K_SLASH, pygame.K_k, pygame.K_SPACE],
    Action.B: [pygame.K_x, pygame.K_PERIOD, pygame.K_l],
    Action.SELECT: [pygame.K_LSHIFT, pygame.K_RSHIFT],
    Action.START: [pygame.K_RETURN],
}
