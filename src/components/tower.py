from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
import math
import pygame

from components.particles import ParticleSpriteType, particle_burst
import core.constants as c
import core.globals as g

import components.enemy as e
from components.camera import camera_to_screen_shake
from components.animation import Animation, Animator, animator_get_frame, animator_update

from utilities.math import Pos, point_in_circle


class TowerType(IntEnum):
    CORE = 0
    NORMAL = 1
    SLOW = 2
    SPLASH = 3
    ZAP = 4


@dataclass(slots=True)
class Tower:
    tile: Pos
    type: TowerType
    level: int

    # visual
    direction: str
    animator: Animator
    blending_anim: Animator

    # for cores
    connected_tower_count: int = 0

    # for non-cores
    core_tower: Tower | None = None

    target: e.Enemy = None


# NOTE: These should be stats for all towers
@dataclass(frozen=True)
class TowerStat:
    sell_price: int
    reload_time: int
    damage: int
    radius: int


# Load animations once here
TOWER_ANIMATIONS: list[Animation] = []

for tower_type in TowerType:
    start = tower_type.value
    animation = Animation(g.TOWERS[start * 7 : (start + 1) * 7], 0.1)
    TOWER_ANIMATIONS.append(animation)

TOWER_PRICES = [
    # TowerType.CORE
    10,
    # TowerType.NORMAL
    5,
    # TowerType.SLOW
    10,
    # TowerType.SPLASH
    20,
    # TowerType.ZAP
    50,
]

MAX_TOWER_LEVEL = 2

TOWER_STATS = (
    # TowerType.CORE
    (
        TowerStat(10, 0, 0, 0),
        TowerStat(20, 0, 0, 0),
        TowerStat(30, 0, 0, 0),
    ),
    # TowerType.NORMAL
    (
        TowerStat(3, 0.1, 1, 80),
        TowerStat(6, 0.1, 3, 80),
        TowerStat(9, 0.05, 5, 80),
    ),
    # TowerType.SLOW
    (
        TowerStat(5, 0.2, 0, 80),
        TowerStat(10, 0.15, 0, 80),
        TowerStat(15, 0.1, 0, 80),
    ),
    # TowerType.SPLASH
    (
        TowerStat(15, 0.2, 5, 80),
        TowerStat(30, 0.15, 10, 80),
        TowerStat(45, 0.1, 15, 80),
    ),
    # TowerType.ZAP
    (
        TowerStat(30, 0.5, 16, 80),
        TowerStat(60, 0.45, 35, 80),
        TowerStat(90, 0.4, 50, 80),
    ),
)


def tower_get_power(tower: Tower) -> float:
    connected_tower_count: int = 0
    if tower.type == TowerType.CORE:
        connected_tower_count = tower.connected_tower_count
    elif tower.core_tower is not None:
        connected_tower_count = tower.core_tower.connected_tower_count
    return min(1.0, math.exp(-0.25 * (connected_tower_count - 1)))


def tower_update(tower: Tower) -> None:
    animator_update(tower.animator, g.dt)
    animator_update(tower.blending_anim, g.dt)

    r = TOWER_STATS[tower.type.value][tower.level].radius

    if r == 0:
        return

    tx, ty = (tower.tile[0] + 0.5) * c.TILE_SIZE, (tower.tile[1] + 0.5) * c.TILE_SIZE

    # TODO: targeting enemies
    i = 0
    while i < e.active_enemies:
        enemy = e.enemies[i]

        if point_in_circle(enemy.x, enemy.y, tx, ty, r):
            for particle_type in (ParticleSpriteType.ATTACK_BIG, ParticleSpriteType.ATTACK_SMALL):
                particle_burst(
                    particle_type,
                    count=2,
                    position=(enemy.x, enemy.y),
                    position_variance=c.TILE_SIZE // 2,
                    velocity=0,
                    velocity_variance=0,
                    lifespan=10,
                    lifespan_variance=2,
                )

        i += 1


def tower_render(tower: Tower) -> None:
    surf = animator_get_frame(tower.animator)

    if tower.level > 0:
        surf = surf.copy()
        surf.blit(animator_get_frame(tower.blending_anim), special_flags=pygame.BLEND_MULT)
        if tower.level > 1:
            surf.fill((128, 128, 128), special_flags=pygame.BLEND_ADD)

    g.window.blit(
        surf,
        camera_to_screen_shake(g.camera, tower.tile[0] * c.TILE_SIZE, tower.tile[1] * c.TILE_SIZE),
    )

    # g.window.blit(
    #     g.FONT.render(
    #         f"{}",
    #         True,
    #         c.WHITE,
    #     ),
    #     camera_to_screen_shake(g.camera, tower.tile[0] * c.TILE_SIZE, tower.tile[1] * c.TILE_SIZE),
    # )

    # TODO: Move this to on view hover ########################################
    radius = TOWER_STATS[tower.type.value][tower.level].radius
    diameter = radius * 2
    position = (
        tower.tile[0] * c.TILE_SIZE - radius + c.TILE_SIZE // 2,
        tower.tile[1] * c.TILE_SIZE - radius + c.TILE_SIZE // 2
    )

    resized_radius = pygame.transform.scale(g.RADIUS, (diameter, diameter))

    temp = pygame.Surface((diameter, diameter)).convert()
    temp.set_colorkey(c.MAGENTA)
    temp.fill(c.MAGENTA)
    temp.blit(resized_radius, (0, 0))
    temp.set_alpha(50)

    g.window.blit(temp, camera_to_screen_shake(g.camera, *position))
    ###########################################################################
