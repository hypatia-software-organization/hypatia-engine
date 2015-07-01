# engine/render.py
# Lillian Lemmer <lillian.lynn.lemmer@gmail.com>
#
# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""How stuff is drawn; spite and surface manipulation.

Includes screen, viewport, and surface/animation manipulation.

"""

import sys
import copy
import time
import itertools
import collections

import pygame
import pyganim
from pygame.locals import *

from hypatia import constants



class Screen(object):
    """Everything blits to screen!

    Notes:
      --

    CONSTANTS:
      FPS (int): frames per second limit

    Attributes:
      clock (pygame.time.Clock):
      time_elapsed_milliseconds (int): the time difference between
        the two most recent frames/updates in milliseconds.
      screen_size (tuple):
      screen (pygame.display surface): --

    """

    FPS = 60

    def __init__(self, filters=None):
        """Will init pygame.

        Args:
          filters (list): list of functions which takes and
            returns a surface.

        """

        pygame.init()
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.time_elapsed_milliseconds = 0
        display_info = pygame.display.Info()
        self.screen_size = (display_info.current_w, display_info.current_h)
        self.screen = pygame.display.set_mode(
                                              self.screen_size,
                                              FULLSCREEN | DOUBLEBUF
                                             )
        self.filters = filters

    def update(self, surface):
        """Update the screen; apply surface to screen, automatically
        rescaling for fullscreen.

        """

        scaled_surface = pygame.transform.scale(surface, self.screen_size)

        if self.filters:

            for filter_function in self.filters:
                scaled_surface = filter_function(scaled_surface)

        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        self.time_elapsed_milliseconds = self.clock.tick(Screen.FPS)


# how much of this is redundant due to pygame Surface.scroll?
class Viewport(object):
    """Display only a fixed area of a surface.

    Attributes:
      surface (pygame.Surface): viewport surface
      rect (pygame.Rect): viewable coordinates

    """

    def __init__(self, size):
        """

        Args:
          size (tuple): (int x, int y) pixel dimensions of viewport.

        Example:
          >>> viewport = Viewport(master_surface, (320, 240))

        """

        self.surface = pygame.Surface(size)
        self.rect = pygame.Rect((0, 0), size)

    def center_on(self, entity, master_rect):
        """Center the viewport rectangle on an object.

        Note:
          entity must have entity.rect (pygame.Rect)

          Does not center if centering would render off-surface;
          finds nearest.

        Args:
          entity: something with an attribute "rect" which value is
            a pygame.Rect.

        Returns:
          bool: --

        """

        entity_position_x, entity_position_y = entity.rect.center
        difference_x = entity_position_x - self.rect.centerx
        difference_y = entity_position_y - self.rect.centery
        potential_rect = self.rect.move(*(difference_x, difference_y))

        if potential_rect.left < 0:
            difference_x = 0

        if potential_rect.top < 0:
            difference_y = 0

        if potential_rect.right > master_rect.right:
            difference_x = (difference_x -
                            (potential_rect.right - master_rect.right))

        if potential_rect.bottom > master_rect.bottom:
            difference_y = (difference_y -
                            (potential_rect.bottom - master_rect.bottom))

        self.rect.move_ip(*(difference_x, difference_y))

    def relative_position(self, position):
        x, y = position
        offset = self.rect.topleft
        x -= offset[0]
        y -= offset[1]
        position_on_screen = (x, y)

        return position_on_screen

    def blit(self, surface):
        """Draw the correct portion of supplied surface onto viewport.

        Args:
          surface (pygame.Surface): will only draw the area described
            by viewport coordinates.

        Example:
          >>> viewport.blit(tilemap.layer_images[0])

        """

        self.surface.blit(
                          surface,
                          (0, 0),
                          self.rect
                         )


def pil_to_pygame(pil_image, encoding):
    """Convert PIL Image() to pygame Surface.

    Note:
      NOT for animations, use Animation() for that!

    Args:
      pil_image (Image): image to convert to pygame.Surface().
      encoding (str): image encoding, e.g., RGBA

    Returns:
      pygame.Surface: the converted image

    Example:
       >>> pil_to_pygame(gif, "RGBA")
       <pygame.Surface>

    """

    image_as_string = pil_image.convert('RGBA').tostring()

    return pygame.image.fromstring(
                                   image_as_string,
                                   pil_image.size,
                                   'RGBA'
                                  )


# HUGELY IMPORTANT NOTE TO GO SOMEWHERE:
# YUO CANNOT MIX SURFACES OF VARYING BITDEPTHS/SETTINGS.
# IF YOU TRY TO DRAW AN 8 BIT IMAGE ON A 32 BIT SURFACE IT
# WON'T SHOW UP


# should go into sprites or effects
def palette_cycle(surface):
    """get_palette is not sufficient; it generates superflous colors.

    surface (pygame.Surface): 8 bit surface

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
        frames.append((frame, 0.2))
        old_color_list = copy.copy(new_color_list)

    return pyganim.PygAnimation(frames)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
