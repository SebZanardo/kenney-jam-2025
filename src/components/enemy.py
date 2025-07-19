from dataclasses import dataclass
from enum import IntEnum, auto


import core.constants as c


class EnemyType(IntEnum):
    NONE = 0

    GROUND = auto()
    FLYING = auto()


@dataclass(slots=True)
class Enemy:
    enemy_type: EnemyType = EnemyType.NONE
    x: float = 0
    y: float = 0

    current_cell_x: int = 0
    current_cell_y: int = 0
    target_cell_x: int = 0
    target_cell_y: int = 0

    health: int = 0


# TODO: Change to array later once enum is stable
enemy_max_health = {
    EnemyType.NONE: 0,
    EnemyType.GROUND: 10,
    EnemyType.FLYING: 10,
}

# TODO: Change to array later once enum is stable
enemy_speed = {
    EnemyType.NONE: 0,
    EnemyType.GROUND: 0.1,
    EnemyType.FLYING: 0.1,
}


MAX_ENEMIES = 100

# Utilising object pooling in a packed array with active count
# No need to order enemies because they path in a flowfield and would
#  get out of order very fast, just need to update all enemies every tick.
enemies = [Enemy() for _ in range(MAX_ENEMIES)]
active_enemies = 0

# These are outside grid
half_height = int(c.GRID_HEIGHT/2)
outside = 30
SPAWN_POS = (-outside, half_height)
GOAL_POS = (c.WINDOW_WIDTH + outside, half_height)

# These are grid tile start
START_POS = (0, half_height)
END_POS = (c.GRID_WIDTH - 1, half_height)


def enemy_spawn(enemy_type: EnemyType) -> bool:
    '''
    Simply add to end of packed array.
    '''
    global active_enemies

    if active_enemies >= MAX_ENEMIES:
        return False

    new_enemy = enemies[active_enemies]
    new_enemy.enemy_type = enemy_type
    new_enemy.x, new_enemy.y = SPAWN_POS

    # (-1, -1) denotes outside grid for either spawn run or goal run
    new_enemy.current_cell_x, new_enemy.current_cell_y = (-1, -1)
    new_enemy.target_cell_x, new_enemy.target_cell_y = START_POS

    new_enemy.health = enemy_max_health[enemy_type]

    active_enemies += 1

    return True


def enemy_remove(i: int) -> None:
    '''
    Swap with last element and reduce active.
    No need to clear out values as will be set when next enemy created
    '''
    global active_enemies

    temp = enemies[i]

    # decrement first so easier end indexing
    active_enemies -= 1

    enemies[i] = enemies[active_enemies]
    enemies[active_enemies] = temp
