# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""py.test unit testing for hypatia/constants.py

"""

import os

import pygame
import pytest

from hypatia import physics
from hypatia import constants

try:
    os.chdir('demo')
except OSError:
    pass


class TestDirection(object):
    """Various tests for py.test regarding constants.Direction.

    See Also:
        constants.Direction

    """

    def test_add(self):
        """Assure that adding cardinal directions
        together produces an ordinal direction.

        """

        # North + West == North West
        assert (constants.Direction.north + constants.Direction.west ==
                constants.Direction.north_west)
        # North + East == North East
        assert (constants.Direction.north + constants.Direction.east ==
                constants.Direction.north_east)
        # South + West == South West
        assert (constants.Direction.south + constants.Direction.west ==
                constants.Direction.south_west)
        # South + East = South East
        assert (constants.Direction.south + constants.Direction.east ==
                constants.Direction.south_east)

    def test_disposition(self):
        """Assure the ability to get a pixel (x, y) offset
        from a direction using Direction.disposition() works.

        """

        direction = constants.Direction

        # north disposition of 1 is (0, -1)
        # The default offset/padding is 1.
        assert direction.disposition(direction.north) == (0, -1)

        # north east disposition of 98 is (98, -98)
        assert direction.disposition(direction.north_east, 98,) == (98, -98)

        # east disposition of 9 is (9, 0):
        assert direction.disposition(direction.east, 9) == (9, 0)

        # South East disposition of 30 is (30, 30)
        assert direction.disposition(direction.south_east, 30) == (30, 30)

        # South disposition of 4 is (0, 4)
        assert direction.disposition(direction.south, 4) == (0, 4)

        # South West disposition of 8 is (-8, 8)
        assert direction.disposition(direction.south_west, 8) == (-8, 8)

        # A west disposition of 1 is (-1, 0)
        assert direction.disposition(direction.west, margin=1) == (-1, 0)

        # north west disposition of 55 is (-55, -55)
        assert direction.disposition(direction.north_west, 55) == (-55, -55)

    def test_from_velocity(self):
        """Check that we are reliably producing
        a direction from a given velocity.

        """

        # (0, -8) is moving North
        velocity = physics.Velocity(0, -8)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.north)

        # (999, 0) is moving East
        velocity = physics.Velocity(999, 0)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.east)

        # (0, 1) is moving South
        velocity = physics.Velocity(0, 1)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.south)

        # (-10, 0) is moving West
        velocity = physics.Velocity(-10, 0)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.west)

        # (2, -5) is moving North East
        velocity = physics.Velocity(2, -5)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.north_east)

        # (73, 9) is moving South East
        velocity = physics.Velocity(73, 9)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.south_east)

        # (-22, 55) is moving South West
        velocity = physics.Velocity(-22, 55)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.south_west)

        # (-6, -44) is moving North West
        velocity = physics.Velocity(-6, -55)
        assert (constants.Direction.from_velocity(velocity) ==
                constants.Direction.north_west)

        # (0, 0) is no direction/none
        velocity = physics.Velocity(0, 0)
        assert constants.Direction.from_velocity(velocity) is None

    def test_cardinal(self):
        """Assure the cardinal directions produce match
        the order and values supplied.

        """

        # Cardinals: North, East, South, West
        assert (constants.Direction.north,
                constants.Direction.east,
                constants.Direction.south,
                constants.Direction.west) == constants.Direction.cardinal()

    def test_direction_aliases(self):
        """Test that the various aliases for directions work, i.e.,
        the axis movement aliases (x+, x-, y+, y-).

        """

        # x+ is East
        assert constants.Direction.x_plus() == constants.Direction.east
        # x- is West
        assert constants.Direction.x_minus() == constants.Direction.west
        # y+ is South
        assert constants.Direction.y_plus() == constants.Direction.south
        # y- is North
        assert constants.Direction.y_minus() == constants.Direction.north

    def test_opposite(self):
        """Assure opposite directions are being produced correctly.

        """

        direction = constants.Direction

        # The opposite of North is South
        assert (direction.opposite(direction.north) ==
                direction.south)

        # The opposite of South is North
        assert (direction.opposite(direction.south) ==
                direction.north)

        # The opposite of East is West
        assert (direction.opposite(direction.east) ==
                direction.west)

        # The opposite of West is East
        assert (direction.opposite(direction.west) ==
                direction.east)

        # The opposite of North East is South West
        assert (direction.opposite(direction.north_east) ==
                direction.south_west)

        # The opposite of South West is North East
        assert (direction.opposite(direction.south_west) ==
                direction.north_east)

        # The opposite of North West is South East
        assert (direction.opposite(direction.north_west) ==
                direction.south_east)

        # The opposite of South East is North West
        assert (direction.opposite(direction.south_east) ==
                direction.north_west)

        # The opposite of North South is East West
        assert (direction.opposite(direction.north_south) ==
                direction.east_west)

        # The opposite of East West is North South
        assert (direction.opposite(direction.north_south) ==
                direction.east_west)


def test_action():
    """Test constants.Action.

    """

    assert constants.Action.stand == constants.Action(1)
    assert constants.Action.walk == constants.Action(2)
