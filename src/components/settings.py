# TODO: This needs to be debugged as missing assets among other things
from dataclasses import dataclass
import pygame

import core.constants as c
import core.input as i
import core.assets as a
import core.globals as g

from components.audio import (
    AudioChannel,
    play_sound,
    set_music_volume,
    set_sfx_volume
)
from components.ui import (
    BUTTON_SIZE,
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
        self.title = a.FONT.render("SETTINGS", False, c.WHITE)

        self.graphic_enabled = a.FONT.render("Enabled", False, c.GREEN)
        self.graphic_disabled = a.FONT.render("Disabled", False, c.RED)

        self.ui_music_slider = Slider(
            "music",
            pygame.Rect(250, 75, *BUTTON_SIZE),
            0,
            100,
            0,
            None,
            a.FONT.render("MUSIC VOLUME", False, c.WHITE),
            None,
            lambda value: set_music_volume(value / 100.0),
        )

        self.ui_sfx_slider = Slider(
            "sfx",
            pygame.Rect(250, 100, *BUTTON_SIZE),
            0,
            100,
            0,
            None,
            a.FONT.render("SFX VOLUME", False, c.WHITE),
            None,
            lambda value: set_sfx_volume(value / 100.0),
        )

        self.ui_fullscreen_checkbox = Checkbox(
            "fullscreen",
            pygame.Rect(250, 100, *BUTTON_SIZE),
            self.graphic_enabled,
            self.graphic_disabled,
            False,
            a.FONT.render("FULLSCREEN?", False, c.WHITE),
            None,
        )

        self.ui_vsync_checkbox = Checkbox(
            "vsync",
            pygame.Rect(250, 125, *BUTTON_SIZE),
            self.graphic_enabled,
            self.graphic_disabled,
            True,
            a.FONT.render("VSYNC?", False, c.WHITE),
            None,
        )

        self.ui_screenshake_checkbox = Checkbox(
            "screenshake",
            pygame.Rect(250, 125, *BUTTON_SIZE),
            self.graphic_enabled,
            self.graphic_disabled,
            True,
            a.FONT.render("SCREENSHAKE?", False, c.WHITE),
            None,
        )

        self.ui_default_button = Button(
            "",
            pygame.Rect(250, 150, *BUTTON_SIZE),
            a.FONT.render("DEFAULT", False, c.WHITE),
            lambda: settings_reset(self),
        )

        self.ui_back_button = Button(
            "",
            pygame.Rect(250, 185, *BUTTON_SIZE),
            a.FONT.render("< BACK", False, c.WHITE),
            lambda: settings_exit(self),
        )

        # the slider currently being dragged by the mouse
        self.selected_slider = None

        self.ui_index = 0
        self.last_mouse_position = None

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


def settings_load(settings: Settings) -> None:
    for element in settings.ui_list:
        if element.key in g.settings:
            value = g.settings[element.key]
            if isinstance(element, Checkbox):
                checkbox_set_enabled(element, value)
            elif isinstance(element, Slider):
                slider_set_value(element, value)


def settings_reset(settings: Settings) -> None:
    g.settings = g.default_settings.copy()
    settings_load(settings)


def settings_exit(settings: Settings) -> None:
    settings.should_exit = True


def settings_update(
    settings: Settings,
    dt: float,
    action_buffer: i.InputBuffer,
    mouse_buffer: i.InputBuffer,
) -> None:
    mouse_position = pygame.mouse.get_pos()

    mouse_to_pass = None
    if (
        settings.selected_slider is None and
        mouse_position != settings.last_mouse_position
    ):
        mouse_to_pass = mouse_position

    settings.ui_index = ui_list_update_selection(
        action_buffer,
        mouse_to_pass,
        settings.ui_list,
        settings.ui_index,
    )

    if settings.selected_slider:
        if mouse_buffer[i.MouseButton.LEFT] == i.InputState.RELEASED:
            play_sound(AudioChannel.UI, a.UI_SELECT)
            settings.selected_slider = None
        else:
            slider_set_value_mouse(settings.selected_slider, mouse_position[0])

    else:
        # MOUSE INPUT
        if mouse_buffer[i.MouseButton.LEFT] == i.InputState.PRESSED:
            element_mouse_update(settings)

        # KEYBOARD INPUT
        if settings.selected_slider is None and settings.ui_index is not None:
            element = settings.ui_list[settings.ui_index]
            element_keyboard_update(element, action_buffer)

    settings.last_mouse_position = mouse_position


def element_mouse_update(settings: Settings) -> None:
    mouse_position = pygame.mouse.get_pos()

    for element in settings.ui_list:
        if element.rect.collidepoint(mouse_position):
            if isinstance(element, Button):
                button_activate(element)
                play_sound(AudioChannel.UI, a.UI_SELECT)
            elif isinstance(element, Checkbox):
                checkbox_toggle(element)
                play_sound(AudioChannel.UI, a.UI_SELECT)
            elif isinstance(element, Slider):
                settings.selected_slider = element


def element_keyboard_update(element, action_buffer: i.InputBuffer) -> None:
    if i.is_pressed(action_buffer, i.Action.A):
        if isinstance(element, Button):
            button_activate(element)
        elif isinstance(element, Checkbox):
            checkbox_toggle(element)
        play_sound(AudioChannel.UI, a.UI_SELECT)
    elif i.is_held(action_buffer, i.Action.LEFT):
        if isinstance(element, Slider):
            slider_set_value(element, element.value - 0.5)
    elif i.is_held(action_buffer, i.Action.RIGHT):
        if isinstance(element, Slider):
            slider_set_value(element, element.value + 0.5)
    elif i.is_released(action_buffer, i.Action.LEFT):
        if isinstance(element, Slider):
            play_sound(AudioChannel.UI, a.UI_SELECT)
    elif i.is_released(action_buffer, i.Action.RIGHT):
        if isinstance(element, Slider):
            play_sound(AudioChannel.UI, a.UI_SELECT)


def settings_render(settings: Settings, surface: pygame.Surface) -> None:
    surface.blit(
        settings.title,
        (surface.get_width() // 2 - settings.title.get_width() // 2, 40)
    )

    surface.blit(
        a.MENU_CONTROLS,
        (surface.get_width() // 2 - a.MENU_CONTROLS.get_width() // 2, 215)
    )

    ui_list_render(surface, settings.ui_list, settings.ui_index)
