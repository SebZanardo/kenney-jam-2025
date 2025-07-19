from dataclasses import dataclass
import math
import random

import pygame

from components.camera import Camera, camera_to_screen_shake
import core.globals as g
from components.motion import Motion, motion_update


@dataclass(slots=True)
class Particle:
    sprite_index: int
    motion: Motion
    rotation: float
    rotational_velocity: float
    lifespan: int  # total number of frames alive
    lifetime: int = 0  # current frame


def particle_burst(
    sprite_index: int,
    count: int,
    *,
    position: tuple[float, float],
    position_variance: float,
    velocity: float,
    velocity_variance: float,
    lifespan: int,
    lifespan_variance: int,
) -> list[Particle]:

    particles: list[Particle] = []

    for _ in range(count):
        # randomise motion
        rotation = random.uniform(0, 360)
        motion = Motion(
            pygame.Vector2(
                position[0] + random.uniform(-position_variance / 2, position_variance / 2),
                position[1] + random.uniform(-position_variance / 2, position_variance / 2),
            ),
            pygame.Vector2(
                velocity * math.cos(math.radians(rotation))
                + random.uniform(-velocity_variance / 2, velocity_variance / 2),
                velocity * math.sin(math.radians(rotation))
                + random.uniform(-velocity_variance / 2, velocity_variance / 2),
            ),
            pygame.Vector2(),
        )

        # create particle
        particle = Particle(
            sprite_index,
            motion,
            rotation,
            random.uniform(-500, 500),
            lifespan + random.randint(-lifespan_variance // 2, lifespan_variance // 2),
        )
        particles.append(particle)

    return particles


def particle_update(particle: Particle) -> None:
    particle.lifetime += 1
    motion_update(particle.motion, g.dt)
    particle.rotation = (particle.rotation + particle.rotational_velocity * g.dt) % 360


def particle_render(particle: Particle, camera: Camera) -> None:
    surf = pygame.transform.rotate(g.PARTICLES[particle.sprite_index], -particle.rotation)
    surf.set_alpha((1 - particle.lifetime / particle.lifespan) * 255)
    g.window.blit(
        surf,
        camera_to_screen_shake(
            camera,
            particle.motion.position[0] - surf.get_width() // 2,
            particle.motion.position[1] - surf.get_height() // 2,
        ),
    )
