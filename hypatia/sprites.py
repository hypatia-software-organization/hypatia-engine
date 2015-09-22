# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""Sprites! Animated sprites, static sprites.

Tools for animation. Animation sources are GIFs from disk, which
have been made into an AnimatedSprite object.

Complex stateful sprites like Walkabout (which represents an Actor).

See Also:
    * effects module
    * actor module
    * resource module

Note:
    I have to modify walkabouts so they can take a regular sprite
    instead of only AnimatedSprites. However, this "regular" sprite,
    i.e., one which does not have more than one frame or image.

"""

import os
import copy
import itertools
import collections

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import pygame
from PIL import Image

from hypatia import resources
from hypatia import constants


class BadWalkabout(Exception):
    """Walkabout Resource specified does not contain any
    GIF files (AnimatedSprite) for creating a Walkabout sprite.

    Used in Walkabout when no files match "*.gif"
    in the provided Resource.

    Attributes:
        failed_name (str): The supplied archive was appended to the
            resources' walkabout direction. This is the value of
            the attempted which resulted in KeyError.

    See Also:
        * Walkabout.__init__()
        * util.Resource

    """

    def __init__(self, failed_name):
        """Set the exception message and "failed_name" attribute
        to the provided failed_name argument.

        Args:
            failed_name (str): :class:`Walkabout` resource archive
                which *should* have contained files of pattern
                ``*.gif,`` but didn't.

        """

        super(BadWalkabout, self).__init__(failed_name)
        self.failed_name = failed_name


class Anchor(object):
    """A coordinate on a surface which is used for pinning to another
    surface Anchor. Used when attempting to afix one surface to
    another, lining up their corresponding anchors.

    Attributes:
        x (int): x-axis coordinate on a surface to place anchor at
        y (int): x-axis coordinate on a surface to place anchor at

    Example:
        >>> anchor = Anchor(5, 3)
        >>> anchor.x
        5
        >>> anchor.y
        3

    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):

        return "<Anchor at (%d, %d)>" % (self.x, self.y)

    def __add__(self, other_anchor):
        """Adds the x, y values of this and another anchor.

        Args:
            other_anchor (Anchor): The Anchor coordinates
                to add to this Anchor's coordinates.

        Returns:
            (x, y) tuple: the new x, y coordinate

        Example:
            >>> anchor_a = Anchor(4, 1)
            >>> anchor_b = Anchor(2, 0)
            >>> anchor_a + anchor_b
            <Anchor at (6, 1)>

        """

        return Anchor(self.x + other_anchor.x,
                      self.y + other_anchor.y)

    def __sub__(self, other_anchor):
        """Find the difference between this anchor and another.

        Args:
            other_anchor (Anchor): the Anchor
                coordinates to subtract from this
                AnchorPoint's coordinates.

        Returns:
            tuple: the (x, y) difference between this
                anchor and the other supplied.

        Example:
            >>> anchor_a = Anchor(4, 1)
            >>> anchor_b = Anchor(2, 0)
            >>> anchor_a - anchor_b
            <Anchor at (2, 1)>

        """

        return Anchor(self.x - other_anchor.x,
                      self.y - other_anchor.y)

    def as_tuple(self):
        """Represent this anchors's (x, y)
        coordinates as a Python tuple.

        Returns:
            tuple(int, int): (x, y) coordinate tuple
                of this Anchor.

        """

        return (self.x, self.y)


class LabeledSurfaceAnchors(object):
    """Labeled anchors for a surface.

    """

    def __init__(self, anchors_config, frame_index):
        """The default is to simply load the anchors from
        the GIF's anchor config file.

        Args:
            anchors_config (resources?): --
            frame_index (int): Which animation frame do the
                anchors belong to?

        Raises:
            KeyError: INI has no anchor entry for frame_index.
            ValueError: INI's corresponding anchor entry is
                malformed.

        """

        self._labeled_anchors = {}

        for section in anchors_config.sections():
            anchor_for_frame = anchors_config.get(section, str(frame_index))
            x, y = anchor_for_frame.split(',')
            self._labeled_anchors[section] = Anchor(int(x), int(y))

    def __getitem__(self, label):
        """Return the anchor corresponding to label.

        Raises:
            KeyError: label does not correspond to anything.

        """

        return self._labeled_anchors[label]


