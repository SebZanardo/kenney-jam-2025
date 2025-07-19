from dataclasses import dataclass
from enum import Enum

import pygame

import core.constants as c
import core.globals as g
from utilities.math import Pos


@dataclass(slots=True)
class HandTypeData:
    sprite_index: int
    render_offset: Pos


class HandType(Enum):
    UP = HandTypeData(0, (4, 1))
    DOWN = HandTypeData(1, (4, 15))
    TWO_FINGER = HandTypeData(2, (4, 1))
    THREE_FINGER = HandTypeData(3, (4, 1))
    GRAB = HandTypeData(4, (4, 3))
    POINTER = HandTypeData(5, (1, 1))
    POINTER_HEAVY = HandTypeData(7, (1, 1))
    POINTER_SLIM = HandTypeData(8, (1, 1))
    NO = HandTypeData(9, (6, 6))

    DEFAULT = POINTER_HEAVY
    HOVER = UP


@dataclass(slots=True)
class Tooltip:
    text: str
    icon: pygame.Surface | None = None


@dataclass(slots=True)
class Hand:
    type: HandType = HandType.DEFAULT
    tooltip: Tooltip | None = None


hand = Hand()


def hand_render():
    data = hand.type.value
    g.window.blit(
        g.HANDS[data.sprite_index],
        (g.mouse_pos[0] - data.render_offset[0], g.mouse_pos[1] - data.render_offset[1]),
    )

    if hand.tooltip is not None:
        data = hand.tooltip
        text = g.FONT.render(hand.tooltip.text, False, c.WHITE, c.BLACK)
        rx, ry = g.mouse_pos
        if g.mouse_pos[0] + text.get_width() > c.WINDOW_WIDTH - c.TILE_SIZE:
            rx -= text.get_width() + 4
        else:
            rx += 12
        if g.mouse_pos[1] + text.get_height() > c.WINDOW_HEIGHT - c.TILE_SIZE:
            ry -= text.get_height() + 4
        else:
            ry += 12
        g.window.blit(text, (rx, ry))
