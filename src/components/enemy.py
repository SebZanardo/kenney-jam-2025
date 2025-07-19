import math
from dataclasses import dataclass
from enum import IntEnum, auto

import core.globals as g
import core.constants as c

from components.pathing import (
    SPAWN_POS, START_POS, GOAL_POS, END_POS, flowfield
)
from components.player import player
from components.camera import camera_to_screen


class EnemyType(IntEnum):
    NONE = 0

    GROUND_WEAK = auto()
    GROUND_FAST = auto()
    GROUND_HEAVY = auto()
    # FLYING = auto()  # TODO: Implement


@dataclass(slots=True)
class Enemy:
    enemy_type: EnemyType = EnemyType.NONE
    x: int = 0
    y: int = 0

    cx: int = 0
    cy: int = 0

    health: int = 0


# TODO: Change to array later once enum is stable
enemy_max_health = {
    EnemyType.NONE: 0,
    EnemyType.GROUND_WEAK: 10,
    EnemyType.GROUND_FAST: 15,
    EnemyType.GROUND_HEAVY: 50,
}

# TODO: Change to array later once enum is stable
# NOTE: Values must be a unit fraction 1/X
enemy_speed = {
    EnemyType.NONE: 0,
    EnemyType.GROUND_WEAK: 0.1,
    EnemyType.GROUND_FAST: 0.2,
    EnemyType.GROUND_HEAVY: 0.05,
}


MAX_ENEMIES = 100

# Utilising object pooling in a packed array with active count
# No need to order enemies because they path in a flowfield and would
#  get out of order very fast, just need to update all enemies every tick.
enemies = [Enemy() for _ in range(MAX_ENEMIES)]
active_enemies = 0
enemy_health_multiplier = 1


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
    new_enemy.cx, new_enemy.cy = SPAWN_POS

    new_enemy.health = enemy_max_health[enemy_type] * enemy_health_multiplier

    active_enemies += 1
    print("Spawned: ", enemy_type)

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

    print("Removed: ", i)


def enemy_update(i: int) -> bool:
    '''
    Moves enemy toward target by speed
    If target reached, find next target --> if at END_POS then GOAL_POS
    If dead then remove

    RETURN: whether died, because if died then dont increment i for next
    '''
    e = enemies[i]

    # Dead then no need to update
    if e.health <= 0:
        return True

    speed = enemy_speed[e.enemy_type]

    # Travelling to start
    if (e.cx, e.cy) == SPAWN_POS:
        e.x += speed  # Move to right
        if int(e.x) == START_POS[0] and int(e.y) == START_POS[1]:
            e.cx, e.cy = START_POS

    # Travelling to goal
    elif (e.cx, e.cy) == END_POS:
        e.x += speed  # Move to right
        if int(e.x) == GOAL_POS[0] and int(e.y) == GOAL_POS[1]:
            # Hurt player
            player.health -= 1
            return True

    # Reached next cell pos
    else:
        # Move e.x and e.y
        dx, dy = c.DIRECTION_OPPOSITES[flowfield[e.cy][e.cx]]

        e.x += dx * speed
        e.y += dy * speed

        # TODO: there is a bug here and i don't know how to fix
        rx = int(e.x)
        ry = int(e.y)

        if rx != e.cx or rx != e.cy:
            e.cx = rx
            e.cy = ry

    return False


def enemy_render(i: int) -> None:
    e = enemies[i]

    rx = (e.x) * c.TILE_SIZE
    ry = (e.y) * c.TILE_SIZE

    g.window.blit(
        g.ENEMIES[e.enemy_type.value - 1],
        camera_to_screen(g.camera, rx, ry)
    )
