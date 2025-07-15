import pygame

import core.constants as c
import core.input as i
import core.globals as g

from components.statemachine import StateMachine, statemachine_change_state
from components.audio import AudioChannel, play_sound
from components.ui import (
    Button,
    ui_list_render,
    ui_list_update_selection,
    button_activate
)

from scenes.scene import Scene
from scenes import manager


class Menu(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

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
            self.enter,
        )

        self.ui_credits_button = Button(
            "",
            pygame.Rect(208, 230, *c.BUTTON_SIZE),
            g.fonts.FONT.render("CREDITS", False, c.WHITE),
            self.enter,
        )

        self.ui_quit_button = Button(
            "",
            pygame.Rect(208, 250, *c.BUTTON_SIZE),
            g.fonts.FONT.render("QUIT", False, c.WHITE),
            self.enter,
        )

        self.ui_index = 0

        self.ui_list = [
            self.ui_start_button,
            self.ui_settings_button,
            self.ui_credits_button,
        ]
        if not c.IS_WEB:
            self.ui_list.append(self.ui_quit_button)

    def enter(self) -> None:
        pass

    def execute(self) -> None:
        mouse_position = pygame.mouse.get_pos()

        self.ui_index = ui_list_update_selection(self.ui_list, self.ui_index)

        # NOTE: Do we not already have this in ui??!?!
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

        # RENDER
        g.window.fill(c.RED)
        ui_list_render(self.ui_list, self.ui_index)

    def exit(self) -> None:
        pass

    def start_game(self) -> None:
        statemachine_change_state(self.statemachine, manager.SceneState.GAME)
