from enum import IntEnum, auto
import pygame


class AudioChannel(IntEnum):
    UI = 0
    MUSIC = auto()
    TOWER = auto()
    TOWER_ALT = auto()
    PLAYER = auto()
    BUILD = auto()
    WAVE = auto()


def set_music_volume(value: float) -> None:
    pygame.mixer.Channel(AudioChannel.MUSIC).set_volume(value / 2)


def set_sfx_volume(value: float) -> None:
    for channel in AudioChannel:
        if channel != AudioChannel.MUSIC:
            pygame.mixer.Channel(channel).set_volume(value / 2)


def channel_busy(channel: AudioChannel) -> bool:
    """
    Returns true if the channel is currently playing a sound
    """
    return pygame.mixer.Channel(channel).get_busy()


def play_sound(channel: AudioChannel, sound: pygame.mixer.Sound, *args) -> None:
    """
    Play sound in the channel, overriding any existing sound in that channel
    """
    pygame.mixer.Channel(channel).play(sound, *args)


def try_play_sound(channel: AudioChannel, sound: pygame.mixer.Sound, *args) -> bool:
    """
    Play sound in the channel if not busy. Returns true if successful
    """
    if channel_busy(channel):
        return False
    play_sound(channel, sound, *args)
    return True
