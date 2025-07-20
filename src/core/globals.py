import copy
import platform
import pygame

from components.camera import Camera
import core.constants as c
from components.statemachine import StateMachine

from utilities.sprite import dim_sprite, invert_sprite, load_image, load_spritesheet


def _setup_window() -> pygame.Surface:
    if c.IS_WEB:
        platform.window.canvas.style.imageRendering = "pixelated"
        return pygame.display.set_mode(c.WINDOW_SETUP["size"])
    else:
        return pygame.display.set_mode(**c.WINDOW_SETUP)


pygame.init()

# Pygame Globals
window = _setup_window()
clock = pygame.time.Clock()

scene_manager = StateMachine()

dt = 1 / c.FPS  # We want fixed dt
mouse_pos = (-1, -1)
last_mouse_pos = (-1, -1)  # for interpolating at low dt

mouse_buffer = None
action_buffer = None
last_action_pressed = None

camera: Camera | None = None

# User settings
default_setting_params = {
    "music": [30],
    "sfx": [50],
    "screenshake": [True],
}

setting_params = copy.deepcopy(default_setting_params)

# Dev settings
pass

# Load fonts (ttf for web compatibility)
path = "data/fonts/"
FONT = pygame.font.Font(path + "Better VCR 9.0.1.ttf", 16)
FONT_LARGE = pygame.font.Font(path + "Better VCR 9.0.1.ttf", 32)
DEBUG_FONT = pygame.font.SysFont("monospace", 8)

# Load sprites (png, webp or jpg for web compatibility)
path = "data/textures/"
ICON = pygame.image.load(path + "icon.png").convert_alpha()
PATTERNS = load_image(path + "patterns.png").convert_alpha()

# I made a new folder for custom textures so we can keep track
# of what was downloaded from Kenney directly and what was compiled
# into new spritesheets. I also put the Aseprite source files there.
path = "data/textures-src/"
TERRAIN = load_spritesheet(path + "terrain.png", 16, 16)
HANDS = load_spritesheet(path + "hands.png", 16, 16, double_size=False)
ICONS = load_spritesheet(path + "icons.png", 16, 16, double_size=False)
TOWERS = load_spritesheet(path + "towers.png", 16, 16)
WIRES = load_spritesheet(path + "wires.png", 16, 16)
ENEMIES = load_spritesheet(path + "enemies.png", 16, 16)
BLENDING_FX = load_spritesheet(path + "blending-fx.png", 16, 16)
PARTICLES = load_spritesheet(path + "particles.png", 8, 8)
BUTTONS: list[pygame.Surface] = []
for surf in load_spritesheet(path + "buttons.png", 16, 16):
    BUTTONS.append((dim_sprite(surf), surf))
BUTTONS_INV: list[pygame.Surface] = []
for dim, surf in BUTTONS:
    inv = invert_sprite(surf)
    BUTTONS_INV.append((dim_sprite(inv), inv))
BIG_BUTTONS: list[pygame.Surface] = []
for surf in load_spritesheet(path + "big-buttons.png", 128, 32, double_size=False):
    BIG_BUTTONS.append((dim_sprite(surf), surf))
RADIUS = pygame.image.load(path + "radius.png").convert_alpha()
LOGO = pygame.image.load(path + "logo.png").convert_alpha()
LOGO = pygame.transform.scale_by(LOGO, 2)

# Load audio (ogg for web compatibility)
path = "data/sfx/"
HOVER_SFX = pygame.mixer.Sound(path + "hover.ogg")
SELECT_SFX = pygame.mixer.Sound(path + "select.ogg")

path = "data/music/"
NINTENDO_MUSIC = path + "theme.ogg"
GAME_MUSIC = path + "The Spirit of the Forest OGG.ogg"
