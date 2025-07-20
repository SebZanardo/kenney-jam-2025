import pygame
from enum import IntEnum, auto

import core.constants as c
import core.globals as g


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


def input_init() -> None:
    g.mouse_buffer = [InputState.NOTHING for _ in MouseButton]
    g.action_buffer = [InputState.NOTHING for _ in Action]
    g.last_action_pressed = [action_mappings[a][0] for a in Action]


def mouse_pressed(button: MouseButton = MouseButton.LEFT) -> bool:
    return g.mouse_buffer[button] == InputState.PRESSED


def mouse_held(button: MouseButton = MouseButton.LEFT) -> bool:
    return g.mouse_buffer[button] == InputState.HELD


def mouse_released(button: MouseButton = MouseButton.LEFT) -> bool:
    return g.mouse_buffer[button] == InputState.RELEASED


def mouse_nothing(button: MouseButton = MouseButton.LEFT) -> bool:
    return g.mouse_buffer[button] == InputState.NOTHING


def is_pressed(action: Action) -> bool:
    return g.action_buffer[action] == InputState.PRESSED


def is_held(action: Action) -> bool:
    return g.action_buffer[action] == InputState.HELD


def is_released(action: Action) -> bool:
    return g.action_buffer[action] == InputState.RELEASED


def is_nothing(action: Action) -> bool:
    return g.action_buffer[action] == InputState.NOTHING


def input_event_queue() -> bool:
    """
    Pumps the event queue and handles application events
    Returns False if application should terminate, else True
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEWHEEL and not c.IS_WEB:
            if event.y < 0:
                g.action_buffer[Action.RIGHT] = InputState.PRESSED
            elif event.y > 0:
                g.action_buffer[Action.LEFT] = InputState.PRESSED

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not c.IS_WEB:
                return False

    return True


def update_action_buffer() -> None:
    # get_just_pressed() and get_just_released() do not work with web ;(
    keys_held = pygame.key.get_pressed()
    for action in Action:
        if g.action_buffer[action] == InputState.NOTHING:
            # Check if any alternate keys for the action were just pressed
            for mapping in action_mappings[action]:
                if mapping == g.last_action_pressed[action]:
                    continue

                # If an alternate key was pressed than last recorded key
                if keys_held[mapping]:
                    # Set that key bind as the current bind to 'track'
                    g.last_action_pressed[action] = mapping

        if keys_held[g.last_action_pressed[action]]:
            if (
                g.action_buffer[action] == InputState.NOTHING
                or g.action_buffer[action] == InputState.RELEASED
            ):
                g.action_buffer[action] = InputState.PRESSED
            elif g.action_buffer[action] == InputState.PRESSED:
                g.action_buffer[action] = InputState.HELD
        else:
            if (
                g.action_buffer[action] == InputState.PRESSED
                or g.action_buffer[action] == InputState.HELD
            ):
                g.action_buffer[action] = InputState.RELEASED
            elif g.action_buffer[action] == InputState.RELEASED:
                g.action_buffer[action] = InputState.NOTHING


def update_mouse_buffer() -> None:
    # get_just_pressed() and get_just_released() do not work with web ;(
    mouse_pressed = pygame.mouse.get_pressed()
    for button in MouseButton:
        if mouse_pressed[button]:
            if (
                g.mouse_buffer[button] == InputState.NOTHING
                or g.mouse_buffer[button] == InputState.RELEASED
            ):
                g.mouse_buffer[button] = InputState.PRESSED
            elif g.mouse_buffer[button] == InputState.PRESSED:
                g.mouse_buffer[button] = InputState.HELD
        else:
            if (
                g.mouse_buffer[button] == InputState.PRESSED
                or g.mouse_buffer[button] == InputState.HELD
            ):
                g.mouse_buffer[button] = InputState.RELEASED
            elif g.mouse_buffer[button] == InputState.RELEASED:
                g.mouse_buffer[button] = InputState.NOTHING


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
