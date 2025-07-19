import core.constants as c

from components.tower import Tower, TowerType, MAX_TOWER_LEVEL


# NOTE: really liking these locally scoped globals
# We should try and do this more when applicable

# All towers objects created upon start, just update their values at runtime
grid = [[Tower()] * c.GRID_WIDTH for _ in range(c.GRID_HEIGHT)]

# This is helpful for me --> will improve performance cause not referencing
# object members all the time
collision_grid = [[False] * c.GRID_WIDTH for _ in range(c.GRID_HEIGHT)]


def inside_grid(x: int, y: int) -> bool:
    return x < c.GRID_WIDTH and x >= 0 and y < c.GRID_HEIGHT and y >= 0


def tower_buy(tower_type: TowerType, x: int, y: int) -> bool:
    if not inside_grid(x, y):
        return False

    cell = grid[y][x]
    if cell.tower_type != TowerType.NONE and tower_type == cell.tower_type:
        if grid[y][x].level < MAX_TOWER_LEVEL:
            grid[y][x].level += 1
            tower_init(x, y)
            collision_grid[y][x] = True
            return True

        else:
            return False

    else:
        # Place level 1 tower
        grid[y][x].tower_type = tower_type
        tower_init(x, y)
        collision_grid[y][x] = True
        return True

    return False


def tower_sell(x: int, y: int) -> bool:
    tower_init(x, y)
    collision_grid[y][x] = False
    return False


def tower_init(x: int, y: int) -> None:
    '''
    This function will handle clean up logic when a tower changes
    - level
    - is sold
    - is placed
    '''
    return
