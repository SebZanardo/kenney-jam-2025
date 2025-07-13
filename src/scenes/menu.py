import pygame

import core.assets as a
import core.constants as c
import core.input as i
import core.globals as g

from components.statemachine import StateMachine, statemachine_change_state

from scenes.scene import Scene
from scenes import manager


class Menu(Scene):
    def __init__(self, statemachine: StateMachine) -> None:
        super().__init__(statemachine)

    def enter(self) -> None:
        pass

    def execute(self) -> None:
        # UPDATE
        if (
            g.action_buffer[i.Action.START] == i.InputState.PRESSED or
            g.mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED
        ):
            statemachine_change_state(
                self.statemachine,
                manager.SceneState.GAME
            )
            return

        # RENDER
        g.window.fill(c.RED)

    def exit(self) -> None:
        pass
