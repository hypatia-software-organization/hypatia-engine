# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""How stuff is drawn. Very specific rendering stuff. Includes
screen and viewport.

Mostly a lot of scaffolding.

See Also:
    :mod:`animations`

"""

import sys
import time
import itertools

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
          >>> viewport = Viewport((320, 240))

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
          >>> viewport = Viewport((100, 100))
          >>> surface = pygame.Surface((800, 600))
          >>> viewport.blit(surface)

        """

        self.surface.blit(
                          surface,
                          (0, 0),
                          self.rect
                         )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
