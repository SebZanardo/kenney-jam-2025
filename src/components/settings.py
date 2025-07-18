from dataclasses import dataclass
import pygame

import core.constants as c
import core.input as i
import core.globals as g

from components.audio import (
    AudioChannel,
    play_sound,
    set_music_volume,
    set_sfx_volume
)
from components.ui import (
    Slider,
    Checkbox,
    Button,
    button_activate,
    checkbox_set_enabled,
    slider_set_value,
    slider_set_value_mouse,
    checkbox_toggle,
    ui_list_render,
    ui_list_update_selection,
)


@dataclass
class Settings:
    def __init__(self) -> None:
        self.title = g.FONT.render("SETTINGS", False, c.WHITE)

        self.graphic_enabled = g.FONT.render("Enabled", False, c.GREEN)
        self.graphic_disabled = g.FONT.render("Disabled", False, c.RED)

        self.ui_music_slider = Slider(
            "music",
            pygame.Rect(250, 75, *c.BUTTON_SIZE),
            0,
            100,
            0,
            None,
            g.FONT.render("MUSIC VOLUME", False, c.WHITE),
            None,
            lambda value: set_music_volume(value / 100.0),
        )

        self.ui_sfx_slider = Slider(
            "sfx",
            pygame.Rect(250, 100, *c.BUTTON_SIZE),
            0,
            100,
            0,
            None,
            g.FONT.render("SFX VOLUME", False, c.WHITE),
            None,
            lambda value: set_sfx_volume(value / 100.0),
        )

        self.ui_fullscreen_checkbox = Checkbox(
            "fullscreen",
            pygame.Rect(250, 100, *c.BUTTON_SIZE),
            self.graphic_enabled,
            self.graphic_disabled,
            False,
            g.FONT.render("FULLSCREEN?", False, c.WHITE),
            None,
        )

        self.ui_vsync_checkbox = Checkbox(
            "vsync",
            pygame.Rect(250, 125, *c.BUTTON_SIZE),
            self.graphic_enabled,
            self.graphic_disabled,
            True,
            g.FONT.render("VSYNC?", False, c.WHITE),
            None,
        )

        self.ui_screenshake_checkbox = Checkbox(
            "screenshake",
            pygame.Rect(250, 125, *c.BUTTON_SIZE),
            self.graphic_enabled,
            self.graphic_disabled,
            True,
            g.FONT.render("SCREENSHAKE?", False, c.WHITE),
            None,
        )

        self.ui_default_button = Button(
            "",
            pygame.Rect(250, 150, *c.BUTTON_SIZE),
            g.FONT.render("DEFAULT", False, c.WHITE),
            lambda: settings_reset(),
        )

        self.ui_back_button = Button(
            "",
            pygame.Rect(250, 185, *c.BUTTON_SIZE),
            g.FONT.render("< BACK", False, c.WHITE),
            lambda: settings_exit(),
        )

        # the slider currently being dragged by the mouse
        self.selected_slider = None

        self.ui_index = 0

        self.ui_list = [
            self.ui_music_slider,
            self.ui_sfx_slider,
            # self.ui_fullscreen_checkbox,
            # self.ui_vsync_checkbox,
            self.ui_screenshake_checkbox,
            self.ui_default_button,
            self.ui_back_button,
        ]

        self.should_exit = False


def settings_load() -> None:
    for element in g.settings.ui_list:
        if element.key in g.setting_params:
            value = g.setting_params[element.key]
            if isinstance(element, Checkbox):
                checkbox_set_enabled(element, value)
            elif isinstance(element, Slider):
                slider_set_value(element, value)


def settings_reset() -> None:
    g.setting_params = g.default_setting_params.copy()
    settings_load()


def settings_exit() -> None:
    g.settings.should_exit = True


def settings_update() -> None:
    g.settings.ui_index = ui_list_update_selection(
        g.settings.ui_list,
        g.settings.ui_index,
    )

    if g.settings.selected_slider:
        if g.mouse_buffer[i.MouseButton.LEFT] == i.InputState.RELEASED:
            play_sound(AudioChannel.UI, g.SELECT_SFX)
            g.settings.selected_slider = None
        else:
            slider_set_value_mouse(g.settings.selected_slider)

    else:
        # MOUSE INPUT
        if g.mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED:
            element_mouse_update()

        # KEYBOARD INPUT
        if (
            g.settings.selected_slider is None and
            g.settings.ui_index is not None
        ):
            element = g.settings.ui_list[g.settings.ui_index]
            element_keyboard_update(element)


def element_mouse_update() -> None:
    mouse_position = pygame.mouse.get_pos()

    for element in g.settings.ui_list:
        if element.rect.collidepoint(mouse_position):
            if isinstance(element, Button):
                button_activate(element)
                play_sound(AudioChannel.UI, g.SELECT_SFX)
            elif isinstance(element, Checkbox):
                checkbox_toggle(element)
                play_sound(AudioChannel.UI, g.SELECT_SFX)
            elif isinstance(element, Slider):
                g.settings.selected_slider = element


def element_keyboard_update(element) -> None:
    if i.is_pressed(i.Action.A):
        if isinstance(element, Button):
            button_activate(element)
        elif isinstance(element, Checkbox):
            checkbox_toggle(element)
        play_sound(AudioChannel.UI, g.SELECT_SFX)
    elif i.is_held(i.Action.LEFT):
        if isinstance(element, Slider):
            slider_set_value(element, element.value - 0.5)
    elif i.is_held(i.Action.RIGHT):
        if isinstance(element, Slider):
            slider_set_value(element, element.value + 0.5)
    elif i.is_released(i.Action.LEFT):
        if isinstance(element, Slider):
            play_sound(AudioChannel.UI, g.SELECT_SFX)
    elif i.is_released(i.Action.RIGHT):
        if isinstance(element, Slider):
            play_sound(AudioChannel.UI, g.SELECT_SFX)


def settings_render() -> None:
    g.window.blit(
        g.settings.title,
        (g.window.get_width() // 2 - g.settings.title.get_width() // 2, 40)
    )

    g.window.blit(
        g.MENU_CONTROLS,
        (g.window.get_width() // 2 - g.MENU_CONTROLS.get_width() // 2, 215)
    )

    ui_list_render(g.settings.ui_list, g.settings.ui_index)
