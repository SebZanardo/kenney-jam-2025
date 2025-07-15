from enum import IntEnum
import pygame

import core.constants as c
import core.input as i
import core.globals as g

from components.statemachine import StateMachine, statemachine_change_state
from components.audio import AudioChannel, play_sound, play_music, stop_music
from components.ui import (
    Button,
    ui_list_render,
    ui_list_update_selection,
    button_activate
)
from components.settings import (
    settings_update,
    settings_render
)
from components.camera import (
    Camera,
    camera_update,
    camera_to_screen_shake,
)

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

        # buttons
        self.ui_start_button = Button(
            "",
            pygame.Rect(208, 190, *c.BUTTON_SIZE),
            g.fonts.FONT.render("START", False, c.WHITE),
            self.start_game,
        )

        self.ui_settings_button = Button(
            "",
            pygame.Rect(208, 210, *c.BUTTON_SIZE),
            g.fonts.FONT.render("SETTINGS", False, c.WHITE),
            self.switch_settings,
        )

        self.ui_credits_button = Button(
            "",
            pygame.Rect(208, 230, *c.BUTTON_SIZE),
            g.fonts.FONT.render("CREDITS", False, c.WHITE),
            self.switch_credit,
        )

        self.ui_quit_button = Button(
            "",
            pygame.Rect(208, 250, *c.BUTTON_SIZE),
            g.fonts.FONT.render("QUIT", False, c.WHITE),
            pygame.quit,
        )

        self.ui_index = 0

        self.ui_list = [
            self.ui_start_button,
            self.ui_settings_button,
            self.ui_credits_button,
        ]

        if not c.IS_WEB:
            self.ui_list.append(self.ui_quit_button)

        self.credit = g.fonts.FONT.render(
            "Made for kenney jam 2025",
            False,
            c.BLACK
        )

        self.camera = Camera.empty()

    def enter(self) -> None:
        play_music(g.music.NINTENDO, -1)

    def execute(self) -> None:
        mouse_position = pygame.mouse.get_pos()

        camera_update(self.camera, g.dt)

        if self.current_state == MenuState.MAIN:
            self.ui_index = ui_list_update_selection(self.ui_list, self.ui_index)

            # NOTE: Do we not already have this logic in settings?!!!
            if g.mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED:
                for element in self.ui_list:
                    if element.rect.collidepoint(mouse_position):
                        button_activate(element)
                        play_sound(AudioChannel.UI, g.sfx.SELECT)

            if self.ui_index is not None:
                element = self.ui_list[self.ui_index]
                if (
                    i.is_pressed(i.Action.A)
                    or i.is_pressed(i.Action.SELECT)
                    or i.is_pressed(i.Action.START)
                ):
                    button_activate(element)
                    play_sound(AudioChannel.UI, g.sfx.SELECT)

        elif self.current_state == MenuState.SETTINGS:
            settings_update()
            if g.settings.should_exit:
                self.current_state = MenuState.MAIN
                g.settings.should_exit = False
                return

        elif self.current_state == MenuState.CREDITS:
            if (
                g.action_buffer[i.Action.START] == i.InputState.PRESSED or
                g.mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED
            ):
                self.current_state = MenuState.MAIN
                return

        if (
            g.action_buffer[i.Action.START] == i.InputState.PRESSED or
            g.mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED
        ):
            self.camera.trauma += 0.5

        # RENDER
        g.window.fill(c.RED)

        g.window.blit(
            g.sprites.ICON,
            camera_to_screen_shake(self.camera, 0, 0)
        )

        if self.current_state == MenuState.MAIN:
            ui_list_render(self.ui_list, self.ui_index)

        elif self.current_state == MenuState.SETTINGS:
            settings_render()

        elif self.current_state == MenuState.CREDITS:
            g.window.blit(
                self.credit,
                (100, 100)
            )

    def exit(self) -> None:
        stop_music()

    def start_game(self) -> None:
        statemachine_change_state(self.statemachine, manager.SceneState.GAME)

    def switch_settings(self) -> None:
        self.current_state = MenuState.SETTINGS

    def switch_credit(self) -> None:
        self.current_state = MenuState.CREDITS
