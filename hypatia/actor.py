# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""Implementation of actors.

Actors are the base of any entities which may perform actions.
Examples of actors are enemies, NPCs, the player herself, etc.  This
module implements a basic ``Actor`` class to serve as the parent for any
classes representing objects such as those examples.  Any logic which
can be shared by all such objects belongs in the class, for example
the logic for moving around the game world.  This approach makes it
possible to allow, for example, enemies and players to share much of
the same behavior, and this can be useful by making it easier (from a
programming point-of-view) to give monsters the same set of core
abilities and logic as NPCs, etc.

When type-checking is necessary the ``Actor`` class provides a useful
way to test for objects which support a bare-minimum of core, shared
actions.  The class is also useful in role-playing games for storing
data that tends to be common between the Player, NPCs, enemies, et
alia, a common example being statistics like hit-points.

"""

from hypatia import animations
from hypatia import constants



class Actor(object):
    """The base class for any entity which can perform actions.

    For example, both ``Player`` and ``NPC`` objects can move around
    the game world.  This is the type of action which is shared by all
    "actors" and therefore best implemented in this class, allowing it
    to be shared by as many entities as possible, e.g. enemies.

    It is typically not useful to directly instantiate ``Actor``
    objects but the implementation does not prevent this.

    Attributes:

        walkabout: An instance of ``animations.Walkabout``.

    """

    def __init__(self, walkabout=None):
        """Constructs a new Actor.

        Arguments:

            walkabout: An instance of ``animations.Walkabout``, which
                is then accessible via the ``walkabout`` property.
                This argument is optional and defaults to new instance
                of ``animations.Walkabout``.

        """
        self.walkabout = walkabout or animations.Walkabout()

        @property
        def direction(self):
            """An intsance of ``constants.Direction``

            This property indicates the direction the actor is facing.
            Is it possible to set this property to a new value.

            Raises:
                AttributeError: If the new value is not a valid object
                    of the ``constants.Direction`` class.

                TypeError: If one tries to delete this property

            """
            return self.walkabout.direction

        @direction.setter
        def direction(self, new_direction):

            if not isinstance(new_direction, constants.Direction):

                raise AttributeError(("Direction must be a valid constants.Direction value"))

            else:
                self.walkabout.direction = new_direction

        @direction.deleter
        def direction(self):

            raise TypeError("Cannot delete the 'direction' of an Actor")
