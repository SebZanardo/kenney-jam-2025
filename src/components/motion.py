from dataclasses import dataclass
import pygame


@dataclass
class Motion:
    position: pygame.Vector2
    velocity: pygame.Vector2
    acceleration: pygame.Vector2

    def copy(self):
        return Motion(self.position.copy(), self.velocity.copy(), self.acceleration.copy())

    @staticmethod
    def empty():
        return Motion(pygame.Vector2(), pygame.Vector2(), pygame.Vector2())


def motion_update(motion: Motion, dt: float) -> None:
    motion.velocity.x += motion.acceleration.x * dt
    motion.velocity.y += motion.acceleration.y * dt
    motion.position.x += motion.velocity.x * dt
    motion.position.y += motion.velocity.y * dt
