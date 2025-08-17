from dataclasses import dataclass
from enum import Enum, IntEnum, auto
import random

import pygame

from components.motion import Motion
import core.constants as c
import core.globals as g
from components.particles import Particle, particle_spawn
from utilities.math import signed_num


class GameMode(Enum):
    WIRING = 0
    DESTROY = auto()


# value of the enum = number of fixed updates per frame
class SpeedType(IntEnum):
    PAUSED = 0
    NORMAL = 1
    FAST = 3


@dataclass(slots=True)
class Player:
    money: int = 50
    health: int = 20
    score: int = 0
    mode: GameMode = GameMode.WIRING
    speed: SpeedType = SpeedType.NORMAL


player: Player | None = None


def player_reset() -> None:
    global player
    player = Player()


def money_add(amount: int) -> None:
    player.money += amount


def score_add(amount: int) -> None:
    player.score = max(player.score + amount, 0)

    if abs(amount) >= 50:
        text = g.FONT.render(signed_num(amount), False, c.GREEN if amount > 0 else c.RED)
        particle_spawn(
            text,
            Motion(
                pygame.Vector2(c.GRID_WIDTH // 2 + random.randint(-30, 30), c.GRID_HEIGHT),
                pygame.Vector2(0, -100),
                pygame.Vector2(),
            ),
            0,
            0,
            20
        )


player_reset()
