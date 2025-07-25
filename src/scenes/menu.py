from enum import IntEnum, auto
from dataclasses import dataclass
import random
import pygame

import core.constants as c
import core.globals as g
import core.input as t

from components.statemachine import StateMachine, statemachine_change_state
import components.enemy as e
from components.hand import HandType, hand, hand_render
from components.hud import hud_render
import components.ui as ui
from components.camera import camera_update, camera_to_screen_shake, camera_to_screen
from components.settings import settings_menu
from components.animation import Animator, animator_get_frame, animator_initialise, animator_update
from components.tower import TowerType, tower_particle_burst
from components.particles import particles_render, particles_update, particles_clear

from scenes.scene import Scene
from scenes import manager


class MenuState(IntEnum):
    MAIN = 0
    SETTINGS = auto()
    CREDITS = auto()


@dataclass(slots=True)
class EnemyWalker:
    x: int
    y: int
    type: e.EnemyType
    animator: Animator
    dead: bool = False


LEFT_BOUND = -64
RIGHT_BOUND = c.WINDOW_WIDTH + 32
TOP_BOUND = 16
BOTTOM_BOUND = c.WINDOW_HEIGHT - 120


class Menu(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

        self.current_state = MenuState.MAIN

    def enter(self) -> None:
        self.walking: list[EnemyWalker] = []
        for _ in range(20):
            w = EnemyWalker(
                random.randint(LEFT_BOUND, RIGHT_BOUND),
                random.randint(TOP_BOUND, BOTTOM_BOUND),
                random.choice(list(e.EnemyType)),
                Animator(),
            )
            animator_initialise(w.animator, {0: e.ENEMY_ANIMATIONS[w.type.value]})
            w.animator.frame_index = 0
            self.walking.append(w)

    def execute(self) -> None:
        hand.type = HandType.DEFAULT

        if t.mouse_held(t.MouseButton.LEFT):
            hand.type = HandType.GRAB

        hand.tooltip = None

        g.camera.trauma = min(g.camera.trauma, 0.5)
        camera_update(g.camera, g.dt)

        g.window.fill(c.BLACK)

        for w in self.walking:

            stat = e.ENEMY_STATS[w.type.value]
            w.x += stat.speed * c.TILE_SIZE

            animator_update(w.animator, g.dt)

            if w.x > RIGHT_BOUND or w.x < LEFT_BOUND or w.y > BOTTOM_BOUND or w.y < TOP_BOUND:
                w.x = LEFT_BOUND
                w.type = random.choice(list(e.EnemyType))
                animator_initialise(w.animator, {0: e.ENEMY_ANIMATIONS[w.type.value]})
                w.animator.frame_index = 0
                w.dead = False
            if not w.dead:
                # check for click
                frame = animator_get_frame(w.animator)
                surf = frame.copy()
                surf.set_alpha(50)

                x, y = camera_to_screen(g.camera, w.x, w.y)

                if (
                    t.mouse_pressed(t.MouseButton.LEFT)
                    and g.mouse_pos[0] >= x
                    and g.mouse_pos[0] <= x + surf.get_width()
                    and g.mouse_pos[1] >= y
                    and g.mouse_pos[1] <= y + surf.get_height()
                ):
                    tower_type = random.choice(list(TowerType)[1:])
                    tower_particle_burst(
                        tower_type, 0, w.x + surf.get_width() // 2, w.y + surf.get_height() // 2
                    )

                    g.camera.trauma += 0.2
                    w.dead = True

                g.window.blit(surf, camera_to_screen_shake(g.camera, w.x, w.y))

        particles_update()
        particles_render()

        hud_render()

        if self.current_state == MenuState.MAIN:
            ui.im_reset_position(
                c.WINDOW_WIDTH // 2 - ui.style.button_dim[0] // 2, c.WINDOW_HEIGHT // 2 - 2
            )
            if ui.im_button_text("play"):
                particles_clear()
                statemachine_change_state(self.statemachine, manager.SceneState.GAME)
                ui.im_new()

            if ui.im_button_text("settings"):
                self.current_state = MenuState.SETTINGS
                ui.im_new()

            if ui.im_button_text("credits"):
                self.current_state = MenuState.CREDITS
                ui.im_new()

            if not c.IS_WEB:
                if ui.im_button_text("quit"):
                    pygame.quit()
                    raise SystemExit

            g.window.blit(g.LOGO, (190, 40))

        elif self.current_state == MenuState.SETTINGS:
            if not settings_menu():
                self.current_state = MenuState.MAIN
                ui.im_new()

        elif self.current_state == MenuState.CREDITS:
            ui.im_reset_position(c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2 - 70)
            ui.im_text("Made for the Kenney Game Jam 2025", 0)
            ui.im_text("By ProfDragon and SebZanardo", 0)
            ui.im_text("", 0)
            ui.im_text("Textures - Kenney", 0)
            ui.im_text("Music - Darren Curtis", 0)

            ui.im_set_next_position(
                c.WINDOW_WIDTH // 2 - ui.style.button_dim[0] // 2, c.WINDOW_HEIGHT - 83
            )
            if ui.im_button_text("back"):
                self.current_state = MenuState.MAIN
                ui.im_new()

        # hand
        hand_render()

    def exit(self) -> None:
        pass
