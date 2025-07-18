import sys
import pygame

# Pygame constants
WINDOW_WIDTH = 540
WINDOW_HEIGHT = 360
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_CENTRE = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

WINDOW_SETUP = {
    "size": WINDOW_SIZE,
    "flags": pygame.SCALED | pygame.RESIZABLE,
    "depth": 0,
    "display": 0,
    "vsync": 1,
}

CAPTION = "kenney-jam-2025"
FPS = 0  # 0 = Uncapped -> let VSYNC decide best tick speed if enabled
# NOTE: if this is 60 then phone will be 1/2 speed as capped at 30FPS
MAX_DT = 1 / 60

IS_WEB = sys.platform == "emscripten"

# Colour constants
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
RED = pygame.Color(255, 0, 0)
YELLOW = pygame.Color(255, 255, 0)
GREEN = pygame.Color(0, 255, 0)
CYAN = pygame.Color(0, 255, 255)
BLUE = pygame.Color(0, 0, 255)
MAGENTA = pygame.Color(255, 0, 255)

# Direction constants
UP = "up"
LEFT = "left"
RIGHT = "right"
DOWN = "down"

# Size constants
BUTTON_SIZE = (96, 16)
TILE_SIZE = 16  # can easily be changed to 32x32
GRID_WIDTH_TILES, GRID_HEIGHT_TILES = 28, 18
GRID_WIDTH, GRID_HEIGHT = GRID_WIDTH_TILES * TILE_SIZE, GRID_HEIGHT_TILES * TILE_SIZE
