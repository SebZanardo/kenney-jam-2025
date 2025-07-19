import core.constants as c


# These are outside grid
half_height = int(c.GRID_HEIGHT/2)
outside = 30
SPAWN_POS = (-outside, half_height)
GOAL_POS = (c.WINDOW_WIDTH + outside, half_height)

# These are grid tile start
START_POS = (0, half_height)
END_POS = (c.GRID_WIDTH - 1, half_height)


flowfield: list[list[float]] = [
    [0.0] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)
]
collision_grid: list[list[bool]] = [
    [False] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)
]


def pathing_reset() -> None:
    global flowfield, collision_grid

    flowfield = [
        [0.0] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)
    ]

    collision_grid = [
        [False] * c.GRID_WIDTH_TILES for _ in range(c.GRID_HEIGHT_TILES)
    ]


def debug_print() -> None:
    print("FLOWFIELD", "#" * 100)
    for row in flowfield:
        buffer = ''
        for v in row:
            buffer += (f"{v} ")
        print(buffer)

    print("COLLISION_GRID", "#" * 100)
    for row in collision_grid:
        buffer = ''
        for v in row:
            buffer += (f"{'#' if v else '.'} ")
        print(buffer)


debug_print()
