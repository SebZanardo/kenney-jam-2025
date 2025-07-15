import pygame

import core.assets as a

from components.statemachine import StateMachine


# Pygame Globals
# NOTE: These get initialised in setup. Typehints should help with autocomplete
window: pygame.Window = None
clock: pygame.time.Clock = None

scene_manager: StateMachine = None

mouse_buffer = None
action_buffer = None
last_action_pressed = None

fonts: a.Fonts = None
sprites: a.Sprites = None
sfx: a.Sfx = None

settings = None


# User settings
default_settings = {
    "music": 50,
    "sfx": 30,
    "fullscreen": False,
    "vsync": True,
    "screenshake": True,
}

settings = default_settings.copy()


# Dev settings
pass
