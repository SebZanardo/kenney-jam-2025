from enum import IntEnum
import pygame

from components.hand import HandType, hand, hand_render
from components.motion import Motion
import core.constants as c
import core.input as t
import core.globals as g

from components.statemachine import StateMachine, statemachine_change_state
from components.audio import play_music, stop_music
import components.ui as ui
from components.camera import Camera, camera_update
from components.settings import settings_menu

from scenes.scene import Scene
from scenes import manager


class MenuState(IntEnum):
    MAIN = 0
    SETTINGS = 1
    CREDITS = 2


class Menu(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

        self.current_state = MenuState.MAIN
        self.camera = Camera(
            Motion.empty(),
            pygame.Vector2(),
            pygame.Vector2(),
            pygame.Vector2(),
        )

    def enter(self) -> None:
        play_music(g.NINTENDO_MUSIC, -1)

    def execute(self) -> None:
        hand.type = HandType.DEFAULT
        hand.tooltip = None

        camera_update(self.camera, g.dt)

        g.window.fill(c.BLACK)

        if self.current_state == MenuState.MAIN:
            ui.im_reset_position(
                c.WINDOW_WIDTH // 2 - ui.style.button_dim[0] // 2, c.WINDOW_HEIGHT // 2
            )
            if ui.im_button_text("play") or t.is_pressed(t.Action.START):
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

        elif self.current_state == MenuState.SETTINGS:
            if not settings_menu():
                self.current_state = MenuState.MAIN
                ui.im_new()

        elif self.current_state == MenuState.CREDITS:
            ui.im_reset_position(c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2 - 50)
            ui.im_text("Made for the Kenney Game Jam 2025", 0)
            ui.im_text("By ProfDragon and SebZanardo", 0)
            ui.im_text("", 0)
            ui.im_text("Textures - Kenney", 0)
            ui.im_text("Music - Darren Curtis", 0)

            ui.im_set_next_position(
                c.WINDOW_WIDTH // 2 - ui.style.button_dim[0] // 2, c.WINDOW_HEIGHT - 80
            )
            if ui.im_button_text("back"):
                self.current_state = MenuState.MAIN
                ui.im_new()

        if t.is_pressed(t.Action.START) or t.mouse_pressed(t.MouseButton.LEFT):
            self.camera.trauma += 0.5

        # hand
        hand_render()

    def exit(self) -> None:
        stop_music()
