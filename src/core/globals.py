import copy
import platform
import pygame

import core.constants as c

from components.statemachine import StateMachine

from utilities.sprite import slice_sheet


def setup_window() -> pygame.Surface:
    if c.IS_WEB:
        platform.window.canvas.style.imageRendering = "pixelated"
        return pygame.display.set_mode(c.WINDOW_SETUP["size"])
    else:
        return pygame.display.set_mode(**c.WINDOW_SETUP)


pygame.init()

# Pygame Globals
window = setup_window()
clock = pygame.time.Clock()

scene_manager = StateMachine()

mouse_buffer = []
action_buffer = []
last_action_pressed = []

dt = 0.0
mouse_pos = (-1, -1)

mouse_buffer = None
action_buffer = None
last_action_pressed = None

# User settings
default_setting_params = {
    "music": [50],
    "sfx": [30],
    "screenshake": [True],
}

setting_params = copy.deepcopy(default_setting_params)

# Dev settings
pass

# Load fonts (ttf for web compatibility)
path = "data/fonts/"
FONT = pygame.font.Font(path + "Better VCR 9.0.1.ttf", 16)

# Load sprites (png, webp or jpg for web compatibility)
path = "data/textures/"
ICON = pygame.image.load(path + "icon.png")
MENU_BUTTONS = slice_sheet(path + "buttons.png", *c.BUTTON_SIZE)
ONE_BIT_COLOR = pygame.image.load(path+"1bit-coloured.png")

# Load audio (ogg for web compatibility)
path = "data/sfx/"
HOVER_SFX = pygame.mixer.Sound(path + "hover.ogg")
SELECT_SFX = pygame.mixer.Sound(path + "select.ogg")

NINTENDO_MUSIC = "data/music/theme.ogg"
