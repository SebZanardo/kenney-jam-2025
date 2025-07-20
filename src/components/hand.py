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
    title: str
    lines: list[tuple[int, str]] | None = None


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
        surf = tooltip_render(hand.tooltip)
        rx, ry = g.mouse_pos
        if g.mouse_pos[0] + surf.get_width() > c.WINDOW_WIDTH - c.TILE_SIZE:
            rx -= surf.get_width() + 4
        else:
            rx += 12
        if g.mouse_pos[1] + surf.get_height() > c.WINDOW_HEIGHT - c.TILE_SIZE:
            ry -= surf.get_height() + 4
        else:
            ry += 12
        g.window.blit(surf, (rx, ry))


def tooltip_render(tooltip: Tooltip) -> pygame.Surface:
    if tooltip.lines is None or len(tooltip.lines) == 0:
        return g.FONT.render(tooltip.title, False, c.WHITE, c.BLACK)

    lines: list[pygame.Surface] = []
    max_width: float = 0
    height: float = 0
    for icon, ln in [(-1, tooltip.title)] + tooltip.lines:
        text = g.FONT.render(ln, False, c.WHITE)
        if icon >= 0:
            surf = pygame.Surface((text.get_width() + 20, text.get_height()))
            surf.blit(g.ICONS[icon], (0, 0))
            surf.blit(text, (20, 0))
        else:
            surf = text
        lines.append(surf)
        max_width = max(max_width, surf.get_width())
        height += surf.get_height()

    final = pygame.Surface((max_width, height))
    final.fill(c.BLACK)
    y: float = 0
    for surf in lines:
        final.blit(surf, (0, y))
        y += surf.get_height()

    return final
