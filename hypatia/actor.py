# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""Implementation of actors.

Actors are the base of any entities (players) which may perform
actions, examples include:

  * human player
  * an enemy NPC
  * a friendly NPC
  * Invisible NPC placed above a sign tile, which displays
    a message when "talked" to.

This module implements a basic :class:`Actor` class to serve as
the parent for any classes representing objects such as those
examples.

Any logic which can by shared by all "players" belongs in the class,
for example, the logic for moving around the game world. This approach
makes it possible to allow, for example, enemies and players to share
much of the same behavior and this can make it easier to give monsters
the same set of core abilities and logic as NPCs, etc.

When type-checking is necessary the :class:`Actor` class provides a
useful way to test for objects which support a bare-minimum of core,
shared actions. The class is also useful in role-playing games for
storing data that tends to be common between the Player, NPCs, enemies,
etalia, a common example being statistics like hit-points.

See Also:
    * animations.Walkabout

"""

import enum

from hypatia import constants
from hypatia import physics


@enum.unique
class NoResponseReason(enum.Enum):
    """Enumeration of reasons Actor.get_response()
    could fail and raise NoResponse.

    """

    no_say_text = "Actor cannot respond."


class ActorException(Exception):
    """The base class for all exceptions related to Actors.

    See Also:
        :class:`Actor`
    """
    pass


class ActorCannotTalk(ActorException):
    """When an actor cannot talk.

    See Also:
        :class:`Actor`
        :meth:`Actor.say()`

    """
    pass


class NoActorResponse(ActorException):
    """When an Actor fails to respond (say).

    Attribs:
        reason (NoResponseReason): The reason the
            get_response attempt failed.

    See Also:
        * Actor.respond()
        * NoResponseReason

    """

    def __init__(self, reason_enum):
        """

        Args:
            reason_enum (NoResponseReason): Why there's
                no response.

        Raises:
            TypeError: reason_enum is not a valid
                NoResponseReason enumeration.

        """
        super(NoActorResponse, self).__init__(reason_enum)

        # Check for a valid reason or fail.
        if isinstance(reason_enum, NoResponseReason):
            self.reason = reason_enum
        else:

            raise TypeError(reason_enum)


class Actor(object):
    """The base class for any entity which can perform actions.

    For example, most actors can move around the game world, so
    there are tools for setting the "direction" the actor is
    facing. Another example: most actors can say something, offer
    some dialog. These are the types of actions which are shared
    by all/most actors and therefore best implemented in this class,
    allowing it to be shared by as many players as possible, e.g.,
    human player, enemies.

    Note:
      It is typically not useful to directly instantiate :class:`Actor`
      objects but the implementation does not prevent this.

    Attributes:
        walkabout (animations.Walkabout): --
        direction (constants.Direction): --

    See Also:
        :mod:`actor`

    """

    def __init__(self, walkabout=None, say_text=None, velocity=None):
        """Constructs a new Actor.

        Args:
            walkabout (Optional[animations.Walkabout]): Optionally
                set a walkabout property, which will graphically
                represent the actor.
            say_text (Optional[str]): Optionally set the text which
                is displayed when this actor's :meth:`Actor.say()`
                is called.
            velocity (Optional[physics.Velocity]): --

        """

        self.walkabout = walkabout
        self.say_text = say_text
        self.velocity = velocity or physics.Velocity()

    @property
    def direction(self):
        """An instance of :class:`constants.Direction`

        This property indicates the direction the actor is facing.
        Is it possible to set this property to a new value.

        Raises:
            AttributeError: If the instance has no `walkabout` property.
            TypeError: If one tries to delete this property

        """

        if self.walkabout is None:

            raise AttributeError("Actor has no 'walkabout' property")

        return self.walkabout.direction

    @direction.setter
    def direction(self, new_direction):
        """Set the direction this actor is facing.

        Args:
            new_direction (constants.Direction): The new direction
                for the actor to face.

        Raises:
            AttributeError: If the new value is not a valid object
                of the :class:`constants.Direction` class or if
                the actor has no `walkabout` property.

        """

        if self.walkabout is None:

            raise AttributeError("Actor has no 'walkabout' property")

        if not isinstance(new_direction, constants.Direction):

            raise AttributeError(("Direction must be a valid "
                                  "constants.Direction value"))

        else:
            self.walkabout.direction = new_direction

    @direction.deleter
    def direction(self):
        """You are not allowed to delete the direction of an Actor.

        Raises:
            TypeError: If one tries to delete this property

        """

        raise TypeError("Cannot delete the 'direction' of an Actor")

    def get_response(self, at_direction, dialogbox):
        """Respond to an NPC in the direction of at_direction. Change
        this actor's direction. Display this actor's say_text attribute
        on the provided dialogbox.


        Args:
            at_direction (constants.Direction): The new direction
                for this actor to face.
            dialogbox (dialog.DialogBox): This actor's say_text
                attribute will be printed to this.

        Raises:
            NoActorResponse: This NPC has no response for the
                included reason.
            AttributeError: The actor has no `walkabout` property.

        Notes:
            Even if this actor doesn't say anything, it will
            change the direction it's facing.

            This method is typically called by another
            actor's :meth:`actor.Actor.talk()`.

        """

        if self.walkabout is None:

            raise AttributeError("Actor has no 'walkabout' property")

        self.walkabout.direction = (constants.Direction.
                                    opposite(at_direction))

        if self.say_text:
            dialogbox.set_message(self.say_text)
        else:

            raise NoActorResponse(NoResponseReason.no_say_text)

    def talk(self, npcs, dialogbox):
        """Trigger another actor's :meth:`actor.Actor.say()` if
        they are immediately *in front* of this actor.

        See Also:
            * :attribute:`animations.Walkabout.direction`
            * :attribute:`Actor.direction`
            * :meth:`actor.Actor.say()`

        Args:
            npcs (List[player.Npc]): NPCs to check for
                collisions immediately in front of this
                actor.
            dialogbox (dialog.DialogBox): The dialogbox which
                another actor will print to if they have
                something to say.

        Raises:
            ActorCannotTalk: If the actor cannot speak to
                the `npcs` around.

        """

        if self.walkabout is None:

            raise ActorCannotTalk(("Actor has no 'direction' to face "
                                   "when talking."))

        # get the current direction, check a bit in front with a rect
        # to talk to npc if collide
        facing = self.walkabout.direction

        # The pixel offset which acts as the collision boundary
        # for checking if there is an actor to get a response from
        # in front of this actor.
        disposition = constants.Direction.disposition(facing)

        talk_rect = self.walkabout.rect.copy()
        talk_rect.move_ip(disposition)

        for npc in npcs:

            if npc.walkabout.rect.colliderect(talk_rect):

                try:
                    npc.get_response(facing, dialogbox)

                # NOTE: I'm just being explicit and showing off
                # the good feature of having a reason for an
                # NPC not being able to respond. This currently
                # does nothing...
                except NoActorResponse as no_response:

                    if response_failure is NoResponseReason.no_say_text:
                        # The NPC we're seeking a response from lacks
                        # a value for say text.
                        pass
