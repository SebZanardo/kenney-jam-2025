import math
from components.player import GameMode, SpeedType, player, player_reset
from dataclasses import dataclass
from enum import IntEnum, auto

import pygame

import core.globals as g
import core.constants as c

from components.pathing import (
    PATH_START_POS,
    PATH_START_TILE,
    PATH_END_POS,
    PATH_END_TILE,
    flowfield,
)
import components.player as p
from components.camera import camera_to_screen
from utilities.math import clamp


class EnemyType(IntEnum):
    NONE = 0

    GROUND_WEAK = auto()
    GROUND_FAST = auto()
    GROUND_HEAVY = auto()
    # FLYING = auto()  # TODO: Implement


@dataclass(slots=True)
class Enemy:
    enemy_type: EnemyType = EnemyType.NONE
    x: float = 0
    y: float = 0

    # cell x, cell y
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
    """
    Simply add to end of packed array.
    """
    global active_enemies

    if active_enemies >= MAX_ENEMIES:
        return False

    new_enemy = enemies[active_enemies]
    new_enemy.enemy_type = enemy_type
    new_enemy.x, new_enemy.y = PATH_START_POS

    new_enemy.cx, new_enemy.cy = PATH_START_POS

    new_enemy.health = enemy_max_health[enemy_type] * enemy_health_multiplier

    active_enemies += 1

    return True


def enemy_remove(i: int) -> None:
    """
    Swap with last element and reduce active.
    No need to clear out values as will be set when next enemy created
    """
    global active_enemies

    temp = enemies[i]

    # decrement first so easier end indexing
    active_enemies -= 1

    enemies[i] = enemies[active_enemies]
    enemies[active_enemies] = temp


def enemy_update(i: int) -> bool:
    """
    Moves enemy toward target by speed
    If target reached, find next target --> if at END_POS then GOAL_POS
    If dead then remove

    RETURN: whether died, because if died then dont increment i for next
    """
    e = enemies[i]

    # Dead then no need to update
    if e.health <= 0:
        return True

    speed = enemy_speed[e.enemy_type] * c.TILE_SIZE

    # Travelling to start
    if (e.cx, e.cy) == PATH_START_POS:
        e.x += speed
        # Reached start of map
        if e.x >= PATH_START_TILE[0] * c.TILE_SIZE:
            e.cx, e.cy = PATH_START_TILE

    # Travelling to goal
    elif (e.cx, e.cy) == PATH_END_TILE:
        e.x += speed
        # Reached end of screen
        if e.x >= PATH_END_POS[0]:
            p.player.health -= 1
            g.camera.trauma = 0.3
            e.health = 0  # Set to dead so tower can see that it died
            return True

    # Reached next cell pos
    else:
        # Move e.x and e.y
        d = flowfield[e.cy][e.cx]
        if d == -1:
            print("Oh shit something went wrong with pathing")
            pygame.quit()

        dx, dy = c.DIRECTIONS[d]
        dx, dy = -dx, -dy

        e.x += dx * speed
        e.y += dy * speed

        rx, ry = round(e.x), round(e.y)
        # add to rx and ry to account for the size of the enemy
        if dx > 0:  # going right
            rx -= c.TILE_SIZE // 2
        if dy < 0:  # going up
            ry += c.TILE_SIZE // 2
        elif dy > 0:  # going down
            ry -= c.TILE_SIZE // 2

        e.cx = clamp(rx // c.TILE_SIZE, 0, c.GRID_WIDTH_TILES - 1)
        e.cy = clamp(ry // c.TILE_SIZE, 0, c.GRID_HEIGHT_TILES - 1)

    return False


def enemy_render(i: int) -> None:
    e = enemies[i]

    g.window.blit(
        g.ENEMIES[e.enemy_type.value - 1],
        camera_to_screen(g.camera, e.x - c.TILE_SIZE // 2, e.y - c.TILE_SIZE // 2),
    )
