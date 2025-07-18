from dataclasses import dataclass

import core.constants as c
import core.globals as g
from components.camera import Camera, camera_to_screen_shake
from components.animation import Animation, Animator, animator_get_frame, animator_update
from components.ui import Pos
from utilities.sprite import rotate_sprite


@dataclass(slots=True)
class Tower:
    tile: Pos
    direction: str = c.UP
    animator: Animator = None
    is_fast: bool = False
    is_splash: bool = False


def tower_create_animator(tower: Tower) -> None:
    start = tower.is_fast + tower.is_splash * 2
    tower.animator = Animator(
        {
            c.UP: Animation(g.POTIONS[start * 7 : (start + 1) * 7], 0.1),
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
