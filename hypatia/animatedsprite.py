"""Quite specifically my pyganim replacement.

More advanced animation/sprite abstractions are in
the animations module.

This gets its own module due to its complicated nature,
and because it avoids circular import issues.

"""

import pygame
from PIL import Image


class Anchor(object):
    """A coordinate on a surface which is used for pinning to another
    surface Anchor. Used when attempting to afix one surface to
    another, lining up their corresponding anchors.

    Attributes:
        x (int): x-axis coordinate on a surface to place anchor at
        y (int): y-axis coordinate on a surface to place anchor at

    Example:
        >>> anchor = Anchor(5, 3)
        >>> anchor.x
        5
        >>> anchor.y
        3
        >>> coordinate_tuple = (1, 2)
        >>> anchor = Anchor(*coordinate_tuple)
        >>> anchor.x
        1
        >>> anchor.y
        2

    """

    def __init__(self, x, y):
        """Create an Anchor using two integers to
        represent this Anchor's coordinate.

        Args:
            x (int): X-axis position of the supplied
                coordinate in pixels.
            y (int): Y-axis position of the supplied
                coordinate in pixels.

        """

        self.x = x
        self.y = y

    def __repr__(self):
        """
        Example:
            >>> anchor = Anchor(1, 2)
            >>> print(anchor)
            <Anchor at (1, 2)>

        """

        return "<Anchor at (%d, %d)>" % (self.x, self.y)

    def __add__(self, coordinates):
        """Adds X-Y coordinates to the coordinates of an Anchor.

        Args:
            coordinates (Union[Anchor|Tuple[int, int]]):
                The X-Y coordinates to add to the coordinates
                of the current Anchor.  The argument may be
                another Anchor object or tuple of two integers.

        Returns:
            Anchor: A new Anchor with the coordinates of
                the first and second added together.

        Raises:
            NotImplemented: If `coordinates` is not an `Anchor`
                or a 2-tuple of integers.

        Example:
            >>> anchor_a = Anchor(4, 1)
            >>> anchor_b = Anchor(2, 0)
            >>> anchor_a + anchor_b
            <Anchor at (6, 1)>
            >>> coordinate_tuple = (10, 20)
            >>> anchor_a + coordinate_tuple
            <Anchor at (14, 21)>
            >>> coordinate_tuple + anchor_a
            <Anchor at (14, 21)>
            >>> anchor_a + 1.5 # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: 'float' object is not subscriptable

        """

        if isinstance(coordinates, Anchor):

            return Anchor(self.x + coordinates.x,
                          self.y + coordinates.y)

        elif type(coordinates[0]) == int and type(coordinates[1]) == int:

            return Anchor(self.x + coordinates[0],
                          self.y + coordinates[1])

        else:

            raise NotImplementedError(coordinates)

    def __radd__(self, coordinates):
        """Implements addition when the Anchor is the right-hand operand.

        See Also: `Anchor.__add__()`

        Example:
            >>> coordinates = (1, 2)
            >>> anchor = Anchor(100, 200)
            >>> coordinates + anchor
            <Anchor at (101, 202)>

        """

        return self + coordinates

    def __sub__(self, coordinates):
        """Subtracts the given X-Y coordinates from the Anchor.

        Args:
            coordinates (Union[Anchor|Tuple[int, int]]):
                The X-Y coordinates to subtract from the coordinates
                of the current Anchor.  The argument may be another
                Anchor object or tuple of two integers.

        Returns:
            Anchor: A new Anchor with the coordinates of
                the second subtracted from the first.

        Raises:
            NotImplemented: If `coordinates` is not an `Anchor`
                or a 2-tuple of integers.

        Example:
            >>> anchor_a = Anchor(4, 1)
            >>> anchor_b = Anchor(2, 0)
            >>> anchor_a - anchor_b
            <Anchor at (2, 1)>
            >>> coordinate_tuple = (3, 0)
            >>> anchor_a - coordinate_tuple
            <Anchor at (1, 1)>
            >>> coordinate_tuple - anchor_b
            <Anchor at (1, 0)>
            >>> anchor_a - 3.2 # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: 'float' object is not subscriptable

        """

        if isinstance(coordinates, Anchor):

            return Anchor(self.x - coordinates.x,
                          self.y - coordinates.y)

        elif type(coordinates[0]) == int and type(coordinates[1]) == int:

            return Anchor(self.x - coordinates[0],
                          self.y - coordinates[1])

        else:

            raise NotImplemented

    def __rsub__(self, coordinates):
        """Implements subtraction when the Anchor is the right-hand operand.

        Example:
            >>> coordinates = (100, 200)
            >>> anchor = Anchor(1, 1)
            >>> coordinates - anchor
            <Anchor at (99, 199)>

        See Also: `Anchor.__sub__()`

        """
        # The naive implementation would be...
        #
        #     return self - coordinates
        #
        # ...but that produces the wrong result because subtraction is
        # not commutative.  We also cannot write...
        #
        #     return coordinates - self
        #
        # ...because then we're invoking this method again, i.e. we
        # create a never-ending loop.
        #
        # To deal with this problem we take advantage of the fact that
        # the following mathematical expressions are equivalent for
        # natural numbers:
        #
        #     x - y
        #     (-x) + y
        #
        # Therefore we create a new `Anchor` which is the inverse of
        # the `self`, i.e. the `x` in the example above, and then we
        # *add* the coordinates (`y`) to that, which gives us the
        # correct result.

        return (self * -1) + coordinates

    def __mul__(self, multiplier):
        """Multiplies the X-Y coordinates of an Anchor by an integer.

        Args:
            multiplier (int): The number to multiply to each coordinate.

        Returns:
            Anchor: A new Anchor object with X-Y coordinates multiplied
                by the `multiplier` argument.

        Raises:
            NotImplemented: If `multiplier` is not an integer.

        Example:
            >>> anchor = Anchor(3, 5)
            >>> anchor * -1
            <Anchor at (-3, -5)>
            >>> anchor * 0
            <Anchor at (0, 0)>
            >>> 2 * anchor
            <Anchor at (6, 10)>
            >>> anchor * 1.5 # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: exceptions must derive from BaseException

        """

        if type(multiplier) == int:

            return Anchor(self.x * multiplier, self.y * multiplier)

        else:

            raise NotImplemented

    def __rmul__(self, multiplier):
        """Allows the Anchor to be on the right-hand of multiplication.

        See Also: `Anchor.__mul__()`

        Example:
            >>> 10 * Anchor(1, 2)
            <Anchor at (10, 20)>
            >>> 2.5 * Anchor(0, 0) # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: exceptions must derive from BaseException

        """

        return self * multiplier

    def as_tuple(self):
        """Represent this anchors's (x, y)
        coordinates as a Python tuple.

        Returns:
            tuple(int, int): (x, y) coordinate tuple
                of this Anchor.

        """

        return (self.x, self.y)


