"""A sprite consisting of several sprites and whose current
sprite is resultant of its direction and action.

"""

import os
import itertools

import pygame

from hypatia import constants
from hypatia import animatedsprite


class NoContextForSprite(Exception):
    """It is impossible to create a viable action/direction
    context from a file_name supplied which happens to have
    a file extension we consider to be an image.

    Attributes:
        file_name (str): The name of the file which was used
            to determine the action and direction, but failed.

    See Also:
        SpriteContexts
        InsufficientContexts

    """

    def __init__(self, file_name):
        self.file_name = file_name


class InsufficientContexts(Exception):
    """While attempting to create a ContextSprite,
    the minimum contexts were not fulfilled by
    whatever resource which supplies the sprites.

    Basically, not all of the action/direction
    combinations are present.

    Attributes:
        collection (any): the sequence of things
            which lacked the required contexts.

    """

    def __init__(self, collection):
        """

        Arguments:
            collection (?): the sequence of things
                which did not have enough contexts.

        """

        self.collection = collection


class SpriteContexts(object):
    """The action/direction to pygame Sprite mapping.

    """

    def __init__(self, sprite_contexts):
        """

        Args:
            sprite_contexts (dict): Keys are (action, direction)
                tuples (enumerations), values are of the
                pygame.Sprite type.

        """

        self.sprite_contexts = sprite_contexts

    def __getitem__(self, key):
        """

        Args:
            key (tuple[Action, Direction]):

        """

        return self.sprite_contexts[key]

    def __setitem__(self, key, value):

        self.sprite_contexts[key] = value

    @classmethod
    def from_files_dict(cls, files):
        """Take dictionary where key is the filename, and
        the values are either BytesIO or pygame.Sprite
        objects.

        Raises:
            NoContextForSprite:
            InsufficientContexts:

        See Also:
            self.validate_dict()

        """

        valid_image_extensions = (".gif", ".png")

        # Just iterate over keys, because it makes it
        # easier to create dictionary-like objects in
        # that you don't need some awkward `items()
        # boilerplate.
        sprite_contexts = {}

        for file_name in files:
            file_data = files[file_name]
            file_name, file_ext = os.path.splitext(file_name)

            if file_ext not in valid_image_extensions:

                continue

            action, direction = file_name.split('_', 1)

            try:
                direction = getattr(constants.Direction, direction)
                action = getattr(constants.Action, action)
                sprite_contexts[(action, direction)] = file_data

            except AttributeError:

                raise NoContextForSprite(file_name)

        cls.validate_dict(sprite_contexts)

        return sprite_contexts

    @staticmethod
    def validate_dict(sprite_contexts, also_ordinals=False):
        """Assure all of the direction/action contexts exist.

        Arguments:
            sprite_contexts (dict):
            also_ordinals (bool): If true, ordinals are required
                in addition to cardinal directions.

        Raises:
            InsufficientContexts:

        See Also:
            hypatia.constants: Action, Direction

        """

        if also_ordinals:
            directions = constants.Direction.cardinals_and_ordinals()
        else:
            directions = constants.Direction.cardinals()

        actions = constants.Action.all()

        for action, direction in itertools.product(actions, directions):

            try:
                sprite_contexts[(action, direction)]
            except KeyError:

                raise Exception([sprite_contexts,
                                 (action, direction)])
                raise InsufficientContexts([sprite_contexts,
                                            (action, direction)])


