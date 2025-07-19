import copy
import json
import platform

import core.globals as g
import core.constants as c

import components.ui as ui
from components.audio import set_music_volume, set_sfx_volume


def settings_menu() -> bool:
    ui.im_reset_position(10, 10)

    ui.im_text("Music Volume ")
    ui.im_same_line()
    if ui.im_slider(g.setting_params["music"], 0, 100):
        set_music_volume(g.setting_params["music"][0] / 100)

    ui.im_text("Sound Volume ")
    ui.im_same_line()
    if ui.im_slider(g.setting_params["sfx"], 0, 100):
        set_sfx_volume(g.setting_params["sfx"][0] / 100)

    ui.im_text("Screenshake ")
    ui.im_same_line()
    ui.im_checkbox(g.setting_params["screenshake"])

    if ui.im_button("reset"):
        g.setting_params = copy.deepcopy(g.default_setting_params)

    if ui.im_button("back"):
        write_settings()
        return False

    return True


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
            if key not in g.setting_params or not isinstance(g.setting_params[key], list):
                is_cooked = True
                break

    if is_cooked:
        g.setting_params = g.default_setting_params.copy()
        print("Cooked settings :(")
        write_settings()

    # Set volume
    set_music_volume(g.setting_params["music"][0] / 100)
    set_sfx_volume(g.setting_params["sfx"][0] / 100)


def write_settings() -> None:
    if not c.IS_WEB:
        return
    json_str = json.dumps(g.setting_params)
    platform.window.localStorage.setItem("settings", json_str)
