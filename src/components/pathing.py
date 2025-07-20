from queue import deque

import core.constants as c

import components.enemy as e


# how far outside is run
outside = 1 * c.TILE_SIZE

PATH_START_POS = (-outside, c.GRID_HEIGHT / 2)
PATH_END_POS = (c.GRID_WIDTH + outside, PATH_START_POS[1])

# These are grid tile start
PATH_START_TILE = (0, c.GRID_HEIGHT_TILES // 2)
PATH_END_TILE = (c.GRID_WIDTH_TILES - 1, PATH_START_TILE[1])


# Flowfield the enemies path off. Must always be valid path.
flowfield: list[list[int]] = [[-1] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)]

# Flowfield the player can place towers off. It takes into account current
# enemy positions. Expected to be invalid often
placement_flowfield: list[list[int]] = [
    [-1] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)
]

# 2D array for where towers have been placed
collision_grid: list[list[bool]] = [
    [False] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)
]


def pathing_reset() -> None:
    global flowfield, placement_flowfield, collision_grid

    for y in range(c.GRID_HEIGHT_TILES):
        for x in range(c.GRID_WIDTH_TILES):
            flowfield[y][x] = -1
            placement_flowfield[y][x] = -1
            collision_grid[y][x] = False


def flowfield_preview(x: int, y: int) -> bool:
    """
    Returns whether there is a valid path between start and end
    """
    global collision_grid

    if collision_grid[y][x]:
        return True

    collision_grid[y][x] = True
    valid = flowfield_regenerate(placement_flowfield)
    collision_grid[y][x] = False

    return valid


def collision_check(x: int, y: int) -> bool:
    """
    Checks if enemies are on tower or not
    """
    checked = set()

    for i in range(e.active_enemies):
        enemy = e.enemies[i]

        # Skip if already verified this cell
        if (enemy.cx, enemy.cy) in checked:
            continue

        checked.add((enemy.cx, enemy.cy))

        # Cannot place on enemy
        if enemy.x // c.TILE_SIZE == x and enemy.y // c.TILE_SIZE == y:
            return True

    return False


def flowfield_regenerate(field: list[list[int]]) -> bool:
    """
    Returns whether there is a valid path between start and end.
    Flood fill BFS algorithm that starts at end and fills to start
    """

    for y in range(c.GRID_HEIGHT_TILES):
        for x in range(c.GRID_WIDTH_TILES):
            field[y][x] = -1

    complete = False

    q = deque()

    q.append(PATH_END_TILE)
    field[PATH_END_TILE[1]][PATH_END_TILE[0]] = 1  # 1 is right but anything != 0 is fine

    while q:
        for _ in range(len(q)):
            x, y = q.popleft()

            for i, d in enumerate(c.DIRECTIONS):
                dx, dy = d
                nx = x + dx
                ny = y + dy

                if not inside_grid(nx, ny):
                    continue

                # Tower placed on this cell
                if collision_grid[ny][nx]:
                    continue

                # Already been visited
                if field[ny][nx] != -1:
                    continue

                if (nx, ny) == PATH_START_TILE:
                    complete = True
                    # Don't break cause we want to fill everything

                q.append((nx, ny))
                field[ny][nx] = i
    ###########################################################################

    return complete


def flowfield_copy(from_field: list[list[int]], to_field: list[list[int]]) -> None:
    for y in range(c.GRID_HEIGHT_TILES):
        for x in range(c.GRID_WIDTH_TILES):
            to_field[y][x] = from_field[y][x]


def debug_print() -> None:
    print("FLOWFIELD", "#" * 100)
    for row in flowfield:
        buffer = ""
        for v in row:
            buffer += f"{v} "
        print(buffer)

    print("PLACEMENT FLOWFIELD", "#" * 100)
    for row in placement_flowfield:
        buffer = ""
        for v in row:
            buffer += f"{v} "
        print(buffer)

    print("COLLISION_GRID", "#" * 100)
    for row in collision_grid:
        buffer = ""
        for v in row:
            buffer += f"{'#' if v else '.'} "
        print(buffer)


def inside_grid(tx: int, ty: int) -> bool:
    return 0 <= tx < c.GRID_WIDTH_TILES and 0 <= ty < c.GRID_HEIGHT_TILES


def coord_to_tile(x: int, y: int) -> tuple[int, int] | None:
    tx, ty = x // c.TILE_SIZE, y // c.TILE_SIZE
    if inside_grid(tx, ty):
        return (int(tx), int(ty))  # cast to int bc // doesn't actually do it
    else:
        return None
