# engine/sprites.py
# Lillian Lemmer <lillian.lynn.lemmer@gmail.com>
#
# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""The stuff being drawn; sprites

Note:
  I wanna add support for loading character animations
  from sprite sheets.

"""

import os
import glob
import itertools

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import pyganim
import pygame
from PIL import Image

from hypatia import render
from hypatia import constants

__author__ = "Lillian Lemmer"
__copyright__ = "Copyright 2015, Lillian Lemmer"
__credits__ = ["Lillian Lemmer"]
__license__ = "MIT"
__maintainer__ = "Lillian Lemmer"
__email__ = "lillian.lynn.lemmer@gmail.com"
__status__ = "Development"


class BadWalkabout(Exception):
    """The supplied directory has no files which match *.gif.

    """

    def __init__(self, supplied_directory):
        super(BadWalkabout, self).__init__(supplied_directory)


class AnimAnchors(object):
    """Named/labeled anchor points whose coordinates depend on the
    frame of the corresponding PygAnim object.

    See: AnchorPoint()

    Attributes:
      anchor_points (dict): key is anchor label/group, value is a list
        of AnchorPoint()s whose index corresponds to respective PygAnim
        frame index.
      anchor_groups (list): the names/labels of the anchor groups, e.g.,
        "head_anchor."

    """

    def __init__(self, gif_path):
        """Loads the INI associated with a GIF (defined in gif_path).

        Args:
          gif_path (str): path to the GIF animation you want to load the
            anchor data thereof.

        Returns:
          dict: frame: (x, y) anchor definition dictionary.

        Example:
          >>> animation_anchors = AnimAnchors('default.gif')

        """

        gif_file_name = os.path.splitext(os.path.basename(gif_path))[0] + '.ini'
        anchor_ini_path = os.path.join(os.path.dirname(gif_path), gif_file_name)
        anchor_ini = configparser.ConfigParser()
        anchor_ini.read(anchor_ini_path)
        anchor_point_groups = anchor_ini.sections()

        # key is group, value is list of frame coord positions
        anchors = {name: [] for name in anchor_point_groups}

        for anchor_point_group in anchor_point_groups:

            for __, frame_anchor in anchor_ini.items(anchor_point_group):
                x, y = frame_anchor.split(',')
                anchor_point = AnchorPoint(int(x), int(y))
                anchors[anchor_point_group].append(anchor_point)

        self.anchor_points = anchors
        self.anchor_groups = anchor_point_groups

    def get_anchor_point(self, anchor_point_group, frame_index):
        """Return an AnchorPoint corresponding to group name and frame
        index.

        Args:
          anchor_point_group (str): name of the anchor point group
          frame_index (int): which frame for group's anchor
        
        Returns:
          AnchorPoint: --

        Note:
          Will simply return last anchor point for group if an anchor
          isn't defined for frame.

        Example:
          >>> animation_anchors = AnimAnchors('default.gif')
          >>> animation_anchors.get_anchor_point('head_anchor', 0)
          (2, 3)

        """

        try:

            return self.anchor_points[anchor_point_group][frame_index]

        except IndexError:

            return self.anchor_points[anchor_point_group][-1]


class AnchorPoint(object):
    """A coordinate on a surface which is used for pinning to another
    surface AnchorPoint. Used when attempting to afix one surface to
    another, lining up their corresponding anchorpoints.

    Attributes:
      x (int): x-axis coordinate on a surface to place anchor at
      y (int): x-axis coordinate on a surface to place anchor at

    """

    def __init__(self, x, y):
        """Create an AnchorPoint at coordinate (x, y).

        Args:
          x (int): the x-axis pixel position
          y (int): the y-axis pixel position

        Example:
          >>> anchor_point = AnchorPoint(5, 3)
          >>> anchor_point.x
          5
          >>> anchor_point.y
          3

        """

        self.x = x
        self.y = y

    def __add__(self, other_anchor_point):
        """Adds the x, y values of this and another anchor point.

        Args:
          other_anchor_point (AnchorPoint): the AnchorPoint coordinates
            to add to this AnchorPoint's coordinates.

        Returns:
          (x, y) tuple: the new x, y coordinate

        Example:
          >>> anchor_point_a = AnchorPoint(4, 1)
          >>> anchor_point_b = AnchorPoint(2, 0)
          >>> anchor_point_a + anchor_point_b
          (6, 1)

        """

        return (self.x + other_anchor_point.x,
                self.y + other_anchor_point.y)

    def __sub__(self, other_anchor_point):
        """Find the difference between this anchor and another.

        Args:
          other_anchor_point (AnchorPoint): the AnchorPoint coordinates
            to subtract from this AnchorPoint's coordinates.

        Returns:
          (x, y) tuple: the x, y difference between this anchor point
            and the other supplied.

        Example:
          >>> anchor_point_a = AnchorPoint(4, 1)
          >>> anchor_point_b = AnchorPoint(2, 0)
          >>> anchor_point_a - anchor_point_b
          (2, 1)

        """
 
        return (self.x - other_anchor_point.x,
                self.y - other_anchor_point.y)


class Walkabout(object):
    """Sprite animations for a character which walks around.

    Note:
      The walkabout sprites specified to be therein
      walkabout_directory, are files with an action__direction.gif
      filename convention.

      ASSUMPTION: walkabout_directory contains sprites for
      walk AND run actions.

      Blits its children relative to its own anchor.

    Attributes:
      animations (dict): 2D dictionary [action][direction] whose
        values are PygAnimations.
      animation_anchors (dict): 2D dictionary [action][direction] whose
        values are AnimAnchors.
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
          >>> walkabout = Walkabout(position=(44, 55), children=[hat])

        """

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
        walkabout_directory = os.path.join(
                                           'resources',
                                           'walkabouts',
                                           directory
                                          )
        sprite_name_pattern = os.path.join(walkabout_directory, '*.gif')

        # get all the animations in this directory
        sprite_paths = glob.glob(sprite_name_pattern)

        # no sprites matching pattern!
        if not sprite_paths:

            raise BadWalkabout(directory)

        for sprite_path in sprite_paths:
            file_name, file_ext = os.path.splitext(sprite_path)
            file_name = os.path.split(file_name)[1]

            if file_name == 'only':
                action = constants.Action.Stand
                direction = constants.Direction.Down

            else:
                action, direction = file_name.split('_', 1)
                direction = getattr(constants, direction.title())
                action = getattr(constants, action.title())

            self.actions.append(action)
            self.directions.append(direction)

            # load pyganim from gif file
            animation = load_gif(sprite_path)

            try:
                self.animations[action][direction] = animation
            except KeyError:
                self.animations[action] = {direction: animation}

            # load anchor points
            ini_path = os.path.join(walkabout_directory, file_name + '.ini')

            if os.path.exists(ini_path):
                anim_anchors = AnimAnchors(sprite_path)

                try:
                    self.animation_anchors[action][direction] = anim_anchors
                except KeyError:
                    self.animation_anchors[action] = {direction: anim_anchors}

            else:
                self.animation_anchors = None

        # ... set the rest of the attribs
        self.size = animation.getMaxSize()
        self.rect = pygame.Rect(position, self.size)
        self.topleft_float = topleft_float
        self.action = constants.Action.Stand
        self.direction = constants.Direction.Down
        self.speed_in_pixels_per_second = 20.0
        self.child_walkabouts = children or []

    def __getitem__(self, key):
        """Fetch sprites associated with action (key).

        Args:
          key (constants.Action): return dictionary of sprites for
            this action (key).

        Returns:
          dict: sprites associated with action supplied (key)

        Examples:
          >>> walkabout = Walkabout()
          >>> walkabout[constants.Action.Walk][constants.Direction.Up]
          <PygAnim Object>

        """

        return self.animations[key]

    def current_animation(self):
        """Returns the animation selected by the current action
        and direction.

        Returns:
          PygAnim: the animation associated with this Walkabout's
            current action and direction.

        Example:
          >>> walkabout = Walkabout()
          >>> walkabout.current_animation()
          <PygAnim Object>

        """

        return self.animations[self.action][self.direction]

    def get_anchors(self):
        """Get anchors per frame in a GIF by identifying th ecoordinate
        of a specific color.

        Note:
          This is an old, but still useful way of loading anchors for
          an animation.

        """

        anchors = {a: {d: [] for d in self.directions} for a in self.actions}

        for action, directions in self.animations.items():

            for direction, animation in directions.items():

                for surface_frame in animation._images:
                    anchor = self.get_anchor(surface_frame)
                    anchors[action][direction].append(anchor)

        return anchors

    def get_anchor(self, surface):
        """Locate the anchor coordinate by identifying which pixel
        coordinate matches color.

        Args:
          surface (pygame.Surface): surface to scan for color and
            return the coord which color appears

        Returns:
          (x, y): pixel coordinate where color shows up.

        Note:
          Old way of defining anchor points, but still handy! I was
          thinking about making it so you can define anchor point
          group colors.

        """
    
        x, y = surface.get_size()
        debug_color = pygame.Color(255, 136, 255)

        for coord in itertools.product(range(0, x), range(0, y)):

            if surface.get_at(coord) == debug_color:

                return coord

    def blit(self, screen, offset):
        """Draw the appropriate/active animation to screen.

        Note:
          Should go to render module?

        Args:
          screen (pygame.Surface): the primary display/screen.
          offset (x, y tuple): the x, y coords of the absolute
            starting top left corner for the current screen/viewport
            position.

        """

        x, y = self.topleft_float
        x -= offset[0]
        y -= offset[1]
        position_on_screen = (x, y)

        pyganim_gif = self.current_animation()
        pyganim_gif.blit(screen, position_on_screen)

        # the rest of this is for children/anchors
        if self.animation_anchors is None:

            return None

        pyganim_frame_index = pyganim.findStartTime(pyganim_gif._startTimes,
                                                    pyganim_gif.elapsed)
        current_frame_surface = pyganim_gif.getFrame(pyganim_frame_index)

        # anchors are all completely wrong
        animation_anchors = self.animation_anchors[self.action][self.direction]
        frame_anchor = animation_anchors.get_anchor_point('head_anchor',
                                                          pyganim_frame_index)
        parent_anchor = AnchorPoint(position_on_screen[0] + frame_anchor.x,
                                    position_on_screen[1] + frame_anchor.y)

        for child_walkabout in self.child_walkabouts:
            # draw at position + difference in child anchor
            child_anim_anchor = (child_walkabout
                                 .animation_anchors[self.action][self.direction])
            child_frame_anchor = (child_anim_anchor
                                  .get_anchor_point('head_anchor',
                                                    pyganim_frame_index))
            child_position = parent_anchor - child_frame_anchor
            child_anim = child_walkabout.current_animation()
            child_anim.blit(screen, child_position)

    def runtime_setup(self):
        """Perform actions to setup the walkabout. Actions performed
        once pygame is running and walkabout has been initialized.

        Convert and play all the animations, run init for children.

        Note:
          It MAY be bad to leave the sprites in play mode in startup
          by default.

        """

        if len(self.animations) == 1:
            actions = (constants.Action.Stand,)
            directions = (constants.Direction.Down,)

        else:
            actions = (constants.Action.Walk, constants.Action.Stand)
            directions = (constants.Direction.Up, constants.Direction.Down,
                          constants.Direction.Left, constants.Direction.Right)

        for action in actions:

            for direction in directions:
                animated_sprite = self.animations[action][direction]
                animated_sprite.convert_alpha()
                animated_sprite.play()

        for walkabout_child in self.child_walkabouts:
            walkabout_child.runtime_setup()


def load_gif(gif_path):
    """Load the PygAnim animation abstraction of a GIF from path.

    Args:
      gif_path (str): create animation using file path to GIF

    Returns:
      PygAnim: the PygAnim animation which accurately depicts the GIF
        referenced in gif_path.

    Example:
      >>> load_gif('default.gif')
      <PygAnim Object>

    """

    pil_gif = Image.open(gif_path)

    frame_index = 0
    frames = []

    try:

        while 1:
            duration = pil_gif.info['duration'] / 1000.0
            frame_as_pygame_image = render.pil_to_pygame(pil_gif, "RGBA")
            frames.append((frame_as_pygame_image, duration))
            frame_index += 1
            pil_gif.seek(pil_gif.tell() + 1)

    except EOFError:

        pass  # end of sequence

    gif = pyganim.PygAnimation(frames)
    gif.anchor(pyganim.CENTER)

    return gif


if __name__ == "__main__":
    import doctest
    doctest.testmod()

