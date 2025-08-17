from dataclasses import dataclass
from enum import IntEnum
import math
import random

import pygame

import core.globals as g

from components.camera import Camera, camera_to_screen_shake
from components.motion import Motion, motion_update


class ParticleSpriteType(IntEnum):
    SHINY = 0
    CREATE = 1
    DELETE = 2
    BUILD = 3
    NORMAL_BIG = 4
    NORMAL_SMALL = 5
    SLOW_BIG = 6
    SLOW_SMALL = 7
    SPLASH_BIG = 8
    SPLASH_SMALL = 9
    ZAP_BIG = 10
    ZAP_SMALL = 11


@dataclass(slots=True)
class Particle:
    sprite: pygame.Surface
    motion: Motion
    rotation: float
    rotational_velocity: float
    lifespan: int  # total number of frames alive
    lifetime: int = 0  # current frame


MAX_PARTICLES = 200
_particles: list[Particle] = []

# Instantiate once here before game. values dont matter
for _ in range(MAX_PARTICLES):
    particle = Particle(
        g.PARTICLES[0],
        Motion(
            pygame.Vector2(),
            pygame.Vector2(),
            pygame.Vector2()
        ),
        0.0,
        0.0,
        0
    )
    _particles.append(particle)

particles_active: int = 0


def particle_spawn(
    sprite: pygame.Surface,
    motion: Motion,
    rotation: float,
    rotational_velocity: float,
    lifespan: int,
    lifetime: int = 0,
):
    global particles_active
    _particles[particles_active].sprite = sprite
    _particles[particles_active].motion = motion
    _particles[particles_active].rotation = rotation
    _particles[particles_active].rotational_velocity = rotational_velocity
    _particles[particles_active].lifespan = lifespan
    _particles[particles_active].lifetime = lifetime

    particles_active = min(particles_active + 1, MAX_PARTICLES-1)


def particle_burst(
    sprite_type: ParticleSpriteType,
    *,
    count: int,
    position: tuple[float, float],
    position_variance: float,
    velocity: float,
    velocity_variance: float,
    lifespan: int,
    lifespan_variance: int,
) -> None:

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
        particle_spawn(
            g.PARTICLES[sprite_type.value],
            motion,
            rotation,
            random.uniform(-500, 500),
            lifespan + random.randint(-lifespan_variance // 2, lifespan_variance // 2),
        )


def particle_update(particle: Particle) -> None:
    particle.lifetime += 1
    motion_update(particle.motion, g.dt)
    particle.rotation = (particle.rotation + particle.rotational_velocity * g.dt) % 360


def particles_update() -> None:
    global particles_active
    i = 0
    while i < particles_active:
        particle = _particles[i]
        particle_update(particle)

        if particle.lifetime >= particle.lifespan:
            # Switch with end of array :)) love this trick
            particles_active -= 1
            _particles[i] = _particles[particles_active]
            _particles[particles_active] = particle
        else:
            i += 1


def particle_render(particle: Particle, camera: Camera) -> None:
    surf = pygame.transform.rotate(particle.sprite, -particle.rotation)
    surf.set_alpha((1 - particle.lifetime / particle.lifespan) * 255)
    g.window.blit(
        surf,
        camera_to_screen_shake(
            camera,
            particle.motion.position.x - surf.get_width() // 2,
            particle.motion.position.y - surf.get_height() // 2,
        ),
    )


def particles_render() -> None:
    for i in range(particles_active):
        particle_render(_particles[i], g.camera)


def particles_clear() -> None:
    global particles_active
    particles_active = 0
