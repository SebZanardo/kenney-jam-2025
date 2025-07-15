import platform
import pygame
import json

import core.constants as c
import core.globals as g
import core.input as i
import core.assets as a

from components.statemachine import StateMachine, statemachine_initialise
from components.settings import Settings, settings_load

from scenes.manager import SCENE_MAPPING, SceneState


def setup() -> None:
    pygame.init()

    # GLOBALS #################################################################
    g.window = setup_window()
    g.clock = pygame.time.Clock()

    g.scene_manager = StateMachine()

    g.mouse_buffer = [i.InputState.NOTHING for _ in i.MouseButton]
    g.action_buffer = [i.InputState.NOTHING for _ in i.Action]
    g.last_action_pressed = [i.action_mappings[a][0] for a in i.Action]

    g.fonts = a.Fonts()
    g.sprites = a.Sprites()
    g.sfx = a.Sfx()
    g.music = a.Music()
    ###########################################################################

    pygame.display.set_caption(c.CAPTION)

    print("Setup complete")

    # Try load settings from web
    load_settings()
    print("Loaded settings")

    # Try load assets
    a.load_fonts()
    a.load_sprites()
    a.load_sfx()
    print("Loaded assets")

    # These must be done after assets have been loaded
    pygame.display.set_icon(g.sprites.ICON)
    statemachine_initialise(g.scene_manager, SCENE_MAPPING, SceneState.MENU)
    g.settings = Settings()
    settings_load()


def setup_window() -> pygame.Surface:
    if c.IS_WEB:
        platform.window.canvas.style.imageRendering = "pixelated"
        return pygame.display.set_mode(c.WINDOW_SETUP["size"])
    else:
        return pygame.display.set_mode(**c.WINDOW_SETUP)


def load_settings() -> None:
    if not c.IS_WEB:
        return

    json_str = platform.window.localStorage.getItem("settings")

    if not json_str:
        return

    is_cooked = False

    try:
        g.settings = json.loads(json_str)
    except json.JSONDecodeError:
        is_cooked = True

    finally:
        for key in g.default_settings.keys():
            if key not in g.settings:
                is_cooked = True
                break

    if is_cooked:
        g.settings = g.default_settings.copy()
        print("Cooked settings :(")
        write_settings()


def write_settings() -> None:
    if not c.IS_WEB:
        return
    json_str = json.dumps(g.settings)
    platform.window.localStorage.setItem("settings", json_str)
