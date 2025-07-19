import core.constants as c

from components.tower import Tower, TowerType, MAX_TOWER_LEVEL


# kinda emptied this file sorry lol


def inside_grid(x: int, y: int) -> bool:
    return 0 <= x < c.GRID_WIDTH and 0 <= y < c.GRID_HEIGHT