class FrameAnchors(object):
    """Labeled anchors for a frame. Each anchor point has
    an associated and unique label, e.g. "head." This is
    the anchors attribute on any given Frame instance.

    Not much distinguishes this from a regular dictionary,
    besides the method to create a FrameAnchors using
    a configparser object. This object exists in case
    more advance operations with frame anchors are
    performed, or perhaps new/more static methods for
    creating FrameAnchors.

    See Also:
        * Frame
        * Frame.anchors
        * AnimatedSprite

    Note:
        May add "belongs_to_frame_index" attribute in
        the future since I'm just discarding that info
        in from_config().

    """

    def __init__(self, labeled_anchors):
        """Set the _labeled_anchors private attribute.

        Args:
            labeled_anchors (dict): A dictionary whose keys
                are "labels" for an anchor (the value). For
                example:

                >>> an_anchor = Anchor(5, 88)
                >>> labeled_anchors = {'head': an_anchor}

        See Also:
            * FrameAnchors.from_config()

        """

        self._labeled_anchors = labeled_anchors

    def __getitem__(self, label):
        """Return the anchor corresponding to label.

        Arg:
            label (str): The label associated with
                the anchor you want.

        Raises:
            KeyError: label does not correspond to anything.

        Returns:
            Anchor: The anchor associated with
                the provided label.

        """

        return self._labeled_anchors[label]

    @staticmethod
    def from_config(anchors_config, frame_index):
        """Load the anchors from a GIF's anchor config file.

        Look for this frame's anchors in an configparser
        object, where the sections are anchor labels, and
        the key/value pairs are "frame index=(x, y)".

        Args:
            anchors_config (ConfigParser): This configparser
                is used for finding this frame's anchors. This
                is the INI which is associated with a Walkabout
                animation or sprite, e.g., walk_down.ini.
            frame_index (int): Which animation frame do the
                anchors belong to?

        Raises:
            KeyError: INI has no anchor entry for frame_index.
            ValueError: INI's corresponding anchor entry is
                malformed.

        Returns:
            FrameAnchors: Instance created from supplied
                anchors_config dictionary and the frame index.

        """

        labeled_anchors = {}

        for section in anchors_config.sections():
            anchor_for_frame = anchors_config.get(section, str(frame_index))
            x, y = anchor_for_frame.split(',')
            labeled_anchors[section] = Anchor(int(x), int(y))

        return FrameAnchors(labeled_anchors)


