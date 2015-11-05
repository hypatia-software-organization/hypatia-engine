# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""Why stuff is drawn; logic flow for the game.

Game logic, game component interaction.

Glues various modules/game components together with behaviors defined
in methods belonging to Game().

Note:
  I have not decided firmly on the approach to take. Expect heavy
  changes in the future.

  Sorry for the poor documentation, I have not devised an actual
  architecture for this particular module. I have not decided
  firmly on the approach to take. Here, I'm sort of imitating
  Flask's app.

"""

import io
import os
import tempfile
import datetime
import pygame
from pygame.locals import *

from hypatia import config
from hypatia import state


class Game(object):
    def __init__(self, vfs):
        """The base game object. This links all the components together,
        and is automatically instantiated when Hypatia is loaded with your
        game.

        Args:
          vfs (hypatia.vfs.VFS): The game's virtual file system.
        """

        self.running = True
        self.vfs = vfs

        # create our config object and load the game config into it
        self.config = config.create_config()

        cfgdata = self.vfs.open("/game/game.ini").read().decode('utf-8')
        self.config.readfp(io.StringIO(cfgdata))

        self.states = []

        pygame.init()
        self.clock = pygame.time.Clock()
        self.ms_elapsed = 0

        displayinfo = pygame.display.Info()
        self.physical_size = (displayinfo.current_w, displayinfo.current_h)

        self.update_screen_size()

    def update_screen_size(self):
        """Updates the screen size to the values stored in the current
        configuration.
        """

        screen_size = self.config.get('display', 'screen_size')
        self.screen_size = [int(i) for i in screen_size.split('x')]

        window_size = self.config.get('display', 'window_size')
        self.window_size = [int(i) for i in window_size.split('x')]

        self.fullscreen = self.config.getboolean('display', 'fullscreen')
        self.scaleup = self.config.getboolean('display', 'scaleup')
        self.max_fps = self.config.getint('display', 'maxfps')

        # set up display itself
        screenres = self.screen_size
        flags = DOUBLEBUF

        if self.fullscreen:
            self.fullscreen = True
            screenres = self.physical_size
            flags = FULLSCREEN | DOUBLEBUF

        elif self.scaleup:
            screenres = self.window_size

        self.screen = pygame.display.set_mode(screenres, flags)

    def update(self):
        """Updates the display. This calls the current state's
        :meth:`hypatia.state.State.update` method, and handles any exceptions
        that may arise running the update method.
        """

        if len(self.states) > 0:
            try:
                self.states[-1].update()

            except Exception as e:
                self.state_jump(state.ExceptionDisplayState)

            surface = self.states[-1].surface

        else:
            surface = pygame.Surface(self.screen_size)
            surface.fill((51, 51, 51))

        if self.fullscreen:
            surface = pygame.transform.scale(surface, self.physical_size)
        elif self.scaleup:
            surface = pygame.transform.scale(surface, self.window_size)

        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

        self.ms_elapsed = self.clock.tick(self.max_fps)

    def handle_events(self):
        """Handle pygame events, passing them down to the current state's
        :meth:`hypatia.state.State.handle_event` method.
        """

        for event in pygame.event.get():
            if len(self.states) > 0:
                try:
                    self.states[-1].handle_event(event)

                except:
                    self.state_jump(state.ExceptionDisplayState)

            if event.type == QUIT:
                self.running = False

    def state_jump(self, cls, *args):
        """Jumps to a new state, clearing the previous state stack.

        Arguments:
            cls (State): State class to jump to
            *args: Arguments to pass to the state class
        """

        try:
            for i in self.states:
                i.shutdown()

            c = cls(self, *args)
            c.startup()
            self.states = [c]

        except:
            if cls == state.ExceptionDisplayState:
                raise

            self.state_jump(state.ExceptionDisplayState)

    def state_push(self, cls, *args):
        """Pushes a new state onto the top of the state stack. This
        becomes the active state.

        Arguments:
            cls (State): State class to push
            *args: Arguments to pass to the state class
        """

        try:
            if len(self.states) > 0:
                self.states[-1].suspend()

            c = cls(self, *args)
            c.startup()
            self.states.append(c)

        except:
            self.state_jump(state.ExceptionDisplayState)

    def state_pop(self):
        """Pops the current state off the stack, returning control
        to the previous state on the stack.
        """

        try:
            if len(self.states) > 0:
                self.states[-1].shutdown()
                self.states.pop()
                self.states[-1].resume()

        except:
            self.state_jump(state.ExceptionDisplayState)

    def main_loop(self):
        """Runs the game.
        """

        while self.running:
            self.handle_events()
            self.update()
