from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

import pygame

import core.constants as c
import core.globals as g
from components.camera import Camera, camera_to_screen_shake
from components.tower import Tower, TowerType
from utilities.math import Pos


@dataclass(slots=True)
class Wire:
    # position and nodes
    tile: Pos
    incoming_side: str | None
    outgoing_sides: dict[str, Wire]  # dir: node

    # per-map config
    is_permanent: bool = False

    # user addition
    tower: Tower | None = None

    # power system keeps reference to the current core
    core_tower: Tower | None = None


def wire_find(
    wires: Iterable[Wire], tile: Pos, parent: Wire | None = None
) -> tuple[Wire | None, Wire | None]:
    for wire in wires:
        if wire.tile == tile:
            return (wire, parent)
        node, node_parent = wire_find(wire.outgoing_sides.values(), tile, wire)
        if node is not None:
            return (node, node_parent)

    return (None, None)


def wire_render_comp(wire: Wire) -> None:
    index: int = 0
    rot: int = 0

    if wire.incoming_side is not None:
        match len(wire.outgoing_sides):
            # dead end
            case 0:
                index = 1
                rot = [c.DOWN, c.LEFT, c.UP, c.RIGHT].index(wire.incoming_side)

            # straight or turn
            case 1:
                if (wire.incoming_side in c.VERTICAL) == (
                    list(wire.outgoing_sides)[0] in c.VERTICAL
                ):
                    index = 2
                    rot = 0 if wire.incoming_side in c.VERTICAL else 1
                else:
                    index = 3
                    rot = [
                        {c.RIGHT, c.DOWN},
                        {c.LEFT, c.DOWN},
                        {c.UP, c.LEFT},
                        {c.UP, c.RIGHT},
                    ].index({wire.incoming_side, *wire.outgoing_sides})

            # 3-way split
            case 2:
                index = 5
                rot = [
                    {c.UP, c.RIGHT, c.DOWN},
                    {c.LEFT, c.RIGHT, c.DOWN},
                    {c.UP, c.LEFT, c.DOWN},
                    {c.UP, c.LEFT, c.RIGHT},
                ].index({wire.incoming_side, *wire.outgoing_sides})

            # 4-way split
            case 3:
                index = 4

    if not wire.is_permanent:
        index += 6

    surf = pygame.transform.rotate(g.WIRES[index], rot * -90)
    if wire.tower is not None:
        surf.set_alpha(100)
    g.window.blit(
        surf,
        camera_to_screen_shake(g.camera, wire.tile[0] * c.TILE_SIZE, wire.tile[1] * c.TILE_SIZE),
    )


def wire_render_chain(wire: Wire) -> None:
    wire_render_comp(wire)
    for node in wire.outgoing_sides.values():
        wire_render_chain(node)
