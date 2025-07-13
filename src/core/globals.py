# Pygame Globals
# NOTE: These get init in setup
window = None
clock = None
scene_manager = None
mouse_buffer = None
action_buffer = None
last_action_pressed = None

# User settings
default_settings = {
    "music": 50,
    "sfx": 30,
    "fullscreen": False,
    "vsync": True,
    "screenshake": True,
}

settings = default_settings.copy()


# Dev settings
pass
