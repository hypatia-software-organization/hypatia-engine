# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""Constants, enumerations for Hypatia.

Generally, these constants and enumerations serve to replace
the usage of strings for such paramount attributes like
direction and action. The benefit of this model is:

  * enhances code clarity
  * provides type checking
  * provides constants operations, e.g.,
    `North + East = North East`.
  * class methods to convert one datatype to a constant, like
    velocity to direction

Example:
    >>> from hypatia import sprites
    >>> sprite = sprites.Walkabout('debug')
    >>> sprite.animations[Action.walk][Direction.east]
    <AnimatedSprite sprite(in ... groups)>

See Also:
   *  :attribute:`actor.Actor.direction`
   *  :attribute:`animations.Walkabout.direction`

"""

import enum


# Intentionally not using `enum.IntEnum` because there is no reason to
# compare values of `Direction` to integers.
@enum.unique
class Direction(enum.Enum):
    """Compass direction. Specific to movement of a sprite/surface.

    Inspired by Unix numerical permissions. Only ever
    combined with one other direction max.

    See Also:
        :class:`physics.Velocity`

    Notes:
        I don't see a point in having a separate class for ordinal
        and cardinal classes.

        When "order" of directions is referred to think of the
        mnemonic "Never Eat Soggy Worms," for North, East, South,
        and West. And specifically this is the order of the ordinal
        and cardinal directions:

          1. Direction.north
          2. Direction.north_east
          3. Direction.east
          4. Direction.south_east
          5. Direction.south
          6. Direction.south_west
          7. Direction.west
          8. Direction.north_west

        The attributes/enumerations which are cardinal directions
        are powers of two because that avoids potential conflicts
        with ordinal directions. The values for ordinal directions
        are the addition of their cardinal components, e.g.,
        `north_east` has the value of `north` plus `east. Defining
        cardinal directions as powers of two avoids a problem by
        which ordinal directoins could end up with same values
        which would make equality comparisons true for directions
        which should never be equal.

    """

    # Cardinal Directions
    #
    # See: Direction.__docstring__ for elaboration
    # on these values.
    north = 1
    east = 2
    south = 4
    west = 8

    # Ordinal Directions
    #
    # The result of adding two cardinal directions
    # together, e.g., north_east = 3 because
    # north is 1 and east is 2, so 1 + 2 = 3.
    north_east = 3
    north_west = 9
    south_east = 6
    south_west = 12

    # just for fun
    north_south = 5
    east_west = 10

    @staticmethod
    def cardinals_and_ordinals():
        """Returns all of the cardinal and ordinal directions.

        Returns:
            list: All of the cardinal and ordinal directions in order:
                1. Direction.north
                2. Direction.north_east
                3. Direction.east
                4. Direction.south_east
                5. Direction.south
                6. Direction.south_west
                7. Direction.west
                8. Direction.north_west

        See Also:
            Direction.__docstring__

        """

        return [Direction.north,
                Direction.north_east,
                Direction.east,
                Direction.south_east,
                Direction.south,
                Direction.south_west,
                Direction.west,
                Direction.north_west]

    # NOTE: should be a static method?
    @classmethod
    def disposition(cls, direction, margin=1):
        """Position offset of "margin" pixels in
        the supplied direction.

        Args:
            direction (Direction): The direction to
                get the pixel offset of.
            margin (Optional[int]): Number of pixels to offset by.

        Returns:
            tuple: The (x, y) offset of adding "margin" pixels
                in the supplied direction.

        """

        dispositions = {
            # Cardinal directions' dispositions
            Direction.north: (0, -margin),
            Direction.east: (margin, 0),
            Direction.south: (0, margin),
            Direction.west: (-margin, 0),

            # Ordinal directions' dispositions
            Direction.north_east: (margin, -margin),
            Direction.south_east: (margin, margin),
            Direction.south_west: (-margin, margin),
            Direction.north_west: (-margin, -margin)
        }

        return dispositions[direction]

    # NOTE: should be a static method?
    @classmethod
    def opposite(cls, direction):
        """Return the direction which is opposite of the
        provided direction.

        Args:
            direction (Direction): Direction enumeration to get the
                opposite Direction enumeration of.

        Returns:
            Direction: Direction opposite of provided direction.

        Raises:
            KeyError: If you supplied a direction which isn't a
                valid Direction enumeration. See the "opposites"
                dictionary in this method.

        Examples:
            >>> Direction.opposite(Direction.north)
            <Direction.south: 4>
            >>> Direction.opposite(Direction.north_west)
            <Direction.south_east: 6>

        """

        opposites = {
            # Cardinal opposite pairs (4):
            #   * North > South
            #   * South > North
            #   * East > West
            #   * West > East
            cls.north: cls.south,
            cls.south: cls.north,
            cls.east: cls.west,
            cls.west: cls.east,

            # Ordinal opposite pairs (4):
            #   * North East > South West
            #   * South West > North East
            #   * North West > South East
            #   * South East > North West
            cls.north_east: cls.south_west,
            cls.south_west: cls.north_east,
            cls.north_west: cls.south_east,
            cls.south_east: cls.north_west,

            # "Just for Fun" opposite pairs (2):
            cls.north_south: cls.east_west,
            cls.east_west: cls.north_south
        }

        return opposites[direction]

    # NOTE: should be static method?
    @classmethod
    def cardinal(cls):
        """Return a tuple of the cardinal directions in the order:
        North, East, South, West.

        Returns:
            tuple: (north, east, south, west)

        """

        return (cls.north, cls.east, cls.south, cls.west)

    # NOTE: should be static method?
    @classmethod
    def x_plus(cls):
        """Returns the direction associated
        with moving RIGHT (+x) on the X-AXIS.

        Returns:
            Direction.east

        """

        return cls.east

    # NOTE: should be static method?
    @classmethod
    def x_minus(cls):
        """Returns the direction associated
        with moving LEFT (-x) on the X-AXIS.

        Returns:
            Direction.west

        """

        return cls.west

    # NOTE: should be static method?
    @classmethod
    def y_plus(cls):
        """Returns the direction associated
        with moving DOWN (+y) on the Y-AXIS.

        Returns:
            Direction.south

        """

        return cls.south

    # NOTE: should be static method?
    @classmethod
    def y_minus(cls):
        """Returns the direction associated
        with moving UP (-y) on the Y-AXIS.

        Returns:
            Direction.north

        """

        return cls.north

    @classmethod
    def from_velocity(cls, velocity):
        """Return a direction which corresponds
        to the current 2D velocity.

        See Also:
            :class:`constants.Direction`

        Returns:
            :class:`constants.Direction`|None: Returns None if
                there is no velocity (both axis have zero)

        """

        # We're going to combine the directions
        # extrapolated from each axis, then
        # combine them to make a new direction!
        collected_directions = []

        for axis in ['x', 'y']:
            # e.g., call Direction.x_plus() to get the positive
            # axis direction for 'x' (which would be East).
            plus_direction = getattr(Direction, axis + '_plus')()

            # e.g., call Direction.y_minus() to get the negative
            # axis direction for 'y' (which would be North).
            minus_direction = getattr(Direction, axis + '_minus')()

            # get the current velocity for this axis, determine
            # if it's positive (use plus_direction), negative
            # (use minus_direction) or neutral (do nothing!).
            axis_value = getattr(velocity, axis)

            if axis_value > 0:
                # the velocity for this axis is positive,
                # therefore it is the "plus direction."
                collected_directions.append(plus_direction)
            elif axis_value == 0:
                # the velocity for this axis is neutral,
                # therefore we cannot extrapolate
                # direction from velocity.
                pass
            else:
                # Deductively, the axis value is negative,
                # therefore it is the "minus_direction."
                collected_directions.append(minus_direction)

        # Cool trick, huh? North + East = North East, so forth.
        # Be sure to check out Direction.__add__.
        number_of_directions_collected = len(collected_directions)

        # ordinal
        if number_of_directions_collected > 1:

            return collected_directions[0] + collected_directions[1]

        # cardinal
        elif number_of_directions_collected == 1:

            return collected_directions[0]

        # no direction
        elif number_of_directions_collected == 0:

            return None

    def __add__(cls, other_direction):
        """Combine one cardinal direction with
        another to get an ordinal direction.

        Args:
            other_direction (Direction): one of the Direction
                enumerations.

        Returns:
            :class:`Direction`: an ordinal direction.

        Example:
          >>> Direction.east + Direction.north == Direction.north_east
          True

        """

        return Direction(cls.value + other_direction.value)


@enum.unique
class Action(enum.Enum):
    """Specific to movement of a sprite/surface.

    Attributes:
        stand (int): Actor standing/normal/no-input state.
        walk (int): Actor walking/moving state. Actor
            has velocity.

    See Also:
        :class:`animations.Walkabout`

    """

    stand = 1
    walk = 2

    @staticmethod
    def all():
        """Return all of the available actions.

        Return:
            list: List of all of the available actions,
                which as of the time of writing this docstring
                is simply `walk` and `stand`.

        Note:
            In the future this will be improved to be a classmethod,
            in order to allow users to make their own custom actions.

        """

        return [Action.stand, Action.walk]
