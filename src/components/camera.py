from dataclasses import dataclass
import random
import pygame

import core.constants as c
import core.globals as g
from utilities.math import Pos

from components.motion import Motion, motion_update

from utilities.math import clamp


@dataclass(slots=True)
class Camera:
    motion: Motion
    offset: pygame.Vector2
    shake_offset: pygame.Vector2
    max_shake_offset: pygame.Vector2
    trauma: float = 0.0
    max_shake_duration: float = 2.0


def camera_rect(camera: Camera) -> pygame.Rect:
    return pygame.Rect(
        camera.motion.position.x - camera.offset.x,
        camera.motion.position.y - camera.offset.y,
        c.WINDOW_WIDTH,
        c.WINDOW_HEIGHT,
    )


def camera_follow(camera: Camera, x: float, y: float, speed: float = 8) -> None:
    dist = pygame.Vector2(x - camera.motion.position.x, y - camera.motion.position.y)
    if dist.magnitude() < 1:
        camera.motion.position = pygame.Vector2(x, y)
        camera.motion.velocity = pygame.Vector2()
    else:
        camera.motion.velocity = pygame.Vector2(
            dist.x * speed,
            dist.y * speed,
        )


def camera_update(camera: Camera, dt: float) -> None:
    # Update shake
    camera.trauma -= dt / camera.max_shake_duration

    if camera.trauma > 0 and g.setting_params["screenshake"][0]:
        shake = camera.trauma**3  # NOTE: Can square trauma too
        camera.shake_offset.x = camera.max_shake_offset.x * shake
        camera.shake_offset.x *= random.uniform(-1, 1)
        camera.shake_offset.y = camera.max_shake_offset.y * shake
        camera.shake_offset.y *= random.uniform(-1, 1)
    elif camera.trauma < 0:
        camera.shake_offset.x = 0
        camera.shake_offset.y = 0

    camera.trauma = clamp(camera.trauma, 0, 1)

    # Update motion
    motion_update(camera.motion, dt)


def camera_to_screen(camera: Camera, x: float, y: float) -> Pos:
    # round to reduce jitter.
    return (
        round(x - camera.motion.position.x + camera.offset.x),
        round(y - camera.motion.position.y + camera.offset.y),
    )


def camera_to_screen_shake(camera: Camera, x: float, y: float) -> Pos:
    return camera_to_screen(camera, x + camera.shake_offset.x, y + camera.shake_offset.y)


def camera_to_screen_shake_rect(
    camera: Camera, x: float, y: float, w: float, h: float
) -> tuple[int, int, int, int]:
    screen_x = x - camera.motion.position.x + camera.offset.x
    screen_y = y - camera.motion.position.y + camera.offset.y
    return (
        round(screen_x + camera.shake_offset.x),
        round(screen_y + camera.shake_offset.y),
        w,
        h,
    )


def camera_from_screen(camera: Camera, x: float, y: float) -> Pos:
    return (
        round(x + camera.motion.position.x - camera.offset.x),
        round(y + camera.motion.position.y - camera.offset.y),
    )


def camera_reset(camera: Camera) -> None:
    camera.trauma = 0.0
    camera.shake_offset.x = 0.0
    camera.shake_offset.y = 0.0
    camera.motion.velocity = pygame.Vector2()
    camera.motion.acceleration = pygame.Vector2()
