import sys
import pygame

# Pygame constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

WINDOW_SETUP = {
    "size": WINDOW_SIZE,
    "flags": pygame.SCALED | pygame.RESIZABLE,
    "depth": 0,
    "display": 0,
    "vsync": 1,
}

CAPTION = "POWER defence"
FPS = 30  # 0 = Uncapped -> let VSYNC decide best tick speed if enabled
# NOTE: Capped at 30FPS on mobile so that is our fixed update

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
HORIZONTAL = (LEFT, RIGHT)
VERTICAL = (UP, DOWN)
INVERTED_DIRECTIONS = {UP: DOWN, LEFT: RIGHT, RIGHT: LEFT, DOWN: UP}

DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))

# Size constants
TILE_SIZE = 32
GRID_WIDTH_TILES, GRID_HEIGHT_TILES = 16, 9
GRID_WIDTH, GRID_HEIGHT = GRID_WIDTH_TILES * TILE_SIZE, GRID_HEIGHT_TILES * TILE_SIZE
