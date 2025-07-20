import pygame

import core.constants as c


def load_image(path: str, *, double_size=True) -> pygame.Surface:
    return pygame.transform.scale_by(pygame.image.load(path), 2 if double_size else 1)


def load_spritesheet(
    path: str, sprite_width: int, sprite_height: int, *, double_size=True
) -> list[pygame.Surface]:
    sprite_sheet = load_image(path, double_size=double_size)
    factor = 2 if double_size else 1
    rows = sprite_sheet.get_height() // (sprite_height * factor)
    columns = sprite_sheet.get_width() // (sprite_width * factor)

    sprites = []
    for y in range(rows):
        for x in range(columns):
            sprites.append(
                get_sprite_from_sheet(
                    sprite_sheet,
                    x * sprite_width * factor,
                    y * sprite_height * factor,
                    sprite_width * factor,
                    sprite_height * factor,
                )
            )

    return sprites


def get_sprite_from_sheet(
    sprite_sheet: pygame.Surface, x: int, y: int, width: int, height: int
) -> pygame.Surface:
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    sprite.blit(sprite_sheet, (0, 0), (x, y, width, height))
    sprite = sprite.convert_alpha()

    return sprite


def dim_sprite(surf: pygame.Surface, value: float = 0.8) -> pygame.Surface:
    dim = surf.copy()
    dim.fill((value * 255, value * 255, value * 255, 255), special_flags=pygame.BLEND_MULT)
    return dim


def invert_sprite(surf: pygame.Surface) -> pygame.Surface:
    inv = pygame.Surface(surf.get_size(), surf.get_flags(), surf.get_bitsize())
    inv.fill((255, 255, 255, 255))
    inv.blit(surf, special_flags=pygame.BLEND_SUB)
    return inv


def gray_sprite(surf: pygame.Surface, value: float = 0.5) -> pygame.Surface:
    gray = surf.copy()
    gray.fill((0, 0, 0, 255), special_flags=pygame.BLEND_MULT)
    gray.fill((value * 255, value * 255, value * 255, 0), special_flags=pygame.BLEND_ADD)
    return gray


# rotates a sprite to match the given direction, assuming it is initially facing up
def rotate_sprite(sprite: pygame.Surface, new_direction: str) -> pygame.Surface:
    if new_direction == c.UP:
        return sprite
    if new_direction == c.LEFT:
        return pygame.transform.rotate(sprite, 90)
    if new_direction == c.RIGHT:
        return pygame.transform.rotate(sprite, -90)
    if new_direction == c.DOWN:
        return pygame.transform.flip(sprite, False, True)
    assert False
