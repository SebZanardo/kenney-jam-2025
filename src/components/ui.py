from dataclasses import dataclass
import pygame

import core.globals as g
import core.input as i

from components.audio import AudioChannel, play_sound


Pos = tuple[int, int]
Bbox = tuple[int, int, int, int]
Colour = tuple[int, int, int]


@dataclass(slots=True)
class StyleUI:
    button_dim: Pos = (100, 20)
    checkbox_dim: Pos = (20, 20)
    slider_dim: Pos = (300, 20)

    padding_x: int = 5
    padding_y: int = 5

    background_colour: Colour = (0, 0, 0)
    hovered_colour: Colour = (50, 50, 50)
    clicked_colour: Colour = (100, 100, 100)
    main_colour: Colour = (255, 0, 255)
    text_colour: Colour = (255, 255, 255)


@dataclass(slots=True)
class ContextUI:
    rx: int = 0
    ry: int = 0

    # To track selected element for keyboard input and sliders
    current_id: int = 0
    hovered_id: int = -1
    held_id: int = -1

    # Where to render next element
    x: int = 0
    y: int = 0

    # Stored incase you want the next element to sit next to the current one
    last_x: int = 0
    last_y: int = 0

    def bbox(self, width: int, height: int) -> Bbox:
        rect = (
                self.x,
                self.y,
                width,
                height
            )

        self.last_x = self.x + width + style.padding_x
        self.last_y = self.y

        self.x = self.rx
        self.y += height + style.padding_y

        return rect

    def interact(self, bbox: bbox) -> tuple[bool, bool, bool]:
        mx, my = g.mouse_pos
        x, y, w, h = bbox

        hovered = False
        clicked = False
        held = False

        if self.held_id == self.current_id:
            if i.mouse_held(i.MouseButton.LEFT):
                held = True
            else:
                held = False
                self.held_id = -1

        elif mx >= x and my >= y and mx <= x + w and my <= y + h:
            hovered = True

            if self.hovered_id != self.current_id:
                play_sound(AudioChannel.UI, g.HOVER_SFX)
                self.hovered_id = self.current_id

            if (i.mouse_pressed(i.MouseButton.LEFT) and self.held_id == -1):
                clicked = True
                play_sound(AudioChannel.UI, g.SELECT_SFX)
                self.held_id = self.current_id

        self.current_id += 1

        return hovered, clicked, held


# GLOBALS #####################################################################
style = StyleUI()
context = ContextUI()
###############################################################################


def im_text(label: str) -> None:
    text = g.FONT.render(label, False, style.background_colour)
    bbox = context.bbox(*text.get_size())
    g.window.blit(text, (bbox[0], bbox[1]))


def im_button(label: str) -> bool:
    bbox = context.bbox(*style.button_dim)
    hovered, clicked, held = context.interact(bbox)
    g.window.blit(g.MENU_BUTTONS[0], (bbox[0], bbox[1]), (0, 0, *style.button_dim))
    if clicked:
        pass
    elif held:
        g.window.blit(g.MENU_BUTTONS[3], (bbox[0], bbox[1]), (0, 0, *style.button_dim))
    elif hovered:
        g.window.blit(g.MENU_BUTTONS[1], (bbox[0], bbox[1]), (0, 0, *style.button_dim))

    text = g.FONT.render(label, False, style.text_colour)
    g.window.blit(text, (bbox[0], bbox[1]))

    return clicked


def im_checkbox(value: list[bool]) -> bool:
    bbox = context.bbox(*style.checkbox_dim)
    hovered, clicked, held = context.interact(bbox)

    g.window.blit(g.MENU_BUTTONS[0], (bbox[0], bbox[1]), (0, 0, *style.checkbox_dim))

    if clicked:
        value[0] = not value[0]
    elif held:
        g.window.blit(g.MENU_BUTTONS[3], (bbox[0], bbox[1]), (0, 0, *style.checkbox_dim))
    elif hovered:
        g.window.blit(g.MENU_BUTTONS[1], (bbox[0], bbox[1]), (0, 0, *style.checkbox_dim))

    if value[0]:
        g.window.blit(g.MENU_BUTTONS[2], (bbox[0], bbox[1]), (0, 0, *style.checkbox_dim))

    return clicked


def im_slider(value: list[float], lo: float, hi: float) -> bool:
    bbox = context.bbox(*style.slider_dim)
    hovered, clicked, held = context.interact(bbox)
    g.window.blit(g.MENU_BUTTONS[0], (bbox[0], bbox[1]), (0, 0, *style.slider_dim))

    if held:
        percent = (g.mouse_pos[0] - bbox[0]) / style.slider_dim[0]
        difference = hi - lo
        value[0] = percent * difference + lo
        value[0] = min(max(value[0], lo), hi)
        g.window.blit(g.MENU_BUTTONS[3], (bbox[0], bbox[1]), (0, 0, *style.slider_dim))
    elif hovered:
        g.window.blit(g.MENU_BUTTONS[1], (bbox[0], bbox[1]), (0, 0, *style.slider_dim))

    g.window.blit(g.MENU_BUTTONS[2], (bbox[0], bbox[1]), (0, 0, value[0] / hi * style.slider_dim[0], bbox[3]))

    value_text = g.FONT.render(str(int(value[0])), False, style.text_colour)
    g.window.blit(value_text, (bbox[0], bbox[1]))

    return held


def im_same_line() -> None:
    context.x = context.last_x
    context.y = context.last_y


def im_set_next_position(x: int, y: int) -> None:
    context.x = x
    context.y = y


def im_reset_position(x: int, y: int) -> None:
    context.rx = x
    context.ry = y
    context.x = context.rx
    context.y = context.ry
    context.current_id = 0


def im_new() -> None:
    context.held_id = -1
