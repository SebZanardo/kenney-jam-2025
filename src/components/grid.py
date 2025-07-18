import core.constants as c

from components.tower import Tower, TowerType


# NOTE: really liking these locally scoped globals
# We should try and do this more when applicable


# All towers objects created upon start, just update their values at runtime
grid = [[Tower()] * c.GRID_WIDTH for _ in range(c.GRID_HEIGHT)]

# This is helpful for me --> will improve performance cause not referencing
# object members all the time
collision_grid = [[False] * c.GRID_WIDTH for _ in range(c.GRID_HEIGHT)]


def inside_grid(x: int, y: int) -> bool:
    return x < c.GRID_WIDTH and x >= 0 and y < c.GRID_HEIGHT and y >= 0


def place_tower(tower_type: TowerType, x: int, y: int) -> bool:
    if not inside_grid(x, y):
        return False

    cell = grid[y][x]
    if cell.tower_type != TowerType.NONE:
        # Check for upgrade
        pass

    else:
        # Place level 1 tower
        # TODO: Call some
        grid[y][x].tower_type = tower_type


def sell_tower(x: int, y: int) -> bool:
    return False
