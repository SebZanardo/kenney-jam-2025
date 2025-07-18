import platform
import pygame
import json

import core.constants as c
import core.input as i
import core.globals as g

from components.statemachine import statemachine_initialise
# from components.settings import Settings, settings_load

from scenes.manager import SCENE_MAPPING, SceneState


def setup() -> None:
    i.input_init()

    # These must be done after assets have been loaded
    pygame.display.set_caption(c.CAPTION)
    pygame.display.set_icon(g.ICON)
    statemachine_initialise(g.scene_manager, SCENE_MAPPING, SceneState.MENU)

    # Try load settings from web
    load_settings()
    print("Loaded settings")

    # g.settings = Settings()
    # settings_load()


def load_settings() -> None:
    if not c.IS_WEB:
        return

    json_str = platform.window.localStorage.getItem("settings")

    if not json_str:
        return

    is_cooked = False

    try:
        g.setting_params = json.loads(json_str)
    except json.JSONDecodeError:
        is_cooked = True

    finally:
        for key in g.default_setting_params.keys():
            if key not in g.setting_params:
                is_cooked = True
                break

    if is_cooked:
        g.setting_params = g.default_setting_params.copy()
        print("Cooked settings :(")
        write_settings()


def write_settings() -> None:
    if not c.IS_WEB:
        return
    json_str = json.dumps(g.setting_params)
    platform.window.localStorage.setItem("settings", json_str)
