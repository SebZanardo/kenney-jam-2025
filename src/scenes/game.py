import math
import pygame

import core.constants as c
import core.input as t
import core.globals as g
from components.animation import (
    Animation,
    Animator,
    animator_get_frame,
    animator_initialise,
    animator_update,
)
from components.camera import (
    Camera,
    camera_from_screen,
    camera_to_screen,
    camera_to_screen_shake,
    camera_update,
)
from components.hand import HandType, hand, hand_render
from components.motion import Motion
from components.particles import (
    Particle,
    ParticleSpriteType,
    particle_burst,
    particle_render,
    particle_update,
)
from components.tower import (
    TOWER_ANIMATIONS,
    TOWER_PRICES,
    Tower,
    TowerType,
    tower_render,
    tower_update,
)
from components.player import player, player_reset
from components.pathing import (
    collision_grid, flowfield,
    pathing_reset, coord_to_tile, flowfield_regenerate, debug_print
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

        # player resources
        player_reset()

        # map
        pathing_reset()
        flowfield_regenerate(flowfield)
        debug_print()

        # towers
        self.towers: list[Tower] = []
        self.dragging_tower_type: TowerType | None = None

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

        # vfx
        self.particles: list[Particle] = []
        self.blending_anim = Animator()
        animator_initialise(self.blending_anim, {0: Animation(g.BLENDING_FX, 0.15)})

    def execute(self) -> None:
        # UPDATE
        if g.action_buffer[t.Action.START] == t.InputState.PRESSED:
            statemachine_change_state(self.statemachine, manager.SceneState.MENU)
            return

        # camera
        camera_update(self.camera, g.dt)

        # generic hand sprite
        hand.type = HandType.DEFAULT
        if self.wire_draw_start is not None or self.dragging_tower_type is not None:
            hand.type = HandType.GRAB

        # mouse pos in camera space
        last_hand_pos = camera_from_screen(self.camera, *g.last_mouse_pos)
        hand_pos = camera_from_screen(self.camera, *g.mouse_pos)

        # hovered tile pos
        tile_pos = coord_to_tile(*hand_pos)

        # user interaction
        # place tower
        game_mode_tower_create(self, tile_pos)

        # make wires (interp mouse pos)
        interp_hand_pos = last_hand_pos[:]
        while True:
            diff = (hand_pos[0] - interp_hand_pos[0], hand_pos[1] - interp_hand_pos[1])
            size = math.sqrt(diff[0] * diff[0] + diff[1] * diff[1])
            if size < c.TILE_SIZE:
                game_mode_wire_create(self, tile_pos)
                break
            unit = (diff[0] / size, diff[1] / size)
            interp_hand_pos = (
                interp_hand_pos[0] + unit[0] * c.TILE_SIZE / 2,
                interp_hand_pos[1] + unit[1] * c.TILE_SIZE / 2,
            )
            if (interp_tile_pos := coord_to_tile(*interp_hand_pos)) is None:
                break
            game_mode_wire_create(self, interp_tile_pos)

        # towers
        for tower in self.towers:
            tower_update(tower)

        # misc
        animator_update(self.blending_anim, g.dt)
        i = 0
        while i < len(self.particles):
            particle_update(self.particles[i])
            if self.particles[i].lifetime >= self.particles[i].lifespan:
                self.particles.pop(i)
            else:
                i += 1

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
        preview_tile: pygame.Surface | None = None
        if self.dragging_tower_type is not None:
            preview_tile = TOWER_ANIMATIONS[self.dragging_tower_type.value].frames[0]
        else:
            if tile_pos is not None:
                preview_tile = g.WIRES[0]

        if preview_tile is not None:
            if tile_pos is None:
                g.window.blit(preview_tile, g.mouse_pos)
            else:
                g.window.blit(
                    tile_preview(preview_tile, self.blending_anim),
                    camera_to_screen(
                        self.camera, tile_pos[0] * c.TILE_SIZE, tile_pos[1] * c.TILE_SIZE
                    ),
                )

        # particles
        for particle in self.particles:
            particle_render(particle, self.camera)

        # sidebars (immediate mode)
        if not (c.TILE_SIZE < g.mouse_pos[0] < c.WINDOW_WIDTH - c.TILE_SIZE):
            self.wire_draw_start = None

        last_dragging_tower_type = self.dragging_tower_type
        for i, tower_type in enumerate(TowerType):
            if tower_type == last_dragging_tower_type:
                continue
            bbox = (c.WINDOW_WIDTH - c.TILE_SIZE, i * c.TILE_SIZE, c.TILE_SIZE, c.TILE_SIZE)
            if (
                bbox[0] <= g.mouse_pos[0] <= bbox[0] + bbox[2]
                and bbox[1] <= g.mouse_pos[1] <= bbox[1] + bbox[3]
            ):
                hand.type = HandType.UP
                if t.mouse_pressed():
                    self.dragging_tower_type = tower_type

            g.window.blit(
                TOWER_ANIMATIONS[tower_type.value].frames[0],
                (bbox[0], bbox[1]),
            )

        hand_render()

        g.window.blit(g.FONT.render(f"${player.money}", False, c.BLACK), (0, 0))

    def exit(self) -> None:
        pass


# UTILS (SHOULD MOVE SOMEWHERE ELSE)
def tile_preview(surf: pygame.Surface, animator: Animator) -> pygame.Surface:
    preview = surf.copy()
    preview.set_alpha(200)
    preview.blit(animator_get_frame(animator), special_flags=pygame.BLEND_MULT)
    return preview


def tile_particle_burst(type: ParticleSpriteType, tile: Pos) -> list[Particle]:
    return particle_burst(
        type,
        count=8,
        position=((tile[0] + 0.5) * c.TILE_SIZE, (tile[1] + 0.5) * c.TILE_SIZE),
        position_variance=4,
        velocity=80,
        velocity_variance=10,
        lifespan=10,
        lifespan_variance=2,
    )


# TOWERS
def game_place_tower_on(self: Game, type: TowerType, parent: Wire):
    tower = Tower(
        parent.tile[:],
        type,
        1,
        c.UP,
        Animator(),
    )
    animator_initialise(tower.animator, {0: TOWER_ANIMATIONS[type.value]})
    parent.tower = tower
    self.towers.append(tower)
    collision_grid[tower.tile[1]][tower.tile[0]] = True
    player.money -= TOWER_PRICES[tower.type]
    self.particles.extend(tile_particle_burst(ParticleSpriteType.BUILD, tower.tile))
    self.camera.trauma = 0.35


def game_delete_tower_from(self: Game, parent: Wire):
    self.towers.remove(parent.tower)
    collision_grid[parent.tile[1]][parent.tile[0]] = False
    player.money += TOWER_PRICES[parent.tower.type]
    self.particles.extend(tile_particle_burst(ParticleSpriteType.DELETE, parent.tower.tile))
    self.camera.trauma = 0.35
    parent.tower = None


def game_mode_tower_create(self: Game, tile_pos: Pos | None):
    if self.dragging_tower_type is None:
        return

    if g.mouse_buffer[t.MouseButton.LEFT] not in (t.InputState.PRESSED, t.InputState.HELD):
        if tile_pos is not None:
            wire = wire_find(self.wires, tile_pos)
            if wire is not None and wire.tower is None:
                if player.money >= TOWER_PRICES[self.dragging_tower_type]:
                    game_place_tower_on(self, self.dragging_tower_type, wire)

        self.dragging_tower_type = None


# WIRES
def game_place_wire(self: Game, wire: Wire, parent: Wire):
    parent.outgoing_sides[c.INVERTED_DIRECTIONS[wire.incoming_side]] = wire
    player.money -= 1
    self.particles.extend(tile_particle_burst(ParticleSpriteType.CREATE, wire.tile))


def game_delete_wire(self: Game, wire: Wire, parent: Wire):
    parent.outgoing_sides = {
        dir: node for dir, node in parent.outgoing_sides.items() if node != wire
    }
    player.money += 1
    if wire.tower is not None:
        game_delete_tower_from(self, wire)
    else:
        self.particles.extend(tile_particle_burst(ParticleSpriteType.SHINY, wire.tile))


def game_mode_wire_create(self: Game, tile_pos: Pos | None):
    if t.mouse_pressed() and tile_pos is not None:
        self.wire_draw_start = wire_find(self.wires, tile_pos)

    if self.wire_draw_start is None:
        return

    if g.mouse_buffer[t.MouseButton.LEFT] not in (t.InputState.PRESSED, t.InputState.HELD):
        self.wire_draw_start = None

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
                if player.money >= 1:
                    wire = Wire(tile_pos[:], c.INVERTED_DIRECTIONS[adjacent_sides[tile_pos]], {})
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
