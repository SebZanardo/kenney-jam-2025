from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
import math
import pygame

from components.audio import AudioChannel, play_sound
import core.constants as c
import core.globals as g

import components.enemy as e
import components.player as p
from components.animation import Animation, Animator, animator_get_frame, animator_update
from components.camera import camera_to_screen_shake
from components.particles import ParticleSpriteType, particle_burst

from utilities.math import Pos, point_in_circle
from utilities.sprite import dim_sprite, gray_sprite


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
# tuple is as follows: (shooting anim, (dim button, button), disabled image)
TOWER_ANIMATIONS: list[tuple[Animation, tuple[pygame.Surface, pygame.Surface], pygame.Surface]] = []

for tower_type in TowerType:
    start = tower_type.value
    first_frame = g.TOWERS[start * 7]
    animation = Animation(g.TOWERS[start * 7 : (start + 1) * 7], 0.1)
    TOWER_ANIMATIONS.append(
        (animation, (dim_sprite(first_frame), first_frame), gray_sprite(first_frame))
    )

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
        TowerStat(3, 8, 4, 80),
        TowerStat(6, 6, 6, 88),
        TowerStat(9, 4, 8, 96),
    ),
    # TowerType.SLOW
    (
        TowerStat(5, 15, 1, 60),
        TowerStat(10, 12, 2, 70),
        TowerStat(15, 8, 4, 80),
    ),
    # TowerType.SPLASH
    (
        TowerStat(15, 10, 20, 140),
        TowerStat(30, 9, 30, 160),
        TowerStat(45, 8, 45, 180),
    ),
    # TowerType.ZAP
    (
        TowerStat(30, 15, 40, 60),
        TowerStat(60, 12, 50, 70),
        TowerStat(90, 8, 65, 80),
    ),
]


def tower_get_power(tower: Tower) -> float:
    if tower.type == TowerType.CORE:
        connected_tower_count = tower.connected_tower_count - (tower.level + 1) * 2
    elif tower.core_tower is not None:
        connected_tower_count = (
            tower.core_tower.connected_tower_count - (tower.core_tower.level + 1) * 2
        )
    else:
        return 0.0
    return min(1.0, math.exp(-0.25 * (connected_tower_count - 1)))


def tower_update(tower: Tower) -> None:
    # Don't update if unpowered
    power = tower_get_power(tower)
    if power == 0:
        return

    stat = TOWER_STATS[tower.type.value][tower.level]

    if tower.target is not None:
        mult = power / (stat.reload_time / 15)
        animator_update(tower.animator, g.dt * mult)
        animator_update(tower.blending_anim, g.dt * mult)

    if stat.radius == 0:
        return

    tx, ty = (tower.tile[0] + 0.5) * c.TILE_SIZE, (tower.tile[1] + 0.5) * c.TILE_SIZE

    # Tick down cooldown no matter what
    tower.cooldown -= 1 * power

    # Find a target
    if tower.target is None:
        i = 0
        while i < e.active_enemies:
            enemy = e.enemies[i]

            if point_in_circle(enemy.x, enemy.y, tx, ty, stat.radius):
                tower.target = enemy
                break

            i += 1

    if tower.target is not None:
        # Rotate towards target
        tower.rotation = math.degrees(math.atan2(ty - tower.target.y, tx - tower.target.x)) - 90

        # Check if target is dead or out of range
        if tower.target.health <= 0 or not point_in_circle(
            tower.target.x, tower.target.y, tx, ty, stat.radius
        ):
            tower.target = None
            return

        # Damage target
        if tower.cooldown <= 0:
            tower.target.health -= stat.damage

            if tower.target.health <= 0:
                reward = e.ENEMY_STATS[tower.target.type.value].reward
                p.money_add(reward)
                p.score_add(10 * reward)
            else:
                p.score_add(1)

            tower.cooldown = stat.reload_time

            tower_particle_burst(tower.type, tower.level, tower.target.x, tower.target.y)


def tower_render(tower: Tower) -> None:
    if tower_get_power(tower) == 0:
        surf = TOWER_ANIMATIONS[tower.type.value][2]
    else:
        surf = animator_get_frame(tower.animator)
    surf = pygame.transform.rotate(surf, -tower.rotation)

    if tower.level > 0:
        surf = surf.copy()
        surf.blit(animator_get_frame(tower.blending_anim), (0, 0), special_flags=pygame.BLEND_MULT)
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


def tower_particle_burst(type: TowerType, level: int, x: int, y: int) -> None:
    if type != TowerType.CORE:
        play_sound(
            (
                AudioChannel.TOWER_ALT
                if type in (TowerType.SPLASH, TowerType.ZAP)
                else AudioChannel.TOWER
            ),
            g.TOWER_SFX[type.value - 1],
        )
    if type == TowerType.NORMAL:
        for particle_type in (ParticleSpriteType.NORMAL_BIG, ParticleSpriteType.NORMAL_SMALL):
            particle_burst(
                particle_type,
                count=5 * (level + 1),
                position=(x, y),
                position_variance=c.TILE_SIZE,
                velocity=0,
                velocity_variance=0,
                lifespan=10,
                lifespan_variance=2,
            )
    elif type == TowerType.SLOW:
        for particle_type in (ParticleSpriteType.SLOW_BIG, ParticleSpriteType.SLOW_SMALL):
            particle_burst(
                particle_type,
                count=7 * (level + 1),
                position=(x, y),
                position_variance=c.TILE_SIZE * 2,
                velocity=0,
                velocity_variance=0,
                lifespan=20,
                lifespan_variance=5,
            )
    elif type == TowerType.SPLASH:
        for particle_type in (ParticleSpriteType.SPLASH_BIG, ParticleSpriteType.SPLASH_SMALL):
            particle_burst(
                particle_type,
                count=8 * (level + 1),
                position=(x, y),
                position_variance=c.TILE_SIZE * 4,
                velocity=20,
                velocity_variance=0,
                lifespan=15,
                lifespan_variance=3,
            )
    elif type == TowerType.ZAP:
        for particle_type in (ParticleSpriteType.ZAP_SMALL, ParticleSpriteType.ZAP_BIG):
            particle_burst(
                particle_type,
                count=6 * (level + 1),
                position=(x, y),
                position_variance=c.TILE_SIZE,
                velocity=0,
                velocity_variance=0,
                lifespan=8,
                lifespan_variance=3,
            )
