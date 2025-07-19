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

dt = 1 / c.FPS  # We want fixed dt
mouse_pos = (-1, -1)
last_mouse_pos = (-1, -1)  # for interpolating at low dt

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
FONT = pygame.font.Font(path + "Better VCR 9.0.1.ttf", 11)
DEBUG_FONT = pygame.font.SysFont("monospace", 8)

# Load sprites (png, webp or jpg for web compatibility)
path = "data/textures/"
ICON = pygame.image.load(path + "icon.png")
MENU_BUTTONS = slice_sheet(path + "buttons.png", *c.BUTTON_SIZE)
PATTERNS = pygame.image.load(path + "patterns.png")
ONE_BIT_COLOR = pygame.image.load(path + "1bit-coloured.png")

# I made a new folder for custom textures so we can keep track
# of what was downloaded from Kenney directly and what was compiled
# into new spritesheets. I also put the Aseprite source files there.
path = "data/textures-src/"
TERRAIN = slice_sheet(path + "terrain.png", 16, 16)
HANDS = slice_sheet(path + "hands.png", 16, 16)
TOWERS = slice_sheet(path + "towers.png", 16, 16)
WIRES = slice_sheet(path + "wires.png", 16, 16)
ENEMIES = slice_sheet(path + "enemies.png", 16, 16)
BLENDING_FX = slice_sheet(path + "blending-fx.png", 16, 16)

# Load audio (ogg for web compatibility)
path = "data/sfx/"
HOVER_SFX = pygame.mixer.Sound(path + "hover.ogg")
SELECT_SFX = pygame.mixer.Sound(path + "select.ogg")

NINTENDO_MUSIC = "data/music/theme.ogg"
