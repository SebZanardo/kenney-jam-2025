import core.constants as c


# These are outside grid
half_height = int(c.GRID_HEIGHT/2)
outside = 30
SPAWN_POS = (-outside, half_height)
GOAL_POS = (c.WINDOW_WIDTH + outside, half_height)

# These are grid tile start
START_POS = (0, half_height)
END_POS = (c.GRID_WIDTH - 1, half_height)