class AnimatedSpriteFrame(object):
    """A frame of an AnimatedSprite animation.

    Attributes:
        surface (pygame.Surface): The pygame image which is used
            for a frame of an animation.
        duration (integer): Milliseconds this frame lasts. How
            long this frame is displayed in corresponding animation.
            The default is 0.
        start_time (integer): The millesecond in which this frame
            will be displayed. The default is 0.
        anchors (LabeledSurfaceAnchors): Optional positional anchors
            used when afixing other surfaces upon another.

    See Also:
        :method:`AnimatedSprite.frames_from_gif()`

    """

    def __init__(self, surface, start_time, duration, anchors=None):
        """

        Args:
            surface (pygame.Surface): The surface/image for this
                frame.
            duration (integer): Milleseconds this frame lasts.
            anchors (LabeledSurfaceAnchors): --

        """

        self.surface = surface
        self.duration = duration
        self.start_time = start_time
        self.end_time = start_time + duration
        self.anchors = anchors or None

    def __repr__(self):
        s = "<AnimatedSpriteFrame duration(%s) start_time(%s) end_time(%s)>"

        return s % (self.duration, self.start_time, self.end_time)


class AnimatedSprite(pygame.sprite.Sprite):
    """Animated sprite with mask, loaded from GIF.

    Supposed to be mostly uniform with the Sprite API.

    Notes:
        This is replacing pyganim as a dependency. Currently,
        does not seem to draw. I assume this is a timedelta
        or blending problem. In elaboration, this could also
        be related to the fact that sprites are rendered
        one-at-a-time, but they SHOULD be rendered through
        sprite groups.

        The rect attribute is useless; should not be used,
        should currently be avoided. This is a problem
        for animated tiles...

    Attributes:
        total_duration (int): The total duration of of this
            animation in milliseconds.
        image (pygame.Surface): Current surface belonging to
            the active frame.
        rect (pygame.Rect): Represents the AnimatedSprite's
            position on screen. Not an absolute position;
            relative position.
        active_frame_index (int): Frame # which is being
            rendered/to be rendered.
        animation_position (int): Animation position in
            milliseconds; milleseconds elapsed in this
            animation. This is used for determining
            which frame to select.

    See Also:

        * :class:`pygame.sprite.Sprite`
        * :class:`AnimatedSpriteFrame`

    """

    def __init__(self, frames):
        super(AnimatedSprite, self).__init__()
        self.frames = frames
        self.total_duration = self.total_duration(self.frames)
        self.active_frame_index = 0

        # animation position in milliseconds
        self.animation_position = 0

        # this gets updated depending on the frame/time
        # needs to be a surface.
        self.image = self.frames[0].surface

        # represents the animated sprite's position
        # on screen.
        self.rect = self.image.get_rect()

    def __getitem__(self, frame_index):

        return self.frames[frame_index]

    def largest_frame_size(self):
        """Goes by area.

        Returns:
            tuple (x, y): pixel dimensions of the largest
                frame surface in this AnimatedSprite.

        """

        largest_frame_size = (0, 0)

        for frame in self.frames:
            largest_x, largest_y = largest_frame_size
            largest_area = largest_x * largest_y

            frame_size = frame.surface.get_size()
            frame_x, frame_y = frame_size
            frame_area = frame_x * frame_y

            if frame_area > largest_area:
                largest_frame_size = (frame_size)

        return largest_frame_size

    @staticmethod
    def from_surface_duration_list(surface_duration_list):
        """Support PygAnimation-style frames.

        A list like [(surface, int duration in ms)]

        """

        running_time = 0
        frames = []

        for surface, duration in surface_duration_list:
            frame = AnimatedSpriteFrame(surface, running_time, duration)
            frames.append(frame)
            running_time += duration

        return AnimatedSprite(frames)

    @classmethod
    def from_file(cls, path_or_readable, anchors_config=None):
        """The default is to create from gif bytes, but this can
        also be done from other methods...

        """

        frames = cls.frames_from_gif(path_or_readable, anchors_config)

        return AnimatedSprite(frames)

    def active_frame(self):

        return self.frames[self.active_frame_index]

    def update(self, clock, absolute_position, viewport):
        self.animation_position += clock.get_time()

        if self.animation_position >= self.total_duration:
            self.animation_position = (self.animation_position %
                                       self.total_duration)
            self.active_frame_index = 0

        while (self.animation_position >
               self.frames[self.active_frame_index].end_time):

            self.active_frame_index += 1

        # NOTE: the fact that I'm using -1 here seems kinda sloppy,
        # because this is a hacky fix due to my own ignorance.
        self.image = self.frames[self.active_frame_index - 1].surface

        image_size = self.image.get_size()

        # NOTE: temporarily disabling this until i fully implement
        # absolute_position... in our current setup we never
        # touch the rect of frame surfaces, only the walkabout
        # relative_position = absolute_position.relative(viewport)
        relative_position = (0, 0)

        self.rect = pygame.rect.Rect(relative_position, image_size)

    @staticmethod
    def total_duration(frames):
        """Return the total duration of the animation in milliseconds,
        milliseconds, from animation frame durations.

        Args:
            frames (List[AnimatedSpriteFrame]): --

        Returns:
            int: The sum of all the frame's "duration" attribute.

        """

        return sum([frame.duration for frame in frames])

    @classmethod
    def frames_from_gif(cls, path_or_readable, anchors_config=None):
        """Create a list of surfaces (frames) and a list of their
        respective frame durations from an animated GIF.

        Args:
            path_or_readable (str|file-like-object): Path to
                an animated-or-not GIF.
            anchors_config (configparser): The anchors ini file
                associated with this GIF.

        Returns
            (List[pygame.Surface], List[int]): --

        """

        pil_gif = Image.open(path_or_readable)

        frame_index = 0
        frames = []
        time_position = 0

        try:

            while True:
                duration = pil_gif.info['duration']
                frame_sprite = cls.pil_image_to_pygame_surface(pil_gif, "RGBA")

                if anchors_config:
                    frame_anchors = LabeledSurfaceAnchors(
                                                          anchors_config,
                                                          frame_index
                                                         )
                else:
                    frame_anchors = None

                frame = AnimatedSpriteFrame(
                                            surface=frame_sprite,
                                            start_time=time_position,
                                            duration=duration,
                                            anchors=frame_anchors
                                           )
                frames.append(frame)
                frame_index += 1
                time_position += duration
                pil_gif.seek(pil_gif.tell() + 1)

        except EOFError:

            pass  # end of sequence

        return frames

    @staticmethod
    def pil_image_to_pygame_surface(pil_image, encoding):
        """Convert PIL Image() to pygame Surface.

        Args:
            pil_image (Image): image to convert to pygame.Surface().
            encoding (str): image encoding, e.g., RGBA

        Returns:
            pygame.Surface: the converted image

        Example:
            >>> import zipfile
            >>> from io import BytesIO
            >>> from PIL import Image
            >>> path = 'resources/walkabouts/debug.zip'
            >>> file_name = 'walk_north.gif'
            >>> sample = zipfile.ZipFile(path).open(file_name).read()
            >>> gif = Image.open(BytesIO(sample))
            >>> AnimatedSprite.pil_image_to_pygame_surface(gif, "RGBA")
            <Surface(6x8x32 SW)>

        """

        image_as_string = pil_image.convert('RGBA').tostring()

        return pygame.image.fromstring(
                                       image_as_string,
                                       pil_image.size,
                                       'RGBA'
                                      )

    def convert_alpha(self):
        """A runtime method for optimizing all of the
        frame surfaces of this animation.

        """

        for frame in self.frames:
            frame.surface.convert()
            frame.surface.convert_alpha()


