from collections.abc import Hashable
from dataclasses import dataclass

import pygame


@dataclass(slots=True)
class Animation:
    frames: list[pygame.Surface]
    frame_duration: float = 1.0
    loop: bool = True


@dataclass(slots=True)
class Animator:
    animations: dict[Hashable, Animation] = None
    state_id: Hashable = None
    frame_index: int = 0
    elapsed_time: float = 0.0


def animator_initialise(
    animator: Animator,
    animation_mapping: dict[Hashable, Animation],
    initial_id: Hashable | None = None,
) -> None:
    animator.animations = animation_mapping

    animator.state_id = initial_id
    if initial_id is None:
        animator.state_id = list(animation_mapping.keys())[0]


def animator_get_frame(animator: Animator) -> pygame.Surface:
    return animator.animations[animator.state_id].frames[animator.frame_index]


def animator_reset(animator: Animator) -> None:
    animator.frame_index = 0
    animator.elapsed_time = 0.0


def animator_switch_animation(animator: Animator, id: Hashable) -> None:
    # Cannot switch to current animation
    if id == animator.state_id:
        return

    if id not in animator.animations:
        return

    animator.state_id = id
    if id is not None:
        animator.frame_index %= len(animator.animations[id].frames)


def animator_update(animator: Animator, dt: float) -> None:
    animator.elapsed_time += dt
    if animator.state_id is not None:
        current_animation = animator.animations[animator.state_id]

    if animator.elapsed_time > current_animation.frame_duration:
        animator.frame_index += 1
        if animator.frame_index >= len(current_animation.frames):
            if current_animation.loop:
                animator.frame_index %= len(current_animation.frames)
            else:
                animator.frame_index = len(current_animation.frames) - 1
        animator.elapsed_time = 0.0
