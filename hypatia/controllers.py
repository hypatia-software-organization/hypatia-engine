# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""Anything to do with game controls. Controller objects, which
handles the association of input with changing the state of a provided
object. For example, the WorldController needs a Game instance
(currently) in order to make input reflect and retrieve changes in the
Game instance and scene.

This is a sloppy implementation. I'll come
back to refine it sooner-than-later.

"""

import pygame
from pygame.locals import *

from hypatia import constants


class GameController(object):
    """Base input controller, "game pad," which is
    inherited by all input classes/controllers.

    This is handy for having controller
    methods which are universal.

    """

    def __init__(self, game):
        self.game = game


class MenuController(GameController):
    """For menu screens.

    Scaffolding.

    """

    pass


class WorldController(GameController):
    """For the overworld. The controller for manipulating the state
    of the general world, when the player is walking about.

    """

    def handle_input(self):
        """For the "overworld," a generic scene where
        the player moves about the scene.

        This is in its infancy.

        Returns
          bool: returns True if escape was never
            pressed; returns false if escape pressed.

        """

        # fetch all the key events and respond to them
        for event in pygame.event.get():

            if event.type == KEYUP:
                # the player specifically let go of a key,
                # so let's change the player's walkabout
                # action to standing
                (self.game.scene.human_player
                 .walkabout.action) = constants.Action.stand

            # This isn't the best implementation of dialog boxes.
            # Ideally, I'll use a MenuController (switch over to one)
            # in the future.
            #
            # need to trap player in a next loop, release when no next
            if event.type == KEYDOWN and event.key == K_SPACE:

                # do until
                if self.game.dialogbox.active:
                    self.game.dialogbox.next()
                else:
                    (self.game.scene.human_player
                     .talk(self.game.scene.npcs, self.game.dialogbox))

        # respond to states
        if self.game.dialogbox.active:

            # As long as a dialog box is active the player
            # cannot hit escape? This seems like bad code.
            return True

        # get the key states
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_ESCAPE]:

            # the escape key is pressed; we're
            # done; quitting time.
            return False

        # movement from key states (if key is pressed)
        # map an input key to a direction enumeration,
        # so when the player is pressing that key,
        # they will be moving in that direction.
        movement = {K_UP: constants.Direction.north,
                    K_RIGHT: constants.Direction.east,
                    K_DOWN: constants.Direction.south,
                    K_LEFT: constants.Direction.west}

        for key, direction in movement.items():

            if pressed_keys[key]:
                self.game.scene.human_player.move(self.game, direction)

        return True
