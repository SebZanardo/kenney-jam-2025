import copy

import core.globals as g

import components.ui as ui
from components.audio import (
    set_music_volume,
    set_sfx_volume
)


def settings_menu() -> bool:
    ui.im_reset_position(10, 100)

    ui.im_text("Music Volume: ")
    ui.im_same_line()
    if ui.im_slider(g.setting_params["music"], 0, 100):
        set_music_volume(g.setting_params["music"][0] / 100)

    ui.im_text("Sound Volume: ")
    ui.im_same_line()
    if ui.im_slider(g.setting_params["sfx"], 0, 100):
        set_sfx_volume(g.setting_params["sfx"][0] / 100)

    ui.im_text("Screenshake:  ")
    ui.im_same_line()
    ui.im_checkbox(g.setting_params["screenshake"])

    if ui.im_button("reset"):
        g.setting_params = copy.deepcopy(g.default_setting_params)

    if ui.im_button("back"):
        return False

    return True
