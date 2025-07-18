from dataclasses import dataclass
from enum import Enum

from components.ui import Pos
import core.globals as g


@dataclass(slots=True)
class HandTypeData:
    sprite_index: int
    render_offset: Pos


class HandType(Enum):
    UP = HandTypeData(0, (4, 1))
    DOWN = HandTypeData(1, (4, 15))
    TWO_FINGER = HandTypeData(2, (4, 1))
    THREE_FINGER = HandTypeData(3, (4, 1))
    GRAB = HandTypeData(4, (4, 1))
    POINTER = HandTypeData(5, (1, 1))
    POINTER_HEAVY = HandTypeData(7, (1, 1))
    POINTER_SLIM = HandTypeData(8, (1, 1))
    NO = HandTypeData(9, (6, 6))

    DEFAULT = POINTER


@dataclass(slots=True)
class Hand:
    type: HandType = HandType.DEFAULT


def hand_render(hand: Hand):
    data = hand.type.value
    g.window.blit(
        g.HANDS[data.sprite_index],
        (g.mouse_pos[0] - data.render_offset[0], g.mouse_pos[1] - data.render_offset[1]),
    )
