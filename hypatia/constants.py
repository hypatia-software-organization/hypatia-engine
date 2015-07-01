# engine/constants.py
# Lillian Lemmer <lillian.lynn.lemmer@gmail.com>
#
# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""Constants for Hypatia Engine

Right now this just contains stuff pertaining to Walkabout, i.e.,
direction and action specifications. These classes are to be passed as
parameters.

Examples:
  >>> import sprites
  >>> sprite = sprites.Walkabout()
  >>> sprite.animations[Walk][Right]
  <Animation Object>

"""

from enum import Enum

class Direction(Enum):
    """Specific to movement of a sprite/surface."""
    Up = 1
    Down = 2
    Left = 3
    Right = 4


class Action(Enum):
    Walk = 1
    Stand = 2
