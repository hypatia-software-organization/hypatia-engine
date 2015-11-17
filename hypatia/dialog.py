"""Dialog, text tools.

Excuse the lack of documentation. This is all very
experimental and it's going to be rewritten.

This module is really bad and uses a horrible, hacked-together
method for text rendering which isn't flexible in the least.

I will be redoing this so it has the same abilities as the
Golden Sun text boxes. The sound module will provide meep
speak.

"""


import textwrap

import pygame


class DialogBox(object):

    def __init__(self, viewport_size, font=None):
        """Place for displaying text...

        Args:
          font (pygame.font.Font): --
          screen_size (tuple): x, y tuple; screen resolution in pixels

        Note:
          There is only one DialogBox in a Game() which gets
          printed to. When it appears self.active is True, when
          it is hidden self.active is False.

        """

        self.font = (font or
                     pygame.font.Font('resources/fonts/VeraMono.ttf', 5))
        self.active = False
        self.viewport_width = viewport_size[0]

        self.character_size = self.font.size('A')
        self.characters_wide = self.viewport_width // self.character_size[0]

        self.message_lines = None
        self.lines_at_a_time = 4
        self.full_surface = None

        # Could just use Viewport!
        self.viewport_rect = None
        self.reset_viewport_rect()

    def reset_viewport_rect(self):
        viewport_dimensions = (self.viewport_width,
                               self.lines_at_a_time * self.character_size[1])
        self.viewport_rect = pygame.Rect((0, 0), viewport_dimensions)

    def set_message(self, message):
        """Blit according to text wrap restrictions.

        can also use surface scroll to attribute index

        """

        message_lines = textwrap.wrap(message, self.characters_wide)
        full_rect_height = self.character_size[1] * len(message_lines)
        full_rect_size = (self.viewport_width, full_rect_height)
        full_surface = pygame.Surface(full_rect_size)
        full_surface.fill((255, 0, 255))
        y_pos = 0

        for line in message_lines:
            text_surface = self.font.render(line,
                                            False,
                                            (0, 0, 0))
            full_surface.blit(text_surface, (0, y_pos))
            y_pos += self.character_size[1]

        self.full_surface = full_surface
        self.active = True
        self.reset_viewport_rect()

    def next(self):
        # NOTE: i forgot what these notes are...
        # will stay off beause viewport rect never resets!
        # when run out set self.active to false!
        offset = (0, self.character_size[1] * self.lines_at_a_time)
        self.viewport_rect.move_ip(offset)

        if not self.viewport_rect.colliderect(self.full_surface.get_rect()):
            self.active = False
            self.reset_viewport_rect()

    # incomplete
    def blit(self, to_surface):
        """Blit current viewport of text to_surface.

        """

        if self.active:
            to_surface.blit(self.full_surface, (0, 0), self.viewport_rect)
