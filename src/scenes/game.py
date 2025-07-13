import pygame

import core.assets as a
import core.constants as c
import core.input as i
import core.globals as g

from core.setup import window

from components.statemachine import StateMachine, statemachine_change_state

from scenes.scene import Scene
from scenes import manager


class Game(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

    # runs when game starts (or is resumed but thats not a thing)
    def enter(self) -> None:
        pass

    def execute(
        self,
        dt: float,
        action_buffer: i.InputBuffer,
        mouse_buffer: i.InputBuffer,
    ) -> None:
        # UPDATE
        if (
            action_buffer[i.Action.START] == i.InputState.PRESSED or
            mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED
        ):
            statemachine_change_state(
                self.statemachine,
                manager.SceneState.MENU
            )
            return

        # RENDER
        window.fill(c.BLUE)

    def exit(self) -> None:
        pass
