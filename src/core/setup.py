import pygame

import core.constants as c
import core.input as t
import core.globals as g

from components.statemachine import statemachine_initialise
from components.settings import load_settings
from components.motion import Motion
from components.camera import Camera

from scenes.manager import SCENE_MAPPING, SceneState


def setup() -> None:
    t.input_init()

    # These must be done after assets have been loaded
    pygame.display.set_caption(c.CAPTION)
    pygame.display.set_icon(g.ICON)
    pygame.mouse.set_visible(False)
    statemachine_initialise(g.scene_manager, SCENE_MAPPING, SceneState.MENU)

    g.camera = Camera(
        Motion.empty(),
        pygame.Vector2(
            c.WINDOW_WIDTH // 2 - c.GRID_WIDTH // 2, c.WINDOW_HEIGHT // 2 - c.GRID_HEIGHT // 2
        ),
        pygame.Vector2(),
        pygame.Vector2(30, 30),
    )

    # Try load settings from web
    load_settings()
    # print(g.setting_params)
    # print("Loaded settings")

    pygame.mouse.set_visible(False)
