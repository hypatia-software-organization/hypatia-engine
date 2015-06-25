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

__author__ = "Lillian Lemmer"
__copyright__ = "Copyright 2015, Lillian Lemmer"
__credits__ = ["Lillian Lemmer"]
__license__ = "MIT"
__maintainer__ = "Lillian Lemmer"
__email__ = "lillian.lynn.lemmer@gmail.com"
__status__ = "Development"



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
