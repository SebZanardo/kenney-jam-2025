from dataclasses import dataclass
from enum import IntEnum, auto

import core.constants as c
import core.globals as g
from components.camera import Camera, camera_to_screen_shake
from components.animation import Animation, Animator, animator_get_frame, animator_update
from components.ui import Pos
from utilities.sprite import rotate_sprite


class TowerType(IntEnum):
    NONE = 0

    CORE = auto()
    NORMAL = auto()
    SLOW = auto()
    SPLASH = auto()
    ZAP = auto()


@dataclass(slots=True)
class Tower:
    tile: Pos
    tower_type: TowerType = TowerType.NONE
    level: int = 0

    direction: str = c.UP
    animator: Animator = None


# NOTE: These should be stats for all towers
@dataclass(frozen=True)
class TowerStat:
    sell_price: int
    reload_time: int
    damage: int


# Load animations once here
tower_animations = []

for tower_type in list(TowerType):
    if tower_type == TowerType.NONE:
        continue
    start = tower_type.value
    animation = Animation(g.TOWERS[start * 7: (start + 1) * 7], 0.1)
    tower_animations.append(animation)

tower_purchase_price = {
    TowerType.CORE: 30,
    TowerType.NORMAL: 5,
    TowerType.SLOW: 10,
    TowerType.SPLASH: 20,
    TowerType.ZAP: 50,
}

# NOTE: index in array is for stats for that level
tower_stats = {
    TowerType.CORE: [
        TowerStat(20, 0, 0),
        TowerStat(40, 0, 0),
        TowerStat(60, 0, 0),
    ],
    TowerType.NORMAL: [
        TowerStat(3, 0.1, 1),
        TowerStat(6, 0.1, 3),
        TowerStat(9, 0.05, 5),
    ],
    TowerType.SLOW: [
        TowerStat(5, 0.2, 0),
        TowerStat(10, 0.15, 0),
        TowerStat(15, 0.1, 0),
    ],
    TowerType.SPLASH: [
        TowerStat(15, 0.2, 5),
        TowerStat(30, 0.15, 10),
        TowerStat(45, 0.1, 15),
    ],
    TowerType.ZAP: [
        TowerStat(30, 0.5, 16),
        TowerStat(60, 0.45, 35),
        TowerStat(90, 0.4, 50),
    ],
}


def tower_create_animator(tower: Tower) -> None:
    # start = tower.tower_type.
    tower.animator = Animator(
        {
            c.UP: tower_animations[tower.tower_type.value - 1]
            # c.LEFT: ...
            # c.RIGHT: ...
            # c.DOWN: ...
        },
        c.UP,
    )


def tower_update(tower: Tower) -> None:
    animator_update(tower.animator, g.dt)


def tower_render(tower: Tower, camera: Camera) -> None:
    g.window.blit(
        rotate_sprite(animator_get_frame(tower.animator), tower.direction),
        camera_to_screen_shake(camera, tower.tile[0] * c.TILE_SIZE, tower.tile[1] * c.TILE_SIZE),
    )
