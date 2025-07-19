from enum import IntEnum
import pygame

from components.hand import hand_render
from components.motion import Motion
import core.constants as c
import core.input as t
import core.globals as g

from components.statemachine import StateMachine, statemachine_change_state
from components.audio import play_music, stop_music
import components.ui as ui
from components.camera import (
    Camera,
    camera_update,
    camera_to_screen_shake,
)
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
        camera_update(self.camera, g.dt)

        g.window.fill(c.BLACK)

        if self.current_state == MenuState.MAIN:
            ui.im_reset_position(10, 10)
            if ui.im_button("play") or t.is_pressed(t.Action.START):
                statemachine_change_state(self.statemachine, manager.SceneState.GAME)
                ui.im_new()

            if ui.im_button("settings"):
                self.current_state = MenuState.SETTINGS
                ui.im_new()

            if ui.im_button("credits"):
                self.current_state = MenuState.CREDITS
                ui.im_new()

            if not c.IS_WEB:
                if ui.im_button("quit"):
                    # TODO: terminate gracefully
                    pygame.quit()

        elif self.current_state == MenuState.SETTINGS:
            if not settings_menu():
                self.current_state = MenuState.MAIN
                ui.im_new()

        elif self.current_state == MenuState.CREDITS:
            if t.is_pressed(t.Action.START) or t.mouse_pressed(t.MouseButton.LEFT):
                self.current_state = MenuState.MAIN
                ui.im_new()

            ui.im_reset_position(10, 10)
            ui.im_text("Made for the Kenney Game Jam 2025")
            ui.im_text("By ProfDragon and SebZanardo")

        if t.is_pressed(t.Action.START) or t.mouse_pressed(t.MouseButton.LEFT):
            self.camera.trauma += 0.5

        hand_render()

    def exit(self) -> None:
        stop_music()