class Walkabout(pygame.sprite.Sprite):
    """Sprite animations for a character which walks around.

    Contextually-aware graphical representation.

    The walkabout sprites specified to be therein
    walkabout_directory, are files with an action__direction.gif
    filename convention.

    Blits its children relative to its own anchor.

    Attributes:
        resource (Resource): --
        animations (dict): 2D dictionary [action][direction] whose
            values are PygAnimations.
        animation_anchors (dict): 2D dictionary [action][direction]
            whose values are AnimAnchors.
        rect (pygame.Rect): position on tilemap
        size (tuple): the size of the animation in pixels.
        action (constants.Action): --
        direction (constnts.Direction): --
        topleft_float (x,y tuple): --
        position_rect

    """

    def __init__(self, directory, position=None, children=None):
        """

        Args:
            directory (str): directory containing (animated)
            walkabout GIFs. Assumed parent is data/walkabouts/
            position (tuple): (x, y) coordinates (integers)
                referring to absolute pixel coordinate.
            children (list|None): Walkabout objects drawn relative to
                this Walkabout instance.

        Example:
            >>> hat = Walkabout('hat')
            >>> Walkabout('debug', position=(44, 55), children=[hat])
            <Walkabout sprite(in ... groups)>

        """

        super(Walkabout, self).__init__()

        # the attributes we're generating
        self.animations = {}
        self.animation_anchors = {}
        self.actions = []
        self.directions = []
        self.size = None  # will be removed in future?

        if not position:
            position = (0, 0)

        topleft_float = (float(position[0]), float(position[1]))

        # specify the files to load
        # how will i glob a resource
        resource = resources.Resource('walkabouts', directory)
        sprite_files = resource.get_type('.gif')

        # no sprites matching pattern!
        if not sprite_files:

            raise BadWalkabout(directory)

        for sprite_path in sprite_files.keys():
            file_name, file_ext = os.path.splitext(sprite_path)
            file_name = os.path.split(file_name)[1]

            if file_name == 'only':
                action = constants.Action.stand
                direction = constants.Direction.south

            else:
                action, direction = file_name.split('_', 1)
                direction = getattr(constants.Direction, direction)
                action = getattr(constants.Action, action)

            self.actions.append(action)
            self.directions.append(direction)

            # load pyganim from gif file
            animation = sprite_files[sprite_path]

            try:
                self.animations[action][direction] = animation
            except KeyError:
                self.animations[action] = {direction: animation}

        # ... set the rest of the attribs
        self.resource = resource

        # NOTE: this is lazy and results in smaller frames
        # having a bunch of "padding"
        self.size = animation.largest_frame_size()

        self.rect = pygame.Rect(position, self.size)
        self.topleft_float = topleft_float
        self.action = constants.Action.stand
        self.direction = constants.Direction.south
        self.child_walkabouts = children or []

        self.image = self.animations[self.action][self.direction]

    def __getitem__(self, key):
        """Fetch sprites associated with action (key).

        Args:
            key (constants.Action): return dictionary of
                sprites for this action (key).

        Returns:
            dict: sprites associated with action supplied (key)

        Examples:
            >>> walkabout = Walkabout('debug')
            >>> walkabout[constants.Action.walk][constants.Direction.south]
            <AnimatedSprite sprite(in ... groups)>

        """

        return self.animations[key]

    def current_animation(self):
        """Returns the animation selected by the current action
        and direction.

        Returns:
            PygAnim: the animation associated with this Walkabout's
                current action and direction.

        Example:
            >>> walkabout = Walkabout('debug')
            >>> walkabout.current_animation()
            <AnimatedSprite sprite(in ... groups)>

        """

        return self.animations[self.action][self.direction]

    def update(self, clock, screen, offset):
        """Call this once per main loop iteration (tick). Advance
        the active animation's frame according to the clock, use
        said surface/image/frame as this Walkabout's "image" attribute.

        Args:
            clock (pygame.time.Clock): The system clock. Typically
                and defaultly the game.screen.clock. It will control
                the animation. Time is a key factor in updating the
                animations.
            screen (???): I think I'm actually sending the
                viewport, here, I'm not sure? Will touch up later.

        See Also:
            * Walkabout.current_animation()
            * AnimatedSprite
            * pygame.time.Clock

        """

        active_animation = self.current_animation()
        active_animation.update(clock,
                                self.topleft_float,
                                screen)
        self.image = active_animation

    def blit(self, clock, screen, offset):
        """Draw the appropriate/active animation to screen.

        Args:
            screen (pygame.Surface): the primary display/screen.
            offset (x, y tuple): the x, y coords of the absolute
                starting top left corner for the current
                screen/viewport position.
            clock (pygame.time.Clock): The system clock. Typically
                and defaultly the game.screen.clock. It will control
                the animation. Time is a key factor in updating the
                animations.

        """

        x, y = self.topleft_float
        x -= offset[0]
        y -= offset[1]
        position_on_screen = (x, y)

        self.update(clock, screen, offset)
        current_frame = self.current_animation().active_frame()
        screen.blit(current_frame.surface, position_on_screen)
        animation_anchors = current_frame.anchors
        # we do this because currently the only
        # applicable anchor is head
        frame_anchor = animation_anchors['head_anchor']

        # outdated method, but using for now...
        parent_anchor_x = position_on_screen[0] + frame_anchor.x
        parent_anchor_y = position_on_screen[1] + frame_anchor.y
        parent_anchor = Anchor(parent_anchor_x, parent_anchor_y)

        for child_walkabout in self.child_walkabouts:
            # draw at position + difference in child anchor
            child_active_anim = child_walkabout.current_animation()
            child_active_anim.update(clock,
                                     self.topleft_float,
                                     screen)
            child_active_frame = child_active_anim.active_frame()
            child_frame_anchor = child_active_frame.anchors['head_anchor']
            child_position = (parent_anchor - child_frame_anchor).as_tuple()
            screen.blit(child_active_anim.image, child_position)

    def runtime_setup(self):
        """Perform actions to setup the walkabout. Actions performed
        once pygame is running and walkabout has been initialized.

        Convert and play all the animations, run init for children.

        Note:
            It MAY be bad to leave the sprites in play mode in startup
            by default.

        """

        if len(self.animations) == 1:
            actions = (constants.Action.stand,)
            directions = (constants.Direction.south,)

        else:
            actions = (constants.Action.walk, constants.Action.stand)
            directions = (constants.Direction.north, constants.Direction.south,
                          constants.Direction.east, constants.Direction.west)

        for action in actions:

            for direction in directions:
                animated_sprite = self.animations[action][direction]
                animated_sprite.convert_alpha()

        for walkabout_child in self.child_walkabouts:
            walkabout_child.runtime_setup()


