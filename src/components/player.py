from dataclasses import dataclass
from enum import Enum, IntEnum, auto


# STARTING_MONEY = 15
# NOTE: This high money value is just for testing
STARTING_MONEY = 100
STARTING_HEALTH = 100


class GameMode(Enum):
    VIEW = 0
    WIRING = auto()
    DESTROY = auto()


# value of the enum = number of fixed updates per frame
class SpeedType(IntEnum):
    PAUSED = 0
    NORMAL = 1
    FAST = 3


@dataclass(slots=True)
class Player:
    money: int = 0
    health: int = 0
    mode: GameMode = GameMode.VIEW
    speed: SpeedType = SpeedType.NORMAL


player: Player = Player()


def player_reset() -> None:
    player.money = STARTING_MONEY
    player.health = STARTING_HEALTH
    player.mode = GameMode.VIEW
    player.speed = SpeedType.NORMAL
