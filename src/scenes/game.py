import pygame

from components.animation import (
    Animation,
    Animator,
    animator_get_frame,
    animator_initialise,
    animator_update,
)
from components.camera import Camera, camera_from_screen, camera_to_screen, camera_to_screen_shake
from components.motion import Motion
from components.tower import Tower, tower_create_animator, tower_render, tower_update
import core.constants as c
import core.input as i
import core.globals as g

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

        # we can make this a 2d array if needed for pathfinding
        self.towers: list[Tower] = []

        self.blending_anim = Animator()
        animator_initialise(self.blending_anim, {0: Animation(g.BLENDING_FX, 0.1)})

    def execute(self) -> None:
        # UPDATE
        if g.action_buffer[i.Action.START] == i.InputState.PRESSED:
            statemachine_change_state(self.statemachine, manager.SceneState.MENU)
            return

        # mouse pos in camera space
        hand_pos = camera_from_screen(self.camera, *g.mouse_pos)

        # hovered tile pos
        tile_pos = (hand_pos[0] // c.TILE_SIZE, hand_pos[1] // c.TILE_SIZE)

        # user interaction (place tower)
        if i.mouse_pressed():
            tower = Tower(tile_pos[:])
            tower_create_animator(tower)
            self.towers.append(tower)

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

        # enemies
        pass

        # towers
        if 0 <= tile_pos[0] < c.GRID_WIDTH_TILES and 0 <= tile_pos[1] < c.GRID_HEIGHT_TILES:
            tile_preview = g.POTIONS[0].copy()
            tile_preview.set_alpha(200)
            tile_preview.blit(
                animator_get_frame(self.blending_anim), special_flags=pygame.BLEND_MULT
            )
            g.window.blit(
                tile_preview,
                camera_to_screen(self.camera, tile_pos[0] * c.TILE_SIZE, tile_pos[1] * c.TILE_SIZE),
            )

        for tower in self.towers:
            tower_render(tower, self.camera)

        # If we want to replace the cursor with the Kenney hand:
        # g.window.blit(
        #     g.HANDS[0],
        #     camera_to_screen(self.camera, hand_pos[0] - 4, hand_pos[1] - 2),
        # )

    def exit(self) -> None:
        pass
