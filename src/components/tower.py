from dataclasses import dataclass
from enum import IntEnum

import core.constants as c
import core.globals as g
from components.camera import Camera, camera_to_screen_shake
from components.animation import Animation, Animator, animator_get_frame, animator_update
from utilities.math import Pos


class TowerType(IntEnum):
    # don't use auto() since the value of the enum is equal to the animation the tower uses
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
    direction: str
    animator: Animator = None


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

TOWER_PRICES = {
    TowerType.CORE: 30,
    TowerType.NORMAL: 5,
    TowerType.SLOW: 10,
    TowerType.SPLASH: 20,
    TowerType.ZAP: 50,
}

MAX_TOWER_LEVEL = 2

# NOTE: index in array is for stats for that level
TOWER_STATS = {
    TowerType.CORE: [
        TowerStat(20, 0, 0, 0),
        TowerStat(40, 0, 0, 0),
        TowerStat(60, 0, 0, 0),
    ],
    TowerType.NORMAL: [
        TowerStat(3, 0.1, 1, 32),
        TowerStat(6, 0.1, 3, 32),
        TowerStat(9, 0.05, 5, 32),
    ],
    TowerType.SLOW: [
        TowerStat(5, 0.2, 0, 32),
        TowerStat(10, 0.15, 0, 32),
        TowerStat(15, 0.1, 0, 32),
    ],
    TowerType.SPLASH: [
        TowerStat(15, 0.2, 5, 32),
        TowerStat(30, 0.15, 10, 32),
        TowerStat(45, 0.1, 15, 32),
    ],
    TowerType.ZAP: [
        TowerStat(30, 0.5, 16, 32),
        TowerStat(60, 0.45, 35, 32),
        TowerStat(90, 0.4, 50, 32),
    ],
}


def tower_update(tower: Tower) -> None:
    animator_update(tower.animator, g.dt)


def tower_render(tower: Tower) -> None:
    g.window.blit(
        animator_get_frame(tower.animator),
        camera_to_screen_shake(g.camera, tower.tile[0] * c.TILE_SIZE, tower.tile[1] * c.TILE_SIZE),
    )
