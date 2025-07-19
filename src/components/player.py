from dataclasses import dataclass


# STARTING_MONEY = 15
# NOTE: This high money value is just for testing
STARTING_MONEY = 100
STARTING_HEALTH = 100


@dataclass(slots=True)
class Player:
    money: int = 0
    health: int = 0
    # TODO: maybe add state too (paused, fastforward, settings)


player: Player = Player()


def player_reset() -> None:
    player.money = STARTING_MONEY
    player.health = STARTING_HEALTH
