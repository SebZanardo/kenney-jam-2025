import pygame

import core.constants as c
import core.input as i
import core.globals as g
from components.animation import (
    Animation,
    Animator,
    animator_get_frame,
    animator_initialise,
    animator_update,
)
from components.camera import Camera, camera_from_screen, camera_to_screen, camera_to_screen_shake
from components.grid import inside_grid
from components.hand import HandType, hand, hand_render
from components.motion import Motion
from components.tower import (
    TOWER_ANIMATIONS,
    TOWER_PRICES,
    Tower,
    TowerType,
    tower_render,
    tower_update,
)
from components.ui import Pos
from components.wire import Wire, wire_find, wire_render_chain

from components.statemachine import StateMachine, statemachine_change_state

from scenes.scene import Scene
from scenes import manager


class Game(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

    # runs when game starts (or is resumed but thats not a thing)
    def enter(self) -> None:
        self.camera = Camera(
            Motion.empty(),
            pygame.Vector2(
                c.WINDOW_WIDTH // 2 - c.GRID_WIDTH // 2, c.WINDOW_HEIGHT // 2 - c.GRID_HEIGHT // 2
            ),
            pygame.Vector2(),
            pygame.Vector2(30, 30),
        )

        # resources
        self.money: int = 20

        # map
        self.collision_grid: list[list[bool]] = [
            [False] * c.GRID_WIDTH for _ in range(c.GRID_HEIGHT)
        ]

        # we can make this a 2d array if needed for pathfinding
        self.towers: list[Tower] = []

        # wires
        self.wires: list[Wire] = [
            Wire((1, 0), c.UP, {}, True),
            Wire(
                (3, 7),
                c.DOWN,
                {
                    c.UP: Wire((3, 6), c.DOWN, {}, True),
                },
                True,
            ),
        ]
        self.wire_draw_start: Wire | None = None

        self.blending_anim = Animator()
        animator_initialise(self.blending_anim, {0: Animation(g.BLENDING_FX, 0.15)})

    def execute(self) -> None:
        # UPDATE
        if g.action_buffer[i.Action.START] == i.InputState.PRESSED:
            statemachine_change_state(self.statemachine, manager.SceneState.MENU)
            return

        # mouse pos in camera space
        hand_pos = camera_from_screen(self.camera, *g.mouse_pos)

        # hovered tile pos
        tile_pos = (hand_pos[0] // c.TILE_SIZE, hand_pos[1] // c.TILE_SIZE)
        if not inside_grid(*tile_pos):
            tile_pos = None

        # user interaction
        # place tower
        game_mode_tower_create(self, tile_pos)

        # make wires
        game_mode_wire_create(self, tile_pos)

        # towers
        for tower in self.towers:
            tower_update(tower)

        # misc
        animator_update(self.blending_anim, g.dt)

        # RENDER
        g.window.fill(c.WHITE)

        # background grid
        for x in range(c.GRID_WIDTH_TILES):
            for y in range(c.GRID_HEIGHT_TILES):
                g.window.blit(
                    g.TERRAIN[(x + y) % 2],
                    camera_to_screen_shake(self.camera, x * c.TILE_SIZE, y * c.TILE_SIZE),
                )

        # wires
        for wire in self.wires:
            wire_render_chain(wire, self.camera)

        # enemies
        pass

        # towers
        for tower in self.towers:
            tower_render(tower, self.camera)

        # preview tile
        if tile_pos is not None:
            tile_preview = g.WIRES[0].copy()
            tile_preview.set_alpha(200)
            tile_preview.blit(
                animator_get_frame(self.blending_anim), special_flags=pygame.BLEND_MULT
            )
            g.window.blit(
                tile_preview,
                camera_to_screen(self.camera, tile_pos[0] * c.TILE_SIZE, tile_pos[1] * c.TILE_SIZE),
            )

        hand_render()

        g.window.blit(g.FONT.render(f"${self.money}", False, c.BLACK), (0, 0))

    def exit(self) -> None:
        pass


## TOWERS


def game_place_tower_on(self: Game, parent: Wire):
    tower = Tower(
        parent.tile[:],
        TowerType.NORMAL,
        1,
        c.UP,
        Animator(),
    )
    animator_initialise(tower.animator, {0: TOWER_ANIMATIONS[TowerType.NORMAL.value]})
    parent.tower = tower
    self.towers.append(tower)
    self.collision_grid[tower.tile[1]][tower.tile[0]] = True
    self.money -= TOWER_PRICES[tower.type]


def game_delete_tower_from(self: Game, parent: Wire):
    self.towers.remove(parent.tower)
    self.collision_grid[parent.tile[1]][parent.tile[0]] = False
    self.money += TOWER_PRICES[parent.tower.type]
    parent.tower = None


def game_mode_tower_create(self: Game, tile_pos: Pos | None):
    if i.mouse_pressed():
        wire = wire_find(self.wires, tile_pos)
        if wire is not None:
            # place tower
            if wire.tower is None:
                if self.money >= 5:
                    game_place_tower_on(self, wire)
            # delete tower
            else:
                game_delete_tower_from(self, wire)


## WIRES


def game_place_wire(self: Game, wire: Wire, parent: Wire):
    parent.outgoing_sides[c.INVERTED_DIRECTIONS[wire.incoming_side]] = wire
    self.money -= 1


def game_delete_wire(self: Game, wire: Wire, parent: Wire):
    parent.outgoing_sides = {
        dir: node for dir, node in parent.outgoing_sides.items() if node != wire
    }
    if wire.tower is not None:
        game_delete_tower_from(self, wire)
    self.money += 1


def game_mode_wire_create(self: Game, tile_pos: Pos | None):
    if i.mouse_pressed() and tile_pos is not None:
        self.wire_draw_start = wire_find(self.wires, tile_pos)

    if self.wire_draw_start is not None:
        hand.type = HandType.GRAB
        if g.mouse_buffer[i.MouseButton.LEFT] not in (i.InputState.PRESSED, i.InputState.HELD):
            self.wire_draw_start = None
            hand.type = HandType.DEFAULT

        elif tile_pos != self.wire_draw_start.tile and tile_pos is not None:
            sx, sy = self.wire_draw_start.tile
            adjacent_sides = {
                (sx, sy - 1): c.UP,
                (sx - 1, sy): c.LEFT,
                (sx + 1, sy): c.RIGHT,
                (sx, sy + 1): c.DOWN,
            }

            # adjacent tile
            if tile_pos in adjacent_sides:
                # place new wire
                if (overwrite := wire_find(self.wires, tile_pos)) is None:
                    if self.money >= 1:
                        wire = Wire(
                            tile_pos[:], c.INVERTED_DIRECTIONS[adjacent_sides[tile_pos]], {}
                        )
                        game_place_wire(self, wire, self.wire_draw_start)
                        self.wire_draw_start = wire
                    else:
                        hand.type = HandType.NO

                # delete previous wire
                elif (
                    not self.wire_draw_start.outgoing_sides
                    and self.wire_draw_start in overwrite.outgoing_sides.values()
                    and not self.wire_draw_start.is_permanent
                ):
                    game_delete_wire(self, self.wire_draw_start, overwrite)
                    self.wire_draw_start = overwrite

                # crossing wires
                else:
                    hand.type = HandType.NO

            # cursor jumped, not an adjacent tile
            else:
                hand.type = HandType.NO
