import json
from os.path import exists
from custom.OneButtonPrompt.utils import path_fixed

DEFAULT_SETTINGS = {
    "OBP_preset": "Standard",
    "hint_chance": 25,
}

def load_settings():
    settings = {}
    # Add any missing default settings
    changed = False
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value
            changed = True
    return settings

default_settings = load_settings()
