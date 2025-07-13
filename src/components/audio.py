from enum import IntEnum, auto
import pygame


class AudioChannel(IntEnum):
    UI = 0
    STATIC = auto()
    PLAYER = auto()
    PLAYER_ALT = auto()
    ENTITY = auto()
    ENTITY_ALT = auto()


def play_music(path: str, *args) -> None:
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(*args)


# returns true if the channel is currently playing a sound
def channel_busy(channel: AudioChannel) -> bool:
    return pygame.mixer.Channel(channel).get_busy()


# play a sound in the given channel, overriding any existing sound in that channel
def play_sound(channel: AudioChannel, sound: pygame.mixer.Sound, *args) -> None:
    pygame.mixer.Channel(channel).play(sound, *args)


# play a sound in the given channel if not busy. returns true if successful
def try_play_sound(channel: AudioChannel, sound: pygame.mixer.Sound, *args) -> bool:
    if channel_busy(channel):
        return False
    play_sound(channel, sound, *args)
    return True


def stop_music() -> None:
    pygame.mixer.music.stop()


def set_music_volume(value: float) -> None:
    pygame.mixer.music.set_volume(value)


def set_sfx_volume(value: float) -> None:
    for channel in AudioChannel:
        pygame.mixer.Channel(channel).set_volume(value)

