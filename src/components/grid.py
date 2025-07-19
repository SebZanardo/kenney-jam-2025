from components.ui import Pos
import core.constants as c

from components.tower import Tower, TowerType, MAX_TOWER_LEVEL


# kinda emptied this file sorry lol


def inside_grid(tx: int, ty: int) -> bool:
    return 0 <= tx < c.GRID_WIDTH_TILES and 0 <= ty < c.GRID_HEIGHT_TILES


def coord_to_tile(x: int, y: int) -> Pos | None:
    tx, ty = x // c.TILE_SIZE, y // c.TILE_SIZE
    if inside_grid(tx, ty):
        return (int(tx), int(ty))  # cast to int bc // doesn't actually do it
    else:
        return None
