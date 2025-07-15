from dataclasses import dataclass
import pygame

import core.constants as c
import core.globals as g

from utilities.sprite import slice_sheet


# NOTE: These get filled out at runtime, after window is initialised
@dataclass(slots=True)
class Fonts:
    FONT: pygame.Font = None


@dataclass(slots=True)
class Sprites:
    ICON: pygame.Surface = None
    MENU_BUTTONS: list[pygame.Surface] = None


@dataclass(slots=True)
class Sfx:
    HOVER: pygame.Sound = None
    SELECT: pygame.Sound = None


def load_fonts() -> None:
    path = "data/fonts/"

    # Load fonts (ttf for web compatibility)
    g.fonts.FONT = pygame.font.Font(path + "joystix.ttf", 10)


def load_sprites() -> None:
    path = "data/textures/"

    # Load sprites (png, webp or jpg for web compatibility)
    g.sprites.ICON = pygame.image.load(path + "icon.png")
    g.sprites.MENU_BUTTONS = slice_sheet(path + "buttons.png", *c.BUTTON_SIZE)


def load_sfx() -> None:
    path = "data/sfx/"

    # Load audio (ogg for web compatibility)
    g.sfx.HOVER = pygame.mixer.Sound(path + "hover.ogg")
    g.sfx.SELECT = pygame.mixer.Sound(path + "select.ogg")
