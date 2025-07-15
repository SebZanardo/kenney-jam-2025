import pygame

import core.assets as a
import core.input as i

from components.statemachine import Statemachine


# Pygame Globals
# NOTE: These get initialised in setup. Typehints should help with autocomplete
window: pygame.Window = None
clock: pygame.time.Clock = None

scene_manager: Statemachine = None

mouse_buffer: i.InputBuffer = None
action_buffer: i.InputBuffer = None
last_action_pressed: list[i.Action] = None

fonts: a.Font = None
sprites: a.Sprites = None
sfx: a.Sfx = None

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
