"""This module handles configuration of the game.
"""

import io

try:
    import ConfigParser as configparser

except ImportError:
    import configparser


DEFAULT_CONFIG = """
[game]
name = Hypatia
savedirname = hypatia

[display]
screen_size = 320x240
window_size = 800x600
scaleup = true
fullscreen = false
maxfps = 60
"""
"""The default game configuration."""


def create_config():
    """Creates a ConfigParser instance with the default configuration
    loaded into it.

    Returns: a ConfigParser instance
    """

    c = configparser.ConfigParser()
    c.readfp(io.StringIO(DEFAULT_CONFIG))
    return c
