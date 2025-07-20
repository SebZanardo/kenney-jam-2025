from dataclasses import dataclass
from enum import IntEnum
import random

import pygame

from components.animation import (
    Animation,
    Animator,
    animator_get_frame,
    animator_initialise,
    animator_update,
)
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
    # ground
    GROUND = 0
    GROUND_FAST = 1
    GROUND_HEAVY = 2
    GROUND_HEAVY_FAST = 3
    GROUND_SUPER_HEAVY = 4

    # flying
    FLYING = 5
    FLYING_FAST = 6
    FLYING_HEAVY = 7


@dataclass(slots=True)
class Enemy:
    type: EnemyType = EnemyType.GROUND
    x: float = 0
    y: float = 0

    # cell x, cell y
    cx: int = 0
    cy: int = 0

    health: int = 0

    # visual
    direction: str = c.RIGHT
    animator: Animator | None = None


@dataclass(frozen=True)
class EnemyStat:
    health: int
    reward: int
    speed: float
    size: float
    flying: bool

    # visual
    anim_length: int
    anim_speed: float
    anim_rotate: bool


ENEMY_STATS = [
    # EnemyType.GROUND
    EnemyStat(10, 1, 0.1, 1, False, 4, 1, False),
    # EnemyType.GROUND_FAST
    EnemyStat(15, 2, 0.2, 1, False, 2, 1, True),
    # EnemyType.GROUND_HEAVY
    EnemyStat(50, 3, 0.05, 1.5, False, 2, 2, True),
    # EnemyType.GROUND_HEAVY_FAST
    EnemyStat(100, 5, 0.1, 1.5, False, 2, 1, False),
    # EnemyType.GROUND_SUPER_HEAVY
    EnemyStat(300, 10, 0.025, 2, False, 2, 5, False),
    # EnemyType.FLYING
    EnemyStat(10, 1, 0.1, 1, True, 2, 1, False),
    # EnemyType.FLYING_FAST
    EnemyStat(15, 2, 0.2, 1, True, 2, 1, True),
    # EnemyType.FLYING_HEAVY
    EnemyStat(50, 3, 0.05, 1.5, True, 2, 1, False),
]

# Load animations once here
ENEMY_ANIMATIONS: list[Animation] = []

for enemy_type in EnemyType:
    start = enemy_type.value
    stat = ENEMY_STATS[enemy_type.value]
    animation = Animation(
        [
            pygame.transform.scale_by(frame, stat.size)
            for frame in g.ENEMIES[start * 4 : start * 4 + stat.anim_length]
        ],
        0.1 * stat.anim_speed,
    )
    ENEMY_ANIMATIONS.append(animation)


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

    stat = ENEMY_STATS[enemy_type]

    new_enemy = enemies[active_enemies]
    new_enemy.type = enemy_type

    new_enemy.x, new_enemy.y = PATH_START_POS
    # if not stat.flying:
    #     new_enemy.x, new_enemy.y = PATH_START_POS
    # else:
    #     new_enemy.x, new_enemy.y = (
    #         PATH_START_POS[0],
    #         random.choice([0, 1, c.GRID_HEIGHT_TILES - 2, c.GRID_HEIGHT_TILES - 1])
    #         + c.TILE_SIZE // 2,
    #     )

    new_enemy.animator = Animator()
    animator_initialise(new_enemy.animator, {0: ENEMY_ANIMATIONS[enemy_type.value]})

    new_enemy.cx, new_enemy.cy = PATH_START_POS

    new_enemy.health = stat.health * enemy_health_multiplier

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
    enemy = enemies[i]

    # Dead then no need to update
    if enemy.health <= 0:
        return True

    animator_update(enemy.animator, g.dt)

    stat = ENEMY_STATS[enemy.type]
    speed = stat.speed * c.TILE_SIZE

    enemy.direction = c.RIGHT

    # Travelling to start
    if (enemy.cx, enemy.cy) == PATH_START_POS:
        enemy.x += speed
        # Reached start of map
        if enemy.x >= PATH_START_TILE[0] * c.TILE_SIZE:
            enemy.cx, enemy.cy = PATH_START_TILE

    # Travelling to goal
    elif (enemy.cx, enemy.cy) == PATH_END_TILE:
        enemy.x += speed
        # Reached end of screen
        if enemy.x >= PATH_END_POS[0]:
            p.player.health -= 1
            g.camera.trauma = 0.3
            enemy.health = 0  # Set to dead so tower can see that it died
            return True

    # Reached next cell pos
    else:
        # pathfind
        if not stat.flying:
            d = flowfield[enemy.cy][enemy.cx]
            if d == -1:
                d = 3  # trapped, jus move right
            dx, dy = c.DIRECTIONS[d]
            xv, yv = -dx * speed, -dy * speed
        # fly
        else:
            xv, yv = speed, 0

        enemy.x += xv
        enemy.y += yv

        rx, ry = round(enemy.x), round(enemy.y)

        # add to rx and ry to account for the size of the enemy
        if xv > 0:  # going right
            rx -= c.TILE_SIZE // 2
        elif xv < 0:  # going left (idk if this ever occurs)
            rx += c.TILE_SIZE // 2
            enemy.direction = c.LEFT
        if yv < 0:  # going up
            ry += c.TILE_SIZE // 2
            enemy.direction = c.UP
        elif yv > 0:  # going down
            ry -= c.TILE_SIZE // 2
            enemy.direction = c.DOWN

        enemy.cx = clamp(rx // c.TILE_SIZE, 0, c.GRID_WIDTH_TILES - 1)
        enemy.cy = clamp(ry // c.TILE_SIZE, 0, c.GRID_HEIGHT_TILES - 1)

    return False


def enemy_render(i: int) -> None:
    enemy = enemies[i]
    stat = ENEMY_STATS[enemy.type.value]

    surf = animator_get_frame(enemy.animator)
    if stat.anim_rotate:
        surf = pygame.transform.rotate(
            surf, {c.RIGHT: 0, c.UP: 90, c.DOWN: -90, c.LEFT: 180}[enemy.direction]
        )

    g.window.blit(
        surf,
        camera_to_screen(
            g.camera,
            enemy.x - (c.TILE_SIZE * stat.size) // 2,
            enemy.y - (c.TILE_SIZE * stat.size) // 2,
        ),
    )
