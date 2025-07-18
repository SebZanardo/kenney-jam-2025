import pygame

import core.constants as c


def slice_sheet(path: str, sprite_width: int, sprite_height: int) -> list[pygame.Surface]:
    sprite_sheet = pygame.image.load(path)
    rows = int(sprite_sheet.get_height() / sprite_height)
    columns = int(sprite_sheet.get_width() / sprite_width)

    sprites = []
    for y in range(rows):
        for x in range(columns):
            sprites.append(
                get_sprite_from_sheet(
                    sprite_sheet,
                    x * sprite_width,
                    y * sprite_height,
                    sprite_width,
                    sprite_height,
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
