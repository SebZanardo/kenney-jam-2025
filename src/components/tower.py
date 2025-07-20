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
    rotation: float = 0.0
    animator: Animator | None = None
    blending_anim: Animator | None = None

    # for cores
    connected_tower_count: int = 0

    # for non-cores
    core_tower: Tower | None = None

    target: e.Enemy | None = None
    cooldown: int = 0


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

TOWER_STATS = [
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
]


def tower_get_power(tower: Tower) -> float:
    if tower.type == TowerType.CORE:
        connected_tower_count = tower.connected_tower_count
    elif tower.core_tower is not None:
        connected_tower_count = tower.core_tower.connected_tower_count
    else:
        return 0.0
    return min(1.0, math.exp(-0.25 * (connected_tower_count - 1)))


def tower_update(tower: Tower) -> None:
    animator_update(tower.animator, g.dt)
    animator_update(tower.blending_anim, g.dt)

    stats = TOWER_STATS[tower.type.value][tower.level]

    if stats.radius == 0:
        return

    tx, ty = (tower.tile[0] + 0.5) * c.TILE_SIZE, (tower.tile[1] + 0.5) * c.TILE_SIZE

    # Tick down cooldown no matter what
    tower.cooldown -= 1

    # Find a target
    if tower.target is None:
        i = 0
        while i < e.active_enemies:
            enemy = e.enemies[i]

            if point_in_circle(enemy.x, enemy.y, tx, ty, stats.radius):
                tower.target = enemy
                break

            i += 1

    if tower.target is not None:
        # Rotate towards target
        tower.rotation = math.degrees(math.atan2(ty - tower.target.y, tx - tower.target.x)) - 90

        # Check if target is dead or out of range
        if tower.target.health <= 0 or not point_in_circle(
            tower.target.x, tower.target.y, tx, ty, stats.radius
        ):
            tower.target = None
            return

        # Damage target
        if tower.cooldown <= 0:
            tower.target.health -= stats.damage
            tower.cooldown = stats.reload_time

            # TODO: make different attacks use different particles
            for particle_type in (ParticleSpriteType.ATTACK_BIG, ParticleSpriteType.ATTACK_SMALL):
                particle_burst(
                    particle_type,
                    count=2,
                    position=(tower.target.x, tower.target.y),
                    position_variance=c.TILE_SIZE // 2,
                    velocity=0,
                    velocity_variance=0,
                    lifespan=10,
                    lifespan_variance=2,
                )


def tower_render(tower: Tower) -> None:
    surf = animator_get_frame(tower.animator)
    surf = pygame.transform.rotate(surf, -tower.rotation)

    if tower.level > 0:
        surf = surf.copy()
        surf.blit(animator_get_frame(tower.blending_anim), special_flags=pygame.BLEND_MULT)
        if tower.level > 1:
            surf.fill((128, 128, 128), special_flags=pygame.BLEND_ADD)

    g.window.blit(
        surf,
        camera_to_screen_shake(
            g.camera,
            (tower.tile[0] + 0.5) * c.TILE_SIZE - surf.get_width() // 2,
            (tower.tile[1] + 0.5) * c.TILE_SIZE - surf.get_height() // 2,
        ),
    )

    # g.window.blit(
    #     g.FONT.render(
    #         f"{}",
    #         True,
    #         c.WHITE,
    #     ),
    #     camera_to_screen_shake(g.camera, tower.tile[0] * c.TILE_SIZE, tower.tile[1] * c.TILE_SIZE),
    # )


def tower_render_radius(tower: Tower) -> None:
    radius = TOWER_STATS[tower.type.value][tower.level].radius
    diameter = radius * 2

    surf = pygame.transform.scale(g.RADIUS, (diameter, diameter))
    surf.set_alpha(50)

    g.window.blit(
        surf,
        camera_to_screen_shake(
            g.camera,
            tower.tile[0] * c.TILE_SIZE - radius + c.TILE_SIZE // 2,
            tower.tile[1] * c.TILE_SIZE - radius + c.TILE_SIZE // 2,
        ),
    )
