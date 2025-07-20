from enum import IntEnum, auto
import math
import random
import pygame

from components.settings import settings_menu
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
from components.audio import play_music
from components.camera import (
    Camera,
    camera_from_screen,
    camera_to_screen,
    camera_to_screen_shake,
    camera_update,
)
from components.hand import HandType, Tooltip, hand, hand_render
from components.motion import Motion
from components.particles import (
    ParticleSpriteType,
    particle_burst,
    particles_render,
    particles_update,
)
from components.tower import (
    MAX_TOWER_LEVEL,
    TOWER_ANIMATIONS,
    TOWER_PRICES,
    TOWER_STATS,
    Tower,
    TowerType,
    tower_get_power,
    tower_render,
    tower_render_radius,
    tower_update,
)
import components.player as p
from components.statemachine import StateMachine, statemachine_change_state
from components.wave import wave_update, wave_reset
import components.pathing as path
import components.enemy as e
from components import ui
from components.wave import wave_data
from components.wire import Wire, wire_find, wire_render_chain
from utilities.math import Pos

from scenes.scene import Scene
from scenes import manager
from utilities.sprite import dim_sprite


class MenuState(IntEnum):
    GAME = 0
    SETTINGS = auto()


class Game(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

    # runs when game starts (or is resumed but thats not a thing)
    def enter(self) -> None:
        self.current_state = MenuState.GAME
        g.camera = Camera(
            Motion.empty(),
            pygame.Vector2(
                c.WINDOW_WIDTH // 2 - c.GRID_WIDTH // 2, c.WINDOW_HEIGHT // 2 - c.GRID_HEIGHT // 2
            ),
            pygame.Vector2(),
            pygame.Vector2(30, 30),
        )

        play_music(g.GAME_MUSIC, -1)

        # player resources
        p.player_reset()

        # map
        path.pathing_reset()
        path.flowfield_regenerate(path.flowfield)
        path.debug_print()

        # wave
        wave_reset()

        # towers
        self.towers: list[Tower] = []
        self.dragging_tower_type: TowerType | None = None

        # wires
        self.wires: list[Wire] = [
            Wire((random.randint(1, 7), 0), c.UP, {}, True),
            Wire((random.randint(8, 14), 0), c.UP, {}, True),
            Wire((random.randint(1, 7), 8), c.DOWN, {}, True),
            Wire((random.randint(8, 14), 8), c.DOWN, {}, True),
        ]
        self.wire_draw_start: Wire | None = None

        # vfx
        self.blending_anim = Animator()
        animator_initialise(self.blending_anim, {0: Animation(g.BLENDING_FX[0:4], 0.15)})

        # placement
        self.last_hov_pos = (-1, -1)
        self.valid_placement = False

    def execute(self) -> None:
        hand.type = HandType.DEFAULT
        if self.wire_draw_start is not None or self.dragging_tower_type is not None:
            hand.type = HandType.GRAB
        hand.tooltip = None

        camera_update(g.camera, g.dt)

        # SETTINGS
        if self.current_state == MenuState.SETTINGS:
            g.window.fill(c.BLACK)

            if not settings_menu():
                self.current_state = MenuState.GAME
                ui.im_new()

            hand_render()
            return

        # UPDATE
        if g.action_buffer[t.Action.START] == t.InputState.PRESSED:
            statemachine_change_state(self.statemachine, manager.SceneState.MENU)
            return

        # mouse pos in camera space
        last_hand_pos = camera_from_screen(g.camera, *g.last_mouse_pos)
        hand_pos = camera_from_screen(g.camera, *g.mouse_pos)

        # hovered tile pos
        hov_tile = path.coord_to_tile(*hand_pos)

        # hovered wire
        hov_wire, hov_wire_parent = wire_find(self.wires, hov_tile)

        if p.player.health > 0:
            # user interaction
            if p.player.mode == p.GameMode.WIRING:
                # make wires (interp mouse pos)
                if hov_wire is not None and self.wire_draw_start is None:
                    hand.type = HandType.HOVER
                interp_hand_pos = last_hand_pos[:]
                while True:
                    diff = (hand_pos[0] - interp_hand_pos[0], hand_pos[1] - interp_hand_pos[1])
                    size = math.sqrt(diff[0] * diff[0] + diff[1] * diff[1])
                    if size < c.TILE_SIZE:
                        game_mode_wire_create(self, hov_tile, hov_wire)
                        break
                    unit = (diff[0] / size, diff[1] / size)
                    interp_hand_pos = (
                        interp_hand_pos[0] + unit[0] * c.TILE_SIZE / 2,
                        interp_hand_pos[1] + unit[1] * c.TILE_SIZE / 2,
                    )
                    if (interp_tile := path.coord_to_tile(*interp_hand_pos)) is None:
                        break
                    game_mode_wire_create(self, interp_tile, hov_wire)

            elif p.player.mode == p.GameMode.DESTROY:
                game_mode_wire_destroy(self, hov_wire, hov_wire_parent)

            # wave, enemy, tower update
            for _ in range(p.player.speed.value):
                wave_update()
                for tower in self.towers:
                    tower_update(tower)

            # tower tooltips
            game_mode_tower_create(self, hov_tile, hov_wire)

            # misc
            particles_update()
            animator_update(self.blending_anim, g.dt)

        # game over
        else:
            if t.is_pressed(t.Action.START) or t.mouse_pressed(t.MouseButton.LEFT):
                statemachine_change_state(self.statemachine, manager.SceneState.MENU)
                return
            pass

        self.last_hov_pos = hov_tile

        # RENDER
        g.window.fill(c.BLACK)

        # background grid
        for x in range(c.GRID_WIDTH_TILES):
            for y in range(c.GRID_HEIGHT_TILES):
                g.window.blit(
                    g.TERRAIN[
                        8 if (x, y) in (path.PATH_START_TILE, path.PATH_END_TILE) else (x + y) % 2
                    ],
                    camera_to_screen_shake(g.camera, x * c.TILE_SIZE, y * c.TILE_SIZE),
                )

        # wires
        for wire in self.wires:
            wire_render_chain(wire)

        # enemies
        for i in range(e.active_enemies):
            e.enemy_render(i)

        # towers
        for tower in self.towers:
            tower_render(tower)
            if p.player.mode == p.GameMode.VIEW and tower.tile == hov_tile:
                tower_render_radius(tower)

        # preview tile
        if p.player.health > 0:
            preview_tile: pygame.Surface | None = None

            if self.dragging_tower_type is not None:
                preview_tile = TOWER_ANIMATIONS[self.dragging_tower_type.value].frames[0]
                if hov_tile is not None:
                    tower_render_radius(Tower(hov_tile, self.dragging_tower_type, 0))

            elif p.player.mode == p.GameMode.WIRING:
                if hov_wire is not None:
                    preview_tile = g.WIRES[0]

            if preview_tile is not None:
                if hov_tile is None:
                    g.window.blit(preview_tile, g.mouse_pos)
                else:
                    surf = preview_tile.copy()
                    surf.set_alpha(200)
                    surf.blit(
                        animator_get_frame(self.blending_anim), special_flags=pygame.BLEND_MULT
                    )
                    g.window.blit(
                        surf,
                        camera_to_screen(
                            g.camera, hov_tile[0] * c.TILE_SIZE, hov_tile[1] * c.TILE_SIZE
                        ),
                    )

        # particles
        particles_render()

        # hud
        if hov_tile is None:
            self.wire_draw_start = None

        # top and bottom
        for x in range(c.WINDOW_WIDTH // 14):
            g.window.blit(g.TERRAIN[3], (x * 14 - 1, 3))
            g.window.blit(g.TERRAIN[2], (x * 14 - 1, c.WINDOW_HEIGHT - c.TILE_SIZE - 4))

        last_speed, last_mode = p.player.speed, p.player.mode
        ui.im_reset_position(c.TILE_SIZE, 0)
        if last_speed == p.SpeedType.PAUSED:
            if ui.im_button_image(g.BUTTONS_INV[9], "Paused"):
                p.player.speed = p.SpeedType.NORMAL
        else:
            if ui.im_button_image(g.BUTTONS[9], "Pause"):
                p.player.speed = p.SpeedType.PAUSED
        ui.im_same_line()
        if last_speed == p.SpeedType.FAST:
            if ui.im_button_image(g.BUTTONS_INV[12], "Fast forwarding"):
                p.player.speed = p.SpeedType.NORMAL
        else:
            if ui.im_button_image(g.BUTTONS[12], "Fast forward"):
                p.player.speed = p.SpeedType.FAST

        ui.im_set_next_position(c.WINDOW_WIDTH - 4 * c.TILE_SIZE, 0)
        if ui.im_button_image(
            (g.BUTTONS_INV if last_mode == p.GameMode.VIEW else g.BUTTONS)[0], "View"
        ):
            p.player.mode = p.GameMode.VIEW
        ui.im_same_line()
        if ui.im_button_image(
            (g.BUTTONS_INV if last_mode == p.GameMode.WIRING else g.BUTTONS)[1], "Lay wire"
        ):
            p.player.mode = p.GameMode.WIRING
        ui.im_same_line()
        if ui.im_button_image(
            (g.BUTTONS_INV if last_mode == p.GameMode.DESTROY else g.BUTTONS)[2], "Destroy"
        ):
            p.player.mode = p.GameMode.DESTROY

        ui.im_set_next_position(c.TILE_SIZE, c.WINDOW_HEIGHT - c.TILE_SIZE)
        if ui.im_button_image(g.BUTTONS[3], "Settings"):
            ui.im_new()
            self.current_state = MenuState.SETTINGS

        text_y, icon_y, icon_w = 7, 8, 18
        wave_text = g.FONT.render(f"WAVE {wave_data.number + 1}", False, c.WHITE)
        g.window.blit(wave_text, (c.WINDOW_WIDTH // 2 - wave_text.get_width() // 2, text_y))
        money_text = g.FONT.render(f"${p.player.money}", False, c.WHITE)
        g.window.blit(
            g.ICONS[0], (c.WINDOW_WIDTH * 0.3 - (money_text.get_width() + icon_w) // 2, icon_y)
        )
        g.window.blit(
            money_text,
            (c.WINDOW_WIDTH * 0.3 - (money_text.get_width() + icon_w) // 2 + icon_w, text_y),
        )
        health_text = g.FONT.render(f"{p.player.health}", False, c.WHITE)
        g.window.blit(
            g.ICONS[1], (c.WINDOW_WIDTH * 0.7 - (health_text.get_width() + icon_w) // 2, icon_y)
        )
        g.window.blit(
            health_text,
            (c.WINDOW_WIDTH * 0.7 - (health_text.get_width() + icon_w) // 2 + icon_w, text_y),
        )
        score_text = g.FONT.render(f"{p.player.score:>08}", False, c.WHITE)
        g.window.blit(
            score_text,
            (
                c.WINDOW_WIDTH // 2 - score_text.get_width() // 2,
                c.WINDOW_HEIGHT - score_text.get_height() - text_y,
            ),
        )

        # right
        last_dragging_tower_type = self.dragging_tower_type
        for i, tower_type in enumerate(TowerType):
            if tower_type == last_dragging_tower_type:
                ui.context.current_id += 1
                continue
            ui.im_set_next_position(
                c.WINDOW_WIDTH - c.TILE_SIZE - 4, i * (c.TILE_SIZE + 6) + c.TILE_SIZE + 6
            )
            surf = TOWER_ANIMATIONS[tower_type.value].frames[0]
            if ui.im_button_image(
                [dim_sprite(surf), surf], f"{tower_type.name}\n-${TOWER_PRICES[tower_type.value]}"
            ):
                ui.context.held_id = -1
                if p.player.money >= TOWER_PRICES[tower_type.value]:
                    self.dragging_tower_type = tower_type

        # heading
        if p.player.health <= 0:
            heading = g.FONT_LARGE.render("GAME OVER", False, c.WHITE)
            g.window.blit(
                heading,
                (
                    c.WINDOW_WIDTH // 2 - heading.get_width() // 2,
                    c.WINDOW_HEIGHT // 2 - heading.get_height() // 2,
                ),
            )

        # hand
        hand_render()

    def exit(self) -> None:
        pass


# UTILS (SHOULD MOVE SOMEWHERE ELSE)
def tile_particle_burst(type: ParticleSpriteType, tile: Pos) -> None:
    particle_burst(
        type,
        count=8,
        position=((tile[0] + 0.5) * c.TILE_SIZE, (tile[1] + 0.5) * c.TILE_SIZE),
        position_variance=4,
        velocity=120,
        velocity_variance=20,
        lifespan=10,
        lifespan_variance=2,
    )


# TOWERS
def game_place_tower_at(self: Game, type: TowerType, tile: Pos) -> Tower:
    tower = Tower(tile[:], type, 0, c.UP, Animator(), Animator())
    animator_initialise(tower.animator, {0: TOWER_ANIMATIONS[type.value]})
    animator_initialise(tower.blending_anim, {0: Animation(g.BLENDING_FX[0:4], 0.08)})
    self.towers.append(tower)

    path.collision_grid[tower.tile[1]][tower.tile[0]] = True

    path.flowfield_copy(path.placement_flowfield, path.flowfield)

    p.player.money -= TOWER_PRICES[tower.type.value]

    tile_particle_burst(ParticleSpriteType.BUILD, tower.tile)
    g.camera.trauma = 0.35

    return tower


def game_place_tower_on(self: Game, type: TowerType, parent: Wire):
    game_attach_tower(self, parent, game_place_tower_at(self, type, parent.tile))


def game_delete_tower(self: Game, tower: Tower):
    self.towers.remove(tower)

    path.collision_grid[tower.tile[1]][tower.tile[0]] = False
    path.flowfield_regenerate(path.flowfield)

    p.player.money += TOWER_STATS[tower.type.value][tower.level].sell_price
    p.score_add(-100)

    tile_particle_burst(ParticleSpriteType.DELETE, tower.tile)
    g.camera.trauma = 0.35


def game_delete_tower_from(self: Game, parent: Wire):
    game_delete_tower(self, parent.tower)
    game_detach_tower(self, parent)

    # delete wires coming from cores
    if parent.incoming_side is None:
        assert parent in self.wires
        self.wires.remove(parent)
        stack = list(parent.outgoing_sides.values())
        while stack:
            wire = stack.pop()
            stack.extend(wire.outgoing_sides.values())
            game_delete_wire(self, wire, None)


def game_upgrade_tower(self: Game, tower: Tower):
    tower.level += 1
    # animator_switch_animation(tower.blending_anim, tower.level)

    p.player.money -= TOWER_PRICES[tower.type.value]

    tile_particle_burst(ParticleSpriteType.BUILD, tower.tile)
    g.camera.trauma = 0.35


def game_mode_tower_create(self: Game, tile: Pos | None, hov_wire: Wire | None):
    # tooltips
    if self.dragging_tower_type is not None:
        if tile in (path.PATH_START_TILE, path.PATH_END_TILE):
            hand.type = HandType.NO
        elif tile is not None:
            if (
                self.dragging_tower_type == TowerType.CORE
                and hov_wire is not None
                and (hov_wire.tower is None or hov_wire.tower.type != TowerType.CORE)
            ):
                hand.type = HandType.NO
                hand.tooltip = Tooltip("Place cores in empty space")

    # Idk how this is working so im just going to make my logic here and
    # recheck things
    ###########################################################################
    # Calculate if tower can be placed here and not block flowfield or enemies
    if self.dragging_tower_type is not None and tile != self.last_hov_pos:

        # Start or end tile
        if tile in (path.PATH_START_TILE, path.PATH_END_TILE):
            self.valid_placement = False

        # Outside grid
        elif not path.inside_grid(*tile):
            self.valid_placement = False

        # Already tower here
        elif path.collision_grid[tile[1]][tile[0]]:
            self.valid_placement = False

        self.valid_placement = path.flowfield_preview(*tile)

    if not self.valid_placement:
        hand.type = HandType.NO
    ###########################################################################

    for tower in self.towers:
        if tower.tile != tile:
            continue

        name = f"{tower.type.name} Lv {tower.level + 1}"

        if self.dragging_tower_type is not None:
            if self.dragging_tower_type == tower.type:
                if tower.level < MAX_TOWER_LEVEL:
                    hand.type = HandType.HOVER
                    hand.tooltip = Tooltip(
                        f"Upgrade {tower.type.name}\nLv {tower.level + 1} -> {tower.level + 2}"
                    )
                else:
                    hand.type = HandType.NO
                    hand.tooltip = Tooltip("MAX LEVEL")
            else:
                hand.type = HandType.NO

        elif p.player.mode == p.GameMode.DESTROY:
            hand.tooltip = Tooltip(
                f"{name}\n+${TOWER_STATS[tower.type.value][tower.level].sell_price}"
            )
            hand.type = HandType.HOVER
            if t.mouse_pressed():
                if hov_wire is not None:
                    game_delete_tower_from(self, hov_wire)
                else:
                    game_delete_tower(self, tower)

        elif p.player.mode == p.GameMode.VIEW:
            hand.tooltip = Tooltip(f"{name}\nPower: {tower_get_power(tower) * 100:.0f}%")
        break

    # placing
    if self.dragging_tower_type is None:
        return

    if g.mouse_buffer[t.MouseButton.LEFT] in (t.InputState.PRESSED, t.InputState.HELD):
        return

    if (
        tile not in (None, path.PATH_START_TILE, path.PATH_END_TILE)
        and p.player.money >= TOWER_PRICES[self.dragging_tower_type.value]
    ):
        # upgrade
        if (
            hov_wire is not None
            and hov_wire.tower is not None
            and hov_wire.tower.type == self.dragging_tower_type
            and hov_wire.tower.level < MAX_TOWER_LEVEL
        ):
            game_upgrade_tower(self, hov_wire.tower)

        # place normal tower
        elif self.dragging_tower_type != TowerType.CORE:
            if hov_wire is None and self.valid_placement:
                game_place_tower_at(self, self.dragging_tower_type, tile)
            else:
                if hov_wire is not None and hov_wire.tower is None:
                    game_place_tower_on(self, self.dragging_tower_type, hov_wire)

        # place core
        else:
            if hov_wire is None and self.valid_placement:
                tower = game_place_tower_at(self, self.dragging_tower_type, tile)
                self.wires.append(Wire(tile, None, {}, True, tower, tower))
                p.player.mode = p.GameMode.WIRING

    self.dragging_tower_type = None


# WIRES
def game_place_wire(self: Game, wire: Wire, parent: Wire):
    parent.outgoing_sides[c.INVERTED_DIRECTIONS[wire.incoming_side]] = wire
    for tower in self.towers:
        if tower.tile == wire.tile:
            game_attach_tower(self, wire, tower)
            break

    p.player.money -= 1

    tile_particle_burst(ParticleSpriteType.CREATE, wire.tile)


def game_delete_wire(self: Game, wire: Wire, parent: Wire | None):
    if parent is not None:
        parent.outgoing_sides = {
            dir: node for dir, node in parent.outgoing_sides.items() if node != wire
        }

    p.player.money += 1

    if wire.tower is None:
        tile_particle_burst(ParticleSpriteType.SHINY, wire.tile)


def game_attach_tower(self: Game, wire: Wire, tower: Tower):
    wire.tower = tower
    if wire.core_tower is not None:
        wire.core_tower.connected_tower_count += 1
        wire.tower.core_tower = wire.core_tower


def game_detach_tower(self: Game, wire: Wire):
    wire.tower = None
    if wire.core_tower is not None:
        wire.core_tower.connected_tower_count -= 1


def game_mode_wire_create(self: Game, tile: Pos | None, hov_wire: Wire | None):
    if t.mouse_pressed() and tile is not None:
        self.wire_draw_start = hov_wire

    if self.wire_draw_start is None:
        return

    if g.mouse_buffer[t.MouseButton.LEFT] not in (t.InputState.PRESSED, t.InputState.HELD):
        self.wire_draw_start = None
        hand.type = HandType.DEFAULT

    elif tile != self.wire_draw_start.tile and tile is not None:
        sx, sy = self.wire_draw_start.tile
        adjacent_sides = {
            (sx, sy - 1): c.UP,
            (sx - 1, sy): c.LEFT,
            (sx + 1, sy): c.RIGHT,
            (sx, sy + 1): c.DOWN,
        }

        # adjacent tile
        if tile in adjacent_sides:
            # place new wire
            if (overwrite := wire_find(self.wires, tile)[0]) is None:
                if p.player.money >= 1:
                    wire = Wire(tile[:], c.INVERTED_DIRECTIONS[adjacent_sides[tile]], {})
                    wire.core_tower = self.wire_draw_start.core_tower
                    game_place_wire(self, wire, self.wire_draw_start)
                    self.wire_draw_start = wire
                else:
                    hand.type = HandType.NO
                    hand.tooltip = Tooltip("Not enough money")

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


def game_mode_wire_destroy(self: Game, hov_wire: Wire | None, hov_wire_parent: Wire | None):
    if hov_wire is None or hov_wire.tower is not None or self.dragging_tower_type is not None:
        return

    if hov_wire.is_permanent:
        hand.type = HandType.NO
        return

    hand.type = HandType.HOVER

    if t.mouse_pressed():
        stack = list(hov_wire.outgoing_sides.values())
        while stack:
            wire = stack.pop()
            stack.extend(wire.outgoing_sides.values())
            game_delete_wire(self, wire, None)
        game_delete_wire(self, hov_wire, hov_wire_parent)