def palette_cycle(surface):
    """get_palette is not sufficient; it generates superflous colors.

    Note:
      Need to see if I can convert 32bit alpha to 8 bit temporarily,
      to be converted back at end of palette/color manipulations.

    """

    original_surface = surface.copy()  # don't touch! used for later calc
    width, height = surface.get_size()
    ordered_color_list = []
    seen_colors = set()

    for coordinate in itertools.product(range(0, width), range(0, height)):
        color = surface.get_at(coordinate)
        color = tuple(color)

        if color in seen_colors:

            continue

        ordered_color_list.append(color)
        seen_colors.add(color)

    # reverse the color list but not the pixel arrays, then replace!
    old_color_list = collections.deque(ordered_color_list)
    new_surface = surface.copy()
    frames = []

    for rotation_i in range(len(ordered_color_list)):
        new_surface = new_surface.copy()

        new_color_list = copy.copy(old_color_list)
        new_color_list.rotate(1)

        color_translations = dict(zip(old_color_list, new_color_list))

        # replace each former color with the color from newcolor_list
        for coordinate in itertools.product(range(0, width), range(0, height)):
            color = new_surface.get_at(coordinate)
            color = tuple(color)
            new_color = color_translations[color]
            new_surface.set_at(coordinate, new_color)

        frame = new_surface.copy()
        frames.append((frame, 250))
        old_color_list = copy.copy(new_color_list)

    return AnimatedSprite.from_surface_duration_list(frames)