class ContextSprite(pygame.sprite.Sprite):
    """A sprite consisting of several sprites and whose current
    sprite is resultant of its current direction + action.

    Contains a mapping (dictionary) of current direction + action
    to pygame sprite (we call these "sprite contexts").

    Attributes:
        sprite_contexts (SpriteContexts): 
        image (pygame.Sprite): This is the current image/frame
            that was set by the update() method to reflect
            the current direction + action.
        animation (AnimatedSprite): Current animation which was
            set by the update() method to reflect the current
            direction + action.

    """

    def __init__(self, sprite_contexts, children=None,
                 position_on_screen=None):

        super(ContextSprite, self).__init__()

        self.sprite_contexts = sprite_contexts
        self.children = children or None

        self.animation = None

        self.direction = constants.Direction.south
        self.action = constants.Action.stand

        self.image = self.sprite_contexts[(self.action, self.direction)]

        self.position_on_screen = position_on_screen or (0, 0)

    @property
    def size(self):

        return self.image.get_size()

    @property
    def rect(self):

        return pygame.Rect(self.position_on_screen, self.size)

    @classmethod
    def from_files_dict(cls, files):
        """Boilerplate which...

        What about children and other args?

        """

        sprite_contexts = SpriteContexts.from_files_dict(files)

        return cls(sprite_contexts)

    def update(self, clock, viewport):
        """Call this once per main loop iteration (tick). Advance
        the active animation's frame according to the clock, use
        said surface/image/frame as this Walkabout's "image" attribute.

        Args:
            clock (pygame.time.Clock): The system clock. Typically
                and defaultly the game.screen.clock. It will control
                the animation. Time is a key factor in updating the
                animations.

        See Also:
            * animatedsprite.AnimatedSprite
            * animatedsprite.AnimatedSprite.update()
            * pygame.time.Clock

        """

        self.animation = self.image_contexts[self.action][self.direction]
        self.animation.update(clock)
        self.image = self.animation.image

    def blit(self, clock, screen_surface):
        """Draw the appropriate/active animation to screen.

        Args:
            clock (pygame.time.Clock): The system clock. Typically
                and defaultly the game.screen.clock. It will control
                the animation. Time is a key factor in updating the
                animations.
            screen_surface (pygame.Surface): presumably the surface
                of the screen, the viewport, etc. The sprite will be
                drawn on this surface, at coordinate position_on_scren.

        Note:
            All sprites will be sync'd because of how clock
            ticks work. The clock is ticked once per main
            loop iteration, and animations are advanced by
            getting the difference between two ticks.

        """

        position_on_screen = self.position_on_screen

        # Update the state of the current animation. This affects
        # this Walkabout's `image` property.
        self.update(clock, viewport)

        self.image.blit(viewport.image, position_on_screen)

        # Render and update child walkabouts. Render a child
        # Walkabout so that its head anchor occupies the same
        # position as its parent head anchor (THIS Walkabout).
        #
        # This means getting the difference between the following
        # child anchors and THIS Walkabout's (parent) anchors and
        # using said difference as the offset for the child
        # Walkabout sprite/animation.
        current_frame = self.animation.active_frame
        parent_anchor = current_frame.anchors['head_anchor']
        # Adjust the parent anchor to consider the
        # position on screen for child walkabout
        # anchor calculations.
        parent_anchor = parent_anchor + position_on_screen

        for child_walkabout in self.child_walkabouts:
            # We update the current animation to reflect this
            # Walkabout's current action and direction.
            child_walkabout.action = self.action
            child_walkabout.direction = self.direction

            # Get and update this child walkabout's
            # current animation.
            child_active_anim = child_walkabout.animation
            child_active_anim.update(clock,
                                     self.topleft_float,
                                     screen)

            # Now that the child walkabout's current animation
            # has been updated, get the active frame of the
            # child animation in order to find its head anchor.
            child_active_frame = child_active_anim.active_frame
            child_frame_anchor = child_active_frame.anchors['head_anchor']

            # As aforementioned, resolve the child Walkabout's
            # position by subtracting the child's anchor from
            # the adjusted parent anchor.
            child_position = (parent_anchor - child_frame_anchor).as_tuple()
            screen.blit(child_active_anim.image, child_position)

    def convert(self, also_ordinals=False):
        """Perform actions to setup the walkabout. Actions performed
        once pygame is running and walkabout has been initialized.

        Convert and play all the animations, run init for children.

        Note:
            It MAY be bad to leave the sprites in play mode in startup
            by default.

        """

        if also_ordinals:
            directions = constants.Direction.cardinals_and_ordinals()
        else:
            directions = constants.Direction.cardinals()

        actions = constants.Action.all()

        for action, direction in itertools.product(actions, directions):
            animated_sprite = self.sprite_contexts[(action, direction)]
            animated_sprite.convert_alpha()

        for child in self.children:
            child.convert()