class Frame(object):
    """A frame of an AnimatedSprite animation.

    Attributes:
        surface (pygame.Surface): The pygame image which is used
            for a frame of an animation.
        duration (integer): Milliseconds this frame lasts. How
            long this frame is displayed in corresponding animation.
        start_time (integer): The animation position in milleseconds,
            when this frame will start being displayed.
        anchors (LabeledSurfaceAnchors): Optional positional anchors
            used when afixing other surfaces upon another.

    See Also:
        * AnimatedSprite.frames_from_gif()
        * AnimatedSprite.animation_position
        * FrameAnchors
        * Anchor

    """

    def __init__(self, surface, start_time, duration, anchors=None):
        """Create a frame using a pygame surface, the start time,
        duration time, and, optionally,  FrameAnchors.

        Args:
            surface (pygame.Surface): The surface/image for this
                frame.
            start_time (int): Millisecond this frame starts. This
                frame is a part of a larger series of frames and
                in order to render the animation properly we
                need to know when each frame begins to be drawn,
                while duration signifies when it ends.
            duration (integer): Milleseconds this frame lasts. See:
                start_time argument description.
            anchors (FrameAnchors): This frame's anchor points.

        See Also:
            * FrameAnchors

        """

        self.surface = surface
        self.duration = duration
        self.start_time = start_time
        self.end_time = start_time + duration
        self.anchors = anchors or None

    def __repr__(self):
        s = "<Frame duration(%s) start_time(%s) end_time(%s)>"

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
            the active frame. Set once per tick through
            the AnimatedSprite.update() method.
        rect (pygame.Rect): Represents the AnimatedSprite's
            position on screen. Not an absolute position;
            relative position. Updated once per tick, see
            the AnimatedSprite.update() method.
        active_frame_index (int): Frame # which is being
            rendered/to be rendered. Also updated once per
            tick, see the AnimatedSprite.update() method.
        active_frame: The current surface representing this
            animation at its current animation position. Set
            once per tick through the update() method.
        animation_position (int): Animation position in
            milliseconds; milleseconds elapsed in this
            animation. This is used for determining
            which frame to select. Set once per tick through
            the AnimatedSprite.update() method.

    See Also:
        * :class:`pygame.sprite.Sprite`
        * :class:`Frame`

    """

    def __init__(self, frames):
        """Create this AnimatedSprite using
        a list of Frame instances.

        Args:
            frames (list[Frame]): A properly assembled list of frames,
                which assumes that each Frame's start_time is greater
                than the previous element and is the previous element's
                start time + previous element/Frame's duration. Here
                is an example of aformentioned:

                >>> frame_one_surface = pygame.Surface((16, 16))
                >>> frame_one = Frame(frame_one_surface, 0, 100)
                >>> frame_two_surface = pygame.Surface((16, 16))
                >>> frame_two = Frame(frame_two_surface, 100, 50)

        Note:
            In the future I may add a method for verifying the
            validity of Frame start_times and durations.

        """

        super(AnimatedSprite, self).__init__()
        self.frames = frames
        self.total_duration = self.get_total_duration(self.frames)
        self.active_frame_index = 0
        self.active_frame = self.frames[self.active_frame_index]

        # animation position in milliseconds
        self.animation_position = 0

        # this gets updated depending on the frame/time
        # needs to be a surface.
        self.image = self.frames[0].surface

        # represents the animated sprite's position
        # on screen.
        self.rect = self.image.get_rect()

    def __getitem__(self, frame_index):
        """Return the frame corresponding to
        the supplied frame_index.

        Args:
            frame_index (int): Index number to lookup
                a frame by element number in the
                self.frames list.

        Returns:
            Frame: The frame of this animation at the
                specified index of frame_index.

        """

        return self.frames[frame_index]

    def largest_frame_size(self):
        """Return the largest frame's (by area)
        dimensions as tuple(int x, int y).

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

        Args:
            surface_duration_list (list[tuple]): A list
                of tuples, first element is a surface,
                second element being how long said surface
                is displayed for. For example:

                >>> a_surface = pygame.Surface((10, 10))
                >>> duration = 100  # 100 MS
                >>> surface_duration_list = [(a_surface, duration)]

        Returns:
            AnimatedSprite: The animated sprite constructed
                from the provided surface_duration_list.

        """

        running_time = 0
        frames = []

        for surface, duration in surface_duration_list:
            frame = Frame(surface, running_time, duration)
            frames.append(frame)
            running_time += duration

        return AnimatedSprite(frames)

    @classmethod
    def from_file(cls, path_or_readable, anchors_config=None):
        """The default is to create from gif bytes, but this can
        also be done from other methods...

        Args:
            path_or_readable (str|file-like-object): Either a string
                or an object with a read() method. So, either a path
                to an animated GIF, or a file-like-object/buffer of
                an animated GIF.
            anchors_config (configparser): INI/config file associated
                with providing anchors for this animation.

        Returns:
            AnimatedSprite: --

        """

        frames = cls.frames_from_gif(path_or_readable, anchors_config)

        return AnimatedSprite(frames)

    def update(self, clock, absolute_position, viewport):
        """Manipulate the state of this AnimatedSprite, namely
        the on-screen/viewport position (not absolute) and
        using the clock to do animation manipulations.

        Using the game's clock we decipher the animation position,
        which in turn allows us to locate the correct frame.

        Sets the image attribute to the current frame's image. Updates
        the rect attribute to the new relative position and frame size.

        Warning:
            Since we're changing the rect size on-the-fly, this can
            get the player stuck in certain boundaries. I will be
            remedying this in the future.

        Args:
            clock (pygame.time.Clock): THE game clock, typically
                found as the attribute Game.screen.clock.
            absolute_position (tuple[int]): (x, y) pixel position
                of this AnimatedSprite on the map--absolute
                position. Meaning this could be outside of the
                current viewport area.

        """

        self.animation_position += clock.get_time()

        if self.animation_position >= self.total_duration:
            self.animation_position = (self.animation_position %
                                       self.total_duration)
            self.active_frame_index = 0

        while (self.animation_position >
               self.frames[self.active_frame_index].end_time):

            self.active_frame_index += 1

        # NOTE: the fact that I'm using -1 here seems sloppy/hacky
        self.image = self.frames[self.active_frame_index - 1].surface

        image_size = self.image.get_size()

        # NOTE: temporarily disabling this until i fully implement
        # absolute_position... in our current setup we never
        # touch the rect of frame surfaces, only the walkabout
        # relative_position = absolute_position.relative(viewport)
        relative_position = (0, 0)

        self.rect = pygame.rect.Rect(relative_position, image_size)

        self.active_frame = self.frames[self.active_frame_index]

    @staticmethod
    def get_total_duration(frames):
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
                frame_sprite = cls.pil_image_to_pygame_surface(pil_gif)

                if anchors_config:
                    frame_anchors = FrameAnchors.from_config(anchors_config,
                                                             frame_index)

                else:
                    frame_anchors = None

                frame = Frame(surface=frame_sprite,
                              start_time=time_position,
                              duration=duration,
                              anchors=frame_anchors)
                frames.append(frame)
                frame_index += 1
                time_position += duration
                pil_gif.seek(pil_gif.tell() + 1)

        except EOFError:

            pass  # end of sequence

        return frames

    @staticmethod
    def pil_image_to_pygame_surface(pil_image):
        """Convert PIL Image() to RGBA pygame Surface.

        Args:
            pil_image (Image): image to convert to pygame.Surface().

        Returns:
            pygame.Surface: the converted image

        Example:
            >>> import zipfile
            >>> from io import BytesIO
            >>> from PIL import Image
            >>> path = 'resources/walkabouts/debug.zip'
            >>> file_name = 'only.gif'
            >>> sample = zipfile.ZipFile(path).open(file_name).read()
            >>> gif = Image.open(BytesIO(sample))
            >>> AnimatedSprite.pil_image_to_pygame_surface(gif)
            <Surface(10x10x32 SW)>

        """

        image_as_string = pil_image.convert('RGBA').tobytes()

        return pygame.image.fromstring(image_as_string,
                                       pil_image.size,
                                       'RGBA')

    def convert_alpha(self):
        """A runtime method for optimizing all of the
        frame surfaces of this animation.

        Pygame recommends converting all image data with
        pygame.surface.convert() to speed up game play.

        Convert each frame's surface to an optimized
        format for pygame gameplay.

        """

        for frame in self.frames:
            frame.surface.convert()
            frame.surface.convert_alpha()
